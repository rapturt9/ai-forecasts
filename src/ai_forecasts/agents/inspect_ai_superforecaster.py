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

from inspect_ai import Task, eval, task
from inspect_ai.model import get_model, Model
from inspect_ai.solver import (
    generate, system_message, user_message, assistant_message,
    chain, fork, basic_agent, use_tools, solver, Solver
)
from inspect_ai.tool import tool, Tool, ToolError
from inspect_ai.agent import Agent

from ..utils.agent_logger import agent_logger
from ..utils.llm_client import LLMClient
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


class InspectAISuperforecaster:
    """
    Enhanced superforecaster system using Inspect AI with strategic analysis and bias correction
    """
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None, training_cutoff: str = "2024-07-01", 
                 recommended_articles: int = 10, max_search_queries: int = None, logger = None, 
                 debate_mode: bool = True, debate_rounds: int = 2, enhanced_quality_mode: bool = True,
                 search_budget_per_advocate: int = 10):
        self.logger = logger if logger is not None else agent_logger
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        self.training_cutoff = training_cutoff
        self.debate_mode = debate_mode
        self.debate_rounds = debate_rounds
        self.enhanced_quality_mode = enhanced_quality_mode
        self.search_budget_per_advocate = search_budget_per_advocate
        
        # Search configuration parameters
        self.recommended_articles = recommended_articles
        self.max_search_queries = max_search_queries or (
            None if recommended_articles == -1 else
            max(2, min(5, recommended_articles // 3))
        )
        
        # Configure model for Inspect AI
        model_name = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-2024-11-20")
        
        # Set up environment for OpenRouter
        os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
        os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
        
        # Create Inspect AI model
        self.model = get_model(
            f"openrouter/{model_name}",
            api_key=openrouter_api_key,
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
        
        self.logger.info("✅ Inspect AI Superforecaster initialized successfully")
    
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
    def debate_judge_solver(self, question: str, background: str, time_horizon: str, 
                           high_argument: str, low_argument: str) -> Solver:
        """Debate judge solver"""
        # Create search parameters for the task description
        search_timeframe = {
            "start": "06/01/2024",
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        cutoff_date = datetime.now().strftime("%Y-%m-%d")
        
        judge_prompt = get_debate_judge_task_description(
            question, cutoff_date, time_horizon, background
        )
        return chain(
            system_message(get_debate_judge_backstory()),
            user_message(judge_prompt),
            generate()
        )
    
    @task
    def debate_forecasting_task(self, question: str, background: str = "", 
                               time_horizon: str = "1 year") -> Task:
        """Create a debate-based forecasting task"""
        
        # Create the debate solver using fork for parallel execution
        debate_solver = chain(
            # First, run advocates in parallel
            fork(
                self.high_advocate_solver(question, background, time_horizon),
                self.low_advocate_solver(question, background, time_horizon)
            ),
            # Then judge the results
            self.debate_judge_solver(question, background, time_horizon, "", "")
        )
        
        return Task(
            dataset=[{"question": question, "background": background, "time_horizon": time_horizon}],
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
            self.logger.info(f"🎯 Starting forecast for time horizon: {time_horizon}")
            
            try:
                if self.debate_mode:
                    result = self._run_debate_forecast(question, background, time_horizon)
                else:
                    result = self._run_standard_forecast(question, background, time_horizon)
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"❌ Error forecasting for {time_horizon}: {str(e)}")
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
        """Run debate-based forecasting using Inspect AI"""
        
        self.logger.info("🗣️ Running debate-based forecast")
        
        try:
            # For now, implement a simplified Inspect AI integration
            # This demonstrates the framework integration without the complex async handling
            
            # Create a simple forecasting prompt that simulates debate
            debate_prompt = f"""
            You are conducting a forecasting debate. Consider both high and low probability arguments for this question:
            
            Question: {question}
            Background: {background}
            Time Horizon: {time_horizon}
            
            Provide:
            1. High probability argument (why this might happen)
            2. Low probability argument (why this might not happen)  
            3. Your final probability estimate (0.0 to 1.0)
            4. Confidence level (Low/Medium/High)
            5. Brief reasoning
            
            Format your response as:
            PROBABILITY: [0.0-1.0]
            CONFIDENCE: [Low/Medium/High]
            REASONING: [your reasoning]
            """
            
            # Use the OpenAI client directly for now (simulating Inspect AI integration)
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key
            )
            
            response = client.chat.completions.create(
                model="openai/gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert forecaster using debate methodology."},
                    {"role": "user", "content": debate_prompt}
                ],
                temperature=0.7
            )
            
            output = response.choices[0].message.content
            
            # Extract probability and confidence
            probability = 0.65  # Default
            confidence = "Medium"
            reasoning = output
            
            try:
                import re
                prob_match = re.search(r'PROBABILITY:\s*([0-9.]+)', output)
                if prob_match:
                    probability = float(prob_match.group(1))
                
                conf_match = re.search(r'CONFIDENCE:\s*(\w+)', output)
                if conf_match:
                    confidence = conf_match.group(1)
                
                reason_match = re.search(r'REASONING:\s*(.+)', output, re.DOTALL)
                if reason_match:
                    reasoning = reason_match.group(1).strip()
            except:
                pass
            
            # Create the result object
            result = ForecastResult(
                question=question,
                prediction=probability,
                confidence=confidence,
                reasoning=reasoning
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in Inspect AI debate forecast: {str(e)}")
            # Return fallback result
            return ForecastResult(
                question=question,
                prediction=0.5,
                confidence=0.3,
                reasoning=f"Error in Inspect AI forecast: {str(e)}"
            )
    
    def _run_standard_forecast(self, question: str, background: str, time_horizon: str) -> ForecastResult:
        """Run standard 4-agent forecasting using Inspect AI"""
        
        self.logger.info("📊 Running standard 4-agent forecast")
        
        # For now, implement a simplified version
        # In a full implementation, you'd create separate solvers for each agent type
        
        # Create a basic forecasting task
        @task
        def standard_forecasting_task():
            return Task(
                dataset=[{"question": question, "background": background, "time_horizon": time_horizon}],
                solver=chain(
                    system_message(get_research_analyst_backstory()),
                    user_message(get_research_task_description(question, background, time_horizon)),
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
def create_superforecaster(**kwargs) -> 'InspectAISuperforecaster':
    """
    Factory function to create Inspect AI superforecaster
    
    Args:
        **kwargs: Arguments to pass to the superforecaster constructor
        
    Returns:
        InspectAISuperforecaster instance
    """
    return InspectAISuperforecaster(**kwargs)