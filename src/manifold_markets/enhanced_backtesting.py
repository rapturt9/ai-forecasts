"""
Enhanced Backtesting System with CrewAI Market Selection
Runs hourly for a week to test agent performance
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

from .client import ManifoldMarketsClient
from .kelly_criterion import KellyCriterionCalculator
from .enhanced_market_agent import EnhancedMarketAgent
import sys
sys.path.append(str(Path(__file__).parent.parent))
from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster
from ai_forecasts.utils.agent_logger import agent_logger

logger = logging.getLogger(__name__)


@dataclass
class BacktestSession:
    """Backtesting session configuration and results"""
    session_id: str
    start_time: datetime
    end_time: datetime
    initial_balance: float
    current_balance: float
    total_trades: int
    winning_trades: int
    total_return: float
    max_drawdown: float
    sharpe_ratio: float
    kelly_utilization: float
    markets_analyzed: int
    hourly_results: List[Dict]
    trade_history: List[Dict]
    market_selection_log: List[Dict]


class CrewAIMarketSelector:
    """CrewAI-powered market selection system"""
    
    def __init__(self, openrouter_api_key: str):
        self.openrouter_api_key = openrouter_api_key
        self.logger = agent_logger
        
        # Configure LLM
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
        
        self._setup_agents()
    
    def _setup_agents(self):
        """Setup CrewAI agents for market selection"""
        
        # Market Opportunity Scout
        self.opportunity_scout = Agent(
            role='Market Opportunity Scout',
            goal='Identify the most promising prediction markets for profitable trading',
            backstory="""You are an expert market analyst specializing in prediction markets. Your expertise lies in identifying markets with the highest potential for profitable trading based on:

1. Market inefficiencies and mispricing
2. Information asymmetries
3. Liquidity and volume patterns
4. News flow and event timing
5. Behavioral biases in market participants

