# AI Forecasting & Strategy System

An AI-powered system that performs bidirectional analysis: forecasting probable outcomes from initial conditions AND recommending optimal strategies to achieve desired outcomes.

## 🌟 Features

### Two Operating Modes

1. **📊 Evaluate Specific Outcomes**
   - Input: Initial conditions + specific outcomes of interest
   - Output: Probability assessments for specified outcomes with detailed analysis
   - Features: Real-time agent logging, evidence quality scoring, confidence intervals

2. **🚀 Find Path to Desired Outcome**
   - Input: Initial conditions + desired outcomes + constraints
   - Output: Strategic implementation plans with step-by-step actions
   - Features: Gap analysis, risk assessment, multiple strategic paths

### Key Capabilities

- **🤖 Multi-Agent Analysis**: Specialized agents for targeted outcome evaluation and strategy generation
  - **TargetedAgent**: Evaluates specific outcomes with probability assessments
  - **StrategyAgent**: Generates optimal paths to achieve desired outcomes
  - **CrewAI Integration**: Advanced multi-agent system with 5 specialized forecasting agents (when enabled)
- **📊 Real-time Logging**: Live agent activity display during analysis with color-coded progress
- **🧠 Superforecaster Methodology**: Proven techniques from top human forecasters
- **🔬 Comprehensive Benchmarking**: Brier score, calibration error, methodology quality assessment
- **🌐 Interactive Frontend**: Streamlit web interface with example buttons and real-time results
- **⚡ Robust Architecture**: Fallback mechanisms and error handling for reliable operation

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/rapturt9/ai-forecasts.git
cd ai-forecasts
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

### 🎯 **One-Command Launch**

**Run the complete system with one command:**

```bash
python run_frontend.py
```

This will automatically:
- Load environment variables from `.env` file
- Start the API server on port 12000
- Launch the Streamlit frontend on port 12001
- Display configuration and status

**Alternative: Manual Setup**

1. **Start the API server (Terminal 1):**

```bash
python run_api.py
```

2. **Start the web interface (Terminal 2):**

```bash
streamlit run src/ai_forecasts/frontend/streamlit_app.py --server.port=12001
```

## 🌐 Access Points

- **Web Interface**: http://localhost:12001
- **API Documentation**: http://localhost:12000/docs
- **API Health Check**: http://localhost:12000/health

## 🎯 Frontend Features

### Interactive Web Interface

The Streamlit frontend provides an intuitive interface with:

- **📋 Quick Example Buttons**: Click to populate forms with realistic examples
- **📊 Real-time Agent Logs**: Watch agents work in real-time with color-coded activity
- **📈 Visual Results**: Probability estimates, confidence levels, and detailed reasoning
- **🔍 Methodology Breakdown**: See which superforecaster techniques were applied
- **⚡ Live Progress**: Visual progress bars and status updates during analysis

### Two Analysis Modes

1. **📊 Evaluate Specific Outcomes**: Assess probability of specific events
2. **🚀 Find Path to Desired Outcome**: Generate strategic implementation plans

### Enhanced Output Display

- **Probability Metrics**: Main forecast with confidence intervals
- **Agent Activity**: Real-time logs from each specialist agent
- **Evidence Quality**: Systematic evaluation of information sources
- **Methodology Components**: Detailed superforecaster techniques applied

## 📖 Usage Examples

### Evaluate Specific Outcomes

```python
import requests

response = requests.post("http://localhost:12000/forecast", json={
    "initial_conditions": "Current AI capabilities as of 2024",
    "outcomes_of_interest": ["AGI achieved by 2030", "Major AI safety incident"],
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
     ┌─────┴─────┐
     │           │
┌────▼────┐ ┌───▼────┐
│Targeted │ │Strategy│
│ Agent   │ │ Agent  │
└────┬────┘ └───┬────┘
     │          │
┌────▼──────────▼────┐
│ Agent Logger &      │
│ Result Synthesis    │
└─────────────────────┘
```

