#!/usr/bin/env python3
"""
Enhanced test script for the improved Google Search News tool
"""
import sys
import os
sys.path.append('src')

from ai_forecasts.agents.browser_google_news_tool import BrowserGoogleNewsTool


def test_enhanced_google_search():
    """Test the enhanced Google Search News tool with better error handling"""
    
    print("🔧 Testing Enhanced Google Search News Tool")
    print("=" * 60)
    
    # Create tool instance
    tool = BrowserGoogleNewsTool()
    
    # Test 1: Basic search without dates
    print("\n📰 Test 1: Basic search")
    result = tool._run("artificial intelligence breakthrough")
    print(f"Result length: {len(result)}")
    print(f"First 200 chars: {result[:200]}")
    
    # Test 2: Search with recent dates 
    print("\n📰 Test 2: Recent search with dates")
    result = tool._run("OpenAI GPT", "2025-05-01", "2025-06-11")
    print(f"Result length: {len(result)}")
    print(f"First 200 chars: {result[:200]}")
    
    # Test 3: Search with broader tech news
    print("\n📰 Test 3: Broader tech news search")
    result = tool._run("technology", "2025-06-01", "2025-06-11")
    print(f"Result length: {len(result)}")
    print(f"First 200 chars: {result[:200]}")
    
    # Test 4: Search for a very specific recent topic
    print("\n📰 Test 4: Very specific recent topic")
    result = tool._run("Apple WWDC 2025", "2025-06-01", "2025-06-11")
    print(f"Result length: {len(result)}")
    print(f"First 200 chars: {result[:200]}")
    
    # Check Selenium availability
    from ai_forecasts.agents.browser_google_news_tool import SELENIUM_AVAILABLE
    print(f"\n🔧 Selenium available: {SELENIUM_AVAILABLE}")
    
    print("\n✅ Enhanced Google Search tool testing completed")


if __name__ == "__main__":
    test_enhanced_google_search()
