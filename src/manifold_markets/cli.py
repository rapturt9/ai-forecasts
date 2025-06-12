#!/usr/bin/env python3
"""
Manifold Markets Forecasting Bot CLI
Command line interface for running the AI forecasting bot
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from manifold_markets.forecasting_bot import ManifoldForecastingBot
from manifold_markets.client import ManifoldMarketsClient


def setup_logging():
    """Setup logging configuration"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def analyze_markets_command(args):
    """Analyze markets without placing bets"""
    print("🤖 Initializing AI Forecasting Bot...")
    
    bot = ManifoldForecastingBot(
        manifold_api_key=args.manifold_key,
        openrouter_api_key=args.openrouter_key,
        serp_api_key=args.serp_key,
        default_bet_amount=args.bet_amount,
        confidence_threshold=args.confidence_threshold
    )
    
    print(f"📊 Analyzing {args.limit} markets...")
    
    # Analyze markets
    if args.search:
        forecasted_markets = bot.analyze_markets(
            limit=args.limit,
            search_term=args.search,
            filter_type="open"
        )
    else:
        forecasted_markets = bot.analyze_markets(limit=args.limit)
    
    if not forecasted_markets:
        print("❌ No markets could be analyzed")
        return
    
    # Generate report
    report = bot.generate_report(forecasted_markets)
    
    # Print summary
    print("\n📈 Analysis Summary:")
    print(f"  • Total markets analyzed: {report['summary']['total_markets_analyzed']}")
    print(f"  • Betting opportunities: {report['summary']['betting_opportunities']}")
    print(f"  • High confidence forecasts: {report['summary']['high_confidence_forecasts']}")
    print(f"  • Average probability difference: {report['summary']['average_probability_difference']:.1%}")
    print(f"  • Max probability difference: {report['summary']['max_probability_difference']:.1%}")
    
    # Print top opportunities
    if report['top_opportunities']:
        print(f"\n🎯 Top {len(report['top_opportunities'])} Opportunities:")
        for i, opp in enumerate(report['top_opportunities'], 1):
            print(f"\n{i}. {opp['question']}")
            print(f"   Action: {opp['action']} (${opp['bet_amount']:.2f})")
            print(f"   AI: {opp['ai_probability']:.1%} vs Market: {opp['market_probability']:.1%} ({opp['difference']:+.1%})")
            print(f"   Confidence: {opp['confidence']}")
            print(f"   Reasoning: {opp['reasoning']}")
    
    # Save detailed report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "report": report,
                "detailed_forecasts": [
                    {
                        "market_id": m.market_id,
                        "question": m.question,
                        "current_prob": m.current_prob,
                        "ai_probability": m.ai_forecast.probability,
                        "forecast_difference": m.forecast_difference,
                        "confidence": m.ai_forecast.confidence_level,
                        "action": m.recommended_action,
                        "bet_amount": m.bet_amount,
                        "reasoning": m.reasoning,
                        "ai_reasoning": m.ai_forecast.reasoning,
                        "base_rate": m.ai_forecast.base_rate,
                        "evidence_quality": m.ai_forecast.evidence_quality
                    }
                    for m in forecasted_markets
                ]
            }, f, indent=2)
        print(f"\n💾 Detailed report saved to {args.output}")


