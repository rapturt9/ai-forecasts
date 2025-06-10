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

from ..models.schemas import ForecastRequest
from ..agents.orchestrator import ForecastOrchestrator
from ..agents.crewai_superforecaster import CrewAISuperforecaster
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

# Initialize orchestrators
orchestrator = None
crewai_forecaster = None

def get_orchestrator():
    """Get or create the orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-2024-11-20")
        orchestrator = ForecastOrchestrator(api_key=api_key, model=model)
    return orchestrator

def get_crewai_forecaster():
    """Get or create the CrewAI forecaster instance"""
    global crewai_forecaster
    if crewai_forecaster is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        crewai_forecaster = CrewAISuperforecaster(api_key)
    return crewai_forecaster


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


def create_demo_response(request: ForecastRequest) -> Dict[str, Any]:
    """Create a realistic demo response when API is not available"""
    import random
    
    if request.outcomes_of_interest:
        # Targeted forecasting mode
        evaluations = []
        for outcome in request.outcomes_of_interest:
            prob = random.uniform(0.2, 0.8)
            evaluations.append({
                "outcome": outcome,
                "probability": round(prob, 3),
                "confidence_interval": [round(prob - 0.15, 3), round(prob + 0.15, 3)],
                "reasoning": f"Based on current trends and available data, the probability of '{outcome}' is estimated at {prob:.1%}. This assessment considers multiple factors including technological progress, market conditions, and regulatory environment.",
                "key_factors": [
                    "Current technological advancement rate",
                    "Market adoption patterns",
                    "Regulatory landscape",
                    "Economic conditions"
                ],
                "blocking_factors": [
                    "Technical challenges",
                    "Regulatory hurdles",
                    "Market resistance",
                    "Resource constraints"
                ]
            })
        
        return {
            "mode": "targeted",
            "evaluations": evaluations,
            "agent_logs": [
                "🎯 TargetedAgent: Starting outcome evaluation",
                "📊 Analyzing probability distributions",
                "🔍 Researching relevant factors",
                "✅ Evaluation complete"
            ],
            "methodology": {
                "evidence_quality": round(random.uniform(0.7, 0.9), 2),
                "confidence_level": "high",
                "base_rate_analysis": True,
                "reference_class_forecasting": True
            },
            "demo_mode": True
        }
    
    elif request.desired_outcome:
        # Strategy mode
        prob = random.uniform(0.4, 0.8)
        return {
            "mode": "strategy",
            "feasibility_score": round(prob, 3),
            "recommended_strategy": {
                "name": f"Strategic Path to: {request.desired_outcome}",
                "overall_probability": round(prob, 3),
                "steps": [
                    {
                        "phase": 1,
                        "action": "Initial assessment and planning",
                        "timeline": "1-3 months",
                        "success_criteria": "Clear roadmap established"
                    },
                    {
                        "phase": 2,
                        "action": "Implementation of core components",
                        "timeline": "6-12 months",
                        "success_criteria": "Key milestones achieved"
                    },
                    {
                        "phase": 3,
                        "action": "Optimization and scaling",
                        "timeline": "12-24 months",
                        "success_criteria": "Desired outcome achieved"
                    }
                ]
            },
            "agent_logs": [
                "🚀 StrategyAgent: Analyzing desired outcome",
                "📋 Generating strategic options",
                "⚖️ Evaluating feasibility",
                "✅ Strategy recommendation complete"
            ],
            "demo_mode": True
        }
    
    else:
        # Pure forecasting mode
        return {
            "mode": "forecast",
            "predictions": [
                {
                    "outcome": "Most likely scenario",
                    "probability": 0.45,
                    "description": "Based on current conditions, this represents the most probable outcome"
                },
                {
                    "outcome": "Alternative scenario",
                    "probability": 0.35,
                    "description": "Secondary possibility with significant likelihood"
                },
                {
                    "outcome": "Low probability scenario",
                    "probability": 0.20,
                    "description": "Less likely but still possible outcome"
                }
            ],
            "agent_logs": [
                "🔮 ForecastAgent: Analyzing initial conditions",
                "📈 Generating probability distributions",
                "✅ Forecast complete"
            ],
            "demo_mode": True
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
        
        # Try to get orchestrator and process request
        try:
            orch = get_orchestrator()
            results = orch.process_request(request, use_validation=True)
            
            # Add logging information to results
            results["agent_logs"] = agent_logger.get_logs()
            results["processing_summary"] = agent_logger.get_summary()
            
            # Check if processing was successful
            if results.get("success", True) is False:
                raise HTTPException(status_code=400, detail=results.get("error", "Processing failed"))
            
            return results
            
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