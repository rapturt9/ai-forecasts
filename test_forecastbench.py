#!/usr/bin/env python3
"""
Test script for ForecastingBench benchmark system
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_forecasts.agents.orchestrator import ForecastOrchestrator
from ai_forecasts.benchmarks.forecastbench import ForecastBenchRunner


def main():
    """Run ForecastingBench test"""
    
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable not set")
        return 1
    
    print("🚀 Starting ForecastingBench Test")
    print("=" * 50)
    
    try:
        # Initialize orchestrator
        print("Initializing orchestrator...")
        orchestrator = ForecastOrchestrator()
        
        # Initialize benchmark runner
        print("Initializing ForecastingBench runner...")
        runner = ForecastBenchRunner(orchestrator)
        
        # Run quick test
        print("Running quick test with 3 questions...")
        results = runner.run_quick_test(num_questions=3)
        
        # Display results
        print("\n📊 BENCHMARK RESULTS")
        print("=" * 50)
        
        summary = results.get("summary", {})
        print(f"Total Questions: {summary.get('total_questions', 0)}")
        print(f"Successful Predictions: {summary.get('successful_predictions', 0)}")
        print(f"Failed Predictions: {summary.get('failed_predictions', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        
        metrics = results.get("metrics", {})
        if "error" not in metrics:
            print(f"\n📈 PERFORMANCE METRICS")
            print(f"Mean Brier Score: {metrics.get('mean_brier_score', 0):.4f}")
            print(f"Mean Absolute Error: {metrics.get('mean_absolute_error', 0):.4f}")
            print(f"Accuracy within 10%: {metrics.get('accuracy_within_10_percent', 0):.1%}")
            print(f"Accuracy within 20%: {metrics.get('accuracy_within_20_percent', 0):.1%}")
        
        # Show individual results
        print(f"\n🔍 INDIVIDUAL RESULTS")
        print("=" * 50)
        
        for i, result in enumerate(results.get("results", [])[:3]):  # Show first 3
            if "error" in result:
                print(f"{i+1}. ERROR: {result['error']}")
                continue
                
            print(f"{i+1}. {result['question']}")
            freeze_val = result['freeze_value']
            if freeze_val == "N/A":
                print(f"   Freeze Value: N/A")
            else:
                freeze_val = float(freeze_val) if isinstance(freeze_val, str) else freeze_val
                print(f"   Freeze Value: {freeze_val:.3f}")
            
            if "prediction" in result and "outcomes" in result["prediction"]:
                pred_prob = result["prediction"]["outcomes"][0].get("probability", 0)
                print(f"   Predicted: {pred_prob:.3f}")
                
                if "evaluation" in result:
                    eval_data = result["evaluation"]
                    if "error" not in eval_data:
                        print(f"   Brier Score: {eval_data.get('brier_score', 0):.4f}")
                        print(f"   Absolute Error: {eval_data.get('absolute_error', 0):.4f}")
            print()
        
        # Save results
        output_file = "forecastbench_results.json"
        runner.save_results(results, output_file)
        print(f"💾 Results saved to {output_file}")
        
        print("\n✅ ForecastingBench test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during benchmark: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())