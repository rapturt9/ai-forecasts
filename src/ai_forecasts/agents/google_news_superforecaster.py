"""
Enhanced AI Superforecaster System
Implements advanced superforecaster methodology with strategic Google News integration
and comprehensive bias correction techniques
"""
import json
import os
import re
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
from ..utils.agent_logger import agent_logger
from ..utils.llm_client import LLMClient
from .forecasting_prompts import (
    get_research_analyst_backstory,
    get_evidence_evaluator_backstory,
    get_forecasting_critic_backstory,
    get_calibrated_synthesizer_backstory,
    get_research_task_description,
    get_evaluation_task_description,
    get_critic_task_description,
    get_synthesis_task_description
)

# Import for LiteLLM fallback parsing
try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    litellm = None
    LITELLM_AVAILABLE = False
    litellm = None


# Pydantic models for structured task outputs
class OutcomeStatus(BaseModel):
    definitely_occurred: bool
    evidence_strength: str
    confirmation_sources: List[str]
    official_statements: List[str]

class SearchExecutionSummary(BaseModel):
    total_searches_conducted: int
    total_articles_found: int
    search_quality: str
    most_effective_queries: List[str]
    information_gaps: List[str]

class EvidenceAnalysis(BaseModel):
    evidence_description: str
    evidence_strength: str
    source_credibility: str
    evidence_direction: str

class BaseRateContext(BaseModel):
    historical_frequency: str
    reference_class: str
    current_vs_historical: str

class TrendIndicators(BaseModel):
    momentum_direction: str
    trend_strength: str
    key_trend_drivers: List[str]

class ResearchOutput(BaseModel):
    outcome_status: OutcomeStatus
    search_execution_summary: SearchExecutionSummary
    evidence_analysis: List[EvidenceAnalysis]
    base_rate_context: BaseRateContext
    trend_indicators: TrendIndicators

class EvidenceQualityAnalysis(BaseModel):
    high_quality_evidence: List[str]
    medium_quality_evidence: List[str]
    low_quality_evidence: List[str]
    excluded_evidence: List[str]
    overall_evidence_quality: float

class BiasDetectionResults(BaseModel):
    anchoring_bias_detected: str
    availability_bias_detected: str
    confirmation_bias_detected: str
    overconfidence_bias_detected: str
    base_rate_neglect_detected: str
    bias_corrections_applied: str

class EvidenceWeighting(BaseModel):
    weighted_evidence_summary: str
    evidence_convergence: str
    key_uncertainties: List[str]
    contradictory_evidence: str

class ProbabilisticCoherence(BaseModel):
    logical_consistency_check: str
    reasoning_chain_validity: str

class EvaluationOutput(BaseModel):
    evidence_quality_analysis: EvidenceQualityAnalysis
    bias_detection_results: BiasDetectionResults
    evidence_weighting: EvidenceWeighting
    probabilistic_coherence: ProbabilisticCoherence

class EvidenceAdjustment(BaseModel):
    evidence_supporting_higher: List[str]
    evidence_supporting_lower: List[str]
    net_adjustment_direction: str
    adjustment_magnitude: str
    adjustment_reasoning: str

class UncertaintyFactors(BaseModel):
    time_horizon_uncertainty: str
    evidence_limitations: List[str]
    key_risks: List[str]
    alternative_scenarios: List[str]

class CalibrationSummary(BaseModel):
    overconfidence_avoided: str
    uncertainty_acknowledged: str
    reasoning_summary: str
    methodology_applied: str

class SynthesisOutput(BaseModel):
    final_probability: float
    confidence_level: str
    base_rate_anchor: float
    evidence_adjustment: EvidenceAdjustment
    uncertainty_factors: UncertaintyFactors
    calibration_summary: CalibrationSummary

class ReferenceClassVerification(BaseModel):
    appropriate_reference_class: str
    alternative_reference_classes: List[str]
    current_vs_historical_conditions: str
    most_relevant_base_rate: float

class EvidenceQualityChallenge(BaseModel):
    strongest_evidence: List[str]
    weakest_evidence: List[str]
    contradictory_evidence: List[str]
    missing_evidence: List[str]

