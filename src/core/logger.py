"""Logging configuration module."""
import logging
import sys
import json
from typing import Optional
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON formatted log entry
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)


def get_logger(
    name: str, level: str = "INFO", use_json: bool = False
) -> logging.Logger:
    """Get or create a logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def log_request(logger: logging.Logger, method: str, endpoint: str, **kwargs):
    """Log incoming request.

    Args:
        logger: Logger instance
        method: HTTP method
        endpoint: API endpoint
        **kwargs: Additional context
    """
    logger.info(f"Request: {method} {endpoint}", extra=kwargs)


def log_response(logger: logging.Logger, status_code: int, duration_ms: float, **kwargs):
    """Log outgoing response.

    Args:
        logger: Logger instance
        status_code: HTTP status code
        duration_ms: Response time in milliseconds
        **kwargs: Additional context
    """
    logger.info(
        f"Response: {status_code} ({duration_ms:.2f}ms)",
        extra=kwargs,
    )


def log_error(logger: logging.Logger, error: Exception, context: Optional[dict] = None):
    """Log error with context.

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
    """
    extra = context or {}
    logger.error(f"Error: {str(error)}", exc_info=True, extra=extra)
