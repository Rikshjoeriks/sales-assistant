"""Logging configuration utilities."""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from src.app.core.config import settings

JSON_LOG_FIELDS = {
    "event",
    "level",
    "logger",
    "timestamp",
    "service",
    "environment",
    "trace_id",
    "span_id",
    "request_id",
}


def _configure_stdlib_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )


def _configure_structlog() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def configure_logging(service_name: str) -> None:
    """Set up structured logging for the provided service name."""
    _configure_stdlib_logging()
    _configure_structlog()
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        service=service_name,
        environment=settings.environment,
    )


def bind_request_context(**kwargs: Any) -> None:
    """Attach request-scoped fields to the logging context."""
    filtered = {key: value for key, value in kwargs.items() if key in JSON_LOG_FIELDS}
    structlog.contextvars.bind_contextvars(**filtered)
