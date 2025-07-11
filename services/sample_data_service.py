"""
Sample Data Service - Provides realistic sample market data for testing
"""

import random
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SampleDataService:
    """Service to provide realistic sample market data for testing"""
    
    def __init__(self):
        self.base_prices = {
            "RELIANCE": 2450.75,
            "TCS": 3280.50,
            "INFY": 1645.25,
            "HDFCBANK": 1510.80,
            "ICICIBANK": 1125.40,
            "SBIN": 805.20,
            "BHARTIARTL": 1185.65,
            "ITC": 415.30,
            "HINDUNILVR": 2380.90,
            "KOTAKBANK": 1720.15
        }
    
    def get_sample_quote(self, symbol: str) -> Dict[str, Any]:
        """Generate realistic sample quote data"""
        try:
            base_price = self.base_prices.get(symbol, 1000.0)
            
            # Add realistic price variation (+/- 2%)
            price_variation = random.uniform(-0.02, 0.02)
            current_price = base_price * (1 + price_variation)
            
            # Generate OHLC data
            high = current_price * random.uniform(1.001, 1.015)
            low = current_price * random.uniform(0.985, 0.999)
            open_price = current_price * random.uniform(0.995, 1.005)
            
            return {
                "instrument_token": str(hash(symbol) % 1000000),
                "last_price": round(current_price, 2),
                "volume": random.randint(500000, 2000000),
                "ohlc": {
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(current_price, 2)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating sample quote: {str(e)}")
            return {}
    
    def get_sample_historical_data(self, symbol: str, interval: str = "15minute", 
                                  days: int = 30) -> List[Dict[str, Any]]:
        """Generate realistic historical data"""
        try:
            base_price = self.base_prices.get(symbol, 1000.0)
            historical_data = []
            
            # Generate data points based on interval
            if interval == "15minute":
                total_points = days * 24 * 4  # 4 points per hour
            elif interval == "1hour":
                total_points = days * 24
            elif interval == "1day":
                total_points = days
            else:
                total_points = days * 24 * 4  # Default to 15minute
            
            # Start from base price and create realistic movements
            current_price = base_price
            
            for i in range(total_points):
                # Random walk with slight upward bias
                price_change = random.uniform(-0.008, 0.010)  # -0.8% to +1.0%
                current_price *= (1 + price_change)
                
                # Generate OHLC for this period
                high = current_price * random.uniform(1.001, 1.008)
                low = current_price * random.uniform(0.992, 0.999)
                open_price = current_price * random.uniform(0.998, 1.002)
                volume = random.randint(10000, 50000)
                
                # Calculate timestamp
                if interval == "15minute":
                    time_delta = timedelta(minutes=15 * i)
                elif interval == "1hour":
                    time_delta = timedelta(hours=i)
                else:
                    time_delta = timedelta(days=i)
                
                timestamp = datetime.now() - timedelta(days=days) + time_delta
                
                historical_data.append({
                    "timestamp": timestamp.isoformat(),
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(current_price, 2),
                    "volume": volume
                })
            
            # Sort by timestamp (oldest first)
            historical_data.sort(key=lambda x: x["timestamp"])
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error generating sample historical data: {str(e)}")
            return []
    
    def get_sample_profile(self) -> Dict[str, Any]:
        """Generate sample user profile"""
        return {
            "user_id": "sample_user_123",
            "user_name": "Sample Trader",
            "email": "sample@example.com",
            "broker": "SAMPLE_BROKER",
            "account_type": "DEMO",
            "enabled": True
        }
    
    def get_sample_positions(self) -> List[Dict[str, Any]]:
        """Generate sample positions"""
        return [
            {
                "tradingsymbol": "RELIANCE",
                "exchange": "NSE",
                "quantity": 10,
                "average_price": 2440.50,
                "last_price": 2450.75,
                "pnl": 102.50,
                "product": "CNC"
            }
        ]
    
    def get_sample_holdings(self) -> List[Dict[str, Any]]:
        """Generate sample holdings"""
        return [
            {
                "tradingsymbol": "TCS",
                "exchange": "NSE",
                "quantity": 5,
                "average_price": 3250.00,
                "last_price": 3280.50,
                "pnl": 152.50,
                "product": "CNC"
            }
        ]
    
    def simulate_order_placement(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate order placement with realistic response"""
        try:
            order_id = f"SAMPLE_{order_data.get('symbol', 'UNKNOWN')}_{random.randint(100000, 999999)}"
            
            # Simulate order success/failure based on market conditions
            success_rate = 0.95  # 95% success rate
            if random.random() < success_rate:
                return {
                    "order_id": order_id,
                    "status": "COMPLETE",
                    "message": "Order placed successfully (sample data)",
                    "order_timestamp": datetime.now().isoformat(),
                    "filled_quantity": order_data.get("quantity", 0),
                    "average_price": order_data.get("price", 0)
                }
            else:
                return {
                    "order_id": order_id,
                    "status": "REJECTED",
                    "message": "Order rejected due to insufficient funds (sample)",
                    "order_timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error simulating order placement: {str(e)}")
            return {"error": str(e)}
    
    def get_market_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Generate sample market news"""
        news_templates = [
            f"{symbol} reports strong quarterly earnings",
            f"{symbol} announces new strategic partnership",
            f"{symbol} stock rises on positive analyst outlook",
            f"{symbol} faces regulatory scrutiny",
            f"{symbol} expands operations in new markets"
        ]
        
        return [
            {
                "headline": random.choice(news_templates),
                "summary": f"Sample news article about {symbol} for testing purposes.",
                "sentiment": random.choice(["positive", "negative", "neutral"]),
                "timestamp": datetime.now().isoformat(),
                "source": "Sample News Agency"
            }
        ]