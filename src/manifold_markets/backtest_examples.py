#!/usr/bin/env python3
"""
Backtesting Examples for Manifold Markets Forecasting Bot
Demonstrates how to test AI strategies on historical market data
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from manifold_markets.backtesting import ManifoldBacktester, ManifoldForecastingBotWithBacktest


def example_download_historical_data():
    """Example: Download historical market data for backtesting"""
    print("📥 Example 1: Downloading Historical Data")
    print("=" * 50)
    
    # Initialize bot
    bot = ManifoldForecastingBotWithBacktest(
        manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
        openrouter_api_key="dummy"  # Not needed for downloading
    )
    
    # Set date range (last 3 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"Downloading markets from {start_date.date()} to {end_date.date()}")
    
    # Initialize backtester
    backtester = ManifoldBacktester(bot)
    
    # Download data
    data_file = "historical_markets_sample.json"
    markets = backtester.download_historical_data(
        start_date=start_date,
        end_date=end_date,
        save_path=data_file,
        limit=100  # Limit for demo
    )
    
    if markets:
        print(f"✅ Downloaded {len(markets)} markets to {data_file}")
        
        # Show statistics
        resolved_markets = [m for m in markets if m.get('isResolved')]
        binary_markets = [m for m in markets if m.get('outcomeType') == 'BINARY']
        
        print(f"📊 Market Statistics:")
        print(f"  • Total markets: {len(markets)}")
        print(f"  • Resolved markets: {len(resolved_markets)}")
        print(f"  • Binary markets: {len(binary_markets)}")
        print(f"  • Testable markets: {len([m for m in resolved_markets if m.get('outcomeType') == 'BINARY'])}")
        
        return data_file
    else:
        print("❌ Failed to download data")
        return None


def example_simple_backtest():
    """Example: Run a simple backtest on historical data"""
    print("\n🕰️  Example 2: Simple Backtest")
    print("=" * 50)
    
    # Check if we have historical data
    data_file = "historical_markets_sample.json"
    if not Path(data_file).exists():
        print(f"❌ No historical data found at {data_file}")
        print("   Run example_download_historical_data() first")
        return
    
    # Initialize bot with backtesting capabilities
    bot = ManifoldForecastingBotWithBacktest(
        manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        serp_api_key=os.getenv("SERP_API_KEY"),
        default_bet_amount=20.0,
        confidence_threshold=0.20  # Conservative threshold
    )
    
    # Initialize backtester with historical data
    backtester = ManifoldBacktester(bot, data_file)
    
    # Set backtest period (last month)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"Running backtest from {start_date.date()} to {end_date.date()}")
    print("⏳ This may take a few minutes as AI analyzes each market...")
    
    # Run backtest
    result = backtester.run_backtest(
        start_date=start_date,
        end_date=end_date,
        initial_balance=1000.0,
        confidence_threshold=0.20,
        min_confidence="medium",
        max_bet_per_market=50.0,
        max_daily_bets=150.0
    )
    
    # Display results
    print(f"\n📈 Backtest Results:")
    print(f"  • Period: {result.start_date.date()} to {result.end_date.date()}")
    print(f"  • Initial balance: ${result.initial_balance:.2f}")
    print(f"  • Final balance: ${result.final_balance:.2f}")
    print(f"  • Total profit: ${result.total_profit:.2f}")
    print(f"  • ROI: {result.total_roi:.2%}")
    print(f"  • Markets analyzed: {result.markets_analyzed}")
    print(f"  • Trades executed: {result.total_trades}")
    print(f"  • Win rate: {result.win_rate:.2%}")
    
    # Save results
    results_file = "backtest_results_simple.json"
    backtester.save_backtest_results(result, results_file)
    print(f"\n💾 Detailed results saved to {results_file}")
    
    return result


def example_strategy_comparison():
    """Example: Compare different strategy parameters"""
    print("\n📊 Example 3: Strategy Comparison")
    print("=" * 50)
    
    data_file = "historical_markets_sample.json"
    if not Path(data_file).exists():
        print(f"❌ No historical data found")
        return
    
    # Test different strategies
    strategies = [
        {"name": "Conservative", "threshold": 0.25, "confidence": "high", "max_bet": 30},
        {"name": "Moderate", "threshold": 0.20, "confidence": "medium", "max_bet": 40},
        {"name": "Aggressive", "threshold": 0.15, "confidence": "medium", "max_bet": 60},
    ]
    
    # Set test period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"Testing strategies from {start_date.date()} to {end_date.date()}")
    
    results = []
    
    for strategy in strategies:
        print(f"\n🧪 Testing {strategy['name']} strategy...")
        
        # Initialize bot for this strategy
        bot = ManifoldForecastingBotWithBacktest(
            manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            serp_api_key=os.getenv("SERP_API_KEY"),
            default_bet_amount=strategy["max_bet"] / 2,
            confidence_threshold=strategy["threshold"]
        )
        
        backtester = ManifoldBacktester(bot, data_file)
        
        # Run backtest
        result = backtester.run_backtest(
            start_date=start_date,
            end_date=end_date,
            initial_balance=1000.0,
            confidence_threshold=strategy["threshold"],
            min_confidence=strategy["confidence"],
            max_bet_per_market=strategy["max_bet"],
            max_daily_bets=200.0
        )
        
        result.strategy_name = strategy["name"]
        results.append(result)
        
        print(f"  ROI: {result.total_roi:.2%}, Trades: {result.total_trades}, Win Rate: {result.win_rate:.2%}")
    
    # Compare results
    print(f"\n🏆 Strategy Comparison:")
    print(f"{'Strategy':<12} {'ROI':<8} {'Trades':<8} {'Win Rate':<10} {'Profit':<10}")
    print("-" * 50)
    
    for result in results:
        print(f"{result.strategy_name:<12} {result.total_roi:>6.1%} {result.total_trades:>7} {result.win_rate:>8.1%} ${result.total_profit:>8.2f}")
    
    # Find best strategy
    best_strategy = max(results, key=lambda r: r.total_roi)
    print(f"\n🥇 Best performing strategy: {best_strategy.strategy_name}")
    print(f"   ROI: {best_strategy.total_roi:.2%}, Profit: ${best_strategy.total_profit:.2f}")


def example_confidence_analysis():
    """Example: Analyze performance by AI confidence levels"""
    print("\n🎯 Example 4: Confidence Level Analysis")
    print("=" * 50)
    
    data_file = "historical_markets_sample.json"
    if not Path(data_file).exists():
        print(f"❌ No historical data found")
        return
    
    # Run backtest with all confidence levels
    bot = ManifoldForecastingBotWithBacktest(
        manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        serp_api_key=os.getenv("SERP_API_KEY"),
        confidence_threshold=0.15
    )
    
    backtester = ManifoldBacktester(bot, data_file)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"Analyzing confidence levels from {start_date.date()} to {end_date.date()}")
    
    result = backtester.run_backtest(
        start_date=start_date,
        end_date=end_date,
        initial_balance=1000.0,
        confidence_threshold=0.15,
        min_confidence="low",  # Include all confidence levels
        max_bet_per_market=40.0
    )
    
    if result.trades:
        # Analyze by confidence level
        confidence_stats = {}
        for trade in result.trades:
            conf = trade.confidence
            if conf not in confidence_stats:
                confidence_stats[conf] = {
                    "trades": 0, "wins": 0, "losses": 0, 
                    "total_profit": 0, "total_bet": 0
                }
            
            stats = confidence_stats[conf]
            stats["trades"] += 1
            stats["total_bet"] += trade.amount
            
            if trade.profit is not None:
                stats["total_profit"] += trade.profit
                if trade.profit > 0:
                    stats["wins"] += 1
                elif trade.profit < 0:
                    stats["losses"] += 1
        
        print(f"\n📊 Performance by Confidence Level:")
        print(f"{'Level':<8} {'Trades':<8} {'Win Rate':<10} {'Avg Profit':<12} {'Total ROI':<10}")
        print("-" * 55)
        
        for conf in ["high", "medium", "low"]:
            if conf in confidence_stats:
                stats = confidence_stats[conf]
                win_rate = stats["wins"] / stats["trades"] if stats["trades"] > 0 else 0
                avg_profit = stats["total_profit"] / stats["trades"] if stats["trades"] > 0 else 0
                roi = stats["total_profit"] / stats["total_bet"] if stats["total_bet"] > 0 else 0
                
                print(f"{conf:<8} {stats['trades']:>7} {win_rate:>8.1%} ${avg_profit:>10.2f} {roi:>8.1%}")


def example_time_series_analysis():
    """Example: Analyze performance over time"""
    print("\n📈 Example 5: Time Series Analysis")
    print("=" * 50)
    
    data_file = "historical_markets_sample.json"
    if not Path(data_file).exists():
        print(f"❌ No historical data found")
        return
    
    # Run backtest and analyze performance over time
    bot = ManifoldForecastingBotWithBacktest(
        manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        serp_api_key=os.getenv("SERP_API_KEY")
    )
    
    backtester = ManifoldBacktester(bot, data_file)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)  # 2 months
    
    result = backtester.run_backtest(
        start_date=start_date,
        end_date=end_date,
        initial_balance=1000.0,
        confidence_threshold=0.18,
        min_confidence="medium"
    )
    
    if result.trades:
        # Group trades by week
        weekly_performance = {}
        running_balance = result.initial_balance
        
        for trade in sorted(result.trades, key=lambda t: t.trade_date):
            week_key = trade.trade_date.strftime("%Y-W%U")
            
            if week_key not in weekly_performance:
                weekly_performance[week_key] = {
                    "trades": 0, "profit": 0, "balance": running_balance
                }
            
            weekly_performance[week_key]["trades"] += 1
            weekly_performance[week_key]["profit"] += (trade.profit or 0)
            running_balance += (trade.profit or 0)
            weekly_performance[week_key]["balance"] = running_balance
        
        print(f"\n📅 Weekly Performance:")
        print(f"{'Week':<10} {'Trades':<8} {'Profit':<10} {'Balance':<10} {'Weekly ROI':<12}")
        print("-" * 55)
        
        prev_balance = result.initial_balance
        for week, perf in weekly_performance.items():
            weekly_roi = (perf["balance"] - prev_balance) / prev_balance if prev_balance > 0 else 0
            print(f"{week:<10} {perf['trades']:>7} ${perf['profit']:>8.2f} ${perf['balance']:>8.2f} {weekly_roi:>10.1%}")
            prev_balance = perf["balance"]


def example_market_category_analysis():
    """Example: Analyze performance by market categories"""
    print("\n🏷️  Example 6: Market Category Analysis")
    print("=" * 50)
    
    data_file = "historical_markets_sample.json"
    if not Path(data_file).exists():
        print(f"❌ No historical data found")
        return
    
    # Load historical data to analyze categories
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    markets = data.get('markets', [])
    
    # Categorize markets by keywords in questions
    categories = {
        "AI/Tech": ["AI", "artificial intelligence", "technology", "tech", "software", "computer"],
        "Politics": ["election", "president", "political", "vote", "republican", "democrat"],
        "Economics": ["market", "economy", "GDP", "inflation", "stock", "economic"],
        "Sports": ["game", "team", "sport", "championship", "match", "tournament"],
        "Science": ["research", "study", "climate", "space", "medical", "health"]
    }
    
    # Categorize markets
    categorized_markets = {cat: [] for cat in categories}
    categorized_markets["Other"] = []
    
    for market in markets:
        question = market.get('question', '').lower()
        categorized = False
        
        for category, keywords in categories.items():
            if any(keyword.lower() in question for keyword in keywords):
                categorized_markets[category].append(market)
                categorized = True
                break
        
        if not categorized:
            categorized_markets["Other"].append(market)
    
    print(f"📊 Market Categories:")
    for category, category_markets in categorized_markets.items():
        resolved = len([m for m in category_markets if m.get('isResolved')])
        print(f"  • {category}: {len(category_markets)} markets ({resolved} resolved)")
    
    # Note: Full category backtesting would require running the bot on each category
    print(f"\n💡 To test performance by category, run separate backtests on each category's markets")


def main():
    """Run all backtesting examples"""
    print("🕰️  Manifold Markets Backtesting Examples")
    print("=" * 60)
    
    # Check for required environment variables
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("   This is required for AI forecasting")
        return
    
    manifold_key = os.getenv("MANIFOLD_API_KEY")
    if not manifold_key:
        print("⚠️  MANIFOLD_API_KEY not set - using read-only mode")
    
    try:
        # Run examples
        print("\n🚀 Starting backtesting examples...")
        
        # 1. Download historical data (if needed)
        data_file = example_download_historical_data()
        
        if data_file and Path(data_file).exists():
            # 2. Simple backtest
            example_simple_backtest()
            
            # 3. Strategy comparison
            example_strategy_comparison()
            
            # 4. Confidence analysis
            example_confidence_analysis()
            
            # 5. Time series analysis
            example_time_series_analysis()
            
            # 6. Market category analysis
            example_market_category_analysis()
        
        print(f"\n✅ All backtesting examples completed!")
        print(f"\nNext steps:")
        print(f"  • Use 'python cli.py backtest' for custom backtests")
        print(f"  • Try different confidence thresholds and bet sizes")
        print(f"  • Download more historical data for longer backtests")
        print(f"  • Analyze specific market categories or time periods")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
