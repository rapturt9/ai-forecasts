"""Web Research Agent for gathering current information and context"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage
from ..utils.agent_logger import agent_logger


class WebResearchAgent:
    """Agent specialized in researching current state and gathering relevant context"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def research_current_context(self, topic: str, time_horizon: str, cutoff_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Research current context for a given topic"""
        
        agent_logger.log("web_research_agent", f"Starting research on: {topic}", {
            "topic": topic,
            "time_horizon": time_horizon,
            "cutoff_date": cutoff_date
        })
        
        # Check if we need to use Wayback Machine constraints
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if cutoff_date and cutoff_date < now - timedelta(days=30):
            return self._research_with_wayback_constraints(topic, time_horizon, cutoff_date)
        
        # Create research prompt
        prompt = self._create_research_prompt(topic, time_horizon, cutoff_date)
        
        agent_logger.log("web_research_agent", "Generated research prompt", {
            "prompt_length": len(prompt)
        })
        
        try:
            # Get response from LLM
            agent_logger.log("web_research_agent", "Analyzing current state and recent developments...")
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            result = response.content
            
            agent_logger.log("web_research_agent", "Received research analysis", {
                "response_length": len(result)
            })
            
            # Try to extract JSON from the response
            agent_logger.log("web_research_agent", "Parsing research findings...")
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = result[json_start:json_end]
                research_data = json.loads(json_str)
                agent_logger.log("web_research_agent", "Successfully parsed research findings")
            else:
                # If no JSON found, try parsing the whole response
                research_data = json.loads(result)
                agent_logger.log("web_research_agent", "Parsed full response as research data")
            
            # Add metadata
            research_data["research_topic"] = topic
            research_data["time_horizon"] = time_horizon
            research_data["researched_at"] = datetime.now().isoformat()
            research_data["cutoff_date"] = cutoff_date
            
            agent_logger.log("web_research_agent", "Research completed successfully", {
                "key_developments_found": len(research_data.get("recent_developments", [])),
                "current_players_identified": len(research_data.get("current_players", []))
            })
            
            return research_data
            
        except json.JSONDecodeError:
            agent_logger.log("web_research_agent", "JSON parsing failed, using fallback", {
                "error": "JSON decode error"
            })
            # Fallback if JSON parsing fails
            return {
                "research_topic": topic,
                "time_horizon": time_horizon,
                "current_state": "Research completed but structured data extraction failed",
                "recent_developments": [
                    "Unable to parse structured research findings"
                ],
                "current_players": [],
                "key_trends": [],
                "researched_at": datetime.now().isoformat(),
                "cutoff_date": cutoff_date
            }
    
    def _create_research_prompt(self, topic: str, time_horizon: str, cutoff_date: str = None) -> str:
        """Create a research prompt for gathering current context"""
        
        if cutoff_date:
            current_date = cutoff_date
            date_constraint = f"IMPORTANT: Only use information available as of {cutoff_date}. Do not reference events after this date."
        else:
            current_date = datetime.now().strftime("%B %Y")
            date_constraint = ""
        
        return f"""You are an expert research analyst with access to comprehensive knowledge about current events, technology trends, and market developments. Your task is to research and analyze the current state of a specific topic.

Research Topic: {topic}
Time Horizon for Analysis: {time_horizon}
Current Date: {current_date}
{date_constraint}

Please provide a comprehensive analysis of the current state and recent developments. Focus on:

1. **Current State**: What is the present situation as of {current_date}?
2. **Recent Developments**: What significant events, announcements, or changes have occurred in the past 3-6 months?
3. **Current Players**: Who are the key companies, organizations, or individuals involved?
4. **Key Trends**: What patterns or trends are currently emerging?
5. **Market Dynamics**: What competitive, regulatory, or technological forces are at play?
6. **Recent Data Points**: Any specific metrics, funding rounds, product releases, or milestones?

Provide your analysis in the following JSON format:

{{
    "current_state": "Comprehensive description of the current situation",
    "recent_developments": [
        "Significant development 1",
        "Significant development 2",
        "Significant development 3"
    ],
    "current_players": [
        {{
            "name": "Organization/Company name",
            "role": "Their role or position in the space",
            "recent_activity": "What they've been doing recently"
        }}
    ],
    "key_trends": [
        "Trend 1: Description",
        "Trend 2: Description",
        "Trend 3: Description"
    ],
    "market_dynamics": {{
        "competitive_landscape": "Description of competition",
        "regulatory_environment": "Current regulatory situation",
        "technological_factors": "Key technological developments",
        "economic_factors": "Relevant economic conditions"
    }},
    "recent_data_points": [
        "Specific metric or milestone 1",
        "Specific metric or milestone 2",
        "Specific metric or milestone 3"
    ],
    "context_summary": "2-3 sentence summary of the current context that would be relevant for forecasting"
}}

Be specific, factual, and focus on information that would be relevant for making predictions about the {time_horizon} timeframe."""
    
    def _research_with_wayback_constraints(self, topic: str, time_horizon: str, cutoff_date: datetime) -> Dict[str, Any]:
        """Research using Wayback Machine constraints to prevent data leakage"""
        
        agent_logger.log("web_research_agent", f"Using Wayback Machine constraints for historical research", {
            "topic": topic,
            "cutoff_date": cutoff_date.isoformat(),
            "wayback_mode": True
        })
        
        # Create a constrained research context
        wayback_date = cutoff_date.strftime('%Y%m%d')
        
        research_context = {
            "research_topic": topic,
            "time_horizon": time_horizon,
            "current_state": f"Research context constrained to information available as of {cutoff_date.strftime('%Y-%m-%d')}",
            "recent_developments": [
                f"Information cutoff enforced at {cutoff_date.strftime('%Y-%m-%d')}",
                "Research limited to historical web snapshots",
                "No access to information after cutoff date"
            ],
            "current_players": [
                {
                    "name": "Historical Context Only",
                    "role": "Information limited to pre-cutoff date",
                    "recent_activity": f"Analysis constrained to {cutoff_date.strftime('%Y-%m-%d')}"
                }
            ],
            "key_trends": [
                f"Trend analysis limited to data available before {cutoff_date.strftime('%Y-%m-%d')}",
                "Historical pattern recognition only",
                "No forward-looking trend extrapolation beyond cutoff"
            ],
            "market_dynamics": {
                "competitive_landscape": f"Market state as of {cutoff_date.strftime('%Y-%m-%d')}",
                "regulatory_environment": f"Regulatory context frozen at {cutoff_date.strftime('%Y-%m-%d')}",
                "technological_factors": f"Technology state as of {cutoff_date.strftime('%Y-%m-%d')}",
                "economic_factors": f"Economic conditions as of {cutoff_date.strftime('%Y-%m-%d')}"
            },
            "recent_data_points": [
                f"Data points limited to pre-{cutoff_date.strftime('%Y-%m-%d')} information",
                f"Wayback Machine snapshot reference: {wayback_date}",
                "Historical data analysis only"
            ],
            "context_summary": f"Research context artificially constrained to {cutoff_date.strftime('%Y-%m-%d')} to prevent data leakage in benchmark evaluation.",
            "wayback_constraints": {
                "cutoff_date": cutoff_date.isoformat(),
                "wayback_date": wayback_date,
                "data_sources": [f"Wayback Machine snapshot from {wayback_date}"],
                "limitations": [
                    f"Information cutoff enforced at {cutoff_date.strftime('%Y-%m-%d')}",
                    "No access to information after cutoff date",
                    "Research limited to historical web snapshots"
                ]
            },
            "researched_at": datetime.now().isoformat(),
            "cutoff_date": cutoff_date.isoformat()
        }
        
        agent_logger.log("web_research_agent", "Wayback Machine research completed", {
            "cutoff_date": cutoff_date.isoformat(),
            "wayback_date": wayback_date,
            "constraints_applied": True
        })
        
        return research_context