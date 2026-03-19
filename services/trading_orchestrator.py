"""
Trading Orchestrator — Thin wrapper around the LangGraph agent graph.

Initializes the system components (KITE MCP client, agent graph) and
provides a simple `run_trading_cycle()` interface that invokes the
compiled graph with an initial state.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from config.settings import Settings
from graph.agent_graph import build_trading_graph
from services.kite_mcp_client import KiteMCPClient

logger = logging.getLogger(__name__)


class TradingOrchestrator:
    """
    High-level orchestrator that wraps the LangGraph trading pipeline.

    Usage:
        orchestrator = TradingOrchestrator(settings)
        await orchestrator.initialize()
        result = await orchestrator.run_trading_cycle()
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.kite_client: Optional[KiteMCPClient] = None
        self.graph = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize KITE MCP client and compile the agent graph."""
        if self._initialized:
            return

        logger.info("Initializing trading orchestrator...")

        # Set up KITE MCP client
        self.kite_client = KiteMCPClient(self.settings)
        await self.kite_client.connect()

        # Build and compile the agent graph
        self.graph = build_trading_graph(self.settings, self.kite_client)

        self._initialized = True
        logger.info("Trading orchestrator initialized — graph compiled with debate & risk panel loops")

    async def run_trading_cycle(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a single trading analysis cycle.

        Args:
            symbol: Optional override for the target symbol

        Returns:
            Final state dictionary with all analysis results
        """
        if not self._initialized:
            await self.initialize()

        target_symbol = symbol or self.settings.TARGET_SYMBOL
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting trading cycle {cycle_id} for {target_symbol}")

        # Build initial state
        initial_state = {
            "symbol": target_symbol,
            "timestamp": datetime.now().isoformat(),
            "cycle_id": cycle_id,
            "messages": [],
            "debate_history": [],
            "debate_round": 0,
            "risk_discussion_history": [],
            "risk_discussion_round": 0,
            "market_data": None,
            "market_analysis": None,
            "technical_indicators": None,
            "technical_analysis": None,
            "fundamentals_analysis": None,
            "sentiment_analysis": None,
            "news_analysis": None,
            "bull_research": None,
            "bear_research": None,
            "research_verdict": None,
            "trade_proposal": None,
            "risk_verdict": None,
            "portfolio_decision": None,
            "execution_result": None,
            "error": None,
            "metadata": {
                "max_debate_rounds": self.settings.MAX_DEBATE_ROUNDS,
                "max_risk_discussion_rounds": self.settings.MAX_RISK_DISCUSSION_ROUNDS,
                "simulation_mode": self.settings.SIMULATION_MODE,
            },
        }

        try:
            # Invoke the graph
            final_state = await self.graph.ainvoke(initial_state)

            logger.info(f"Trading cycle {cycle_id} completed")
            self._log_summary(final_state)
            return final_state

        except Exception as e:
            logger.error(f"Trading cycle {cycle_id} failed: {e}")
            return {
                **initial_state,
                "error": str(e),
                "messages": initial_state["messages"] + [f"SYSTEM ERROR: {e}"],
            }

    def _log_summary(self, state: Dict[str, Any]) -> None:
        """Log a brief summary of the trading cycle outcome."""
        decision = state.get("portfolio_decision", {})
        execution = state.get("execution_result", {})
        verdict = state.get("research_verdict", {})
        risk = state.get("risk_verdict", {})

        logger.info("=" * 60)
        logger.info("TRADING CYCLE SUMMARY")
        logger.info("-" * 60)
        logger.info(f"Symbol: {state.get('symbol')}")
        logger.info(f"Research Verdict: {verdict.get('winning_side', '?')} / {verdict.get('recommendation', '?')}")
        logger.info(f"Risk Verdict: {'APPROVED' if risk.get('approved') else 'REJECTED'} ({risk.get('risk_level', '?')})")
        logger.info(f"Final Action: {decision.get('final_action', 'HOLD')}")
        logger.info(f"Execution: {execution.get('execution_status', 'N/A')}")
        logger.info(f"Debate rounds: {state.get('debate_round', 0)}")
        logger.info(f"Risk discussion rounds: {state.get('risk_discussion_round', 0)}")
        logger.info(f"Total messages: {len(state.get('messages', []))}")
        logger.info("=" * 60)