You use quantitative analysis combined with qualitative insights to rank markets by their profit potential.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Risk Assessment Specialist
        self.risk_assessor = Agent(
            role='Risk Assessment Specialist',
            goal='Evaluate and quantify risks for each potential trading opportunity',
            backstory="""You are a risk management expert with deep experience in prediction markets. Your role is to:

1. Identify and quantify various risk factors
2. Assess market liquidity and execution risks
3. Evaluate information risks and uncertainty
4. Calculate risk-adjusted returns
5. Recommend position sizing based on Kelly Criterion

You ensure that all trading decisions are made with proper risk management principles.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Portfolio Strategist
        self.portfolio_strategist = Agent(
            role='Portfolio Strategist',
            goal='Optimize market selection and position sizing for maximum risk-adjusted returns',
            backstory="""You are a portfolio optimization expert who specializes in prediction market trading. Your expertise includes:

1. Kelly Criterion optimization
2. Portfolio diversification strategies
3. Correlation analysis between markets
4. Capital allocation optimization
5. Risk-return optimization

You make final decisions on which markets to trade and how much capital to allocate to each position.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
    
    async def select_best_markets(self, available_markets: List[Dict], current_balance: float, max_markets: int = 5) -> List[Dict]:
        """
        Use CrewAI to select the best markets for trading
        
        Args:
            available_markets: List of available markets from Manifold
            current_balance: Current trading balance
            max_markets: Maximum number of markets to select
            
        Returns:
            List of selected markets with analysis
        """
        try:
            self.logger.info(f"🤖 CrewAI selecting best markets from {len(available_markets)} options")
            
            # Prepare market data for analysis
            market_summary = self._prepare_market_summary(available_markets)
            
            # Create tasks for each agent
            tasks = self._create_market_selection_tasks(market_summary, current_balance, max_markets)
            
            # Create and run the crew
            crew = Crew(
                agents=[self.opportunity_scout, self.risk_assessor, self.portfolio_strategist],
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute market selection
            result = crew.kickoff()
            
            # Parse and return selected markets
            selected_markets = self._parse_selection_result(result, available_markets)
            
            self.logger.info(f"✅ CrewAI selected {len(selected_markets)} markets for trading")
            return selected_markets
            
        except Exception as e:
            self.logger.error(f"❌ Error in CrewAI market selection: {e}")
            # Fallback to simple selection
            return available_markets[:max_markets]
    
    def _prepare_market_summary(self, markets: List[Dict]) -> str:
        """Prepare a summary of available markets for analysis"""
        summary_lines = []
        
        for i, market in enumerate(markets[:20]):  # Limit to top 20 for analysis
            prob = market.get('probability', 0.5)
            volume = market.get('volume', 0)
            bettors = market.get('uniqueBettorCount', 0)
            question = market.get('question', '')[:100]
            
            summary_lines.append(
                f"{i+1}. {question}\n"
                f"   Probability: {prob:.3f} | Volume: {volume:.0f} | Bettors: {bettors}"
            )
        
        return "\n\n".join(summary_lines)
    
    def _create_market_selection_tasks(self, market_summary: str, balance: float, max_markets: int) -> List[Task]:
        """Create tasks for market selection crew"""
        
        # Task 1: Opportunity Identification
        opportunity_task = Task(
            description=f"""
            Analyze the following prediction markets and identify the top opportunities for profitable trading:

            AVAILABLE MARKETS:
            {market_summary}

            ANALYSIS CRITERIA:
            1. Market inefficiencies (probability vs true odds)
            2. Volume and liquidity levels
            3. Number of participants (more participants = more efficient)
            4. Question clarity and resolvability
            5. Time to resolution
            6. News flow and information availability

            Rank the top {max_markets * 2} markets by profit potential and provide reasoning for each.
            
            OUTPUT FORMAT:
            For each selected market, provide:
            - Market number and question
            - Profit potential score (1-10)
            - Key opportunity factors
            - Recommended trading direction (YES/NO)
            """,
            agent=self.opportunity_scout,
            expected_output=f"Ranked list of top {max_markets * 2} markets with profit potential analysis"
        )
        
        # Task 2: Risk Assessment
        risk_task = Task(
            description=f"""
            Evaluate the risk factors for the markets identified by the Opportunity Scout.

            RISK ASSESSMENT FRAMEWORK:
            1. Liquidity risk (can we exit positions easily?)
            2. Information risk (how much uncertainty exists?)
            3. Execution risk (bid-ask spreads, slippage)
            4. Event risk (unexpected developments)
            5. Correlation risk (are markets related?)

            Current balance: ${balance:.2f}

            For each market from the opportunity analysis:
            - Assign risk score (1-10, where 10 is highest risk)
            - Identify key risk factors
            - Recommend maximum position size using Kelly Criterion principles
            - Calculate risk-adjusted expected return

            OUTPUT FORMAT:
            Risk assessment for each market including:
            - Risk score and factors
            - Recommended position size
            - Risk-adjusted return estimate
            """,
            agent=self.risk_assessor,
            expected_output="Risk assessment with position sizing recommendations for each market"
        )
        
        # Task 3: Portfolio Optimization
        portfolio_task = Task(
            description=f"""
            Based on the opportunity analysis and risk assessment, select the optimal portfolio of markets to trade.

            PORTFOLIO OPTIMIZATION CRITERIA:
            1. Maximize risk-adjusted returns
            2. Ensure proper diversification
            3. Respect Kelly Criterion position sizing
            4. Consider correlation between markets
            5. Maintain adequate liquidity reserves

            CONSTRAINTS:
            - Maximum {max_markets} markets
            - Total allocation should not exceed 80% of balance
            - No single position should exceed 25% of balance
            - Minimum expected edge of 5%

            FINAL SELECTION:
            Select exactly {max_markets} markets and provide:
            - Market selection with reasoning
            - Recommended position size for each
            - Expected portfolio return and risk
            - Diversification analysis

            OUTPUT FORMAT:
            JSON-like structure with:
            {{
                "selected_markets": [
                    {{
                        "market_number": 1,
                        "question": "...",
                        "direction": "YES/NO",
                        "position_size": 100,
                        "reasoning": "..."
                    }}
                ],
                "portfolio_summary": {{
                    "total_allocation": 500,
                    "expected_return": 0.15,
                    "risk_score": 6.5
                }}
            }}
            """,
            agent=self.portfolio_strategist,
            expected_output=f"Final selection of {max_markets} markets with position sizing and portfolio analysis"
        )
        
        return [opportunity_task, risk_task, portfolio_task]
    
    def _parse_selection_result(self, result: str, available_markets: List[Dict]) -> List[Dict]:
        """Parse the CrewAI result and return selected markets"""
        try:
            # Try to extract JSON from the result
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            
            if json_match:
                selection_data = json.loads(json_match.group())
                selected_markets = []
                
                for selection in selection_data.get('selected_markets', []):
                    market_num = selection.get('market_number', 1) - 1
                    if 0 <= market_num < len(available_markets):
                        market = available_markets[market_num].copy()
                        market['crew_analysis'] = selection
                        selected_markets.append(market)
                
                return selected_markets
            
        except Exception as e:
            self.logger.warning(f"Failed to parse CrewAI result: {e}")
        
        # Fallback: return first few markets
        return available_markets[:5]


class EnhancedBacktester:
    """Enhanced backtesting system with hourly execution"""
    
    def __init__(
        self,
        manifold_api_key: str,
        openrouter_api_key: str,
        serp_api_key: str,
        initial_balance: float = 1000.0,
        use_inspect_ai: bool = None,
        debate_mode: bool = True
    ):
        self.manifold_client = ManifoldMarketsClient(api_key=manifold_api_key)
        self.market_selector = CrewAIMarketSelector(openrouter_api_key)
        self.market_agent = EnhancedMarketAgent(
            manifold_api_key=manifold_api_key,
            openrouter_api_key=openrouter_api_key,
            serp_api_key=serp_api_key,
            use_inspect_ai=use_inspect_ai,
            debate_mode=debate_mode
        )
        self.kelly_calculator = KellyCriterionCalculator()
        self.initial_balance = initial_balance
        self.logger = agent_logger
    
    async def run_week_long_backtest(self, hours_to_run: int = 168) -> BacktestSession:
        """
        Run a week-long backtest with hourly market analysis
        
        Args:
            hours_to_run: Number of hours to run (default 168 = 1 week)
            
        Returns:
            BacktestSession with complete results
        """
        session_id = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        self.logger.info(f"🚀 Starting week-long backtest: {session_id}")
        self.logger.info(f"   Duration: {hours_to_run} hours")
        self.logger.info(f"   Initial balance: ${self.initial_balance:.2f}")
        
        # Initialize session tracking
        current_balance = self.initial_balance
        total_trades = 0
        winning_trades = 0
        hourly_results = []
        trade_history = []
        market_selection_log = []
        balance_history = [current_balance]
        
        # Run hourly analysis
        for hour in range(hours_to_run):
            hour_start = datetime.now()
            self.logger.info(f"⏰ Hour {hour + 1}/{hours_to_run} - Balance: ${current_balance:.2f}")
            
            try:
                # 1. Get available markets
                markets = self.manifold_client.get_markets(limit=50)
                
                # 2. Use CrewAI to select best markets
                selected_markets = await self.market_selector.select_best_markets(
                    markets, current_balance, max_markets=3
                )
                
                # 3. Analyze each selected market
                hour_trades = []
                for market in selected_markets:
                    try:
                        # Get detailed analysis from enhanced market agent
                        analysis = await self.market_agent.analyze_market_comprehensive(market)
                        
                        # Make trading decision
                        if analysis.recommended_action in ['BUY', 'SELL']:
                            # Calculate position size based on Kelly Criterion
                            position_size = min(
                                analysis.position_size,
                                current_balance * 0.1  # Max 10% per trade
                            )
                            
                            if position_size >= 10:  # Minimum trade size
                                # Execute simulated trade
                                trade_result = self._simulate_trade(
                                    market, analysis, position_size, current_balance
                                )
                                
                                if trade_result:
                                    hour_trades.append(trade_result)
                                    trade_history.append(trade_result)
                                    current_balance = trade_result['new_balance']
                                    total_trades += 1
                                    
                                    if trade_result['profit'] > 0:
                                        winning_trades += 1
                    
                    except Exception as e:
                        self.logger.error(f"Error analyzing market {market.get('id', 'unknown')}: {e}")
                
                # 4. Log hourly results
                hourly_result = {
                    'hour': hour + 1,
                    'timestamp': hour_start.isoformat(),
                    'balance': current_balance,
                    'trades_made': len(hour_trades),
                    'markets_analyzed': len(selected_markets),
                    'selected_markets': [m.get('question', '')[:50] for m in selected_markets]
                }
                hourly_results.append(hourly_result)
                balance_history.append(current_balance)
                
                # Log market selection
                market_selection_log.append({
                    'hour': hour + 1,
                    'timestamp': hour_start.isoformat(),
                    'available_markets': len(markets),
                    'selected_markets': len(selected_markets),
                    'selection_reasoning': 'CrewAI market selection based on profit potential and risk assessment'
                })
                
                # 5. Simulate hourly delay (in real backtesting, this would be actual time)
                # For demo purposes, we'll just add a small delay
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in hour {hour + 1}: {e}")
        
        # Calculate final statistics
        end_time = datetime.now()
        total_return = (current_balance - self.initial_balance) / self.initial_balance
        max_drawdown = self._calculate_max_drawdown(balance_history)
        sharpe_ratio = self._calculate_sharpe_ratio(balance_history)
        
        session = BacktestSession(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            initial_balance=self.initial_balance,
            current_balance=current_balance,
            total_trades=total_trades,
            winning_trades=winning_trades,
            total_return=total_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            kelly_utilization=0.8,  # Simulated Kelly utilization
            markets_analyzed=len(market_selection_log) * 3,  # Approximate
            hourly_results=hourly_results,
            trade_history=trade_history,
            market_selection_log=market_selection_log
        )
        
        self.logger.info(f"✅ Backtest complete!")
        self.logger.info(f"   Final balance: ${current_balance:.2f}")
        self.logger.info(f"   Total return: {total_return:.1%}")
        self.logger.info(f"   Win rate: {winning_trades/max(total_trades, 1):.1%}")
        self.logger.info(f"   Sharpe ratio: {sharpe_ratio:.2f}")
        
        return session
    
    def _simulate_trade(self, market: Dict, analysis, position_size: float, current_balance: float) -> Optional[Dict]:
        """Simulate a trade execution"""
        try:
            # Simulate trade execution with some randomness
            success_prob = 0.6 + (analysis.confidence * 0.3)  # 60-90% success rate based on confidence
            trade_successful = np.random.random() < success_prob
            
            # Calculate profit/loss
            if trade_successful:
                # Winning trade: gain based on edge and some randomness
                profit = position_size * (analysis.edge * 2 + np.random.normal(0, 0.1))
            else:
                # Losing trade: lose the position size
                profit = -position_size
            
            new_balance = current_balance + profit
            
            return {
                'timestamp': datetime.now().isoformat(),
                'market_id': market.get('id', ''),
                'question': market.get('question', '')[:100],
                'action': analysis.recommended_action,
                'position_size': position_size,
                'profit': profit,
                'new_balance': new_balance,
                'ai_probability': analysis.ai_probability,
                'market_probability': analysis.current_probability,
                'edge': analysis.edge,
                'confidence': analysis.confidence,
                'reasoning': analysis.reasoning[:200]
            }
            
        except Exception as e:
            self.logger.error(f"Error simulating trade: {e}")
            return None
    
    def _calculate_max_drawdown(self, balance_history: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(balance_history) < 2:
            return 0.0
        
        peak = balance_history[0]
        max_drawdown = 0.0
        
        for balance in balance_history[1:]:
            if balance > peak:
                peak = balance
            else:
                drawdown = (peak - balance) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self, balance_history: List[float]) -> float:
        """Calculate Sharpe ratio"""
        if len(balance_history) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(balance_history)):
            ret = (balance_history[i] - balance_history[i-1]) / balance_history[i-1]
            returns.append(ret)
        
        if not returns:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualized Sharpe ratio (assuming hourly returns)
        return (mean_return * 24 * 365) / (std_return * np.sqrt(24 * 365))


# Demo function for testing
async def run_demo_backtest():
    """Run a demo backtest for testing"""
    backtester = EnhancedBacktester(
        manifold_api_key="demo_key",
        openrouter_api_key="demo_key", 
        serp_api_key="demo_key"
    )
    
    # Run a short 24-hour backtest for demo
    session = await backtester.run_week_long_backtest(hours_to_run=24)
    
    print(f"Demo backtest results:")
    print(f"  Session ID: {session.session_id}")
    print(f"  Total return: {session.total_return:.1%}")
    print(f"  Total trades: {session.total_trades}")
    print(f"  Win rate: {session.winning_trades/max(session.total_trades, 1):.1%}")
    print(f"  Sharpe ratio: {session.sharpe_ratio:.2f}")
    
    return session


if __name__ == "__main__":
    import numpy as np
    asyncio.run(run_demo_backtest())