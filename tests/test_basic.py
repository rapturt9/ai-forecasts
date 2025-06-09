"""Basic tests for the AI Forecasting System"""

import pytest
from src.ai_forecasts.models.schemas import ForecastRequest, ForecastMode
from src.ai_forecasts.agents.orchestrator import ForecastOrchestrator


def test_forecast_request_creation():
    """Test creating a basic forecast request"""
    request = ForecastRequest(
        initial_conditions="Test conditions",
        time_horizon="1 year"
    )
    
    assert request.initial_conditions == "Test conditions"
    assert request.time_horizon == "1 year"
    assert request.outcomes_of_interest is None
    assert request.desired_outcome is None


def test_forecast_request_modes():
    """Test mode classification logic"""
    
    # Pure forecast mode
    request1 = ForecastRequest(time_horizon="1 year")
    
    # Targeted mode
    request2 = ForecastRequest(
        time_horizon="1 year",
        outcomes_of_interest=["outcome1", "outcome2"]
    )
    
    # Strategy mode
    request3 = ForecastRequest(
        time_horizon="1 year",
        desired_outcome="achieve goal"
    )
    
    # Test that requests are created correctly
    assert request1.outcomes_of_interest is None
    assert request1.desired_outcome is None
    
    assert request2.outcomes_of_interest == ["outcome1", "outcome2"]
    assert request2.desired_outcome is None
    
    assert request3.desired_outcome == "achieve goal"


def test_orchestrator_initialization():
    """Test that orchestrator can be initialized"""
    try:
        # This might fail if no API key is available, which is expected
        orchestrator = ForecastOrchestrator()
        assert orchestrator is not None
    except ValueError as e:
        # Expected if no API key is configured
        assert "API key" in str(e)


if __name__ == "__main__":
    pytest.main([__file__])