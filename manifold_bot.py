#!/usr/bin/env python3
"""
Quick launcher for Manifold Markets Forecasting Bot
Provides easy access to common operations
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main launcher"""
    print("🤖 Manifold Markets AI Forecasting Bot")
    print("=" * 40)
    
    # Check for API keys
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    manifold_key = os.getenv("MANIFOLD_API_KEY")
    
    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("   This is required for AI forecasting functionality")
        print("   Get your key from: https://openrouter.ai")
        return 1
    
    print("✅ OpenRouter API key detected")
    if manifold_key:
        print("✅ Manifold API key detected (betting enabled)")
    else:
        print("⚠️  No Manifold API key (read-only mode)")
    
    print("\nWhat would you like to do?")
    print("1. Quick market analysis (analyze 10 markets)")
    print("2. Find betting opportunities") 
    print("3. Test API connections")
    print("4. Run examples")
    print("5. Open CLI help")
    
    try:
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🔄 Running quick market analysis...")
            os.system("python src/manifold_markets/cli.py analyze --limit 10")
            
        elif choice == "2":
            print("\n🔄 Finding betting opportunities...")
            os.system("python src/manifold_markets/cli.py opportunities --min-difference 0.15")
            
        elif choice == "3":
            print("\n🔄 Testing API connections...")
            os.system("python src/manifold_markets/cli.py test")
            
        elif choice == "4":
            print("\n🔄 Running examples...")
            os.system("python src/manifold_markets/examples.py")
            
        elif choice == "5":
            print("\n🔄 Showing CLI help...")
            os.system("python src/manifold_markets/cli.py --help")
            
        else:
            print("❌ Invalid choice")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
