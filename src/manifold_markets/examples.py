#!/usr/bin/env python3
"""
Example usage of Manifold Markets Forecasting Bot
Demonstrates how to use the AI forecasting bot to analyze markets
"""

import os
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from manifold_markets.forecasting_bot import ManifoldForecastingBot
from manifold_markets.client import ManifoldMarketsClient


def example_basic_analysis():
    """Example: Basic market analysis"""
    print("🤖 Example 1: Basic Market Analysis")
    print("=" * 50)
    
    # Initialize the bot
    bot = ManifoldForecastingBot(
        manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        serp_api_key=os.getenv("SERP_API_KEY"),
        default_bet_amount=10.0
    )
    
    # Analyze a few markets
    print("Analyzing top 5 markets...")
    forecasted_markets = bot.analyze_markets(limit=5)
    
    # Print results
    for i, market in enumerate(forecasted_markets, 1):
        print(f"\n{i}. {market.question}")
        print(f"   Market probability: {market.current_prob:.1%}")
        print(f"   AI probability: {market.ai_forecast.probability:.1%}")
        print(f"   Difference: {market.forecast_difference:+.1%}")
        print(f"   Confidence: {market.ai_forecast.confidence_level}")
        print(f"   Recommendation: {market.recommended_action}")
        if market.bet_amount:
            print(f"   Suggested bet: ${market.bet_amount:.2f}")


def example_search_and_analyze():
    """Example: Search for specific topics and analyze"""
    print("\n🔍 Example 2: Search and Analyze Specific Topics")
    print("=" * 50)
    
    bot = ManifoldForecastingBot()
    
    # Search for AI-related markets
    print("Searching for AI-related markets...")
    ai_markets = bot.analyze_markets(limit=10, search_term="AI")
    
    if ai_markets:
        print(f"Found {len(ai_markets)} AI-related markets")
        
        # Show most confident predictions
        confident_markets = [m for m in ai_markets if m.ai_forecast.confidence_level == "high"]
        if confident_markets:
            print(f"\nHigh confidence AI predictions ({len(confident_markets)}):")
            for market in confident_markets:
                print(f"  • {market.question}")
                print(f"    AI: {market.ai_forecast.probability:.1%} vs Market: {market.current_prob:.1%}")
    else:
        print("No AI markets found")


def example_find_opportunities():
    """Example: Find betting opportunities"""
    print("\n🎯 Example 3: Find Betting Opportunities")
    print("=" * 50)
    
    bot = ManifoldForecastingBot()
    
    # Find opportunities with significant disagreement
    print("Finding betting opportunities...")
    opportunities = bot.find_opportunities(
        min_difference=0.20,  # 20% difference
        min_confidence="medium",
        limit=20
    )
    
    if opportunities:
        print(f"Found {len(opportunities)} betting opportunities:")
        
        for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
            print(f"\n{i}. {opp.question}")
            print(f"   Action: {opp.recommended_action}")
            print(f"   AI: {opp.ai_forecast.probability:.1%} vs Market: {opp.current_prob:.1%}")
            print(f"   Difference: {opp.forecast_difference:+.1%}")
            print(f"   Suggested bet: ${opp.bet_amount:.2f}")
            print(f"   Reasoning: {opp.reasoning}")
    else:
        print("No significant opportunities found")


def example_dry_run_betting():
    """Example: Simulate betting (dry run)"""
    print("\n💸 Example 4: Simulate Betting (Dry Run)")
    print("=" * 50)
    
    bot = ManifoldForecastingBot()
    
    # Find opportunities
    opportunities = bot.find_opportunities(
        min_difference=0.15,
        min_confidence="medium",
        limit=10
    )
    
    if opportunities:
        print(f"Simulating bets on {len(opportunities)} opportunities...")
        
        # Execute in dry run mode
        results = bot.execute_bets(
            opportunities,
            dry_run=True,
            max_total_amount=50.0
        )
        
        # Show results
        total_amount = sum(r["amount"] for r in results if r["success"])
        print(f"\nDry run complete:")
        print(f"  • Bets placed: {len([r for r in results if r['success']])}")
        print(f"  • Total amount: ${total_amount:.2f}")
        print(f"  • Failed bets: {len([r for r in results if not r['success']])}")
        
        # Show sample bets
        print("\nSample bets:")
        for result in results[:3]:
            if result["success"]:
                print(f"  • {result['outcome']} ${result['amount']:.2f} on: {result['question'][:60]}...")
    else:
        print("No opportunities found for betting")


