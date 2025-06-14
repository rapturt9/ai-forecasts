"""
Enhanced Market Agent with Advanced Trading Strategies
Implements sophisticated prompting and algorithmic trading techniques
"""

import json
import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np
from pathlib import Path

from .client import ManifoldMarketsClient
from .kelly_criterion import KellyCriterionCalculator, KellyBet
from .historical_data import ManifoldHistoricalDataManager
import sys
sys.path.append(str(Path(__file__).parent.parent))
from ai_forecasts.agents.google_news_superforecaster import GoogleNewsSuperforecaster

logger = logging.getLogger(__name__)


@dataclass
class MarketAnalysis:
    """Comprehensive market analysis result"""
    market_id: str
    question: str
    current_probability: float
    ai_probability: float
    confidence: float
    edge: float
    sentiment_score: float
    arbitrage_opportunities: List[Dict]
    technical_indicators: Dict[str, float]
    order_book_analysis: Dict[str, Any]
    liquidity_assessment: Dict[str, float]
    risk_factors: List[str]
    trading_signals: List[Dict]
    reasoning: str
    recommended_action: str
    position_size: float
    expected_value: float
    time_horizon: str


@dataclass
class TradingDecision:
    """Structured trading decision with full reasoning"""
    market_id: str
    action: str  # 'BUY', 'SELL', 'HOLD', 'ARBITRAGE'
    outcome: str  # 'YES', 'NO'
    amount: float
    confidence: float
    strategy_type: str  # 'arbitrage', 'momentum', 'mean_reversion', 'sentiment', 'kelly_optimal'
    reasoning: str
    risk_assessment: str
    expected_return: float
    time_sensitivity: str
    market_conditions: Dict[str, Any]
    supporting_evidence: List[str]
    contrarian_factors: List[str]


