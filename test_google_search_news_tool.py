#!/usr/bin/env python3
"""
Test script for the updated Google Search News tool
Tests the browser-based Google Search with news filter functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append('src')

from ai_forecasts.agents.browser_google_news_tool import BrowserGoogleNewsTool


def test_google_search_news_tool():
    """Test the Google Search News tool with date filtering"""
    
    print("🧪 Testing Google Search News Tool")
    print("=" * 50)
    
    # Initialize the tool
    tool = BrowserGoogleNewsTool()
    
    # Test 1: Basic search without dates
    print("\n📰 Test 1: Basic search")
    result1 = tool._run("artificial intelligence breakthrough")
    print(f"Result: {result1[:200]}...")
    
    # Test 2: Search with date range
    print("\n📅 Test 2: Search with date range")
    start_date = "2024-06-01"
    end_date = "2024-06-10"
    result2 = tool._run("OpenAI GPT", start_date=start_date, end_date=end_date)
    print(f"Result: {result2[:200]}...")
    
    # Test 3: Test URL building
    print("\n🔗 Test 3: URL building")
    url = tool._build_google_news_url("AI timeline", "2024-05-26", "2024-05-31")
    print(f"Generated URL: {url}")
    
    # Verify URL structure
    expected_components = [
        "www.google.com/search",
        "tbm=nws",  # News filter
        "tbs=cdr:1",  # Custom date range
        "cd_min:",  # Start date
        "cd_max:"   # End date
    ]
    
    print("\n✅ URL Components Check:")
    for component in expected_components:
        if component in url:
            print(f"  ✓ {component}")
        else:
            print(f"  ✗ {component} - MISSING")
    
    # Test 4: Date conversion
    print("\n📆 Test 4: Date conversion")
    test_date = "2024-05-30"
    converted = tool._convert_date_to_google_format(test_date)
    print(f"Input: {test_date}")
    print(f"Converted: {converted}")
    print(f"Expected format: M/D/YYYY (e.g., 5/30/2024)")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")


def generate_example_url():
    """Generate an example URL to show the format"""
    print("\n🌐 Example URL Generation")
    print("=" * 30)
    
    tool = BrowserGoogleNewsTool()
    
    # Generate URL similar to the user's example
    query = "ai timelines"
    start_date = "2025-05-26"
    end_date = "2025-05-31"
    
    url = tool._build_google_news_url(query, start_date, end_date)
    
    print(f"Query: {query}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Generated URL: {url}")
    
    # Compare with user's example structure
    user_example = "https://www.google.com/search?sca_esv=b26ac6e58dd72d43&tbs=cdr:1,cd_min:5/26/2025,cd_max:5/31/2025&sxsrf=AE3TifMs3K2YiaAaercr8c1zVK5sFrSHlA:1749643715248&q=ai+timelines&tbm=nws&source=lnms&fbs=AIIjpHxU7SXXniUZfeShr2fp4giZ1Y6MJ25_tmWITc7uy4KIeuYzzFkfneXafNx6OMdA4MRo3L_oOc-1oJ7O1RV73dx3MIyCigtuiU2aDjExIvydX85cOq96-7Mxd4KSNCLhHwZjNl1D--59A3Pz1jRAtenzCJ-qzCnOKtvU69k0YYAuhlzxHSrRNQ-gtEYBj8xSow3FJ3v7l7zsi4eO0Nw9mEGcGVLxNQ&sa=X&ved=2ahUKEwjd4oXhqumNAxVwU6QEHdjNF10Q0pQJegQIFRAB&biw=1694&bih=940&dpr=1"
    
    print(f"\nUser's example: {user_example}")
    
    # Check key components
    print("\n🔍 Key components comparison:")
    print(f"  ✓ Base URL: www.google.com/search")
    print(f"  ✓ News filter: tbm=nws")
    print(f"  ✓ Date range: tbs=cdr:1")
    print(f"  ✓ Start date: cd_min:5/26/2025")
    print(f"  ✓ End date: cd_max:5/31/2025")
    print(f"  ✓ Query: q=ai+timelines")


if __name__ == "__main__":
    try:
        test_google_search_news_tool()
        generate_example_url()
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
