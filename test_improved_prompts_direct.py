#!/usr/bin/env python3
"""
Direct Test of Improved Prompts
Tests the enhanced prompting methodology directly with the LLM
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

def create_enhanced_prompt(question: str, background: str, freeze_date: str) -> str:
    """Create an enhanced prompt using superforecaster methodology"""
    
    return f"""You are an expert superforecaster. Your task is to predict the probability of the following event using rigorous methodology.

QUESTION: {question}

BACKGROUND: {background}

INFORMATION CUTOFF: {freeze_date}

FORECASTING METHODOLOGY:

**STEP 1: BASE RATE ANALYSIS (Outside View)**
- Identify the most relevant reference class for this question
- Estimate the base rate: What percentage of similar events typically occur?
- Consider sample size and quality of historical data
- Start with this base rate as your initial estimate

**STEP 2: SPECIFIC FACTOR ADJUSTMENTS (Inside View)**
- List 3-5 specific factors that could move probability up or down from the base rate
- For each factor, assess its impact strength:
  * Strong impact: ±10-20% from base rate
  * Moderate impact: ±5-10% from base rate  
  * Weak impact: ±1-5% from base rate
- Apply adjustments incrementally to the base rate

**STEP 3: EVIDENCE QUALITY ASSESSMENT**
- Rate your evidence quality: High/Medium/Low
- High quality: Multiple credible sources, recent, directly relevant
- Medium quality: Some credible sources, somewhat recent/relevant
- Low quality: Limited sources, older, indirectly relevant

**STEP 4: UNCERTAINTY AND CALIBRATION**
- Consider what you might be missing or what could surprise you
- Avoid overconfidence - don't go below 5% or above 95% unless overwhelming evidence
- Ensure your probability reflects true uncertainty

**STEP 5: FINAL CALCULATION**
Show your work: Base rate ± Factor adjustments = Final probability

**OUTPUT FORMAT:**
Provide your response in this exact JSON format:
{{
    "base_rate": 0.XX,
    "base_rate_reasoning": "explanation of reference class and historical data",
    "adjusting_factors": [
        {{"factor": "factor name", "impact": "+/-X%", "reasoning": "why this factor matters"}},
        {{"factor": "factor name", "impact": "+/-X%", "reasoning": "why this factor matters"}}
    ],
    "evidence_quality": "high/medium/low",
    "calculation": "base_rate ± adjustments = final_probability",
    "final_probability": 0.XX,
    "confidence_level": "high/medium/low",
    "key_uncertainties": ["uncertainty 1", "uncertainty 2"]
}}

**CRITICAL REQUIREMENTS:**
1. Provide a precise probability between 0.01 and 0.99
2. Show your mathematical calculation
3. Avoid round numbers like 0.50 unless truly justified
4. Be specific about factors and their quantified impacts
5. Ground your reasoning in evidence and historical patterns

