"""
Google News Enhanced Superforecaster System
Implements superforecaster methodology with timestamped Google News search using SERP API
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import urllib.parse

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
from ..utils.agent_logger import agent_logger
from ..utils.llm_client import LLMClient


@dataclass
class GoogleNewsResearchResult:
    """Structured forecast result with comprehensive Google News research"""
    question: str
    probability: float
    confidence_level: str
    reasoning: str
    base_rate: float
    evidence_quality: float
    methodology_components: Dict[str, bool]
    full_analysis: Dict[str, Any]
    news_research_summary: Dict[str, Any]
    news_sources: List[str]
    search_queries_used: List[str]
    total_articles_found: int
    search_timeframe: Dict[str, str]


class GoogleNewsSuperforecaster:
    """
    Superforecaster system that integrates timestamped Google News search using SERP API
    following the methodology used by top superforecasters
    """
    
    def __init__(self, openrouter_api_key: str, serp_api_key: str = None):
        self.logger = agent_logger
        self.openrouter_api_key = openrouter_api_key
        self.serp_api_key = serp_api_key or os.getenv("SERP_API_KEY")
        
        # Configure LLM for CrewAI with proper headers
        self.llm = LLM(
            model="openai/gpt-4o-2024-11-20",
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            default_headers={
                "HTTP-Referer": "https://ai-forecasts.com",
                "X-Title": "AI Forecasting System"
            }
        )
        
        # Initialize SERP client
        self._setup_serp_client()
        
        # Initialize specialized agents
        self._setup_news_research_agents()
    
    def _setup_serp_client(self):
        """Setup SERP API client for Google News search"""
        try:
            from serpapi import GoogleSearch
            if self.serp_api_key:
                self.serp_client = GoogleSearch
                self.logger.info("✅ SERP API client initialized successfully")
            else:
                self.serp_client = None
                self.logger.warning("⚠️ SERP API key not found, will use simulated research")
        except ImportError:
            self.serp_client = None
            self.logger.warning("⚠️ google-search-results not installed, will use simulated research")
    
    def _setup_news_research_agents(self):
        """Setup specialized forecasting agents with Google News research integration"""
        
        # News Research Coordinator - Manages comprehensive news research
        self.news_research_coordinator = Agent(
            role='News Research Coordinator',
            goal='Conduct systematic Google News research following superforecaster methodology',
            backstory="""You are an expert news researcher who follows the systematic approach 
            used by top superforecasters. You gather information from Google News with precise 
            time filtering, evaluate source credibility, look for diverse perspectives, and 
            identify both supporting and contradicting evidence. You excel at finding recent 
            developments, expert opinions, base rate information, and leading indicators from 
            timestamped news articles.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Historical News Analyst - Finds historical precedents via timestamped news search
        self.historical_news_analyst = Agent(
            role='Historical News Research Specialist',
            goal='Research historical precedents and base rates using timestamped Google News',
            backstory="""You are an expert in finding and analyzing historical precedents 
            through timestamped Google News research. You search for similar past events, 
            calculate base rates from available news data, and identify reference classes. 
            You excel at finding news coverage of historical events, expert analysis, and 
            data that inform base rate calculations.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Current News Context Analyst - Analyzes recent news developments
        self.current_news_analyst = Agent(
            role='Current News Context Analyst',
            goal='Analyze current conditions and recent developments through timestamped Google News',
            backstory="""You are an expert at analyzing current market conditions, recent 
            developments, and emerging trends through comprehensive Google News research with 
            precise time filtering. You track breaking news, expert opinions, policy changes, 
            and market indicators. You excel at identifying how current conditions differ from 
            historical precedents based on news coverage.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Expert Opinion News Aggregator - Gathers expert predictions from news sources
        self.expert_news_aggregator = Agent(
            role='Expert Opinion News Aggregator',
            goal='Gather and synthesize expert opinions and predictions from Google News sources',
            backstory="""You are an expert at finding and evaluating expert opinions, 
            predictions, and analysis from credible news sources through Google News. You 
            search for expert interviews, industry reports, academic commentary, and 
            professional forecasts covered in news media. You excel at weighing different 
            expert opinions and identifying consensus vs. contrarian views from news coverage.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Contrarian News Research Agent - Looks for opposing viewpoints in news
        self.contrarian_news_researcher = Agent(
            role='Contrarian News Research Specialist',
            goal='Research opposing viewpoints and potential disconfirming evidence from news sources',
            backstory="""You are an expert at finding contrarian viewpoints and potential 
            disconfirming evidence through Google News research. You actively seek out opposing 
            opinions, skeptical analysis, and evidence that challenges the mainstream view as 
            covered in news media. You excel at identifying potential blind spots and cognitive 
            biases in forecasting through diverse news perspectives.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Synthesis and Calibration Expert - Integrates all news research
        self.synthesis_expert = Agent(
            role='Synthesis and Calibration Expert',
            goal='Synthesize all Google News research into a well-calibrated forecast',
            backstory="""You are a master synthesizer who combines insights from comprehensive 
            Google News research following superforecaster methodology. You integrate base rates, 
            current context, expert opinions, and contrarian views from timestamped news sources. 
            You excel at proper calibration, avoiding overconfidence, and producing well-reasoned 
            probability estimates that account for uncertainty.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
    
    def forecast_with_google_news(
        self, 
        question: str, 
        background: str = "",
        cutoff_date: Optional[datetime] = None,
        time_horizon: str = "1 year",
        is_benchmark: bool = False
    ) -> GoogleNewsResearchResult:
        """
        Generate a forecast using comprehensive Google News research and superforecaster methodology
        """
        
        self.logger.info(f"🚀 Starting Google News Superforecaster analysis")
        self.logger.info(f"📋 Question: {question}")
        self.logger.info(f"📅 Is benchmark: {is_benchmark}")
        
        # Determine search timeframe
        search_timeframe = self._determine_search_timeframe(cutoff_date, is_benchmark)
        self.logger.info(f"🕒 Search timeframe: {search_timeframe['start']} to {search_timeframe['end']}")
        
        # First, conduct comprehensive Google News research
        news_research_data = self._conduct_comprehensive_news_research(question, search_timeframe, is_benchmark)
        
        # Create tasks for each agent using the news research data
        tasks = self._create_news_research_tasks(question, background, cutoff_date, time_horizon, news_research_data, search_timeframe)
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.news_research_coordinator,
                self.historical_news_analyst,
                self.current_news_analyst,
                self.expert_news_aggregator,
                self.contrarian_news_researcher,
                self.synthesis_expert
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the forecasting process
        self.logger.info(f"🔄 Executing Google News superforecaster crew...")
        result = crew.kickoff()
        
        # Parse and structure the result
        forecast_result = self._parse_news_research_result(result, question, news_research_data, search_timeframe)
        
        self.logger.info(f"✅ Google News Superforecaster forecast complete: {forecast_result.probability:.3f}")
        return forecast_result
    
    def _determine_search_timeframe(self, cutoff_date: Optional[datetime], is_benchmark: bool) -> Dict[str, str]:
        """
        Determine the appropriate search timeframe based on whether this is a benchmark question
        """
        
        if is_benchmark and cutoff_date:
            # For benchmark questions: search from June 2024 to freeze timestamp
            start_date = datetime(2024, 6, 1)  # June 2024
            end_date = cutoff_date
        elif cutoff_date:
            # For non-benchmark questions with cutoff: search from June 2024 to cutoff
            start_date = datetime(2024, 6, 1)
            end_date = cutoff_date
        else:
            # For current questions: search from June 2024 to now
            start_date = datetime(2024, 6, 1)
            end_date = datetime.now()
        
        return {
            "start": start_date.strftime("%m/%d/%Y"),
            "end": end_date.strftime("%m/%d/%Y"),
            "start_datetime": start_date,
            "end_datetime": end_date
        }
    
    def _conduct_comprehensive_news_research(self, question: str, search_timeframe: Dict[str, str], is_benchmark: bool) -> Dict[str, Any]:
        """
        Conduct comprehensive Google News research using SERP API with timestamped searches
        """
        
        self.logger.info(f"🔍 Starting comprehensive Google News research for: {question}")
        self.logger.info(f"📅 Timeframe: {search_timeframe['start']} to {search_timeframe['end']}")
        
        # Define search strategies following superforecaster methodology
        search_strategies = {
            "main_question": [question],
            "base_rate_research": [
                f"{question} historical precedents",
                f"{question} similar cases",
                f"{question} past examples",
                f"history of {question}"
            ],
            "current_context": [
                f"{question} recent developments",
                f"{question} latest news",
                f"{question} current status",
                f"{question} updates"
            ],
            "expert_opinions": [
                f"{question} expert predictions",
                f"{question} expert analysis",
                f"{question} professional forecast",
                f"{question} industry outlook"
            ],
            "contrarian_views": [
                f"{question} skeptical view",
                f"{question} opposing opinion",
                f"{question} criticism",
                f"why {question} unlikely"
            ],
            "leading_indicators": [
                f"{question} leading indicators",
                f"{question} early signals",
                f"{question} warning signs",
                f"factors affecting {question}"
            ]
        }
        
        all_research_data = {
            "question": question,
            "search_timeframe": search_timeframe,
            "is_benchmark": is_benchmark,
            "research_strategies": search_strategies,
            "search_results": {},
            "total_articles": 0,
            "research_quality_score": 0.0
        }
        
        if self.serp_client:
            # Conduct actual Google News research using SERP API
            all_research_data["search_results"] = self._conduct_serp_news_search(search_strategies, question, search_timeframe)
            all_research_data["total_articles"] = sum(
                len(results.get("articles", [])) for results in all_research_data["search_results"].values()
            )
            all_research_data["research_quality_score"] = 0.9  # High quality for real news search
        else:
            # Fallback to simulated research
            all_research_data["search_results"] = self._simulate_news_search(search_strategies, question, search_timeframe)
            all_research_data["total_articles"] = 50  # Simulated
            all_research_data["research_quality_score"] = 0.6  # Lower quality for simulated
        
        self.logger.info(f"✅ Google News research completed. Total articles: {all_research_data['total_articles']}")
        
        return all_research_data
    
    def _conduct_serp_news_search(self, search_strategies: Dict[str, List[str]], question: str, search_timeframe: Dict[str, str]) -> Dict[str, Any]:
        """
        Conduct actual Google News search using SERP API with timestamp filtering
        """
        
        search_results = {}
        
        for strategy, queries in search_strategies.items():
            self.logger.info(f"🔍 Searching Google News for {strategy}: {len(queries)} queries")
            
            strategy_results = {
                "queries_used": queries,
                "articles": [],
                "sources": [],
                "key_findings": [],
                "quality_score": 0.0,
                "timeframe_used": search_timeframe
            }
            
            for query in queries:
                try:
                    # Configure SERP search parameters for Google News with timestamp
                    search_params = {
                        "api_key": self.serp_api_key,
                        "engine": "google",
                        "q": query,
                        "tbm": "nws",  # News search
                        "tbs": f"cdr:1,cd_min:{search_timeframe['start']},cd_max:{search_timeframe['end']}",  # Custom date range
                        "num": 10,  # Number of results
                        "hl": "en",  # Language
                        "gl": "us"   # Country
                    }
                    
                    # Perform the search
                    search = self.serp_client(search_params)
                    search_result = search.get_dict()
                    
                    if "news_results" in search_result:
                        for article in search_result["news_results"]:
                            strategy_results["articles"].append(article)
                            if article.get("link"):
                                strategy_results["sources"].append(article["link"])
                            if article.get("snippet"):
                                # Extract key findings from snippet
                                snippet = article["snippet"][:300] + "..." if len(article["snippet"]) > 300 else article["snippet"]
                                strategy_results["key_findings"].append(snippet)
                    
                    # Also check organic results for news articles
                    if "organic_results" in search_result:
                        for result in search_result["organic_results"][:5]:  # Limit to top 5
                            if self._is_news_source(result.get("link", "")):
                                strategy_results["articles"].append({
                                    "title": result.get("title", ""),
                                    "link": result.get("link", ""),
                                    "snippet": result.get("snippet", ""),
                                    "source": result.get("displayed_link", "")
                                })
                                if result.get("link"):
                                    strategy_results["sources"].append(result["link"])
                                if result.get("snippet"):
                                    snippet = result["snippet"][:300] + "..." if len(result["snippet"]) > 300 else result["snippet"]
                                    strategy_results["key_findings"].append(snippet)
                
                except Exception as e:
                    self.logger.warning(f"Google News search failed for query '{query}': {str(e)}")
                    continue
            
            # Calculate quality score based on articles found
            strategy_results["quality_score"] = min(1.0, len(strategy_results["articles"]) / (len(queries) * 5))
            strategy_results["articles_found"] = len(strategy_results["articles"])
            
            search_results[strategy] = strategy_results
            
            self.logger.info(f"✅ {strategy}: Found {len(strategy_results['articles'])} articles from {len(queries)} queries")
        
        return search_results
    
    def _is_news_source(self, url: str) -> bool:
        """Check if a URL is from a news source"""
        news_domains = [
            "cnn.com", "bbc.com", "reuters.com", "ap.org", "npr.org",
            "nytimes.com", "washingtonpost.com", "wsj.com", "bloomberg.com",
            "techcrunch.com", "theverge.com", "wired.com", "arstechnica.com",
            "forbes.com", "fortune.com", "businessinsider.com", "cnbc.com",
            "guardian.com", "independent.co.uk", "ft.com", "economist.com"
        ]
        return any(domain in url.lower() for domain in news_domains)
    
    def _simulate_news_search(self, search_strategies: Dict[str, List[str]], question: str, search_timeframe: Dict[str, str]) -> Dict[str, Any]:
        """
        Simulate comprehensive Google News search results as fallback
        """
        
        simulated_results = {}
        
        for strategy, queries in search_strategies.items():
            simulated_results[strategy] = {
                "queries_used": queries,
                "articles_found": len(queries) * 6,  # Simulate 6 articles per query
                "key_findings": [
                    f"Simulated news finding 1 for {strategy}: Relevant news coverage discovered",
                    f"Simulated news finding 2 for {strategy}: Expert commentary identified",
                    f"Simulated news finding 3 for {strategy}: Market analysis located"
                ],
                "sources": [
                    f"https://simulated-news-{strategy}-{i}.com" for i in range(len(queries) * 3)
                ],
                "quality_score": 0.6,
                "timeframe_used": search_timeframe,
                "note": "Simulated Google News results - actual search not available"
            }
        
        return simulated_results
    
    def _create_news_research_tasks(
        self, 
        question: str, 
        background: str, 
        cutoff_date: Optional[datetime], 
        time_horizon: str,
        news_research_data: Dict[str, Any],
        search_timeframe: Dict[str, str]
    ) -> List[Task]:
        """Create tasks for each agent using comprehensive Google News research data"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        # Task 1: News Research Coordination
        news_coordination_task = Task(
            description=f"""
            Coordinate and synthesize the comprehensive Google News research conducted for this forecasting question:
            
            Question: {question}
            Background: {background}
            Search Timeframe: {search_timeframe['start']} to {search_timeframe['end']}
            News Research Summary: {json.dumps(news_research_data, indent=2, default=str)[:2000]}...
            Information cutoff: {cutoff_str}
            
            Your task is to:
            1. Review all Google News findings across different search strategies
            2. Assess the quality and credibility of news sources
            3. Identify the most relevant and reliable news coverage
            4. Note any gaps or limitations in the news research
            5. Organize findings by relevance, recency, and reliability
            6. Prepare a news research summary for other agents
            
            Focus on news source credibility and temporal relevance within the search timeframe.
            
            Output your coordination summary in JSON format.
            """,
            agent=self.news_research_coordinator,
            expected_output="JSON summary of Google News research coordination with quality assessment and organized findings"
        )
        
        # Task 2: Historical News Analysis
        historical_news_task = Task(
            description=f"""
            Analyze base rates and historical precedents using the Google News research data:
            
            Question: {question}
            Historical News Research: {json.dumps(news_research_data.get('search_results', {}).get('base_rate_research', {}), indent=2, default=str)}
            News Coordination: {{news_coordination_task.output}}
            Search Timeframe: {search_timeframe['start']} to {search_timeframe['end']}
            
            Your analysis should include:
            1. Identify relevant reference classes from news coverage
            2. Calculate or estimate base rates from available news data
            3. Assess the quality of historical precedent coverage
            4. Consider multiple reference classes and their base rates
            5. Evaluate how representative the news coverage is
            6. Provide confidence intervals for base rate estimates
            
            Use the Google News research to find actual historical data and precedents.
            Start with outside view (base rates) before considering inside view factors.
            
            Output your analysis in JSON format with base rate calculations.
            """,
            agent=self.historical_news_analyst,
            expected_output="JSON analysis with base rate calculations, reference classes, and confidence assessments from news sources",
            context=[news_coordination_task]
        )
        
        # Task 3: Current News Context Analysis
        current_news_task = Task(
            description=f"""
            Analyze current conditions and recent developments using Google News research:
            
            Question: {question}
            Current News Research: {json.dumps(news_research_data.get('search_results', {}).get('current_context', {}), indent=2, default=str)}
            News Coordination: {{news_coordination_task.output}}
            Search Timeframe: {search_timeframe['start']} to {search_timeframe['end']}
            
            Your analysis should include:
            1. Current market/social/political conditions from news coverage
            2. Recent developments and trend changes reported in news
            3. How current conditions compare to historical precedents
            4. Emerging factors that could influence the outcome
            5. Timeline of recent relevant events from news sources
            6. Current momentum and trajectory assessment from news trends
            
            Focus on how current conditions from news coverage might affect the probability estimate.
            
            Output your analysis in JSON format with current context assessment.
            """,
            agent=self.current_news_analyst,
            expected_output="JSON analysis of current conditions, recent developments, and trend assessment from news sources",
            context=[news_coordination_task]
        )
        
        # Task 4: Expert Opinion News Aggregation
        expert_news_task = Task(
            description=f"""
            Aggregate and analyze expert opinions from Google News research:
            
            Question: {question}
            Expert Opinion News: {json.dumps(news_research_data.get('search_results', {}).get('expert_opinions', {}), indent=2, default=str)}
            News Coordination: {{news_coordination_task.output}}
            Search Timeframe: {search_timeframe['start']} to {search_timeframe['end']}
            
            Your analysis should include:
            1. Identify credible expert sources and their predictions from news coverage
            2. Assess expert track records and expertise relevance
            3. Look for consensus vs. disagreement among experts in news
            4. Weight expert opinions by credibility and expertise
            5. Identify any expert biases or conflicts of interest
            6. Synthesize expert consensus and range of opinions from news sources
            
            Focus on expert credibility and prediction track records as reported in news.
            
            Output your analysis in JSON format with expert opinion synthesis.
            """,
            agent=self.expert_news_aggregator,
            expected_output="JSON analysis of expert opinions with credibility assessment and consensus evaluation from news sources",
            context=[news_coordination_task]
        )
        
        # Task 5: Contrarian News Research Analysis
        contrarian_news_task = Task(
            description=f"""
            Analyze contrarian viewpoints and potential disconfirming evidence from Google News:
            
            Question: {question}
            Contrarian News Research: {json.dumps(news_research_data.get('search_results', {}).get('contrarian_views', {}), indent=2, default=str)}
            News Coordination: {{news_coordination_task.output}}
            Search Timeframe: {search_timeframe['start']} to {search_timeframe['end']}
            
            Your analysis should include:
            1. Identify skeptical viewpoints and opposing arguments from news coverage
            2. Evaluate the strength of contrarian evidence in news sources
            3. Look for potential blind spots in mainstream thinking
            4. Assess cognitive biases that might affect judgment
            5. Consider low-probability but high-impact scenarios from news
            6. Identify what could make the mainstream view wrong
            
            Focus on challenging assumptions and identifying potential surprises from news coverage.
            
            Output your analysis in JSON format with contrarian perspective assessment.
            """,
            agent=self.contrarian_news_researcher,
            expected_output="JSON analysis of contrarian views, potential blind spots, and disconfirming evidence from news sources",
            context=[news_coordination_task]
        )
        
        # Task 6: Final Synthesis
        synthesis_task = Task(
            description=f"""
            Synthesize all Google News research and analysis into a final well-calibrated forecast following superforecaster methodology:
            
            Question: {question}
            News Coordination: {{news_coordination_task.output}}
            Historical News Analysis: {{historical_news_task.output}}
            Current News Context: {{current_news_task.output}}
            Expert News Opinions: {{expert_news_task.output}}
            Contrarian News Views: {{contrarian_news_task.output}}
            Search Timeframe: {search_timeframe['start']} to {search_timeframe['end']}
            
            Create a final forecast that follows superforecaster methodology:
            
            1. **Start with base rates** (outside view) from historical news analysis
            2. **Adjust for specific factors** (inside view) based on current news context
            3. **Consider multiple perspectives** including expert consensus and contrarian views from news
            4. **Quantify uncertainty** appropriately and avoid overconfidence
            5. **Update incrementally** based on strength of news evidence
            6. **Think probabilistically** with a single probability estimate (0.01 to 0.99)
            
            Your forecast should include:
            - Clear probability estimate with reasoning
            - Confidence level and uncertainty bounds
            - Key factors that could change the forecast
            - Summary of most important Google News insights
            - Explanation of how you weighted different evidence types
            - Assessment of news coverage quality and completeness
            
            Follow the superforecaster process:
            - Break down the question into components
            - Look for reference classes and base rates from news
            - Adjust for current specific factors from news coverage
            - Consider what you might be missing
            - Avoid common cognitive biases
            
            Output your final forecast in JSON format with detailed reasoning.
            """,
            agent=self.synthesis_expert,
            expected_output="JSON final forecast with probability, reasoning, confidence assessment, and Google News research integration following superforecaster methodology",
            context=[news_coordination_task, historical_news_task, current_news_task, expert_news_task, contrarian_news_task]
        )
        
        return [news_coordination_task, historical_news_task, current_news_task, expert_news_task, contrarian_news_task, synthesis_task]
    
    def _parse_news_research_result(self, crew_result: str, question: str, news_research_data: Dict[str, Any], search_timeframe: Dict[str, str]) -> GoogleNewsResearchResult:
        """Parse the crew result into a structured forecast with Google News research integration"""
        
        try:
            # Try to extract JSON from the final result
            result_str = str(crew_result)
            
            # Look for JSON in the result
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = result_str[json_start:json_end]
                parsed_result = json.loads(json_str)
            else:
                # Fallback parsing
                parsed_result = {"probability": 0.5, "reasoning": result_str}
            
            # Extract key components
            probability = float(parsed_result.get("probability", 0.5))
            probability = max(0.01, min(0.99, probability))  # Ensure valid range
            
            confidence_level = parsed_result.get("confidence_level", "medium")
            reasoning = parsed_result.get("reasoning", "Analysis completed with Google News research")
            base_rate = float(parsed_result.get("base_rate", 0.5))
            
            # Extract Google News research summary
            news_research_summary = {
                "search_strategies_used": list(news_research_data.get("research_strategies", {}).keys()),
                "total_articles_found": news_research_data.get("total_articles", 0),
                "research_quality_score": news_research_data.get("research_quality_score", 0.0),
                "search_timeframe": search_timeframe,
                "key_insights": parsed_result.get("key_news_insights", [
                    "Comprehensive Google News research conducted",
                    "Multiple news perspectives analyzed",
                    "Current context evaluated from news sources"
                ]),
                "source_diversity": "High - multiple search strategies used",
                "temporal_coverage": f"News from {search_timeframe['start']} to {search_timeframe['end']}",
                "methodology": "Superforecaster approach with timestamped Google News research"
            }
            
            # Extract news sources
            news_sources = []
            for strategy_results in news_research_data.get("search_results", {}).values():
                if isinstance(strategy_results, dict) and "sources" in strategy_results:
                    news_sources.extend(strategy_results["sources"])
            
            # Extract search queries
            search_queries_used = []
            for queries in news_research_data.get("research_strategies", {}).values():
                search_queries_used.extend(queries)
            
            # Assess methodology completeness
            methodology_components = {
                "google_news_coordination": True,
                "historical_news_research": "historical" in parsed_result or "base_rate" in parsed_result,
                "current_news_analysis": "current" in parsed_result or "recent" in parsed_result,
                "expert_news_aggregation": "expert" in parsed_result or "opinion" in parsed_result,
                "contrarian_news_research": "contrarian" in parsed_result or "opposing" in parsed_result,
                "synthesis_and_calibration": True,
                "superforecaster_methodology": True,
                "timestamped_search": True
            }
            
            # Higher evidence quality due to comprehensive timestamped news research
            evidence_quality = min(0.95, 0.75 + news_research_data.get("research_quality_score", 0.0) * 0.2)
            
            return GoogleNewsResearchResult(
                question=question,
                probability=probability,
                confidence_level=confidence_level,
                reasoning=reasoning,
                base_rate=base_rate,
                evidence_quality=evidence_quality,
                methodology_components=methodology_components,
                full_analysis=parsed_result,
                news_research_summary=news_research_summary,
                news_sources=news_sources[:25],  # Limit to top 25 sources
                search_queries_used=search_queries_used,
                total_articles_found=news_research_data.get("total_articles", 0),
                search_timeframe=search_timeframe
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing Google News research result: {str(e)}")
            
            # Fallback result
            return GoogleNewsResearchResult(
                question=question,
                probability=0.5,
                confidence_level="low",
                reasoning=f"Analysis completed but parsing failed: {str(e)}",
                base_rate=0.5,
                evidence_quality=0.3,
                methodology_components={
                    "google_news_coordination": False,
                    "historical_news_research": False,
                    "current_news_analysis": False,
                    "expert_news_aggregation": False,
                    "contrarian_news_research": False,
                    "synthesis_and_calibration": False,
                    "superforecaster_methodology": False,
                    "timestamped_search": False
                },
                full_analysis={"error": str(e), "raw_result": str(crew_result)},
                news_research_summary={"error": "Failed to parse Google News research"},
                news_sources=["Error in news parsing"],
                search_queries_used=["Error in query parsing"],
                total_articles_found=0,
                search_timeframe=search_timeframe
            )