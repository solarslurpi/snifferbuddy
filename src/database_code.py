"""This code stores SnifferBuddy readings into a SQLite Database identified in config.yaml.
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Literal

import duckdb
from pydantic import BaseModel, Field

from src.appconfig import AppConfig
from src.common import setup_logging


class SCD4XSensorReading(BaseModel):
    timestamp: datetime
    device_name: str
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
        self.db_path = Path(config.get('database_path')).resolve() 
        # Create all parent directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"***---> Database path is: {self.db_path} <----***")
        self._create_table_if_not_exists()
        self.logger.debug(f"Initializing Sensor Database. Database path is: {self.db_path}")

    def _create_table_if_not_exists(self):
        """Create the SCD4X_SensorReadings table if it doesn't exist."""
        try:
            with duckdb.connect(self.db_path) as conn:
                conn.execute('''
                            CREATE TABLE IF NOT EXISTS readings (
                                timestamp TIMESTAMP PRIMARY KEY,
                                device_name TEXT,
                                light_on BOOLEAN,
                                CO2 INTEGER,
                                temperature REAL,
                                humidity REAL,
                                vpd REAL,
                                dew_point REAL,
                                temp_unit TEXT
                            )

                ''')
        except duckdb.Error as e:
            self.logger.error(f"Error creating table: {e}")

    def store_reading(self, sensor_reading:SCD4XSensorReading):
        """Store a sensor reading in the database."""
        try:
            with duckdb.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO readings
                    (timestamp,device_name,light_on,CO2,temperature,humidity,vpd,dew_point,temp_unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sensor_reading.timestamp,
                        sensor_reading.device_name,
                        sensor_reading.light_on,
                        sensor_reading.CO2,
                        sensor_reading.temperature,
                        sensor_reading.humidity,
                        sensor_reading.vpd,
                        sensor_reading.dew_point,
                        sensor_reading.temp_unit
                    )
                )
                self.logger.info("Successfully inserted reading into database")

        except duckdb.Error as e:
            self.logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
