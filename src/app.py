import logging
from pathlib import Path
from src.appconfig import AppConfig
from src.listener_code import SensorListener
from src.database_code import SensorDatabase
from src.logger_setup import logger_setup

logger = logger_setup(__name__)
logger.setLevel(logging.DEBUG)

# Get the user's home directory
home_directory = Path.home()
# Construct the project directory path
project_dir = home_directory / "Documents" / "Projects" / "snifferbuddy"

db = None

def store_readings():
    app_config = AppConfig.from_yaml(project_dir / 'config.yaml')
    global db
    db = SensorDatabase(app_config)
    listener = SensorListener(app_config, _store_reading)
    logger.info("Starting listing for sensor readings...")
    listener.start()


def _store_reading(reading):
    db.store_reading(reading)


def main():

    store_readings()

if __name__ == "__main__":
    main()