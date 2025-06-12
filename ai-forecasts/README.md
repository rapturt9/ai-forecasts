# AI Forecasting Trading System

A minimal, focused AI forecasting system with 3 core functionalities:

1. **ForecastBench Parallel Evaluation** - Run Google News Superforecaster on ForecastBench dataset
2. **Trading Interface Frontend** - Next.js interface for strategy and forecast prediction  
3. **Manifold Trading & Backtesting** - Live trading and historical backtesting with Manifold Markets

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- OpenRouter API key (required)
- Manifold Markets API key (optional, for live trading)
- SERP API key (optional, for enhanced Google News search)

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for trading interface
cd trading-interface
npm install
cd ..
```

### Environment Setup

Create a `.env` file in the root directory:

```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional (for enhanced functionality)
MANIFOLD_API_KEY=your_manifold_api_key_here
SERP_API_KEY=your_serp_api_key_here
```

## 📋 How to Run Everything

### 1. 🧪 ForecastBench Parallel Evaluation

**Purpose**: Evaluate the Google News Superforecaster on the ForecastBench dataset with parallel processing.

```bash
python run_forecastbench.py
```

**What it does**:
- Loads 200 questions from ForecastBench dataset
- Runs Google News Superforecaster in parallel (configurable workers)
- Provides detailed forecasting with confidence levels and reasoning
- Saves results with performance metrics and timestamps
- Shows success rate, average confidence, and processing time

**Expected Output**:
```
🚀 Starting ForecastBench parallel evaluation (max_questions=20, workers=3)
📊 Loaded 200 questions from ForecastBench dataset
🔄 Processing questions in parallel...
✅ Completed 20/20 questions (100.0% success rate)
📈 Average confidence: 0.75, Average probability: 0.62
⏱️ Total time: 45.2 seconds
💾 Results saved to: results/forecastbench_results_20241212_143022.json
```

### 2. 🖥️ Trading Interface Frontend

**Purpose**: Launch the Next.js trading interface for interactive forecasting and trading analysis.

```bash
python run_frontend.py
```

**What it does**:
- Starts Next.js development server on port 12000
- Provides complete trading interface with AI analysis
- Shows live trading metrics and performance charts
- Enables backtesting with historical data
- Displays trade history with detailed reasoning

**Features**:
- **Live Trading Tab**: Real-time performance metrics (balance, returns, win rate)
- **Market Analysis**: AI-powered trading decisions with BUY_YES/BUY_NO recommendations
- **Backtesting**: Historical performance analysis with Sharpe ratios
- **Trade History**: Detailed trade records with strategy indicators
- **Trade Details**: Comprehensive AI reasoning and risk assessment

**Access**: Open http://localhost:12000 in your browser

### 3. 💰 Manifold Trading & Backtesting

**Purpose**: Execute live trading and backtesting with Manifold Markets API integration.

```bash
python run_manifold_trading.py
```

**What it does**:
- **Live Trading Demo**: Analyzes real Manifold markets and makes trading decisions
- **Historical Backtesting**: Tests strategy performance over configurable time periods
- **Kelly Criterion**: Optimizes position sizing based on edge and confidence
- **Performance Analysis**: Calculates returns, win rates, and risk metrics

**Expected Output**:
```
🤖 Manifold Markets Trading & Backtesting System
================================================
🔴 Starting Live Trading Demo (max_markets=3)
📊 Analyzing market: "Will Bitcoin reach $100,000 by end of 2024?"
🎯 AI Decision: BUY_YES (confidence: 72%, edge: 15.2%)
💰 Kelly Criterion: Bet 185 mana (18.5% of balance)
📈 Trade executed: +12.3% return

🔙 Starting Backtesting (2024-11-12 to 2024-12-12)
📊 Backtesting Results:
   • Total Return: +18.7%
   • Win Rate: 71.4%
   • Sharpe Ratio: 1.52
   • Max Drawdown: -8.3%
   • Total Trades: 14