class TimingMechanismAnalysis(BaseModel):
    specific_mechanism_required: str
    necessary_preconditions: List[str]
    timeline_realism: str
    potential_barriers: List[str]

class AlternativeScenarios(BaseModel):
    ways_prediction_could_be_wrong: List[str]
    alternative_outcomes: List[str]
    low_probability_high_impact_events: List[str]
    scenario_probability_effects: str

class OutsideViewChallenge(BaseModel):
    skeptical_outsider_perspective: str
    expert_field_opinion: str
    overconfidence_relative_to_difficulty: str
    consequences_if_wrong: str

class ProbabilityRangeTesting(BaseModel):
    could_be_twenty_percent_higher: bool
    could_be_twenty_percent_lower: bool
    evidence_to_change_mind: List[str]
    anchored_to_round_numbers: bool
    confidence_justified_by_evidence: str

class CriticOutput(BaseModel):
    reference_class_verification: ReferenceClassVerification
    evidence_quality_challenge: EvidenceQualityChallenge
    timing_mechanism_analysis: TimingMechanismAnalysis
    alternative_scenarios: AlternativeScenarios
    outside_view_challenge: OutsideViewChallenge
    probability_range_testing: ProbabilityRangeTesting
    recommended_adjustments: List[str]


@dataclass
class ForecastResult:
    """Structured forecast result with comprehensive analysis"""
    question: str
    probability: float
    confidence_level: str
    reasoning: str
    base_rate: float
    evidence_quality: float
    methodology_components: Dict[str, bool]
    full_analysis: Dict[str, Any]
    news_research_summary: Dict[str, Any]
    news_sources: List[str]
    search_queries_used: List[str]
    total_articles_found: int
    search_timeframe: Dict[str, str]
    time_horizon: str  # Add time horizon information
    time_horizon_adjustment: Optional[str] = None  # Track any time-based adjustments made


# Import cached SERP API Google News Tool with intelligent caching
from ..utils.google_news_tool import CachedGoogleNewsTool

