"""
Manifold Markets Integration Package

This package provides integration between AI forecasting capabilities 
and Manifold Markets prediction markets.

Main components:
- ManifoldMarketsClient: API client for Manifold Markets
- ManifoldForecastingBot: AI-powered forecasting bot
- CLI tools for analysis and betting

Example usage:
    from manifold_markets import ManifoldForecastingBot
    
    bot = ManifoldForecastingBot()
    opportunities = bot.find_opportunities()
    results = bot.execute_bets(opportunities, dry_run=True)
"""

from .client import ManifoldMarketsClient
from .forecasting_bot import ManifoldForecastingBot, ForecastedMarket

__all__ = [
    "ManifoldMarketsClient",
    "ManifoldForecastingBot", 
    "ForecastedMarket"
]

__version__ = "0.1.0"
