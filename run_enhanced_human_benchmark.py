#!/usr/bin/env python3
"""
Enhanced Human Benchmark Runner - Uses superforecaster methodology with web archive research
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

from ai_forecasts.agents.enhanced_orchestrator import EnhancedForecastOrchestrator
from ai_forecasts.utils.agent_logger import agent_logger
from ai_forecasts.models.schemas import ForecastRequest

class EnhancedHumanBenchmarkRunner:
    """Enhanced time-bound RAG pipeline using superforecaster methodology"""
    
    def __init__(self):
        self.orchestrator = EnhancedForecastOrchestrator()
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
    
    def select_diverse_questions(self, num_questions: int = 5) -> List[Dict]:
        """Select diverse questions for comprehensive testing"""
        # Filter for clear, well-formed questions
        good_questions = []
        for q in self.questions:
            if (len(q["question"]) < 300 and 
                "Will" in q["question"] and 
                "?" in q["question"] and
                q["source"] in ["manifold", "metaculus"]):
                good_questions.append(q)
        
        # Use random sampling for better coverage
        random.seed(42)
        return random.sample(good_questions, min(num_questions, len(good_questions)))
    
    def make_enhanced_prediction(self, question: Dict) -> Dict[str, Any]:
        """Make prediction using enhanced superforecaster methodology"""
        
        print(f"\n🎯 Processing: {question['question']}")
        print(f"📅 Freeze date: {question['freeze_datetime']}")
        print(f"🎲 Actual outcome: {question['freeze_value']}")
        print(f"🔍 Starting enhanced superforecaster analysis...")
        
        try:
            # Create enhanced forecast request
            request = ForecastRequest(
                outcomes_of_interest=[question["question"]],
                time_horizon="immediate",
                constraints=[f"Background: {question['background']}"] if question['background'] else []
            )
            
            # Process with enhanced methodology
            cutoff_date = question["freeze_datetime"]
            result = self.orchestrator.process_enhanced_request(
                request, 
                cutoff_date=cutoff_date,
                research_depth="comprehensive"
            )
            
            # Extract probability and methodology details
            probability = self._extract_probability(result, question["question"])
            methodology_details = result.get("methodology_details", {})
            
            print(f"🤖 AI Prediction: {probability:.3f}")
            print(f"📊 Brier Score: {(probability - question['freeze_value'])**2:.4f}")
            
            # Extract quality metrics
            research_quality = result.get("quality_metrics", {})
            
            return {
                "question_id": question["id"],
                "question": question["question"],
                "prediction": probability,
                "actual_outcome": question["freeze_value"],
                "brier_score": (probability - question["freeze_value"])**2,
                "freeze_datetime": question["freeze_datetime"].isoformat(),
                "methodology": "enhanced_superforecaster",
                "methodology_details": methodology_details,
                "quality_metrics": research_quality,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "question_id": question["id"],
                "question": question["question"],
                "prediction": 0.5,
                "actual_outcome": question["freeze_value"],
                "brier_score": (0.5 - question["freeze_value"])**2,
                "freeze_datetime": question["freeze_datetime"].isoformat(),
                "methodology": "enhanced_superforecaster_failed",
                "error": str(e),
                "success": False
            }
    
    def _extract_probability(self, result: Dict, question: str) -> float:
        """Extract probability from enhanced forecast result"""
        try:
            # Look for evaluations in targeted mode result
            if "evaluations" in result:
                for eval_item in result["evaluations"]:
                    return float(eval_item.get("probability", 0.5))
            
            # Look for outcomes in forecast mode result
            if "outcomes" in result:
                for outcome in result["outcomes"]:
                    return float(outcome.get("probability", 0.5))
            
            # Look for feasibility in strategy mode
            if "feasibility_probability" in result:
                return float(result["feasibility_probability"])
            
            # Default fallback
            return 0.5
            
        except Exception as e:
            print(f"Warning: Error extracting probability: {str(e)}")
            return 0.5
    
    def calculate_enhanced_metrics(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Calculate enhanced metrics including methodology analysis"""
        
        valid_predictions = [p for p in predictions if p.get("success", False)]
        
        if not valid_predictions:
            return {"error": "No valid predictions to evaluate"}
        
        # Basic Brier score metrics
        brier_scores = [p["brier_score"] for p in valid_predictions]
        mean_brier = statistics.mean(brier_scores)
        
        # Enhanced methodology metrics
        research_qualities = []
        validation_confidences = []
        methodology_rigors = []
        
        for pred in valid_predictions:
            quality_metrics = pred.get("quality_metrics", {})
            research_qualities.append(quality_metrics.get("research_quality", 0.5))
            validation_confidences.append(quality_metrics.get("validation_confidence", 0.5))
            methodology_rigors.append(quality_metrics.get("methodology_rigor", 0.5))
        
        # Calibration analysis
        calibration_error = self._calculate_calibration_error(valid_predictions)
        
        return {
            "brier_score": mean_brier,
            "num_predictions": len(valid_predictions),
            "individual_scores": brier_scores,
            "calibration_error": calibration_error,
            "methodology_quality": {
                "average_research_quality": statistics.mean(research_qualities),
                "average_validation_confidence": statistics.mean(validation_confidences),
                "average_methodology_rigor": statistics.mean(methodology_rigors)
            },
            "performance_analysis": {
                "best_brier": min(brier_scores),
                "worst_brier": max(brier_scores),
                "brier_std": statistics.stdev(brier_scores) if len(brier_scores) > 1 else 0,
                "predictions_under_0_05": sum(1 for b in brier_scores if b < 0.05),
                "predictions_over_0_10": sum(1 for b in brier_scores if b > 0.10)
            },
            "predictions": valid_predictions
        }
    
    def _calculate_calibration_error(self, predictions: List[Dict]) -> float:
        """Calculate calibration error (reliability)"""
        
        if len(predictions) < 3:
            return 0.0
        
        # Group predictions into bins
        bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        bin_counts = [0] * (len(bins) - 1)
        bin_correct = [0] * (len(bins) - 1)
        bin_confidence = [0] * (len(bins) - 1)
        
        for pred in predictions:
            prob = pred["prediction"]
            outcome = pred["actual_outcome"]
            
            # Find appropriate bin
            for i in range(len(bins) - 1):
                if bins[i] <= prob < bins[i + 1]:
                    bin_counts[i] += 1
                    bin_confidence[i] += prob
                    bin_correct[i] += outcome
                    break
        
        # Calculate calibration error
        calibration_error = 0.0
        total_predictions = len(predictions)
        
        for i in range(len(bins) - 1):
            if bin_counts[i] > 0:
                avg_confidence = bin_confidence[i] / bin_counts[i]
                avg_accuracy = bin_correct[i] / bin_counts[i]
                weight = bin_counts[i] / total_predictions
                calibration_error += weight * abs(avg_confidence - avg_accuracy)
        
        return calibration_error
    
    def run_enhanced_benchmark(self, num_questions: int = 5) -> Dict[str, Any]:
        """Run enhanced benchmark with superforecaster methodology"""
        
        print("🚀 Starting Enhanced Human ForecastingBench Benchmark")
        print("🧠 Using Superforecaster Methodology + Web Archive Research")
        print("=" * 70)
        
        # Load and select questions
        self.load_human_questions()
        questions = self.select_diverse_questions(num_questions)
        
        if not questions:
            return {"error": "No suitable questions found"}
        
        print(f"\n📋 Selected {len(questions)} questions for enhanced testing")
        
        # Make predictions using enhanced methodology
        predictions = []
        for i, question in enumerate(questions):
            print(f"\n{'='*70}")
            print(f"Question {i+1}/{len(questions)}")
            
            prediction = self.make_enhanced_prediction(question)
            predictions.append(prediction)
        
        # Calculate enhanced metrics
        metrics = self.calculate_enhanced_metrics(predictions)
        
        # Compile results
        results = {
            "benchmark_type": "enhanced_human_forecasting_2024",
            "methodology": "superforecaster_with_web_archive",
            "num_questions": len(questions),
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "questions_tested": [q["id"] for q in questions],
            "system_info": {
                "uses_gpt4o": True,
                "superforecaster_methodology": True,
                "web_archive_research": True,
                "time_bound_constraints": True,
                "validation_system": True
            }
        }
        
        return results

