#!/usr/bin/env python3
"""
Test the corrected benchmark with mock predictions to verify Brier score calculation
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class MockForecastResult:
    """Mock forecast result for testing"""
    def __init__(self, probability, confidence_level=0.8, reasoning="Mock reasoning", base_rate=0.5, evidence_quality=0.7):
        self.probability = probability
        self.confidence_level = confidence_level
        self.reasoning = reasoning
        self.base_rate = base_rate
        self.evidence_quality = evidence_quality

class MockSuperforecaster:
    """Mock superforecaster for testing"""
    def __init__(self, base_prediction=0.5):
        self.base_prediction = base_prediction
    
    def forecast(self, question, cutoff_date=None):
        # Use a simple mock prediction based on question content
        # In real testing, we'll use the freeze_datetime_value
        return MockForecastResult(self.base_prediction)

class TestCorrectedBenchmark:
    """Test class for corrected benchmark functionality"""
    
    TIME_HORIZONS = [7, 30, 90, 180]
    
    def __init__(self):
        pass
        
    def load_local_data(self) -> Tuple[List[Dict], Dict[str, Any]]:
        """Load questions and resolutions from local JSON files"""
        try:
            # Load questions
            with open('forecastbench_human_2024.json', 'r') as f:
                questions_data = json.load(f)
            
            # Load resolutions
            with open('forecast_human_resolution_2024.json', 'r') as f:
                resolutions_data = json.load(f)
            
            questions = questions_data['questions']
            print(f"✅ Loaded {len(questions)} questions from local file")
            print(f"✅ Loaded {len(resolutions_data['resolutions'])} resolutions from local file")
            
            return questions, resolutions_data
            
        except Exception as e:
            print(f"❌ Error loading local data: {e}")
            return [], {}
    
    def get_resolution_for_question_and_date(self, question_id: str, resolution_date: str, resolutions_data: Dict) -> float:
        """Get the resolution value for a specific question ID and date"""
        for resolution in resolutions_data['resolutions']:
            if (resolution['id'] == question_id and 
                resolution['resolution_date'] == resolution_date):
                return resolution['resolved_to']
        return None
    
    def process_single_question(self, question_data: Dict, question_idx: int, resolutions_data: Dict, base_date: datetime) -> Dict:
        """Process a single question with 4 time horizon predictions using mock forecaster"""
        try:
            # Use freeze_datetime_value as base for mock predictions
            freeze_value = float(question_data.get('freeze_datetime_value', 0.5))
            superforecaster = MockSuperforecaster(freeze_value)
            
            question = question_data.get('question', '')
            question_id = question_data.get('id', f"q_{question_idx}")
            
            print(f"Processing question {question_idx + 1}: {question[:80]}...")
            
            # Calculate resolution dates for all time horizons
            resolution_dates = []
            for horizon_days in self.TIME_HORIZONS:
                res_date = base_date + timedelta(days=horizon_days)
                resolution_dates.append(res_date.strftime('%Y-%m-%d'))
            
            # Generate predictions for each time horizon
            predictions = {}
            brier_scores = {}
            actual_values = {}
            
            for i, (horizon_days, resolution_date) in enumerate(zip(self.TIME_HORIZONS, resolution_dates)):
                try:
                    # Calculate cutoff date for this horizon
                    cutoff_date = base_date + timedelta(days=horizon_days)
                    
                    # Generate mock forecast - add some variation based on horizon
                    base_prob = freeze_value + (i - 1.5) * 0.05  # Vary by horizon
                    base_prob = max(0.0, min(1.0, base_prob))  # Clamp to [0,1]
                    
                    result = MockForecastResult(base_prob)
                    
                    # Get actual resolution value
                    actual_value = self.get_resolution_for_question_and_date(question_id, resolution_date, resolutions_data)
                    
                    # Calculate Brier score if resolution data available
                    brier_score = None
                    if actual_value is not None:
                        brier_score = (result.probability - actual_value) ** 2
                    
                    # Store prediction
                    horizon_key = f"{horizon_days}d"
                    predictions[horizon_key] = {
                        'probability': result.probability,
                        'confidence': result.confidence_level,
                        'reasoning': result.reasoning,
                        'base_rate': result.base_rate,
                        'evidence_quality': result.evidence_quality,
                        'cutoff_date': cutoff_date.strftime("%Y-%m-%d"),
                        'resolution_date': resolution_date
                    }
                    
                    brier_scores[horizon_key] = brier_score
                    actual_values[horizon_key] = actual_value
                    
                except Exception as e:
                    print(f"Error processing {horizon_days}d horizon for question {question_idx + 1}: {e}")
                    predictions[f"{horizon_days}d"] = {'error': str(e)}
                    brier_scores[f"{horizon_days}d"] = None
                    actual_values[f"{horizon_days}d"] = None
            
            return {
                'question_idx': question_idx,
                'question_id': question_id,
                'question': question,
                'freeze_value': question_data.get('freeze_datetime_value'),
                'predictions': predictions,
                'brier_scores': brier_scores,
                'actual_values': actual_values,
                'success': True
            }
            
        except Exception as e:
            print(f"Error processing question {question_idx + 1}: {e}")
            return {
                'question_idx': question_idx,
                'question_id': question_data.get('id', f"q_{question_idx}"),
                'question': question_data.get('question', ''),
                'error': str(e),
                'success': False
            }
    
    def run_test_benchmark(self, max_questions: int = 3) -> Dict[str, Any]:
        """Run test benchmark evaluation with mock predictions"""
        print(f"🧪 Starting Test Benchmark with Mock Predictions")
        print(f"   Questions: {max_questions}")
        print(f"   Time horizons: {self.TIME_HORIZONS} days")
        
        # Load questions and resolutions from local files
        questions, resolutions_data = self.load_local_data()
        if not questions:
            return {"error": "Failed to load ForecastBench questions"}
            
        if not resolutions_data:
            return {"error": "Failed to load resolution data"}
        
        # Limit questions for testing
        questions = questions[:max_questions]
        
        # Base date for time horizon calculations (forecast due date)
        base_date = datetime(2024, 7, 21)
        
        results = []
        start_time = datetime.now()
        
        # Process questions sequentially for testing
        for idx, question in enumerate(questions):
            result = self.process_single_question(question, idx, resolutions_data, base_date)
            results.append(result)
            
            if result['success']:
                # Show progress with Brier scores for each horizon
                brier_info = []
                for horizon in self.TIME_HORIZONS:
                    brier = result['brier_scores'].get(f"{horizon}d")
                    if brier is not None:
                        brier_info.append(f"{horizon}d:{brier:.3f}")
                brier_str = f" (Brier: {', '.join(brier_info)})" if brier_info else ""
                print(f"✅ Completed question {result['question_idx'] + 1}/{len(questions)}{brier_str}")
            else:
                print(f"❌ Failed question {result['question_idx'] + 1}/{len(questions)}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate comprehensive statistics
        successful_results = [r for r in results if r['success']]
        success_rate = len(successful_results) / len(results) if results else 0
        
        # Calculate Brier scores by time horizon
        horizon_stats = {}
        for horizon in self.TIME_HORIZONS:
            horizon_key = f"{horizon}d"
            brier_scores = []
            predictions = []
            actual_values = []
            
            for result in successful_results:
                brier = result['brier_scores'].get(horizon_key)
                if brier is not None:
                    brier_scores.append(brier)
                    
                pred = result['predictions'].get(horizon_key, {}).get('probability')
                if pred is not None:
                    predictions.append(pred)
                    
                actual = result['actual_values'].get(horizon_key)
                if actual is not None:
                    actual_values.append(actual)
            
            horizon_stats[horizon_key] = {
                'avg_brier_score': sum(brier_scores) / len(brier_scores) if brier_scores else None,
                'brier_score_count': len(brier_scores),
                'avg_prediction': sum(predictions) / len(predictions) if predictions else None,
                'prediction_count': len(predictions),
                'avg_actual_value': sum(actual_values) / len(actual_values) if actual_values else None,
                'actual_value_count': len(actual_values)
            }
        
        # Overall statistics
        total_predictions = sum(len([r for r in successful_results if r['predictions'].get(f"{h}d")]) for h in self.TIME_HORIZONS)
        total_brier_scores = sum(len([r for r in successful_results if r['brier_scores'].get(f"{h}d") is not None]) for h in self.TIME_HORIZONS)
        
        summary = {
            'base_date': base_date.strftime("%Y-%m-%d"),
            'time_horizons': self.TIME_HORIZONS,
            'total_questions': len(questions),
            'successful_forecasts': len(successful_results),
            'success_rate': success_rate,
            'duration_seconds': duration,
            'total_predictions': total_predictions,
            'total_brier_scores': total_brier_scores,
            'horizon_statistics': horizon_stats,
            'results': results
        }
        
        # Log comprehensive results
        print(f"\n🎯 Test Benchmark Complete!")
        print(f"   Questions processed: {len(successful_results)}/{len(questions)} ({success_rate:.1%})")
        print(f"   Total predictions: {total_predictions}")
        print(f"   Total Brier scores: {total_brier_scores}")
        print(f"   Duration: {duration:.1f}s")
        
        # Log Brier scores by time horizon
        for horizon in self.TIME_HORIZONS:
            horizon_key = f"{horizon}d"
            stats = horizon_stats[horizon_key]
            if stats['avg_brier_score'] is not None:
                print(f"   {horizon}-day Brier Score: {stats['avg_brier_score']:.4f} (n={stats['brier_score_count']})")
            else:
                print(f"   {horizon}-day Brier Score: N/A (no resolutions)")
        
        return summary

def main():
    """Main function to run test benchmark"""
    tester = TestCorrectedBenchmark()
    
    # Run test on first 3 questions
    results = tester.run_test_benchmark(max_questions=3)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_benchmark_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Results saved to: {output_file}")
    
    # Print detailed results for verification
    print(f"\n📋 DETAILED RESULTS FOR VERIFICATION")
    print("=" * 60)
    
    for result in results['results']:
        if result['success']:
            print(f"\nQuestion {result['question_idx'] + 1}: {result['question_id']}")
            print(f"Text: {result['question']}")
            print(f"Freeze Value: {result['freeze_value']}")
            
            for horizon in [7, 30, 90, 180]:
                horizon_key = f"{horizon}d"
                pred_data = result['predictions'].get(horizon_key, {})
                actual = result['actual_values'].get(horizon_key)
                brier = result['brier_scores'].get(horizon_key)
                
                print(f"  {horizon}-day: pred={pred_data.get('probability', 'N/A'):.4f}, actual={actual}, brier={brier:.4f}" if brier is not None else f"  {horizon}-day: pred={pred_data.get('probability', 'N/A'):.4f}, actual={actual}, brier=N/A")

if __name__ == "__main__":
    main()