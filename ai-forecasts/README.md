# AI Forecasting Trading System

A streamlined AI forecasting system with 3 core functionalities:

## 🤖 Agent Groups

1. **Google News Superforecaster** (`src/ai_forecasts/agents/google_news_superforecaster.py`)
   - Advanced superforecasting with Google News integration
   - Bias correction and evidence quality assessment

2. **Market Agent** (`src/ai_forecasts/agents/market_agent.py`)
   - Integrates superforecaster with Manifold Markets trading
   - Kelly Criterion position sizing

## 🚀 Core Functionalities

### 1. ForecastBench Parallel Evaluation
```bash
python run_forecastbench.py
```
- Runs the Google News Superforecaster on ForecastBench dataset in parallel
- Evaluates forecasting performance with comprehensive metrics

### 2. Trading Interface Frontend
```bash
python run_frontend.py
```
- Next.js trading interface with real-time market analysis
- AI-powered trading decisions with detailed reasoning
- Live trading and backtesting capabilities

### 3. Manifold Markets Trading & Backtesting
```bash
python run_manifold_trading.py
```
- Live trading with Manifold Markets API
- Historical backtesting between time periods
- Kelly Criterion optimization

## 📁 Minimal File Structure

```
ai-forecasts-clean/
├── src/
│   ├── ai_forecasts/
│   │   ├── agents/
│   │   │   ├── google_news_superforecaster.py  # Core forecasting agent
│   │   │   └── market_agent.py                 # Trading agent
│   │   └── utils/                              # Utilities
│   └── manifold_markets/                       # Manifold integration
├── trading-interface/                          # Next.js frontend
├── run_forecastbench.py                       # Functionality 1
├── run_frontend.py                            # Functionality 2
├── run_manifold_trading.py                    # Functionality 3
└── requirements.txt
```

## 🔧 Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
cd trading-interface && npm install
```

2. Set environment variables:
```bash
OPENROUTER_API_KEY=your_key_here
MANIFOLD_API_KEY=your_key_here  # Optional
SERP_API_KEY=your_key_here      # Optional
```

3. Run any of the 3 functionalities above

## 🎯 Features

- **Parallel Processing**: ForecastBench evaluation with configurable workers
- **Real-time Trading**: Live market analysis and trading decisions
- **Backtesting**: Historical performance analysis with Sharpe ratio
- **Kelly Criterion**: Optimal position sizing for risk management
- **Comprehensive UI**: Modern Next.js interface with charts and analytics