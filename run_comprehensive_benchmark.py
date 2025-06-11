#!/usr/bin/env python3
"""
Comprehensive AI Forecasting Benchmark - Uses the best CrewAI multi-agent system with parallel processing
"""

import json
import random
import statistics
import traceback
import os
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
sys.path.append('src')

from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster
from ai_forecasts.utils.agent_logger import agent_logger

class ComprehensiveBenchmarkRunner:
    """Comprehensive benchmark runner using CrewAI multi-agent superforecaster system"""
    
    def __init__(self, max_workers: int = 10):
        # Set API key if not already set
        if not os.getenv("OPENROUTER_API_KEY"):
            os.environ["OPENROUTER_API_KEY"] = "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"
        
        # Set SERP API key if not already set
        if not os.getenv("SERP_API_KEY"):
            os.environ["SERP_API_KEY"] = "8b66ef544709847671ce739cb89b51601505777ffdfcd82f0246419387922342"
        
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.serp_api_key = os.getenv("SERP_API_KEY")
        self.max_workers = max_workers  # Control parallel execution
        
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        if not self.serp_api_key:
            raise ValueError("SERP_API_KEY environment variable is required")
        
        # Use Google News Superforecaster with SERP API integration
        print("🔄 Using Google News Superforecaster with SERP API")
        print("📰 This system will search Google News with timestamps from June 2024 to freeze date")
        print(f"⚡ Parallel processing enabled with {max_workers} concurrent workers")
        
        # We'll create superforecaster instances per worker to avoid conflicts
        self.use_google_news = True
        self.logger = agent_logger
        self.questions = []
    
    def _create_superforecaster_instance(self):
        """Create a new superforecaster instance for parallel processing"""
        return GoogleNewsSuperforecaster(
            openrouter_api_key=self.openrouter_api_key,
            serp_api_key=self.serp_api_key
        )
        
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
    
    def select_test_questions(self, num_questions: int = 10) -> List[Dict]:
        """Select diverse questions for comprehensive testing"""
        # Filter for high-quality, clear questions
        good_questions = []
        for q in self.questions:
            if (len(q["question"]) < 250 and 
                "Will" in q["question"] and 
                "?" in q["question"] and
                q["source"] in ["manifold", "metaculus"] and
                len(q["background"]) > 10):  # Ensure some background context
                good_questions.append(q)
        
        # Use random sampling for better coverage
        random.seed(42)
        return random.sample(good_questions, min(num_questions, len(good_questions)))
    
    def make_prediction(self, question: Dict) -> Dict[str, Any]:
        """Make prediction using the best available forecasting system"""
        
        print(f"\n🎯 Processing: {question['question']}")
        print(f"📅 Freeze date: {question['freeze_datetime']}")
        print(f"🎲 Actual outcome: {question['freeze_value']}")
        
        if self.use_google_news:
            print(f"📰 Starting Google News Superforecaster analysis...")
            print(f"📅 Searching Google News from June 2024 to: {question['freeze_datetime']}")
        
        try:
            # Create a fresh superforecaster instance for each prediction to avoid conflicts
            superforecaster = self._create_superforecaster_instance()
            
            # Start logging session
            self.logger.start_session("comprehensive_benchmark", {
                "question_id": question["id"],
                "question": question["question"],
                "method": "google_news_superforecaster",
                "freeze_date": question["freeze_datetime"].isoformat()
            })
            
            if self.use_google_news:
                # Use Google News Superforecaster system
                forecast_result = superforecaster.forecast_with_google_news(
                    question=question["question"],
                    background=question["background"],
                    cutoff_date=question["freeze_datetime"],
                    time_horizon="immediate",
                    is_benchmark=True  # This is a benchmark question
                )
                
                # Calculate methodology completeness score
                methodology_score = sum(forecast_result.methodology_components.values()) / len(forecast_result.methodology_components)
                
                methodology_details = {
                    "confidence_level": forecast_result.confidence_level,
                    "base_rate": forecast_result.base_rate,
                    "evidence_quality": forecast_result.evidence_quality,
                    "methodology_completeness": methodology_score,
                    "components_used": forecast_result.methodology_components,
                    "news_research_summary": forecast_result.news_research_summary,
                    "total_articles_found": forecast_result.total_articles_found,
                    "search_queries_used": len(forecast_result.search_queries_used),
                    "search_timeframe": forecast_result.search_timeframe
                }
                
                reasoning = forecast_result.reasoning
                full_analysis = forecast_result.full_analysis
                probability = forecast_result.probability
                
            else:

                probability = 0.5
                reasoning = "Fallback analysis"
                full_analysis = {"error": "Could not parse result"}
                
                methodology_details = {
                    "confidence_level": "medium",
                    "base_rate": 0.5,
                    "evidence_quality": 0.7,
                    "methodology_completeness": 0.8,
                    "components_used": {"basic_analysis": True}
                }
            
            print(f"🎯 AI Prediction: {probability:.3f}")
            print(f"📊 Brier Score: {(probability - question['freeze_value'])**2:.4f}")
            print(f"🔬 Confidence: {methodology_details['confidence_level']}")
            
            return {
                "question_id": question["id"],
                "question": question["question"],
                "prediction": probability,
                "actual_outcome": question["freeze_value"],
                "brier_score": (probability - question["freeze_value"])**2,
                "freeze_datetime": question["freeze_datetime"].isoformat(),
                "methodology": "google_news_superforecaster" if self.use_google_news else "basic_agent",
                "methodology_details": methodology_details,
                "reasoning": reasoning,
                "full_analysis": full_analysis,
                "agent_logs": self.logger.get_logs(),
                "processing_summary": self.logger.get_summary(),
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
                "methodology": "failed",
                "error": str(e),
                "agent_logs": self.logger.get_logs(),
                "success": False
            }
    
    def calculate_comprehensive_metrics(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive metrics including methodology analysis"""
        
        valid_predictions = [p for p in predictions if p.get("success", False)]
        
        if not valid_predictions:
            return {"error": "No valid predictions to evaluate"}
        
        # Basic Brier score metrics
        brier_scores = [p["brier_score"] for p in valid_predictions]
        mean_brier = statistics.mean(brier_scores)
        
        # Enhanced methodology metrics
        methodology_completeness = []
        evidence_qualities = []
        confidence_levels = []
        base_rates = []
        
        for pred in valid_predictions:
            details = pred.get("methodology_details", {})
            methodology_completeness.append(details.get("methodology_completeness", 0.5))
            evidence_qualities.append(details.get("evidence_quality", 0.5))
            
            # Convert confidence to numeric
            conf_str = details.get("confidence_level", "medium")
            conf_map = {"high": 0.9, "medium": 0.7, "low": 0.5}
            confidence_levels.append(conf_map.get(conf_str, 0.7))
            
            base_rates.append(details.get("base_rate", 0.5))
        
        # Calibration analysis
        calibration_error = self._calculate_calibration_error(valid_predictions)
        
        # Agent performance analysis
        agent_performance = self._analyze_agent_performance(valid_predictions)
        
        return {
            "brier_score": mean_brier,
            "num_predictions": len(valid_predictions),
            "individual_scores": brier_scores,
            "calibration_error": calibration_error,
            "methodology_quality": {
                "average_methodology_completeness": statistics.mean(methodology_completeness),
                "average_evidence_quality": statistics.mean(evidence_qualities),
                "average_confidence_level": statistics.mean(confidence_levels),
                "average_base_rate": statistics.mean(base_rates)
            },
            "performance_analysis": {
                "best_brier": min(brier_scores),
                "worst_brier": max(brier_scores),
                "brier_std": statistics.stdev(brier_scores) if len(brier_scores) > 1 else 0,
                "predictions_under_0_05": sum(1 for b in brier_scores if b < 0.05),
                "predictions_over_0_10": sum(1 for b in brier_scores if b > 0.10),
                "accuracy_at_extremes": self._calculate_extreme_accuracy(valid_predictions)
            },
            "agent_performance": agent_performance,
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
    
    def _calculate_extreme_accuracy(self, predictions: List[Dict]) -> Dict[str, float]:
        """Calculate accuracy for extreme predictions (< 0.2 or > 0.8)"""
        extreme_predictions = []
        for pred in predictions:
            if pred["prediction"] < 0.2 or pred["prediction"] > 0.8:
                extreme_predictions.append(pred)
        
        if not extreme_predictions:
            return {"count": 0, "accuracy": 0.0}
        
        correct = 0
        for pred in extreme_predictions:
            # For extreme predictions, check if direction is correct
            if pred["prediction"] < 0.2 and pred["actual_outcome"] == 0:
                correct += 1
            elif pred["prediction"] > 0.8 and pred["actual_outcome"] == 1:
                correct += 1
        
        return {
            "count": len(extreme_predictions),
            "accuracy": correct / len(extreme_predictions)
        }
    
    def _analyze_agent_performance(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Analyze performance of individual agents in the CrewAI system"""
        
        total_processing_time = 0
        agent_usage = {}
        
        for pred in predictions:
            # Analyze processing summary
            if "processing_summary" in pred:
                summary = pred["processing_summary"]
                total_processing_time += summary.get("total_time", 0)
                
                agents_used = summary.get("agents_used", [])
                for agent in agents_used:
                    agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        return {
            "average_processing_time": total_processing_time / len(predictions) if predictions else 0,
            "agent_usage_frequency": agent_usage,
            "most_used_agent": max(agent_usage.items(), key=lambda x: x[1])[0] if agent_usage else None
        }
    
    def run_comprehensive_benchmark(self, num_questions: int = 10) -> Dict[str, Any]:
        """Run comprehensive benchmark with CrewAI multi-agent superforecaster system"""
        
        print("🚀 Starting Comprehensive AI Forecasting Benchmark")
        print("📰 Using Google News Superforecaster System with SERP API (GPT-4o)")
        print("🕒 Searching Google News with timestamps from June 2024 to freeze dates")
        print("=" * 70)
        
        # Load and select questions
        self.load_human_questions()
        questions = self.select_test_questions(num_questions)
        
        if not questions:
            return {"error": "No suitable questions found"}
        
        print(f"\n📋 Selected {len(questions)} high-quality questions for testing")
        print("🔬 Agents: News Research Coordinator, Historical News Analyst, Current News Analyst, Expert News Aggregator, Contrarian News Researcher, Synthesis Expert")
        print("📰 Each question will be researched using Google News with precise timestamp filtering")
        
        # Make predictions using CrewAI system with parallel processing
        predictions = []
        
        print(f"\n⚡ Running {len(questions)} predictions in parallel with {self.max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all prediction tasks
            future_to_question = {
                executor.submit(self.make_prediction, question): question 
                for question in questions
            }
            
            # Collect results as they complete
            for i, future in enumerate(as_completed(future_to_question), 1):
                question = future_to_question[future]
                print(f"\n{'='*70}")
                print(f"Completed prediction {i}/{len(questions)}: {question['question'][:60]}...")
                
                try:
                    prediction = future.result()
                    predictions.append(prediction)
                except Exception as e:
                    print(f"❌ Error in parallel prediction: {str(e)}")
                    # Create error prediction
                    error_prediction = {
                        "question_id": question["id"],
                        "question": question["question"],
                        "prediction": 0.5,
                        "actual_outcome": question["freeze_value"],
                        "brier_score": (0.5 - question["freeze_value"])**2,
                        "freeze_datetime": question["freeze_datetime"].isoformat(),
                        "methodology": "failed_parallel",
                        "error": str(e),
                        "success": False
                    }
                    predictions.append(error_prediction)
        
        # Calculate comprehensive metrics
        metrics = self.calculate_comprehensive_metrics(predictions)
        
        # Compile results
        results = {
            "benchmark_type": "comprehensive_ai_forecasting_2024",
            "methodology": "crewai_multi_agent_superforecaster",
            "num_questions": len(questions),
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "questions_tested": [q["id"] for q in questions],
            "system_info": {
                "uses_gpt4o": True,
                "multi_agent_system": True,
                "crewai_framework": True,
                "superforecaster_methodology": True,
                "specialized_agents": [
                    "Base Rate Analyst",
                    "Evidence Researcher", 
                    "Perspective Analyst",
                    "Uncertainty Quantifier",
                    "Synthesis Expert"
                ],
                "methodology_components": [
                    "Reference Class Forecasting",
                    "Evidence Evaluation",
                    "Multiple Perspectives",
                    "Uncertainty Quantification",
                    "Expert Synthesis"
                ],
                "time_bound_constraints": True,
                "live_agent_logging": True
            }
        }
        
        return results

def main():
    """Run the comprehensive AI forecasting benchmark"""
    try:
        runner = ComprehensiveBenchmarkRunner()
        results = runner.run_comprehensive_benchmark(num_questions=10)
        
        # Print results
        print(f"\n" + "="*70)
        print(f"📊 COMPREHENSIVE AI FORECASTING BENCHMARK RESULTS")
        print("="*70)
        
        if "error" not in results["metrics"]:
            print(f"🎯 **BRIER SCORE: {results['metrics']['brier_score']:.4f}**")
            print(f"📏 **CALIBRATION ERROR: {results['metrics']['calibration_error']:.4f}**")
            print(f"✅ Valid Predictions: {results['metrics']['num_predictions']}")
            
            # Methodology quality
            quality = results['metrics']['methodology_quality']
            print(f"\n🔬 **METHODOLOGY QUALITY:**")
            print(f"   Methodology Completeness: {quality['average_methodology_completeness']:.3f}")
            print(f"   Evidence Quality: {quality['average_evidence_quality']:.3f}")
            print(f"   Confidence Level: {quality['average_confidence_level']:.3f}")
            print(f"   Base Rate Usage: {quality['average_base_rate']:.3f}")
            
            # Performance analysis
            perf = results['metrics']['performance_analysis']
            print(f"\n📈 **PERFORMANCE ANALYSIS:**")
            print(f"   Best Brier Score: {perf['best_brier']:.4f}")
            print(f"   Worst Brier Score: {perf['worst_brier']:.4f}")
            print(f"   Predictions < 0.05 Brier: {perf['predictions_under_0_05']}")
            print(f"   Predictions > 0.10 Brier: {perf['predictions_over_0_10']}")
            print(f"   Extreme Predictions Accuracy: {perf['accuracy_at_extremes']['accuracy']:.3f} ({perf['accuracy_at_extremes']['count']} predictions)")
            
            # Agent performance
            agent_perf = results['metrics']['agent_performance']
            print(f"\n🤖 **AGENT PERFORMANCE:**")
            print(f"   Average Processing Time: {agent_perf['average_processing_time']:.2f}s")
            print(f"   Most Used Agent: {agent_perf['most_used_agent']}")
            print(f"   Agent Usage: {agent_perf['agent_usage_frequency']}")
            
            print(f"\n📋 Individual Results:")
            for i, pred in enumerate(results["metrics"]["predictions"], 1):
                print(f"\n  {i}. {pred['question'][:80]}...")
                print(f"    🎯 Prediction: {pred['prediction']:.3f} | Actual: {pred['actual_outcome']:.3f} | Brier: {pred['brier_score']:.4f}")
                
                # Show methodology details if available
                if pred.get('methodology_details'):
                    md = pred['methodology_details']
                    base_rate = md.get('base_rate', 0.5)
                    evidence_quality = md.get('evidence_quality', 0.5)
                    methodology_completeness = md.get('methodology_completeness', 0.5)
                    
                    base_rate_str = f"{base_rate:.3f}" if base_rate is not None else "N/A"
                    evidence_str = f"{evidence_quality:.3f}" if evidence_quality is not None else "N/A"
                    methodology_str = f"{methodology_completeness:.3f}" if methodology_completeness is not None else "N/A"
                    
                    print(f"    📊 Confidence: {md.get('confidence_level', 'unknown')}, Base Rate: {base_rate_str}")
                    print(f"    🔬 Evidence Quality: {evidence_str}, Methodology: {methodology_str}")
                
                # Show reasoning if available
                if pred.get('reasoning'):
                    reasoning = pred['reasoning']
                    # Truncate very long reasoning for display
                    if len(reasoning) > 300:
                        reasoning = reasoning[:300] + "..."
                    print(f"    💭 Reasoning: {reasoning}")
                
                # Show full analysis summary if available
                if pred.get('full_analysis') and isinstance(pred['full_analysis'], dict):
                    analysis = pred['full_analysis']
                    if 'probability' in analysis and 'base_rate' in analysis:
                        base_rate = analysis.get('base_rate')
                        probability = analysis.get('probability', pred['prediction'])
                        
                        base_rate_str = f"{base_rate:.3f}" if base_rate is not None else "N/A"
                        probability_str = f"{probability:.3f}" if probability is not None else "N/A"
                        
                        print(f"    📈 Analysis: Base rate {base_rate_str} → Final {probability_str}")
                    
                    # Show key insights if available
                    if 'key_uncertainties' in analysis:
                        uncertainties = analysis['key_uncertainties']
                        if uncertainties and len(uncertainties) > 0:
                            print(f"    ❓ Key Uncertainties: {', '.join(uncertainties[:2])}")
                
                print()
        else:
            print(f"❌ Error: {results['metrics']['error']}")
        
        # Save results
        with open("comprehensive_benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to comprehensive_benchmark_results.json")
        return 0
        
    except Exception as e:
        print(f"❌ Comprehensive benchmark failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())