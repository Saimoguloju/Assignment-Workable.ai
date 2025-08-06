"""Logging configuration"""
from typing import Optional
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(
    name: str = "rd_sharma_extractor",
    level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """Setup logger configuration
    
    Args:
        name: Logger name
        level: Log level
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger