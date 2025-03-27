import pytest
from pathlib import Path
from src.appconfig import AppConfig, MQTTConfig, DatabasePaths
from pydantic import ValidationError
import os

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

def test_platform_specific_database_paths(config):
    """Test that database_paths are accessible and platform-specific path is used."""
    # First verify the database_paths attribute exists
    assert hasattr(config, 'database_paths'), "Config should have database_paths attribute"
    
    # Verify it has both platform options
    assert hasattr(config.database_paths, 'windows'), "Config should have database_paths.windows attribute"
    assert hasattr(config.database_paths, 'linux'), "Config should have database_paths.linux attribute"
    
    # Verify the database_path property returns the correct path based on platform
    original_platform = os.name
    try:
        # Test that database_path selects the right platform-specific path
        if os.name == 'nt':  # Windows
            assert config.database_path == config.database_paths.windows
        else:  # Linux/macOS
            assert config.database_path == config.database_paths.linux
        
        # Test opposite platform to ensure logic works
        if os.name == 'nt':
            os.name = 'posix'  # Switch to Linux
            assert config.database_path == config.database_paths.linux
        else:
            os.name = 'nt'  # Switch to Windows
            assert config.database_path == config.database_paths.windows
    finally:
        # Restore original platform
        os.name = original_platform

def test_platform_specific_path_selection_works():
    """Test that the correct platform-specific path is selected based on OS."""
    # Create a test config with specific test paths
    test_config = AppConfig(
        mqtt=MQTTConfig(
            host="test.local",
            port=1883,
            readings_topic="test/topic",
            lwt_topic="test/lwt",
            light_threshold=500
        ),
        database_paths=DatabasePaths(
            linux="/linux/path/test.sqlite",
            windows="C:/windows/path/test.sqlite"
        )
    )
    
    # Save original platform value
    original_platform = os.name
    
    try:
        # Force Windows platform
        os.name = 'nt'
        # Verify Windows path is selected
        assert test_config.database_path == "C:/windows/path/test.sqlite"
        
        # Force Linux platform
        os.name = 'posix'
        # Verify Linux path is selected
        assert test_config.database_path == "/linux/path/test.sqlite"
        
    finally:
        # Restore original platform
        os.name = original_platform
