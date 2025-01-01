import yaml
from pydantic import BaseModel

class MQTTConfig(BaseModel):
    """MQTT connection settings."""
    host: str
    port: int
    readings_topic: str
    lwt_topic: str
    light_threshold: int

class AppConfig(BaseModel):
    """Application configuration."""
    mqtt: MQTTConfig
    database_path: str



    @classmethod
    def from_yaml(cls, file_path: str):
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file)

        return cls(**config_data)

# Usage
# config = AppConfig.from_yaml('config.yaml')
