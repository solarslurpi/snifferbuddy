from pathlib import Path
from src.appconfig import AppConfig
from src.listener_code import SensorListener
from src.database_code import SensorDatabase
from src.common import setup_logging

logger = setup_logging(__name__)

# Load configuration
config_path = Path(__file__).parent / "config.yaml"
CONFIG = AppConfig.from_yaml(config_path)

db = None

def store_readings():
    global db
    db = SensorDatabase(CONFIG)
    listener = SensorListener(CONFIG, _store_reading)
    logger.info("Starting listing for sensor readings...")
    listener.start()


def _store_reading(reading):
    db.store_reading(reading)


def main():
    store_readings()

if __name__ == "__main__":
    main()