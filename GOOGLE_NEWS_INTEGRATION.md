# Google News Superforecaster Integration

## Overview

The AI forecasting system has been enhanced with a Google News Superforecaster that uses timestamped Google News search via SERP API to simulate the research process used by top superforecasters. This system provides comprehensive news research with precise time filtering to avoid data leakage in benchmark evaluations.

## Key Features

### 🔍 Timestamped Google News Search
- **SERP API Integration**: Uses Google Search Results API for real-time news search
- **Precise Time Filtering**: Searches from June 2024 to freeze date for benchmarks
- **Multiple Search Strategies**: 6 different research approaches per question
- **Source Diversity**: Searches across major news outlets and domains

### 📰 Search Timeframes
- **Benchmark Questions**: June 2024 → Freeze timestamp (avoids data leakage)
- **Current Questions**: June 2024 → Current timestamp
- **Custom Date Ranges**: Supports any specified cutoff date

### 🤖 Specialized Agent Team
1. **News Research Coordinator**: Manages comprehensive Google News research
2. **Historical News Analyst**: Finds historical precedents via timestamped search
3. **Current News Context Analyst**: Analyzes recent developments
4. **Expert Opinion News Aggregator**: Gathers expert predictions from news
5. **Contrarian News Research Specialist**: Seeks opposing viewpoints
6. **Synthesis and Calibration Expert**: Integrates all research into calibrated forecast

## Implementation Details

### Core Components

#### GoogleNewsSuperforecaster Class
```python
from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster

forecaster = GoogleNewsSuperforecaster(
    openrouter_api_key="your_key",
    serp_api_key="your_serp_key"
)

result = forecaster.forecast_with_google_news(
    question="Will AGI be achieved by 2027?",
    background="Context about AGI development",
    cutoff_date=datetime(2024, 8, 15),
    is_benchmark=True  # Enables proper time filtering
)
```

#### Search Strategies
The system employs 6 research strategies per question:

1. **Main Question**: Direct search for the question topic
2. **Base Rate Research**: Historical precedents and similar cases
3. **Current Context**: Recent developments and latest news
4. **Expert Opinions**: Expert predictions and professional forecasts
5. **Contrarian Views**: Skeptical viewpoints and opposing opinions
6. **Leading Indicators**: Early signals and warning signs

#### SERP API Configuration
```python
search_params = {
    "api_key": serp_api_key,
    "engine": "google",
    "q": query,
    "tbm": "nws",  # News search
    "tbs": f"cdr:1,cd_min:{start_date},cd_max:{end_date}",  # Custom date range
    "num": 10,
    "hl": "en",
    "gl": "us"
}
```

### Integration Points

#### Benchmark System
- **File**: `run_comprehensive_benchmark.py`
- **Enhancement**: Uses Google News Superforecaster with `is_benchmark=True`
- **Time Filtering**: Automatically searches June 2024 → freeze date
- **Data Integrity**: Prevents future information leakage

#### Frontend System
- **File**: `src/ai_forecasts/frontend/streamlit_app.py`
- **Enhancement**: Added "Google News Superforecaster" option
- **API Endpoint**: `/forecast/google_news`
- **User Control**: Checkbox to enable/disable Google News research

## Configuration

### Environment Variables
```bash
# Required: SERP API Key for Google News search
SERP_API_KEY=your_serp_api_key_here

# Required: OpenRouter API Key for LLM access
OPENROUTER_API_KEY=your_openrouter_key_here
```

### Dependencies
```bash
pip install google-search-results>=2.4.2
pip install crewai>=0.126.0
pip install langchain>=0.3.25
```

## Usage Examples

### Benchmark Evaluation
```python
from run_comprehensive_benchmark import ComprehensiveBenchmarkRunner

runner = ComprehensiveBenchmarkRunner()
results = runner.run_comprehensive_benchmark(num_questions=5)
```