class GoogleNewsSuperforecaster:
    """
    Enhanced superforecaster system with strategic analysis and bias correction
    """
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None, training_cutoff: str = "2024-07-01", 
                 recommended_articles: int = 10, max_search_queries: int = None, logger = None):
        self.logger = logger if logger is not None else agent_logger
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        self.training_cutoff = training_cutoff
        
        # Search configuration parameters - optimized for efficiency
        self.recommended_articles = recommended_articles  # Target number of articles per search task
        self.max_search_queries = max_search_queries or (
            None if recommended_articles == -1 else  # -1 means unlimited
            max(2, min(5, recommended_articles // 3))  # More conservative search strategy
        )
        
        # Configure LLM with correct OpenRouter configuration for CrewAI
        from litellm import LiteLLM
        
        # Set up environment for litellm/openrouter
        os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
        
        # Use the model directly with openrouter prefix
        model_name = "openrouter/" + os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")
        
        self.llm = LLM(
            model=model_name,
            api_key=openrouter_api_key,
            temperature=0.7
        )
        
        # Initialize fallback parser
        self._setup_fallback_parser()
        
        # Initialize agents
        self._setup_agents()
    
    def _set_benchmark_cutoff_date(self, cutoff_date: str):
        """Set benchmark cutoff date on all Google News tools"""
        # Find and update Google News tools used by agents
        for agent in [self.research_analyst, self.evidence_evaluator, self.forecasting_critic, self.calibrated_synthesizer]:
            for tool in agent.tools:
                if hasattr(tool, 'set_benchmark_cutoff_date'):
                    tool.set_benchmark_cutoff_date(cutoff_date)
    
    def _setup_fallback_parser(self):
        """Setup LiteLLM fallback parser"""
        if LITELLM_AVAILABLE and self.openrouter_api_key:
            try:
                self.fallback_parser = litellm
                self.fallback_model = "openrouter/openai/gpt-4o-mini"
                self.fallback_available = True
                self.logger.info("✅ LiteLLM fallback parser initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ LiteLLM fallback setup failed: {e}")
                self.fallback_available = False
        else:
            self.fallback_available = False
    
    def _setup_agents(self):
        """Setup 4 enhanced forecasting agents with forecasting critics"""
        
        # Create Google News tool with improved date handling
        search_timeframe = {
            "start": "06/01/2024",  # From June 2024 to freeze date
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        google_news_tool = CachedGoogleNewsTool(
            serp_api_key=self.serp_api_key,
            search_timeframe=search_timeframe
        )
        
        # 1. Research Analyst - Enhanced with specific outcome detection
        self.research_analyst = Agent(
            role='Research Analyst & Outcome Detective',
            goal='Conduct comprehensive research with special focus on detecting if the outcome has already occurred or is definitively determined',
            backstory=get_research_analyst_backstory(),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[google_news_tool]
        )
        
        # 2. Evidence Evaluator - Enhanced with bias detection
        self.evidence_evaluator = Agent(
            role='Critical Evidence Evaluator & Bias Detector',
            goal='Apply rigorous evaluation to research findings while systematically detecting and correcting cognitive biases',
            backstory=get_evidence_evaluator_backstory(),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[google_news_tool]
        )
        
        # 3. Forecasting Critic - New agent for systematic critique
        self.forecasting_critic = Agent(
            role='Forecasting Critic & Devil\'s Advocate',
            goal='Systematically challenge forecasting reasoning and identify potential errors before final probability assignment',
            backstory=get_forecasting_critic_backstory(),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[google_news_tool]
        )
        
        # 4. Calibrated Synthesizer - Enhanced with systematic calibration
        self.calibrated_synthesizer = Agent(
            role='Master Synthesizer & Probability Calibrator',
            goal='Synthesize all analysis into well-calibrated probabilities using advanced superforecaster techniques and systematic calibration checks',
            backstory=get_calibrated_synthesizer_backstory(),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[google_news_tool]
        )
    
    
    def forecast_with_google_news(
        self, 
        question: str, 
        background: str = "",
        cutoff_date: Optional[datetime] = None,
        time_horizons: List[str] = None,
        is_benchmark: bool = False,
        recommended_articles: int = None,
        max_search_queries: int = None
    ) -> List[ForecastResult]:
        """
        Generate forecasts using enhanced superforecaster methodology
        
        Args:
            question: The forecasting question
            background: Additional context
            cutoff_date: Effective current date for analysis
            time_horizons: List of time horizons to forecast for (e.g., ["7d", "30d", "90d", "180d"]). 
                          If None, returns single forecast with default time horizon.
            is_benchmark: Whether this is a benchmark run
            recommended_articles: Number of articles to search for
            max_search_queries: Maximum search queries to use
            
        Returns:
            List of ForecastResult objects (single item if no time_horizons specified)
        """
        
        # Use cutoff_date as current date for agents, or actual current date if not provided
        effective_current_date = cutoff_date if cutoff_date else datetime.now()
        cutoff_str = effective_current_date.strftime("%Y-%m-%d")
        
        # Handle time horizons
        if time_horizons is None:
            time_horizons = ["1 year"]  # Default single forecast
            
        self.logger.log("enhanced_superforecaster", f"🚀 Starting Enhanced Superforecaster analysis")
        self.logger.log("enhanced_superforecaster", f"📋 Question: {question}")
        self.logger.log("enhanced_superforecaster", f"📅 Effective current date: {cutoff_str}")
        self.logger.log("enhanced_superforecaster", f"⏰ Time horizons: {time_horizons}")
        
        # Determine search timeframe (using consistent YYYY-MM-DD format)
        search_timeframe = {
            "start": self.training_cutoff,
            "end": cutoff_str,
            "start_datetime": self.training_cutoff,
            "end_datetime": cutoff_str
        }
        
        # Use provided parameters or instance defaults
        effective_recommended_articles = recommended_articles if recommended_articles is not None else self.recommended_articles
        effective_max_queries = max_search_queries if max_search_queries is not None else self.max_search_queries
        
        # Create tasks for forecasting (agents handle time horizon considerations internally)
        tasks = self._create_forecasting_tasks(
            question, background, cutoff_str, time_horizons, search_timeframe,
            effective_recommended_articles, effective_max_queries
        )
        
        # Update Google News tool to use the cutoff date for benchmark constraints
        self._set_benchmark_cutoff_date(cutoff_str)
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.research_analyst,
                self.evidence_evaluator,
                self.forecasting_critic,
                self.calibrated_synthesizer
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the forecasting process
        self.logger.info(f"🔄 Executing Enhanced Superforecaster crew...")
        result = crew.kickoff()
        
        # Extract structured Pydantic outputs and create ForecastResults
        forecast_results = []
        
        for i, horizon in enumerate(time_horizons):
            # Extract synthesis output from the crew result
            synthesis_output = None
            if hasattr(result, 'tasks_output') and result.tasks_output:
                # Get the last task output (synthesis)
                synthesis_task_output = result.tasks_output[-1]
                if hasattr(synthesis_task_output, 'pydantic') and synthesis_task_output.pydantic:
                    synthesis_output = synthesis_task_output.pydantic
            
            # Create ForecastResult from structured output
            if synthesis_output:
                forecast_result = ForecastResult(
                    question=question,
                    probability=synthesis_output.final_probability,
                    confidence_level=synthesis_output.confidence_level,
                    reasoning=synthesis_output.calibration_summary.reasoning_summary,
                    base_rate=synthesis_output.base_rate_anchor,
                    evidence_quality=0.85,  # High quality since using structured outputs
                    methodology_components={
                        "strategic_search_coordination": True,
                        "evidence_based_analysis": True,
                        "bias_detection_and_correction": True,
                        "calibrated_probability_assignment": True,
                        "superforecaster_best_practices": True,
                        "google_news_integration": True,
                        "comprehensive_reasoning": True
                    },
                    full_analysis=synthesis_output.dict(),
                    news_research_summary={"methodology": "Enhanced Superforecaster with Pydantic Structured Outputs"},
                    news_sources=["Strategic Google News integration"],
                    search_queries_used=["Strategic multi-query approach"],
                    total_articles_found=0,  # Will be populated from research output if needed
                    search_timeframe=search_timeframe,
                    time_horizon=horizon
                )
                forecast_results.append(forecast_result)
            else:
                # Fallback result if structured output not available
                fallback_probability = self._get_domain_fallback_probability(question)
                forecast_result = ForecastResult(
                    question=question,
                    probability=fallback_probability,
                    confidence_level="medium",
                    reasoning="Analysis completed but structured output not available",
                    base_rate=fallback_probability,
                    evidence_quality=0.6,
                    methodology_components={comp: False for comp in ["strategic_search_coordination", "evidence_based_analysis", "bias_detection_and_correction", "calibrated_probability_assignment", "superforecaster_best_practices", "google_news_integration", "comprehensive_reasoning"]},
                    full_analysis={"fallback": True},
                    news_research_summary={"error": "Structured output not available"},
                    news_sources=["Fallback integration"],
                    search_queries_used=["Fallback approach"],
                    total_articles_found=0,
                    search_timeframe=search_timeframe,
                    time_horizon=horizon
                )
                forecast_results.append(forecast_result)
        
        self.logger.info(f"✅ Enhanced Superforecaster forecast complete: {len(forecast_results)} results")
        return forecast_results
    
    def _create_forecasting_tasks(
        self, 
        question: str, 
        background: str, 
        cutoff_date: str,
        time_horizons: List[str],
        search_timeframe: Dict[str, str],
        recommended_articles: int,
        max_search_queries: int
    ) -> List[Task]:
        """Create tasks for forecasting with time horizon support"""
        
        # Convert time horizons to readable format
        if len(time_horizons) == 1:
            horizon_text = time_horizons[0]
        else:
            horizon_text = ", ".join(time_horizons)
        
        # Generate search strategy based on article target
        if recommended_articles == -1:
            search_strategy = "UNLIMITED"
            article_target = "unlimited articles"
            query_limit = "no limit on queries"
        elif recommended_articles >= 20:
            search_strategy = "COMPREHENSIVE"
            article_target = f"target {recommended_articles} articles"
            query_limit = f"up to {max_search_queries or 8} search queries"
        elif recommended_articles >= 10:
            search_strategy = "BALANCED"
            article_target = f"target {recommended_articles} articles"
            query_limit = f"up to {max_search_queries or 6} search queries"
        else:
            search_strategy = "FOCUSED"
            article_target = f"target {recommended_articles} articles"
            query_limit = f"up to {max_search_queries or 4} search queries"
        
        # Task 1: Research and Evidence Gathering
        research_task = Task(
            description=get_research_task_description(
                question, search_timeframe, cutoff_date, search_strategy, query_limit, article_target, background
            ),
            agent=self.research_analyst,
            expected_output="Comprehensive research summary with evidence analysis and base rate context",
            output_pydantic=ResearchOutput
        )
        
        # Task 2: Critical Evidence Evaluation and Bias Correction
        evaluation_task = Task(
            description=get_evaluation_task_description(question, cutoff_date),
            agent=self.evidence_evaluator,
            expected_output="Evidence evaluation with bias detection and quality weighting",
            context=[research_task],
            output_pydantic=EvaluationOutput
        )
        
        # Task 3: Forecasting Critique and Devil's Advocate Analysis
        critic_task = Task(
            description=get_critic_task_description(question, cutoff_date),
            agent=self.forecasting_critic,
            expected_output="Critical analysis with systematic challenges to forecasting reasoning",
            context=[research_task, evaluation_task],
            output_pydantic=CriticOutput
        )
        
        # Task 4: Calibrated Probability Synthesis
        synthesis_task = Task(
            description=get_synthesis_task_description(question, cutoff_date, horizon_text),
            agent=self.calibrated_synthesizer,
            expected_output="Final forecast with clear calibration methodology and conservative probability",
            context=[research_task, evaluation_task, critic_task],
            output_pydantic=SynthesisOutput
        )
        
        return [research_task, evaluation_task, critic_task, synthesis_task]
    
    def _execute_crew_with_logging(self, crew, question: str):
        """Execute the crew with enhanced logging to capture agent responses"""
        self.logger.log("crew_start", f"🎯 Starting crew execution for: {question}")
        
        try:
            # Execute the crew
            result = crew.kickoff()
            
            # Log completion
            self.logger.log("crew_completion", f"🎉 Crew execution completed successfully")
            
            # Log individual task outputs from CrewAI's result structure
            self._log_crew_task_outputs(crew, result)
            
            return result
            
        except Exception as e:
            self.logger.log("crew_error", f"❌ Crew execution failed: {str(e)}")
            raise e
    
    def _log_crew_task_outputs(self, crew, result):
        """Log individual task outputs from the crew execution"""
        try:
            # Try to access task outputs through the crew's tasks
            if hasattr(crew, 'tasks') and crew.tasks:
                for i, task in enumerate(crew.tasks):
                    agent_name = task.agent.role.replace(' ', '_').lower() if hasattr(task, 'agent') else f"agent_{i+1}"
                    task_name = f"task_{i+1}_{agent_name}"
                    
                    # Log task description
                    if hasattr(task, 'description'):
                        self.logger.log(f"task_{agent_name}", f"🎯 Task: {task.description[:150]}...")
                    
                    # Log task output if available
                    if hasattr(task, 'output') and task.output:
                        output_str = str(task.output)
                        output_preview = output_str[:1000] if len(output_str) > 1000 else output_str
                        self.logger.log(f"agent_{agent_name}", f"📝 Output: {output_preview}")
            
            # Also log the final result
            if hasattr(result, 'raw'):
                final_output = str(result.raw)[:1000]
                self.logger.log("final_result", f"🏁 Final result: {final_output}")
            elif hasattr(result, 'json_dict'):
                self.logger.log("final_result", f"🏁 Final JSON: {str(result.json_dict)[:1000]}")
            else:
                self.logger.log("final_result", f"🏁 Final result: {str(result)[:1000]}")
                
        except Exception as e:
            self.logger.log("logging_error", f"⚠️ Error logging task outputs: {str(e)}")
    

    

    

    

    

    

    

    

    










