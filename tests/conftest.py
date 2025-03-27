import pytest
from pathlib import Path

from src.appconfig import AppConfig
from src.database_code import SensorDatabase

@pytest.fixture
def config():
    # Use the same path resolution as app.py to find config.yaml in src/
    src_dir = Path(__file__).parent.parent / "src"
    config = AppConfig.from_yaml(src_dir / 'config.yaml')
    # Don't use the project's db, use a test db
    config.database_path = Path(__file__).parent / 'test_db.sqlite3'
    return config

@pytest.fixture
def db(config):
    return SensorDatabase(config)
