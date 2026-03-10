import logging

from backend.settings import settings


def configure_logger() -> logging.Logger:
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("ailab")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


logger = configure_logger()
