"""
Bear Researcher — Advocates for bearish positions and identifies risks.

In the debate loop, accepts the Bull's arguments from state and
produces rebuttals. The debate continues for N rounds before the
Research Arbiter renders a verdict.
"""

import logging
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from models.trading_state import TradingState
from utils.agent_memory import AgentMemory

logger = logging.getLogger(__name__)


class BearResearcher:
    """Builds and defends the bearish investment thesis through debate."""

    def __init__(self, settings, memory: AgentMemory = None):
        self.settings = settings
        self.memory = memory
        self.use_sample_llm = not settings.OPENAI_API_KEY

        self.llm = None
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.3,
            )

    async def research_bearish_case(self, state: TradingState) -> Dict[str, Any]:
        """Build or defend the bearish case. Reads debate history for rebuttals."""
        market_data = state.get("market_data", {})
        fundamentals = state.get("fundamentals_analysis", {})
        sentiment = state.get("sentiment_analysis", {})
        news = state.get("news_analysis", {})
        technical = state.get("technical_analysis", {})
        debate_history = state.get("debate_history", [])
        round_num = state.get("debate_round", 0)

        if self.use_sample_llm:
            return self._sample_research(state, debate_history, round_num)

        prior_debate = "\n".join(
            f"[Round {e['round']}] {e['speaker'].upper()}: {e['argument']}"
            for e in debate_history
        ) or "This is the opening round — no prior arguments."

        memory_ctx = self.memory.get_context_summary() if self.memory else ""
        symbol = market_data.get("symbol", "UNKNOWN")

        system_prompt = """You are a Bear Researcher — your job is to build and defend
the bearish investment thesis. In later rounds, you must directly rebut the Bull's arguments.

Rules:
1. In Round 1, present your initial bearish case
2. In later rounds, directly counter the Bull's latest arguments
3. Highlight risks, overvaluations, and headwinds with data
4. Maintain intellectual honesty — acknowledge strong bull points but show why they're insufficient

Respond in JSON:
{
    "bearish_thesis": "your full argument (2-4 sentences)",
    "key_risk_factors": ["risk1", "risk2", "risk3"],
    "downside_potential": "percentage range",
    "counter_to_bull": "direct rebuttal to bull's latest argument (if any)",
    "confidence_level": 0-100,
    "recommended_action": "SELL|REDUCE|AVOID"
}"""

        user_prompt = f"""Debate Round {round_num + 1} for {symbol}:

=== MARKET DATA ===
Price: ₹{market_data.get('current_price', 0):.2f} | Volume: {market_data.get('volume', 0):,}

=== ANALYST REPORTS ===
Fundamentals: {fundamentals.get('financial_health', '?')} | Valuation: {fundamentals.get('valuation_assessment', '?')}
Sentiment: {sentiment.get('overall_sentiment', '?')} | News: {news.get('overall_news_sentiment', '?')}
Technical: {technical.get('trend_direction', '?')} | Score: {technical.get('overall_score', '?')}

=== DEBATE HISTORY ===
{prior_debate}

{memory_ctx}

Present your bearish case{' and rebut the bull' if round_num > 0 else ''}."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            research = json.loads(response.content)
        except Exception as e:
            logger.error(f"Bear LLM failed: {e}")
            research = self._sample_research(state, debate_history, round_num)

        if self.memory:
            self.memory.store("bear_thesis", {
                "symbol": symbol,
                "round": round_num + 1,
                "confidence": research.get("confidence_level"),
            })

        return research

    def _sample_research(self, state: TradingState, history: list, round_num: int) -> Dict[str, Any]:
        """Sample bear research for when no LLM is available."""
        market_data = state.get("market_data", {})
        fundamentals = state.get("fundamentals_analysis", {})
        sentiment = state.get("sentiment_analysis", {})
        symbol = market_data.get("symbol", "UNKNOWN")
        price = market_data.get("current_price", 0)

        downside = "10-20%"
        if fundamentals.get("valuation_assessment") == "overvalued":
            downside = "20-30%"
        elif sentiment.get("overall_sentiment") == "bearish":
            downside = "15-25%"

        counter = ""
        if round_num > 0 and history:
            bull_args = [e for e in history if e.get("speaker") == "bull"]
            if bull_args:
                counter = f"The bull's optimism about {bull_args[-1].get('argument', '')[:50]}... ignores the macro headwinds and valuation stretch."

        risks = [
            "Market volatility and macro uncertainty",
            "Valuation pressure at current levels",
            "Sector rotation risk",
        ]
        if fundamentals.get("key_risks"):
            risks.extend(fundamentals["key_risks"][:2])

        return {
            "bearish_thesis": f"{symbol} faces {downside} downside risk due to valuation concerns, competitive pressure, and macro headwinds.",
            "key_risk_factors": risks,
            "downside_potential": downside,
            "counter_to_bull": counter or "No bull arguments to counter yet.",
            "confidence_level": 68,
            "recommended_action": "REDUCE",
        }

    async def process(self, state: TradingState) -> Dict[str, Any]:
        """LangGraph node entry point."""
        round_num = state.get("debate_round", 0)
        logger.info(f"Bear Researcher: Round {round_num + 1}...")

        research = await self.research_bearish_case(state)

        debate_entry = {
            "round": round_num + 1,
            "speaker": "bear",
            "argument": research.get("bearish_thesis", ""),
            "counter_to": research.get("counter_to_bull", ""),
            "confidence": research.get("confidence_level", 50),
        }

        return {
            "bear_research": research,
            "debate_history": [debate_entry],
            "debate_round": round_num + 1,
            "messages": [
                f"Bear Researcher (Round {round_num + 1}): {research.get('bearish_thesis', '')[:100]}...",
                f"Downside: {research.get('downside_potential', '?')} | Action: {research.get('recommended_action', 'AVOID')}",
            ],
        }