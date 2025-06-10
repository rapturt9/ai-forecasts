"""
CrewAI-based Superforecaster System
Implements advanced forecasting using multiple specialized agents
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
from ..utils.agent_logger import agent_logger
from ..utils.llm_client import LLMClient


@dataclass
class ForecastResult:
    """Structured forecast result"""
    question: str
    probability: float
    confidence_level: str
    reasoning: str
    base_rate: float
    evidence_quality: float
    methodology_components: Dict[str, bool]
    full_analysis: Dict[str, Any]


class CrewAISuperforecaster:
    """
    Advanced forecasting system using CrewAI with specialized agents
    that implement superforecaster methodologies
    """
    
    def __init__(self, openrouter_api_key: str):
        self.logger = agent_logger
        
        # Configure LLM for CrewAI with proper headers
        self.llm = LLM(
            model="openrouter/openai/gpt-4o-2024-11-20",
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            default_headers={
                "HTTP-Referer": "https://ai-forecasts.com",
                "X-Title": "AI Forecasting System"
            }
        )
        
        # Initialize specialized agents
        self._setup_agents()
    
    def _setup_agents(self):
        """Setup specialized forecasting agents"""
        
        # Base Rate Analyst - Focuses on reference class forecasting
        self.base_rate_agent = Agent(
            role='Base Rate Analyst',
            goal='Identify reference classes and establish base rates for forecasting questions',
            backstory="""You are an expert in reference class forecasting, a key technique used by 
            superforecasters. You excel at finding similar historical situations and calculating 
            base rates. You always start with outside view before considering inside view factors.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Evidence Researcher - Gathers and evaluates evidence
        self.evidence_agent = Agent(
            role='Evidence Researcher',
            goal='Systematically gather and evaluate evidence relevant to forecasting questions',
            backstory="""You are a meticulous researcher who systematically gathers evidence 
            from multiple sources. You evaluate evidence quality, identify biases, and organize 
            information to support accurate forecasting. You focus on facts over opinions.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Perspective Analyst - Analyzes multiple viewpoints
        self.perspective_agent = Agent(
            role='Perspective Analyst',
            goal='Analyze questions from multiple perspectives to avoid cognitive biases',
            backstory="""You are an expert at considering multiple perspectives and scenarios. 
            You systematically examine optimistic, pessimistic, and neutral viewpoints. You 
            identify potential blind spots and challenge assumptions to improve forecast accuracy.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Uncertainty Quantifier - Handles uncertainty and confidence
        self.uncertainty_agent = Agent(
            role='Uncertainty Quantifier',
            goal='Quantify uncertainties and assess confidence levels in forecasts',
            backstory="""You are an expert in uncertainty quantification and probabilistic 
            reasoning. You identify sources of uncertainty, assess confidence intervals, and 
            help calibrate probability estimates. You prevent overconfidence and ensure 
            appropriate humility in forecasting.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Synthesis Expert - Combines all analysis into final forecast
        self.synthesis_agent = Agent(
            role='Synthesis Expert',
            goal='Synthesize all analysis into a well-calibrated final forecast',
            backstory="""You are a master synthesizer who combines insights from base rates, 
            evidence, multiple perspectives, and uncertainty analysis. You create well-calibrated 
            probability estimates that balance all available information. You are the final 
            decision maker in the forecasting process.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
    
    def forecast(
        self, 
        question: str, 
        background: str = "",
        cutoff_date: Optional[datetime] = None,
        time_horizon: str = "1 year"
    ) -> ForecastResult:
        """
        Generate a forecast using the CrewAI superforecaster system
        """
        
        self.logger.info(f"🚀 Starting CrewAI superforecaster analysis")
        self.logger.info(f"📋 Question: {question}")
        
        # Create tasks for each agent
        tasks = self._create_tasks(question, background, cutoff_date, time_horizon)
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.base_rate_agent,
                self.evidence_agent, 
                self.perspective_agent,
                self.uncertainty_agent,
                self.synthesis_agent
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the forecasting process
        self.logger.info(f"🔄 Executing forecasting crew...")
        result = crew.kickoff()
        
        # Parse and structure the result
        forecast_result = self._parse_crew_result(result, question)
        
        self.logger.info(f"✅ CrewAI forecast complete: {forecast_result.probability:.3f}")
        return forecast_result
    
    def _create_tasks(
        self, 
        question: str, 
        background: str, 
        cutoff_date: Optional[datetime], 
        time_horizon: str
    ) -> List[Task]:
        """Create tasks for each specialized agent"""
        
        cutoff_str = cutoff_date.strftime("%Y-%m-%d") if cutoff_date else "present"
        
        # Task 1: Base Rate Analysis
        base_rate_task = Task(
            description=f"""
            Analyze the base rates for this forecasting question using reference class forecasting:
            
            Question: {question}
            Background: {background}
            Information cutoff: {cutoff_str}
            Time horizon: {time_horizon}
            
            Your analysis should include:
            1. Identify the most appropriate reference class (similar historical situations)
            2. Calculate the base rate frequency for this type of event
            3. Assess the quality and size of your reference class
            4. Consider any adjustments needed for current context
            5. Provide confidence level in your base rate estimate
            
            Focus on historical precedents and avoid being influenced by the specific details 
            of this case (outside view). Provide specific numbers and reasoning.
            
            Output your analysis in JSON format with clear base rate estimate.
            """,
            agent=self.base_rate_agent,
            expected_output="JSON analysis with base rate estimate, reference class details, and confidence assessment"
        )
        
        # Task 2: Evidence Gathering
        evidence_task = Task(
            description=f"""
            Systematically gather and evaluate evidence for this forecasting question:
            
            Question: {question}
            Background: {background}
            Information cutoff: {cutoff_str}
            
            Your analysis should include:
            1. Identify key evidence categories (trends, expert opinions, leading indicators, etc.)
            2. Evaluate evidence quality and reliability
            3. Note any missing or contradictory evidence
            4. Assess potential biases in available evidence
            5. Organize evidence by relevance and credibility
            
            Focus on factual information available before {cutoff_str}. Be systematic and thorough.
            
            Output your analysis in JSON format with categorized evidence.
            """,
            agent=self.evidence_agent,
            expected_output="JSON analysis with categorized evidence, quality assessments, and reliability scores"
        )
        
        # Task 3: Multiple Perspectives
        perspective_task = Task(
            description=f"""
            Analyze this question from multiple perspectives to identify potential biases:
            
            Question: {question}
            Background: {background}
            
            Your analysis should include:
            1. Optimistic scenario (what could make this more likely?)
            2. Pessimistic scenario (what could prevent this?)
            3. Status quo scenario (what if trends continue?)
            4. Black swan scenario (unexpected events)
            5. Different stakeholder perspectives
            6. Potential cognitive biases affecting judgment
            
            For each perspective, provide probability estimates and key factors.
            Challenge assumptions and look for blind spots.
            
            Output your analysis in JSON format with multiple scenario assessments.
            """,
            agent=self.perspective_agent,
            expected_output="JSON analysis with multiple perspectives, scenario probabilities, and bias identification"
        )
        
        # Task 4: Uncertainty Quantification
        uncertainty_task = Task(
            description=f"""
            Quantify uncertainties and assess confidence for this forecasting question:
            
            Question: {question}
            Base rate analysis: {{base_rate_task.output}}
            Evidence analysis: {{evidence_task.output}}
            Perspective analysis: {{perspective_task.output}}
            
            Your analysis should include:
            1. Identify major sources of uncertainty
            2. Assess the quality of available information
            3. Determine appropriate confidence intervals
            4. Evaluate potential for overconfidence
            5. Consider what additional information would be most valuable
            6. Recommend confidence level for final forecast
            
            Be honest about limitations and avoid false precision.
            
            Output your analysis in JSON format with uncertainty assessment.
            """,
            agent=self.uncertainty_agent,
            expected_output="JSON analysis with uncertainty quantification, confidence intervals, and quality assessment",
            context=[base_rate_task, evidence_task, perspective_task]
        )
        
        # Task 5: Final Synthesis
        synthesis_task = Task(
            description=f"""
            Synthesize all previous analysis into a final well-calibrated forecast:
            
            Question: {question}
            Base rate analysis: {{base_rate_task.output}}
            Evidence analysis: {{evidence_task.output}}
            Perspective analysis: {{perspective_task.output}}
            Uncertainty analysis: {{uncertainty_task.output}}
            
            Create a final forecast that:
            1. Starts with the base rate as an anchor
            2. Adjusts based on specific evidence and context
            3. Considers multiple perspectives and scenarios
            4. Accounts for uncertainty and confidence levels
            5. Provides a single probability estimate (0.01 to 0.99)
            6. Explains the reasoning chain clearly
            7. Identifies key factors that could change the forecast
            
            Be well-calibrated and avoid overconfidence. Explain how you weighted 
            different pieces of analysis.
            
            Output your final forecast in JSON format with probability and reasoning.
            """,
            agent=self.synthesis_agent,
            expected_output="JSON final forecast with probability estimate, confidence level, and detailed reasoning",
            context=[base_rate_task, evidence_task, perspective_task, uncertainty_task]
        )
        
        return [base_rate_task, evidence_task, perspective_task, uncertainty_task, synthesis_task]
    
    def _parse_crew_result(self, crew_result: str, question: str) -> ForecastResult:
        """Parse the crew result into a structured forecast"""
        
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
            reasoning = parsed_result.get("reasoning", "Analysis completed")
            base_rate = float(parsed_result.get("base_rate", 0.5))
            
            # Assess methodology completeness
            methodology_components = {
                "base_rate_analysis": "base_rate" in parsed_result,
                "evidence_gathering": "evidence" in parsed_result,
                "multiple_perspectives": "perspectives" in parsed_result or "scenarios" in parsed_result,
                "uncertainty_quantification": "uncertainty" in parsed_result or "confidence" in parsed_result,
                "synthesis": True  # Always true if we got here
            }
            
            evidence_quality = parsed_result.get("evidence_quality", 0.7)
            
            return ForecastResult(
                question=question,
                probability=probability,
                confidence_level=confidence_level,
                reasoning=reasoning,
                base_rate=base_rate,
                evidence_quality=evidence_quality,
                methodology_components=methodology_components,
                full_analysis=parsed_result
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing crew result: {str(e)}")
            
            # Fallback result
            return ForecastResult(
                question=question,
                probability=0.5,
                confidence_level="low",
                reasoning=f"Analysis completed but parsing failed: {str(e)}",
                base_rate=0.5,
                evidence_quality=0.3,
                methodology_components={
                    "base_rate_analysis": False,
                    "evidence_gathering": False,
                    "multiple_perspectives": False,
                    "uncertainty_quantification": False,
                    "synthesis": False
                },
                full_analysis={"error": str(e), "raw_result": str(crew_result)}
            )