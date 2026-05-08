"""Logging configuration module."""
import logging
import sys
import json
import os
from typing import Optional
from datetime import datetime

try:
    import google.cloud.logging
    from google.cloud.logging.handlers import CloudLoggingHandler
    HAS_CLOUD_LOGGING = True
except ImportError:
    HAS_CLOUD_LOGGING = False


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Merge extra fields
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename", "funcName", "levelname", "levelno", "lineno", "module", "msecs", "message", "msg", "name", "pathname", "process", "processName", "relativeCreated", "stack_info", "thread", "threadName"]:
                log_data[key] = value

        return json.dumps(log_data)


def get_logger(
    name: str, level: str = "INFO", use_json: bool = False
) -> logging.Logger:
    """Get or create a logger instance."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if use_json or os.getenv("LOG_FORMAT", "").lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Cloud Logging handler (if on GCP)
    if HAS_CLOUD_LOGGING and os.getenv("ENABLE_CLOUD_LOGGING", "false").lower() == "true":
        try:
            client = google.cloud.logging.Client()
            handler = CloudLoggingHandler(client, name=name)
            handler.setLevel(log_level)
            logger.addHandler(handler)
            logger.info("Google Cloud Logging handler added")
        except Exception as e:
            logger.warning(f"Failed to initialize Cloud Logging: {str(e)}")

    return logger
