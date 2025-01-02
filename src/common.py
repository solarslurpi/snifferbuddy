import logging
from src.logger_setup import logger_setup

def setup_logging(name: str) -> str:
    logger = logger_setup(name)
    logger.setLevel(logging.DEBUG)
    logger.info("Starting up...")
    return logger