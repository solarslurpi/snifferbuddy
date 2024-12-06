import pytest
import sqlite3
from threading import Event
from dotenv import load_dotenv
import os

from src.database_code import SensorDatabase
from src.mqtt_code import MQTTListener

load_dotenv()

@pytest.fixture
def test_db():
    """Fixture to create a test database."""
    db_path = os.getenv("TEST_DB_PATH")
    db = SensorDatabase(db_path=db_path)
    return db
    # yield db
    # # Cleanup: remove test database after tests
    # os.remove(db_path)

def test_dummy_insert(test_db):
    """Test that we can insert a dummy reading and retrieve it correctly."""
    # Arrange
    test_reading = {
        "Time": "2024-11-30T13:25:13",
        "ANALOG": {"A0": 855},
        "SCD40": {
            "CarbonDioxide": 547,
            "eCO2": 568,
            "Temperature": 27.9,
            "Humidity": 34.2,
            "DewPoint": 10.6
        },
        "TempUnit": "C"
    }

    # Act
    test_db.store_reading(test_reading)

    # Assert
    with sqlite3.connect(test_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SCD4X_SensorReadings ORDER BY id DESC LIMIT 1")
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        result = dict(zip(columns, row))

    # Verify each field matches the input
    assert result['timestamp'] == test_reading['Time']
    assert result['analog_a0'] == test_reading['ANALOG']['A0']
    assert result['carbon_dioxide'] == test_reading['SCD40']['CarbonDioxide']
    assert result['eco2'] == test_reading['SCD40']['eCO2']
    assert result['temperature'] == test_reading['SCD40']['Temperature']
    assert result['humidity'] == test_reading['SCD40']['Humidity']
    assert result['dew_point'] == test_reading['SCD40']['DewPoint']
    assert result['temp_unit'] == test_reading['TempUnit']

def test_real_insert(test_db):
    """Test that we can receive and store real MQTT data."""
    # Create an event to signal when we get a sensor reading
    sensor_received = Event()

    # Subclass MQTTListener to detect sensor messages and store them
    class TestListener(MQTTListener):
        def _on_message(self, client, userdata, msg):
            data = super()._on_message(client, userdata, msg)
            if msg.topic.endswith('/SENSOR'):
                test_db.store_reading(data)
                sensor_received.set()

    # Create and connect the listener
    listener = TestListener()
    listener.connect()

    # Wait for a sensor message (timeout after 30 seconds)
    print("\nWaiting for a sensor reading...")
    received = sensor_received.wait(timeout=30)

    # Clean up
    listener.client.loop_stop()
    listener.client.disconnect()

    # Verify we got a reading
    assert received, "No sensor reading received within timeout period"

    # Verify the data was stored in the database
    with sqlite3.connect(test_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SCD4X_SensorReadings ORDER BY id DESC LIMIT 1")
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        result = dict(zip(columns, row))

    # Verify essential fields are present and not NULL
    assert result['timestamp'] is not None, "Timestamp should not be NULL"
    assert result['analog_a0'] is not None, "Analog reading should not be NULL"
    assert result['carbon_dioxide'] is not None, "CO2 reading should not be NULL"
    assert result['temperature'] is not None, "Temperature should not be NULL"
    assert result['humidity'] is not None, "Humidity should not be NULL"

    # Print the received data for inspection
    print("\nReceived and stored sensor data:")
    for key, value in result.items():
        print(f"  {key}: {value}")