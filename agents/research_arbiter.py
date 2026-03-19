"""
Research Arbiter — Evaluates the bull/bear debate and renders a verdict.

After multiple rounds of debate between the Bull and Bear Researchers,
the Arbiter reads the full debate history, weighs both arguments,
and produces a synthesized research verdict that informs the Trade Strategist.
"""

import logging
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from models.trading_state import TradingState
from utils.agent_memory import AgentMemory

logger = logging.getLogger(__name__)


class ResearchArbiter:
    """Judges the bull/bear research debate and produces a final verdict."""

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

    async def evaluate_debate(self, state: TradingState) -> Dict[str, Any]:
        """Evaluate the full bull/bear debate and render a verdict."""
        debate_history = state.get("debate_history", [])
        bull = state.get("bull_research", {})
        bear = state.get("bear_research", {})
        market_data = state.get("market_data", {})

        if self.use_sample_llm:
            return self._sample_verdict(bull, bear, debate_history)

        # Build debate transcript
        transcript_lines = []
        for entry in debate_history:
            speaker = entry.get("speaker", "?").upper()
            arg = entry.get("argument", "")
            transcript_lines.append(f"[Round {entry.get('round', '?')}] {speaker}: {arg}")
        transcript = "\n".join(transcript_lines) if transcript_lines else "No debate occurred."

        memory_context = self.memory.get_context_summary() if self.memory else ""

        system_prompt = """You are the Research Arbiter — an impartial senior analyst 
who evaluates investment debates between bull and bear researchers.

Your job:
1. Read the full debate transcript carefully
2. Identify the strongest arguments from each side
3. Assess which side presented more compelling evidence
4. Synthesize a balanced verdict that captures the true risk/reward picture
5. Provide a clear directional recommendation

Respond in JSON:
{
    "winning_side": "bull|bear|balanced",
    "verdict_summary": "2-3 sentence synthesis",
    "bull_strength_score": 0-100,
    "bear_strength_score": 0-100,
    "key_bull_points": ["point1", "point2"],
    "key_bear_points": ["point1", "point2"],
    "recommendation": "BUY|SELL|HOLD|ACCUMULATE|REDUCE",
    "confidence": 0-100,
    "reasoning": "detailed reasoning"
}"""

        user_prompt = f"""Evaluate this investment debate for {market_data.get('symbol', 'UNKNOWN')}:

Current Price: ₹{market_data.get('current_price', 0):.2f}

=== BULL THESIS ===
{bull.get('bullish_thesis', 'No thesis provided')}
Upside Potential: {bull.get('upside_potential', 'unknown')}
Confidence: {bull.get('confidence_level', 0)}%

=== BEAR THESIS ===
{bear.get('bearish_thesis', 'No thesis provided')}
Downside Potential: {bear.get('downside_potential', 'unknown')}
Confidence: {bear.get('confidence_level', 0)}%

=== DEBATE TRANSCRIPT ===
{transcript}

{memory_context}

Render your verdict."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            verdict = json.loads(response.content)
        except Exception as e:
            logger.error(f"LLM verdict failed: {e}")
            verdict = self._sample_verdict(bull, bear, debate_history)

        if self.memory:
            self.memory.store("verdict", {
                "symbol": market_data.get("symbol"),
                "winning_side": verdict.get("winning_side"),
                "recommendation": verdict.get("recommendation"),
            })

        return verdict

    def _sample_verdict(self, bull: Dict, bear: Dict, history: list) -> Dict[str, Any]:
        """Generate a sample verdict when no LLM is available."""
        bull_conf = bull.get("confidence_level", 50)
        bear_conf = bear.get("confidence_level", 50)

        if bull_conf > bear_conf + 10:
            winning = "bull"
            rec = "ACCUMULATE"
        elif bear_conf > bull_conf + 10:
            winning = "bear"
            rec = "REDUCE"
        else:
            winning = "balanced"
            rec = "HOLD"

        return {
            "winning_side": winning,
            "verdict_summary": f"After {len(history)} debate exchanges, the {winning} case prevails with moderate conviction.",
            "bull_strength_score": bull_conf,
            "bear_strength_score": bear_conf,
            "key_bull_points": bull.get("key_catalysts", ["Strong fundamentals"])[:2],
            "key_bear_points": bear.get("key_risk_factors", ["Market uncertainty"])[:2],
            "recommendation": rec,
            "confidence": max(bull_conf, bear_conf),
            "reasoning": f"Bull confidence ({bull_conf}%) vs Bear confidence ({bear_conf}%) — verdict: {winning}",
        }

    async def process(self, state: TradingState) -> Dict[str, Any]:
        """LangGraph node entry point."""
        logger.info("Research Arbiter: Evaluating debate...")
        verdict = await self.evaluate_debate(state)

        symbol = state.get("market_data", {}).get("symbol", "UNKNOWN")
        return {
            "research_verdict": verdict,
            "messages": [
                f"Research Arbiter: Verdict rendered for {symbol}",
                f"Winning Side: {verdict.get('winning_side', '?')}",
                f"Recommendation: {verdict.get('recommendation', 'HOLD')}",
                f"Confidence: {verdict.get('confidence', 0)}%",
            ],
        }
