"""
Logger utility - Single Responsibility Principle.
Centralized logging configuration.
"""

import logging
import os
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get configured logger instance.
    
    SOLID: Single Responsibility - only handles logging configuration
    
    Args:
        name: Logger name (typically __name__)
        level: Log level override
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Configure handler only once
        handler = logging.StreamHandler()
        
        # Set format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set level from environment or parameter
        log_level = level or os.getenv("LOG_LEVEL", "INFO")
        logger.setLevel(getattr(logging, log_level.upper()))
    
    return logger