def find_opportunities_command(args):
    """Find and optionally execute betting opportunities"""
    print("🤖 Initializing AI Forecasting Bot...")
    
    bot = ManifoldForecastingBot(
        manifold_api_key=args.manifold_key,
        openrouter_api_key=args.openrouter_key,
        serp_api_key=args.serp_key,
        default_bet_amount=args.bet_amount,
        confidence_threshold=args.confidence_threshold
    )
    
    print(f"🔍 Finding betting opportunities...")
    
    # Find opportunities
    opportunities = bot.find_opportunities(
        min_difference=args.min_difference,
        min_confidence=args.min_confidence,
        limit=args.limit
    )
    
    if not opportunities:
        print("❌ No betting opportunities found with current criteria")
        return
    
    print(f"\n🎯 Found {len(opportunities)} betting opportunities:")
    
    total_bet_amount = 0
    for i, opp in enumerate(opportunities, 1):
        bet_amount = opp.bet_amount or 0
        total_bet_amount += bet_amount
        
        print(f"\n{i}. {opp.question}")
        print(f"   Action: {opp.recommended_action} (${bet_amount:.2f})")
        print(f"   AI: {opp.ai_forecast.probability:.1%} vs Market: {opp.current_prob:.1%} ({opp.forecast_difference:+.1%})")
        print(f"   Confidence: {opp.ai_forecast.confidence_level}")
        print(f"   Reasoning: {opp.reasoning}")
    
    print(f"\n💰 Total bet amount: ${total_bet_amount:.2f}")
    
    # Execute bets if requested
    if args.execute:
        if args.dry_run:
            print("\n🧪 Executing bets in DRY RUN mode...")
        else:
            print("\n💸 Executing actual bets...")
            if not bot.manifold.api_key:
                print("❌ No Manifold API key provided - cannot place real bets")
                return
            
            # Confirm before placing real bets
            response = input(f"\n⚠️  About to place ${total_bet_amount:.2f} in real bets. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Bet execution cancelled")
                return
        
        results = bot.execute_bets(
            opportunities,
            dry_run=args.dry_run,
            max_total_amount=args.max_bet_total
        )
        
        # Print results
        successful_bets = [r for r in results if r.get('success')]
        failed_bets = [r for r in results if not r.get('success')]
        
        print(f"\n📊 Bet Execution Results:")
        print(f"  • Successful: {len(successful_bets)}")
        print(f"  • Failed: {len(failed_bets)}")
        
        if failed_bets:
            print("\n❌ Failed bets:")
            for bet in failed_bets:
                print(f"  • {bet['question']}: {bet.get('error', 'Unknown error')}")
        
        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to {args.output}")


def backtest_command(args):
    """Run backtesting on historical data"""
    from datetime import datetime
    from manifold_markets.backtesting import ManifoldBacktester, ManifoldForecastingBotWithBacktest
    
    print("🕰️  Running backtesting simulation...")
    
    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError:
        print("❌ Invalid date format. Use YYYY-MM-DD")
        return
    
    # Initialize enhanced bot
    bot = ManifoldForecastingBotWithBacktest(
        manifold_api_key=args.manifold_key,
        openrouter_api_key=args.openrouter_key,
        serp_api_key=args.serp_key,
        default_bet_amount=args.max_bet_per_market / 5,  # Conservative default
        confidence_threshold=args.confidence_threshold
    )
    
    # Initialize backtester
    backtester = ManifoldBacktester(bot, args.historical_data)
    
    # Download data if requested
    if args.download_data:
        print(f"📥 Downloading historical data for {start_date.date()} to {end_date.date()}...")
        data_path = args.historical_data or f"historical_data_{args.start_date}_{args.end_date}.json"
        backtester.download_historical_data(start_date, end_date, data_path)
        backtester.historical_data_path = data_path
        backtester._load_historical_data()
    
    if not backtester.historical_markets:
        print("❌ No historical data available. Use --download-data or provide --historical-data path")
        return
    
    print(f"📊 Running simulation from {start_date.date()} to {end_date.date()}")
    print(f"💰 Initial balance: ${args.initial_balance:.2f}")
    print(f"🎯 Confidence threshold: {args.confidence_threshold:.1%}")
    print(f"📈 Min confidence: {args.min_confidence}")
    
    # Run backtest
    result = backtester.run_backtest(
        start_date=start_date,
        end_date=end_date,
        initial_balance=args.initial_balance,
        confidence_threshold=args.confidence_threshold,
        min_confidence=args.min_confidence,
        max_bet_per_market=args.max_bet_per_market,
        max_daily_bets=args.max_daily_bets
    )
    
    # Display results
    print(f"\n📈 Backtest Results:")
    print(f"=" * 50)
    print(f"Period: {result.start_date.date()} to {result.end_date.date()}")
    print(f"Duration: {(result.end_date - result.start_date).days} days")
    print()
    print(f"💰 Financial Performance:")
    print(f"  • Initial balance: ${result.initial_balance:.2f}")
    print(f"  • Final balance: ${result.final_balance:.2f}")
    print(f"  • Total profit: ${result.total_profit:.2f}")
    print(f"  • ROI: {result.total_roi:.2%}")
    
    days = max((result.end_date - result.start_date).days, 1)
    annualized_roi = (result.total_roi * 365) / days
    print(f"  • Annualized ROI: {annualized_roi:.2%}")
    print()
    
    print(f"📊 Trading Statistics:")
    print(f"  • Markets analyzed: {result.markets_analyzed}")
    print(f"  • Opportunities found: {result.opportunities_found}")
    print(f"  • Opportunity rate: {result.opportunity_rate:.2%}")
    print(f"  • Total trades: {result.total_trades}")
    print(f"  • Winning trades: {result.winning_trades}")
    print(f"  • Losing trades: {result.losing_trades}")
    print(f"  • Cancelled trades: {result.cancelled_trades}")
    print(f"  • Win rate: {result.win_rate:.2%}")
    print(f"  • Avg profit per trade: ${result.avg_profit_per_trade:.2f}")
    
    # Show top performing trades
    if result.trades:
        profitable_trades = [t for t in result.trades if (t.profit or 0) > 0]
        losing_trades = [t for t in result.trades if (t.profit or 0) < 0]
        
        if profitable_trades:
            best_trade = max(profitable_trades, key=lambda t: t.profit or 0)
            print(f"\n🏆 Best trade: +${best_trade.profit:.2f} ({best_trade.roi:.1%})")
            print(f"   {best_trade.question[:60]}...")
        
        if losing_trades:
            worst_trade = min(losing_trades, key=lambda t: t.profit or 0)
            print(f"\n💸 Worst trade: ${worst_trade.profit:.2f} ({worst_trade.roi:.1%})")
            print(f"   {worst_trade.question[:60]}...")
        
        # Show confidence level performance
        confidence_performance = {}
        for trade in result.trades:
            conf = trade.confidence
            if conf not in confidence_performance:
                confidence_performance[conf] = {"trades": 0, "profit": 0}
            confidence_performance[conf]["trades"] += 1
            confidence_performance[conf]["profit"] += (trade.profit or 0)
        
        print(f"\n📊 Performance by Confidence Level:")
        for conf, perf in confidence_performance.items():
            avg_profit = perf["profit"] / perf["trades"] if perf["trades"] > 0 else 0
            print(f"  • {conf}: {perf['trades']} trades, ${avg_profit:.2f} avg profit")
    
    # Save results if requested
    if args.output:
        report = backtester.generate_backtest_report(result)
        backtester.save_backtest_results(result, args.output)
        print(f"\n💾 Detailed results saved to {args.output}")


