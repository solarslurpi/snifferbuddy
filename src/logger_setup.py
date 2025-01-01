import logging
import logging.config
import yaml

def logger_setup(name: str) -> logging.Logger:
    # Load logging configuration from YAML file
    with open('logging_config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Configure logging
    logging.config.dictConfig(config)

    # Create a logger
    logger = logging.getLogger(name)

    return logger