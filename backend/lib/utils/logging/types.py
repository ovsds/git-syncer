import logging

AbstractLogger = logging.Logger | logging.LoggerAdapter[logging.Logger]

__all__ = [
    "AbstractLogger",
]
