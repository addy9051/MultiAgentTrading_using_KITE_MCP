#!/usr/bin/env python3
"""
Multi-Agent Kite Trading System — Main entry point.

Runs a single trading analysis cycle through the LangGraph agent pipeline,
including bull/bear debate and risk panel discussion.
"""

import asyncio
import logging
from config.settings import Settings
from services.trading_orchestrator import TradingOrchestrator
from utils.logging_config import setup_logging


async def main():
    """Run one trading cycle."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        settings = Settings()
        logger.info("Starting Multi-Agent Kite Trading System")
        logger.info(f"Target: {settings.TARGET_SYMBOL} | Mode: {'SIMULATION' if settings.SIMULATION_MODE else 'LIVE'}")
        logger.info(f"Debate rounds: {settings.MAX_DEBATE_ROUNDS} | Risk rounds: {settings.MAX_RISK_DISCUSSION_ROUNDS}")

        orchestrator = TradingOrchestrator(settings)
        await orchestrator.initialize()

        result = await orchestrator.run_trading_cycle()

        # Print key results
        decision = result.get("portfolio_decision", {})
        logger.info(f"Final Action: {decision.get('final_action', 'HOLD')}")
        logger.info(f"Rationale: {decision.get('rationale', 'N/A')[:200]}")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
