"""Targeted Agent for evaluating specific outcomes of interest"""

from typing import Dict, Any, List
import json
from datetime import datetime
from langchain_core.messages import HumanMessage


class TargetedAgent:
    """Agent specialized in evaluating specific outcomes of interest"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def _create_targeted_prompt(
        self, 
        initial_conditions: str, 
        outcomes_of_interest: List[str], 
        time_horizon: str,
        constraints: List[str] = None
    ) -> str:
        """Create a targeted evaluation prompt"""
        
        constraints_text = ""
        if constraints:
            constraints_text = f"\nConstraints to consider: {', '.join(constraints)}"
        
        outcomes_text = "\n".join([f"- {outcome}" for outcome in outcomes_of_interest])
        
        return f"""You are an expert analyst who specializes in evaluating the likelihood of specific outcomes. You excel at breaking down complex scenarios into their component parts, identifying necessary preconditions, and mapping causal pathways.

Evaluate the following specific outcomes given the current conditions:

Initial conditions: {initial_conditions}
Time horizon: {time_horizon}{constraints_text}

Outcomes to evaluate:
{outcomes_text}

For each outcome, provide a detailed assessment:

1. Feasibility Assessment (0-100%):
   - Is this outcome technically/practically possible?
   - What would need to be true for this to happen?

2. Probability Estimation:
   - Likelihood of occurrence within the timeframe
   - Confidence level in this estimate

3. Preconditions Analysis:
   - What must happen first?
   - What conditions must be met?

4. Causal Pathway Mapping:
   - Step-by-step path from current state to outcome
   - Key decision points and inflection points

5. Blocking Factors:
   - What could prevent this outcome?
   - Most likely failure modes

6. Historical Analogies:
   - Similar situations from the past
   - What can we learn from them?

7. Timeline Analysis:
   - When might this outcome occur?
   - Critical milestones along the way

Return your analysis as a JSON object:
{{
    "evaluations": [
        {{
            "outcome": "The specific outcome being evaluated",
            "feasibility_score": 0.75,
            "probability": 0.45,
            "confidence": "medium",
            "preconditions": ["condition1", "condition2"],
            "causal_path": ["step1", "step2", "step3"],
            "blocking_factors": ["blocker1", "blocker2"],
            "historical_analogies": ["analogy1", "analogy2"],
            "timeline_estimate": "12-18 months",
            "key_milestones": ["milestone1", "milestone2"],
            "reasoning": "Detailed explanation of assessment"
        }}
    ]
}}"""
    
    def analyze(
        self, 
        initial_conditions: str, 
        outcomes_of_interest: List[str], 
        time_horizon: str,
        constraints: List[str] = None
    ) -> Dict[str, Any]:
        """Generate targeted outcome analysis"""
        
        # Create prompt and get LLM response
        prompt = self._create_targeted_prompt(initial_conditions, outcomes_of_interest, time_horizon, constraints)
        
        try:
            # Get response from LLM
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            result = response.content
            
            # Try to extract JSON from the response - look for complete JSON object
            json_start = result.find('{')
            if json_start != -1:
                # Find the matching closing brace by counting braces
                brace_count = 0
                json_end = json_start
                for i, char in enumerate(result[json_start:], json_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                if json_end > json_start:
                    json_str = result[json_start:json_end]
                    analysis_data = json.loads(json_str)
                else:
                    # If no complete JSON found, try parsing the whole response
                    analysis_data = json.loads(result)
            else:
                # If no JSON found, try parsing the whole response
                analysis_data = json.loads(result)
            
            # Add metadata
            analysis_data["mode"] = "targeted"
            analysis_data["initial_conditions_summary"] = initial_conditions
            analysis_data["time_horizon"] = time_horizon
            analysis_data["outcomes_of_interest"] = outcomes_of_interest
            analysis_data["generated_at"] = datetime.now().isoformat()
            
            return analysis_data
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "mode": "targeted",
                "initial_conditions_summary": initial_conditions,
                "time_horizon": time_horizon,
                "outcomes_of_interest": outcomes_of_interest,
                "evaluations": [
                    {
                        "outcome": outcome,
                        "feasibility_score": 0.5,
                        "probability": 0.5,
                        "confidence": "low",
                        "preconditions": ["Analysis parsing failed"],
                        "causal_path": ["Unable to parse detailed analysis"],
                        "blocking_factors": ["JSON parsing error"],
                        "historical_analogies": ["Check raw output"],
                        "timeline_estimate": time_horizon,
                        "key_milestones": ["Analysis completion"],
                        "reasoning": "The analysis was generated but could not be parsed"
                    } for outcome in outcomes_of_interest
                ],
                "raw_output": result if 'result' in locals() else "No response received",
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            # Handle any other errors
            return {
                "mode": "targeted",
                "initial_conditions_summary": initial_conditions,
                "time_horizon": time_horizon,
                "outcomes_of_interest": outcomes_of_interest,
                "evaluations": [],
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }