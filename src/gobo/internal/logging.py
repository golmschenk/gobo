from __future__ import annotations

import datetime
import logging
import sys

logger_initialized = False


def create_default_formatter() -> logging.Formatter:
    formatter = logging.Formatter('gobo [{asctime} {levelname} {name}] {message}', style='{')
    return formatter


def set_up_default_logger():
    global logger_initialized  # noqa PLW0603 : TODO: Probably a bad hack. Consider further.
    if not logger_initialized:
        formatter = create_default_formatter()
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger = logging.getLogger('gobo')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        logger_initialized = True
