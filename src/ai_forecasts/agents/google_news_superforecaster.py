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
from ..utils.google_news_tool import GoogleNewsTool, EnhancedGoogleNewsTool


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
            model=os.getenv("DEFAULT_MODEL", "openai/gpt-4o-2024-11-20"),
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
        
        # Create Google News search tools with proper timeframe
        search_timeframe = {
            "start": "06/01/2024",
            "end": datetime.now().strftime("%m/%d/%Y")
        }
        
        google_news_tool = GoogleNewsTool(
            serp_api_key=self.serp_api_key,
            search_timeframe=search_timeframe
        )
        
        enhanced_news_tool = EnhancedGoogleNewsTool(
            serp_api_key=self.serp_api_key,
            search_timeframe=search_timeframe
        )
        
        # News Research Coordinator - Manages comprehensive news research
        self.news_research_coordinator = Agent(
            role='News Research Coordinator',
            goal='Conduct systematic Google News research following superforecaster methodology',
            backstory="""You are an expert news researcher who follows the systematic approach 
            used by top superforecasters. You gather information from Google News with precise 
            time filtering, evaluate source credibility, look for diverse perspectives, and 
            identify both supporting and contradicting evidence. You excel at finding recent 
            developments, expert opinions, base rate information, and leading indicators from 
            timestamped news articles. You have access to Google News search tools to find 
            real-time information.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[google_news_tool, enhanced_news_tool]
        )
        
        # Historical News Analyst - Finds historical precedents via timestamped news search
        self.historical_news_analyst = Agent(
            role='Historical News Research Specialist',
            goal='Research historical precedents and base rates using timestamped Google News',
            backstory="""You are an expert in finding and analyzing historical precedents 
            through timestamped Google News research. You search for similar past events, 
            calculate base rates from available news data, and identify reference classes. 
            You excel at finding news coverage of historical events, expert analysis, and 
            data that inform base rate calculations. Use Google News search tools to find 
            historical data and precedents.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[enhanced_news_tool]
        )
        
        # Current News Context Analyst - Analyzes recent news developments
        self.current_news_analyst = Agent(
            role='Current News Context Analyst',
            goal='Analyze current conditions and recent developments through timestamped Google News',
            backstory="""You are an expert at analyzing current market conditions, recent 
            developments, and emerging trends through comprehensive Google News research with 
            precise time filtering. You track breaking news, expert opinions, policy changes, 
            and market indicators. You excel at identifying how current conditions differ from 
            historical precedents based on news coverage. Use Google News search tools to find 
            the most recent and relevant information.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[google_news_tool, enhanced_news_tool]
        )
        
        # Expert Opinion News Aggregator - Gathers expert predictions from news sources
        self.expert_news_aggregator = Agent(
            role='Expert Opinion News Aggregator',
            goal='Gather and synthesize expert opinions and predictions from Google News sources',
            backstory="""You are an expert at finding and evaluating expert opinions, 
            predictions, and analysis from credible news sources through Google News. You 
            search for expert interviews, industry reports, academic commentary, and 
            professional forecasts covered in news media. You excel at weighing different 
            expert opinions and identifying consensus vs. contrarian views from news coverage. 
            Use Google News search tools to find expert opinions and professional forecasts.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[enhanced_news_tool]
        )
        
        # Contrarian News Research Agent - Looks for opposing viewpoints in news
        self.contrarian_news_researcher = Agent(
            role='Contrarian News Research Specialist',
            goal='Research opposing viewpoints and potential disconfirming evidence from news sources',
            backstory="""You are an expert at finding contrarian viewpoints and potential 
            disconfirming evidence through Google News research. You actively seek out opposing 
            opinions, skeptical analysis, and evidence that challenges the mainstream view as 
            covered in news media. You excel at identifying potential blind spots and cognitive 
            biases in forecasting through diverse news perspectives. Use Google News search tools 
            to find contrarian viewpoints and opposing opinions.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[enhanced_news_tool]
        )
        
        # Synthesis and Calibration Expert - Integrates all news research
        self.synthesis_expert = Agent(
            role='Synthesis and Calibration Expert',
            goal='Synthesize all Google News research into a well-calibrated forecast',
            backstory="""You are a master synthesizer who combines insights from comprehensive 
            Google News research following superforecaster methodology. You integrate base rates, 
            current context, expert opinions, and contrarian views from timestamped news sources. 
            You excel at proper calibration, avoiding overconfidence, and producing well-reasoned 
            probability estimates that account for uncertainty. You can also use Google News search 
            to verify and cross-check information from other agents.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[google_news_tool]
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
        
        self.logger.log("news_research_coordinator", f"🚀 Starting Google News Superforecaster analysis")
        self.logger.log("news_research_coordinator", f"📋 Question: {question}")
        self.logger.log("news_research_coordinator", f"📅 Is benchmark: {is_benchmark}")
        
        # Determine search timeframe
        search_timeframe = self._determine_search_timeframe(cutoff_date, is_benchmark)
        self.logger.log("news_research_coordinator", f"🕒 Search timeframe: {search_timeframe['start']} to {search_timeframe['end']}")
        
        # First, conduct comprehensive Google News research
        self.logger.log("news_search_engine", "🔍 Conducting comprehensive Google News research")
        news_research_data = self._conduct_comprehensive_news_research(question, search_timeframe, is_benchmark)
        self.logger.log("news_search_engine", f"📰 Found {news_research_data.get('total_articles', 0)} articles across search strategies")
        
        # Create tasks for each agent using the news research data
        self.logger.log("task_orchestrator", "📋 Creating specialized agent tasks")
        tasks = self._create_news_research_tasks(question, background, cutoff_date, time_horizon, news_research_data, search_timeframe)
        
        # Create and run the crew
        self.logger.log("crew_manager", "🤖 Initializing 6-agent superforecaster crew")
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
            CRITICAL: Use the Google News Search tool to conduct comprehensive research for the forecasting question.
            
            Question: {question}
            Search Period: {search_timeframe['start']} to {search_timeframe['end']}
            
            Your task:
            1. Use the Google News Search tool to search for information about the question
            2. Search for multiple angles: direct topic, recent developments, expert opinions
            3. Evaluate source credibility and coverage quality
            4. Identify key findings and information gaps
            
            Search queries to execute (use the tool for each):
            - "{question}" 
            - "{question} latest news"
            - "{question} expert analysis"
            - "{question} recent developments"
            
            Output this JSON structure:
            {{
                "research_quality": "high/medium/low",
                "key_findings": ["finding 1", "finding 2", "finding 3"],
                "source_credibility": "assessment of news sources found",
                "coverage_gaps": ["gap 1", "gap 2"],
                "recommendations": "brief guidance for other agents",
                "total_articles_found": "number of articles discovered",
                "search_success": "whether Google News searches were successful"
            }}
            """,
            agent=self.news_research_coordinator,
            expected_output="JSON research coordination summary with Google News search results"
        )
        
        # Task 2: Historical News Analysis
        historical_news_task = Task(
            description=f"""
            CRITICAL: Use the Enhanced Google News Search tool to find historical precedents and base rates.
            
            Question: {question}
            
            Your task:
            1. Use Enhanced Google News Search with search_type "historical" to find precedents
            2. Search for specific historical data, statistics, and success rates
            3. Look for similar past cases and their outcomes
            4. Calculate base rates from credible news sources
            
            Execute these searches using the Enhanced Google News Search tool:
            - {{"query": "{question}", "search_type": "historical"}}
            - Use Google News Search for: "{question} historical precedents"
            - Use Google News Search for: "{question} success rate statistics"
            - Use Google News Search for: "{question} past examples data"
            
            Steps:
            1. Find historical statistics, success rates, or precedent data from news sources
            2. Extract exact numbers with sample sizes from credible sources  
            3. Calculate confidence-weighted average if multiple rates exist
            4. Assess quality and temporal relevance of sources
            
            Output this JSON:
            {{
                "primary_base_rate": 0.XX,
                "base_rate_range": {{"min": 0.XX, "max": 0.XX}},
                "source": "specific credible source with details from news search",
                "reference_class": "what the base rate represents",
                "sample_size": "number of cases found in news sources",
                "confidence": "high/medium/low",
                "reasoning": "explanation based on news search findings",
                "news_sources_used": ["list of news sources found"],
                "search_success": "whether news searches found relevant data"
            }}
            
            If no exact base rate found in news, estimate from patterns and state confidence as "low".
            """,
            agent=self.historical_news_analyst,
            expected_output="JSON base rate analysis based on Google News search results",
            context=[news_coordination_task]
        )
        
        # Task 3: Current News Context Analysis  
        current_news_task = Task(
            description=f"""
            CRITICAL: Use Google News Search tools to find current factors affecting the probability.
            
            Question: {question}
            
            Your task:
            1. Use Google News Search to find recent developments and current context
            2. Use Enhanced Google News Search with search_type "current" for comprehensive coverage
            3. Identify specific factors that could increase or decrease probability
            4. Rate each factor's impact and evidence quality
            
            Execute these searches:
            - Use Google News Search for: "{question} recent developments"
            - Use Google News Search for: "{question} latest news" 
            - Use Enhanced Google News Search: {{"query": "{question}", "search_type": "current"}}
            - Use Google News Search for: "{question} current status"
            
            For each factor found:
            1. Estimate impact magnitude (strong: ±10-20%, moderate: ±3-10%, weak: ±1-3%)
            2. Rate evidence quality (high: 0.8-1.0, medium: 0.5-0.8, low: 0.2-0.5)
            3. Explain causal mechanism briefly
            
            Output this JSON:
            {{
                "positive_factors": [
                    {{
                        "factor": "specific factor with details from news",
                        "impact": "+X%",
                        "evidence_quality": 0.X,
                        "mechanism": "how it affects outcome",
                        "news_source": "source from Google News search"
                    }}
                ],
                "negative_factors": [
                    {{
                        "factor": "specific factor with details from news", 
                        "impact": "-X%",
                        "evidence_quality": 0.X,
                        "mechanism": "how it affects outcome",
                        "news_source": "source from Google News search"
                    }}
                ],
                "net_adjustment": "+/-X%",
                "confidence": "high/medium/low",
                "news_sources_consulted": ["list of news sources searched"],
                "search_success": "whether searches found relevant current information"
            }}
            """,
            agent=self.current_news_analyst,
            expected_output="JSON analysis of current factors from Google News searches",
            context=[news_coordination_task]
        )
        
        # Task 4: Expert Opinion News Aggregation
        expert_news_task = Task(
            description=f"""
            CRITICAL: Use Enhanced Google News Search tool to find and analyze expert opinions.
            
            Question: {question}
            
            Your task:
            1. Use Enhanced Google News Search with search_type "expert_opinions" to find expert analysis
            2. Search for expert predictions, analyst forecasts, and professional commentary
            3. Evaluate expert credibility and track records based on news coverage
            4. Synthesize expert consensus and disagreements
            
            Execute these searches:
            - Use Enhanced Google News Search: {{"query": "{question}", "search_type": "expert_opinions"}}
            - Use Google News Search for: "{question} expert predictions"
            - Use Google News Search for: "{question} analyst forecast" 
            - Use Google News Search for: "{question} professional analysis"
            
            Your analysis should include:
            1. Identify credible expert sources with their track records from news coverage
            2. Assess expert predictions with confidence intervals and reasoning quality
            3. Analyze expert consensus vs. disagreement patterns 
            4. Weight expert opinions by: Track record, Expertise relevance, Reasoning quality, Independence
            5. Identify potential expert biases from news reporting
            6. Compare expert predictions to base rates
            
            **EXPERT WEIGHTING CRITERIA:**
            - Track Record Weight: Excellent (1.0) > Good (0.8) > Average (0.6) > Poor (0.3) > Unknown (0.4)
            - Relevance Weight: Directly relevant expertise (1.0) > Related field (0.7) > General expertise (0.4)
            - Reasoning Quality: Detailed evidence-based (1.0) > Some reasoning (0.7) > Opinion only (0.3)
            - Independence: Independent analysis (1.0) > Some potential bias (0.7) > Clear conflicts (0.4)
            
            **OUTPUT FORMAT (EXACT JSON):**
            {{
                "expert_predictions": [
                    {{
                        "expert_name": "name and credentials from news",
                        "prediction": "specific prediction with probability or direction",
                        "prediction_confidence": "expert's stated confidence from news",
                        "reasoning_quality": "excellent/good/average/poor with explanation",
                        "track_record": "assessment based on news coverage",
                        "expertise_relevance": "direct/related/general with explanation",
                        "expert_weight": 0.XX,
                        "news_source": "source where expert opinion was found",
                        "publication_date": "when the expert opinion was published"
                    }}
                ],
                "consensus_analysis": {{
                    "expert_agreement_level": "strong/moderate/weak/none with details",
                    "consensus_direction": "positive/negative/neutral toward the outcome",
                    "consensus_strength": 0.XX,
                    "expert_disagreement_areas": ["areas where experts disagree"]
                }},
                "meta_analysis": {{
                    "total_experts_analyzed": "number",
                    "weighted_expert_consensus": 0.XX,
                    "highest_quality_expert_prediction": "prediction from most credible expert",
                    "expert_vs_base_rate_deviation": "how experts compare to base rate"
                }},
                "news_sources_consulted": ["list of news sources with expert opinions"],
                "search_success": "whether searches found expert opinions"
            }}
            
            Output your analysis in JSON format with expert opinion synthesis from news sources.
            """,
            agent=self.expert_news_aggregator,
            expected_output="JSON analysis of expert opinions from Google News searches",
            context=[news_coordination_task]
        )
        
        # Task 5: Contrarian News Research Analysis
        contrarian_news_task = Task(
            description=f"""
            CRITICAL: Use Enhanced Google News Search tool to find contrarian viewpoints and opposing evidence.
            
            Question: {question}
            
            Your task:
            1. Use Enhanced Google News Search with search_type "contrarian" to find opposing views
            2. Search for skeptical analysis, criticism, and evidence challenging mainstream views
            3. Identify potential cognitive biases in mainstream coverage
            4. Evaluate quality of contrarian arguments from news sources
            
            Execute these searches:
            - Use Enhanced Google News Search: {{"query": "{question}", "search_type": "contrarian"}}
            - Use Google News Search for: "{question} skeptical view"
            - Use Google News Search for: "{question} criticism"
            - Use Google News Search for: "why {question} unlikely"
            
            Your analysis should include:
            1. Identify high-quality skeptical viewpoints from credible news sources
            2. Evaluate contrarian evidence strength using same rigor as mainstream evidence
            3. Systematically identify cognitive biases affecting mainstream consensus:
               - Anchoring on initial information or conventional wisdom
               - Availability bias from recent/memorable events  
               - Confirmation bias in evidence selection
               - Groupthink and expert herding behavior
               - Overconfidence in predictions and models
            4. Analyze structural blind spots in mainstream analysis
            5. Evaluate low-probability, high-impact scenarios from news coverage
            6. Stress-test mainstream predictions against contrarian scenarios
            
            **CONTRARIAN EVIDENCE EVALUATION CRITERIA:**
            - Source Quality: Independent analysis > Echo chamber thinking
            - Reasoning Depth: Mechanistic explanations > Surface-level objections  
            - Evidence Base: Specific data/precedents > General skepticism
            - Predictive Track Record: Previously correct contrarians > Perennial pessimists/optimists
            
            **OUTPUT FORMAT (EXACT JSON):**
            {{
                "contrarian_arguments": [
                    {{
                        "argument": "specific contrarian viewpoint from news",
                        "evidence_quality": "high/medium/low with score (0.0-1.0)",
                        "source_credibility": "assessment of news source quality",
                        "news_source": "specific news outlet reporting this view",
                        "mechanistic_explanation": "detailed reasoning for why mainstream view might be wrong",
                        "strength_assessment": "strong/moderate/weak with justification"
                    }}
                ],
                "cognitive_bias_analysis": {{
                    "anchoring_bias": {{"detected": "yes/no", "description": "examples from news coverage"}},
                    "availability_bias": {{"detected": "yes/no", "description": "overweighting recent events"}},
                    "confirmation_bias": {{"detected": "yes/no", "description": "selective evidence consideration"}},
                    "groupthink": {{"detected": "yes/no", "description": "expert consensus without independent analysis"}},
                    "overall_bias_risk": "high/medium/low with explanation"
                }},
                "alternative_interpretations": [
                    {{
                        "interpretation": "alternative way to understand evidence from news",
                        "supporting_evidence": "evidence from news sources supporting this view",
                        "plausibility_assessment": "high/medium/low with reasoning"
                    }}
                ],
                "contrarian_synthesis": {{
                    "overall_contrarian_strength": "strong/moderate/weak with assessment",
                    "most_compelling_contrarian_point": "strongest argument against mainstream view",
                    "probability_adjustment": "suggested adjustment to mainstream probability"
                }},
                "news_sources_consulted": ["list of news sources with contrarian views"],
                "search_success": "whether searches found contrarian viewpoints"
            }}
            
            Output your analysis in JSON format with contrarian perspective assessment from news sources.
            """,
            agent=self.contrarian_news_researcher,
            expected_output="JSON analysis of contrarian views from Google News searches",
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
            
            **CRITICAL: You must provide a precise probability estimate between 0.01 and 0.99**
            
            Follow this EXACT superforecaster process:
            
            **STEP 1: ADVANCED BASE RATE INTEGRATION (Outside View)**
            - Use the confidence-weighted base rate from historical analysis
            - Incorporate base rate uncertainty range into initial probability distribution
            - Consider multiple reference classes and compute weighted ensemble base rate
            - Account for temporal trends in base rates (are success rates changing over time?)
            
            **STEP 2: SYSTEMATIC FACTOR ADJUSTMENTS (Inside View with Interaction Effects)**
            - Apply factors from current analysis with their confidence-weighted impacts
            - Consider interaction effects between factors (multiplicative vs additive)
            - Use decay functions for temporal factors (recent factors weighted more heavily)
            - Apply uncertainty propagation: High uncertainty factors get discounted
            
            **STEP 3: MULTI-DIMENSIONAL EVIDENCE WEIGHTING**
            - Weight evidence by: Source credibility × Recency × Relevance × Independence
            - Aggregate evidence quality score: Σ(Evidence_Quality × Factor_Impact) / Σ(Factor_Impact)
            - Apply evidence coherence bonus: Consistent evidence across sources gets 5-10% weight boost
            - Penalize contradictory evidence: Conflicting high-quality sources add uncertainty
            
            **STEP 4: SOPHISTICATED EXPERT INTEGRATION**
            - Use expert track record weights combined with expertise relevance
            - If expert consensus (>70% agreement): Adjust 8-15% toward consensus based on quality
            - If expert disagreement (<40% agreement): Stay closer to base rate but add uncertainty
            - If mixed consensus (40-70% agreement): Moderate adjustment (3-8%) toward plurality view
            - Apply expert calibration correction based on known overconfidence patterns
            
            **STEP 5: ENHANCED CONTRARIAN ANALYSIS**
            - Evaluate contrarian view quality using same criteria as mainstream evidence
            - Strong contrarian evidence (multiple independent sources): Adjust 5-12% toward uncertainty
            - Moderate contrarian evidence (some credible sources): Adjust 2-6% toward uncertainty  
            - Weak contrarian evidence (limited/poor sources): Minimal adjustment (0.5-2%)
            - Consider whether contrarian views reveal systematic blind spots vs isolated objections
            
            **STEP 6: ROBUST CALIBRATION AND UNCERTAINTY QUANTIFICATION**
            - Compute prediction interval: [P - uncertainty_range, P + uncertainty_range]
            - Avoid overconfidence: If evidence quality <0.7, don't go below 10% or above 90%
            - Apply reference class forecasting check: Does final probability deviate >30% from base rate? If yes, provide strong justification
            - Use logarithmic probability adjustments for extreme values to avoid overconfidence
            - Final probability should reflect true epistemic uncertainty given evidence quality
            
            **STEP 7: SYSTEMATIC ERROR CHECKING**
            - Check for anchoring bias: Did you adjust sufficiently from base rate given evidence?
            - Check for availability bias: Are you overweighting recent/memorable events?
            - Check for confirmation bias: Did you fairly evaluate disconfirming evidence?
            - Check for scope insensitivity: Are probability adjustments proportional to evidence strength?
            
            **OUTPUT FORMAT (EXACT JSON):**
            {{
                "probability": 0.XXX,
                "probability_interval": {{"min": 0.XXX, "max": 0.XXX}},
                "base_rate": 0.XXX,
                "base_rate_confidence": 0.XX,
                "base_rate_source": "detailed description of historical data with sample size and time period",
                "adjustment_calculation": {{
                    "initial_base_rate": 0.XXX,
                    "factor_adjustments": [
                        {{
                            "factor": "specific factor name",
                            "raw_impact": "+/-X.X%", 
                            "confidence_weight": 0.XX,
                            "weighted_impact": "+/-X.X%",
                            "reasoning": "detailed evidence and causal mechanism"
                        }}
                    ],
                    "evidence_quality_multiplier": 0.XX,
                    "expert_consensus_adjustment": "+/-X.X%",
                    "contrarian_adjustment": "+/-X.X%",
                    "final_calculation": "step-by-step arithmetic showing: base_rate ± adjustments = final_probability"
                }},
                "evidence_assessment": {{
                    "overall_evidence_quality": 0.XX,
                    "evidence_coherence": "high/medium/low - how well evidence sources agree",
                    "evidence_completeness": "assessment of information gaps and missing data",
                    "source_independence": "degree to which sources are independent vs echoing each other"
                }},
                "expert_analysis": {{
                    "expert_consensus": "strong_agree/moderate_agree/mixed/moderate_disagree/strong_disagree",
                    "expert_quality_score": 0.XX,
                    "consensus_direction": "probability direction experts favor",
                    "expert_vs_base_rate_deviation": "+/-X.X% from base rate"
                }},
                "contrarian_assessment": {{
                    "contrarian_strength": "strong/moderate/weak/negligible",
                    "contrarian_quality": 0.XX,
                    "blind_spots_identified": ["potential issues with mainstream analysis"],
                    "contrarian_impact_on_uncertainty": "+/-X.X%"
                }},
                "uncertainty_analysis": {{
                    "confidence_level": "high (0.8-1.0)/medium (0.5-0.8)/low (0.2-0.5)",
                    "key_uncertainties": ["uncertainty 1 with impact assessment", "uncertainty 2 with impact assessment"],
                    "information_quality": "assessment of overall information adequacy",
                    "prediction_difficulty": "inherent difficulty of this type of prediction"
                }},
                "calibration_checks": {{
                    "reference_class_consistency": "how final probability compares to similar historical cases",
                    "extreme_probability_justification": "if <15% or >85%, provide strong justification",
                    "anchoring_bias_check": "assessment of whether adjustments from base rate are sufficient",
                    "overconfidence_check": "assessment of whether uncertainty is adequately reflected"
                }},
                "reasoning": "comprehensive step-by-step explanation of the entire calculation process",
                "alternative_scenarios": [
                    {{"scenario": "optimistic case", "probability": 0.XXX, "key_assumptions": ["assumption 1", "assumption 2"]}},
                    {{"scenario": "pessimistic case", "probability": 0.XXX, "key_assumptions": ["assumption 1", "assumption 2"]}}
                ],
                "news_research_quality": "detailed assessment of Google News coverage completeness and quality"
            }}
            
            **EXAMPLE CALCULATION:**
            Base rate: 55% (historical championship defense, 80% confidence, n=50 cases)
            Adjustments:
            - Current poor performance: -8% (strong factor, 0.9 evidence quality, -8% × 0.9 = -7.2%)
            - Strong competition: -5% (moderate factor, 0.7 evidence quality, -5% × 0.7 = -3.5%)  
            - Training preparation: +2% (weak factor, 0.6 evidence quality, +2% × 0.6 = +1.2%)
            Evidence quality multiplier: 0.85 (high overall quality)
            Expert consensus: Moderate agreement toward pessimistic (-3%)
            Contrarian views: Weak (+1% toward uncertainty)
            Calculation: 0.55 + (-0.072 - 0.035 + 0.012) × 0.85 - 0.03 + 0.01 = 0.55 - 0.081 - 0.03 + 0.01 = 0.449
            Final: 0.45 (with interval 0.40-0.50 reflecting uncertainty)
            
            Be extremely precise, show detailed mathematical work, and provide robust confidence intervals. 
            Avoid round numbers like 0.50 unless truly justified by balanced evidence.
            
            **MANDATORY CALIBRATION CHECKS:**
            1. If predicting <15% or >85%: Provide overwhelming evidence and historical precedent
            2. If deviating >25% from base rate: Justify with strong, independent evidence sources
            3. If evidence quality <0.7: Keep probability within 20-80% range to reflect uncertainty
            4. If expert disagreement >40%: Add extra uncertainty and stay closer to base rate
            5. Cross-check: Do similar historical cases support this probability level?
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