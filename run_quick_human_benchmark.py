#!/usr/bin/env python3
"""
Quick time-bound RAG pipeline for ForecastingBench human dataset
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
from ai_forecasts.models.schemas import ForecastRequest

class QuickHumanBenchmarkRunner:
    """Quick time-bound RAG pipeline for human forecasting benchmark"""
    
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
                "url": q_data.get("url", ""),
                "source": q_data.get("source", ""),
                "resolution_criteria": q_data.get("resolution_criteria", "")
            }
            
            # Only include questions with valid freeze datetime and value
            if freeze_dt and freeze_value is not None:
                self.questions.append(question)
        
        print(f"Loaded {len(self.questions)} valid questions from {filename}")
    
    def select_simple_questions(self, num_questions: int = 3) -> List[Dict]:
        """Select simple, clear questions for testing"""
        # Filter for simpler questions (shorter text, clear yes/no format)
        simple_questions = []
        for q in self.questions:
            if (len(q["question"]) < 200 and 
                "Will" in q["question"] and 
                "?" in q["question"] and
                q["source"] == "manifold"):
                simple_questions.append(q)
        
        # Use random sampling for better coverage
        random.seed(42)
        return random.sample(simple_questions, min(num_questions, len(simple_questions)))
    
    def make_simple_prediction(self, question: Dict) -> Dict[str, Any]:
        """Make a simple prediction without complex web research"""
        
        print(f"\n🎯 Processing: {question['question']}")
        print(f"📅 Freeze date: {question['freeze_datetime']}")
        print(f"🎲 Actual outcome: {question['freeze_value']}")
        
        try:
            # Create a simple targeted forecast request
            request = ForecastRequest(
                outcomes_of_interest=[question["question"]],
                time_horizon="immediate",
                constraints=[f"Background: {question['background']}"]
            )
            
            # Process with cutoff date
            cutoff_date = question["freeze_datetime"]
            result = self.orchestrator.process_request(request, cutoff_date=cutoff_date)
            
            # Extract probability
            probability = self._extract_probability(result, question["question"])
            
            print(f"🤖 AI Prediction: {probability:.3f}")
            print(f"📊 Brier Score: {(probability - question['freeze_value'])**2:.4f}")
            
            return {
                "question_id": question["id"],
                "question": question["question"],
                "prediction": probability,
                "actual_outcome": question["freeze_value"],
                "brier_score": (probability - question["freeze_value"])**2,
                "freeze_datetime": question["freeze_datetime"].isoformat(),
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                "question_id": question["id"],
                "question": question["question"],
                "prediction": 0.5,
                "actual_outcome": question["freeze_value"],
                "brier_score": (0.5 - question["freeze_value"])**2,
                "freeze_datetime": question["freeze_datetime"].isoformat(),
                "error": str(e),
                "success": False
            }
    
    def _extract_probability(self, result: Dict, question: str) -> float:
        """Extract probability from forecast result"""
        try:
            # Look for evaluations in targeted mode result
            if "evaluations" in result:
                for eval_item in result["evaluations"]:
                    return float(eval_item.get("probability", 0.5))
            
            # Look for outcomes in forecast mode result
            if "outcomes" in result:
                for outcome in result["outcomes"]:
                    return float(outcome.get("probability", 0.5))
            
            # Default fallback
            return 0.5
            
        except Exception as e:
            print(f"Warning: Error extracting probability: {str(e)}")
            return 0.5
    
    def calculate_brier_score(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Calculate Brier score and other metrics"""
        
        valid_predictions = [p for p in predictions if p.get("success", False)]
        
        if not valid_predictions:
            return {"error": "No valid predictions to evaluate"}
        
        brier_scores = [p["brier_score"] for p in valid_predictions]
        mean_brier = statistics.mean(brier_scores)
        
        return {
            "brier_score": mean_brier,
            "num_predictions": len(valid_predictions),
            "individual_scores": brier_scores,
            "predictions": valid_predictions
        }
    
    def run_quick_benchmark(self, num_questions: int = 10) -> Dict[str, Any]:
        """Run a quick benchmark with simple questions"""
        
        print("🚀 Starting Quick Human ForecastingBench Benchmark")
        print("=" * 60)
        
        # Load and select questions
        self.load_human_questions()
        questions = self.select_simple_questions(num_questions)
        
        if not questions:
            return {"error": "No suitable questions found"}
        
        print(f"\n📋 Selected {len(questions)} questions for testing")
        
        # Make predictions
        predictions = []
        for i, question in enumerate(questions):
            print(f"\n{'='*60}")
            print(f"Question {i+1}/{len(questions)}")
            
            prediction = self.make_simple_prediction(question)
            predictions.append(prediction)
        
        # Calculate metrics
        metrics = self.calculate_brier_score(predictions)
        
        # Compile results
        results = {
            "benchmark_type": "quick_human_forecasting_2024",
            "num_questions": len(questions),
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "questions_tested": [q["id"] for q in questions]
        }
        
        return results

def main():
    """Run the quick human benchmark"""
    try:
        runner = QuickHumanBenchmarkRunner()
        results = runner.run_quick_benchmark(num_questions=10)
        
        # Print results
        print(f"\n" + "="*60)
        print(f"📊 FINAL BENCHMARK RESULTS")
        print("="*60)
        
        if "error" not in results["metrics"]:
            print(f"🎯 **BRIER SCORE: {results['metrics']['brier_score']:.4f}**")
            print(f"✅ Valid Predictions: {results['metrics']['num_predictions']}")
            
            print(f"\n📋 Individual Results:")
            for pred in results["metrics"]["predictions"]:
                print(f"  • {pred['question'][:80]}...")
                print(f"    Prediction: {pred['prediction']:.3f} | Actual: {pred['actual_outcome']:.3f} | Brier: {pred['brier_score']:.4f}")
                print()
        else:
            print(f"❌ Error: {results['metrics']['error']}")
        
        # Save results
        with open("quick_human_benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to quick_human_benchmark_results.json")
        return 0
        
    except Exception as e:
        print(f"❌ Benchmark failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())