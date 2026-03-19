"""
Trading State — Defines the shared state structure for the multi-agent trading pipeline.

This state flows through the LangGraph StateGraph and is read/written by every agent node.
It tracks market data, analysis outputs, debate histories, risk discussions, and final decisions.
"""

from typing import Dict, Any, List, Optional, TypedDict, Sequence
from typing_extensions import Annotated
import operator


def _merge_messages(left: List[str], right: List[str]) -> List[str]:
    """Custom reducer that appends new messages to the existing list."""
    return left + right


def _merge_debate(left: List[Dict[str, Any]], right: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Custom reducer for debate history — appends new rounds."""
    return left + right


class TradingState(TypedDict):
    """
    Central state shared across all agent nodes in the trading graph.

    Groups:
    - Identification: symbol, timestamps, cycle tracking
    - Market intelligence: raw data + analyst outputs
    - Debate arena: bull/bear debate history + research verdict
    - Risk panel: risk discussion history + risk verdict
    - Decision: trade proposal, portfolio decision, execution result
    - Meta: messages log, errors, metadata
    """

    # ── Identification ──────────────────────────────────────────────
    symbol: str
    timestamp: str
    cycle_id: str

    # ── Market Intelligence ─────────────────────────────────────────
    market_data: Optional[Dict[str, Any]]
    market_analysis: Optional[Dict[str, Any]]
    technical_indicators: Optional[Dict[str, Any]]
    technical_analysis: Optional[Dict[str, Any]]
    fundamentals_analysis: Optional[Dict[str, Any]]
    sentiment_analysis: Optional[Dict[str, Any]]
    news_analysis: Optional[Dict[str, Any]]

    # ── Debate Arena (Bull vs Bear) ─────────────────────────────────
    bull_research: Optional[Dict[str, Any]]
    bear_research: Optional[Dict[str, Any]]
    debate_history: Annotated[List[Dict[str, Any]], _merge_debate]
    debate_round: int
    research_verdict: Optional[Dict[str, Any]]

    # ── Risk Panel Discussion ───────────────────────────────────────
    risk_discussion_history: Annotated[List[Dict[str, Any]], _merge_debate]
    risk_discussion_round: int
    risk_verdict: Optional[Dict[str, Any]]

    # ── Trade Decision Pipeline ─────────────────────────────────────
    trade_proposal: Optional[Dict[str, Any]]
    portfolio_decision: Optional[Dict[str, Any]]
    execution_result: Optional[Dict[str, Any]]

    # ── Meta ────────────────────────────────────────────────────────
    messages: Annotated[List[str], _merge_messages]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]


# ── Convenience sub-schemas for documentation / validation ──────────

class MarketData(TypedDict):
    """Raw market data snapshot."""
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
    """Computed technical indicator values."""
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


class DebateEntry(TypedDict):
    """Single round in the bull/bear debate."""
    round: int
    speaker: str          # "bull" | "bear"
    argument: str
    counter_to: Optional[str]
    confidence: float


class RiskDiscussionEntry(TypedDict):
    """Single contribution in the risk panel discussion."""
    round: int
    speaker: str          # "hawk" | "owl" | "dove"
    position: str
    reasoning: str
    recommended_action: str


class TradeProposal(TypedDict):
    """Trade proposal produced by the Trade Strategist."""
    action: str           # BUY | SELL | HOLD
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size_pct: float
    time_horizon: str
    reasoning: str
    supporting_factors: List[str]
    risk_factors: List[str]


class RiskVerdict(TypedDict):
    """Final ruling from the Risk Arbiter."""
    approved: bool
    risk_level: str
    adjusted_position_size: float
    adjusted_stop_loss: float
    reasoning: str
    dissenting_views: List[str]


class ExecutionResult(TypedDict):
    """Order execution outcome."""
    executed: bool
    order_id: Optional[str]
    execution_price: float
    execution_quantity: int
    execution_status: str
    order_data: Optional[Dict[str, Any]]
    error: Optional[str]
