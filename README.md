# AI Forecasting & Strategy System

An AI-powered system that performs bidirectional analysis: forecasting probable outcomes from initial conditions AND recommending optimal strategies to achieve desired outcomes.

## 🌟 Features

### Three Operating Modes

1. **Pure Forecasting Mode**

   - Input: Initial conditions only
   - Output: Probability distribution of most notable outcomes

2. **Targeted Forecasting Mode**

   - Input: Initial conditions + specific outcomes of interest
   - Output: Probability assessments for specified outcomes

3. **Strategy Generation Mode**
   - Input: Initial conditions + desired outcomes
   - Output: Optimal action paths with success probabilities

### Key Capabilities

- **🤖 CrewAI Multi-Agent System**: 5 specialized agents implementing superforecaster methodologies
  - **Base Rate Analyst**: Reference class forecasting and historical analysis
  - **Evidence Researcher**: Systematic evidence gathering and quality evaluation
  - **Perspective Analyst**: Multiple scenario analysis and bias detection
  - **Uncertainty Quantifier**: Confidence assessment and calibration
  - **Synthesis Expert**: Final forecast integration and reasoning
- **🧠 Superforecaster Methodology**: Proven techniques from top human forecasters
- **📊 Enhanced Analysis**: Evidence quality scoring, methodology tracking, agent logs
- **🔬 Rigorous Validation**: Multi-dimensional quality assessment and calibration
- **🌐 Interactive Frontend**: Easy-to-use web interface with example buttons and real-time results
- **⚡ Flexible Architecture**: Choose between standard or enhanced CrewAI analysis

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenRouter API key

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ai-forecasts
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

### 🎯 **One-Command Launch**

**Run the complete system with one command:**

```bash
python run_frontend.py
```

This will automatically:
- Start the API server on port 12000
- Launch the Streamlit frontend on port 12001
- Open your browser to the web interface

**Alternative: Manual Setup**

1. **Start the API server (Terminal 1):**

```bash
python run_api.py
```

2. **Start the web interface (Terminal 2):**

```bash
python run_frontend.py
```

3. **Run the demo:**

```bash
python demo.py
```

## 🌐 Access Points

- **Web Interface**: https://work-2-ypcpnwlsffvpolgg.prod-runtime.all-hands.dev
- **API Documentation**: https://work-1-ypcpnwlsffvpolgg.prod-runtime.all-hands.dev/docs
- **API Health Check**: https://work-1-ypcpnwlsffvpolgg.prod-runtime.all-hands.dev/health

## 🎯 Frontend Features

### Interactive Web Interface

The Streamlit frontend provides an intuitive interface with:

- **📋 Quick Example Buttons**: Click to populate forms with realistic examples
- **🤖 CrewAI Toggle**: Switch between standard and enhanced multi-agent analysis
- **📊 Real-time Results**: See probability estimates, confidence levels, and reasoning
- **🔍 Agent Logs**: View intermediate analysis from each specialized agent
- **📈 Visual Charts**: Interactive probability distributions and confidence intervals
- **🔬 Methodology Breakdown**: Detailed view of superforecaster techniques used

### Three Analysis Modes

1. **🎯 Forecast Outcomes**: Predict likely future developments
2. **📊 Evaluate Specific Outcomes**: Assess probability of specific events
3. **🚀 Find Path to Desired Outcome**: Generate strategic implementation plans

### Enhanced Output Display

- **Probability Metrics**: Main forecast with confidence intervals
- **Base Rate Analysis**: Historical reference class comparisons  
- **Evidence Quality**: Systematic evaluation of information sources
- **Agent Analysis**: Breakdown of each specialist agent's contribution
- **Methodology Components**: Detailed superforecaster techniques applied

## 📖 Usage Examples

### Pure Forecasting

```python
import requests

response = requests.post("http://localhost:12000/forecast", json={
    "initial_conditions": "OpenAI has released GPT-4, competition is increasing",
    "time_horizon": "18 months"
})

results = response.json()
for outcome in results["outcomes"]:
    print(f"{outcome['description']}: {outcome['probability']:.1%}")
```

### Targeted Forecasting

