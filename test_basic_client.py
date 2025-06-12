#!/usr/bin/env python3
"""
Simple test for Manifold Markets client only
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_client():
    """Test just the client without the forecasting bot"""
    print("Testing Manifold Markets client...")
    
    try:
        from manifold_markets.client import ManifoldMarketsClient
        print("✅ Successfully imported ManifoldMarketsClient")
        
        # Test client creation
        client = ManifoldMarketsClient()
        print("✅ Successfully created client")
        
        # Test API call
        markets = client.get_markets(limit=1)
        print(f"✅ Successfully fetched {len(markets)} market(s)")
        
        if markets:
            market = markets[0]
            print(f"   Sample market: {market.get('question', 'Unknown')[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_client()
    print("✅ Basic client test passed!" if success else "❌ Basic client test failed!")
    exit(0 if success else 1)
