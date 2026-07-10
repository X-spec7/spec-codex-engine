import dataclasses
import logging
import sys

import structlog

from packages.shared.config.enums import Environment
from packages.shared.config.settings import get_settings


class BracketLevelFormatter:
    """Render the log level as an upper-case, tightly-bracketed token: ``[INFO]``.

    Unlike structlog's default (``[info     ]``), the padding sits *outside* the
    bracket so levels stay aligned while the bracket hugs the word.
    """

    def __init__(self, level_styles: dict[str, str], reset_style: str, width: int) -> None:
        self.level_styles = level_styles
        self.reset_style = reset_style
        self.width = width

    def __call__(self, key: str, value: object) -> str:
        level = str(value)
        style = self.level_styles.get(level, "")
        token = f"[{level.upper()}]".ljust(self.width)
        return f"{style}{token}{self.reset_style}"


def _build_console_renderer() -> structlog.dev.ConsoleRenderer:
    """A dev ConsoleRenderer whose level column uses ``[INFO]``-style tokens."""

    renderer = structlog.dev.ConsoleRenderer(colors=True)
    width = len("[CRITICAL]")  # widest bracketed level, so all levels align
    columns = [
        dataclasses.replace(
            col,
            formatter=BracketLevelFormatter(
                renderer._level_styles, structlog.dev.RESET_ALL, width
            ),
        )
        if col.key == "level"
        else col
        for col in renderer.columns
    ]

    # Show the level before the timestamp: [INFO]  2026-07-10 23:38:36  message
    by_key = {col.key: i for i, col in enumerate(columns)}
    if "level" in by_key and "timestamp" in by_key:
        li, ti = by_key["level"], by_key["timestamp"]
        columns[ti], columns[li] = columns[li], columns[ti]

    renderer.columns = columns
    return renderer


def configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.name, logging.INFO)

    is_production = settings.app_env == Environment.PRODUCTION

    # Machine-readable ISO for production; human-readable, second-precision for dev.
    timestamper = structlog.processors.TimeStamper(
        fmt="iso" if is_production else "%Y-%m-%d %H:%M:%S",
        utc=True,
    )

    shared_processors = [
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    renderer = (
        structlog.processors.JSONRenderer()
        if is_production
        else _build_console_renderer()
    )

    # structlog hands its events off to the stdlib formatter instead of printing
    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # one formatter renders BOTH structlog events and plain stdlib logs
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,  # applied to uvicorn/sqlalchemy logs
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()      # drop anything a prior basicConfig added
    root.addHandler(handler)
    root.setLevel(level)

    # Libraries like uvicorn attach their own handlers and set propagate=False,
    # so their logs never reach our root handler. Reset them to hand off to us.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        lib_logger = logging.getLogger(name)
        lib_logger.handlers.clear()   # remove the library's own handler
        lib_logger.propagate = True   # let records bubble up to root → our formatter
