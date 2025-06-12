"""
Backtesting module for Manifold Markets Forecasting Bot
Allows testing strategies on historical market data with simulated trades
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pandas as pd
from pathlib import Path

from .client import ManifoldMarketsClient
from .forecasting_bot import ManifoldForecastingBot, ForecastedMarket

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
    
    # Trading statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    cancelled_trades: int
    win_rate: float
    avg_profit_per_trade: float
    
    # Market analysis
    markets_analyzed: int
    opportunities_found: int
    opportunity_rate: float
    
    # Performance metrics
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    trades: List[HistoricalTrade] = None
    daily_returns: List[float] = None


class ManifoldBacktester:
    """
    Backtesting engine for Manifold Markets forecasting strategies
    Tests AI predictions against historical market outcomes
    """
    
    def __init__(
        self,
        bot: ManifoldForecastingBot,
        historical_data_path: Optional[str] = None
    ):
        """
        Initialize backtester
        
        Args:
            bot: Configured ManifoldForecastingBot instance
            historical_data_path: Path to historical market data (optional)
        """
        self.bot = bot
        self.historical_data_path = historical_data_path
        self.historical_markets = []
        
        # Load historical data if available
        if historical_data_path and Path(historical_data_path).exists():
            self._load_historical_data()
    
    def _load_historical_data(self):
        """Load historical market data from file"""
        try:
            with open(self.historical_data_path, 'r') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                self.historical_markets = data
            elif isinstance(data, dict) and 'markets' in data:
                self.historical_markets = data['markets']
            else:
                logger.warning("Unexpected historical data format")
                
            logger.info(f"Loaded {len(self.historical_markets)} historical markets")
            
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
    
    def download_historical_data(
        self,
        start_date: datetime,
        end_date: datetime,
        save_path: str,
        limit: int = 1000
    ):
        """
        Download historical market data for backtesting
        
        Args:
            start_date: Start date for data collection
            end_date: End date for data collection  
            save_path: Path to save the data
            limit: Maximum markets to download per request
        """
        logger.info(f"Downloading historical data from {start_date} to {end_date}")
        
        all_markets = []
        
        try:
            # Get markets in batches
            markets = self.bot.manifold.get_markets(limit=limit)
            
            # Filter by date range and resolved status
            start_ts = start_date.timestamp() * 1000
            end_ts = end_date.timestamp() * 1000
            
            filtered_markets = []
            for market in markets:
                created_time = market.get('createdTime', 0)
                close_time = market.get('closeTime', float('inf'))
                
                # Include markets created before end_date and closed after start_date
                if created_time <= end_ts and close_time >= start_ts:
                    # Add historical price data if available
                    market['_backtest_metadata'] = {
                        'downloaded_at': datetime.now().isoformat(),
                        'price_history': self._get_market_price_history(market['id'])
                    }
                    filtered_markets.append(market)
            
            # Save to file
            data = {
                'metadata': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'downloaded_at': datetime.now().isoformat(),
                    'total_markets': len(filtered_markets)
                },
                'markets': filtered_markets
            }
            
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(filtered_markets)} markets to {save_path}")
            return filtered_markets
            
        except Exception as e:
            logger.error(f"Failed to download historical data: {e}")
            return []
    
    def _get_market_price_history(self, market_id: str) -> List[Dict]:
        """Get historical price data for a market (if available)"""
        try:
            # This would need to be implemented based on available APIs
            # For now, return empty list
            return []
        except:
            return []
    
    def run_backtest(
        self,
        start_date: datetime,
        end_date: datetime,
        initial_balance: float = 1000.0,
        confidence_threshold: float = 0.15,
        min_confidence: str = "medium",
        max_bet_per_market: float = 50.0,
        max_daily_bets: float = 200.0
    ) -> BacktestResult:
        """
        Run a backtest simulation
        
        Args:
            start_date: Start date for simulation
            end_date: End date for simulation
            initial_balance: Starting balance in Mana
            confidence_threshold: Minimum probability difference to trade
            min_confidence: Minimum AI confidence level
            max_bet_per_market: Maximum bet per individual market
            max_daily_bets: Maximum total bets per day
            
        Returns:
            BacktestResult with simulation outcomes
        """
        logger.info(f"Running backtest from {start_date} to {end_date}")
        
        # Filter markets for the time period
        markets_to_test = self._get_markets_for_period(start_date, end_date)
        logger.info(f"Found {len(markets_to_test)} markets to test")
        
        if not markets_to_test:
            logger.warning("No markets found for the specified period")
            return self._empty_backtest_result(start_date, end_date, initial_balance)
        
        # Simulation state
        current_balance = initial_balance
        trades = []
        daily_spending = {}
        markets_analyzed = 0
        opportunities_found = 0
        
        # Sort markets by creation date
        markets_to_test.sort(key=lambda m: m.get('createdTime', 0))
        
        for market in markets_to_test:
            try:
                # Skip if market doesn't have required data
                if not self._validate_market_for_backtest(market):
                    continue
                
                markets_analyzed += 1
                
                # Get market creation date for AI cutoff
                created_time = market.get('createdTime', 0) / 1000
                market_date = datetime.fromtimestamp(created_time)
                
                # Skip if market was created outside our test window
                if market_date < start_date or market_date > end_date:
                    continue
                
                # Check daily spending limit
                date_key = market_date.strftime('%Y-%m-%d')
                daily_spent = daily_spending.get(date_key, 0)
                if daily_spent >= max_daily_bets:
                    continue
                
                # Analyze market with AI (using creation date as cutoff)
                forecast = self._analyze_market_historical(market, market_date)
                
                if not forecast:
                    continue
                
                # Check if this is a trading opportunity
                if abs(forecast.forecast_difference) < confidence_threshold:
                    continue
                    
                if forecast.ai_forecast.confidence_level == "low" and min_confidence != "low":
                    continue
                    
                if forecast.ai_forecast.confidence_level != "high" and min_confidence == "high":
                    continue
                
                opportunities_found += 1
                
                # Calculate bet size
                bet_amount = min(
                    forecast.bet_amount or self.bot.default_bet_amount,
                    max_bet_per_market,
                    current_balance * 0.1,  # Don't bet more than 10% of balance
                    max_daily_bets - daily_spent
                )
                
                if bet_amount < 1.0:  # Minimum bet size
                    continue
                
                # Simulate the trade
                trade = self._simulate_trade(
                    market, forecast, market_date, bet_amount
                )
                
                if trade:
                    trades.append(trade)
                    current_balance -= bet_amount
                    daily_spending[date_key] = daily_spent + bet_amount
                    
                    logger.debug(f"Simulated trade: {trade.outcome} ${bet_amount:.2f} on {trade.question[:50]}...")
                
            except Exception as e:
                logger.error(f"Error processing market {market.get('id', 'unknown')}: {e}")
                continue
        
        # Calculate trade outcomes
        self._calculate_trade_outcomes(trades)
        
        # Calculate final results
        total_payout = sum(t.payout or 0 for t in trades)
        final_balance = current_balance + total_payout
        
        return self._calculate_backtest_result(
            start_date, end_date, initial_balance, final_balance,
            trades, markets_analyzed, opportunities_found
        )
    
    def _get_markets_for_period(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict]:
        """Get markets that were active during the specified period"""
        if not self.historical_markets:
            logger.warning("No historical market data available")
            return []
        
        start_ts = start_date.timestamp() * 1000
        end_ts = end_date.timestamp() * 1000
        
        filtered_markets = []
        for market in self.historical_markets:
            created_time = market.get('createdTime', 0)
            close_time = market.get('closeTime', float('inf'))
            
            # Include markets created before end and closed after start
            if created_time <= end_ts and close_time >= start_ts:
                filtered_markets.append(market)
        
        return filtered_markets
    
    def _validate_market_for_backtest(self, market: Dict) -> bool:
        """Check if market has required data for backtesting"""
        required_fields = ['id', 'question', 'createdTime', 'isResolved']
        
        for field in required_fields:
            if field not in market:
                return False
        
        # Must be a binary market
        if market.get('outcomeType') != 'BINARY':
            return False
        
        # Must be resolved (for calculating outcomes)
        if not market.get('isResolved', False):
            return False
            
        # Must have resolution data
        if 'resolution' not in market:
            return False
        
        return True
    
    def _analyze_market_historical(
        self, 
        market: Dict, 
        analysis_date: datetime
    ) -> Optional[ForecastedMarket]:
        """Analyze a market using AI with historical cutoff date"""
        try:
            # Create a copy of the market without resolution data
            market_copy = market.copy()
            
            # Remove future information that wouldn't have been available
            fields_to_remove = [
                'resolution', 'resolutionTime', 'resolutionProbability',
                'isResolved', 'resolvedDate'
            ]
            
            for field in fields_to_remove:
                market_copy.pop(field, None)
            
            # Set probability to what it was at market creation (if available)
            # Otherwise use a neutral 50%
            market_copy['probability'] = market.get('initialProbability', 0.5)
            
            # Analyze using the forecasting bot with the historical cutoff
            return self.bot.analyze_market_with_cutoff(market_copy, analysis_date)
            
        except Exception as e:
            logger.error(f"Error in historical analysis: {e}")
            return None
    
    def _simulate_trade(
        self,
        market: Dict,
        forecast: ForecastedMarket,
        trade_date: datetime,
        bet_amount: float
    ) -> Optional[HistoricalTrade]:
        """Simulate placing a trade on a historical market"""
        try:
            # Determine trade direction
            outcome = "YES" if forecast.forecast_difference > 0 else "NO"
            
            # Get entry price (market probability at time of trade)
            entry_price = market.get('initialProbability', 0.5)
            
            trade = HistoricalTrade(
                trade_id=f"{market['id']}_{trade_date.strftime('%Y%m%d')}",
                market_id=market['id'],
                question=market['question'],
                trade_date=trade_date,
                outcome=outcome,
                amount=bet_amount,
                entry_price=entry_price,
                ai_probability=forecast.ai_forecast.probability,
                confidence=forecast.ai_forecast.confidence_level,
                reasoning=forecast.reasoning
            )
            
            return trade
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
            return None
    
    def _calculate_trade_outcomes(self, trades: List[HistoricalTrade]):
        """Calculate outcomes for all trades based on market resolutions"""
        for trade in trades:
            try:
                # Find the original market to get resolution
                market = next(
                    (m for m in self.historical_markets if m['id'] == trade.market_id),
                    None
                )
                
                if not market or not market.get('isResolved'):
                    continue
                
                resolution = market.get('resolution')
                resolution_time = market.get('resolutionTime')
                
                if resolution_time:
                    trade.resolution_date = datetime.fromtimestamp(resolution_time / 1000)
                
                # Calculate payout based on resolution
                if resolution == 'YES':
                    trade.resolved_outcome = 'YES'
                    if trade.outcome == 'YES':
                        # Won the bet - payout based on entry price
                        trade.payout = trade.amount / trade.entry_price
                    else:
                        # Lost the bet
                        trade.payout = 0
                        
                elif resolution == 'NO':
                    trade.resolved_outcome = 'NO'
                    if trade.outcome == 'NO':
                        # Won the bet - payout based on (1 - entry_price)
                        trade.payout = trade.amount / (1 - trade.entry_price)
                    else:
                        # Lost the bet
                        trade.payout = 0
                        
                elif resolution in ['CANCEL', 'MKT']:
                    trade.resolved_outcome = 'CANCEL'
                    trade.payout = trade.amount  # Get money back
                
                # Calculate profit and ROI
                trade.profit = (trade.payout or 0) - trade.amount
                trade.roi = trade.profit / trade.amount if trade.amount > 0 else 0
                
            except Exception as e:
                logger.error(f"Error calculating outcome for trade {trade.trade_id}: {e}")
    
    def _calculate_backtest_result(
        self,
        start_date: datetime,
        end_date: datetime,
        initial_balance: float,
        final_balance: float,
        trades: List[HistoricalTrade],
        markets_analyzed: int,
        opportunities_found: int
    ) -> BacktestResult:
        """Calculate comprehensive backtest results"""
        
        # Basic metrics
        total_profit = final_balance - initial_balance
        total_roi = total_profit / initial_balance if initial_balance > 0 else 0
        
        # Trade statistics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if (t.profit or 0) > 0])
        losing_trades = len([t for t in trades if (t.profit or 0) < 0])
        cancelled_trades = len([t for t in trades if t.resolved_outcome == 'CANCEL'])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        avg_profit = total_profit / total_trades if total_trades > 0 else 0
        
        opportunity_rate = opportunities_found / markets_analyzed if markets_analyzed > 0 else 0
        
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
            cancelled_trades=cancelled_trades,
            win_rate=win_rate,
            avg_profit_per_trade=avg_profit,
            markets_analyzed=markets_analyzed,
            opportunities_found=opportunities_found,
            opportunity_rate=opportunity_rate,
            trades=trades
        )
    
    def _empty_backtest_result(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        initial_balance: float
    ) -> BacktestResult:
        """Return empty backtest result when no data available"""
        return BacktestResult(
            start_date=start_date,
            end_date=end_date,
            initial_balance=initial_balance,
            final_balance=initial_balance,
            total_profit=0,
            total_roi=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            cancelled_trades=0,
            win_rate=0,
            avg_profit_per_trade=0,
            markets_analyzed=0,
            opportunities_found=0,
            opportunity_rate=0,
            trades=[]
        )
    
    def generate_backtest_report(self, result: BacktestResult) -> Dict[str, Any]:
        """Generate a comprehensive backtest report"""
        
        # Performance summary
        performance = {
            "period": {
                "start_date": result.start_date.isoformat(),
                "end_date": result.end_date.isoformat(),
                "duration_days": (result.end_date - result.start_date).days
            },
            "returns": {
                "initial_balance": result.initial_balance,
                "final_balance": result.final_balance,
                "total_profit": result.total_profit,
                "total_roi": f"{result.total_roi:.2%}",
                "annualized_roi": f"{(result.total_roi * 365) / max((result.end_date - result.start_date).days, 1):.2%}"
            },
            "trading_stats": {
                "total_trades": result.total_trades,
                "winning_trades": result.winning_trades,
                "losing_trades": result.losing_trades,
                "cancelled_trades": result.cancelled_trades,
                "win_rate": f"{result.win_rate:.2%}",
                "avg_profit_per_trade": result.avg_profit_per_trade
            },
            "market_analysis": {
                "markets_analyzed": result.markets_analyzed,
                "opportunities_found": result.opportunities_found,
                "opportunity_rate": f"{result.opportunity_rate:.2%}"
            }
        }
        
        # Trade details
        if result.trades:
            trades_by_outcome = {}
            for trade in result.trades:
                outcome = trade.resolved_outcome or "PENDING"
                if outcome not in trades_by_outcome:
                    trades_by_outcome[outcome] = []
                trades_by_outcome[outcome].append({
                    "question": trade.question,
                    "trade_date": trade.trade_date.isoformat(),
                    "outcome": trade.outcome,
                    "amount": trade.amount,
                    "profit": trade.profit,
                    "roi": f"{trade.roi:.2%}" if trade.roi else "N/A",
                    "confidence": trade.confidence
                })
            
            performance["trades_by_outcome"] = trades_by_outcome
            
            # Best and worst trades
            profitable_trades = [t for t in result.trades if (t.profit or 0) > 0]
            losing_trades = [t for t in result.trades if (t.profit or 0) < 0]
            
            if profitable_trades:
                best_trade = max(profitable_trades, key=lambda t: t.profit or 0)
                performance["best_trade"] = {
                    "question": best_trade.question,
                    "profit": best_trade.profit,
                    "roi": f"{best_trade.roi:.2%}" if best_trade.roi else "N/A"
                }
            
            if losing_trades:
                worst_trade = min(losing_trades, key=lambda t: t.profit or 0)
                performance["worst_trade"] = {
                    "question": worst_trade.question,
                    "profit": worst_trade.profit,
                    "roi": f"{worst_trade.roi:.2%}" if worst_trade.roi else "N/A"
                }
        
        return performance
    
    def save_backtest_results(
        self, 
        result: BacktestResult, 
        filepath: str,
        include_trades: bool = True
    ):
        """Save backtest results to file"""
        
        # Convert to dictionary
        data = asdict(result)
        
        # Convert datetime objects to strings
        data['start_date'] = result.start_date.isoformat()
        data['end_date'] = result.end_date.isoformat()
        
        if include_trades and result.trades:
            trades_data = []
            for trade in result.trades:
                trade_dict = asdict(trade)
                trade_dict['trade_date'] = trade.trade_date.isoformat()
                if trade.resolution_date:
                    trade_dict['resolution_date'] = trade.resolution_date.isoformat()
                trades_data.append(trade_dict)
            data['trades'] = trades_data
        
        # Add generation metadata
        data['_metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Backtest results saved to {filepath}")


# Extension to the main bot class
class ManifoldForecastingBotWithBacktest(ManifoldForecastingBot):
    """Extended bot with backtesting capabilities"""
    
    def analyze_market_with_cutoff(
        self, 
        market: Dict[str, Any], 
        cutoff_date: datetime
    ) -> Optional[ForecastedMarket]:
        """Analyze a market with a specific knowledge cutoff date"""
        try:
            # Use the forecaster with the specific cutoff date
            ai_forecast = self.forecaster.forecast_with_google_news(
                question=market.get('question', ''),
                background=market.get('description', ''),
                cutoff_date=cutoff_date,
                time_horizon="1 year",
                is_benchmark=True  # Use benchmark mode for historical analysis
            )
            
            # Extract current probability (or use neutral if not available)
            current_prob = market.get('probability', 0.5)
            
            # Calculate forecast difference
            forecast_diff = ai_forecast.probability - current_prob
            
            # Determine action with historical context
            action, bet_amount, reasoning = self._determine_action(
                ai_forecast, current_prob, forecast_diff, market
            )
            
            return ForecastedMarket(
                market_id=market['id'],
                question=market['question'],
                current_prob=current_prob,
                ai_forecast=ai_forecast,
                forecast_difference=forecast_diff,
                confidence_score=self._calculate_confidence_score(ai_forecast),
                recommended_action=action,
                bet_amount=bet_amount,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market with cutoff: {e}")
            return None
