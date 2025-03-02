import logging
import os
from typing import Dict, Any

def setup_logging(config: Dict[str, Any] = None) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        config (Dict[str, Any], optional): Configuration dictionary. Defaults to None.
        
    Returns:
        logging.Logger: Configured logger
    """
    # Get log level from config or default to INFO
    log_level_str = os.environ.get('LOGGING_LEVEL', 'INFO')
    if config and 'logging' in config and 'level' in config['logging']:
        log_level_str = config['logging']['level']
    
    # Map string log level to logging constants
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and return logger for this module
    logger = logging.getLogger('audience_deployment')
    logger.setLevel(log_level)
    
    # When running in Google Cloud Functions, the platform will automatically
    # capture logs from the Python logging module at the INFO level and above
    
    return logger
