"""
Manifold Markets Integration with Google News Superforecaster
Combines AI forecasting capabilities with Manifold Markets trading
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import sys
from pathlib import Path

# Add the parent directory to path to import from ai_forecasts
sys.path.insert(0, str(Path(__file__).parent.parent))

from .client import ManifoldMarketsClient

# Import from ai_forecasts module
try:
    from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster, ForecastResult
except ImportError:
    # Alternative import path
    sys.path.insert(0, str(Path(__file__).parent.parent / "ai_forecasts"))
    from agents.google_news_superforecaster import GoogleNewsSuperforecaster, ForecastResult

logger = logging.getLogger(__name__)


@dataclass
class ForecastedMarket:
    """Market with AI forecast analysis"""
    market_id: str
    question: str
    current_prob: float
    ai_forecast: ForecastResult
    forecast_difference: float  # AI forecast - current market probability
    confidence_score: float  # How confident the AI is
    recommended_action: str  # "BUY_YES", "BUY_NO", "HOLD", "AVOID"
    bet_amount: Optional[float] = None
    reasoning: str = ""


class ManifoldForecastingBot:
    """
    Bot that uses Google News Superforecaster to analyze Manifold Markets
    and make informed predictions/bets
    """
    
    def __init__(
        self, 
        manifold_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        serp_api_key: Optional[str] = None,
        default_bet_amount: float = 10.0,
        confidence_threshold: float = 0.15  # Minimum difference to consider betting
    ):
        """
        Initialize the forecasting bot
        
        Args:
            manifold_api_key: Manifold Markets API key
            openrouter_api_key: OpenRouter API key for LLM
            serp_api_key: SERP API key for Google News searches
            default_bet_amount: Default amount to bet in Mana
            confidence_threshold: Minimum confidence difference to make bets
        """
        # Initialize API clients
        self.manifold = ManifoldMarketsClient(manifold_api_key)
        
        # Initialize Google News Superforecaster
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        
        if not self.openrouter_api_key:
            raise ValueError("OpenRouter API key is required for AI forecasting")
            
        self.forecaster = GoogleNewsSuperforecaster(
            openrouter_api_key=self.openrouter_api_key,
            serp_api_key=self.serp_api_key
        )
        
        # Bot configuration
        self.default_bet_amount = default_bet_amount
        self.confidence_threshold = confidence_threshold
        
        logger.info("ManifoldForecastingBot initialized")
    
    def analyze_market(self, market: Dict[str, Any]) -> Optional[ForecastedMarket]:
        """
        Analyze a single market using AI forecasting
        
        Args:
            market: Market dictionary from Manifold API
            
        Returns:
            ForecastedMarket with analysis, or None if analysis failed
        """
        try:
            # Extract market information
            market_id = market.get("id")
            question = market.get("question", "")
            current_prob = market.get("probability", 0.5)  # Current market probability
            
            # Skip if market is closed or resolved
            if market.get("isResolved", False) or market.get("closeTime", 0) < datetime.now().timestamp() * 1000:
                logger.info(f"Skipping resolved/closed market: {question}")
                return None
            
            # Skip non-binary markets for now
            if market.get("outcomeType") != "BINARY":
                logger.info(f"Skipping non-binary market: {question}")
                return None
            
            logger.info(f"Analyzing market: {question}")
            
            # Generate AI forecast
            ai_forecast = self.forecaster.forecast_with_google_news(
                question=question,
                background=market.get("description", ""),
                cutoff_date=datetime.now(),
                time_horizon="1 year",
                is_benchmark=False
            )
            
            # Calculate forecast difference
            forecast_diff = ai_forecast.probability - current_prob
            
            # Determine recommended action
            action, bet_amount, reasoning = self._determine_action(
                ai_forecast, current_prob, forecast_diff, market
            )
            
            return ForecastedMarket(
                market_id=market_id,
                question=question,
                current_prob=current_prob,
                ai_forecast=ai_forecast,
                forecast_difference=forecast_diff,
                confidence_score=self._calculate_confidence_score(ai_forecast),
                recommended_action=action,
                bet_amount=bet_amount,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market {market.get('id', 'unknown')}: {e}")
            return None
    
    def analyze_markets(
        self, 
        limit: int = 50, 
        search_term: Optional[str] = None,
        filter_type: str = "open"
    ) -> List[ForecastedMarket]:
        """
        Analyze multiple markets and return forecasted results
        
        Args:
            limit: Number of markets to analyze
            search_term: Optional search term to filter markets
            filter_type: Type of markets to fetch ("open", "all", etc.)
            
        Returns:
            List of ForecastedMarket objects
        """
        try:
            # Fetch markets
            if search_term:
                markets = self.manifold.search_markets(
                    term=search_term, 
                    limit=limit, 
                    filter=filter_type
                )
            else:
                markets = self.manifold.get_markets(limit=limit)
            
            logger.info(f"Fetched {len(markets)} markets for analysis")
            
            # Analyze each market
            forecasted_markets = []
            for market in markets:
                forecasted_market = self.analyze_market(market)
                if forecasted_market:
                    forecasted_markets.append(forecasted_market)
            
            # Sort by confidence score (highest first)
            forecasted_markets.sort(key=lambda x: abs(x.forecast_difference), reverse=True)
            
            logger.info(f"Successfully analyzed {len(forecasted_markets)} markets")
            return forecasted_markets
            
        except Exception as e:
            logger.error(f"Error analyzing markets: {e}")
            return []
    
    def find_opportunities(
        self, 
        min_difference: float = 0.15,
        min_confidence: str = "medium",
        limit: int = 100
    ) -> List[ForecastedMarket]:
        """
        Find betting opportunities where AI forecast significantly differs from market
        
        Args:
            min_difference: Minimum absolute difference between AI and market probability
            min_confidence: Minimum confidence level ("low", "medium", "high")
            limit: Number of markets to analyze
            
        Returns:
            List of promising betting opportunities
        """
        # Analyze markets
        all_forecasts = self.analyze_markets(limit=limit)
        
        # Filter for opportunities
        opportunities = []
        confidence_levels = {"low": 1, "medium": 2, "high": 3}
        min_conf_score = confidence_levels.get(min_confidence, 2)
        
        for forecast in all_forecasts:
            # Check difference threshold
            if abs(forecast.forecast_difference) < min_difference:
                continue
                
            # Check confidence level
            forecast_conf_score = confidence_levels.get(forecast.ai_forecast.confidence_level, 1)
            if forecast_conf_score < min_conf_score:
                continue
                
            # Skip if action is HOLD or AVOID
            if forecast.recommended_action in ["HOLD", "AVOID"]:
                continue
                
            opportunities.append(forecast)
        
        logger.info(f"Found {len(opportunities)} betting opportunities")
        return opportunities
    
    def execute_bets(
        self, 
        opportunities: List[ForecastedMarket],
        dry_run: bool = True,
        max_total_amount: float = 100.0
    ) -> List[Dict[str, Any]]:
        """
        Execute bets on identified opportunities
        
        Args:
            opportunities: List of betting opportunities
            dry_run: If True, don't actually place bets (just simulate)
            max_total_amount: Maximum total amount to bet across all opportunities
            
        Returns:
            List of bet results
        """
        if not self.manifold.api_key and not dry_run:
            logger.warning("No API key provided - running in dry run mode")
            dry_run = True
        
        results = []
        total_bet = 0.0
        
        for opportunity in opportunities:
            # Check if we've reached betting limit
            if total_bet + (opportunity.bet_amount or 0) > max_total_amount:
                logger.warning(f"Reached maximum betting limit of {max_total_amount}")
                break
            
            # Determine bet outcome
            outcome = "YES" if opportunity.forecast_difference > 0 else "NO"
            bet_amount = opportunity.bet_amount or self.default_bet_amount
            
            result = {
                "market_id": opportunity.market_id,
                "question": opportunity.question,
                "outcome": outcome,
                "amount": bet_amount,
                "ai_probability": opportunity.ai_forecast.probability,
                "market_probability": opportunity.current_prob,
                "difference": opportunity.forecast_difference,
                "reasoning": opportunity.reasoning,
                "dry_run": dry_run
            }
            
            if not dry_run:
                try:
                    # Place actual bet
                    bet_response = self.manifold.place_bet(
                        contract_id=opportunity.market_id,
                        amount=bet_amount,
                        outcome=outcome
                    )
                    result.update({
                        "success": True,
                        "bet_id": bet_response.get("id"),
                        "bet_response": bet_response
                    })
                    total_bet += bet_amount
                    logger.info(f"Placed bet: {outcome} ${bet_amount} on '{opportunity.question}'")
                    
                except Exception as e:
                    result.update({
                        "success": False,
                        "error": str(e)
                    })
                    logger.error(f"Failed to place bet on {opportunity.question}: {e}")
            else:
                result["success"] = True
                total_bet += bet_amount
                logger.info(f"[DRY RUN] Would bet: {outcome} ${bet_amount} on '{opportunity.question}'")
            
            results.append(result)
        
        logger.info(f"Executed {len(results)} bets (total: ${total_bet:.2f})")
        return results
    
    def _determine_action(
        self, 
        ai_forecast: ForecastResult, 
        current_prob: float, 
        forecast_diff: float,
        market: Dict[str, Any]
    ) -> Tuple[str, Optional[float], str]:
        """
        Determine what action to take based on AI forecast vs market probability
        
        Returns:
            Tuple of (action, bet_amount, reasoning)
        """
        abs_diff = abs(forecast_diff)
        
        # Avoid betting if forecast is uncertain or market is about to close
        if ai_forecast.confidence_level == "low":
            return "AVOID", None, "AI forecast confidence is too low"
        
        # Check if market closes soon (within 24 hours)
        close_time = market.get("closeTime", float('inf'))
        if close_time < (datetime.now().timestamp() + 86400) * 1000:  # 24 hours in ms
            return "AVOID", None, "Market closes too soon"
        
        # Don't bet if difference is below threshold
        if abs_diff < self.confidence_threshold:
            return "HOLD", None, f"Difference ({abs_diff:.3f}) below threshold ({self.confidence_threshold})"
        
        # Calculate bet amount based on confidence and difference
        base_amount = self.default_bet_amount
        confidence_multiplier = {"low": 0.5, "medium": 1.0, "high": 1.5}[ai_forecast.confidence_level]
        difference_multiplier = min(abs_diff * 3, 2.0)  # Cap at 2x
        
        bet_amount = base_amount * confidence_multiplier * difference_multiplier
        bet_amount = round(bet_amount, 2)
        
        # Determine direction
        if forecast_diff > 0:
            action = "BUY_YES"
            reasoning = f"AI predicts {ai_forecast.probability:.1%} vs market {current_prob:.1%} (+{forecast_diff:.1%})"
        else:
            action = "BUY_NO"
            reasoning = f"AI predicts {ai_forecast.probability:.1%} vs market {current_prob:.1%} ({forecast_diff:.1%})"
        
        return action, bet_amount, reasoning
    
    def _calculate_confidence_score(self, forecast: ForecastResult) -> float:
        """Calculate a numeric confidence score from forecast"""
        confidence_map = {"low": 0.3, "medium": 0.6, "high": 0.9}
        return confidence_map.get(forecast.confidence_level, 0.5)
    
    def generate_report(self, forecasted_markets: List[ForecastedMarket]) -> Dict[str, Any]:
        """
        Generate a summary report of market analysis
        
        Args:
            forecasted_markets: List of analyzed markets
            
        Returns:
            Summary report dictionary
        """
        if not forecasted_markets:
            return {"error": "No markets analyzed"}
        
        # Calculate summary statistics
        total_markets = len(forecasted_markets)
        opportunities = [m for m in forecasted_markets if m.recommended_action in ["BUY_YES", "BUY_NO"]]
        high_confidence = [m for m in forecasted_markets if m.ai_forecast.confidence_level == "high"]
        
        avg_difference = sum(abs(m.forecast_difference) for m in forecasted_markets) / total_markets
        max_difference = max(abs(m.forecast_difference) for m in forecasted_markets)
        
        # Top opportunities
        top_opportunities = sorted(
            opportunities, 
            key=lambda x: abs(x.forecast_difference), 
            reverse=True
        )[:10]
        
        report = {
            "summary": {
                "total_markets_analyzed": total_markets,
                "betting_opportunities": len(opportunities),
                "high_confidence_forecasts": len(high_confidence),
                "average_probability_difference": round(avg_difference, 3),
                "max_probability_difference": round(max_difference, 3)
            },
            "top_opportunities": [
                {
                    "question": opp.question,
                    "market_id": opp.market_id,
                    "action": opp.recommended_action,
                    "ai_probability": round(opp.ai_forecast.probability, 3),
                    "market_probability": round(opp.current_prob, 3),
                    "difference": round(opp.forecast_difference, 3),
                    "confidence": opp.ai_forecast.confidence_level,
                    "bet_amount": opp.bet_amount,
                    "reasoning": opp.reasoning
                }
                for opp in top_opportunities
            ],
            "confidence_distribution": {
                "high": len([m for m in forecasted_markets if m.ai_forecast.confidence_level == "high"]),
                "medium": len([m for m in forecasted_markets if m.ai_forecast.confidence_level == "medium"]),
                "low": len([m for m in forecasted_markets if m.ai_forecast.confidence_level == "low"])
            },
            "action_distribution": {
                "BUY_YES": len([m for m in forecasted_markets if m.recommended_action == "BUY_YES"]),
                "BUY_NO": len([m for m in forecasted_markets if m.recommended_action == "BUY_NO"]),
                "HOLD": len([m for m in forecasted_markets if m.recommended_action == "HOLD"]),
                "AVOID": len([m for m in forecasted_markets if m.recommended_action == "AVOID"])
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return report
