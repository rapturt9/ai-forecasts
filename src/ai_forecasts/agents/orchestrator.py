"""Main orchestrator for coordinating multiple agents"""

from typing import Dict, Any, Optional
from datetime import datetime

from ..models.schemas import ForecastRequest, ForecastMode
from ..utils.llm_client import LLMClient
from .forecast_agent import ForecastAgent
from .targeted_agent import TargetedAgent
from .strategy_agent import StrategyAgent
from .validator_agent import ValidatorAgent


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
    
    def _classify_mode(self, request: ForecastRequest) -> ForecastMode:
        """Determine which mode to use based on the request"""
        
        if request.desired_outcome:
            return ForecastMode.STRATEGY
        elif request.outcomes_of_interest:
            return ForecastMode.TARGETED
        else:
            return ForecastMode.PURE_FORECAST
    
    def _prepare_initial_conditions(self, request: ForecastRequest) -> str:
        """Prepare initial conditions description"""
        
        if request.initial_conditions:
            return request.initial_conditions
        else:
            # Use current date as baseline
            current_date = datetime.now().strftime("%Y-%m-%d")
            return f"Current state as of {current_date}"
    
    def process_request(self, request: ForecastRequest, use_validation: bool = True) -> Dict[str, Any]:
        """Process a forecast request and return results"""
        
        # Determine mode and prepare inputs
        mode = self._classify_mode(request)
        initial_conditions = self._prepare_initial_conditions(request)
        
        print(f"Processing request in {mode.value} mode...")
        
        try:
            # Route to appropriate agent(s)
            if mode == ForecastMode.PURE_FORECAST:
                results = self.forecast_agent.analyze(
                    initial_conditions=initial_conditions,
                    time_horizon=request.time_horizon,
                    constraints=request.constraints
                )
            
            elif mode == ForecastMode.TARGETED:
                results = self.targeted_agent.analyze(
                    initial_conditions=initial_conditions,
                    outcomes_of_interest=request.outcomes_of_interest,
                    time_horizon=request.time_horizon,
                    constraints=request.constraints
                )
            
            elif mode == ForecastMode.STRATEGY:
                # First get forecast context to inform strategy
                print("Generating forecast context for strategy...")
                forecast_context = self.forecast_agent.analyze(
                    initial_conditions=initial_conditions,
                    time_horizon=request.time_horizon,
                    constraints=request.constraints
                )
                
                # Then generate strategy
                print("Generating strategic recommendations...")
                results = self.strategy_agent.generate(
                    initial_conditions=initial_conditions,
                    desired_outcome=request.desired_outcome,
                    time_horizon=request.time_horizon,
                    constraints=request.constraints,
                    forecast_context=forecast_context
                )
                
                # Include forecast context in results
                results["forecast_context"] = forecast_context
            
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            # Validate and enhance results
            if use_validation:
                print("Validating results...")
                results = self.validator_agent.quick_check(results)
            
            # Add processing metadata
            results["processing_metadata"] = {
                "mode_used": mode.value,
                "processed_at": datetime.now().isoformat(),
                "validation_applied": use_validation
            }
            
            return results
            
        except Exception as e:
            # Return error response
            return {
                "mode": mode.value,
                "error": str(e),
                "initial_conditions_summary": initial_conditions,
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