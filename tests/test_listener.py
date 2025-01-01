from threading import Event
import pytest

from src.listener_code import SensorListener
from src.database_code import SCD4XSensorReading


def test_receive(config):
    """Test that the MQTT listener receives valid SCD4XSensorReadings.
    
    Uses the Event pattern to coordinate between:
    - Main test thread that starts the listener and waits for verification
    - MQTT callback thread that receives and verifies readings
    
    Flow:
    1. Create Event to coordinate threads
    2. Start listener with callback that:
       - Verifies reading is correct type
       - Signals the Event
       - Stops the listener
    3. Main thread waits for Event to be signaled
    4. Test passes when valid reading is received and verified
    
    Args:
        config: Fixture providing test configuration
        callback: Function to verify and handle received readings
    """
    reading_verified = Event()
    
    def callback(reading):
        print(f"Received reading: {reading}")
        assert isinstance(reading, SCD4XSensorReading), "Received reading is not a SCD4XSensorReading"
        reading_verified.set()
        listener.stop()
        
    listener = SensorListener(config, callback)
    listener.start()
    
    assert reading_verified.wait(timeout=30), "No reading received within timeout"
    

