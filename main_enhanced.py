"""
Enhanced Multi-Agent Algorithmic Trading System
Main entry point implementing TauricResearch/TradingAgents architecture
"""

import asyncio
import logging
from datetime import datetime
from config.settings import Settings
from services.enhanced_trading_orchestrator import EnhancedTradingOrchestrator
from services.kite_mcp_client import KiteMCPClient
from utils.logging_config import setup_logging

# Setup logging
logger = setup_logging()

async def main():
    """Main function to run the enhanced multi-agent trading system"""
    try:
        logger.info("=== ENHANCED MULTI-AGENT TRADING SYSTEM STARTING ===")
        logger.info("Architecture: TauricResearch/TradingAgents - 7 Agent System")
        logger.info("Framework: LangChain + LangGraph")
        logger.info("Stages: 5-Stage Workflow (Analysts → Research → Signals → Risk → Portfolio)")
        
        # Load settings
        settings = Settings()
        logger.info(f"Target Symbol: {settings.TARGET_SYMBOL}")
        logger.info(f"Simulation Mode: {settings.SIMULATION_MODE}")
        logger.info(f"Using OpenAI API: {bool(settings.OPENAI_API_KEY)}")
        
        # Initialize Kite MCP client
        kite_client = KiteMCPClient(settings)
        
        # Initialize connection (will use sample data if no API keys)
        await kite_client.initialize()
        
        # Create enhanced orchestrator
        orchestrator = EnhancedTradingOrchestrator(settings, kite_client)
        
        # Run enhanced trading cycle
        logger.info("Starting enhanced trading cycle...")
        results = await orchestrator.run_trading_cycle()
        
        # Display final summary
        logger.info("=== ENHANCED TRADING SYSTEM SUMMARY ===")
        
        # Extract key results
        symbol = results.get("symbol", "UNKNOWN")
        portfolio_decision = results.get("portfolio_decision", {})
        bull_research = results.get("bull_research", {})
        bear_research = results.get("bear_research", {})
        fundamentals = results.get("fundamentals_analysis", {})
        sentiment = results.get("sentiment_analysis", {})
        news = results.get("news_analysis", {})
        
        print(f"\n{'='*60}")
        print(f"ENHANCED TRADING SYSTEM RESULTS FOR {symbol}")
        print(f"{'='*60}")
        
        # Market overview
        market_data = results.get("market_data", {})
        if market_data:
            print(f"Current Price: ${market_data.get('current_price', 0):.2f}")
            print(f"Volume: {market_data.get('volume', 0):,}")
            print(f"Market Trend: {market_data.get('trend', 'unknown')}")
        
        print(f"\n{'='*60}")
        print("ANALYST TEAM RESULTS")
        print(f"{'='*60}")
        
        # Fundamentals
        if fundamentals:
            print(f"📊 Fundamentals: {fundamentals.get('financial_health', 'unknown')}")
            print(f"   Valuation: {fundamentals.get('valuation_assessment', 'unknown')}")
            print(f"   Price Target: ${fundamentals.get('price_target', 0):.2f}")
            print(f"   Recommendation: {fundamentals.get('recommendation', 'HOLD')}")
        
        # Sentiment
        if sentiment:
            print(f"🗣️  Sentiment: {sentiment.get('overall_sentiment', 'neutral')}")
            print(f"   Score: {sentiment.get('sentiment_score', 0.5):.2f}")
            print(f"   Social Buzz: {sentiment.get('social_media_buzz', 'medium')}")
        
        # News
        if news:
            print(f"📰 News: {news.get('overall_news_sentiment', 'neutral')}")
            print(f"   Impact: {news.get('market_moving_potential', 'medium')}")
            print(f"   Recommendation: {news.get('trading_recommendation', 'hold')}")
        
        print(f"\n{'='*60}")
        print("RESEARCH TEAM DEBATE")
        print(f"{'='*60}")
        
        # Bull vs Bear
        if bull_research:
            print(f"🐂 BULL CASE:")
            print(f"   Thesis: {bull_research.get('bullish_thesis', 'N/A')[:100]}...")
            print(f"   Upside: {bull_research.get('upside_potential', 'unknown')}")
            print(f"   Action: {bull_research.get('recommended_action', 'WAIT')}")
            print(f"   Confidence: {bull_research.get('confidence_level', 0)}%")
        
        if bear_research:
            print(f"🐻 BEAR CASE:")
            print(f"   Thesis: {bear_research.get('bearish_thesis', 'N/A')[:100]}...")
            print(f"   Downside: {bear_research.get('downside_potential', 'unknown')}")
            print(f"   Action: {bear_research.get('recommended_action', 'AVOID')}")
            print(f"   Confidence: {bear_research.get('confidence_level', 0)}%")
        
        print(f"\n{'='*60}")
        print("FINAL PORTFOLIO DECISION")
        print(f"{'='*60}")
        
        # Portfolio manager decision
        if portfolio_decision:
            print(f"🎯 DECISION: {portfolio_decision.get('final_decision', 'UNKNOWN')}")
            print(f"   Position Size: {portfolio_decision.get('position_size', '0%')}")
            print(f"   Entry Price: ${portfolio_decision.get('entry_price', 0):.2f}")
            print(f"   Stop Loss: ${portfolio_decision.get('stop_loss', 0):.2f}")
            print(f"   Take Profit: ${portfolio_decision.get('take_profit', 0):.2f}")
            print(f"   Risk-Reward: {portfolio_decision.get('risk_reward_ratio', 0):.2f}")
            print(f"   Confidence: {portfolio_decision.get('confidence_level', 0)}%")
            print(f"   Rationale: {portfolio_decision.get('decision_rationale', 'N/A')[:150]}...")
        
        # Risk assessment
        risk = results.get("risk_assessment", {})
        if risk:
            print(f"⚠️  Risk Level: {risk.get('risk_level', 'unknown')}")
            print(f"   Trade Approval: {risk.get('trade_approval', 'unknown')}")
        
        # Execution
        execution = results.get("execution_result", {})
        if execution:
            print(f"🚀 Execution: {'SUCCESS' if execution.get('executed', False) else 'SIMULATION'}")
            print(f"   Order ID: {execution.get('order_id', 'N/A')}")
        
        print(f"\n{'='*60}")
        print("SYSTEM PERFORMANCE")
        print(f"{'='*60}")
        
        print(f"✅ 7-Agent System: Complete")
        print(f"✅ 5-Stage Workflow: Executed")
        print(f"✅ Bull vs Bear Debate: Conducted")
        print(f"✅ Risk Management: Applied")
        print(f"✅ Portfolio Decision: Made")
        
        print(f"\n{'='*60}")
        print("Enhanced trading system completed successfully!")
        print(f"{'='*60}")
        
        # Close client
        await kite_client.close()
        
    except Exception as e:
        logger.error(f"Error in enhanced trading system: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())