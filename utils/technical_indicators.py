"""
Technical indicators calculation utilities
"""

import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Utility class for calculating technical indicators"""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        try:
            if len(prices) < period:
                return None
            return sum(prices[-period:]) / period
        except Exception as e:
            logger.error(f"Error calculating SMA: {str(e)}")
            return None
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> Optional[float]:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) < period:
                return None
            
            prices_array = np.array(prices)
            multiplier = 2 / (period + 1)
            ema = prices_array[0]
            
            for price in prices_array[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            
            return float(ema)
        except Exception as e:
            logger.error(f"Error calculating EMA: {str(e)}")
            return None
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index"""
        try:
            if len(prices) < period + 1:
                return None
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi)
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return None
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, 
                                 std_dev: float = 2) -> Optional[Dict[str, float]]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < period:
                return None
            
            sma = TechnicalIndicators.calculate_sma(prices, period)
            if sma is None:
                return None
            
            std = np.std(prices[-period:])
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return {
                "upper": float(upper_band),
                "middle": float(sma),
                "lower": float(lower_band)
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return None
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, 
                      slow_period: int = 26, signal_period: int = 9) -> Optional[Dict[str, float]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            if len(prices) < slow_period:
                return None
            
            ema_fast = TechnicalIndicators.calculate_ema(prices, fast_period)
            ema_slow = TechnicalIndicators.calculate_ema(prices, slow_period)
            
            if ema_fast is None or ema_slow is None:
                return None
            
            macd_line = ema_fast - ema_slow
            
            # For signal line, we would need MACD history
            # Simplified version returns just the MACD line
            return {
                "macd": float(macd_line),
                "signal": float(macd_line * 0.9),  # Simplified signal
                "histogram": float(macd_line * 0.1)
            }
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return None
    
    @staticmethod
    def calculate_stochastic(highs: List[float], lows: List[float], 
                           closes: List[float], period: int = 14) -> Optional[Dict[str, float]]:
        """Calculate Stochastic Oscillator"""
        try:
            if len(highs) < period or len(lows) < period or len(closes) < period:
                return None
            
            highest_high = max(highs[-period:])
            lowest_low = min(lows[-period:])
            current_close = closes[-1]
            
            if highest_high == lowest_low:
                k_percent = 50.0
            else:
                k_percent = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
            
            # Simplified %D (usually 3-period SMA of %K)
            d_percent = k_percent * 0.9  # Simplified
            
            return {
                "k_percent": float(k_percent),
                "d_percent": float(d_percent)
            }
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {str(e)}")
            return None
    
    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], 
                     closes: List[float], period: int = 14) -> Optional[float]:
        """Calculate Average True Range"""
        try:
            if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
                return None
            
            true_ranges = []
            for i in range(1, len(highs)):
                high_low = highs[i] - lows[i]
                high_close = abs(highs[i] - closes[i-1])
                low_close = abs(lows[i] - closes[i-1])
                
                true_range = max(high_low, high_close, low_close)
                true_ranges.append(true_range)
            
            if len(true_ranges) < period:
                return None
            
            atr = sum(true_ranges[-period:]) / period
            return float(atr)
        except Exception as e:
            logger.error(f"Error calculating ATR: {str(e)}")
            return None
    
    @staticmethod
    def calculate_volume_indicators(volumes: List[float], prices: List[float]) -> Dict[str, Any]:
        """Calculate volume-based indicators"""
        try:
            if len(volumes) < 2 or len(prices) < 2:
                return {}
            
            # Volume SMA
            volume_sma_20 = TechnicalIndicators.calculate_sma(volumes, min(20, len(volumes)))
            
            # On-Balance Volume (simplified)
            obv = 0
            for i in range(1, len(prices)):
                if prices[i] > prices[i-1]:
                    obv += volumes[i]
                elif prices[i] < prices[i-1]:
                    obv -= volumes[i]
            
            return {
                "volume_sma_20": volume_sma_20,
                "obv": obv,
                "volume_ratio": volumes[-1] / volume_sma_20 if volume_sma_20 else 1.0
            }
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {str(e)}")
            return {}
