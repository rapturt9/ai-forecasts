#!/usr/bin/env python3
"""Test script for the initial conditions feature"""

import requests
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_initial_conditions():
    """Test the initial conditions feature with API calls"""
    
    base_url = "http://localhost:12000"
    
    # Test 1: Targeted forecasting without initial conditions
    print("🧪 Test 1: Targeted forecasting without initial conditions")
    request_data_1 = {
        "outcomes_of_interest": ["AGI achieved by any company"],
        "time_horizon": "2 years"
    }
    
    try:
        response_1 = requests.post(f"{base_url}/forecast", json=request_data_1, timeout=30)
        if response_1.status_code == 200:
            result_1 = response_1.json()
            print("✅ Request successful")
            print(f"📊 Mode: {result_1.get('mode', 'unknown')}")
            if 'agent_logs' in result_1:
                for log in result_1['agent_logs'][-3:]:  # Show last 3 logs
                    print(f"📝 {log}")
        else:
            print(f"❌ Request failed: {response_1.status_code}")
            print(response_1.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Targeted forecasting WITH initial conditions
    print("🧪 Test 2: Targeted forecasting WITH initial conditions")
    request_data_2 = {
        "initial_conditions": "$1B additional investment in AI safety research announced by major tech companies",
        "outcomes_of_interest": ["AGI achieved safely", "Major AI alignment breakthrough"],
        "time_horizon": "2 years"
    }
    
    try:
        response_2 = requests.post(f"{base_url}/forecast", json=request_data_2, timeout=30)
        if response_2.status_code == 200:
            result_2 = response_2.json()
            print("✅ Request successful")
            print(f"📊 Mode: {result_2.get('mode', 'unknown')}")
            if 'agent_logs' in result_2:
                for log in result_2['agent_logs'][-3:]:  # Show last 3 logs
                    print(f"📝 {log}")
        else:
            print(f"❌ Request failed: {response_2.status_code}")
            print(response_2.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Strategy generation WITH initial conditions
    print("🧪 Test 3: Strategy generation WITH initial conditions")
    request_data_3 = {
        "initial_conditions": "Economic recession with 30% reduction in tech hiring and limited venture funding",
        "desired_outcome": "Successfully launch AI consulting business generating $500K revenue",
        "time_horizon": "18 months",
        "constraints": ["Minimal startup capital", "Reduced market demand"]
    }
    
    try:
        response_3 = requests.post(f"{base_url}/forecast", json=request_data_3, timeout=30)
        if response_3.status_code == 200:
            result_3 = response_3.json()
            print("✅ Request successful")
            print(f"📊 Mode: {result_3.get('mode', 'unknown')}")
            if 'agent_logs' in result_3:
                for log in result_3['agent_logs'][-3:]:  # Show last 3 logs
                    print(f"📝 {log}")
        else:
            print(f"❌ Request failed: {response_3.status_code}")
            print(response_3.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔮 Testing Initial Conditions Feature")
    print("="*50)
    test_initial_conditions()
    print("\n✅ Testing completed!")