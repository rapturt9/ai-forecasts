#!/usr/bin/env python3
"""
ForecastBench Parallel Runner - Uses Google News Superforecaster in parallel
"""

import json
import random
import statistics
import traceback
import os
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
sys.path.append('src')

from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster
from ai_forecasts.utils.agent_logger import agent_logger

class ForecastBenchRunner:
    """ForecastBench runner using Google News Superforecaster with parallel processing"""
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None):
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key
        self.logger = agent_logger
        
    def load_forecastbench_data(self, file_path: str = "forecastbench_human_2024.json") -> List[Dict]:
        """Load ForecastBench dataset"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.logger.info(f"Loaded {len(data)} questions from ForecastBench")
            return data
        except Exception as e:
            self.logger.error(f"Error loading ForecastBench data: {e}")
            return []
    
    def process_single_question(self, question_data: Dict, question_idx: int) -> Dict:
        """Process a single question with the superforecaster"""
        try:
            # Initialize superforecaster for this thread
            superforecaster = GoogleNewsSuperforecaster(
                openrouter_api_key=self.openrouter_api_key,
                serp_api_key=self.serp_api_key
            )
            
            question = question_data.get('question', '')
            self.logger.info(f"Processing question {question_idx + 1}: {question[:100]}...")
            
            # Generate forecast
            result = superforecaster.forecast(question)
            
            return {
                'question_idx': question_idx,
                'question': question,
                'forecast_probability': result.probability,
                'confidence_level': result.confidence_level,
                'reasoning': result.reasoning,
                'base_rate': result.base_rate,
                'evidence_quality': result.evidence_quality,
                'news_sources_count': len(result.news_sources),
                'total_articles': result.total_articles_found,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error processing question {question_idx + 1}: {e}")
            return {
                'question_idx': question_idx,
                'question': question_data.get('question', ''),
                'error': str(e),
                'success': False
            }
    
    def run_parallel_benchmark(self, max_questions: int = 50, max_workers: int = 4) -> Dict[str, Any]:
        """Run ForecastBench evaluation in parallel"""
        self.logger.info(f"🚀 Starting ForecastBench parallel evaluation (max_questions={max_questions}, workers={max_workers})")
        
        # Load data
        questions = self.load_forecastbench_data()
        if not questions:
            return {"error": "Failed to load ForecastBench data"}
        
        # Limit questions
        questions = questions[:max_questions]
        
        results = []
        start_time = datetime.now()
        
        # Process questions in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_idx = {
                executor.submit(self.process_single_question, q, idx): idx 
                for idx, q in enumerate(questions)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_idx):
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        self.logger.info(f"✅ Completed question {result['question_idx'] + 1}/{len(questions)}")
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
        
        # Calculate statistics
        successful_results = [r for r in results if r['success']]
        success_rate = len(successful_results) / len(results) if results else 0
        
        if successful_results:
            probabilities = [r['forecast_probability'] for r in successful_results]
            avg_probability = statistics.mean(probabilities)
            confidence_levels = [r['confidence_level'] for r in successful_results]
            
            # Count confidence levels
            confidence_counts = {}
            for conf in confidence_levels:
                confidence_counts[conf] = confidence_counts.get(conf, 0) + 1
        else:
            avg_probability = 0
            confidence_counts = {}
        
        summary = {
            'total_questions': len(questions),
            'successful_forecasts': len(successful_results),
            'success_rate': success_rate,
            'duration_seconds': duration,
            'questions_per_minute': (len(questions) / duration) * 60 if duration > 0 else 0,
            'average_probability': avg_probability,
            'confidence_distribution': confidence_counts,
            'results': results
        }
        
        self.logger.info(f"🎯 ForecastBench Evaluation Complete!")
        self.logger.info(f"   Success Rate: {success_rate:.1%}")
        self.logger.info(f"   Duration: {duration:.1f}s")
        self.logger.info(f"   Rate: {summary['questions_per_minute']:.1f} questions/minute")
        
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
    
    # Run benchmark
    results = runner.run_parallel_benchmark(max_questions=20, max_workers=3)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"forecastbench_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📊 Results saved to: {output_file}")

if __name__ == "__main__":
    main()