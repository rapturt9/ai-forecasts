#!/usr/bin/env python3
"""
Test script for Manifold Markets integration
Tests basic functionality without requiring API keys
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from manifold_markets import ManifoldMarketsClient, ManifoldForecastingBot, ForecastedMarket
        print("✅ Successfully imported ManifoldMarketsClient")
        print("✅ Successfully imported ManifoldForecastingBot")
        print("✅ Successfully imported ForecastedMarket")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_client_initialization():
    """Test client initialization without API key"""
    print("\n🧪 Testing client initialization...")
    
    try:
        from manifold_markets import ManifoldMarketsClient
        
        # Test without API key
        client = ManifoldMarketsClient()
        print("✅ ManifoldMarketsClient initialized without API key")
        
        # Test with dummy API key
        client_with_key = ManifoldMarketsClient("dummy_key")
        print("✅ ManifoldMarketsClient initialized with API key")
        
        return True
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False

def test_public_api_access():
    """Test public API access (no auth required)"""
    print("\n🧪 Testing public API access...")
    
    try:
        from manifold_markets import ManifoldMarketsClient
        
        client = ManifoldMarketsClient()
        
        # Try to fetch markets (should work without auth)
        markets = client.get_markets(limit=1)
        
        if markets and len(markets) > 0:
            market = markets[0]
            print(f"✅ Successfully fetched market: {market.get('question', 'Unknown')[:50]}...")
            print(f"   Market ID: {market.get('id', 'Unknown')}")
            print(f"   Probability: {market.get('probability', 'Unknown')}")
            return True
        else:
            print("⚠️  No markets returned (API might be down)")
            return False
            
    except Exception as e:
        print(f"❌ Public API access failed: {e}")
        return False

def test_forecasting_bot_creation():
    """Test forecasting bot creation (without actual forecasting)"""
    print("\n🧪 Testing forecasting bot creation...")
    
    try:
        from manifold_markets import ManifoldForecastingBot
        
        # This should fail gracefully without OpenRouter key
        try:
            bot = ManifoldForecastingBot()
            print("❌ Bot creation should have failed without OpenRouter key")
            return False
        except ValueError as e:
            if "OpenRouter API key" in str(e):
                print("✅ Bot correctly requires OpenRouter API key")
                return True
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error type: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Forecasting bot test failed: {e}")
        return False

def test_with_env_vars():
    """Test with environment variables if available"""
    print("\n🧪 Testing with environment variables...")
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    manifold_key = os.getenv("MANIFOLD_API_KEY")
    serp_key = os.getenv("SERP_API_KEY")
    
    print(f"   OpenRouter API key: {'✅ Set' if openrouter_key else '❌ Not set'}")
    print(f"   Manifold API key: {'✅ Set' if manifold_key else '❌ Not set'}")
    print(f"   SERP API key: {'✅ Set' if serp_key else '❌ Not set'}")
    
    if openrouter_key:
        try:
            from manifold_markets import ManifoldForecastingBot
            
            print("   Attempting to create forecasting bot with API keys...")
            bot = ManifoldForecastingBot(
                manifold_api_key=manifold_key,
                openrouter_api_key=openrouter_key,
                serp_api_key=serp_key,
                default_bet_amount=1.0  # Small amount for testing
            )
            print("✅ Forecasting bot created successfully with API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create bot with API keys: {e}")
            return False
    else:
        print("⚠️  Cannot test full functionality without OpenRouter API key")
        print("   Set OPENROUTER_API_KEY environment variable to test forecasting")
        return True

def main():
    """Run all tests"""
    print("🚀 Manifold Markets Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_client_initialization,
        test_public_api_access,
        test_forecasting_bot_creation,
        test_with_env_vars
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        print("\nNext steps:")
        print("1. Set OPENROUTER_API_KEY to enable AI forecasting")
        print("2. Set MANIFOLD_API_KEY to enable bet placement")
        print("3. Try: python src/manifold_markets/cli.py test")
        print("4. Try: python src/manifold_markets/examples.py")
    else:
        print(f"⚠️  {total - passed} tests failed. Check error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
