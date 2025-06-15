"""
Mock Superforecaster for testing without API calls
"""
import random
from typing import List, Dict, Any
from datetime import datetime
import logging

# Set up default logger
logger = logging.getLogger(__name__)

class MockSuperforecaster:
    """Mock superforecaster that generates random predictions for testing"""
    
    def __init__(self, openrouter_api_key: str = None, serp_api_key: str = None, 
                 search_budget: int = 10, debate_turns: int = 2, 
                 time_horizons: List[int] = None, **kwargs):
        """Initialize mock superforecaster"""
        self.search_budget = search_budget
        self.debate_turns = debate_turns
        self.time_horizons = time_horizons or [7, 30, 90, 180]
        logger.info("✅ Mock Superforecaster initialized successfully")
    
    def forecast_multi_horizon(self, question: str, comprehensive_context: str, 
                             cutoff_date: datetime, time_horizons_str: List[str]) -> List[Dict[str, Any]]:
        """Generate mock forecasts for multiple time horizons"""
        logger.info(f"🎯 Mock forecasting for {len(time_horizons_str)} time horizons")
        
        results = []
        for horizon in time_horizons_str:
            # Generate random but reasonable prediction
            prediction = random.uniform(0.1, 0.9)  # Avoid extreme values
            confidence = random.uniform(0.6, 0.9)  # Mock confidence
            
            result = {
                'prediction': prediction,
                'confidence': confidence,
                'reasoning': f"Mock reasoning for {horizon} horizon: Based on simulated analysis, "
                           f"the probability is estimated at {prediction:.2f} with {confidence:.2f} confidence.",
                'time_horizon': horizon,
                'search_queries_used': random.randint(1, min(5, self.max_queries)),
                'articles_analyzed': random.randint(1, self.recommended_articles)
            }
            results.append(result)
            logger.info(f"🎯 Mock forecast for {horizon}: {prediction:.3f} (confidence: {confidence:.3f})")
        
        return results
    
    def forecast_with_google_news(self, question: str, background: str = "", 
                                 time_horizons: List[str] = None, cutoff_date: datetime = None,
                                 **kwargs) -> List:
        """Generate mock forecasts using the new interface"""
        from dataclasses import dataclass
        
        @dataclass
        class MockForecastResult:
            question: str
            prediction: float
            confidence: str
            reasoning: str
            
        if time_horizons is None:
            time_horizons = [f"{h}d" for h in self.time_horizons]
        
        logger.info(f"🎯 Mock debate forecasting for {len(time_horizons)} time horizons with {self.debate_turns} turns")
        
        results = []
        for horizon in time_horizons:
            # Generate random but reasonable prediction
            prediction = random.uniform(0.1, 0.9)
            confidence_levels = ["Low", "Medium", "High"]
            confidence = random.choice(confidence_levels)
            
            reasoning = f"Mock {self.debate_turns}-turn debate result for {horizon} horizon: " \
                       f"After simulated debate with search budget of {self.search_budget}, " \
                       f"probability estimated at {prediction:.3f}"
            
            result = MockForecastResult(
                question=question,
                prediction=prediction,
                confidence=confidence,
                reasoning=reasoning
            )
            results.append(result)
            logger.info(f"🎯 Mock forecast for {horizon}: {prediction:.3f} (confidence: {confidence})")
        
        return results
    
    def set_cutoff_date(self, cutoff_date: datetime):
        """Set cutoff date for mock forecaster"""
        logger.info(f"🛡️ Mock cutoff date set: {cutoff_date.strftime('%Y-%m-%d')}")