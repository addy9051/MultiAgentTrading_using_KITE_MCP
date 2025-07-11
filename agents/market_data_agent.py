"""
Market Data Agent - Responsible for fetching and processing market data
"""

import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from services.kite_mcp_client import KiteMCPClient
from services.sample_llm_service import SampleLLMService
from models.trading_state import TradingState
import json

logger = logging.getLogger(__name__)

class MarketDataAgent:
    """Agent responsible for market data collection and processing"""
    
    def __init__(self, settings, kite_client: KiteMCPClient):
        self.settings = settings
        self.kite_client = kite_client
        self.sample_llm_service = SampleLLMService()
        self.use_sample_llm = not settings.OPENAI_API_KEY
        
        # Initialize OpenAI client only if API key is available
        self.llm = None
        if settings.OPENAI_API_KEY:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.1
            )
        
    async def fetch_market_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch current market data for a symbol"""
        try:
            logger.info(f"Fetching market data for {symbol}")
            
            # Get live quote
            quote_data = await self.kite_client.get_quote(symbol)
            
            # Get historical data for technical analysis
            historical_data = await self.kite_client.get_historical_data(
                symbol=symbol,
                interval="15minute",
                days=30
            )
            
            market_data = {
                "symbol": symbol,
                "current_price": quote_data.get("last_price", 0),
                "volume": quote_data.get("volume", 0),
                "high": quote_data.get("ohlc", {}).get("high", 0),
                "low": quote_data.get("ohlc", {}).get("low", 0),
                "open": quote_data.get("ohlc", {}).get("open", 0),
                "close": quote_data.get("ohlc", {}).get("close", 0),
                "historical_data": historical_data,
                "timestamp": quote_data.get("timestamp", "")
            }
            
            logger.info(f"Successfully fetched market data for {symbol}")
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {str(e)}")
            raise
    
    async def analyze_market_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market context using LLM"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for market analysis")
                return self.sample_llm_service.analyze_market_context(market_data)
            
            system_prompt = """You are a market data analysis expert. 
            Analyze the provided market data and provide insights about:
            1. Current market trend (bullish/bearish/sideways)
            2. Volume analysis
            3. Price volatility
            4. Support and resistance levels
            5. Market sentiment
            
            Respond in JSON format with the following structure:
            {
                "trend": "bullish|bearish|sideways",
                "volatility": "high|medium|low",
                "volume_analysis": "description",
                "support_level": price,
                "resistance_level": price,
                "sentiment": "positive|negative|neutral",
                "key_observations": ["observation1", "observation2"]
            }"""
            
            user_prompt = f"""
            Analyze this market data:
            Symbol: {market_data['symbol']}
            Current Price: {market_data['current_price']}
            High: {market_data['high']}
            Low: {market_data['low']}
            Open: {market_data['open']}
            Volume: {market_data['volume']}
            
            Historical data points available: {len(market_data.get('historical_data', []))}
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            analysis = json.loads(response.content)
            
            logger.info(f"Market analysis completed for {market_data['symbol']}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market context: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for market analysis")
            return self.sample_llm_service.analyze_market_context(market_data)
    
    async def process_market_data(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for market data"""
        try:
            symbol = state.get("symbol", self.settings.TARGET_SYMBOL)
            
            # Fetch market data
            market_data = await self.fetch_market_data(symbol)
            
            # Analyze market context
            market_analysis = await self.analyze_market_context(market_data)
            
            # Update state
            updated_state = {
                "market_data": market_data,
                "market_analysis": market_analysis,
                "messages": state.get("messages", []) + [
                    f"Market Data Agent: Processed data for {symbol}",
                    f"Current Price: {market_data['current_price']}",
                    f"Market Trend: {market_analysis['trend']}",
                    f"Volatility: {market_analysis['volatility']}"
                ]
            }
            
            return updated_state
            
        except Exception as e:
            logger.error(f"Error processing market data: {str(e)}")
            return {
                "error": str(e),
                "messages": state.get("messages", []) + [
                    f"Market Data Agent: Error processing data - {str(e)}"
                ]
            }