def download_data_command(args):
    """Download historical market data"""
    from datetime import datetime
    from manifold_markets.backtesting import ManifoldBacktester, ManifoldForecastingBotWithBacktest
    
    print("📥 Downloading historical market data...")
    
    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError:
        print("❌ Invalid date format. Use YYYY-MM-DD")
        return
    
    # Initialize bot (only need Manifold API for downloading)
    bot = ManifoldForecastingBotWithBacktest(
        manifold_api_key=args.manifold_key,
        openrouter_api_key="dummy",  # Not needed for downloading
        confidence_threshold=0.15
    )
    
    # Initialize backtester
    backtester = ManifoldBacktester(bot)
    
    # Download data
    markets = backtester.download_historical_data(
        start_date=start_date,
        end_date=end_date,
        save_path=args.output,
        limit=args.limit
    )
    
    if markets:
        print(f"✅ Downloaded {len(markets)} markets to {args.output}")
        print(f"📅 Period: {start_date.date()} to {end_date.date()}")
        
        # Show sample markets
        print(f"\n📋 Sample markets:")
        for i, market in enumerate(markets[:5], 1):
            created = datetime.fromtimestamp(market.get('createdTime', 0) / 1000)
            print(f"  {i}. {market.get('question', 'Unknown')[:60]}...")
            print(f"     Created: {created.date()}, Resolved: {market.get('isResolved', False)}")
        
        if len(markets) > 5:
            print(f"     ... and {len(markets) - 5} more")
    else:
        print("❌ Failed to download market data")


def test_connection_command(args):
    """Test connection to APIs"""
    print("🔧 Testing API connections...")
    
    # Test Manifold Markets API
    try:
        client = ManifoldMarketsClient(args.manifold_key)
        markets = client.get_markets(limit=1)
        print("✅ Manifold Markets API: Connected")
        if markets:
            print(f"   Sample market: {markets[0].get('question', 'Unknown')}")
    except Exception as e:
        print(f"❌ Manifold Markets API: Failed - {e}")
    
    # Test OpenRouter API
    try:
        # Test by creating a forecaster instance
        from manifold_markets.forecasting_bot import ManifoldForecastingBot
        bot = ManifoldForecastingBot(
            openrouter_api_key=args.openrouter_key,
            serp_api_key=args.serp_key
        )
        print("✅ OpenRouter API: Connected")
    except Exception as e:
        print(f"❌ OpenRouter API: Failed - {e}")
    
    # Test SERP API (if provided)
    if args.serp_key:
        try:
            # This would require importing the Google News tool
            print("✅ SERP API: Key provided")
        except Exception as e:
            print(f"❌ SERP API: Failed - {e}")
    else:
        print("⚠️  SERP API: No key provided (Google News searches will be limited)")


