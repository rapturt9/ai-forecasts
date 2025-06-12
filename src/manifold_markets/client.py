"""
Manifold Markets API Client
Provides interface to interact with Manifold Markets API for fetching markets and placing bets
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ManifoldMarketsClient:
    """Client for interacting with Manifold Markets API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Manifold Markets client
        
        Args:
            api_key: Manifold API key. If not provided, will try to get from environment
        """
        self.api_key = api_key or os.getenv("MANIFOLD_API_KEY")
        self.base_url = "https://api.manifold.markets/v0"
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Key {self.api_key}",
                "Content-Type": "application/json"
            })
    
    def get_markets(self, limit: int = 100, before: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of markets from Manifold
        
        Args:
            limit: Number of markets to fetch (max 1000)
            before: Get markets before this ID (for pagination)
            
        Returns:
            List of market dictionaries
        """
        try:
            params = {"limit": limit}
            if before:
                params["before"] = before
                
            response = self.session.get(f"{self.base_url}/markets", params=params)
            response.raise_for_status()
            
            markets = response.json()
            logger.info(f"Fetched {len(markets)} markets from Manifold")
            return markets
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching markets: {e}")
            raise
    
    def get_market(self, market_id: str) -> Dict[str, Any]:
        """
        Get specific market details
        
        Args:
            market_id: The market ID
            
        Returns:
            Market dictionary
        """
        try:
            response = self.session.get(f"{self.base_url}/market/{market_id}")
            response.raise_for_status()
            
            market = response.json()
            logger.info(f"Fetched market: {market.get('question', 'Unknown')}")
            return market
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            raise
    
    def search_markets(self, term: str, limit: int = 25, filter: str = "all") -> List[Dict[str, Any]]:
        """
        Search for markets by term
        
        Args:
            term: Search term
            limit: Number of results (max 100)
            filter: Filter type ("all", "open", "closed", "resolved")
            
        Returns:
            List of matching markets
        """
        try:
            params = {
                "term": term,
                "limit": limit,
                "filter": filter
            }
            
            response = self.session.get(f"{self.base_url}/search-markets", params=params)
            response.raise_for_status()
            
            markets = response.json()
            logger.info(f"Found {len(markets)} markets matching '{term}'")
            return markets
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching markets for '{term}': {e}")
            raise
    
    def place_bet(self, contract_id: str, amount: float, outcome: str) -> Dict[str, Any]:
        """
        Place a bet on a market
        
        Args:
            contract_id: The market/contract ID
            amount: Amount to bet (in Mana)
            outcome: "YES" or "NO" for binary markets
            
        Returns:
            Bet confirmation
        """
        if not self.api_key:
            raise ValueError("API key required to place bets")
            
        try:
            data = {
                "contractId": contract_id,
                "amount": amount,
                "outcome": outcome
            }
            
            response = self.session.post(f"{self.base_url}/bet", json=data)
            response.raise_for_status()
            
            bet_result = response.json()
            logger.info(f"Placed {outcome} bet of {amount} on {contract_id}")
            return bet_result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error placing bet: {e}")
            raise
    
    def get_user_bets(self, username: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get user's bets
        
        Args:
            username: Username to get bets for (if None, gets current user's bets)
            limit: Number of bets to fetch
            
        Returns:
            List of bet dictionaries
        """
        try:
            params = {"limit": limit}
            if username:
                params["username"] = username
                
            response = self.session.get(f"{self.base_url}/bets", params=params)
            response.raise_for_status()
            
            bets = response.json()
            logger.info(f"Fetched {len(bets)} bets")
            return bets
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching bets: {e}")
            raise
    
    def get_market_bets(self, market_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all bets for a specific market
        
        Args:
            market_id: The market ID
            limit: Number of bets to fetch
            
        Returns:
            List of bet dictionaries for the market
        """
        try:
            params = {"limit": limit}
            
            response = self.session.get(f"{self.base_url}/bets", params={**params, "contractId": market_id})
            response.raise_for_status()
            
            bets = response.json()
            logger.info(f"Fetched {len(bets)} bets for market {market_id}")
            return bets
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching bets for market {market_id}: {e}")
            raise
    
    def get_user_positions(self, username: str) -> List[Dict[str, Any]]:
        """
        Get user's current positions
        
        Args:
            username: Username to get positions for
            
        Returns:
            List of position dictionaries
        """
        try:
            response = self.session.get(f"{self.base_url}/user/{username}/positions")
            response.raise_for_status()
            
            positions = response.json()
            logger.info(f"Fetched {len(positions)} positions for {username}")
            return positions
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching positions for {username}: {e}")
            raise
    
    def get_user(self, username: str) -> Dict[str, Any]:
        """
        Get user information
        
        Args:
            username: Username to look up
            
        Returns:
            User dictionary
        """
        try:
            response = self.session.get(f"{self.base_url}/user/{username}")
            response.raise_for_status()
            
            user = response.json()
            logger.info(f"Fetched user info for {username}")
            return user
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching user {username}: {e}")
            raise
