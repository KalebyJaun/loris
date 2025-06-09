import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from datetime import datetime
import json
from typing import Any, Dict, Optional

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Define log format with more details
log_format = "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] [%(funcName)s] - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=date_format,
    handlers=[
        RotatingFileHandler(
            "logs/app.log",
            maxBytes=1000000,
            backupCount=5,
            encoding='utf-8'
        ),
        logging.StreamHandler(sys.stdout)
    ],
)

# Create logger instance
logger = logging.getLogger("loris_app")

# Add error file handler for critical errors
error_handler = RotatingFileHandler(
    "logs/error.log",
    maxBytes=1000000,
    backupCount=5,
    encoding='utf-8'
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(log_format, date_format))
logger.addHandler(error_handler)

class StructuredLogger:
    """Helper class for structured logging"""
    
    @staticmethod
    def _format_context(context: Optional[Dict[str, Any]] = None) -> str:
        """Format context dictionary into a string"""
        if not context:
            return ""
        return f" | Context: {json.dumps(context, ensure_ascii=False)}"

    @staticmethod
    def info(message: str, **context):
        """Log info message with context"""
        logger.info(f"{message}{StructuredLogger._format_context(context)}")

    @staticmethod
    def error(error: Exception, message: str = None, **context):
        """Log error with context and stack trace"""
        error_msg = f"{error.__class__.__name__}: {str(error)}"
        if message:
            error_msg = f"{message} - {error_msg}"
        logger.error(f"{error_msg}{StructuredLogger._format_context(context)}", exc_info=True)

    @staticmethod
    def warning(message: str, **context):
        """Log warning message with context"""
        logger.warning(f"{message}{StructuredLogger._format_context(context)}")

    @staticmethod
    def debug(message: str, **context):
        """Log debug message with context"""
        logger.debug(f"{message}{StructuredLogger._format_context(context)}")

    @staticmethod
    def critical(message: str, **context):
        """Log critical message with context"""
        logger.critical(f"{message}{StructuredLogger._format_context(context)}")

# Create a global instance
log = StructuredLogger()
