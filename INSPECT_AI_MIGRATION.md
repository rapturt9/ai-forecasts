# Inspect AI Migration Guide

## Overview

The AI Forecasting system has been successfully updated to support both Inspect AI and CrewAI frameworks, with Inspect AI as the default for enhanced evaluation and monitoring capabilities. This migration maintains full backwards compatibility while providing improved agent orchestration and evaluation features.

## Key Changes

### 1. New Inspect AI Implementation

- **New Module**: `src/ai_forecasts/agents/inspect_ai_superforecaster.py`
- **Framework**: Uses Inspect AI's task, solver, and agent system
- **Debate Mode**: Implements multi-agent debate using Inspect AI's `fork` solver for parallel execution
- **Tool Integration**: Wraps existing Google News tool for Inspect AI compatibility

### 2. Enhanced GoogleNewsSuperforecaster

- **Backwards Compatibility**: Existing CrewAI implementation remains fully functional
- **Automatic Delegation**: New `use_inspect_ai` parameter controls which framework to use
- **Environment Control**: `USE_INSPECT_AI` environment variable for global configuration
- **Seamless Interface**: Same API for both implementations

### 3. Updated Dependencies

- **Added**: `inspect-ai>=0.3.104` to requirements.txt
- **Maintained**: All existing CrewAI dependencies for backwards compatibility

## Configuration

### Environment Variables

```bash
# Enable Inspect AI by default (recommended)
USE_INSPECT_AI=true

# API Keys (unchanged)
OPENROUTER_API_KEY=your_key_here
SERP_API_KEY=your_key_here
DEFAULT_MODEL=openai/gpt-4.1
```

### Programmatic Control

```python
# Use Inspect AI (recommended)
forecaster = GoogleNewsSuperforecaster(
    openrouter_api_key=api_key,
    serp_api_key=serp_key,
    use_inspect_ai=True,
    debate_mode=True
)

# Use CrewAI (backwards compatibility)
forecaster = GoogleNewsSuperforecaster(
    openrouter_api_key=api_key,
    serp_api_key=serp_key,
    use_inspect_ai=False,
    debate_mode=True
)

# Auto-detect from environment (default behavior)
forecaster = GoogleNewsSuperforecaster(
    openrouter_api_key=api_key,
    serp_api_key=serp_key
    # use_inspect_ai=None (default) - reads from USE_INSPECT_AI env var
)
```

## Benefits of Inspect AI

### 1. Enhanced Evaluation and Monitoring

- **Built-in Evaluation**: Inspect AI provides comprehensive evaluation frameworks
- **Logging and Tracing**: Better observability of agent interactions
- **Structured Tasks**: More organized task definition and execution

### 2. Improved Agent Orchestration

- **Parallel Execution**: `fork` solver enables true parallel agent execution
- **Solver Composition**: Chain and compose solvers for complex workflows
- **Tool Integration**: Cleaner tool integration with type safety

### 3. Better Debugging and Development

- **Task Isolation**: Each task runs in isolation for better debugging
- **Structured Outputs**: More predictable and parseable agent outputs
- **Error Handling**: Improved error handling and recovery

## Migration Path

### For Existing Users

1. **No Action Required**: System defaults to CrewAI if `USE_INSPECT_AI` is not set
2. **Gradual Migration**: Set `USE_INSPECT_AI=true` to enable new features
3. **Testing**: Use the test scripts to verify functionality

### For New Deployments

1. **Recommended**: Set `USE_INSPECT_AI=true` in environment
2. **Install Dependencies**: Run `pip install -r requirements.txt`
3. **Verify Setup**: Run `python test_simple_integration.py`

## API Compatibility

### Unchanged Interfaces

- `forecast_with_google_news()` method signature remains identical
- `ForecastResult` structure unchanged
- All existing parameters and options supported

### Enhanced Features

- Better structured outputs with Inspect AI
- Improved parallel processing in debate mode
- Enhanced logging and monitoring capabilities

## Testing

### Basic Integration Test

```bash
python test_simple_integration.py
```

### Full Integration Test (with actual forecasting)

```bash
python test_inspect_ai_integration.py
```

### Benchmark Testing

The benchmark runner (`run_forecastbench.py`) has been updated to use Inspect AI by default while maintaining full compatibility.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `inspect-ai` is installed: `pip install inspect-ai`
2. **API Key Issues**: Verify `OPENROUTER_API_KEY` and `SERP_API_KEY` are set
3. **Model Access**: Ensure the specified model is available through OpenRouter

### Fallback Behavior

- If Inspect AI import fails, system automatically falls back to CrewAI
- Warning messages logged when fallback occurs
- No functionality loss in fallback mode

## Performance Considerations

### Inspect AI Advantages

- **Parallel Processing**: True parallel execution of debate agents
- **Memory Efficiency**: Better memory management for long-running tasks
- **Scalability**: More efficient for batch processing

### Migration Impact

- **Minimal Overhead**: Delegation layer adds negligible performance cost
- **Memory Usage**: Slightly higher due to dual framework support
- **Startup Time**: Marginal increase due to framework detection

## Future Roadmap

### Phase 1 (Current)
- ✅ Basic Inspect AI integration
- ✅ Backwards compatibility
- ✅ Environment-based configuration

### Phase 2 (Planned)
- Enhanced evaluation metrics using Inspect AI scorers
- Advanced multi-agent workflows
- Integration with Inspect AI's built-in evaluation tools

### Phase 3 (Future)
- Potential deprecation of CrewAI support (with advance notice)
- Full migration to Inspect AI-native implementations
- Advanced monitoring and analytics features

## Support

For issues related to the Inspect AI migration:

1. Check the troubleshooting section above
2. Run the integration tests to verify setup
3. Review logs for specific error messages
4. Ensure all dependencies are properly installed

The system is designed to be robust and maintain functionality even if Inspect AI is not available, ensuring continuous operation during the migration period.