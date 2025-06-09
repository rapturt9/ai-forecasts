"""Benchmark runner for evaluating AI forecasting system accuracy"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from dataclasses import dataclass
import requests
import time

from ..agents.orchestrator import ForecastOrchestrator
from ..models.schemas import ForecastRequest


@dataclass
class BenchmarkResult:
    """Results from running a single benchmark case"""
    case_id: str
    prediction: Dict[str, Any]
    ground_truth: Dict[str, Any]
    accuracy_metrics: Dict[str, float]
    execution_time: float
    error: Optional[str] = None


class BenchmarkRunner:
    """Runs benchmarks and evaluates forecasting system performance"""
    
    def __init__(self, orchestrator: ForecastOrchestrator):
        self.orchestrator = orchestrator
        self.results: List[BenchmarkResult] = []
    
    async def run_benchmark_suite(
        self, 
        benchmark_file: str,
        max_cases: Optional[int] = None
    ) -> Dict[str, Any]:
        """Run complete benchmark suite and return results"""
        
        # Load benchmark data
        with open(benchmark_file, 'r') as f:
            benchmark_data = json.load(f)
        
        cases = benchmark_data["benchmark_cases"]
        if max_cases:
            cases = cases[:max_cases]
        
        print(f"Running benchmark on {len(cases)} cases...")
        
        # Run each benchmark case
        results = []
        for i, case in enumerate(cases):
            print(f"Running case {i+1}/{len(cases)}: {case['case_id']}")
            
            result = await self._run_single_case(case)
            results.append(result)
            
            # Add delay to avoid rate limiting
            time.sleep(2)
        
        self.results = results
        
        # Calculate aggregate metrics
        aggregate_metrics = self._calculate_aggregate_metrics(results)
        
        # Generate report
        report = {
            "benchmark_info": {
                "total_cases": len(cases),
                "successful_cases": len([r for r in results if r.error is None]),
                "failed_cases": len([r for r in results if r.error is not None]),
                "run_date": datetime.now().isoformat()
            },
            "aggregate_metrics": aggregate_metrics,
            "individual_results": [self._result_to_dict(r) for r in results],
            "analysis": self._generate_analysis(results, aggregate_metrics)
        }
        
        return report
    
    async def _run_single_case(self, case: Dict[str, Any]) -> BenchmarkResult:
        """Run a single benchmark case"""
        start_time = time.time()
        
        try:
            # Create forecast request
            request = ForecastRequest(
                initial_conditions=case["initial_conditions"],
                outcomes_of_interest=[case["target_outcome"]],
                time_horizon=case["time_horizon"]
            )
            
            # Get prediction from system
            prediction = self.orchestrator.process_request(request)
            
            execution_time = time.time() - start_time
            
            # Calculate accuracy metrics
            accuracy_metrics = self._calculate_accuracy_metrics(
                prediction, 
                case["ground_truth"]
            )
            
            return BenchmarkResult(
                case_id=case["case_id"],
                prediction=prediction,
                ground_truth=case["ground_truth"],
                accuracy_metrics=accuracy_metrics,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return BenchmarkResult(
                case_id=case["case_id"],
                prediction={},
                ground_truth=case["ground_truth"],
                accuracy_metrics={},
                execution_time=execution_time,
                error=str(e)
            )
    
    def _calculate_accuracy_metrics(
        self, 
        prediction: Dict[str, Any], 
        ground_truth: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate accuracy metrics for a single prediction"""
        
        metrics = {}
        
        try:
            # Extract predicted probability
            predicted_prob = None
            if prediction.get("mode") == "targeted" and prediction.get("evaluations"):
                # Find the evaluation for our target outcome
                for eval_item in prediction["evaluations"]:
                    predicted_prob = eval_item.get("probability", 0.5)
                    break
            elif prediction.get("mode") == "forecast" and prediction.get("forecasts"):
                # Use the highest probability forecast
                predicted_prob = max(
                    forecast.get("probability", 0.5) 
                    for forecast in prediction["forecasts"]
                )
            
            if predicted_prob is None:
                predicted_prob = 0.5  # Default to 50% if no prediction found
            
            # Ground truth
            actual_outcome = ground_truth.get("resolution") == "YES"
            market_prob = ground_truth.get("final_probability", 0.5)
            
            # Brier Score (lower is better)
            brier_score = (predicted_prob - (1.0 if actual_outcome else 0.0)) ** 2
            metrics["brier_score"] = brier_score
            
            # Log Score (higher is better)
            epsilon = 1e-15  # Avoid log(0)
            prob_used = max(epsilon, min(1-epsilon, predicted_prob))
            if actual_outcome:
                log_score = np.log(prob_used)
            else:
                log_score = np.log(1 - prob_used)
            metrics["log_score"] = log_score
            
            # Calibration error (absolute difference from market)
            if market_prob is not None:
                calibration_error = abs(predicted_prob - market_prob)
                metrics["calibration_error"] = calibration_error
            
            # Binary accuracy (correct prediction)
            predicted_outcome = predicted_prob > 0.5
            binary_accuracy = 1.0 if predicted_outcome == actual_outcome else 0.0
            metrics["binary_accuracy"] = binary_accuracy
            
            # Confidence score
            confidence = abs(predicted_prob - 0.5) * 2  # 0 to 1 scale
            metrics["confidence"] = confidence
            
            # Market comparison (how much better/worse than market)
            if market_prob is not None:
                market_brier = (market_prob - (1.0 if actual_outcome else 0.0)) ** 2
                market_improvement = market_brier - brier_score
                metrics["market_improvement"] = market_improvement
            
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            metrics["error"] = str(e)
        
        return metrics
    
    def _calculate_aggregate_metrics(self, results: List[BenchmarkResult]) -> Dict[str, float]:
        """Calculate aggregate metrics across all results"""
        
        successful_results = [r for r in results if r.error is None and r.accuracy_metrics]
        
        if not successful_results:
            return {"error": "No successful results to analyze"}
        
        # Collect all metrics
        all_metrics = {}
        for metric_name in ["brier_score", "log_score", "calibration_error", "binary_accuracy", "confidence"]:
            values = [
                r.accuracy_metrics.get(metric_name) 
                for r in successful_results 
                if metric_name in r.accuracy_metrics
            ]
            
            if values:
                all_metrics[f"mean_{metric_name}"] = np.mean(values)
                all_metrics[f"std_{metric_name}"] = np.std(values)
                all_metrics[f"median_{metric_name}"] = np.median(values)
        
        # Overall performance metrics
        all_metrics["success_rate"] = len(successful_results) / len(results)
        
        # Average execution time
        execution_times = [r.execution_time for r in results]
        all_metrics["mean_execution_time"] = np.mean(execution_times)
        
        # Market comparison
        market_improvements = [
            r.accuracy_metrics.get("market_improvement") 
            for r in successful_results 
            if "market_improvement" in r.accuracy_metrics
        ]
        if market_improvements:
            all_metrics["mean_market_improvement"] = np.mean(market_improvements)
            all_metrics["market_beat_rate"] = np.mean([x > 0 for x in market_improvements])
        
        return all_metrics
    
    def _generate_analysis(
        self, 
        results: List[BenchmarkResult], 
        aggregate_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate analysis and insights from benchmark results"""
        
        analysis = {}
        
        # Performance summary
        mean_brier = aggregate_metrics.get("mean_brier_score")
        mean_accuracy = aggregate_metrics.get("mean_binary_accuracy")
        market_beat_rate = aggregate_metrics.get("market_beat_rate")
        
        if mean_brier is not None:
            if mean_brier < 0.2:
                performance_level = "Excellent"
            elif mean_brier < 0.25:
                performance_level = "Good"
            elif mean_brier < 0.3:
                performance_level = "Fair"
            else:
                performance_level = "Poor"
            
            analysis["performance_level"] = performance_level
        
        # Strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if mean_accuracy and mean_accuracy > 0.6:
            strengths.append("Good binary prediction accuracy")
        elif mean_accuracy and mean_accuracy < 0.5:
            weaknesses.append("Below-random binary accuracy")
        
        if market_beat_rate and market_beat_rate > 0.5:
            strengths.append("Outperforms market predictions on average")
        elif market_beat_rate and market_beat_rate < 0.4:
            weaknesses.append("Underperforms compared to market predictions")
        
        if aggregate_metrics.get("success_rate", 0) < 0.8:
            weaknesses.append("High failure rate in generating predictions")
        
        analysis["strengths"] = strengths
        analysis["weaknesses"] = weaknesses
        
        # Recommendations
        recommendations = []
        
        if mean_brier and mean_brier > 0.25:
            recommendations.append("Improve probability calibration")
        
        if aggregate_metrics.get("mean_confidence", 0) < 0.3:
            recommendations.append("Increase confidence in predictions when appropriate")
        
        if aggregate_metrics.get("success_rate", 0) < 0.9:
            recommendations.append("Improve system reliability and error handling")
        
        analysis["recommendations"] = recommendations
        
        return analysis
    
    def _result_to_dict(self, result: BenchmarkResult) -> Dict[str, Any]:
        """Convert BenchmarkResult to dictionary for JSON serialization"""
        return {
            "case_id": result.case_id,
            "prediction": result.prediction,
            "ground_truth": result.ground_truth,
            "accuracy_metrics": result.accuracy_metrics,
            "execution_time": result.execution_time,
            "error": result.error
        }
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to file"""
        if not self.results:
            print("No results to save")
            return
        
        report = {
            "benchmark_info": {
                "total_cases": len(self.results),
                "successful_cases": len([r for r in self.results if r.error is None]),
                "run_date": datetime.now().isoformat()
            },
            "aggregate_metrics": self._calculate_aggregate_metrics(self.results),
            "individual_results": [self._result_to_dict(r) for r in self.results]
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Benchmark results saved to {filename}")
        return filename


# Quick test function
async def run_quick_benchmark():
    """Run a quick benchmark test"""
    from ..utils.llm_client import LLMClient
    
    # Initialize system
    llm_client = LLMClient()
    orchestrator = ForecastOrchestrator(llm_client.get_client())
    runner = BenchmarkRunner(orchestrator)
    
    # Create a simple test case
    test_case = {
        "case_id": "test_001",
        "initial_conditions": "As of 2024-01-01: OpenAI has released GPT-4, competition in AI is increasing",
        "target_outcome": "Will OpenAI release GPT-5 by end of 2024?",
        "time_horizon": "1 year",
        "ground_truth": {
            "resolution": "NO",
            "final_probability": 0.3
        }
    }
    
    result = await runner._run_single_case(test_case)
    print(f"Test result: {result}")
    
    return result


if __name__ == "__main__":
    asyncio.run(run_quick_benchmark())