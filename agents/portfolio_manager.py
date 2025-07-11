"""
Portfolio Manager Agent - Makes final trading decisions and manages portfolio
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

class PortfolioManager:
    """Agent responsible for final trading decisions and portfolio management"""
    
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
                temperature=0.1  # Conservative temperature for final decisions
            )
    
    async def make_portfolio_decision(self, state: TradingState) -> Dict[str, Any]:
        """Make final portfolio decision based on all analysis"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for portfolio decision")
                return self.generate_sample_portfolio_decision(state)
            
            # Extract all analysis data
            market_data = state.get("market_data", {})
            fundamentals = state.get("fundamentals_analysis", {})
            sentiment = state.get("sentiment_analysis", {})
            news = state.get("news_analysis", {})
            technical = state.get("technical_analysis", {})
            bull_research = state.get("bull_research", {})
            bear_research = state.get("bear_research", {})
            risk_assessment = state.get("risk_assessment", {})
            
            symbol = market_data.get('symbol', 'UNKNOWN')
            
            system_prompt = """You are a senior portfolio manager at a top investment firm.
            Your role is to make final trading decisions based on comprehensive analysis from all teams.
            
            Consider:
            1. All analyst reports and research findings
            2. Bull vs Bear research debates
            3. Risk management recommendations
            4. Portfolio optimization and diversification
            5. Market timing and execution strategy
            
            Make decisive, well-reasoned decisions with clear rationale.
            
            Provide decision in JSON format:
            {
                "final_decision": "BUY|SELL|HOLD|REDUCE|ACCUMULATE",
                "position_size": "percentage_of_portfolio",
                "entry_price": target_entry_price,
                "stop_loss": stop_loss_price,
                "take_profit": take_profit_price,
                "time_horizon": "short_term|medium_term|long_term",
                "execution_strategy": "detailed execution plan",
                "portfolio_impact": "how this affects overall portfolio",
                "decision_rationale": "comprehensive reasoning",
                "key_considerations": ["consideration1", "consideration2"],
                "risk_reward_ratio": ratio_number,
                "confidence_level": confidence_0_to_100,
                "review_triggers": ["trigger1", "trigger2"]
            }"""
            
            user_prompt = f"""
            Make final portfolio decision for {symbol}:
            
            === MARKET DATA ===
            Current Price: ${market_data.get('current_price', 0):.2f}
            Volume: {market_data.get('volume', 0):,}
            
            === FUNDAMENTALS ANALYSIS ===
            Financial Health: {fundamentals.get('financial_health', 'unknown')}
            Valuation: {fundamentals.get('valuation_assessment', 'unknown')}
            Recommendation: {fundamentals.get('recommendation', 'HOLD')}
            Price Target: ${fundamentals.get('price_target', 0):.2f}
            
            === SENTIMENT ANALYSIS ===
            Overall Sentiment: {sentiment.get('overall_sentiment', 'neutral')}
            Sentiment Score: {sentiment.get('sentiment_score', 0.5):.2f}
            Trading Implications: {sentiment.get('trading_implications', 'sideways_action')}
            
            === NEWS ANALYSIS ===
            News Sentiment: {news.get('overall_news_sentiment', 'neutral')}
            Trading Recommendation: {news.get('trading_recommendation', 'hold')}
            Market Moving Potential: {news.get('market_moving_potential', 'medium')}
            
            === TECHNICAL ANALYSIS ===
            Trend Direction: {technical.get('trend_direction', 'sideways')}
            Overall Score: {technical.get('overall_score', 50)}
            
            === BULL RESEARCH ===
            Thesis: {bull_research.get('bullish_thesis', 'N/A')[:100]}...
            Upside Potential: {bull_research.get('upside_potential', 'unknown')}
            Recommendation: {bull_research.get('recommended_action', 'WAIT')}
            Confidence: {bull_research.get('confidence_level', 0)}%
            
            === BEAR RESEARCH ===
            Thesis: {bear_research.get('bearish_thesis', 'N/A')[:100]}...
            Downside Potential: {bear_research.get('downside_potential', 'unknown')}
            Recommendation: {bear_research.get('recommended_action', 'AVOID')}
            Confidence: {bear_research.get('confidence_level', 0)}%
            
            === RISK ASSESSMENT ===
            Risk Level: {risk_assessment.get('risk_level', 'medium')}
            Trade Approval: {risk_assessment.get('trade_approval', 'conditional')}
            Position Size: {risk_assessment.get('recommended_position_size', 0.01)}
            
            Based on all analysis, make a comprehensive portfolio decision with clear execution plan.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            decision = json.loads(response.content)
            
            logger.info(f"Portfolio decision completed for {symbol}: {decision.get('final_decision', 'UNKNOWN')}")
            return decision
            
        except Exception as e:
            logger.error(f"Error making portfolio decision: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for portfolio decision")
            return self.generate_sample_portfolio_decision(state)
    
    def generate_sample_portfolio_decision(self, state: TradingState) -> Dict[str, Any]:
        """Generate sample portfolio decision"""
        try:
            market_data = state.get("market_data", {})
            symbol = market_data.get('symbol', 'UNKNOWN')
            current_price = market_data.get('current_price', 0)
            
            # Gather all recommendations
            fundamentals = state.get("fundamentals_analysis", {})
            sentiment = state.get("sentiment_analysis", {})
            news = state.get("news_analysis", {})
            bull_research = state.get("bull_research", {})
            bear_research = state.get("bear_research", {})
            risk_assessment = state.get("risk_assessment", {})
            
            # Score different recommendations
            recommendations = []
            if fundamentals.get('recommendation') == 'BUY':
                recommendations.append('BUY')
            elif fundamentals.get('recommendation') == 'SELL':
                recommendations.append('SELL')
            else:
                recommendations.append('HOLD')
            
            if sentiment.get('trading_implications') == 'buy_momentum':
                recommendations.append('BUY')
            elif sentiment.get('trading_implications') == 'sell_pressure':
                recommendations.append('SELL')
            else:
                recommendations.append('HOLD')
            
            if news.get('trading_recommendation') == 'buy_news':
                recommendations.append('BUY')
            elif news.get('trading_recommendation') == 'sell_news':
                recommendations.append('SELL')
            else:
                recommendations.append('HOLD')
            
            # Count recommendations
            buy_count = recommendations.count('BUY')
            sell_count = recommendations.count('SELL')
            hold_count = recommendations.count('HOLD')
            
            # Make final decision
            if buy_count > sell_count and buy_count > hold_count:
                final_decision = "BUY"
                position_size = "1.5%"
            elif sell_count > buy_count and sell_count > hold_count:
                final_decision = "SELL"
                position_size = "0%"
            else:
                final_decision = "HOLD"
                position_size = "1%"
            
            # Calculate price targets
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.10
            
            # Risk-reward ratio
            risk_reward_ratio = (take_profit - current_price) / (current_price - stop_loss) if current_price > stop_loss else 1.0
            
            return {
                "final_decision": final_decision,
                "position_size": position_size,
                "entry_price": current_price,
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "time_horizon": "medium_term",
                "execution_strategy": f"Execute {final_decision} order with position size {position_size} of portfolio",
                "portfolio_impact": f"Adding {position_size} allocation to {symbol}",
                "decision_rationale": f"Based on consensus from analyst teams. Buy signals: {buy_count}, Sell signals: {sell_count}, Hold signals: {hold_count}",
                "key_considerations": [
                    "Risk management through stop-loss",
                    "Position sizing based on volatility",
                    "Regular review of thesis"
                ],
                "risk_reward_ratio": round(risk_reward_ratio, 2),
                "confidence_level": 75,
                "review_triggers": [
                    "10% price movement",
                    "Significant news events",
                    "Change in fundamentals"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating sample portfolio decision: {str(e)}")
            return {
                "final_decision": "HOLD",
                "position_size": "0%",
                "entry_price": 0,
                "stop_loss": 0,
                "take_profit": 0,
                "time_horizon": "medium_term",
                "execution_strategy": "Sample execution strategy",
                "portfolio_impact": "No impact",
                "decision_rationale": "Sample decision rationale",
                "key_considerations": ["Sample considerations"],
                "risk_reward_ratio": 1.0,
                "confidence_level": 50,
                "review_triggers": ["Sample triggers"]
            }
    
    async def process_portfolio_decision(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for portfolio decision"""
        try:
            logger.info("Processing portfolio decision...")
            
            # Make portfolio decision
            portfolio_decision = await self.make_portfolio_decision(state)
            
            # Add agent message
            messages = state.get("messages", [])
            symbol = state.get("market_data", {}).get('symbol', 'UNKNOWN')
            messages.append(f"Portfolio Manager: Final decision for {symbol}")
            messages.append(f"Decision: {portfolio_decision.get('final_decision', 'UNKNOWN')}")
            messages.append(f"Position Size: {portfolio_decision.get('position_size', '0%')}")
            messages.append(f"Entry Price: ${portfolio_decision.get('entry_price', 0):.2f}")
            messages.append(f"Risk-Reward Ratio: {portfolio_decision.get('risk_reward_ratio', 1.0):.2f}")
            messages.append(f"Confidence: {portfolio_decision.get('confidence_level', 0)}%")
            
            return {
                "portfolio_decision": portfolio_decision,
                "messages": messages
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio decision processing: {str(e)}")
            messages = state.get("messages", [])
            messages.append(f"Portfolio Manager: Decision failed - {str(e)}")
            
            return {
                "portfolio_decision": {
                    "error": str(e),
                    "final_decision": "HOLD",
                    "position_size": "0%",
                    "confidence_level": 0
                },
                "messages": messages
            }