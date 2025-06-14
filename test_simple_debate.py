#!/usr/bin/env python3
"""
Simple test script to verify the consolidated debate functionality works
"""
import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster

def test_simple_debate():
    """Test the consolidated debate with a simple question"""
    
    # Get API keys from environment
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    serp_api_key = os.getenv("SERP_API_KEY")
    
    if not openrouter_api_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return False
    
    if not serp_api_key:
        print("⚠️ SERP_API_KEY not found, using fallback")
    
    print("🚀 Starting simple debate test...")
    
    try:
        # Create forecaster with minimal configuration
        forecaster = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_api_key,
            serp_api_key=serp_api_key,
            debate_mode=True,
            debate_rounds=1,  # Just 1 round for testing
            enhanced_quality_mode=False,  # Disable enhanced mode initially
            recommended_articles=3,  # Small number for testing
            max_search_queries=2
        )
        
        print("✅ Forecaster created successfully")
        
        # Test with a simple question
        question = "Will the price of Bitcoin exceed $100,000 by December 31, 2025?"
        cutoff_date = datetime(2025, 6, 14)  # Current date
        time_horizons = ["6 months"]  # Single short horizon
        
        print(f"📋 Testing question: {question}")
        print(f"⏰ Time horizon: {time_horizons}")
        
        # Execute the forecast
        results = forecaster.forecast_with_google_news(
            question=question,
            background="Bitcoin price prediction for 2025",
            cutoff_date=cutoff_date,
            time_horizons=time_horizons,
            is_benchmark=False
        )
        
        print(f"✅ Test completed successfully!")
        print(f"📊 Results: {len(results)} forecast(s) generated")
        
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  Probability: {result.probability}")
            print(f"  Confidence: {result.confidence_level}")
            print(f"  Time Horizon: {result.time_horizon}")
            print(f"  Reasoning: {result.reasoning[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_debate()
    if success:
        print("🎉 Simple debate test passed!")
    else:
        print("💥 Simple debate test failed!")
    
    sys.exit(0 if success else 1)
