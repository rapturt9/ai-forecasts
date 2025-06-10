"""
Domain-Adaptive Search Strategy System

This module implements intelligent search strategies that adapt to the domain
and question type to find the most relevant information for forecasting.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from langchain.schema import HumanMessage, SystemMessage
from ..utils.llm_client import LLMClient
from ..utils.agent_logger import agent_logger
from .dynamic_discovery import DomainType, DiscoveredKnowledge


@dataclass
class SearchQuery:
    """Represents an optimized search query"""
    query_text: str
    search_type: str  # news, academic, historical, trend, expert
    time_focus: str  # recent, historical, long_term
    expected_relevance: float
    domain_specificity: float


@dataclass  
class SearchStrategy:
    """Complete search strategy for a domain"""
    domain: DomainType
    primary_queries: List[SearchQuery]
    secondary_queries: List[SearchQuery]
    fallback_queries: List[SearchQuery]
    search_order: List[str]
    time_allocation: Dict[str, float]


class DomainAdaptiveSearchStrategy:
    """
    Generates domain-specific search strategies for optimal information discovery
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        self.logger = agent_logger
    
    def generate_search_strategy(
        self,
        question: str,
        background: str,
        domain_knowledge: DiscoveredKnowledge,
        cutoff_date: Optional[datetime] = None
    ) -> SearchStrategy:
        """Generate optimized search strategy for the domain and question"""
        
        self.logger.log("search_strategy", f"Generating search strategy for {domain_knowledge.domain_type.value}")
        
        # Generate primary search queries (most important)
        primary_queries = self._generate_primary_queries(
            question, background, domain_knowledge, cutoff_date
        )
        
        # Generate secondary queries (supporting evidence)
        secondary_queries = self._generate_secondary_queries(
            question, background, domain_knowledge, cutoff_date
        )
        
        # Generate fallback queries (if primary searches fail)
        fallback_queries = self._generate_fallback_queries(
            question, background, domain_knowledge, cutoff_date
        )
        
        # Determine optimal search order
        search_order = self._determine_search_order(domain_knowledge.domain_type)
        
        # Allocate time/resources to different search types
        time_allocation = self._allocate_search_time(domain_knowledge)
        
        strategy = SearchStrategy(
            domain=domain_knowledge.domain_type,
            primary_queries=primary_queries,
            secondary_queries=secondary_queries,
            fallback_queries=fallback_queries,
            search_order=search_order,
            time_allocation=time_allocation
        )
        
        self.logger.log("search_strategy", f"Generated {len(primary_queries)} primary queries", {
            "domain": domain_knowledge.domain_type.value,
            "total_queries": len(primary_queries) + len(secondary_queries) + len(fallback_queries)
        })
        
        return strategy
    
    def _generate_primary_queries(
        self,
        question: str,
        background: str,
        domain_knowledge: DiscoveredKnowledge,
        cutoff_date: Optional[datetime]
    ) -> List[SearchQuery]:
        """Generate primary search queries tailored to the domain"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        # Extract key terms and concepts from discovered knowledge
        scaling_law_terms = []
        for law in domain_knowledge.scaling_laws:
            scaling_law_terms.extend([law.domain, law.pattern_type])
        
        trend_terms = []
        for trend in domain_knowledge.trends:
            trend_terms.append(trend.trend_description.split()[0:3])  # First few words
        
        prompt = f"""
        Generate primary search queries for this forecasting question using discovered domain knowledge:
        
        Question: {question}
        Background: {background}
        Domain: {domain_knowledge.domain_type.value}
        Information cutoff: {cutoff_str}
        
        DISCOVERED SCALING LAWS:
        {[f"{law.domain}: {law.mathematical_form}" for law in domain_knowledge.scaling_laws]}
        
        DISCOVERED TRENDS:
        {[f"{trend.trend_description} ({trend.direction})" for trend in domain_knowledge.trends]}
        
        BASE RATES:
        {domain_knowledge.base_rates}
        
        Generate 5-8 primary search queries that are:
        1. **Highly specific** to the question and domain
        2. **Leverage discovered knowledge** (scaling laws, trends, base rates)
        3. **Target different information types**:
           - Current developments and news
           - Historical precedents and patterns
           - Expert opinions and predictions
           - Quantitative data and metrics
           - Trend analysis and extrapolation
        
        For each query:
        - Craft specific search terms that incorporate domain terminology
        - Choose optimal search type (news/academic/historical/trend/expert)
        - Set time focus (recent/historical/long_term)
        - Estimate relevance and domain specificity
        
        Format as JSON array:
        [{{
            "query_text": "specific search query incorporating domain terms",
            "search_type": "news/academic/historical/trend/expert",
            "time_focus": "recent/historical/long_term", 
            "expected_relevance": 0.XX,
            "domain_specificity": 0.XX
        }}]
        """
        
        messages = [
            SystemMessage(content="You are an expert at crafting domain-specific search queries."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            data = json.loads(response.content)
            queries = []
            for item in data:
                queries.append(SearchQuery(
                    query_text=item.get("query_text", ""),
                    search_type=item.get("search_type", "news"),
                    time_focus=item.get("time_focus", "recent"),
                    expected_relevance=item.get("expected_relevance", 0.7),
                    domain_specificity=item.get("domain_specificity", 0.7)
                ))
            return queries
        except:
            # Fallback basic queries
            return [
                SearchQuery(
                    query_text=question.split('?')[0],
                    search_type="news",
                    time_focus="recent",
                    expected_relevance=0.6,
                    domain_specificity=0.5
                )
            ]
    
    def _generate_secondary_queries(
        self,
        question: str,
        background: str,
        domain_knowledge: DiscoveredKnowledge,
        cutoff_date: Optional[datetime]
    ) -> List[SearchQuery]:
        """Generate secondary queries for supporting evidence"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        prompt = f"""
        Generate secondary search queries to support the primary analysis:
        
        Question: {question}
        Domain: {domain_knowledge.domain_type.value}
        Information cutoff: {cutoff_str}
        
        Focus on:
        1. **Reference class examples** - similar situations in the past
        2. **Analogous domains** - patterns from related fields
        3. **Contrarian evidence** - opposing viewpoints and skeptical analysis
        4. **Methodological evidence** - how experts typically forecast in this domain
        5. **Boundary conditions** - when trends break down or change
        
        Generate 3-5 secondary queries that complement the primary analysis.
        
        Format as JSON array with same structure as primary queries.
        """
        
        messages = [
            SystemMessage(content="You are an expert at finding supporting evidence for forecasts."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            data = json.loads(response.content)
            queries = []
            for item in data:
                queries.append(SearchQuery(
                    query_text=item.get("query_text", ""),
                    search_type=item.get("search_type", "historical"),
                    time_focus=item.get("time_focus", "historical"),
                    expected_relevance=item.get("expected_relevance", 0.6),
                    domain_specificity=item.get("domain_specificity", 0.6)
                ))
            return queries
        except:
            return []
    
    def _generate_fallback_queries(
        self,
        question: str,
        background: str,
        domain_knowledge: DiscoveredKnowledge,
        cutoff_date: Optional[datetime]
    ) -> List[SearchQuery]:
        """Generate fallback queries for when primary searches fail"""
        
        # Extract key nouns and concepts from the question
        key_terms = self._extract_key_terms(question, background)
        
        fallback_queries = []
        
        # Basic term searches
        for term in key_terms[:3]:  # Top 3 terms
            fallback_queries.append(SearchQuery(
                query_text=f"{term} trends forecast prediction",
                search_type="news",
                time_focus="recent",
                expected_relevance=0.4,
                domain_specificity=0.3
            ))
        
        # Domain-general searches
        domain_terms = {
            DomainType.TECHNOLOGY: ["innovation", "adoption", "development"],
            DomainType.ECONOMICS: ["market", "growth", "forecast"],
            DomainType.CLIMATE: ["trends", "patterns", "projections"],
            DomainType.BUSINESS: ["industry", "market", "competition"],
            DomainType.SCIENTIFIC: ["research", "progress", "breakthrough"]
        }
        
        general_terms = domain_terms.get(domain_knowledge.domain_type, ["trends", "patterns", "forecast"])
        
        for term in general_terms:
            fallback_queries.append(SearchQuery(
                query_text=f"{domain_knowledge.domain_type.value} {term}",
                search_type="academic",
                time_focus="historical",
                expected_relevance=0.3,
                domain_specificity=0.4
            ))
        
        return fallback_queries
    
    def _extract_key_terms(self, question: str, background: str) -> List[str]:
        """Extract key terms from question and background"""
        
        import re
        
        # Combine question and background
        text = f"{question} {background}".lower()
        
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'does', 'do', 'did', 'have', 'has', 'had',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'what', 'when', 'where',
            'how', 'why', 'which', 'that', 'this', 'these', 'those'
        }
        
        # Extract words (alphanumeric, 3+ characters)
        words = re.findall(r'\b[a-zA-Z0-9]{3,}\b', text)
        
        # Filter stop words and get unique terms
        key_terms = []
        for word in words:
            if word not in stop_words and len(word) >= 3:
                key_terms.append(word)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms[:10]  # Top 10 terms
    
    def _determine_search_order(self, domain: DomainType) -> List[str]:
        """Determine optimal search order for the domain"""
        
        # Domain-specific search priorities
        search_priorities = {
            DomainType.TECHNOLOGY: ["news", "trend", "expert", "academic", "historical"],
            DomainType.ECONOMICS: ["news", "expert", "trend", "academic", "historical"],
            DomainType.CLIMATE: ["academic", "expert", "trend", "news", "historical"],
            DomainType.GEOPOLITICS: ["news", "expert", "historical", "trend", "academic"],
            DomainType.BUSINESS: ["news", "trend", "expert", "academic", "historical"],
            DomainType.SCIENTIFIC: ["academic", "expert", "trend", "news", "historical"],
            DomainType.SPORTS: ["news", "expert", "historical", "trend", "academic"],
            DomainType.HEALTHCARE: ["academic", "expert", "news", "trend", "historical"]
        }
        
        return search_priorities.get(domain, ["news", "expert", "trend", "academic", "historical"])
    
    def _allocate_search_time(self, domain_knowledge: DiscoveredKnowledge) -> Dict[str, float]:
        """Allocate search time/resources based on domain and confidence"""
        
        # Base allocation
        base_allocation = {
            "primary_queries": 0.5,
            "secondary_queries": 0.3,
            "fallback_queries": 0.1,
            "analysis_time": 0.1
        }
        
        # Adjust based on discovery confidence
        if domain_knowledge.discovery_confidence > 0.8:
            # High confidence - focus more on primary queries
            base_allocation["primary_queries"] = 0.6
            base_allocation["secondary_queries"] = 0.25
        elif domain_knowledge.discovery_confidence < 0.5:
            # Low confidence - need more fallback searching
            base_allocation["primary_queries"] = 0.4
            base_allocation["secondary_queries"] = 0.25
            base_allocation["fallback_queries"] = 0.25
        
        return base_allocation
    
    def optimize_queries_for_timeframe(
        self,
        queries: List[SearchQuery],
        cutoff_date: Optional[datetime],
        time_horizon: str
    ) -> List[SearchQuery]:
        """Optimize search queries for specific timeframe constraints"""
        
        if not cutoff_date:
            return queries
        
        optimized_queries = []
        
        for query in queries:
            # Add time constraints to query text
            optimized_text = query.query_text
            
            if query.time_focus == "recent":
                # Focus on period before cutoff
                months_back = 12 if "year" in time_horizon else 6
                start_date = cutoff_date - timedelta(days=months_back*30)
                optimized_text += f" after:{start_date.strftime('%Y-%m-%d')} before:{cutoff_date.strftime('%Y-%m-%d')}"
            
            elif query.time_focus == "historical":
                # Focus on longer historical period
                years_back = 10 if "long" in time_horizon else 5
                start_date = cutoff_date - timedelta(days=years_back*365)
                optimized_text += f" after:{start_date.strftime('%Y-%m-%d')} before:{cutoff_date.strftime('%Y-%m-%d')}"
            
            optimized_query = SearchQuery(
                query_text=optimized_text,
                search_type=query.search_type,
                time_focus=query.time_focus,
                expected_relevance=query.expected_relevance,
                domain_specificity=query.domain_specificity
            )
            
            optimized_queries.append(optimized_query)
        
        return optimized_queries
