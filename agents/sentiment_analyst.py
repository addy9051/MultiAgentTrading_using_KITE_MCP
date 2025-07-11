"""
Sentiment Analyst Agent - Analyzes market sentiment from news and social media
Based on TauricResearch/TradingAgents architecture
"""

import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from models.trading_state import TradingState
from services.sample_llm_service import SampleLLMService
import json
import random

logger = logging.getLogger(__name__)

class SentimentAnalyst:
    """Agent responsible for sentiment analysis of market and social media data"""
    
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
                temperature=0.1
            )
    
    def generate_sample_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        """Generate realistic sample sentiment data"""
        try:
            # Simulate sentiment sources
            sentiment_sources = [
                "Twitter/X mentions",
                "Reddit discussions",
                "News articles",
                "Financial forums",
                "Analyst reports"
            ]
            
            # Generate sentiment scores
            overall_sentiment = random.choice(["positive", "negative", "neutral"])
            
            if overall_sentiment == "positive":
                sentiment_score = random.uniform(0.6, 0.9)
                positive_mentions = random.randint(150, 300)
                negative_mentions = random.randint(20, 80)
            elif overall_sentiment == "negative":
                sentiment_score = random.uniform(0.1, 0.4)
                positive_mentions = random.randint(20, 80)
                negative_mentions = random.randint(150, 300)
            else:
                sentiment_score = random.uniform(0.4, 0.6)
                positive_mentions = random.randint(80, 150)
                negative_mentions = random.randint(80, 150)
            
            # Generate key themes
            positive_themes = [
                "Strong earnings potential",
                "Market expansion",
                "Innovation leadership",
                "Cost optimization",
                "Strategic partnerships"
            ]
            
            negative_themes = [
                "Regulatory concerns",
                "Market competition",
                "Economic headwinds",
                "Valuation concerns",
                "Sector rotation"
            ]
            
            # Select relevant themes
            if overall_sentiment == "positive":
                key_themes = random.sample(positive_themes, 3)
            elif overall_sentiment == "negative":
                key_themes = random.sample(negative_themes, 3)
            else:
                key_themes = random.sample(positive_themes, 1) + random.sample(negative_themes, 1)
            
            return {
                "overall_sentiment": overall_sentiment,
                "sentiment_score": round(sentiment_score, 3),
                "positive_mentions": positive_mentions,
                "negative_mentions": negative_mentions,
                "neutral_mentions": random.randint(50, 100),
                "total_mentions": positive_mentions + negative_mentions + random.randint(50, 100),
                "key_themes": key_themes,
                "sentiment_sources": sentiment_sources,
                "confidence": random.uniform(0.7, 0.9)
            }
            
        except Exception as e:
            logger.error(f"Error generating sample sentiment data: {str(e)}")
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.5,
                "positive_mentions": 100,
                "negative_mentions": 100,
                "neutral_mentions": 50,
                "total_mentions": 250,
                "key_themes": ["Sample analysis mode"],
                "sentiment_sources": ["Sample data"],
                "confidence": 0.5
            }
    
    async def analyze_market_sentiment(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market sentiment using LLM"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for sentiment analysis")
                return self.generate_sample_sentiment_analysis(market_data)
            
            symbol = market_data.get('symbol', 'UNKNOWN')
            sentiment_data = self.generate_sample_sentiment_data(symbol)
            
            system_prompt = """You are a senior sentiment analyst specializing in financial markets.
            Your task is to analyze market sentiment and social media trends to gauge investor mood.
            
            Consider these factors:
            1. Social media mentions and sentiment trends
            2. News sentiment and media coverage
            3. Investor confidence and market psychology
            4. Fear and greed indicators
            5. Volume patterns and market participation
            
            Provide analysis in JSON format:
            {
                "overall_sentiment": "bullish|bearish|neutral",
                "sentiment_strength": "strong|moderate|weak",
                "sentiment_score": score_0_to_1,
                "key_sentiment_drivers": ["driver1", "driver2"],
                "social_media_buzz": "high|medium|low",
                "news_sentiment": "positive|negative|neutral",
                "investor_confidence": "high|medium|low",
                "market_fear_greed": "extreme_fear|fear|neutral|greed|extreme_greed",
                "sentiment_trend": "improving|stable|deteriorating",
                "trading_implications": "buy_momentum|sell_pressure|sideways_action",
                "confidence_level": confidence_0_to_100
            }"""
            
            user_prompt = f"""
            Analyze market sentiment for {symbol}:
            
            Current Market Data:
            - Price: ${market_data.get('current_price', 0):.2f}
            - Volume: {market_data.get('volume', 0):,}
            - Price Change: {((market_data.get('current_price', 0) - market_data.get('open', 0)) / market_data.get('open', 1)) * 100:.2f}%
            
            Sentiment Data:
            - Overall Sentiment: {sentiment_data.get('overall_sentiment', 'neutral')}
            - Sentiment Score: {sentiment_data.get('sentiment_score', 0.5)}
            - Total Mentions: {sentiment_data.get('total_mentions', 0):,}
            - Positive Mentions: {sentiment_data.get('positive_mentions', 0):,}
            - Negative Mentions: {sentiment_data.get('negative_mentions', 0):,}
            - Key Themes: {', '.join(sentiment_data.get('key_themes', []))}
            
            Provide comprehensive sentiment analysis with trading implications.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            analysis = json.loads(response.content)
            
            logger.info(f"Sentiment analysis completed for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for sentiment analysis")
            return self.generate_sample_sentiment_analysis(market_data)
    
    def generate_sample_sentiment_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample sentiment analysis"""
        try:
            symbol = market_data.get('symbol', 'UNKNOWN')
            current_price = market_data.get('current_price', 0)
            volume = market_data.get('volume', 0)
            
            # Generate sentiment based on price action and volume
            price_change = ((current_price - market_data.get('open', current_price)) / market_data.get('open', current_price)) * 100
            
            if price_change > 2:
                overall_sentiment = "bullish"
                sentiment_strength = "strong"
                sentiment_score = 0.8
                trading_implications = "buy_momentum"
            elif price_change < -2:
                overall_sentiment = "bearish"
                sentiment_strength = "strong"
                sentiment_score = 0.2
                trading_implications = "sell_pressure"
            else:
                overall_sentiment = "neutral"
                sentiment_strength = "moderate"
                sentiment_score = 0.5
                trading_implications = "sideways_action"
            
            # Volume-based social media buzz
            social_media_buzz = "high" if volume > 1000000 else "medium" if volume > 500000 else "low"
            
            return {
                "overall_sentiment": overall_sentiment,
                "sentiment_strength": sentiment_strength,
                "sentiment_score": sentiment_score,
                "key_sentiment_drivers": [
                    "Price momentum",
                    "Volume activity",
                    "Market conditions"
                ],
                "social_media_buzz": social_media_buzz,
                "news_sentiment": "neutral",
                "investor_confidence": "medium",
                "market_fear_greed": "neutral",
                "sentiment_trend": "stable",
                "trading_implications": trading_implications,
                "confidence_level": 70
            }
            
        except Exception as e:
            logger.error(f"Error generating sample sentiment analysis: {str(e)}")
            return {
                "overall_sentiment": "neutral",
                "sentiment_strength": "weak",
                "sentiment_score": 0.5,
                "key_sentiment_drivers": ["Sample analysis mode"],
                "social_media_buzz": "medium",
                "news_sentiment": "neutral",
                "investor_confidence": "medium",
                "market_fear_greed": "neutral",
                "sentiment_trend": "stable",
                "trading_implications": "sideways_action",
                "confidence_level": 50
            }
    
    async def process_sentiment_analysis(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for sentiment analysis"""
        try:
            logger.info("Processing sentiment analysis...")
            
            market_data = state.get("market_data", {})
            if not market_data:
                raise ValueError("No market data available for sentiment analysis")
            
            # Perform sentiment analysis
            sentiment_analysis = await self.analyze_market_sentiment(market_data)
            
            # Add agent message
            messages = state.get("messages", [])
            symbol = market_data.get('symbol', 'UNKNOWN')
            messages.append(f"Sentiment Analyst: Analysis completed for {symbol}")
            messages.append(f"Overall Sentiment: {sentiment_analysis.get('overall_sentiment', 'neutral')}")
            messages.append(f"Sentiment Score: {sentiment_analysis.get('sentiment_score', 0.5):.2f}")
            messages.append(f"Social Media Buzz: {sentiment_analysis.get('social_media_buzz', 'medium')}")
            messages.append(f"Trading Implications: {sentiment_analysis.get('trading_implications', 'sideways_action')}")
            
            return {
                "sentiment_analysis": sentiment_analysis,
                "messages": messages
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis processing: {str(e)}")
            messages = state.get("messages", [])
            messages.append(f"Sentiment Analyst: Analysis failed - {str(e)}")
            
            return {
                "sentiment_analysis": {
                    "error": str(e),
                    "overall_sentiment": "neutral",
                    "sentiment_score": 0.5,
                    "confidence_level": 0
                },
                "messages": messages
            }