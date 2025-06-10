"""
Trend Extrapolation Engine

This module implements sophisticated trend extrapolation capabilities that can:
1. Identify trend patterns from discovered domain knowledge
2. Apply appropriate mathematical models for extrapolation  
3. Account for trend breaks, cycles, and saturation points
4. Generate probabilistic forecasts based on trend continuation
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import math

from langchain.schema import HumanMessage, SystemMessage
from ..utils.llm_client import LLMClient
from ..utils.agent_logger import agent_logger
from .dynamic_discovery import DiscoveredKnowledge, ScalingLaw, DomainTrend


class TrendType(Enum):
    """Types of trend patterns"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    LOGISTIC = "logistic"
    POWER_LAW = "power_law"
    CYCLICAL = "cyclical"
    DECAY = "decay"
    STEP_FUNCTION = "step_function"
    UNKNOWN = "unknown"


@dataclass
class TrendModel:
    """Mathematical model for a trend"""
    trend_type: TrendType
    parameters: Dict[str, float]
    confidence: float
    applicable_range: Tuple[float, float]
    saturation_point: Optional[float]
    breakdown_conditions: List[str]


@dataclass
class ExtrapolationResult:
    """Result of trend extrapolation"""
    predicted_value: float
    confidence_interval: Tuple[float, float]
    probability_ranges: Dict[str, float]  # e.g., {"<0.2": 0.1, "0.2-0.5": 0.3, ...}
    model_used: TrendModel
    assumptions: List[str]
    risk_factors: List[str]
    extrapolation_confidence: float


@dataclass
class TrendBreakAnalysis:
    """Analysis of potential trend breaks"""
    break_probability: float
    break_timeframe: str
    break_triggers: List[str]
    alternative_scenarios: List[Dict[str, Any]]


