"""
Google News Search Tool for CrewAI Agents
Provides real-time Google News search capabilities via SERP API
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GoogleNewsInput(BaseModel):
    """Input model for Google News search"""
    query: str = Field(..., description="Search query for Google News")
    search_type: Optional[str] = Field("current", description="Type of search: current, expert_opinions, historical, contrarian")


class GoogleNewsTool(BaseTool):
    """Tool for searching Google News with timestamp filtering"""
    
    name: str = "Google News Search"
    description: str = """
    Search Google News for recent articles and developments. Use this tool to find:
    - Recent news about specific topics
    - Expert opinions and analysis
    - Market developments and trends
    - Historical precedents and comparisons
    - Contrarian viewpoints and criticism
    
    Input should be a search query string. The tool will return recent news articles
    with titles, sources, snippets, and publication information.
    """
    args_schema: type = GoogleNewsInput
    
    def __init__(self, serp_api_key: str = None, search_timeframe: Dict[str, str] = None):
        super().__init__()
        # Store configuration in internal attributes that don't conflict with Pydantic
        self._serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        self._search_timeframe = search_timeframe or {
            "start": "06/01/2024",
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        self._setup_serp_client()
    
    def _setup_serp_client(self):
        """Setup SERP API client"""
        try:
            from serpapi import GoogleSearch
            if self._serp_api_key:
                self._serp_client = GoogleSearch
                self._client_available = True
            else:
                self._serp_client = None
                self._client_available = False
                print("⚠️ SERP API key not found, Google News search will be simulated")
        except ImportError:
            self._serp_client = None
            self._client_available = False
            print("⚠️ google-search-results not installed, Google News search will be simulated")
    
    def _run(self, query: str, search_type: str = "current") -> str:
        """Execute Google News search for the given query"""
        
        if not self._client_available:
            return self._simulate_search(query)
        
        try:
            # Configure SERP search parameters for Google News
            search_params = {
                "api_key": self._serp_api_key,
                "engine": "google",
                "q": query,
                "tbm": "nws",  # News search
                "tbs": f"cdr:1,cd_min:{self._search_timeframe['start']},cd_max:{self._search_timeframe['end']}",
                "num": 15,  # Number of results
                "hl": "en",   # Language
                "gl": "us"    # Country
            }
            
            # Perform the search
            search = self._serp_client(search_params)
            search_result = search.get_dict()
            
            articles = []
            
            # Process news results
            if "news_results" in search_result:
                for article in search_result["news_results"][:10]:  # Limit to top 10
                    articles.append({
                        "title": article.get("title", ""),
                        "source": article.get("source", ""),
                        "link": article.get("link", ""),
                        "snippet": article.get("snippet", ""),
                        "date": article.get("date", ""),
                        "position": article.get("position", 0)
                    })
            
            # Also check organic results for additional news articles
            if "organic_results" in search_result:
                for result in search_result["organic_results"][:5]:
                    if self._is_news_source(result.get("link", "")):
                        articles.append({
                            "title": result.get("title", ""),
                            "source": result.get("displayed_link", ""),
                            "link": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "date": "Recent",
                            "position": result.get("position", 0)
                        })
            
            if not articles:
                return f"No recent news articles found for query: '{query}'"
            
            # Format results for agent consumption
            result_text = f"Found {len(articles)} recent news articles for '{query}':\n\n"
            
            for i, article in enumerate(articles, 1):
                result_text += f"{i}. **{article['title']}**\n"
                result_text += f"   Source: {article['source']}\n"
                if article['date']:
                    result_text += f"   Date: {article['date']}\n"
                if article['snippet']:
                    result_text += f"   Summary: {article['snippet']}\n"
                result_text += f"   URL: {article['link']}\n\n"
            
            result_text += f"\nSearch timeframe: {self._search_timeframe['start']} to {self._search_timeframe['end']}\n"
            result_text += f"Total articles analyzed: {len(articles)}"
            
            return result_text
            
        except Exception as e:
            return f"Error searching Google News: {str(e)}. Using simulated results."
    
    def _is_news_source(self, url: str) -> bool:
        """Check if a URL is from a credible news source"""
        news_domains = [
            "cnn.com", "bbc.com", "reuters.com", "ap.org", "npr.org",
            "nytimes.com", "washingtonpost.com", "wsj.com", "bloomberg.com",
            "techcrunch.com", "theverge.com", "wired.com", "arstechnica.com",
            "forbes.com", "fortune.com", "businessinsider.com", "cnbc.com",
            "guardian.com", "independent.co.uk", "ft.com", "economist.com",
            "politico.com", "axios.com", "thehill.com", "usatoday.com",
            "abcnews.go.com", "cbsnews.com", "nbcnews.com", "foxnews.com"
        ]
        return any(domain in url.lower() for domain in news_domains)
    
    def _simulate_search(self, query: str) -> str:
        """Simulate Google News search when SERP API is not available"""
        
        simulated_articles = [
            {
                "title": f"Recent developments in {query} show mixed signals",
                "source": "Reuters",
                "snippet": f"Latest analysis suggests that {query} continues to evolve with new factors emerging in the market.",
                "date": "2 days ago"
            },
            {
                "title": f"Expert analysis: What {query} means for the future",
                "source": "Bloomberg",
                "snippet": f"Industry experts weigh in on the implications of {query} and its potential impact.",
                "date": "1 day ago"
            },
            {
                "title": f"Market responds to {query} with cautious optimism",
                "source": "Financial Times",
                "snippet": f"Financial markets show measured reaction to recent {query} developments.",
                "date": "3 hours ago"
            }
        ]
        
        result_text = f"Found {len(simulated_articles)} simulated news articles for '{query}':\n\n"
        
        for i, article in enumerate(simulated_articles, 1):
            result_text += f"{i}. **{article['title']}**\n"
            result_text += f"   Source: {article['source']}\n"
            result_text += f"   Date: {article['date']}\n"
            result_text += f"   Summary: {article['snippet']}\n\n"
        
        result_text += "\n⚠️ NOTE: These are simulated results. For real news search, configure SERP API key."
        
        return result_text


class EnhancedGoogleNewsTool(GoogleNewsTool):
    """Enhanced version with multiple search strategies"""
    
    name: str = "Enhanced Google News Search"
    description: str = """
    Advanced Google News search tool with multiple search strategies. Use this for comprehensive research:
    - Direct topic search with various angles
    - Historical precedent research
    - Expert opinion gathering
    - Contrarian viewpoint discovery
    - Market sentiment analysis
    
    Provide a query and optional search_type (current, expert_opinions, historical, contrarian).
    """
    args_schema: type = GoogleNewsInput
    
    def _run(self, query: str, search_type: str = "current") -> str:
        """Execute enhanced Google News search with strategy-based queries"""
        
        try:
            # Generate strategic queries based on search type
            if search_type == 'expert_opinions':
                queries = [
                    f"{query} expert predictions",
                    f"{query} analyst forecast",
                    f"{query} professional outlook",
                    f"experts say {query}"
                ]
            elif search_type == 'historical':
                queries = [
                    f"{query} historical precedents",
                    f"{query} past examples",
                    f"history of {query}",
                    f"{query} similar cases"
                ]
            elif search_type == 'contrarian':
                queries = [
                    f"{query} skeptical view",
                    f"{query} criticism",
                    f"why {query} unlikely",
                    f"{query} opposing opinion"
                ]
            else:  # current
                queries = [
                    query,
                    f"{query} latest news",
                    f"{query} recent developments",
                    f"{query} current status"
                ]
            
            all_results = []
            
            # Execute multiple searches
            for search_query in queries:
                result = super()._run(search_query)
                if "No recent news articles found" not in result:
                    all_results.append(f"=== Results for '{search_query}' ===\n{result}\n")
            
            if not all_results:
                return f"No news articles found for {search_type} search about: {query}"
            
            combined_results = f"Comprehensive {search_type} news search for '{query}':\n\n"
            combined_results += "\n".join(all_results)
            
            return combined_results
            
        except Exception as e:
            # Fallback to basic search
            return super()._run(query)
