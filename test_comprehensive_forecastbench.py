#!/usr/bin/env python3
"""
Comprehensive ForecastingBench Test with Evaluation Metrics
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_forecasts.agents.orchestrator import ForecastOrchestrator
from ai_forecasts.benchmarks.forecastbench import ForecastBenchRunner


def main():
    print("🚀 Starting Comprehensive ForecastingBench Test")
    print("=" * 60)
    
    try:
        # Initialize orchestrator
        print("Initializing orchestrator...")
        orchestrator = ForecastOrchestrator()
        
        # Initialize ForecastingBench runner
        print("Initializing ForecastingBench runner...")
        runner = ForecastBenchRunner(orchestrator)
        
        # Run comprehensive test with 10 questions
        print("Running comprehensive test with 10 questions...")
        results = runner.run_quick_test(num_questions=10)
        
        print("\n📊 COMPREHENSIVE BENCHMARK RESULTS")
        print("=" * 60)
        print(f"Total Questions: {results['total_questions']}")
        print(f"Successful Predictions: {results['successful_predictions']}")
        print(f"Failed Predictions: {results['failed_predictions']}")
        print(f"Success Rate: {results['success_rate']:.1%}")
        
        # Calculate evaluation metrics
        if results['successful_predictions'] > 0:
            print(f"\n📈 EVALUATION METRICS")
            print("=" * 60)
            
            # Calculate average metrics
            total_brier = 0
            total_log_score = 0
            total_abs_error = 0
            valid_metrics = 0
            
            for result in results['individual_results']:
                if 'error' not in result and 'metrics' in result:
                    metrics = result['metrics']
                    if 'brier_score' in metrics and metrics['brier_score'] is not None:
                        total_brier += metrics['brier_score']
                        valid_metrics += 1
                    if 'log_score' in metrics and metrics['log_score'] is not None:
                        total_log_score += metrics['log_score']
                    if 'absolute_error' in metrics and metrics['absolute_error'] is not None:
                        total_abs_error += metrics['absolute_error']
            
            if valid_metrics > 0:
                avg_brier = total_brier / valid_metrics
                avg_log_score = total_log_score / valid_metrics
                avg_abs_error = total_abs_error / valid_metrics
                
                print(f"Average Brier Score: {avg_brier:.4f} (lower is better)")
                print(f"Average Log Score: {avg_log_score:.4f} (higher is better)")
                print(f"Average Absolute Error: {avg_abs_error:.4f} (lower is better)")
                
                # Calibration assessment
                if avg_brier < 0.25:
                    print("✅ Good calibration (Brier < 0.25)")
                elif avg_brier < 0.5:
                    print("⚠️  Moderate calibration (0.25 ≤ Brier < 0.5)")
                else:
                    print("❌ Poor calibration (Brier ≥ 0.5)")
        
        print(f"\n🔍 DETAILED RESULTS")
        print("=" * 60)
        
        for i, result in enumerate(results['individual_results']):
            if 'error' in result:
                print(f"{i+1}. ERROR: {result['error']}")
                continue
                
            print(f"\n{i+1}. {result['question'][:80]}...")
            
            freeze_val = result['freeze_value']
            if freeze_val == "N/A":
                print(f"   Ground Truth: N/A")
            else:
                freeze_val = float(freeze_val) if isinstance(freeze_val, str) else freeze_val
                print(f"   Ground Truth: {freeze_val:.3f}")
            
            if "prediction" in result and "evaluations" in result["prediction"]:
                pred_prob = result["prediction"]["evaluations"][0].get("probability", 0)
                print(f"   Predicted: {pred_prob:.3f}")
                
                if 'metrics' in result:
                    metrics = result['metrics']
                    if 'brier_score' in metrics and metrics['brier_score'] is not None:
                        print(f"   Brier Score: {metrics['brier_score']:.4f}")
                    if 'absolute_error' in metrics and metrics['absolute_error'] is not None:
                        print(f"   Absolute Error: {metrics['absolute_error']:.4f}")
        
        print(f"\n💾 Results saved to forecastbench_results.json")
        print(f"\n✅ Comprehensive ForecastingBench test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())