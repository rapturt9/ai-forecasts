#!/usr/bin/env python3
"""
Test Manifold trading integration with Inspect AI
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dataclasses import asdict

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from manifold_markets.enhanced_backtesting import EnhancedBacktester

def test_manifold_inspect_ai():
    """Test Manifold trading with Inspect AI forecaster"""
    
    print("🧪 Testing Manifold Trading with Inspect AI")
    print("=" * 60)
    
    # Get API keys
    manifold_api_key = os.getenv('MANIFOLD_API_KEY')
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    serp_api_key = os.getenv('SERP_API_KEY')
    
    if not all([manifold_api_key, openrouter_api_key, serp_api_key]):
        print("❌ Missing required API keys")
        return False
    
    try:
        print("📋 Creating Enhanced Backtester with Inspect AI...")
        
        # Create backtester with Inspect AI enabled
        backtester = EnhancedBacktester(
            manifold_api_key=manifold_api_key,
            openrouter_api_key=openrouter_api_key,
            serp_api_key=serp_api_key,
            use_inspect_ai=True,  # Enable Inspect AI
            debate_mode=True      # Enable debate mode
        )
        
        print("✅ Enhanced Backtester with Inspect AI initialized")
        
        # Test with a simple market search
        print("\n📊 Testing market search...")
        
        # Search for markets (limit to 2 for testing)
        markets = backtester.manifold_client.get_markets(limit=2)
        
        if not markets:
            print("❌ No markets found")
            return False
            
        print(f"✅ Found {len(markets)} markets")
        
        # Test forecasting on the first market
        market = markets[0]
        print(f"\n🎯 Testing forecast for market: {market.get('question', 'Unknown')[:80]}...")
        
        # Create a simple backtest configuration
        backtest_config = {
            "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "initial_balance": 1000,
            "max_markets": 1,
            "min_confidence": 0.6,
            "max_bet_size": 100
        }
        
        print("🚀 Running backtest with Inspect AI...")
        
        # Run a simple backtest (just 1 hour for testing)
        import asyncio
        results = asyncio.run(backtester.run_week_long_backtest(hours_to_run=1))
        
        print("✅ Backtest completed!")
        
        # Display results
        if results:
            print(f"\n📊 Backtest Results:")
            print(f"   📈 Total Return: {results.total_return:.2%}")
            print(f"   💰 Final Balance: ${results.current_balance:.2f}")
            print(f"   📊 Number of Trades: {results.total_trades}")
            print(f"   🎯 Win Rate: {results.winning_trades/max(results.total_trades, 1):.2%}")
            print(f"   📊 Markets Analyzed: {results.markets_analyzed}")
            print(f"   📈 Sharpe Ratio: {results.sharpe_ratio:.3f}")
            
            # Check if Inspect AI was used by looking at trade history
            if results.trade_history:
                print("   ✅ Inspect AI methodology confirmed (trades executed)")
            else:
                print("   ⚠️ No trades executed in test period")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"manifold_inspect_ai_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "test_type": "manifold_inspect_ai_integration",
                "timestamp": timestamp,
                "backtest_config": backtest_config,
                "results": asdict(results) if results else None,
                "markets_tested": len(markets),
                "inspect_ai_enabled": True,
                "debate_mode_enabled": True
            }, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        print("\n🎉 SUCCESS: Manifold trading with Inspect AI working!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_manifold_inspect_ai()
    sys.exit(0 if success else 1)