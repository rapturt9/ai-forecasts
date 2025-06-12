# AI Forecasts - Minimal Superforecaster System

A minimal AI forecasting system with 3 core functionalities using the Google News Superforecaster agent.

## Core Components

### Main Agent Group
- **GoogleNewsSuperforecaster** (`src/ai_forecasts/agents/google_news_superforecaster.py`) - Advanced superforecaster with Google News integration
- **MarketAgent** (`src/ai_forecasts/agents/market_agent.py`) - Market trading agent that uses the superforecaster for Manifold Markets

## 3 Core Functionalities

### 1. Benchmark Runner (Parallel ForecastBench)
Run the agent group on ForecastBench in parallel to measure performance.

```bash
python run_comprehensive_benchmark.py
```

**Features:**
- Parallel processing of forecast questions
- Performance metrics and Brier scores
- Comprehensive analysis with Google News integration

### 2. Frontend Interface (Strategy & Forecast Prediction)
Interactive web interface for both strategy and forecast prediction.

```bash
python run_frontend.py
```

**Features:**
- Streamlit web interface
- Real-time forecasting
- Strategy analysis
- API backend for scalability

**Access:** https://work-1-gfoiobausejjruqa.prod-runtime.all-hands.dev

### 3. Manifold Markets Integration (Trading & Backtesting)
Use the agent group with Manifold API for trading and backtesting.

```bash
python manifold_bot.py
```

**Features:**
- Market analysis using superforecaster
- Automated trading decisions
- Backtesting between time periods
- ROI calculation and performance tracking

## Setup

### Environment Variables
Create a `.env` file with:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
SERP_API_KEY=your-serp-api-key-here
MANIFOLD_API_KEY=your-manifold-key-here  # Optional, for trading
```

### Installation
```bash
pip install -r requirements.txt
```

## File Structure

```
ai-forecasts/
├── src/
│   ├── ai_forecasts/
│   │   ├── agents/
│   │   │   ├── google_news_superforecaster.py  # Main agent
│   │   │   ├── market_agent.py                 # Market trading agent
│   │   │   └── strategy_agent.py               # Strategy analysis
│   │   ├── api/
│   │   │   └── main.py                         # FastAPI backend
│   │   ├── benchmark/
│   │   │   └── benchmark_runner.py             # ForecastBench runner
│   │   ├── frontend/
│   │   │   └── streamlit_app.py                # Web interface
│   │   └── utils/
│   │       ├── agent_logger.py                 # Logging
│   │       ├── google_news_tool.py             # News integration
│   │       └── llm_client.py                   # LLM client
│   └── manifold_markets/
│       ├── client.py                           # Manifold API client
│       ├── forecasting_bot.py                  # Trading bot
│       ├── backtesting.py                      # Backtesting engine
│       └── cli.py                              # Command line interface
├── run_comprehensive_benchmark.py              # Entry point 1
├── run_frontend.py                             # Entry point 2
├── manifold_bot.py                             # Entry point 3
└── requirements.txt
```

## Usage Examples

### Benchmark a Single Question
```python
from src.ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster

forecaster = GoogleNewsSuperforecaster(
    openrouter_api_key="your-key",
    serp_api_key="your-serp-key"
)

result = forecaster.forecast_with_google_news(
    question="Will X happen by Y date?",
    background="Additional context..."
)

print(f"Probability: {result.probability}")
print(f"Reasoning: {result.reasoning}")
```

### Analyze Markets
```python
from src.ai_forecasts.agents.market_agent import MarketAgent

agent = MarketAgent(
    openrouter_api_key="your-key",
    manifold_api_key="your-manifold-key"
)

# Find opportunities
opportunities = agent.find_opportunities(limit=10, min_edge=0.1)

# Execute trades (dry run)
results = agent.execute_trades(opportunities, dry_run=True)
```

### Backtest Strategy
```python
# Backtest performance over time period
backtest_results = agent.backtest_period(
    start_date="2024-01-01",
    end_date="2024-06-01",
    initial_balance=1000
)

print(f"Final balance: ${backtest_results['final_balance']}")
print(f"ROI: {backtest_results['roi']:.2%}")
```

## Key Features

- **Superforecaster Methodology**: Based on Good Judgment Project principles
- **Google News Integration**: Real-time news analysis for informed predictions
- **Parallel Processing**: Efficient benchmark execution
- **Web Interface**: User-friendly frontend for interactive forecasting
- **Market Trading**: Automated trading with Manifold Markets
- **Backtesting**: Historical performance analysis
- **Minimal Dependencies**: Only essential components included