class EnhancedMarketAgent:
    """
    Advanced market agent implementing sophisticated trading strategies
    Based on optimal LLM prediction market strategies
    """
    
    def __init__(
        self,
        manifold_api_key: str,
        openrouter_api_key: str,
        serp_api_key: str,
        max_kelly_fraction: float = 0.25,
        min_edge: float = 0.03,
        risk_tolerance: str = "moderate",
        use_inspect_ai: bool = None,
        debate_mode: bool = True
    ):
        """
        Initialize enhanced market agent
        
        Args:
            manifold_api_key: Manifold Markets API key
            openrouter_api_key: OpenRouter API key
            serp_api_key: SERP API key for news
            max_kelly_fraction: Maximum Kelly fraction
            min_edge: Minimum edge required
            risk_tolerance: 'conservative', 'moderate', 'aggressive'
        """
        self.manifold_client = ManifoldMarketsClient(api_key=manifold_api_key)
        self.kelly_calculator = KellyCriterionCalculator(max_kelly_fraction, min_edge)
        self.historical_data = ManifoldHistoricalDataManager()
        self.forecaster = GoogleNewsSuperforecaster(
            openrouter_api_key=openrouter_api_key,
            serp_api_key=serp_api_key,
            use_inspect_ai=use_inspect_ai,
            debate_mode=debate_mode
        )
        
        self.risk_tolerance = risk_tolerance
        self.active_positions = {}
        self.market_cache = {}
        self.sentiment_cache = {}
        
        # Strategy weights based on risk tolerance
        self.strategy_weights = self._get_strategy_weights(risk_tolerance)
        
    def _get_strategy_weights(self, risk_tolerance: str) -> Dict[str, float]:
        """Get strategy weights based on risk tolerance"""
        if risk_tolerance == "conservative":
            return {
                "arbitrage": 0.4,
                "mean_reversion": 0.3,
                "sentiment": 0.2,
                "momentum": 0.1
            }
        elif risk_tolerance == "aggressive":
            return {
                "momentum": 0.35,
                "sentiment": 0.3,
                "arbitrage": 0.2,
                "mean_reversion": 0.15
            }
        else:  # moderate
            return {
                "arbitrage": 0.3,
                "sentiment": 0.25,
                "mean_reversion": 0.25,
                "momentum": 0.2
            }
    
    async def analyze_market_comprehensive(self, market: Dict) -> MarketAnalysis:
        """
        Perform comprehensive market analysis using multiple strategies
        
        Args:
            market: Market data from Manifold API
            
        Returns:
            Comprehensive MarketAnalysis object
        """
        try:
            market_id = market.get('id', '')
            question = market.get('question', '')
            current_prob = market.get('probability', 0.5)
            
            logger.info(f"Analyzing market: {question[:60]}...")
            
            # 1. AI Prediction with enhanced prompting
            ai_analysis = await self._get_enhanced_ai_prediction(market)
            
            # 2. Sentiment Analysis
            sentiment_analysis = await self._analyze_market_sentiment(market)
            
            # 3. Technical Analysis
            technical_indicators = await self._calculate_technical_indicators(market)
            
            # 4. Arbitrage Detection
            arbitrage_opportunities = await self._detect_arbitrage_opportunities(market)
            
            # 5. Order Book Analysis
            order_book_analysis = await self._analyze_order_book(market)
            
            # 6. Liquidity Assessment
            liquidity_assessment = self._assess_market_liquidity(market)
            
            # 7. Risk Factor Analysis
            risk_factors = await self._identify_risk_factors(market)
            
            # 8. Generate Trading Signals
            trading_signals = self._generate_trading_signals(
                ai_analysis, sentiment_analysis, technical_indicators, arbitrage_opportunities
            )
            
            # 9. Calculate edge and position sizing
            ai_prob = ai_analysis.get('probability', current_prob)
            edge = abs(ai_prob - current_prob)
            confidence = ai_analysis.get('confidence', 0.5)
            
            # 10. Kelly Criterion position sizing
            kelly_fraction = self.kelly_calculator.calculate_kelly_fraction(
                ai_prob, current_prob, "YES" if ai_prob > current_prob else "NO"
            )
            
            # 11. Determine recommended action
            recommended_action, reasoning = self._determine_recommended_action(
                trading_signals, edge, confidence, kelly_fraction
            )
            
            # 12. Calculate expected value
            position_size = kelly_fraction * 1000  # Assuming 1000 mana balance
            expected_value = self.kelly_calculator.calculate_expected_value(
                ai_prob, current_prob, position_size, "YES" if ai_prob > current_prob else "NO"
            )
            
            return MarketAnalysis(
                market_id=market_id,
                question=question,
                current_probability=current_prob,
                ai_probability=ai_prob,
                confidence=confidence,
                edge=edge,
                sentiment_score=sentiment_analysis.get('score', 0),
                arbitrage_opportunities=arbitrage_opportunities,
                technical_indicators=technical_indicators,
                order_book_analysis=order_book_analysis,
                liquidity_assessment=liquidity_assessment,
                risk_factors=risk_factors,
                trading_signals=trading_signals,
                reasoning=reasoning,
                recommended_action=recommended_action,
                position_size=position_size,
                expected_value=expected_value,
                time_horizon=self._determine_time_horizon(market)
            )
            
        except Exception as e:
            logger.error(f"Error in comprehensive market analysis: {e}")
            raise
    
    async def _get_enhanced_ai_prediction(self, market: Dict) -> Dict:
        """
        Get AI prediction with enhanced prompting strategies
        """
        try:
            question = market.get('question', '')
            current_prob = market.get('probability', 0.5)
            volume = market.get('volume', 0)
            unique_bettors = market.get('uniqueBettorCount', 0)
            
            # Enhanced prompt incorporating multiple strategies
            enhanced_prompt = f"""
            You are an expert prediction market analyst with access to advanced trading strategies.
            
            MARKET ANALYSIS REQUEST:
            Question: {question}
            Current Market Probability: {current_prob:.3f}
            Volume: {volume} mana
            Unique Bettors: {unique_bettors}
            
            ANALYSIS FRAMEWORK:
            Apply these sophisticated strategies in your analysis:
            
            1. ARBITRAGE DETECTION:
            - Look for logical inconsistencies in the market pricing
            - Consider related markets that might create arbitrage opportunities
            - Identify statistical arbitrage based on historical patterns
            
            2. SENTIMENT ANALYSIS:
            - Analyze the question for emotional or trending topics
            - Consider public opinion momentum and social media influence
            - Evaluate news cycle impact and timing
            
            3. MEAN REVERSION ANALYSIS:
            - Assess if current probability deviates from historical norms
            - Consider if market has overreacted to recent events
            - Evaluate fundamental value vs current pricing
            
            4. MOMENTUM ANALYSIS:
            - Identify if there's sustained directional movement
            - Consider volume and participation trends
            - Evaluate if momentum is likely to continue
            
            5. MARKET MICROSTRUCTURE:
            - Assess liquidity and bid-ask dynamics
            - Consider order flow and informed vs uninformed trading
            - Evaluate market depth and potential price impact
            
            6. RISK ASSESSMENT:
            - Identify key risk factors and uncertainty sources
            - Consider tail risks and black swan events
            - Evaluate information asymmetries
            
            REQUIRED OUTPUT FORMAT:
            {{
                "probability": <your probability estimate 0-1>,
                "confidence": <confidence level 0-1>,
                "primary_strategy": "<arbitrage|sentiment|mean_reversion|momentum>",
                "reasoning": "<detailed reasoning incorporating multiple strategies>",
                "risk_factors": ["<factor1>", "<factor2>", ...],
                "supporting_evidence": ["<evidence1>", "<evidence2>", ...],
                "contrarian_view": "<what could make you wrong>",
                "time_sensitivity": "<high|medium|low>",
                "edge_assessment": "<strong|moderate|weak|none>"
            }}
            
            Focus on mathematical rigor and avoid cognitive biases. Consider both bullish and bearish scenarios.
            """
            
            # Use the forecaster to get prediction
            prediction = await self.forecaster.forecast_market(
                question=question,
                background="",
                freeze_datetime=datetime.now(),
                enhanced_prompt=enhanced_prompt
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error getting enhanced AI prediction: {e}")
            return {"probability": 0.5, "confidence": 0.3, "reasoning": "Error in analysis"}
    
    async def _analyze_market_sentiment(self, market: Dict) -> Dict:
        """Analyze market sentiment using NLP"""
        try:
            question = market.get('question', '')
            
            # Simple sentiment analysis based on keywords
            positive_keywords = ['will', 'success', 'win', 'achieve', 'increase', 'grow', 'improve']
            negative_keywords = ['fail', 'lose', 'decrease', 'decline', 'crash', 'crisis']
            
            question_lower = question.lower()
            positive_score = sum(1 for word in positive_keywords if word in question_lower)
            negative_score = sum(1 for word in negative_keywords if word in question_lower)
            
            # Normalize sentiment score
            total_words = len(question.split())
            sentiment_score = (positive_score - negative_score) / max(total_words, 1)
            
            return {
                'score': sentiment_score,
                'positive_signals': positive_score,
                'negative_signals': negative_score,
                'analysis': f"Sentiment analysis: {sentiment_score:.3f} (positive: {positive_score}, negative: {negative_score})"
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {'score': 0, 'analysis': 'Error in sentiment analysis'}
    
    async def _calculate_technical_indicators(self, market: Dict) -> Dict[str, float]:
        """Calculate technical indicators for the market"""
        try:
            # For now, return simulated technical indicators
            # In production, you'd calculate these from historical price data
            current_prob = market.get('probability', 0.5)
            volume = market.get('volume', 0)
            
            return {
                'rsi': 50.0 + (current_prob - 0.5) * 100,  # Simulated RSI
                'momentum': (current_prob - 0.5) * 2,  # Simulated momentum
                'volume_trend': min(volume / 1000, 1.0),  # Volume as trend indicator
                'volatility': abs(current_prob - 0.5) * 2,  # Simulated volatility
                'support_level': max(0.1, current_prob - 0.2),
                'resistance_level': min(0.9, current_prob + 0.2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {}
    
    async def _detect_arbitrage_opportunities(self, market: Dict) -> List[Dict]:
        """Detect arbitrage opportunities"""
        try:
            # Simple arbitrage detection
            current_prob = market.get('probability', 0.5)
            opportunities = []
            
            # Check for obvious mispricing
            if current_prob < 0.05:
                opportunities.append({
                    'type': 'undervalued',
                    'description': 'Market probability extremely low, potential value bet',
                    'confidence': 0.7
                })
            elif current_prob > 0.95:
                opportunities.append({
                    'type': 'overvalued', 
                    'description': 'Market probability extremely high, potential contrarian bet',
                    'confidence': 0.7
                })
            
            # Check for round number bias
            if abs(current_prob - 0.5) < 0.01:
                opportunities.append({
                    'type': 'round_number_bias',
                    'description': 'Probability close to 50%, may indicate uncertainty rather than true odds',
                    'confidence': 0.4
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error detecting arbitrage: {e}")
            return []
    
    async def _analyze_order_book(self, market: Dict) -> Dict[str, Any]:
        """Analyze order book dynamics"""
        try:
            # Simulated order book analysis
            current_prob = market.get('probability', 0.5)
            volume = market.get('volume', 0)
            
            return {
                'bid_ask_spread': 0.02,  # Simulated 2% spread
                'market_depth': min(volume / 100, 10),  # Simulated depth
                'order_imbalance': (current_prob - 0.5) * 0.1,  # Simulated imbalance
                'liquidity_score': min(volume / 1000, 1.0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing order book: {e}")
            return {}
    
    def _assess_market_liquidity(self, market: Dict) -> Dict[str, float]:
        """Assess market liquidity"""
        try:
            volume = market.get('volume', 0)
            unique_bettors = market.get('uniqueBettorCount', 0)
            
            # Liquidity scoring
            volume_score = min(volume / 1000, 1.0)  # Normalize to 0-1
            participation_score = min(unique_bettors / 50, 1.0)  # Normalize to 0-1
            
            overall_liquidity = (volume_score + participation_score) / 2
            
            return {
                'volume_score': volume_score,
                'participation_score': participation_score,
                'overall_liquidity': overall_liquidity,
                'liquidity_tier': 'high' if overall_liquidity > 0.7 else 'medium' if overall_liquidity > 0.3 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error assessing liquidity: {e}")
            return {'overall_liquidity': 0.5}
    
    async def _identify_risk_factors(self, market: Dict) -> List[str]:
        """Identify key risk factors"""
        try:
            risk_factors = []
            
            volume = market.get('volume', 0)
            unique_bettors = market.get('uniqueBettorCount', 0)
            current_prob = market.get('probability', 0.5)
            
            # Low liquidity risk
            if volume < 100:
                risk_factors.append("Low volume - high price impact risk")
            
            # Low participation risk
            if unique_bettors < 5:
                risk_factors.append("Few participants - potential manipulation risk")
            
            # Extreme probability risk
            if current_prob < 0.1 or current_prob > 0.9:
                risk_factors.append("Extreme probability - limited upside potential")
            
            # Time risk (if close time available)
            close_time = market.get('closeTime')
            if close_time:
                close_dt = datetime.fromtimestamp(close_time / 1000)
                time_to_close = (close_dt - datetime.now()).days
                if time_to_close < 7:
                    risk_factors.append("Short time to resolution - high time decay risk")
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Error identifying risk factors: {e}")
            return ["Error in risk assessment"]
    
    def _generate_trading_signals(
        self,
        ai_analysis: Dict,
        sentiment_analysis: Dict,
        technical_indicators: Dict,
        arbitrage_opportunities: List[Dict]
    ) -> List[Dict]:
        """Generate trading signals from multiple analyses"""
        try:
            signals = []
            
            # AI prediction signal
            ai_prob = ai_analysis.get('probability', 0.5)
            confidence = ai_analysis.get('confidence', 0.5)
            
            if confidence > 0.7:
                signals.append({
                    'type': 'ai_prediction',
                    'strength': confidence,
                    'direction': 'bullish' if ai_prob > 0.5 else 'bearish',
                    'reasoning': f"High confidence AI prediction: {ai_prob:.3f}"
                })
            
            # Sentiment signal
            sentiment_score = sentiment_analysis.get('score', 0)
            if abs(sentiment_score) > 0.1:
                signals.append({
                    'type': 'sentiment',
                    'strength': abs(sentiment_score),
                    'direction': 'bullish' if sentiment_score > 0 else 'bearish',
                    'reasoning': f"Sentiment analysis: {sentiment_score:.3f}"
                })
            
            # Technical signals
            if technical_indicators:
                rsi = technical_indicators.get('rsi', 50)
                if rsi > 70:
                    signals.append({
                        'type': 'technical_overbought',
                        'strength': (rsi - 70) / 30,
                        'direction': 'bearish',
                        'reasoning': f"RSI overbought: {rsi:.1f}"
                    })
                elif rsi < 30:
                    signals.append({
                        'type': 'technical_oversold',
                        'strength': (30 - rsi) / 30,
                        'direction': 'bullish',
                        'reasoning': f"RSI oversold: {rsi:.1f}"
                    })
            
            # Arbitrage signals
            for opportunity in arbitrage_opportunities:
                signals.append({
                    'type': 'arbitrage',
                    'strength': opportunity.get('confidence', 0.5),
                    'direction': 'bullish' if opportunity['type'] == 'undervalued' else 'bearish',
                    'reasoning': opportunity['description']
                })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return []
    
    def _determine_recommended_action(
        self,
        trading_signals: List[Dict],
        edge: float,
        confidence: float,
        kelly_fraction: float
    ) -> Tuple[str, str]:
        """Determine recommended action based on all analyses"""
        try:
            if not trading_signals or edge < self.kelly_calculator.min_edge:
                return "HOLD", "Insufficient edge or signals for trading"
            
            # Weight signals by strategy preferences
            bullish_strength = 0
            bearish_strength = 0
            
            for signal in trading_signals:
                strength = signal['strength'] * self.strategy_weights.get(signal['type'], 0.1)
                if signal['direction'] == 'bullish':
                    bullish_strength += strength
                else:
                    bearish_strength += strength
            
            net_strength = bullish_strength - bearish_strength
            
            # Decision logic
            if abs(net_strength) < 0.1:
                action = "HOLD"
                reasoning = f"Conflicting signals (bullish: {bullish_strength:.3f}, bearish: {bearish_strength:.3f})"
            elif net_strength > 0:
                action = "BUY_YES"
                reasoning = f"Strong bullish signals (net strength: {net_strength:.3f}, Kelly: {kelly_fraction:.3f})"
            else:
                action = "BUY_NO"
                reasoning = f"Strong bearish signals (net strength: {net_strength:.3f}, Kelly: {kelly_fraction:.3f})"
            
            # Add confidence and edge to reasoning
            reasoning += f" | Edge: {edge:.3f}, Confidence: {confidence:.3f}"
            
            return action, reasoning
            
        except Exception as e:
            logger.error(f"Error determining recommended action: {e}")
            return "HOLD", "Error in decision analysis"
    
    def _determine_time_horizon(self, market: Dict) -> str:
        """Determine appropriate time horizon for the trade"""
        try:
            close_time = market.get('closeTime')
            if not close_time:
                return "unknown"
            
            close_dt = datetime.fromtimestamp(close_time / 1000)
            time_to_close = (close_dt - datetime.now()).days
            
            if time_to_close < 7:
                return "short_term"
            elif time_to_close < 30:
                return "medium_term"
            else:
                return "long_term"
                
        except Exception as e:
            logger.error(f"Error determining time horizon: {e}")
            return "unknown"
    
    async def make_trading_decision(self, market: Dict) -> TradingDecision:
        """
        Make a comprehensive trading decision for a market
        
        Args:
            market: Market data from Manifold API
            
        Returns:
            TradingDecision with full reasoning and analysis
        """
        try:
            # Perform comprehensive analysis
            analysis = await self.analyze_market_comprehensive(market)
            
            # Determine position size using Kelly Criterion
            kelly_fraction = self.kelly_calculator.calculate_kelly_fraction(
                analysis.ai_probability,
                analysis.current_probability,
                "YES" if analysis.ai_probability > analysis.current_probability else "NO"
            )
            
            # Create trading decision
            decision = TradingDecision(
                market_id=analysis.market_id,
                action=analysis.recommended_action,
                outcome="YES" if analysis.ai_probability > analysis.current_probability else "NO",
                amount=analysis.position_size,
                confidence=analysis.confidence,
                strategy_type=self._determine_primary_strategy(analysis.trading_signals),
                reasoning=analysis.reasoning,
                risk_assessment="; ".join(analysis.risk_factors),
                expected_return=analysis.expected_value,
                time_sensitivity=self._assess_time_sensitivity(analysis.trading_signals),
                market_conditions={
                    'liquidity': analysis.liquidity_assessment,
                    'volatility': analysis.technical_indicators.get('volatility', 0),
                    'sentiment': analysis.sentiment_score
                },
                supporting_evidence=[signal['reasoning'] for signal in analysis.trading_signals if signal['direction'] == ('bullish' if analysis.ai_probability > analysis.current_probability else 'bearish')],
                contrarian_factors=[signal['reasoning'] for signal in analysis.trading_signals if signal['direction'] != ('bullish' if analysis.ai_probability > analysis.current_probability else 'bearish')]
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Error making trading decision: {e}")
            raise
    
    def _determine_primary_strategy(self, trading_signals: List[Dict]) -> str:
        """Determine the primary strategy based on strongest signal"""
        if not trading_signals:
            return "hold"
        
        strongest_signal = max(trading_signals, key=lambda x: x['strength'])
        return strongest_signal['type']
    
    def _assess_time_sensitivity(self, trading_signals: List[Dict]) -> str:
        """Assess time sensitivity of the trading opportunity"""
        arbitrage_signals = [s for s in trading_signals if s['type'] == 'arbitrage']
        if arbitrage_signals:
            return "high"
        
        momentum_signals = [s for s in trading_signals if 'momentum' in s['type']]
        if momentum_signals:
            return "medium"
        
        return "low"