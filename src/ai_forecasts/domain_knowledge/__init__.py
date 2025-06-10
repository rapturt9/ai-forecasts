"""
Domain Knowledge Discovery Module for AI Forecasting System
"""

from .dynamic_discovery import (
    DynamicDomainKnowledgeDiscovery,
    DiscoveredKnowledge,
    DomainType,
    ScalingLaw,
    DomainTrend,
    ExpertConsensusPattern
)

from .adaptive_search import (
    DomainAdaptiveSearchStrategy,
    SearchQuery,
    SearchStrategy
)

from .trend_extrapolation import (
    TrendExtrapolationEngine,
    TrendModel,
    ExtrapolationResult,
    TrendBreakAnalysis,
    TrendType
)

__all__ = [
    "DynamicDomainKnowledgeDiscovery",
    "DiscoveredKnowledge", 
    "DomainType",
    "ScalingLaw",
    "DomainTrend",
    "ExpertConsensusPattern",
    "DomainAdaptiveSearchStrategy",
    "SearchQuery", 
    "SearchStrategy",
    "TrendExtrapolationEngine",
    "TrendModel",
    "ExtrapolationResult",
    "TrendBreakAnalysis",
    "TrendType"
]
