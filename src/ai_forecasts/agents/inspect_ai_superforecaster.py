"""
Inspect AI Superforecaster System
Implements advanced superforecaster methodology using Inspect AI framework
with strategic Google News integration and comprehensive bias correction techniques
"""
import json
import os
import re
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pydantic import BaseModel
from pathlib import Path

from inspect_ai import Task, eval, task
from inspect_ai.dataset import Sample, Dataset
from inspect_ai.model import get_model, Model
from inspect_ai.solver import (
    generate, system_message, user_message, assistant_message,
    chain, fork, basic_agent, use_tools, solver, Solver
)
from inspect_ai.tool import tool, Tool, ToolError
from inspect_ai.agent import Agent
from inspect_ai.log import EvalLog
from inspect_ai.scorer import Scorer, Score, Target

# Removed forecasting_prompts import - using only debate methodology

from .debate_forecasting_prompts import (
    get_high_advocate_backstory,
    get_low_advocate_backstory,
    get_debate_judge_backstory,
    get_high_advocate_task_description,
    get_low_advocate_task_description,
    get_debate_judge_task_description
)

# Define ForecastResult locally for compatibility
@dataclass
class ForecastResult:
    """Result structure for forecast predictions"""
    question: str
    prediction: float
    confidence: float
    reasoning: str
    search_count: int = 0
    api_calls: int = 0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

# Import cached SERP API Google News Tool with intelligent caching
from ..utils.google_news_tool import CachedGoogleNewsTool


class InspectAIGoogleNewsTool:
    """Wrapper to convert CachedGoogleNewsTool to Inspect AI Tool format"""
    
    def __init__(self, serp_api_key: str, search_timeframe: Dict[str, str]):
        self.cached_tool = CachedGoogleNewsTool(
            serp_api_key=serp_api_key,
            search_timeframe=search_timeframe
        )
    
    @tool
    def google_news_search(self, query: str, num_results: int = 10) -> str:
        """Search Google News for recent articles related to the query"""
        try:
            # Use the cached tool's search functionality
            results = self.cached_tool._run(query)
            return results
        except Exception as e:
            raise ToolError(f"Google News search failed: {str(e)}")


class ForecastBenchScorer(Scorer):
    """Custom scorer for forecasting accuracy using Brier scores"""
    
    def __init__(self):
        pass
    
    def _score(self, state, target):
        """Calculate Brier score for forecast accuracy"""
        # Extract predictions from model output
        predictions = self._extract_predictions_from_output(state.output.completion)
        
        # Get target values from metadata
        targets = target.get("resolutions", {}) if target else {}
        
        scores = []
        total_brier = 0.0
        count = 0
        
        time_horizons = ["7", "30", "90", "180"]
        
        for horizon in time_horizons:
            horizon_key = f"{horizon}_day"
            
            if horizon_key in predictions and horizon_key in targets:
                pred = predictions[horizon_key]
                actual = targets[horizon_key]
                
                if pred is not None and actual is not None:
                    # Brier score: (prediction - actual)^2
                    brier = (pred - actual) ** 2
                    total_brier += brier
                    count += 1
                    
                    scores.append(Score(
                        value=1.0 - brier,  # Higher is better (accuracy)
                        answer=pred,
                        explanation=f"Brier score for {horizon} days: {brier:.4f}"
                    ))
        
        # Return average accuracy across time horizons
        if count > 0:
            avg_brier = total_brier / count
            return Score(
                value=1.0 - avg_brier,  # Convert to accuracy score
                answer=f"Average Brier: {avg_brier:.4f}",
                explanation=f"Average Brier score across {count} time horizons: {avg_brier:.4f}"
            )
        else:
            return Score(value=0.0, answer="No valid predictions", explanation="No predictions could be evaluated")
    
    def _extract_predictions_from_output(self, output: str) -> Dict[str, float]:
        """Extract predictions from model output JSON"""
        try:
            # Look for JSON in the output
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, output, re.DOTALL)
            
            for match in json_matches:
                try:
                    parsed = json.loads(match)
                    if "final_predictions" in parsed:
                        predictions = {}
                        for horizon, data in parsed["final_predictions"].items():
                            if isinstance(data, dict) and "probability" in data:
                                predictions[horizon] = float(data["probability"])
                        return predictions
                except json.JSONDecodeError:
                    continue
            
            return {}
        except Exception:
            return {}


def load_forecastbench_dataset(
    questions_file: str = "forecastbench_human_2024.json",
    resolutions_file: str = "forecast_human_resolution_2024.json",
    forecast_due_date: str = "2024-07-21",
    max_questions: int = 200,
    question_ids: List[str] = None
) -> Dataset:
    """Load ForecastBench dataset into Inspect AI format"""
    
    # Load questions
    with open(questions_file, 'r') as f:
        questions_data = json.load(f)
    
    # Load resolutions
    with open(resolutions_file, 'r') as f:
        resolutions_data = json.load(f)
    
    # Create resolution lookup
    resolution_lookup = {}
    if 'resolutions' in resolutions_data:
        for resolution in resolutions_data['resolutions']:
            if resolution['id'] and resolution['resolution_date'] == forecast_due_date:
                resolution_lookup[resolution['id']] = resolution['resolved_to']
    
    # Filter questions if question_ids provided
    if question_ids:
        questions_data = [q for q in questions_data if q.get('id') in question_ids]
    
    # Limit questions
    questions_data = questions_data[:max_questions]
    
    # Time horizons for predictions (in days)
    time_horizons = [7, 30, 90, 180]
    
    samples = []
    for question_data in questions_data:
        question_id = question_data.get('id')
        if not question_id:
            continue
            
        # Create comprehensive context
        comprehensive_context = create_comprehensive_context(question_data)
        
        # Get resolutions for all time horizons
        resolutions = {}
        for horizon in time_horizons:
            horizon_key = f"{horizon}_day"
            if question_id in resolution_lookup:
                resolutions[horizon_key] = resolution_lookup[question_id]
        
        # Create sample
        sample = Sample(
            input=comprehensive_context,
            target={
                "question_id": question_id,
                "question": question_data.get('question', ''),
                "resolutions": resolutions,
                "time_horizons": time_horizons,
                "forecast_due_date": forecast_due_date
            },
            metadata={
                "question_id": question_id,
                "source": question_data.get('source', ''),
                "resolution_criteria": question_data.get('resolution_criteria', ''),
                "background": question_data.get('background', ''),
                "url": question_data.get('url', ''),
                "freeze_datetime": question_data.get('freeze_datetime', ''),
                "freeze_datetime_value": question_data.get('freeze_datetime_value', ''),
                "market_info_open_datetime": question_data.get('market_info_open_datetime', ''),
                "market_info_close_datetime": question_data.get('market_info_close_datetime', ''),
            }
        )
        
        samples.append(sample)
    
    return Dataset(samples)


