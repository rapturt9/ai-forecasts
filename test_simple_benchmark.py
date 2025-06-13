#!/usr/bin/env python3
"""
Simple test to verify the enhanced ForecastBench works correctly
Tests the first 3 questions with mock predictions to verify Brier score calculation
"""

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path

class SimpleForecastBenchTest:
    """Simple test of ForecastBench with mock predictions"""
    
    # Local files for ForecastBench datasets
    QUESTIONS_FILE = "forecastbench_human_2024.json"
    RESOLUTIONS_FILE = "forecast_human_resolution_2024.json"
    
    # Time horizons for predictions (in days)
    TIME_HORIZONS = [7, 30, 90, 180]
    
    def load_local_data(self):
        """Load questions and resolutions from local JSON files"""
        try:
            # Load questions
            with open(self.QUESTIONS_FILE, 'r') as f:
                questions_data = json.load(f)
            
            # Load resolutions
            with open(self.RESOLUTIONS_FILE, 'r') as f:
                resolutions_data = json.load(f)
            
            questions = questions_data['questions']
            print(f"✅ Loaded {len(questions)} questions from local file")
            print(f"✅ Loaded {len(resolutions_data['resolutions'])} resolutions from local file")
            
            return questions, resolutions_data
            
        except Exception as e:
            print(f"❌ Error loading local data: {e}")
            return [], {}
    
    def get_resolution_for_question_and_date(self, question_id: str, resolution_date: str, resolutions_data: dict) -> float:
        """Get the resolution value for a specific question ID and date"""
        if 'resolutions' not in resolutions_data:
            return None
            
        for resolution in resolutions_data['resolutions']:
            if (resolution['id'] == question_id and 
                resolution['resolution_date'] == resolution_date):
                return resolution['resolved_to']
        return None
    
    def generate_mock_prediction(self, question_idx: int, horizon_days: int) -> float:
        """Generate a mock prediction based on question index and horizon"""
        # Simple mock predictions that vary by question and horizon
        base_predictions = [0.65, 0.55, 0.60]  # Different base for each question
        horizon_adjustment = horizon_days * 0.0005  # Small adjustment based on horizon
        
        prediction = base_predictions[question_idx % 3] + horizon_adjustment
        return min(max(prediction, 0.0), 1.0)  # Clamp to [0, 1]
    
    def test_first_3_questions(self):
        """Test the first 3 questions with mock predictions"""
        print("🚀 Testing Enhanced ForecastBench with first 3 questions")
        
        # Load questions and resolutions from local files
        questions, resolutions_data = self.load_local_data()
        if not questions:
            return {"error": "Failed to load ForecastBench questions"}
            
        if not resolutions_data:
            return {"error": "Failed to load resolution data"}
        
        # Limit to first 3 questions
        questions = questions[:3]
        
        # Base date for time horizon calculations (forecast due date)
        base_date = datetime(2024, 7, 21)
        
        results = []
        all_brier_scores = []
        
        for question_idx, question_data in enumerate(questions):
            question = question_data.get('question', '')
            question_id = question_data.get('id', f"q_{question_idx}")
            
            print(f"\n📋 Processing question {question_idx + 1}: {question[:80]}...")
            
            # Calculate resolution dates for all time horizons
            resolution_dates = []
            for horizon_days in self.TIME_HORIZONS:
                res_date = base_date + timedelta(days=horizon_days)
                resolution_dates.append(res_date.strftime('%Y-%m-%d'))
            
            # Generate mock predictions for each time horizon
            predictions = {}
            brier_scores = {}
            actual_values = {}
            
            for i, (horizon_days, resolution_date) in enumerate(zip(self.TIME_HORIZONS, resolution_dates)):
                # Generate mock prediction
                prediction = self.generate_mock_prediction(question_idx, horizon_days)
                
                # Get actual resolution value
                actual_value = self.get_resolution_for_question_and_date(question_id, resolution_date, resolutions_data)
                
                # Calculate Brier score if resolution data available
                brier_score = None
                if actual_value is not None:
                    brier_score = (prediction - actual_value) ** 2
                    all_brier_scores.append(brier_score)
                
                # Store results
                horizon_key = f"{horizon_days}d"
                predictions[horizon_key] = prediction
                brier_scores[horizon_key] = brier_score
                actual_values[horizon_key] = actual_value
                
                print(f"  ✅ {horizon_days}d horizon: pred={prediction:.6f}, actual={actual_value}, brier={brier_score:.6f}" if brier_score is not None else f"  ✅ {horizon_days}d horizon: pred={prediction:.6f}, actual={actual_value}")
            
            results.append({
                'question_idx': question_idx,
                'question_id': question_id,
                'question': question,
                'predictions': predictions,
                'brier_scores': brier_scores,
                'actual_values': actual_values
            })
        
        # Calculate overall statistics
        if all_brier_scores:
            average_brier = sum(all_brier_scores) / len(all_brier_scores)
            print(f"\n🎯 FINAL RESULTS:")
            print(f"   Total Brier scores: {len(all_brier_scores)}")
            print(f"   Average Brier score: {average_brier:.6f}")
            
            # Print detailed results table
            print(f"\n📊 DETAILED RESULTS TABLE:")
            print("=" * 80)
            for result in results:
                print(f"\nQuestion {result['question_idx'] + 1}: {result['question_id']}")
                for horizon in self.TIME_HORIZONS:
                    horizon_key = f"{horizon}d"
                    pred = result['predictions'].get(horizon_key)
                    actual = result['actual_values'].get(horizon_key)
                    brier = result['brier_scores'].get(horizon_key)
                    if brier is not None:
                        print(f"  {horizon}-day horizon: pred={pred:.6f}, actual={actual:.6f}, brier={brier:.6f}")
                    else:
                        print(f"  {horizon}-day horizon: pred={pred:.6f}, actual={actual}, brier=N/A")
        else:
            print(f"\n❌ No valid Brier scores calculated")
        
        return {
            'total_questions': len(questions),
            'total_brier_scores': len(all_brier_scores),
            'average_brier_score': average_brier if all_brier_scores else None,
            'results': results
        }

def main():
    """Main function to run the simple benchmark test"""
    tester = SimpleForecastBenchTest()
    results = tester.test_first_3_questions()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"simple_benchmark_test_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Results saved to: {output_file}")

if __name__ == "__main__":
    main()