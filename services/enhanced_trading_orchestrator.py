"""
Enhanced Trading Orchestrator - Implements TauricResearch 7-agent architecture
Based on the TauricResearch/TradingAgents multi-agent system
"""

import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import uuid

from models.trading_state import TradingState
from agents.market_data_agent import MarketDataAgent
from agents.technical_analysis_agent import TechnicalAnalysisAgent
from agents.fundamentals_analyst import FundamentalsAnalyst
from agents.sentiment_analyst import SentimentAnalyst
from agents.news_analyst import NewsAnalyst
from agents.bull_researcher import BullResearcher
from agents.bear_researcher import BearResearcher
from agents.signal_generation_agent import SignalGenerationAgent
from agents.risk_assessment_agent import RiskAssessmentAgent
from agents.portfolio_manager import PortfolioManager
from services.kite_mcp_client import KiteMCPClient

logger = logging.getLogger(__name__)

class EnhancedTradingOrchestrator:
    """
    Enhanced Trading Orchestrator implementing TauricResearch 7-agent architecture
    
    Agent Flow:
    Stage I: Analyst Team (4 agents) - Parallel analysis
    Stage II: Research Team (2 agents) - Bull vs Bear research
    Stage III: Trading Signals - Signal generation
    Stage IV: Risk Management - Risk assessment
    Stage V: Portfolio Management - Final decision
    """
    
    def __init__(self, settings, kite_client: KiteMCPClient):
        self.settings = settings
        self.kite_client = kite_client
        
        # Initialize all agents
        self.market_data_agent = MarketDataAgent(settings, kite_client)
        self.technical_analysis_agent = TechnicalAnalysisAgent(settings)
        self.fundamentals_analyst = FundamentalsAnalyst(settings)
        self.sentiment_analyst = SentimentAnalyst(settings)
        self.news_analyst = NewsAnalyst(settings)
        self.bull_researcher = BullResearcher(settings)
        self.bear_researcher = BearResearcher(settings)
        self.signal_generation_agent = SignalGenerationAgent(settings)
        self.risk_assessment_agent = RiskAssessmentAgent(settings)
        self.portfolio_manager = PortfolioManager(settings)
        
        # Agent execution order
        self.stage_1_agents = [
            ("Market Data Agent", self.market_data_agent.process_market_data),
            ("Technical Analysis Agent", self.technical_analysis_agent.process_technical_analysis),
            ("Fundamentals Analyst", self.fundamentals_analyst.process_fundamentals_analysis),
            ("Sentiment Analyst", self.sentiment_analyst.process_sentiment_analysis),
            ("News Analyst", self.news_analyst.process_news_analysis)
        ]
        
        self.stage_2_agents = [
            ("Bull Researcher", self.bull_researcher.process_bull_research),
            ("Bear Researcher", self.bear_researcher.process_bear_research)
        ]
        
        self.stage_3_agents = [
            ("Signal Generation Agent", self.signal_generation_agent.process_signal_generation)
        ]
        
        self.stage_4_agents = [
            ("Risk Assessment Agent", self.risk_assessment_agent.process_risk_assessment)
        ]
        
        self.stage_5_agents = [
            ("Portfolio Manager", self.portfolio_manager.process_portfolio_decision)
        ]
        
        # Results storage
        self.latest_results = {}
    
    async def run_trading_cycle(self, symbol: str = None) -> Dict[str, Any]:
        """
        Run a complete trading cycle with the enhanced 7-agent architecture
        """
        try:
            # Use configured symbol if none provided
            if symbol is None:
                symbol = self.settings.TARGET_SYMBOL
            
            # Initialize state
            state = TradingState(
                symbol=symbol,
                timestamp=datetime.now().isoformat(),
                cycle_id=str(uuid.uuid4()),
                messages=[f"Starting enhanced trading analysis for {symbol}"],
                market_data=None,
                market_analysis=None,
                technical_indicators=None,
                technical_analysis=None,
                fundamentals_analysis=None,
                sentiment_analysis=None,
                news_analysis=None,
                bull_research=None,
                bear_research=None,
                trading_signals=None,
                risk_assessment=None,
                portfolio_decision=None,
                execution_result=None,
                error=None,
                metadata={}
            )
            
            logger.info(f"=== STARTING ENHANCED TRADING CYCLE FOR {symbol} ===")
            
            # STAGE I: ANALYST TEAM - Parallel execution
            logger.info("STAGE I: Running Analyst Team (5 agents in parallel)")
            await self._run_stage_parallel(state, self.stage_1_agents, "Stage I")
            
            # STAGE II: RESEARCH TEAM - Bull vs Bear research
            logger.info("STAGE II: Running Research Team (Bull vs Bear)")
            await self._run_stage_parallel(state, self.stage_2_agents, "Stage II")
            
            # STAGE III: TRADING SIGNALS
            logger.info("STAGE III: Generating Trading Signals")
            await self._run_stage_sequential(state, self.stage_3_agents, "Stage III")
            
            # STAGE IV: RISK MANAGEMENT
            logger.info("STAGE IV: Risk Assessment")
            await self._run_stage_sequential(state, self.stage_4_agents, "Stage IV")
            
            # STAGE V: PORTFOLIO MANAGEMENT
            logger.info("STAGE V: Portfolio Management Decision")
            await self._run_stage_sequential(state, self.stage_5_agents, "Stage V")
            
            # Store results
            self.latest_results = dict(state)
            
            # Log final results
            await self._log_final_results(state)
            
            logger.info(f"=== ENHANCED TRADING CYCLE COMPLETED FOR {symbol} ===")
            
            return dict(state)
            
        except Exception as e:
            logger.error(f"Error in enhanced trading cycle: {str(e)}")
            error_state = TradingState(
                symbol=symbol or "UNKNOWN",
                timestamp=datetime.now().isoformat(),
                cycle_id=str(uuid.uuid4()),
                messages=[f"Enhanced trading cycle failed: {str(e)}"],
                market_data=None,
                market_analysis=None,
                technical_indicators=None,
                technical_analysis=None,
                fundamentals_analysis=None,
                sentiment_analysis=None,
                news_analysis=None,
                bull_research=None,
                bear_research=None,
                trading_signals=None,
                risk_assessment=None,
                portfolio_decision=None,
                execution_result=None,
                error=str(e),
                metadata={}
            )
            return dict(error_state)
    
    async def _run_stage_parallel(self, state: TradingState, agents: List, stage_name: str):
        """Run agents in parallel for maximum efficiency"""
        try:
            logger.info(f"Executing {stage_name} agents in parallel...")
            
            # Create tasks for parallel execution
            tasks = []
            for agent_name, agent_func in agents:
                task = asyncio.create_task(
                    self._safe_agent_execution(agent_func, state, agent_name)
                )
                tasks.append(task)
            
            # Wait for all agents to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                agent_name, agent_func = agents[i]
                if isinstance(result, Exception):
                    logger.error(f"{agent_name} failed: {str(result)}")
                    state["messages"].append(f"{agent_name}: Failed - {str(result)}")
                else:
                    # Update state with agent results
                    state.update(result)
            
            logger.info(f"{stage_name} completed successfully")
            
        except Exception as e:
            logger.error(f"Error in {stage_name}: {str(e)}")
            state["messages"].append(f"{stage_name}: Failed - {str(e)}")
    
    async def _run_stage_sequential(self, state: TradingState, agents: List, stage_name: str):
        """Run agents sequentially when order matters"""
        try:
            logger.info(f"Executing {stage_name} agents sequentially...")
            
            for agent_name, agent_func in agents:
                try:
                    result = await self._safe_agent_execution(agent_func, state, agent_name)
                    state.update(result)
                except Exception as e:
                    logger.error(f"{agent_name} failed: {str(e)}")
                    state["messages"].append(f"{agent_name}: Failed - {str(e)}")
            
            logger.info(f"{stage_name} completed successfully")
            
        except Exception as e:
            logger.error(f"Error in {stage_name}: {str(e)}")
            state["messages"].append(f"{stage_name}: Failed - {str(e)}")
    
    async def _safe_agent_execution(self, agent_func, state: TradingState, agent_name: str):
        """Safely execute an agent function with error handling"""
        try:
            logger.info(f"Executing {agent_name}...")
            result = await agent_func(state)
            logger.info(f"{agent_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{agent_name} execution failed: {str(e)}")
            raise e
    
    async def _log_final_results(self, state: TradingState):
        """Log comprehensive final results"""
        try:
            logger.info("=== ENHANCED TRADING CYCLE RESULTS ===")
            
            # Basic info
            logger.info(f"Symbol: {state.get('symbol', 'UNKNOWN')}")
            logger.info(f"Cycle ID: {state.get('cycle_id', 'UNKNOWN')}")
            logger.info(f"Timestamp: {state.get('timestamp', 'UNKNOWN')}")
            
            # Market data
            market_data = state.get("market_data", {})
            if market_data:
                logger.info(f"Current Price: ${market_data.get('current_price', 0):.2f}")
                logger.info(f"Volume: {market_data.get('volume', 0):,}")
                logger.info(f"Trend: {market_data.get('trend', 'unknown')}")
            
            # Technical analysis
            technical = state.get("technical_analysis", {})
            if technical:
                logger.info(f"RSI: {technical.get('rsi_value', 0):.2f}")
                logger.info(f"Technical Score: {technical.get('overall_score', 0)}")
            
            # Fundamentals
            fundamentals = state.get("fundamentals_analysis", {})
            if fundamentals:
                logger.info(f"Financial Health: {fundamentals.get('financial_health', 'unknown')}")
                logger.info(f"Valuation: {fundamentals.get('valuation_assessment', 'unknown')}")
                logger.info(f"Price Target: ${fundamentals.get('price_target', 0):.2f}")
            
            # Sentiment
            sentiment = state.get("sentiment_analysis", {})
            if sentiment:
                logger.info(f"Sentiment: {sentiment.get('overall_sentiment', 'unknown')}")
                logger.info(f"Sentiment Score: {sentiment.get('sentiment_score', 0):.2f}")
            
            # News
            news = state.get("news_analysis", {})
            if news:
                logger.info(f"News Sentiment: {news.get('overall_news_sentiment', 'unknown')}")
                logger.info(f"News Impact: {news.get('market_moving_potential', 'unknown')}")
            
            # Bull research
            bull = state.get("bull_research", {})
            if bull:
                logger.info(f"Bull Case: {bull.get('recommended_action', 'unknown')}")
                logger.info(f"Upside Potential: {bull.get('upside_potential', 'unknown')}")
            
            # Bear research
            bear = state.get("bear_research", {})
            if bear:
                logger.info(f"Bear Case: {bear.get('recommended_action', 'unknown')}")
                logger.info(f"Downside Risk: {bear.get('downside_potential', 'unknown')}")
            
            # Trading signals
            signals = state.get("trading_signals", {})
            if signals:
                logger.info(f"Trading Signal: {signals.get('final_signal', 'unknown')}")
                logger.info(f"Signal Confidence: {signals.get('confidence', 0)}%")
            
            # Risk assessment
            risk = state.get("risk_assessment", {})
            if risk:
                logger.info(f"Risk Level: {risk.get('risk_level', 'unknown')}")
                logger.info(f"Trade Approval: {risk.get('trade_approval', 'unknown')}")
            
            # Portfolio decision
            portfolio = state.get("portfolio_decision", {})
            if portfolio:
                logger.info(f"Final Decision: {portfolio.get('final_decision', 'unknown')}")
                logger.info(f"Position Size: {portfolio.get('position_size', 'unknown')}")
                logger.info(f"Entry Price: ${portfolio.get('entry_price', 0):.2f}")
                logger.info(f"Risk-Reward: {portfolio.get('risk_reward_ratio', 0):.2f}")
            
            # Execution
            execution = state.get("execution_result", {})
            if execution:
                logger.info(f"Executed: {execution.get('executed', False)}")
                logger.info(f"Order ID: {execution.get('order_id', 'None')}")
            
            # Agent messages
            logger.info("=== AGENT MESSAGES ===")
            for message in state.get("messages", []):
                logger.info(f"  {message}")
            
            logger.info("=== END ENHANCED RESULTS ===")
            
        except Exception as e:
            logger.error(f"Error logging results: {str(e)}")
    
    def get_latest_results(self) -> Dict[str, Any]:
        """Get the latest trading results"""
        return self.latest_results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "status": "ready",
            "agents_count": 7,
            "architecture": "TauricResearch Enhanced",
            "stages": 5,
            "latest_cycle": self.latest_results.get("cycle_id", "none"),
            "latest_symbol": self.latest_results.get("symbol", "none"),
            "latest_timestamp": self.latest_results.get("timestamp", "none")
        }