"""Forecast Agent for generating probability distributions of future outcomes"""

from typing import Dict, Any, List
import json
from datetime import datetime
from langchain_core.messages import HumanMessage


class ForecastAgent:
    """Agent specialized in generating probability distributions for likely outcomes"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def _create_forecast_prompt(self, initial_conditions: str, time_horizon: str, constraints: List[str] = None) -> str:
        """Create a forecasting prompt"""
        
        constraints_text = ""
        if constraints:
            constraints_text = f"\nConstraints to consider: {', '.join(constraints)}"
        
        return f"""You are an expert forecaster with deep knowledge of reference class forecasting, base rates, and probabilistic reasoning. You excel at identifying the most probable outcomes and quantifying uncertainty.

Analyze the following situation and generate probability forecasts:

Initial conditions: {initial_conditions}
Time horizon: {time_horizon}{constraints_text}

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
    
    def analyze(self, initial_conditions: str, time_horizon: str, constraints: List[str] = None) -> Dict[str, Any]:
        """Generate forecast analysis"""
        
        # Create prompt and get LLM response
        prompt = self._create_forecast_prompt(initial_conditions, time_horizon, constraints)
        
        try:
            # Get response from LLM
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            result = response.content
            
            # Try to extract JSON from the response
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = result[json_start:json_end]
                forecast_data = json.loads(json_str)
            else:
                # If no JSON found, try parsing the whole response
                forecast_data = json.loads(result)
            
            # Add metadata
            forecast_data["initial_conditions_summary"] = initial_conditions
            forecast_data["time_horizon"] = time_horizon
            forecast_data["mode"] = "forecast"
            forecast_data["generated_at"] = datetime.now().isoformat()
            
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
                "raw_output": result if 'result' in locals() else "No response received",
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