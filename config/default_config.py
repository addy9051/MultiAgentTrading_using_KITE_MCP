"""
Default Configuration — Centralized configuration dictionary for the trading system.

Override any value by passing a modified copy to the orchestrator or graph builder.
Environment variables in settings.py take precedence at runtime.
"""

DEFAULT_CONFIG = {
    # ── LLM Provider ─────────────────────────────────────────────
    "llm_provider": "openai",
    "llm_model": "gpt-4o",
    "llm_temperature": 0.1,
    "llm_temperature_creative": 0.3,   # for researchers / debate agents

    # ── Debate Settings ──────────────────────────────────────────
    "max_debate_rounds": 2,             # bull ↔ bear exchange rounds
    "max_risk_discussion_rounds": 2,    # hawk → dove → owl rotation rounds

    # ── Trading Parameters ───────────────────────────────────────
    "target_symbol": "RELIANCE",
    "exchange": "NSE",
    "default_quantity": 1,
    "simulation_mode": True,

    # ── Risk Management ──────────────────────────────────────────
    "max_position_size_pct": 0.02,      # 2% of portfolio
    "default_stop_loss_pct": 0.05,      # 5% stop loss
    "account_balance": 100_000,         # default paper balance

    # ── Technical Analysis ───────────────────────────────────────
    "rsi_period": 14,
    "rsi_overbought": 70.0,
    "rsi_oversold": 30.0,

    # ── Memory ───────────────────────────────────────────────────
    "memory_enabled": True,
    "memory_dir": "data/agent_memory",
    "memory_max_entries": 50,

    # ── KITE MCP ─────────────────────────────────────────────────
    "kite_mcp_url": "http://localhost:8080",
    "kite_historical_interval": "15minute",
    "kite_historical_days": 30,

    # ── Logging ──────────────────────────────────────────────────
    "log_level": "INFO",
}
