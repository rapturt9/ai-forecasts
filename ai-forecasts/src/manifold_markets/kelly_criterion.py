"""
Kelly Criterion implementation for optimal betting on Manifold Markets
Calculates optimal bet sizes to maximize long-term growth
"""

import math
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class KellyBet:
    """Represents an optimal bet calculated using Kelly Criterion"""
    market_id: str
    question: str
    outcome: str  # "YES" or "NO"
    kelly_fraction: float  # Fraction of bankroll to bet
    bet_amount: float  # Actual amount to bet
    market_probability: float  # Current market probability
    ai_probability: float  # AI's estimated probability
    expected_value: float  # Expected value of the bet
    confidence: float  # AI confidence level
    reasoning: str  # Why this bet is recommended


class KellyCriterionCalculator:
    """
    Implements Kelly Criterion for optimal betting on prediction markets
    
    Kelly Formula: f* = (bp - q) / b
    Where:
    - f* = fraction of bankroll to bet
    - b = odds received on the wager (payout ratio - 1)
    - p = probability of winning
    - q = probability of losing (1 - p)
    """
    
    def __init__(self, max_kelly_fraction: float = 0.25, min_edge: float = 0.05):
        """
        Initialize Kelly Calculator
        
        Args:
            max_kelly_fraction: Maximum fraction of bankroll to bet (safety cap)
            min_edge: Minimum edge required to place a bet
        """
        self.max_kelly_fraction = max_kelly_fraction
        self.min_edge = min_edge
    
    def calculate_kelly_fraction(
        self,
        ai_probability: float,
        market_probability: float,
        outcome: str = "YES"
    ) -> float:
        """
        Calculate optimal Kelly fraction for a bet
        
        Args:
            ai_probability: AI's estimated probability of YES outcome
            market_probability: Current market probability
            outcome: "YES" or "NO"
            
        Returns:
            Optimal fraction of bankroll to bet (0 if no bet recommended)
        """
        try:
            # Adjust probabilities based on outcome
            if outcome == "YES":
                p = ai_probability  # Probability of winning
                market_p = market_probability
            else:
                p = 1 - ai_probability  # Probability of winning (betting NO)
                market_p = 1 - market_probability
            
            q = 1 - p  # Probability of losing
            
            # Calculate odds (payout ratio - 1)
            # On Manifold, if you bet on outcome with probability market_p,
            # you get paid 1/market_p if you win
            if market_p <= 0 or market_p >= 1:
                return 0.0
                
            b = (1 / market_p) - 1  # Odds received
            
            # Kelly formula: f* = (bp - q) / b
            kelly_fraction = (b * p - q) / b
            
            # Apply safety constraints
            kelly_fraction = max(0, kelly_fraction)  # Never bet negative
            kelly_fraction = min(kelly_fraction, self.max_kelly_fraction)  # Cap at max
            
            # Check minimum edge requirement
            edge = p - market_p
            if abs(edge) < self.min_edge:
                return 0.0
                
            return kelly_fraction
            
        except Exception as e:
            logger.error(f"Error calculating Kelly fraction: {e}")
            return 0.0
    
    def calculate_expected_value(
        self,
        ai_probability: float,
        market_probability: float,
        bet_amount: float,
        outcome: str = "YES"
    ) -> float:
        """
        Calculate expected value of a bet
        
        Args:
            ai_probability: AI's estimated probability
            market_probability: Current market probability
            bet_amount: Amount to bet
            outcome: "YES" or "NO"
            
        Returns:
            Expected value of the bet
        """
        try:
            if outcome == "YES":
                p_win = ai_probability
                market_p = market_probability
            else:
                p_win = 1 - ai_probability
                market_p = 1 - market_probability
            
            if market_p <= 0 or market_p >= 1:
                return 0.0
            
            # Payout if win (including original bet)
            payout_if_win = bet_amount / market_p
            
            # Expected value = (probability of win * payout) - bet_amount
            expected_value = (p_win * payout_if_win) - bet_amount
            
            return expected_value
            
        except Exception as e:
            logger.error(f"Error calculating expected value: {e}")
            return 0.0
    
    def recommend_bets(
        self,
        markets_with_predictions: List[Dict],
        current_balance: float,
        max_simultaneous_bets: int = 5,
        min_bet_amount: float = 1.0,
        max_bet_amount: float = 100.0
    ) -> List[KellyBet]:
        """
        Recommend optimal bets using Kelly Criterion
        
        Args:
            markets_with_predictions: List of markets with AI predictions
            current_balance: Current bankroll
            max_simultaneous_bets: Maximum number of simultaneous bets
            min_bet_amount: Minimum bet amount
            max_bet_amount: Maximum bet amount per market
            
        Returns:
            List of recommended Kelly bets, sorted by expected value
        """
        recommended_bets = []
        
        for market_data in markets_with_predictions:
            try:
                market = market_data.get('market', {})
                prediction = market_data.get('prediction', {})
                
                market_id = market.get('id', '')
                question = market.get('question', '')
                market_probability = market.get('probability', 0.5)
                ai_probability = prediction.get('probability', 0.5)
                confidence = prediction.get('confidence', 0.5)
                reasoning = prediction.get('reasoning', '')
                
                # Calculate Kelly fractions for both YES and NO
                for outcome in ["YES", "NO"]:
                    kelly_fraction = self.calculate_kelly_fraction(
                        ai_probability, market_probability, outcome
                    )
                    
                    if kelly_fraction > 0:
                        # Calculate bet amount
                        bet_amount = kelly_fraction * current_balance
                        bet_amount = max(min_bet_amount, min(bet_amount, max_bet_amount))
                        
                        # Calculate expected value
                        expected_value = self.calculate_expected_value(
                            ai_probability, market_probability, bet_amount, outcome
                        )
                        
                        if expected_value > 0:
                            kelly_bet = KellyBet(
                                market_id=market_id,
                                question=question,
                                outcome=outcome,
                                kelly_fraction=kelly_fraction,
                                bet_amount=bet_amount,
                                market_probability=market_probability,
                                ai_probability=ai_probability,
                                expected_value=expected_value,
                                confidence=confidence,
                                reasoning=f"{outcome} bet: {reasoning}"
                            )
                            recommended_bets.append(kelly_bet)
                            
            except Exception as e:
                logger.error(f"Error processing market for Kelly recommendation: {e}")
                continue
        
        # Sort by expected value (descending) and limit to max simultaneous bets
        recommended_bets.sort(key=lambda x: x.expected_value, reverse=True)
        return recommended_bets[:max_simultaneous_bets]
    
    def calculate_portfolio_kelly(
        self,
        current_positions: List[Dict],
        new_opportunities: List[Dict],
        current_balance: float
    ) -> Dict:
        """
        Calculate optimal portfolio allocation considering existing positions
        
        Args:
            current_positions: List of current market positions
            new_opportunities: List of new betting opportunities
            current_balance: Available balance
            
        Returns:
            Portfolio allocation recommendations
        """
        try:
            total_portfolio_value = current_balance
            
            # Add value of current positions
            for position in current_positions:
                total_portfolio_value += position.get('payout', 0)
            
            # Calculate risk-adjusted Kelly fractions
            portfolio_allocation = {
                'total_value': total_portfolio_value,
                'available_balance': current_balance,
                'recommended_bets': [],
                'risk_metrics': {
                    'portfolio_concentration': 0.0,
                    'expected_return': 0.0,
                    'risk_level': 'low'
                }
            }
            
            # Get Kelly recommendations
            kelly_bets = self.recommend_bets(new_opportunities, current_balance)
            
            # Adjust for portfolio concentration
            total_recommended_amount = sum(bet.bet_amount for bet in kelly_bets)
            if total_recommended_amount > current_balance * 0.8:  # Don't bet more than 80% of balance
                scale_factor = (current_balance * 0.8) / total_recommended_amount
                for bet in kelly_bets:
                    bet.bet_amount *= scale_factor
                    bet.kelly_fraction *= scale_factor
            
            portfolio_allocation['recommended_bets'] = kelly_bets
            
            # Calculate risk metrics
            if kelly_bets:
                portfolio_allocation['risk_metrics']['expected_return'] = sum(
                    bet.expected_value for bet in kelly_bets
                )
                portfolio_allocation['risk_metrics']['portfolio_concentration'] = (
                    total_recommended_amount / current_balance
                )
                
                # Determine risk level
                if portfolio_allocation['risk_metrics']['portfolio_concentration'] > 0.5:
                    portfolio_allocation['risk_metrics']['risk_level'] = 'high'
                elif portfolio_allocation['risk_metrics']['portfolio_concentration'] > 0.3:
                    portfolio_allocation['risk_metrics']['risk_level'] = 'medium'
                else:
                    portfolio_allocation['risk_metrics']['risk_level'] = 'low'
            
            return portfolio_allocation
            
        except Exception as e:
            logger.error(f"Error calculating portfolio Kelly: {e}")
            return {
                'total_value': current_balance,
                'available_balance': current_balance,
                'recommended_bets': [],
                'risk_metrics': {'error': str(e)}
            }


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
    """
    Calculate Sharpe ratio for a series of returns
    
    Args:
        returns: List of returns
        risk_free_rate: Risk-free rate (default 0 for Manifold)
        
    Returns:
        Sharpe ratio
    """
    if not returns or len(returns) < 2:
        return 0.0
    
    try:
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return 0.0
        
        return (mean_return - risk_free_rate) / std_dev
        
    except Exception:
        return 0.0


def calculate_maximum_drawdown(portfolio_values: List[float]) -> float:
    """
    Calculate maximum drawdown from portfolio values
    
    Args:
        portfolio_values: List of portfolio values over time
        
    Returns:
        Maximum drawdown as a fraction
    """
    if not portfolio_values or len(portfolio_values) < 2:
        return 0.0
    
    try:
        peak = portfolio_values[0]
        max_drawdown = 0.0
        
        for value in portfolio_values[1:]:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
        
    except Exception:
        return 0.0