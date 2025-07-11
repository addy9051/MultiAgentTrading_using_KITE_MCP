"""
Configuration settings for the Multi-Agent Trading System
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Settings:
    """Configuration settings loaded from environment variables"""
    
    # Kite Connect API Configuration
    KITE_API_KEY: str = os.getenv("KITE_API_KEY", "")
    KITE_API_SECRET: str = os.getenv("KITE_API_SECRET", "")
    KITE_ACCESS_TOKEN: str = os.getenv("KITE_ACCESS_TOKEN", "")
    KITE_MCP_URL: str = os.getenv("KITE_MCP_URL", "http://localhost:8080")
    
    # OpenAI Configuration
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Trading Configuration
    TARGET_SYMBOL: str = os.getenv("TARGET_SYMBOL", "RELIANCE")
    EXCHANGE: str = os.getenv("EXCHANGE", "NSE")
    QUANTITY: int = int(os.getenv("QUANTITY", "1"))
    
    # Strategy Configuration
    RSI_PERIOD: int = int(os.getenv("RSI_PERIOD", "14"))
    RSI_OVERBOUGHT: float = float(os.getenv("RSI_OVERBOUGHT", "70.0"))
    RSI_OVERSOLD: float = float(os.getenv("RSI_OVERSOLD", "30.0"))
    
    # Risk Management
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "0.02"))  # 2% of portfolio
    STOP_LOSS_PERCENT: float = float(os.getenv("STOP_LOSS_PERCENT", "0.05"))  # 5% stop loss
    
    # System Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SIMULATION_MODE: bool = os.getenv("SIMULATION_MODE", "true").lower() == "true"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        # Only validate API keys when not in simulation mode
        if not self.SIMULATION_MODE:
            if not self.KITE_API_KEY:
                raise ValueError("KITE_API_KEY environment variable is required")
            if not self.KITE_API_SECRET:
                raise ValueError("KITE_API_SECRET environment variable is required")
            if not self.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def get_instrument_token(self) -> str:
        """Get the full instrument identifier"""
        return f"{self.EXCHANGE}:{self.TARGET_SYMBOL}"
