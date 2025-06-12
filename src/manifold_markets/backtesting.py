"""
Enhanced Backtesting module for Manifold Markets Trading Bot
Uses real historical data and Kelly Criterion for comprehensive strategy testing
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pandas as pd
from pathlib import Path
import asyncio

from .client import ManifoldMarketsClient
from .kelly_criterion import KellyCriterionCalculator, KellyBet
from .historical_data import ManifoldHistoricalDataManager, HistoricalMarket
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster

logger = logging.getLogger(__name__)


@dataclass
class HistoricalTrade:
    """Record of a simulated historical trade"""
    trade_id: str
    market_id: str
    question: str
    trade_date: datetime
    outcome: str  # "YES" or "NO"
    amount: float
    entry_price: float  # Market probability when bet was placed
    ai_probability: float
    confidence: str
    reasoning: str
    
    # Results (filled when market resolves)
    resolution_date: Optional[datetime] = None
    resolved_outcome: Optional[str] = None  # "YES", "NO", "CANCEL"
    payout: Optional[float] = None
    profit: Optional[float] = None
    roi: Optional[float] = None


@dataclass
class BacktestResult:
    """Results from a backtesting run"""
    start_date: datetime
    end_date: datetime
    initial_balance: float
    final_balance: float
    total_profit: float
    total_roi: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    kelly_utilization: float
    markets_analyzed: int
    avg_trade_size: float
    largest_win: float
    largest_loss: float
    avg_profit_per_trade: float
    daily_returns: List[float]
    balance_history: List[Tuple[datetime, float]]
    trade_history: List[HistoricalTrade]

# Extension to the main bot class
class RealDataBacktester:
    """
    Enhanced backtesting system using real Manifold Markets historical data
    Implements Kelly Criterion and sophisticated risk management
    """
    
    def __init__(
        self,
        openrouter_api_key: str,
        serp_api_key: str,
        max_kelly_fraction: float = 0.25,
        min_edge: float = 0.05,
        data_dir: str = "data/backtesting"
    ):
        """
        Initialize the real data backtester
        
        Args:
            openrouter_api_key: OpenRouter API key for AI predictions
            serp_api_key: SERP API key for Google News
            max_kelly_fraction: Maximum Kelly fraction to use
            min_edge: Minimum edge required for betting
            data_dir: Directory for storing backtest data
        """
        self.kelly_calculator = KellyCriterionCalculator(max_kelly_fraction, min_edge)
        self.historical_data = ManifoldHistoricalDataManager()
        self.forecaster = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_api_key,
            serp_api_key=serp_api_key
        )
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_historical_backtest(
        self,
        start_date: datetime,
        end_date: datetime,
        initial_balance: float = 100.0,
        max_simultaneous_positions: int = 5,
        min_market_volume: float = 100.0,
        min_market_bettors: int = 5
    ) -> BacktestResult:
        """
        Run a comprehensive backtest using real historical data
        
        Args:
            start_date: Start date for backtesting
            end_date: End date for backtesting
            initial_balance: Starting balance
            max_simultaneous_positions: Maximum simultaneous positions
            min_market_volume: Minimum market volume to consider
            min_market_bettors: Minimum number of bettors to consider
            
        Returns:
            BacktestResult with comprehensive metrics
        """
        try:
            logger.info(f"Starting historical backtest from {start_date} to {end_date}")
            
            # Download historical data if needed
            if not (self.data_dir.parent / "manifold_historical" / "markets.json").exists():
                logger.info("Downloading historical data...")
                self.historical_data.download_historical_data()
            
            # Get suitable markets for backtesting
            markets = self.historical_data.get_markets_for_backtesting(
                start_date=start_date,
                end_date=end_date,
                min_volume=min_market_volume,
                min_bettors=min_market_bettors,
                resolved_only=True
            )
            
            logger.info(f"Found {len(markets)} suitable markets for backtesting")
            
            if not markets:
                raise ValueError("No suitable markets found for backtesting")
            
            # Initialize backtest state
            current_balance = initial_balance
            active_positions = {}
            completed_trades = []
            balance_history = [(start_date, initial_balance)]
            markets_analyzed = 0
            
            # Sort markets by creation time
            markets.sort(key=lambda x: x.created_time)
            
            # Simulate trading day by day
            current_date = start_date
            while current_date <= end_date:
                # Process markets created on this day
                daily_markets = [m for m in markets if m.created_time.date() == current_date.date()]
                
                for market in daily_markets:
                    markets_analyzed += 1
                    
                    # Skip if we already have too many positions
                    if len(active_positions) >= max_simultaneous_positions:
                        continue
                    
                    # Get AI prediction for this market
                    prediction = await self._get_historical_prediction(market, current_date)
                    
                    if prediction:
                        # Calculate Kelly bet
                        market_prob = 0.5  # Initial market probability (simplified)
                        ai_prob = prediction['probability']
                        
                        # Calculate Kelly recommendations for both outcomes
                        for outcome in ["YES", "NO"]:
                            kelly_fraction = self.kelly_calculator.calculate_kelly_fraction(
                                ai_prob, market_prob, outcome
                            )
                            
                            if kelly_fraction > 0:
                                bet_amount = min(
                                    kelly_fraction * current_balance,
                                    current_balance * 0.2  # Max 20% per bet
                                )
                                
                                if bet_amount >= 1.0:  # Minimum bet size
                                    # Create simulated trade
                                    trade = HistoricalTrade(
                                        trade_id=f"trade_{len(completed_trades)}",
                                        market_id=market.id,
                                        question=market.question,
                                        trade_date=current_date,
                                        outcome=outcome,
                                        amount=bet_amount,
                                        entry_price=market_prob if outcome == "YES" else 1 - market_prob,
                                        ai_probability=ai_prob,
                                        confidence=prediction.get('confidence', 0.5),
                                        reasoning=prediction.get('reasoning', '')
                                    )
                                    
                                    active_positions[trade.trade_id] = trade
                                    current_balance -= bet_amount
                                    
                                    logger.debug(f"Placed {outcome} bet of {bet_amount:.2f} on: {market.question[:50]}...")
                                    break  # Only place one bet per market
                
                # Check for market resolutions
                resolved_today = []
                for trade_id, trade in active_positions.items():
                    market = next((m for m in markets if m.id == trade.market_id), None)
                    
                    if market and market.resolution_time and market.resolution_time.date() <= current_date.date():
                        # Market resolved, calculate payout
                        if market.resolution == trade.outcome:
                            # Won the bet
                            payout = trade.amount / trade.entry_price
                            trade.payout = payout
                            trade.profit = payout - trade.amount
                            current_balance += payout
                        else:
                            # Lost the bet
                            trade.payout = 0.0
                            trade.profit = -trade.amount
                        
                        trade.resolution_date = market.resolution_time
                        trade.resolved_outcome = market.resolution
                        trade.roi = trade.profit / trade.amount if trade.amount > 0 else 0
                        
                        completed_trades.append(trade)
                        resolved_today.append(trade_id)
                
                # Remove resolved positions
                for trade_id in resolved_today:
                    del active_positions[trade_id]
                
                # Record daily balance
                balance_history.append((current_date, current_balance))
                
                # Move to next day
                current_date += timedelta(days=1)
            
            # Calculate final metrics
            result = self._calculate_backtest_metrics(
                start_date=start_date,
                end_date=end_date,
                initial_balance=initial_balance,
                final_balance=current_balance,
                completed_trades=completed_trades,
                balance_history=balance_history,
                markets_analyzed=markets_analyzed
            )
            
            logger.info(f"Backtest completed. Final balance: {current_balance:.2f}, ROI: {result.total_roi:.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running historical backtest: {e}")
            raise
    
    async def _get_historical_prediction(self, market: HistoricalMarket, prediction_date: datetime) -> Optional[Dict]:
        """
        Get AI prediction for a historical market
        
        Args:
            market: Historical market to predict
            prediction_date: Date when prediction is made
            
        Returns:
            Prediction dictionary or None
        """
        try:
            # For backtesting, we'll use a simplified prediction model
            # In practice, you'd use the full forecasting pipeline with historical news data
            
            # Get similar historical markets for context
            similar_markets = self.historical_data.get_similar_markets(market.question, limit=5)
            
            # Calculate base rate from similar markets
            resolved_similar = [m for m in similar_markets if m.resolution in ['YES', 'NO']]
            
            if resolved_similar:
                yes_rate = sum(1 for m in resolved_similar if m.resolution == 'YES') / len(resolved_similar)
                
                # Simple prediction based on historical base rate with some noise
                import random
                noise = random.uniform(-0.1, 0.1)
                ai_probability = max(0.1, min(0.9, yes_rate + noise))
                
                confidence = 0.6 if len(resolved_similar) >= 3 else 0.4
                
                return {
                    'probability': ai_probability,
                    'confidence': confidence,
                    'reasoning': f"Based on {len(resolved_similar)} similar markets with {yes_rate:.2f} YES rate"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting historical prediction: {e}")
            return None
    
    def _calculate_backtest_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        initial_balance: float,
        final_balance: float,
        completed_trades: List[HistoricalTrade],
        balance_history: List[Tuple[datetime, float]],
        markets_analyzed: int
    ) -> BacktestResult:
        """Calculate comprehensive backtest metrics"""
        try:
            total_profit = final_balance - initial_balance
            total_roi = total_profit / initial_balance if initial_balance > 0 else 0
            
            # Trade statistics
            total_trades = len(completed_trades)
            winning_trades = sum(1 for trade in completed_trades if trade.profit > 0)
            losing_trades = total_trades - winning_trades
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # Calculate trade sizes and profits
            trade_amounts = [trade.amount for trade in completed_trades]
            trade_profits = [trade.profit for trade in completed_trades]
            
            avg_trade_size = sum(trade_amounts) / len(trade_amounts) if trade_amounts else 0
            avg_profit_per_trade = sum(trade_profits) / len(trade_profits) if trade_profits else 0
            largest_win = max(trade_profits) if trade_profits else 0
            largest_loss = min(trade_profits) if trade_profits else 0
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(balance_history)):
                prev_balance = balance_history[i-1][1]
                curr_balance = balance_history[i][1]
                if prev_balance > 0:
                    daily_returns.append((curr_balance - prev_balance) / prev_balance)
            
            # Calculate Sharpe ratio
            sharpe_ratio = 0.0
            if len(daily_returns) > 1:
                mean_return = sum(daily_returns) / len(daily_returns)
                variance = sum((r - mean_return) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
                std_dev = variance ** 0.5
                if std_dev > 0:
                    sharpe_ratio = mean_return / std_dev
            
            # Calculate maximum drawdown
            max_drawdown = 0.0
            peak_balance = initial_balance
            for _, balance in balance_history:
                if balance > peak_balance:
                    peak_balance = balance
                else:
                    drawdown = (peak_balance - balance) / peak_balance
                    max_drawdown = max(max_drawdown, drawdown)
            
            # Calculate Kelly utilization (simplified)
            kelly_utilization = 0.15  # Placeholder - would calculate from actual Kelly fractions used
            
            return BacktestResult(
                start_date=start_date,
                end_date=end_date,
                initial_balance=initial_balance,
                final_balance=final_balance,
                total_profit=total_profit,
                total_roi=total_roi,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                kelly_utilization=kelly_utilization,
                markets_analyzed=markets_analyzed,
                avg_trade_size=avg_trade_size,
                largest_win=largest_win,
                largest_loss=largest_loss,
                avg_profit_per_trade=avg_profit_per_trade,
                daily_returns=daily_returns,
                balance_history=balance_history,
                trade_history=completed_trades
            )
            
        except Exception as e:
            logger.error(f"Error calculating backtest metrics: {e}")
            raise


