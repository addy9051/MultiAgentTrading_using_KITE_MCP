"""
Bull Researcher Agent - Advocates for bullish positions and long opportunities
Based on TauricResearch/TradingAgents architecture
"""

import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from models.trading_state import TradingState
from services.sample_llm_service import SampleLLMService
import json

logger = logging.getLogger(__name__)

class BullResearcher:
    """Agent that researches and advocates for bullish trading positions"""
    
    def __init__(self, settings):
        self.settings = settings
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
                temperature=0.3  # Slightly higher temperature for creative research
            )
    
    async def research_bullish_case(self, state: TradingState) -> Dict[str, Any]:
        """Research and build the bullish case"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for bull research")
                return self.generate_sample_bull_research(state)
            
            # Extract all analysis data
            market_data = state.get("market_data", {})
            fundamentals = state.get("fundamentals_analysis", {})
            sentiment = state.get("sentiment_analysis", {})
            news = state.get("news_analysis", {})
            technical = state.get("technical_analysis", {})
            
            symbol = market_data.get('symbol', 'UNKNOWN')
            
            system_prompt = """You are a bull researcher at a top investment firm.
            Your role is to research and advocate for bullish positions. You should:
            1. Identify all positive catalysts and opportunities
            2. Build a compelling case for upside potential
            3. Address potential counterarguments proactively
            4. Provide specific price targets and timeframes
            5. Recommend optimal entry strategies
            
            Be thorough, optimistic but realistic, and focus on actionable insights.
            
            Provide analysis in JSON format:
            {
                "bullish_thesis": "comprehensive thesis statement",
                "key_catalysts": ["catalyst1", "catalyst2", "catalyst3"],
                "upside_potential": "percentage or price target",
                "timeline": "short_term|medium_term|long_term",
                "entry_strategy": "detailed entry recommendation",
                "risk_mitigation": "how to manage downside",
                "supporting_evidence": ["evidence1", "evidence2"],
                "counterargument_responses": ["response1", "response2"],
                "confidence_level": confidence_0_to_100,
                "recommended_action": "BUY|ACCUMULATE|WAIT"
            }"""
            
            user_prompt = f"""
            Research the bullish case for {symbol}:
            
            Market Data:
            - Current Price: ${market_data.get('current_price', 0):.2f}
            - Volume: {market_data.get('volume', 0):,}
            - Daily Range: ${market_data.get('low', 0):.2f} - ${market_data.get('high', 0):.2f}
            
            Fundamentals Analysis:
            - Financial Health: {fundamentals.get('financial_health', 'unknown')}
            - Valuation: {fundamentals.get('valuation_assessment', 'unknown')}
            - Growth Potential: {fundamentals.get('growth_potential', 'unknown')}
            - Price Target: ${fundamentals.get('price_target', 0):.2f}
            
            Sentiment Analysis:
            - Overall Sentiment: {sentiment.get('overall_sentiment', 'neutral')}
            - Sentiment Score: {sentiment.get('sentiment_score', 0.5):.2f}
            - Social Media Buzz: {sentiment.get('social_media_buzz', 'medium')}
            
            News Analysis:
            - News Sentiment: {news.get('overall_news_sentiment', 'neutral')}
            - Key Catalysts: {', '.join(news.get('key_catalysts', []))}
            - Market Moving Potential: {news.get('market_moving_potential', 'medium')}
            
            Technical Analysis:
            - Trend Direction: {technical.get('trend_direction', 'sideways')}
            - RSI: {technical.get('rsi_signal', 'neutral')}
            - Overall Score: {technical.get('overall_score', 50)}
            
            Build a comprehensive bullish case with specific actionable recommendations.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            analysis = json.loads(response.content)
            
            logger.info(f"Bull research completed for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in bull research: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for bull research")
            return self.generate_sample_bull_research(state)
    
    def generate_sample_bull_research(self, state: TradingState) -> Dict[str, Any]:
        """Generate sample bull research"""
        try:
            market_data = state.get("market_data", {})
            symbol = market_data.get('symbol', 'UNKNOWN')
            current_price = market_data.get('current_price', 0)
            
            # Generate bullish thesis based on available data
            fundamentals = state.get("fundamentals_analysis", {})
            sentiment = state.get("sentiment_analysis", {})
            
            # Build bullish case
            upside_potential = "15-25%"
            if fundamentals.get('valuation_assessment') == 'undervalued':
                upside_potential = "25-35%"
            elif fundamentals.get('growth_potential') == 'high':
                upside_potential = "20-30%"
            
            # Determine timeline
            if sentiment.get('overall_sentiment') == 'bullish':
                timeline = "short_term"
            else:
                timeline = "medium_term"
            
            key_catalysts = [
                "Strong fundamentals support",
                "Positive market sentiment building",
                "Technical breakout potential"
            ]
            
            if fundamentals.get('financial_health') == 'strong':
                key_catalysts.append("Robust financial position")
            
            return {
                "bullish_thesis": f"{symbol} presents compelling upside opportunity with {upside_potential} potential driven by strong fundamentals and improving market sentiment.",
                "key_catalysts": key_catalysts,
                "upside_potential": upside_potential,
                "timeline": timeline,
                "entry_strategy": f"Consider accumulating on any dips below ${current_price * 0.98:.2f} with position sizing of 1-2% of portfolio",
                "risk_mitigation": f"Set stop-loss at ${current_price * 0.95:.2f} to limit downside to 5%",
                "supporting_evidence": [
                    "Fundamentals analysis supports value",
                    "Sentiment indicators improving",
                    "Technical setup favorable"
                ],
                "counterargument_responses": [
                    "Market volatility is manageable with proper risk management",
                    "Short-term noise doesn't change long-term fundamentals"
                ],
                "confidence_level": 75,
                "recommended_action": "ACCUMULATE"
            }
            
        except Exception as e:
            logger.error(f"Error generating sample bull research: {str(e)}")
            return {
                "bullish_thesis": "Sample bull research analysis",
                "key_catalysts": ["Sample analysis mode"],
                "upside_potential": "10-15%",
                "timeline": "medium_term",
                "entry_strategy": "Sample entry strategy",
                "risk_mitigation": "Sample risk management",
                "supporting_evidence": ["Sample evidence"],
                "counterargument_responses": ["Sample response"],
                "confidence_level": 50,
                "recommended_action": "WAIT"
            }
    
    async def process_bull_research(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for bull research"""
        try:
            logger.info("Processing bull research...")
            
            # Perform bull research
            bull_research = await self.research_bullish_case(state)
            
            # Add agent message
            messages = state.get("messages", [])
            symbol = state.get("market_data", {}).get('symbol', 'UNKNOWN')
            messages.append(f"Bull Researcher: Research completed for {symbol}")
            messages.append(f"Bullish Thesis: {bull_research.get('bullish_thesis', 'No thesis')[:100]}...")
            messages.append(f"Upside Potential: {bull_research.get('upside_potential', 'unknown')}")
            messages.append(f"Timeline: {bull_research.get('timeline', 'unknown')}")
            messages.append(f"Recommended Action: {bull_research.get('recommended_action', 'WAIT')}")
            
            return {
                "bull_research": bull_research,
                "messages": messages
            }
            
        except Exception as e:
            logger.error(f"Error in bull research processing: {str(e)}")
            messages = state.get("messages", [])
            messages.append(f"Bull Researcher: Research failed - {str(e)}")
            
            return {
                "bull_research": {
                    "error": str(e),
                    "bullish_thesis": "Research failed",
                    "recommended_action": "WAIT",
                    "confidence_level": 0
                },
                "messages": messages
            }