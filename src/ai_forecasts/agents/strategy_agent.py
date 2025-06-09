"""Strategy Agent for generating optimal paths to achieve desired outcomes"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from langchain.schema import HumanMessage


class StrategyAgent:
    """Agent specialized in generating optimal strategies to achieve desired outcomes"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def _create_strategy_prompt(
        self, 
        initial_conditions: str, 
        desired_outcome: str, 
        time_horizon: str,
        constraints: List[str] = None,
        forecast_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a strategy generation prompt"""
        
        constraints_text = ""
        if constraints:
            constraints_text = f"\nConstraints: {', '.join(constraints)}"
        
        context_text = ""
        if forecast_context:
            context_text = f"\nContext from forecasting analysis: {json.dumps(forecast_context, indent=2)}"
        
        return f"""You are an expert strategic planner with deep knowledge of backward induction, game theory, and strategic planning. You excel at breaking down complex goals into actionable steps, identifying critical decision points, and optimizing for success probability while considering resource constraints.

Design an optimal strategy to achieve the desired outcome:

Current state: {initial_conditions}
Desired outcome: {desired_outcome}
Time horizon: {time_horizon}{constraints_text}{context_text}

Your task is to generate a comprehensive strategic plan:

1. GAP ANALYSIS:
   - What needs to change from current to desired state?
   - What resources and capabilities are required?
   - What are the main capability gaps?

2. STRATEGY GENERATION:
   - Identify 3-5 possible strategic paths
   - For each path, break down into sequential steps
   - Estimate success probability for each path
   - Consider different approaches (fast vs. safe, resource-intensive vs. lean, etc.)

3. PATH OPTIMIZATION:
   - Rank paths by: probability × speed × resource efficiency
   - Identify critical decision points
   - Specify measurable milestones
   - Determine optimal resource allocation

4. RISK ASSESSMENT:
   - What could derail each path?
   - What contingencies are needed?
   - How to mitigate major risks?

5. IMPLEMENTATION PLANNING:
   - Detailed action steps for recommended path
   - Timeline and dependencies
   - Success criteria for each step
   - Resource requirements

Use these strategic principles:
- Backward induction: Start from the goal and work backwards
- Optionality: Preserve future choices when possible
- Critical path analysis: Identify bottlenecks and dependencies
- Risk-adjusted planning: Account for uncertainty
- Iterative approach: Build in learning and adaptation

Return your analysis as a JSON object:
{{
    "gap_analysis": {{
        "required_changes": ["change1", "change2"],
        "needed_resources": ["resource1", "resource2"],
        "capability_gaps": ["gap1", "gap2"]
    }},
    "strategies": [
        {{
            "path_name": "Strategy name",
            "approach": "Description of approach",
            "steps": [
                {{
                    "phase": 1,
                    "action": "Specific action to take",
                    "timeline": "Duration or deadline",
                    "success_criteria": "How to measure success",
                    "dependencies": ["prerequisite1", "prerequisite2"],
                    "resources_needed": ["resource1", "resource2"],
                    "risk_factors": ["risk1", "risk2"]
                }}
            ],
            "overall_probability": 0.72,
            "timeline": "Total expected duration",
            "cost_estimate": "Resource requirements",
            "critical_decisions": ["decision1", "decision2"],
            "contingency_plans": ["plan1", "plan2"],
            "advantages": ["pro1", "pro2"],
            "disadvantages": ["con1", "con2"]
        }}
    ],
    "recommended_path": "Name of best strategy",
    "reasoning": "Why this path is recommended",
    "success_factors": ["factor1", "factor2"],
    "failure_modes": ["failure1", "failure2"]
}}"""
    
    def generate(
        self, 
        initial_conditions: str, 
        desired_outcome: str, 
        time_horizon: str,
        constraints: List[str] = None,
        forecast_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate strategic analysis"""
        
        # Create prompt and get LLM response
        prompt = self._create_strategy_prompt(
            initial_conditions, 
            desired_outcome, 
            time_horizon, 
            constraints, 
            forecast_context
        )
        
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
                strategy_data = json.loads(json_str)
            else:
                # If no JSON found, try parsing the whole response
                strategy_data = json.loads(result)
            
            # Add metadata
            strategy_data["mode"] = "strategy"
            strategy_data["initial_conditions_summary"] = initial_conditions
            strategy_data["desired_outcome"] = desired_outcome
            strategy_data["time_horizon"] = time_horizon
            strategy_data["generated_at"] = datetime.now().isoformat()
            
            # Calculate feasibility score based on recommended strategy
            if "strategies" in strategy_data and strategy_data["strategies"]:
                recommended_name = strategy_data.get("recommended_path", "")
                recommended_strategy = None
                
                for strategy in strategy_data["strategies"]:
                    if strategy.get("path_name") == recommended_name:
                        recommended_strategy = strategy
                        break
                
                if not recommended_strategy and strategy_data["strategies"]:
                    recommended_strategy = strategy_data["strategies"][0]
                
                if recommended_strategy:
                    strategy_data["feasibility_score"] = recommended_strategy.get("overall_probability", 0.5)
                    strategy_data["recommended_strategy"] = recommended_strategy
            
            return strategy_data
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "mode": "strategy",
                "initial_conditions_summary": initial_conditions,
                "desired_outcome": desired_outcome,
                "time_horizon": time_horizon,
                "feasibility_score": 0.0,
                "gap_analysis": {
                    "required_changes": [],
                    "needed_resources": [],
                    "capability_gaps": ["Unable to parse strategy results"]
                },
                "strategies": [],
                "recommended_path": "",
                "reasoning": "Failed to parse strategy analysis",
                "raw_output": result,
                "generated_at": datetime.now().isoformat()
            }