"""
Fundamentals Analyst Agent - Evaluates company financials, earnings, and market metrics
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

class FundamentalsAnalyst:
    """Agent responsible for fundamental analysis of companies and markets"""
    
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
    
    def calculate_basic_metrics(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic fundamental metrics"""
        try:
            current_price = market_data.get('current_price', 0)
            volume = market_data.get('volume', 0)
            high = market_data.get('high', 0)
            low = market_data.get('low', 0)
            
            # Basic valuation metrics (sample calculations)
            price_range = high - low if high > low else 0
            volatility = (price_range / current_price) * 100 if current_price > 0 else 0
            
            # Volume analysis
            volume_strength = "high" if volume > 1000000 else "medium" if volume > 500000 else "low"
            
            # Price momentum
            mid_price = (high + low) / 2 if high > 0 and low > 0 else current_price
            price_position = ((current_price - low) / (high - low)) * 100 if high > low else 50
            
            return {
                "current_price": current_price,
                "price_volatility": round(volatility, 2),
                "volume_strength": volume_strength,
                "price_position": round(price_position, 2),
                "daily_range": round(price_range, 2),
                "market_cap_indicator": "large" if current_price > 2000 else "medium" if current_price > 500 else "small"
            }
            
        except Exception as e:
            logger.error(f"Error calculating basic metrics: {str(e)}")
            return {}
    
    async def analyze_company_fundamentals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company fundamentals using LLM"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for fundamentals analysis")
                return self.generate_sample_fundamentals_analysis(market_data)
            
            symbol = market_data.get('symbol', 'UNKNOWN')
            basic_metrics = self.calculate_basic_metrics(market_data)
            
            system_prompt = """You are a senior fundamentals analyst at a top investment firm.
            Your task is to evaluate company fundamentals and provide detailed analysis.
            
            Consider these factors:
            1. Company financial health and earnings potential
            2. Market position and competitive advantages
            3. Industry trends and sector performance
            4. Valuation metrics and growth prospects
            5. Risk factors and potential catalysts
            
            Provide analysis in JSON format:
            {
                "financial_health": "strong|moderate|weak",
                "valuation_assessment": "undervalued|fairly_valued|overvalued",
                "growth_potential": "high|medium|low",
                "competitive_position": "strong|moderate|weak",
                "sector_outlook": "positive|neutral|negative",
                "key_strengths": ["strength1", "strength2"],
                "key_risks": ["risk1", "risk2"],
                "price_target": price_estimate,
                "investment_thesis": "detailed reasoning",
                "recommendation": "BUY|HOLD|SELL",
                "confidence_level": confidence_0_to_100
            }"""
            
            user_prompt = f"""
            Analyze the fundamentals for {symbol}:
            
            Current Market Data:
            - Price: ${basic_metrics.get('current_price', 0):.2f}
            - Market Cap Category: {basic_metrics.get('market_cap_indicator', 'unknown')}
            - Price Volatility: {basic_metrics.get('price_volatility', 0):.2f}%
            - Volume Strength: {basic_metrics.get('volume_strength', 'unknown')}
            - Price Position in Range: {basic_metrics.get('price_position', 0):.1f}%
            
            Provide comprehensive fundamentals analysis considering current market conditions.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            analysis = json.loads(response.content)
            
            logger.info(f"Fundamentals analysis completed for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing fundamentals: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for fundamentals analysis")
            return self.generate_sample_fundamentals_analysis(market_data)
    
    def generate_sample_fundamentals_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample fundamentals analysis"""
        try:
            symbol = market_data.get('symbol', 'UNKNOWN')
            current_price = market_data.get('current_price', 0)
            basic_metrics = self.calculate_basic_metrics(market_data)
            
            # Generate realistic analysis based on price and market data
            if current_price > 2000:
                financial_health = "strong"
                valuation = "fairly_valued"
                growth_potential = "medium"
                competitive_position = "strong"
            elif current_price > 1000:
                financial_health = "moderate"
                valuation = "undervalued"
                growth_potential = "high"
                competitive_position = "moderate"
            else:
                financial_health = "moderate"
                valuation = "fairly_valued"
                growth_potential = "medium"
                competitive_position = "moderate"
            
            # Price target based on current price
            price_target = current_price * 1.15  # 15% upside potential
            
            return {
                "financial_health": financial_health,
                "valuation_assessment": valuation,
                "growth_potential": growth_potential,
                "competitive_position": competitive_position,
                "sector_outlook": "positive",
                "key_strengths": [
                    "Strong market position",
                    "Consistent earnings growth",
                    "Robust balance sheet"
                ],
                "key_risks": [
                    "Market volatility",
                    "Regulatory changes",
                    "Competition pressure"
                ],
                "price_target": round(price_target, 2),
                "investment_thesis": f"Based on current price of ${current_price:.2f}, the company shows {financial_health} fundamentals with {growth_potential} growth potential. The stock appears {valuation} at current levels.",
                "recommendation": "HOLD" if valuation == "fairly_valued" else "BUY",
                "confidence_level": 75
            }
            
        except Exception as e:
            logger.error(f"Error generating sample fundamentals analysis: {str(e)}")
            return {
                "financial_health": "moderate",
                "valuation_assessment": "fairly_valued",
                "growth_potential": "medium",
                "competitive_position": "moderate",
                "sector_outlook": "neutral",
                "key_strengths": ["Sample analysis mode"],
                "key_risks": ["Analysis unavailable"],
                "price_target": 0,
                "investment_thesis": "Sample fundamentals analysis",
                "recommendation": "HOLD",
                "confidence_level": 50
            }
    
    async def process_fundamentals_analysis(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for fundamentals analysis"""
        try:
            logger.info("Processing fundamentals analysis...")
            
            market_data = state.get("market_data", {})
            if not market_data:
                raise ValueError("No market data available for fundamentals analysis")
            
            # Perform fundamentals analysis
            fundamentals_analysis = await self.analyze_company_fundamentals(market_data)
            
            # Add agent message
            messages = state.get("messages", [])
            symbol = market_data.get('symbol', 'UNKNOWN')
            messages.append(f"Fundamentals Analyst: Analysis completed for {symbol}")
            messages.append(f"Financial Health: {fundamentals_analysis.get('financial_health', 'unknown')}")
            messages.append(f"Valuation: {fundamentals_analysis.get('valuation_assessment', 'unknown')}")
            messages.append(f"Recommendation: {fundamentals_analysis.get('recommendation', 'HOLD')}")
            messages.append(f"Price Target: ${fundamentals_analysis.get('price_target', 0):.2f}")
            
            return {
                "fundamentals_analysis": fundamentals_analysis,
                "messages": messages
            }
            
        except Exception as e:
            logger.error(f"Error in fundamentals analysis processing: {str(e)}")
            messages = state.get("messages", [])
            messages.append(f"Fundamentals Analyst: Analysis failed - {str(e)}")
            
            return {
                "fundamentals_analysis": {
                    "error": str(e),
                    "financial_health": "unknown",
                    "recommendation": "HOLD",
                    "confidence_level": 0
                },
                "messages": messages
            }