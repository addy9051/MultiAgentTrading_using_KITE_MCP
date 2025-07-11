"""
Trading State - Defines the state structure for the multi-agent system
"""

from typing import Dict, Any, List, Optional, TypedDict
from typing_extensions import Annotated

class TradingState(TypedDict):
    """State structure for the trading system"""
    
    # Basic information
    symbol: str
    timestamp: str
    cycle_id: str
    messages: Annotated[List[str], "List of messages from agents"]
    
    # Market data
    market_data: Optional[Dict[str, Any]]
    market_analysis: Optional[Dict[str, Any]]
    
    # Technical analysis
    technical_indicators: Optional[Dict[str, Any]]
    technical_analysis: Optional[Dict[str, Any]]
    
    # Trading signals
    trading_signals: Optional[Dict[str, Any]]
    
    # Risk assessment
    risk_assessment: Optional[Dict[str, Any]]
    
    # Execution results
    execution_result: Optional[Dict[str, Any]]
    
    # Error handling
    error: Optional[str]
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]]

class MarketData(TypedDict):
    """Market data structure"""
    symbol: str
    current_price: float
    volume: int
    high: float
    low: float
    open: float
    close: float
    historical_data: List[Dict[str, Any]]
    timestamp: str

class TechnicalIndicators(TypedDict):
    """Technical indicators structure"""
    rsi: Optional[float]
    sma_20: Optional[float]
    sma_50: Optional[float]
    ema_12: Optional[float]
    ema_26: Optional[float]
    bollinger_bands: Optional[Dict[str, float]]
    macd: Optional[Dict[str, float]]
    stochastic: Optional[Dict[str, float]]
    atr: Optional[float]
    volume_sma: Optional[float]

class TradingSignal(TypedDict):
    """Trading signal structure"""
    primary_signal: str  # BUY, SELL, HOLD
    confidence: float  # 0-100
    signal_strength: str  # strong, moderate, weak
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    time_horizon: str  # short, medium, long
    risk_level: str  # low, medium, high
    reasoning: str
    supporting_factors: List[str]
    risk_factors: List[str]

class RiskAssessment(TypedDict):
    """Risk assessment structure"""
    overall_risk_score: float  # 0-100
    risk_level: str  # low, medium, high, extreme
    recommended_position_size: float
    max_acceptable_loss: float
    stop_loss_recommendation: float
    risk_factors: List[str]
    mitigation_strategies: List[str]
    trade_approval: str  # approved, conditional, rejected
    approval_reason: str

class ExecutionResult(TypedDict):
    """Execution result structure"""
    executed: bool
    order_id: Optional[str]
    execution_price: float
    execution_quantity: int
    execution_status: str
    order_data: Optional[Dict[str, Any]]
    error: Optional[str]
