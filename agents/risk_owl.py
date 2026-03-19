"""
Risk Owl — Balanced/neutral risk perspective in the risk panel.

Takes a pragmatic, data-driven view. Neither aggressive nor conservative —
weighs both sides and anchors the discussion in quantitative risk metrics.
"""

import logging
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from models.trading_state import TradingState

logger = logging.getLogger(__name__)


class RiskOwl:
    """Argues the balanced risk perspective in risk panel discussions."""

    def __init__(self, settings):
        self.settings = settings
        self.use_sample_llm = not settings.OPENAI_API_KEY

        self.llm = None
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.1,
            )

    async def argue(self, state: TradingState) -> Dict[str, Any]:
        """Present the balanced risk perspective."""
        proposal = state.get("trade_proposal", {})
        market_data = state.get("market_data", {})
        technical = state.get("technical_analysis", {})
        indicators = state.get("technical_indicators", {})
        history = state.get("risk_discussion_history", [])
        round_num = state.get("risk_discussion_round", 0)

        if self.use_sample_llm:
            return self._sample_argument(proposal, market_data, indicators, history, round_num)

        prior = "\n".join(
            f"[Round {e['round']}] {e['speaker'].upper()}: {e['position']}"
            for e in history
        ) or "No prior discussion."

        system_prompt = """You are the Risk Owl — the balanced, data-driven voice on a risk panel.
Your philosophy: let the numbers speak. Neither too aggressive nor too cautious.

Your role:
1. Anchor the discussion in quantitative metrics (ATR, volatility, R:R ratio)
2. Find the middle ground between the Hawk and the Dove
3. Propose position sizes that balance opportunity with risk
4. Highlight when one side is being irrational

Respond in JSON:
{
    "position": "2-3 sentence balanced assessment",
    "recommended_position_size_pct": number,
    "recommended_stop_loss_pct": number,
    "risk_reward_ratio": number,
    "reasoning": "data-driven justification",
    "synthesis": "how hawk and dove views should be weighted"
}"""

        atr = indicators.get("atr", 0)
        price = market_data.get("current_price", 1)
        vol_pct = (atr / price * 100) if price > 0 else 0

        user_prompt = f"""Risk panel discussion for {market_data.get('symbol', '?')}:

Trade Proposal: {proposal.get('action', 'HOLD')} at ₹{price:.2f}
Confidence: {proposal.get('confidence', 0)}%
Proposed SL: ₹{proposal.get('stop_loss', 0):.2f} | TP: ₹{proposal.get('take_profit', 0):.2f}

Volatility (ATR%): {vol_pct:.2f}%
Trend: {technical.get('trend_direction', 'N/A')}

Prior Discussion:
{prior}

Present your balanced assessment (Round {round_num + 1})."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            argument = json.loads(response.content)
        except Exception as e:
            logger.error(f"Risk Owl LLM failed: {e}")
            argument = self._sample_argument(proposal, market_data, indicators, history, round_num)

        return argument

    def _sample_argument(self, proposal: Dict, market_data: Dict,
                         indicators: Dict, history: list, round_num: int) -> Dict[str, Any]:
        """Sample argument when no LLM is available."""
        confidence = proposal.get("confidence", 50)
        price = market_data.get("current_price", 0)
        atr = indicators.get("atr", 0)
        action = proposal.get("action", "HOLD")

        # Calculate data-driven position size
        vol_pct = (atr / price * 100) if price > 0 else 2.0
        if vol_pct > 3:
            size = 0.5
            sl = 5.0
        elif vol_pct > 1.5:
            size = 1.0
            sl = 5.0
        else:
            size = 1.5
            sl = 4.0

        if action == "HOLD":
            size = 0.0

        # R:R ratio
        sl_price = price * (1 - sl / 100)
        tp_price = proposal.get("take_profit", price * 1.10)
        rr = abs(tp_price - price) / abs(price - sl_price) if abs(price - sl_price) > 0 else 1.0

        return {
            "position": f"Data says volatility is {vol_pct:.1f}% — moderate sizing at {size}% with {sl}% stop is appropriate.",
            "recommended_position_size_pct": size,
            "recommended_stop_loss_pct": sl,
            "risk_reward_ratio": round(rr, 2),
            "reasoning": f"ATR-based volatility ({vol_pct:.1f}%) and confidence ({confidence}%) suggest a balanced approach.",
            "synthesis": "Hawk's aggression is warranted only if R:R exceeds 2:1. Dove's caution is valid given current volatility.",
        }

    async def process(self, state: TradingState) -> Dict[str, Any]:
        """LangGraph node entry point."""
        logger.info("Risk Owl: Presenting balanced perspective...")
        argument = await self.argue(state)
        round_num = state.get("risk_discussion_round", 0)

        entry = {
            "round": round_num + 1,
            "speaker": "owl",
            "position": argument.get("position", ""),
            "reasoning": argument.get("reasoning", ""),
            "recommended_action": f"Size: {argument.get('recommended_position_size_pct', 0)}%, SL: {argument.get('recommended_stop_loss_pct', 0)}%, R:R: {argument.get('risk_reward_ratio', 1.0)}",
        }

        return {
            "risk_discussion_history": [entry],
            "risk_discussion_round": round_num + 1,
            "messages": [f"Risk Owl: {argument.get('position', '')[:120]}"],
        }
