"""
News Analyst Agent - Monitors and analyzes news events and market catalysts
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
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NewsAnalyst:
    """Agent responsible for analyzing news events and market catalysts"""
    
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
    
    def generate_sample_news_data(self, symbol: str) -> List[Dict[str, Any]]:
        """Generate realistic sample news data"""
        try:
            news_categories = [
                "earnings",
                "product_launch",
                "regulatory",
                "market_update",
                "analyst_rating",
                "partnership",
                "leadership",
                "sector_news"
            ]
            
            sample_news = []
            
            # Generate 5-10 news items
            for i in range(random.randint(5, 10)):
                category = random.choice(news_categories)
                
                # Generate news based on category
                if category == "earnings":
                    headlines = [
                        f"{symbol} Reports Strong Q3 Earnings Beat",
                        f"{symbol} Exceeds Revenue Expectations",
                        f"{symbol} Announces Quarterly Results"
                    ]
                elif category == "product_launch":
                    headlines = [
                        f"{symbol} Unveils New Product Line",
                        f"{symbol} Launches Innovation Initiative",
                        f"{symbol} Expands Service Offerings"
                    ]
                elif category == "regulatory":
                    headlines = [
                        f"New Regulations May Impact {symbol}",
                        f"{symbol} Faces Regulatory Review",
                        f"Industry Regulation Updates Affect {symbol}"
                    ]
                elif category == "analyst_rating":
                    headlines = [
                        f"Analyst Upgrades {symbol} Rating",
                        f"{symbol} Receives Price Target Increase",
                        f"Wall Street Bullish on {symbol}"
                    ]
                else:
                    headlines = [
                        f"{symbol} Market Update",
                        f"{symbol} Industry News",
                        f"{symbol} Business Development"
                    ]
                
                headline = random.choice(headlines)
                
                # Generate sentiment and impact
                sentiment = random.choice(["positive", "negative", "neutral"])
                impact = random.choice(["high", "medium", "low"])
                
                # Generate timestamp (last 24 hours)
                hours_ago = random.randint(1, 24)
                timestamp = datetime.now() - timedelta(hours=hours_ago)
                
                news_item = {
                    "headline": headline,
                    "category": category,
                    "sentiment": sentiment,
                    "impact": impact,
                    "timestamp": timestamp.isoformat(),
                    "source": random.choice(["Reuters", "Bloomberg", "CNBC", "WSJ", "Financial Times"]),
                    "relevance": random.uniform(0.6, 0.9)
                }
                
                sample_news.append(news_item)
            
            return sample_news
            
        except Exception as e:
            logger.error(f"Error generating sample news data: {str(e)}")
            return [{
                "headline": "Sample news analysis mode",
                "category": "market_update",
                "sentiment": "neutral",
                "impact": "low",
                "timestamp": datetime.now().isoformat(),
                "source": "Sample",
                "relevance": 0.5
            }]
    
    async def analyze_news_impact(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze news impact using LLM"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for news analysis")
                return self.generate_sample_news_analysis(market_data)
            
            symbol = market_data.get('symbol', 'UNKNOWN')
            news_data = self.generate_sample_news_data(symbol)
            
            system_prompt = """You are a senior news analyst specializing in financial markets.
            Your task is to analyze news events and assess their potential impact on stock prices.
            
            Consider these factors:
            1. News relevance and credibility
            2. Potential market impact and timing
            3. Sector-wide implications
            4. Catalyst potential for price movements
            5. Risk factors and opportunities
            
            Provide analysis in JSON format:
            {
                "overall_news_sentiment": "positive|negative|neutral",
                "news_impact_score": score_0_to_1,
                "key_catalysts": ["catalyst1", "catalyst2"],
                "risk_factors": ["risk1", "risk2"],
                "sector_implications": "positive|negative|neutral",
                "timing_sensitivity": "immediate|short_term|long_term",
                "market_moving_potential": "high|medium|low",
                "news_categories": ["category1", "category2"],
                "most_impactful_news": "headline of most important news",
                "trading_recommendation": "buy_news|sell_news|hold",
                "confidence_level": confidence_0_to_100
            }"""
            
            # Prepare news summary
            news_summary = []
            for news in news_data[:5]:  # Top 5 news items
                news_summary.append(f"- {news['headline']} ({news['sentiment']}, {news['impact']} impact)")
            
            user_prompt = f"""
            Analyze news impact for {symbol}:
            
            Current Market Data:
            - Price: ${market_data.get('current_price', 0):.2f}
            - Volume: {market_data.get('volume', 0):,}
            - Price Change: {((market_data.get('current_price', 0) - market_data.get('open', 0)) / market_data.get('open', 1)) * 100:.2f}%
            
            Recent News (Last 24 hours):
            {chr(10).join(news_summary)}
            
            Total News Items: {len(news_data)}
            Positive News: {len([n for n in news_data if n['sentiment'] == 'positive'])}
            Negative News: {len([n for n in news_data if n['sentiment'] == 'negative'])}
            
            Provide comprehensive news impact analysis with trading implications.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            analysis = json.loads(response.content)
            
            logger.info(f"News analysis completed for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing news impact: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for news analysis")
            return self.generate_sample_news_analysis(market_data)
    
    def generate_sample_news_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample news analysis"""
        try:
            symbol = market_data.get('symbol', 'UNKNOWN')
            news_data = self.generate_sample_news_data(symbol)
            
            # Analyze news sentiment distribution
            positive_news = [n for n in news_data if n['sentiment'] == 'positive']
            negative_news = [n for n in news_data if n['sentiment'] == 'negative']
            neutral_news = [n for n in news_data if n['sentiment'] == 'neutral']
            
            # Determine overall sentiment
            if len(positive_news) > len(negative_news):
                overall_sentiment = "positive"
                news_impact_score = 0.7
                trading_recommendation = "buy_news"
            elif len(negative_news) > len(positive_news):
                overall_sentiment = "negative"
                news_impact_score = 0.3
                trading_recommendation = "sell_news"
            else:
                overall_sentiment = "neutral"
                news_impact_score = 0.5
                trading_recommendation = "hold"
            
            # Extract key catalysts and risks
            key_catalysts = []
            risk_factors = []
            
            for news in news_data:
                if news['sentiment'] == 'positive' and news['impact'] == 'high':
                    key_catalysts.append(news['headline'][:50] + "...")
                elif news['sentiment'] == 'negative' and news['impact'] == 'high':
                    risk_factors.append(news['headline'][:50] + "...")
            
            # Fallback if no high-impact news
            if not key_catalysts:
                key_catalysts = ["Earnings potential", "Market expansion"]
            if not risk_factors:
                risk_factors = ["Market volatility", "Competitive pressure"]
            
            # Find most impactful news
            high_impact_news = [n for n in news_data if n['impact'] == 'high']
            most_impactful = high_impact_news[0]['headline'] if high_impact_news else news_data[0]['headline']
            
            return {
                "overall_news_sentiment": overall_sentiment,
                "news_impact_score": news_impact_score,
                "key_catalysts": key_catalysts[:3],
                "risk_factors": risk_factors[:3],
                "sector_implications": "neutral",
                "timing_sensitivity": "short_term",
                "market_moving_potential": "medium",
                "news_categories": list(set([n['category'] for n in news_data])),
                "most_impactful_news": most_impactful,
                "trading_recommendation": trading_recommendation,
                "confidence_level": 75
            }
            
        except Exception as e:
            logger.error(f"Error generating sample news analysis: {str(e)}")
            return {
                "overall_news_sentiment": "neutral",
                "news_impact_score": 0.5,
                "key_catalysts": ["Sample analysis mode"],
                "risk_factors": ["Analysis unavailable"],
                "sector_implications": "neutral",
                "timing_sensitivity": "short_term",
                "market_moving_potential": "low",
                "news_categories": ["sample"],
                "most_impactful_news": "Sample news analysis",
                "trading_recommendation": "hold",
                "confidence_level": 50
            }
    
    async def process_news_analysis(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for news analysis"""
        try:
            logger.info("Processing news analysis...")
            
            market_data = state.get("market_data", {})
            if not market_data:
                raise ValueError("No market data available for news analysis")
            
            # Perform news analysis
            news_analysis = await self.analyze_news_impact(market_data)
            
            # Add agent message
            messages = state.get("messages", [])
            symbol = market_data.get('symbol', 'UNKNOWN')
            messages.append(f"News Analyst: Analysis completed for {symbol}")
            messages.append(f"News Sentiment: {news_analysis.get('overall_news_sentiment', 'neutral')}")
            messages.append(f"Impact Score: {news_analysis.get('news_impact_score', 0.5):.2f}")
            messages.append(f"Market Moving Potential: {news_analysis.get('market_moving_potential', 'medium')}")
            messages.append(f"Trading Recommendation: {news_analysis.get('trading_recommendation', 'hold')}")
            
            return {
                "news_analysis": news_analysis,
                "messages": messages
            }
            
        except Exception as e:
            logger.error(f"Error in news analysis processing: {str(e)}")
            messages = state.get("messages", [])
            messages.append(f"News Analyst: Analysis failed - {str(e)}")
            
            return {
                "news_analysis": {
                    "error": str(e),
                    "overall_news_sentiment": "neutral",
                    "news_impact_score": 0.5,
                    "confidence_level": 0
                },
                "messages": messages
            }