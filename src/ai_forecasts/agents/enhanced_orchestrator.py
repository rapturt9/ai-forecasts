"""
Enhanced Orchestrator - Combines superforecaster methodology with web archive research
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from .superforecaster_agent import SuperforecasterAgent
from .web_archive_agent import WebArchiveAgent
from .web_research_agent import WebResearchAgent
from .validator_agent import ValidatorAgent
from ..models.schemas import ForecastRequest
from ..utils.llm_client import LLMClient
from ..utils.agent_logger import agent_logger


class EnhancedForecastOrchestrator:
    """
    Enhanced orchestrator that combines multiple advanced forecasting methodologies:
    1. Superforecaster techniques (reference class, multiple perspectives, etc.)
    2. Web archive research for historical context
    3. Current web research (when appropriate)
    4. Systematic validation and calibration
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.superforecaster = SuperforecasterAgent(self.llm_client)
        self.web_archive = WebArchiveAgent(self.llm_client)
        self.web_research = WebResearchAgent(self.llm_client)
        self.validator = ValidatorAgent(self.llm_client)
        self.logger = agent_logger
        
    def process_enhanced_request(
        self, 
        request: ForecastRequest, 
        cutoff_date: Optional[datetime] = None,
        research_depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Process a forecasting request using enhanced methodology
        """
        
        self.logger.info(f"🚀 Starting enhanced forecasting process")
        self.logger.info(f"📋 Request: {request.outcomes_of_interest or request.desired_outcome}")
        
        # Determine the main question to forecast
        main_question = self._extract_main_question(request)
        
        # Step 1: Web archive research for historical context
        historical_context = self._conduct_historical_research(main_question, cutoff_date, research_depth)
        
        # Step 2: Current web research (if cutoff allows)
        current_context = self._conduct_current_research(main_question, cutoff_date, research_depth)
        
        # Step 3: Superforecaster analysis with enriched context
        superforecaster_analysis = self._conduct_superforecaster_analysis(
            main_question, request, historical_context, current_context, cutoff_date
        )
        
        # Step 4: Cross-validation and calibration
        validation_results = self._validate_and_calibrate(
            superforecaster_analysis, historical_context, current_context
        )
        
        # Step 5: Final synthesis
        final_forecast = self._synthesize_final_forecast(
            request, main_question, historical_context, current_context,
            superforecaster_analysis, validation_results
        )
        
        return final_forecast
    
    def _extract_main_question(self, request: ForecastRequest) -> str:
        """Extract the main forecasting question from the request"""
        
        if request.outcomes_of_interest:
            return request.outcomes_of_interest[0]
        elif request.desired_outcome:
            return f"Will the following outcome be achieved: {request.desired_outcome}"
        else:
            return "General forecasting question"
    
    def _conduct_historical_research(
        self, 
        question: str, 
        cutoff_date: Optional[datetime], 
        research_depth: str
    ) -> Dict[str, Any]:
        """Conduct comprehensive historical research using web archives"""
        
        self.logger.info(f"📚 Conducting historical research")
        
        if not cutoff_date:
            cutoff_date = datetime.now()
        
        try:
            historical_research = self.web_archive.research_historical_context(
                topic=question,
                cutoff_date=cutoff_date,
                research_depth=research_depth
            )
            
            self.logger.info(f"✅ Historical research completed: {historical_research.get('confidence_level', 0):.2f} confidence")
            return historical_research
            
        except Exception as e:
            self.logger.error(f"❌ Historical research failed: {str(e)}")
            return {
                "research_topic": question,
                "error": str(e),
                "confidence_level": 0.1,
                "summary": "Historical research unavailable"
            }
    
    def _conduct_current_research(
        self, 
        question: str, 
        cutoff_date: Optional[datetime], 
        research_depth: str
    ) -> Dict[str, Any]:
        """Conduct current web research if appropriate"""
        
        self.logger.info(f"🌐 Conducting current web research")
        
        # Only do current research if cutoff is recent or not specified
        if cutoff_date and cutoff_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            self.logger.info(f"⏰ Skipping current research due to cutoff date: {cutoff_date}")
            return {
                "research_topic": question,
                "skipped": True,
                "reason": "Cutoff date prevents current research",
                "confidence_level": 0.0
            }
        
        try:
            current_research = self.web_research.research_topic(
                topic=question,
                time_horizon="current",
                cutoff_date=cutoff_date
            )
            
            self.logger.info(f"✅ Current research completed")
            return current_research
            
        except Exception as e:
            self.logger.error(f"❌ Current research failed: {str(e)}")
            return {
                "research_topic": question,
                "error": str(e),
                "confidence_level": 0.1,
                "summary": "Current research unavailable"
            }
    
    def _conduct_superforecaster_analysis(
        self,
        question: str,
        request: ForecastRequest,
        historical_context: Dict[str, Any],
        current_context: Dict[str, Any],
        cutoff_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Conduct superforecaster analysis with enriched context"""
        
        self.logger.info(f"🧠 Conducting superforecaster analysis")
        
        # Enrich background with research findings
        enriched_background = self._create_enriched_background(
            request, historical_context, current_context
        )
        
        try:
            superforecaster_result = self.superforecaster.forecast_with_superforecaster_methodology(
                question=question,
                background=enriched_background,
                cutoff_date=cutoff_date,
                time_horizon=request.time_horizon
            )
            
            self.logger.info(f"✅ Superforecaster analysis completed: {superforecaster_result.get('probability', 0.5):.3f} probability")
            return superforecaster_result
            
        except Exception as e:
            self.logger.error(f"❌ Superforecaster analysis failed: {str(e)}")
            return {
                "question": question,
                "error": str(e),
                "probability": 0.5,
                "confidence_level": "low",
                "methodology": "superforecaster_failed"
            }
    
    def _create_enriched_background(
        self,
        request: ForecastRequest,
        historical_context: Dict[str, Any],
        current_context: Dict[str, Any]
    ) -> str:
        """Create enriched background combining original request with research"""
        
        background_parts = []
        
        # Original background
        if hasattr(request, 'background') and request.background:
            background_parts.append(f"Original context: {request.background}")
        
        # Historical research summary
        if historical_context.get("summary"):
            background_parts.append(f"Historical context: {historical_context['summary']}")
        
        # Key historical trends
        if historical_context.get("trend_analysis", {}).get("directional_trends"):
            trends = historical_context["trend_analysis"]["directional_trends"][:3]
            background_parts.append(f"Historical trends: {', '.join([t.get('description', '') for t in trends])}")
        
        # Expert opinions from archives
        if historical_context.get("expert_opinions", {}).get("consensus_view"):
            consensus = historical_context["expert_opinions"]["consensus_view"]
            background_parts.append(f"Historical expert consensus: {consensus}")
        
        # Current research (if available)
        if not current_context.get("skipped") and current_context.get("summary"):
            background_parts.append(f"Current context: {current_context['summary']}")
        
        # Constraints
        if request.constraints:
            background_parts.append(f"Constraints: {', '.join(request.constraints)}")
        
        return "\n\n".join(background_parts)
    
    def _validate_and_calibrate(
        self,
        superforecaster_analysis: Dict[str, Any],
        historical_context: Dict[str, Any],
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and calibrate the forecast"""
        
        self.logger.info(f"🔍 Validating and calibrating forecast")
        
        try:
            # Prepare validation context
            validation_context = {
                "forecast": superforecaster_analysis,
                "historical_research": historical_context,
                "current_research": current_context,
                "methodology": "enhanced_superforecaster"
            }
            
            validation_result = self.validator.validate_forecast(validation_context)
            
            self.logger.info(f"✅ Validation completed: {validation_result.get('overall_confidence', 0.5):.3f} confidence")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {str(e)}")
            return {
                "validation_status": "failed",
                "error": str(e),
                "overall_confidence": 0.5,
                "calibration_adjustment": 0.0
            }
    
    def _synthesize_final_forecast(
        self,
        request: ForecastRequest,
        question: str,
        historical_context: Dict[str, Any],
        current_context: Dict[str, Any],
        superforecaster_analysis: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize all components into final forecast"""
        
        self.logger.info(f"🎯 Synthesizing final forecast")
        
        # Extract key components
        base_probability = superforecaster_analysis.get("probability", 0.5)
        calibration_adjustment = validation_results.get("calibration_adjustment", 0.0)
        final_probability = max(0.01, min(0.99, base_probability + calibration_adjustment))
        
        # Determine forecast mode
        if request.outcomes_of_interest:
            mode = "targeted"
            evaluations = [{
                "outcome": question,
                "probability": final_probability,
                "confidence": superforecaster_analysis.get("confidence_level", "medium"),
                "methodology": "enhanced_superforecaster",
                "reasoning": superforecaster_analysis.get("reasoning_chain", ""),
                "base_rate": superforecaster_analysis.get("base_rates", {}).get("historical_frequency", 0.5),
                "evidence_quality": historical_context.get("research_quality", {}).get("quality_score", 0.5),
                "validation_score": validation_results.get("overall_confidence", 0.5)
            }]
            
            result = {
                "mode": mode,
                "question": question,
                "evaluations": evaluations,
                "methodology_details": {
                    "superforecaster_analysis": superforecaster_analysis,
                    "historical_research": {
                        "sources_researched": historical_context.get("sources_researched", 0),
                        "confidence_level": historical_context.get("confidence_level", 0.5),
                        "key_trends": historical_context.get("trend_analysis", {}).get("directional_trends", [])[:3]
                    },
                    "current_research": {
                        "conducted": not current_context.get("skipped", True),
                        "summary": current_context.get("summary", "Not conducted")
                    },
                    "validation": validation_results
                },
                "research_quality": {
                    "historical_confidence": historical_context.get("confidence_level", 0.5),
                    "current_confidence": current_context.get("confidence_level", 0.0),
                    "overall_confidence": validation_results.get("overall_confidence", 0.5)
                }
            }
            
        elif request.desired_outcome:
            mode = "strategy"
            # For strategy mode, we'd need additional strategy generation logic
            # For now, return a simplified strategy response
            result = {
                "mode": mode,
                "desired_outcome": request.desired_outcome,
                "feasibility_probability": final_probability,
                "methodology": "enhanced_superforecaster",
                "analysis": superforecaster_analysis,
                "research_context": {
                    "historical": historical_context.get("summary", ""),
                    "current": current_context.get("summary", "")
                }
            }
            
        else:
            mode = "forecast"
            outcomes = [{
                "description": question,
                "probability": final_probability,
                "confidence_interval": superforecaster_analysis.get("uncertainties", {}).get("confidence_interval", [0.3, 0.7]),
                "key_factors": superforecaster_analysis.get("final_forecast", {}).get("key_factors", []),
                "methodology": "enhanced_superforecaster"
            }]
            
            result = {
                "mode": mode,
                "question": question,
                "outcomes": outcomes,
                "methodology_details": {
                    "superforecaster_analysis": superforecaster_analysis,
                    "historical_research": historical_context,
                    "validation": validation_results
                }
            }
        
        # Add common metadata
        result.update({
            "timestamp": datetime.now().isoformat(),
            "enhanced_methodology": True,
            "research_conducted": {
                "historical": historical_context.get("sources_researched", 0) > 0,
                "current": not current_context.get("skipped", True)
            },
            "quality_metrics": {
                "research_quality": historical_context.get("research_quality", {}).get("quality_score", 0.5),
                "validation_confidence": validation_results.get("overall_confidence", 0.5),
                "methodology_rigor": 0.9  # High rigor due to superforecaster + archive research
            }
        })
        
        self.logger.info(f"✅ Final forecast synthesized: {final_probability:.3f} probability")
        return result