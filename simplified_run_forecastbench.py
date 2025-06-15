#!/usr/bin/env python3
"""
Simplified ForecastBench Runner - Configurable debate-based forecasting
Passes all configuration parameters to the superforecaster
"""

import json
import statistics
import traceback
import os
import sys
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('forecastbench.log')
    ]
)

sys.path.append('src')

# Import the simplified superforecaster
from ai_forecasts.agents.simplified_inspect_ai_superforecaster import create_superforecaster

def extract_question_ids_from_failure_file(file_path: str = "failure.txt") -> List[str]:
    """Return a deterministic list of question IDs from the top 10 most incorrect predictions"""
    question_ids = [
        "4puVWhIkvQiHnTxbH4NL",  # Question 20: Apple iPhone LLM ChatBot
        "1373",                   # Question 47: Exoplanets discovery
        "ccda7990a2565cabd7c375a036751bd3b953b8bed45d859010919cd3a84d7e78",  # Question 92: Montenegro violence
        "0x60752c2a562d7faff00a82238520a13a9a5a5ee2927afd397d224dc54361afd6",  # Question 76: Tesla Robotaxi delay
        "1353",                   # Question 57: Israel-Hamas ceasefire
        "T10YIE",                 # Question 144: US 10-year breakeven inflation
        "TMBACBW027SBOG",         # Question 135: Mortgage-backed securities
        "9043472375a02690dfb338bd3d11605105562e5cae9672a989961b0c5bef9b51",  # Question 94: Bahrain protests
        "4204aec5ff81b3d331f27141b072979d838ed95bcd0de36e887ca9a70523060a"   # Question 93: China protests
    ]
    
    print(f"📋 Using deterministic list of {len(question_ids)} question IDs from failure analysis")
    return question_ids

