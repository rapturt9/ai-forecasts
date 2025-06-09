"""Streamlit frontend for the AI Forecasting & Strategy System"""

import streamlit as st
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

# Page configuration
st.set_page_config(
    page_title="AI Forecasting & Strategy System",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_BASE_URL = "http://localhost:12000"

def main():
    """Main Streamlit application"""
    
    # Title and description
    st.title("🔮 AI Forecasting & Strategy System")
    st.markdown("""
    An AI-powered system that performs bidirectional analysis: forecasting probable outcomes 
    from initial conditions AND recommending optimal strategies to achieve desired outcomes.
    """)
    
    # Sidebar for mode selection and configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Mode selection
        mode = st.radio(
            "Select Analysis Mode:",
            [
                "🎯 Forecast Outcomes",
                "📊 Evaluate Specific Outcomes", 
                "🚀 Find Path to Desired Outcome"
            ],
            help="Choose the type of analysis you want to perform"
        )
        
        st.divider()
        
        # Advanced options
        st.subheader("Advanced Options")
        use_validation = st.checkbox("Enable validation", value=True, help="Adds quality checks but takes longer")
        show_raw_output = st.checkbox("Show raw output", value=False, help="Display technical details")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input form based on selected mode
        if "Forecast Outcomes" in mode:
            results = render_forecast_mode(use_validation)
        elif "Evaluate Specific Outcomes" in mode:
            results = render_targeted_mode(use_validation)
        elif "Find Path to Desired Outcome" in mode:
            results = render_strategy_mode(use_validation)
    
    with col2:
        # Help and examples
        render_help_panel(mode)
    
    # Display results if available
    if 'results' in locals() and results:
        st.divider()
        render_results(results, show_raw_output)


def render_forecast_mode(use_validation: bool) -> Dict[str, Any]:
    """Render the pure forecasting mode interface"""
    
    st.header("🎯 Forecast Likely Outcomes")
    st.markdown("Predict the most probable outcomes given current conditions.")
    
    with st.form("forecast_form"):
        # Input fields
        initial_conditions = st.text_area(
            "Initial Conditions",
            placeholder="Describe the current situation...",
            height=100,
            help="Leave blank to use current date as baseline"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            time_horizon = st.selectbox(
                "Time Horizon",
                ["1 month", "3 months", "6 months", "1 year", "2 years", "5 years"],
                index=3
            )
        
        with col2:
            constraints = st.text_area(
                "Constraints (optional)",
                placeholder="e.g., budget < $1M, no regulatory changes",
                height=60
            )
        
        submitted = st.form_submit_button("Generate Forecast", type="primary")
    
    if submitted:
        # Prepare request
        request_data = {
            "time_horizon": time_horizon
        }
        
        if initial_conditions.strip():
            request_data["initial_conditions"] = initial_conditions
        
        if constraints.strip():
            request_data["constraints"] = [c.strip() for c in constraints.split(",") if c.strip()]
        
        # Make API call
        with st.spinner("Generating forecast..."):
            results = make_api_call("/forecast", request_data, use_validation)
            return results
    
    return None


def render_targeted_mode(use_validation: bool) -> Dict[str, Any]:
    """Render the targeted forecasting mode interface"""
    
    st.header("📊 Evaluate Specific Outcomes")
    st.markdown("Assess the probability and feasibility of specific outcomes of interest.")
    
    with st.form("targeted_form"):
        # Input fields
        initial_conditions = st.text_area(
            "Initial Conditions",
            placeholder="Describe the current situation...",
            height=100
        )
        
        outcomes_text = st.text_area(
            "Outcomes to Evaluate",
            placeholder="Enter one outcome per line:\n- AI breakthrough announced\n- New regulation passed\n- Market crash occurs",
            height=120,
            help="Enter each outcome on a separate line"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            time_horizon = st.selectbox(
                "Time Horizon",
                ["1 month", "3 months", "6 months", "1 year", "2 years", "5 years"],
                index=3
            )
        
        with col2:
            constraints = st.text_area(
                "Constraints (optional)",
                placeholder="e.g., budget < $1M",
                height=60
            )
        
        submitted = st.form_submit_button("Evaluate Outcomes", type="primary")
    
    if submitted:
        if not initial_conditions.strip():
            st.error("Please provide initial conditions")
            return None
        
        if not outcomes_text.strip():
            st.error("Please provide outcomes to evaluate")
            return None
        
        # Parse outcomes
        outcomes = [line.strip().lstrip("- ") for line in outcomes_text.split("\n") if line.strip()]
        
        # Prepare request
        request_data = {
            "initial_conditions": initial_conditions,
            "outcomes_of_interest": outcomes,
            "time_horizon": time_horizon
        }
        
        if constraints.strip():
            request_data["constraints"] = [c.strip() for c in constraints.split(",") if c.strip()]
        
        # Make API call
        with st.spinner("Evaluating outcomes..."):
            results = make_api_call("/forecast", request_data, use_validation)
            return results
    
    return None


def render_strategy_mode(use_validation: bool) -> Dict[str, Any]:
    """Render the strategy generation mode interface"""
    
    st.header("🚀 Find Path to Desired Outcome")
    st.markdown("Generate optimal strategies to achieve your desired outcome.")
    
    with st.form("strategy_form"):
        # Input fields
        initial_conditions = st.text_area(
            "Current Situation",
            placeholder="Describe where you are now...",
            height=100
        )
        
        desired_outcome = st.text_area(
            "Desired Outcome",
            placeholder="Describe what you want to achieve...",
            height=80
        )
        
        col1, col2 = st.columns(2)
        with col1:
            time_horizon = st.selectbox(
                "Time Horizon",
                ["1 month", "3 months", "6 months", "1 year", "2 years", "5 years"],
                index=3
            )
        
        with col2:
            constraints = st.text_area(
                "Constraints",
                placeholder="e.g., limited budget, small team, regulatory requirements",
                height=60
            )
        
        submitted = st.form_submit_button("Generate Strategy", type="primary")
    
    if submitted:
        if not initial_conditions.strip():
            st.error("Please describe the current situation")
            return None
        
        if not desired_outcome.strip():
            st.error("Please describe the desired outcome")
            return None
        
        # Prepare request
        request_data = {
            "initial_conditions": initial_conditions,
            "desired_outcome": desired_outcome,
            "time_horizon": time_horizon
        }
        
        if constraints.strip():
            request_data["constraints"] = [c.strip() for c in constraints.split(",") if c.strip()]
        
        # Make API call
        with st.spinner("Generating strategy..."):
            results = make_api_call("/forecast", request_data, use_validation)
            return results
    
    return None


def render_help_panel(mode: str):
    """Render the help panel with examples and tips"""
    
    st.subheader("💡 Tips & Examples")
    
    if "Forecast Outcomes" in mode:
        st.markdown("""
        **Example Initial Conditions:**
        - "OpenAI has released GPT-4, competition is increasing"
        - "New AI regulation is being debated in Congress"
        - "Major tech companies are investing heavily in AI"
        
        **Tips:**
        - Be specific about the current situation
        - Include relevant context and recent developments
        - Consider multiple perspectives and stakeholders
        """)
    
    elif "Evaluate Specific Outcomes" in mode:
        st.markdown("""
        **Example Outcomes:**
        - AI breakthrough in reasoning announced
        - Major AI safety incident occurs
        - New AI regulation enacted
        - Tech stock market correction
        
        **Tips:**
        - Be specific and measurable
        - Focus on outcomes you care about
        - Consider both positive and negative scenarios
        """)
    
    elif "Find Path to Desired Outcome" in mode:
        st.markdown("""
        **Example Scenarios:**
        - Startup → Successful AI product
        - Research lab → AGI breakthrough
        - Company → AI transformation
        
        **Tips:**
        - Be clear about your starting point
        - Define success criteria precisely
        - Include realistic constraints
        - Consider resource limitations
        """)
    
    st.divider()
    
    # System status
    with st.expander("🔧 System Status"):
        if st.button("Check API Health"):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ API is healthy")
                    st.json(response.json())
                else:
                    st.error(f"❌ API error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Cannot connect to API: {str(e)}")


def make_api_call(endpoint: str, data: Dict[str, Any], use_validation: bool) -> Dict[str, Any]:
    """Make API call to the forecasting system"""
    
    try:
        # Choose endpoint based on validation preference
        if use_validation:
            url = f"{API_BASE_URL}{endpoint}"
        else:
            url = f"{API_BASE_URL}{endpoint}/quick"
        
        response = requests.post(url, json=data, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. The analysis is taking longer than expected.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API. Please check if the server is running.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None


def render_results(results: Dict[str, Any], show_raw: bool):
    """Render the analysis results"""
    
    if not results or results.get("error"):
        st.error(f"Error: {results.get('error', 'Unknown error')}")
        return
    
    mode = results.get("mode", "unknown")
    
    st.header("📋 Analysis Results")
    
    # Mode-specific rendering
    if mode == "forecast":
        render_forecast_results(results)
    elif mode == "targeted":
        render_targeted_results(results)
    elif mode == "strategy":
        render_strategy_results(results)
    
    # Validation results
    if "validations" in results:
        render_validation_results(results["validations"])
    
    # Raw output
    if show_raw:
        with st.expander("🔍 Raw Output"):
            st.json(results)


def render_forecast_results(results: Dict[str, Any]):
    """Render pure forecasting results"""
    
    st.subheader("🎯 Predicted Outcomes")
    
    forecasts = results.get("forecasts", [])
    
    if not forecasts:
        st.warning("No forecasts generated")
        return
    
    # Create probability chart
    if forecasts:
        df = pd.DataFrame([
            {
                "Outcome": f["description"][:50] + "..." if len(f["description"]) > 50 else f["description"],
                "Probability": f["probability"],
                "Lower": f.get("confidence_interval", [0, 0])[0],
                "Upper": f.get("confidence_interval", [0, 0])[1]
            }
            for f in forecasts
        ])
        
        fig = px.bar(
            df, 
            x="Probability", 
            y="Outcome",
            orientation="h",
            title="Outcome Probabilities",
            color="Probability",
            color_continuous_scale="viridis"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown
    for i, forecast in enumerate(forecasts, 1):
        with st.expander(f"#{i}: {forecast['description']}", expanded=i <= 3):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Probability",
                    f"{forecast['probability']:.1%}",
                    help="Estimated likelihood of occurrence"
                )
            
            with col2:
                ci = forecast.get("confidence_interval", [0, 0])
                st.metric(
                    "Confidence Range",
                    f"{ci[0]:.1%} - {ci[1]:.1%}",
                    help="Uncertainty range around the estimate"
                )
            
            with col3:
                timeline = forecast.get("timeline", "Not specified")
                st.metric("Timeline", timeline)
            
            if forecast.get("key_drivers"):
                st.write("**Key Drivers:**")
                for driver in forecast["key_drivers"]:
                    st.write(f"• {driver}")
            
            if forecast.get("early_indicators"):
                st.write("**Early Indicators:**")
                for indicator in forecast["early_indicators"]:
                    st.write(f"• {indicator}")


def render_targeted_results(results: Dict[str, Any]):
    """Render targeted forecasting results"""
    
    st.subheader("📊 Outcome Evaluations")
    
    evaluations = results.get("evaluations", [])
    
    if not evaluations:
        st.warning("No evaluations generated")
        return
    
    # Summary metrics
    if evaluations:
        col1, col2, col3 = st.columns(3)
        
        avg_prob = sum(e.get("probability", 0) for e in evaluations) / len(evaluations)
        avg_feasibility = sum(e.get("feasibility_score", 0) for e in evaluations) / len(evaluations)
        high_confidence = sum(1 for e in evaluations if e.get("confidence") == "high")
        
        with col1:
            st.metric("Average Probability", f"{avg_prob:.1%}")
        with col2:
            st.metric("Average Feasibility", f"{avg_feasibility:.1%}")
        with col3:
            st.metric("High Confidence", f"{high_confidence}/{len(evaluations)}")
    
    # Detailed evaluations
    for i, evaluation in enumerate(evaluations, 1):
        with st.expander(f"#{i}: {evaluation['outcome']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Probability", f"{evaluation.get('probability', 0):.1%}")
            with col2:
                st.metric("Feasibility", f"{evaluation.get('feasibility_score', 0):.1%}")
            with col3:
                confidence = evaluation.get("confidence", "unknown")
                st.metric("Confidence", confidence.title())
            
            if evaluation.get("preconditions"):
                st.write("**Preconditions:**")
                for condition in evaluation["preconditions"]:
                    st.write(f"• {condition}")
            
            if evaluation.get("blocking_factors"):
                st.write("**Blocking Factors:**")
                for blocker in evaluation["blocking_factors"]:
                    st.write(f"• {blocker}")


def render_strategy_results(results: Dict[str, Any]):
    """Render strategy generation results"""
    
    st.subheader("🚀 Strategic Recommendations")
    
    # Feasibility score
    feasibility = results.get("feasibility_score", 0)
    st.metric("Overall Feasibility", f"{feasibility:.1%}")
    
    # Gap analysis
    gap_analysis = results.get("gap_analysis", {})
    if gap_analysis:
        st.subheader("📋 Gap Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Required Changes:**")
            for change in gap_analysis.get("required_changes", []):
                st.write(f"• {change}")
        
        with col2:
            st.write("**Needed Resources:**")
            for resource in gap_analysis.get("needed_resources", []):
                st.write(f"• {resource}")
        
        with col3:
            st.write("**Capability Gaps:**")
            for gap in gap_analysis.get("capability_gaps", []):
                st.write(f"• {gap}")
    
    # Recommended strategy
    recommended = results.get("recommended_strategy")
    if recommended:
        st.subheader("⭐ Recommended Strategy")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Success Probability", f"{recommended.get('overall_probability', 0):.1%}")
        with col2:
            st.metric("Timeline", recommended.get("timeline", "Not specified"))
        
        # Strategy steps
        steps = recommended.get("steps", [])
        if steps:
            st.write("**Implementation Steps:**")
            
            for step in steps:
                with st.expander(f"Phase {step.get('phase', '?')}: {step.get('action', 'Unknown')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Timeline:** {step.get('timeline', 'Not specified')}")
                        st.write(f"**Success Criteria:** {step.get('success_criteria', 'Not specified')}")
                    
                    with col2:
                        if step.get("dependencies"):
                            st.write("**Dependencies:**")
                            for dep in step["dependencies"]:
                                st.write(f"• {dep}")
    
    # Alternative strategies
    alternatives = results.get("strategies", [])
    if len(alternatives) > 1:
        st.subheader("🔄 Alternative Strategies")
        
        for strategy in alternatives[1:]:  # Skip the first one (recommended)
            with st.expander(f"{strategy.get('path_name', 'Alternative Strategy')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Success Probability", f"{strategy.get('overall_probability', 0):.1%}")
                with col2:
                    st.metric("Timeline", strategy.get("timeline", "Not specified"))
                
                if strategy.get("advantages"):
                    st.write("**Advantages:**")
                    for adv in strategy["advantages"]:
                        st.write(f"• {adv}")


def render_validation_results(validations: Dict[str, Any]):
    """Render validation and quality metrics"""
    
    with st.expander("🔍 Quality Assessment"):
        validation_results = validations.get("validation_results", {})
        
        if validation_results:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Logical Consistency",
                    f"{validation_results.get('logical_consistency', 0):.1%}"
                )
            
            with col2:
                st.metric(
                    "Probability Calibration",
                    f"{validation_results.get('probability_calibration', 0):.1%}"
                )
            
            with col3:
                st.metric(
                    "Uncertainty Handling",
                    f"{validation_results.get('uncertainty_quantification', 0):.1%}"
                )
            
            with col4:
                st.metric(
                    "Overall Quality",
                    f"{validation_results.get('overall_quality_score', 0):.1%}"
                )
        
        # Improvement suggestions
        suggestions = validations.get("improvement_suggestions", [])
        if suggestions:
            st.write("**Improvement Suggestions:**")
            for suggestion in suggestions:
                st.write(f"• {suggestion}")


if __name__ == "__main__":
    main()