### Direct Forecasting
```python
from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster
from datetime import datetime

forecaster = GoogleNewsSuperforecaster(
    openrouter_api_key="your_key",
    serp_api_key="your_serp_key"
)

# For benchmark question (time-filtered)
result = forecaster.forecast_with_google_news(
    question="Will Bitcoin reach $100k by end of 2024?",
    cutoff_date=datetime(2024, 8, 15),
    is_benchmark=True
)

# For current question (up to now)
result = forecaster.forecast_with_google_news(
    question="Will AGI be achieved by 2027?",
    is_benchmark=False
)
```

### Frontend Usage
1. Open Streamlit app
2. Check "📰 Use Google News Superforecaster"
3. Enter your forecasting question
4. System automatically searches Google News with appropriate time filtering

## Technical Architecture

### Search Process Flow
1. **Question Analysis**: Parse question and determine search strategies
2. **Timeframe Calculation**: Set appropriate date range based on benchmark status
3. **Multi-Strategy Search**: Execute 6 different search approaches via SERP API
4. **Source Evaluation**: Assess credibility and relevance of news sources
5. **Agent Analysis**: 6 specialized agents analyze different aspects
6. **Synthesis**: Combine all research into calibrated probability forecast

### Data Quality Measures
- **Source Credibility**: Prioritizes major news outlets and verified sources
- **Temporal Relevance**: Filters articles by publication date
- **Content Quality**: Evaluates snippet relevance and article depth
- **Bias Mitigation**: Seeks diverse perspectives and contrarian views

### Fallback Mechanisms
- **Simulated Research**: If SERP API unavailable, uses simulated news results
- **Error Handling**: Graceful degradation with informative error messages
- **Quality Scoring**: Tracks research quality and completeness

## Benefits

### For Benchmarks
- **No Data Leakage**: Strict time filtering prevents future information
- **Historical Accuracy**: Searches only news available at freeze time
- **Reproducible Results**: Consistent search parameters across evaluations

### For Current Forecasting
- **Real-Time Research**: Access to latest news and developments
- **Comprehensive Coverage**: Multiple search strategies ensure thoroughness
- **Expert Integration**: Captures professional opinions and analysis

### For Superforecaster Methodology
- **Base Rate Research**: Finds historical precedents via news archives
- **Current Context**: Analyzes recent developments and trends
- **Multiple Perspectives**: Includes both mainstream and contrarian views
- **Calibrated Synthesis**: Combines all evidence into well-reasoned forecast

## Performance Characteristics

### Search Efficiency
- **Parallel Processing**: Multiple search strategies executed efficiently
- **Rate Limiting**: Respects SERP API limits and quotas
- **Caching**: Avoids duplicate searches for similar queries

### Quality Metrics
- **Articles Found**: Tracks total articles discovered per question
- **Source Diversity**: Measures variety of news outlets consulted
- **Research Completeness**: Scores methodology component coverage
- **Evidence Quality**: Assesses strength and relevance of findings

## Future Enhancements

### Planned Improvements
- **Advanced Filtering**: More sophisticated relevance scoring
- **Source Ranking**: Weighted credibility scoring for news outlets
- **Trend Analysis**: Temporal analysis of news coverage patterns
- **Multi-Language**: Support for non-English news sources

### Integration Opportunities
- **Real-Time Updates**: Live news monitoring for ongoing forecasts
- **Social Media**: Integration with Twitter/X and other platforms
- **Academic Sources**: Addition of research papers and reports
- **Market Data**: Integration with financial and economic indicators

## Conclusion

The Google News Superforecaster represents a significant enhancement to the AI forecasting system, providing:

1. **Rigorous Research**: Systematic news research following superforecaster methodology
2. **Temporal Integrity**: Proper time filtering for benchmark evaluations
3. **Comprehensive Coverage**: Multiple search strategies and diverse perspectives
4. **Quality Assurance**: Source credibility assessment and bias mitigation
5. **Scalable Architecture**: Efficient processing of multiple questions

This system enables the AI forecasting platform to conduct research comparable to top human superforecasters while maintaining the speed and consistency advantages of automated systems.