def example_generate_report():
    """Example: Generate comprehensive analysis report"""
    print("\n📊 Example 5: Generate Analysis Report")
    print("=" * 50)
    
    bot = ManifoldForecastingBot()
    
    # Analyze markets
    print("Analyzing markets for report...")
    forecasted_markets = bot.analyze_markets(limit=15)
    
    # Generate report
    report = bot.generate_report(forecasted_markets)
    
    # Print summary
    print("\nMarket Analysis Report:")
    print(f"  • Markets analyzed: {report['summary']['total_markets_analyzed']}")
    print(f"  • Betting opportunities: {report['summary']['betting_opportunities']}")
    print(f"  • High confidence forecasts: {report['summary']['high_confidence_forecasts']}")
    print(f"  • Average difference: {report['summary']['average_probability_difference']:.1%}")
    
    # Confidence distribution
    conf_dist = report['confidence_distribution']
    print(f"\nConfidence distribution:")
    print(f"  • High: {conf_dist['high']}")
    print(f"  • Medium: {conf_dist['medium']}")
    print(f"  • Low: {conf_dist['low']}")
    
    # Action distribution
    action_dist = report['action_distribution']
    print(f"\nRecommended actions:")
    print(f"  • Buy YES: {action_dist['BUY_YES']}")
    print(f"  • Buy NO: {action_dist['BUY_NO']}")
    print(f"  • Hold: {action_dist['HOLD']}")
    print(f"  • Avoid: {action_dist['AVOID']}")
    
    # Save report
    with open("market_analysis_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Full report saved to market_analysis_report.json")


def example_single_market_analysis():
    """Example: Analyze a single specific market"""
    print("\n🎯 Example 6: Single Market Analysis")
    print("=" * 50)
    
    # Initialize clients
    manifold_client = ManifoldMarketsClient()
    bot = ManifoldForecastingBot()
    
    # Get a market (this gets the first market)
    print("Fetching a sample market...")
    markets = manifold_client.get_markets(limit=1)
    
    if markets:
        market = markets[0]
        print(f"Analyzing market: {market['question']}")
        
        # Analyze the specific market
        forecast = bot.analyze_market(market)
        
        if forecast:
            print(f"\nDetailed Analysis:")
            print(f"  • Question: {forecast.question}")
            print(f"  • Market ID: {forecast.market_id}")
            print(f"  • Current probability: {forecast.current_prob:.1%}")
            print(f"  • AI probability: {forecast.ai_forecast.probability:.1%}")
            print(f"  • Difference: {forecast.forecast_difference:+.1%}")
            print(f"  • Confidence: {forecast.ai_forecast.confidence_level}")
            print(f"  • Base rate: {forecast.ai_forecast.base_rate:.1%}")
            print(f"  • Evidence quality: {forecast.ai_forecast.evidence_quality:.1%}")
            print(f"  • Recommendation: {forecast.recommended_action}")
            if forecast.bet_amount:
                print(f"  • Suggested bet: ${forecast.bet_amount:.2f}")
            print(f"  • Reasoning: {forecast.reasoning}")
            print(f"\nAI Analysis:")
            print(f"  {forecast.ai_forecast.reasoning}")
        else:
            print("Failed to analyze market")
    else:
        print("No markets found")


def main():
    """Run all examples"""
    print("🚀 Manifold Markets Forecasting Bot Examples")
    print("=" * 60)
    
    # Check for required environment variables
    required_vars = ["OPENROUTER_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables:")
        print("  • OPENROUTER_API_KEY: Your OpenRouter API key")
        print("  • MANIFOLD_API_KEY: Your Manifold Markets API key (optional for read-only)")
        print("  • SERP_API_KEY: Your SERP API key for Google News (optional)")
        return
    
    try:
        # Run examples
        example_basic_analysis()
        example_search_and_analyze()
        example_find_opportunities()
        example_dry_run_betting()
        example_generate_report()
        example_single_market_analysis()
        
        print("\n✅ All examples completed successfully!")
        print("\nNext steps:")
        print("  • Use 'python cli.py analyze' for quick analysis")
        print("  • Use 'python cli.py opportunities --execute --dry-run' to simulate betting")
        print("  • Set MANIFOLD_API_KEY to place real bets")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
