import logging
import signal
import argparse
from pathlib import Path
from src.appconfig import AppConfig
from src.listener_code import SensorListener
from src.logger_setup import logger_setup

logger = logger_setup(__name__)
logger.setLevel(logging.DEBUG)

# Get the user's home directory
home_directory = Path.home()
# Construct the project directory path
project_dir = home_directory / "Documents" / "Projects" / "snifferbuddy"


mqtt_client = None

def store_readings():
    app_config = AppConfig.from_yaml(project_dir / 'config.yaml')
    sensor_readings_client = SensorListener(app_config, _store_reading)
    logger.info("Starting listing for sensor readings...")
    mqtt_client.start()

def stop_storing_readings():
    if mqtt_client:
        mqtt_client.stop()
        mqtt_client = None
        logger.info("Stopping MQTT client...")
    else:
        logger.warn("MQTT client is not running.")

def _store_reading(reading):
    database.store_reading(reading)


def main():
    parser = argparse.ArgumentParser(description="Control the MQTT client.")
    parser.add_argument('--start', action='store_true', help='Start the MQTT client')
    parser.add_argument('--stop', action='store_true', help='Stop the MQTT client')
    args = parser.parse_args()

    if args.start:
        store_readings()
    elif args.stop:
        stop_storing_readings()
    else:
        logger.error("Please specify either --start or --stop.")

if __name__ == "__main__":
    main()