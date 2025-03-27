import yaml
from pydantic import BaseModel
import os

class MQTTConfig(BaseModel):
    """MQTT connection settings."""
    host: str
    port: int
    readings_topic: str
    lwt_topic: str
    light_threshold: int

class DatabasePaths(BaseModel):
    """Platform-specific database paths."""
    linux: str
    windows: str

class AppConfig(BaseModel):
    """Application configuration."""
    mqtt: MQTTConfig
    database_paths: DatabasePaths
    
    @property
    def database_path(self) -> str:
        """Get the appropriate database path for the current platform."""
        if os.name == 'nt':  # Windows
            return self.database_paths.windows
        else:  # Linux/macOS
            return self.database_paths.linux

    @classmethod
    def from_yaml(cls, file_path: str):
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file)

        return cls(**config_data)

# Usage
# config = AppConfig.from_yaml('config.yaml')
