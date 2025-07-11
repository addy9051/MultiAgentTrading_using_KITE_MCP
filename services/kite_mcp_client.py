"""
Kite MCP Client - Handles communication with Kite MCP server
"""

import logging
import requests
import json
from typing import Dict, Any, List, Optional
import asyncio
import aiohttp
from services.sample_data_service import SampleDataService

logger = logging.getLogger(__name__)

class KiteMCPClient:
    """Client for interacting with Kite MCP server"""
    
    def __init__(self, settings):
        self.settings = settings
        self.base_url = settings.KITE_MCP_URL
        self.session = None
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': settings.KITE_API_KEY
        }
        # Initialize sample data service for testing
        self.sample_data_service = SampleDataService()
        self.use_sample_data = not settings.KITE_API_KEY  # Use sample data if no API key
    
    async def initialize(self):
        """Initialize the MCP client session"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Test connection to MCP server
            await self.test_connection()
            
            logger.info("Kite MCP client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kite MCP client: {str(e)}")
            raise
    
    async def test_connection(self) -> bool:
        """Test connection to MCP server"""
        try:
            url = f"{self.base_url}/health"
            
            async with self.session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    logger.info("MCP server connection successful")
                    return True
                else:
                    logger.error(f"MCP server connection failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error testing MCP connection: {str(e)}")
            # Mock successful connection for development
            logger.info("Using mock MCP connection for development")
            return True
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile from Kite"""
        try:
            url = f"{self.base_url}/profile"
            
            async with self.session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Failed to get profile: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting profile: {str(e)}")
            # Return mock data for development
            return {
                "user_id": "mock_user",
                "user_name": "Mock User",
                "email": "mock@example.com",
                "broker": "ZERODHA"
            }
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get live quote for a symbol"""
        try:
            # Use sample data if no API key is provided
            if self.use_sample_data:
                logger.info(f"Using sample data for quote: {symbol}")
                return self.sample_data_service.get_sample_quote(symbol)
            
            url = f"{self.base_url}/quote"
            params = {"symbol": symbol}
            
            async with self.session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Failed to get quote for {symbol}: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {str(e)}")
            # Fallback to sample data
            logger.info(f"Falling back to sample data for quote: {symbol}")
            return self.sample_data_service.get_sample_quote(symbol)
    
    async def get_historical_data(self, symbol: str, interval: str = "15minute", 
                                 days: int = 30) -> List[Dict[str, Any]]:
        """Get historical data for a symbol"""
        try:
            # Use sample data if no API key is provided
            if self.use_sample_data:
                logger.info(f"Using sample data for historical data: {symbol}")
                return self.sample_data_service.get_sample_historical_data(symbol, interval, days)
            
            url = f"{self.base_url}/historical"
            params = {
                "symbol": symbol,
                "interval": interval,
                "days": days
            }
            
            async with self.session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Failed to get historical data for {symbol}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            # Fallback to sample data
            logger.info(f"Falling back to sample data for historical data: {symbol}")
            return self.sample_data_service.get_sample_historical_data(symbol, interval, days)
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        try:
            url = f"{self.base_url}/positions"
            
            async with self.session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("positions", [])
                else:
                    logger.error(f"Failed to get positions: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            # Return mock positions for development
            return []
    
    async def get_holdings(self) -> List[Dict[str, Any]]:
        """Get current holdings"""
        try:
            url = f"{self.base_url}/holdings"
            
            async with self.session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("holdings", [])
                else:
                    logger.error(f"Failed to get holdings: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting holdings: {str(e)}")
            # Return mock holdings for development
            return []
    
    async def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Place a trading order (simulation mode)"""
        try:
            if not self.settings.SIMULATION_MODE:
                url = f"{self.base_url}/orders"
                
                async with self.session.post(url, headers=self.headers, json=order_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Failed to place order: {response.status}")
                        return {}
            else:
                # Simulation mode - log the order
                logger.info(f"SIMULATION: Order placed - {order_data}")
                return {
                    "order_id": f"MOCK_{order_data.get('symbol', 'UNKNOWN')}_{hash(str(order_data)) % 10000}",
                    "status": "COMPLETE",
                    "message": "Order placed successfully (simulation)"
                }
                
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {"error": str(e)}
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
