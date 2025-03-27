import pytest
from pathlib import Path
from src.appconfig import AppConfig
from pydantic import ValidationError

def test_config_is_pydantic_model(config):
    """Test that loaded config is a Pydantic model, not a dict."""
    assert isinstance(config, AppConfig), "Config should be an AppConfig instance, not a dictionary"
    
def test_config_database_path_accessible(config):
    """Test that database_path is accessible as a Pydantic model attribute."""
    assert hasattr(config, 'database_path'), "Config should have database_path attribute"
    assert isinstance(config.database_path, (str, Path)), "database_path should be string or Path"

def test_config_mqtt_settings_accessible(config):
    """Test that MQTT settings are accessible as nested Pydantic model attributes."""
    assert hasattr(config, 'mqtt'), "Config should have mqtt attribute"
    assert hasattr(config.mqtt, 'host'), "Config should have mqtt.host attribute"
    assert hasattr(config.mqtt, 'port'), "Config should have mqtt.port attribute"
    assert hasattr(config.mqtt, 'readings_topic'), "Config should have mqtt.readings_topic attribute"
    assert hasattr(config.mqtt, 'lwt_topic'), "Config should have mqtt.lwt_topic attribute"
    assert hasattr(config.mqtt, 'light_threshold'), "Config should have mqtt.light_threshold attribute"

def test_invalid_config_raises_error():
    """Test that invalid config data raises ValidationError."""
    invalid_config_data = {
        'database_path': 123,  # Should be string or Path
        'mqtt': {
            'host': 'localhost',
            'port': 'not_a_number',  # Should be int
            'readings_topic': None,  # Should be string
            'lwt_topic': None,  # Should be string
            'light_threshold': 'not_a_number'  # Should be int
        }
    }
    
    with pytest.raises(ValidationError):
        AppConfig(**invalid_config_data)