### Core Components

- **TargetedAgent**: Evaluates specific outcomes of interest with detailed probability analysis
- **StrategyAgent**: Designs optimal paths to achieve desired outcomes
- **AgentLogger**: Real-time logging and activity tracking for all agent operations
- **LLMClient**: Unified interface for OpenRouter API with proper authentication
- **ForecastOrchestrator**: Coordinates workflows and manages agent interactions

## 📊 API Reference

### Main Endpoint

**POST /forecast**

Request body:

```json
{
  "initial_conditions": "string (required)",
  "outcomes_of_interest": ["string"] (optional),
  "desired_outcome": "string (optional)",
  "time_horizon": "string (default: '1 year')",
  "constraints": ["string"] (optional)
}
```

### Response Formats

**Targeted Forecasting Response:**

```json
{
  "mode": "targeted",
  "evaluations": [
    {
      "outcome": "string",
      "probability": 0.65,
      "confidence_interval": [0.45, 0.8],
      "reasoning": "string",
      "key_factors": ["string"],
      "blocking_factors": ["string"]
    }
  ],
  "agent_logs": ["string"],
  "methodology": {
    "evidence_quality": 0.8,
    "confidence_level": "high"
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
  },
  "agent_logs": ["string"]
}
```

## 🧪 Testing & Benchmarking

### Run the comprehensive benchmark:

```bash
python run_comprehensive_benchmark.py
```

This will:
- Test the system on real forecasting questions
- Calculate Brier scores and calibration metrics
- Generate detailed performance reports
- Save results to `comprehensive_benchmark_results.json`

### Run individual tests:

```bash
python -m pytest tests/ -v
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required: OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Optional: OpenRouter API Base URL (default: https://openrouter.ai/api/v1)
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Optional: Default LLM model (default: openai/gpt-4o)
DEFAULT_MODEL=openai/gpt-4o
```

### Supported Models

The system supports any OpenRouter-compatible model. Popular choices:

- `openai/gpt-4o` (default, recommended)
- `anthropic/claude-3.5-sonnet`
- `google/gemini-pro-1.5`
- `meta-llama/llama-3.1-405b-instruct`

### Model Selection

You can change the model by:
1. Setting `DEFAULT_MODEL` in your `.env` file
2. Or passing it directly to the LLMClient in code

## 📈 Benchmarking Results

The system includes comprehensive benchmarking with:

- **Brier Score**: Measures probability calibration accuracy
- **Calibration Error**: Assesses prediction reliability
- **Methodology Quality**: Evaluates superforecaster technique usage
- **Agent Performance**: Tracks individual agent contributions
- **Extreme Prediction Accuracy**: Tests performance on high-confidence predictions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [OpenRouter](https://openrouter.ai) for LLM access
- Uses [FastAPI](https://fastapi.tiangolo.com) for the backend API
- [Streamlit](https://streamlit.io) for the web interface
- [LangChain](https://langchain.com) for LLM integration
- [CrewAI](https://crewai.com) for multi-agent orchestration

## 📞 Support

For questions or issues:

1. Check the API documentation at http://localhost:12000/docs
2. Review the examples in this README
3. Run the benchmark script for a complete walkthrough
4. Open an issue on GitHub

## 🔍 Troubleshooting

### Common Issues

**API Key Not Found:**
```bash
❌ OPENROUTER_API_KEY not found!
```
- Create a `.env` file with your API key
- Or set the environment variable: `export OPENROUTER_API_KEY=your-key`

**Port Already in Use:**
```bash
❌ Port 12000 already in use
```
- Kill existing processes: `pkill -f "run_api.py"`
- Or use different ports in the configuration

**Dependencies Missing:**
```bash
❌ ModuleNotFoundError: No module named 'streamlit'
```
- Install dependencies: `pip install -r requirements.txt`

---

**Note**: This system is designed for research and decision support. Always validate important decisions with domain experts and additional analysis.