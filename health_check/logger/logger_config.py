"""
Logger configuration for health check system.
"""

import logging
import os
from typing import Optional, Dict, Any


def get_logger(name: str, config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Get configured logger instance.
    
    Args:
        name: Logger name
        config: Logging configuration dictionary
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        # Logger already configured
        return logger
    
    # Default configuration
    default_config = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'health_check.log',
        'console': True
    }
    
    if config:
        default_config.update(config)
    
    # Set log level
    level = getattr(logging, default_config['level'].upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(default_config['format'])
    
    # Console handler
    if default_config['console']:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if default_config['file']:
        # Ensure log directory exists
        log_dir = os.path.dirname(default_config['file'])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(default_config['file'])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def configure_logging(config: Dict[str, Any]) -> None:
    """
    Configure root logger for the application.
    
    Args:
        config: Logging configuration
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set to lowest level
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Apply configuration
    logger = get_logger('health_check', config)
    
    # Configure all existing loggers to use the same handlers
    for handler in logger.handlers:
        root_logger.addHandler(handler)