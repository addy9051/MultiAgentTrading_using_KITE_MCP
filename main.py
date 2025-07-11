#!/usr/bin/env python3
"""
Multi-Agent Algorithmic Trading System MVP
Main entry point for the trading system
"""

import asyncio
import logging
from config.settings import Settings
from services.trading_orchestrator import TradingOrchestrator
from utils.logging_config import setup_logging

async def main():
    """Main function to run the multi-agent trading system"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize settings
        settings = Settings()
        logger.info("Starting Multi-Agent Trading System MVP")
        logger.info(f"Target Symbol: {settings.TARGET_SYMBOL}")
        logger.info(f"MCP Server URL: {settings.KITE_MCP_URL}")
        
        # Create and run trading orchestrator
        orchestrator = TradingOrchestrator(settings)
        
        # Initialize the system
        await orchestrator.initialize()
        
        # Run trading cycle
        await orchestrator.run_trading_cycle()
        
        logger.info("Trading system completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
