"""
Technical Analysis Agent - Calculates technical indicators and patterns
"""

import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from models.trading_state import TradingState
from utils.technical_indicators import TechnicalIndicators
from services.sample_llm_service import SampleLLMService
import json

logger = logging.getLogger(__name__)

class TechnicalAnalysisAgent:
    """Agent responsible for technical analysis of market data"""
    
    def __init__(self, settings):
        self.settings = settings
        self.sample_llm_service = SampleLLMService()
        self.use_sample_llm = not settings.OPENAI_API_KEY
        self.technical_indicators = TechnicalIndicators()
        
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
    
    def calculate_indicators(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calculate technical indicators from historical data"""
        try:
            if not historical_data or len(historical_data) < self.settings.RSI_PERIOD:
                logger.warning("Insufficient historical data for technical analysis")
                return {}
            
            # Extract price data
            prices = [float(candle.get("close", 0)) for candle in historical_data]
            highs = [float(candle.get("high", 0)) for candle in historical_data]
            lows = [float(candle.get("low", 0)) for candle in historical_data]
            volumes = [float(candle.get("volume", 0)) for candle in historical_data]
            
            # Calculate indicators
            indicators = {
                "rsi": self.technical_indicators.calculate_rsi(prices, self.settings.RSI_PERIOD),
                "sma_20": self.technical_indicators.calculate_sma(prices, 20),
                "sma_50": self.technical_indicators.calculate_sma(prices, 50),
                "ema_12": self.technical_indicators.calculate_ema(prices, 12),
                "ema_26": self.technical_indicators.calculate_ema(prices, 26),
                "bollinger_bands": self.technical_indicators.calculate_bollinger_bands(prices, 20, 2),
                "macd": self.technical_indicators.calculate_macd(prices),
                "stochastic": self.technical_indicators.calculate_stochastic(highs, lows, prices, 14),
                "atr": self.technical_indicators.calculate_atr(highs, lows, prices, 14),
                "volume_sma": self.technical_indicators.calculate_sma(volumes, 20)
            }
            
            logger.info("Technical indicators calculated successfully")
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}
    
    async def analyze_technical_patterns(self, indicators: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical patterns using LLM"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for technical pattern analysis")
                return self.sample_llm_service.analyze_technical_patterns(indicators, market_data)
            
            system_prompt = """You are a technical analysis expert. 
            Analyze the provided technical indicators and identify:
            1. Key technical patterns
            2. Support and resistance levels
            3. Trend strength and direction
            4. Momentum indicators
            5. Entry/exit signals
            
            Respond in JSON format with the following structure:
            {
                "trend_direction": "bullish|bearish|sideways",
                "trend_strength": "strong|moderate|weak",
                "momentum": "positive|negative|neutral",
                "rsi_signal": "oversold|overbought|neutral",
                "macd_signal": "bullish|bearish|neutral",
                "bollinger_position": "upper|middle|lower",
                "support_level": price,
                "resistance_level": price,
                "entry_signals": ["signal1", "signal2"],
                "exit_signals": ["signal1", "signal2"],
                "overall_score": score_between_0_and_100
            }"""
            
            user_prompt = f"""
            Analyze these technical indicators:
            RSI: {indicators.get('rsi', 'N/A')}
            SMA 20: {indicators.get('sma_20', 'N/A')}
            SMA 50: {indicators.get('sma_50', 'N/A')}
            EMA 12: {indicators.get('ema_12', 'N/A')}
            EMA 26: {indicators.get('ema_26', 'N/A')}
            MACD: {indicators.get('macd', 'N/A')}
            Bollinger Bands: {indicators.get('bollinger_bands', 'N/A')}
            Stochastic: {indicators.get('stochastic', 'N/A')}
            ATR: {indicators.get('atr', 'N/A')}
            
            Current Price: {market_data.get('current_price', 'N/A')}
            Volume: {market_data.get('volume', 'N/A')}
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            analysis = json.loads(response.content)
            
            logger.info("Technical pattern analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing technical patterns: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for technical pattern analysis")
            return self.sample_llm_service.analyze_technical_patterns(indicators, market_data)
    
    async def process_technical_analysis(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for technical analysis"""
        try:
            market_data = state.get("market_data", {})
            historical_data = market_data.get("historical_data", [])
            
            # Calculate technical indicators
            indicators = self.calculate_indicators(historical_data)
            
            # Analyze patterns
            technical_analysis = await self.analyze_technical_patterns(indicators, market_data)
            
            # Update state
            updated_state = {
                "technical_indicators": indicators,
                "technical_analysis": technical_analysis,
                "messages": state.get("messages", []) + [
                    f"Technical Analysis Agent: Analysis completed",
                    f"RSI: {indicators.get('rsi', 'N/A')}",
                    f"Trend: {technical_analysis['trend_direction']}",
                    f"Overall Score: {technical_analysis['overall_score']}"
                ]
            }
            
            return updated_state
            
        except Exception as e:
            logger.error(f"Error processing technical analysis: {str(e)}")
            return {
                "error": str(e),
                "messages": state.get("messages", []) + [
                    f"Technical Analysis Agent: Error in analysis - {str(e)}"
                ]
            }
