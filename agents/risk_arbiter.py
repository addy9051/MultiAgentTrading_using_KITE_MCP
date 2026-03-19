"""
Risk Arbiter — Final judge of the risk panel discussion.

Reads the full Hawk/Owl/Dove discussion, weighs all perspectives,
and produces a binding risk verdict that either approves or rejects
the trade proposal (potentially with adjusted parameters).
"""

import logging
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from models.trading_state import TradingState
from utils.agent_memory import AgentMemory

logger = logging.getLogger(__name__)


class RiskArbiter:
    """Renders the final risk verdict after the risk panel discussion."""

    def __init__(self, settings, memory: AgentMemory = None):
        self.settings = settings
        self.memory = memory
        self.use_sample_llm = not settings.OPENAI_API_KEY

        self.llm = None
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.1,
            )

    async def judge(self, state: TradingState) -> Dict[str, Any]:
        """Evaluate the risk panel discussion and render a verdict."""
        proposal = state.get("trade_proposal", {})
        market_data = state.get("market_data", {})
        history = state.get("risk_discussion_history", [])

        if self.use_sample_llm:
            return self._sample_verdict(proposal, history)

        transcript = "\n".join(
            f"[Round {e['round']}] {e['speaker'].upper()}: {e['position']} | {e.get('reasoning', '')}"
            for e in history
        ) or "No discussion occurred."

        memory_context = self.memory.get_context_summary() if self.memory else ""

        system_prompt = """You are the Risk Arbiter — the final authority on trade risk approval.
After listening to the Hawk (aggressive), Owl (balanced), and Dove (conservative) perspectives,
you must render a binding verdict.

Rules:
1. You MUST either approve or reject the trade
2. If approved, you may adjust position size and stop loss
3. Provide clear reasoning referencing specific panel arguments
4. Identify any dissenting views worth noting

Respond in JSON:
{
    "approved": true|false,
    "risk_level": "low|moderate|elevated|high|extreme",
    "adjusted_position_size_pct": number,
    "adjusted_stop_loss_pct": number,
    "reasoning": "detailed reasoning",
    "key_risk_factors": ["risk1", "risk2"],
    "dissenting_views": ["view1"],
    "conditions": ["condition for approval, if any"]
}"""

        user_prompt = f"""Render risk verdict for {market_data.get('symbol', '?')}:

Trade Proposal: {proposal.get('action', 'HOLD')} at ₹{proposal.get('entry_price', 0):.2f}
Proposed Size: {proposal.get('position_size_pct', 0)}%
Proposed SL: ₹{proposal.get('stop_loss', 0):.2f}

=== RISK PANEL TRANSCRIPT ===
{transcript}

{memory_context}

Render your final verdict."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            verdict = json.loads(response.content)
        except Exception as e:
            logger.error(f"Risk Arbiter LLM failed: {e}")
            verdict = self._sample_verdict(proposal, history)

        if self.memory:
            self.memory.store("risk_verdict", {
                "symbol": market_data.get("symbol"),
                "approved": verdict.get("approved"),
                "risk_level": verdict.get("risk_level"),
            })

        return verdict

    def _sample_verdict(self, proposal: Dict, history: list) -> Dict[str, Any]:
        """Generate a sample verdict when no LLM is available."""
        action = proposal.get("action", "HOLD")
        confidence = proposal.get("confidence", 50)

        # Collect recommended sizes from discussion
        sizes = []
        for entry in history:
            rec = entry.get("recommended_action", "")
            if "Size:" in rec:
                try:
                    size_str = rec.split("Size:")[1].split("%")[0].strip()
                    sizes.append(float(size_str))
                except (ValueError, IndexError):
                    pass

        avg_size = sum(sizes) / len(sizes) if sizes else 1.0

        if action == "HOLD" or confidence < 40:
            return {
                "approved": False,
                "risk_level": "elevated",
                "adjusted_position_size_pct": 0.0,
                "adjusted_stop_loss_pct": 0.0,
                "reasoning": "Insufficient conviction to take a position. Panel discussion inconclusive.",
                "key_risk_factors": ["Low confidence", "Mixed signals"],
                "dissenting_views": ["Hawk argued for speculative entry"],
                "conditions": [],
            }

        approved = confidence >= 55
        risk_level = "moderate" if confidence >= 70 else "elevated" if confidence >= 55 else "high"

        return {
            "approved": approved,
            "risk_level": risk_level,
            "adjusted_position_size_pct": round(min(avg_size, self.settings.MAX_POSITION_SIZE * 100), 2),
            "adjusted_stop_loss_pct": round(self.settings.STOP_LOSS_PERCENT * 100, 2),
            "reasoning": f"Panel consensus favors {'approval' if approved else 'rejection'}. Average recommended size: {avg_size:.1f}%.",
            "key_risk_factors": ["Market volatility", "Execution risk"],
            "dissenting_views": ["Dove recommended smaller size"] if avg_size > 1.0 else [],
            "conditions": ["Monitor for stop-loss trigger within first hour"] if approved else [],
        }

    async def process(self, state: TradingState) -> Dict[str, Any]:
        """LangGraph node entry point."""
        logger.info("Risk Arbiter: Rendering final verdict...")
        verdict = await self.judge(state)

        status = "APPROVED" if verdict.get("approved") else "REJECTED"
        return {
            "risk_verdict": verdict,
            "messages": [
                f"Risk Arbiter: Trade {status}",
                f"Risk Level: {verdict.get('risk_level', '?')}",
                f"Adjusted Size: {verdict.get('adjusted_position_size_pct', 0)}%",
                f"Reasoning: {verdict.get('reasoning', '')[:120]}",
            ],
        }
