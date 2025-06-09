"""
Superforecaster Agent - Implements advanced forecasting methodologies
Based on research from Philip Tetlock's "Superforecasting" and best practices
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from langchain.schema import HumanMessage, SystemMessage
from ..utils.llm_client import LLMClient
from ..utils.agent_logger import agent_logger


@dataclass
class ForecastingEvidence:
    """Structure for organizing forecasting evidence"""
    source: str
    content: str
    reliability_score: float
    date: datetime
    relevance_score: float
    evidence_type: str  # "base_rate", "trend", "expert_opinion", "leading_indicator", etc.


@dataclass
class BaseRateAnalysis:
    """Base rate analysis for reference class forecasting"""
    reference_class: str
    historical_frequency: float
    sample_size: int
    time_period: str
    adjustments: List[str]
    confidence: float


class SuperforecasterAgent:
    """
    Advanced forecasting agent that implements superforecaster methodologies:
    1. Reference class forecasting
    2. Multiple perspective analysis
    3. Base rate consideration
    4. Systematic evidence evaluation
    5. Uncertainty quantification
    6. Temporal decomposition
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = (llm_client or LLMClient()).get_client()
        self.logger = agent_logger
        
    def forecast_with_superforecaster_methodology(
        self, 
        question: str, 
        background: str = "",
        cutoff_date: Optional[datetime] = None,
        time_horizon: str = "1 year"
    ) -> Dict[str, Any]:
        """
        Main forecasting method using superforecaster techniques
        """
        
        self.logger.info(f"🧠 Starting superforecaster analysis for: {question}")
        
        # Step 1: Question decomposition and clarification
        decomposition = self._decompose_question(question, background)
        
        # Step 2: Reference class forecasting
        base_rates = self._analyze_base_rates(question, background, cutoff_date)
        
        # Step 3: Gather and evaluate evidence
        evidence = self._gather_systematic_evidence(question, background, cutoff_date)
        
        # Step 4: Multiple perspective analysis
        perspectives = self._analyze_multiple_perspectives(question, evidence, cutoff_date)
        
        # Step 5: Trend analysis and leading indicators
        trends = self._analyze_trends_and_indicators(question, evidence, cutoff_date)
        
        # Step 6: Expert opinion synthesis
        expert_synthesis = self._synthesize_expert_opinions(question, evidence, cutoff_date)
        
        # Step 7: Uncertainty quantification
        uncertainties = self._quantify_uncertainties(question, evidence)
        
        # Step 8: Final probability synthesis
        final_forecast = self._synthesize_final_forecast(
            question, decomposition, base_rates, evidence, 
            perspectives, trends, expert_synthesis, uncertainties
        )
        
        return {
            "question": question,
            "methodology": "superforecaster",
            "decomposition": decomposition,
            "base_rates": base_rates,
            "evidence_summary": self._summarize_evidence(evidence),
            "perspectives": perspectives,
            "trends": trends,
            "expert_synthesis": expert_synthesis,
            "uncertainties": uncertainties,
            "final_forecast": final_forecast,
            "confidence_level": final_forecast.get("confidence", "medium"),
            "reasoning_chain": final_forecast.get("reasoning", ""),
            "probability": final_forecast.get("probability", 0.5)
        }
    
    def _decompose_question(self, question: str, background: str) -> Dict[str, Any]:
        """Decompose complex questions into manageable components"""
        
        prompt = f"""
        As a superforecaster, decompose this forecasting question into its key components:
        
        Question: {question}
        Background: {background}
        
        Provide:
        1. Core event being predicted
        2. Key conditions that must be met
        3. Potential ambiguities in the question
        4. Time constraints and deadlines
        5. Success criteria and resolution conditions
        6. Sub-questions that could inform the main question
        
        Format as JSON with clear structure.
        """
        
        messages = [
            SystemMessage(content="You are an expert superforecaster skilled at question decomposition."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "core_event": question,
                "conditions": [],
                "ambiguities": [],
                "time_constraints": [],
                "success_criteria": [],
                "sub_questions": []
            }
    
    def _analyze_base_rates(self, question: str, background: str, cutoff_date: Optional[datetime]) -> BaseRateAnalysis:
        """Perform reference class forecasting to establish base rates"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        As a superforecaster, identify the reference class and base rates for this question:
        
        Question: {question}
        Background: {background}
        Information cutoff: {cutoff_str}
        
        Analyze:
        1. What is the most appropriate reference class? (similar events/situations)
        2. What is the historical frequency of such events?
        3. How many examples are in your reference class?
        4. What time period does this cover?
        5. What adjustments should be made for current context?
        6. How confident are you in this base rate?
        
        Provide specific numbers and reasoning. Be conservative and cite historical precedents.
        
        Format as JSON:
        {{
            "reference_class": "description",
            "historical_frequency": 0.XX,
            "sample_size": number,
            "time_period": "description",
            "adjustments": ["reason1", "reason2"],
            "confidence": 0.XX,
            "reasoning": "detailed explanation"
        }}
        """
        
        messages = [
            SystemMessage(content="You are an expert at reference class forecasting and base rate analysis."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            data = json.loads(response.content)
            return BaseRateAnalysis(
                reference_class=data.get("reference_class", "Unknown"),
                historical_frequency=data.get("historical_frequency", 0.5),
                sample_size=data.get("sample_size", 0),
                time_period=data.get("time_period", "Unknown"),
                adjustments=data.get("adjustments", []),
                confidence=data.get("confidence", 0.5)
            )
        except:
            return BaseRateAnalysis(
                reference_class="Unknown",
                historical_frequency=0.5,
                sample_size=0,
                time_period="Unknown",
                adjustments=[],
                confidence=0.3
            )
    
    def _gather_systematic_evidence(
        self, 
        question: str, 
        background: str, 
        cutoff_date: Optional[datetime]
    ) -> List[ForecastingEvidence]:
        """Systematically gather and categorize evidence"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        As a superforecaster, systematically gather evidence for this question:
        
        Question: {question}
        Background: {background}
        Information cutoff: {cutoff_str}
        
        Identify and categorize evidence into:
        1. Base rates and historical precedents
        2. Current trends and momentum
        3. Leading indicators and early signals
        4. Expert opinions and predictions
        5. Structural factors and constraints
        6. Recent developments and news
        
        For each piece of evidence, assess:
        - Reliability (0-1 scale)
        - Relevance (0-1 scale)
        - Recency and timeliness
        - Source credibility
        
        Focus on evidence available before {cutoff_str}.
        
        Format as JSON array of evidence items.
        """
        
        messages = [
            SystemMessage(content="You are an expert at systematic evidence gathering for forecasting."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        evidence_list = []
        try:
            data = json.loads(response.content)
            if isinstance(data, list):
                for item in data:
                    evidence_list.append(ForecastingEvidence(
                        source=item.get("source", "Unknown"),
                        content=item.get("content", ""),
                        reliability_score=item.get("reliability", 0.5),
                        date=datetime.now(),  # Simplified for now
                        relevance_score=item.get("relevance", 0.5),
                        evidence_type=item.get("type", "general")
                    ))
        except:
            pass
        
        return evidence_list
    
    def _analyze_multiple_perspectives(
        self, 
        question: str, 
        evidence: List[ForecastingEvidence], 
        cutoff_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Analyze the question from multiple perspectives"""
        
        prompt = f"""
        As a superforecaster, analyze this question from multiple perspectives:
        
        Question: {question}
        
        Provide analysis from these viewpoints:
        1. Optimistic scenario (what could make this more likely?)
        2. Pessimistic scenario (what could prevent this?)
        3. Status quo scenario (what if current trends continue?)
        4. Black swan scenario (what unexpected events could matter?)
        5. Institutional perspective (how do organizations/systems affect this?)
        6. Individual actor perspective (how do key people affect this?)
        
        For each perspective:
        - Probability estimate
        - Key factors
        - Confidence level
        
        Format as JSON with structured analysis.
        """
        
        messages = [
            SystemMessage(content="You are an expert at multi-perspective analysis for forecasting."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "optimistic": {"probability": 0.7, "factors": [], "confidence": 0.5},
                "pessimistic": {"probability": 0.3, "factors": [], "confidence": 0.5},
                "status_quo": {"probability": 0.5, "factors": [], "confidence": 0.5},
                "black_swan": {"probability": 0.1, "factors": [], "confidence": 0.3},
                "institutional": {"probability": 0.5, "factors": [], "confidence": 0.5},
                "individual": {"probability": 0.5, "factors": [], "confidence": 0.5}
            }
    
    def _analyze_trends_and_indicators(
        self, 
        question: str, 
        evidence: List[ForecastingEvidence], 
        cutoff_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Analyze trends and leading indicators"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        As a superforecaster, analyze trends and leading indicators for this question:
        
        Question: {question}
        Information cutoff: {cutoff_str}
        
        Identify:
        1. Current trends (direction and momentum)
        2. Leading indicators (early signals of change)
        3. Lagging indicators (confirmatory signals)
        4. Trend reversals or inflection points
        5. Cyclical patterns
        6. Acceleration or deceleration factors
        
        For each trend/indicator:
        - Current status
        - Direction (positive/negative for the outcome)
        - Strength/reliability
        - Time horizon for impact
        
        Focus on quantifiable metrics where possible.
        
        Format as JSON with structured analysis.
        """
        
        messages = [
            SystemMessage(content="You are an expert at trend analysis and leading indicators for forecasting."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "current_trends": [],
                "leading_indicators": [],
                "lagging_indicators": [],
                "trend_reversals": [],
                "cyclical_patterns": [],
                "acceleration_factors": []
            }
    
    def _synthesize_expert_opinions(
        self, 
        question: str, 
        evidence: List[ForecastingEvidence], 
        cutoff_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Synthesize expert opinions and predictions"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        As a superforecaster, synthesize expert opinions on this question:
        
        Question: {question}
        Information cutoff: {cutoff_str}
        
        Consider:
        1. Domain expert predictions and forecasts
        2. Institutional forecasts (government, think tanks, etc.)
        3. Market-based predictions (betting markets, prediction markets)
        4. Academic research and studies
        5. Track record of different expert sources
        6. Consensus vs. contrarian views
        
        Analyze:
        - Range of expert predictions
        - Confidence levels expressed
        - Reasoning provided by experts
        - Track record and credibility
        - Potential biases or conflicts of interest
        
        Synthesize into a coherent assessment of expert opinion.
        
        Format as JSON with structured analysis.
        """
        
        messages = [
            SystemMessage(content="You are an expert at synthesizing expert opinions for forecasting."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "expert_range": {"min": 0.2, "max": 0.8, "median": 0.5},
                "consensus_view": 0.5,
                "contrarian_views": [],
                "high_credibility_sources": [],
                "market_predictions": {},
                "academic_consensus": 0.5
            }
    
    def _quantify_uncertainties(self, question: str, evidence: List[ForecastingEvidence]) -> Dict[str, Any]:
        """Quantify key uncertainties and their impact"""
        
        prompt = f"""
        As a superforecaster, identify and quantify key uncertainties for this question:
        
        Question: {question}
        
        Identify:
        1. Epistemic uncertainties (things we could know but don't)
        2. Aleatory uncertainties (inherent randomness)
        3. Model uncertainties (assumptions that could be wrong)
        4. Parameter uncertainties (imprecise estimates)
        5. Scenario uncertainties (different possible futures)
        
        For each uncertainty:
        - Description
        - Impact on forecast (high/medium/low)
        - Reducibility (can more info help?)
        - Time sensitivity (when will we know more?)
        
        Provide confidence intervals and sensitivity analysis.
        
        Format as JSON with structured analysis.
        """
        
        messages = [
            SystemMessage(content="You are an expert at uncertainty quantification for forecasting."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "epistemic_uncertainties": [],
                "aleatory_uncertainties": [],
                "model_uncertainties": [],
                "parameter_uncertainties": [],
                "scenario_uncertainties": [],
                "confidence_interval": [0.3, 0.7],
                "key_assumptions": []
            }
    
    def _synthesize_final_forecast(
        self,
        question: str,
        decomposition: Dict[str, Any],
        base_rates: BaseRateAnalysis,
        evidence: List[ForecastingEvidence],
        perspectives: Dict[str, Any],
        trends: Dict[str, Any],
        expert_synthesis: Dict[str, Any],
        uncertainties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize all analysis into final forecast"""
        
        prompt = f"""
        As a superforecaster, synthesize all analysis into a final forecast:
        
        Question: {question}
        
        Analysis Summary:
        - Base rate: {base_rates.historical_frequency:.3f} (confidence: {base_rates.confidence:.3f})
        - Reference class: {base_rates.reference_class}
        - Expert consensus: {expert_synthesis.get('consensus_view', 0.5):.3f}
        - Perspective range: {perspectives.get('optimistic', {}).get('probability', 0.7):.3f} to {perspectives.get('pessimistic', {}).get('probability', 0.3):.3f}
        
        Synthesize using superforecaster principles:
        1. Start with base rate as anchor
        2. Adjust based on specific evidence
        3. Consider multiple perspectives
        4. Weight evidence by reliability
        5. Account for uncertainties
        6. Avoid overconfidence
        7. Express appropriate confidence intervals
        
        Provide:
        - Final probability estimate
        - Confidence level (high/medium/low)
        - Key reasoning chain
        - Main factors driving the forecast
        - Confidence interval
        - Conditions that could change the forecast
        
        Be precise and well-calibrated. Explain your reasoning clearly.
        
        Format as JSON with structured output.
        """
        
        messages = [
            SystemMessage(content="You are an expert superforecaster synthesizing a final prediction."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            result = json.loads(response.content)
            # Ensure probability is within valid range
            prob = max(0.01, min(0.99, result.get("probability", 0.5)))
            result["probability"] = prob
            return result
        except:
            return {
                "probability": base_rates.historical_frequency,
                "confidence": "medium",
                "reasoning": "Based primarily on base rate analysis",
                "key_factors": ["Historical precedent"],
                "confidence_interval": [0.3, 0.7],
                "conditions_for_change": []
            }
    
    def _summarize_evidence(self, evidence: List[ForecastingEvidence]) -> Dict[str, Any]:
        """Summarize evidence for reporting"""
        
        if not evidence:
            return {"total_pieces": 0, "average_reliability": 0, "evidence_types": []}
        
        total_pieces = len(evidence)
        avg_reliability = sum(e.reliability_score for e in evidence) / total_pieces
        evidence_types = list(set(e.evidence_type for e in evidence))
        
        return {
            "total_pieces": total_pieces,
            "average_reliability": avg_reliability,
            "evidence_types": evidence_types,
            "high_reliability_count": sum(1 for e in evidence if e.reliability_score > 0.7)
        }