"""
JSON Parser Fix for Google News Superforecaster
Robust JSON parsing with multiple fallback strategies
"""
import json
import re
from typing import Dict, Any, Optional

def fix_json_formatting(json_str: str) -> str:
    """Fix common JSON formatting issues more comprehensively"""
    
    # Remove inline comments and newlines within JSON
    json_str = re.sub(r'//.*?(?=\n|$)', '', json_str)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    
    # Remove extra whitespace and normalize
    json_str = re.sub(r'\s+', ' ', json_str)
    json_str = json_str.strip()
    
    # Fix missing quotes around property names (more comprehensive)
    json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
    
    # Fix boolean values (ensure lowercase)
    json_str = re.sub(r'\bTrue\b', 'true', json_str)
    json_str = re.sub(r'\bFalse\b', 'false', json_str)
    json_str = re.sub(r'\bNone\b', 'null', json_str)
    
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix double quotes in string values by escaping them
    json_str = re.sub(r':\s*"([^"]*)"([^"]*)"([^"]*)"', r': "\1\\\"\2\\\"\3"', json_str)
    
    return json_str

def extract_key_fields_from_text(text: str) -> Dict[str, Any]:
    """Extract key fields using regex when JSON parsing fails"""
    
    result = {
        "final_probability": 0.50, 
        "confidence_level": "medium", 
        "reasoning_summary": "Analysis completed",
        "base_rate_anchor": 0.50
    }
    
    # Extract probability with multiple patterns
    prob_patterns = [
        r'"final_probability":\s*([0-9.]+)',
        r'"final_probability":\s*"([0-9.]+)"',
        r'final_probability["\']?\s*:\s*([0-9.]+)',
        r'probability.*?([0-9.]+)',
        r'estimate.*?([0-9.]+)',
        r'([0-9.]+)%',
        r'(\d+\.\d+)\s*(?:probability|chance|likelihood)'
    ]
    
    for pattern in prob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                prob = float(match.group(1))
                if prob > 1:
                    prob = prob / 100
                if 0.01 <= prob <= 0.99:
                    result["final_probability"] = prob
                    break
            except ValueError:
                continue
    
    # Extract confidence level
    confidence_patterns = [
        r'"confidence_level":\s*"(high|medium|low)"',
        r'confidence.*?(high|medium|low)',
        r'(high|medium|low).*?confidence'
    ]
    
    for pattern in confidence_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["confidence_level"] = match.group(1).lower()
            break
    
    # Extract base rate
    base_rate_patterns = [
        r'"base_rate_anchor":\s*([0-9.]+)',
        r'"base_rate":\s*([0-9.]+)',
        r'base\s+rate.*?([0-9.]+)',
        r'historical.*?frequency.*?([0-9.]+)'
    ]
    
    for pattern in base_rate_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                base_rate = float(match.group(1))
                if base_rate > 1:
                    base_rate = base_rate / 100
                if 0.01 <= base_rate <= 0.99:
                    result["base_rate_anchor"] = base_rate
                    break
            except ValueError:
                continue
    
    # Extract reasoning
    reasoning_patterns = [
        r'"reasoning_summary":\s*"([^"]+)"',
        r'"reasoning":\s*"([^"]+)"',
        r'reasoning.*?:\s*"([^"]+)"'
    ]
    
    for pattern in reasoning_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["reasoning_summary"] = match.group(1)
            break
    
    return result

def parse_json_with_fallbacks(text: str) -> Optional[Dict[str, Any]]:
    """Try multiple strategies to parse JSON from text"""
    
    # Strategy 1: Look for complete JSON blocks
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Complete JSON object
        r'```json\s*(\{.*?\})\s*```',         # JSON code block
        r'```\s*(\{.*?\})\s*```',             # Generic code block
        r'OUTPUT FORMAT:\s*(\{.*?\})'         # Output format section
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                # Try to fix common JSON issues
                json_str = fix_json_formatting(match)
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue
    
    # Strategy 2: Extract key-value patterns
    return extract_key_fields_from_text(text)
