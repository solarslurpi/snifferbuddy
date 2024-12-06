# src/logging_config.py
import logging
from pathlib import Path


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
        handlers=[
            # File handler - writes everything to a file
            logging.FileHandler(
                filename=log_dir / "askgrowbuddy.log",
                mode='a',  # append mode
                encoding='utf-8'
            ),

            logging.StreamHandler()
        ]
    )

    # Set the logging levels for specific loggers
    logging.getLogger('src.database_code').setLevel(logging.INFO)
    logging.getLogger('src.mqtt_code').setLevel(logging.INFO)
    logging.getLogger('__main__').setLevel(logging.INFO)

    # You can add more specific logger configurations here if needed
    # For example:
    # logging.getLogger('ingest').setLevel(logging.DEBUG)
    # logging.getLogger('obsidian_rag').setLevel(logging.DEBUG)
    # logging.getLogger('retrieval').setLevel(logging.DEBUG)
