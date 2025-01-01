import pytest
from datetime import datetime
import duckdb

from src.database_code import SCD4XSensorReading

# python -m pytest -s tests/test_database.py


@pytest.fixture
def reading():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return SCD4XSensorReading(
        timestamp=current_time,
        device_name="test_device",
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
    
    # Get the last reading from DuckDB
    with duckdb.connect(config.database_path) as conn:
        result = conn.execute("""
            SELECT * FROM readings 
            ORDER BY timestamp DESC 
            LIMIT 1
        """).fetchone()
        # Get column names
        columns = conn.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='readings'
        """).fetchall()
        column_names = [col[0] for col in columns]
        result_dict = dict(zip(column_names, result))

    # Verify each field matches the input
    assert result_dict.get('timestamp') == reading.timestamp
    assert result_dict.get('device_name') == reading.device_name
    assert result_dict.get('light_on') == reading.light_on
    assert result_dict.get('CO2') == reading.CO2
    assert round(result_dict.get('temperature'),1) == reading.temperature
    assert round(result_dict.get('humidity'),1) == reading.humidity
    assert round(result_dict.get('vpd'),1) == reading.vpd
    assert round(result_dict.get('dew_point'),1) == reading.dew_point
    assert result_dict.get('temp_unit') == reading.temp_unit

    # Print the received data for inspection
    print("\nReceived and stored sensor data:")
    for key, value in result_dict.items():
        if isinstance(value, float):
            print(f"  {key}: {round(value, 1)}")
        else:
            print(f"  {key}: {value}")
