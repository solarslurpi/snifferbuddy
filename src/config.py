from pathlib import Path

# Create a directory in the user's home directory
home_dir = Path.home()
app_dir = home_dir / ".snifferbuddy"  # Hidden directory in user's home
data_dir = app_dir / "data"
db_path = home_dir / "snifferbuddy/sniffer_data.duckdb"

# Create directories if they don't exist
data_dir.mkdir(parents=True, exist_ok=True)

CONFIG = {
    'mqtt': {
        'host': "beanie.local",
        'port': 1883,
        'readings_topic': "tele/snifferbuddy/+/+/SENSOR",
        'lwt_topic': "tele/snifferbuddy/+/+/LWT",
        'light_threshold': 500
    },
    'database_path': str(db_path)
}