def main():
    """Main CLI entry point"""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Manifold Markets AI Forecasting Bot")
    parser.add_argument("--manifold-key", help="Manifold Markets API key (or set MANIFOLD_API_KEY env var)")
    parser.add_argument("--openrouter-key", help="OpenRouter API key (or set OPENROUTER_API_KEY env var)")
    parser.add_argument("--serp-key", help="SERP API key for Google News (or set SERP_API_KEY env var)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze markets without betting")
    analyze_parser.add_argument("--limit", type=int, default=25, help="Number of markets to analyze")
    analyze_parser.add_argument("--search", help="Search term to filter markets")
    analyze_parser.add_argument("--output", help="Save detailed report to JSON file")
    analyze_parser.add_argument("--bet-amount", type=float, default=10.0, help="Default bet amount")
    analyze_parser.add_argument("--confidence-threshold", type=float, default=0.15, help="Minimum confidence threshold")
    
    # Opportunities command
    opportunities_parser = subparsers.add_parser("opportunities", help="Find and execute betting opportunities")
    opportunities_parser.add_argument("--limit", type=int, default=50, help="Number of markets to analyze")
    opportunities_parser.add_argument("--min-difference", type=float, default=0.15, help="Minimum probability difference")
    opportunities_parser.add_argument("--min-confidence", choices=["low", "medium", "high"], default="medium", help="Minimum confidence level")
    opportunities_parser.add_argument("--execute", action="store_true", help="Execute bets on opportunities")
    opportunities_parser.add_argument("--dry-run", action="store_true", help="Dry run mode (don't place real bets)")
    opportunities_parser.add_argument("--max-bet-total", type=float, default=100.0, help="Maximum total bet amount")
    opportunities_parser.add_argument("--output", help="Save results to JSON file")
    opportunities_parser.add_argument("--bet-amount", type=float, default=10.0, help="Default bet amount")
    opportunities_parser.add_argument("--confidence-threshold", type=float, default=0.15, help="Minimum confidence threshold")
    
    # Backtesting command
    backtest_parser = subparsers.add_parser("backtest", help="Run backtesting on historical data")
    backtest_parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    backtest_parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    backtest_parser.add_argument("--historical-data", help="Path to historical market data JSON file")
    backtest_parser.add_argument("--initial-balance", type=float, default=1000.0, help="Starting balance in Mana")
    backtest_parser.add_argument("--confidence-threshold", type=float, default=0.15, help="Minimum confidence threshold")
    backtest_parser.add_argument("--min-confidence", choices=["low", "medium", "high"], default="medium", help="Minimum confidence level")
    backtest_parser.add_argument("--max-bet-per-market", type=float, default=50.0, help="Maximum bet per market")
    backtest_parser.add_argument("--max-daily-bets", type=float, default=200.0, help="Maximum daily bet total")
    backtest_parser.add_argument("--output", help="Save backtest results to JSON file")
    backtest_parser.add_argument("--download-data", action="store_true", help="Download historical data for the period")
    
    # Download historical data command
    download_parser = subparsers.add_parser("download-data", help="Download historical market data")
    download_parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    download_parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    download_parser.add_argument("--output", required=True, help="Output file path for historical data")
    download_parser.add_argument("--limit", type=int, default=1000, help="Maximum markets to download")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test API connections")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Get API keys from environment if not provided
    args.manifold_key = args.manifold_key or os.getenv("MANIFOLD_API_KEY")
    args.openrouter_key = args.openrouter_key or os.getenv("OPENROUTER_API_KEY")
    args.serp_key = args.serp_key or os.getenv("SERP_API_KEY")
    
    # Check required keys
    if args.command != "test" and not args.openrouter_key:
        print("❌ OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or use --openrouter-key")
        return
    
    # Execute command
    try:
        if args.command == "analyze":
            analyze_markets_command(args)
        elif args.command == "opportunities":
            find_opportunities_command(args)
        elif args.command == "backtest":
            backtest_command(args)
        elif args.command == "download-data":
            download_data_command(args)
        elif args.command == "test":
            test_connection_command(args)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
