import logging
import sys

import structlog

from packages.shared.config.settings import get_settings

def configure_logging_dev() -> None:
    """
    Configure global logging using structlog.

    This function should be called once at application startup.

    It:
    - Configures Python standard logging.
    - Configures structlog processors.
    - Sets log level from Settings.
    """
    settings = get_settings()

    # Map our LogLevel enum to standard logging levels
    level = getattr(logging, settings.log_level.name, logging.INFO)

    # Basic Python logging configuration
    logging.basicConfig(
        level=level,
        format="%(message)s",
        stream=sys.stdout,
    )

    # structlog processors
    processors = [
        structlog.processors.add_log_level,             # adds level field
        structlog.processors.TimeStamper(fmt="iso"),   # adds timestamp
        structlog.processors.StackInfoRenderer(),      # stack info if available
        structlog.processors.format_exc_info,          # formats exceptions
        structlog.processors.UnicodeDecoder(),        # ensures string decoding
    ]

    # Decide JSON or pretty output based on environment
    if settings.app_env == "production":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=processors + [renderer],
        context_class=dict,        # can be changed to ContextVar if needed
        wrapper_class=structlog.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )