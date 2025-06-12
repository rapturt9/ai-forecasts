"""Pydantic schemas for API requests and responses"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ForecastRequest(BaseModel):
    """Request model for forecast generation"""
    question: str = Field(..., description="The forecasting question")
    context: Optional[str] = Field(None, description="Additional context for the question")
    deadline: Optional[str] = Field(None, description="Deadline for the forecast (YYYY-MM-DD)")
    use_google_news: bool = Field(True, description="Whether to use Google News for research")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Will the US stock market be higher at the end of 2025?",
                "context": "Consider current economic indicators",
                "deadline": "2025-12-31",
                "use_google_news": True
            }
        }


class ForecastResponse(BaseModel):
    """Response model for forecast results"""
    question: str
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability between 0 and 1")
    reasoning: str
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in the forecast")
    sources: List[str] = Field(default_factory=list, description="Sources used for the forecast")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the forecast was generated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Will the US stock market be higher at the end of 2025?",
                "probability": 0.65,
                "reasoning": "Based on historical trends and current economic indicators...",
                "confidence": 0.7,
                "sources": ["Reuters", "Bloomberg", "Financial Times"],
                "metadata": {"model_version": "1.0", "search_queries": 5},
                "timestamp": "2025-06-12T10:00:00Z"
            }
        }


class MarketAnalysisRequest(BaseModel):
    """Request model for market analysis"""
    market_id: str = Field(..., description="Manifold market ID")
    min_edge: float = Field(0.05, description="Minimum edge required for trading")
    
    
class TradingDecision(BaseModel):
    """Trading decision model"""
    action: str = Field(..., description="Trading action: BUY, SELL, or HOLD")
    probability: float = Field(..., ge=0.0, le=1.0)
    market_probability: float = Field(..., ge=0.0, le=1.0)
    edge: float = Field(..., description="Expected edge")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    recommended_amount: Optional[float] = Field(None, description="Recommended bet amount")