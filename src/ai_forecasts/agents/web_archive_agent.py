"""
Web Archive Research Agent - Advanced historical web research using Wayback Machine
"""

import json
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import quote, urljoin
import time

from langchain.schema import HumanMessage, SystemMessage
from ..utils.llm_client import LLMClient
from ..utils.agent_logger import agent_logger


class WebArchiveAgent:
    """
    Advanced web archive research agent that uses Wayback Machine and other archives
    to gather historical information for forecasting
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = (llm_client or LLMClient()).get_client()
        self.logger = agent_logger
        self.wayback_api = "https://web.archive.org/wayback/available"
        self.wayback_search = "https://web.archive.org/cdx/search/cdx"
        
    def research_historical_context(
        self, 
        topic: str, 
        cutoff_date: datetime,
        research_depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Research historical context for a forecasting question using web archives
        """
        
        self.logger.info(f"🔍 Starting web archive research for: {topic}")
        self.logger.info(f"📅 Cutoff date: {cutoff_date}")
        
        # Step 1: Identify key sources and websites to research
        key_sources = self._identify_key_sources(topic)
        
        # Step 2: Search for archived content
        archived_content = self._search_archived_content(key_sources, cutoff_date)
        
        # Step 3: Extract and analyze historical data
        historical_analysis = self._analyze_historical_content(archived_content, topic, cutoff_date)
        
        # Step 4: Identify trends and patterns
        trend_analysis = self._identify_historical_trends(historical_analysis, topic)
        
        # Step 5: Gather expert opinions from archives
        expert_opinions = self._extract_historical_expert_opinions(archived_content, topic)
        
        # Step 6: Compile comprehensive research report
        research_report = self._compile_research_report(
            topic, cutoff_date, key_sources, archived_content, 
            historical_analysis, trend_analysis, expert_opinions
        )
        
        return research_report
    
    def _identify_key_sources(self, topic: str) -> List[Dict[str, Any]]:
        """Identify key websites and sources to research for the topic"""
        
        prompt = f"""
        As a research expert, identify the most important websites and sources to research for this topic:
        
        Topic: {topic}
        
        Identify:
        1. News websites (major newspapers, news agencies)
        2. Industry publications and trade journals
        3. Government websites and official sources
        4. Academic institutions and research centers
        5. Think tanks and policy organizations
        6. Company websites and investor relations
        7. Social media and forums (if relevant)
        8. Specialized databases and archives
        
        For each source, provide:
        - Website URL/domain
        - Type of source
        - Relevance to topic (1-10)
        - Expected information quality
        - Specific sections/pages to focus on
        
        Prioritize authoritative, well-archived sources.
        
        Format as JSON array of source objects.
        """
        
        messages = [
            SystemMessage(content="You are an expert research librarian specializing in web archives."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            sources = json.loads(response.content)
            return sources if isinstance(sources, list) else []
        except:
            # Fallback to common sources
            return [
                {"url": "reuters.com", "type": "news", "relevance": 8},
                {"url": "bloomberg.com", "type": "financial_news", "relevance": 7},
                {"url": "nytimes.com", "type": "news", "relevance": 7},
                {"url": "wsj.com", "type": "business_news", "relevance": 8},
                {"url": "bbc.com", "type": "news", "relevance": 7}
            ]
    
    def _search_archived_content(
        self, 
        sources: List[Dict[str, Any]], 
        cutoff_date: datetime
    ) -> List[Dict[str, Any]]:
        """Search for archived content from identified sources"""
        
        archived_content = []
        cutoff_timestamp = cutoff_date.strftime("%Y%m%d")
        
        for source in sources[:10]:  # Limit to top 10 sources
            try:
                domain = source.get("url", "").replace("https://", "").replace("http://", "")
                
                # Search for archived snapshots
                snapshots = self._get_wayback_snapshots(domain, cutoff_date)
                
                for snapshot in snapshots[:5]:  # Limit to 5 snapshots per source
                    content = self._extract_snapshot_content(snapshot, source)
                    if content:
                        archived_content.append(content)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.logger.warning(f"Error searching {source.get('url', 'unknown')}: {str(e)}")
                continue
        
        return archived_content
    
    def _get_wayback_snapshots(self, domain: str, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Get Wayback Machine snapshots for a domain before cutoff date"""
        
        try:
            # Search for snapshots in the year before cutoff
            start_date = (cutoff_date - timedelta(days=365)).strftime("%Y%m%d")
            end_date = cutoff_date.strftime("%Y%m%d")
            
            # Use CDX API to find snapshots
            params = {
                "url": f"{domain}/*",
                "from": start_date,
                "to": end_date,
                "output": "json",
                "limit": 100,
                "filter": "statuscode:200"
            }
            
            response = requests.get(self.wayback_search, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                snapshots = []
                
                # Skip header row
                for row in data[1:]:
                    if len(row) >= 3:
                        snapshots.append({
                            "timestamp": row[1],
                            "url": row[2],
                            "wayback_url": f"https://web.archive.org/web/{row[1]}/{row[2]}"
                        })
                
                return snapshots
            
        except Exception as e:
            self.logger.warning(f"Error getting snapshots for {domain}: {str(e)}")
        
        return []
    
    def _extract_snapshot_content(self, snapshot: Dict[str, Any], source: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract content from a Wayback Machine snapshot"""
        
        try:
            # For now, we'll simulate content extraction
            # In a real implementation, you'd fetch and parse the archived page
            
            return {
                "source": source.get("url", "unknown"),
                "timestamp": snapshot.get("timestamp", ""),
                "url": snapshot.get("url", ""),
                "wayback_url": snapshot.get("wayback_url", ""),
                "content_type": source.get("type", "unknown"),
                "relevance": source.get("relevance", 5),
                "extracted_text": f"Archived content from {source.get('url', 'unknown')} at {snapshot.get('timestamp', 'unknown time')}",
                "metadata": {
                    "source_type": source.get("type", "unknown"),
                    "archive_date": snapshot.get("timestamp", ""),
                    "original_url": snapshot.get("url", "")
                }
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting content from snapshot: {str(e)}")
            return None
    
    def _analyze_historical_content(
        self, 
        archived_content: List[Dict[str, Any]], 
        topic: str, 
        cutoff_date: datetime
    ) -> Dict[str, Any]:
        """Analyze historical content for patterns and insights"""
        
        if not archived_content:
            return {"analysis": "No archived content available", "insights": []}
        
        content_summary = "\n".join([
            f"Source: {item['source']} ({item['timestamp']}): {item['extracted_text'][:200]}..."
            for item in archived_content[:10]
        ])
        
        prompt = f"""
        As a historical analyst, analyze this archived web content related to the topic:
        
        Topic: {topic}
        Cutoff Date: {cutoff_date.strftime('%Y-%m-%d')}
        
        Archived Content Summary:
        {content_summary}
        
        Analyze:
        1. Key themes and topics discussed
        2. Evolution of sentiment and opinions over time
        3. Important events and milestones mentioned
        4. Expert predictions and forecasts made
        5. Data points and statistics referenced
        6. Emerging trends and patterns
        7. Contradictions or changes in narrative
        
        Focus on information that could inform forecasting about the topic.
        
        Format as JSON with structured analysis.
        """
        
        messages = [
            SystemMessage(content="You are an expert historical analyst specializing in web archive research."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "key_themes": [],
                "sentiment_evolution": "neutral",
                "important_events": [],
                "expert_predictions": [],
                "data_points": [],
                "trends": [],
                "narrative_changes": []
            }
    
    def _identify_historical_trends(self, historical_analysis: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Identify trends and patterns from historical analysis"""
        
        prompt = f"""
        Based on the historical analysis, identify key trends and patterns:
        
        Topic: {topic}
        Historical Analysis: {json.dumps(historical_analysis, indent=2)}
        
        Identify:
        1. Directional trends (increasing, decreasing, cyclical)
        2. Acceleration or deceleration patterns
        3. Inflection points and trend reversals
        4. Seasonal or cyclical patterns
        5. Leading and lagging indicators
        6. Correlation with external events
        7. Predictive patterns from the past
        
        For each trend:
        - Description and direction
        - Strength and consistency
        - Time horizon
        - Potential future implications
        
        Format as JSON with structured trend analysis.
        """
        
        messages = [
            SystemMessage(content="You are an expert trend analyst specializing in historical pattern recognition."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "directional_trends": [],
                "acceleration_patterns": [],
                "inflection_points": [],
                "cyclical_patterns": [],
                "leading_indicators": [],
                "correlations": [],
                "predictive_patterns": []
            }
    
    def _extract_historical_expert_opinions(
        self, 
        archived_content: List[Dict[str, Any]], 
        topic: str
    ) -> Dict[str, Any]:
        """Extract and analyze expert opinions from archived content"""
        
        expert_content = [
            item for item in archived_content 
            if item.get("content_type") in ["expert_analysis", "research", "academic", "think_tank"]
        ]
        
        if not expert_content:
            return {"expert_opinions": [], "consensus": "unknown"}
        
        content_summary = "\n".join([
            f"Expert source: {item['source']} ({item['timestamp']}): {item['extracted_text'][:300]}..."
            for item in expert_content[:5]
        ])
        
        prompt = f"""
        Extract and analyze expert opinions from this archived content:
        
        Topic: {topic}
        
        Expert Content:
        {content_summary}
        
        Extract:
        1. Specific predictions and forecasts made
        2. Confidence levels expressed
        3. Reasoning and methodology used
        4. Track record and credibility of sources
        5. Consensus vs. contrarian views
        6. Changes in expert opinion over time
        7. Accuracy of past predictions (if verifiable)
        
        Synthesize into coherent expert opinion analysis.
        
        Format as JSON with structured expert analysis.
        """
        
        messages = [
            SystemMessage(content="You are an expert at analyzing and synthesizing expert opinions."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "expert_predictions": [],
                "confidence_levels": [],
                "reasoning_patterns": [],
                "credibility_assessment": [],
                "consensus_view": "unknown",
                "contrarian_views": [],
                "opinion_evolution": []
            }
    
    def _compile_research_report(
        self,
        topic: str,
        cutoff_date: datetime,
        key_sources: List[Dict[str, Any]],
        archived_content: List[Dict[str, Any]],
        historical_analysis: Dict[str, Any],
        trend_analysis: Dict[str, Any],
        expert_opinions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile comprehensive research report"""
        
        return {
            "research_topic": topic,
            "cutoff_date": cutoff_date.isoformat(),
            "methodology": "web_archive_research",
            "sources_researched": len(key_sources),
            "content_pieces_analyzed": len(archived_content),
            "key_sources": key_sources,
            "historical_analysis": historical_analysis,
            "trend_analysis": trend_analysis,
            "expert_opinions": expert_opinions,
            "research_quality": self._assess_research_quality(archived_content),
            "limitations": self._identify_research_limitations(archived_content, cutoff_date),
            "confidence_level": self._calculate_research_confidence(
                archived_content, historical_analysis, expert_opinions
            ),
            "summary": self._generate_research_summary(
                topic, historical_analysis, trend_analysis, expert_opinions
            )
        }
    
    def _assess_research_quality(self, archived_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the quality of research conducted"""
        
        if not archived_content:
            return {"quality_score": 0.1, "issues": ["No archived content found"]}
        
        source_diversity = len(set(item.get("source", "") for item in archived_content))
        avg_relevance = sum(item.get("relevance", 5) for item in archived_content) / len(archived_content)
        
        quality_score = min(1.0, (source_diversity / 5) * 0.5 + (avg_relevance / 10) * 0.5)
        
        return {
            "quality_score": quality_score,
            "source_diversity": source_diversity,
            "average_relevance": avg_relevance,
            "content_pieces": len(archived_content),
            "issues": []
        }
    
    def _identify_research_limitations(
        self, 
        archived_content: List[Dict[str, Any]], 
        cutoff_date: datetime
    ) -> List[str]:
        """Identify limitations in the research"""
        
        limitations = []
        
        if len(archived_content) < 5:
            limitations.append("Limited archived content available")
        
        if cutoff_date < datetime.now() - timedelta(days=365):
            limitations.append("Cutoff date is more than 1 year ago - may miss recent developments")
        
        source_types = set(item.get("content_type", "unknown") for item in archived_content)
        if len(source_types) < 3:
            limitations.append("Limited diversity in source types")
        
        return limitations
    
    def _calculate_research_confidence(
        self,
        archived_content: List[Dict[str, Any]],
        historical_analysis: Dict[str, Any],
        expert_opinions: Dict[str, Any]
    ) -> float:
        """Calculate confidence level in research findings"""
        
        if not archived_content:
            return 0.1
        
        # Base confidence on content quantity and quality
        content_score = min(1.0, len(archived_content) / 10)
        
        # Boost for expert opinions
        expert_score = 0.2 if expert_opinions.get("expert_predictions") else 0.0
        
        # Boost for trend analysis
        trend_score = 0.2 if historical_analysis.get("trends") else 0.0
        
        return min(1.0, content_score * 0.6 + expert_score + trend_score)
    
    def _generate_research_summary(
        self,
        topic: str,
        historical_analysis: Dict[str, Any],
        trend_analysis: Dict[str, Any],
        expert_opinions: Dict[str, Any]
    ) -> str:
        """Generate a concise research summary"""
        
        summary_parts = [f"Web archive research on: {topic}"]
        
        if historical_analysis.get("key_themes"):
            summary_parts.append(f"Key themes: {', '.join(historical_analysis['key_themes'][:3])}")
        
        if trend_analysis.get("directional_trends"):
            summary_parts.append(f"Main trends identified: {len(trend_analysis['directional_trends'])}")
        
        if expert_opinions.get("consensus_view"):
            summary_parts.append(f"Expert consensus: {expert_opinions['consensus_view']}")
        
        return ". ".join(summary_parts)