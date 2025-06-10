"""
Dynamic Domain Knowledge Discovery System for AI Forecasting

This module implements a dynamic system that automatically discovers relevant:
- Scaling laws and growth patterns
- Domain-specific trends and patterns
- Base rates and historical precedents
- Expert consensus patterns
- Mathematical models and extrapolation frameworks

Replacing hard-coded domain knowledge with adaptive discovery.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from langchain.schema import HumanMessage, SystemMessage
from ..utils.llm_client import LLMClient
from ..utils.agent_logger import agent_logger


class DomainType(Enum):
    """Types of domains for forecasting questions"""
    TECHNOLOGY = "technology"
    ECONOMICS = "economics"
    CLIMATE = "climate"
    GEOPOLITICS = "geopolitics"
    SPORTS = "sports"
    PUBLISHING = "publishing"
    HEALTHCARE = "healthcare"
    BUSINESS = "business"
    SCIENTIFIC = "scientific"
    SOCIAL = "social"
    UNKNOWN = "unknown"


@dataclass
class ScalingLaw:
    """Represents a discovered scaling law or growth pattern"""
    domain: str
    pattern_type: str  # exponential, power_law, logistic, linear, etc.
    mathematical_form: str
    parameters: Dict[str, float]
    confidence: float
    supporting_evidence: List[str]
    time_range: str
    exceptions: List[str]


@dataclass
class DomainTrend:
    """Represents a discovered domain-specific trend"""
    domain: str
    trend_description: str
    direction: str  # increasing, decreasing, cyclical, stable
    strength: float  # 0-1
    time_horizon: str
    supporting_examples: List[str]
    base_rate: Optional[float]
    confidence: float


@dataclass
class ExpertConsensusPattern:
    """Represents discovered expert consensus patterns"""
    domain: str
    consensus_type: str
    accuracy_pattern: str  # conservative, optimistic, accurate, volatile
    typical_bias: str
    track_record: Dict[str, float]
    confidence: float


@dataclass
class DiscoveredKnowledge:
    """Container for all discovered domain knowledge"""
    domain_type: DomainType
    scaling_laws: List[ScalingLaw]
    trends: List[DomainTrend]
    expert_patterns: List[ExpertConsensusPattern]
    base_rates: Dict[str, float]
    mathematical_models: List[str]
    discovery_confidence: float
    discovery_timestamp: datetime


class DynamicDomainKnowledgeDiscovery:
    """
    Dynamic system for discovering domain-specific knowledge for forecasting
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        self.logger = agent_logger
        self.knowledge_cache = {}  # Cache discovered knowledge
        
    def discover_domain_knowledge(
        self, 
        question: str, 
        background: str = "",
        cutoff_date: Optional[datetime] = None
    ) -> DiscoveredKnowledge:
        """
        Main method to discover all relevant domain knowledge for a forecasting question
        """
        
        self.logger.log("domain_discovery", f"Starting domain knowledge discovery for: {question[:100]}...")
        
        # Step 1: Classify the domain
        domain_type = self._classify_domain(question, background)
        
        # Step 2: Discover scaling laws and growth patterns
        scaling_laws = self._discover_scaling_laws(question, background, domain_type, cutoff_date)
        
        # Step 3: Identify domain-specific trends
        trends = self._discover_domain_trends(question, background, domain_type, cutoff_date)
        
        # Step 4: Find expert consensus patterns
        expert_patterns = self._discover_expert_patterns(question, background, domain_type, cutoff_date)
        
        # Step 5: Calculate domain-specific base rates
        base_rates = self._discover_base_rates(question, background, domain_type, cutoff_date)
        
        # Step 6: Identify applicable mathematical models
        mathematical_models = self._discover_mathematical_models(question, background, domain_type, cutoff_date)
        
        # Step 7: Calculate overall discovery confidence
        discovery_confidence = self._calculate_discovery_confidence(
            scaling_laws, trends, expert_patterns, base_rates
        )
        
        discovered_knowledge = DiscoveredKnowledge(
            domain_type=domain_type,
            scaling_laws=scaling_laws,
            trends=trends,
            expert_patterns=expert_patterns,
            base_rates=base_rates,
            mathematical_models=mathematical_models,
            discovery_confidence=discovery_confidence,
            discovery_timestamp=datetime.now()
        )
        
        self.logger.log("domain_discovery", f"Discovery complete. Found {len(scaling_laws)} scaling laws, {len(trends)} trends", {
            "domain": domain_type.value,
            "confidence": discovery_confidence,
            "scaling_laws": len(scaling_laws),
            "trends": len(trends)
        })
        
        return discovered_knowledge
    
    def _classify_domain(self, question: str, background: str) -> DomainType:
        """Classify the domain of the forecasting question"""
        
        prompt = f"""
        Classify the primary domain of this forecasting question:
        
        Question: {question}
        Background: {background}
        
        Choose the most appropriate domain from:
        - technology (AI, software, hardware, digital innovation)
        - economics (markets, business, finance, trade)
        - climate (environment, weather, climate change)
        - geopolitics (international relations, conflicts, diplomacy)
        - sports (athletic events, competitions, records)
        - publishing (books, media, content creation)
        - healthcare (medicine, public health, pharmaceuticals)
        - business (companies, industries, management)
        - scientific (research, discoveries, academic progress)
        - social (society, culture, demographics)
        - unknown (if unclear or mixed domain)
        
        Consider:
        1. What field does this question primarily relate to?
        2. What type of expertise would be most relevant?
        3. What historical patterns would be most applicable?
        
        Return only the domain name (lowercase).
        """
        
        messages = [
            SystemMessage(content="You are an expert at domain classification for forecasting."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        domain_str = response.content.strip().lower()
        
        # Map to enum
        domain_mapping = {
            "technology": DomainType.TECHNOLOGY,
            "economics": DomainType.ECONOMICS,
            "climate": DomainType.CLIMATE,
            "geopolitics": DomainType.GEOPOLITICS,
            "sports": DomainType.SPORTS,
            "publishing": DomainType.PUBLISHING,
            "healthcare": DomainType.HEALTHCARE,
            "business": DomainType.BUSINESS,
            "scientific": DomainType.SCIENTIFIC,
            "social": DomainType.SOCIAL
        }
        
        return domain_mapping.get(domain_str, DomainType.UNKNOWN)
    
    def _discover_scaling_laws(
        self, 
        question: str, 
        background: str, 
        domain: DomainType, 
        cutoff_date: Optional[datetime]
    ) -> List[ScalingLaw]:
        """Discover relevant scaling laws and growth patterns"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        Identify relevant scaling laws and growth patterns for this forecasting question:
        
        Question: {question}
        Background: {background}
        Domain: {domain.value}
        Information cutoff: {cutoff_str}
        
        Search for patterns like:
        1. **Technology Domain**: Moore's Law, Wright's Law, scaling laws for AI, adoption curves
        2. **Economics Domain**: Pareto distributions, power laws in wealth, network effects
        3. **Climate Domain**: Temperature trends, feedback loops, emission patterns
        4. **Scientific Domain**: Citation growth, research productivity patterns
        5. **Business Domain**: Market penetration curves, company growth patterns
        
        For each scaling law or pattern:
        - Mathematical form (exponential, power law, logistic, etc.)
        - Key parameters and rates
        - Historical time range where it applies
        - Confidence in applicability
        - Supporting evidence and examples
        - Known exceptions or breakdown points
        
        Focus on patterns that could help extrapolate trends relevant to the question.
        Information must be available before {cutoff_str}.
        
        Format as JSON array of scaling laws:
        [{{
            "domain": "specific_subdomain",
            "pattern_type": "exponential/power_law/logistic/linear/cyclical",
            "mathematical_form": "y = a * x^b or similar",
            "parameters": {{"growth_rate": 0.XX, "doubling_time": XX}},
            "confidence": 0.XX,
            "supporting_evidence": ["example1", "example2"],
            "time_range": "YYYY-YYYY",
            "exceptions": ["when it breaks down"]
        }}]
        """
        
        messages = [
            SystemMessage(content="You are an expert at identifying scaling laws and growth patterns."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            data = json.loads(response.content)
            scaling_laws = []
            for item in data:
                scaling_laws.append(ScalingLaw(
                    domain=item.get("domain", domain.value),
                    pattern_type=item.get("pattern_type", "unknown"),
                    mathematical_form=item.get("mathematical_form", ""),
                    parameters=item.get("parameters", {}),
                    confidence=item.get("confidence", 0.5),
                    supporting_evidence=item.get("supporting_evidence", []),
                    time_range=item.get("time_range", ""),
                    exceptions=item.get("exceptions", [])
                ))
            return scaling_laws
        except:
            return []
    
    def _discover_domain_trends(
        self, 
        question: str, 
        background: str, 
        domain: DomainType, 
        cutoff_date: Optional[datetime]
    ) -> List[DomainTrend]:
        """Discover domain-specific trends and patterns"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        Identify relevant domain-specific trends for this forecasting question:
        
        Question: {question}
        Background: {background}
        Domain: {domain.value}
        Information cutoff: {cutoff_str}
        
        Look for trends such as:
        1. **Technology**: Capability improvements, adoption rates, performance metrics
        2. **Economics**: Market growth, sector development, economic indicators
        3. **Climate**: Temperature trends, extreme events, policy responses
        4. **Geopolitics**: Diplomatic patterns, conflict cycles, alliance shifts
        5. **Business**: Industry evolution, competitive dynamics, innovation cycles
        
        For each trend:
        - Clear description of the trend
        - Direction (increasing/decreasing/cyclical/stable)
        - Strength and consistency (0-1 scale)
        - Typical time horizon for manifestation
        - Supporting examples and evidence
        - Estimated base rate if applicable
        - Confidence in trend continuation
        
        Focus on trends that could impact the forecasting question.
        Information must be available before {cutoff_str}.
        
        Format as JSON array:
        [{{
            "domain": "specific_subdomain",
            "trend_description": "clear description",
            "direction": "increasing/decreasing/cyclical/stable",
            "strength": 0.XX,
            "time_horizon": "months/years/decades",
            "supporting_examples": ["example1", "example2"],
            "base_rate": 0.XX,
            "confidence": 0.XX
        }}]
        """
        
        messages = [
            SystemMessage(content="You are an expert at identifying domain-specific trends."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            data = json.loads(response.content)
            trends = []
            for item in data:
                trends.append(DomainTrend(
                    domain=item.get("domain", domain.value),
                    trend_description=item.get("trend_description", ""),
                    direction=item.get("direction", "stable"),
                    strength=item.get("strength", 0.5),
                    time_horizon=item.get("time_horizon", ""),
                    supporting_examples=item.get("supporting_examples", []),
                    base_rate=item.get("base_rate"),
                    confidence=item.get("confidence", 0.5)
                ))
            return trends
        except:
            return []
    
    def _discover_expert_patterns(
        self, 
        question: str, 
        background: str, 
        domain: DomainType, 
        cutoff_date: Optional[datetime]
    ) -> List[ExpertConsensusPattern]:
        """Discover patterns in expert consensus and accuracy"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        Identify expert consensus patterns relevant to this forecasting question:
        
        Question: {question}
        Background: {background}
        Domain: {domain.value}
        Information cutoff: {cutoff_str}
        
        Analyze how experts in this domain typically perform:
        1. **Consensus Patterns**: Do experts usually agree or disagree?
        2. **Accuracy Patterns**: Are they conservative, optimistic, or well-calibrated?
        3. **Bias Patterns**: Common systematic biases in predictions
        4. **Track Record**: Historical accuracy in similar questions
        
        Consider domain-specific expert behavior:
        - **Technology**: Often underestimate adoption speed, focus on technical barriers
        - **Economics**: Mixed track record, sensitive to cycles and shocks
        - **Climate**: Tend to be conservative, high confidence in directional trends
        - **Business**: Often optimistic about growth, underestimate disruption
        
        For each expert pattern:
        - Type of consensus (strong/weak/divided)
        - Accuracy pattern (conservative/optimistic/accurate)
        - Typical bias direction
        - Track record metrics
        - Confidence in pattern
        
        Information must be available before {cutoff_str}.
        
        Format as JSON array:
        [{{
            "domain": "specific_subdomain",
            "consensus_type": "strong/weak/divided",
            "accuracy_pattern": "conservative/optimistic/accurate/volatile",
            "typical_bias": "description of bias",
            "track_record": {{"accuracy": 0.XX, "calibration": 0.XX}},
            "confidence": 0.XX
        }}]
        """
        
        messages = [
            SystemMessage(content="You are an expert at analyzing expert consensus patterns."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            data = json.loads(response.content)
            patterns = []
            for item in data:
                patterns.append(ExpertConsensusPattern(
                    domain=item.get("domain", domain.value),
                    consensus_type=item.get("consensus_type", "unknown"),
                    accuracy_pattern=item.get("accuracy_pattern", "unknown"),
                    typical_bias=item.get("typical_bias", ""),
                    track_record=item.get("track_record", {}),
                    confidence=item.get("confidence", 0.5)
                ))
            return patterns
        except:
            return []
    
    def _discover_base_rates(
        self, 
        question: str, 
        background: str, 
        domain: DomainType, 
        cutoff_date: Optional[datetime]
    ) -> Dict[str, float]:
        """Discover relevant base rates for the domain"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        Calculate relevant base rates for this forecasting question:
        
        Question: {question}
        Background: {background}
        Domain: {domain.value}
        Information cutoff: {cutoff_str}
        
        Find appropriate reference classes and calculate base rates:
        1. **Direct Reference Class**: Similar events/achievements in this exact domain
        2. **Analogous Reference Class**: Similar events in related domains
        3. **General Reference Class**: Broader category of achievements/events
        
        For each reference class:
        - Historical frequency of success
        - Sample size
        - Time period
        - Adjustments for current context
        
        Consider domain-specific base rates:
        - **Technology**: Product launches, capability milestones, adoption rates
        - **Economics**: Market predictions, recession frequencies, growth targets
        - **Climate**: Extreme events, policy implementations, temperature targets
        - **Business**: Project success, market disruptions, company survivability
        
        Information must be available before {cutoff_str}.
        
        Format as JSON object:
        {{
            "primary_reference_class": 0.XX,
            "analogous_reference_class": 0.XX,
            "general_reference_class": 0.XX,
            "domain_specific_base_rate": 0.XX,
            "adjusted_base_rate": 0.XX
        }}
        """
        
        messages = [
            SystemMessage(content="You are an expert at calculating base rates for forecasting."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {"adjusted_base_rate": 0.5}
    
    def _discover_mathematical_models(
        self, 
        question: str, 
        background: str, 
        domain: DomainType, 
        cutoff_date: Optional[datetime]
    ) -> List[str]:
        """Discover applicable mathematical models for extrapolation"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        Identify mathematical models applicable to this forecasting question:
        
        Question: {question}
        Background: {background}
        Domain: {domain.value}
        Information cutoff: {cutoff_str}
        
        Consider models like:
        1. **Growth Models**: Exponential, logistic, power law, S-curves
        2. **Diffusion Models**: Bass diffusion, Rogers adoption curves
        3. **Network Models**: Metcalfe's law, network effects
        4. **Economic Models**: Supply/demand, elasticity, market dynamics
        5. **Physical Models**: Scaling laws, thermodynamic limits
        6. **Statistical Models**: Regression, time series, probability distributions
        
        For each model:
        - Model name and type
        - Applicability to the question
        - Key parameters needed
        - Historical performance
        - Limitations and assumptions
        
        Information must be available before {cutoff_str}.
        
        Return as JSON array of model names/descriptions.
        """
        
        messages = [
            SystemMessage(content="You are an expert at mathematical modeling for forecasting."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            data = json.loads(response.content)
            if isinstance(data, list):
                return data
            return []
        except:
            return []
    
    def _calculate_discovery_confidence(
        self, 
        scaling_laws: List[ScalingLaw], 
        trends: List[DomainTrend], 
        expert_patterns: List[ExpertConsensusPattern], 
        base_rates: Dict[str, float]
    ) -> float:
        """Calculate overall confidence in the discovered knowledge"""
        
        # Base confidence from number of discovered elements
        elements_found = len(scaling_laws) + len(trends) + len(expert_patterns) + len(base_rates)
        quantity_confidence = min(elements_found / 10.0, 1.0)  # Normalize to 0-1
        
        # Quality confidence from individual confidences
        all_confidences = []
        all_confidences.extend([law.confidence for law in scaling_laws])
        all_confidences.extend([trend.confidence for trend in trends])
        all_confidences.extend([pattern.confidence for pattern in expert_patterns])
        
        quality_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.5
        
        # Combined confidence
        return (quantity_confidence * 0.3 + quality_confidence * 0.7)
    
    def generate_dynamic_domain_context(self, discovered_knowledge: DiscoveredKnowledge) -> str:
        """Generate dynamic domain context to replace hard-coded knowledge"""
        
        domain_context = f"""
DYNAMICALLY DISCOVERED DOMAIN KNOWLEDGE ({discovered_knowledge.domain_type.value.upper()}):

**SCALING LAWS & GROWTH PATTERNS:**
"""
        
        for law in discovered_knowledge.scaling_laws:
            domain_context += f"""
- {law.domain}: {law.mathematical_form} ({law.pattern_type})
  Evidence: {', '.join(law.supporting_evidence[:3])}
  Confidence: {law.confidence:.2f}
"""
        
        domain_context += f"""
**DOMAIN-SPECIFIC TRENDS:**
"""
        
        for trend in discovered_knowledge.trends:
            base_rate_str = f" (Base rate: {trend.base_rate:.1%})" if trend.base_rate else ""
            domain_context += f"""
- {trend.trend_description} ({trend.direction})
  Strength: {trend.strength:.2f}, Horizon: {trend.time_horizon}{base_rate_str}
"""
        
        domain_context += f"""
**EXPERT CONSENSUS PATTERNS:**
"""
        
        for pattern in discovered_knowledge.expert_patterns:
            domain_context += f"""
- {pattern.domain}: {pattern.accuracy_pattern} bias, {pattern.consensus_type} consensus
  Pattern: {pattern.typical_bias}
"""
        
        domain_context += f"""
**BASE RATES:**
"""
        
        for rate_type, rate_value in discovered_knowledge.base_rates.items():
            domain_context += f"""
- {rate_type.replace('_', ' ').title()}: {rate_value:.1%}
"""
        
        domain_context += f"""
**APPLICABLE MODELS:**
{', '.join(discovered_knowledge.mathematical_models)}

**DISCOVERY CONFIDENCE:** {discovered_knowledge.discovery_confidence:.2f}
**DISCOVERED AT:** {discovered_knowledge.discovery_timestamp.strftime('%Y-%m-%d %H:%M')}

Use this discovered knowledge to inform forecasting instead of relying on pre-programmed assumptions.
Adapt your reasoning to the specific patterns and trends identified for this domain.
"""
        
        return domain_context
