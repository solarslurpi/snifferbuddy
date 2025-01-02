import logging
import logging.config
import yaml
from importlib.resources import files

def logger_setup(name: str) -> logging.Logger:
    # Load logging configuration from YAML file
    config_path = files("src").joinpath('logging_config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Configure logging
    logging.config.dictConfig(config)

    # Create a logger
    logger = logging.getLogger(name)

    return logger