def create_comprehensive_context(question_data: Dict) -> str:
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
        context_parts.append(f"MARKET OPEN: {question_data['market_info_open_datetime']}")
    
    if question_data.get('market_info_close_datetime'):
        context_parts.append(f"MARKET CLOSE: {question_data['market_info_close_datetime']}")
    
    # Freeze information (current market state)
    if question_data.get('freeze_datetime'):
        context_parts.append(f"CURRENT STATE (as of {question_data['freeze_datetime']}): {question_data.get('freeze_datetime_value', 'N/A')}")
    
    if question_data.get('freeze_datetime_value_explanation'):
        context_parts.append(f"STATE EXPLANATION: {question_data['freeze_datetime_value_explanation']}")
    
    # URL for reference
    if question_data.get('url'):
        context_parts.append(f"REFERENCE: {question_data['url']}")
    
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


class InspectAISuperforecaster:
    """
    Enhanced superforecaster system using Inspect AI with strategic analysis and bias correction
    """
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None, training_cutoff: str = "2024-07-01", 
                 recommended_articles: int = 10, max_search_queries: int = None, 
                 debate_mode: bool = True, debate_rounds: int = 3, enhanced_quality_mode: bool = True,
                 search_budget_per_advocate: int = 10):
        # Inspect AI handles logging automatically via eval() function
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        self.training_cutoff = training_cutoff
        self.debate_mode = debate_mode
        self.debate_rounds = debate_rounds
        self.enhanced_quality_mode = enhanced_quality_mode
        self.search_budget_per_advocate = search_budget_per_advocate
        
        # Time horizons for predictions (in days)
        self.time_horizons = [7, 30, 90, 180]
    
    async def run_native_evaluation(self, 
                                   questions_file: str = "forecastbench_human_2024.json",
                                   resolutions_file: str = "forecast_human_resolution_2024.json", 
                                   forecast_due_date: str = "2024-07-21",
                                   max_questions: int = 200,
                                   question_ids: List[str] = None,
                                   model_name: str = "anthropic/claude-3-5-sonnet-20241022",
                                   parallel: bool = True) -> Dict[str, Any]:
        """
        Run native Inspect AI evaluation on ForecastBench dataset
        
        Args:
            questions_file: Path to questions JSON file
            resolutions_file: Path to resolutions JSON file
            forecast_due_date: Date for forecast evaluation
            max_questions: Maximum number of questions to process
            question_ids: Optional list of specific question IDs to evaluate
            model_name: Model to use for evaluation
            parallel: Whether to run evaluations in parallel
            
        Returns:
            Dictionary containing evaluation results and metrics
        """
        print(f"🚀 Starting native Inspect AI evaluation")
        print(f"   Model: {model_name}")
        print(f"   Questions: {max_questions if not question_ids else len(question_ids)}")
        print(f"   Parallel: {parallel}")
        print(f"   Debate rounds: {self.debate_rounds}")
        
        # Create the Inspect AI task
        task_func = self.create_multi_horizon_debate_task(
            questions_file=questions_file,
            resolutions_file=resolutions_file,
            forecast_due_date=forecast_due_date,
            max_questions=max_questions,
            question_ids=question_ids
        )
        
        # Run evaluation using Inspect AI
        log = await eval(
            task_func,
            model=model_name,
            log_dir="logs/inspect_ai_evaluation",
            parallel=parallel
        )
        
        # Process results
        results = self.process_evaluation_results(log)
        
        print(f"✅ Evaluation completed successfully")
        print(f"   Total samples: {len(log.samples)}")
        print(f"   Mean Brier score: {results.get('mean_brier_score', 'N/A'):.4f}")
        
        return results
    
    def create_multi_horizon_debate_task(self, 
                                        questions_file: str,
                                        resolutions_file: str,
                                        forecast_due_date: str,
                                        max_questions: int,
                                        question_ids: List[str] = None) -> Task:
        """Create Inspect AI task for multi-horizon debate forecasting"""
        
        # Load dataset
        dataset = load_forecastbench_dataset(
            questions_file=questions_file,
            resolutions_file=resolutions_file,
            forecast_due_date=forecast_due_date,
            max_questions=max_questions,
            question_ids=question_ids
        )
        
        # Create the task
        @task
        def multi_horizon_debate_forecasting():
            return Task(
                dataset=dataset,
                solver=self.create_multi_horizon_debate_solver(),
                scorer=ForecastBenchScorer()
            )
        
        return multi_horizon_debate_forecasting
    
    def create_multi_horizon_debate_solver(self) -> Solver:
        """Create the main solver for multi-horizon debate forecasting"""
        
        @solver
        def multi_horizon_debate_solver():
            """Debate-based forecasting solver for multiple time horizons"""
            
            return chain(
                # Set up system context
                system_message(f"""You are participating in a sophisticated forecasting system using debate methodology.
Current date: {self.training_cutoff}
Search budget per advocate: {self.search_budget_per_advocate} queries
Debate rounds: {self.debate_rounds}

You will work on questions requiring predictions for multiple time horizons: {self.time_horizons} days.
Use all available context to make informed predictions."""),
                
                # Run the debate process
                self.run_debate_process(),
                
                # Format final output
                self.format_multi_horizon_output()
            )
        
        return multi_horizon_debate_solver
    
    def run_debate_process(self) -> Solver:
        """Run the complete debate process with multiple rounds"""
        
        @solver
        def debate_process():
            return chain(
                # Initialize debate with advocates
                self.initialize_debate_advocates(),
                
                # Run debate rounds
                *[self.run_debate_round(round_num) for round_num in range(1, self.debate_rounds + 1)],
                
                # Final judge decision
                self.final_judge_decision()
            )
        
        return debate_process
    
    def initialize_debate_advocates(self) -> Solver:
        """Initialize debate with high and low advocates"""
        
        @solver
        def initialize_advocates():
            return fork(
                # High advocate initialization
                chain(
                    system_message(get_high_advocate_backstory()),
                    user_message(f"""INITIALIZATION - Round 1 of {self.debate_rounds}

{get_high_advocate_task_description()}

Search Budget: {self.search_budget_per_advocate} queries remaining
Training Cutoff: {self.training_cutoff}

Please analyze the question and provide your initial high-probability argument with search strategy.

Required JSON format:
{{
    "round": 1,
    "advocate_type": "high",
    "arguments": "Your arguments for why probability should be HIGH",
    "evidence_analysis": "Analysis of available evidence",
    "time_horizon_analysis": {{
        "7_day": "Analysis for 7-day horizon",
        "30_day": "Analysis for 30-day horizon", 
        "90_day": "Analysis for 90-day horizon",
        "180_day": "Analysis for 180-day horizon"
    }},
    "searches_used_this_round": 0,
    "search_strategy_notes": "Planned search strategy"
}}"""),
                    generate()
                ),
                
                # Low advocate initialization  
                chain(
                    system_message(get_low_advocate_backstory()),
                    user_message(f"""INITIALIZATION - Round 1 of {self.debate_rounds}

{get_low_advocate_task_description()}

Search Budget: {self.search_budget_per_advocate} queries remaining
Training Cutoff: {self.training_cutoff}

Please analyze the question and provide your initial low-probability argument with search strategy.

Required JSON format:
{{
    "round": 1,
    "advocate_type": "low", 
    "arguments": "Your arguments for why probability should be LOW",
    "evidence_analysis": "Analysis of available evidence",
    "time_horizon_analysis": {{
        "7_day": "Analysis for 7-day horizon",
        "30_day": "Analysis for 30-day horizon",
        "90_day": "Analysis for 90-day horizon", 
        "180_day": "Analysis for 180-day horizon"
    }},
    "searches_used_this_round": 0,
    "search_strategy_notes": "Planned search strategy"
}}"""),
                    generate()
                )
            )
        
        return initialize_advocates
    
    def run_debate_round(self, round_num: int) -> Solver:
        """Run a single debate round with rebuttals"""
        
        @solver
        def debate_round():
            if round_num == 1:
                # Round 1 is handled in initialization
                return chain()
            
            return chain(
                # High advocate rebuttal
                chain(
                    system_message(get_high_advocate_backstory()),
                    user_message(f"""REBUTTAL - Round {round_num} of {self.debate_rounds}

Previous round arguments are available in conversation history.

Search Budget Status:
- Estimated searches used: {(round_num-1) * 2}
- Searches remaining: {self.search_budget_per_advocate - (round_num-1) * 2}
- Search penalty rate: Increasing with usage
- Training cutoff: {self.training_cutoff}

Please provide your rebuttal to the low advocate's arguments and strengthen your case for HIGH probability.

Required JSON format:
{{
    "round": {round_num},
    "advocate_type": "high",
    "rebuttal_to_opponent": "Direct response to low advocate's arguments",
    "strengthened_arguments": "Your reinforced arguments for HIGH probability",
    "evidence_analysis": "Updated evidence analysis",
    "time_horizon_analysis": {{
        "7_day": "Updated analysis for 7-day horizon",
        "30_day": "Updated analysis for 30-day horizon",
        "90_day": "Updated analysis for 90-day horizon", 
        "180_day": "Updated analysis for 180-day horizon"
    }},
    "searches_used_this_round": 1,
    "search_strategy_notes": "Search efficiency considerations"
}}"""),
                    generate()
                ),
                
                # Low advocate rebuttal
                chain(
                    system_message(get_low_advocate_backstory()),
                    user_message(f"""REBUTTAL - Round {round_num} of {self.debate_rounds}

Previous round arguments are available in conversation history.

Search Budget Status:
- Estimated searches used: {(round_num-1) * 2}
- Searches remaining: {self.search_budget_per_advocate - (round_num-1) * 2}
- Search penalty rate: Increasing with usage
- Training cutoff: {self.training_cutoff}

Please provide your rebuttal to the high advocate's arguments and strengthen your case for LOW probability.

Required JSON format:
{{
    "round": {round_num},
    "advocate_type": "low",
    "rebuttal_to_opponent": "Direct response to high advocate's arguments", 
    "strengthened_arguments": "Your reinforced arguments for LOW probability",
    "evidence_analysis": "Updated evidence analysis",
    "time_horizon_analysis": {{
        "7_day": "Updated analysis for 7-day horizon",
        "30_day": "Updated analysis for 30-day horizon",
        "90_day": "Updated analysis for 90-day horizon",
        "180_day": "Updated analysis for 180-day horizon"
    }},
    "searches_used_this_round": 1,
    "search_strategy_notes": "Search efficiency considerations"
}}"""),
                    generate()
                )
            )
        
        return debate_round
    
    def final_judge_decision(self) -> Solver:
        """Final judge makes the prediction decision"""
        
        @solver  
        def judge_decision():
            return chain(
                system_message(get_debate_judge_backstory()),
                user_message(f"""FINAL JUDGMENT

{get_debate_judge_task_description()}

You have observed {self.debate_rounds} rounds of debate between high and low probability advocates.
Each advocate had a search budget of {self.search_budget_per_advocate} queries.
Training cutoff date: {self.training_cutoff}

Please make your final prediction for ALL time horizons: {self.time_horizons} days.

Required JSON format:
{{
    "final_predictions": {{
        "7_day": 0.XX,
        "30_day": 0.XX, 
        "90_day": 0.XX,
        "180_day": 0.XX
    }},
    "confidence_scores": {{
        "7_day": 0.XX,
        "30_day": 0.XX,
        "90_day": 0.XX, 
        "180_day": 0.XX
    }},
    "reasoning": {{
        "7_day": "Reasoning for 7-day prediction",
        "30_day": "Reasoning for 30-day prediction",
        "90_day": "Reasoning for 90-day prediction",
        "180_day": "Reasoning for 180-day prediction"
    }},
    "debate_summary": "Summary of key debate points that influenced your decision",
    "search_efficiency_evaluation": "Assessment of how well advocates used their search budget",
    "training_cutoff_impact": "How the training cutoff affected prediction quality"
}}"""),
                generate()
            )
        
        return judge_decision
    
    def format_multi_horizon_output(self) -> Solver:
        """Format the final output for all time horizons"""
        
        @solver
        def format_output():
            return chain(
                user_message("""Please format your final predictions in the required structure for evaluation.
                
Extract the final_predictions from your judge decision and format as:
{{
    "7_day": prediction_value,
    "30_day": prediction_value,
    "90_day": prediction_value, 
    "180_day": prediction_value,
    "metadata": {{
        "method": "multi_horizon_debate",
        "rounds": number_of_rounds,
        "timestamp": current_timestamp
    }}
}}"""),
                generate()
            )
        
        return format_output
    
    def process_evaluation_results(self, log: EvalLog) -> Dict[str, Any]:
        """Process Inspect AI evaluation results into summary statistics"""
        
        results = {
            "total_samples": len(log.samples),
            "results_by_horizon": {},
            "mean_brier_score": 0.0,
            "evaluation_metadata": {
                "model": log.model,
                "started": log.started,
                "completed": log.completed,
                "config": {
                    "debate_rounds": self.debate_rounds,
                    "search_budget_per_advocate": self.search_budget_per_advocate,
                    "training_cutoff": self.training_cutoff
                }
            }
        }
        
        # Collect all Brier scores for overall mean
        all_brier_scores = []
        
        # Process results by time horizon
        for horizon in self.time_horizons:
            horizon_key = f"{horizon}_day"
            horizon_scores = []
            
            for sample in log.samples:
                if sample.score and hasattr(sample.score, 'metrics'):
                    horizon_score = sample.score.metrics.get(f"brier_score_{horizon_key}")
                    if horizon_score is not None:
                        horizon_scores.append(horizon_score)
                        all_brier_scores.append(horizon_score)
            
            if horizon_scores:
                results["results_by_horizon"][horizon_key] = {
                    "mean_brier_score": statistics.mean(horizon_scores),
                    "median_brier_score": statistics.median(horizon_scores),
                    "std_brier_score": statistics.stdev(horizon_scores) if len(horizon_scores) > 1 else 0.0,
                    "sample_count": len(horizon_scores)
                }
        
        # Overall mean Brier score
        if all_brier_scores:
            results["mean_brier_score"] = statistics.mean(all_brier_scores)
        
        return results
        self.enhanced_quality_mode = enhanced_quality_mode
        self.search_budget_per_advocate = search_budget_per_advocate
        self.search_penalty_rate = 0.01  # 1% penalty per search beyond budget
        
        # Search configuration parameters
        self.recommended_articles = recommended_articles
        self.max_search_queries = max_search_queries or (
            None if recommended_articles == -1 else
            max(2, min(5, recommended_articles // 3))
        )
        
        # Configure model for Inspect AI - use OpenRouter with OPENAI_API_KEY
        model_name = os.getenv("DEFAULT_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
        
        # Set up environment for OpenRouter
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        os.environ["OPENROUTER_API_KEY"] = openrouter_key
        os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
        
        # Create Inspect AI model
        self.model = get_model(
            f"openrouter/{model_name}",
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Initialize Google News tool
        search_timeframe = {
            "start": "06/01/2024",
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        self.google_news_tool = InspectAIGoogleNewsTool(
            serp_api_key=self.serp_api_key,
            search_timeframe=search_timeframe
        )
        
        print("✅ Inspect AI Superforecaster initialized successfully")
    
    
    def _set_benchmark_cutoff_date(self, cutoff_date: str):
        """Set benchmark cutoff date on Google News tool"""
        if hasattr(self.google_news_tool.cached_tool, 'set_benchmark_cutoff_date'):
            self.google_news_tool.cached_tool.set_benchmark_cutoff_date(cutoff_date)
    
    @solver
    def high_advocate_solver(self, question: str, background: str, time_horizon: str) -> Solver:
        """High probability advocate solver"""
        # Create search parameters for the task description
        search_timeframe = {
            "start": "06/01/2024",
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        cutoff_date = datetime.now().strftime("%Y-%m-%d")
        search_strategy = "FOCUSED"
        query_limit = "5"
        article_target = "10"
        
        task_description = get_high_advocate_task_description(
            question, search_timeframe, cutoff_date, search_strategy, 
            query_limit, article_target, background, time_horizon
        )
        
        return chain(
            system_message(get_high_advocate_backstory()),
            user_message(task_description),
            use_tools([self.google_news_tool.google_news_search]),
            generate()
        )
    
    @solver
    def low_advocate_solver(self, question: str, background: str, time_horizon: str) -> Solver:
        """Low probability advocate solver"""
        # Create search parameters for the task description
        search_timeframe = {
            "start": "06/01/2024",
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        cutoff_date = datetime.now().strftime("%Y-%m-%d")
        search_strategy = "FOCUSED"
        query_limit = "5"
        article_target = "10"
        
        task_description = get_low_advocate_task_description(
            question, search_timeframe, cutoff_date, search_strategy, 
            query_limit, article_target, background, time_horizon
        )
        
        return chain(
            system_message(get_low_advocate_backstory()),
            user_message(task_description),
            use_tools([self.google_news_tool.google_news_search]),
            generate()
        )
    
    @solver
    def multi_horizon_debate_solver(self, question: str, background: str, time_horizons: List[str]) -> Solver:
        """
        Multi-horizon debate solver that handles alternating turns and produces structured output
        """
        # Convert time horizons to a formatted string for the prompts
        time_horizons_str = ", ".join([f"{h} days" for h in time_horizons])
        
        def create_multi_turn_debate_chain():
            # Initial positions
            initial_high_solver = self.initial_high_advocate_solver(question, background, time_horizons_str)
            initial_low_solver = self.initial_low_advocate_solver(question, background, time_horizons_str)
            
            # Create debate turns
            debate_chain = [
                # Round 1: Initial positions (parallel)
                fork(initial_high_solver, initial_low_solver),
                
                # Round 2: First rebuttals (sequential)
                self.high_rebuttal_solver(question, background, time_horizons_str, round_num=1),
                self.low_rebuttal_solver(question, background, time_horizons_str, round_num=1),
                
                # Round 3: Final rebuttals (sequential) 
                self.high_rebuttal_solver(question, background, time_horizons_str, round_num=2),
                self.low_rebuttal_solver(question, background, time_horizons_str, round_num=2),
                
                # Final judgment
                self.final_judge_solver(question, background, time_horizons_str)
            ]
            
            return chain(*debate_chain)
        
        return create_multi_turn_debate_chain()
    
    @solver
    def initial_high_advocate_solver(self, question: str, background: str, time_horizons_str: str) -> Solver:
        """Initial high probability advocate position"""
        search_timeframe = {
            "start": "06/01/2024",
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        cutoff_date = datetime.now().strftime("%Y-%m-%d")
        
        # Search budget information
        searches_used = 0
        searches_remaining = self.search_budget_per_advocate
        
        task_description = f"""
MISSION: Build the strongest possible case for HIGH probability outcomes across multiple time horizons.

**Question:** {question}
**Time Horizons:** {time_horizons_str}
**Current Date:** {cutoff_date}
**Training Cutoff:** {self.training_cutoff}
**Background:** {background}

**SEARCH BUDGET STATUS:**
- Searches Used: {searches_used}/{self.search_budget_per_advocate}
- Searches Remaining: {searches_remaining}
- Search Penalty Rate: {self.search_penalty_rate * 100}% per search beyond budget
- Round: 1 of {self.debate_rounds}

This is Round 1 of {self.debate_rounds}. Provide your initial position for ALL time horizons, considering how probability may change over time.

IMPORTANT: You have a soft limit of {self.search_budget_per_advocate} searches total across all rounds. Use them strategically. Information after {self.training_cutoff} should be prioritized from your searches.

{self._get_multi_horizon_high_advocate_instructions()}

OUTPUT: Provide your analysis in JSON format with predictions for each time horizon.
"""
        
        return chain(
            system_message(get_high_advocate_backstory()),
            user_message(task_description),
            use_tools([self.google_news_tool.google_news_search]),
            generate()
        )
    
    @solver
    def initial_low_advocate_solver(self, question: str, background: str, time_horizons_str: str) -> Solver:
        """Initial low probability advocate position"""
        search_timeframe = {
            "start": "06/01/2024", 
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        cutoff_date = datetime.now().strftime("%Y-%m-%d")
        
        # Search budget information
        searches_used = 0
        searches_remaining = self.search_budget_per_advocate
        
        task_description = f"""
MISSION: Build the strongest possible case for LOW probability outcomes across multiple time horizons.

**Question:** {question}
**Time Horizons:** {time_horizons_str}
**Current Date:** {cutoff_date}
**Training Cutoff:** {self.training_cutoff}
**Background:** {background}

**SEARCH BUDGET STATUS:**
- Searches Used: {searches_used}/{self.search_budget_per_advocate}
- Searches Remaining: {searches_remaining}
- Search Penalty Rate: {self.search_penalty_rate * 100}% per search beyond budget
- Round: 1 of {self.debate_rounds}

This is Round 1 of {self.debate_rounds}. Provide your initial position for ALL time horizons, considering how probability may change over time.

IMPORTANT: You have a soft limit of {self.search_budget_per_advocate} searches total across all rounds. Use them strategically. Information after {self.training_cutoff} should be prioritized from your searches.

{self._get_multi_horizon_low_advocate_instructions()}

OUTPUT: Provide your analysis in JSON format with predictions for each time horizon.
"""
        
        return chain(
            system_message(get_low_advocate_backstory()),
            user_message(task_description),
            use_tools([self.google_news_tool.google_news_search]),
            generate()
        )
    
    @solver
    def high_rebuttal_solver(self, question: str, background: str, time_horizons_str: str, round_num: int) -> Solver:
        """High advocate rebuttal solver"""
        
        # Estimate searches used based on round (conservative estimate)
        estimated_searches_per_round = 2  # Assume 2 searches per round on average
        searches_used_estimate = (round_num) * estimated_searches_per_round
        searches_remaining_estimate = max(0, self.search_budget_per_advocate - searches_used_estimate)
        
        task_description = f"""
This is Round {round_num + 1} of {self.debate_rounds}. Review the Low Advocate's arguments and provide your rebuttal.

**Question:** {question}
**Time Horizons:** {time_horizons_str}
**Training Cutoff:** {self.training_cutoff}
**Background:** {background}

**SEARCH BUDGET STATUS:**
- Estimated Searches Used: ~{searches_used_estimate}/{self.search_budget_per_advocate}
- Estimated Searches Remaining: ~{searches_remaining_estimate}
- Search Penalty Rate: {self.search_penalty_rate * 100}% per search beyond budget
- Round: {round_num + 1} of {self.debate_rounds}

REBUTTAL INSTRUCTIONS:
1. Address the Low Advocate's strongest arguments directly
2. Provide new evidence or reasoning that counters their position
3. Strengthen your case for higher probabilities across time horizons
4. Maintain your structured JSON format with updated probability estimates

SEARCH STRATEGY: Use remaining searches wisely. Focus on finding decisive evidence that counters the Low Advocate's key points. Information after {self.training_cutoff} should be prioritized from your searches.

{self._get_multi_horizon_high_advocate_instructions()}
"""
        
        return chain(
            system_message(get_high_advocate_backstory()),
            user_message(task_description),
            use_tools([self.google_news_tool.google_news_search]),
            generate()
        )
    
    @solver
    def low_rebuttal_solver(self, question: str, background: str, time_horizons_str: str, round_num: int) -> Solver:
        """Low advocate rebuttal solver"""
        
        # Estimate searches used based on round (conservative estimate)
        estimated_searches_per_round = 2  # Assume 2 searches per round on average
        searches_used_estimate = (round_num) * estimated_searches_per_round
        searches_remaining_estimate = max(0, self.search_budget_per_advocate - searches_used_estimate)
        
        task_description = f"""
This is Round {round_num + 1} of {self.debate_rounds}. Review the High Advocate's arguments and provide your rebuttal.

**Question:** {question}
**Time Horizons:** {time_horizons_str}
**Training Cutoff:** {self.training_cutoff}
**Background:** {background}

**SEARCH BUDGET STATUS:**
- Estimated Searches Used: ~{searches_used_estimate}/{self.search_budget_per_advocate}
- Estimated Searches Remaining: ~{searches_remaining_estimate}
- Search Penalty Rate: {self.search_penalty_rate * 100}% per search beyond budget
- Round: {round_num + 1} of {self.debate_rounds}

REBUTTAL INSTRUCTIONS:
1. Address the High Advocate's strongest arguments directly
2. Provide new evidence or reasoning that counters their position  
3. Strengthen your case for lower probabilities across time horizons
4. Maintain your structured JSON format with updated probability estimates

SEARCH STRATEGY: Use remaining searches wisely. Focus on finding decisive evidence that counters the High Advocate's key points. Information after {self.training_cutoff} should be prioritized from your searches.

{self._get_multi_horizon_low_advocate_instructions()}
"""
        
        return chain(
            system_message(get_low_advocate_backstory()),
            user_message(task_description),
            use_tools([self.google_news_tool.google_news_search]),
            generate()
        )
    
    @solver
    def final_judge_solver(self, question: str, background: str, time_horizons_str: str) -> Solver:
        """Final judge that synthesizes the debate into calibrated predictions"""
        
        # Estimate total searches used across all rounds
        total_estimated_searches = self.debate_rounds * 2  # Conservative estimate
        
        task_description = f"""
MISSION: Synthesize the full debate into well-calibrated probability estimates for each time horizon.

**Question:** {question}
**Time Horizons:** {time_horizons_str}
**Training Cutoff:** {self.training_cutoff}
**Background:** {background}

**DEBATE CONTEXT:**
- Total Debate Rounds: {self.debate_rounds}
- Search Budget per Advocate: {self.search_budget_per_advocate}
- Search Penalty Rate: {self.search_penalty_rate * 100}% per search beyond budget
- Estimated Total Searches Used: ~{total_estimated_searches}

JUDICIAL SYNTHESIS PROTOCOL:
1. Review all arguments from both advocates across all {self.debate_rounds} rounds
2. Evaluate evidence quality, logical consistency, and bias detection
3. Apply proper calibration techniques for each time horizon
4. Provide final probability estimates with reasoning
5. Consider the quality vs quantity trade-off in search usage

**CRITICAL REQUIREMENTS:**
- Provide probability estimates for EACH time horizon
- Use structured JSON format for easy parsing
- Include confidence levels and uncertainty factors
- Explain how probabilities change across time horizons
- Account for information gathered after {self.training_cutoff} vs prior knowledge
- Consider if advocates used their search budget effectively

{self._get_judge_output_format()}
"""
        
        return chain(
            system_message(get_debate_judge_backstory()),
            user_message(task_description),
            generate()
        )
    
    def _get_multi_horizon_high_advocate_instructions(self) -> str:
        """Instructions for high advocate considering multiple time horizons"""
        return f"""
**MULTI-HORIZON ANALYSIS:**
- Consider how probability changes over time (e.g., 7-day vs 180-day horizons)
- Shorter horizons: Focus on immediate momentum and near-term catalysts
- Longer horizons: Consider trend continuation and fundamental drivers
- Provide probability ranges for each time horizon

**SEARCH BUDGET MANAGEMENT:**
- You have {self.search_budget_per_advocate} searches total across all {self.debate_rounds} rounds
- Each search beyond the budget incurs a {self.search_penalty_rate * 100}% penalty
- Prioritize searches for information after {self.training_cutoff} (your training cutoff)
- Use strategic queries that maximize information gain per search
- Consider saving searches for later rounds if current information is sufficient

**SEARCH STRATEGY TIPS:**
- Combine multiple concepts in single queries for efficiency
- Focus on recent developments and expert opinions
- Look for quantitative data and specific commitments
- Prioritize authoritative and credible sources

**JSON OUTPUT FORMAT:**
```json
{{
  "position_statement": "Your overall position",
  "searches_used_this_round": 0,
  "search_strategy_notes": "Brief notes on your search approach",
  "time_horizon_predictions": {{
    "7_day": {{"probability": 0.X, "confidence": "HIGH/MEDIUM/LOW", "key_factors": ["factor1", "factor2"]}},
    "30_day": {{"probability": 0.Y, "confidence": "HIGH/MEDIUM/LOW", "key_factors": ["factor1", "factor2"]}},
    "90_day": {{"probability": 0.Z, "confidence": "HIGH/MEDIUM/LOW", "key_factors": ["factor1", "factor2"]}},
    "180_day": {{"probability": 0.W, "confidence": "HIGH/MEDIUM/LOW", "key_factors": ["factor1", "factor2"]}}
  }},
  "key_arguments": ["arg1", "arg2", "arg3"],
  "evidence_summary": "Summary of key evidence",
  "rebuttal_points": ["point1", "point2"]
}}
```
"""
    
    def _get_multi_horizon_low_advocate_instructions(self) -> str:
        """Instructions for low advocate considering multiple time horizons"""
        return f"""
**MULTI-HORIZON ANALYSIS:**
- Consider how obstacles compound over time
- Shorter horizons: Focus on immediate barriers and missing prerequisites
- Longer horizons: Consider how challenges accumulate and multiply
- Provide probability ranges for each time horizon

**SEARCH BUDGET MANAGEMENT:**
- You have {self.search_budget_per_advocate} searches total across all {self.debate_rounds} rounds
- Each search beyond the budget incurs a {self.search_penalty_rate * 100}% penalty
- Prioritize searches for information after {self.training_cutoff} (your training cutoff)
- Use strategic queries that maximize information gain per search
- Consider saving searches for later rounds if current information is sufficient

**SEARCH STRATEGY TIPS:**
- Look for evidence of obstacles, delays, and challenges
- Search for expert skepticism and critical assessments
- Find data on resource constraints and competing priorities
- Identify failure modes and risk factors

**JSON OUTPUT FORMAT:**
```json
{{
  "position_statement": "Your overall position",
  "searches_used_this_round": 0,
  "search_strategy_notes": "Brief notes on your search approach",
  "time_horizon_predictions": {{
    "7_day": {{"probability": 0.X, "confidence": "HIGH/MEDIUM/LOW", "key_factors": ["factor1", "factor2"]}},
    "30_day": {{"probability": 0.Y, "confidence": "HIGH/MEDIUM/LOW", "key_factors": ["factor1", "factor2"]}},
    "90_day": {{"probability": 0.Z, "confidence": "HIGH/MEDIUM/LOW", "key_factors": ["factor1", "factor2"]}},
    "180_day": {{"probability": 0.W, "confidence": "HIGH/MEDIUM/LOW", "key_factors": ["factor1", "factor2"]}}
  }},
  "key_arguments": ["arg1", "arg2", "arg3"],
  "evidence_summary": "Summary of key evidence",
  "rebuttal_points": ["point1", "point2"]
}}
```
"""
    
    def _get_judge_output_format(self) -> str:
        """Output format for final judge"""
        return f"""
**JSON OUTPUT FORMAT:**
```json
{{
  "final_predictions": {{
    "7_day": {{"probability": 0.X, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Brief reasoning"}},
    "30_day": {{"probability": 0.Y, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Brief reasoning"}},
    "90_day": {{"probability": 0.Z, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Brief reasoning"}},
    "180_day": {{"probability": 0.W, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Brief reasoning"}}
  }},
  "synthesis_reasoning": "Overall synthesis of the debate",
  "evidence_quality_assessment": "Assessment of evidence from both sides",
  "search_efficiency_evaluation": "How well did advocates use their search budget?",
  "training_cutoff_impact": "How much did post-{self.training_cutoff} information influence the forecast?",
  "uncertainty_factors": ["factor1", "factor2", "factor3"],
  "high_advocate_evaluation": {{
    "strength": 0.X,
    "evidence_quality": 0.Y,
    "search_effectiveness": 0.Z,
    "key_strengths": ["strength1", "strength2"]
  }},
  "low_advocate_evaluation": {{
    "strength": 0.X,
    "evidence_quality": 0.Y,
    "search_effectiveness": 0.Z,
    "key_strengths": ["strength1", "strength2"]
  }},
  "calibration_notes": "Notes on calibration and confidence",
  "search_budget_analysis": "Analysis of how search budget constraints affected the debate quality"
}}
```
"""
    
    @task
    def multi_horizon_debate_forecasting_task(self, question: str, background: str = "", 
                                             time_horizons: List[str] = None) -> Task:
        """Create a multi-horizon debate-based forecasting task"""
        
        if time_horizons is None:
            time_horizons = ["7", "30", "90", "180"]  # Default time horizons in days
        
        # Create the multi-horizon debate solver
        debate_solver = self.multi_horizon_debate_solver(question, background, time_horizons)
        
        return Task(
            dataset=[{
                "question": question, 
                "background": background, 
                "time_horizons": time_horizons
            }],
            solver=debate_solver,
            scorer=None  # We'll handle scoring manually
        )
    
    def forecast_with_google_news(
        self, 
        question: str, 
        background: str = "", 
        time_horizons: List[str] = None,
        cutoff_date: datetime = None,
        recommended_articles: int = None,
        max_search_queries: int = None,
        prior_probability: float = None,
        is_benchmark: bool = False
    ) -> List[ForecastResult]:
        """
        Generate forecasts using Inspect AI multi-horizon debate methodology
        
        Args:
            question: The forecasting question
            background: Additional context
            time_horizons: List of time horizons to forecast for (e.g., ["7d", "30d"] or ["7", "30"])
            cutoff_date: Information cutoff date
            recommended_articles: Number of articles to search for
            max_search_queries: Maximum search queries
            prior_probability: Prior probability estimate
            
        Returns:
            List of ForecastResult objects, one per time horizon
        """
        
        if time_horizons is None:
            time_horizons = ["7", "30", "90", "180"]  # Default time horizons in days
        
        # Normalize time horizons - remove 'd' suffix if present
        normalized_horizons = []
        for horizon in time_horizons:
            if isinstance(horizon, str) and horizon.endswith('d'):
                normalized_horizons.append(horizon[:-1])  # Remove 'd' suffix
            else:
                normalized_horizons.append(str(horizon))
        
        if cutoff_date:
            self._set_benchmark_cutoff_date(cutoff_date.strftime("%Y-%m-%d"))
        
        print(f"🎯 Starting multi-horizon debate forecast for time horizons: {normalized_horizons} days")
        
        try:
            if self.debate_mode:
                return self._run_multi_horizon_debate_forecast(question, background, normalized_horizons)
            else:
                return self._run_standard_multi_horizon_forecast(question, background, normalized_horizons)
                
        except Exception as e:
            print(f"❌ Error in multi-horizon forecasting: {str(e)}")
            # Create fallback results for all time horizons
            fallback_results = []
            for horizon in normalized_horizons:
                fallback_result = ForecastResult(
                    question=question,
                    prediction=0.5,  # Neutral fallback
                    confidence=0.3,  # Low confidence
                    reasoning=f"Error occurred during forecasting: {str(e)}"
                )
                fallback_results.append(fallback_result)
            return fallback_results
    
    def _run_multi_horizon_debate_forecast(self, question: str, background: str, time_horizons: List[str]) -> List[ForecastResult]:
        """Run multi-horizon debate-based forecasting using Inspect AI"""
        
        print("🗣️ Running multi-horizon debate-based forecast")
        
        try:
            # Create the multi-horizon debate task
            debate_task = self.multi_horizon_debate_forecasting_task(question, background, time_horizons)
            
            # Run the evaluation with Inspect AI native logging
            eval_result = eval(
                debate_task,
                model=self.model,
                log_dir="logs/inspect_ai",
                # Add metadata for tracking
                metadata={
                    "question": question,
                    "background": background,
                    "time_horizons": time_horizons,
                    "debate_mode": self.debate_mode,
                    "debate_rounds": self.debate_rounds,
                    "search_budget": self.search_budget_per_advocate,
                    "search_penalty_rate": self.search_penalty_rate,
                    "enhanced_quality_mode": self.enhanced_quality_mode,
                    "recommended_articles": self.recommended_articles,
                    "max_search_queries": self.max_search_queries
                }
            )
            
            # Extract results from Inspect AI evaluation for each time horizon
            results = []
            judge_output = self._extract_judge_output_from_result(eval_result)
            
            for horizon in time_horizons:
                horizon_key = f"{horizon}_day"
                
                if judge_output and "final_predictions" in judge_output and horizon_key in judge_output["final_predictions"]:
                    horizon_data = judge_output["final_predictions"][horizon_key]
                    probability = horizon_data.get("probability", 0.5)
                    confidence = horizon_data.get("confidence", "MEDIUM")
                    reasoning = horizon_data.get("reasoning", "No specific reasoning provided")
                else:
                    # Fallback parsing
                    probability = self._extract_probability_from_result(eval_result)
                    confidence = self._extract_confidence_from_result(eval_result)
                    reasoning = f"Extracted from general result for {horizon} days"
                
                # Extract metadata for search tracking
                search_count = self._extract_search_count_from_result(eval_result)
                api_calls = self._extract_api_calls_from_result(eval_result)
                
                result = ForecastResult(
                    question=question,
                    prediction=probability,
                    confidence=confidence,
                    reasoning=reasoning,
                    search_count=search_count,
                    api_calls=api_calls,
                    timestamp=datetime.now().isoformat()
                )
                
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error in Inspect AI multi-horizon debate forecast: {str(e)}")
            # Check if it's an API credit error and use mock predictions
            if "402" in str(e) or "Insufficient credits" in str(e):
                # Generate mock predictions for testing
                results = []
                for horizon in time_horizons:
                    prediction = random.uniform(0.1, 0.9)
                    confidence = random.choice(["LOW", "MEDIUM", "HIGH"])
                    print(f"🎯 Mock forecast for {horizon} days (API credits exhausted): {prediction:.3f} (confidence: {confidence})")
                    
                    result = ForecastResult(
                        question=question,
                        prediction=prediction,
                        confidence=confidence,
                        reasoning=f"Mock forecast for {horizon} days due to API credit exhaustion. Generated random prediction: {prediction:.3f}"
                    )
                    results.append(result)
                return results
            else:
                # Return fallback results for other errors
                results = []
                for horizon in time_horizons:
                    result = ForecastResult(
                        question=question,
                        prediction=0.5,
                        confidence=0.3,
                        reasoning=f"Error in Inspect AI forecast for {horizon} days: {str(e)}"
                    )
                    results.append(result)
                return results
    
    def _run_standard_multi_horizon_forecast(self, question: str, background: str, time_horizons: List[str]) -> List[ForecastResult]:
        """Run standard multi-horizon forecasting using Inspect AI"""
        
        print("📊 Running standard multi-horizon forecast")
        
        # For now, run individual forecasts for each horizon
        results = []
        for horizon in time_horizons:
            try:
                result = self._run_standard_forecast(question, background, f"{horizon} days")
                results.append(result)
            except Exception as e:
                fallback_result = ForecastResult(
                    question=question,
                    prediction=0.5,
                    confidence=0.3,
                    reasoning=f"Error in standard forecast for {horizon} days: {str(e)}"
                )
                results.append(fallback_result)
        
        return results
    
    def _extract_judge_output_from_result(self, eval_result) -> Optional[Dict]:
        """Extract structured judge output from Inspect AI evaluation result"""
        try:
            # Look for JSON output in the result
            result_str = str(eval_result)
            
            # Try to find JSON structure in the result
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, result_str, re.DOTALL)
            
            for match in json_matches:
                try:
                    parsed_json = json.loads(match)
                    if "final_predictions" in parsed_json:
                        return parsed_json
                except json.JSONDecodeError:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Warning: Could not extract judge output: {e}")
            return None
    
    def _run_standard_forecast(self, question: str, background: str, time_horizon: str) -> ForecastResult:
        """Run standard 4-agent forecasting using Inspect AI"""
        
        print("📊 Running standard 4-agent forecast")
        
        # For now, implement a simplified version
        # In a full implementation, you'd create separate solvers for each agent type
        
        # Create a basic forecasting task
        @task
        def standard_forecasting_task():
            return Task(
                dataset=[{"question": question, "background": background, "time_horizon": time_horizon}],
                solver=chain(
                    system_message("You are an expert forecasting analyst. Provide probability estimates based on available information."),
                    user_message(f"Question: {question}\nBackground: {background}\nTime Horizon: {time_horizon}\n\nProvide a probability estimate (0.0-1.0) and reasoning."),
                    use_tools([self.google_news_tool.google_news_search]),
                    generate()
                ),
                scorer=None
            )
        
        # Run the evaluation
        eval_result = eval(
            standard_forecasting_task(),
            model=self.model,
            log_dir="logs/inspect_ai"
        )
        
        # Extract results
        probability = self._extract_probability_from_result(eval_result)
        confidence = self._extract_confidence_from_result(eval_result)
        reasoning = self._extract_reasoning_from_result(eval_result)
        
        result = ForecastResult(
            question=question,
            prediction=probability,
            confidence=confidence,
            reasoning=reasoning
        )
        
        return result
    
    def _extract_search_count_from_result(self, eval_result) -> int:
        """Extract search count from Inspect AI evaluation result"""
        try:
            # Look for search count in metadata or logs
            if hasattr(eval_result, 'metadata') and eval_result.metadata:
                return eval_result.metadata.get('search_count', 0)
            return 0
        except Exception:
            return 0
    
    def _extract_api_calls_from_result(self, eval_result) -> int:
        """Extract API calls from Inspect AI evaluation result"""
        try:
            # Look for API calls in metadata or stats
            if hasattr(eval_result, 'stats') and eval_result.stats:
                return eval_result.stats.get('api_calls', 0)
            return 0
        except Exception:
            return 0
    
    def _extract_probability_from_result(self, eval_result) -> float:
        """Extract probability from Inspect AI evaluation result"""
        # This is a placeholder - in practice, you'd parse the actual model output
        # to extract the probability estimate
        try:
            # Look for probability patterns in the result
            result_str = str(eval_result)
            
            # Common probability patterns
            prob_patterns = [
                r'probability[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)%',
                r'(\d+(?:\.\d+)?)\s*percent',
                r'estimate[:\s]*(\d+(?:\.\d+)?)'
            ]
            
            for pattern in prob_patterns:
                match = re.search(pattern, result_str, re.IGNORECASE)
                if match:
                    prob = float(match.group(1))
                    # Convert percentage to decimal if needed
                    if prob > 1.0:
                        prob = prob / 100.0
                    return max(0.01, min(0.99, prob))  # Clamp to reasonable range
            
            # Default fallback
            return 0.5
            
        except Exception:
            return 0.5
    
    def _extract_confidence_from_result(self, eval_result) -> str:
        """Extract confidence level from Inspect AI evaluation result"""
        # Placeholder implementation
        result_str = str(eval_result).lower()
        
        if any(word in result_str for word in ['high', 'confident', 'certain']):
            return "High"
        elif any(word in result_str for word in ['low', 'uncertain', 'unsure']):
            return "Low"
        else:
            return "Medium"
    
    def _extract_reasoning_from_result(self, eval_result) -> str:
        """Extract reasoning from Inspect AI evaluation result"""
        # Placeholder implementation
        return f"Forecast generated using Inspect AI methodology. Result: {str(eval_result)[:500]}..."


# Compatibility function to maintain the same interface
def create_superforecaster(**kwargs):
    """
    Factory function to create Inspect AI superforecaster with fallback to mock
    
    Args:
        **kwargs: Arguments to pass to the superforecaster constructor
        
    Returns:
        InspectAISuperforecaster or MockSuperforecaster instance
    """
    # Remove logger from kwargs since Inspect AI handles logging natively
    kwargs.pop('logger', None)
    
    try:
        return InspectAISuperforecaster(**kwargs)
    except Exception as e:
        print(f"⚠️ Failed to initialize Inspect AI Superforecaster: {e}")
        print("🔄 Falling back to Mock Superforecaster for testing")
        try:
            from .mock_superforecaster import MockSuperforecaster
            return MockSuperforecaster(**kwargs)
        except Exception as mock_e:
            print(f"❌ Failed to initialize Mock Superforecaster: {mock_e}")
            raise mock_e