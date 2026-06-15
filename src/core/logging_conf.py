import logging
from logging.config import dictConfig

from src.core.config import config  # noqa: F401

HANDLERS = ["default"]


def obfuscated(email: str, obfuscated_length: int) -> str:
    if "@" not in email:
        return email

    parts = email.split("@")
    if len(parts) != 2:
        return email

    first, last = parts
    visible_length = min(obfuscated_length, len(first))
    chars = first[:visible_length]
    masked = "*" * max(0, len(first) - visible_length)

    return chars + masked + "@" + last


class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8,
                    "default_value": "-",
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
            },
            "loggers": {
                "uvicorn": {"handlers": HANDLERS, "level": "INFO"},
                "src": {  # root.app.routers.post
                    "handlers": HANDLERS,
                    "level": "INFO",
                    "propagate": False,
                },
                "src.core": {
                    "handlers": HANDLERS,
                    "level": "WARNING",
                },
                "src.services": {
                    "handlers": HANDLERS,
                    "level": "WARNING",
                },
                "src.repository": {
                    "handlers": HANDLERS,
                    "level": "WARNING",
                },
                "sqlalchemy": {"handlers": ["default"], "level": "WARNING"},
                "aiosqlite": {"handlers": ["default"], "level": "WARNING"},
            },
        }
    )
