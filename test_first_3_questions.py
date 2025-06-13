#!/usr/bin/env python3
"""
Test script to verify benchmark functionality on first 3 questions
Shows 12 predictions (3 questions × 4 time horizons), actual answers, and Brier scores
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def load_local_data():
    """Load questions and resolutions from local JSON files"""
    # Load questions
    with open('forecastbench_human_2024.json', 'r') as f:
        questions_data = json.load(f)
    
    # Load resolutions
    with open('forecast_human_resolution_2024.json', 'r') as f:
        resolutions_data = json.load(f)
    
    return questions_data, resolutions_data

def get_resolution_for_question_and_date(question_id, resolution_date, resolutions):
    """Get the resolution value for a specific question ID and date"""
    for resolution in resolutions['resolutions']:
        if (resolution['id'] == question_id and 
            resolution['resolution_date'] == resolution_date):
            return resolution['resolved_to']
    return None

def calculate_brier_score(prediction, actual):
    """Calculate Brier score: (prediction - actual)^2"""
    return (prediction - actual) ** 2

def test_first_3_questions():
    """Test the first 3 questions with mock predictions"""
    print("🧪 Testing First 3 Questions from ForecastBench")
    print("=" * 60)
    
    # Load data
    questions_data, resolutions_data = load_local_data()
    questions = questions_data['questions'][:3]  # First 3 questions
    
    # Forecast due date and time horizons
    forecast_due_date = datetime.strptime(questions_data['forecast_due_date'], '%Y-%m-%d')
    time_horizons = [7, 30, 90, 180]  # days
    
    # Calculate resolution dates
    resolution_dates = []
    for horizon in time_horizons:
        res_date = forecast_due_date + timedelta(days=horizon)
        resolution_dates.append(res_date.strftime('%Y-%m-%d'))
    
    print(f"Forecast due date: {forecast_due_date.strftime('%Y-%m-%d')}")
    print(f"Time horizons: {time_horizons} days")
    print(f"Resolution dates: {resolution_dates}")
    print()
    
    all_results = []
    
    for i, question in enumerate(questions):
        question_id = question['id']
        question_text = question['question']
        
        print(f"Question {i+1}: {question_id}")
        print(f"Text: {question_text}")
        print(f"Freeze value: {question.get('freeze_datetime_value', 'N/A')}")
        print()
        
        question_results = {
            'question_id': question_id,
            'question_text': question_text,
            'freeze_value': question.get('freeze_datetime_value'),
            'predictions': {},
            'actual_values': {},
            'brier_scores': {}
        }
        
        # For testing, use the freeze_datetime_value as our "prediction"
        # In real implementation, this would come from the AI model
        base_prediction = float(question.get('freeze_datetime_value', 0.5))
        
        for j, (horizon, res_date) in enumerate(zip(time_horizons, resolution_dates)):
            # Mock prediction (in real implementation, this would be from AI model)
            # Add some variation to make it more realistic
            prediction = min(max(base_prediction + (j-1.5)*0.05, 0.0), 1.0)
            
            # Get actual resolution value
            actual_value = get_resolution_for_question_and_date(question_id, res_date, resolutions_data)
            
            # Calculate Brier score
            brier_score = None
            if actual_value is not None:
                brier_score = calculate_brier_score(prediction, actual_value)
            
            # Store results
            horizon_key = f"{horizon}d"
            question_results['predictions'][horizon_key] = prediction
            question_results['actual_values'][horizon_key] = actual_value
            question_results['brier_scores'][horizon_key] = brier_score
            
            print(f"  {horizon}-day horizon ({res_date}):")
            print(f"    Prediction: {prediction:.4f}")
            print(f"    Actual: {actual_value}")
            print(f"    Brier Score: {brier_score:.4f}" if brier_score is not None else "    Brier Score: N/A")
            print()
        
        all_results.append(question_results)
        print("-" * 40)
    
    # Summary statistics
    print("\n📊 SUMMARY")
    print("=" * 60)
    
    total_predictions = 0
    total_brier_scores = []
    
    for horizon in time_horizons:
        horizon_key = f"{horizon}d"
        horizon_brier_scores = []
        
        print(f"\n{horizon}-day horizon:")
        for i, result in enumerate(all_results):
            prediction = result['predictions'][horizon_key]
            actual = result['actual_values'][horizon_key]
            brier = result['brier_scores'][horizon_key]
            
            print(f"  Q{i+1}: pred={prediction:.4f}, actual={actual}, brier={brier:.4f}" if brier is not None else f"  Q{i+1}: pred={prediction:.4f}, actual={actual}, brier=N/A")
            
            total_predictions += 1
            if brier is not None:
                horizon_brier_scores.append(brier)
                total_brier_scores.append(brier)
        
        if horizon_brier_scores:
            avg_brier = sum(horizon_brier_scores) / len(horizon_brier_scores)
            print(f"  Average Brier Score: {avg_brier:.4f}")
        else:
            print(f"  Average Brier Score: N/A")
    
    if total_brier_scores:
        overall_avg_brier = sum(total_brier_scores) / len(total_brier_scores)
        print(f"\nOverall Average Brier Score: {overall_avg_brier:.4f}")
        print(f"Total predictions: {total_predictions}")
        print(f"Total Brier scores calculated: {len(total_brier_scores)}")
    else:
        print(f"\nNo Brier scores could be calculated")
    
    return all_results

if __name__ == "__main__":
    try:
        results = test_first_3_questions()
        print("\n✅ Test completed successfully!")
        
        # Save results for verification
        with open('test_results_first_3.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print("📁 Results saved to test_results_first_3.json")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)