Begin your analysis:"""

def test_direct_prompts():
    """Test the improved prompts directly with the LLM"""
    
    print('🔮 Direct Improved Prompts Test - 3 Questions')
    print('=' * 55)
    print('🎯 Testing enhanced superforecaster methodology directly')
    print('📊 Focus on precise probability estimation with reasoning')
    print()
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")
    
    print(f'🔑 API Key: {api_key[:20]}...')
    
    # Initialize LLM client
    llm_client = LLMClient(api_key=api_key)
    client = llm_client.get_client()
    
    # Load and sample questions
    all_questions = load_benchmark_questions()
    if len(all_questions) < 3:
        print(f"❌ Only {len(all_questions)} questions available")
        return
    
    # Select 3 diverse questions for testing
    random.seed(42)
    test_questions = random.sample(all_questions, 3)
    
    print(f'📊 Testing 3 questions from {len(all_questions)} total')
    print()
    
    results = []
    total_brier_score = 0
    successful_predictions = 0
    
    for i, question_data in enumerate(test_questions, 1):
        print(f'📋 Question {i}/3:')
        print(f'   Question: {question_data["question"][:80]}...')
        print(f'   Actual: {question_data["actual_outcome"]:.4f}')
        
        try:
            # Create enhanced prompt
            prompt = create_enhanced_prompt(
                question_data["question"],
                question_data.get("background", ""),
                question_data["freeze_date"]
            )
            
            print('🤖 Running enhanced superforecaster analysis...')
            
            # Make prediction
            response = client.invoke(prompt)
            
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to extract JSON from response
            try:
                # Find JSON in response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    parsed_result = json.loads(json_str)
                    
                    prediction = float(parsed_result.get("final_probability", 0.5))
                    prediction = max(0.01, min(0.99, prediction))  # Ensure valid range
                    
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
                        'base_rate': parsed_result.get("base_rate", None),
                        'confidence': parsed_result.get("confidence_level", "unknown"),
                        'calculation': parsed_result.get("calculation", ""),
                        'reasoning': parsed_result.get("base_rate_reasoning", "")[:200] + "..."
                    }
                    results.append(result_data)
                    
                    print(f'   🎯 AI Prediction: {prediction:.4f}')
                    print(f'   📈 Brier Score: {brier_score:.6f}')
                    print(f'   📊 Base Rate: {parsed_result.get("base_rate", "N/A")}')
                    print(f'   🔬 Confidence: {parsed_result.get("confidence_level", "unknown")}')
                    print(f'   🧮 Calculation: {parsed_result.get("calculation", "N/A")}')
                    
                    # Show brief reasoning
                    reasoning = parsed_result.get("base_rate_reasoning", "")
                    if reasoning:
                        print(f'   🧠 Reasoning: {reasoning[:150]}...')
                    
                else:
                    print('   ❌ Could not extract JSON from response')
                    print(f'   Response: {response_text[:200]}...')
                    
            except json.JSONDecodeError as e:
                print(f'   ❌ JSON parsing error: {e}')
                print(f'   Response: {response_text[:200]}...')
                
        except Exception as e:
            print(f'   ❌ Error: {e}')
        
        print()
    
    # Calculate final statistics
    if successful_predictions > 0:
        avg_brier_score = total_brier_score / successful_predictions
        
        print('🏆 FINAL RESULTS')
        print('=' * 30)
        print(f'✅ Successful predictions: {successful_predictions}/3')
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
        print('📊 DETAILED RESULTS:')
        for i, result in enumerate(results, 1):
            print(f'{i}. Prediction: {result["prediction"]:.3f} vs Actual: {result["actual_outcome"]:.3f}')
            print(f'   Brier Score: {result["brier_score"]:.4f}')
            print(f'   Base Rate: {result["base_rate"]}')
            print(f'   Calculation: {result["calculation"]}')
            print()
        
        # Save results
        with open('direct_prompts_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_questions': 3,
                    'successful_predictions': successful_predictions,
                    'average_brier_score': avg_brier_score,
                    'total_brier_score': total_brier_score,
                    'performance': performance,
                    'timestamp': datetime.now().isoformat()
                },
                'individual_results': results
            }, f, indent=2, default=str)
        
        print('✅ DIRECT PROMPTS TEST COMPLETE!')
        print('🎯 Enhanced superforecaster methodology demonstrated')
        print('📊 Results saved to direct_prompts_results.json')
        
        return avg_brier_score
    else:
        print('❌ No successful predictions')
        return None

if __name__ == "__main__":
    print('🚀 Starting Direct Improved Prompts Test')
    print('🔧 Testing enhanced superforecaster methodology')
    print()
    
    brier_score = test_direct_prompts()
    if brier_score is not None:
        print(f"\n🏆 FINAL AVERAGE BRIER SCORE: {brier_score:.6f}")
        print("✅ Improved prompts demonstrated successfully!")
    else:
        print("\n❌ Test failed")