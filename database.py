#!/usr/bin/env python3
"""
Database models and operations for AI Forecasting & Trading System
Uses SQLite with SQLAlchemy for real-time data storage and retrieval
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import uuid

# Database setup
DATABASE_URL = "sqlite:///ai_forecasts.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models

class ForecastSession(Base):
    __tablename__ = "forecast_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    background = Column(Text)
    prior_probability = Column(Float)
    time_horizon = Column(String)
    
    # Results
    forecast_probability = Column(Float)
    confidence_level = Column(String)
    reasoning = Column(Text)
    strategies = Column(JSON)  # List of strategies
    evidence_quality = Column(String)
    news_sources_count = Column(Integer)
    total_articles = Column(Integer)
    base_rate = Column(Float)
    
    # Metadata
    status = Column(String, default="processing")  # processing, completed, error
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    processing_time_seconds = Column(Float)

class TradingSession(Base):
    __tablename__ = "trading_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_type = Column(String, nullable=False)  # live, backtest
    initial_balance = Column(Float, default=1000.0)
    current_balance = Column(Float, default=1000.0)
    duration_hours = Column(Integer)
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    kelly_utilization = Column(Float, default=0.0)
    markets_analyzed = Column(Integer, default=0)
    
    # Status
    status = Column(String, default="starting")  # starting, running, completed, error, stopped
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    last_activity = Column(DateTime)

class AgentActivity(Base):
    __tablename__ = "agent_activities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)  # Links to trading session or monitoring session
    session_type = Column(String, default="trading")  # trading, monitoring
    
    # Agent action details
    agent_type = Column(String, nullable=False)  # Risk Assessment, Market Scout, etc.
    action = Column(String, nullable=False)  # BUY_YES, BUY_NO, ANALYZE, etc.
    market_question = Column(Text)
    confidence = Column(Float)
    edge = Column(Float)
    position_size = Column(Float)
    expected_return = Column(Float)
    
    # Results
    status = Column(String, default="pending")  # pending, success, error
    result_data = Column(JSON)  # Additional result data
    error_message = Column(Text)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    processing_time_ms = Column(Integer)

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(String, primary_key=True)
    question = Column(Text, nullable=False)
    probability = Column(Float, nullable=False)
    volume = Column(Integer, default=0)
    bettors = Column(Integer, default=0)
    
    # Market metadata
    source = Column(String, default="manifold")
    market_type = Column(String, default="binary")
    close_time = Column(DateTime)
    is_resolved = Column(Boolean, default=False)
    resolution = Column(String)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_fetched = Column(DateTime, default=datetime.utcnow)

class MonitoringSession(Base):
    __tablename__ = "monitoring_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="active")  # active, stopped
    
    # Metrics
    total_activities = Column(Integer, default=0)
    successful_activities = Column(Integer, default=0)
    error_activities = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime)
    last_activity = Column(DateTime)

# Database operations class
class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    # Forecast operations
    def create_forecast_session(self, question: str, background: str = "", 
                              prior_probability: Optional[float] = None,
                              time_horizon: str = "1 year") -> str:
        """Create a new forecast session"""
        with self.get_session() as db:
            session = ForecastSession(
                question=question,
                background=background,
                prior_probability=prior_probability,
                time_horizon=time_horizon,
                status="processing"
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session.id
    
    def update_forecast_session(self, session_id: str, **kwargs):
        """Update a forecast session with results"""
        with self.get_session() as db:
            session = db.query(ForecastSession).filter(ForecastSession.id == session_id).first()
            if session:
                for key, value in kwargs.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                
                if kwargs.get('status') == 'completed':
                    session.completed_at = datetime.utcnow()
                    if session.created_at:
                        session.processing_time_seconds = (session.completed_at - session.created_at).total_seconds()
                
                db.commit()
                db.refresh(session)
                return session
            return None
    
    def get_forecast_session(self, session_id: str) -> Optional[ForecastSession]:
        """Get a forecast session by ID"""
        with self.get_session() as db:
            return db.query(ForecastSession).filter(ForecastSession.id == session_id).first()
    
    def get_recent_forecasts(self, limit: int = 10) -> List[ForecastSession]:
        """Get recent forecast sessions"""
        with self.get_session() as db:
            return db.query(ForecastSession).order_by(ForecastSession.created_at.desc()).limit(limit).all()
    
    # Trading operations
    def create_trading_session(self, session_type: str, initial_balance: float = 1000.0,
                             duration_hours: Optional[int] = None) -> str:
        """Create a new trading session"""
        with self.get_session() as db:
            session = TradingSession(
                session_type=session_type,
                initial_balance=initial_balance,
                current_balance=initial_balance,
                duration_hours=duration_hours,
                status="starting"
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session.id
    
    def update_trading_session(self, session_id: str, **kwargs):
        """Update a trading session"""
        with self.get_session() as db:
            session = db.query(TradingSession).filter(TradingSession.id == session_id).first()
            if session:
                for key, value in kwargs.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                
                session.last_activity = datetime.utcnow()
                
                if kwargs.get('status') == 'running' and not session.started_at:
                    session.started_at = datetime.utcnow()
                elif kwargs.get('status') in ['completed', 'stopped', 'error']:
                    session.completed_at = datetime.utcnow()
                
                db.commit()
                db.refresh(session)
                return session
            return None
    
    def get_trading_session(self, session_id: str) -> Optional[TradingSession]:
        """Get a trading session by ID"""
        with self.get_session() as db:
            return db.query(TradingSession).filter(TradingSession.id == session_id).first()
    
    def get_all_trading_sessions(self) -> List[TradingSession]:
        """Get all trading sessions"""
        with self.get_session() as db:
            return db.query(TradingSession).order_by(TradingSession.created_at.desc()).all()
    
    # Agent activity operations
    def log_agent_activity(self, session_id: str, agent_type: str, action: str,
                          market_question: str = "", confidence: float = 0.0,
                          edge: float = 0.0, session_type: str = "trading", **kwargs) -> int:
        """Log an agent activity"""
        with self.get_session() as db:
            activity = AgentActivity(
                session_id=session_id,
                session_type=session_type,
                agent_type=agent_type,
                action=action,
                market_question=market_question,
                confidence=confidence,
                edge=edge,
                **kwargs
            )
            db.add(activity)
            db.commit()
            db.refresh(activity)
            return activity.id
    
    def update_agent_activity(self, activity_id: int, **kwargs):
        """Update an agent activity"""
        with self.get_session() as db:
            activity = db.query(AgentActivity).filter(AgentActivity.id == activity_id).first()
            if activity:
                for key, value in kwargs.items():
                    if hasattr(activity, key):
                        setattr(activity, key, value)
                db.commit()
                db.refresh(activity)
                return activity
            return None
    
    def get_session_activities(self, session_id: str, limit: int = 50) -> List[AgentActivity]:
        """Get activities for a session"""
        with self.get_session() as db:
            return db.query(AgentActivity).filter(
                AgentActivity.session_id == session_id
            ).order_by(AgentActivity.timestamp.desc()).limit(limit).all()
    
    def get_recent_activities(self, limit: int = 20) -> List[AgentActivity]:
        """Get recent activities across all sessions"""
        with self.get_session() as db:
            return db.query(AgentActivity).order_by(AgentActivity.timestamp.desc()).limit(limit).all()
    
    # Market data operations
    def upsert_market_data(self, market_id: str, question: str, probability: float,
                          volume: int = 0, bettors: int = 0, **kwargs):
        """Insert or update market data"""
        with self.get_session() as db:
            market = db.query(MarketData).filter(MarketData.id == market_id).first()
            if market:
                # Update existing
                market.question = question
                market.probability = probability
                market.volume = volume
                market.bettors = bettors
                market.updated_at = datetime.utcnow()
                market.last_fetched = datetime.utcnow()
                for key, value in kwargs.items():
                    if hasattr(market, key):
                        setattr(market, key, value)
            else:
                # Create new
                market = MarketData(
                    id=market_id,
                    question=question,
                    probability=probability,
                    volume=volume,
                    bettors=bettors,
                    **kwargs
                )
                db.add(market)
            
            db.commit()
            db.refresh(market)
            return market
    
    def get_all_markets(self, limit: int = 50) -> List[MarketData]:
        """Get all markets"""
        with self.get_session() as db:
            return db.query(MarketData).order_by(MarketData.updated_at.desc()).limit(limit).all()
    
    # Monitoring operations
    def create_monitoring_session(self) -> str:
        """Create a new monitoring session"""
        with self.get_session() as db:
            session = MonitoringSession(status="active")
            db.add(session)
            db.commit()
            db.refresh(session)
            return session.id
    
    def update_monitoring_session(self, session_id: str, **kwargs):
        """Update a monitoring session"""
        with self.get_session() as db:
            session = db.query(MonitoringSession).filter(MonitoringSession.id == session_id).first()
            if session:
                for key, value in kwargs.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                
                if kwargs.get('status') == 'stopped':
                    session.stopped_at = datetime.utcnow()
                
                db.commit()
                db.refresh(session)
                return session
            return None

# Global database manager instance
db_manager = DatabaseManager()

def init_database():
    """Initialize the database"""
    print("🗄️ Initializing database...")
    db_manager.create_tables()
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    init_database()