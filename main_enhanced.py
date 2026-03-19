#!/usr/bin/env python3
"""
Multi-Agent Kite Trading System — Enhanced entry point with detailed output.

Runs a trading cycle and displays a rich summary of all agent outputs,
debate results, risk panel discussion, and final execution.
"""

import asyncio
import logging
from config.settings import Settings
from services.trading_orchestrator import TradingOrchestrator
from utils.logging_config import setup_logging


async def main():
    """Run a trading cycle with detailed console output."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        settings = Settings()
        logger.info("=== MULTI-AGENT KITE TRADING SYSTEM ===")
        logger.info(f"Target: {settings.TARGET_SYMBOL} | Mode: {'SIMULATION' if settings.SIMULATION_MODE else 'LIVE'}")
        logger.info(f"Debate Rounds: {settings.MAX_DEBATE_ROUNDS} | Risk Rounds: {settings.MAX_RISK_DISCUSSION_ROUNDS}")

        orchestrator = TradingOrchestrator(settings)
        await orchestrator.initialize()

        results = await orchestrator.run_trading_cycle()

        # ── Display summary ─────────────────────────────────────
        symbol = results.get("symbol", "UNKNOWN")
        market_data = results.get("market_data", {})
        fundamentals = results.get("fundamentals_analysis", {})
        sentiment = results.get("sentiment_analysis", {})
        news = results.get("news_analysis", {})
        bull = results.get("bull_research", {})
        bear = results.get("bear_research", {})
        verdict = results.get("research_verdict", {})
        proposal = results.get("trade_proposal", {})
        risk_verdict = results.get("risk_verdict", {})
        decision = results.get("portfolio_decision", {})
        execution = results.get("execution_result", {})

        print(f"\n{'='*60}")
        print(f"  TRADING RESULTS — {symbol}")
        print(f"{'='*60}")

        if market_data:
            print(f"\n📈 Market: ₹{market_data.get('current_price', 0):.2f} | Vol: {market_data.get('volume', 0):,}")

        print(f"\n{'─'*60}")
        print("  ANALYST PANEL")
        print(f"{'─'*60}")
        if fundamentals:
            print(f"  📊 Fundamentals: {fundamentals.get('financial_health', '?')} | {fundamentals.get('valuation_assessment', '?')}")
        if sentiment:
            print(f"  🗣️  Sentiment: {sentiment.get('overall_sentiment', '?')} ({sentiment.get('sentiment_score', 0):.2f})")
        if news:
            print(f"  📰 News: {news.get('overall_news_sentiment', '?')} | Impact: {news.get('market_moving_potential', '?')}")

        print(f"\n{'─'*60}")
        print("  RESEARCH DEBATE")
        print(f"{'─'*60}")
        if bull:
            print(f"  🐂 Bull: {bull.get('bullish_thesis', '?')[:80]}...")
            print(f"     Upside: {bull.get('upside_potential', '?')} | Confidence: {bull.get('confidence_level', 0)}%")
        if bear:
            print(f"  🐻 Bear: {bear.get('bearish_thesis', '?')[:80]}...")
            print(f"     Downside: {bear.get('downside_potential', '?')} | Confidence: {bear.get('confidence_level', 0)}%")
        if verdict:
            print(f"  ⚖️  Verdict: {verdict.get('winning_side', '?')} → {verdict.get('recommendation', '?')} ({verdict.get('confidence', 0)}%)")

        print(f"\n{'─'*60}")
        print("  RISK PANEL")
        print(f"{'─'*60}")
        if risk_verdict:
            status = "✅ APPROVED" if risk_verdict.get("approved") else "❌ REJECTED"
            print(f"  {status} | Risk: {risk_verdict.get('risk_level', '?')}")
            print(f"  Size: {risk_verdict.get('adjusted_position_size_pct', 0)}% | SL: {risk_verdict.get('adjusted_stop_loss_pct', 0)}%")

        print(f"\n{'─'*60}")
        print("  FINAL DECISION")
        print(f"{'─'*60}")
        if decision:
            print(f"  🎯 {decision.get('final_action', 'HOLD')} — {decision.get('rationale', '')[:120]}")
        if execution:
            print(f"  🚀 Execution: {execution.get('execution_status', 'N/A')} | Order: {execution.get('order_id', 'None')}")

        print(f"\n{'─'*60}")
        print(f"  Debate rounds: {results.get('debate_round', 0)} | Risk rounds: {results.get('risk_discussion_round', 0)}")
        print(f"  Total agent messages: {len(results.get('messages', []))}")
        print(f"{'='*60}\n")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())