```

## 🏗️ Architecture

### Agent Groups

#### 🤖 Core Agent Group
- **Google News Superforecaster** (`src/ai_forecasts/agents/google_news_superforecaster.py`)
  - Advanced superforecasting with Google News integration
  - CrewAI multi-agent system with bias correction
  - Evidence quality assessment and base rate analysis
  - Confidence calibration and reasoning transparency

#### 💼 Market Agent Group  
- **Market Agent** (`src/ai_forecasts/agents/market_agent.py`)
  - Integrates superforecaster with Manifold Markets trading
  - Kelly Criterion position sizing optimization
  - Risk management and edge detection
  - Sophisticated trading decision logic

### Key Components

#### 📊 Manifold Markets Integration (`src/manifold_markets/`)
- **Client** (`client.py`): API wrapper for Manifold Markets
- **Backtesting** (`backtesting.py`): Historical performance testing
- **Kelly Criterion** (`kelly_criterion.py`): Optimal position sizing
- **Historical Data** (`historical_data.py`): Mock data for testing

#### 🖥️ Trading Interface (`trading-interface/`)
- **Next.js 15** with TypeScript and Tailwind CSS
- **Prisma ORM** with SQLite database
- **Real-time charts** and performance metrics
- **API routes** for backend integration

#### 🛠️ Utilities (`src/ai_forecasts/utils/`)
- **Agent Logger** (`agent_logger.py`): Comprehensive logging system
- **LLM Client** (`llm_client.py`): OpenRouter API integration
- **Google News Tool** (`google_news_tool.py`): News search and analysis

## 🔧 Configuration

### ForecastBench Settings
- `max_questions`: Number of questions to process (default: 20)
- `max_workers`: Parallel processing threads (default: 3)

### Trading Settings
- `initial_balance`: Starting balance for backtesting (default: 1000)
- `max_markets`: Number of markets to analyze (default: 5)
- `confidence_threshold`: Minimum confidence for trades (default: 0.6)

### Frontend Settings
- `port`: Development server port (default: 12000)
- `hostname`: Server hostname (default: 0.0.0.0)

## 📈 Performance Metrics

### ForecastBench Evaluation
- **Success Rate**: Percentage of successfully processed questions
- **Average Confidence**: Mean confidence level across predictions
- **Processing Time**: Total time for parallel evaluation
- **Accuracy**: Comparison with human forecaster benchmarks

### Trading Performance
- **Total Return**: Percentage gain/loss over period
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted return metric
- **Max Drawdown**: Largest peak-to-trough decline
- **Kelly Utilization**: Fraction of optimal Kelly bet size used

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in Python path
2. **API Key Issues**: Verify environment variables are set correctly
3. **Port Conflicts**: Change port in `run_frontend.py` if 12000 is occupied
4. **Node.js Issues**: Ensure Node.js 18+ is installed for trading interface

### Debug Mode
Add `DEBUG=true` to your `.env` file for verbose logging.

## 📝 File Structure

```
ai-forecasts/
├── src/
│   ├── ai_forecasts/
│   │   ├── agents/
│   │   │   ├── google_news_superforecaster.py  # Core forecasting
│   │   │   └── market_agent.py                 # Trading execution
│   │   └── utils/                              # Essential utilities
│   └── manifold_markets/                       # Manifold integration
├── trading-interface/                          # Next.js frontend
├── run_forecastbench.py                       # Functionality 1
├── run_frontend.py                            # Functionality 2
├── run_manifold_trading.py                    # Functionality 3
├── requirements.txt                           # Python dependencies
└── README.md                                  # This file
```

## 🎯 Next Steps

1. **Deploy Frontend**: Use Vercel for production deployment
2. **Add Real Data**: Integrate live Manifold Markets data
3. **Enhance Models**: Add more sophisticated forecasting models
4. **Scale Trading**: Implement automated trading strategies
5. **Monitor Performance**: Add real-time performance tracking