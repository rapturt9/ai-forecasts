"""FastAPI application for the AI Forecasting & Strategy System"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import os
from datetime import datetime

from ..models.schemas import ForecastRequest
from ..agents.orchestrator import ForecastOrchestrator
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

# Initialize orchestrator
orchestrator = None

def get_orchestrator():
    """Get or create the orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("DEFAULT_MODEL", "anthropic/claude-3-haiku")
        orchestrator = ForecastOrchestrator(api_key=api_key, model=model)
    return orchestrator


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
        # Test if we can initialize the orchestrator
        orch = get_orchestrator()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "orchestrator": "initialized",
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
        
        # Get orchestrator and process request
        orch = get_orchestrator()
        results = orch.process_request(request, use_validation=True)
        
        # Add logging information to results
        results["agent_logs"] = agent_logger.get_logs()
        results["processing_summary"] = agent_logger.get_summary()
        
        # Check if processing was successful
        if results.get("success", True) is False:
            raise HTTPException(status_code=400, detail=results.get("error", "Processing failed"))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/forecast/quick")
async def forecast_quick(request: ForecastRequest):
    """
    Quick forecasting endpoint without validation (faster response)
    """
    try:
        orch = get_orchestrator()
        results = orch.process_request(request, use_validation=False)
        
        if results.get("success", True) is False:
            raise HTTPException(status_code=400, detail=results.get("error", "Processing failed"))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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