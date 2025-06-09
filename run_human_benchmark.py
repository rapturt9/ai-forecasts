#!/usr/bin/env python3
"""
Time-bound RAG pipeline for ForecastingBench human dataset
Implements proper Wayback Machine constraints and Brier score calculation
"""

import json
import random
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
sys.path.append('src')

from ai_forecasts.agents.orchestrator import ForecastOrchestrator
from ai_forecasts.utils.agent_logger import agent_logger

class HumanBenchmarkRunner:
    """Time-bound RAG pipeline for human forecasting benchmark"""
    
    def __init__(self):
        self.orchestrator = ForecastOrchestrator()
        self.logger = agent_logger
        self.questions = []
        
    def load_human_questions(self, filename: str = "forecastbench_human_2024.json") -> None:
        """Load questions from human benchmark dataset"""
        questions_path = Path(filename)
        if not questions_path.exists():
            raise FileNotFoundError(f"Questions file not found: {filename}")
        
        with open(questions_path, 'r') as f:
            data = json.load(f)
        
        self.questions = []
        for q_data in data["questions"]:
            # Parse datetime fields
            freeze_dt = None
            if q_data.get("freeze_datetime") and q_data["freeze_datetime"] != "N/A":
                try:
                    freeze_dt = datetime.fromisoformat(q_data["freeze_datetime"].replace('Z', '+00:00'))
                except:
                    freeze_dt = None
            
            market_open_dt = None
            if q_data.get("market_info_open_datetime") and q_data["market_info_open_datetime"] != "N/A":
                try:
                    market_open_dt = datetime.fromisoformat(q_data["market_info_open_datetime"].replace('Z', '+00:00'))
                except:
                    market_open_dt = None
            
            # Parse freeze value (outcome)
            freeze_value = None
            if q_data.get("freeze_datetime_value") and q_data["freeze_datetime_value"] != "N/A":
                try:
                    freeze_value = float(q_data["freeze_datetime_value"])
                except:
                    freeze_value = None
            
            question = {
                "id": q_data["id"],
                "question": q_data["question"],
                "background": q_data.get("background", ""),
                "freeze_datetime": freeze_dt,
                "freeze_value": freeze_value,
                "market_open_datetime": market_open_dt,
                "url": q_data.get("url", ""),
                "source": q_data.get("source", ""),
                "resolution_criteria": q_data.get("resolution_criteria", "")
            }
            
            # Only include questions with valid freeze datetime and value
            if freeze_dt and freeze_value is not None:
                self.questions.append(question)
                print(f"Loaded question: {question['id']} - {question['question'][:100]}...")
        
        self.logger.log("human_benchmark", f"Loaded {len(self.questions)} valid questions from {filename}")
    
    def select_random_questions(self, num_questions: int = 10, seed: int = 42) -> List[Dict]:
        """Select random questions for testing"""
        random.seed(seed)
        return random.sample(self.questions, min(num_questions, len(self.questions)))
    
    def make_time_bound_prediction(self, question: Dict) -> Dict[str, Any]:
        """Make a prediction using time-bound RAG with Wayback Machine constraints"""
        
        # Use freeze_datetime as the cutoff for web research
        cutoff_date = question["freeze_datetime"]
        
        self.logger.log("human_benchmark", 
                       f"Making prediction for: {question['id']} with cutoff: {cutoff_date}")
        
        # Create forecast request with time constraints
        from ai_forecasts.models.schemas import ForecastRequest
        
        request = ForecastRequest(
            outcomes_of_interest=[question["question"]],
            time_horizon="immediate",  # Since we're forecasting at freeze time
            constraints=[
                f"Research cutoff date: {cutoff_date.isoformat()}",
                f"Background: {question['background']}"
            ]
        )
        
        try:
            # Process with time-bound research
            self.logger.log("human_benchmark", f"Processing request with orchestrator...")
            result = self.orchestrator.process_request(request, cutoff_date=cutoff_date)
            self.logger.log("human_benchmark", f"Received result: {type(result)}")
            
            # Extract probability from result
            probability = self._extract_probability(result, question["question"])
            self.logger.log("human_benchmark", f"Extracted probability: {probability}")
            
            return {
                "question_id": question["id"],
                "question": question["question"],
                "prediction": probability,
                "actual_outcome": question["freeze_value"],
                "freeze_datetime": question["freeze_datetime"].isoformat(),
                "cutoff_date": cutoff_date.isoformat(),
                "result": result
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.logger.log("human_benchmark", f"Error making prediction: {str(e)}\n{error_details}")
            print(f"ERROR in prediction: {str(e)}")
            print(f"Full traceback: {error_details}")
            return {
                "question_id": question["id"],
                "question": question["question"],
                "prediction": 0.5,  # Default to 50% if error
                "actual_outcome": question["freeze_value"],
                "freeze_datetime": question["freeze_datetime"].isoformat(),
                "cutoff_date": cutoff_date.isoformat(),
                "error": str(e),
                "error_details": error_details
            }
    
    def _extract_probability(self, result: Dict, question: str) -> float:
        """Extract probability from forecast result"""
        try:
            # Look for evaluations in targeted mode result
            if "evaluations" in result:
                for eval_item in result["evaluations"]:
                    if question.lower() in eval_item.get("outcome", "").lower():
                        return float(eval_item.get("probability", 0.5))
            
            # Look for outcomes in forecast mode result
            if "outcomes" in result:
                for outcome in result["outcomes"]:
                    if question.lower() in outcome.get("description", "").lower():
                        return float(outcome.get("probability", 0.5))
            
            # Default fallback
            return 0.5
            
        except Exception as e:
            self.logger.log("human_benchmark", f"Error extracting probability: {str(e)}")
            return 0.5
    
    def calculate_brier_score(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Calculate Brier score and other metrics"""
        
        brier_scores = []
        valid_predictions = []
        
        for pred in predictions:
            if "error" not in pred and pred["actual_outcome"] is not None:
                # Brier score = (forecast - outcome)^2
                forecast = pred["prediction"]
                outcome = pred["actual_outcome"]
                brier = (forecast - outcome) ** 2
                brier_scores.append(brier)
                valid_predictions.append(pred)
        
        if not brier_scores:
            return {"error": "No valid predictions to evaluate"}
        
        # Calculate metrics
        mean_brier = statistics.mean(brier_scores)
        median_brier = statistics.median(brier_scores)
        
        # Calculate calibration (simplified)
        calibration_error = self._calculate_calibration_error(valid_predictions)
        
        return {
            "brier_score": mean_brier,
            "median_brier_score": median_brier,
            "num_predictions": len(valid_predictions),
            "calibration_error": calibration_error,
            "individual_scores": brier_scores,
            "predictions": valid_predictions
        }
    
    def _calculate_calibration_error(self, predictions: List[Dict]) -> float:
        """Calculate calibration error (simplified version)"""
        try:
            # Group predictions into bins
            bins = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            bin_errors = []
            
            for i in range(len(bins) - 1):
                bin_preds = [p for p in predictions 
                           if bins[i] <= p["prediction"] < bins[i+1]]
                
                if bin_preds:
                    avg_forecast = statistics.mean([p["prediction"] for p in bin_preds])
                    avg_outcome = statistics.mean([p["actual_outcome"] for p in bin_preds])
                    bin_error = abs(avg_forecast - avg_outcome)
                    bin_errors.append(bin_error * len(bin_preds))
            
            if bin_errors:
                return sum(bin_errors) / len(predictions)
            return 0.0
            
        except Exception:
            return 0.0
    
    def run_benchmark(self, num_questions: int = 10) -> Dict[str, Any]:
        """Run the complete time-bound RAG benchmark"""
        
        self.logger.log("human_benchmark", f"Starting benchmark with {num_questions} questions")
        
        # Load and select questions
        self.load_human_questions()
        questions = self.select_random_questions(num_questions)
        
        self.logger.log("human_benchmark", f"Selected {len(questions)} questions for testing")
        
        # Make predictions
        predictions = []
        for i, question in enumerate(questions):
            self.logger.log("human_benchmark", 
                           f"Processing question {i+1}/{len(questions)}: {question['id']}")
            
            prediction = self.make_time_bound_prediction(question)
            predictions.append(prediction)
        
        # Calculate metrics
        metrics = self.calculate_brier_score(predictions)
        
        # Compile results
        results = {
            "benchmark_type": "human_forecasting_2024",
            "num_questions": len(questions),
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "questions_tested": [q["id"] for q in questions]
        }
        
        self.logger.log("human_benchmark", "Benchmark completed")
        return results

def main():
    """Run the human benchmark"""
    print("🚀 Starting Human ForecastingBench Benchmark")
    print("=" * 60)
    
    try:
        runner = HumanBenchmarkRunner()
        results = runner.run_benchmark(num_questions=10)
        
        # Print results
        print(f"\n📊 BENCHMARK RESULTS")
        print("=" * 40)
        print(f"Questions tested: {results['num_questions']}")
        
        if "error" not in results["metrics"]:
            print(f"🎯 Brier Score: {results['metrics']['brier_score']:.4f}")
            print(f"📈 Median Brier: {results['metrics']['median_brier_score']:.4f}")
            print(f"🎪 Calibration Error: {results['metrics']['calibration_error']:.4f}")
            print(f"✅ Valid Predictions: {results['metrics']['num_predictions']}")
            
            # Show individual predictions
            print(f"\n📋 Individual Predictions:")
            for pred in results["metrics"]["predictions"]:
                brier = (pred["prediction"] - pred["actual_outcome"]) ** 2
                print(f"  {pred['question_id']}: {pred['prediction']:.3f} vs {pred['actual_outcome']:.3f} (Brier: {brier:.4f})")
        else:
            print(f"❌ Error: {results['metrics']['error']}")
        
        # Save results
        with open("human_benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to human_benchmark_results.json")
        return 0
        
    except Exception as e:
        print(f"❌ Benchmark failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())