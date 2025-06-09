"""Main orchestrator for coordinating multiple agents"""

from typing import Dict, Any, Optional
from datetime import datetime

from ..models.schemas import ForecastRequest, ForecastMode
from ..utils.llm_client import LLMClient
from ..utils.agent_logger import agent_logger
from .forecast_agent import ForecastAgent
from .targeted_agent import TargetedAgent
from .strategy_agent import StrategyAgent
from .validator_agent import ValidatorAgent
from .web_research_agent import WebResearchAgent


class ForecastOrchestrator:
    """Main orchestrator that coordinates multiple agents to process forecast requests"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "anthropic/claude-3-haiku"):
        """Initialize the orchestrator with LLM client and agents"""
        
        # Initialize LLM client
        self.llm_client = LLMClient(api_key=api_key, model=model).get_client()
        
        # Initialize agents
        self.forecast_agent = ForecastAgent(self.llm_client)
        self.targeted_agent = TargetedAgent(self.llm_client)
        self.strategy_agent = StrategyAgent(self.llm_client)
        self.validator_agent = ValidatorAgent(self.llm_client)
        self.web_research_agent = WebResearchAgent(self.llm_client)
    
    def _classify_mode(self, request: ForecastRequest) -> ForecastMode:
        """Determine which mode to use based on the request"""
        
        if request.desired_outcome:
            return ForecastMode.STRATEGY
        elif request.outcomes_of_interest:
            return ForecastMode.TARGETED
        else:
            return ForecastMode.PURE_FORECAST
    
    def _prepare_research_context(self, request: ForecastRequest, cutoff_date: str = None) -> Dict[str, Any]:
        """Research current context for the forecast topic"""
        
        # Determine research topic from the request
        if request.outcomes_of_interest:
            topic = f"Current developments related to: {', '.join(request.outcomes_of_interest)}"
        elif request.desired_outcome:
            topic = f"Current state relevant to achieving: {request.desired_outcome}"
        else:
            # For pure forecasting, use a general topic based on common themes
            topic = "Current AI and technology developments"
        
        agent_logger.log("orchestrator", f"Researching context for: {topic}")
        
        # Use web research agent to gather current context
        research_context = self.web_research_agent.research_current_context(
            topic=topic,
            time_horizon=request.time_horizon,
            cutoff_date=cutoff_date
        )
        
        return research_context
    
    def process_request(self, request: ForecastRequest, use_validation: bool = True, cutoff_date: str = None) -> Dict[str, Any]:
        """Process a forecast request and return results"""
        
        # Determine mode and prepare inputs
        mode = self._classify_mode(request)
        research_context = self._prepare_research_context(request, cutoff_date)
        
        agent_logger.log("orchestrator", f"Processing request in {mode.value} mode", {
            "mode": mode.value,
            "research_topic": research_context.get("research_topic", "unknown"),
            "time_horizon": request.time_horizon
        })
        
        try:
            # Route to appropriate agent(s)
            if mode == ForecastMode.PURE_FORECAST:
                agent_logger.log("orchestrator", "Routing to forecast agent")
                results = self.forecast_agent.analyze(
                    initial_conditions=research_context.get("context_summary", "Current state research completed"),
                    time_horizon=request.time_horizon,
                    constraints=request.constraints,
                    research_context=research_context
                )
            
            elif mode == ForecastMode.TARGETED:
                agent_logger.log("orchestrator", "Routing to targeted agent", {
                    "outcomes_count": len(request.outcomes_of_interest)
                })
                results = self.targeted_agent.analyze(
                    initial_conditions=research_context.get("context_summary", "Current state research completed"),
                    outcomes_of_interest=request.outcomes_of_interest,
                    time_horizon=request.time_horizon,
                    constraints=request.constraints,
                    research_context=research_context
                )
            
            elif mode == ForecastMode.STRATEGY:
                # First get forecast context to inform strategy
                agent_logger.log("orchestrator", "Generating forecast context for strategy...")
                forecast_context = self.forecast_agent.analyze(
                    initial_conditions=research_context.get("context_summary", "Current state research completed"),
                    time_horizon=request.time_horizon,
                    constraints=request.constraints,
                    research_context=research_context
                )
                
                # Then generate strategy
                agent_logger.log("orchestrator", "Generating strategic recommendations...")
                results = self.strategy_agent.generate(
                    initial_conditions=research_context.get("context_summary", "Current state research completed"),
                    desired_outcome=request.desired_outcome,
                    time_horizon=request.time_horizon,
                    constraints=request.constraints,
                    forecast_context=forecast_context,
                    research_context=research_context
                )
                
                # Include forecast context in results
                results["forecast_context"] = forecast_context
            
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            # Validate and enhance results
            if use_validation:
                agent_logger.log("orchestrator", "Running validation checks...")
                results = self.validator_agent.quick_check(results)
                agent_logger.log("orchestrator", "Validation completed")
            
            # Add processing metadata
            results["processing_metadata"] = {
                "mode_used": mode.value,
                "processed_at": datetime.now().isoformat(),
                "validation_applied": use_validation
            }
            
            agent_logger.log("orchestrator", "Request processing completed successfully")
            
            return results
            
        except Exception as e:
            # Return error response
            return {
                "mode": mode.value if 'mode' in locals() else "unknown",
                "error": str(e),
                "initial_conditions_summary": "Error occurred during processing",
                "time_horizon": request.time_horizon,
                "processed_at": datetime.now().isoformat(),
                "success": False
            }
    
    def process_request_dict(self, request_dict: Dict[str, Any], use_validation: bool = True) -> Dict[str, Any]:
        """Process a request from a dictionary (useful for API endpoints)"""
        
        try:
            request = ForecastRequest(**request_dict)
            return self.process_request(request, use_validation)
        except Exception as e:
            return {
                "error": f"Invalid request format: {str(e)}",
                "processed_at": datetime.now().isoformat(),
                "success": False
            }