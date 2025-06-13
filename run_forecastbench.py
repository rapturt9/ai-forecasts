#!/usr/bin/env python3
"""
ForecastBench Parallel Runner - Uses Google News Superforecaster with 4 time horizons
Evaluates on all 200 questions with proper Brier score calculation
"""

import json
import random
import statistics
import traceback
import os
import asyncio
import concurrent.futures
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
sys.path.append('src')

from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster
from ai_forecasts.utils.agent_logger import agent_logger

class ForecastBenchRunner:
    """ForecastBench runner using Google News Superforecaster with 4 time horizons"""
    
    # URLs for ForecastBench datasets
    QUESTIONS_URL = "https://github.com/forecastingresearch/forecastbench-datasets/blob/main/datasets/question_sets/2024-07-21-human.json"
    RESOLUTIONS_URL = "https://raw.githubusercontent.com/forecastingresearch/forecastbench-datasets/refs/heads/main/datasets/resolution_sets/2024-07-21_resolution_set.json"
    
    # Time horizons for predictions (in days)
    TIME_HORIZONS = [7, 30, 90, 180]
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None):
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key
        self.logger = agent_logger
        
    def load_forecastbench_questions(self) -> List[Dict]:
        """Load all 200 questions from ForecastBench GitHub repository"""
        try:
            # Convert GitHub blob URL to raw URL
            raw_url = self.QUESTIONS_URL.replace("github.com", "raw.githubusercontent.com").replace("/blob", "")
            
            self.logger.info(f"Loading questions from: {raw_url}")
            response = requests.get(raw_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract questions from the JSON structure
            if isinstance(data, dict) and 'questions' in data:
                questions = data['questions']
            elif isinstance(data, list):
                questions = data
            else:
                self.logger.error("Invalid ForecastBench questions format")
                return []
                
            self.logger.info(f"✅ Loaded {len(questions)} questions from ForecastBench dataset")
            return questions
            
        except Exception as e:
            self.logger.error(f"❌ Error loading ForecastBench questions: {e}")
            return []
    
    def load_resolution_data(self) -> Dict[str, Any]:
        """Load resolution data from ForecastBench GitHub repository"""
        try:
            self.logger.info(f"Loading resolutions from: {self.RESOLUTIONS_URL}")
            response = requests.get(self.RESOLUTIONS_URL, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract resolutions from the JSON structure
            if isinstance(data, dict) and 'resolutions' in data:
                resolutions = data['resolutions']
            elif isinstance(data, list):
                resolutions = data
            else:
                self.logger.error("Invalid resolution data format")
                return {}
                
            self.logger.info(f"✅ Loaded {len(resolutions)} resolutions")
            
            # Create lookup dictionary by question ID
            resolution_lookup = {}
            for resolution in resolutions:
                question_id = resolution.get('id')
                if question_id:
                    resolution_lookup[question_id] = resolution
                    
            return resolution_lookup
            
        except Exception as e:
            self.logger.error(f"❌ Error loading resolution data: {e}")
            return {}
    
    def process_single_question(self, question_data: Dict, question_idx: int, resolution_lookup: Dict, base_date: datetime) -> Dict:
        """Process a single question with 4 time horizon predictions"""
        try:
            # Initialize superforecaster for this thread
            superforecaster = GoogleNewsSuperforecaster(
                openrouter_api_key=self.openrouter_api_key,
                serp_api_key=self.serp_api_key
            )
            
            question = question_data.get('question', '')
            question_id = question_data.get('id', f"q_{question_idx}")
            
            self.logger.info(f"Processing question {question_idx + 1}: {question[:80]}...")
            
            # Generate predictions for each time horizon
            predictions = {}
            brier_scores = {}
            
            for horizon_days in self.TIME_HORIZONS:
                try:
                    # Calculate cutoff date for this horizon
                    cutoff_date = base_date + timedelta(days=horizon_days)
                    
                    # Generate forecast with cutoff date
                    result = superforecaster.forecast(question, cutoff_date=cutoff_date)
                    
                    # Store prediction
                    predictions[f"{horizon_days}d"] = {
                        'probability': result.probability,
                        'confidence': result.confidence_level,
                        'reasoning': result.reasoning[:200] + "..." if len(result.reasoning) > 200 else result.reasoning,
                        'base_rate': result.base_rate,
                        'evidence_quality': result.evidence_quality,
                        'cutoff_date': cutoff_date.strftime("%Y-%m-%d")
                    }
                    
                    # Calculate Brier score if resolution data available
                    brier_score = self.calculate_brier_score(question_id, result.probability, resolution_lookup, cutoff_date)
                    brier_scores[f"{horizon_days}d"] = brier_score
                    
                except Exception as e:
                    self.logger.warning(f"Error processing {horizon_days}d horizon for question {question_idx + 1}: {e}")
                    predictions[f"{horizon_days}d"] = {'error': str(e)}
                    brier_scores[f"{horizon_days}d"] = None
            
            return {
                'question_idx': question_idx,
                'question_id': question_id,
                'question': question,
                'predictions': predictions,
                'brier_scores': brier_scores,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error processing question {question_idx + 1}: {e}")
            return {
                'question_idx': question_idx,
                'question_id': question_data.get('id', f"q_{question_idx}"),
                'question': question_data.get('question', ''),
                'error': str(e),
                'success': False
            }
    
    def calculate_brier_score(self, question_id: str, prediction: float, resolution_lookup: Dict, cutoff_date: datetime) -> float:
        """Calculate Brier score by matching question ID and resolution date"""
        try:
            resolution = resolution_lookup.get(question_id)
            if not resolution:
                return None
                
            # Get resolution date and value
            resolution_date_str = resolution.get('resolution_date')
            resolution_value = resolution.get('resolution_value')
            
            if not resolution_date_str or resolution_value is None:
                return None
                
            # Parse resolution date
            resolution_date = datetime.strptime(resolution_date_str, "%Y-%m-%d")
            
            # Only calculate Brier score if resolution occurred after cutoff date
            if resolution_date <= cutoff_date:
                return None
                
            # Convert resolution value to binary outcome (1 if true, 0 if false)
            outcome = 1.0 if resolution_value else 0.0
            
            # Calculate Brier score: (prediction - outcome)^2
            brier_score = (prediction - outcome) ** 2
            return brier_score
            
        except Exception as e:
            self.logger.warning(f"Error calculating Brier score for question {question_id}: {e}")
            return None
    
    def run_parallel_benchmark(self, max_questions: int = 200, max_workers: int = 3) -> Dict[str, Any]:
        """Run ForecastBench evaluation with 4 time horizons in parallel"""
        self.logger.info(f"🚀 Starting ForecastBench evaluation with 4 time horizons")
        self.logger.info(f"   Questions: {max_questions}, Workers: {max_workers}")
        self.logger.info(f"   Time horizons: {self.TIME_HORIZONS} days")
        
        # Load questions and resolutions
        questions = self.load_forecastbench_questions()
        if not questions:
            return {"error": "Failed to load ForecastBench questions"}
            
        resolution_lookup = self.load_resolution_data()
        
        # Limit questions for testing (default 200 for full evaluation)
        questions = questions[:max_questions]
        
        # Base date for time horizon calculations (forecast due date)
        base_date = datetime(2024, 7, 21)
        
        results = []
        start_time = datetime.now()
        
        # Process questions in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_idx = {
                executor.submit(self.process_single_question, q, idx, resolution_lookup, base_date): idx 
                for idx, q in enumerate(questions)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_idx):
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        # Show progress with Brier scores for each horizon
                        brier_info = []
                        for horizon in self.TIME_HORIZONS:
                            brier = result['brier_scores'].get(f"{horizon}d")
                            if brier is not None:
                                brier_info.append(f"{horizon}d:{brier:.3f}")
                        brier_str = f" (Brier: {', '.join(brier_info)})" if brier_info else ""
                        self.logger.info(f"✅ Completed question {result['question_idx'] + 1}/{len(questions)}{brier_str}")
                    else:
                        self.logger.error(f"❌ Failed question {result['question_idx'] + 1}/{len(questions)}")
                        
                except Exception as e:
                    idx = future_to_idx[future]
                    self.logger.error(f"❌ Exception in question {idx + 1}: {e}")
                    results.append({
                        'question_idx': idx,
                        'error': str(e),
                        'success': False
                    })
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate comprehensive statistics
        successful_results = [r for r in results if r['success']]
        success_rate = len(successful_results) / len(results) if results else 0
        
        # Calculate Brier scores by time horizon
        horizon_stats = {}
        for horizon in self.TIME_HORIZONS:
            horizon_key = f"{horizon}d"
            brier_scores = []
            predictions = []
            
            for result in successful_results:
                brier = result['brier_scores'].get(horizon_key)
                if brier is not None:
                    brier_scores.append(brier)
                    
                pred = result['predictions'].get(horizon_key, {}).get('probability')
                if pred is not None:
                    predictions.append(pred)
            
            horizon_stats[horizon_key] = {
                'avg_brier_score': statistics.mean(brier_scores) if brier_scores else None,
                'brier_score_count': len(brier_scores),
                'avg_prediction': statistics.mean(predictions) if predictions else None,
                'prediction_count': len(predictions)
            }
        
        # Overall statistics
        total_predictions = sum(len([r for r in successful_results if r['predictions'].get(f"{h}d")]) for h in self.TIME_HORIZONS)
        total_brier_scores = sum(len([r for r in successful_results if r['brier_scores'].get(f"{h}d") is not None]) for h in self.TIME_HORIZONS)
        
        summary = {
            'base_date': base_date.strftime("%Y-%m-%d"),
            'time_horizons': self.TIME_HORIZONS,
            'total_questions': len(questions),
            'successful_forecasts': len(successful_results),
            'success_rate': success_rate,
            'duration_seconds': duration,
            'questions_per_minute': (len(questions) / duration) * 60 if duration > 0 else 0,
            'total_predictions': total_predictions,
            'total_brier_scores': total_brier_scores,
            'horizon_statistics': horizon_stats,
            'results': results
        }
        
        # Log comprehensive results
        self.logger.info(f"🎯 ForecastBench Evaluation Complete!")
        self.logger.info(f"   Questions processed: {len(successful_results)}/{len(questions)} ({success_rate:.1%})")
        self.logger.info(f"   Total predictions: {total_predictions}")
        self.logger.info(f"   Total Brier scores: {total_brier_scores}")
        self.logger.info(f"   Duration: {duration:.1f}s ({summary['questions_per_minute']:.1f} questions/minute)")
        
        # Log Brier scores by time horizon
        for horizon in self.TIME_HORIZONS:
            horizon_key = f"{horizon}d"
            stats = horizon_stats[horizon_key]
            if stats['avg_brier_score'] is not None:
                self.logger.info(f"   {horizon}-day Brier Score: {stats['avg_brier_score']:.3f} (n={stats['brier_score_count']})")
            else:
                self.logger.info(f"   {horizon}-day Brier Score: N/A (no resolutions)")
        
        return summary

def main():
    """Main function to run ForecastBench evaluation"""
    # Get API keys
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    serp_api_key = os.getenv('SERP_API_KEY')
    
    if not openrouter_api_key:
        print("❌ OPENROUTER_API_KEY environment variable required")
        return
    
    # Create runner
    runner = ForecastBenchRunner(
        openrouter_api_key=openrouter_api_key,
        serp_api_key=serp_api_key
    )
    
    # Run benchmark (default: all 200 questions, 3 workers)
    results = runner.run_parallel_benchmark(max_questions=200, max_workers=3)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"forecastbench_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📊 Results saved to: {output_file}")

if __name__ == "__main__":
    main()