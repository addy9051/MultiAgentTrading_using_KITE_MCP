"""
Risk Assessment Agent - Evaluates and manages trading risks
"""

import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from models.trading_state import TradingState
from services.sample_llm_service import SampleLLMService
import json

logger = logging.getLogger(__name__)

class RiskAssessmentAgent:
    """Agent responsible for risk assessment and management"""
    
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
    
    def calculate_position_size(self, account_balance: float, risk_per_trade: float, 
                              entry_price: float, stop_loss: float) -> Dict[str, Any]:
        """Calculate optimal position size based on risk management rules"""
        try:
            if stop_loss == 0 or entry_price == 0:
                return {"position_size": 0, "risk_amount": 0, "shares": 0}
            
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            # Calculate maximum risk amount
            max_risk_amount = account_balance * risk_per_trade
            
            # Calculate position size
            shares = int(max_risk_amount / risk_per_share)
            actual_position_size = shares * entry_price
            actual_risk_amount = shares * risk_per_share
            
            return {
                "position_size": actual_position_size,
                "risk_amount": actual_risk_amount,
                "shares": shares,
                "risk_per_share": risk_per_share,
                "risk_percentage": (actual_risk_amount / account_balance) * 100
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return {"position_size": 0, "risk_amount": 0, "shares": 0}
    
    def assess_market_risk(self, market_data: Dict[str, Any], technical_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market-specific risks"""
        try:
            risks = {}
            
            # Volatility risk
            atr = technical_indicators.get('atr', 0)
            current_price = market_data.get('current_price', 0)
            if current_price > 0:
                volatility_percent = (atr / current_price) * 100
                if volatility_percent > 5:
                    risks['volatility'] = 'high'
                elif volatility_percent > 2:
                    risks['volatility'] = 'medium'
                else:
                    risks['volatility'] = 'low'
            
            # Volume risk
            volume = market_data.get('volume', 0)
            volume_sma = technical_indicators.get('volume_sma', 0)
            if volume_sma > 0:
                volume_ratio = volume / volume_sma
                if volume_ratio < 0.5:
                    risks['liquidity'] = 'high'
                elif volume_ratio < 0.8:
                    risks['liquidity'] = 'medium'
                else:
                    risks['liquidity'] = 'low'
            
            # Price gap risk
            open_price = market_data.get('open', 0)
            close_price = market_data.get('close', 0)
            if close_price > 0:
                gap_percent = abs((open_price - close_price) / close_price) * 100
                if gap_percent > 3:
                    risks['gap'] = 'high'
                elif gap_percent > 1:
                    risks['gap'] = 'medium'
                else:
                    risks['gap'] = 'low'
            
            return risks
            
        except Exception as e:
            logger.error(f"Error assessing market risk: {str(e)}")
            return {}
    
    async def comprehensive_risk_analysis(self, state: TradingState) -> Dict[str, Any]:
        """Perform comprehensive risk analysis using LLM"""
        try:
            # Use sample LLM service if no OpenAI API key
            if self.use_sample_llm:
                logger.info("Using sample LLM service for risk analysis")
                market_data = state.get("market_data", {})
                technical_indicators = state.get("technical_indicators", {})
                trading_signals = state.get("trading_signals", {})
                return self.sample_llm_service.assess_risk(market_data, technical_indicators, trading_signals)
            
            market_data = state.get("market_data", {})
            technical_indicators = state.get("technical_indicators", {})
            trading_signals = state.get("trading_signals", {})
            
            system_prompt = """You are a risk management expert. 
            Analyze the provided trading scenario and assess all relevant risks.
            
            Consider:
            1. Market volatility and liquidity
            2. Technical indicator reliability
            3. Signal strength and confidence
            4. Economic and sector-specific risks
            5. Position sizing and portfolio impact
            
            Respond in JSON format with the following structure:
            {
                "overall_risk_score": score_0_to_100,
                "risk_level": "low|medium|high|extreme",
                "recommended_position_size": percentage_of_portfolio,
                "max_acceptable_loss": percentage,
                "stop_loss_recommendation": price,
                "risk_factors": ["factor1", "factor2"],
                "mitigation_strategies": ["strategy1", "strategy2"],
                "trade_approval": "approved|conditional|rejected",
                "approval_reason": "detailed explanation"
            }"""
            
            user_prompt = f"""
            Assess the risk for this trading scenario:
            
            Market Data:
            - Symbol: {market_data.get('symbol', 'N/A')}
            - Current Price: {market_data.get('current_price', 'N/A')}
            - Volume: {market_data.get('volume', 'N/A')}
            - Volatility (ATR): {technical_indicators.get('atr', 'N/A')}
            
            Trading Signal:
            - Signal: {trading_signals.get('final_signal', 'N/A')}
            - Confidence: {trading_signals.get('confidence', 'N/A')}%
            - Entry Price: {trading_signals.get('advanced_signals', {}).get('entry_price', 'N/A')}
            - Stop Loss: {trading_signals.get('advanced_signals', {}).get('stop_loss', 'N/A')}
            
            Risk Parameters:
            - Max Position Size: {self.settings.MAX_POSITION_SIZE * 100}%
            - Stop Loss Percent: {self.settings.STOP_LOSS_PERCENT * 100}%
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parse the JSON response
            risk_analysis = json.loads(response.content)
            
            logger.info(f"Risk analysis completed: {risk_analysis['risk_level']}")
            return risk_analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive risk analysis: {str(e)}")
            # Fallback to sample service
            logger.info("Falling back to sample LLM service for risk analysis")
            market_data = state.get("market_data", {})
            technical_indicators = state.get("technical_indicators", {})
            trading_signals = state.get("trading_signals", {})
            return self.sample_llm_service.assess_risk(market_data, technical_indicators, trading_signals)
    
    async def process_risk_assessment(self, state: TradingState) -> Dict[str, Any]:
        """Main processing function for risk assessment"""
        try:
            market_data = state.get("market_data", {})
            technical_indicators = state.get("technical_indicators", {})
            trading_signals = state.get("trading_signals", {})
            
            # Assess market-specific risks
            market_risks = self.assess_market_risk(market_data, technical_indicators)
            
            # Perform comprehensive risk analysis
            comprehensive_analysis = await self.comprehensive_risk_analysis(state)
            
            # Calculate position sizing
            advanced_signals = trading_signals.get("advanced_signals", {})
            position_sizing = self.calculate_position_size(
                account_balance=100000,  # Mock account balance
                risk_per_trade=self.settings.MAX_POSITION_SIZE,
                entry_price=advanced_signals.get("entry_price", 0),
                stop_loss=advanced_signals.get("stop_loss", 0)
            )
            
            # Combine all risk assessments
            risk_assessment = {
                "market_risks": market_risks,
                "comprehensive_analysis": comprehensive_analysis,
                "position_sizing": position_sizing,
                "final_approval": comprehensive_analysis.get("trade_approval", "rejected"),
                "risk_score": comprehensive_analysis.get("overall_risk_score", 100)
            }
            
            # Update state
            updated_state = {
                "risk_assessment": risk_assessment,
                "messages": state.get("messages", []) + [
                    f"Risk Assessment Agent: Analysis completed",
                    f"Risk Level: {comprehensive_analysis.get('risk_level', 'unknown')}",
                    f"Trade Approval: {comprehensive_analysis.get('trade_approval', 'rejected')}",
                    f"Recommended Position: {position_sizing.get('shares', 0)} shares"
                ]
            }
            
            return updated_state
            
        except Exception as e:
            logger.error(f"Error processing risk assessment: {str(e)}")
            return {
                "error": str(e),
                "messages": state.get("messages", []) + [
                    f"Risk Assessment Agent: Error in risk assessment - {str(e)}"
                ]
            }
