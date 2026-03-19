"""
Risk Hawk — Aggressive risk perspective in the risk panel.

Advocates for taking calculated risks: tighter stops, larger positions,
and capitalizing on high-conviction opportunities. Challenges overly
cautious views from the Dove.
"""

import logging
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from models.trading_state import TradingState

logger = logging.getLogger(__name__)


class RiskHawk:
    """Argues the aggressive risk perspective in risk panel discussions."""

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
        """Present the aggressive risk perspective."""
        proposal = state.get("trade_proposal", {})
        market_data = state.get("market_data", {})
        history = state.get("risk_discussion_history", [])
        round_num = state.get("risk_discussion_round", 0)

        if self.use_sample_llm:
            return self._sample_argument(proposal, market_data, history, round_num)

        # Build prior discussion context
        prior = "\n".join(
            f"[Round {e['round']}] {e['speaker'].upper()}: {e['position']}"
            for e in history
        ) or "No prior discussion."

        system_prompt = """You are the Risk Hawk — the aggressive voice on a risk panel.
Your philosophy: fortune favors the bold. High-conviction ideas deserve larger position sizes.
Risk is not something to avoid — it's something to manage intelligently.

Your role:
1. Argue for maximizing opportunity capture
2. Push for tighter stops (not wider) to increase R:R ratio
3. Challenge conservative positions as potentially leaving profits on the table
4. Address counterarguments from prior rounds

Respond in JSON:
{
    "position": "2-3 sentence argument",
    "recommended_position_size_pct": number,
    "recommended_stop_loss_pct": number,
    "reasoning": "why this is the right risk posture",
    "counter_to_dove": "rebuttal to conservative views (if any)"
}"""

        user_prompt = f"""Risk panel discussion for {market_data.get('symbol', '?')}:

Trade Proposal: {proposal.get('action', 'HOLD')} at ₹{proposal.get('entry_price', 0):.2f}
Proposal Confidence: {proposal.get('confidence', 0)}%

Prior Discussion:
{prior}

Present your aggressive risk perspective (Round {round_num + 1})."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            argument = json.loads(response.content)
        except Exception as e:
            logger.error(f"Risk Hawk LLM failed: {e}")
            argument = self._sample_argument(proposal, market_data, history, round_num)

        return argument

    def _sample_argument(self, proposal: Dict, market_data: Dict,
                         history: list, round_num: int) -> Dict[str, Any]:
        """Sample argument when no LLM is available."""
        confidence = proposal.get("confidence", 50)
        action = proposal.get("action", "HOLD")

        if action == "BUY" and confidence > 60:
            position = f"Strong conviction BUY — scale up to 2% position. Market conditions favor aggressive entry."
            size = 2.0
            sl = 3.0
        elif action == "SELL":
            position = f"Take the short side aggressively. Tight stops protect capital while maximizing downside capture."
            size = 1.5
            sl = 3.0
        else:
            position = f"Even HOLD signals can be traded — consider a smaller speculative position to capture any breakout."
            size = 0.5
            sl = 2.0

        return {
            "position": position,
            "recommended_position_size_pct": size,
            "recommended_stop_loss_pct": sl,
            "reasoning": f"Confidence at {confidence}% warrants an aggressive posture. Risk can be managed with tight stops.",
            "counter_to_dove": "Being too cautious means missing the move entirely.",
        }

    async def process(self, state: TradingState) -> Dict[str, Any]:
        """LangGraph node entry point."""
        logger.info("Risk Hawk: Presenting aggressive perspective...")
        argument = await self.argue(state)
        round_num = state.get("risk_discussion_round", 0)

        entry = {
            "round": round_num + 1,
            "speaker": "hawk",
            "position": argument.get("position", ""),
            "reasoning": argument.get("reasoning", ""),
            "recommended_action": f"Size: {argument.get('recommended_position_size_pct', 0)}%, SL: {argument.get('recommended_stop_loss_pct', 0)}%",
        }

        return {
            "risk_discussion_history": [entry],
            "risk_discussion_round": round_num + 1,
            "messages": [f"Risk Hawk: {argument.get('position', '')[:120]}"],
        }
