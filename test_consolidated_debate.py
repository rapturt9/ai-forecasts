#!/usr/bin/env python3
"""
Quick test of the consolidated debate system
"""

import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster

def test_consolidated_debate():
    """Test the consolidated debate system with a simple question"""
    print("🧪 Testing consolidated debate system...")
    
    # Get API keys from environment
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    serp_key = os.getenv("SERP_API_KEY")
    
    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return False
        
    if not serp_key:
        print("❌ SERP_API_KEY not found in environment")
        return False
    
    try:
        # Create forecaster with consolidated debate mode
        forecaster = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_key,
            serp_api_key=serp_key,
            debate_mode=True,
            debate_rounds=2,  # Keep it short for testing
            enhanced_quality_mode=False,  # Use regular mode for simpler testing
            recommended_articles=5  # Limit articles for faster testing
        )
        
        print("✅ Forecaster initialized successfully")
        
        # Test with a simple question and multiple time horizons
        question = "Will the S&P 500 close above 6000 by the end of 2025?"
        background = "Testing the consolidated debate system"
        time_horizons = ["30d", "90d"]  # Test with 2 horizons
        
        print(f"📋 Question: {question}")
        print(f"⏰ Time horizons: {time_horizons}")
        
        # Run the forecast
        results = forecaster.forecast_with_google_news(
            question=question,
            background=background,
            time_horizons=time_horizons,
            cutoff_date=datetime(2024, 12, 1),  # Use past date for testing
            recommended_articles=3,  # Very limited for quick test
            max_search_queries=2
        )
        
        print(f"✅ Got {len(results)} forecast results")
        
        # Check results
        for i, result in enumerate(results):
            print(f"\n📊 Result {i+1} ({result.time_horizon}):")
            print(f"   Probability: {result.probability}")
            print(f"   Confidence: {result.confidence_level}")
            print(f"   Methodology: {list(result.methodology_components.keys())}")
            
            # Check if we have consolidated debate components
            if "consolidated_adversarial_debate" in result.methodology_components:
                print("   ✅ Consolidated debate mode confirmed")
            else:
                print("   ⚠️ Consolidated debate mode not detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_consolidated_debate()
    sys.exit(0 if success else 1)