```python
response = requests.post("http://localhost:12000/forecast", json={
    "initial_conditions": "Current AI capabilities as of 2024",
    "outcomes_of_interest": ["AGI achieved", "Major AI safety incident"],
    "time_horizon": "5 years"
})

results = response.json()
for evaluation in results["evaluations"]:
    print(f"{evaluation['outcome']}: {evaluation['probability']:.1%}")
```

### Strategy Generation

```python
response = requests.post("http://localhost:12000/forecast", json={
    "initial_conditions": "Small AI startup with $1M funding",
    "desired_outcome": "Successful AI product with 100K users",
    "time_horizon": "2 years",
    "constraints": ["Limited budget", "Small team"]
})

results = response.json()
strategy = results["recommended_strategy"]
print(f"Strategy: {strategy['name']}")
print(f"Success Rate: {strategy['overall_probability']:.1%}")
```

## 🏗️ Architecture

```
┌─────────────────────┐
│   Input Parser      │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Mode Classifier    │
└──────────┬──────────┘
           │
     ┌─────┴─────┬──────────┐
     │           │          │
┌────▼────┐ ┌───▼────┐ ┌───▼────┐
│Forecast │ │Targeted│ │Strategy│
│  Agent  │ │ Agent  │ │ Agent  │
└────┬────┘ └───┬────┘ └───┬────┘
     │          │          │
┌────▼──────────▼──────────▼────┐
│    Synthesis & Validation      │
└────────────────┬───────────────┘
                 │
         ┌───────▼────────┐
         │ Output Builder │
         └────────────────┘
```

### Core Components

- **ForecastAgent**: Generates probability distributions for likely outcomes
- **TargetedAgent**: Evaluates specific outcomes of interest
- **StrategyAgent**: Designs optimal paths to achieve desired outcomes
- **ValidatorAgent**: Ensures logical consistency and calibration
- **ForecastOrchestrator**: Coordinates multi-agent workflows

## 📊 API Reference

### Main Endpoint

**POST /forecast**

Request body:

```json
{
  "initial_conditions": "string (optional)",
  "outcomes_of_interest": ["string"] (optional),
  "desired_outcome": "string (optional)",
  "time_horizon": "string (default: '1 year')",
  "constraints": ["string"] (optional)
}
```

### Response Formats

**Pure Forecasting Response:**

```json
{
  "mode": "forecast",
  "outcomes": [
    {
      "description": "string",
      "probability": 0.65,
      "confidence_interval": [0.45, 0.8],
      "key_drivers": ["string"],
      "early_indicators": ["string"]
    }
  ],
  "meta_analysis": {
    "dominant_scenarios": ["string"],
    "key_uncertainties": ["string"]
  }
}
```

**Strategy Response:**

```json
{
  "mode": "strategy",
  "feasibility_score": 0.72,
  "recommended_strategy": {
    "name": "string",
    "overall_probability": 0.72,
    "steps": [
      {
        "phase": 1,
        "action": "string",
        "timeline": "string",
        "success_criteria": "string"
      }
    ]
  }
}
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run the demo:

```bash
python demo.py
```

## 🔧 Configuration

### Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_BASE_URL`: OpenRouter API base URL (default: https://openrouter.ai/api/v1)
- `DEFAULT_MODEL`: Default LLM model (default: anthropic/claude-opus-4)

### Model Selection

The system supports any OpenRouter-compatible model. Popular choices:

- `anthropic/claude-opus-4`
- `anthropic/google/gemini-2.5-pro-preview`
- `openai/o4-mini-high`

## 📈 Benchmarking

The system includes a comprehensive benchmarking framework for evaluating forecast accuracy:

- **Brier Score**: Measures probability calibration
- **Log Score**: Assesses prediction quality
- **Top-K Accuracy**: Evaluates outcome ranking
- **Strategy Success Rate**: Measures strategic recommendation quality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with OpenRouter for LLM access
- Uses FastAPI for the backend API
- Streamlit for the web interface
- LangChain for LLM integration

## 📞 Support

For questions or issues:

1. Check the API documentation at `/docs`
2. Review the examples in this README
3. Run the demo script for a complete walkthrough
4. Open an issue on GitHub

---

**Note**: This system is designed for research and decision support. Always validate important decisions with domain experts and additional analysis.
