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
    
    def validate_forecast(self, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced validation for superforecaster methodology"""
        
        # Extract key components
        probability = self._extract_probability(forecast_data)
        reasoning = self._extract_reasoning(forecast_data)
        
        # Perform validation checks
        logical_consistency = self._check_logical_consistency(forecast_data)
        probability_calibration = self._check_probability_calibration(probability, reasoning)
        confidence_assessment = self._assess_confidence_level(forecast_data)
        
        # Enhanced validation for superforecaster methodology
        methodology_validation = self._validate_methodology(forecast_data)
        research_quality = self._assess_research_quality(forecast_data)
        
        # Generate overall validation score
        overall_score = self._calculate_enhanced_overall_score(
            logical_consistency, probability_calibration, confidence_assessment,
            methodology_validation, research_quality
        )
        
        # Calculate calibration adjustment
        calibration_adjustment = self._calculate_calibration_adjustment(
            probability, methodology_validation, research_quality
        )
        
        validation_result = {
            "validation_timestamp": datetime.now().isoformat(),
            "overall_confidence": overall_score,
            "logical_consistency": logical_consistency,
            "probability_calibration": probability_calibration,
            "confidence_assessment": confidence_assessment,
            "methodology_validation": methodology_validation,
            "research_quality": research_quality,
            "calibration_adjustment": calibration_adjustment,
            "recommendations": self._generate_enhanced_recommendations(forecast_data, overall_score)
        }
        
        return validation_result
    
    def _extract_probability(self, forecast_data: Dict[str, Any]) -> float:
        """Extract probability from forecast data"""
        if "forecast" in forecast_data:
            return forecast_data["forecast"].get("probability", 0.5)
        return forecast_data.get("probability", 0.5)
    
    def _extract_reasoning(self, forecast_data: Dict[str, Any]) -> str:
        """Extract reasoning from forecast data"""
        if "forecast" in forecast_data:
            return forecast_data["forecast"].get("reasoning_chain", "")
        return forecast_data.get("reasoning", "")
    
    def _check_logical_consistency(self, forecast_data: Dict[str, Any]) -> float:
        """Check logical consistency of the forecast"""
        # Basic consistency checks
        probability = self._extract_probability(forecast_data)
        
        # Check if probability is in valid range
        if not (0.01 <= probability <= 0.99):
            return 0.3
        
        # Check for extreme confidence without strong evidence
        if probability < 0.1 or probability > 0.9:
            research_quality = forecast_data.get("historical_research", {}).get("confidence_level", 0.5)
            if research_quality < 0.7:
                return 0.6  # Penalize extreme confidence with weak evidence
        
        return 0.8  # Default good consistency
    
    def _check_probability_calibration(self, probability: float, reasoning: str) -> float:
        """Check probability calibration"""
        # Basic calibration checks
        if not reasoning:
            return 0.5  # No reasoning provided
        
        # Check for overconfidence indicators
        overconfidence_words = ["definitely", "certainly", "absolutely", "impossible"]
        if any(word in reasoning.lower() for word in overconfidence_words):
            if 0.1 < probability < 0.9:
                return 0.6  # Inconsistent language and probability
        
        return 0.8  # Default good calibration
    
    def _assess_confidence_level(self, forecast_data: Dict[str, Any]) -> float:
        """Assess confidence level of the forecast"""
        confidence_str = forecast_data.get("forecast", {}).get("confidence", "medium")
        
        confidence_map = {
            "high": 0.9,
            "medium": 0.7,
            "low": 0.5
        }
        
        return confidence_map.get(confidence_str, 0.7)
    
    def _validate_methodology(self, forecast_data: Dict[str, Any]) -> float:
        """Validate the forecasting methodology used"""
        methodology_score = 0.5  # Base score
        
        # Check for superforecaster components
        forecast = forecast_data.get("forecast", {})
        
        if "base_rates" in forecast:
            methodology_score += 0.2
        
        if "perspectives" in forecast:
            methodology_score += 0.1
        
        if "evidence_summary" in forecast:
            methodology_score += 0.1
        
        if "uncertainties" in forecast:
            methodology_score += 0.1
        
        return min(1.0, methodology_score)
    
    def _assess_research_quality(self, forecast_data: Dict[str, Any]) -> float:
        """Assess quality of research conducted"""
        historical_research = forecast_data.get("historical_research", {})
        current_research = forecast_data.get("current_research", {})
        
        quality_score = 0.3  # Base score
        
        # Historical research quality
        if historical_research.get("sources_researched", 0) > 0:
            quality_score += 0.2
        
        if historical_research.get("confidence_level", 0) > 0.7:
            quality_score += 0.2
        
        # Current research quality (if conducted)
        if not current_research.get("skipped", True):
            quality_score += 0.2
        
        # Evidence quality
        if forecast_data.get("forecast", {}).get("evidence_summary", {}).get("total_pieces", 0) > 5:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    def _calculate_enhanced_overall_score(
        self, 
        logical_consistency: float,
        probability_calibration: float,
        confidence_assessment: float,
        methodology_validation: float,
        research_quality: float
    ) -> float:
        """Calculate enhanced overall validation score"""
        
        weights = {
            "logical_consistency": 0.25,
            "probability_calibration": 0.25,
            "confidence_assessment": 0.15,
            "methodology_validation": 0.20,
            "research_quality": 0.15
        }
        
        overall_score = (
            logical_consistency * weights["logical_consistency"] +
            probability_calibration * weights["probability_calibration"] +
            confidence_assessment * weights["confidence_assessment"] +
            methodology_validation * weights["methodology_validation"] +
            research_quality * weights["research_quality"]
        )
        
        return overall_score
    
    def _calculate_calibration_adjustment(
        self,
        probability: float,
        methodology_validation: float,
        research_quality: float
    ) -> float:
        """Calculate calibration adjustment based on methodology and research quality"""
        
        # No adjustment if methodology and research are high quality
        if methodology_validation > 0.8 and research_quality > 0.8:
            return 0.0
        
        # Adjust towards 0.5 if methodology/research is poor
        adjustment_strength = 1.0 - (methodology_validation + research_quality) / 2.0
        adjustment_direction = 0.5 - probability
        
        # Maximum adjustment of 0.1
        max_adjustment = 0.1
        adjustment = adjustment_direction * adjustment_strength * max_adjustment
        
        return adjustment
    
    def _generate_enhanced_recommendations(
        self, 
        forecast_data: Dict[str, Any], 
        overall_score: float
    ) -> List[str]:
        """Generate enhanced recommendations for forecast improvement"""
        
        recommendations = []
        
        if overall_score < 0.6:
            recommendations.append("Consider gathering more evidence before making forecast")
        
        if forecast_data.get("historical_research", {}).get("confidence_level", 1.0) < 0.5:
            recommendations.append("Improve historical research depth and source diversity")
        
        if not forecast_data.get("forecast", {}).get("base_rates"):
            recommendations.append("Include reference class forecasting and base rate analysis")
        
        if not forecast_data.get("forecast", {}).get("uncertainties"):
            recommendations.append("Add explicit uncertainty quantification")
        
        probability = self._extract_probability(forecast_data)
        if probability < 0.1 or probability > 0.9:
            recommendations.append("Consider if extreme confidence is justified by evidence quality")
        
        return recommendations