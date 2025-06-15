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
import sys
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
sys.path.append('src')

from ai_forecasts.agents.inspect_ai_superforecaster import create_superforecaster
# AgentLogger removed - using simple logging

def extract_question_ids_from_failure_file(file_path: str = "failure.txt") -> List[str]:
    """
    Return a deterministic list of question IDs from the top 10 most incorrect predictions,
    excluding YulPWDHFTUkekmrO3v4J
    
    Args:
        file_path: Path to the failure.txt file (unused, kept for compatibility)
        
    Returns:
        List of question IDs from the failure analysis
    """
    # Deterministic list of question IDs from the top 10 most incorrect predictions
    # Based on the failure.txt analysis, excluding YulPWDHFTUkekmrO3v4J
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
    print(f"   Excluded: YulPWDHFTUkekmrO3v4J")
    
    return question_ids

class EnhancedForecastBenchRunner:
    """Enhanced ForecastBench runner with comprehensive question context and corrected Brier score calculation"""
    
    # Local files for ForecastBench datasets
    QUESTIONS_FILE = "forecastbench_human_2024.json"
    RESOLUTIONS_FILE = "forecast_human_resolution_2024.json"
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None, 
                 time_horizons: List[int] = None, search_budget: int = 10, 
                 debate_turns: int = 2):
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key
        # Simple logger replacement
        self.logger = self
        
        # Configurable parameters
        self.time_horizons = time_horizons or [7, 30, 90, 180]  # Time horizons for predictions (in days)
        self.search_budget = search_budget  # Search budget per question
        self.debate_turns = debate_turns  # Number of debate turns
        
        # Create logs and checkpoints directories
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        self.checkpoints_dir = Path("checkpoints")
        self.checkpoints_dir.mkdir(exist_ok=True)
    
    def info(self, message: str):
        """Simple info logger"""
        print(f"[INFO] {message}")
    
    def error(self, message: str):
        """Simple error logger"""
        print(f"[ERROR] {message}")
    
    def warning(self, message: str):
        """Simple warning logger"""
        print(f"[WARNING] {message}")
        
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
            forecast_due_date = questions_data.get('forecast_due_date', '2024-07-21')  # Default fallback
            
            self.logger.info(f"✅ Loaded {len(questions)} questions from local file")
            self.logger.info(f"✅ Loaded {len(resolutions_data['resolutions'])} resolutions from local file")
            self.logger.info(f"✅ Forecast due date: {forecast_due_date}")
            
            return questions, resolutions_data, forecast_due_date
            
        except Exception as e:
            self.logger.error(f"❌ Error loading local data: {e}")
            return [], {}, "2024-07-21"  # Return default forecast due date on error
    
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
    
    def _has_valid_predictions(self, horizon_results: List) -> bool:
        """Check if all horizon results have valid probability values (not None/N/A)"""
        if not horizon_results or len(horizon_results) != len(self.time_horizons):
            return False
        
        for result in horizon_results:
            if not hasattr(result, 'prediction') or result.prediction is None:
                return False
            # Check for invalid probability values
            if not isinstance(result.prediction, (int, float)) or result.prediction < 0 or result.prediction > 1:
                return False
        
        return True

    def _forecast_with_retry(self, superforecaster, question: str, comprehensive_context: str, cutoff_date: datetime, 
                           time_horizons_str: List[str], effective_recommended_articles: int, 
                           effective_max_queries: int, max_retries: int = 3) -> List:
        """Forecast with retry logic for handling N/A results"""
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"    🔄 Forecasting attempt {attempt + 1}/{max_retries}")
                
                horizon_results = superforecaster.forecast_with_google_news(
                    question=question,
                    background=comprehensive_context,
                    cutoff_date=cutoff_date,
                    time_horizons=time_horizons_str,
                    is_benchmark=True,
                    recommended_articles=effective_recommended_articles,
                    max_search_queries=effective_max_queries
                )
                
                # Check if we got valid results for all horizons
                if self._has_valid_predictions(horizon_results):
                    self.logger.info(f"    ✅ Valid predictions obtained on attempt {attempt + 1}")
                    return horizon_results
                else:
                    # Log which horizons have invalid results
                    invalid_horizons = []
                    for i, result in enumerate(horizon_results):
                        if not hasattr(result, 'prediction') or result.prediction is None:
                            invalid_horizons.append(time_horizons_str[i])
                        elif not isinstance(result.prediction, (int, float)) or result.prediction < 0 or result.prediction > 1:
                            invalid_horizons.append(f"{time_horizons_str[i]}(invalid_value)")
                    
                    self.logger.warning(f"    ⚠️ Attempt {attempt + 1} produced invalid results for horizons: {invalid_horizons}")
                    print(f"⚠️ Attempt {attempt + 1} invalid results", {
                        "invalid_horizons": invalid_horizons,
                        "total_results": len(horizon_results)
                    })
                    
                    if attempt < max_retries - 1:
                        # Add a small delay before retry
                        import time
                        time.sleep(2)
                        continue
                    else:
                        self.logger.error(f"    ❌ All {max_retries} attempts failed to produce valid results")
                        return horizon_results  # Return the last attempt's results
                        
            except Exception as e:
                self.logger.error(f"    ❌ Attempt {attempt + 1} failed with exception: {e}")
                print(f"❌ Forecast attempt {attempt + 1} failed", {
                    "error": str(e), 
                    "attempt": attempt + 1,
                    "max_retries": max_retries
                })
                
                if attempt < max_retries - 1:
                    # Add a delay before retry
                    import time
                    time.sleep(2)
                    continue
                else:
                    # Re-raise the exception if all attempts failed
                    raise e
        
        # Should not reach here, but return empty list as fallback
        return []

    def process_single_question(self, question_data: Dict, question_idx: int, resolutions_data: Dict, base_date: datetime, forecast_due_date: str, run_timestamp: str) -> Dict:
        """Process a single question with 4 time horizon predictions using enhanced context and retry logic"""
        try:
            # Create individual logger for this question
            question_id = question_data.get('id', f"q_{question_idx}")
            log_file = self.logs_dir / f"question_{question_idx+1}_{question_id}_{run_timestamp}.json"
            # Initialize superforecaster for this thread
            # Use Inspect AI with debate mode
            superforecaster = create_superforecaster(
                openrouter_api_key=self.openrouter_api_key,
                serp_api_key=self.serp_api_key,
                logger=None,  # Use default logger
                debate_mode=True,
                search_budget=self.search_budget,
                debate_turns=self.debate_turns,
                time_horizons=self.time_horizons
            )
            
            question = question_data.get('question', '')
            question_id = question_data.get('id', f"q_{question_idx}")
            
            # Create comprehensive context from all question information
            comprehensive_context = self.create_comprehensive_context(question_data)
            
            # Start processing this question
            print(f"Processing question {question_idx+1}: {question[:100]}...")
            
            self.logger.info(f"Processing question {question_idx + 1}: {question[:80]}...")
            self.logger.info(f"Comprehensive context length: {len(comprehensive_context)} characters")
            self.logger.info(f"Question logs: {log_file}")
            
            # Calculate resolution dates for all time horizons
            resolution_dates = []
            for horizon_days in self.time_horizons:
                res_date = base_date + timedelta(days=horizon_days)
                resolution_dates.append(res_date.strftime('%Y-%m-%d'))
            
            # Generate predictions for all time horizons using the new multi-horizon method
            # Use the forecast due date as cutoff - predictions should not use information after this date
            cutoff_date = datetime.strptime(forecast_due_date, '%Y-%m-%d')
            
            self.logger.info(f"  📅 Using forecast due date as cutoff: {forecast_due_date}")
            self.logger.info(f"  📅 Cutoff date object: {cutoff_date.strftime('%Y-%m-%d')}")
            
            # Use the updated forecast_with_google_news method for all time horizons at once
            time_horizons_str = [f"{h}d" for h in self.time_horizons]
            
            # Default parameters for multi-horizon forecasting
            effective_recommended_articles = 10
            effective_max_queries = 5
            
            try:
                # Use retry logic for forecasting
                horizon_results = self._forecast_with_retry(
                    superforecaster=superforecaster,
                    question=question,
                    comprehensive_context=comprehensive_context,
                    cutoff_date=cutoff_date,
                    time_horizons_str=time_horizons_str,
                    effective_recommended_articles=effective_recommended_articles,
                    effective_max_queries=effective_max_queries,

                    max_retries=3
                )
                
                self.logger.info(f"  ✅ Multi-horizon forecast completed: {len(horizon_results)} predictions")
                
                # Process each horizon result
                predictions = {}
                brier_scores = {}
                actual_values = {}
                
                for i, (horizon_days, resolution_date, result) in enumerate(zip(self.time_horizons, resolution_dates, horizon_results)):
                    # Get actual resolution value
                    actual_value = self.get_resolution_for_question_and_date(question_id, resolution_date, resolutions_data)
                    
                    # Handle invalid or None results
                    if not hasattr(result, 'prediction') or result.prediction is None:
                        self.logger.warning(f"  ⚠️ {horizon_days}d horizon: Invalid probability (None/N/A)")
                        horizon_key = f"{horizon_days}d"
                        predictions[horizon_key] = {
                            'prediction': None,
                            'error': 'Invalid probability result',
                            'confidence': 'N/A',
                            'reasoning': 'Failed to generate valid probability after retries',
                            'cutoff_date': cutoff_date.strftime("%Y-%m-%d"),
                            'resolution_date': resolution_date,
                            'time_horizon': horizon_key
                        }
                        brier_scores[horizon_key] = None
                        actual_values[horizon_key] = actual_value
                        continue
                    
                    # Calculate Brier score if resolution data available
                    brier_score = None
                    if actual_value is not None:
                        brier_score = (result.prediction - actual_value) ** 2
                    
                    # Store prediction
                    horizon_key = f"{horizon_days}d"
                    predictions[horizon_key] = {
                        'prediction': result.prediction,
                        'confidence': result.confidence,
                        'reasoning': result.reasoning,
                        'base_rate': getattr(result, 'base_rate', None),
                        'evidence_quality': getattr(result, 'evidence_quality', None),
                        'cutoff_date': cutoff_date.strftime("%Y-%m-%d"),
                        'resolution_date': resolution_date,
                        'news_sources_count': len(getattr(result, 'news_sources', [])),
                        'search_queries_used': getattr(result, 'search_queries_used', result.search_count),
                        'total_articles_found': getattr(result, 'total_articles_found', 0),
                        'time_horizon': getattr(result, 'time_horizon', horizon_key)
                    }
                    
                    brier_scores[horizon_key] = brier_score
                    actual_values[horizon_key] = actual_value
                    
                    self.logger.info(f"  ✅ {horizon_days}d horizon: prob={result.prediction:.3f}, actual={actual_value}, brier={brier_score:.3f}" if brier_score is not None else f"  ✅ {horizon_days}d horizon: prob={result.prediction:.3f}, actual={actual_value}")
                
            except Exception as e:
                self.logger.error(f"Multi-horizon forecasting failed for question {question_idx + 1}: {e}")
                print(f"❌ Multi-horizon forecasting failed: {str(e)}")
                
                # Fallback to empty results
                predictions = {}
                brier_scores = {}
                actual_values = {}
                
                for horizon_days in self.time_horizons:
                    horizon_key = f"{horizon_days}d"
                    predictions[horizon_key] = {'error': str(e)}
                    brier_scores[horizon_key] = None
                    actual_values[horizon_key] = None
            
            # Finalize question logging session
            # Session finalized
            
            return {
                'question_idx': question_idx,
                'question_id': question_id,
                'question': question,
                'freeze_value': question_data.get('freeze_datetime_value'),
                'comprehensive_context_length': len(comprehensive_context),
                'predictions': predictions,
                'brier_scores': brier_scores,
                'actual_values': actual_values,
                'log_file': str(log_file),
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error processing question {question_idx + 1}: {e}")
            traceback.print_exc()
            
            # Try to finalize logger even on error
            try:
                if False:  # question_logger removed
                    print("Question processing failed", {"error": str(e), "traceback": traceback.format_exc()})
                    # Session finalized
            except:
                pass
            
            return {
                'question_idx': question_idx,
                'question_id': question_data.get('id', f"q_{question_idx}"),
                'question': question_data.get('question', ''),
                'error': str(e),
                'success': False
            }
    
    def run_parallel_benchmark(self, max_questions: int = 200, max_workers: int = 3, resume_from_checkpoint: str = None, question_ids: List[str] = None) -> Dict[str, Any]:
        """Run enhanced ForecastBench evaluation with comprehensive context and checkpoint support
        
        Args:
            max_questions: Maximum number of questions to process
            max_workers: Number of parallel workers
            resume_from_checkpoint: Path to checkpoint file or 'latest'
            question_ids: Optional list of specific question IDs to test on
        """
        
        # Handle checkpoint resumption or create new timestamp
        if resume_from_checkpoint:
            if resume_from_checkpoint == "latest":
                checkpoint_file = self.find_latest_checkpoint()
                if checkpoint_file:
                    checkpoint_data = self.load_checkpoint(checkpoint_file)
                    run_timestamp = checkpoint_data.get('run_timestamp', datetime.now().strftime("%Y%m%d_%H%M%S"))
                    self.logger.info(f"🔄 Resuming from latest checkpoint: {checkpoint_file}")
                else:
                    self.logger.info("📄 No checkpoint found, starting fresh")
                    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    checkpoint_data = {}
            else:
                # Specific checkpoint file
                checkpoint_file = Path(resume_from_checkpoint)
                checkpoint_data = self.load_checkpoint(checkpoint_file)
                run_timestamp = checkpoint_data.get('run_timestamp', datetime.now().strftime("%Y%m%d_%H%M%S"))
        else:
            # Fresh start
            run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_data = {}
            checkpoint_file = self.get_checkpoint_file(run_timestamp)
        
        # Create master log file for the entire run
        master_log_file = self.logs_dir / f"benchmark_run_{run_timestamp}.json"
        # Simple logging instead of AgentLogger
        print(f"🚀 Starting benchmark run at {run_timestamp}")
        print(f"📁 Master log would be: {master_log_file}")
        
        # Start session equivalent
        print(f"Starting benchmark session with {max_questions} questions, {max_workers} workers")
        
        self.logger.info(f"🚀 Starting Enhanced ForecastBench evaluation with comprehensive context")
        self.logger.info(f"   Questions: {max_questions}, Workers: {max_workers}")
        self.logger.info(f"   Time horizons: {self.time_horizons} days")
        self.logger.info(f"   Master log: {master_log_file}")
        self.logger.info(f"   Individual logs: {self.logs_dir}/question_*_{run_timestamp}.json")
        self.logger.info(f"   Checkpoint file: {checkpoint_file}")
        
        # Load questions and resolutions from local files
        questions, resolutions_data, forecast_due_date = self.load_local_data()
        if not questions:
            print("❌ Failed to load ForecastBench questions")
            return {"error": "Failed to load ForecastBench questions"}
            
        if not resolutions_data:
            print("❌ Failed to load resolution data")
            return {"error": "Failed to load resolution data"}
        
        print(f"✅ Loaded {len(questions)} questions and {len(resolutions_data.get('resolutions', []))} resolutions, forecast due date: {forecast_due_date}")
        
        # Filter questions by question IDs if specified
        if question_ids:
            original_count = len(questions)
            # Create a mapping of question ID to question data
            questions_by_id = {q.get('id', ''): q for q in questions}
            
            # Filter questions to only include those with matching IDs
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
            
            self.logger.info(f"🔍 Question ID filtering applied:")
            self.logger.info(f"   Original questions: {original_count}")
            self.logger.info(f"   Requested question IDs: {len(question_ids)}")
            self.logger.info(f"   Found matching questions: {len(found_ids)}")
            self.logger.info(f"   Found IDs: {found_ids}")
            
            if missing_ids:
                self.logger.warning(f"   Missing question IDs: {missing_ids}")
            
            print("question_id_filtering", f"Filtered to {len(questions)} questions from {original_count}", {
                "requested_ids": question_ids,
                "found_ids": found_ids,
                "missing_ids": missing_ids
            })
            
            if not questions:
                self.logger.error("❌ No questions found matching the specified question IDs")
                print("No questions found matching specified IDs")
                
                return {"error": "No questions found matching the specified question IDs"}
        
        # Limit questions for testing (apply after filtering)
        questions = questions[:max_questions]
        print("question_selection", f"Processing {len(questions)} questions")
        
        # Base date for time horizon calculations (forecast due date)
        base_date = datetime(2024, 7, 21)
        print("base_date", f"Using base date: {base_date.strftime('%Y-%m-%d')}")
        
        # Resume from checkpoint if available
        if checkpoint_data and 'results' in checkpoint_data:
            completed_indices = set(r['question_idx'] for r in checkpoint_data['results'] if r.get('success', False))
            self.logger.info(f"⏮️ Found checkpoint with {len(completed_indices)} completed questions")
            results = checkpoint_data['results']
            start_time = datetime.fromisoformat(checkpoint_data.get('start_time', datetime.now().isoformat()))
        else:
            completed_indices = set()
            results = []
            start_time = datetime.now()
        
        # Filter questions that haven't been completed yet
        remaining_questions = [(idx, q) for idx, q in enumerate(questions) if idx not in completed_indices]
        
        if not remaining_questions:
            self.logger.info("✅ All questions already completed from checkpoint!")
        else:
            self.logger.info(f"📋 Processing {len(remaining_questions)} remaining questions (out of {len(questions)} total)")
        
        # Process remaining questions in parallel
        if remaining_questions:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit tasks for remaining questions
                future_to_idx = {
                    executor.submit(self.process_single_question, q, idx, resolutions_data, base_date, forecast_due_date, run_timestamp): idx 
                    for idx, q in remaining_questions
                }
                
                # Track progress for checkpointing
                completed_count = len(completed_indices)
                total_questions = len(questions)
                
                # Collect results as they complete
                for future in as_completed(future_to_idx):
                    try:
                        result = future.result()
                        results.append(result)
                        completed_count += 1
                        
                        if result['success']:
                            # Show progress with Brier scores for each horizon
                            brier_info = []
                            for horizon in self.time_horizons:
                                brier = result['brier_scores'].get(f"{horizon}d")
                                if brier is not None:
                                    brier_info.append(f"{horizon}d:{brier:.3f}")
                            brier_str = f" (Brier: {', '.join(brier_info)})" if brier_info else ""
                            self.logger.info(f"✅ Completed question {result['question_idx'] + 1}/{total_questions} ({completed_count}/{total_questions}){brier_str}")
                            print("question_completed", f"Question {result['question_idx'] + 1} completed", {
                                "question_id": result['question_id'],
                                "log_file": result.get('log_file'),
                                "brier_scores": result['brier_scores']
                            })
                        else:
                            self.logger.error(f"❌ Failed question {result['question_idx'] + 1}/{total_questions}")
                            print(f"Question {result['question_idx'] + 1} failed", {
                                "question_id": result.get('question_id'),
                                "error": result.get('error')
                            })
                        
                        # Save checkpoint after every completed question
                        checkpoint_data_to_save = {
                            'run_timestamp': run_timestamp,
                            'start_time': start_time.isoformat(),
                            'base_date': base_date.strftime('%Y-%m-%d'),
                            'max_questions': max_questions,
                            'max_workers': max_workers,
                            'time_horizons': self.time_horizons,
                            'total_questions': len(questions),
                            'completed_count': completed_count,
                            'results': results
                        }
                        self.save_checkpoint(checkpoint_data_to_save, checkpoint_file)
                            
                    except Exception as e:
                        idx = future_to_idx[future]
                        self.logger.error(f"❌ Exception in question {idx + 1}: {e}")
                        print(f"Question {idx + 1} exception", {"error": str(e), "traceback": traceback.format_exc()})
                        results.append({
                            'question_idx': idx,
                            'error': str(e),
                            'success': False
                        })
                        completed_count += 1
                        
                        # Save checkpoint even after errors
                        checkpoint_data_to_save = {
                            'run_timestamp': run_timestamp,
                            'start_time': start_time.isoformat(),
                            'base_date': base_date.strftime('%Y-%m-%d'),
                            'max_questions': max_questions,
                            'max_workers': max_workers,
                            'time_horizons': self.time_horizons,
                            'total_questions': len(questions),
                            'completed_count': completed_count,
                            'results': results
                        }
                        self.save_checkpoint(checkpoint_data_to_save, checkpoint_file)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("benchmark_completed", f"Benchmark completed in {duration:.1f}s", {
            "total_questions": len(questions),
            "successful_results": len([r for r in results if r['success']]),
            "duration_seconds": duration
        })
        
        # Calculate comprehensive statistics
        successful_results = [r for r in results if r['success']]
        success_rate = len(successful_results) / len(results) if results else 0
        
        # Calculate Brier scores by time horizon
        horizon_stats = {}
        all_brier_scores = []
        
        for horizon in self.time_horizons:
            horizon_key = f"{horizon}d"
            brier_scores = []
            predictions = []
            actual_values = []
            
            for result in successful_results:
                brier = result['brier_scores'].get(horizon_key)
                if brier is not None:
                    brier_scores.append(brier)
                    all_brier_scores.append(brier)
                    
                pred = result['predictions'].get(horizon_key, {}).get('prediction')
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
        total_predictions = sum(len([r for r in successful_results if r['predictions'].get(f"{h}d")]) for h in self.time_horizons)
        total_brier_scores = len(all_brier_scores)
        overall_avg_brier = statistics.mean(all_brier_scores) if all_brier_scores else None
        sum_brier_scores = sum(all_brier_scores) if all_brier_scores else None
        
        summary = {
            'base_date': base_date.strftime("%Y-%m-%d"),
            'forecast_due_date': forecast_due_date,
            'time_horizons': self.time_horizons,
            'total_questions': len(questions),
            'successful_forecasts': len(successful_results),
            'success_rate': success_rate,
            'duration_seconds': duration,
            'questions_per_minute': (len(questions) / duration) * 60 if duration > 0 else 0,
            'total_predictions': total_predictions,
            'total_brier_scores': total_brier_scores,
            'overall_avg_brier_score': overall_avg_brier,
            'sum_brier_scores': sum_brier_scores,
            'horizon_statistics': horizon_stats,
            'run_timestamp': run_timestamp,
            'master_log_file': str(master_log_file),
            'logs_directory': str(self.logs_dir),
            'results': results
        }
        
        # Log summary to master log
        print("final_summary", "Benchmark run completed", {
            "summary": {k: v for k, v in summary.items() if k != 'results'}  # Exclude full results to avoid huge log
        })
        
        # Finalize master logging session
        
        
        # Log comprehensive results
        self.logger.info(f"🎯 Enhanced ForecastBench Evaluation Complete!")
        self.logger.info(f"   Questions processed: {len(successful_results)}/{len(questions)} ({success_rate:.1%})")
        self.logger.info(f"   Forecast due date (cutoff): {forecast_due_date}")
        self.logger.info(f"   Total predictions: {total_predictions}")
        self.logger.info(f"   Total Brier scores: {total_brier_scores}")
        self.logger.info(f"   Overall Average Brier Score: {overall_avg_brier:.4f}" if overall_avg_brier else "   Overall Average Brier Score: N/A")
        self.logger.info(f"   Sum of All Brier Scores: {sum_brier_scores:.4f}" if sum_brier_scores else "   Sum of All Brier Scores: N/A")
        self.logger.info(f"   Duration: {duration:.1f}s ({summary['questions_per_minute']:.1f} questions/minute)")
        self.logger.info(f"   📁 Master log: {master_log_file}")
        self.logger.info(f"   📁 Individual logs: {self.logs_dir}/question_*_{run_timestamp}.json")
        
        # Log Brier scores by time horizon
        for horizon in self.time_horizons:
            horizon_key = f"{horizon}d"
            stats = horizon_stats[horizon_key]
            if stats['avg_brier_score'] is not None:
                self.logger.info(f"   {horizon}-day Brier Score: {stats['avg_brier_score']:.4f} (n={stats['brier_score_count']})")
            else:
                self.logger.info(f"   {horizon}-day Brier Score: N/A (no resolutions)")
        
        # Save final results to checkpoint
        self.save_checkpoint({
            'run_timestamp': run_timestamp,
            'results': results
        }, checkpoint_file)
        
        return summary
    
    def save_checkpoint(self, checkpoint_data: Dict, checkpoint_file: Path):
        """Save checkpoint data to file"""
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2, default=str)
            self.logger.info(f"💾 Checkpoint saved: {checkpoint_file}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save checkpoint: {e}")
    
    def load_checkpoint(self, checkpoint_file: Path) -> Dict:
        """Load checkpoint data from file"""
        try:
            if checkpoint_file.exists():
                with open(checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
                self.logger.info(f"📂 Checkpoint loaded: {checkpoint_file}")
                return checkpoint_data
            else:
                self.logger.info("📄 No checkpoint file found, starting fresh")
                return {}
        except Exception as e:
            self.logger.error(f"❌ Failed to load checkpoint: {e}")
            return {}
    
    def get_checkpoint_file(self, run_timestamp: str) -> Path:
        """Get the checkpoint file path for a run"""
        return self.checkpoints_dir / f"benchmark_checkpoint_{run_timestamp}.json"
    
    def find_latest_checkpoint(self) -> Path:
        """Find the most recent checkpoint file"""
        checkpoint_files = list(self.checkpoints_dir.glob("benchmark_checkpoint_*.json"))
        if checkpoint_files:
            # Sort by modification time and return the latest
            latest = max(checkpoint_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"🔍 Found latest checkpoint: {latest}")
            return latest
        return None

def main():
    """Main function to run enhanced ForecastBench evaluation"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Enhanced ForecastBench Runner with Checkpoint Support')
    parser.add_argument('--max-questions', type=int, default=200, help='Maximum number of questions to process')
    parser.add_argument('--max-workers', type=int, default=20, help='Maximum number of parallel workers')
    parser.add_argument('--resume', type=str, help='Resume from checkpoint file (use "latest" for most recent)')
    parser.add_argument('--list-checkpoints', action='store_true', help='List available checkpoints and exit')
    parser.add_argument('--question-ids', type=str, nargs='+', help='Specific question IDs to test (space-separated)')
    parser.add_argument('--failure-questions', action='store_true', help='Test only questions from failure.txt (excludes YulPWDHFTUkekmrO3v4J)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible results')
    parser.add_argument('--time-horizons', type=int, nargs='+', default=[7, 30, 90, 180], help='Time horizons for predictions (in days)')
    parser.add_argument('--search-budget', type=int, default=10, help='Search budget per question')
    parser.add_argument('--debate-turns', type=int, default=2, help='Number of debate turns')
    
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
    
    # Set random seed if provided
    if args.seed is not None:
        import random
        import numpy as np
        random.seed(args.seed)
        np.random.seed(args.seed)
        os.environ["PYTHONHASHSEED"] = str(args.seed)
        print(f"🎲 Random seed set to: {args.seed}")
    
    # Create runner
    runner = EnhancedForecastBenchRunner(
        openrouter_api_key=openrouter_api_key,
        serp_api_key=serp_api_key,
        time_horizons=args.time_horizons,
        search_budget=args.search_budget,
        debate_turns=args.debate_turns
    )
    
    # Handle checkpoint listing
    if args.list_checkpoints:
        checkpoints_dir = Path("checkpoints")
        if checkpoints_dir.exists():
            checkpoint_files = list(checkpoints_dir.glob("benchmark_checkpoint_*.json"))
            if checkpoint_files:
                print("📋 Available checkpoints:")
                for checkpoint_file in sorted(checkpoint_files, key=lambda f: f.stat().st_mtime, reverse=True):
                    try:
                        with open(checkpoint_file, 'r') as f:
                            data = json.load(f)
                        completed = data.get('completed_count', 0)
                        total = data.get('total_questions', 0)
                        timestamp = data.get('run_timestamp', 'unknown')
                        print(f"   {checkpoint_file.name}: {completed}/{total} questions completed (run: {timestamp})")
                    except Exception as e:
                        print(f"   {checkpoint_file.name}: Error reading checkpoint - {e}")
            else:
                print("📋 No checkpoints found")
        else:
            print("📋 Checkpoints directory doesn't exist")
        return
    
    # Handle question ID filtering
    question_ids_to_run = None
    if args.failure_questions:
        question_ids_to_run = extract_question_ids_from_failure_file()
        if question_ids_to_run:
            print(f"🎯 Testing {len(question_ids_to_run)} questions from failure.txt")
        else:
            print("❌ No question IDs found in failure.txt")
            return
    elif args.question_ids:
        question_ids_to_run = args.question_ids
        print(f"🎯 Testing {len(question_ids_to_run)} specific question IDs: {question_ids_to_run}")
    
    print(f"🚀 Starting benchmark with {args.max_questions} questions and {args.max_workers} workers")
    if args.resume:
        print(f"🔄 Will attempt to resume from checkpoint: {args.resume}")
    if question_ids_to_run:
        print(f"🔍 Filtering to specific question IDs: {len(question_ids_to_run)} questions")
    
    # Run benchmark
    results = runner.run_parallel_benchmark(
        max_questions=args.max_questions, 
        max_workers=args.max_workers,
        resume_from_checkpoint=args.resume,
        question_ids=question_ids_to_run
    )
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"enhanced_forecastbench_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📊 Results saved to: {output_file}")
    
    # Print log file information
    print(f"\n📁 LOGGING INFORMATION:")
    print(f"   Master log: {results.get('master_log_file', 'N/A')}")
    print(f"   Individual logs directory: {results.get('logs_directory', 'N/A')}")
    print(f"   Log files pattern: question_*_{results.get('run_timestamp', 'TIMESTAMP')}.json")
    
    # Count individual log files
    if 'results' in results:
        log_files = [r.get('log_file') for r in results['results'] if r.get('log_file')]
        print(f"   Individual log files created: {len(log_files)}")
    
    # Print detailed results with prediction, actual value, and reasoning
    if 'results' in results:
        print(f"\n🎯 DETAILED RESULTS: Predictions, Actual Values, and Reasoning")
        print("=" * 120)
        
        all_brier_scores = []
        for i, result in enumerate(results['results']):
            if result['success']:
                print(f"\nQuestion {i+1}: {result['question_id']}")
                print(f"Question Text: {result['question'][:100]}{'...' if len(result['question']) > 100 else ''}")
                
                # Display freeze information if available
                freeze_value = result.get('freeze_value')
                if freeze_value is not None:
                    try:
                        freeze_val_float = float(freeze_value)
                        print(f"Market Freeze Value: {freeze_val_float:.4f}")
                    except (ValueError, TypeError):
                        print(f"Market Freeze Value: {freeze_value}")
                else:
                    print(f"Market Freeze Value: N/A")
                
                for horizon in [7, 30, 90, 180]:
                    horizon_key = f"{horizon}d"
                    brier = result['brier_scores'].get(horizon_key)
                    prediction_data = result['predictions'].get(horizon_key, {})
                    actual = result['actual_values'].get(horizon_key)
                    
                    print(f"\n  {horizon}-day horizon:")
                    
                    if brier is not None:
                        all_brier_scores.append(brier)
                        print(f"    Brier Score: {brier:.6f}")
                    else:
                        print(f"    Brier Score: N/A")
                    
                    # Prediction
                    prediction = prediction_data.get('prediction')
                    if prediction is not None:
                        print(f"    Prediction: {prediction:.4f}")
                    else:
                        print(f"    Prediction: N/A")
                    
                    # Actual value
                    if actual is not None:
                        print(f"    Actual Value: {actual:.4f}")
                    else:
                        print(f"    Actual Value: N/A")
                    
                    # Show comparison with freeze value if both available
                    if freeze_value is not None and prediction is not None:
                        try:
                            freeze_val_float = float(freeze_value)
                            freeze_diff = abs(prediction - freeze_val_float)
                            print(f"    Difference from Market: {freeze_diff:.4f}")
                        except (ValueError, TypeError):
                            print(f"    Market Value (non-numeric): {freeze_value}")
                            print(f"    Difference from Market: N/A")
                    
                    # Reasoning (truncated for readability)
                    reasoning = prediction_data.get('reasoning', '')
                    if reasoning and isinstance(reasoning, str):
                        # Truncate reasoning to first 200 characters for display
                        reasoning_display = reasoning[:200].strip()
                        if len(reasoning) > 200:
                            reasoning_display += "..."
                        print(f"    Reasoning: {reasoning_display}")
                    else:
                        print(f"    Reasoning: N/A")
                    
                    # Additional info
                    confidence = prediction_data.get('confidence')
                    if confidence:
                        print(f"    Confidence: {confidence}")
                
                print(f"\n{'-' * 100}")
        
        if all_brier_scores:
            average_brier = sum(all_brier_scores) / len(all_brier_scores)
            sum_brier = sum(all_brier_scores)
            print(f"\n📊 SUMMARY STATISTICS:")
            print(f"   Total Brier scores: {len(all_brier_scores)}")
            print(f"   Average Brier score: {average_brier:.6f}")
            print(f"   Sum of all Brier scores: {sum_brier:.6f}")
        else:
            print(f"\n❌ No valid Brier scores calculated")

if __name__ == "__main__":
    main()