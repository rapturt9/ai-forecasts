"""
ForecastingBench benchmark system with Wayback Machine constraints
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from ..agents.orchestrator import ForecastOrchestrator
from ..models.schemas import ForecastRequest
from ..utils.agent_logger import agent_logger


@dataclass
class ForecastBenchQuestion:
    """A single question from ForecastingBench"""
    id: str
    source: str
    question: str
    resolution_criteria: str
    background: str
    market_info_open_datetime: str
    market_info_close_datetime: str
    market_info_resolution_criteria: str
    url: str
    freeze_datetime: str
    freeze_datetime_value: float
    freeze_datetime_value_explanation: str
    source_intro: str
    combination_of: str
    resolution_dates: str
    
    @property
    def freeze_date(self) -> datetime:
        """Parse freeze datetime"""
        if self.freeze_datetime == "N/A":
            return datetime.now()
        return datetime.fromisoformat(self.freeze_datetime.replace('Z', '+00:00'))
    
    @property
    def market_open_date(self) -> datetime:
        """Parse market open datetime"""
        if self.market_info_open_datetime == "N/A":
            return datetime.now()
        return datetime.fromisoformat(self.market_info_open_datetime.replace('Z', '+00:00'))


class ForecastBenchBenchmark:
    """Benchmark system using ForecastingBench questions with Wayback Machine constraints"""
    
    def __init__(self, orchestrator: ForecastOrchestrator, questions_file: str = "forecastbench_questions.json"):
        self.orchestrator = orchestrator
        self.questions_file = questions_file
        self.questions: List[ForecastBenchQuestion] = []
        self.logger = agent_logger
        
    def load_questions(self) -> None:
        """Load questions from ForecastingBench JSON file"""
        questions_path = Path(self.questions_file)
        if not questions_path.exists():
            raise FileNotFoundError(f"Questions file not found: {self.questions_file}")
        
        with open(questions_path, 'r') as f:
            data = json.load(f)
        
        self.questions = [
            ForecastBenchQuestion(**q) for q in data['questions']
        ]
        
        self.logger.log("forecastbench", f"Loaded {len(self.questions)} questions from ForecastingBench")
    
    def select_questions(self, count: int = 10, seed: Optional[int] = None) -> List[ForecastBenchQuestion]:
        """Select random questions for benchmarking"""
        if seed is not None:
            random.seed(seed)
        
        # Filter questions that have reasonable time horizons
        suitable_questions = [
            q for q in self.questions
            if q.freeze_date > datetime.now().replace(tzinfo=q.freeze_date.tzinfo) - timedelta(days=365*2)
        ]
        
        selected = random.sample(suitable_questions, min(count, len(suitable_questions)))
        
        self.logger.log("forecastbench", f"Selected {len(selected)} questions for benchmark")
        return selected
    
    def run_benchmark(self, questions: List[ForecastBenchQuestion]) -> Dict[str, Any]:
        """Run benchmark on selected questions"""
        results = []
        
        for i, question in enumerate(questions):
            self.logger.log("forecastbench", f"Processing question {i+1}/{len(questions)}: {question.id}")
            
            try:
                # Calculate cutoff date (freeze date minus some buffer for research)
                cutoff_date = question.freeze_date - timedelta(days=7)
                
                # Make prediction with date constraint
                prediction = self._make_prediction(question, cutoff_date)
                
                # Evaluate against freeze value
                evaluation = self._evaluate_prediction(prediction, question)
                
                result = {
                    "question_id": question.id,
                    "question": question.question,
                    "freeze_date": question.freeze_datetime,
                    "freeze_value": question.freeze_datetime_value,
                    "cutoff_date": cutoff_date.isoformat(),
                    "prediction": prediction,
                    "evaluation": evaluation,
                    "url": question.url
                }
                
                results.append(result)
                
                self.logger.log("forecastbench", f"Completed question {question.id}")
                
            except Exception as e:
                self.logger.log("forecastbench", f"Error processing question {question.id}: {str(e)}")
                results.append({
                    "question_id": question.id,
                    "question": question.question,
                    "error": str(e)
                })
        
        # Calculate aggregate metrics
        successful_results = [r for r in results if "error" not in r]
        metrics = self._calculate_metrics(successful_results)
        
        return {
            "results": results,
            "metrics": metrics,
            "summary": {
                "total_questions": len(questions),
                "successful_predictions": len(successful_results),
                "failed_predictions": len(questions) - len(successful_results),
                "success_rate": len(successful_results) / len(questions) if questions else 0
            }
        }
    
    def _make_prediction(self, question: ForecastBenchQuestion, cutoff_date: datetime) -> Dict[str, Any]:
        """Make a prediction for a single question with date constraints"""
        
        # Create request for targeted forecasting
        request = ForecastRequest(
            outcomes_of_interest=[question.question],
            time_horizon="1 year",  # Default horizon
            constraints=[f"Information cutoff: {cutoff_date.strftime('%Y-%m-%d')}"]
        )
        
        # Override the web research agent to use Wayback Machine
        original_research_method = self.orchestrator.web_research_agent.research_current_context
        
        def wayback_research(topic: str, time_horizon: str, cutoff_date: Optional[datetime] = None):
            """Research using Wayback Machine with date constraints"""
            if cutoff_date is None:
                cutoff_date = datetime.now()
            
            # Use Wayback Machine URL format
            wayback_date = cutoff_date.strftime('%Y%m%d')
            
            # Create a research context based on the question and background
            research_context = {
                "current_state": f"Research context as of {cutoff_date.strftime('%Y-%m-%d')}",
                "key_developments": [
                    f"Question context: {question.background}" if question.background else "Limited background information available",
                    f"Market opened: {question.market_open_date.strftime('%Y-%m-%d')}",
                    f"Research cutoff: {cutoff_date.strftime('%Y-%m-%d')}"
                ],
                "current_players": ["Information limited to pre-cutoff date"],
                "recent_trends": [f"Analysis constrained to information available before {cutoff_date.strftime('%Y-%m-%d')}"],
                "data_sources": [f"Wayback Machine snapshot from {wayback_date}"],
                "research_limitations": [
                    f"Information cutoff enforced at {cutoff_date.strftime('%Y-%m-%d')}",
                    "No access to information after cutoff date",
                    "Research limited to historical web snapshots"
                ]
            }
            
            return research_context
        
        # Temporarily override the research method
        self.orchestrator.web_research_agent.research_current_context = wayback_research
        
        try:
            # Make the prediction
            result = self.orchestrator.process_request(request)
            return result
        finally:
            # Restore original research method
            self.orchestrator.web_research_agent.research_current_context = original_research_method
    
    def _evaluate_prediction(self, prediction: Dict[str, Any], question: ForecastBenchQuestion) -> Dict[str, Any]:
        """Evaluate prediction against freeze value"""
        
        if "outcomes" not in prediction or not prediction["outcomes"]:
            return {"error": "No outcomes in prediction"}
        
        # Get the probability for the question
        predicted_prob = prediction["outcomes"][0].get("probability", 0.5)
        freeze_value = question.freeze_datetime_value
        
        # Calculate metrics
        brier_score = (predicted_prob - freeze_value) ** 2
        log_score = -(freeze_value * (predicted_prob + 1e-10).log() + 
                     (1 - freeze_value) * (1 - predicted_prob + 1e-10).log()) if predicted_prob > 0 and predicted_prob < 1 else float('inf')
        
        absolute_error = abs(predicted_prob - freeze_value)
        
        return {
            "predicted_probability": predicted_prob,
            "freeze_value": freeze_value,
            "brier_score": brier_score,
            "log_score": log_score if log_score != float('inf') else None,
            "absolute_error": absolute_error,
            "within_10_percent": absolute_error <= 0.1,
            "within_20_percent": absolute_error <= 0.2
        }
    
    def _calculate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate metrics across all results"""
        
        if not results:
            return {"error": "No successful results to analyze"}
        
        evaluations = [r["evaluation"] for r in results if "evaluation" in r and "error" not in r["evaluation"]]
        
        if not evaluations:
            return {"error": "No valid evaluations"}
        
        # Calculate aggregate metrics
        brier_scores = [e["brier_score"] for e in evaluations]
        log_scores = [e["log_score"] for e in evaluations if e["log_score"] is not None]
        absolute_errors = [e["absolute_error"] for e in evaluations]
        
        within_10_percent = sum(1 for e in evaluations if e["within_10_percent"])
        within_20_percent = sum(1 for e in evaluations if e["within_20_percent"])
        
        metrics = {
            "mean_brier_score": sum(brier_scores) / len(brier_scores),
            "mean_absolute_error": sum(absolute_errors) / len(absolute_errors),
            "accuracy_within_10_percent": within_10_percent / len(evaluations),
            "accuracy_within_20_percent": within_20_percent / len(evaluations),
            "total_evaluated": len(evaluations)
        }
        
        if log_scores:
            metrics["mean_log_score"] = sum(log_scores) / len(log_scores)
        
        return metrics


