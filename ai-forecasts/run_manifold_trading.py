#!/usr/bin/env python3
"""
Manifold Trading & Backtesting Runner - Uses Market Agent with Manifold API
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_forecasts.agents.market_agent import MarketAgent
from manifold_markets.client import ManifoldMarketsClient
from manifold_markets.simple_backtesting import SimpleBacktester
from manifold_markets.kelly_criterion import KellyCriterionCalculator
from ai_forecasts.utils.agent_logger import agent_logger

class ManifoldTradingSystem:
    """Complete Manifold Markets trading system with backtesting"""
    
    def __init__(self, openrouter_api_key: str, manifold_api_key: str = None, serp_api_key: str = None):
        self.openrouter_api_key = openrouter_api_key
        self.manifold_api_key = manifold_api_key
        self.serp_api_key = serp_api_key
        self.logger = agent_logger
        
        # Initialize components
        self.market_agent = MarketAgent(
            openrouter_api_key=openrouter_api_key,
            manifold_api_key=manifold_api_key,
            serp_api_key=serp_api_key
        )
        
        if manifold_api_key:
            self.manifold_client = ManifoldMarketsClient(api_key=manifold_api_key)
        else:
            self.manifold_client = None
            self.logger.warning("No Manifold API key provided - using demo mode")
    
    async def run_live_trading_demo(self, max_markets: int = 5):
        """Run live trading demonstration"""
        self.logger.info(f"🔴 Starting Live Trading Demo (max_markets={max_markets})")
        
        if not self.manifold_client:
            self.logger.error("❌ Manifold API key required for live trading")
            return
        
        try:
            # Get active markets
            markets = self.manifold_client.get_markets(limit=max_markets)
            self.logger.info(f"📊 Found {len(markets)} markets")
            
            trading_results = []
            
            for i, market in enumerate(markets[:max_markets]):
                self.logger.info(f"🎯 Analyzing market {i+1}/{max_markets}: {market['question'][:80]}...")
                
                try:
                    # Get trading decision
                    decision = await self.market_agent.analyze_market_async(market)
                    
                    if decision.recommended_action != "HOLD":
                        self.logger.info(f"💡 Recommendation: {decision.recommended_action}")
                        self.logger.info(f"   Edge: {decision.edge:.1%}")
                        self.logger.info(f"   Position Size: {decision.position_size:.1%}")
                        self.logger.info(f"   Confidence: {decision.confidence}")
                        
                        # In demo mode, just log the decision
                        trading_results.append({
                            'market_id': market['id'],
                            'question': market['question'],
                            'action': decision.recommended_action,
                            'edge': decision.edge,
                            'position_size': decision.position_size,
                            'confidence': decision.confidence,
                            'reasoning': decision.reasoning[:200] + "..."
                        })
                    else:
                        self.logger.info("⏸️  Recommendation: HOLD (no edge detected)")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error analyzing market: {e}")
            
            self.logger.info(f"✅ Live trading demo complete. Found {len(trading_results)} trading opportunities")
            return trading_results
            
        except Exception as e:
            self.logger.error(f"❌ Error in live trading demo: {e}")
            return []
    
    def run_backtesting(self, start_date: str, end_date: str, initial_balance: float = 1000.0):
        """Run backtesting between two time periods"""
        self.logger.info(f"📊 Starting Backtesting ({start_date} to {end_date})")
        
        try:
            # Parse dates
            from datetime import datetime
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Initialize simplified backtester
            backtester = SimpleBacktester(initial_balance=initial_balance)
            
            # Run backtest
            results = backtester.run_backtest(start_dt, end_dt, max_markets=30)
            
            # Display results
            self.logger.info("🎯 Backtesting Results:")
            self.logger.info(f"   Initial Balance: ${results.initial_balance:.2f}")
            self.logger.info(f"   Final Balance: ${results.final_balance:.2f}")
            self.logger.info(f"   Total Return: {results.total_return:.1%}")
            self.logger.info(f"   Total Trades: {results.total_trades}")
            self.logger.info(f"   Win Rate: {results.win_rate:.1%}")
            self.logger.info(f"   Sharpe Ratio: {results.sharpe_ratio:.2f}")
            self.logger.info(f"   Max Drawdown: {results.max_drawdown:.1%}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error in backtesting: {e}")
            return None
    
    def demonstrate_kelly_criterion(self):
        """Demonstrate Kelly Criterion calculations"""
        self.logger.info("🎯 Kelly Criterion Demonstration")
        
        kelly_calc = KellyCriterionCalculator(max_kelly_fraction=0.25, min_edge=0.05)
        
        # Example scenarios
        scenarios = [
            {"forecast": 0.7, "market": 0.6, "description": "Strong bullish signal"},
            {"forecast": 0.3, "market": 0.45, "description": "Bearish contrarian play"},
            {"forecast": 0.55, "market": 0.52, "description": "Slight edge"},
            {"forecast": 0.8, "market": 0.85, "description": "Overpriced market"},
        ]
        
        for scenario in scenarios:
            # Calculate edge manually
            edge = abs(scenario["forecast"] - scenario["market"])
            
            # Calculate Kelly fraction
            kelly_fraction = kelly_calc.calculate_kelly_fraction(
                ai_probability=scenario["forecast"],
                market_probability=scenario["market"],
                outcome="YES"
            )
            
            # Calculate position size (simple percentage of balance)
            position_size = kelly_fraction * 1000  # 1000 is the balance
            
            self.logger.info(f"📈 {scenario['description']}:")
            self.logger.info(f"   Forecast: {scenario['forecast']:.1%}, Market: {scenario['market']:.1%}")
            self.logger.info(f"   Edge: {edge:.1%}")
            self.logger.info(f"   Kelly Fraction: {kelly_fraction:.1%}")
            self.logger.info(f"   Position Size: ${position_size:.2f}")
            self.logger.info("")

async def main():
    """Main function to run Manifold trading system"""
    # Get API keys
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    manifold_api_key = os.getenv('MANIFOLD_API_KEY')
    serp_api_key = os.getenv('SERP_API_KEY')
    
    if not openrouter_api_key:
        print("❌ OPENROUTER_API_KEY environment variable required")
        return
    
    # Create trading system
    trading_system = ManifoldTradingSystem(
        openrouter_api_key=openrouter_api_key,
        manifold_api_key=manifold_api_key,
        serp_api_key=serp_api_key
    )
    
    print("🤖 Manifold Markets Trading System")
    print("=" * 50)
    
    # Demonstrate Kelly Criterion
    trading_system.demonstrate_kelly_criterion()
    
    # Run live trading demo
    if manifold_api_key:
        await trading_system.run_live_trading_demo(max_markets=3)
    else:
        print("⚠️  No Manifold API key - skipping live trading demo")
    
    # Run backtesting demo
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    trading_system.run_backtesting(
        start_date=start_date,
        end_date=end_date,
        initial_balance=1000.0
    )

if __name__ == "__main__":
    asyncio.run(main())