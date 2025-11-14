"""Structured logging configuration."""

import logging
import sys
from typing import Any

from app.core.config import get_settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


# Create a logger instance for use throughout the application
logger = logging.getLogger("oncall-agent")


def log_with_context(level: str, message: str, **context: Any) -> None:
    """Log a message with structured context.

    Args:
        level: Log level (info, warning, error, debug)
        message: Log message
        **context: Additional context as keyword arguments
    """
    log_func = getattr(logger, level.lower())
    if context:
        log_func(f"{message} | {context}")
    else:
        log_func(message)