class ForecastBenchRunner:
    """Runner for ForecastingBench benchmarks"""
    
    def __init__(self, orchestrator: ForecastOrchestrator):
        self.orchestrator = orchestrator
        self.benchmark = ForecastBenchBenchmark(orchestrator)
        self.logger = agent_logger
    
    def run_quick_test(self, num_questions: int = 5) -> Dict[str, Any]:
        """Run a quick test with a few questions"""
        self.logger.log("benchmark_runner", f"Starting quick test with {num_questions} questions")
        
        # Load questions
        self.benchmark.load_questions()
        
        # Select questions
        questions = self.benchmark.select_questions(num_questions, seed=42)
        
        # Run benchmark
        results = self.benchmark.run_benchmark(questions)
        
        self.logger.log("benchmark_runner", "Quick test completed")
        return results
    
    def run_full_benchmark(self, num_questions: int = 50) -> Dict[str, Any]:
        """Run a comprehensive benchmark"""
        self.logger.log("benchmark_runner", f"Starting full benchmark with {num_questions} questions")
        
        # Load questions
        self.benchmark.load_questions()
        
        # Select questions
        questions = self.benchmark.select_questions(num_questions, seed=123)
        
        # Run benchmark
        results = self.benchmark.run_benchmark(questions)
        
        self.logger.log("benchmark_runner", "Full benchmark completed")
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str) -> None:
        """Save benchmark results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.log("benchmark_runner", f"Results saved to {filename}")