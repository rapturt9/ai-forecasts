"""FastAPI application for the AI Forecasting & Strategy System"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ..models.schemas import ForecastRequest, ForecastResponse
from ..agents.google_news_superforecaster import GoogleNewsSuperforecaster
from ..utils.agent_logger import agent_logger

# Initialize FastAPI app
app = FastAPI(
    title="AI Forecasting & Strategy System",
    description="An AI-powered system for forecasting outcomes and generating strategies",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize forecaster
google_news_forecaster = None

def get_google_news_forecaster():
    """Get or create the Google News forecaster instance"""
    global google_news_forecaster
    if google_news_forecaster is None:
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        serp_api_key = os.getenv("SERP_API_KEY")
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        google_news_forecaster = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_api_key,
            serp_api_key=serp_api_key
        )
    return google_news_forecaster


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "AI Forecasting & Strategy System",
        "version": "0.1.0",
        "description": "Generate forecasts and strategies using AI agents",
        "endpoints": {
            "forecast": "/forecast - Main forecasting endpoint",
            "health": "/health - System health check",
            "docs": "/docs - API documentation"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test if we can initialize the forecaster
        forecaster = get_google_news_forecaster()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "google_news_forecaster": "initialized",
                "llm_client": "configured"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


def create_demo_response(request: ForecastRequest) -> Dict[str, Any]:
    """Create a realistic demo response when API is not available"""
    import random
    
    return {
        "question": request.question,
        "probability": round(random.uniform(0.3, 0.8), 2),
        "reasoning": f"Demo response for: {request.question}. This is a placeholder response when the full forecasting system is not available.",
        "confidence": round(random.uniform(0.5, 0.9), 2),
        "sources": ["Demo Source 1", "Demo Source 2"],
        "metadata": {"mode": "demo", "timestamp": datetime.now().isoformat()},
        "timestamp": datetime.now().isoformat()
    }


@app.post("/forecast")
async def forecast(request: ForecastRequest, background_tasks: BackgroundTasks):
    """
    Main forecasting endpoint that handles all three modes:
    - Pure Forecasting: Predict likely outcomes
    - Targeted Forecasting: Evaluate specific outcomes
    - Strategy Generation: Find paths to desired outcomes
    """
    try:
        # Start logging session
        mode = "forecast"
        if request.outcomes_of_interest:
            mode = "targeted"
        elif request.desired_outcome:
            mode = "strategy"
        
        agent_logger.start_session(mode, request.dict())
        
        # Try to get forecaster and process request
        try:
            forecaster = get_google_news_forecaster()
            result = forecaster.forecast_with_google_news(request.question)
            
            # Convert to API response format
            response = {
                "question": result.question,
                "probability": result.probability,
                "reasoning": result.reasoning,
                "confidence": getattr(result, 'confidence', 0.7),
                "sources": result.sources,
                "metadata": {"mode": "google_news", "timestamp": datetime.now().isoformat()},
                "timestamp": datetime.now().isoformat()
            }
            
            return response
            
        except Exception as api_error:
            # If API fails, return demo response
            print(f"API error, using demo mode: {api_error}")
            return create_demo_response(request)
        
    except Exception as e:
        # Last resort: return demo response
        print(f"Fallback to demo mode: {e}")
        return create_demo_response(request)


@app.post("/forecast/quick")
async def forecast_quick(request: ForecastRequest):
    """
    Quick forecasting endpoint without validation (faster response)
    """
    try:
        # Try to get orchestrator and process request
        try:
            orch = get_orchestrator()
            results = orch.process_request(request, use_validation=False)
            
            if results.get("success", True) is False:
                raise HTTPException(status_code=400, detail=results.get("error", "Processing failed"))
            
            return results
            
        except Exception as api_error:
            # If API fails, return demo response
            print(f"API error in quick mode, using demo: {api_error}")
            return create_demo_response(request)
        
    except Exception as e:
        # Last resort: return demo response
        print(f"Fallback to demo mode in quick: {e}")
        return create_demo_response(request)


@app.post("/forecast/raw")
async def forecast_raw(request_data: Dict[str, Any]):
    """
    Raw forecasting endpoint that accepts any JSON structure
    """
    try:
        orch = get_orchestrator()
        results = orch.process_request_dict(request_data, use_validation=True)
        
        if results.get("success", True) is False:
            raise HTTPException(status_code=400, detail=results.get("error", "Processing failed"))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/forecast/crewai")
async def forecast_crewai(request: ForecastRequest, background_tasks: BackgroundTasks):
    """
    CrewAI multi-agent superforecaster endpoint with enhanced methodology
    """
    try:
        # Start logging session
        mode = "crewai_forecast"
        if request.outcomes_of_interest:
            mode = "crewai_targeted"
        elif request.desired_outcome:
            mode = "crewai_strategy"
        
        agent_logger.start_session(mode, request.dict())
        
        # Get CrewAI forecaster
        forecaster = get_crewai_forecaster()
        
        # Determine the question based on mode
        if request.desired_outcome:
            question = f"How can we achieve: {request.desired_outcome}"
            background = f"Constraints: {', '.join(request.constraints or [])}"
        elif request.outcomes_of_interest:
            question = f"What is the probability of these outcomes: {', '.join(request.outcomes_of_interest)}"
            background = f"Initial conditions: {request.initial_conditions or 'Current state'}"
        else:
            question = f"What are the most likely outcomes in the next {request.time_horizon}?"
            background = f"Initial conditions: {request.initial_conditions or 'Current state'}"
        
        # Process with CrewAI
        forecast_result = forecaster.forecast(
            question=question,
            background=background,
            cutoff_date=None,  # Use current date
            time_horizon=request.time_horizon
        )
        
        # Convert to API response format
        results = {
            "mode": mode,
            "question": question,
            "time_horizon": request.time_horizon,
            "methodology": "crewai_superforecaster",
            "forecast": {
                "probability": forecast_result.probability,
                "confidence_level": forecast_result.confidence_level,
                "reasoning": forecast_result.reasoning,
                "base_rate": forecast_result.base_rate,
                "evidence_quality": forecast_result.evidence_quality,
                "methodology_components": forecast_result.methodology_components
            },
            "agent_analysis": forecast_result.full_analysis,
            "agent_logs": agent_logger.get_logs(),
            "processing_summary": agent_logger.get_summary(),
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
        return results
        
    except Exception as e:
        agent_logger.log("error", f"CrewAI forecast failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CrewAI forecast error: {str(e)}")


@app.get("/modes")
async def get_modes():
    """Get information about available forecasting modes"""
    return {
        "modes": {
            "pure_forecast": {
                "description": "Generate probability distributions for likely outcomes",
                "required_fields": ["initial_conditions", "time_horizon"],
                "optional_fields": ["constraints"],
                "example": {
                    "initial_conditions": "AI lab has developed GPT-4 level model",
                    "time_horizon": "2 years"
                }
            },
            "targeted": {
                "description": "Evaluate specific outcomes of interest",
                "required_fields": ["initial_conditions", "outcomes_of_interest", "time_horizon"],
                "optional_fields": ["constraints"],
                "example": {
                    "initial_conditions": "Current AI capabilities as of 2024",
                    "outcomes_of_interest": ["AGI achieved", "AI regulation passed"],
                    "time_horizon": "5 years"
                }
            },
            "strategy": {
                "description": "Generate optimal paths to achieve desired outcomes",
                "required_fields": ["initial_conditions", "desired_outcome", "time_horizon"],
                "optional_fields": ["constraints"],
                "example": {
                    "initial_conditions": "Small AI startup with $1M funding",
                    "desired_outcome": "Successful AI product with 1M users",
                    "time_horizon": "3 years",
                    "constraints": ["Limited budget", "Small team"]
                }
            }
        }
    }


@app.get("/examples")
async def get_examples():
    """Get example requests for each mode"""
    return {
        "pure_forecast_example": {
            "initial_conditions": "OpenAI has released GPT-4, competition is increasing, regulatory attention is growing",
            "time_horizon": "18 months"
        },
        "targeted_example": {
            "initial_conditions": "Current state of AI development in 2024",
            "outcomes_of_interest": [
                "Major AI breakthrough announced",
                "Significant AI regulation enacted",
                "AI safety incident occurs"
            ],
            "time_horizon": "2 years"
        },
        "strategy_example": {
            "initial_conditions": "AI research lab with 50 researchers, $10M annual budget, focus on language models",
            "desired_outcome": "Develop and deploy safe AGI system",
            "time_horizon": "5 years",
            "constraints": [
                "Must maintain safety standards",
                "Limited compute budget",
                "Regulatory compliance required"
            ]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=12000,
        reload=True,
        log_level="info"
    )