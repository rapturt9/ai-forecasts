#!/usr/bin/env python3
"""
Enhanced ForecastBench Runner - Combines corrected data loading with comprehensive question context
Provides all question information to the superforecaster for improved accuracy
"""

import json
import statistics
import traceback
import os
import asyncio
import concurrent.futures
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

class EnhancedForecastBenchRunner:
    """Enhanced ForecastBench runner with comprehensive question context and corrected Brier score calculation"""
    
    # Local files for ForecastBench datasets
    QUESTIONS_FILE = "forecastbench_human_2024.json"
    RESOLUTIONS_FILE = "forecast_human_resolution_2024.json"
    
    # Time horizons for predictions (in days)
    TIME_HORIZONS = [7, 30, 90, 180]
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None):
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key
        self.logger = agent_logger
        
    def load_local_data(self) -> Tuple[List[Dict], Dict[str, Any]]:
        """Load questions and resolutions from local JSON files"""
        try:
            # Load questions
            with open(self.QUESTIONS_FILE, 'r') as f:
                questions_data = json.load(f)
            
            # Load resolutions
            with open(self.RESOLUTIONS_FILE, 'r') as f:
                resolutions_data = json.load(f)
            
            questions = questions_data['questions']
            self.logger.info(f"✅ Loaded {len(questions)} questions from local file")
            self.logger.info(f"✅ Loaded {len(resolutions_data['resolutions'])} resolutions from local file")
            
            return questions, resolutions_data
            
        except Exception as e:
            self.logger.error(f"❌ Error loading local data: {e}")
            return [], {}
    
    def get_resolution_for_question_and_date(self, question_id: str, resolution_date: str, resolutions_data: Dict) -> float:
        """Get the resolution value for a specific question ID and date"""
        if 'resolutions' not in resolutions_data:
            return None
            
        for resolution in resolutions_data['resolutions']:
            if (resolution['id'] == question_id and 
                resolution['resolution_date'] == resolution_date):
                return resolution['resolved_to']
        return None
    
    def create_comprehensive_context(self, question_data: Dict) -> str:
        """Create comprehensive context from all available question information"""
        context_parts = []
        
        # Main question
        context_parts.append(f"QUESTION: {question_data.get('question', '')}")
        
        # Source and context
        if question_data.get('source'):
            context_parts.append(f"SOURCE: {question_data['source']}")
        
        if question_data.get('source_intro'):
            context_parts.append(f"SOURCE CONTEXT: {question_data['source_intro']}")
        
        # Resolution criteria
        if question_data.get('resolution_criteria'):
            context_parts.append(f"RESOLUTION CRITERIA: {question_data['resolution_criteria']}")
        
        # Background information
        if question_data.get('background'):
            context_parts.append(f"BACKGROUND: {question_data['background']}")
        
        # Market information
        if question_data.get('market_info_open_datetime'):
            context_parts.append(f"MARKET OPENED: {question_data['market_info_open_datetime']}")
        
        if question_data.get('market_info_close_datetime'):
            context_parts.append(f"MARKET CLOSES: {question_data['market_info_close_datetime']}")
        
        # Freeze information (current market state)
        if question_data.get('freeze_datetime'):
            context_parts.append(f"CURRENT MARKET STATE AS OF: {question_data['freeze_datetime']}")
        
        if question_data.get('freeze_datetime_value'):
            context_parts.append(f"CURRENT MARKET PROBABILITY: {question_data['freeze_datetime_value']}")
        
        if question_data.get('freeze_datetime_value_explanation'):
            context_parts.append(f"MARKET PROBABILITY EXPLANATION: {question_data['freeze_datetime_value_explanation']}")
        
        # URL for reference
        if question_data.get('url'):
            context_parts.append(f"REFERENCE URL: {question_data['url']}")
        
        # Additional market criteria
        if question_data.get('market_info_resolution_criteria') and question_data['market_info_resolution_criteria'] != 'N/A':
            context_parts.append(f"MARKET RESOLUTION CRITERIA: {question_data['market_info_resolution_criteria']}")
        
        # Combination information
        if question_data.get('combination_of') and question_data['combination_of'] != 'N/A':
            context_parts.append(f"COMBINATION OF: {question_data['combination_of']}")
        
        # Resolution dates
        if question_data.get('resolution_dates') and question_data['resolution_dates'] != 'N/A':
            context_parts.append(f"RESOLUTION DATES: {question_data['resolution_dates']}")
        
        return "\n\n".join(context_parts)
    
    def process_single_question(self, question_data: Dict, question_idx: int, resolutions_data: Dict, base_date: datetime) -> Dict:
        """Process a single question with 4 time horizon predictions using enhanced context"""
        try:
            # Initialize superforecaster for this thread
            superforecaster = GoogleNewsSuperforecaster(
                openrouter_api_key=self.openrouter_api_key,
                serp_api_key=self.serp_api_key
            )
            
            question = question_data.get('question', '')
            question_id = question_data.get('id', f"q_{question_idx}")
            
            # Create comprehensive context from all question information
            comprehensive_context = self.create_comprehensive_context(question_data)
            
            self.logger.info(f"Processing question {question_idx + 1}: {question[:80]}...")
            self.logger.info(f"Comprehensive context length: {len(comprehensive_context)} characters")
            
            # Calculate resolution dates for all time horizons
            resolution_dates = []
            for horizon_days in self.TIME_HORIZONS:
                res_date = base_date + timedelta(days=horizon_days)
                resolution_dates.append(res_date.strftime('%Y-%m-%d'))
            
            # Generate predictions for each time horizon
            predictions = {}
            brier_scores = {}
            actual_values = {}
            
            for i, (horizon_days, resolution_date) in enumerate(zip(self.TIME_HORIZONS, resolution_dates)):
                try:
                    # Calculate cutoff date for this horizon
                    cutoff_date = base_date + timedelta(days=horizon_days)
                    
                    # Generate forecast with comprehensive context and cutoff date
                    result = superforecaster.forecast_with_google_news(
                        question=question,
                        background=comprehensive_context,  # Pass all context as background
                        cutoff_date=cutoff_date,
                        is_benchmark=True
                    )
                    
                    # Get actual resolution value
                    actual_value = self.get_resolution_for_question_and_date(question_id, resolution_date, resolutions_data)
                    
                    # Calculate Brier score if resolution data available
                    brier_score = None
                    if actual_value is not None:
                        brier_score = (result.probability - actual_value) ** 2
                    
                    # Store prediction
                    horizon_key = f"{horizon_days}d"
                    predictions[horizon_key] = {
                        'probability': result.probability,
                        'confidence': result.confidence_level,
                        'reasoning': result.reasoning[:500] + "..." if len(result.reasoning) > 500 else result.reasoning,
                        'base_rate': result.base_rate,
                        'evidence_quality': result.evidence_quality,
                        'cutoff_date': cutoff_date.strftime("%Y-%m-%d"),
                        'resolution_date': resolution_date,
                        'news_sources_count': len(result.news_sources),
                        'search_queries_used': result.search_queries_used,
                        'total_articles_found': result.total_articles_found
                    }
                    
                    brier_scores[horizon_key] = brier_score
                    actual_values[horizon_key] = actual_value
                    
                    self.logger.info(f"  ✅ {horizon_days}d horizon: prob={result.probability:.3f}, actual={actual_value}, brier={brier_score:.3f}" if brier_score is not None else f"  ✅ {horizon_days}d horizon: prob={result.probability:.3f}, actual={actual_value}")
                    
                except Exception as e:
                    self.logger.warning(f"Error processing {horizon_days}d horizon for question {question_idx + 1}: {e}")
                    predictions[f"{horizon_days}d"] = {'error': str(e)}
                    brier_scores[f"{horizon_days}d"] = None
                    actual_values[f"{horizon_days}d"] = None
            
            return {
                'question_idx': question_idx,
                'question_id': question_id,
                'question': question,
                'freeze_value': question_data.get('freeze_datetime_value'),
                'comprehensive_context_length': len(comprehensive_context),
                'predictions': predictions,
                'brier_scores': brier_scores,
                'actual_values': actual_values,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error processing question {question_idx + 1}: {e}")
            traceback.print_exc()
            return {
                'question_idx': question_idx,
                'question_id': question_data.get('id', f"q_{question_idx}"),
                'question': question_data.get('question', ''),
                'error': str(e),
                'success': False
            }
    
    def run_parallel_benchmark(self, max_questions: int = 200, max_workers: int = 3) -> Dict[str, Any]:
        """Run enhanced ForecastBench evaluation with comprehensive context"""
        self.logger.info(f"🚀 Starting Enhanced ForecastBench evaluation with comprehensive context")
        self.logger.info(f"   Questions: {max_questions}, Workers: {max_workers}")
        self.logger.info(f"   Time horizons: {self.TIME_HORIZONS} days")
        
        # Load questions and resolutions from local files
        questions, resolutions_data = self.load_local_data()
        if not questions:
            return {"error": "Failed to load ForecastBench questions"}
            
        if not resolutions_data:
            return {"error": "Failed to load resolution data"}
        
        # Limit questions for testing
        questions = questions[:max_questions]
        
        # Base date for time horizon calculations (forecast due date)
        base_date = datetime(2024, 7, 21)
        
        results = []
        start_time = datetime.now()
        
        # Process questions in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_idx = {
                executor.submit(self.process_single_question, q, idx, resolutions_data, base_date): idx 
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
        all_brier_scores = []
        
        for horizon in self.TIME_HORIZONS:
            horizon_key = f"{horizon}d"
            brier_scores = []
            predictions = []
            actual_values = []
            
            for result in successful_results:
                brier = result['brier_scores'].get(horizon_key)
                if brier is not None:
                    brier_scores.append(brier)
                    all_brier_scores.append(brier)
                    
                pred = result['predictions'].get(horizon_key, {}).get('probability')
                if pred is not None:
                    predictions.append(pred)
                    
                actual = result['actual_values'].get(horizon_key)
                if actual is not None:
                    actual_values.append(actual)
            
            horizon_stats[horizon_key] = {
                'avg_brier_score': statistics.mean(brier_scores) if brier_scores else None,
                'brier_score_count': len(brier_scores),
                'avg_prediction': statistics.mean(predictions) if predictions else None,
                'prediction_count': len(predictions),
                'avg_actual_value': statistics.mean(actual_values) if actual_values else None,
                'actual_value_count': len(actual_values)
            }
        
        # Overall statistics
        total_predictions = sum(len([r for r in successful_results if r['predictions'].get(f"{h}d")]) for h in self.TIME_HORIZONS)
        total_brier_scores = len(all_brier_scores)
        overall_avg_brier = statistics.mean(all_brier_scores) if all_brier_scores else None
        
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
            'overall_avg_brier_score': overall_avg_brier,
            'horizon_statistics': horizon_stats,
            'results': results
        }
        
        # Log comprehensive results
        self.logger.info(f"🎯 Enhanced ForecastBench Evaluation Complete!")
        self.logger.info(f"   Questions processed: {len(successful_results)}/{len(questions)} ({success_rate:.1%})")
        self.logger.info(f"   Total predictions: {total_predictions}")
        self.logger.info(f"   Total Brier scores: {total_brier_scores}")
        self.logger.info(f"   Overall Average Brier Score: {overall_avg_brier:.4f}" if overall_avg_brier else "   Overall Average Brier Score: N/A")
        self.logger.info(f"   Duration: {duration:.1f}s ({summary['questions_per_minute']:.1f} questions/minute)")
        
        # Log Brier scores by time horizon
        for horizon in self.TIME_HORIZONS:
            horizon_key = f"{horizon}d"
            stats = horizon_stats[horizon_key]
            if stats['avg_brier_score'] is not None:
                self.logger.info(f"   {horizon}-day Brier Score: {stats['avg_brier_score']:.4f} (n={stats['brier_score_count']})")
            else:
                self.logger.info(f"   {horizon}-day Brier Score: N/A (no resolutions)")
        
        return summary

def main():
    """Main function to run enhanced ForecastBench evaluation"""
    # Get API keys
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    serp_api_key = os.getenv('SERP_API_KEY')
    
    if not openrouter_api_key:
        print("❌ OPENROUTER_API_KEY environment variable required")
        return
    
    if not serp_api_key:
        print("❌ SERP_API_KEY environment variable required")
        return
    
    # Create runner
    runner = EnhancedForecastBenchRunner(
        openrouter_api_key=openrouter_api_key,
        serp_api_key=serp_api_key
    )
    
    # Run benchmark on first 3 questions with 3 workers as requested
    results = runner.run_parallel_benchmark(max_questions=3, max_workers=3)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"enhanced_forecastbench_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📊 Results saved to: {output_file}")
    
    # Print the 12 Brier scores and average as requested
    if 'results' in results:
        print(f"\n🎯 REQUESTED RESULTS: 12 Brier Scores from First 3 Questions")
        print("=" * 80)
        
        all_brier_scores = []
        for i, result in enumerate(results['results']):
            if result['success']:
                print(f"\nQuestion {i+1}: {result['question_id']}")
                for horizon in [7, 30, 90, 180]:
                    horizon_key = f"{horizon}d"
                    brier = result['brier_scores'].get(horizon_key)
                    if brier is not None:
                        all_brier_scores.append(brier)
                        print(f"  {horizon}-day horizon: {brier:.6f}")
                    else:
                        print(f"  {horizon}-day horizon: N/A")
        
        if all_brier_scores:
            average_brier = sum(all_brier_scores) / len(all_brier_scores)
            print(f"\n📊 FINAL RESULTS:")
            print(f"   Total Brier scores: {len(all_brier_scores)}")
            print(f"   Average Brier score: {average_brier:.6f}")
        else:
            print(f"\n❌ No valid Brier scores calculated")

if __name__ == "__main__":
    main()