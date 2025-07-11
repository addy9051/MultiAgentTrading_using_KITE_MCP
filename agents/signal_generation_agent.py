"""
Signal Generation Agent - Generates trading signals based on analysis
"""

import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from models.trading_state import TradingState
from strategies.simple_rsi_strategy import SimpleRSIStrategy
from services.sample_llm_service import SampleLLMService
import json

logger = logging.getLogger(__name__)

class SignalGenerationAgent:
    """Agent responsible for generating trading signals"""
    
    def __init__(self, settings):
        self.settings = settings
        self.sample_llm_service = SampleLLMService()
        self.use_sample_llm = not settings.OPENAI_API_KEY
        self.rsi_strategy = SimpleRSIStrategy(settings)
        
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
    
    def generate_simple_signals(self, technical_indicators: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simple trading signals based on technical indicators"""
        try:
            signals = {}
            
            # RSI-based signals
            rsi_signal = self.rsi_strategy.generate_signal(technical_indicators, market_data)
            signals.update(rsi_signal)
            
            # Moving average crossover signals
            sma_20 = technical_indicators.get('sma_20', 0)
            sma_50 = technical_indicators.get('sma_50', 0)
            current_price = market_data.get('current_price', 0)
            
            if sma_20 > sma_50 and current_price > sma_20:
                signals['ma_signal'] = 'BUY'
                signals['ma_strength'] = 'strong' if current_price > sma_20 * 1.02 else 'moderate'
            elif sma_20 < sma_50 and current_price < sma_20:
                signals['ma_signal'] = 'SELL'
                signals['ma_strength'] = 'strong' if current_price < sma_20 * 0.98 else 'moderate'
            else:
                signals['ma_signal'] = 'HOLD'
                signals['ma_strength'] = 'weak'
            
            # Volume confirmation
            volume = market_data.get('volume', 0)
            volume_sma = technical_indicators.get('volume_sma', 0)
            
            if volume > volume_sma * 1.5:
                signals['volume_confirmation'] = 'strong'
            elif volume > volume_sma * 1.2:
                signals['volume_confirmation'] = 'moderate'
            else:
                signals['volume_confirmation'] = 'weak'
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating simple signals: {str(e)}")
            return {}
    
    async def generate_advanced_signals(self, state: TradingState) -> Dict[str, Any]:
        """Generate advanced trading signals using LLM analysis"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for signal generation")
                market_data = state.get("market_data", {})
                technical_indicators = state.get("technical_indicators", {})
                technical_analysis = state.get("technical_analysis", {})
                market_analysis = state.get("market_analysis", {})
                return self.sample_llm_service.generate_trading_signals(
                    market_data, technical_indicators, technical_analysis, market_analysis
                )
            
            market_data = state.get("market_data", {})
            technical_indicators = state.get("technical_indicators", {})
            technical_analysis = state.get("technical_analysis", {})
            market_analysis = state.get("market_analysis", {})
            
            system_prompt = """You are a professional trading signal generator. 
            Based on the provided market data, technical indicators, and analysis, generate trading signals.
            
            Consider:
            1. Multiple timeframe analysis
            2. Risk-reward ratio
            3. Market sentiment
            4. Volume confirmation
            5. Technical pattern strength
            
            Respond in JSON format with the following structure:
            {
                "primary_signal": "BUY|SELL|HOLD",
                "confidence": percentage_0_to_100,
                "signal_strength": "strong|moderate|weak",
                "entry_price": price,
                "stop_loss": price,
                "take_profit": price,
                "position_size": percentage_of_portfolio,
                "time_horizon": "short|medium|long",
                "risk_level": "low|medium|high",
                "reasoning": "detailed explanation",
                "supporting_factors": ["factor1", "factor2"],
                "risk_factors": ["risk1", "risk2"]
            }"""
            
            user_prompt = f"""
            Generate trading signals based on this data:
            
            Market Data:
            - Symbol: {market_data.get('symbol', 'N/A')}
            - Current Price: {market_data.get('current_price', 'N/A')}
            - Volume: {market_data.get('volume', 'N/A')}
            
            Technical Indicators:
            - RSI: {technical_indicators.get('rsi', 'N/A')}
            - MACD: {technical_indicators.get('macd', 'N/A')}
            - Bollinger Bands: {technical_indicators.get('bollinger_bands', 'N/A')}
            
            Technical Analysis:
            - Trend Direction: {technical_analysis.get('trend_direction', 'N/A')}
            - Trend Strength: {technical_analysis.get('trend_strength', 'N/A')}
            - Overall Score: {technical_analysis.get('overall_score', 'N/A')}
            
            Market Analysis:
            - Market Trend: {market_analysis.get('trend', 'N/A')}
            - Sentiment: {market_analysis.get('sentiment', 'N/A')}
            - Volatility: {market_analysis.get('volatility', 'N/A')}
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            signals = json.loads(response.content)
            
            logger.info(f"Advanced signals generated: {signals['primary_signal']}")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating advanced signals: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for signal generation")
            market_data = state.get("market_data", {})
            technical_indicators = state.get("technical_indicators", {})
            technical_analysis = state.get("technical_analysis", {})
            market_analysis = state.get("market_analysis", {})
            return self.sample_llm_service.generate_trading_signals(
                market_data, technical_indicators, technical_analysis, market_analysis
            )
    
    async def process_signal_generation(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for signal generation"""
        try:
            market_data = state.get("market_data", {})
            technical_indicators = state.get("technical_indicators", {})
            
            # Generate simple signals
            simple_signals = self.generate_simple_signals(technical_indicators, market_data)
            
            # Generate advanced signals
            advanced_signals = await self.generate_advanced_signals(state)
            
            # Combine signals
            combined_signals = {
                "simple_signals": simple_signals,
                "advanced_signals": advanced_signals,
                "final_signal": advanced_signals.get("primary_signal", "HOLD"),
                "confidence": advanced_signals.get("confidence", 0),
                "timestamp": market_data.get("timestamp", "")
            }
            
            # Update state
            updated_state = {
                "trading_signals": combined_signals,
                "messages": state.get("messages", []) + [
                    f"Signal Generation Agent: Signals generated",
                    f"Primary Signal: {combined_signals['final_signal']}",
                    f"Confidence: {combined_signals['confidence']}%",
                    f"RSI Signal: {simple_signals.get('rsi_signal', 'N/A')}"
                ]
            }
            
            return updated_state
            
        except Exception as e:
            logger.error(f"Error processing signal generation: {str(e)}")
            return {
                "error": str(e),
                "messages": state.get("messages", []) + [
                    f"Signal Generation Agent: Error generating signals - {str(e)}"
                ]
            }
