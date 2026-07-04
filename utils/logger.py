import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import LOG_LEVEL


LOG_FOLDER = Path("logs")
LOG_FOLDER.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_FOLDER / "chatbot.log"

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(module)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _get_log_level() -> int:
    return getattr(
        logging,
        str(LOG_LEVEL or "INFO").upper(),
        logging.INFO,
    )


def _build_formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )


def _build_file_handler() -> RotatingFileHandler:
    handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(_build_formatter())
    handler.setLevel(_get_log_level())

    return handler


def _build_console_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setFormatter(_build_formatter())
    handler.setLevel(_get_log_level())

    return handler


def get_logger(name: str = "ChatBot") -> logging.Logger:
    app_logger = logging.getLogger(name)
    app_logger.setLevel(_get_log_level())
    app_logger.propagate = False

    if not app_logger.handlers:
        app_logger.addHandler(_build_file_handler())
        app_logger.addHandler(_build_console_handler())

    return app_logger


logger = get_logger("ChatBot")


# Reduce noisy third-party logs
_NOISY_LOGGERS = [
    "httpx",
    "httpcore",
    "urllib3",
    "sentence_transformers",
    "huggingface_hub",
    "transformers",
    "faiss",
    "uvicorn.access",
    "watchfiles",
    "pymongo",
    "multipart",
]

for logger_name in _NOISY_LOGGERS:
    logging.getLogger(logger_name).setLevel(logging.WARNING)


def log_startup_banner() -> None:
    logger.info("Logger initialized. pid=%s log_file=%s", os.getpid(), LOG_FILE)