#!/usr/bin/env python3
"""
Fast CrewAI Benchmark Test - Tests multiple questions quickly
"""

import sys
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append('src')

from ai_forecasts.agents.targeted_agent import TargetedAgent
from ai_forecasts.utils.llm_client import LLMClient

def load_test_questions():
    """Load a few test questions from the benchmark dataset"""
    try:
        with open('forecastbench_human_2024.json', 'r') as f:
            data = json.load(f)
        
        # Select a few diverse questions for quick testing
        test_questions = []
        for item in data[:10]:  # Just first 10 for speed
            if 'question' in item and 'freeze_value' in item:
                test_questions.append({
                    'question': item['question'],
                    'actual_outcome': item['freeze_value'],
                    'freeze_date': item.get('freeze_datetime', 'Unknown'),
                    'background': item.get('background', '')
                })
        
        return test_questions[:3]  # Test with 3 questions
    except Exception as e:
        print(f"⚠️ Could not load benchmark questions: {e}")
        return []

def calculate_brier_score(prediction: float, actual_outcome: float) -> float:
    """Calculate Brier score for a prediction"""
    return (prediction - actual_outcome) ** 2

def test_crewai_benchmark():
    """Test CrewAI system with multiple benchmark questions"""
    
    print('🔮 CrewAI Benchmark Test - Multiple Questions')
    print('=' * 55)
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")
    
    print(f'🔑 API Key: {api_key[:20]}...')
    
    # Initialize LLM client and agent
    llm_client = LLMClient(api_key=api_key)
    agent = TargetedAgent(llm_client.get_client())
    
    # Load test questions
    questions = load_test_questions()
    if not questions:
        print("❌ No questions loaded")
        return
    
    print(f'📊 Testing {len(questions)} questions')
    print()
    
    total_brier_score = 0
    successful_predictions = 0
    
    for i, question_data in enumerate(questions, 1):
        print(f'📋 Question {i}/{len(questions)}:')
        print(f'   {question_data["question"]}')
        print(f'   Actual: {question_data["actual_outcome"]:.4f}')
        
        try:
            # Make prediction with CrewAI
            print('🤖 Running CrewAI prediction...')
            
            result = agent.analyze(
                initial_conditions=question_data.get("background", "No background provided"),
                outcomes_of_interest=[question_data["question"]],
                time_horizon="immediate",
                constraints=[f"Information cutoff: {question_data['freeze_date']}"]
            )
            
            if result and "evaluations" in result and len(result["evaluations"]) > 0:
                outcome_data = result["evaluations"][0]
                prediction = outcome_data.get("probability", 0.5)
                actual_outcome = question_data["actual_outcome"]
                
                # Calculate Brier score
                brier_score = calculate_brier_score(prediction, actual_outcome)
                total_brier_score += brier_score
                successful_predictions += 1
                
                print(f'   🎯 AI Prediction: {prediction:.4f}')
                print(f'   📈 Brier Score: {brier_score:.6f}')
                print(f'   🔬 Confidence: {outcome_data.get("confidence", "N/A")}')
                
                # Show brief reasoning
                reasoning = outcome_data.get("reasoning", "")
                if reasoning:
                    print(f'   🧠 Reasoning: {reasoning[:100]}...')
                
            else:
                print('   ❌ No valid prediction returned')
                
        except Exception as e:
            print(f'   ❌ Error: {e}')
        
        print()
    
    # Calculate average Brier score
    if successful_predictions > 0:
        avg_brier_score = total_brier_score / successful_predictions
        
        print('🏆 FINAL RESULTS')
        print('=' * 25)
        print(f'✅ Successful predictions: {successful_predictions}/{len(questions)}')
        print(f'📈 Average Brier Score: {avg_brier_score:.6f}')
        print(f'🎯 Total Brier Score: {total_brier_score:.6f}')
        
        # Interpret performance
        if avg_brier_score < 0.1:
            performance = "Excellent"
        elif avg_brier_score < 0.25:
            performance = "Good"
        elif avg_brier_score < 0.5:
            performance = "Moderate"
        else:
            performance = "Poor"
        
        print(f'🏅 Performance: {performance}')
        print()
        print('✅ CrewAI BENCHMARK SYSTEM WORKING!')
        print('🎯 Successfully generating Brier scores with real AI predictions')
        
        return avg_brier_score
    else:
        print('❌ No successful predictions')
        return None

if __name__ == "__main__":
    brier_score = test_crewai_benchmark()
    if brier_score is not None:
        print(f"\n🏆 FINAL BRIER SCORE: {brier_score:.6f}")
        print("✅ CrewAI benchmark system is fully functional!")
    else:
        print("\n❌ Benchmark test failed")