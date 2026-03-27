"""
Logging configuration for Fleet Intelligence AI
"""

import logging
import sys
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

# Module instances
app_logger = get_logger("fleet_intelligence")
data_logger = get_logger("data_pipeline")
model_logger = get_logger("risk_model")
