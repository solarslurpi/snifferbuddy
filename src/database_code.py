"""This code stores SnifferBuddy readings into a SQLite Database identified in config.yaml.
"""
from pathlib import Path
from datetime import datetime
from typing import Literal
import os

import sqlite3
from pydantic import BaseModel

from src.appconfig import AppConfig
from src.common import setup_logging


class SCD4XSensorReading(BaseModel):
    timestamp: datetime
    device_name: str
    tent_name: str
    light_on: bool
    CO2: int
    temperature: float
    humidity: float
    vpd: float
    dew_point: float
    temp_unit: Literal['C', 'F']

class SensorDatabase:
    def __init__(self, config: AppConfig):
        self.logger = setup_logging(__name__)
        """Initialize the database connection."""
        
        # Determine platform and choose appropriate path
        if os.name == 'nt':  # Windows
            db_path_str = config.database_paths.windows
        else:  # Linux/macOS
            db_path_str = config.database_paths.linux
            
        # Resolve the path
        self.db_path = Path(db_path_str).expanduser().resolve()
        
        # Create all parent directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_table_if_not_exists()
        self.logger.debug(f"Initializing Sensor Database. Database path is: {self.db_path}")

    def _create_table_if_not_exists(self):
        """Create the SCD4X_SensorReadings table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS readings (
                        timestamp TIMESTAMP PRIMARY KEY,
                        device_name TEXT,
                        tent_name TEXT,
                        light_on INTEGER,
                        CO2 INTEGER,
                        temperature REAL,
                        humidity REAL,
                        vpd REAL,
                        dew_point REAL,
                        temp_unit TEXT
                    )
                ''')
        except sqlite3.Error as e:
            self.logger.error(f"Error creating table: {e}")

    def store_reading(self, sensor_reading:SCD4XSensorReading):
        """Store a sensor reading in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO readings
                    (timestamp,device_name,tent_name,light_on,CO2,temperature,humidity,vpd,dew_point,temp_unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sensor_reading.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # Format to match SQLite
                        sensor_reading.device_name,
                        sensor_reading.tent_name,
                        sensor_reading.light_on,
                        sensor_reading.CO2,
                        sensor_reading.temperature,
                        sensor_reading.humidity,
                        sensor_reading.vpd,
                        sensor_reading.dew_point,
                        sensor_reading.temp_unit
                    )
                )
                # Log the absolute path to the database file
                self.logger.info(f"Successfully inserted reading into database at: {self.db_path.absolute()}")

        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
