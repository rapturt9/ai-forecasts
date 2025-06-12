# Manifold Markets AI Forecasting Bot

This module integrates Google News Superforecaster AI capabilities with Manifold Markets prediction markets, allowing you to:

- Analyze prediction markets using AI forecasting
- Find betting opportunities where AI predictions differ significantly from market prices
- Execute automated trading strategies (with safeguards)
- Generate comprehensive market analysis reports

## Features

🤖 **AI-Powered Analysis**: Uses Google News Superforecaster with multi-agent CrewAI system
📊 **Market Intelligence**: Fetches and analyzes Manifold Markets data via API
🎯 **Opportunity Detection**: Identifies markets where AI disagrees with crowd wisdom
💸 **Automated Trading**: Optional bet execution with configurable risk management
📈 **Comprehensive Reporting**: Detailed analysis and performance tracking

## Quick Start

### 1. Set up environment variables

```bash
export MANIFOLD_API_KEY="your_manifold_api_key"      # Required for betting
export OPENROUTER_API_KEY="your_openrouter_api_key"  # Required for AI
export SERP_API_KEY="your_serp_api_key"             # Optional for news search
```

### 2. Install dependencies

```bash
# Activate mamba environment
mamba activate forecaster

# Install additional dependencies if needed
pip install requests python-dotenv
```

### 3. Basic usage

```python
from manifold_markets import ManifoldForecastingBot

# Initialize bot
bot = ManifoldForecastingBot()

# Analyze markets
forecasts = bot.analyze_markets(limit=10)

# Find opportunities
opportunities = bot.find_opportunities(min_difference=0.15)

# Simulate betting (dry run)
results = bot.execute_bets(opportunities, dry_run=True)
```

## API Setup

### Manifold Markets API Key

