"""Forecast Agent for generating probability distributions of future outcomes"""

from typing import Dict, Any, List
import json
from datetime import datetime
from langchain_core.messages import HumanMessage
from ..utils.agent_logger import agent_logger


class ForecastAgent:
    """Agent specialized in generating probability distributions for likely outcomes"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def _create_forecast_prompt(self, initial_conditions: str, time_horizon: str, constraints: List[str] = None, research_context: Dict[str, Any] = None) -> str:
        """Create a forecasting prompt"""
        
        constraints_text = ""
        if constraints:
            constraints_text = f"\nConstraints to consider: {', '.join(constraints)}"
        
        # Add research context if available
        research_text = ""
        if research_context:
            research_text = f"""

CURRENT RESEARCH CONTEXT:
Current State: {research_context.get('current_state', 'Not available')}

Recent Developments:
{chr(10).join(f"• {dev}" for dev in research_context.get('recent_developments', []))}

Key Players:
{chr(10).join(f"• {player.get('name', 'Unknown')}: {player.get('recent_activity', 'No recent activity')}" for player in research_context.get('current_players', []))}

Key Trends:
{chr(10).join(f"• {trend}" for trend in research_context.get('key_trends', []))}

Market Dynamics:
• Competition: {research_context.get('market_dynamics', {}).get('competitive_landscape', 'Not analyzed')}
• Technology: {research_context.get('market_dynamics', {}).get('technological_factors', 'Not analyzed')}
• Regulation: {research_context.get('market_dynamics', {}).get('regulatory_environment', 'Not analyzed')}
"""
        
        return f"""You are an expert forecaster with deep knowledge of reference class forecasting, base rates, and probabilistic reasoning. You excel at identifying the most probable outcomes and quantifying uncertainty.

Analyze the following situation and generate probability forecasts:

Initial conditions: {initial_conditions}
Time horizon: {time_horizon}{constraints_text}{research_text}

Your task is to identify and rank the 5-7 most probable outcomes within this timeframe.

For each outcome, provide:
1. Clear description of the outcome
2. Probability estimate (0.0 to 1.0) with reasoning
3. Confidence interval [lower_bound, upper_bound]
4. Key drivers and dependencies
5. Observable leading indicators
6. Critical uncertainties

Use these forecasting principles:
- Reference class forecasting: Compare to similar historical situations
- Base rates: Consider how often similar outcomes occur
- Causal chain analysis: Map out cause-and-effect relationships
- Second-order effects: Consider indirect consequences
- Outside view: Step back from specific details to see patterns

Return your analysis as a JSON object with this structure:
{{
    "outcomes": [
        {{
            "description": "Clear description of outcome",
            "probability": 0.65,
            "confidence_interval": [0.45, 0.80],
            "timeline": "Expected timeframe",
            "key_drivers": ["driver1", "driver2"],
            "early_indicators": ["indicator1", "indicator2"],
            "uncertainties": ["uncertainty1", "uncertainty2"],
            "reasoning": "Detailed reasoning for this probability"
        }}
    ],
    "meta_analysis": {{
        "dominant_scenarios": ["Most likely overall scenarios"],
        "black_swan_events": ["Low probability, high impact events"],
        "key_uncertainties": ["Major unknowns affecting all outcomes"]
    }}
}}"""
    
    def analyze(self, initial_conditions: str, time_horizon: str, constraints: List[str] = None, research_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate forecast analysis"""
        
        agent_logger.log("forecast_agent", "Starting forecast analysis", {
            "time_horizon": time_horizon,
            "has_constraints": bool(constraints),
            "initial_conditions_length": len(initial_conditions) if initial_conditions else 0
        })
        
        # Create prompt and get LLM response
        prompt = self._create_forecast_prompt(initial_conditions, time_horizon, constraints, research_context)
        
        agent_logger.log("forecast_agent", "Generated forecast prompt", {
            "prompt_length": len(prompt)
        })
        
        try:
            # Get response from LLM
            agent_logger.log("forecast_agent", "Sending request to LLM...")
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            result = response.content
            
            agent_logger.log("forecast_agent", "Received LLM response", {
                "response_length": len(result)
            })
            
            # Try to extract JSON from the response
            agent_logger.log("forecast_agent", "Parsing JSON response...")
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = result[json_start:json_end]
                forecast_data = json.loads(json_str)
                agent_logger.log("forecast_agent", "Successfully parsed JSON response")
            else:
                # If no JSON found, try parsing the whole response
                forecast_data = json.loads(result)
                agent_logger.log("forecast_agent", "Parsed full response as JSON")
            
            # Add metadata
            forecast_data["initial_conditions_summary"] = initial_conditions
            forecast_data["time_horizon"] = time_horizon
            forecast_data["mode"] = "forecast"
            forecast_data["generated_at"] = datetime.now().isoformat()
            
            num_outcomes = len(forecast_data.get("outcomes", []))
            agent_logger.log("forecast_agent", f"Forecast analysis completed successfully", {
                "outcomes_generated": num_outcomes
            })
            
            return forecast_data
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails - create a structured response
            return {
                "mode": "forecast",
                "initial_conditions_summary": initial_conditions,
                "time_horizon": time_horizon,
                "outcomes": [
                    {
                        "description": "Analysis completed but JSON parsing failed",
                        "probability": 0.5,
                        "confidence_interval": [0.3, 0.7],
                        "timeline": time_horizon,
                        "key_drivers": ["Unable to parse detailed analysis"],
                        "early_indicators": ["Check raw output for details"],
                        "uncertainties": ["JSON parsing error"],
                        "reasoning": "The analysis was generated but could not be parsed into structured format"
                    }
                ],
                "meta_analysis": {
                    "dominant_scenarios": ["Analysis parsing failed"],
                    "black_swan_events": ["Unexpected response format"],
                    "key_uncertainties": ["Unable to parse forecast results"]
                },
                "raw_output": result,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            # Handle any other errors
            return {
                "mode": "forecast",
                "initial_conditions_summary": initial_conditions,
                "time_horizon": time_horizon,
                "outcomes": [],
                "meta_analysis": {
                    "dominant_scenarios": [],
                    "black_swan_events": [],
                    "key_uncertainties": [f"Error occurred: {str(e)}"]
                },
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }