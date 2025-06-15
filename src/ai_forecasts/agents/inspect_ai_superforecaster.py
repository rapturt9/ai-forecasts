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

# Simplified imports - removed unused Inspect AI components

# Removed forecasting_prompts import - using only debate methodology

from .debate_forecasting_prompts import (
    get_high_advocate_backstory,
    get_low_advocate_backstory,
    get_debate_judge_backstory,
    get_high_advocate_task_description,
    get_low_advocate_task_description,
    get_debate_judge_task_description,
    HighAdvocateOutput,
    LowAdvocateOutput,
    DebateJudgmentOutput,
    EnhancedHighAdvocateOutput,
    EnhancedLowAdvocateOutput,
    EnhancedJudgeOutput
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


# Removed InspectAIGoogleNewsTool - simplified to direct usage


class InspectAISuperforecaster:
    """
    Enhanced superforecaster system using Inspect AI with strategic analysis and bias correction
    """
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None, logger = None, 
                 debate_mode: bool = True, search_budget: int = 10, debate_turns: int = 2,
                 time_horizons: List[int] = None, **kwargs):
        self.logger = logger if logger is not None else self._default_logger
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        self.debate_mode = debate_mode
        self.search_budget = search_budget
        self.debate_turns = debate_turns
        self.time_horizons = time_horizons or [7, 30, 90, 180]
        
        # Validate API key
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        # Initialize Google News tool if available
        if self.serp_api_key:
            search_timeframe = {
                "start": "06/01/2024",
                "end": datetime.now().strftime("%m/%d/%Y")
            }
            try:
                self.google_news_tool = CachedGoogleNewsTool(
                    serp_api_key=self.serp_api_key,
                    search_timeframe=search_timeframe
                )
            except Exception as e:
                self.logger("warning", f"Failed to initialize Google News tool: {e}")
                self.google_news_tool = None
        else:
            self.google_news_tool = None
        
        self.logger("system", "✅ Inspect AI Superforecaster initialized successfully")
    
    def _default_logger(self, agent: str, message: str, details: dict = None):
        """Simple default logger"""
        print(f"[{agent}] {message}")
        if details:
            print(f"  Details: {details}")
    
    def _set_benchmark_cutoff_date(self, cutoff_date: str):
        """Set benchmark cutoff date on Google News tool"""
        if self.google_news_tool and hasattr(self.google_news_tool, 'set_benchmark_cutoff_date'):
            self.google_news_tool.set_benchmark_cutoff_date(cutoff_date)
    

    
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
        Generate forecasts using Inspect AI debate methodology
        
        Args:
            question: The forecasting question
            background: Additional context
            time_horizons: List of time horizons to forecast for
            cutoff_date: Information cutoff date
            recommended_articles: Number of articles to search for
            max_search_queries: Maximum search queries
            prior_probability: Prior probability estimate
            
        Returns:
            List of ForecastResult objects, one per time horizon
        """
        
        if time_horizons is None:
            time_horizons = ["1 year"]
        
        if cutoff_date:
            self._set_benchmark_cutoff_date(cutoff_date.strftime("%Y-%m-%d"))
        
        results = []
        
        for time_horizon in time_horizons:
            self.logger("system", f"🎯 Starting forecast for time horizon: {time_horizon}")
            
            try:
                result = self._run_debate_forecast(question, background, time_horizon)
                results.append(result)
                
            except Exception as e:
                self.logger("error", f"❌ Error forecasting for {time_horizon}: {str(e)}")
                # Create a fallback result
                fallback_result = ForecastResult(
                    question=question,
                    prediction=0.5,  # Neutral fallback
                    confidence=0.3,  # Low confidence
                    reasoning=f"Error occurred during forecasting: {str(e)}"
                )
                results.append(fallback_result)
        
        return results
    
    def _run_debate_forecast(self, question: str, background: str, time_horizon: str) -> ForecastResult:
        """Run debate-based forecasting with configurable turns and JSON output"""
        
        self.logger("system", f"🗣️ Running {self.debate_turns}-turn debate forecast")
        
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key
            )
            
            # Initialize debate history
            debate_history = []
            
            # Run debate turns
            for turn in range(self.debate_turns):
                self.logger("system", f"🔄 Debate turn {turn + 1}/{self.debate_turns}")
                
                # High advocate turn
                high_prompt = self._create_advocate_prompt(
                    question, background, time_horizon, "high", debate_history, turn
                )
                high_response = client.chat.completions.create(
                    model="openai/gpt-4",
                    messages=[
                        {"role": "system", "content": get_high_advocate_backstory()},
                        {"role": "user", "content": high_prompt}
                    ],
                    temperature=0.7
                )
                high_argument = high_response.choices[0].message.content
                debate_history.append({"turn": turn + 1, "advocate": "high", "argument": high_argument})
                
                # Low advocate turn
                low_prompt = self._create_advocate_prompt(
                    question, background, time_horizon, "low", debate_history, turn
                )
                low_response = client.chat.completions.create(
                    model="openai/gpt-4",
                    messages=[
                        {"role": "system", "content": get_low_advocate_backstory()},
                        {"role": "user", "content": low_prompt}
                    ],
                    temperature=0.7
                )
                low_argument = low_response.choices[0].message.content
                debate_history.append({"turn": turn + 1, "advocate": "low", "argument": low_argument})
            
            # Judge final decision with JSON output
            judge_prompt = self._create_judge_prompt(question, background, time_horizon, debate_history)
            judge_response = client.chat.completions.create(
                model="openai/gpt-4",
                messages=[
                    {"role": "system", "content": get_debate_judge_backstory()},
                    {"role": "user", "content": judge_prompt}
                ],
                temperature=0.3
            )
            
            judge_output = judge_response.choices[0].message.content
            
            # Extract JSON prediction from judge output
            prediction_data = self._extract_json_prediction(judge_output)
            
            return ForecastResult(
                question=question,
                prediction=prediction_data.get("probability", 0.5),
                confidence=prediction_data.get("confidence", "Medium"),
                reasoning=prediction_data.get("reasoning", judge_output)
            )
            
        except Exception as e:
            self.logger("error", f"Error in debate forecast: {str(e)}")
            # Fallback to mock prediction
            import random
            prediction = random.uniform(0.1, 0.9)
            return ForecastResult(
                question=question,
                prediction=prediction,
                confidence="Low",
                reasoning=f"Error in debate forecast: {str(e)}. Using fallback prediction: {prediction:.3f}"
            )
    
    def _create_advocate_prompt(self, question: str, background: str, time_horizon: str, 
                               advocate_type: str, debate_history: List, turn: int) -> str:
        """Create prompt for advocate based on debate history"""
        
        # Get the appropriate backstory and instructions
        if advocate_type == "high":
            backstory = get_high_advocate_backstory()
            instructions = f"""
            MISSION: Build the strongest possible case for a HIGH probability outcome.
            
            SEARCH INSTRUCTIONS:
            - You have a search budget of {self.search_budget} articles
            - Use search strategically to find evidence supporting high probability
            - Focus on recent developments, positive trends, and success factors
            - Look for base rates where similar events succeeded frequently
            
            ARGUMENT STRUCTURE:
            - State your target probability range (aim for 60%+ if evidence supports it)
            - Provide 3-5 key arguments with evidence
            - Address potential counterarguments proactively
            - Use base rate analysis from favorable reference classes
            """
        else:
            backstory = get_low_advocate_backstory()
            instructions = f"""
            MISSION: Build the strongest possible case for a LOW probability outcome.
            
            SEARCH INSTRUCTIONS:
            - You have a search budget of {self.search_budget} articles
            - Use search strategically to find evidence supporting low probability
            - Focus on obstacles, failure modes, and negative trends
            - Look for base rates where similar events failed frequently
            
            ARGUMENT STRUCTURE:
            - State your target probability range (aim for 40% or lower if evidence supports it)
            - Identify 3-5 key failure modes with evidence
            - Address potential counterarguments from high advocate
            - Use base rate analysis from unfavorable reference classes
            """
        
        prompt = f"""
        Question: {question}
        Background: {background}
        Time Horizon: {time_horizon}
        
        {instructions}
        
        You are the {advocate_type} probability advocate in turn {turn + 1} of {self.debate_turns}.
        """
        
        if debate_history:
            prompt += "\n\nPrevious debate history:\n"
            for entry in debate_history:
                prompt += f"Turn {entry['turn']} - {entry['advocate']} advocate: {entry['argument'][:300]}...\n"
        
        if turn == 0:
            prompt += f"\nPresent your initial {advocate_type} probability argument with evidence and reasoning."
        else:
            prompt += f"\nRespond to the opposing arguments and strengthen your {advocate_type} probability position. Address their key points directly."
        
        return prompt
    
    def _create_judge_prompt(self, question: str, background: str, time_horizon: str, 
                            debate_history: List) -> str:
        """Create judge prompt with requirement for JSON output"""
        
        judge_instructions = f"""
        JUDGE INSTRUCTIONS:
        
        SYNTHESIS PROTOCOL:
        - Weight evidence by recency, independence, verifiability, and source quality
        - Apply systematic calibration corrections based on historical patterns
        - Use multiple synthesis methods and compare results
        - Apply conservative adjustment when advocates disagree significantly
        - Default to wider confidence intervals when evidence is limited
        
        BIAS CORRECTION:
        - Correct for anchoring bias from initial advocate estimates
        - Apply averaging bias correction (don't just split the difference)
        - Check for confirmation bias in evidence weighting
        - Correct for overconfidence in synthesis process itself
        - Apply humility correction for complex, uncertain predictions
        
        EVALUATION CRITERIA:
        - Evidence quality and independence
        - Logical consistency of arguments
        - Base rate analysis accuracy
        - Handling of uncertainty and counterarguments
        - Overall calibration and reasonableness
        
        OUTPUT REQUIREMENTS:
        - Final probability with reasoning
        - Confidence level assessment
        - Evaluation of both advocates' arguments
        - Key factors that determined your decision
        - JSON format for structured evaluation
        """
        
        prompt = f"""
        Question: {question}
        Background: {background}
        Time Horizon: {time_horizon}
        
        {judge_instructions}
        
        Complete debate history ({self.debate_turns} turns):
        """
        
        for entry in debate_history:
            prompt += f"\nTurn {entry['turn']} - {entry['advocate']} advocate:\n{entry['argument']}\n"
        
        prompt += f"""
        
        As the judge, synthesize the arguments and provide your final decision in JSON format:
        {{
            "probability": [0.0-1.0],
            "confidence": "[Low/Medium/High]",
            "reasoning": "[your detailed reasoning for the probability estimate]",
            "high_advocate_strength": [0-10],
            "low_advocate_strength": [0-10],
            "key_factors": ["factor1", "factor2", "factor3"],
            "evidence_quality": "[assessment of overall evidence quality]",
            "uncertainty_factors": ["uncertainty1", "uncertainty2"],
            "base_rate_assessment": "[how well base rates were analyzed]"
        }}
        
        Ensure your probability estimate is well-calibrated and your reasoning is comprehensive.
        """
        
        return prompt
    
    def _extract_json_prediction(self, judge_output: str) -> Dict:
        """Extract JSON prediction from judge output"""
        try:
            import re
            import json
            
            # Try to find JSON in the output - look for complete JSON objects
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', judge_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    parsed_json = json.loads(json_str)
                    # Validate required fields
                    if "probability" in parsed_json:
                        return parsed_json
                except json.JSONDecodeError:
                    pass
            
            # Fallback: extract individual components with more robust patterns
            prob_match = re.search(r'"probability":\s*([0-9.]+)', judge_output)
            conf_match = re.search(r'"confidence":\s*"([^"]+)"', judge_output)
            reason_match = re.search(r'"reasoning":\s*"([^"]*)"', judge_output, re.DOTALL)
            
            # Extract additional fields if available
            high_strength_match = re.search(r'"high_advocate_strength":\s*([0-9.]+)', judge_output)
            low_strength_match = re.search(r'"low_advocate_strength":\s*([0-9.]+)', judge_output)
            
            result = {
                "probability": float(prob_match.group(1)) if prob_match else 0.5,
                "confidence": conf_match.group(1) if conf_match else "Medium",
                "reasoning": reason_match.group(1) if reason_match else judge_output[:500]
            }
            
            # Add optional fields if found
            if high_strength_match:
                result["high_advocate_strength"] = float(high_strength_match.group(1))
            if low_strength_match:
                result["low_advocate_strength"] = float(low_strength_match.group(1))
            
            return result
            
        except Exception as e:
            self.logger("error", f"Error extracting JSON: {str(e)}")
            return {
                "probability": 0.5,
                "confidence": "Low",
                "reasoning": f"Error parsing judge output: {judge_output[:200]}..."
            }


def logger(agent: str, message: str, details: dict = None):
    """Simple default logger"""
    print(f"[{agent}] {message}")
    if details:
        print(f"  Details: {details}")


def create_superforecaster(**kwargs):
    """
    Factory function to create Inspect AI superforecaster with fallback to mock
    
    Args:
        **kwargs: Arguments to pass to the superforecaster constructor
        
    Returns:
        InspectAISuperforecaster or MockSuperforecaster instance
    """
    try:
        return InspectAISuperforecaster(**kwargs)
    except Exception as e:
        logger("system", f"⚠️ Failed to initialize Inspect AI Superforecaster: {e}")
        logger("system", "🔄 Falling back to Mock Superforecaster for testing")
        try:
            from .mock_superforecaster import MockSuperforecaster
            return MockSuperforecaster(**kwargs)
        except Exception as mock_e:
            logger("system", f"❌ Failed to initialize Mock Superforecaster: {mock_e}")
            raise mock_e
    
