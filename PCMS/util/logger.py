import logging
from logging.handlers import RotatingFileHandler
import os

from PCMS.util.file_util import FileUtil
from PCMS.util.folder_names import FolderNames


FILE_SIZE = 1024 * 1024 * 100  # 100 MB
BACKUP_COUNT = 5  # keep up to 5 files

def configure_logger(logger_name: str, file_util: FileUtil, debug: bool = False):
    file_util.create_folder(FolderNames.LOGS)

    logging_level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    logging_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

    # File Handler
    log_folder_path = file_util.get_path(FolderNames.LOGS)
    log_file_path = os.path.join(log_folder_path, f"{logger_name}.log" )
    file_handler = RotatingFileHandler(
        filename=log_file_path,
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
