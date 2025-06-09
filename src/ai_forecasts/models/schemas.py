"""Data models and schemas for the AI Forecasting System"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class ForecastMode(str, Enum):
    """Operating modes for the forecasting system"""
    PURE_FORECAST = "forecast"
    TARGETED = "targeted"
    STRATEGY = "strategy"


class ForecastRequest(BaseModel):
    """Input schema for forecast requests"""
    initial_conditions: Optional[str] = Field(
        default=None,
        description="Current state description. If None, uses current date as baseline"
    )
    outcomes_of_interest: Optional[List[str]] = Field(
        default=None,
        description="Specific outcomes to evaluate (for targeted mode)"
    )
    desired_outcome: Optional[str] = Field(
        default=None,
        description="Target outcome to achieve (for strategy mode)"
    )
    time_horizon: str = Field(
        default="1 year",
        description="Time frame for analysis (e.g., '6 months', '2 years')"
    )
    constraints: Optional[List[str]] = Field(
        default=None,
        description="Constraints and limitations (e.g., 'budget < $1M')"
    )


class OutcomePrediction(BaseModel):
    """Individual outcome prediction"""
    description: str = Field(description="Clear description of the outcome")
    probability: float = Field(ge=0.0, le=1.0, description="Probability estimate")
    confidence_interval: List[float] = Field(
        description="[lower_bound, upper_bound] confidence interval"
    )
    timeline: Optional[str] = Field(description="Expected timeline")
    key_drivers: List[str] = Field(description="Main factors influencing this outcome")
    early_indicators: List[str] = Field(description="Observable leading indicators")
    uncertainties: List[str] = Field(description="Key uncertainties affecting prediction")


class StrategyStep(BaseModel):
    """Individual step in a strategy"""
    phase: int = Field(description="Step sequence number")
    action: str = Field(description="Action to take")
    timeline: str = Field(description="Duration or deadline")
    success_criteria: str = Field(description="How to measure success")
    dependencies: List[str] = Field(description="Prerequisites for this step")
    probability: Optional[float] = Field(description="Success probability for this step")


class Strategy(BaseModel):
    """Complete strategy definition"""
    name: str = Field(description="Strategy name")
    steps: List[StrategyStep] = Field(description="Sequential steps")
    overall_probability: float = Field(description="Overall success probability")
    timeline: str = Field(description="Total timeline")
    cost_estimate: Optional[str] = Field(description="Resource requirements")
    critical_decisions: List[str] = Field(description="Key decision points")
    risk_factors: List[str] = Field(description="Main risks")


class GapAnalysis(BaseModel):
    """Analysis of gaps between current and desired state"""
    required_changes: List[str] = Field(description="What needs to change")
    needed_resources: List[str] = Field(description="Required resources")
    capability_gaps: List[str] = Field(description="Missing capabilities")


class ValidationResults(BaseModel):
    """Validation and confidence metrics"""
    logical_consistency: float = Field(description="Internal consistency score")
    probability_calibration: float = Field(description="Calibration quality")
    assumption_tracking: List[str] = Field(description="Key assumptions made")
    uncertainty_quantification: float = Field(description="Overall uncertainty level")


class ForecastResponse(BaseModel):
    """Pure forecasting mode response"""
    mode: str = Field(default="forecast")
    initial_conditions_summary: str
    time_horizon: str
    forecasts: List[OutcomePrediction]
    meta_analysis: Dict[str, Any] = Field(
        description="Dominant scenarios, black swans, key uncertainties"
    )
    validations: Optional[ValidationResults] = None


class TargetedResponse(BaseModel):
    """Targeted forecasting mode response"""
    mode: str = Field(default="targeted")
    initial_conditions_summary: str
    time_horizon: str
    evaluations: List[Dict[str, Any]] = Field(
        description="Evaluations of specific outcomes"
    )
    validations: Optional[ValidationResults] = None


class StrategyResponse(BaseModel):
    """Strategy generation mode response"""
    mode: str = Field(default="strategy")
    desired_outcome: str
    feasibility_score: float = Field(description="Overall feasibility assessment")
    gap_analysis: GapAnalysis
    recommended_strategy: Strategy
    alternative_strategies: List[Strategy]
    validations: Optional[ValidationResults] = None


# Benchmark-related models
class BenchmarkCase(BaseModel):
    """Individual benchmark test case"""
    case_id: str
    timestamp: datetime = Field(description="When forecast was meant to be made")
    initial_conditions: str
    mode: ForecastMode
    outcomes_of_interest: Optional[List[str]] = None
    desired_outcome: Optional[str] = None
    time_horizon: str
    
    # Ground truth
    actual_outcomes: List[Dict[str, Any]]
    actual_probabilities: Optional[Dict[str, float]] = None
    successful_strategies: Optional[List[Dict[str, Any]]] = None
    
    # Metadata
    domain: str = Field(description="Domain category")
    difficulty: str = Field(description="easy, medium, hard")
    source: str = Field(description="Source of this benchmark case")


class BenchmarkMetrics(BaseModel):
    """Evaluation metrics for benchmark results"""
    brier_score: Optional[float] = None
    log_score: Optional[float] = None
    calibration_error: Optional[float] = None
    top_k_accuracy: Optional[Dict[str, float]] = None
    strategy_success_rate: Optional[float] = None
    path_optimality: Optional[float] = None


class BenchmarkResult(BaseModel):
    """Results from running a benchmark case"""
    case_id: str
    prediction: Union[ForecastResponse, TargetedResponse, StrategyResponse]
    ground_truth: Dict[str, Any]
    metrics: BenchmarkMetrics
    evaluation_timestamp: datetime