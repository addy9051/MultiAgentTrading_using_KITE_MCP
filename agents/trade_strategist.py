"""
Trade Strategist — Synthesizes all analysis into a concrete trade proposal.

Consumes the research verdict, analyst outputs, and market data to produce
a specific, actionable trade proposal with entry/exit levels and sizing.
"""

import logging
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from models.trading_state import TradingState
from strategies.simple_rsi_strategy import SimpleRSIStrategy
from utils.agent_memory import AgentMemory

logger = logging.getLogger(__name__)


class TradeStrategist:
    """Converts multi-source analysis into a single trade proposal."""

    def __init__(self, settings, memory: AgentMemory = None):
        self.settings = settings
        self.memory = memory
        self.rsi_strategy = SimpleRSIStrategy(settings)
        self.use_sample_llm = not settings.OPENAI_API_KEY

        self.llm = None
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.1,
            )

    async def craft_proposal(self, state: TradingState) -> Dict[str, Any]:
        """Build a trade proposal from all available analysis."""
        market_data = state.get("market_data", {})
        technical = state.get("technical_analysis", {})
        indicators = state.get("technical_indicators", {})
        verdict = state.get("research_verdict", {})
        fundamentals = state.get("fundamentals_analysis", {})
        sentiment = state.get("sentiment_analysis", {})

        # Always compute rule-based signals as a baseline
        rule_signals = self._rule_based_signals(indicators, market_data)

        if self.use_sample_llm:
            return self._sample_proposal(market_data, indicators, technical, verdict, rule_signals)

        memory_context = self.memory.get_context_summary() if self.memory else ""

        system_prompt = """You are a Trade Strategist at a quantitative trading desk.
Your job is to synthesize analyst reports, research verdicts, and technical signals
into a single, precise trade proposal.

Rules:
- Be specific about entry price, stop loss, and take profit levels
- Position size should be expressed as % of portfolio (max 2%)
- Always justify your time horizon
- If the evidence is conflicting, default to HOLD

Respond in JSON:
{
    "action": "BUY|SELL|HOLD",
    "confidence": 0-100,
    "entry_price": number,
    "stop_loss": number,
    "take_profit": number,
    "position_size_pct": 0.0-2.0,
    "time_horizon": "intraday|swing|positional",
    "reasoning": "concise explanation",
    "supporting_factors": ["factor1", "factor2"],
    "risk_factors": ["risk1", "risk2"]
}"""

        user_prompt = f"""Craft a trade proposal for {market_data.get('symbol', '?')}:

=== MARKET SNAPSHOT ===
Price: ₹{market_data.get('current_price', 0):.2f}
Volume: {market_data.get('volume', 0):,}
Day Range: ₹{market_data.get('low', 0):.2f} – ₹{market_data.get('high', 0):.2f}

=== TECHNICAL SIGNALS ===
RSI: {indicators.get('rsi', 'N/A')} | Trend: {technical.get('trend_direction', 'N/A')}
MACD: {indicators.get('macd', 'N/A')}
Rule-based signal: {rule_signals.get('rsi_signal', 'N/A')}

=== RESEARCH VERDICT ===
Winner: {verdict.get('winning_side', 'N/A')}
Recommendation: {verdict.get('recommendation', 'HOLD')}
Confidence: {verdict.get('confidence', 0)}%
Reasoning: {verdict.get('reasoning', 'N/A')[:200]}

=== FUNDAMENTALS ===
Health: {fundamentals.get('financial_health', 'N/A')}
Valuation: {fundamentals.get('valuation_assessment', 'N/A')}

=== SENTIMENT ===
Overall: {sentiment.get('overall_sentiment', 'N/A')}
Score: {sentiment.get('sentiment_score', 'N/A')}

{memory_context}

Produce your trade proposal."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            proposal = json.loads(response.content)
        except Exception as e:
            logger.error(f"LLM proposal failed: {e}")
            proposal = self._sample_proposal(market_data, indicators, technical, verdict, rule_signals)

        if self.memory:
            self.memory.store("proposal", {
                "symbol": market_data.get("symbol"),
                "action": proposal.get("action"),
                "confidence": proposal.get("confidence"),
            })

        return proposal

    def _rule_based_signals(self, indicators: Dict, market_data: Dict) -> Dict[str, Any]:
        """Generate rule-based signals as a sanity check baseline."""
        try:
            return self.rsi_strategy.generate_signal(indicators, market_data)
        except Exception:
            return {"rsi_signal": "HOLD", "rsi_strength": "weak"}

    def _sample_proposal(self, market_data: Dict, indicators: Dict,
                         technical: Dict, verdict: Dict, rule_signals: Dict) -> Dict[str, Any]:
        """Produce a sample proposal when no LLM is available."""
        price = market_data.get("current_price", 0)
        rec = verdict.get("recommendation", "HOLD")

        action_map = {"BUY": "BUY", "ACCUMULATE": "BUY", "SELL": "SELL", "REDUCE": "SELL"}
        action = action_map.get(rec, "HOLD")

        return {
            "action": action,
            "confidence": verdict.get("confidence", 50),
            "entry_price": price,
            "stop_loss": round(price * 0.95, 2),
            "take_profit": round(price * 1.10, 2),
            "position_size_pct": 1.0 if action != "HOLD" else 0.0,
            "time_horizon": "swing",
            "reasoning": f"Based on research verdict ({rec}) and rule-based RSI signal ({rule_signals.get('rsi_signal', '?')})",
            "supporting_factors": [
                f"Research verdict: {rec}",
                f"Technical trend: {technical.get('trend_direction', '?')}",
            ],
            "risk_factors": [
                "Market volatility",
                "Sample-mode analysis — limited accuracy",
            ],
        }

    async def process(self, state: TradingState) -> Dict[str, Any]:
        """LangGraph node entry point."""
        logger.info("Trade Strategist: Crafting proposal...")
        proposal = await self.craft_proposal(state)

        return {
            "trade_proposal": proposal,
            "messages": [
                f"Trade Strategist: Proposal — {proposal.get('action', 'HOLD')}",
                f"Confidence: {proposal.get('confidence', 0)}%",
                f"Entry: ₹{proposal.get('entry_price', 0):.2f} | SL: ₹{proposal.get('stop_loss', 0):.2f} | TP: ₹{proposal.get('take_profit', 0):.2f}",
            ],
        }
