"""
Enhanced Google News Superforecaster with Dynamic Domain Knowledge Discovery

This enhanced version replaces hard-coded domain knowledge with dynamic discovery
of scaling laws, trends, and domain-specific patterns for each forecasting task.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from langchain_openrouter import ChatOpenRouter

from ..utils.llm_client import LLMClient
from ..utils.agent_logger import agent_logger
from ..tools.google_news_tool import GoogleNewsTool
from ..tools.enhanced_google_news_tool import EnhancedGoogleNewsTool
from ..domain_knowledge import (
    DynamicDomainKnowledgeDiscovery,
    DomainAdaptiveSearchStrategy, 
    TrendExtrapolationEngine,
    DiscoveredKnowledge
)


class EnhancedGoogleNewsSuperforecaster:
    """
    Enhanced Google News Superforecaster with Dynamic Domain Knowledge Discovery
    
    Key enhancements:
    1. Automatic domain classification and knowledge discovery
    2. Dynamic search strategy adaptation
    3. Trend extrapolation based on discovered patterns
    4. Domain-specific base rate calculation
    5. Adaptive expert consensus analysis
    """
    
    def __init__(self, serp_api_key: str = None, openrouter_api_key: str = None):
        # Initialize LLM
        self.llm = ChatOpenRouter(
            model="anthropic/claude-3.5-sonnet",
            openrouter_api_key=openrouter_api_key,
            headers={
                "HTTP-Referer": "https://fsgeek.ca",
                "X-Title": "AI Forecasting System"
            },
            temperature=0.1
        )
        
        self.serp_api_key = serp_api_key
        self.logger = agent_logger
        
        # Initialize domain knowledge discovery systems
        self.domain_discovery = DynamicDomainKnowledgeDiscovery()
        self.search_strategy = DomainAdaptiveSearchStrategy()
        self.trend_extrapolation = TrendExtrapolationEngine()
        
        # Initialize tools and agents
        self._setup_enhanced_agents()
    
    def forecast(
        self, 
        question: str, 
        background: str = "", 
        cutoff_date: Optional[datetime] = None,
        time_horizon: str = "1 year"
    ) -> Dict[str, Any]:
        """
        Generate enhanced forecast using dynamic domain knowledge discovery
        """
        
        self.logger.log("enhanced_forecaster", f"Starting enhanced forecast: {question[:100]}...")
        
        try:
            # Step 1: Discover domain knowledge
            self.logger.log("enhanced_forecaster", "Discovering domain knowledge...")
            discovered_knowledge = self.domain_discovery.discover_domain_knowledge(
                question, background, cutoff_date
            )
            
            # Step 2: Generate adaptive search strategy
            self.logger.log("enhanced_forecaster", "Generating adaptive search strategy...")
            search_strategy = self.search_strategy.generate_search_strategy(
                question, background, discovered_knowledge, cutoff_date
            )
            
            # Step 3: Perform trend extrapolation
            self.logger.log("enhanced_forecaster", "Performing trend extrapolation...")
            trend_extrapolation = self.trend_extrapolation.extrapolate_trends(
                question, background, discovered_knowledge, time_horizon, cutoff_date
            )
            
            # Step 4: Conduct enhanced news research using adaptive strategy
            self.logger.log("enhanced_forecaster", "Conducting enhanced news research...")
            news_research_data = self._conduct_enhanced_news_research(
                question, background, search_strategy, cutoff_date
            )
            
            # Step 5: Generate dynamic domain context
            dynamic_domain_context = self.domain_discovery.generate_dynamic_domain_context(
                discovered_knowledge
            )
            
            # Step 6: Create enhanced research tasks with discovered knowledge
            tasks = self._create_enhanced_research_tasks(
                question, background, cutoff_date, time_horizon,
                news_research_data, discovered_knowledge, 
                trend_extrapolation, dynamic_domain_context
            )
            
            # Step 7: Execute crew with enhanced knowledge
            crew = Crew(
                agents=[
                    self.enhanced_research_coordinator,
                    self.domain_specialist,
                    self.trend_analyst,
                    self.expert_synthesizer,
                    self.enhanced_synthesis_expert
                ],
                tasks=tasks,
                verbose=True,
                memory=True,
                embedder=None
            )
            
            self.logger.log("enhanced_forecaster", "Executing enhanced crew...")
            result = crew.kickoff()
            
            # Step 8: Parse and enhance results
            enhanced_result = self._parse_enhanced_results(
                result, discovered_knowledge, trend_extrapolation
            )
            
            self.logger.log("enhanced_forecaster", "Enhanced forecast complete", {
                "domain": discovered_knowledge.domain_type.value,
                "discovery_confidence": discovered_knowledge.discovery_confidence,
                "extrapolation_confidence": trend_extrapolation.extrapolation_confidence,
                "predicted_probability": enhanced_result.get("probability", 0.5)
            })
            
            return enhanced_result
            
        except Exception as e:
            self.logger.log("enhanced_forecaster", f"Error in enhanced forecast: {str(e)}", {
                "error_type": type(e).__name__,
                "question": question[:100]
            })
            
            # Fallback to basic analysis
            return self._fallback_forecast(question, background, cutoff_date, time_horizon)
    
    def _setup_enhanced_agents(self):
        """Setup enhanced agents with dynamic domain knowledge capabilities"""
        
        # Create enhanced Google News search tools
        search_timeframe = {
            "start": "06/01/2024",
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        
        google_news_tool = GoogleNewsTool(
            serp_api_key=self.serp_api_key,
            search_timeframe=search_timeframe
        )
        
        enhanced_news_tool = EnhancedGoogleNewsTool(
            serp_api_key=self.serp_api_key,
            search_timeframe=search_timeframe
        )
        
        # Enhanced Research Coordinator with adaptive search
        self.enhanced_research_coordinator = Agent(
            role='Enhanced Research Coordinator',
            goal='Conduct systematic research using dynamically discovered domain knowledge and adaptive search strategies',
            backstory="""You are an advanced research coordinator who dynamically adapts 
            search strategies based on discovered domain knowledge. You use domain-specific 
            scaling laws, trends, and expert patterns to guide research rather than relying 
            on pre-programmed assumptions. You excel at finding relevant evidence that 
            supports trend extrapolation and pattern-based forecasting.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[google_news_tool, enhanced_news_tool]
        )
        
        # Domain Specialist with discovered knowledge
        self.domain_specialist = Agent(
            role='Domain Knowledge Specialist',
            goal='Apply discovered scaling laws, trends, and domain patterns to forecasting analysis',
            backstory="""You are an expert at applying dynamically discovered domain knowledge 
            to forecasting problems. You understand scaling laws, growth patterns, expert 
            consensus patterns, and base rates that have been discovered for the specific 
            domain. You avoid hard-coded assumptions and instead rely on evidence-based 
            patterns discovered through systematic analysis.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Trend Analyst with extrapolation capabilities
        self.trend_analyst = Agent(
            role='Trend Extrapolation Analyst',
            goal='Extrapolate trends using discovered mathematical models and analyze potential trend breaks',
            backstory="""You are an expert at trend extrapolation using mathematical models 
            discovered from domain analysis. You apply exponential, logistic, power law, and 
            other models based on discovered patterns rather than assumptions. You analyze 
            trend break probabilities and saturation points to provide well-calibrated 
            extrapolations.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Expert Opinion Synthesizer with discovered consensus patterns
        self.expert_synthesizer = Agent(
            role='Expert Opinion Synthesizer',
            goal='Synthesize expert opinions using discovered expert consensus patterns and track records',
            backstory="""You are an expert at synthesizing expert opinions based on 
            discovered patterns of expert consensus and accuracy in the specific domain. 
            You understand domain-specific expert biases, track records, and consensus 
            patterns rather than using generic assumptions about expert performance.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Enhanced Synthesis Expert
        self.enhanced_synthesis_expert = Agent(
            role='Enhanced Synthesis Expert',
            goal='Synthesize all discovered knowledge, trends, and research into a well-calibrated forecast',
            backstory=f"""You are a master synthesizer who integrates dynamically discovered 
            domain knowledge with comprehensive research. You combine:
            
            - Discovered scaling laws and growth patterns
            - Trend extrapolation results with uncertainty bounds
            - Domain-specific base rates and expert consensus patterns  
            - Adaptive search results and evidence quality
            - Mathematical model predictions and trend break analysis
            
            You produce well-calibrated forecasts that leverage discovered knowledge rather 
            than relying on hard-coded domain assumptions. You actively fight conservative 
            bias by using discovered base rates and trend extrapolations.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
    
    def _conduct_enhanced_news_research(
        self,
        question: str,
        background: str,
        search_strategy,
        cutoff_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Conduct news research using adaptive search strategy"""
        
        # This would implement the adaptive search strategy
        # For now, return basic structure
        return {
            "adaptive_research_conducted": True,
            "search_strategy_used": search_strategy.domain.value,
            "primary_queries": len(search_strategy.primary_queries),
            "research_depth": "enhanced"
        }
    
    def _create_enhanced_research_tasks(
        self,
        question: str,
        background: str,
        cutoff_date: Optional[datetime],
        time_horizon: str,
        news_research_data: Dict[str, Any],
        discovered_knowledge: DiscoveredKnowledge,
        trend_extrapolation,
        dynamic_domain_context: str
    ) -> List[Task]:
        """Create enhanced research tasks using discovered knowledge"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        # Task 1: Enhanced Research Coordination
        enhanced_research_task = Task(
            description=f"""
            Conduct systematic Google News research for this forecasting question using 
            dynamically discovered domain knowledge and adaptive search strategies:
            
            QUESTION: {question}
            BACKGROUND: {background}
            TIME HORIZON: {time_horizon}
            INFORMATION CUTOFF: {cutoff_str}
            
            {dynamic_domain_context}
            
            RESEARCH INSTRUCTIONS:
            1. Use the discovered scaling laws and trends to guide your search queries
            2. Focus on finding evidence that supports or contradicts the trend extrapolations
            3. Look for base rate information using the discovered reference classes
            4. Search for expert opinions that match the discovered expert consensus patterns
            5. Identify any evidence of trend breaks or saturation points
            
            Use adaptive search strategies rather than generic news searches.
            Provide comprehensive research findings with source credibility assessment.
            """,
            agent=self.enhanced_research_coordinator,
            expected_output="Comprehensive research findings organized by relevance to discovered knowledge patterns"
        )
        
        # Task 2: Domain Knowledge Application
        domain_analysis_task = Task(
            description=f"""
            Apply the discovered domain knowledge to analyze this forecasting question:
            
            QUESTION: {question}
            DISCOVERED DOMAIN: {discovered_knowledge.domain_type.value}
            
            SCALING LAWS DISCOVERED:
            {json.dumps([{
                "pattern": law.mathematical_form,
                "confidence": law.confidence,
                "evidence": law.supporting_evidence[:2]
            } for law in discovered_knowledge.scaling_laws], indent=2)}
            
            DOMAIN TRENDS DISCOVERED:
            {json.dumps([{
                "trend": trend.trend_description,
                "direction": trend.direction,
                "strength": trend.strength,
                "base_rate": trend.base_rate
            } for trend in discovered_knowledge.trends], indent=2)}
            
            BASE RATES DISCOVERED:
            {discovered_knowledge.base_rates}
            
            TASK:
            1. Assess which scaling laws and trends are most applicable to the question
            2. Calculate domain-specific base rates using discovered patterns
            3. Identify relevant expert consensus patterns for this domain
            4. Note any limitations or boundary conditions for the discovered knowledge
            5. Provide domain-informed probability estimates
            
            Use discovered knowledge rather than generic domain assumptions.
            """,
            agent=self.domain_specialist,
            expected_output="Domain-specific analysis using discovered scaling laws, trends, and base rates"
        )
        
        # Task 3: Trend Extrapolation Analysis  
        trend_extrapolation_task = Task(
            description=f"""
            Analyze the trend extrapolation results for this forecasting question:
            
            QUESTION: {question}
            TIME HORIZON: {time_horizon}
            
            TREND EXTRAPOLATION RESULTS:
            - Predicted Value: {trend_extrapolation.predicted_value:.3f}
            - Confidence Interval: {trend_extrapolation.confidence_interval}
            - Model Used: {trend_extrapolation.model_used.trend_type.value}
            - Extrapolation Confidence: {trend_extrapolation.extrapolation_confidence:.3f}
            - Key Assumptions: {trend_extrapolation.assumptions}
            - Risk Factors: {trend_extrapolation.risk_factors}
            
            PROBABILITY RANGES:
            {json.dumps(trend_extrapolation.probability_ranges, indent=2)}
            
            TASK:
            1. Evaluate the reliability of the trend extrapolation for this specific question
            2. Assess the mathematical model used and its appropriateness
            3. Analyze the trend break risks and their impact on predictions
            4. Compare extrapolation results with research evidence
            5. Provide calibrated probability estimates based on trend analysis
            
            Focus on mathematical rigor and uncertainty quantification.
            """,
            agent=self.trend_analyst,
            expected_output="Detailed trend extrapolation analysis with uncertainty assessment"
        )
        
        # Task 4: Expert Opinion Synthesis
        expert_synthesis_task = Task(
            description=f"""
            Synthesize expert opinions using discovered expert consensus patterns:
            
            QUESTION: {question}
            
            DISCOVERED EXPERT PATTERNS:
            {json.dumps([{
                "domain": pattern.domain,
                "consensus_type": pattern.consensus_type,
                "accuracy_pattern": pattern.accuracy_pattern,
                "typical_bias": pattern.typical_bias,
                "confidence": pattern.confidence
            } for pattern in discovered_knowledge.expert_patterns], indent=2)}
            
            TASK:
            1. Apply discovered expert consensus patterns to evaluate expert opinions found in research
            2. Adjust for known expert biases in this domain
            3. Weight expert opinions based on discovered track record patterns
            4. Identify any consensus vs. contrarian expert views
            5. Provide expert-opinion-informed probability estimates
            
            Use discovered expert patterns rather than generic expert evaluation methods.
            """,
            agent=self.expert_synthesizer,
            expected_output="Expert opinion synthesis based on discovered consensus patterns"
        )
        
        # Task 5: Enhanced Final Synthesis
        final_synthesis_task = Task(
            description=f"""
            Synthesize all analysis into a final forecast using discovered domain knowledge:
            
            QUESTION: {question}
            TIME HORIZON: {time_horizon}
            
            INTEGRATION REQUIREMENTS:
            1. **Domain Knowledge**: Use discovered scaling laws, trends, and base rates
            2. **Trend Extrapolation**: Incorporate mathematical model predictions and uncertainty
            3. **Research Evidence**: Weight evidence based on adaptive search strategy results
            4. **Expert Patterns**: Apply discovered expert consensus patterns and biases
            5. **Uncertainty Quantification**: Combine all sources of uncertainty
            
            DISCOVERED KNOWLEDGE SUMMARY:
            - Domain: {discovered_knowledge.domain_type.value}
            - Discovery Confidence: {discovered_knowledge.discovery_confidence:.3f}
            - Scaling Laws: {len(discovered_knowledge.scaling_laws)}
            - Trends: {len(discovered_knowledge.trends)}
            - Base Rates: {list(discovered_knowledge.base_rates.keys())}
            
            FINAL SYNTHESIS REQUIREMENTS:
            - Integrate trend extrapolation: {trend_extrapolation.predicted_value:.3f} 
              (confidence: {trend_extrapolation.extrapolation_confidence:.3f})
            - Apply discovered base rates and scaling laws
            - Account for expert consensus patterns
            - Quantify uncertainty from all sources
            - Provide well-calibrated final probability with detailed reasoning
            
            Output final forecast in JSON format with comprehensive reasoning.
            """,
            agent=self.enhanced_synthesis_expert,
            expected_output="Final well-calibrated forecast integrating all discovered knowledge and analysis"
        )
        
        return [
            enhanced_research_task,
            domain_analysis_task,
            trend_extrapolation_task,
            expert_synthesis_task,
            final_synthesis_task
        ]
    
    def _parse_enhanced_results(
        self,
        crew_result,
        discovered_knowledge: DiscoveredKnowledge,
        trend_extrapolation
    ) -> Dict[str, Any]:
        """Parse and enhance the crew results"""
        
        result_str = str(crew_result)
        
        # Try to extract JSON from the final result
        try:
            json_start = result_str.rfind('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = result_str[json_start:json_end]
                parsed_result = json.loads(json_str)
            else:
                # Fallback parsing
                parsed_result = {"probability": 0.5, "reasoning": "Could not parse crew result"}
        
        except json.JSONDecodeError:
            parsed_result = {"probability": 0.5, "reasoning": "JSON parsing failed"}
        
        # Enhance with discovered knowledge metadata
        enhanced_result = {
            **parsed_result,
            "enhanced_forecast": True,
            "domain_discovery": {
                "domain_type": discovered_knowledge.domain_type.value,
                "discovery_confidence": discovered_knowledge.discovery_confidence,
                "scaling_laws_found": len(discovered_knowledge.scaling_laws),
                "trends_found": len(discovered_knowledge.trends),
                "expert_patterns_found": len(discovered_knowledge.expert_patterns),
                "base_rates_discovered": discovered_knowledge.base_rates
            },
            "trend_extrapolation": {
                "predicted_value": trend_extrapolation.predicted_value,
                "confidence_interval": trend_extrapolation.confidence_interval,
                "extrapolation_confidence": trend_extrapolation.extrapolation_confidence,
                "model_type": trend_extrapolation.model_used.trend_type.value,
                "risk_factors": trend_extrapolation.risk_factors
            },
            "methodology": "Enhanced forecasting with dynamic domain knowledge discovery",
            "generated_at": datetime.now().isoformat()
        }
        
        return enhanced_result
    
    def _fallback_forecast(
        self,
        question: str,
        background: str,
        cutoff_date: Optional[datetime],
        time_horizon: str
    ) -> Dict[str, Any]:
        """Fallback forecast when enhanced analysis fails"""
        
        return {
            "probability": 0.5,
            "confidence_interval": [0.3, 0.7],
            "reasoning": "Enhanced analysis failed, using fallback forecast",
            "enhanced_forecast": False,
            "fallback_reason": "Error in dynamic domain knowledge discovery",
            "methodology": "Fallback basic analysis",
            "generated_at": datetime.now().isoformat()
        }
