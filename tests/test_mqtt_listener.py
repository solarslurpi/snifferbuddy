from threading import Event
import sqlite3
from dotenv import load_dotenv
import os

import pytest

from src.mqtt_code import MQTTListener
from src.database_code import SensorDatabase

load_dotenv()

@pytest.fixture
def test_db():
    """Fixture to create a test database."""
    db_path = os.getenv("TEST_DB_PATH")
    db = SensorDatabase(db_path)
    return db
    # yield db
    # # Cleanup: remove test database after tests
    # os.remove(db_path)

def test_receive_and_store_sensor_reading(test_db):
    """Test that the MQTT listener can receive messages from SnifferBuddy and store them in the database."""
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
        cursor.execute("SELECT COUNT(*) FROM SCD4X_SensorReadings")
        count = cursor.fetchone()[0]
        assert count > 0, "No readings were stored in the database"
