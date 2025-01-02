
from src.appconfig import AppConfig
from src.listener_code import SensorListener
from src.database_code import SensorDatabase
from src.common import setup_logging

logger = setup_logging(__name__)

db = None

def store_readings():
    app_config = AppConfig.from_yaml( 'src/config.yaml')
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