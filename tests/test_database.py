import pytest
from datetime import datetime
import sqlite3

from src.database_code import SCD4XSensorReading

# python -m pytest -s tests/test_database.py


@pytest.fixture
def reading():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return SCD4XSensorReading(
        timestamp=current_time,
        device_name="test_device",
        tent_name="test_tent",
        light_on=1,
        CO2=547,
        temperature=74.3,
        humidity=57.2,
        vpd=1.2,    
        dew_point=10.6,
        temp_unit="F"
    )

def test_insert(config, reading, db):
    db.store_reading(reading)
    
    # Get the last reading from SQLite
    with sqlite3.connect(config.database_path) as conn:
        result = conn.execute("""
            SELECT * FROM readings 
            ORDER BY timestamp DESC 
            LIMIT 1
        """).fetchone()
        
        columns = conn.execute("PRAGMA table_info(readings)").fetchall()
        column_names = [col[1] for col in columns]
        result_dict = dict(zip(column_names, result))

    # Convert SQLite integer back to boolean for light_on
    result_dict['light_on'] = bool(result_dict['light_on'])

    # Compare with the correct format (space instead of 'T')
    assert result_dict['timestamp'] == reading.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    assert result_dict['device_name'] == reading.device_name
    assert result_dict['light_on'] == reading.light_on
    assert result_dict['CO2'] == reading.CO2
    assert round(result_dict['temperature'], 1) == reading.temperature
    assert round(result_dict['humidity'], 1) == reading.humidity
    assert round(result_dict['vpd'], 1) == reading.vpd
    assert round(result_dict['dew_point'], 1) == reading.dew_point
    assert result_dict['temp_unit'] == reading.temp_unit

    # Print the received data for inspection
    print("\nReceived and stored sensor data:")
    for key, value in result_dict.items():
        if isinstance(value, float):
            print(f"  {key}: {round(value, 1)}")
        else:
            print(f"  {key}: {value}")

def test_fields_exist_in_db(db):
    """Test that all required fields exist in the readings table."""
    with sqlite3.connect(db.db_path) as conn:
        columns = conn.execute("PRAGMA table_info(readings)").fetchall()
        column_names = [col[1] for col in columns]
        
    # Check that all required fields exist
    required_fields = [
        'timestamp', 
        'device_name',
        'tent_name',  # Our new field
        'light_on', 
        'CO2', 
        'temperature', 
        'humidity', 
        'vpd', 
        'dew_point', 
        'temp_unit'
    ]
    
    for field in required_fields:
        assert field in column_names, f"Field '{field}' not found in database schema"
