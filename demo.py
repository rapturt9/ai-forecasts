#!/usr/bin/env python3
"""Demo script for the AI Forecasting & Strategy System"""

import requests
import json
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

API_BASE_URL = "http://localhost:12000"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n--- {title} ---")

def demo_forecast_mode():
    """Demonstrate pure forecasting mode"""
    print_header("DEMO: Pure Forecasting Mode")
    
    request_data = {
        "initial_conditions": "OpenAI has released GPT-4, competition in AI is increasing rapidly, and there is growing regulatory attention on AI safety",
        "time_horizon": "18 months"
    }
    
    print("Request:")
    print(json.dumps(request_data, indent=2))
    
    print("\nMaking API call...")
    response = requests.post(f"{API_BASE_URL}/forecast", json=request_data, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        
        print_section("Top 3 Predicted Outcomes")
        for i, outcome in enumerate(result.get("outcomes", [])[:3], 1):
            print(f"\n{i}. {outcome['description']}")
            print(f"   Probability: {outcome['probability']:.1%}")
            print(f"   Timeline: {outcome.get('timeline', 'Not specified')}")
            print(f"   Key Drivers: {', '.join(outcome.get('key_drivers', [])[:2])}")
        
        print_section("Meta Analysis")
        meta = result.get("meta_analysis", {})
        print(f"Dominant Scenarios: {', '.join(meta.get('dominant_scenarios', [])[:2])}")
        print(f"Key Uncertainties: {', '.join(meta.get('key_uncertainties', [])[:2])}")
        
    else:
        print(f"Error: {response.status_code} - {response.text}")

def demo_targeted_mode():
    """Demonstrate targeted forecasting mode"""
    print_header("DEMO: Targeted Forecasting Mode")
    
    request_data = {
        "initial_conditions": "Current AI capabilities as of 2024",
        "outcomes_of_interest": ["AGI achieved", "Major AI safety incident occurs"],
        "time_horizon": "5 years"
    }
    
    print("Request:")
    print(json.dumps(request_data, indent=2))
    
    print("\nMaking API call...")
    response = requests.post(f"{API_BASE_URL}/forecast", json=request_data, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        
        print_section("Outcome Evaluations")
        for evaluation in result.get("evaluations", []):
            print(f"\nOutcome: {evaluation['outcome']}")
            print(f"Probability: {evaluation.get('probability', 0):.1%}")
            print(f"Feasibility: {evaluation.get('feasibility_score', 0):.1%}")
            print(f"Confidence: {evaluation.get('confidence', 'unknown').title()}")
            print(f"Timeline: {evaluation.get('timeline_estimate', 'Not specified')}")
            
            if evaluation.get('blocking_factors'):
                print(f"Main Blockers: {', '.join(evaluation['blocking_factors'][:2])}")
        
    else:
        print(f"Error: {response.status_code} - {response.text}")

def demo_strategy_mode():
    """Demonstrate strategy generation mode"""
    print_header("DEMO: Strategy Generation Mode")
    
    request_data = {
        "initial_conditions": "Small AI startup with $1M funding and 5 engineers",
        "desired_outcome": "Successful AI product with 100K users",
        "time_horizon": "2 years",
        "constraints": ["Limited budget", "Small team"]
    }
    
    print("Request:")
    print(json.dumps(request_data, indent=2))
    
    print("\nMaking API call...")
    response = requests.post(f"{API_BASE_URL}/forecast", json=request_data, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        
        print_section("Strategic Analysis")
        print(f"Feasibility Score: {result.get('feasibility_score', 0):.1%}")
        
        gap_analysis = result.get("gap_analysis", {})
        if gap_analysis.get("required_changes"):
            print(f"\nRequired Changes:")
            for change in gap_analysis["required_changes"][:3]:
                print(f"  • {change}")
        
        if gap_analysis.get("needed_resources"):
            print(f"\nNeeded Resources:")
            for resource in gap_analysis["needed_resources"][:3]:
                print(f"  • {resource}")
        
        recommended = result.get("recommended_strategy")
        if recommended:
            print_section("Recommended Strategy")
            print(f"Strategy: {recommended.get('name', 'Not specified')}")
            print(f"Success Probability: {recommended.get('overall_probability', 0):.1%}")
            print(f"Timeline: {recommended.get('timeline', 'Not specified')}")
            
            steps = recommended.get("steps", [])
            if steps:
                print(f"\nKey Steps:")
                for step in steps[:3]:
                    print(f"  {step.get('phase', '?')}. {step.get('action', 'Unknown action')}")
                    print(f"     Timeline: {step.get('timeline', 'Not specified')}")
        
        strategies = result.get("strategies", [])
        if len(strategies) > 1:
            print_section("Alternative Strategies")
            for strategy in strategies[1:2]:  # Show one alternative
                print(f"• {strategy.get('path_name', 'Alternative Strategy')}")
                print(f"  Success Rate: {strategy.get('overall_probability', 0):.1%}")
        
    else:
        print(f"Error: {response.status_code} - {response.text}")

def check_system_health():
    """Check if the system is running"""
    print_header("System Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API is healthy")
            print(f"Status: {health_data.get('status')}")
            print(f"Components: {health_data.get('components')}")
            return True
        else:
            print(f"❌ API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        return False

def main():
    """Run the complete demo"""
    print_header("AI Forecasting & Strategy System - Demo")
    print("This demo showcases all three operating modes of the system:")
    print("1. Pure Forecasting - Predict likely outcomes")
    print("2. Targeted Forecasting - Evaluate specific outcomes")
    print("3. Strategy Generation - Find paths to desired outcomes")
    
    # Check system health
    if not check_system_health():
        print("\n❌ System is not available. Please ensure the API server is running.")
        print("Run: python run_api.py")
        return
    
    print("\n🚀 Starting demonstrations...")
    
    # Demo each mode
    try:
        demo_forecast_mode()
        time.sleep(2)
        
        demo_targeted_mode()
        time.sleep(2)
        
        demo_strategy_mode()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {str(e)}")
    
    print_header("Demo Complete")
    print("🌐 Web Interface: https://work-2-ypcpnwlsffvpolgg.prod-runtime.all-hands.dev")
    print("📚 API Documentation: https://work-1-ypcpnwlsffvpolgg.prod-runtime.all-hands.dev/docs")
    print("\nThank you for trying the AI Forecasting & Strategy System!")

if __name__ == "__main__":
    main()