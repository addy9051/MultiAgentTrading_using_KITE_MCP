"""
Risk Dove — Conservative risk perspective in the risk panel.

Advocates for capital preservation: wider stops, smaller positions,
and erring on the side of caution. Challenges aggressive positions
from the Hawk.
"""

import logging
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from models.trading_state import TradingState

logger = logging.getLogger(__name__)


class RiskDove:
    """Argues the conservative risk perspective in risk panel discussions."""

    def __init__(self, settings):
        self.settings = settings
        self.use_sample_llm = not settings.OPENAI_API_KEY

        self.llm = None
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.2,
            )

    async def argue(self, state: TradingState) -> Dict[str, Any]:
        """Present the conservative risk perspective."""
        proposal = state.get("trade_proposal", {})
        market_data = state.get("market_data", {})
        history = state.get("risk_discussion_history", [])
        round_num = state.get("risk_discussion_round", 0)

        if self.use_sample_llm:
            return self._sample_argument(proposal, market_data, history, round_num)

        prior = "\n".join(
            f"[Round {e['round']}] {e['speaker'].upper()}: {e['position']}"
            for e in history
        ) or "No prior discussion."

        system_prompt = """You are the Risk Dove — the conservative voice on a risk panel.
Your philosophy: capital preservation is the #1 priority. It's always better to miss a trade
than to blow up the account.

Your role:
1. Advocate for smaller position sizes and wider stop losses
2. Highlight tail risks and worst-case scenarios
3. Challenge aggressive positions with historical examples of drawdowns
4. Suggest hedging strategies when appropriate

Respond in JSON:
{
    "position": "2-3 sentence argument",
    "recommended_position_size_pct": number,
    "recommended_stop_loss_pct": number,
    "reasoning": "why caution is warranted",
    "counter_to_hawk": "rebuttal to aggressive views (if any)"
}"""

        user_prompt = f"""Risk panel discussion for {market_data.get('symbol', '?')}:

Trade Proposal: {proposal.get('action', 'HOLD')} at ₹{proposal.get('entry_price', 0):.2f}
Proposal Confidence: {proposal.get('confidence', 0)}%

Prior Discussion:
{prior}

Present your conservative risk perspective (Round {round_num + 1})."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            argument = json.loads(response.content)
        except Exception as e:
            logger.error(f"Risk Dove LLM failed: {e}")
            argument = self._sample_argument(proposal, market_data, history, round_num)

        return argument

    def _sample_argument(self, proposal: Dict, market_data: Dict,
                         history: list, round_num: int) -> Dict[str, Any]:
        """Sample argument when no LLM is available."""
        confidence = proposal.get("confidence", 50)
        action = proposal.get("action", "HOLD")

        if confidence < 60:
            position = "Low conviction — recommend sitting this one out. Capital preservation should be the priority."
            size = 0.0
            sl = 7.0
        elif action in ("BUY", "SELL"):
            position = f"Proceed with extreme caution — half the proposed size with wide stops. Markets can reverse quickly."
            size = 0.5
            sl = 7.0
        else:
            position = "HOLD is the correct call. No need to force a trade in uncertain conditions."
            size = 0.0
            sl = 0.0

        return {
            "position": position,
            "recommended_position_size_pct": size,
            "recommended_stop_loss_pct": sl,
            "reasoning": f"With {confidence}% confidence, the risk/reward doesn't justify full exposure. Protect capital first.",
            "counter_to_hawk": "Aggressive sizing in uncertain markets is how accounts blow up. Size down.",
        }

    async def process(self, state: TradingState) -> Dict[str, Any]:
        """LangGraph node entry point."""
        logger.info("Risk Dove: Presenting conservative perspective...")
        argument = await self.argue(state)
        round_num = state.get("risk_discussion_round", 0)

        entry = {
            "round": round_num + 1,
            "speaker": "dove",
            "position": argument.get("position", ""),
            "reasoning": argument.get("reasoning", ""),
            "recommended_action": f"Size: {argument.get('recommended_position_size_pct', 0)}%, SL: {argument.get('recommended_stop_loss_pct', 0)}%",
        }

        return {
            "risk_discussion_history": [entry],
            "risk_discussion_round": round_num + 1,
            "messages": [f"Risk Dove: {argument.get('position', '')[:120]}"],
        }