1. Go to [Manifold Markets](https://manifold.markets)
2. Sign in to your account
3. Navigate to your profile settings
4. Generate an API key
5. Set as `MANIFOLD_API_KEY` environment variable

### OpenRouter API Key

1. Go to [OpenRouter](https://openrouter.ai)
2. Sign up/sign in
3. Go to Keys section
4. Create a new API key
5. Set as `OPENROUTER_API_KEY` environment variable

### SERP API Key (Optional)

1. Go to [SerpAPI](https://serpapi.com)
2. Sign up for an account
3. Get your API key from dashboard
4. Set as `SERP_API_KEY` environment variable

## CLI Usage

The module includes a command-line interface for easy operation:

### Analyze markets without betting

```bash
python src/manifold_markets/cli.py analyze --limit 20 --output analysis.json
```

### Find betting opportunities

```bash
python src/manifold_markets/cli.py opportunities --min-difference 0.15 --min-confidence medium
```

### Execute bets (dry run)

```bash
python src/manifold_markets/cli.py opportunities --execute --dry-run --max-bet-total 50
```

### Test API connections

```bash
python src/manifold_markets/cli.py test
```

## Examples

### Basic Market Analysis

```python
from manifold_markets import ManifoldForecastingBot

bot = ManifoldForecastingBot()

# Analyze top markets
markets = bot.analyze_markets(limit=5)

for market in markets:
    print(f"Question: {market.question}")
    print(f"Market: {market.current_prob:.1%}")
    print(f"AI: {market.ai_forecast.probability:.1%}")
    print(f"Difference: {market.forecast_difference:+.1%}")
    print(f"Action: {market.recommended_action}")
    print()
```

### Find Opportunities

```python
# Find markets where AI significantly disagrees
opportunities = bot.find_opportunities(
    min_difference=0.20,      # 20% difference
    min_confidence="high",    # High confidence only
    limit=50                  # Check 50 markets
)

print(f"Found {len(opportunities)} opportunities")
```

### Execute Betting Strategy

```python
# Dry run first
dry_results = bot.execute_bets(opportunities, dry_run=True, max_total_amount=100)

# If satisfied with dry run, execute for real
if input("Execute real bets? (y/N): ").lower() == 'y':
    real_results = bot.execute_bets(opportunities, dry_run=False, max_total_amount=100)
```

### Generate Analysis Report

```python
markets = bot.analyze_markets(limit=25)
report = bot.generate_report(markets)

print(f"Analyzed {report['summary']['total_markets_analyzed']} markets")
print(f"Found {report['summary']['betting_opportunities']} opportunities")
print(f"Average difference: {report['summary']['average_probability_difference']:.1%}")
```

## Configuration

### Bot Parameters

```python
bot = ManifoldForecastingBot(
    default_bet_amount=10.0,        # Default bet size in Mana
    confidence_threshold=0.15,      # Minimum difference to consider betting
    manifold_api_key="your_key",    # API keys
    openrouter_api_key="your_key",
    serp_api_key="your_key"
)
```

### Risk Management

The bot includes several risk management features:

- **Confidence thresholds**: Only bet on high-confidence predictions
- **Difference thresholds**: Require significant disagreement with market
- **Maximum bet limits**: Cap total betting amounts
- **Market filters**: Avoid closed/resolved markets
- **Time filters**: Skip markets closing soon
- **Dry run mode**: Test strategies without real money

## Understanding the Output

### Market Analysis

Each analyzed market includes:

- **Current probability**: Market's current price
- **AI probability**: AI forecast probability
- **Difference**: How much AI disagrees with market
- **Confidence**: AI's confidence level (low/medium/high)
- **Action**: Recommended action (BUY_YES/BUY_NO/HOLD/AVOID)
- **Reasoning**: AI's explanation for the forecast

### Betting Opportunities

Opportunities are ranked by:

1. **Absolute difference**: Larger disagreements ranked higher
2. **Confidence level**: Higher confidence preferred
3. **Evidence quality**: Better evidence weighted more

### Risk Indicators

- **Low confidence**: AI is uncertain, avoid betting
- **Market closing soon**: Avoid due to time risk
- **Small difference**: Below threshold, not worth betting
- **High volatility**: Market may be unstable

## Safety Features

### Dry Run Mode

Always test strategies in dry run mode first:

```python
results = bot.execute_bets(opportunities, dry_run=True)
```

### Position Limits

Set maximum betting amounts:

```python
results = bot.execute_bets(opportunities, max_total_amount=50.0)
```

### Confidence Filters

Only bet on high-confidence predictions:

```python
opportunities = bot.find_opportunities(min_confidence="high")
```

## Monitoring and Tracking

### Save Analysis Results

```python
# Save detailed analysis
import json
with open('analysis.json', 'w') as f:
    json.dump(report, f, indent=2)
```

### Track Performance

```python
# Monitor bet results
results = bot.execute_bets(opportunities)
successful_bets = [r for r in results if r['success']]
print(f"Placed {len(successful_bets)} bets successfully")
```

## Troubleshooting

### Common Issues

1. **"No OpenRouter API key"**

   - Set `OPENROUTER_API_KEY` environment variable
   - Check key is valid at openrouter.ai

2. **"No markets found"**

   - Check Manifold Markets is accessible
   - Try different search terms or increase limit

3. **"Failed to place bet"**

   - Verify `MANIFOLD_API_KEY` is set and valid
   - Check you have sufficient Mana balance
   - Ensure market is still open

4. **"SERP API errors"**
   - SERP key is optional but improves forecasting
   - Bot will work without it but with limited news data

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Ethics and Responsible Use

### Guidelines

- **Start small**: Begin with small bet amounts to test strategies
- **Diversify**: Don't put all money on a single prediction
- **Monitor performance**: Track accuracy and adjust strategies
- **Respect limits**: Don't exceed your risk tolerance
- **Educational use**: Consider this primarily a learning tool

### Disclaimers

- AI predictions are not guaranteed to be accurate
- Prediction markets involve financial risk
- Past performance doesn't predict future results
- Use only money you can afford to lose
- This is experimental software - use at your own risk

## Advanced Usage

### Custom Forecasting Strategy

```python
class CustomForecastingBot(ManifoldForecastingBot):
    def _determine_action(self, ai_forecast, current_prob, forecast_diff, market):
        # Custom logic for bet sizing and market selection
        # Override default behavior
        pass
```

### Batch Processing

```python
# Process many markets efficiently
all_markets = bot.manifold.get_markets(limit=500)
forecasts = []

for market in all_markets:
    forecast = bot.analyze_market(market)
    if forecast:
        forecasts.append(forecast)

# Filter and rank opportunities
opportunities = [f for f in forecasts if abs(f.forecast_difference) > 0.20]
```

### Portfolio Management

```python
# Track positions and performance
positions = bot.manifold.get_user_positions("your_username")
bets = bot.manifold.get_user_bets()

# Analyze performance
profitable_bets = [b for b in bets if b.get('profit', 0) > 0]
print(f"Profitable bets: {len(profitable_bets)}/{len(bets)}")
```

## API Reference

See individual module documentation:

- `ManifoldMarketsClient`: Raw API access
- `ManifoldForecastingBot`: Main bot class
- `ForecastedMarket`: Market analysis result

## Support

For issues or questions:

1. Check this README
2. Review example scripts
3. Enable debug logging
4. Check API key configuration
5. Verify network connectivity

## Contributing

To improve the forecasting bot:

1. Test with different confidence thresholds
2. Implement new risk management strategies
3. Add market filtering criteria
4. Enhance reporting capabilities
5. Optimize API usage patterns