class SimplifiedForecastBenchRunner:
    """Simplified ForecastBench runner with configurable parameters"""
    
    # Local files for ForecastBench datasets
    QUESTIONS_FILE = "forecastbench_human_2024.json"
    RESOLUTIONS_FILE = "forecast_human_resolution_2024.json"
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None,
                 time_horizons: List[int] = None, 
                 search_budget_per_advocate: int = 10,
                 debate_rounds: int = 3,
                 training_cutoff: str = "2024-07-01"):
        """
        Initialize runner with configurable parameters
        
        Args:
            openrouter_api_key: API key for OpenRouter
            serp_api_key: API key for SERP (Google News)
            time_horizons: List of time horizons in days (e.g., [7, 30, 90, 180])
            search_budget_per_advocate: Number of searches per advocate
            debate_rounds: Number of debate rounds
            training_cutoff: Model training cutoff date
        """
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key
        self.time_horizons = time_horizons or [7, 30, 90, 180]
        self.search_budget_per_advocate = search_budget_per_advocate
        self.debate_rounds = debate_rounds
        self.training_cutoff = training_cutoff
        
        # Create directories
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        self.checkpoints_dir = Path("checkpoints")
        self.checkpoints_dir.mkdir(exist_ok=True)
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        print(f"✅ Initialized SimplifiedForecastBenchRunner")
        print(f"   Time horizons: {self.time_horizons} days")
        print(f"   Search budget per advocate: {self.search_budget_per_advocate}")
        print(f"   Debate rounds: {self.debate_rounds}")
        print(f"   Training cutoff: {self.training_cutoff}")
    
    def load_local_data(self) -> Tuple[List[Dict], Dict[str, Any], str]:
        """Load questions and resolutions from local JSON files"""
        try:
            # Load questions
            with open(self.QUESTIONS_FILE, 'r') as f:
                questions_data = json.load(f)
            
            # Load resolutions
            with open(self.RESOLUTIONS_FILE, 'r') as f:
                resolutions_data = json.load(f)
            
            questions = questions_data['questions']
            forecast_due_date = questions_data.get('forecast_due_date', '2024-07-21')
            
            print(f"✅ Loaded {len(questions)} questions from local file")
            print(f"✅ Loaded {len(resolutions_data['resolutions'])} resolutions from local file")
            print(f"✅ Forecast due date: {forecast_due_date}")
            
            return questions, resolutions_data, forecast_due_date
            
        except Exception as e:
            print(f"❌ Error loading local data: {e}")
            return [], {}, "2024-07-21"
    
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
    
    def process_single_question(self, question_data: Dict, question_idx: int, resolutions_data: Dict, 
                              base_date: datetime, forecast_due_date: str, run_timestamp: str) -> Dict:
        """Process a single question with configurable time horizon predictions"""
        try:
            question_id = question_data.get('id', f"q_{question_idx}")
            question = question_data.get('question', '')
            
            # Create comprehensive context
            comprehensive_context = self.create_comprehensive_context(question_data)
            
            print(f"Processing question {question_idx + 1}: {question[:80]}...")
            print(f"Comprehensive context length: {len(comprehensive_context)} characters")
            
            # Initialize superforecaster with all configuration parameters
            superforecaster = create_superforecaster(
                openrouter_api_key=self.openrouter_api_key,
                serp_api_key=self.serp_api_key
            )
            
            # Calculate resolution dates for all time horizons
            resolution_dates = []
            for horizon_days in self.time_horizons:
                res_date = base_date + timedelta(days=horizon_days)
                resolution_dates.append(res_date.strftime('%Y-%m-%d'))
            
            # Use the forecast due date as cutoff
            cutoff_date = datetime.strptime(forecast_due_date, '%Y-%m-%d')
            
            print(f"  📅 Using forecast due date as cutoff: {forecast_due_date}")
            
            # Convert time horizons to strings for the superforecaster
            time_horizons_str = [str(h) for h in self.time_horizons]
            
            try:
                # Call the simplified superforecaster with all parameters
                horizon_results = superforecaster.forecast_with_google_news(
                    question=question,
                    background=comprehensive_context,
                    time_horizons=time_horizons_str,
                    cutoff_date=cutoff_date,
                    search_budget_per_advocate=self.search_budget_per_advocate,
                    debate_rounds=self.debate_rounds,
                    training_cutoff=self.training_cutoff
                )
                
                print(f"  ✅ Multi-horizon forecast completed: {len(horizon_results)} predictions")
                
                # Process each horizon result
                predictions = {}
                brier_scores = {}
                actual_values = {}
                
                for i, (horizon_days, resolution_date, result) in enumerate(zip(self.time_horizons, resolution_dates, horizon_results)):
                    horizon_key = f"{horizon_days}d"
                    
                    # Store prediction
                    predictions[horizon_key] = result.prediction
                    
                    # Get actual resolution value
                    actual_value = self.get_resolution_for_question_and_date(question_id, resolution_date, resolutions_data)
                    actual_values[horizon_key] = actual_value
                    
                    # Calculate Brier score if we have actual value
                    if actual_value is not None:
                        brier_score = (result.prediction - actual_value) ** 2
                        brier_scores[horizon_key] = brier_score
                        print(f"    {horizon_key}: Pred={result.prediction:.3f}, Actual={actual_value:.3f}, Brier={brier_score:.6f}")
                    else:
                        brier_scores[horizon_key] = None
                        print(f"    {horizon_key}: Pred={result.prediction:.3f}, Actual=N/A, Brier=N/A")
                
            except Exception as e:
                print(f"❌ Multi-horizon forecasting failed for question {question_idx + 1}: {e}")
                
                # Fallback to empty results
                predictions = {}
                brier_scores = {}
                actual_values = {}
                
                for horizon_days in self.time_horizons:
                    horizon_key = f"{horizon_days}d"
                    predictions[horizon_key] = None
                    brier_scores[horizon_key] = None
                    actual_values[horizon_key] = None
            
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
            print(f"❌ Error processing question {question_idx + 1}: {e}")
            traceback.print_exc()
            
            return {
                'question_idx': question_idx,
                'question_id': question_data.get('id', f"q_{question_idx}"),
                'question': question_data.get('question', ''),
                'error': str(e),
                'success': False
            }
    
    def run_parallel_benchmark(self, max_questions: int = 200, max_workers: int = 3, 
                             question_ids: List[str] = None) -> Dict[str, Any]:
        """Run simplified ForecastBench evaluation with configurable parameters"""
        
        run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"🚀 Starting Simplified ForecastBench evaluation")
        print(f"   Max questions: {max_questions}, Workers: {max_workers}")
        print(f"   Time horizons: {self.time_horizons} days")
        print(f"   Search budget per advocate: {self.search_budget_per_advocate}")
        print(f"   Debate rounds: {self.debate_rounds}")
        print(f"   Training cutoff: {self.training_cutoff}")
        
        # Load questions and resolutions
        questions, resolutions_data, forecast_due_date = self.load_local_data()
        if not questions:
            return {"error": "Failed to load ForecastBench questions"}
            
        if not resolutions_data:
            return {"error": "Failed to load resolution data"}
        
        # Filter questions by question IDs if specified
        if question_ids:
            original_count = len(questions)
            questions_by_id = {q.get('id', ''): q for q in questions}
            
            filtered_questions = []
            found_ids = []
            missing_ids = []
            
            for question_id in question_ids:
                if question_id in questions_by_id:
                    filtered_questions.append(questions_by_id[question_id])
                    found_ids.append(question_id)
                else:
                    missing_ids.append(question_id)
            
            questions = filtered_questions
            
            print(f"🔍 Question ID filtering applied:")
            print(f"   Original questions: {original_count}")
            print(f"   Found matching questions: {len(found_ids)}")
            
            if missing_ids:
                print(f"   Missing IDs: {missing_ids}")
            
            if not questions:
                return {"error": "No matching questions found"}
        
        # Limit questions
        questions = questions[:max_questions]
        print(f"📋 Processing {len(questions)} questions")
        
        # Base date for time horizon calculations (forecast due date)
        base_date = datetime(2024, 7, 21)
        print(f"📅 Using base date: {base_date.strftime('%Y-%m-%d')}")
        
        results = []
        start_time = datetime.now()
        
        # Process questions in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_question = {
                executor.submit(
                    self.process_single_question, 
                    question_data, 
                    idx, 
                    resolutions_data, 
                    base_date, 
                    forecast_due_date, 
                    run_timestamp
                ): (idx, question_data) for idx, question_data in enumerate(questions)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_question):
                idx, question_data = future_to_question[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✅ Completed question {idx + 1}/{len(questions)}")
                except Exception as e:
                    print(f"❌ Question {idx + 1} failed: {e}")
                    results.append({
                        'question_idx': idx,
                        'question_id': question_data.get('id', f"q_{idx}"),
                        'question': question_data.get('question', ''),
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
        
        for horizon_days in self.time_horizons:
            horizon_key = f"{horizon_days}d"
            brier_scores = []
            predictions = []
            actual_values = []
            
            for result in successful_results:
                if result['brier_scores'].get(horizon_key) is not None:
                    brier_scores.append(result['brier_scores'][horizon_key])
                    all_brier_scores.append(result['brier_scores'][horizon_key])
                
                if result['predictions'].get(horizon_key) is not None:
                    predictions.append(result['predictions'][horizon_key])
                
                if result['actual_values'].get(horizon_key) is not None:
                    actual_values.append(result['actual_values'][horizon_key])
            
            horizon_stats[horizon_key] = {
                'avg_brier_score': statistics.mean(brier_scores) if brier_scores else None,
                'brier_score_count': len(brier_scores),
                'avg_prediction': statistics.mean(predictions) if predictions else None,
                'prediction_count': len(predictions),
                'avg_actual_value': statistics.mean(actual_values) if actual_values else None,
                'actual_value_count': len(actual_values)
            }
        
        # Overall statistics
        total_predictions = sum(len([r for r in successful_results if r['predictions'].get(f"{h}d")]) for h in self.time_horizons)
        total_brier_scores = len(all_brier_scores)
        overall_avg_brier = statistics.mean(all_brier_scores) if all_brier_scores else None
        
        summary = {
            'configuration': {
                'time_horizons': self.time_horizons,
                'search_budget_per_advocate': self.search_budget_per_advocate,
                'debate_rounds': self.debate_rounds,
                'training_cutoff': self.training_cutoff
            },
            'base_date': base_date.strftime("%Y-%m-%d"),
            'forecast_due_date': forecast_due_date,
            'total_questions': len(questions),
            'successful_forecasts': len(successful_results),
            'success_rate': success_rate,
            'duration_seconds': duration,
            'questions_per_minute': (len(questions) / duration) * 60 if duration > 0 else 0,
            'total_predictions': total_predictions,
            'total_brier_scores': total_brier_scores,
            'overall_avg_brier_score': overall_avg_brier,
            'horizon_statistics': horizon_stats,
            'run_timestamp': run_timestamp,
            'results': results
        }
        
        # Log results
        print(f"🎯 Simplified ForecastBench Evaluation Complete!")
        print(f"   Questions processed: {len(successful_results)}/{len(questions)} ({success_rate:.1%})")
        print(f"   Total predictions: {total_predictions}")
        print(f"   Total Brier scores: {total_brier_scores}")
        if overall_avg_brier is not None:
            print(f"   Overall Average Brier Score: {overall_avg_brier:.4f}")
        print(f"   Duration: {duration:.1f}s ({summary['questions_per_minute']:.1f} questions/minute)")
        
        # Log Brier scores by time horizon
        for horizon_days in self.time_horizons:
            horizon_key = f"{horizon_days}d"
            stats = horizon_stats[horizon_key]
            if stats['avg_brier_score'] is not None:
                print(f"   {horizon_key}: Avg Brier = {stats['avg_brier_score']:.4f} ({stats['brier_score_count']} samples)")
            else:
                print(f"   {horizon_key}: No Brier scores available")
        
        return summary

def main():
    """Main function to run simplified ForecastBench evaluation"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simplified ForecastBench Runner')
    parser.add_argument('--max-questions', type=int, default=200, help='Maximum number of questions to process')
    parser.add_argument('--max-workers', type=int, default=3, help='Maximum number of parallel workers')
    parser.add_argument('--question-ids', type=str, nargs='+', help='Specific question IDs to test')
    parser.add_argument('--failure-questions', action='store_true', help='Test only questions from failure analysis')
    parser.add_argument('--time-horizons', type=int, nargs='+', default=[7, 30, 90, 180], help='Time horizons in days')
    parser.add_argument('--search-budget', type=int, default=10, help='Search budget per advocate')
    parser.add_argument('--debate-rounds', type=int, default=3, help='Number of debate rounds')
    parser.add_argument('--training-cutoff', type=str, default='2024-07-01', help='Model training cutoff date')
    
    args = parser.parse_args()
    
    # Get API keys
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    serp_api_key = os.getenv('SERP_API_KEY')
    
    if not openrouter_api_key:
        print("❌ OPENROUTER_API_KEY environment variable required")
        return
    
    if not serp_api_key:
        print("❌ SERP_API_KEY environment variable required")
        return
    
    # Handle question ID filtering
    question_ids_to_run = None
    if args.failure_questions:
        question_ids_to_run = extract_question_ids_from_failure_file()
        if question_ids_to_run:
            print(f"🎯 Testing {len(question_ids_to_run)} questions from failure analysis")
        else:
            print("❌ No question IDs found in failure analysis")
            return
    elif args.question_ids:
        question_ids_to_run = args.question_ids
        print(f"🎯 Testing {len(question_ids_to_run)} specific question IDs")
    
    # Create runner with configurable parameters
    runner = SimplifiedForecastBenchRunner(
        openrouter_api_key=openrouter_api_key,
        serp_api_key=serp_api_key,
        time_horizons=args.time_horizons,
        search_budget_per_advocate=args.search_budget,
        debate_rounds=args.debate_rounds,
        training_cutoff=args.training_cutoff
    )
    
    print(f"🚀 Starting benchmark with configurable parameters:")
    print(f"   Max questions: {args.max_questions}")
    print(f"   Max workers: {args.max_workers}")
    print(f"   Time horizons: {args.time_horizons} days")
    print(f"   Search budget per advocate: {args.search_budget}")
    print(f"   Debate rounds: {args.debate_rounds}")
    print(f"   Training cutoff: {args.training_cutoff}")
    
    if question_ids_to_run:
        print(f"🔍 Filtering to specific question IDs: {len(question_ids_to_run)} questions")
    
    # Run benchmark
    results = runner.run_parallel_benchmark(
        max_questions=args.max_questions, 
        max_workers=args.max_workers,
        question_ids=question_ids_to_run
    )
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = runner.results_dir / f"simplified_forecastbench_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📊 Results saved to: {output_file}")

if __name__ == "__main__":
    main()
