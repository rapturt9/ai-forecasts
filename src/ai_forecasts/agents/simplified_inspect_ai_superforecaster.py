"""
Simplified Inspect AI Superforecaster System
Configurable debate-based forecasting system with parameters passed from run_forecastbench.py
"""
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from inspect_ai import Task, eval, task
from inspect_ai.dataset import Sample, Dataset
from inspect_ai.model import get_model
from inspect_ai.solver import (
    generate, system_message, user_message,
    chain, fork, use_tools, solver, Solver
)
from inspect_ai.tool import tool, ToolError
from inspect_ai.scorer import Scorer, Score
from inspect_ai.log import EvalLog

from .simplified_debate_prompts import (
    get_high_advocate_backstory,
    get_low_advocate_backstory,
    get_debate_judge_backstory
)

# Import cached SERP API Google News Tool
from ..utils.google_news_tool import CachedGoogleNewsTool


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
            results = self.cached_tool._run(query)
            return results
        except Exception as e:
            raise ToolError(f"Google News search failed: {str(e)}")


class SimplifiedInspectAISuperforecaster:
    """
    Simplified configurable superforecaster system using Inspect AI
    All parameters are passed from the benchmark runner
    """
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None):
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        
        # Configure model for Inspect AI
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
        
        print("✅ Simplified Inspect AI Superforecaster initialized successfully")
    
    def forecast_with_google_news(
        self, 
        question: str, 
        background: str = "", 
        time_horizons: List[str] = None,
        cutoff_date: datetime = None,
        search_budget_per_advocate: int = 10,
        debate_rounds: int = 3,
        training_cutoff: str = "2024-07-01",
        **kwargs
    ) -> List[ForecastResult]:
        """
        Generate forecasts using configurable debate methodology
        
        Args:
            question: The forecasting question
            background: Additional context
            time_horizons: List of time horizons to forecast for (e.g., ["7", "30", "90", "180"])
            cutoff_date: Information cutoff date
            search_budget_per_advocate: Number of searches per advocate
            debate_rounds: Number of debate rounds
            training_cutoff: Model training cutoff date
            
        Returns:
            List of ForecastResult objects, one per time horizon
        """
        if time_horizons is None:
            time_horizons = ["7", "30", "90", "180"]
        
        # Normalize time horizons - remove 'd' suffix if present
        normalized_horizons = []
        for horizon in time_horizons:
            if isinstance(horizon, str) and horizon.endswith('d'):
                normalized_horizons.append(horizon[:-1])
            else:
                normalized_horizons.append(str(horizon))
        
        # Initialize Google News tool
        search_timeframe = {
            "start": "06/01/2024",
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        google_news_tool = InspectAIGoogleNewsTool(
            serp_api_key=self.serp_api_key,
            search_timeframe=search_timeframe
        )
        
        # Set cutoff date if provided
        if cutoff_date and hasattr(google_news_tool.cached_tool, 'set_benchmark_cutoff_date'):
            google_news_tool.cached_tool.set_benchmark_cutoff_date(cutoff_date.strftime("%Y-%m-%d"))
        
        print(f"🎯 Starting configurable debate forecast")
        print(f"   Time horizons: {normalized_horizons} days")
        print(f"   Debate rounds: {debate_rounds}")
        print(f"   Search budget per advocate: {search_budget_per_advocate}")
        print(f"   Training cutoff: {training_cutoff}")
        
        try:
            # Create and run the debate task
            debate_task = self._create_debate_task(
                question=question,
                background=background,
                time_horizons=normalized_horizons,
                search_budget_per_advocate=search_budget_per_advocate,
                debate_rounds=debate_rounds,
                training_cutoff=training_cutoff,
                google_news_tool=google_news_tool
            )
            
            # Run the evaluation
            eval_result = eval(
                debate_task,
                model=self.model,
                log_dir="logs/inspect_ai"
            )
            
            # Extract results for each time horizon
            results = []
            judge_output = self._extract_judge_output_from_result(eval_result)
            
            for horizon in normalized_horizons:
                horizon_key = f"{horizon}_day"
                
                if judge_output and "final_predictions" in judge_output:
                    # Try different key formats
                    prediction_data = None
                    for key in [horizon_key, horizon, f"{horizon}d"]:
                        if key in judge_output["final_predictions"]:
                            prediction_data = judge_output["final_predictions"][key]
                            break
                    
                    if prediction_data:
                        if isinstance(prediction_data, dict):
                            probability = prediction_data.get("probability", 0.5)
                            confidence = prediction_data.get("confidence", "MEDIUM")
                            reasoning = prediction_data.get("reasoning", "No specific reasoning provided")
                        else:
                            probability = float(prediction_data) if prediction_data else 0.5
                            confidence = "MEDIUM"
                            reasoning = f"Numeric prediction for {horizon} days"
                    else:
                        probability = 0.5
                        confidence = "LOW"
                        reasoning = f"No prediction found for {horizon} days"
                else:
                    # Fallback parsing
                    probability = self._extract_probability_from_result(eval_result)
                    confidence = "MEDIUM"
                    reasoning = f"Fallback extraction for {horizon} days"
                
                result = ForecastResult(
                    question=question,
                    prediction=probability,
                    confidence=confidence,
                    reasoning=reasoning,
                    timestamp=datetime.now().isoformat()
                )
                
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error in debate forecasting: {str(e)}")
            # Return fallback results for all time horizons
            fallback_results = []
            for horizon in normalized_horizons:
                fallback_result = ForecastResult(
                    question=question,
                    prediction=0.5,
                    confidence="LOW",
                    reasoning=f"Error occurred during forecasting: {str(e)}"
                )
                fallback_results.append(fallback_result)
            return fallback_results
    
    def _create_debate_task(
        self,
        question: str,
        background: str,
        time_horizons: List[str],
        search_budget_per_advocate: int,
        debate_rounds: int,
        training_cutoff: str,
        google_news_tool: InspectAIGoogleNewsTool
    ) -> Task:
        """Create a configurable debate task"""
        
        @task
        def configurable_debate_forecasting():
            return Task(
                dataset=[{
                    "question": question,
                    "background": background,
                    "time_horizons": time_horizons
                }],
                solver=self._create_debate_solver(
                    time_horizons=time_horizons,
                    search_budget_per_advocate=search_budget_per_advocate,
                    debate_rounds=debate_rounds,
                    training_cutoff=training_cutoff,
                    google_news_tool=google_news_tool
                ),
                scorer=None
            )
        
        return configurable_debate_forecasting
    
    def _create_debate_solver(
        self,
        time_horizons: List[str],
        search_budget_per_advocate: int,
        debate_rounds: int,
        training_cutoff: str,
        google_news_tool: InspectAIGoogleNewsTool
    ) -> Solver:
        """Create the main debate solver with configurable parameters"""
        
        @solver
        def debate_solver():
            time_horizons_str = ", ".join([f"{h} days" for h in time_horizons])
            
            # Create debate chain with configurable rounds
            debate_chain = []
            
            # Round 1: Initial positions (parallel)
            debate_chain.append(
                fork(
                    # High advocate initial position
                    chain(
                        system_message(get_high_advocate_backstory()),
                        user_message(self._get_initial_advocate_prompt(
                            advocate_type="high",
                            round_num=1,
                            time_horizons_str=time_horizons_str,
                            search_budget_per_advocate=search_budget_per_advocate,
                            debate_rounds=debate_rounds,
                            training_cutoff=training_cutoff
                        )),
                        use_tools([google_news_tool.google_news_search]),
                        generate()
                    ),
                    # Low advocate initial position
                    chain(
                        system_message(get_low_advocate_backstory()),
                        user_message(self._get_initial_advocate_prompt(
                            advocate_type="low",
                            round_num=1,
                            time_horizons_str=time_horizons_str,
                            search_budget_per_advocate=search_budget_per_advocate,
                            debate_rounds=debate_rounds,
                            training_cutoff=training_cutoff
                        )),
                        use_tools([google_news_tool.google_news_search]),
                        generate()
                    )
                )
            )
            
            # Subsequent rounds: alternating rebuttals
            for round_num in range(2, debate_rounds + 1):
                # High advocate rebuttal
                debate_chain.append(
                    chain(
                        system_message(get_high_advocate_backstory()),
                        user_message(self._get_rebuttal_prompt(
                            advocate_type="high",
                            round_num=round_num,
                            time_horizons_str=time_horizons_str,
                            search_budget_per_advocate=search_budget_per_advocate,
                            debate_rounds=debate_rounds,
                            training_cutoff=training_cutoff
                        )),
                        use_tools([google_news_tool.google_news_search]),
                        generate()
                    )
                )
                
                # Low advocate rebuttal
                debate_chain.append(
                    chain(
                        system_message(get_low_advocate_backstory()),
                        user_message(self._get_rebuttal_prompt(
                            advocate_type="low",
                            round_num=round_num,
                            time_horizons_str=time_horizons_str,
                            search_budget_per_advocate=search_budget_per_advocate,
                            debate_rounds=debate_rounds,
                            training_cutoff=training_cutoff
                        )),
                        use_tools([google_news_tool.google_news_search]),
                        generate()
                    )
                )
            
            # Final judge decision
            debate_chain.append(
                chain(
                    system_message(get_debate_judge_backstory()),
                    user_message(self._get_judge_prompt(
                        time_horizons_str=time_horizons_str,
                        search_budget_per_advocate=search_budget_per_advocate,
                        debate_rounds=debate_rounds,
                        training_cutoff=training_cutoff,
                        time_horizons=time_horizons
                    )),
                    generate()
                )
            )
            
            return chain(*debate_chain)
        
        return debate_solver
    
    def _get_initial_advocate_prompt(
        self,
        advocate_type: str,
        round_num: int,
        time_horizons_str: str,
        search_budget_per_advocate: int,
        debate_rounds: int,
        training_cutoff: str
    ) -> str:
        """Generate initial advocate prompt"""
        mission = "HIGH probability outcomes" if advocate_type == "high" else "LOW probability outcomes"
        
        return f"""
MISSION: Build the strongest possible case for {mission} across multiple time horizons.

**Time Horizons:** {time_horizons_str}
**Training Cutoff:** {training_cutoff}
**Round:** {round_num} of {debate_rounds}

**SEARCH BUDGET STATUS:**
- Total Search Budget: {search_budget_per_advocate} queries
- Searches Used This Round: 0
- Searches Remaining: {search_budget_per_advocate}

**INSTRUCTIONS:**
1. Analyze the question for ALL time horizons
2. Consider how probability changes over time
3. Use your search budget strategically
4. Provide structured analysis with probability estimates

**REQUIRED JSON OUTPUT:**
```json
{{
  "round": {round_num},
  "advocate_type": "{advocate_type}",
  "position_statement": "Your overall position",
  "time_horizon_predictions": {{
    "7_day": {{"probability": 0.X, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Brief reasoning"}},
    "30_day": {{"probability": 0.Y, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Brief reasoning"}},
    "90_day": {{"probability": 0.Z, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Brief reasoning"}},
    "180_day": {{"probability": 0.W, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Brief reasoning"}}
  }},
  "key_arguments": ["arg1", "arg2", "arg3"],
  "evidence_summary": "Summary of key evidence",
  "searches_used_this_round": 0
}}
```
"""
    
    def _get_rebuttal_prompt(
        self,
        advocate_type: str,
        round_num: int,
        time_horizons_str: str,
        search_budget_per_advocate: int,
        debate_rounds: int,
        training_cutoff: str
    ) -> str:
        """Generate rebuttal prompt"""
        mission = "HIGH probability outcomes" if advocate_type == "high" else "LOW probability outcomes"
        opponent_type = "Low" if advocate_type == "high" else "High"
        
        estimated_searches_used = (round_num - 1) * 2
        searches_remaining = max(0, search_budget_per_advocate - estimated_searches_used)
        
        return f"""
REBUTTAL - Round {round_num} of {debate_rounds}

Review the {opponent_type} Advocate's arguments and provide your rebuttal to strengthen your case for {mission}.

**Time Horizons:** {time_horizons_str}
**Training Cutoff:** {training_cutoff}

**SEARCH BUDGET STATUS:**
- Total Search Budget: {search_budget_per_advocate} queries
- Estimated Searches Used: ~{estimated_searches_used}
- Searches Remaining: ~{searches_remaining}

**REBUTTAL INSTRUCTIONS:**
1. Address the opponent's strongest arguments directly
2. Provide new evidence or reasoning that counters their position
3. Strengthen your case across all time horizons
4. Use remaining searches strategically

**REQUIRED JSON OUTPUT:**
```json
{{
  "round": {round_num},
  "advocate_type": "{advocate_type}",
  "rebuttal_to_opponent": "Direct response to opponent's arguments",
  "strengthened_position": "Your reinforced position",
  "time_horizon_predictions": {{
    "7_day": {{"probability": 0.X, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Updated reasoning"}},
    "30_day": {{"probability": 0.Y, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Updated reasoning"}},
    "90_day": {{"probability": 0.Z, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Updated reasoning"}},
    "180_day": {{"probability": 0.W, "confidence": "HIGH/MEDIUM/LOW", "reasoning": "Updated reasoning"}}
  }},
  "new_evidence": "New evidence presented in this round",
  "searches_used_this_round": 1
}}
```
"""
    
    def _get_judge_prompt(
        self,
        time_horizons_str: str,
        search_budget_per_advocate: int,
        debate_rounds: int,
        training_cutoff: str,
        time_horizons: List[str]
    ) -> str:
        """Generate judge prompt"""
        # Create dynamic predictions structure based on actual time horizons
        predictions_structure = {}
        for horizon in time_horizons:
            predictions_structure[f"{horizon}_day"] = "0.XX"
        
        predictions_json = json.dumps(predictions_structure, indent=4)
        
        return f"""
FINAL JUDGMENT

You have observed {debate_rounds} rounds of debate between high and low probability advocates.
Each advocate had a search budget of {search_budget_per_advocate} queries.

**Time Horizons:** {time_horizons_str}
**Training Cutoff:** {training_cutoff}

**JUDICIAL SYNTHESIS PROTOCOL:**
1. Review all arguments from both advocates across all {debate_rounds} rounds
2. Evaluate evidence quality, logical consistency, and bias detection
3. Apply proper calibration techniques for each time horizon
4. Provide final probability estimates with reasoning
5. Consider how probabilities change across time horizons

**REQUIRED JSON OUTPUT:**
```json
{{
  "final_predictions": {predictions_json.replace('"0.XX"', '0.XX')},
  "confidence_scores": {predictions_json.replace('"0.XX"', '0.XX')},
  "reasoning": {{
    {', '.join([f'"{horizon}_day": "Reasoning for {horizon}-day prediction"' for horizon in time_horizons])}
  }},
  "debate_summary": "Summary of key debate points that influenced your decision",
  "search_efficiency_evaluation": "Assessment of how well advocates used their search budget",
  "training_cutoff_impact": "How the training cutoff affected prediction quality"
}}
```
"""
    
    def _extract_judge_output_from_result(self, eval_result: EvalLog) -> Optional[Dict]:
        """Extract structured judge output from Inspect AI evaluation result"""
        try:
            # The eval_result is an EvalLog object
            if hasattr(eval_result, 'samples') and eval_result.samples:
                # Get the last sample (should contain the judge's final output)
                last_sample = eval_result.samples[-1]
                
                if hasattr(last_sample, 'output') and last_sample.output:
                    result_str = str(last_sample.output.completion)
                else:
                    # Fallback: look through all samples for judge output
                    result_str = ""
                    for sample in eval_result.samples:
                        if hasattr(sample, 'output') and sample.output:
                            result_str += str(sample.output.completion) + "\n"
            else:
                result_str = str(eval_result)
            
            # Try to find JSON structure in the result
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
    
    def _extract_probability_from_result(self, eval_result) -> float:
        """Extract probability from Inspect AI evaluation result"""
        try:
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
            
            return 0.5  # Default fallback
            
        except Exception:
            return 0.5


# Compatibility function to maintain the same interface
def create_superforecaster(**kwargs):
    """
    Factory function to create simplified superforecaster
    
    Args:
        **kwargs: Arguments to pass to the superforecaster constructor
        
    Returns:
        SimplifiedInspectAISuperforecaster instance
    """
    # Remove logger from kwargs since Inspect AI handles logging natively
    kwargs.pop('logger', None)
    
    try:
        return SimplifiedInspectAISuperforecaster(**kwargs)
    except Exception as e:
        print(f"❌ Failed to initialize Simplified Superforecaster: {e}")
        raise e
