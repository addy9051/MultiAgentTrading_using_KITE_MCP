"""
Trading Orchestrator - Coordinates all trading agents using LangGraph
"""

import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END, START
from agents.market_data_agent import MarketDataAgent
from agents.technical_analysis_agent import TechnicalAnalysisAgent
from agents.signal_generation_agent import SignalGenerationAgent
from agents.risk_assessment_agent import RiskAssessmentAgent
from services.kite_mcp_client import KiteMCPClient
from models.trading_state import TradingState

logger = logging.getLogger(__name__)

class TradingOrchestrator:
    """Main orchestrator for the multi-agent trading system"""
    
    def __init__(self, settings):
        self.settings = settings
        self.kite_client = KiteMCPClient(settings)
        
        # Initialize agents
        self.market_data_agent = MarketDataAgent(settings, self.kite_client)
        self.technical_analysis_agent = TechnicalAnalysisAgent(settings)
        self.signal_generation_agent = SignalGenerationAgent(settings)
        self.risk_assessment_agent = RiskAssessmentAgent(settings)
        
        # Initialize workflow
        self.workflow = None
        self.compiled_workflow = None
    
    async def initialize(self):
        """Initialize the trading orchestrator"""
        try:
            # Initialize MCP client
            await self.kite_client.initialize()
            
            # Create the workflow
            self.create_workflow()
            
            logger.info("Trading orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize trading orchestrator: {str(e)}")
            raise
    
    def create_workflow(self):
        """Create the LangGraph workflow"""
        try:
            # Create StateGraph
            self.workflow = StateGraph(TradingState)
            
            # Add agent nodes
            self.workflow.add_node("market_data", self.market_data_node)
            self.workflow.add_node("technical_analysis", self.technical_analysis_node)
            self.workflow.add_node("signal_generation", self.signal_generation_node)
            self.workflow.add_node("risk_assessment", self.risk_assessment_node)
            self.workflow.add_node("trade_execution", self.trade_execution_node)
            
            # Define workflow edges
            self.workflow.add_edge(START, "market_data")
            self.workflow.add_edge("market_data", "technical_analysis")
            self.workflow.add_edge("technical_analysis", "signal_generation")
            self.workflow.add_edge("signal_generation", "risk_assessment")
            self.workflow.add_edge("risk_assessment", "trade_execution")
            self.workflow.add_edge("trade_execution", END)
            
            # Compile the workflow
            self.compiled_workflow = self.workflow.compile()
            
            logger.info("Trading workflow created successfully")
            
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            raise
    
    async def market_data_node(self, state: TradingState) -> TradingState:
        """Market data processing node"""
        try:
            logger.info("Processing market data...")
            updated_state = await self.market_data_agent.process_market_data(state)
            return {**state, **updated_state}
            
        except Exception as e:
            logger.error(f"Error in market data node: {str(e)}")
            return {**state, "error": str(e)}
    
    async def technical_analysis_node(self, state: TradingState) -> TradingState:
        """Technical analysis processing node"""
        try:
            logger.info("Processing technical analysis...")
            updated_state = await self.technical_analysis_agent.process_technical_analysis(state)
            return {**state, **updated_state}
            
        except Exception as e:
            logger.error(f"Error in technical analysis node: {str(e)}")
            return {**state, "error": str(e)}
    
    async def signal_generation_node(self, state: TradingState) -> TradingState:
        """Signal generation processing node"""
        try:
            logger.info("Processing signal generation...")
            updated_state = await self.signal_generation_agent.process_signal_generation(state)
            return {**state, **updated_state}
            
        except Exception as e:
            logger.error(f"Error in signal generation node: {str(e)}")
            return {**state, "error": str(e)}
    
    async def risk_assessment_node(self, state: TradingState) -> TradingState:
        """Risk assessment processing node"""
        try:
            logger.info("Processing risk assessment...")
            updated_state = await self.risk_assessment_agent.process_risk_assessment(state)
            return {**state, **updated_state}
            
        except Exception as e:
            logger.error(f"Error in risk assessment node: {str(e)}")
            return {**state, "error": str(e)}
    
    async def trade_execution_node(self, state: TradingState) -> TradingState:
        """Trade execution processing node"""
        try:
            logger.info("Processing trade execution...")
            
            # Get final trading decision
            risk_assessment = state.get("risk_assessment", {})
            trading_signals = state.get("trading_signals", {})
            
            approval = risk_assessment.get("final_approval", "rejected")
            signal = trading_signals.get("final_signal", "HOLD")
            
            execution_result = {
                "executed": False,
                "order_id": None,
                "execution_price": 0,
                "execution_quantity": 0,
                "execution_status": "NOT_EXECUTED"
            }
            
            if approval == "approved" and signal in ["BUY", "SELL"]:
                # Prepare order data
                market_data = state.get("market_data", {})
                position_sizing = risk_assessment.get("position_sizing", {})
                
                order_data = {
                    "symbol": market_data.get("symbol", self.settings.TARGET_SYMBOL),
                    "exchange": self.settings.EXCHANGE,
                    "transaction_type": signal,
                    "quantity": position_sizing.get("shares", 1),
                    "price": market_data.get("current_price", 0),
                    "order_type": "MARKET",
                    "product": "CNC"
                }
                
                # Execute order (simulation)
                order_result = await self.kite_client.place_order(order_data)
                
                execution_result = {
                    "executed": True,
                    "order_id": order_result.get("order_id", "MOCK_ORDER"),
                    "execution_price": order_data["price"],
                    "execution_quantity": order_data["quantity"],
                    "execution_status": "COMPLETED_SIMULATION",
                    "order_data": order_data
                }
                
                logger.info(f"Order executed (simulation): {signal} {order_data['quantity']} shares at {order_data['price']}")
            
            else:
                logger.info(f"Trade not executed - Approval: {approval}, Signal: {signal}")
            
            updated_state = {
                "execution_result": execution_result,
                "messages": state.get("messages", []) + [
                    f"Trade Execution: {execution_result['execution_status']}",
                    f"Signal: {signal}, Approval: {approval}"
                ]
            }
            
            return {**state, **updated_state}
            
        except Exception as e:
            logger.error(f"Error in trade execution node: {str(e)}")
            return {**state, "error": str(e)}
    
    async def run_trading_cycle(self) -> Dict[str, Any]:
        """Run a complete trading cycle"""
        try:
            logger.info("Starting trading cycle...")
            
            # Initialize state
            initial_state = {
                "symbol": self.settings.TARGET_SYMBOL,
                "messages": [f"Starting trading analysis for {self.settings.TARGET_SYMBOL}"],
                "timestamp": "",
                "cycle_id": "cycle_001"
            }
            
            # Run the workflow
            result = await self.compiled_workflow.ainvoke(initial_state)
            
            # Log final results
            self.log_trading_results(result)
            
            logger.info("Trading cycle completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
            raise
        
        finally:
            # Clean up
            await self.kite_client.close()
    
    def log_trading_results(self, result: Dict[str, Any]):
        """Log the final trading results"""
        try:
            logger.info("=== TRADING CYCLE RESULTS ===")
            
            # Market data summary
            market_data = result.get("market_data", {})
            logger.info(f"Symbol: {market_data.get('symbol', 'N/A')}")
            logger.info(f"Current Price: {market_data.get('current_price', 'N/A')}")
            logger.info(f"Volume: {market_data.get('volume', 'N/A')}")
            
            # Technical analysis summary
            technical_analysis = result.get("technical_analysis", {})
            logger.info(f"Trend: {technical_analysis.get('trend_direction', 'N/A')}")
            logger.info(f"RSI: {result.get('technical_indicators', {}).get('rsi', 'N/A')}")
            
            # Trading signals
            trading_signals = result.get("trading_signals", {})
            logger.info(f"Final Signal: {trading_signals.get('final_signal', 'N/A')}")
            logger.info(f"Confidence: {trading_signals.get('confidence', 'N/A')}%")
            
            # Risk assessment
            risk_assessment = result.get("risk_assessment", {})
            logger.info(f"Risk Level: {risk_assessment.get('comprehensive_analysis', {}).get('risk_level', 'N/A')}")
            logger.info(f"Trade Approval: {risk_assessment.get('final_approval', 'N/A')}")
            
            # Execution results
            execution_result = result.get("execution_result", {})
            logger.info(f"Executed: {execution_result.get('executed', False)}")
            logger.info(f"Order ID: {execution_result.get('order_id', 'N/A')}")
            
            # All messages
            logger.info("=== AGENT MESSAGES ===")
            for message in result.get("messages", []):
                logger.info(f"  {message}")
            
            logger.info("=== END RESULTS ===")
            
        except Exception as e:
            logger.error(f"Error logging trading results: {str(e)}")
