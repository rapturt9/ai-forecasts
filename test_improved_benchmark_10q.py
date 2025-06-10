#!/usr/bin/env python3
"""
Test Improved CrewAI Benchmark System with 10 Random Questions
Tests the enhanced agent prompts for more granular and accurate forecasts
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

from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster
from ai_forecasts.utils.llm_client import LLMClient

def load_benchmark_questions():
    """Load all questions from the benchmark dataset"""
    try:
        with open('forecastbench_human_2024.json', 'r') as f:
            data = json.load(f)
        
        # Extract questions from the correct structure
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
                    # Skip questions with invalid outcome values
                    continue
        
        return questions
    except Exception as e:
        print(f"⚠️ Could not load benchmark questions: {e}")
        return []

def calculate_brier_score(prediction: float, actual_outcome: float) -> float:
    """Calculate Brier score for a prediction"""
    return (prediction - actual_outcome) ** 2

def test_improved_benchmark():
    """Test the improved CrewAI system with 10 random questions"""
    
    print('🔮 Improved CrewAI Benchmark Test - 10 Random Questions')
    print('=' * 65)
    print('🎯 Testing enhanced agent prompts for granular forecasting')
    print('📊 Each prediction uses superforecaster methodology with precise calculations')
    print()
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")
    
    print(f'🔑 API Key: {api_key[:20]}...')
    
    # Initialize system
    llm_client = LLMClient(api_key=api_key)
    superforecaster = GoogleNewsSuperforecaster(llm_client.get_client())
    
    # Load and sample questions
    all_questions = load_benchmark_questions()
    if len(all_questions) < 10:
        print(f"❌ Only {len(all_questions)} questions available")
        return
    
    # Randomly sample 10 questions
    random.seed(42)  # For reproducibility
    test_questions = random.sample(all_questions, 10)
    
    print(f'📊 Randomly sampled 10 questions from {len(all_questions)} total')
    print()
    
    results = []
    total_brier_score = 0
    successful_predictions = 0
    
    for i, question_data in enumerate(test_questions, 1):
        print(f'📋 Question {i}/10:')
        print(f'   ID: {question_data.get("id", "unknown")}')
        print(f'   Question: {question_data["question"]}')
        print(f'   Actual: {question_data["actual_outcome"]:.4f}')
        print(f'   Freeze: {question_data["freeze_date"]}')
        
        try:
            # Make prediction with improved CrewAI system
            print('🤖 Running enhanced CrewAI prediction...')
            
            # Parse freeze date for search timeframe
            freeze_date = None
            if question_data["freeze_date"] != "Unknown":
                try:
                    freeze_date = datetime.fromisoformat(question_data["freeze_date"].replace('Z', '+00:00'))
                except:
                    freeze_date = None
            
            result = superforecaster.forecast_with_google_news(
                question=question_data["question"],
                background=question_data.get("background", ""),
                cutoff_date=freeze_date,
                time_horizon="immediate"
            )
            
            if result and hasattr(result, 'probability'):
                prediction = result.probability
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
                    'confidence': getattr(result, 'confidence_level', 'unknown'),
                    'base_rate': getattr(result, 'base_rate', None),
                    'reasoning_snippet': getattr(result, 'reasoning', '')[:200] + '...'
                }
                results.append(result_data)
                
                print(f'   🎯 AI Prediction: {prediction:.4f}')
                print(f'   📈 Brier Score: {brier_score:.6f}')
                print(f'   🔬 Confidence: {getattr(result, "confidence_level", "unknown")}')
                if hasattr(result, 'base_rate') and result.base_rate:
                    print(f'   📊 Base Rate: {result.base_rate:.4f}')
                
                # Show brief reasoning
                if hasattr(result, 'reasoning'):
                    reasoning = result.reasoning[:150]
                    print(f'   🧠 Reasoning: {reasoning}...')
                
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
        print(f'✅ Successful predictions: {successful_predictions}/10')
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
        
        # Show best and worst predictions
        if results:
            best_result = min(results, key=lambda x: x['brier_score'])
            worst_result = max(results, key=lambda x: x['brier_score'])
            
            print()
            print('🎯 BEST PREDICTION:')
            print(f'   Question: {best_result["question"][:80]}...')
            print(f'   Prediction: {best_result["prediction"]:.4f} vs Actual: {best_result["actual_outcome"]:.4f}')
            print(f'   Brier Score: {best_result["brier_score"]:.6f}')
            
            print()
            print('📉 WORST PREDICTION:')
            print(f'   Question: {worst_result["question"][:80]}...')
            print(f'   Prediction: {worst_result["prediction"]:.4f} vs Actual: {worst_result["actual_outcome"]:.4f}')
            print(f'   Brier Score: {worst_result["brier_score"]:.6f}')
        
        # Save detailed results
        with open('improved_benchmark_results_10q.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_questions': 10,
                    'successful_predictions': successful_predictions,
                    'average_brier_score': avg_brier_score,
                    'total_brier_score': total_brier_score,
                    'performance': performance,
                    'timestamp': datetime.now().isoformat()
                },
                'individual_results': results
            }, f, indent=2, default=str)
        
        print()
        print('✅ IMPROVED CREWAI BENCHMARK COMPLETE!')
        print('🎯 Enhanced agent prompts successfully tested')
        print('📊 Results saved to improved_benchmark_results_10q.json')
        
        return avg_brier_score
    else:
        print('❌ No successful predictions')
        return None

if __name__ == "__main__":
    print('🚀 Starting Improved CrewAI Benchmark Test')
    print('🔧 Testing enhanced agent prompts for granular forecasting')
    print()
    
    brier_score = test_improved_benchmark()
    if brier_score is not None:
        print(f"\n🏆 FINAL AVERAGE BRIER SCORE: {brier_score:.6f}")
        print("✅ Improved CrewAI benchmark system tested successfully!")
    else:
        print("\n❌ Benchmark test failed")