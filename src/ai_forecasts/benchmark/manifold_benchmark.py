"""Manifold Markets benchmark data collection and evaluation"""

import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
from dataclasses import dataclass


@dataclass
class ManifoldQuestion:
    """Represents a Manifold Markets question for benchmarking"""
    id: str
    question: str
    description: str
    created_time: datetime
    close_time: datetime
    resolution_time: Optional[datetime]
    resolution: Optional[str]  # "YES", "NO", "CANCEL", "MKT" (multiple choice)
    probability: Optional[float]  # Final probability before resolution
    initial_probability: float
    volume: float
    category: str
    tags: List[str]
    
    @property
    def is_resolved(self) -> bool:
        return self.resolution is not None
    
    @property
    def is_binary(self) -> bool:
        return self.resolution in ["YES", "NO"] if self.resolution else True
    
    @property
    def time_to_resolution(self) -> Optional[timedelta]:
        if self.resolution_time and self.created_time:
            return self.resolution_time - self.created_time
        return None


class ManifoldBenchmark:
    """Collects and manages Manifold Markets data for benchmarking"""
    
    def __init__(self):
        self.base_url = "https://api.manifold.markets/v0"
        self.questions: List[ManifoldQuestion] = []
    
    def fetch_resolved_questions(
        self, 
        limit: int = 100,
        category: Optional[str] = None,
        min_volume: float = 100.0,
        days_back: int = 30
    ) -> List[ManifoldQuestion]:
        """Fetch resolved questions from Manifold Markets"""
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Build API request
        params = {
            "limit": limit,
            "sort": "resolve-time",
            "order": "desc"
        }
        
        if category:
            params["category"] = category
            
        try:
            response = requests.get(f"{self.base_url}/markets", params=params)
            response.raise_for_status()
            markets_data = response.json()
            
            questions = []
            for market in markets_data:
                # Filter for resolved questions with sufficient volume
                if (market.get("isResolved") and 
                    market.get("volume", 0) >= min_volume and
                    market.get("outcomeType") == "BINARY"):
                    
                    question = self._parse_market_data(market)
                    if question and self._is_in_date_range(question, start_date, end_date):
                        questions.append(question)
            
            self.questions.extend(questions)
            return questions
            
        except requests.RequestException as e:
            print(f"Error fetching Manifold data: {e}")
            return []
    
    def _parse_market_data(self, market_data: Dict[str, Any]) -> Optional[ManifoldQuestion]:
        """Parse raw market data into ManifoldQuestion object"""
        try:
            # Parse timestamps
            created_time = datetime.fromtimestamp(market_data["createdTime"] / 1000)
            close_time = datetime.fromtimestamp(market_data["closeTime"] / 1000)
            
            resolution_time = None
            if market_data.get("resolutionTime"):
                resolution_time = datetime.fromtimestamp(market_data["resolutionTime"] / 1000)
            
            # Get final probability (last probability before resolution)
            probability = market_data.get("probability")
            
            return ManifoldQuestion(
                id=market_data["id"],
                question=market_data["question"],
                description=market_data.get("description", ""),
                created_time=created_time,
                close_time=close_time,
                resolution_time=resolution_time,
                resolution=market_data.get("resolution"),
                probability=probability,
                initial_probability=market_data.get("initialProbability", 0.5),
                volume=market_data.get("volume", 0),
                category=market_data.get("groupSlugs", ["general"])[0] if market_data.get("groupSlugs") else "general",
                tags=market_data.get("tags", [])
            )
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error parsing market data: {e}")
            return None
    
    def _is_in_date_range(self, question: ManifoldQuestion, start_date: datetime, end_date: datetime) -> bool:
        """Check if question resolution is within date range"""
        if not question.resolution_time:
            return False
        return start_date <= question.resolution_time <= end_date
    
    def get_ai_related_questions(self) -> List[ManifoldQuestion]:
        """Filter for AI-related questions"""
        ai_keywords = [
            "ai", "artificial intelligence", "gpt", "llm", "openai", "anthropic",
            "machine learning", "neural network", "agi", "artificial general intelligence",
            "chatgpt", "claude", "gemini", "automation", "robot"
        ]
        
        ai_questions = []
        for question in self.questions:
            question_text = (question.question + " " + question.description).lower()
            if any(keyword in question_text for keyword in ai_keywords):
                ai_questions.append(question)
        
        return ai_questions
    
    def get_tech_questions(self) -> List[ManifoldQuestion]:
        """Filter for technology-related questions"""
        tech_keywords = [
            "technology", "tech", "software", "app", "platform", "startup",
            "company", "product launch", "ipo", "acquisition", "funding"
        ]
        
        tech_questions = []
        for question in self.questions:
            question_text = (question.question + " " + question.description).lower()
            if any(keyword in question_text for keyword in tech_keywords):
                tech_questions.append(question)
        
        return tech_questions
    
    def create_benchmark_dataset(self, max_questions: int = 20) -> List[Dict[str, Any]]:
        """Create a benchmark dataset from collected questions"""
        
        # Prioritize AI and tech questions
        ai_questions = self.get_ai_related_questions()
        tech_questions = self.get_tech_questions()
        
        # Combine and deduplicate
        priority_questions = list({q.id: q for q in ai_questions + tech_questions}.values())
        
        # Add other high-volume questions if needed
        all_questions = sorted(self.questions, key=lambda q: q.volume, reverse=True)
        
        selected_questions = priority_questions[:max_questions//2]
        remaining_slots = max_questions - len(selected_questions)
        
        for question in all_questions:
            if len(selected_questions) >= max_questions:
                break
            if question not in selected_questions:
                selected_questions.append(question)
        
        # Convert to benchmark format
        benchmark_cases = []
        for question in selected_questions[:max_questions]:
            case = {
                "case_id": f"manifold_{question.id}",
                "source": "manifold_markets",
                "question": question.question,
                "description": question.description,
                "initial_conditions": self._extract_initial_conditions(question),
                "target_outcome": question.question,
                "time_horizon": self._calculate_time_horizon(question),
                "ground_truth": {
                    "resolution": question.resolution,
                    "final_probability": question.probability,
                    "market_volume": question.volume,
                    "resolution_date": question.resolution_time.isoformat() if question.resolution_time else None
                },
                "metadata": {
                    "category": question.category,
                    "tags": question.tags,
                    "created_date": question.created_time.isoformat(),
                    "close_date": question.close_time.isoformat()
                }
            }
            benchmark_cases.append(case)
        
        return benchmark_cases
    
    def _extract_initial_conditions(self, question: ManifoldQuestion) -> str:
        """Extract initial conditions from question context"""
        # Use the question creation date as the reference point
        date_str = question.created_time.strftime("%Y-%m-%d")
        
        # Combine question and description for context
        context = f"As of {date_str}: {question.description}" if question.description else f"As of {date_str}, considering the question: {question.question}"
        
        return context
    
    def _calculate_time_horizon(self, question: ManifoldQuestion) -> str:
        """Calculate time horizon from creation to close"""
        if question.time_to_resolution:
            days = question.time_to_resolution.days
            if days <= 7:
                return "1 week"
            elif days <= 30:
                return "1 month"
            elif days <= 90:
                return "3 months"
            elif days <= 180:
                return "6 months"
            elif days <= 365:
                return "1 year"
            else:
                return "2+ years"
        
        return "unknown"
    
    def save_benchmark_data(self, filename: str = "manifold_benchmark.json"):
        """Save collected benchmark data to file"""
        benchmark_data = {
            "created_at": datetime.now().isoformat(),
            "total_questions": len(self.questions),
            "benchmark_cases": self.create_benchmark_dataset()
        }
        
        with open(filename, 'w') as f:
            json.dump(benchmark_data, f, indent=2)
        
        print(f"Saved {len(benchmark_data['benchmark_cases'])} benchmark cases to {filename}")
        return filename


# Example usage and test
if __name__ == "__main__":
    benchmark = ManifoldBenchmark()
    
    print("Fetching resolved questions from Manifold Markets...")
    questions = benchmark.fetch_resolved_questions(limit=200, min_volume=50, days_back=60)
    
    print(f"Collected {len(questions)} resolved questions")
    print(f"AI-related questions: {len(benchmark.get_ai_related_questions())}")
    print(f"Tech-related questions: {len(benchmark.get_tech_questions())}")
    
    # Create and save benchmark dataset
    filename = benchmark.save_benchmark_data()
    print(f"Benchmark dataset saved to {filename}")