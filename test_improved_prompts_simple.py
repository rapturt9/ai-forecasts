#!/usr/bin/env python3
"""
Test Improved Agent Prompts - Simple Version
Tests the enhanced prompts without Google News integration for faster results
"""

import sys
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append('src')

from ai_forecasts.agents.targeted_agent import TargetedAgent
from ai_forecasts.utils.llm_client import LLMClient

def load_benchmark_questions():
    """Load questions from the benchmark dataset"""
    try:
        with open('forecastbench_human_2024.json', 'r') as f:
            data = json.load(f)
        
        questions_data = data.get('questions', [])
        
        questions = []
        for item in questions_data:
            if 'question' in item and 'freeze_datetime_value' in item:
                try:
                    actual_outcome = float(item['freeze_datetime_value'])
                    questions.append({
                        'question': item['question'],
                        'actual_outcome': actual_outcome,
                        'freeze_date': item.get('freeze_datetime', 'Unknown'),
                        'background': item.get('background', ''),
                        'id': item.get('id', len(questions))
                    })
                except (ValueError, TypeError):
                    continue
        
        return questions
    except Exception as e:
        print(f"⚠️ Could not load benchmark questions: {e}")
        return []

def calculate_brier_score(prediction: float, actual_outcome: float) -> float:
    """Calculate Brier score for a prediction"""
    return (prediction - actual_outcome) ** 2

def test_improved_prompts():
    """Test the improved agent prompts with 5 questions"""
    
    print('🔮 Improved Agent Prompts Test - 5 Questions')
    print('=' * 55)
    print('🎯 Testing enhanced TargetedAgent with improved reasoning')
    print('📊 Focus on granular probability estimation')
    print()
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")
    
    print(f'🔑 API Key: {api_key[:20]}...')
    
    # Initialize system
    llm_client = LLMClient(api_key=api_key)
    agent = TargetedAgent(llm_client.get_client())
    
    # Load and sample questions
    all_questions = load_benchmark_questions()
    if len(all_questions) < 5:
        print(f"❌ Only {len(all_questions)} questions available")
        return
    
    # Randomly sample 5 questions for faster testing
    random.seed(42)
    test_questions = random.sample(all_questions, 5)
    
    print(f'📊 Testing 5 randomly sampled questions from {len(all_questions)} total')
    print()
    
    results = []
    total_brier_score = 0
    successful_predictions = 0
    
    for i, question_data in enumerate(test_questions, 1):
        print(f'📋 Question {i}/5:')
        print(f'   Question: {question_data["question"][:100]}...')
        print(f'   Actual: {question_data["actual_outcome"]:.4f}')
        
        try:
            # Make prediction with TargetedAgent
            print('🤖 Running improved TargetedAgent prediction...')
            
            # Enhanced prompt for more granular analysis
            enhanced_background = f"""
            {question_data.get("background", "")}
            
            FORECASTING INSTRUCTIONS:
            1. Start with base rates - what percentage of similar events typically occur?
            2. Identify 3-5 specific factors that could move probability up or down
            3. Estimate impact of each factor: Strong (±15%), Moderate (±8%), Weak (±3%)
            4. Apply adjustments incrementally to base rate
            5. Provide final probability between 0.01 and 0.99 (avoid 0.50 unless truly uncertain)
            6. Show your calculation: Base rate ± adjustments = final probability
            
            Information cutoff: {question_data["freeze_date"]}
            """
            
            result = agent.analyze(
                initial_conditions=enhanced_background,
                outcomes_of_interest=[question_data["question"]],
                time_horizon="immediate",
                constraints=[
                    "Use superforecaster methodology",
                    "Provide precise probability estimate",
                    "Show step-by-step reasoning",
                    "Avoid overconfidence"
                ]
            )
            
            if result and "evaluations" in result and len(result["evaluations"]) > 0:
                outcome_data = result["evaluations"][0]
                prediction = outcome_data.get("probability", 0.5)
                actual_outcome = question_data["actual_outcome"]
                
                # Calculate Brier score
                brier_score = calculate_brier_score(prediction, actual_outcome)
                total_brier_score += brier_score
                successful_predictions += 1
                
                # Store result
                result_data = {
                    'question_id': question_data.get("id", i),
                    'question': question_data["question"],
                    'prediction': prediction,
                    'actual_outcome': actual_outcome,
                    'brier_score': brier_score,
                    'confidence': outcome_data.get("confidence", "unknown"),
                    'reasoning_snippet': outcome_data.get("reasoning", "")[:300] + "..."
                }
                results.append(result_data)
                
                print(f'   🎯 AI Prediction: {prediction:.4f}')
                print(f'   📈 Brier Score: {brier_score:.6f}')
                print(f'   🔬 Confidence: {outcome_data.get("confidence", "unknown")}')
                
                # Show reasoning
                reasoning = outcome_data.get("reasoning", "")
                if reasoning:
                    print(f'   🧠 Reasoning: {reasoning[:200]}...')
                
            else:
                print('   ❌ No valid prediction returned')
                
        except Exception as e:
            print(f'   ❌ Error: {e}')
        
        print()
    
    # Calculate final statistics
    if successful_predictions > 0:
        avg_brier_score = total_brier_score / successful_predictions
        
        print('🏆 FINAL RESULTS')
        print('=' * 30)
        print(f'✅ Successful predictions: {successful_predictions}/5')
        print(f'📈 Average Brier Score: {avg_brier_score:.6f}')
        print(f'🎯 Total Brier Score: {total_brier_score:.6f}')
        
        # Performance interpretation
        if avg_brier_score < 0.1:
            performance = "Excellent"
        elif avg_brier_score < 0.2:
            performance = "Good"
        elif avg_brier_score < 0.3:
            performance = "Moderate"
        else:
            performance = "Poor"
        
        print(f'🏅 Performance: {performance}')
        
        # Show individual results
        print()
        print('📊 INDIVIDUAL RESULTS:')
        for i, result in enumerate(results, 1):
            print(f'{i}. Prediction: {result["prediction"]:.3f} vs Actual: {result["actual_outcome"]:.3f} → Brier: {result["brier_score"]:.4f}')
        
        # Save results
        with open('improved_prompts_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_questions': 5,
                    'successful_predictions': successful_predictions,
                    'average_brier_score': avg_brier_score,
                    'total_brier_score': total_brier_score,
                    'performance': performance,
                    'timestamp': datetime.now().isoformat()
                },
                'individual_results': results
            }, f, indent=2, default=str)
        
        print()
        print('✅ IMPROVED PROMPTS TEST COMPLETE!')
        print('🎯 Enhanced reasoning methodology demonstrated')
        print('📊 Results saved to improved_prompts_results.json')
        
        return avg_brier_score
    else:
        print('❌ No successful predictions')
        return None

if __name__ == "__main__":
    print('🚀 Starting Improved Prompts Test')
    print('🔧 Testing enhanced agent reasoning without Google News')
    print()
    
    brier_score = test_improved_prompts()
    if brier_score is not None:
        print(f"\n🏆 FINAL AVERAGE BRIER SCORE: {brier_score:.6f}")
        print("✅ Improved prompts tested successfully!")
    else:
        print("\n❌ Test failed")