def main():
    """Run the enhanced human benchmark"""
    try:
        runner = EnhancedHumanBenchmarkRunner()
        results = runner.run_enhanced_benchmark(num_questions=5)
        
        # Print results
        print(f"\n" + "="*70)
        print(f"📊 ENHANCED BENCHMARK RESULTS")
        print("="*70)
        
        if "error" not in results["metrics"]:
            print(f"🎯 **BRIER SCORE: {results['metrics']['brier_score']:.4f}**")
            print(f"📏 **CALIBRATION ERROR: {results['metrics']['calibration_error']:.4f}**")
            print(f"✅ Valid Predictions: {results['metrics']['num_predictions']}")
            
            # Methodology quality
            quality = results['metrics']['methodology_quality']
            print(f"\n🔬 **METHODOLOGY QUALITY:**")
            print(f"   Research Quality: {quality['average_research_quality']:.3f}")
            print(f"   Validation Confidence: {quality['average_validation_confidence']:.3f}")
            print(f"   Methodology Rigor: {quality['average_methodology_rigor']:.3f}")
            
            # Performance analysis
            perf = results['metrics']['performance_analysis']
            print(f"\n📈 **PERFORMANCE ANALYSIS:**")
            print(f"   Best Brier Score: {perf['best_brier']:.4f}")
            print(f"   Worst Brier Score: {perf['worst_brier']:.4f}")
            print(f"   Predictions < 0.05 Brier: {perf['predictions_under_0_05']}")
            print(f"   Predictions > 0.10 Brier: {perf['predictions_over_0_10']}")
            
            print(f"\n📋 Individual Results:")
            for pred in results["metrics"]["predictions"]:
                print(f"  • {pred['question'][:80]}...")
                print(f"    Prediction: {pred['prediction']:.3f} | Actual: {pred['actual_outcome']:.3f} | Brier: {pred['brier_score']:.4f}")
                
                # Show methodology details if available
                if pred.get('quality_metrics'):
                    qm = pred['quality_metrics']
                    print(f"    Quality: Research={qm.get('research_quality', 0):.2f}, Validation={qm.get('validation_confidence', 0):.2f}")
                print()
        else:
            print(f"❌ Error: {results['metrics']['error']}")
        
        # Save results
        with open("enhanced_human_benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to enhanced_human_benchmark_results.json")
        return 0
        
    except Exception as e:
        print(f"❌ Enhanced benchmark failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())