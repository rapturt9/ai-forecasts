#!/usr/bin/env python3
"""
Simple test to verify the basic integration works
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_integration():
    """Test basic integration without running full forecasts"""
    print("🧪 Testing simple integration...")
    
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
        # Test 1: Import and create Inspect AI forecaster
        print("\n📋 Test 1: Creating Inspect AI forecaster")
        from ai_forecasts.agents.inspect_ai_superforecaster import InspectAISuperforecaster
        
        inspect_forecaster = InspectAISuperforecaster(
            openrouter_api_key=openrouter_key,
            serp_api_key=serp_key,
            recommended_articles=3
        )
        print("✅ Inspect AI forecaster created successfully")
        
        # Test 2: Create GoogleNewsSuperforecaster with Inspect AI enabled
        print("\n📋 Test 2: Creating GoogleNewsSuperforecaster with Inspect AI")
        from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster
        
        forecaster_inspect = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_key,
            serp_api_key=serp_key,
            use_inspect_ai=True,
            debate_mode=True,
            recommended_articles=3
        )
        
        if hasattr(forecaster_inspect, '_inspect_ai_forecaster'):
            print("✅ Inspect AI delegation working")
        else:
            print("❌ Inspect AI delegation not working")
            return False
        
        # Test 3: Create GoogleNewsSuperforecaster with CrewAI (backwards compatibility)
        print("\n📋 Test 3: Creating GoogleNewsSuperforecaster with CrewAI")
        forecaster_crew = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_key,
            serp_api_key=serp_key,
            use_inspect_ai=False,
            debate_mode=True,
            recommended_articles=3
        )
        
        if hasattr(forecaster_crew, 'llm'):
            print("✅ CrewAI mode working")
        else:
            print("❌ CrewAI mode not working")
            return False
        
        # Test 4: Test environment variable control
        print("\n📋 Test 4: Testing environment variable control")
        os.environ['USE_INSPECT_AI'] = 'true'
        
        forecaster_env = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_key,
            serp_api_key=serp_key,
            recommended_articles=3
        )
        
        # Should default to Inspect AI based on env var
        if hasattr(forecaster_env, '_inspect_ai_forecaster'):
            print("✅ Environment variable control working")
        else:
            print("❌ Environment variable control not working")
            return False
        
        print("\n🎉 All basic integration tests passed!")
        print("✅ Inspect AI integration is properly set up")
        print("✅ Backwards compatibility with CrewAI is maintained")
        print("✅ Environment variable control is working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_integration()
    sys.exit(0 if success else 1)