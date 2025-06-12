"""
Market Agent - Integrates Google News Superforecaster with Manifold Markets trading
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add manifold_markets to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'manifold_markets'))

from .google_news_superforecaster import GoogleNewsSuperforecaster, ForecastResult
from manifold_markets.client import ManifoldMarketsClient
# from manifold_markets.forecasting_bot import ManifoldForecastingBot  # Avoid circular import
from ..utils.agent_logger import agent_logger


@dataclass
class TradingDecision:
    """Trading decision with forecast and position sizing"""
    market_id: str
    market_question: str
    forecast_probability: float
    current_market_probability: float
    edge: float
    recommended_action: str  # "BUY_YES", "BUY_NO", "HOLD"
    position_size: float
    confidence: str
    reasoning: str
    forecast_result: ForecastResult


class MarketAgent:
    """
    Market Agent that combines superforecasting with Manifold Markets trading
    """
    
    def __init__(self, openrouter_api_key: str, manifold_api_key: str = None, serp_api_key: str = None):
        self.logger = agent_logger
        self.openrouter_api_key = openrouter_api_key
        self.manifold_api_key = manifold_api_key
        self.serp_api_key = serp_api_key
        
        # Initialize superforecaster
        self.superforecaster = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_api_key,
            serp_api_key=serp_api_key
        )
        
        # Initialize Manifold client
        self.manifold_client = ManifoldMarketsClient(api_key=manifold_api_key)
        
        # Initialize forecasting bot (lazy import to avoid circular dependency)
        self.forecasting_bot = None
        
        self.logger.info("✅ Market Agent initialized")
    
    def analyze_market(self, market_id: str, min_edge: float = 0.05) -> TradingDecision:
        """
        Analyze a single market and make trading decision
        
        Args:
            market_id: Manifold market ID
            min_edge: Minimum edge required to trade
            
        Returns:
            TradingDecision with forecast and recommendation
        """
        self.logger.info(f"🔍 Analyzing market: {market_id}")
        
        # Get market details
        market = self.manifold_client.get_market(market_id)
        if not market:
            raise ValueError(f"Market {market_id} not found")
        
        question = market['question']
        current_prob = market['probability']
        
        self.logger.info(f"📋 Question: {question}")
        self.logger.info(f"📊 Current market probability: {current_prob:.3f}")
        
        # Generate forecast using superforecaster
        forecast_result = self.superforecaster.forecast_with_google_news(
            question=question,
            background=market.get('description', ''),
            is_benchmark=False
        )
        
        forecast_prob = forecast_result.probability
        edge = abs(forecast_prob - current_prob)
        
        self.logger.info(f"🎯 Forecast probability: {forecast_prob:.3f}")
        self.logger.info(f"📈 Edge: {edge:.3f}")
        
        # Determine trading action
        if edge < min_edge:
            action = "HOLD"
            position_size = 0.0
            reasoning = f"Edge {edge:.3f} below minimum threshold {min_edge:.3f}"
        elif forecast_prob > current_prob + min_edge:
            action = "BUY_YES"
            position_size = min(edge * 100, 50)  # Position size based on edge, max 50
            reasoning = f"Forecast {forecast_prob:.3f} significantly above market {current_prob:.3f}"
        elif forecast_prob < current_prob - min_edge:
            action = "BUY_NO"
            position_size = min(edge * 100, 50)
            reasoning = f"Forecast {forecast_prob:.3f} significantly below market {current_prob:.3f}"
        else:
            action = "HOLD"
            position_size = 0.0
            reasoning = f"Edge {edge:.3f} insufficient for trading"
        
        return TradingDecision(
            market_id=market_id,
            market_question=question,
            forecast_probability=forecast_prob,
            current_market_probability=current_prob,
            edge=edge,
            recommended_action=action,
            position_size=position_size,
            confidence=forecast_result.confidence_level,
            reasoning=reasoning,
            forecast_result=forecast_result
        )
    
    def analyze_markets(self, market_ids: List[str], min_edge: float = 0.05) -> List[TradingDecision]:
        """
        Analyze multiple markets and return trading decisions
        
        Args:
            market_ids: List of Manifold market IDs
            min_edge: Minimum edge required to trade
            
        Returns:
            List of TradingDecision objects
        """
        decisions = []
        
        for market_id in market_ids:
            try:
                decision = self.analyze_market(market_id, min_edge)
                decisions.append(decision)
                self.logger.info(f"✅ Analyzed {market_id}: {decision.recommended_action}")
            except Exception as e:
                self.logger.error(f"❌ Failed to analyze {market_id}: {e}")
                continue
        
        return decisions
    
    def execute_trades(self, decisions: List[TradingDecision], dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute trades based on decisions
        
        Args:
            decisions: List of trading decisions
            dry_run: If True, only simulate trades
            
        Returns:
            Dictionary with execution results
        """
        if not self.manifold_api_key and not dry_run:
            raise ValueError("Manifold API key required for live trading")
        
        results = {
            "executed_trades": [],
            "skipped_trades": [],
            "total_amount": 0,
            "dry_run": dry_run
        }
        
        for decision in decisions:
            if decision.recommended_action == "HOLD":
                results["skipped_trades"].append({
                    "market_id": decision.market_id,
                    "reason": "No edge"
                })
                continue
            
            trade_info = {
                "market_id": decision.market_id,
                "question": decision.market_question,
                "action": decision.recommended_action,
                "amount": decision.position_size,
                "forecast_prob": decision.forecast_probability,
                "market_prob": decision.current_market_probability,
                "edge": decision.edge
            }
            
            if dry_run:
                self.logger.info(f"🎭 DRY RUN: Would {decision.recommended_action} {decision.position_size} on {decision.market_id}")
                trade_info["status"] = "simulated"
            else:
                try:
                    # Execute actual trade via forecasting bot
                    if decision.recommended_action == "BUY_YES":
                        outcome = "YES"
                    else:
                        outcome = "NO"
                    
                    # Place bet using manifold client
                    bet_result = self.manifold_client.place_bet(
                        market_id=decision.market_id,
                        outcome=outcome,
                        amount=decision.position_size
                    )
                    
                    trade_info["status"] = "executed"
                    trade_info["bet_id"] = bet_result.get("id")
                    results["total_amount"] += decision.position_size
                    
                    self.logger.info(f"✅ Executed trade: {decision.recommended_action} {decision.position_size} on {decision.market_id}")
                    
                except Exception as e:
                    trade_info["status"] = "failed"
                    trade_info["error"] = str(e)
                    self.logger.error(f"❌ Failed to execute trade on {decision.market_id}: {e}")
            
            results["executed_trades"].append(trade_info)
        
        return results
    
    def find_opportunities(self, limit: int = 20, min_edge: float = 0.1) -> List[TradingDecision]:
        """
        Find trading opportunities from active markets
        
        Args:
            limit: Maximum number of markets to analyze
            min_edge: Minimum edge required
            
        Returns:
            List of profitable trading opportunities
        """
        self.logger.info(f"🔍 Searching for opportunities (limit={limit}, min_edge={min_edge})")
        
        # Get active markets
        markets = self.manifold_client.get_markets(limit=limit * 2)  # Get more to filter
        
        # Filter for binary markets that are still open
        binary_markets = [
            m for m in markets 
            if m.get('outcomeType') == 'BINARY' and not m.get('isResolved', False)
        ][:limit]
        
        market_ids = [m['id'] for m in binary_markets]
        
        # Analyze markets
        decisions = self.analyze_markets(market_ids, min_edge)
        
        # Filter for profitable opportunities
        opportunities = [
            d for d in decisions 
            if d.recommended_action != "HOLD" and d.edge >= min_edge
        ]
        
        # Sort by edge (highest first)
        opportunities.sort(key=lambda x: x.edge, reverse=True)
        
        self.logger.info(f"✅ Found {len(opportunities)} opportunities out of {len(decisions)} markets analyzed")
        
        return opportunities
    
    def backtest_period(self, start_date: str, end_date: str, initial_balance: float = 1000) -> Dict[str, Any]:
        """
        Backtest trading strategy over a time period
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            initial_balance: Starting balance
            
        Returns:
            Backtest results
        """
        self.logger.info(f"📊 Starting backtest from {start_date} to {end_date}")
        
        # Simple backtest implementation
        # Get historical markets from the period
        # This is a simplified version - full implementation would need historical data
        
        results = {
            "start_date": start_date,
            "end_date": end_date,
            "initial_balance": initial_balance,
            "final_balance": initial_balance,  # Placeholder
            "total_trades": 0,
            "profitable_trades": 0,
            "roi": 0.0,
            "message": "Backtest functionality requires historical market data integration"
        }
        
        return results