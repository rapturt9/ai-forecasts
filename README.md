# AI Forecasting System with Inspect AI

A sophisticated forecasting system that leverages the Inspect AI framework for superforecasting with debate methodology. This system combines advanced AI agents with comprehensive evaluation capabilities for accurate prediction tasks.

## Features

- **Inspect AI Integration**: Native support for Inspect AI's evaluation framework
- **Debate Methodology**: Multi-agent debate system with high/low advocates and judges
- **Google News Integration**: Real-time information gathering for informed predictions
- **ForecastBench Evaluation**: Standardized benchmarking against historical data
- **Advanced Logging**: Native Inspect AI logging with web interface viewing
- **Search Budget Management**: Configurable search limits with penalty systems
- **Checkpoint Support**: Resume long-running evaluations from checkpoints

## Installation

1. **Clone the repository:**

```bash
git clone <repository-url>
cd ai-forecasts
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
   Create a `.env` file with:

```bash
OPENROUTER_API_KEY=your_openrouter_api_key
SERP_API_KEY=your_serp_api_key  # Optional for Google News
DEFAULT_MODEL=meta-llama/llama-3.1-8b-instruct:free  # Or your preferred model
```

## Quick Start

### Basic Forecasting

Run a simple forecast on a few questions:

```bash
python run_forecastbench.py --max-questions 5 --max-workers 5 --failure-questions
```

### Full Benchmark Evaluation

Run the complete ForecastBench evaluation:

```bash
python run_forecastbench.py --max-questions 200 --max-workers 10
```

### Resume from Checkpoint

Resume a previous run:

```bash
python run_forecastbench.py --resume latest --max-workers 10
```

### Test Specific Questions

Run on specific question IDs:

```bash
python run_forecastbench.py --question-ids "question1" "question2" --max-workers 3
```

### Test Failure Cases

Run on questions that previously performed poorly:

````bash
python run_forecastbench.py --max-questions 5 --max-workers 5 --failure-questions
```

## Inspect AI Logging and Visualization

This system uses Inspect AI's native logging capabilities for comprehensive evaluation tracking and visualization.

### Automatic Logging

All evaluations are automatically logged using Inspect AI's built-in logging system. Logs are stored in:

- **Log Directory**: `logs/inspect_ai/`
- **Log Format**: JSON with complete evaluation metadata
- **Individual Evaluations**: One log per question/time horizon combination

### Viewing Logs with Inspect AI

#### 1. Start the Inspect AI Log Viewer

After running evaluations, start the web interface:

```bash
inspect view
````

This opens a web browser at `http://localhost:7575` with the Inspect AI log viewer.

#### 2. Alternative: View Specific Log Directory

View logs from a specific directory:

```bash
inspect view logs/inspect_ai/
```

#### 3. Command Line Log Viewing

List recent evaluations:

```bash
inspect logs
```

View a specific evaluation:

```bash
inspect logs list --last 10
inspect logs view <eval_id>
```

### Log Structure

Each evaluation log contains:

```json
{
  "eval": {
    "task": "debate_forecasting_task",
    "dataset": "forecast_question",
    "model": "openrouter/meta-llama/llama-3.1-8b-instruct:free",
    "created": "2025-06-15T10:30:00Z",
    "status": "success"
  },
  "plan": {
    "name": "debate_forecasting",
    "steps": [
      "high_advocate_solver",
      "low_advocate_solver",
      "debate_judge_solver"
    ]
  },
  "samples": [
    {
      "id": 1,
      "input": {
        "question": "Will Apple release...",
        "background": "...",
        "time_horizon": "90 days"
      },
      "target": "forecast_prediction",
      "output": {
        "completion": "...",
        "probability": 0.72,
        "reasoning": "...",
        "confidence": "High"
      },
      "metadata": {
        "search_count": 5,
        "api_calls": 12,
        "search_penalty": 0.0,
        "debate_rounds": 2
      }
    }
  ],
  "stats": {
    "total_time": 45.2,
    "model_usage": {
      "input_tokens": 1250,
      "output_tokens": 340,
      "total_tokens": 1590
    }
  }
}
```

### Key Logging Features

#### 1. Interactive Web Interface

- **Evaluation Browser**: View all evaluations with filtering and search
- **Sample Inspector**: Drill down into individual predictions
- **Performance Metrics**: Built-in charts and statistics
- **Model Comparison**: Compare different model performances

#### 2. Detailed Metadata Tracking

- **Search Activities**: Google News queries and results
- **Agent Interactions**: High advocate, low advocate, and judge reasoning
- **Token Usage**: Input/output tokens for cost tracking
- **Timing Information**: Step-by-step execution timing
- **Error Handling**: Detailed error logs and recovery information

#### 3. Search and Filtering

- **Date Range**: Filter evaluations by time period
- **Model Type**: Filter by specific models used
- **Success/Failure**: View only successful or failed evaluations
- **Question Categories**: Filter by question types or topics

### Advanced Logging Configuration

#### Custom Log Directory

Specify a custom log directory:

```python
from inspect_ai import eval

# Custom log directory
eval_result = eval(
    task=my_forecasting_task(),
    model="openrouter/gpt-4",
    log_dir="custom_logs/experiment_1/"
)
```

#### Metadata Enrichment

The system automatically includes forecast-specific metadata:

```python
# Automatically logged metadata
{
    "search_budget": 10,
    "search_penalty_rate": 0.01,
    "debate_rounds": 2,
    "time_horizons": ["7 days", "30 days", "90 days", "180 days"],
    "google_news_queries": ["query1", "query2"],
    "articles_found": 15,
    "benchmark_mode": true
}
```

## System Architecture

### Core Components

1. **InspectAISuperforecaster**: Main forecasting engine using Inspect AI framework
2. **Debate Methodology**: Multi-agent system with advocates and judges
3. **Google News Integration**: Real-time information gathering
4. **ForecastBench Runner**: Standardized evaluation framework
5. **Checkpoint System**: Fault-tolerant execution with resume capability

### Debate Process

Each forecast follows this process:

1. **High Advocate**: Argues for higher probability outcome
2. **Low Advocate**: Argues for lower probability outcome
3. **Judge**: Synthesizes arguments and makes final prediction
4. **Multiple Rounds**: Iterative refinement (configurable)

### Search Budget System

- **Default Budget**: 10 searches per advocate
- **Penalty Rate**: 0.01 per search beyond budget
- **Search Tracking**: Logged in Inspect AI metadata
- **Budget Enforcement**: Automatic limiting and penalty calculation

## Configuration Options

### Model Configuration

```python
# Environment variables
DEFAULT_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
OPENROUTER_API_KEY = "your_key"

# Supported models (via OpenRouter)
- meta-llama/llama-3.1-8b-instruct:free
- openai/gpt-4o-mini
- anthropic/claude-3-haiku
- And many more...
```

### Forecasting Parameters

```python
superforecaster = InspectAISuperforecaster(
    openrouter_api_key="your_key",
    serp_api_key="your_serp_key",
    debate_mode=True,                    # Enable debate methodology
    debate_rounds=2,                     # Number of debate rounds
    enhanced_quality_mode=True,          # Enhanced quality processing
    search_budget_per_advocate=10,       # Search budget per agent
    recommended_articles=10,             # Target articles to find
    max_search_queries=5                 # Max queries per agent
)
```

### Benchmark Configuration

```bash
# Run parameters
--max-questions 200        # Number of questions to process
--max-workers 10           # Parallel workers
--resume latest           # Resume from latest checkpoint
--seed 42                 # Random seed for reproducibility
--failure-questions       # Test only previously failed questions
```

## Data Files

### Required Files

- `forecastbench_human_2024.json`: Question dataset
- `forecast_human_resolution_2024.json`: Historical resolutions

### Generated Files

- `logs/inspect_ai/`: Native Inspect AI evaluation logs
- `checkpoints/`: Evaluation checkpoints for resuming
- `results/`: Final benchmark results and analysis
- `cache/google_news/`: Cached Google News results

## Performance and Monitoring

### Viewing Real-time Performance

Use the Inspect AI web interface to monitor:

- **Active Evaluations**: See currently running tasks
- **Progress Tracking**: Real-time completion status
- **Resource Usage**: Token consumption and API costs
- **Error Monitoring**: Failed evaluations and error details

### Performance Metrics

The system tracks:

- **Brier Scores**: Accuracy of probability predictions
- **Search Efficiency**: Searches per question ratio
- **Time per Question**: Processing speed metrics
- **Success Rate**: Evaluation completion rate
- **Cost Tracking**: Token usage and API costs

### Benchmark Results

Results include:

- **Overall Brier Score**: Average prediction accuracy
- **Time Horizon Performance**: Accuracy by prediction timeframe
- **Search Penalties**: Impact of exceeding search budgets
- **Individual Question Analysis**: Detailed per-question breakdown

## Troubleshooting

### Common Issues

1. **API Key Issues**

   ```bash
   # Check environment variables
   echo $OPENROUTER_API_KEY
   echo $SERP_API_KEY
   ```

2. **Missing Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Log Viewing Issues**

   ```bash
   # Start log viewer manually
   inspect view logs/inspect_ai/
   ```

4. **Memory Issues with Large Evaluations**
   ```bash
   # Reduce parallel workers
   python run_forecastbench.py --max-workers 3
   ```

### Debug Mode

Enable detailed debugging:

```bash
# Set debug environment
export INSPECT_AI_LOG_LEVEL=debug
python run_forecastbench.py --max-questions 5
```

## Advanced Usage

### Custom Evaluation Tasks

Create custom forecasting tasks:

```python
from inspect_ai import Task, task
from inspect_ai.solver import chain, generate

@task
def custom_forecasting_task():
    return Task(
        dataset=[{"question": "Your question here"}],
        solver=chain(
            system_message("You are a superforecaster..."),
            generate()
        )
    )
```

### Extending the System

1. **Custom Agents**: Add new agent types to the debate system
2. **New Data Sources**: Integrate additional information sources
3. **Custom Scorers**: Implement domain-specific evaluation metrics
4. **Model Integration**: Add support for new model providers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the Inspect AI documentation: https://inspect.ai-safety-institute.org.uk/
2. Review the troubleshooting section above
3. Open an issue in the repository
4. Check the Inspect AI community resources

## Inspect AI Resources

- **Documentation**: https://inspect.ai-safety-institute.org.uk/
- **Examples**: https://github.com/UKGovernmentBEIS/inspect_ai/tree/main/examples
- **Community**: https://github.com/UKGovernmentBEIS/inspect_ai/discussions
- **API Reference**: https://inspect.ai-safety-institute.org.uk/api/
