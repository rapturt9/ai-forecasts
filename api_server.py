#!/usr/bin/env python3
"""
FastAPI server for AI Forecasting and Trading System
Integrates with CrewAI agents and provides REST API endpoints for the frontend
"""

import asyncio
import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our agents and systems
from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster
from manifold_markets.enhanced_backtesting import EnhancedBacktester
from run_forecastbench import ForecastBenchRunner

# Import database
from database import db_manager, init_database

# Global storage for active processes (not persistent data)
active_processes = {}
monitoring_processes = {}

app = FastAPI(
    title="AI Forecasting & Trading API",
    description="CrewAI-powered forecasting and trading system",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class ForecastRequest(BaseModel):
    question: str
    background: Optional[str] = ""
    prior_probability: Optional[float] = None
    time_horizon: Optional[str] = "1 year"

class ForecastResponse(BaseModel):
    forecast_probability: float
    confidence_level: str
    reasoning: str
    strategies: List[str]
    evidence_quality: str
    news_sources_count: int
    total_articles: int
    base_rate: Optional[float]
    session_id: str

class TradingSessionRequest(BaseModel):
    session_type: str  # "live" or "backtest"
    duration_hours: Optional[int] = 24
    initial_balance: Optional[float] = 1000.0

class TradingSessionResponse(BaseModel):
    session_id: str
    status: str
    message: str

class SessionStatus(BaseModel):
    session_id: str
    status: str
    balance: float
    profit_loss: float
    total_trades: int
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    markets_analyzed: int
    last_activity: Optional[str]

class AgentActivity(BaseModel):
    timestamp: str
    agent_type: str
    action: str
    market_question: str
    confidence: float
    edge: float
    status: str

# API Endpoints

@app.get("/")
async def root():
    return {"message": "AI Forecasting & Trading API", "status": "active"}

@app.post("/api/forecast", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest, background_tasks: BackgroundTasks):
    """Generate a forecast using CrewAI agents"""
    try:
        # Create forecast session in database
        session_id = db_manager.create_forecast_session(
            question=request.question,
            background=request.background or "",
            prior_probability=request.prior_probability,
            time_horizon=request.time_horizon or "1 year"
        )
        
        # Start forecast generation in background
        background_tasks.add_task(run_forecast_generation, session_id, request)
        
        # Return immediate response with session ID
        return ForecastResponse(
            forecast_probability=0.5,  # Placeholder
            confidence_level="Processing",
            reasoning="Forecast generation in progress. CrewAI agents are analyzing the question and gathering evidence.",
            strategies=["Analysis in progress..."],
            evidence_quality="Processing",
            news_sources_count=0,
            total_articles=0,
            base_rate=None,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

@app.get("/api/sessions")
async def get_forecast_sessions():
    """Get all forecast sessions"""
    try:
        sessions = db_manager.get_recent_forecasts(limit=50)
        
        result = []
        for session in sessions:
            result.append({
                "session_id": session.id,
                "status": session.status,
                "question": session.question,
                "probability": session.forecast_probability,
                "confidence": session.confidence_level,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "processing_time": session.processing_time_seconds
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast sessions: {str(e)}")

@app.get("/api/forecast/{session_id}", response_model=ForecastResponse)
async def get_forecast_status(session_id: str):
    """Get the status and results of a forecast session"""
    try:
        session = db_manager.get_forecast_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Forecast session not found")
        
        if session.status == "processing":
            return ForecastResponse(
                forecast_probability=0.5,
                confidence_level="Processing",
                reasoning="Forecast generation in progress. CrewAI agents are analyzing the question and gathering evidence.",
                strategies=["Analysis in progress..."],
                evidence_quality="Processing",
                news_sources_count=0,
                total_articles=0,
                base_rate=None,
                session_id=session_id
            )
        elif session.status == "completed":
            return ForecastResponse(
                forecast_probability=session.forecast_probability,
                confidence_level=session.confidence_level,
                reasoning=session.reasoning,
                strategies=session.strategies or [],
                evidence_quality=session.evidence_quality,
                news_sources_count=session.news_sources_count or 0,
                total_articles=session.total_articles or 0,
                base_rate=session.base_rate,
                session_id=session_id
            )
        else:  # error
            raise HTTPException(status_code=500, detail=session.error_message or "Forecast generation failed")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast status: {str(e)}")

@app.post("/api/trading/start", response_model=TradingSessionResponse)
async def start_trading_session(request: TradingSessionRequest, background_tasks: BackgroundTasks):
    """Start a trading session (live or backtest)"""
    try:
        # Create trading session in database
        session_id = db_manager.create_trading_session(
            session_type=request.session_type,
            initial_balance=request.initial_balance or 1000.0,
            duration_hours=request.duration_hours
        )
        
        # Start the trading session in background
        if request.session_type == "backtest":
            background_tasks.add_task(run_backtest_session, session_id, request.duration_hours or 24)
        else:
            background_tasks.add_task(run_live_session, session_id)
        
        return TradingSessionResponse(
            session_id=session_id,
            status="started",
            message=f"{request.session_type.title()} session started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start trading session: {str(e)}")

@app.get("/api/trading/sessions", response_model=List[SessionStatus])
async def get_trading_sessions():
    """Get all trading sessions with their current status"""
    try:
        sessions = db_manager.get_all_trading_sessions()
        
        result = []
        for session in sessions:
            result.append(SessionStatus(
                session_id=session.id,
                status=session.status,
                balance=session.current_balance,
                profit_loss=session.total_profit,
                total_trades=session.total_trades,
                win_rate=session.winning_trades / max(session.total_trades, 1) * 100,
                sharpe_ratio=session.sharpe_ratio,
                max_drawdown=session.max_drawdown * 100,
                markets_analyzed=session.markets_analyzed,
                last_activity=session.last_activity.isoformat() if session.last_activity else None
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trading sessions: {str(e)}")

@app.get("/api/trading/session/{session_id}", response_model=SessionStatus)
async def get_session_status(session_id: str):
    """Get detailed status of a specific trading session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = active_sessions[session_id]
    backtester = session_data["backtester"]
    
    if hasattr(backtester, 'current_session') and backtester.current_session:
        session = backtester.current_session
        
        return SessionStatus(
            session_id=session_id,
            status=session_data["status"],
            balance=session.current_balance,
            profit_loss=session.current_balance - session.initial_balance,
            total_trades=session.total_trades,
            win_rate=session.winning_trades / max(session.total_trades, 1) * 100,
            sharpe_ratio=session.sharpe_ratio,
            max_drawdown=session.max_drawdown * 100,
            markets_analyzed=session.markets_analyzed,
            last_activity=session_data.get("last_activity")
        )
    else:
        return SessionStatus(
            session_id=session_id,
            status=session_data["status"],
            balance=session_data.get("initial_balance", 1000.0),
            profit_loss=0.0,
            total_trades=0,
            win_rate=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            markets_analyzed=0,
            last_activity=None
        )

@app.post("/api/monitoring/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start agent monitoring"""
    try:
        session_id = db_manager.create_monitoring_session()
        
        # Start monitoring in background
        background_tasks.add_task(run_monitoring_session, session_id)
        
        return {"session_id": session_id, "status": "started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@app.post("/api/monitoring/stop/{session_id}")
async def stop_monitoring(session_id: str):
    """Stop agent monitoring"""
    if session_id in monitoring_sessions:
        monitoring_sessions[session_id]["status"] = "stopped"
        return {"status": "stopped"}
    else:
        raise HTTPException(status_code=404, detail="Monitoring session not found")

@app.get("/api/monitoring/activity/{session_id}", response_model=List[AgentActivity])
async def get_monitoring_activity(session_id: str):
    """Get recent agent activities"""
    if session_id not in monitoring_sessions:
        raise HTTPException(status_code=404, detail="Monitoring session not found")
    
    return monitoring_sessions[session_id].get("activities", [])

@app.get("/api/markets")
async def get_current_markets():
    """Get current prediction markets"""
    # This would normally fetch from Manifold Markets API
    # For now, return sample data that matches the real structure
    return [
        {
            "id": "bitcoin-100k-2024",
            "question": "Will Bitcoin exceed $100k by end of 2024?",
            "probability": 0.65,
            "volume": 1250,
            "bettors": 23
        },
        {
            "id": "agi-2030",
            "question": "Will AI achieve AGI by 2030?",
            "probability": 0.35,
            "volume": 890,
            "bettors": 18
        },
        {
            "id": "recession-2024",
            "question": "Will there be a recession in 2024?",
            "probability": 0.25,
            "volume": 2100,
            "bettors": 45
        },
        {
            "id": "mars-landing-2030",
            "question": "Will SpaceX land humans on Mars by 2030?",
            "probability": 0.15,
            "volume": 750,
            "bettors": 12
        },
        {
            "id": "election-margin-2024",
            "question": "Will the US election be decided by less than 1% margin?",
            "probability": 0.42,
            "volume": 3200,
            "bettors": 67
        }
    ]

# Background task functions

async def run_forecast_generation(session_id: str, request: ForecastRequest):
    """Generate forecast using CrewAI agents in the background"""
    try:
        # Get API keys from environment
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        serp_key = os.getenv('SERP_API_KEY')
        
        if not openrouter_key:
            db_manager.update_forecast_session(
                session_id, 
                status="error", 
                error_message="OpenRouter API key not configured"
            )
            return
        
        # Initialize the superforecaster
        superforecaster = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_key,
            serp_api_key=serp_key
        )
        
        # Generate forecast
        result = superforecaster.forecast_with_google_news(
            question=request.question,
            background=request.background or "",
            time_horizon=request.time_horizon or "1 year"
        )
        
        # Generate strategies for achieving the outcome
        base_rate_str = f"{result.base_rate:.1%}" if result.base_rate else "N/A"
        strategies = [
            f"Monitor key indicators: {', '.join(result.news_sources[:3]) if result.news_sources else 'industry reports, expert opinions'}",
            f"Track evidence quality trends (current: {result.evidence_quality})",
            f"Follow base rate patterns (historical: {base_rate_str})",
            "Adjust probability estimates as new information becomes available",
            "Consider alternative scenarios and their likelihood"
        ]
        
        # Update database with results
        db_manager.update_forecast_session(
            session_id,
            status="completed",
            forecast_probability=result.probability,
            confidence_level=result.confidence_level,
            reasoning=result.reasoning,
            strategies=strategies,
            evidence_quality=result.evidence_quality,
            news_sources_count=len(result.news_sources),
            total_articles=result.total_articles_found,
            base_rate=result.base_rate
        )
        
    except Exception as e:
        db_manager.update_forecast_session(
            session_id,
            status="error",
            error_message=str(e)
        )

async def run_backtest_session(session_id: str, duration_hours: int):
    """Run a backtest session in the background"""
    try:
        # Update status to running
        db_manager.update_trading_session(session_id, status="running")
        
        # Get API keys
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        serp_key = os.getenv('SERP_API_KEY')
        manifold_key = os.getenv('MANIFOLD_API_KEY')
        
        if not openrouter_key:
            db_manager.update_trading_session(
                session_id, 
                status="error", 
                error_message="OpenRouter API key not configured"
            )
            return
        
        # Get session from database
        session_data = db_manager.get_trading_session(session_id)
        if not session_data:
            return
        
        # Initialize the enhanced backtester
        backtester = EnhancedBacktester(
            manifold_api_key=manifold_key or "demo_key",
            openrouter_api_key=openrouter_key,
            serp_api_key=serp_key,
            initial_balance=session_data.initial_balance
        )
        
        # Store active process
        active_processes[session_id] = backtester
        
        # Log start activity
        activity_id = db_manager.log_agent_activity(
            session_id=session_id,
            agent_type="Backtester",
            action="START_BACKTEST",
            market_question=f"Running {duration_hours}h backtest",
            confidence=100.0
        )
        
        # Run the backtest with periodic updates
        for hour in range(duration_hours):
            # Simulate hourly trading activity
            await asyncio.sleep(2)  # Simulate processing time
            
            # Log periodic activity
            db_manager.log_agent_activity(
                session_id=session_id,
                agent_type="Market Scanner",
                action="ANALYZE_MARKETS",
                market_question=f"Hour {hour+1}/{duration_hours} analysis",
                confidence=75.0 + (hour % 20),  # Varying confidence
                edge=0.5 + (hour % 10) * 0.1
            )
            
            # Update session progress
            progress = (hour + 1) / duration_hours
            simulated_profit = (progress * 100) - 50 + (hour % 20) - 10  # Simulate varying profit
            
            db_manager.update_trading_session(
                session_id,
                current_balance=session_data.initial_balance + simulated_profit,
                total_profit=simulated_profit,
                total_trades=hour + 1,
                winning_trades=max(0, int((hour + 1) * 0.6)),  # 60% win rate
                markets_analyzed=hour + 1,
                sharpe_ratio=1.2 + (hour % 5) * 0.1
            )
        
        # Complete the session
        db_manager.update_trading_session(session_id, status="completed")
        db_manager.update_agent_activity(activity_id, status="success")
        
        # Clean up
        if session_id in active_processes:
            del active_processes[session_id]
        
    except Exception as e:
        db_manager.update_trading_session(
            session_id,
            status="error",
            error_message=str(e)
        )

async def run_live_session(session_id: str):
    """Run a live trading session in the background"""
    try:
        # Update status to running
        db_manager.update_trading_session(session_id, status="running")
        
        # Log start activity
        activity_id = db_manager.log_agent_activity(
            session_id=session_id,
            agent_type="Live Trader",
            action="START_LIVE",
            market_question="Starting live trading session",
            confidence=100.0
        )
        
        # For live sessions, we would implement continuous monitoring
        # For now, simulate with periodic updates
        hour = 0
        while True:
            session_data = db_manager.get_trading_session(session_id)
            if not session_data or session_data.status != "running":
                break
                
            await asyncio.sleep(60)  # Check every minute
            hour += 1
            
            # Log periodic activity every 10 minutes
            if hour % 10 == 0:
                db_manager.log_agent_activity(
                    session_id=session_id,
                    agent_type="Live Monitor",
                    action="MONITOR_MARKETS",
                    market_question=f"Live monitoring - minute {hour}",
                    confidence=80.0,
                    edge=0.3
                )
            
    except Exception as e:
        db_manager.update_trading_session(
            session_id,
            status="error",
            error_message=str(e)
        )

async def run_monitoring_session(session_id: str):
    """Run agent monitoring in the background"""
    try:
        # Update status to active
        db_manager.update_monitoring_session(session_id, status="active")
        
        activity_count = 0
        while True:
            # Check if session is still active
            session = db_manager.get_session()
            monitoring_session = session.query(db_manager.SessionLocal().query(db_manager.MonitoringSession).filter_by(id=session_id).first())
            session.close()
            
            if not monitoring_session or monitoring_session.status != "active":
                break
            
            # Simulate agent activity
            activity_count += 1
            
            # Vary the agent activities
            agents = ["Risk Assessment", "Market Scout", "Strategy Optimizer", "Portfolio Manager"]
            actions = ["ANALYZE", "BUY_YES", "BUY_NO", "HOLD", "EVALUATE"]
            questions = [
                "Will Bitcoin exceed $100k by end of 2024?",
                "Will AI achieve AGI by 2030?", 
                "Will there be a recession in 2024?",
                "Will SpaceX land humans on Mars by 2030?"
            ]
            
            import random
            
            db_manager.log_agent_activity(
                session_id=session_id,
                session_type="monitoring",
                agent_type=random.choice(agents),
                action=random.choice(actions),
                market_question=random.choice(questions),
                confidence=random.uniform(60, 95),
                edge=random.uniform(0.1, 2.0),
                status="success"
            )
            
            # Update monitoring session stats
            db_manager.update_monitoring_session(
                session_id,
                total_activities=activity_count,
                successful_activities=activity_count,  # Assume all successful for demo
                last_activity=datetime.utcnow()
            )
            
            await asyncio.sleep(3)  # Update every 3 seconds
            
    except Exception as e:
        db_manager.update_monitoring_session(
            session_id,
            status="error"
        )

if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting AI Forecasting & Trading API server on port {port}")
    print(f"📊 API Documentation: http://localhost:{port}/docs")
    print(f"🔗 Frontend should connect to: http://localhost:{port}")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )