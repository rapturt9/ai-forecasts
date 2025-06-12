"""
Simplified Backtesting module for Manifold Markets Trading Bot
Uses mock data for demonstration purposes
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import random
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Results from a backtesting run"""
    start_date: datetime
    end_date: datetime
    initial_balance: float
    final_balance: float
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    kelly_utilization: float
    trades: List[Dict]

class SimpleBacktester:
    """Simplified backtester using mock historical data"""
    
    def __init__(self, initial_balance: float = 1000.0):
        self.initial_balance = initial_balance
        self.logger = logging.getLogger(__name__)
        
    def generate_mock_markets(self, start_date: datetime, end_date: datetime, num_markets: int = 50) -> List[Dict]:
        """Generate mock historical markets for backtesting"""
        markets = []
        current_date = start_date
        
        for i in range(num_markets):
            # Generate realistic market data
            market = {
                'id': f'mock_market_{i}',
                'question': f'Mock prediction market question {i}',
                'created_date': current_date,
                'close_date': current_date + timedelta(days=random.randint(1, 7)),
                'initial_prob': random.uniform(0.2, 0.8),
                'final_prob': random.uniform(0.1, 0.9),
                'resolved': random.choice([True, False]),
                'resolution': random.choice(['YES', 'NO']) if random.choice([True, False]) else None,
                'volume': random.uniform(100, 10000),
                'liquidity': random.uniform(50, 1000)
            }
            markets.append(market)
            current_date += timedelta(hours=random.randint(1, 24))
            
        return markets
    
    def simulate_prediction(self, market: Dict) -> Dict:
        """Simulate AI prediction for a market"""
        # Mock prediction with some realistic patterns
        base_prob = market['initial_prob']
        
        # Add some noise and bias
        predicted_prob = base_prob + random.gauss(0, 0.1)
        predicted_prob = max(0.05, min(0.95, predicted_prob))
        
        confidence = random.uniform(0.6, 0.9)
        
        # Determine action based on edge
        edge = abs(predicted_prob - base_prob)
        action = 'BUY_YES' if predicted_prob > base_prob + 0.05 else 'BUY_NO' if predicted_prob < base_prob - 0.05 else 'HOLD'
        
        return {
            'predicted_probability': predicted_prob,
            'confidence': confidence,
            'action': action,
            'edge': edge,
            'reasoning': f"Mock AI analysis suggests {predicted_prob:.2f} probability based on market conditions"
        }
    
    def calculate_trade_outcome(self, market: Dict, prediction: Dict, bet_amount: float) -> Dict:
        """Calculate the outcome of a trade"""
        if prediction['action'] == 'HOLD':
            return {
                'profit': 0,
                'success': None,
                'bet_amount': 0
            }
        
        # Simulate trade execution
        buy_yes = prediction['action'] == 'BUY_YES'
        
        # Determine if trade was successful based on resolution
        if market['resolution'] is None:
            # Market didn't resolve - assume small loss
            profit = -bet_amount * 0.1
            success = False
        else:
            market_resolved_yes = market['resolution'] == 'YES'
            trade_correct = (buy_yes and market_resolved_yes) or (not buy_yes and not market_resolved_yes)
            
            if trade_correct:
                # Calculate profit based on odds
                initial_prob = market['initial_prob']
                if buy_yes:
                    odds = 1 / initial_prob
                else:
                    odds = 1 / (1 - initial_prob)
                profit = bet_amount * (odds - 1) * 0.8  # 80% of theoretical profit
                success = True
            else:
                profit = -bet_amount
                success = False
        
        return {
            'profit': profit,
            'success': success,
            'bet_amount': bet_amount
        }
    
    def run_backtest(self, start_date: datetime, end_date: datetime, max_markets: int = 50) -> BacktestResult:
        """Run a simplified backtest"""
        self.logger.info(f"🔄 Starting backtest from {start_date.date()} to {end_date.date()}")
        
        # Generate mock markets
        markets = self.generate_mock_markets(start_date, end_date, max_markets)
        
        balance = self.initial_balance
        trades = []
        daily_balances = [balance]
        
        for market in markets:
            # Generate prediction
            prediction = self.simulate_prediction(market)
            
            if prediction['action'] != 'HOLD':
                # Calculate bet size (simple fixed percentage)
                bet_amount = min(balance * 0.05, 100)  # 5% of balance or $100 max
                
                if bet_amount >= 10:  # Minimum bet size
                    # Execute trade
                    outcome = self.calculate_trade_outcome(market, prediction, bet_amount)
                    balance += outcome['profit']
                    
                    trade_record = {
                        'market_id': market['id'],
                        'question': market['question'],
                        'date': market['created_date'],
                        'action': prediction['action'],
                        'predicted_prob': prediction['predicted_probability'],
                        'confidence': prediction['confidence'],
                        'bet_amount': outcome['bet_amount'],
                        'profit': outcome['profit'],
                        'success': outcome['success'],
                        'balance_after': balance
                    }
                    trades.append(trade_record)
                    daily_balances.append(balance)
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t['success'])
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        total_return = (balance - self.initial_balance) / self.initial_balance
        
        # Calculate max drawdown
        peak = self.initial_balance
        max_drawdown = 0
        for balance_point in daily_balances:
            if balance_point > peak:
                peak = balance_point
            drawdown = (peak - balance_point) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate Sharpe ratio (simplified)
        if len(daily_balances) > 1:
            returns = np.diff(daily_balances) / daily_balances[:-1]
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        result = BacktestResult(
            start_date=start_date,
            end_date=end_date,
            initial_balance=self.initial_balance,
            final_balance=balance,
            total_return=total_return,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            kelly_utilization=0.15,  # Mock value
            trades=trades
        )
        
        self.logger.info(f"✅ Backtest completed: {total_return:.1%} return, {win_rate:.1%} win rate")
        return result