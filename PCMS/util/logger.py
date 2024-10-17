import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


FILE_SIZE = 1024 * 1024 * 100  # 100 MB
BACKUP_COUNT = 5  # keep up to 5 files

def configure_logger(logger_name: str, debug: bool = False):
    Path("./logs/").mkdir(parents=True, exist_ok=True)

    logging_level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    logging_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

    # File Handler
    file_handler = RotatingFileHandler(
        filename=f"./logs/{logger_name}.log",
        mode="a+",
        maxBytes=FILE_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(logging_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging_formatter)
    logger.addHandler(console_handler)
