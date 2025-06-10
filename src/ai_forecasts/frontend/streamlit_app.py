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
    
    # Quick mode explanation
    with st.expander("📖 How to use this system", expanded=False):
        st.markdown("""
        **Choose your analysis mode:**
        
        📊 **Evaluate Specific Outcomes**: *"What outcomes are we trying to predict?"*
        - Enter specific outcomes you want to evaluate
        - Get detailed probability assessments and feasibility analysis
        - Understand preconditions and blocking factors
        
        🚀 **Find Path to Desired Outcome**: *"Given an outcome, what are the most probable strategies?"*
        - Describe what you want to achieve
        - Get multiple strategic paths with step-by-step implementation plans
        - Includes gap analysis and risk assessment
        """)
    
    # Sidebar for mode selection and configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Mode selection
        mode = st.radio(
            "Select Analysis Mode:",
            [
                "📊 Evaluate Specific Outcomes", 
                "🚀 Find Path to Desired Outcome"
            ],
            help="Choose the type of analysis you want to perform"
        )
        
        st.divider()
        
        # Advanced options
        st.subheader("Advanced Options")
        use_crewai = st.checkbox("🤖 Use CrewAI Multi-Agent System", value=True, help="Enhanced superforecaster methodology with 5 specialized agents")
        use_validation = st.checkbox("Enable validation", value=True, help="Adds quality checks but takes longer")
        show_raw_output = st.checkbox("Show raw output", value=False, help="Display technical details")
        show_agent_logs = st.checkbox("Show agent logs", value=True, help="Display intermediate agent analysis")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    # Initialize results variable
    results = None
    
    with col1:
        # Input form based on selected mode
        if "Evaluate Specific Outcomes" in mode:
            results = render_targeted_mode(use_validation, use_crewai)
        elif "Find Path to Desired Outcome" in mode:
            results = render_strategy_mode(use_validation, use_crewai)
    
    with col2:
        # Help and examples
        render_help_panel(mode)
    
    # Display results if available
    if results:
        st.divider()
        render_results(results, show_raw_output, show_agent_logs)


def render_forecast_mode(use_validation: bool, use_crewai: bool) -> Dict[str, Any]:
    """Render the pure forecasting mode interface"""
    
    st.header("🎯 Forecast Likely Outcomes")
    st.markdown("Predict the most probable outcomes based on current global developments. The system will automatically research current conditions and generate a comprehensive forecast.")
    
    # Optional outcomes input
    st.markdown("### 🎯 Optional: Specify Outcomes to Focus On")
    with st.expander("🔍 Focus on specific outcomes (optional)", expanded=False):
        st.info("💡 **Tip**: If you have specific outcomes in mind, enter them here to get more targeted analysis while still receiving a comprehensive forecast.")
        focus_outcomes = st.text_area(
            "Outcomes to prioritize in the forecast",
            placeholder="Enter specific outcomes you're interested in (one per line):\n- AI breakthrough announcements\n- Major tech company acquisitions\n- Regulatory changes in AI",
            height=100,
            help="If specified, the forecast will pay special attention to these outcomes while still providing a comprehensive analysis"
        )
    
    # Sample examples
    st.markdown("**📋 Quick Examples:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤖 AI Development", key="forecast_ai_example"):
            st.session_state.forecast_horizon = "1 year"
            st.rerun()
    
    with col2:
        if st.button("🏢 Tech Industry", key="forecast_tech_example"):
            st.session_state.forecast_horizon = "6 months"
            st.rerun()
    
    with col3:
        if st.button("🌍 Global Economy", key="forecast_economy_example"):
            st.session_state.forecast_horizon = "2 years"
            st.rerun()
    
    st.divider()
    
    with st.form("forecast_form"):
        # Input fields
        col1, col2 = st.columns(2)
        with col1:
            horizon_options = ["1 month", "3 months", "6 months", "1 year", "2 years", "5 years"]
            default_horizon = st.session_state.get('forecast_horizon', "1 year")
            horizon_index = horizon_options.index(default_horizon) if default_horizon in horizon_options else 3
            time_horizon = st.selectbox(
                "Time Horizon",
                horizon_options,
                index=horizon_index,
                help="How far into the future to forecast"
            )
        
        with col2:
            constraints = st.text_area(
                "Constraints (optional)",
                placeholder="e.g., budget < $1M, no regulatory changes",
                height=100,
                help="Any specific constraints or assumptions to consider"
            )
        
        st.info("💡 The system will automatically research current global developments to inform the forecast.")
        
        submitted = st.form_submit_button("Generate Forecast", type="primary")
    
    if submitted:
        # Prepare request
        request_data = {
            "time_horizon": time_horizon
        }
        
        if constraints.strip():
            request_data["constraints"] = [c.strip() for c in constraints.split(",") if c.strip()]
        
        # Add focus outcomes if specified
        if focus_outcomes.strip():
            focus_list = [line.strip().lstrip("- ") for line in focus_outcomes.split("\n") if line.strip()]
            request_data["outcomes_of_interest"] = focus_list
        
        # Make API call
        with st.spinner("Generating forecast..."):
            results = make_api_call("/forecast", request_data, use_validation, use_crewai)
            return results
    
    return None


