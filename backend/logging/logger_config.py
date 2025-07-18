"""Structured JSON logging configuration."""
from __future__ import annotations

import json
import logging
import os
from logging.config import dictConfig
from typing import Mapping

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")

DEFAULT_FORMAT = {
    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
}


def setup_logger() -> None:
    """Configure the root logger with JSON output and rotation."""
    try:
        from pythonjsonlogger import jsonlogger  # type: ignore
    except ImportError:  # pragma: no cover
        # Fallback to simple logging if jsonlogger not available
        logging.basicConfig(level=LOG_LEVEL)
        return

    config: Mapping[str, object] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"json": DEFAULT_FORMAT},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "level": LOG_LEVEL,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": LOG_FILE,
                "maxBytes": 10 * 1024 * 1024,  # 10 MiB
                "backupCount": 5,
                "level": LOG_LEVEL,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
        },
    }
    dictConfig(config)  # type: ignore[arg-type]
