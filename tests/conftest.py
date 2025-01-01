import pytest
from pathlib import Path

from src.appconfig import AppConfig

@pytest.fixture
def config():
    # Get the user's home directory
    home_directory = Path.home()
    # Construct the project directory path
    project_dir = home_directory / "Documents" / "Projects" / "snifferbuddy"
    config = AppConfig.from_yaml(project_dir / 'config.yaml')
    # Don't use the project's db, use a test db
    config.database_path = project_dir / 'tests/test_db.duckdb'
    return config
