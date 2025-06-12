#!/usr/bin/env python3
"""
Test script for benchmark functionality without requiring real API calls
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_benchmark_data_loading():
    """Test that we can load the benchmark data correctly"""
    from run_forecastbench import ForecastBenchRunner
    
    # Create a test runner
    runner = ForecastBenchRunner(
        openrouter_api_key="test_key",
        serp_api_key="test_key"
    )
    
    # Load the data
    questions, forecast_due_date = runner.load_forecastbench_data()
    
    print(f"✅ Loaded {len(questions)} questions")
    print(f"✅ Forecast due date: {forecast_due_date}")
    
    if questions:
        first_question = questions[0]
        print(f"✅ First question: {first_question['question']}")
        print(f"✅ Ground truth value: {first_question.get('freeze_datetime_value', 'N/A')}")
        print(f"✅ Freeze datetime: {first_question.get('freeze_datetime', 'N/A')}")
    
    # Test that forecast_due_date is before current date (for benchmark validity)
    due_date = datetime.strptime(forecast_due_date, "%Y-%m-%d")
    current_date = datetime.now()
    
    if due_date < current_date:
        print(f"✅ Forecast due date ({forecast_due_date}) is in the past - good for benchmarking")
    else:
        print(f"⚠️ Forecast due date ({forecast_due_date}) is in the future")
    
    return True

def test_brier_score_calculation():
    """Test Brier score calculation"""
    # Test cases: (forecast, ground_truth, expected_brier)
    test_cases = [
        (0.7, 0.75, 0.0025),  # Close prediction
        (0.5, 1.0, 0.25),     # Uncertain prediction, event happened
        (0.9, 0.1, 0.64),     # Overconfident wrong prediction
        (0.3, 0.3, 0.0),      # Perfect prediction
    ]
    
    for forecast, ground_truth, expected in test_cases:
        brier = (forecast - ground_truth) ** 2
        assert abs(brier - expected) < 0.001, f"Brier score calculation failed: {brier} != {expected}"
        print(f"✅ Brier score test passed: forecast={forecast}, truth={ground_truth}, brier={brier:.3f}")
    
    return True

def test_date_restriction_logic():
    """Test that date restriction logic is working"""
    from ai_forecasts.utils.google_news_tool import CachedGoogleNewsTool
    
    # Create a tool with a cutoff date
    tool = CachedGoogleNewsTool(serp_api_key="test_key")
    
    # Set a benchmark cutoff date
    cutoff_date = "2024-07-21"
    tool.set_benchmark_cutoff_date(cutoff_date)
    
    # Test the effective timeframe calculation
    effective_timeframe = tool._get_effective_timeframe(cutoff_date)
    
    print(f"✅ Cutoff date: {cutoff_date}")
    print(f"✅ Effective end date: {effective_timeframe['end']}")
    print(f"✅ Original cutoff: {effective_timeframe.get('original_cutoff', 'N/A')}")
    
    # The effective end date should be 1 day before the cutoff
    from datetime import datetime, timedelta
    cutoff_dt = datetime.fromisoformat(cutoff_date)
    expected_end_dt = cutoff_dt - timedelta(days=1)
    expected_end_str = expected_end_dt.strftime("%m/%d/%Y")
    
    assert effective_timeframe['end'] == expected_end_str, f"Date restriction failed: {effective_timeframe['end']} != {expected_end_str}"
    print(f"✅ Date restriction working correctly: searches limited to before {effective_timeframe['end']}")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing AI Forecasting Benchmark Functionality")
    print("=" * 60)
    
    try:
        print("\n1. Testing benchmark data loading...")
        test_benchmark_data_loading()
        
        print("\n2. Testing Brier score calculation...")
        test_brier_score_calculation()
        
        print("\n3. Testing date restriction logic...")
        test_date_restriction_logic()
        
        print("\n✅ All tests passed! Benchmark functionality is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)