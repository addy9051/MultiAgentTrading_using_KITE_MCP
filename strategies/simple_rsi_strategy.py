"""
Simple RSI Strategy - Basic trading strategy based on RSI indicator
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SimpleRSIStrategy:
    """Simple RSI-based trading strategy"""
    
    def __init__(self, settings):
        self.settings = settings
        self.rsi_overbought = settings.RSI_OVERBOUGHT
        self.rsi_oversold = settings.RSI_OVERSOLD
    
    def generate_signal(self, technical_indicators: Dict[str, Any], 
                       market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signal based on RSI"""
        try:
            rsi = technical_indicators.get('rsi', 50)
            current_price = market_data.get('current_price', 0)
            
            signal_data = {
                'rsi_value': rsi,
                'rsi_signal': 'HOLD',
                'signal_strength': 'weak',
                'entry_price': current_price,
                'stop_loss': 0,
                'take_profit': 0
            }
            
            # RSI oversold condition - potential buy signal
            if rsi < self.rsi_oversold:
                signal_data['rsi_signal'] = 'BUY'
                signal_data['signal_strength'] = 'strong' if rsi < 25 else 'moderate'
                signal_data['stop_loss'] = current_price * (1 - self.settings.STOP_LOSS_PERCENT)
                signal_data['take_profit'] = current_price * (1 + self.settings.STOP_LOSS_PERCENT * 2)
                
            # RSI overbought condition - potential sell signal
            elif rsi > self.rsi_overbought:
                signal_data['rsi_signal'] = 'SELL'
                signal_data['signal_strength'] = 'strong' if rsi > 75 else 'moderate'
                signal_data['stop_loss'] = current_price * (1 + self.settings.STOP_LOSS_PERCENT)
                signal_data['take_profit'] = current_price * (1 - self.settings.STOP_LOSS_PERCENT * 2)
            
            # Log the signal
            logger.info(f"RSI Strategy Signal: {signal_data['rsi_signal']} "
                       f"(RSI: {rsi:.2f}, Strength: {signal_data['signal_strength']})")
            
            return signal_data
            
        except Exception as e:
            logger.error(f"Error generating RSI signal: {str(e)}")
            return {
                'rsi_value': 50,
                'rsi_signal': 'HOLD',
                'signal_strength': 'weak',
                'entry_price': 0,
                'stop_loss': 0,
                'take_profit': 0
            }
    
    def validate_signal(self, signal_data: Dict[str, Any], 
                       market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated signal against market conditions"""
        try:
            # Add validation logic here
            # For now, just return the signal as-is
            validated_signal = signal_data.copy()
            
            # Add volume confirmation
            volume = market_context.get('volume', 0)
            volume_sma = market_context.get('volume_sma', 0)
            
            if volume_sma > 0:
                volume_ratio = volume / volume_sma
                if volume_ratio < 0.5:
                    # Low volume, reduce signal strength
                    if validated_signal['signal_strength'] == 'strong':
                        validated_signal['signal_strength'] = 'moderate'
                    elif validated_signal['signal_strength'] == 'moderate':
                        validated_signal['signal_strength'] = 'weak'
            
            return validated_signal
            
        except Exception as e:
            logger.error(f"Error validating RSI signal: {str(e)}")
            return signal_data
