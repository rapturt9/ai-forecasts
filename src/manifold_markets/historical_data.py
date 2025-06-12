"""
Historical Data Manager for Manifold Markets
Provides mock historical data for backtesting
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)

@dataclass
class HistoricalMarket:
    """Historical market data"""
    id: str
    question: str
    created_time: datetime
    close_time: datetime
    resolution: Optional[str]
    resolution_time: Optional[datetime]
    probability_history: List[Dict[str, Any]]
    volume: float
    liquidity: float
    creator_username: str
    outcome_type: str
    mechanism: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'question': self.question,
            'createdTime': self.created_time.isoformat() if self.created_time else None,
            'closeTime': self.close_time.isoformat() if self.close_time else None,
            'resolution': self.resolution,
            'resolutionTime': self.resolution_time.isoformat() if self.resolution_time else None,
            'probability': self.probability_history[-1]['probability'] if self.probability_history else 0.5,
            'volume': self.volume,
            'liquidity': self.liquidity,
            'creatorUsername': self.creator_username,
            'outcomeType': self.outcome_type,
            'mechanism': self.mechanism
        }

class ManifoldHistoricalDataManager:
    """Manages historical market data for backtesting"""
    
    def __init__(self):
        self.logger = logger
        self._mock_markets = self._generate_mock_markets()
    
    def _generate_mock_markets(self) -> List[HistoricalMarket]:
        """Generate mock historical markets for testing"""
        markets = []
        
        # Sample questions for mock markets
        sample_questions = [
            "Will Bitcoin reach $100,000 by end of 2024?",
            "Will there be a recession in the US in 2024?",
            "Will AI achieve AGI by 2025?",
            "Will SpaceX successfully land on Mars by 2026?",
            "Will the Democrats win the 2024 presidential election?",
            "Will inflation in the US drop below 2% in 2024?",
            "Will Tesla stock price exceed $300 by end of 2024?",
            "Will there be a major earthquake (>7.0) in California in 2024?",
            "Will renewable energy exceed 50% of US electricity by 2025?",
            "Will a new COVID variant cause lockdowns in 2024?"
        ]
        
        base_time = datetime.now() - timedelta(days=365)
        
        for i, question in enumerate(sample_questions):
            created_time = base_time + timedelta(days=i * 30)
            close_time = created_time + timedelta(days=random.randint(30, 180))
            
            # Generate probability history
            prob_history = []
            current_prob = random.uniform(0.3, 0.7)
            
            for day in range(30):
                timestamp = created_time + timedelta(days=day)
                current_prob += random.uniform(-0.05, 0.05)
                current_prob = max(0.01, min(0.99, current_prob))
                
                prob_history.append({
                    'timestamp': timestamp,
                    'probability': current_prob,
                    'volume': random.uniform(100, 1000)
                })
            
            # Determine resolution
            resolution = None
            resolution_time = None
            if close_time < datetime.now():
                resolution = 'YES' if random.random() > 0.5 else 'NO'
                resolution_time = close_time + timedelta(days=random.randint(1, 7))
            
            market = HistoricalMarket(
                id=f"market_{i+1:03d}",
                question=question,
                created_time=created_time,
                close_time=close_time,
                resolution=resolution,
                resolution_time=resolution_time,
                probability_history=prob_history,
                volume=random.uniform(1000, 10000),
                liquidity=random.uniform(500, 5000),
                creator_username=f"user_{i+1}",
                outcome_type="BINARY",
                mechanism="cpmm-1"
            )
            
            markets.append(market)
        
        return markets
    
    def download_historical_data(self) -> bool:
        """Mock download of historical data"""
        self.logger.info("📊 Using mock historical data for backtesting")
        return True
    
    def get_markets_for_backtesting(self, start_date: datetime, end_date: datetime, 
                                  min_volume: float = 100) -> List[HistoricalMarket]:
        """Get markets that were active during the specified period"""
        filtered_markets = []
        
        for market in self._mock_markets:
            # Check if market was active during the period
            if (market.created_time <= end_date and 
                market.close_time >= start_date and
                market.volume >= min_volume):
                filtered_markets.append(market)
        
        self.logger.info(f"Found {len(filtered_markets)} markets for backtesting period")
        return filtered_markets
    
    def get_similar_markets(self, question: str, limit: int = 5) -> List[HistoricalMarket]:
        """Get markets similar to the given question"""
        # Simple similarity based on common keywords
        question_words = set(question.lower().split())
        
        scored_markets = []
        for market in self._mock_markets:
            market_words = set(market.question.lower().split())
            similarity = len(question_words.intersection(market_words)) / len(question_words.union(market_words))
            scored_markets.append((similarity, market))
        
        # Sort by similarity and return top results
        scored_markets.sort(key=lambda x: x[0], reverse=True)
        similar_markets = [market for _, market in scored_markets[:limit]]
        
        self.logger.info(f"Found {len(similar_markets)} similar markets")
        return similar_markets
    
    def get_market_probability_at_time(self, market_id: str, timestamp: datetime) -> Optional[float]:
        """Get market probability at a specific time"""
        market = next((m for m in self._mock_markets if m.id == market_id), None)
        if not market:
            return None
        
        # Find closest probability entry
        closest_entry = None
        min_diff = float('inf')
        
        for entry in market.probability_history:
            diff = abs((entry['timestamp'] - timestamp).total_seconds())
            if diff < min_diff:
                min_diff = diff
                closest_entry = entry
        
        return closest_entry['probability'] if closest_entry else None
    
    def get_market_resolution(self, market_id: str) -> Optional[str]:
        """Get market resolution"""
        market = next((m for m in self._mock_markets if m.id == market_id), None)
        return market.resolution if market else None