"""
Logger configuration and utility functions for the AI Content Factory.
"""
import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (Optional[str]): Path to log file. If None, logs only to console.
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": sys.stdout
            }
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": True
            }
        }
    }
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": str(log_path),
            "mode": "a"
        }
        config["loggers"][""]["handlers"].append("file")
    
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Name of the logger, typically __name__
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)