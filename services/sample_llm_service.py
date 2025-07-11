"""
Sample LLM Service - Provides sample AI analysis when OpenAI API is not available
"""

import json
import random
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SampleLLMService:
    """Service to provide sample AI analysis for testing"""
    
    def __init__(self):
        self.market_trends = ["bullish", "bearish", "sideways"]
        self.volatility_levels = ["high", "medium", "low"]
        self.sentiment_types = ["positive", "negative", "neutral"]
        self.signal_types = ["BUY", "SELL", "HOLD"]
        self.risk_levels = ["low", "medium", "high", "extreme"]
        
    def analyze_market_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample market context analysis"""
        try:
            current_price = market_data.get("current_price", 0)
            high = market_data.get("high", 0)
            low = market_data.get("low", 0)
            volume = market_data.get("volume", 0)
            
            # Simple analysis based on price action
            price_range = high - low if high > low else 0
            volatility = "high" if price_range > current_price * 0.02 else "medium" if price_range > current_price * 0.01 else "low"
            
            # Determine trend based on price position
            if current_price > (high + low) / 2:
                trend = "bullish"
                sentiment = "positive"
            elif current_price < (high + low) / 2:
                trend = "bearish"
                sentiment = "negative"
            else:
                trend = "sideways"
                sentiment = "neutral"
            
            return {
                "trend": trend,
                "volatility": volatility,
                "volume_analysis": f"Volume of {volume:,} indicates {'high' if volume > 1000000 else 'moderate'} trading activity",
                "support_level": round(low * 0.995, 2),
                "resistance_level": round(high * 1.005, 2),
                "sentiment": sentiment,
                "key_observations": [
                    f"Price trading at {current_price}",
                    f"Daily range: {price_range:.2f} ({(price_range/current_price)*100:.1f}%)",
                    f"Volume indicates {'strong' if volume > 1500000 else 'moderate'} interest"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in sample market analysis: {str(e)}")
            return {
                "trend": "sideways",
                "volatility": "medium",
                "volume_analysis": "Analysis unavailable",
                "support_level": 0,
                "resistance_level": 0,
                "sentiment": "neutral",
                "key_observations": ["Sample analysis mode"]
            }
    
    def analyze_technical_patterns(self, indicators: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample technical pattern analysis"""
        try:
            rsi = indicators.get("rsi", 50)
            sma_20 = indicators.get("sma_20", 0)
            sma_50 = indicators.get("sma_50", 0)
            current_price = market_data.get("current_price", 0)
            
            # Determine trend based on indicators
            if rsi > 70:
                trend_direction = "bearish"
                trend_strength = "strong"
                rsi_signal = "overbought"
            elif rsi < 30:
                trend_direction = "bullish"
                trend_strength = "strong"
                rsi_signal = "oversold"
            else:
                trend_direction = "sideways"
                trend_strength = "moderate"
                rsi_signal = "neutral"
            
            # Moving average analysis
            if sma_20 > sma_50 and current_price > sma_20:
                ma_trend = "bullish"
            elif sma_20 < sma_50 and current_price < sma_20:
                ma_trend = "bearish"
            else:
                ma_trend = "sideways"
            
            # Overall score based on multiple factors
            score = 50  # Base score
            if rsi_signal == "oversold":
                score += 15
            elif rsi_signal == "overbought":
                score -= 15
            
            if ma_trend == "bullish":
                score += 10
            elif ma_trend == "bearish":
                score -= 10
            
            return {
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "momentum": "positive" if score > 55 else "negative" if score < 45 else "neutral",
                "rsi_signal": rsi_signal,
                "macd_signal": "bullish" if score > 50 else "bearish",
                "bollinger_position": "middle",
                "support_level": round(current_price * 0.98, 2),
                "resistance_level": round(current_price * 1.02, 2),
                "entry_signals": ["RSI momentum", "Moving average crossover"],
                "exit_signals": ["Resistance test", "Volume decline"],
                "overall_score": max(0, min(100, score))
            }
            
        except Exception as e:
            logger.error(f"Error in sample technical analysis: {str(e)}")
            return {
                "trend_direction": "sideways",
                "trend_strength": "moderate",
                "momentum": "neutral",
                "rsi_signal": "neutral",
                "macd_signal": "neutral",
                "bollinger_position": "middle",
                "support_level": 0,
                "resistance_level": 0,
                "entry_signals": [],
                "exit_signals": [],
                "overall_score": 50
            }
    
    def generate_trading_signals(self, market_data: Dict[str, Any], 
                               technical_indicators: Dict[str, Any],
                               technical_analysis: Dict[str, Any],
                               market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample trading signals"""
        try:
            current_price = market_data.get("current_price", 0)
            rsi = technical_indicators.get("rsi", 50)
            trend = technical_analysis.get("trend_direction", "sideways")
            overall_score = technical_analysis.get("overall_score", 50)
            
            # Generate primary signal
            if rsi < 30 and trend == "bullish":
                primary_signal = "BUY"
                confidence = random.randint(75, 90)
                signal_strength = "strong"
            elif rsi > 70 and trend == "bearish":
                primary_signal = "SELL"
                confidence = random.randint(70, 85)
                signal_strength = "strong"
            elif overall_score > 60:
                primary_signal = "BUY"
                confidence = random.randint(60, 75)
                signal_strength = "moderate"
            elif overall_score < 40:
                primary_signal = "SELL"
                confidence = random.randint(55, 70)
                signal_strength = "moderate"
            else:
                primary_signal = "HOLD"
                confidence = random.randint(50, 65)
                signal_strength = "weak"
            
            # Calculate entry and exit levels
            stop_loss = current_price * 0.95 if primary_signal == "BUY" else current_price * 1.05
            take_profit = current_price * 1.08 if primary_signal == "BUY" else current_price * 0.92
            
            return {
                "primary_signal": primary_signal,
                "confidence": confidence,
                "signal_strength": signal_strength,
                "entry_price": current_price,
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "position_size": 0.02,  # 2% of portfolio
                "time_horizon": "short",
                "risk_level": "medium",
                "reasoning": f"Signal based on RSI ({rsi:.1f}), trend ({trend}), and overall score ({overall_score})",
                "supporting_factors": [
                    f"RSI at {rsi:.1f}",
                    f"Trend direction: {trend}",
                    f"Technical score: {overall_score}"
                ],
                "risk_factors": [
                    "Market volatility",
                    "External news impact",
                    "Volume considerations"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in sample signal generation: {str(e)}")
            return {
                "primary_signal": "HOLD",
                "confidence": 50,
                "signal_strength": "weak",
                "entry_price": 0,
                "stop_loss": 0,
                "take_profit": 0,
                "position_size": 0,
                "time_horizon": "short",
                "risk_level": "high",
                "reasoning": "Sample analysis mode",
                "supporting_factors": [],
                "risk_factors": ["Analysis unavailable"]
            }
    
    def assess_risk(self, market_data: Dict[str, Any],
                   technical_indicators: Dict[str, Any],
                   trading_signals: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample risk assessment"""
        try:
            signal = trading_signals.get("primary_signal", "HOLD")
            confidence = trading_signals.get("confidence", 50)
            volatility = technical_indicators.get("atr", 0)
            current_price = market_data.get("current_price", 0)
            
            # Calculate risk score
            risk_score = 50  # Base risk
            
            if signal == "HOLD":
                risk_score -= 20
            elif confidence < 60:
                risk_score += 15
            elif confidence > 80:
                risk_score -= 10
            
            # Volatility impact
            if volatility > current_price * 0.03:
                risk_score += 20
            elif volatility < current_price * 0.01:
                risk_score -= 10
            
            # Determine risk level
            if risk_score > 75:
                risk_level = "extreme"
                trade_approval = "rejected"
            elif risk_score > 60:
                risk_level = "high"
                trade_approval = "conditional"
            elif risk_score > 40:
                risk_level = "medium"
                trade_approval = "approved"
            else:
                risk_level = "low"
                trade_approval = "approved"
            
            return {
                "overall_risk_score": max(0, min(100, risk_score)),
                "risk_level": risk_level,
                "recommended_position_size": 0.02 if risk_level == "low" else 0.01,
                "max_acceptable_loss": 0.05,
                "stop_loss_recommendation": current_price * 0.95,
                "risk_factors": [
                    f"Market volatility: {volatility:.2f}",
                    f"Signal confidence: {confidence}%",
                    "Liquidity considerations"
                ],
                "mitigation_strategies": [
                    "Use stop-loss orders",
                    "Diversify positions",
                    "Monitor market news"
                ],
                "trade_approval": trade_approval,
                "approval_reason": f"Risk assessment complete - {risk_level} risk level"
            }
            
        except Exception as e:
            logger.error(f"Error in sample risk assessment: {str(e)}")
            return {
                "overall_risk_score": 100,
                "risk_level": "extreme",
                "recommended_position_size": 0,
                "max_acceptable_loss": 0,
                "stop_loss_recommendation": 0,
                "risk_factors": ["Analysis error"],
                "mitigation_strategies": ["Do not trade"],
                "trade_approval": "rejected",
                "approval_reason": "Risk analysis failed"
            }