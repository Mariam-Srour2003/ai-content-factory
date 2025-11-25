"""
Main entry point for the AI Content Factory.
"""
from pathlib import Path
from .utils.logger import setup_logging, get_logger
from .utils.exceptions import ConfigurationError

# Initialize logger for the main module
logger = get_logger(__name__)

def main():
    """
    Main entry point for the application.
    """
    try:
        # Setup logging with a file in the logs directory
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_file = log_dir / "ai_content_factory.log"
        setup_logging(log_level="INFO", log_file=str(log_file))
        
        logger.info("Starting AI Content Factory")
        # Add your main application logic here
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise
    except Exception as e:
        logger.exception("Unexpected error occurred")
        raise

if __name__ == "__main__":
    main()
