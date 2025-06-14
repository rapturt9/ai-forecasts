"""
Google News Search Tool for AI Forecasting
Provides efficient Google News search capabilities via SERP API
Optimized to conserve API calls while maximizing information gathering
Includes intelligent caching to minimize redundant API calls
"""

import os
import json
import hashlib
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class GoogleNewsInput(BaseModel):
    """Input model for Google News search"""
    query: str = Field(..., description="Search query for Google News")
    search_type: Optional[str] = Field("focused", description="Type of search: focused, comprehensive, expert_opinions, historical, contrarian")
    priority: Optional[str] = Field("high", description="Priority level: high, medium, low - affects API usage")
    cutoff_date: Optional[str] = Field(None, description="ISO date string for benchmark cutoff (YYYY-MM-DD). Articles must be at least 1 day before this date.")


class CachedGoogleNewsTool:
    """
    Cached Google News search tool with intelligent caching to minimize API calls
    Caches search results by query signature and reuses data across agents
    """
    
    name: str = "Google News Search"
    description: str = """
    Search Google News efficiently with intelligent caching to minimize API calls.
    Automatically caches results by query parameters and reuses data when possible.
    
    Features:
    - Query-based caching with content deduplication
    - Cross-agent result sharing within session
    - Automatic cache invalidation for time-sensitive queries
    - Strategic API usage with fallback to similar queries
    
    Use priority='high' for critical forecasting questions, 'medium' for supporting research,
    'low' for background information. Results are used when available.
    """
    args_schema: type = GoogleNewsInput
    
    def __init__(self, serp_api_key: str = None, search_timeframe: Dict[str, str] = None, cache_dir: str = None):
        # Store configuration in internal attributes
        self._serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        self._search_timeframe = search_timeframe or {
            "start": "06/01/2024",  # From June 2024 to freeze date
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        
        # Setup caching
        self._cache_dir = Path(cache_dir or "cache/google_news")
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._session_cache = {}  # In-memory cache for current session
        self._cache_ttl_hours = 6  # Cache validity in hours
        
        self._setup_serp_client()
        self._search_count = 0  # Track API usage
        self._cache_hits = 0  # Track cache efficiency
        self._max_searches_per_session = 50  # Increased limit for actual research
        self._benchmark_cutoff_date = None  # For benchmark constraints
        
        print(f"🗄️ Google News cache initialized at: {self._cache_dir}")
    
    def set_benchmark_cutoff_date(self, cutoff_date: str):
        """Set benchmark cutoff date for all subsequent searches"""
        self._benchmark_cutoff_date = cutoff_date
        print(f"🛡️ Benchmark cutoff date set: {cutoff_date} (searches will be limited to 1 day before)")
    
    def _get_effective_timeframe(self, cutoff_date: str = None) -> Dict[str, str]:
        """Get effective search timeframe with benchmark constraints"""
        if cutoff_date:
            try:
                # Parse cutoff date and subtract 1 day to prevent answer leakage
                cutoff_dt = datetime.fromisoformat(cutoff_date)
                # Subtract 1 day to ensure articles are at least 1 day before cutoff
                safe_end_dt = cutoff_dt - timedelta(days=1)
                safe_end_str = safe_end_dt.strftime("%m/%d/%Y")
                
                return {
                    "start": self._search_timeframe["start"],
                    "end": safe_end_str,
                    "original_cutoff": cutoff_date,
                    "benchmark_safe": True
                }
            except Exception as e:
                print(f"⚠️ Error parsing cutoff date '{cutoff_date}': {e}, using default timeframe")
        
        # Default to original timeframe
        return {
            "start": self._search_timeframe["start"],
            "end": self._search_timeframe["end"],
            "benchmark_safe": False
        }
    
    def _setup_serp_client(self):
        """Setup SERP API client"""
        try:
            from serpapi import GoogleSearch
            if self._serp_api_key:
                self._serp_client = GoogleSearch
                self._client_available = True
                print("✅ SERP API client ready for Google News search")
            else:
                self._serp_client = None
                self._client_available = False
                print("⚠️ SERP API key not found, Google News search will be simulated")
        except ImportError:
            self._serp_client = None
            self._client_available = False
            print("⚠️ google-search-results not installed, Google News search will be simulated")
    
    def _run(self, query: str, search_type: str = "focused", priority: str = "high", cutoff_date: str = None) -> str:
        """Execute strategic Google News search with intelligent caching and benchmark date constraints"""
        
        # Use provided cutoff_date or stored benchmark cutoff date
        effective_cutoff = cutoff_date or self._benchmark_cutoff_date
        
        # Apply benchmark constraint: ensure articles are at least 1 day before cutoff date
        effective_timeframe = self._get_effective_timeframe(effective_cutoff)
        
        # Generate cache key for this search (include timeframe for uniqueness)
        cache_key = self._generate_cache_key(query, search_type, priority, effective_timeframe)
        
        # Check session cache first (fastest)
        if cache_key in self._session_cache:
            self._cache_hits += 1
            print(f"🎯 Session cache hit for '{query}' (Cache hits: {self._cache_hits})")
            return self._session_cache[cache_key]["result"]
        
        # Check persistent cache
        cached_result = self._load_from_cache(cache_key)
        if cached_result:
            self._cache_hits += 1
            self._session_cache[cache_key] = cached_result
            print(f"💾 Disk cache hit for '{query}' (Cache hits: {self._cache_hits})")
            return cached_result["result"]
        
        # Check for similar cached queries to avoid redundant searches
        similar_result = self._find_similar_cached_query(query, search_type)
        if similar_result:
            self._cache_hits += 1
            print(f"🔄 Using similar cached query for '{query}' (Cache hits: {self._cache_hits})")
            return similar_result
        
        # No cache hit - perform new search if API available and under limits
        if not self._client_available:
            return f"❌ SERP API not available for Google News search: '{query}'. Configure SERP_API_KEY environment variable."
        
        # Check API usage limits - use cached alternatives instead of simulation
        if self._search_count >= self._max_searches_per_session:
            print(f"⚠️ Reached API limit ({self._max_searches_per_session} searches), trying cache alternatives")
            fallback_result = self._get_cache_fallback(query, search_type)
            if fallback_result:
                return fallback_result
            return f"❌ API limit reached and no cached alternatives available for '{query}'. Consider increasing search limit or using more specific queries."
        
        try:
            # Generate strategic search queries based on type and priority
            search_queries = self._generate_strategic_queries(query, search_type, priority)
            
            all_articles = []
            
            for search_query in search_queries:
                if self._search_count >= self._max_searches_per_session:
                    break
                
                # Check if we have this specific query cached
                sub_cache_key = self._generate_cache_key(search_query, search_type, priority, effective_timeframe)
                if sub_cache_key in self._session_cache:
                    cached_articles = self._session_cache[sub_cache_key].get("articles", [])
                    all_articles.extend(cached_articles)
                    print(f"🎯 Using cached sub-query: '{search_query}'")
                    continue
                
                articles = self._execute_single_search(search_query, effective_timeframe)
                all_articles.extend(articles)
                self._search_count += 1
                
                # Cache individual query results
                self._cache_query_result(sub_cache_key, search_query, articles)
                
                print(f"🔍 Search {self._search_count}/{self._max_searches_per_session}: '{search_query}' - Found {len(articles)} articles")
            
            # Remove duplicates and sort by relevance
            unique_articles = self._deduplicate_articles(all_articles)
            
            if not unique_articles:
                result = f"No recent news articles found for {search_type} search about: '{query}'"
            else:
                # Format results
                result = self._format_search_results(query, search_type, unique_articles, effective_timeframe)
            
            # Cache the final result
            self._save_to_cache(cache_key, query, search_type, result, unique_articles, effective_timeframe)
            
            return result
            
        except Exception as e:
            print(f"❌ Error in Google News search: {str(e)}")
            # Try cache fallback before giving up
            fallback_result = self._get_cache_fallback(query, search_type)
            if fallback_result:
                return fallback_result
            return f"❌ Google News search failed for '{query}': {str(e)}. No cached alternatives available."
    
    def _generate_cache_key(self, query: str, search_type: str, priority: str, effective_timeframe: Dict[str, str] = None) -> str:
        """Generate a cache key for the query parameters including timeframe"""
        # Use effective timeframe if provided, otherwise use default
        timeframe = effective_timeframe or self._search_timeframe
        key_data = f"{query.lower().strip()}|{search_type}|{priority}|{timeframe['start']}|{timeframe['end']}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load cached result from disk if still valid"""
        cache_file = self._cache_dir / f"{cache_key}.pkl"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Check if cache is still valid (TTL check)
            cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2020-01-01'))
            if datetime.now() - cache_time > timedelta(hours=self._cache_ttl_hours):
                print(f"🕒 Cache expired for key {cache_key[:8]}...")
                cache_file.unlink()  # Remove expired cache
                return None
            
            return cached_data
            
        except Exception as e:
            print(f"⚠️ Error loading cache {cache_key[:8]}...: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, query: str, search_type: str, result: str, articles: List[Dict[str, Any]], effective_timeframe: Dict[str, str] = None):
        """Save search result to both session and disk cache"""
        timeframe = effective_timeframe or self._search_timeframe
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'search_type': search_type,
            'result': result,
            'articles': articles,
            'search_count': self._search_count,
            'timeframe_used': timeframe,
            'benchmark_safe': timeframe.get('benchmark_safe', False)
        }
        
        # Save to session cache
        self._session_cache[cache_key] = cache_data
        
        # Save to disk cache
        try:
            cache_file = self._cache_dir / f"{cache_key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"⚠️ Error saving cache: {e}")
    
    def _cache_query_result(self, cache_key: str, query: str, articles: List[Dict[str, Any]]):
        """Cache individual query results for reuse"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'articles': articles,
            'search_type': 'sub_query'
        }
        self._session_cache[cache_key] = cache_data
    
    def _find_similar_cached_query(self, query: str, search_type: str) -> Optional[str]:
        """Find similar cached queries to avoid redundant searches"""
        query_words = set(query.lower().split())
        
        # Check session cache for similar queries
        for cached_key, cached_data in self._session_cache.items():
            if cached_data.get('search_type') == search_type:
                cached_query = cached_data.get('query', '')
                cached_words = set(cached_query.lower().split())
                
                # Calculate word overlap
                overlap = len(query_words.intersection(cached_words))
                total_words = len(query_words.union(cached_words))
                similarity = overlap / total_words if total_words > 0 else 0
                
                # If queries are similar enough (>60% word overlap), reuse results
                if similarity > 0.6:
                    print(f"🔄 Found similar cached query: '{cached_query}' (similarity: {similarity:.2f})")
                    return cached_data['result']
        
        # Check disk cache for similar queries
        try:
            for cache_file in self._cache_dir.glob("*.pkl"):
                try:
                    with open(cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    # Check TTL
                    cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2020-01-01'))
                    if datetime.now() - cache_time > timedelta(hours=self._cache_ttl_hours):
                        continue
                    
                    if cached_data.get('search_type') == search_type:
                        cached_query = cached_data.get('query', '')
                        cached_words = set(cached_query.lower().split())
                        
                        overlap = len(query_words.intersection(cached_words))
                        total_words = len(query_words.union(cached_words))
                        similarity = overlap / total_words if total_words > 0 else 0
                        
                        if similarity > 0.6:
                            print(f"💾 Found similar disk cached query: '{cached_query}' (similarity: {similarity:.2f})")
                            # Load into session cache for faster future access
                            cache_key = self._generate_cache_key(query, search_type, "medium")
                            self._session_cache[cache_key] = cached_data
                            return cached_data['result']
                            
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error searching disk cache for similar queries: {e}")
        
        return None
    
    def _get_cache_fallback(self, query: str, search_type: str) -> Optional[str]:
        """Get best available cached result when API limits are reached"""
        # Try to find any cached result related to this query
        query_words = set(query.lower().split())
        
        best_match = None
        best_similarity = 0
        
        # Check all cached results for best match
        for cached_key, cached_data in self._session_cache.items():
            cached_query = cached_data.get('query', '')
            cached_words = set(cached_query.lower().split())
            
            overlap = len(query_words.intersection(cached_words))
            total_words = len(query_words.union(cached_words))
            similarity = overlap / total_words if total_words > 0 else 0
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = cached_data
        
        if best_match and best_similarity > 0.3:  # Lower threshold for fallback
            print(f"🆘 Using fallback cached result (similarity: {best_similarity:.2f})")
            fallback_result = best_match['result']
            fallback_result += f"\n\n⚠️ NOTE: This is a cached result from a similar query due to API limits."
            return fallback_result
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self._search_count + self._cache_hits
        cache_hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            "cache_hits": self._cache_hits,
            "api_calls": self._search_count,
            "total_requests": total_requests,
            "cache_hit_rate": cache_hit_rate,
            "session_cache_size": len(self._session_cache),
            "disk_cache_files": len(list(self._cache_dir.glob("*.pkl")))
        }
    
    def clear_expired_cache(self):
        """Clear expired cache files from disk"""
        try:
            expired_count = 0
            for cache_file in self._cache_dir.glob("*.pkl"):
                try:
                    with open(cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2020-01-01'))
                    if datetime.now() - cache_time > timedelta(hours=self._cache_ttl_hours):
                        cache_file.unlink()
                        expired_count += 1
                        
                except Exception:
                    cache_file.unlink()  # Remove corrupted cache files
                    expired_count += 1
            
            if expired_count > 0:
                print(f"🧹 Cleared {expired_count} expired cache files")
                
        except Exception as e:
            print(f"⚠️ Error clearing expired cache: {e}")
    
    def clear_all_cache(self):
        """Clear all cache (session and disk)"""
        self._session_cache.clear()
        try:
            for cache_file in self._cache_dir.glob("*.pkl"):
                cache_file.unlink()
            print("🧹 Cleared all cache files")
        except Exception as e:
            print(f"⚠️ Error clearing cache: {e}")
    
    def _generate_strategic_queries(self, query: str, search_type: str, priority: str) -> List[str]:
        """Generate strategic search queries to maximize information with minimal API calls"""
        
        queries = []
        
        if search_type == "focused":
            # Single, well-crafted query for high efficiency
            if priority == "high":
                queries = [query, f"{query} latest developments"]
            elif priority == "medium":
                queries = [query]
            else:  # low priority
                queries = [f"{query} news"]
        
        elif search_type == "comprehensive":
            # Multiple angles for critical forecasting questions
            if priority == "high":
                queries = [
                    query,
                    f"{query} latest news",
                    f"{query} expert analysis",
                    f"{query} market impact"
                ]
            elif priority == "medium":
                queries = [query, f"{query} latest developments"]
            else:
                queries = [query]
        
        elif search_type == "expert_opinions":
            # Focus on expert analysis and predictions
            if priority == "high":
                queries = [
                    f"{query} expert predictions",
                    f"{query} analyst forecast",
                    f"{query} professional analysis"
                ]
            else:
                queries = [f"{query} expert analysis"]
        
        elif search_type == "historical":
            # Historical context and precedents
            if priority == "high":
                queries = [
                    f"{query} historical data",
                    f"{query} past trends",
                    f"{query} precedents"
                ]
            else:
                queries = [f"{query} historical analysis"]
        
        elif search_type == "contrarian":
            # Alternative viewpoints and criticism
            if priority == "high":
                queries = [
                    f"{query} criticism",
                    f"{query} skeptical analysis",
                    f"why {query} unlikely"
                ]
            else:
                queries = [f"{query} alternative view"]
        
        return queries[:4]  # Maximum 4 queries even for comprehensive searches
    
    def _execute_single_search(self, query: str, effective_timeframe: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Execute a single SERP API search with timeframe constraints"""
        
        try:
            # Use effective timeframe if provided, otherwise use default
            timeframe = effective_timeframe or self._search_timeframe
            
            # Configure search parameters for Google News
            search_params = {
                "api_key": self._serp_api_key,
                "engine": "google",
                "q": query,
                "tbm": "nws",  # News search
                "tbs": f"cdr:1,cd_min:{timeframe['start']},cd_max:{timeframe['end']}",
                "num": 20,  # More results per search to maximize efficiency
                "hl": "en",
                "gl": "us"
            }
            
            # Log benchmark constraint if applied
            if effective_timeframe and effective_timeframe.get("benchmark_safe"):
                print(f"🛡️ Benchmark constraint applied: searching until {timeframe['end']} (1 day before cutoff {effective_timeframe.get('original_cutoff', 'unknown')})")
            
            # Perform the search
            search = self._serp_client(search_params)
            search_result = search.get_dict()
            
            articles = []
            
            # Process news results
            if "news_results" in search_result:
                for article in search_result["news_results"]:
                    articles.append({
                        "title": article.get("title", ""),
                        "source": article.get("source", ""),
                        "link": article.get("link", ""),
                        "snippet": article.get("snippet", ""),
                        "date": article.get("date", ""),
                        "position": article.get("position", 0),
                        "query": query  # Track which query found this
                    })
            
            # Also check organic results for additional news
            if "organic_results" in search_result:
                for result in search_result["organic_results"][:5]:
                    if self._is_news_source(result.get("link", "")):
                        articles.append({
                            "title": result.get("title", ""),
                            "source": result.get("displayed_link", ""),
                            "link": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "date": "Recent",
                            "position": result.get("position", 0),
                            "query": query
                        })
            
            return articles
            
        except Exception as e:
            print(f"❌ Search failed for '{query}': {str(e)}")
            return []
    
    def _deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles and sort by relevance"""
        
        seen_urls = set()
        unique_articles = []
        
        # Sort by position (lower is better) and source credibility
        articles.sort(key=lambda x: (x.get("position", 999), 0 if self._is_credible_source(x.get("source", "")) else 1))
        
        for article in articles:
            url = article.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles[:15]  # Limit to top 15 most relevant articles
    
    def _is_news_source(self, url: str) -> bool:
        """Check if a URL is from a credible news source"""
        news_domains = [
            "cnn.com", "bbc.com", "reuters.com", "ap.org", "npr.org",
            "nytimes.com", "washingtonpost.com", "wsj.com", "bloomberg.com",
            "techcrunch.com", "theverge.com", "wired.com", "arstechnica.com",
            "forbes.com", "fortune.com", "businessinsider.com", "cnbc.com",
            "guardian.com", "independent.co.uk", "ft.com", "economist.com",
            "politico.com", "axios.com", "thehill.com", "usatoday.com",
            "abcnews.go.com", "cbsnews.com", "nbcnews.com", "foxnews.com",
            "sciencemag.org", "nature.com", "newscientist.com", "spectrum.ieee.org"
        ]
        return any(domain in url.lower() for domain in news_domains)
    
    def _is_credible_source(self, source: str) -> bool:
        """Check if a source is considered highly credible"""
        credible_sources = [
            "Reuters", "Associated Press", "BBC", "NPR", "Wall Street Journal",
            "Financial Times", "Bloomberg", "The Economist", "Nature", "Science",
            "IEEE Spectrum", "New York Times", "Washington Post", "CNN", "CNBC"
        ]
        return any(credible in source for credible in credible_sources)
    
    def _format_search_results(self, query: str, search_type: str, articles: List[Dict[str, Any]], effective_timeframe: Dict[str, str] = None) -> str:
        """Format search results for agent consumption with cache info"""
        
        cache_stats = self.get_cache_stats()
        timeframe = effective_timeframe or self._search_timeframe
        
        result_text = f"Found {len(articles)} articles for {search_type} search '{query}':\n\n"
        
        for i, article in enumerate(articles, 1):
            result_text += f"{i}. **{article['title']}**\n"
            result_text += f"   Source: {article['source']}\n"
            if article['date']:
                result_text += f"   Date: {article['date']}\n"
            if article['snippet']:
                result_text += f"   Summary: {article['snippet']}\n"
            result_text += f"   URL: {article['link']}\n"
            if article.get('query') != query:
                result_text += f"   Found via: {article.get('query')}\n"
            result_text += "\n"
        
        result_text += f"\nSearch period: {timeframe['start']} to {timeframe['end']}\n"
        
        # Add benchmark constraint information
        if effective_timeframe and effective_timeframe.get("benchmark_safe"):
            result_text += f"🛡️ BENCHMARK CONSTRAINT APPLIED: Search limited to articles at least 1 day before cutoff date ({effective_timeframe.get('original_cutoff', 'unknown')})\n"
        
        result_text += f"API searches used: {self._search_count}/{self._max_searches_per_session}\n"
        result_text += f"Cache hits: {cache_stats['cache_hits']} | Hit rate: {cache_stats['cache_hit_rate']:.1%}\n"
        result_text += f"Search strategy: {search_type}"
        
        return result_text
    
    def _simulate_search(self, query: str, search_type: str) -> str:
        """Simulate search when API is not available"""
        
        simulated_articles = [
            {
                "title": f"Recent {search_type} analysis of {query}",
                "source": "Reuters",
                "snippet": f"Latest {search_type} research on {query} reveals key insights for forecasting.",
                "date": "2 days ago"
            },
            {
                "title": f"Expert perspective on {query} developments",
                "source": "Bloomberg",
                "snippet": f"Industry experts analyze the implications of {query} for future predictions.",
                "date": "1 day ago"
            },
            {
                "title": f"Market signals point to {query} trends",
                "source": "Financial Times",
                "snippet": f"Financial indicators suggest {query} patterns continue to evolve.",
                "date": "6 hours ago"
            }
        ]
        
        result_text = f"Simulated {search_type} search for '{query}' found {len(simulated_articles)} articles:\n\n"
        
        for i, article in enumerate(simulated_articles, 1):
            result_text += f"{i}. **{article['title']}**\n"
            result_text += f"   Source: {article['source']}\n"
            result_text += f"   Date: {article['date']}\n"
            result_text += f"   Summary: {article['snippet']}\n\n"
        
        result_text += "\n⚠️ NOTE: These are simulated results. Configure SERP API key for real data."
        
        return result_text


# Backwards compatibility aliases
EfficientGoogleNewsTool = CachedGoogleNewsTool
GoogleNewsTool = CachedGoogleNewsTool
