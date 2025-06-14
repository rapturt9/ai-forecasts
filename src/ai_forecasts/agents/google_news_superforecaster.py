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

from .debate_forecasting_prompts import (
    get_high_advocate_backstory,
    get_low_advocate_backstory,
    get_debate_judge_backstory,
    get_high_advocate_task_description,
    get_low_advocate_task_description,
    get_debate_judge_task_description,
    get_high_advocate_rebuttal_description,
    get_low_advocate_rebuttal_description,
    get_judge_intermediate_description,
    get_enhanced_high_advocate_task_description,
    get_enhanced_low_advocate_task_description,
    get_enhanced_judge_task_description,
    HighAdvocateOutput,
    LowAdvocateOutput,
    DebateJudgmentOutput,
    HighRebuttalOutput,
    LowRebuttalOutput,
    JudgeIntermediateOutput,
    EnhancedHighAdvocateOutput,
    EnhancedLowAdvocateOutput,
    EnhancedJudgeOutput,
    EnhancedRebuttalOutput
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
                 recommended_articles: int = 10, max_search_queries: int = None, logger = None, 
                 debate_mode: bool = True, debate_rounds: int = 2, enhanced_quality_mode: bool = True,
                 search_budget_per_advocate: int = 10):
        self.logger = logger if logger is not None else agent_logger
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        self.training_cutoff = training_cutoff
        self.debate_mode = debate_mode  # New parameter for debate forecasting
        self.debate_rounds = debate_rounds  # Number of back-and-forth rounds in debate mode
        self.enhanced_quality_mode = enhanced_quality_mode  # Enable quality pruning and misconception refuting
        self.search_budget_per_advocate = search_budget_per_advocate  # Total searches allowed per advocate across all rounds
        
        # Search configuration parameters - optimized for efficiency
        self.recommended_articles = recommended_articles  # Target number of articles per search task
        self.max_search_queries = max_search_queries or (
            None if recommended_articles == -1 else  # -1 means unlimited
            max(2, min(5, recommended_articles // 3))  # More conservative search strategy
        )
        
        # Configure LLM with enhanced configuration for CrewAI
        # Set up environment for OpenRouter
        os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
        
        # Use the model directly with openrouter prefix
        model_name = "openrouter/" + os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")
        
        # Create LLM with minimal configuration to avoid function calling issues
        try:
            self.llm = LLM(
                model=model_name,
                api_key=openrouter_api_key,
                temperature=1.0
            )
            
            # Test the LLM to ensure it's working
            test_response = self.llm.call("Test")
            self.logger.info(f"✅ LLM test successful: {len(str(test_response))} chars")
            
        except Exception as e:
            self.logger.error(f"❌ LLM initialization failed: {e}")
            # Fallback to the most basic LLM configuration
            self.llm = LLM(model=model_name, api_key=openrouter_api_key)
        
        # Set additional environment variables for CrewAI compatibility
        os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
        os.environ["OPENAI_MODEL_NAME"] = model_name.replace("openrouter/", "")
        
        # Initialize fallback parser
        self._setup_fallback_parser()
        
        # Initialize agents
        if self.debate_mode:
            self._setup_debate_agents()
        else:
            self._setup_agents()
    
    def _set_benchmark_cutoff_date(self, cutoff_date: str):
        """Set benchmark cutoff date on all Google News tools"""
        # Find and update Google News tools used by agents
        if self.debate_mode:
            agents_to_update = [self.high_advocate, self.low_advocate, self.debate_judge]
        else:
            agents_to_update = [self.research_analyst, self.evidence_evaluator, self.forecasting_critic, self.calibrated_synthesizer]
            
        for agent in agents_to_update:
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
    
    def _setup_debate_agents(self):
        """Setup 3 debate agents: High Advocate, Low Advocate, and Judge"""
        
        # Create Google News tool with improved date handling
        search_timeframe = {
            "start": "06/01/2024",  # From June 2024 to freeze date
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        google_news_tool = CachedGoogleNewsTool(
            serp_api_key=self.serp_api_key,
            search_timeframe=search_timeframe
        )
        
        # 1. High Probability Advocate
        self.high_advocate = Agent(
            role='High Probability Advocate',
            goal='Build the strongest possible case for why the probability should be HIGH, using rigorous evidence and reasoning',
            backstory=get_high_advocate_backstory(),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[google_news_tool]
        )
        
        # 2. Low Probability Advocate
        self.low_advocate = Agent(
            role='Low Probability Advocate',
            goal='Build the strongest possible case for why the probability should be LOW, using rigorous evidence and reasoning',
            backstory=get_low_advocate_backstory(),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[google_news_tool]
        )
        
        # 3. Debate Judge (No search tools - only evaluates existing arguments)
        self.debate_judge = Agent(
            role='Forecasting Judge & Synthesizer',
            goal='Evaluate competing arguments and synthesize them into well-calibrated probabilities based on evidence quality',
            backstory=get_debate_judge_backstory(),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[]  # No search tools - judge only evaluates existing evidence
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
        
        # Update Google News tool to use the cutoff date for benchmark constraints
        self._set_benchmark_cutoff_date(cutoff_str)
        
        # Execute the forecasting process
        forecast_results = []
        
        if self.debate_mode:
            # Execute single consolidated debate for all time horizons
            self.logger.log("system", f"🔄 Executing consolidated debate for all time horizons: {time_horizons}")
            
            forecast_results = self._execute_consolidated_debate(
                question, background, cutoff_str, time_horizons, search_timeframe,
                effective_recommended_articles, effective_max_queries
            )
        else:
            # Traditional mode: Execute for each time horizon separately
            for i, horizon in enumerate(time_horizons):
                self.logger.log("system", f"🔄 Executing Enhanced Superforecaster crew for {horizon} horizon...")
                # Create traditional forecasting tasks
                horizon_tasks = self._create_forecasting_tasks(
                    question, background, cutoff_str, [horizon], search_timeframe,
                    effective_recommended_articles, effective_max_queries
                )
                
                # Create and run the traditional crew
                horizon_crew = Crew(
                    agents=[
                        self.research_analyst,
                        self.evidence_evaluator,
                        self.forecasting_critic,
                        self.calibrated_synthesizer
                    ],
                    tasks=horizon_tasks,
                    process=Process.sequential,
                    verbose=True
                )
            
            try:
                result = self._execute_crew_with_logging(horizon_crew, f"{question} (horizon: {horizon})")
                
                # Log detailed task outputs
                self._log_detailed_task_outputs(result, horizon)
                
                # Extract structured outputs and research data
                research_output, evaluation_output, critic_output, synthesis_output = self._extract_structured_outputs(result)
                
                # Extract research details
                news_sources, search_queries, total_articles = self._extract_research_details(research_output, result)
                
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
                            "strategic_search_coordination": bool(research_output),
                            "evidence_based_analysis": bool(research_output and research_output.evidence_analysis),
                            "bias_detection_and_correction": bool(evaluation_output and evaluation_output.bias_detection_results),
                            "calibrated_probability_assignment": bool(synthesis_output),
                            "superforecaster_best_practices": bool(critic_output),
                            "google_news_integration": bool(research_output and research_output.search_execution_summary),
                            "comprehensive_reasoning": bool(synthesis_output and synthesis_output.calibration_summary)
                        },
                        full_analysis={
                            "research": research_output.dict() if research_output else None,
                            "evaluation": evaluation_output.dict() if evaluation_output else None,
                            "critic": critic_output.dict() if critic_output else None,
                            "synthesis": synthesis_output.dict() if synthesis_output else None,
                            "horizon": horizon
                        },
                        news_research_summary={"methodology": f"Enhanced Superforecaster with Pydantic Structured Outputs for {horizon}"},
                        news_sources=news_sources,
                        search_queries_used=search_queries,
                        total_articles_found=total_articles,
                        search_timeframe=search_timeframe,
                        time_horizon=horizon
                    )
                    
                    self.logger.log("system", f"✅ {horizon} forecast: {synthesis_output.final_probability:.3f} (confidence: {synthesis_output.confidence_level})")
                    forecast_results.append(forecast_result)
                else:
                    # Fallback result if structured output not available
                    self.logger.log("system", f"⚠️ {horizon} forecast: Using fallback (no structured output)")
                    fallback_probability = 0.5  # Use neutral probability for fallback
                    forecast_result = ForecastResult(
                        question=question,
                        probability=fallback_probability,
                        confidence_level="low",
                        reasoning=f"Analysis completed for {horizon} but structured output not available",
                        base_rate=fallback_probability,
                        evidence_quality=0.6,
                        methodology_components={comp: False for comp in ["strategic_search_coordination", "evidence_based_analysis", "bias_detection_and_correction", "calibrated_probability_assignment", "superforecaster_best_practices", "google_news_integration", "comprehensive_reasoning"]},
                        full_analysis={"fallback": True, "horizon": horizon},
                        news_research_summary={"error": f"Structured output not available for {horizon}"},
                        news_sources=["Fallback integration"],
                        search_queries_used=["Fallback approach"],
                        total_articles_found=0,
                        search_timeframe=search_timeframe,
                        time_horizon=horizon
                    )
                    forecast_results.append(forecast_result)
                    
            except Exception as e:
                self.logger.error(f"❌ Error in {horizon} forecast: {str(e)}")
                # Create error result
                error_result = ForecastResult(
                    question=question,
                    probability=None,
                    confidence_level="low",
                    reasoning=f"Error occurred during {horizon} forecast: {str(e)}",
                    base_rate=None,
                    evidence_quality=0.0,
                    methodology_components={comp: False for comp in ["strategic_search_coordination", "evidence_based_analysis", "bias_detection_and_correction", "calibrated_probability_assignment", "superforecaster_best_practices", "google_news_integration", "comprehensive_reasoning"]},
                    full_analysis={"error": str(e), "horizon": horizon},
                    news_research_summary={"error": f"Failed to complete {horizon} forecast"},
                    news_sources=[],
                    search_queries_used=[],
                    total_articles_found=0,
                    search_timeframe=search_timeframe,
                    time_horizon=horizon
                )
                forecast_results.append(error_result)
        
        self.logger.info(f"✅ Enhanced Superforecaster forecast complete: {len(forecast_results)} results")
        return forecast_results
    
    # Removed _execute_iterative_debate - replaced by consolidated debate approach
    
    def _execute_consolidated_debate(
        self, 
        question: str, 
        background: str, 
        cutoff_str: str,
        time_horizons: List[str],
        search_timeframe: Dict[str, str],
        effective_recommended_articles: int,
        effective_max_queries: int
    ) -> List[ForecastResult]:
        """Execute consolidated debate with advocates researching for all time horizons, then judge evaluates at end"""
        
        self.logger.log("debate", f"🎭 Starting consolidated debate for all time horizons: {time_horizons}")
        
        try:
            # Convert time horizons to readable format for prompts
            horizon_text = ", ".join(time_horizons)
            
            # Round 1: Initial arguments for all time horizons
            self.logger.log("debate", "📍 Round 1: Initial Arguments for All Time Horizons")
            
            # Create initial argument tasks for all horizons combined
            initial_tasks = self._create_consolidated_debate_tasks(
                question, background, cutoff_str, time_horizons, search_timeframe,
                effective_recommended_articles, effective_max_queries
            )
            
            # Execute initial arguments (High Advocate and Low Advocate only, no judge yet)
            initial_crew = Crew(
                agents=[self.high_advocate, self.low_advocate],
                tasks=initial_tasks[:-1],  # Exclude judge task for now
                process=Process.sequential,
                verbose=True,
                output_log_file=None  # Disable output log to prevent issues
            )
            
            try:
                initial_result = self._execute_crew_with_logging(initial_crew, f"Initial arguments: {question} (all horizons)")
                
                # Extract structured outputs from initial arguments with fallback handling
                try:
                    high_output, low_output, _ = self._extract_debate_outputs(initial_result)
                except Exception as pydantic_error:
                    self.logger.warning(f"⚠️ Pydantic extraction failed: {pydantic_error}. Using text fallback.")
                    high_output, low_output = None, None
                
            except Exception as crew_error:
                self.logger.error(f"❌ Initial crew execution failed: {crew_error}")
                raise Exception(f"Failed to execute initial debate arguments: {crew_error}")
            
            # Store debate history
            debate_history = {
                "round_1": {
                    "high_advocate": high_output.dict() if high_output else "High advocate output not available",
                    "low_advocate": low_output.dict() if low_output else "Low advocate output not available"
                }
            }
            
            # Additional rounds of rebuttals (no intermediate judge evaluations)
            for round_num in range(2, self.debate_rounds + 2):
                self.logger.log("debate", f"📍 Round {round_num}: Rebuttals for All Time Horizons")
                
                # Create rebuttal tasks for all horizons with Pydantic outputs
                if self.enhanced_quality_mode:
                    high_rebuttal_task = Task(
                        description=get_high_advocate_rebuttal_description(question, cutoff_str, horizon_text),
                        agent=self.high_advocate,
                        expected_output="Enhanced rebuttal to Low Advocate arguments across all time horizons",
                        output_pydantic=EnhancedRebuttalOutput
                    )
                    
                    low_rebuttal_task = Task(
                        description=get_low_advocate_rebuttal_description(question, cutoff_str, horizon_text),
                        agent=self.low_advocate,
                        expected_output="Enhanced rebuttal to High Advocate arguments across all time horizons",
                        output_pydantic=EnhancedRebuttalOutput
                    )
                else:
                    high_rebuttal_task = Task(
                        description=get_high_advocate_rebuttal_description(question, cutoff_str, horizon_text),
                        agent=self.high_advocate,
                        expected_output="Strong rebuttal to Low Advocate arguments across all time horizons",
                        output_pydantic=HighRebuttalOutput
                    )
                    
                    low_rebuttal_task = Task(
                        description=get_low_advocate_rebuttal_description(question, cutoff_str, horizon_text),
                        agent=self.low_advocate,
                        expected_output="Strong rebuttal to High Advocate arguments across all time horizons",
                        output_pydantic=LowRebuttalOutput
                    )
                
                # Execute rebuttal round
                rebuttal_crew = Crew(
                    agents=[self.high_advocate, self.low_advocate],
                    tasks=[high_rebuttal_task, low_rebuttal_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                try:
                    rebuttal_result = self._execute_crew_with_logging(rebuttal_crew, f"Rebuttal round {round_num-1}: {question} (all horizons)")
                    
                    # Extract structured rebuttal outputs with fallback handling
                    try:
                        high_rebuttal, low_rebuttal = self._extract_rebuttal_outputs(rebuttal_result)
                    except Exception as pydantic_error:
                        self.logger.warning(f"⚠️ Rebuttal Pydantic extraction failed: {pydantic_error}. Using fallback.")
                        high_rebuttal, low_rebuttal = None, None
                        
                except Exception as rebuttal_error:
                    self.logger.error(f"❌ Rebuttal round {round_num-1} failed: {rebuttal_error}")
                    high_rebuttal, low_rebuttal = None, None
                
                # Store this round's results
                debate_history[f"round_{round_num}"] = {
                    "high_rebuttal": high_rebuttal.dict() if high_rebuttal else "High rebuttal not available",
                    "low_rebuttal": low_rebuttal.dict() if low_rebuttal else "Low rebuttal not available"
                }
            
            # Final judge decision
            self.logger.log("debate", "⚖️ Final Judge Decision")
            
            # Create final judgment task with full context and Pydantic output
            all_tasks = initial_tasks[:-1]  # Original tasks without original judge
            
            if self.enhanced_quality_mode:
                final_judge_task = Task(
                    description=get_enhanced_judge_task_description(question, cutoff_str, horizon_text),
                    agent=self.debate_judge,
                    expected_output="Enhanced final judgment with calibrated probability based on debate evaluation",
                    context=all_tasks,  # Full context of all previous arguments and rebuttals
                    output_pydantic=EnhancedJudgeOutput
                )
            else:
                final_judge_task = Task(
                    description=get_debate_judge_task_description(question, cutoff_str, horizon_text),
                    agent=self.debate_judge,
                    expected_output="Final judgment with calibrated probability based on debate evaluation",
                    context=all_tasks,  # Full context of all previous arguments and rebuttals
                    output_pydantic=DebateJudgmentOutput
                )
            
            final_judge_crew = Crew(
                agents=[self.debate_judge],
                tasks=[final_judge_task],
                process=Process.sequential,
                verbose=True
            )
            
            try:
                judge_result = self._execute_crew_with_logging(final_judge_crew, f"Final judgment: {question} (all horizons)")
                
                # Extract structured judge output (Pydantic object) with fallback handling
                try:
                    _, _, judge_output = self._extract_debate_outputs(judge_result)
                except Exception as pydantic_error:
                    self.logger.warning(f"⚠️ Judge Pydantic extraction failed: {pydantic_error}. Using fallback.")
                    judge_output = None
                    
            except Exception as judge_error:
                self.logger.error(f"❌ Final judge execution failed: {judge_error}")
                judge_output = None
            
            # Store final judgment
            debate_history["final_judgment"] = judge_output.dict() if judge_output else "Judge output not available"
            
            # Create ForecastResult for each time horizon from consolidated judgment
            forecast_results = []
            for horizon in time_horizons:
                # Create comprehensive forecast result
                forecast_result = ForecastResult(
                    question=question,
                    probability=judge_output.final_probability if judge_output else 0.5,
                    confidence_level=judge_output.confidence_level if judge_output else "low",
                    reasoning=judge_output.decision_rationale if judge_output else "Debate completed but no judgment available",
                    base_rate=0.5,  # Debate mode doesn't focus on single base rate
                    evidence_quality=0.9,  # Higher quality due to iterative adversarial process
                    methodology_components={
                        "consolidated_adversarial_debate": True,
                        "multi_round_rebuttals": True,
                        "evidence_based_advocacy": True,
                        "final_judicial_evaluation": True,
                        "bias_resistance": True,
                        "google_news_integration": True,
                        "multiple_perspectives": True,
                        "comprehensive_reasoning": True,
                        f"debate_rounds_{self.debate_rounds}": True
                    },
                    full_analysis={
                        "debate_history": debate_history,
                        "final_judgment": judge_output.dict() if judge_output else None,
                        "horizon": horizon,
                        "debate_mode": True,
                        "consolidated_mode": True,
                        "total_rounds": len([k for k in debate_history.keys() if k.startswith("round_")])
                    },
                    news_research_summary={"methodology": f"Consolidated debate forecasting for {horizon}"},
                    news_sources=["Strategic adversarial Google News research"],
                    search_queries_used=["High-probability queries", "Low-probability queries", "Rebuttal evidence"],
                    total_articles_found=0,  # Will be aggregated from debate history if needed
                    search_timeframe=search_timeframe,
                    time_horizon=horizon
                )
                
                forecast_results.append(forecast_result)
                self.logger.log("debate", f"✅ {horizon} forecast: {judge_output.final_probability:.3f}" if judge_output else f"✅ {horizon} forecast: fallback")
            
            self.logger.log("debate", f"✅ Consolidated debate completed for all horizons: {len(forecast_results)} results")
            return forecast_results
            
        except Exception as e:
            self.logger.error(f"❌ Error in consolidated debate: {str(e)}")
            # Return error results for all horizons
            error_results = []
            for horizon in time_horizons:
                error_result = ForecastResult(
                    question=question,
                    probability=None,
                    confidence_level="low",
                    reasoning=f"Error in consolidated debate: {str(e)}",
                    base_rate=None,
                    evidence_quality=0.0,
                    methodology_components={"consolidated_debate_error": True},
                    full_analysis={"error": str(e), "horizon": horizon, "debate_mode": True},
                    news_research_summary={"error": "Consolidated debate failed"},
                    news_sources=[],
                    search_queries_used=[],
                    total_articles_found=0,
                    search_timeframe=search_timeframe,
                    time_horizon=horizon
                )
                error_results.append(error_result)
            return error_results
    
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
    
    def _create_debate_tasks(
        self, 
        question: str, 
        background: str, 
        cutoff_date: str,
        time_horizons: List[str],
        search_timeframe: Dict[str, str],
        recommended_articles: int,
        max_search_queries: int
    ) -> List[Task]:
        """Create tasks for debate-based forecasting"""
        
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
            query_limit = f"up to {max_search_queries or 5} search queries"
        else:
            search_strategy = "FOCUSED"
            article_target = f"target {recommended_articles} articles"
            query_limit = f"up to {max_search_queries or 3} search queries"
        
        # Task 1: High Probability Advocate
        if self.enhanced_quality_mode:
            high_advocate_task = Task(
                description=get_enhanced_high_advocate_task_description(
                    question, search_timeframe, cutoff_date, search_strategy, query_limit, article_target, background
                ),
                agent=self.high_advocate,
                expected_output="Enhanced case for high probability with quality pruning and misconception refuting",
                output_pydantic=EnhancedHighAdvocateOutput
            )
        else:
            high_advocate_task = Task(
                description=get_high_advocate_task_description(
                    question, search_timeframe, cutoff_date, search_strategy, query_limit, article_target, background
                ),
                agent=self.high_advocate,
                expected_output="Strong case for high probability with evidence and reasoning",
                output_pydantic=HighAdvocateOutput
            )
        
        # Task 2: Low Probability Advocate
        if self.enhanced_quality_mode:
            low_advocate_task = Task(
                description=get_enhanced_low_advocate_task_description(
                    question, search_timeframe, cutoff_date, search_strategy, query_limit, article_target, background
                ),
                agent=self.low_advocate,
                expected_output="Enhanced case for low probability with quality pruning and misconception refuting",
                output_pydantic=EnhancedLowAdvocateOutput
            )
        else:
            low_advocate_task = Task(
                description=get_low_advocate_task_description(
                    question, search_timeframe, cutoff_date, search_strategy, query_limit, article_target, background
                ),
                agent=self.low_advocate,
                expected_output="Strong case for low probability with evidence and reasoning",
                output_pydantic=LowAdvocateOutput
            )
        
        # Task 3: Debate Judge
        if self.enhanced_quality_mode:
            judge_task = Task(
                description=get_enhanced_judge_task_description(question, cutoff_date, horizon_text),
                agent=self.debate_judge,
                expected_output="Enhanced judgment with quality assessment and misconception resolution",
                context=[high_advocate_task, low_advocate_task],
                output_pydantic=EnhancedJudgeOutput
            )
        else:
            judge_task = Task(
                description=get_debate_judge_task_description(question, cutoff_date, horizon_text),
                agent=self.debate_judge,
                expected_output="Final judgment with calibrated probability based on debate evaluation",
                context=[high_advocate_task, low_advocate_task],
                output_pydantic=DebateJudgmentOutput
            )
        
        return [high_advocate_task, low_advocate_task, judge_task]
    
    def _create_consolidated_debate_tasks(
        self, 
        question: str, 
        background: str, 
        cutoff_date: str,
        time_horizons: List[str],
        search_timeframe: Dict[str, str],
        recommended_articles: int,
        max_search_queries: int
    ) -> List[Task]:
        """Create tasks for consolidated debate with multiple time horizons"""
        
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
        
        # Task 1: High Probability Advocate - Consolidated for all time horizons
        if self.enhanced_quality_mode:
            high_advocate_task = Task(
                description=get_enhanced_high_advocate_task_description(
                    question, search_timeframe, cutoff_date, search_strategy, query_limit, article_target, background
                ),
                agent=self.high_advocate,
                expected_output="Enhanced case for high probability with quality pruning and misconception refuting for all time horizons",
                output_pydantic=EnhancedHighAdvocateOutput
            )
        else:
            high_advocate_task = Task(
                description=get_high_advocate_task_description(
                    question, search_timeframe, cutoff_date, search_strategy, query_limit, article_target, background
                ),
                agent=self.high_advocate,
                expected_output="Strong case for high probability with evidence and reasoning for all time horizons",
                output_pydantic=HighAdvocateOutput
            )
        
        # Task 2: Low Probability Advocate - Consolidated for all time horizons
        if self.enhanced_quality_mode:
            low_advocate_task = Task(
                description=get_enhanced_low_advocate_task_description(
                    question, search_timeframe, cutoff_date, search_strategy, query_limit, article_target, background
                ),
                agent=self.low_advocate,
                expected_output="Enhanced case for low probability with quality pruning and misconception refuting for all time horizons",
                output_pydantic=EnhancedLowAdvocateOutput
            )
        else:
            low_advocate_task = Task(
                description=get_low_advocate_task_description(
                    question, search_timeframe, cutoff_date, search_strategy, query_limit, article_target, background
                ),
                agent=self.low_advocate,
                expected_output="Strong case for low probability with evidence and reasoning for all time horizons",
                output_pydantic=LowAdvocateOutput
            )
        
        # Task 3: Debate Judge - Consolidated for all time horizons
        if self.enhanced_quality_mode:
            judge_task = Task(
                description=get_enhanced_judge_task_description(question, cutoff_date, horizon_text),
                agent=self.debate_judge,
                expected_output="Enhanced judgment with quality assessment and misconception resolution for all time horizons",
                context=[high_advocate_task, low_advocate_task],
                output_pydantic=EnhancedJudgeOutput
            )
        else:
            judge_task = Task(
                description=get_debate_judge_task_description(question, cutoff_date, horizon_text),
                agent=self.debate_judge,
                expected_output="Final judgment with calibrated probability based on debate evaluation for all time horizons",
                context=[high_advocate_task, low_advocate_task],
                output_pydantic=DebateJudgmentOutput
            )
        
        return [high_advocate_task, low_advocate_task, judge_task]
    
    # Removed unused _process_debate_result and _process_traditional_result methods
    # These were replaced by consolidated debate approach
    
    def _extract_rebuttal_outputs(self, crew_result):
        """Extract rebuttal outputs from crew result"""
        high_rebuttal = None
        low_rebuttal = None
        
        if hasattr(crew_result, 'tasks_output') and crew_result.tasks_output:
            for task_output in crew_result.tasks_output:
                if hasattr(task_output, 'pydantic') and task_output.pydantic:
                    pydantic_obj = task_output.pydantic
                    
                    if isinstance(pydantic_obj, (HighRebuttalOutput, EnhancedRebuttalOutput)):
                        high_rebuttal = pydantic_obj
                        self.logger.log("system", "✅ Found High Rebuttal Output")
                    elif isinstance(pydantic_obj, (LowRebuttalOutput, EnhancedRebuttalOutput)):
                        low_rebuttal = pydantic_obj
                        self.logger.log("system", "✅ Found Low Rebuttal Output")
        
        return high_rebuttal, low_rebuttal
    
    def _extract_judge_intermediate_output(self, crew_result):
        """Extract judge intermediate output from crew result"""
        judge_intermediate = None
        
        if hasattr(crew_result, 'tasks_output') and crew_result.tasks_output:
            for task_output in crew_result.tasks_output:
                if hasattr(task_output, 'pydantic') and task_output.pydantic:
                    pydantic_obj = task_output.pydantic
                    
                    if isinstance(pydantic_obj, JudgeIntermediateOutput):
                        judge_intermediate = pydantic_obj
                        self.logger.log("system", "✅ Found Judge Intermediate Output")
                        break
        
        return judge_intermediate
    
    def _create_iterative_debate_result(
        self, 
        question: str, 
        horizon: str, 
        search_timeframe: Dict[str, str], 
        debate_history: Dict, 
        judge_output: Optional[DebateJudgmentOutput]
    ) -> ForecastResult:
        """Create comprehensive forecast result from iterative debate"""
        
        if judge_output:
            # Extract comprehensive reasoning from full debate
            reasoning_parts = []
            
            # Add initial arguments
            if "round_1" in debate_history:
                if debate_history["round_1"].get("high_advocate"):
                    reasoning_parts.append(f"High Advocate Initial: {debate_history['round_1']['high_advocate'].get('position_statement', 'N/A')}")
                if debate_history["round_1"].get("low_advocate"):
                    reasoning_parts.append(f"Low Advocate Initial: {debate_history['round_1']['low_advocate'].get('position_statement', 'N/A')}")
            
            # Add rebuttal summaries
            for round_key in sorted([k for k in debate_history.keys() if k.startswith("round_") and k != "round_1"]):
                round_data = debate_history[round_key]
                if round_data.get("high_rebuttal"):
                    reasoning_parts.append(f"High Rebuttal {round_key}: {round_data['high_rebuttal'].get('rebuttal_summary', 'N/A')}")
                if round_data.get("low_rebuttal"):
                    reasoning_parts.append(f"Low Rebuttal {round_key}: {round_data['low_rebuttal'].get('rebuttal_summary', 'N/A')}")
            
            # Add final judgment
            reasoning_parts.append(f"Final Judgment: {judge_output.decision_rationale}")
            
            reasoning = " | ".join(reasoning_parts)
            
            # Count total rounds
            total_rounds = len([k for k in debate_history.keys() if k.startswith("round_")])
            
            forecast_result = ForecastResult(
                question=question,
                probability=judge_output.final_probability,
                confidence_level=judge_output.confidence_level,
                reasoning=reasoning,
                base_rate=0.5,  # Debate mode doesn't focus on single base rate
                evidence_quality=0.9,  # Higher quality due to iterative adversarial process
                methodology_components={
                    "iterative_adversarial_debate": True,
                    "multi_round_rebuttals": True,
                    "evidence_based_advocacy": True,
                    "judicial_evaluation": True,
                    "bias_resistance": True,
                    "google_news_integration": True,
                    "multiple_perspectives": True,
                    "comprehensive_reasoning": True,
                    f"debate_rounds_{total_rounds}": True
                },
                full_analysis={
                    "debate_history": debate_history,
                    "final_judgment": judge_output.dict(),
                    "horizon": horizon,
                    "debate_mode": True,
                    "total_rounds": total_rounds
                },
                news_research_summary={"methodology": f"Iterative {total_rounds}-round debate forecasting for {horizon}"},
                news_sources=["Strategic adversarial Google News research"],
                search_queries_used=["High-probability queries", "Low-probability queries", "Rebuttal evidence"],
                total_articles_found=0,  # Will be aggregated from debate history if needed
                search_timeframe=search_timeframe,
                time_horizon=horizon
            )
            
            return forecast_result
        else:
            # Fallback if final judgment not available
            return ForecastResult(
                question=question,
                probability=0.5,
                confidence_level="Low",
                reasoning="Iterative debate completed but final judgment unavailable",
                base_rate=0.5,
                evidence_quality=0.6,
                methodology_components={"iterative_debate_error": True},
                full_analysis={"error": "Final judgment not available", "debate_history": debate_history, "horizon": horizon},
                news_research_summary={"error": "Iterative debate processing failed"},
                news_sources=["Debate process"],
                search_queries_used=["Debate queries"],
                total_articles_found=0,
                search_timeframe=search_timeframe,
                time_horizon=horizon
            )
    
    def _extract_debate_outputs(self, crew_result):
        """Extract structured outputs from debate crew result"""
        high_output = None
        low_output = None
        judge_output = None
        
        # Extract outputs from each task
        if hasattr(crew_result, 'tasks_output') and crew_result.tasks_output:
            self.logger.log("system", f"📊 Found {len(crew_result.tasks_output)} debate task outputs")
            
            for i, task_output in enumerate(crew_result.tasks_output):
                self.logger.log("system", f"🔍 Processing debate task {i+1} output...")
                
                # Check if output is a Pydantic model instance
                if hasattr(task_output, 'pydantic') and task_output.pydantic:
                    pydantic_obj = task_output.pydantic
                    
                    if isinstance(pydantic_obj, (HighAdvocateOutput, EnhancedHighAdvocateOutput)):
                        high_output = pydantic_obj
                        self.logger.log("system", "✅ Found High Advocate Output")
                    elif isinstance(pydantic_obj, (LowAdvocateOutput, EnhancedLowAdvocateOutput)):
                        low_output = pydantic_obj
                        self.logger.log("system", "✅ Found Low Advocate Output")
                    elif isinstance(pydantic_obj, (DebateJudgmentOutput, EnhancedJudgeOutput)):
                        judge_output = pydantic_obj
                        self.logger.log("system", "✅ Found Judge Output")
        
        return high_output, low_output, judge_output
    
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
    
    def _extract_structured_outputs(self, crew_result):
        """Extract structured Pydantic outputs from crew result"""
        research_output = None
        evaluation_output = None 
        critic_output = None
        synthesis_output = None
        
        # Extract outputs from each task
        if hasattr(crew_result, 'tasks_output') and crew_result.tasks_output:
            self.logger.log("system", f"📊 Found {len(crew_result.tasks_output)} task outputs")
            
            for i, task_output in enumerate(crew_result.tasks_output):
                self.logger.log("system", f"🔍 Processing task {i+1} output...")
                
                # Check if output is a Pydantic model instance
                if hasattr(task_output, 'pydantic') and task_output.pydantic:
                    pydantic_obj = task_output.pydantic
                    
                    if isinstance(pydantic_obj, ResearchOutput):
                        research_output = pydantic_obj
                        self.logger.log("system", "✅ Found Research Output")
                    elif isinstance(pydantic_obj, EvaluationOutput):
                        evaluation_output = pydantic_obj
                        self.logger.log("system", "✅ Found Evaluation Output")
                    elif isinstance(pydantic_obj, CriticOutput):
                        critic_output = pydantic_obj
                        self.logger.log("system", "✅ Found Critic Output")
                    elif isinstance(pydantic_obj, SynthesisOutput):
                        synthesis_output = pydantic_obj
                        self.logger.log("system", "✅ Found Synthesis Output")
        
        return research_output, evaluation_output, critic_output, synthesis_output
    
    def _extract_research_details(self, research_output, crew_result):
        """Extract news sources, search queries, and article count from research output"""
        news_sources = []
        search_queries = []
        total_articles = 0
        
        if research_output:
            # Extract from research output
            total_articles = research_output.search_execution_summary.total_articles_found
            search_queries = research_output.search_execution_summary.most_effective_queries
            
            # Try to extract news sources from evidence analysis
            for evidence in research_output.evidence_analysis:
                if hasattr(evidence, 'evidence_description'):
                    # Extract potential news source mentions from evidence descriptions
                    desc = evidence.evidence_description
                    # Simple extraction - look for common news source patterns
                    import re
                    sources = re.findall(r'(?:according to|reported by|from) ([A-Z][a-z]+ ?[A-Z][a-z]*)', desc)
                    news_sources.extend(sources)
        else:
            # Fallback extraction from string content
            result_str = str(crew_result)
            # Simple fallback extraction
            news_sources = ["Strategic Google News integration"]
            search_queries = ["Strategic multi-query approach"]
            total_articles = 0
        
        # Return unique sources, default if none found
        unique_sources = list(set(news_sources)) if news_sources else ["Strategic Google News integration"]
        unique_queries = list(set(search_queries)) if search_queries else ["Strategic multi-query approach"]
        
        return unique_sources[:10], unique_queries[:8], total_articles
    
    def _log_detailed_task_outputs(self, crew_result, horizon):
        """Log detailed task outputs including agent responses and research data"""
        try:
            if hasattr(crew_result, 'tasks_output') and crew_result.tasks_output:
                for i, task_output in enumerate(crew_result.tasks_output):
                    task_name = f"task_{i+1}_{horizon}"
                    
                    # Log raw task output
                    if hasattr(task_output, 'raw'):
                        output_str = str(task_output.raw)
                        output_preview = output_str[:2000] if len(output_str) > 2000 else output_str
                        self.logger.log(task_name, f"📝 Raw Output: {output_preview}")
                    
                    # Log structured output if available
                    if hasattr(task_output, 'pydantic') and task_output.pydantic:
                        pydantic_obj = task_output.pydantic
                        
                        if isinstance(pydantic_obj, ResearchOutput):
                            self.logger.log(task_name, "🔍 Research Agent Output", {
                                "outcome_status": pydantic_obj.outcome_status.dict() if pydantic_obj.outcome_status else None,
                                "search_summary": pydantic_obj.search_execution_summary.dict() if pydantic_obj.search_execution_summary else None,
                                "evidence_count": len(pydantic_obj.evidence_analysis) if pydantic_obj.evidence_analysis else 0,
                                "base_rate_context": pydantic_obj.base_rate_context.dict() if pydantic_obj.base_rate_context else None
                            })
                            
                            # Log individual evidence pieces
                            if pydantic_obj.evidence_analysis:
                                for j, evidence in enumerate(pydantic_obj.evidence_analysis[:5]):  # Log first 5 pieces
                                    self.logger.log(task_name, f"📋 Evidence {j+1}", {
                                        "description": evidence.evidence_description[:200] + "..." if len(evidence.evidence_description) > 200 else evidence.evidence_description,
                                        "strength": evidence.evidence_strength,
                                        "credibility": evidence.source_credibility,
                                        "direction": evidence.evidence_direction
                                    })
                        
                        elif isinstance(pydantic_obj, EvaluationOutput):
                            self.logger.log(task_name, "⚖️ Evaluation Agent Output", {
                                "evidence_quality": pydantic_obj.evidence_quality_analysis.dict() if pydantic_obj.evidence_quality_analysis else None,
                                "bias_detection": pydantic_obj.bias_detection_results.dict() if pydantic_obj.bias_detection_results else None,
                                "evidence_weighting": pydantic_obj.evidence_weighting.dict() if pydantic_obj.evidence_weighting else None
                            })
                        
                        elif isinstance(pydantic_obj, CriticOutput):
                            self.logger.log(task_name, "🔎 Critic Agent Output", {
                                "reference_class": pydantic_obj.reference_class_verification.dict() if pydantic_obj.reference_class_verification else None,
                                "alternative_scenarios": pydantic_obj.alternative_scenarios.dict() if pydantic_obj.alternative_scenarios else None,
                                "probability_testing": pydantic_obj.probability_range_testing.dict() if pydantic_obj.probability_range_testing else None,
                                "recommended_adjustments": pydantic_obj.recommended_adjustments
                            })
                        
                        elif isinstance(pydantic_obj, SynthesisOutput):
                            self.logger.log(task_name, "🎯 Synthesis Agent Output", {
                                "final_probability": pydantic_obj.final_probability,
                                "confidence_level": pydantic_obj.confidence_level,
                                "base_rate_anchor": pydantic_obj.base_rate_anchor,
                                "evidence_adjustment": pydantic_obj.evidence_adjustment.dict() if pydantic_obj.evidence_adjustment else None,
                                "uncertainty_factors": pydantic_obj.uncertainty_factors.dict() if pydantic_obj.uncertainty_factors else None,
                                "calibration_summary": pydantic_obj.calibration_summary.dict() if pydantic_obj.calibration_summary else None
                            })
                    
                    # Log agent information if available
                    if hasattr(task_output, 'agent'):
                        agent_role = task_output.agent if isinstance(task_output.agent, str) else getattr(task_output.agent, 'role', 'Unknown')
                        self.logger.log(task_name, f"👤 Agent: {agent_role}")
        
        except Exception as e:
            self.logger.log("logging_error", f"⚠️ Error logging detailed task outputs: {str(e)}")
    
    def _finalize_consolidated_debate(
        self, 
        question: str,
        time_horizons: List[str],
        search_timeframe: Dict[str, str],
        debate_history: Dict,
        initial_tasks: List
    ) -> List[ForecastResult]:
        """Finalize consolidated debate with judge providing final evaluation for all time horizons"""
        
        # Final judge decision for ALL time horizons at once
        self.logger.log("debate", "⚖️ Final Judge Decision for All Time Horizons")
        
        # Create final judgment task with full context for all horizons
        all_tasks = initial_tasks[:-1]  # Original tasks without original judge
        horizon_text = ", ".join(time_horizons)
        
        final_judge_task = Task(
            description=get_debate_judge_task_description(question, "", horizon_text),
            agent=self.debate_judge,
            expected_output="Final judgment with calibrated probabilities for each time horizon based on full debate",
            output_pydantic=DebateJudgmentOutput,
            context=all_tasks  # Full context of all previous arguments and rebuttals
        )
        
        final_judge_crew = Crew(
            agents=[self.debate_judge],
            tasks=[final_judge_task],
            process=Process.sequential,
            verbose=True
        )
        
        judge_result = self._execute_crew_with_logging(final_judge_crew, f"Final judgment: {question} (all horizons)")
        _, _, judge_output = self._extract_debate_outputs(judge_result)
        
        # Store final judgment
        debate_history["final_judgment"] = judge_output.dict() if judge_output else None
        
        # Create ForecastResult for each time horizon from consolidated judgment
        forecast_results = []
        for horizon in time_horizons:
            # Create comprehensive forecast result
            forecast_result = ForecastResult(
                question=question,
                probability=judge_output.final_probability if judge_output else 0.5,
                confidence_level=judge_output.confidence_level if judge_output else "low",
                reasoning=judge_output.decision_rationale if judge_output else "Debate completed but no judgment available",
                base_rate=0.5,  # Debate mode doesn't focus on single base rate
                evidence_quality=0.9,  # Higher quality due to iterative adversarial process
                methodology_components={
                    "consolidated_adversarial_debate": True,
                    "multi_round_rebuttals": True,
                    "evidence_based_advocacy": True,
                    "final_judicial_evaluation": True,
                    "bias_resistance": True,
                    "google_news_integration": True,
                    "multiple_perspectives": True,
                    "comprehensive_reasoning": True,
                    f"debate_rounds_{self.debate_rounds}": True
                },
                full_analysis={
                    "debate_history": debate_history,
                    "final_judgment": judge_output.dict() if judge_output else None,
                    "horizon": horizon,
                    "debate_mode": True,
                    "consolidated_mode": True,
                    "total_rounds": len([k for k in debate_history.keys() if k.startswith("round_")])
                },
                news_research_summary={"methodology": f"Consolidated debate forecasting for {horizon}"},
                news_sources=["Strategic adversarial Google News research"],
                search_queries_used=["High-probability queries", "Low-probability queries", "Rebuttal evidence"],
                total_articles_found=0,  # Will be aggregated from debate history if needed
                search_timeframe=search_timeframe,
                time_horizon=horizon
            )
            
            forecast_results.append(forecast_result)
            self.logger.log("debate", f"✅ {horizon} forecast: {judge_output.final_probability:.3f}" if judge_output else f"✅ {horizon} forecast: fallback")
        
        self.logger.log("debate", f"✅ Consolidated debate completed for all horizons: {len(forecast_results)} results")
        return forecast_results