class TrendExtrapolationEngine:
    """
    Engine for extrapolating trends using discovered domain knowledge
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        self.logger = agent_logger
    
    def extrapolate_trends(
        self,
        question: str,
        background: str,
        domain_knowledge: DiscoveredKnowledge,
        time_horizon: str,
        cutoff_date: Optional[datetime] = None
    ) -> ExtrapolationResult:
        """Main method to extrapolate trends for forecasting"""
        
        self.logger.log("trend_extrapolation", f"Starting trend extrapolation for {time_horizon}")
        
        # Step 1: Select the most relevant trends and scaling laws
        relevant_patterns = self._select_relevant_patterns(
            question, background, domain_knowledge
        )
        
        # Step 2: Fit mathematical models to the patterns
        trend_models = self._fit_trend_models(relevant_patterns, domain_knowledge)
        
        # Step 3: Analyze potential trend breaks
        break_analysis = self._analyze_trend_breaks(
            question, background, trend_models, time_horizon, cutoff_date
        )
        
        # Step 4: Perform extrapolation
        extrapolation = self._perform_extrapolation(
            trend_models, time_horizon, break_analysis, cutoff_date
        )
        
        # Step 5: Calculate confidence and uncertainty
        extrapolation = self._calculate_extrapolation_uncertainty(
            extrapolation, break_analysis, time_horizon
        )
        
        self.logger.log("trend_extrapolation", f"Extrapolation complete", {
            "predicted_value": extrapolation.predicted_value,
            "confidence": extrapolation.extrapolation_confidence,
            "model_type": extrapolation.model_used.trend_type.value
        })
        
        return extrapolation
    
    def _select_relevant_patterns(
        self,
        question: str,
        background: str,
        domain_knowledge: DiscoveredKnowledge
    ) -> Dict[str, Any]:
        """Select the most relevant patterns for extrapolation"""
        
        prompt = f"""
        Analyze this forecasting question and select the most relevant patterns for trend extrapolation:
        
        Question: {question}
        Background: {background}
        
        AVAILABLE SCALING LAWS:
        {json.dumps([{
            "domain": law.domain,
            "pattern": law.mathematical_form,
            "type": law.pattern_type,
            "confidence": law.confidence,
            "evidence": law.supporting_evidence[:2]
        } for law in domain_knowledge.scaling_laws], indent=2)}
        
        AVAILABLE TRENDS:
        {json.dumps([{
            "description": trend.trend_description,
            "direction": trend.direction,
            "strength": trend.strength,
            "confidence": trend.confidence,
            "examples": trend.supporting_examples[:2]
        } for trend in domain_knowledge.trends], indent=2)}
        
        Select the 1-3 most relevant patterns that could be used to extrapolate an answer to the question.
        Consider:
        1. **Direct relevance** to the question topic
        2. **Strength and reliability** of the pattern
        3. **Applicable time horizon**
        4. **Supporting evidence quality**
        
        For each selected pattern:
        - Explain why it's relevant
        - Assess its applicability to the question
        - Identify key parameters for extrapolation
        - Note any limitations or boundary conditions
        
        Format as JSON:
        {{
            "selected_patterns": [
                {{
                    "pattern_id": "scaling_law_0" or "trend_0",
                    "relevance_score": 0.XX,
                    "applicability": "explanation",
                    "key_parameters": ["param1", "param2"],
                    "limitations": ["limit1", "limit2"]
                }}
            ],
            "primary_pattern": "most_relevant_pattern_id",
            "extrapolation_approach": "how to combine patterns"
        }}
        """
        
        messages = [
            SystemMessage(content="You are an expert at pattern recognition and trend analysis."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {"selected_patterns": [], "primary_pattern": None}
    
    def _fit_trend_models(
        self,
        relevant_patterns: Dict[str, Any],
        domain_knowledge: DiscoveredKnowledge
    ) -> List[TrendModel]:
        """Fit mathematical models to the selected patterns"""
        
        trend_models = []
        
        for pattern_info in relevant_patterns.get("selected_patterns", []):
            pattern_id = pattern_info.get("pattern_id", "")
            
            if pattern_id.startswith("scaling_law_"):
                # Extract scaling law
                try:
                    idx = int(pattern_id.split("_")[-1])
                    scaling_law = domain_knowledge.scaling_laws[idx]
                    model = self._convert_scaling_law_to_model(scaling_law, pattern_info)
                    if model:
                        trend_models.append(model)
                except:
                    continue
            
            elif pattern_id.startswith("trend_"):
                # Extract trend
                try:
                    idx = int(pattern_id.split("_")[-1])
                    trend = domain_knowledge.trends[idx]
                    model = self._convert_trend_to_model(trend, pattern_info)
                    if model:
                        trend_models.append(model)
                except:
                    continue
        
        return trend_models
    
    def _convert_scaling_law_to_model(self, scaling_law: ScalingLaw, pattern_info: Dict) -> Optional[TrendModel]:
        """Convert a scaling law to a trend model"""
        
        # Map pattern types to trend types
        pattern_mapping = {
            "exponential": TrendType.EXPONENTIAL,
            "power_law": TrendType.POWER_LAW,
            "logistic": TrendType.LOGISTIC,
            "linear": TrendType.LINEAR
        }
        
        trend_type = pattern_mapping.get(scaling_law.pattern_type, TrendType.UNKNOWN)
        
        if trend_type == TrendType.UNKNOWN:
            return None
        
        # Extract parameters from the mathematical form
        parameters = scaling_law.parameters.copy()
        
        # Add relevance weighting
        parameters["relevance_weight"] = pattern_info.get("relevance_score", 0.5)
        
        return TrendModel(
            trend_type=trend_type,
            parameters=parameters,
            confidence=scaling_law.confidence * pattern_info.get("relevance_score", 0.5),
            applicable_range=(0.0, float('inf')),  # Default, could be refined
            saturation_point=None,  # Could be inferred from logistic models
            breakdown_conditions=scaling_law.exceptions
        )
    
    def _convert_trend_to_model(self, trend: DomainTrend, pattern_info: Dict) -> Optional[TrendModel]:
        """Convert a domain trend to a trend model"""
        
        # Infer trend type from direction and description
        trend_type = TrendType.LINEAR  # Default
        
        if "exponential" in trend.trend_description.lower():
            trend_type = TrendType.EXPONENTIAL
        elif "cyclical" in trend.trend_description.lower() or "cycle" in trend.trend_description.lower():
            trend_type = TrendType.CYCLICAL
        elif "logistic" in trend.trend_description.lower() or "s-curve" in trend.trend_description.lower():
            trend_type = TrendType.LOGISTIC
        elif "decay" in trend.trend_description.lower() or "declining" in trend.trend_description.lower():
            trend_type = TrendType.DECAY
        
        # Create parameters based on trend strength and direction
        parameters = {
            "strength": trend.strength,
            "direction_multiplier": 1.0 if trend.direction in ["increasing", "stable"] else -1.0,
            "base_rate": trend.base_rate or 0.5,
            "relevance_weight": pattern_info.get("relevance_score", 0.5)
        }
        
        return TrendModel(
            trend_type=trend_type,
            parameters=parameters,
            confidence=trend.confidence * pattern_info.get("relevance_score", 0.5),
            applicable_range=(0.0, 1.0),  # Assume probability range
            saturation_point=1.0 if trend.direction == "increasing" else 0.0,
            breakdown_conditions=[]
        )
    
    def _analyze_trend_breaks(
        self,
        question: str,
        background: str,
        trend_models: List[TrendModel],
        time_horizon: str,
        cutoff_date: Optional[datetime]
    ) -> TrendBreakAnalysis:
        """Analyze potential points where trends might break down"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        Analyze potential trend breaks for this forecasting question:
        
        Question: {question}
        Background: {background}
        Time Horizon: {time_horizon}
        Information cutoff: {cutoff_str}
        
        IDENTIFIED TREND MODELS:
        {json.dumps([{
            "type": model.trend_type.value,
            "confidence": model.confidence,
            "breakdown_conditions": model.breakdown_conditions
        } for model in trend_models], indent=2)}
        
        Analyze potential trend breaks:
        1. **Break Probability**: How likely is the trend to break or change significantly?
        2. **Break Timeframe**: When might trend breaks occur?
        3. **Break Triggers**: What events could cause trend breaks?
        4. **Alternative Scenarios**: What happens if trends break?
        
        Consider factors like:
        - Technological limits or saturation points
        - Economic cycles and disruptions
        - Regulatory changes or policy shifts
        - Competitive dynamics
        - Physical or natural constraints
        - Social acceptance and adoption limits
        
        Format as JSON:
        {{
            "break_probability": 0.XX,
            "break_timeframe": "short_term/medium_term/long_term",
            "break_triggers": ["trigger1", "trigger2"],
            "alternative_scenarios": [
                {{
                    "scenario": "description",
                    "probability": 0.XX,
                    "impact": "high/medium/low"
                }}
            ],
            "trend_stability": 0.XX
        }}
        """
        
        messages = [
            SystemMessage(content="You are an expert at analyzing trend stability and potential breaks."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            data = json.loads(response.content)
            return TrendBreakAnalysis(
                break_probability=data.get("break_probability", 0.3),
                break_timeframe=data.get("break_timeframe", "medium_term"),
                break_triggers=data.get("break_triggers", []),
                alternative_scenarios=data.get("alternative_scenarios", [])
            )
        except:
            return TrendBreakAnalysis(
                break_probability=0.3,
                break_timeframe="medium_term",
                break_triggers=["Unknown factors"],
                alternative_scenarios=[]
            )
    
    def _perform_extrapolation(
        self,
        trend_models: List[TrendModel],
        time_horizon: str,
        break_analysis: TrendBreakAnalysis,
        cutoff_date: Optional[datetime]
    ) -> ExtrapolationResult:
        """Perform the actual trend extrapolation"""
        
        if not trend_models:
            # No models available - return conservative estimate
            return ExtrapolationResult(
                predicted_value=0.5,
                confidence_interval=(0.2, 0.8),
                probability_ranges={"0.2-0.8": 1.0},
                model_used=TrendModel(
                    trend_type=TrendType.UNKNOWN,
                    parameters={},
                    confidence=0.1,
                    applicable_range=(0.0, 1.0),
                    saturation_point=None,
                    breakdown_conditions=[]
                ),
                assumptions=["No reliable trend models available"],
                risk_factors=["High uncertainty due to lack of trend data"],
                extrapolation_confidence=0.1
            )
        
        # Use the highest confidence model as primary
        primary_model = max(trend_models, key=lambda m: m.confidence)
        
        # Calculate time factor based on horizon
        time_factors = {
            "1 month": 1/12,
            "3 months": 0.25,
            "6 months": 0.5,
            "1 year": 1.0,
            "2 years": 2.0,
            "5 years": 5.0,
            "10 years": 10.0
        }
        
        # Extract time factor (default to 1 year)
        time_factor = 1.0
        for horizon_key, factor in time_factors.items():
            if horizon_key in time_horizon.lower():
                time_factor = factor
                break
        
        # Perform extrapolation based on model type
        predicted_value = self._extrapolate_with_model(primary_model, time_factor, break_analysis)
        
        # Calculate confidence interval
        base_uncertainty = 0.1 + (time_factor * 0.05)  # Uncertainty increases with time
        break_uncertainty = break_analysis.break_probability * 0.2
        model_uncertainty = (1 - primary_model.confidence) * 0.3
        
        total_uncertainty = min(base_uncertainty + break_uncertainty + model_uncertainty, 0.4)
        
        confidence_interval = (
            max(0.01, predicted_value - total_uncertainty),
            min(0.99, predicted_value + total_uncertainty)
        )
        
        # Generate probability ranges
        probability_ranges = self._generate_probability_ranges(predicted_value, total_uncertainty)
        
        return ExtrapolationResult(
            predicted_value=predicted_value,
            confidence_interval=confidence_interval,
            probability_ranges=probability_ranges,
            model_used=primary_model,
            assumptions=[f"Trend continues as modeled by {primary_model.trend_type.value}"],
            risk_factors=[f"Trend break probability: {break_analysis.break_probability:.1%}"],
            extrapolation_confidence=primary_model.confidence * (1 - break_analysis.break_probability)
        )
    
    def _extrapolate_with_model(
        self,
        model: TrendModel,
        time_factor: float,
        break_analysis: TrendBreakAnalysis
    ) -> float:
        """Extrapolate using a specific trend model"""
        
        base_rate = model.parameters.get("base_rate", 0.5)
        strength = model.parameters.get("strength", 0.5)
        direction_mult = model.parameters.get("direction_multiplier", 1.0)
        
        if model.trend_type == TrendType.LINEAR:
            # Linear extrapolation: base + (strength * direction * time)
            change = strength * direction_mult * time_factor * 0.1  # Scale factor
            predicted = base_rate + change
        
        elif model.trend_type == TrendType.EXPONENTIAL:
            # Exponential: base * (1 + growth_rate)^time
            growth_rate = model.parameters.get("growth_rate", strength * 0.1)
            predicted = base_rate * ((1 + growth_rate) ** time_factor)
        
        elif model.trend_type == TrendType.LOGISTIC:
            # Logistic curve: L / (1 + e^(-k*(t-t0)))
            L = model.parameters.get("carrying_capacity", 1.0)
            k = model.parameters.get("growth_rate", strength)
            t0 = model.parameters.get("midpoint", 0.0)
            predicted = L / (1 + math.exp(-k * (time_factor - t0)))
        
        elif model.trend_type == TrendType.POWER_LAW:
            # Power law: a * t^b
            a = model.parameters.get("coefficient", base_rate)
            b = model.parameters.get("exponent", strength)
            predicted = a * (time_factor ** b)
        
        elif model.trend_type == TrendType.DECAY:
            # Exponential decay: base * e^(-decay_rate * time)
            decay_rate = model.parameters.get("decay_rate", strength * 0.1)
            predicted = base_rate * math.exp(-decay_rate * time_factor)
        
        else:
            # Default to base rate for unknown models
            predicted = base_rate
        
        # Apply trend break adjustment
        break_adjustment = 1 - (break_analysis.break_probability * time_factor * 0.1)
        predicted *= break_adjustment
        
        # Ensure within valid range
        if model.applicable_range:
            min_val, max_val = model.applicable_range
            predicted = max(min_val, min(max_val, predicted))
        
        return max(0.01, min(0.99, predicted))  # Ensure in probability range
    
    def _generate_probability_ranges(self, predicted_value: float, uncertainty: float) -> Dict[str, float]:
        """Generate probability ranges around the prediction"""
        
        # Define ranges
        ranges = {
            "0.00-0.10": (0.00, 0.10),
            "0.10-0.25": (0.10, 0.25),
            "0.25-0.50": (0.25, 0.50),
            "0.50-0.75": (0.50, 0.75),
            "0.75-0.90": (0.75, 0.90),
            "0.90-1.00": (0.90, 1.00)
        }
        
        # Simple normal-like distribution around predicted value
        range_probs = {}
        total_prob = 0.0
        
        for range_name, (low, high) in ranges.items():
            # Calculate probability that prediction falls in this range
            if predicted_value >= low and predicted_value <= high:
                # Core range gets higher probability
                range_prob = 0.4 + (0.3 * (1 - uncertainty))
            else:
                # Distance-based probability with uncertainty
                mid_range = (low + high) / 2
                distance = abs(predicted_value - mid_range)
                range_prob = max(0.01, (1 - distance) * uncertainty)
            
            range_probs[range_name] = range_prob
            total_prob += range_prob
        
        # Normalize to sum to 1.0
        if total_prob > 0:
            for range_name in range_probs:
                range_probs[range_name] /= total_prob
        
        return range_probs
    
    def _calculate_extrapolation_uncertainty(
        self,
        extrapolation: ExtrapolationResult,
        break_analysis: TrendBreakAnalysis,
        time_horizon: str
    ) -> ExtrapolationResult:
        """Calculate and adjust uncertainty in the extrapolation"""
        
        # Base confidence from model
        base_confidence = extrapolation.model_used.confidence
        
        # Reduce confidence based on time horizon
        time_penalty = 0.0
        if "year" in time_horizon:
            time_penalty = 0.1
        if "2 year" in time_horizon or "5 year" in time_horizon:
            time_penalty = 0.2
        if "10 year" in time_horizon:
            time_penalty = 0.3
        
        # Reduce confidence based on break probability
        break_penalty = break_analysis.break_probability * 0.3
        
        # Final confidence
        final_confidence = max(0.1, base_confidence - time_penalty - break_penalty)
        
        # Update extrapolation
        extrapolation.extrapolation_confidence = final_confidence
        
        # Widen confidence interval if low confidence
        if final_confidence < 0.5:
            lower, upper = extrapolation.confidence_interval
            center = (lower + upper) / 2
            width = (upper - lower) * (1.5 - final_confidence)  # Widen interval
            extrapolation.confidence_interval = (
                max(0.01, center - width/2),
                min(0.99, center + width/2)
            )
        
        return extrapolation
