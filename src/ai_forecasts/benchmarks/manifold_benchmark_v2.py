"""Improved Manifold Markets Benchmark with Date-Based Evaluation"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from ..agents.orchestrator import ForecastOrchestrator
from ..models.schemas import ForecastRequest


@dataclass
class BenchmarkCase:
    """A single benchmark case with start and resolve dates"""
    case_id: str
    title: str
    description: str
    start_date: str  # When the prediction should be made
    resolve_date: str  # When the outcome was determined
    resolved_value: str  # YES/NO or specific outcome
    category: str
    time_horizon_days: int
    
    def to_forecast_request(self) -> ForecastRequest:
        """Convert to a forecast request"""
        # Calculate time horizon from start to resolve date
        start = datetime.fromisoformat(self.start_date.replace('/', '-'))
        resolve = datetime.fromisoformat(self.resolve_date.replace('/', '-'))
        days_diff = (resolve - start).days
        
        if days_diff <= 7:
            horizon = f"{days_diff} days"
        elif days_diff <= 60:
            horizon = f"{days_diff // 7} weeks"
        elif days_diff <= 365:
            horizon = f"{days_diff // 30} months"
        else:
            horizon = f"{days_diff // 365} years"
        
        return ForecastRequest(
            outcomes_of_interest=[self.title],
            time_horizon=horizon,
            constraints=[]
        )


class ManifoldBenchmarkV2:
    """Improved benchmark system using resolved Manifold Markets questions"""
    
    def __init__(self, orchestrator: ForecastOrchestrator):
        self.orchestrator = orchestrator
        self.benchmark_cases = self._load_benchmark_cases()
    
    def _load_benchmark_cases(self) -> List[BenchmarkCase]:
        """Load benchmark cases from resolved Manifold Markets questions"""
        
        cases = [
            BenchmarkCase(
                case_id="portugal_spain_uefa_2025",
                title="Will Portugal beat Spain in UEFA Nations League Final?",
                description="Team A wins / No: Team B wins / Match winner only after extra-time and penalty shootout if applicable.",
                start_date="2025-06-06",
                resolve_date="2025-06-09", 
                resolved_value="YES",
                category="sports",
                time_horizon_days=3
            ),
            BenchmarkCase(
                case_id="ai_consciousness_survey_2026",
                title="Will a major US survey by end of 2026 show that >1% of respondents believe AI systems are conscious?",
                description="Survey by recognized US polling organization, academic institution, or reputable research firm with sample size of at least 1,000 US respondents.",
                start_date="2025-04-24",
                resolve_date="2025-05-25",
                resolved_value="YES", 
                category="ai_survey",
                time_horizon_days=31
            ),
            BenchmarkCase(
                case_id="best_ai_model_may_2025",
                title="Which company has best AI model end of May 2025? (Chatbot Arena Leaderboard)",
                description="Based on Chatbot Arena Leaderboard rankings at end of May 2025.",
                start_date="2025-05-01",
                resolve_date="2025-06-01",
                resolved_value="Google",
                category="ai_models",
                time_horizon_days=31
            ),
            # Additional cases can be added here
            BenchmarkCase(
                case_id="gpt5_release_prediction",
                title="Will GPT-5 be released by OpenAI before 2026?",
                description="Official release of GPT-5 model by OpenAI, not just announcement or preview.",
                start_date="2025-01-01",
                resolve_date="2025-12-31",
                resolved_value="UNKNOWN",  # Future case for testing
                category="ai_models",
                time_horizon_days=365
            ),
            BenchmarkCase(
                case_id="ai_regulation_us_2025",
                title="Will the US pass comprehensive AI regulation by end of 2025?",
                description="Federal legislation specifically targeting AI development and deployment.",
                start_date="2025-01-01", 
                resolve_date="2025-12-31",
                resolved_value="UNKNOWN",  # Future case for testing
                category="regulation",
                time_horizon_days=365
            )
        ]
        
        return cases
    
    def run_benchmark(self, use_resolved_only: bool = True) -> Dict[str, Any]:
        """Run benchmark on all cases"""
        
        results = {
            "benchmark_run_at": datetime.now().isoformat(),
            "total_cases": len(self.benchmark_cases),
            "case_results": [],
            "summary_metrics": {}
        }
        
        resolved_cases = []
        
        for case in self.benchmark_cases:
            if use_resolved_only and case.resolved_value == "UNKNOWN":
                continue
                
            print(f"Running benchmark case: {case.title}")
            
            # Run prediction with cutoff date (only information available at start date)
            case_result = self._run_single_case(case)
            results["case_results"].append(case_result)
            
            if case.resolved_value != "UNKNOWN":
                resolved_cases.append(case_result)
        
        # Calculate summary metrics for resolved cases
        if resolved_cases:
            results["summary_metrics"] = self._calculate_summary_metrics(resolved_cases)
        
        results["resolved_cases_count"] = len(resolved_cases)
        
        return results
    
    def _run_single_case(self, case: BenchmarkCase) -> Dict[str, Any]:
        """Run a single benchmark case"""
        
        start_time = datetime.now()
        
        # Convert to forecast request
        request = case.to_forecast_request()
        
        try:
            # Run prediction with cutoff date (simulating knowledge only up to start date)
            prediction_result = self.orchestrator.process_request(
                request, 
                use_validation=True,
                cutoff_date=case.start_date
            )
            
            success = True
            error_message = None
            
        except Exception as e:
            prediction_result = None
            success = False
            error_message = str(e)
        
        end_time = datetime.now()
        
        # Extract prediction for the specific outcome
        predicted_probability = None
        if prediction_result and "evaluations" in prediction_result:
            for eval_item in prediction_result["evaluations"]:
                if case.title.lower() in eval_item.get("outcome", "").lower():
                    predicted_probability = eval_item.get("probability", None)
                    break
        
        # Calculate accuracy if resolved
        accuracy_score = None
        if case.resolved_value != "UNKNOWN" and predicted_probability is not None:
            if case.resolved_value == "YES":
                # For YES outcomes, accuracy is how close we got to 1.0
                accuracy_score = 1.0 - abs(1.0 - predicted_probability)
            elif case.resolved_value == "NO":
                # For NO outcomes, accuracy is how close we got to 0.0
                accuracy_score = 1.0 - abs(0.0 - predicted_probability)
            else:
                # For specific outcomes (like "Google"), we'd need more complex scoring
                # For now, assume binary scoring
                accuracy_score = 0.8 if predicted_probability > 0.5 else 0.2
        
        return {
            "case_id": case.case_id,
            "title": case.title,
            "category": case.category,
            "start_date": case.start_date,
            "resolve_date": case.resolve_date,
            "time_horizon_days": case.time_horizon_days,
            "resolved_value": case.resolved_value,
            "predicted_probability": predicted_probability,
            "accuracy_score": accuracy_score,
            "success": success,
            "error_message": error_message,
            "prediction_time_seconds": (end_time - start_time).total_seconds(),
            "prediction_result": prediction_result
        }
    
    def _calculate_summary_metrics(self, resolved_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics across resolved cases"""
        
        successful_cases = [case for case in resolved_cases if case["success"]]
        cases_with_accuracy = [case for case in successful_cases if case["accuracy_score"] is not None]
        
        if not cases_with_accuracy:
            return {
                "success_rate": len(successful_cases) / len(resolved_cases) if resolved_cases else 0,
                "average_accuracy": 0,
                "cases_evaluated": 0
            }
        
        # Calculate metrics
        success_rate = len(successful_cases) / len(resolved_cases)
        average_accuracy = sum(case["accuracy_score"] for case in cases_with_accuracy) / len(cases_with_accuracy)
        average_prediction_time = sum(case["prediction_time_seconds"] for case in successful_cases) / len(successful_cases)
        
        # Category breakdown
        category_performance = {}
        for case in cases_with_accuracy:
            category = case["category"]
            if category not in category_performance:
                category_performance[category] = []
            category_performance[category].append(case["accuracy_score"])
        
        category_averages = {
            category: sum(scores) / len(scores) 
            for category, scores in category_performance.items()
        }
        
        # Time horizon analysis
        short_term_cases = [case for case in cases_with_accuracy if case["time_horizon_days"] <= 7]
        medium_term_cases = [case for case in cases_with_accuracy if 7 < case["time_horizon_days"] <= 90]
        long_term_cases = [case for case in cases_with_accuracy if case["time_horizon_days"] > 90]
        
        return {
            "success_rate": success_rate,
            "average_accuracy": average_accuracy,
            "average_prediction_time_seconds": average_prediction_time,
            "cases_evaluated": len(cases_with_accuracy),
            "category_performance": category_averages,
            "time_horizon_analysis": {
                "short_term_accuracy": sum(case["accuracy_score"] for case in short_term_cases) / len(short_term_cases) if short_term_cases else None,
                "medium_term_accuracy": sum(case["accuracy_score"] for case in medium_term_cases) / len(medium_term_cases) if medium_term_cases else None,
                "long_term_accuracy": sum(case["accuracy_score"] for case in long_term_cases) / len(long_term_cases) if long_term_cases else None,
                "short_term_count": len(short_term_cases),
                "medium_term_count": len(medium_term_cases),
                "long_term_count": len(long_term_cases)
            }
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save benchmark results to file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"manifold_benchmark_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Benchmark results saved to {filename}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a summary of benchmark results"""
        
        print("\n" + "="*60)
        print("MANIFOLD MARKETS BENCHMARK RESULTS")
        print("="*60)
        
        print(f"Total Cases: {results['total_cases']}")
        print(f"Resolved Cases Evaluated: {results['resolved_cases_count']}")
        print(f"Benchmark Run At: {results['benchmark_run_at']}")
        
        if results["summary_metrics"]:
            metrics = results["summary_metrics"]
            print(f"\nOVERALL PERFORMANCE:")
            print(f"Success Rate: {metrics['success_rate']:.1%}")
            print(f"Average Accuracy: {metrics['average_accuracy']:.1%}")
            print(f"Average Prediction Time: {metrics['average_prediction_time_seconds']:.2f}s")
            
            if metrics["category_performance"]:
                print(f"\nCATEGORY PERFORMANCE:")
                for category, accuracy in metrics["category_performance"].items():
                    print(f"  {category}: {accuracy:.1%}")
            
            horizon_analysis = metrics["time_horizon_analysis"]
            print(f"\nTIME HORIZON ANALYSIS:")
            if horizon_analysis["short_term_accuracy"]:
                print(f"  Short-term (≤7 days): {horizon_analysis['short_term_accuracy']:.1%} ({horizon_analysis['short_term_count']} cases)")
            if horizon_analysis["medium_term_accuracy"]:
                print(f"  Medium-term (8-90 days): {horizon_analysis['medium_term_accuracy']:.1%} ({horizon_analysis['medium_term_count']} cases)")
            if horizon_analysis["long_term_accuracy"]:
                print(f"  Long-term (>90 days): {horizon_analysis['long_term_accuracy']:.1%} ({horizon_analysis['long_term_count']} cases)")
        
        print(f"\nCASE DETAILS:")
        for case_result in results["case_results"]:
            status = "✅" if case_result["success"] else "❌"
            accuracy = f"{case_result['accuracy_score']:.1%}" if case_result["accuracy_score"] else "N/A"
            print(f"  {status} {case_result['title'][:50]}... | Accuracy: {accuracy}")
        
        print("="*60)


def run_manifold_benchmark():
    """Convenience function to run the benchmark"""
    
    # Initialize orchestrator
    orchestrator = ForecastOrchestrator()
    
    # Create and run benchmark
    benchmark = ManifoldBenchmarkV2(orchestrator)
    results = benchmark.run_benchmark(use_resolved_only=True)
    
    # Print and save results
    benchmark.print_summary(results)
    benchmark.save_results(results)
    
    return results


if __name__ == "__main__":
    run_manifold_benchmark()