"""Validator Agent for checking logical consistency and adding confidence scores"""

from typing import Dict, Any, List
import json
from datetime import datetime
from langchain_core.messages import HumanMessage


class ValidatorAgent:
    """Agent specialized in validating and enhancing forecast results"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def _create_validation_prompt(self, results: Dict[str, Any]) -> str:
        """Create a validation prompt for forecast results"""
        
        return f"""You are an expert in probabilistic calibration, logical consistency checking, and uncertainty quantification. You excel at identifying inconsistencies in reasoning, checking if probabilities sum correctly, and assessing the quality of uncertainty estimates.

Validate and enhance the following forecast results:

{json.dumps(results, indent=2)}

Perform these validation checks:

1. LOGICAL CONSISTENCY:
   - Do the probabilities make logical sense?
   - Are there any contradictions in the reasoning?
   - Do related outcomes have consistent probability relationships?
   - Score: 0.0 (many issues) to 1.0 (perfectly consistent)

2. PROBABILITY CALIBRATION:
   - Are the probability estimates well-calibrated?
   - Do confidence intervals seem reasonable?
   - Are probabilities appropriately distributed?
   - Score: 0.0 (poorly calibrated) to 1.0 (well calibrated)

3. ASSUMPTION TRACKING:
   - What key assumptions are being made?
   - Are assumptions clearly stated?
   - How sensitive are results to these assumptions?

4. UNCERTAINTY QUANTIFICATION:
   - Is uncertainty appropriately captured?
   - Are confidence intervals meaningful?
   - What are the major sources of uncertainty?
   - Score: 0.0 (poor uncertainty handling) to 1.0 (excellent)

5. COMPLETENESS CHECK:
   - Are important outcomes missing?
   - Is the analysis comprehensive?
   - What additional considerations might be relevant?

6. QUALITY IMPROVEMENTS:
   - Suggest specific improvements
   - Identify areas needing more analysis
   - Recommend additional data or considerations

Return your validation as a JSON object:
{{
    "validation_results": {{
        "logical_consistency": 0.85,
        "probability_calibration": 0.78,
        "uncertainty_quantification": 0.82,
        "overall_quality_score": 0.82
    }},
    "assumption_tracking": [
        "Key assumption 1",
        "Key assumption 2"
    ],
    "consistency_issues": [
        "Issue 1 description",
        "Issue 2 description"
    ],
    "calibration_notes": [
        "Calibration observation 1",
        "Calibration observation 2"
    ],
    "uncertainty_analysis": {{
        "major_uncertainties": ["uncertainty1", "uncertainty2"],
        "confidence_assessment": "medium",
        "sensitivity_factors": ["factor1", "factor2"]
    }},
    "improvement_suggestions": [
        "Suggestion 1",
        "Suggestion 2"
    ],
    "missing_considerations": [
        "Missing aspect 1",
        "Missing aspect 2"
    ],
    "validation_summary": "Overall assessment of the forecast quality"
}}"""
    
    def validate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate forecast results and add validation metadata"""
        
        # Create prompt and get LLM response
        prompt = self._create_validation_prompt(results)
        
        try:
            # Get response from LLM
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            validation_result = response.content
            
            # Try to extract JSON from the response
            json_start = validation_result.find('{')
            json_end = validation_result.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = validation_result[json_start:json_end]
                validation_data = json.loads(json_str)
            else:
                # If no JSON found, try parsing the whole response
                validation_data = json.loads(validation_result)
            
            # Add validation results to original results
            enhanced_results = results.copy()
            enhanced_results["validations"] = validation_data
            enhanced_results["validated_at"] = datetime.now().isoformat()
            
            return enhanced_results
            
        except json.JSONDecodeError:
            # Fallback if validation parsing fails
            enhanced_results = results.copy()
            enhanced_results["validations"] = {
                "validation_results": {
                    "logical_consistency": 0.5,
                    "probability_calibration": 0.5,
                    "uncertainty_quantification": 0.5,
                    "overall_quality_score": 0.5
                },
                "assumption_tracking": ["Validation parsing failed"],
                "validation_summary": "Unable to parse validation results",
                "raw_validation_output": validation_result
            }
            enhanced_results["validated_at"] = datetime.now().isoformat()
            
            return enhanced_results
    
    def quick_check(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic validation checks without full LLM analysis"""
        
        validation_results = {
            "logical_consistency": 0.8,  # Default reasonable score
            "probability_calibration": 0.8,
            "uncertainty_quantification": 0.8,
            "overall_quality_score": 0.8
        }
        
        issues = []
        
        # Check probability ranges
        if "forecasts" in results:
            for forecast in results["forecasts"]:
                prob = forecast.get("probability", 0)
                if not (0 <= prob <= 1):
                    issues.append(f"Invalid probability: {prob}")
                    validation_results["probability_calibration"] = 0.3
        
        # Check for missing required fields
        required_fields = ["mode", "time_horizon"]
        for field in required_fields:
            if field not in results:
                issues.append(f"Missing required field: {field}")
                validation_results["logical_consistency"] = 0.5
        
        enhanced_results = results.copy()
        enhanced_results["validations"] = {
            "validation_results": validation_results,
            "assumption_tracking": ["Quick validation performed"],
            "consistency_issues": issues,
            "validation_summary": "Basic validation completed"
        }
        enhanced_results["validated_at"] = datetime.now().isoformat()
        
        return enhanced_results