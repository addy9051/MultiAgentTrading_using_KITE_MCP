"""
Portfolio Manager — Makes final trading decisions and executes via KITE MCP.

Receives the risk verdict and trade proposal, and either executes the trade
through the Kite MCP client or logs a simulation. This is the final node
in the trading graph.
"""

import logging
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from models.trading_state import TradingState
from services.kite_mcp_client import KiteMCPClient
from utils.agent_memory import AgentMemory

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Final decision-maker and trade executor in the pipeline."""

    def __init__(self, settings, kite_client: KiteMCPClient = None,
                 memory: AgentMemory = None):
        self.settings = settings
        self.kite_client = kite_client
        self.memory = memory
        self.use_sample_llm = not settings.OPENAI_API_KEY

        self.llm = None
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.1,
            )

    async def decide_and_execute(self, state: TradingState) -> Dict[str, Any]:
        """Make final decision based on risk verdict and execute if approved."""
        risk_verdict = state.get("risk_verdict", {})
        trade_proposal = state.get("trade_proposal", {})
        market_data = state.get("market_data", {})
        research_verdict = state.get("research_verdict", {})
        symbol = market_data.get("symbol", self.settings.TARGET_SYMBOL)

        approved = risk_verdict.get("approved", False)
        action = trade_proposal.get("action", "HOLD")

        # Build portfolio decision
        if not approved or action == "HOLD":
            decision = self._build_no_trade_decision(risk_verdict, trade_proposal, symbol)
            execution = self._no_execution()
        else:
            decision = await self._build_trade_decision(
                trade_proposal, risk_verdict, research_verdict, market_data
            )
            execution = await self._execute_trade(decision, market_data)

        if self.memory:
            self.memory.store("portfolio_decision", {
                "symbol": symbol,
                "action": decision.get("final_action", "HOLD"),
                "executed": execution.get("executed", False),
            })

        return {
            "portfolio_decision": decision,
            "execution_result": execution,
        }

    async def _build_trade_decision(self, proposal: Dict, risk_verdict: Dict,
                                     research_verdict: Dict, market_data: Dict) -> Dict[str, Any]:
        """Build the final trade decision with adjusted parameters."""
        price = market_data.get("current_price", 0)
        adj_size = risk_verdict.get("adjusted_position_size_pct", 1.0)
        adj_sl_pct = risk_verdict.get("adjusted_stop_loss_pct", 5.0)

        stop_loss = round(price * (1 - adj_sl_pct / 100), 2)
        take_profit = proposal.get("take_profit", round(price * 1.10, 2))

        # Calculate shares from position size
        position_value = self.settings.ACCOUNT_BALANCE * (adj_size / 100)
        shares = int(position_value / price) if price > 0 else 0

        return {
            "final_action": proposal.get("action", "HOLD"),
            "symbol": market_data.get("symbol", "UNKNOWN"),
            "shares": max(shares, 1),
            "entry_price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size_pct": adj_size,
            "time_horizon": proposal.get("time_horizon", "swing"),
            "risk_level": risk_verdict.get("risk_level", "moderate"),
            "research_winner": research_verdict.get("winning_side", "balanced"),
            "rationale": f"Approved by Risk Arbiter ({risk_verdict.get('risk_level', '?')}) "
                         f"based on {research_verdict.get('winning_side', '?')} research verdict. "
                         f"Position: {adj_size}% / {shares} shares at ₹{price:.2f}",
        }

    def _build_no_trade_decision(self, risk_verdict: Dict, proposal: Dict,
                                  symbol: str) -> Dict[str, Any]:
        """Decision when trade is not approved."""
        reason = risk_verdict.get("reasoning", "Risk verdict rejected the trade")
        if proposal.get("action") == "HOLD":
            reason = "Trade strategist recommended HOLD — no action needed"

        return {
            "final_action": "HOLD",
            "symbol": symbol,
            "shares": 0,
            "entry_price": 0,
            "stop_loss": 0,
            "take_profit": 0,
            "position_size_pct": 0,
            "time_horizon": "none",
            "risk_level": risk_verdict.get("risk_level", "unknown"),
            "research_winner": "n/a",
            "rationale": reason,
        }

    async def _execute_trade(self, decision: Dict, market_data: Dict) -> Dict[str, Any]:
        """Execute the trade via KITE MCP or simulation."""
        action = decision.get("final_action", "HOLD")
        if action == "HOLD":
            return self._no_execution()

        order_data = {
            "symbol": decision.get("symbol", self.settings.TARGET_SYMBOL),
            "exchange": self.settings.EXCHANGE,
            "transaction_type": action,
            "quantity": decision.get("shares", 1),
            "price": decision.get("entry_price", 0),
            "order_type": "MARKET",
            "product": "CNC",
        }

        if self.kite_client:
            try:
                order_result = await self.kite_client.place_order(order_data)
                return {
                    "executed": True,
                    "order_id": order_result.get("order_id", "UNKNOWN"),
                    "execution_price": order_data["price"],
                    "execution_quantity": order_data["quantity"],
                    "execution_status": "COMPLETED" if not self.settings.SIMULATION_MODE else "SIMULATED",
                    "order_data": order_data,
                    "error": None,
                }
            except Exception as e:
                logger.error(f"Order execution failed: {e}")
                return {
                    "executed": False,
                    "order_id": None,
                    "execution_price": 0,
                    "execution_quantity": 0,
                    "execution_status": "FAILED",
                    "order_data": order_data,
                    "error": str(e),
                }
        else:
            # No kite client — log as simulation
            logger.info(f"SIMULATION: {action} {order_data['quantity']} shares of {order_data['symbol']} at ₹{order_data['price']:.2f}")
            return {
                "executed": True,
                "order_id": f"SIM_{order_data['symbol']}_{id(order_data) % 10000}",
                "execution_price": order_data["price"],
                "execution_quantity": order_data["quantity"],
                "execution_status": "SIMULATED",
                "order_data": order_data,
                "error": None,
            }

    def _no_execution(self) -> Dict[str, Any]:
        return {
            "executed": False,
            "order_id": None,
            "execution_price": 0,
            "execution_quantity": 0,
            "execution_status": "NOT_EXECUTED",
            "order_data": None,
            "error": None,
        }

    async def process(self, state: TradingState) -> Dict[str, Any]:
        """LangGraph node entry point."""
        logger.info("Portfolio Manager: Making final decision...")
        result = await self.decide_and_execute(state)

        decision = result.get("portfolio_decision", {})
        execution = result.get("execution_result", {})

        return {
            "portfolio_decision": decision,
            "execution_result": execution,
            "messages": [
                f"Portfolio Manager: {decision.get('final_action', 'HOLD')} — {decision.get('rationale', '')[:100]}",
                f"Execution: {execution.get('execution_status', 'N/A')} | Order: {execution.get('order_id', 'None')}",
            ],
        }