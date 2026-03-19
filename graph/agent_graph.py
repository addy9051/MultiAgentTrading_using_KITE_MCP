"""
Agent Graph — Full LangGraph StateGraph for the multi-agent trading pipeline.

This module builds and compiles the trading graph with:
1. Analyst nodes (parallel-ready): Market Data → Technical → Fundamentals → Sentiment → News
2. Debate loop: Bull ↔ Bear researchers with conditional edges
3. Research Arbiter: judges the debate
4. Trade Strategist: crafts a trade proposal
5. Risk panel loop: Hawk → Dove → Owl rotation with conditional edges
6. Risk Arbiter: final risk verdict
7. Portfolio Manager: execution via KITE MCP
"""

import logging
from typing import Optional

from langgraph.graph import StateGraph, END

from models.trading_state import TradingState
from agents.market_data_agent import MarketDataAgent
from agents.technical_analysis_agent import TechnicalAnalysisAgent
from agents.fundamentals_analyst import FundamentalsAnalyst
from agents.sentiment_analyst import SentimentAnalyst
from agents.news_analyst import NewsAnalyst
from agents.bull_researcher import BullResearcher
from agents.bear_researcher import BearResearcher
from agents.research_arbiter import ResearchArbiter
from agents.trade_strategist import TradeStrategist
from agents.risk_hawk import RiskHawk
from agents.risk_dove import RiskDove
from agents.risk_owl import RiskOwl
from agents.risk_arbiter import RiskArbiter
from agents.portfolio_manager import PortfolioManager
from graph.graph_conditions import after_bear, after_risk_panelist
from services.kite_mcp_client import KiteMCPClient
from utils.agent_memory import AgentMemory

logger = logging.getLogger(__name__)


def build_trading_graph(settings, kite_client: Optional[KiteMCPClient] = None):
    """
    Build and compile the full trading graph.

    Args:
        settings: Application settings
        kite_client: Optional KITE MCP client for live trading

    Returns:
        Compiled LangGraph StateGraph ready for .ainvoke()
    """
    # ── Initialize agent memory namespaces ──────────────────────
    memory_dir = getattr(settings, "MEMORY_DIR", "data/agent_memory") if settings else "data/agent_memory"
    memory_enabled = getattr(settings, "MEMORY_ENABLED", True) if settings else True

    def make_memory(name: str) -> Optional[AgentMemory]:
        return AgentMemory(name, memory_dir=memory_dir) if memory_enabled else None

    # ── Instantiate all agents ──────────────────────────────────
    market_data_agent = MarketDataAgent(settings, kite_client or KiteMCPClient(settings))
    tech_agent = TechnicalAnalysisAgent(settings)
    fundamentals_agent = FundamentalsAnalyst(settings)
    sentiment_agent = SentimentAnalyst(settings)
    news_agent = NewsAnalyst(settings)
    bull = BullResearcher(settings, memory=make_memory("bull_researcher"))
    bear = BearResearcher(settings, memory=make_memory("bear_researcher"))
    arbiter = ResearchArbiter(settings, memory=make_memory("research_arbiter"))
    strategist = TradeStrategist(settings, memory=make_memory("trade_strategist"))
    hawk = RiskHawk(settings)
    dove = RiskDove(settings)
    owl = RiskOwl(settings)
    risk_judge = RiskArbiter(settings, memory=make_memory("risk_arbiter"))
    pm = PortfolioManager(settings, kite_client=kite_client, memory=make_memory("portfolio_manager"))

    # ── Build the StateGraph ────────────────────────────────────
    graph = StateGraph(TradingState)

    # ── Add nodes ───────────────────────────────────────────────
    graph.add_node("market_data", market_data_agent.process_market_data)
    graph.add_node("technical_analysis", tech_agent.process_technical_analysis)
    graph.add_node("fundamentals", fundamentals_agent.process_fundamentals_analysis)
    graph.add_node("sentiment", sentiment_agent.process_sentiment_analysis)
    graph.add_node("news", news_agent.process_news_analysis)
    graph.add_node("bull_researcher", bull.process)
    graph.add_node("bear_researcher", bear.process)
    graph.add_node("research_arbiter", arbiter.process)
    graph.add_node("trade_strategist", strategist.process)
    graph.add_node("risk_hawk", hawk.process)
    graph.add_node("risk_dove", dove.process)
    graph.add_node("risk_owl", owl.process)
    graph.add_node("risk_arbiter", risk_judge.process)
    graph.add_node("portfolio_manager", pm.process)

    # ── Define edges ────────────────────────────────────────────

    # Stage 1: Sequential analyst pipeline
    graph.set_entry_point("market_data")
    graph.add_edge("market_data", "technical_analysis")
    graph.add_edge("technical_analysis", "fundamentals")
    graph.add_edge("fundamentals", "sentiment")
    graph.add_edge("sentiment", "news")

    # Stage 2: News feeds into bull researcher (debate entry point)
    graph.add_edge("news", "bull_researcher")

    # Stage 3: Debate loop — bull → bear → (conditional: bull again or arbiter)
    graph.add_edge("bull_researcher", "bear_researcher")
    graph.add_conditional_edges(
        "bear_researcher",
        after_bear,
        {
            "bull_researcher": "bull_researcher",
            "research_arbiter": "research_arbiter",
        },
    )

    # Stage 4: Arbiter → Trade Strategist
    graph.add_edge("research_arbiter", "trade_strategist")

    # Stage 5: Trade Strategist → Risk panel entry (hawk first)
    graph.add_edge("trade_strategist", "risk_hawk")

    # Stage 6: Risk panel rotation — hawk → dove → owl → (conditional: continue or arbiter)
    graph.add_edge("risk_hawk", "risk_dove")
    graph.add_edge("risk_dove", "risk_owl")
    graph.add_conditional_edges(
        "risk_owl",
        after_risk_panelist,
        {
            "risk_hawk": "risk_hawk",
            "risk_arbiter": "risk_arbiter",
        },
    )

    # Stage 7: Risk Arbiter → Portfolio Manager → END
    graph.add_edge("risk_arbiter", "portfolio_manager")
    graph.add_edge("portfolio_manager", END)

    # ── Compile ─────────────────────────────────────────────────
    compiled = graph.compile()
    logger.info("Trading graph compiled successfully with %d nodes", 14)

    return compiled
