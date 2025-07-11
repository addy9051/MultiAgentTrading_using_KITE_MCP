"""
Bear Researcher Agent - Advocates for bearish positions and identifies risks
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

class BearResearcher:
    """Agent that researches and advocates for bearish trading positions"""
    
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
    
    async def research_bearish_case(self, state: TradingState) -> Dict[str, Any]:
        """Research and build the bearish case"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for bear research")
                return self.generate_sample_bear_research(state)
            
            # Extract all analysis data
            market_data = state.get("market_data", {})
            fundamentals = state.get("fundamentals_analysis", {})
            sentiment = state.get("sentiment_analysis", {})
            news = state.get("news_analysis", {})
            technical = state.get("technical_analysis", {})
            
            symbol = market_data.get('symbol', 'UNKNOWN')
            
            system_prompt = """You are a bear researcher at a top investment firm.
            Your role is to research and advocate for bearish positions. You should:
            1. Identify all risk factors and potential catalysts for decline
            2. Build a compelling case for downside potential
            3. Challenge bullish assumptions critically
            4. Provide specific downside targets and timeframes
            5. Recommend defensive strategies
            
            Be thorough, skeptical but realistic, and focus on risk management.
            
            Provide analysis in JSON format:
            {
                "bearish_thesis": "comprehensive thesis statement",
                "key_risk_factors": ["risk1", "risk2", "risk3"],
                "downside_potential": "percentage or price target",
                "timeline": "short_term|medium_term|long_term",
                "defensive_strategy": "detailed defensive recommendation",
                "exit_triggers": "when to exit positions",
                "supporting_evidence": ["evidence1", "evidence2"],
                "bull_case_rebuttals": ["rebuttal1", "rebuttal2"],
                "confidence_level": confidence_0_to_100,
                "recommended_action": "SELL|REDUCE|AVOID"
            }"""
            
            user_prompt = f"""
            Research the bearish case for {symbol}:
            
            Market Data:
            - Current Price: ${market_data.get('current_price', 0):.2f}
            - Volume: {market_data.get('volume', 0):,}
            - Daily Range: ${market_data.get('low', 0):.2f} - ${market_data.get('high', 0):.2f}
            
            Fundamentals Analysis:
            - Financial Health: {fundamentals.get('financial_health', 'unknown')}
            - Valuation: {fundamentals.get('valuation_assessment', 'unknown')}
            - Key Risks: {', '.join(fundamentals.get('key_risks', []))}
            
            Sentiment Analysis:
            - Overall Sentiment: {sentiment.get('overall_sentiment', 'neutral')}
            - Sentiment Score: {sentiment.get('sentiment_score', 0.5):.2f}
            - Key Drivers: {', '.join(sentiment.get('key_sentiment_drivers', []))}
            
            News Analysis:
            - News Sentiment: {news.get('overall_news_sentiment', 'neutral')}
            - Risk Factors: {', '.join(news.get('risk_factors', []))}
            - Market Moving Potential: {news.get('market_moving_potential', 'medium')}
            
            Technical Analysis:
            - Trend Direction: {technical.get('trend_direction', 'sideways')}
            - RSI: {technical.get('rsi_signal', 'neutral')}
            - Overall Score: {technical.get('overall_score', 50)}
            
            Build a comprehensive bearish case with specific risk assessments and defensive strategies.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            analysis = json.loads(response.content)
            
            logger.info(f"Bear research completed for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in bear research: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for bear research")
            return self.generate_sample_bear_research(state)
    
    def generate_sample_bear_research(self, state: TradingState) -> Dict[str, Any]:
        """Generate sample bear research"""
        try:
            market_data = state.get("market_data", {})
            symbol = market_data.get('symbol', 'UNKNOWN')
            current_price = market_data.get('current_price', 0)
            
            # Generate bearish thesis based on available data
            fundamentals = state.get("fundamentals_analysis", {})
            sentiment = state.get("sentiment_analysis", {})
            
            # Build bearish case
            downside_potential = "10-20%"
            if fundamentals.get('valuation_assessment') == 'overvalued':
                downside_potential = "20-30%"
            elif sentiment.get('overall_sentiment') == 'bearish':
                downside_potential = "15-25%"
            
            # Determine timeline
            if sentiment.get('sentiment_trend') == 'deteriorating':
                timeline = "short_term"
            else:
                timeline = "medium_term"
            
            key_risk_factors = [
                "Market volatility concerns",
                "Valuation pressure",
                "Macroeconomic headwinds"
            ]
            
            if fundamentals.get('key_risks'):
                key_risk_factors.extend(fundamentals.get('key_risks', [])[:2])
            
            return {
                "bearish_thesis": f"{symbol} faces significant downside risk with {downside_potential} potential decline due to valuation concerns and market headwinds.",
                "key_risk_factors": key_risk_factors,
                "downside_potential": downside_potential,
                "timeline": timeline,
                "defensive_strategy": f"Consider reducing exposure or setting stop-loss at ${current_price * 0.90:.2f}",
                "exit_triggers": "Break below key support levels or deteriorating fundamentals",
                "supporting_evidence": [
                    "Valuation metrics suggest caution",
                    "Market sentiment showing weakness",
                    "Technical indicators mixed"
                ],
                "bull_case_rebuttals": [
                    "Growth projections may be too optimistic",
                    "Market conditions more challenging than expected"
                ],
                "confidence_level": 70,
                "recommended_action": "REDUCE"
            }
            
        except Exception as e:
            logger.error(f"Error generating sample bear research: {str(e)}")
            return {
                "bearish_thesis": "Sample bear research analysis",
                "key_risk_factors": ["Sample analysis mode"],
                "downside_potential": "5-10%",
                "timeline": "medium_term",
                "defensive_strategy": "Sample defensive strategy",
                "exit_triggers": "Sample exit criteria",
                "supporting_evidence": ["Sample evidence"],
                "bull_case_rebuttals": ["Sample rebuttal"],
                "confidence_level": 50,
                "recommended_action": "AVOID"
            }
    
    async def process_bear_research(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for bear research"""
        try:
            logger.info("Processing bear research...")
            
            # Perform bear research
            bear_research = await self.research_bearish_case(state)
            
            # Add agent message
            messages = state.get("messages", [])
            symbol = state.get("market_data", {}).get('symbol', 'UNKNOWN')
            messages.append(f"Bear Researcher: Research completed for {symbol}")
            messages.append(f"Bearish Thesis: {bear_research.get('bearish_thesis', 'No thesis')[:100]}...")
            messages.append(f"Downside Potential: {bear_research.get('downside_potential', 'unknown')}")
            messages.append(f"Timeline: {bear_research.get('timeline', 'unknown')}")
            messages.append(f"Recommended Action: {bear_research.get('recommended_action', 'AVOID')}")
            
            return {
                "bear_research": bear_research,
                "messages": messages
            }
            
        except Exception as e:
            logger.error(f"Error in bear research processing: {str(e)}")
            messages = state.get("messages", [])
            messages.append(f"Bear Researcher: Research failed - {str(e)}")
            
            return {
                "bear_research": {
                    "error": str(e),
                    "bearish_thesis": "Research failed",
                    "recommended_action": "AVOID",
                    "confidence_level": 0
                },
                "messages": messages
            }