def render_targeted_mode(use_validation: bool, use_crewai: bool) -> Dict[str, Any]:
    """Render the targeted forecasting mode interface"""
    
    st.header("📊 Evaluate Specific Outcomes")
    st.markdown("**What outcomes are we trying to predict?** Enter specific outcomes you want to evaluate, and the system will assess their probability, feasibility, and provide detailed analysis based on current developments.")
    
    # Sample examples
    st.markdown("**📋 Quick Examples:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤖 AI Milestones", key="targeted_ai_example"):
            st.session_state.targeted_outcomes = "GPT-5 released by OpenAI\nAGI achieved by any company\nMajor AI safety breakthrough\nComprehensive AI regulation passed"
            st.session_state.targeted_horizon = "2 years"
            st.rerun()
    
    with col2:
        if st.button("💰 Market Events", key="targeted_market_example"):
            st.session_state.targeted_outcomes = "Stock market crash (>20% drop)\nRecession declared in US\nFed cuts rates below 3%\nBitcoin reaches $100k"
            st.session_state.targeted_horizon = "1 year"
            st.rerun()
    
    with col3:
        if st.button("🌍 Global Events", key="targeted_global_example"):
            st.session_state.targeted_outcomes = "Climate tipping point reached\nMajor breakthrough in fusion energy\nNew pandemic declared\nSpace tourism becomes mainstream"
            st.session_state.targeted_horizon = "3 years"
            st.rerun()
    
    st.divider()
    
    with st.form("targeted_form"):
        # Input fields
        st.markdown("#### 🎯 What outcomes are we trying to predict?")
        st.info("💡 **Enter specific outcomes** you want to evaluate. The system will assess probability, feasibility, and provide detailed analysis for each.")
        outcomes_text = st.text_area(
            "Outcomes to evaluate (one per line)",
            value=st.session_state.get('targeted_outcomes', ''),
            placeholder="Enter one outcome per line:\n- GPT-5 released by OpenAI\n- Major AI regulation passed\n- Bitcoin reaches $100k",
            height=120,
            help="Enter each specific outcome you want to evaluate on a separate line.",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            horizon_options = ["1 month", "3 months", "6 months", "1 year", "2 years", "5 years"]
            default_horizon = st.session_state.get('targeted_horizon', "1 year")
            horizon_index = horizon_options.index(default_horizon) if default_horizon in horizon_options else 3
            time_horizon = st.selectbox(
                "Time Horizon",
                horizon_options,
                index=horizon_index,
                help="How far into the future to evaluate"
            )
        
        with col2:
            constraints = st.text_area(
                "Constraints (optional)",
                placeholder="e.g., budget < $1M, no regulatory changes",
                height=100,
                help="Any specific constraints or assumptions to consider"
            )
        
        st.info("💡 The system will automatically research current context relevant to these outcomes.")
        
        submitted = st.form_submit_button("Evaluate Outcomes", type="primary")
    
    if submitted:
        if not outcomes_text.strip():
            st.error("Please provide outcomes to evaluate")
            return None
        
        # Parse outcomes
        outcomes = [line.strip().lstrip("- ") for line in outcomes_text.split("\n") if line.strip()]
        
        # Prepare request
        request_data = {
            "outcomes_of_interest": outcomes,
            "time_horizon": time_horizon
        }
        
        if constraints.strip():
            request_data["constraints"] = [c.strip() for c in constraints.split(",") if c.strip()]
        
        # Make API call
        with st.spinner("Evaluating outcomes..."):
            results = make_api_call("/forecast", request_data, use_validation, use_crewai)
            return results
    
    return None


def render_strategy_mode(use_validation: bool, use_crewai: bool) -> Dict[str, Any]:
    """Render the strategy generation mode interface"""
    
    st.header("🚀 Find Path to Desired Outcome")
    st.markdown("**Given an outcome, what are the most probable strategies to achieve it?** Describe your desired outcome, and the system will generate optimal strategies with step-by-step implementation plans based on current market conditions.")
    
    # Sample examples
    st.markdown("**📋 Quick Examples:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 AI Startup Success", key="strategy_startup_example"):
            st.session_state.strategy_desired = "Launch a successful AI startup that reaches $10M ARR within 2 years"
            st.session_state.strategy_constraints = "Limited initial funding, competitive market, need to hire top talent"
            st.session_state.strategy_horizon = "2 years"
            st.rerun()
    
    with col2:
        if st.button("🎓 AI Career Transition", key="strategy_career_example"):
            st.session_state.strategy_desired = "Transition from software engineering to AI research scientist role at a top lab"
            st.session_state.strategy_constraints = "Need to maintain current income, limited time for study, no PhD"
            st.session_state.strategy_horizon = "18 months"
            st.rerun()
    
    with col3:
        if st.button("🏢 AI Adoption", key="strategy_transform_example"):
            st.session_state.strategy_desired = "Transform traditional company into AI-first organization with 30% efficiency gains"
            st.session_state.strategy_constraints = "Legacy systems, change resistance, limited AI expertise, budget constraints"
            st.session_state.strategy_horizon = "3 years"
            st.rerun()
    
    st.divider()
    
    with st.form("strategy_form"):
        # Input fields
        st.markdown("#### 🚀 What outcome do you want to achieve?")
        st.info("💡 **Describe your desired outcome** with specific goals and success metrics. The system will generate multiple strategic paths to achieve this outcome.")
        desired_outcome = st.text_area(
            "Desired outcome",
            value=st.session_state.get('strategy_desired', ''),
            placeholder="Describe what you want to achieve...\nExample: Launch a successful AI startup that reaches $10M ARR",
            height=100,
            help="Be specific about your goal and success metrics.",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            horizon_options = ["1 month", "3 months", "6 months", "1 year", "18 months", "2 years", "3 years", "5 years"]
            default_horizon = st.session_state.get('strategy_horizon', "1 year")
            horizon_index = horizon_options.index(default_horizon) if default_horizon in horizon_options else 3
            time_horizon = st.selectbox(
                "Time Horizon",
                horizon_options,
                index=horizon_index,
                help="How long you have to achieve this outcome"
            )
        
        with col2:
            constraints = st.text_area(
                "Constraints",
                value=st.session_state.get('strategy_constraints', ''),
                placeholder="e.g., limited budget, small team, regulatory requirements",
                height=100,
                help="Any limitations or constraints to consider"
            )
        
        st.info("💡 The system will automatically research current market conditions and opportunities relevant to your goal.")
        
        submitted = st.form_submit_button("Generate Strategy", type="primary")
    
    if submitted:
        if not desired_outcome.strip():
            st.error("Please describe the desired outcome")
            return None
        
        # Prepare request
        request_data = {
            "desired_outcome": desired_outcome,
            "time_horizon": time_horizon
        }
        
        if constraints.strip():
            request_data["constraints"] = [c.strip() for c in constraints.split(",") if c.strip()]
        
        # Make API call
        with st.spinner("Generating strategy..."):
            results = make_api_call("/forecast", request_data, use_validation, use_crewai)
            return results
    
    return None


def render_help_panel(mode: str):
    """Render the help panel with examples and tips"""
    
    st.subheader("💡 Tips & Examples")
    
    if "Evaluate Specific Outcomes" in mode:
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


def make_api_call(endpoint: str, data: Dict[str, Any], use_validation: bool, use_crewai: bool = False) -> Dict[str, Any]:
    """Make API call to the forecasting system"""
    
    try:
        # Choose endpoint based on preferences
        if use_crewai:
            url = f"{API_BASE_URL}{endpoint}/crewai"
        elif use_validation:
            url = f"{API_BASE_URL}{endpoint}"
        else:
            url = f"{API_BASE_URL}{endpoint}/quick"
        
        response = requests.post(url, json=data, timeout=300)  # Increased timeout for CrewAI
        
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


def render_results(results: Dict[str, Any], show_raw: bool, show_agent_logs: bool):
    """Render the analysis results"""
    
    if not results or results.get("error"):
        st.error(f"Error: {results.get('error', 'Unknown error')}")
        return
    
    mode = results.get("mode", "unknown")
    methodology = results.get("methodology", "standard")
    
    st.header("📋 Analysis Results")
    
    # Show methodology info
    if methodology == "crewai_superforecaster":
        st.info("🤖 **Enhanced Analysis**: This forecast was generated using the CrewAI multi-agent superforecaster system with 5 specialized agents.")
    
    # Mode-specific rendering
    if "crewai" in mode or methodology == "crewai_superforecaster":
        render_crewai_results(results)
    elif mode == "forecast":
        render_forecast_results(results)
    elif mode == "targeted":
        render_targeted_results(results)
    elif mode == "strategy":
        render_strategy_results(results)
    
    # Agent computation logs
    if show_agent_logs:
        render_agent_logs(results)
    
    # Validation results
    if "validations" in results:
        render_validation_results(results["validations"])
    
    # Raw output
    if show_raw:
        with st.expander("🔍 Raw Output"):
            st.json(results)


def render_crewai_results(results: Dict[str, Any]):
    """Render CrewAI multi-agent superforecaster results"""
    
    forecast = results.get("forecast", {})
    agent_analysis = results.get("agent_analysis", {})
    
    # Main forecast display
    st.subheader("🎯 Superforecaster Analysis")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        probability = forecast.get("probability", 0)
        st.metric(
            "Probability",
            f"{probability:.1%}",
            help="Final probability estimate from multi-agent analysis"
        )
    
    with col2:
        confidence = forecast.get("confidence_level", "Unknown")
        st.metric(
            "Confidence",
            confidence,
            help="Confidence level in the forecast"
        )
    
    with col3:
        base_rate = forecast.get("base_rate", 0)
        st.metric(
            "Base Rate",
            f"{base_rate:.1%}",
            help="Historical base rate for similar situations"
        )
    
    with col4:
        evidence_quality = forecast.get("evidence_quality", 0)
        st.metric(
            "Evidence Quality",
            f"{evidence_quality:.1%}",
            help="Quality score of available evidence"
        )
    
    # Main reasoning
    if forecast.get("reasoning"):
        st.subheader("🧠 Reasoning")
        st.write(forecast["reasoning"])
    
    # Methodology components
    methodology = forecast.get("methodology_components", {})
    if methodology:
        st.subheader("🔬 Methodology Components")
        
        for component, details in methodology.items():
            with st.expander(f"📋 {component.replace('_', ' ').title()}", expanded=False):
                if isinstance(details, dict):
                    for key, value in details.items():
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                else:
                    st.write(details)
    
    # Agent analysis breakdown
    if agent_analysis:
        st.subheader("🤖 Agent Analysis Breakdown")
        
        for agent_name, analysis in agent_analysis.items():
            with st.expander(f"🔍 {agent_name.replace('_', ' ').title()}", expanded=False):
                if isinstance(analysis, dict):
                    for key, value in analysis.items():
                        if isinstance(value, list):
                            st.write(f"**{key.replace('_', ' ').title()}:**")
                            for item in value:
                                st.write(f"• {item}")
                        else:
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                else:
                    st.write(analysis)


def render_forecast_results(results: Dict[str, Any]):
    """Render pure forecasting results"""
    
    st.subheader("🎯 Predicted Outcomes")
    
    forecasts = results.get("outcomes", [])
    
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


def render_agent_logs(results: Dict[str, Any]):
    """Render agent computation logs and processing summary"""
    
    with st.expander("🤖 Agent Computation Log", expanded=True):
        # Processing summary
        if "processing_summary" in results:
            summary = results["processing_summary"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Time", f"{summary.get('total_time', 0):.2f}s")
            with col2:
                st.metric("Agents Used", summary.get('agent_count', 0))
            with col3:
                st.metric("Activities", len(summary.get('activities', [])))
            
            # Agents used
            agents_used = summary.get('agents_used', [])
            if agents_used:
                st.write("**Agents Involved:**")
                agent_colors = {
                    'orchestrator': '🎯',
                    'forecast_agent': '📊',
                    'targeted_agent': '🎯',
                    'strategy_agent': '🚀',
                    'validator_agent': '✅'
                }
                
                cols = st.columns(len(agents_used))
                for i, agent in enumerate(agents_used):
                    with cols[i]:
                        icon = agent_colors.get(agent, '🤖')
                        st.write(f"{icon} {agent.replace('_', ' ').title()}")
        
        # Detailed logs
        if "agent_logs" in results:
            logs = results["agent_logs"]
            
            st.write("**Detailed Activity Log:**")
            
            for log in logs:
                timestamp = log.get('timestamp', '')
                elapsed = log.get('elapsed_seconds', 0)
                agent = log.get('agent', 'unknown')
                message = log.get('message', '')
                
                # Format timestamp to show just time
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M:%S')
                except:
                    time_str = timestamp
                
                # Color code by agent
                agent_colors = {
                    'orchestrator': '#1f77b4',
                    'forecast_agent': '#ff7f0e', 
                    'targeted_agent': '#2ca02c',
                    'strategy_agent': '#d62728',
                    'validator_agent': '#9467bd'
                }
                
                color = agent_colors.get(agent, '#7f7f7f')
                
                st.markdown(f"""
                <div style="
                    padding: 8px 12px; 
                    margin: 4px 0; 
                    border-left: 4px solid {color}; 
                    background-color: rgba(128,128,128,0.1);
                    border-radius: 4px;
                ">
                    <strong style="color: {color};">{agent.replace('_', ' ').title()}</strong> 
                    <span style="color: #666; font-size: 0.9em;">({elapsed:.2f}s)</span><br>
                    {message}
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()