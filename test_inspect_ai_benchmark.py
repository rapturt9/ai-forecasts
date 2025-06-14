#!/usr/bin/env python3
"""
Test Inspect AI integration with the benchmark system using debate mode
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster

def test_inspect_ai_benchmark():
    """Test Inspect AI with a single benchmark question using debate mode"""
    print("🧪 Testing Inspect AI with Benchmark (Debate Mode)")
    print("=" * 60)
    
    # Get API keys from environment
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    serp_key = os.getenv("SERP_API_KEY")
    
    if not openrouter_key or not serp_key:
        print("❌ Missing required API keys")
        return False
    
    try:
        # Create forecaster with Inspect AI enabled and debate mode
        print("\n📋 Creating Inspect AI forecaster with debate mode...")
        forecaster = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_key,
            serp_api_key=serp_key,
            use_inspect_ai=True,
            debate_mode=True,
            recommended_articles=5,  # Limit for testing
            max_search_queries=3     # Limit for testing
        )
        
        # Verify Inspect AI is being used
        if not hasattr(forecaster, '_inspect_ai_forecaster'):
            print("❌ Inspect AI forecaster not initialized")
            return False
        
        print("✅ Inspect AI forecaster with debate mode initialized")
        
        # Test question from ForecastBench
        question = "Will the S&P 500 close above 6000 by the end of 2025?"
        background = "Testing Inspect AI integration with benchmark using debate methodology"
        
        print(f"\n📊 Testing question: {question}")
        print(f"📝 Background: {background}")
        
        # Run forecast with multiple time horizons
        time_horizons = ["30d", "90d"]  # Limited for testing
        cutoff_date = datetime(2024, 12, 1)
        
        print(f"\n🎯 Running forecast with time horizons: {time_horizons}")
        print(f"📅 Cutoff date: {cutoff_date}")
        
        results = forecaster.forecast_with_google_news(
            question=question,
            background=background,
            time_horizons=time_horizons,
            cutoff_date=cutoff_date,
            recommended_articles=5,
            max_search_queries=3
        )
        
        print(f"\n✅ Forecast completed! Generated {len(results)} results")
        
        # Analyze results
        for i, result in enumerate(results):
            print(f"\n📊 Result {i+1}:")
            print(f"   🎯 Time Horizon: {result.time_horizon}")
            print(f"   📈 Probability: {result.probability:.3f}")
            print(f"   🎯 Confidence: {result.confidence_level}")
            print(f"   🔧 Methodology Components: {list(result.methodology_components.keys())}")
            
            # Check if Inspect AI methodology is detected
            if "inspect_ai_debate" in result.methodology_components:
                print("   ✅ Inspect AI debate methodology confirmed")
            elif "consolidated_adversarial_debate" in result.methodology_components:
                print("   ⚠️ CrewAI methodology detected (fallback occurred)")
            else:
                print("   ❓ Unknown methodology detected")
            
            # Show reasoning summary
            if hasattr(result, 'reasoning_summary') and result.reasoning_summary:
                print(f"   💭 Reasoning: {result.reasoning_summary[:200]}...")
        
        # Save results for verification
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "background": background,
            "time_horizons": time_horizons,
            "cutoff_date": cutoff_date.isoformat(),
            "framework": "inspect_ai",
            "debate_mode": True,
            "results": [
                {
                    "time_horizon": r.time_horizon,
                    "probability": r.probability,
                    "confidence_level": r.confidence_level,
                    "methodology_components": list(r.methodology_components.keys()),
                    "reasoning_summary": getattr(r, 'reasoning_summary', '')[:500]
                }
                for r in results
            ]
        }
        
        results_file = f"inspect_ai_benchmark_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Verify debate methodology was used
        debate_detected = any(
            "inspect_ai_debate" in result.methodology_components 
            for result in results
        )
        
        if debate_detected:
            print("\n🎉 SUCCESS: Inspect AI debate methodology working correctly!")
        else:
            print("\n⚠️ WARNING: Inspect AI debate methodology not detected (may have fallen back to CrewAI)")
        
        print("\n✅ Benchmark test completed successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during benchmark test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_inspect_ai_benchmark()
    sys.exit(0 if success else 1)