import pytest
from pathlib import Path

from src.appconfig import AppConfig
from src.database_code import SensorDatabase

@pytest.fixture
def config():
    # Use the same path resolution as app.py to find config.yaml in src/
    src_dir = Path(__file__).parent.parent / "src"
    config = AppConfig.from_yaml(src_dir / 'config.yaml')
    
    # Instead of setting database_path directly, modify the underlying database_paths
    test_db_path = str(Path(__file__).parent / 'test_db.sqlite3')
    
    # Set both platform paths to the test path
    config.database_paths.windows = test_db_path
    config.database_paths.linux = test_db_path
    
    return config

@pytest.fixture
def db(config):
    return SensorDatabase(config)
