#!/usr/bin/env python3
"""
Test script for the Browser Google News Tool
"""
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append('src')

from ai_forecasts.agents.browser_google_news_tool import BrowserGoogleNewsTool

def test_google_news_tool():
    """Test the Google News tool with various queries"""
    
    print("🧪 Testing Browser Google News Tool")
    print("=" * 50)
    
    # Initialize the tool
    tool = BrowserGoogleNewsTool()
    
    # Test 1: Basic search without dates
    print("\n📰 Test 1: Basic search (no date restrictions)")
    result1 = tool._run("artificial intelligence")
    print("Result length:", len(result1))
    print("First 200 chars:", result1[:200])
    
    # Test 2: Search with date range
    print("\n📰 Test 2: Search with date range")
    end_date = "2024-12-31"
    start_date = "2024-06-01"
    result2 = tool._run("climate change", start_date=start_date, end_date=end_date)
    print("Result length:", len(result2))
    print("First 200 chars:", result2[:200])
    
    # Test 3: Recent search
    print("\n📰 Test 3: Recent search")
    recent_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    recent_end = datetime.now().strftime("%Y-%m-%d")
    result3 = tool._run("technology news", start_date=recent_start, end_date=recent_end)
    print("Result length:", len(result3))
    print("First 200 chars:", result3[:200])
    
    # Test 4: Check if Selenium is available
    print(f"\n🔧 Selenium available: {tool._browser_available}")
    
    return all([
        len(result1) > 50,
        len(result2) > 50, 
        len(result3) > 50
    ])

if __name__ == "__main__":
    try:
        success = test_google_news_tool()
        if success:
            print("\n✅ All Google News tool tests passed!")
        else:
            print("\n❌ Some tests failed")
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
