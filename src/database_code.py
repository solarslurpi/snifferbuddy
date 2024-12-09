"""This code stores SnifferBuddy readings into a SQLite Database identified in .env.
"""
from dotenv import load_dotenv
import os
from pathlib import Path
import sqlite3
import logging
import math

from config import AppConfig
from anyio.streams.memory import MemoryObjectReceiveStream

from src.logging_config import setup_logging
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

class SensorDatabase:
    def __init__(self, config: AppConfig, receive_stream: MemoryObjectReceiveStream):
        """Initialize the database connection and receive stream."""
        self.db_path = config.database_path
        # Extract the directory path without the filename
        db_directory = os.path.dirname(self.db_path)
        # Create all necessary parent directories
        Path(db_directory).mkdir(parents=True, exist_ok=True)
        self.receive_stream = receive_stream
        self.light_threshold = config.mqtt.light_threshold
        self._create_table_if_not_exists()
        logger.debug(f"Initializing Sensor Database. Database path is: {self.db_path}")

    def _create_table_if_not_exists(self):
        """Create the SCD4X_SensorReadings table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS SCD4X_SensorReadings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        light_on BOOLEAN,
                        carbon_dioxide INTEGER,
                        eco2 INTEGER,
                        temperature REAL,
                        humidity REAL,
                        dew_point REAL,
                        temp_unit TEXT,
                        vpd REAL
                    )
                ''')
        except sqlite3.Error as e:
            logger.error(f"Error creating table: {e}")

    def _calculate_vpd(self, temperature: float, humidity: float) -> float:
        """Calculate Vapor Pressure Deficit (VPD) in kPa."""
        def saturation_vapor_pressure(temp_celsius: float) -> float:
            return 0.6108 * math.exp((17.27 * temp_celsius) / (temp_celsius + 237.3))
        
        air_temp = temperature
        leaf_temp = air_temp - 2  # Assume leaf temp is 2°C cooler than air
        svp_air = saturation_vapor_pressure(air_temp)
        svp_leaf = saturation_vapor_pressure(leaf_temp)
        actual_vapor_pressure = humidity * svp_air / 100
        return svp_leaf - actual_vapor_pressure

    async def run(self):
        """Continuously read from the receive stream and store readings."""
        logger.info("Starting database processing loop")
        async with self.receive_stream:
            async for data in self.receive_stream:
                logger.debug(f"Database received data through stream: {data}")
                await self.store_reading(data)

    async def store_reading(self, data):
        """Store a sensor reading in the database."""
        try:
            # Log the incoming data
            logger.debug(f"Received data: {data}")

            # Skip LWT messages (which are strings)
            if isinstance(data, str):
                logger.debug(f"Skipping LWT message: {data}")
                return

            # Extract values from the data
            time_str = data.get('Time')
            analog_data = data.get('ANALOG', {})
            scd40_data = data.get('SCD40', {})

            # Log the extracted data for debugging
            logger.debug(f"Extracted time: {time_str}, ANALOG: {analog_data}, SCD40: {scd40_data}")

            # Skip if we don't have SCD40 sensor data
            if not scd40_data:
                logger.debug("Skipping reading without SCD40 data")
                return

            # Convert analog reading to light state
            light_value = analog_data.get('A0', 0)
            light_on = 1 if light_value > self.light_threshold else 0
            logger.debug(f"Light reading: A0={light_value}, converted to light_on={light_on}")

            # Calculate VPD before storing
            temperature = scd40_data.get('Temperature')
            humidity = scd40_data.get('Humidity')
            vpd = self._calculate_vpd(temperature, humidity) if temperature is not None and humidity is not None else None
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO SCD4X_SensorReadings
                    (timestamp, light_on, carbon_dioxide, eco2, temperature,
                    humidity, dew_point, temp_unit, vpd)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        time_str,
                        light_on,
                        scd40_data.get('CarbonDioxide'),
                        scd40_data.get('eCO2'),
                        temperature,
                        humidity,
                        scd40_data.get('DewPoint'),
                        data.get('TempUnit'),
                        vpd
                    )
                )
                logger.info("Successfully inserted reading into database")

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
