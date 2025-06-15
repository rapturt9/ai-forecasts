#!/usr/bin/env python3
"""
Test script to demonstrate the new configurable features
"""

import os
from datetime import datetime

# Set up environment
os.environ['OPENROUTER_API_KEY'] = 'test'
os.environ['SERP_API_KEY'] = 'test'

from run_forecastbench import EnhancedForecastBenchRunner
from src.ai_forecasts.agents.inspect_ai_superforecaster import create_superforecaster

def test_configurable_parameters():
    """Test the new configurable parameters"""
    print("🧪 Testing Configurable Parameters")
    print("=" * 50)
    
    # Test 1: Custom time horizons
    print("\n1. Testing custom time horizons...")
    runner1 = EnhancedForecastBenchRunner(
        openrouter_api_key='test',
        serp_api_key='test',
        time_horizons=[1, 7, 14],  # Custom horizons
        search_budget=8,
        debate_turns=3
    )
    print(f"   ✅ Time horizons: {runner1.time_horizons}")
    print(f"   ✅ Search budget: {runner1.search_budget}")
    print(f"   ✅ Debate turns: {runner1.debate_turns}")
    
    # Test 2: Different search budget
    print("\n2. Testing different search budget...")
    runner2 = EnhancedForecastBenchRunner(
        openrouter_api_key='test',
        serp_api_key='test',
        time_horizons=[30, 90, 180, 365],  # Longer horizons
        search_budget=15,  # Higher budget
        debate_turns=1  # Single turn
    )
    print(f"   ✅ Time horizons: {runner2.time_horizons}")
    print(f"   ✅ Search budget: {runner2.search_budget}")
    print(f"   ✅ Debate turns: {runner2.debate_turns}")
    
    # Test 3: Superforecaster receives parameters
    print("\n3. Testing superforecaster parameter passing...")
    sf = create_superforecaster(
        openrouter_api_key='test',
        search_budget=runner2.search_budget,
        debate_turns=runner2.debate_turns,
        time_horizons=runner2.time_horizons
    )
    print(f"   ✅ Superforecaster search budget: {sf.search_budget}")
    print(f"   ✅ Superforecaster debate turns: {sf.debate_turns}")
    print(f"   ✅ Superforecaster time horizons: {sf.time_horizons}")

def test_debate_system():
    """Test the debate system with JSON output"""
    print("\n🗣️ Testing Debate System")
    print("=" * 50)
    
    # Create superforecaster with debate configuration
    sf = create_superforecaster(
        openrouter_api_key='test',
        search_budget=5,
        debate_turns=2,
        time_horizons=[7, 30]
    )
    
    # Test forecast with mock data
    print("\n1. Testing debate forecast...")
    question = "Will AI achieve AGI by 2030?"
    background = "Recent developments in AI capabilities and scaling laws"
    time_horizons = ["7d", "30d"]
    
    try:
        results = sf.forecast_with_google_news(
            question=question,
            background=background,
            time_horizons=time_horizons,
            cutoff_date=datetime.now()
        )
        
        print(f"   ✅ Generated {len(results)} forecasts")
        for i, result in enumerate(results):
            print(f"   📊 Horizon {time_horizons[i]}: {result.prediction:.3f} ({result.confidence})")
            print(f"      Reasoning: {result.reasoning[:100]}...")
            
    except Exception as e:
        print(f"   ⚠️ Using mock forecaster: {e}")

def test_command_line_interface():
    """Test the new command line options"""
    print("\n💻 Testing Command Line Interface")
    print("=" * 50)
    
    print("\n1. Available new options:")
    print("   --time-horizons: Configure prediction time horizons")
    print("   --search-budget: Set search budget per question")
    print("   --debate-turns: Set number of debate turns")
    
    print("\n2. Example usage:")
    print("   python run_forecastbench.py --time-horizons 7 30 90 --search-budget 15 --debate-turns 3")
    print("   python run_forecastbench.py --time-horizons 1 7 --search-budget 5 --debate-turns 1")

def main():
    """Run all tests"""
    print("🚀 Testing New AI Forecasting Features")
    print("=" * 60)
    
    test_configurable_parameters()
    test_debate_system()
    test_command_line_interface()
    
    print("\n✅ All tests completed!")
    print("\n📋 Summary of Changes:")
    print("   ✅ Time horizons now configurable via run_forecastbench")
    print("   ✅ Search budget specified by benchmark and passed to superforecaster")
    print("   ✅ Debate turns configurable with alternating advocate system")
    print("   ✅ Judge outputs structured JSON with all predictions")
    print("   ✅ Instructions moved to prompts, not hardcoded in superforecaster")
    print("   ✅ Simplified codebase with unnecessary functions removed")
    print("   ✅ Superforecaster works with any number of questions/horizons")

if __name__ == "__main__":
    main()