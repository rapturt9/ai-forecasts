#!/usr/bin/env python3
"""
Simple benchmark test to demonstrate Brier score calculation
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append('src')

from ai_forecasts.agents.targeted_agent import TargetedAgent
from ai_forecasts.utils.llm_client import LLMClient

def test_simple_benchmark():
    """Test the benchmark system with a simple prediction"""
    
    print('🔮 Simple AI Forecasting Benchmark Test')
    print('=' * 45)
    
    try:
        # Initialize LLM client
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found")
        
        llm_client = LLMClient(api_key=api_key)
        
        # Initialize targeted agent
        agent = TargetedAgent(llm_client.get_client())
        
        # Test question and known outcome
        question = "Will the average global temperature in 2024 exceed 2023?"
        actual_outcome = 0.7565624485542961  # Known result from benchmark data
        
        print(f'📋 Test Question: {question}')
        print(f'✅ Actual Outcome: {actual_outcome:.4f}')
        print()
        
        # Make prediction
        print('🤖 Running AI Forecast...')
        
        result = agent.analyze(
            initial_conditions="2023 is trending to be the hottest year on record. Climate data through July 2024.",
            outcomes_of_interest=[question],
            time_horizon="immediate",
            constraints=["Information cutoff: July 12, 2024"]
        )
        
        print(f"🔍 Debug - Result type: {type(result)}")
        print(f"🔍 Debug - Result keys: {result.keys() if result else 'None'}")
        if result and "evaluations" in result:
            print(f"🔍 Debug - Evaluations count: {len(result['evaluations'])}")
        if result and "error" in result:
            print(f"🔍 Debug - Error: {result['error']}")
        
        if result and "evaluations" in result and len(result["evaluations"]) > 0:
            outcome_data = result["evaluations"][0]
            prediction = outcome_data.get("probability", 0.5)
            
            # Calculate Brier score
            brier_score = (prediction - actual_outcome) ** 2
            
            print()
            print('📊 BENCHMARK RESULTS')
            print('=' * 30)
            print(f'🎯 AI Prediction: {prediction:.4f}')
            print(f'✅ Actual Outcome: {actual_outcome:.4f}')
            print(f'📈 Brier Score: {brier_score:.6f}')
            print(f'🔬 Confidence: {outcome_data.get("confidence", "N/A")}')
            
            # Show reasoning snippet
            reasoning = outcome_data.get("reasoning", "")
            if reasoning:
                print(f'🧠 Reasoning: {reasoning[:200]}...')
            
            print()
            print('✅ BENCHMARK TEST SUCCESSFUL!')
            print(f'🎯 Final Brier Score: {brier_score:.6f}')
            
            return brier_score
            
        else:
            print('❌ No valid prediction returned')
            return None
            
    except Exception as e:
        print(f'❌ Error during benchmark test: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    brier_score = test_simple_benchmark()
    if brier_score is not None:
        print(f'\n🏆 FINAL RESULT: Brier Score = {brier_score:.6f}')
    else:
        print('\n❌ Benchmark test failed')