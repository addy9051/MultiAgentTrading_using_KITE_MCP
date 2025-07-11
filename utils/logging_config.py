"""
Logging configuration for the trading system
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup comprehensive logging for the trading system"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Default log file with timestamp
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{log_dir}/trading_system_{timestamp}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.INFO)
    
    # Create logger for trading system
    logger = logging.getLogger("trading_system")
    logger.info("Logging system initialized")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Log level: {log_level}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
