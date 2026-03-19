"""
Bull Researcher — Advocates for bullish positions and long opportunities.

In the debate loop, accepts the Bear's counter-arguments from state and
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


class BullResearcher:
    """Builds and defends the bullish investment thesis through debate."""

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

    async def research_bullish_case(self, state: TradingState) -> Dict[str, Any]:
        """Build or defend the bullish case. Reads debate history for rebuttals."""
        market_data = state.get("market_data", {})
        fundamentals = state.get("fundamentals_analysis", {})
        sentiment = state.get("sentiment_analysis", {})
        news = state.get("news_analysis", {})
        technical = state.get("technical_analysis", {})
        debate_history = state.get("debate_history", [])
        round_num = state.get("debate_round", 0)

        if self.use_sample_llm:
            return self._sample_research(state, debate_history, round_num)

        # Build prior debate context
        prior_debate = "\n".join(
            f"[Round {e['round']}] {e['speaker'].upper()}: {e['argument']}"
            for e in debate_history
        ) or "This is the opening round — no prior arguments."

        memory_ctx = self.memory.get_context_summary() if self.memory else ""
        symbol = market_data.get("symbol", "UNKNOWN")

        system_prompt = """You are a Bull Researcher — your job is to build and defend 
the bullish investment thesis. In later rounds, you must directly rebut the Bear's arguments.

Rules:
1. In Round 1, present your initial bullish case
2. In later rounds, directly counter the Bear's latest arguments
3. Use specific data points to support your claims
4. Maintain intellectual honesty — acknowledge weak points but reframe them

Respond in JSON:
{
    "bullish_thesis": "your full argument (2-4 sentences)",
    "key_catalysts": ["catalyst1", "catalyst2", "catalyst3"],
    "upside_potential": "percentage range",
    "counter_to_bear": "direct rebuttal to bear's latest argument (if any)",
    "confidence_level": 0-100,
    "recommended_action": "BUY|ACCUMULATE|WAIT"
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

Present your bullish case{' and rebut the bear' if round_num > 0 else ''}."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            research = json.loads(response.content)
        except Exception as e:
            logger.error(f"Bull LLM failed: {e}")
            research = self._sample_research(state, debate_history, round_num)

        if self.memory:
            self.memory.store("bull_thesis", {
                "symbol": symbol,
                "round": round_num + 1,
                "confidence": research.get("confidence_level"),
            })

        return research

    def _sample_research(self, state: TradingState, history: list, round_num: int) -> Dict[str, Any]:
        """Sample bull research for when no LLM is available."""
        market_data = state.get("market_data", {})
        fundamentals = state.get("fundamentals_analysis", {})
        sentiment = state.get("sentiment_analysis", {})
        symbol = market_data.get("symbol", "UNKNOWN")
        price = market_data.get("current_price", 0)

        upside = "15-25%"
        if fundamentals.get("valuation_assessment") == "undervalued":
            upside = "25-35%"

        # In later rounds, generate a counter-argument
        counter = ""
        if round_num > 0 and history:
            bear_args = [e for e in history if e.get("speaker") == "bear"]
            if bear_args:
                counter = f"The bear's concerns about {bear_args[-1].get('argument', '')[:50]}... are overblown — the fundamentals remain solid."

        catalysts = [
            "Strong market position and pricing power",
            "Positive earnings momentum",
            "Technical breakout potential above resistance",
        ]
        if fundamentals.get("financial_health") == "strong":
            catalysts.append("Robust balance sheet supports growth")

        return {
            "bullish_thesis": f"{symbol} presents compelling upside of {upside} driven by strong fundamentals and improving sentiment.",
            "key_catalysts": catalysts,
            "upside_potential": upside,
            "counter_to_bear": counter or "No bear arguments to counter yet.",
            "confidence_level": 72,
            "recommended_action": "ACCUMULATE",
        }

    async def process(self, state: TradingState) -> Dict[str, Any]:
        """LangGraph node entry point."""
        round_num = state.get("debate_round", 0)
        logger.info(f"Bull Researcher: Round {round_num + 1}...")

        research = await self.research_bullish_case(state)

        debate_entry = {
            "round": round_num + 1,
            "speaker": "bull",
            "argument": research.get("bullish_thesis", ""),
            "counter_to": research.get("counter_to_bear", ""),
            "confidence": research.get("confidence_level", 50),
        }

        return {
            "bull_research": research,
            "debate_history": [debate_entry],
            "debate_round": round_num + 1,
            "messages": [
                f"Bull Researcher (Round {round_num + 1}): {research.get('bullish_thesis', '')[:100]}...",
                f"Upside: {research.get('upside_potential', '?')} | Action: {research.get('recommended_action', 'WAIT')}",
            ],
        }