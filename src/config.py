from pathlib import Path

# Create a directory in the user's home directory
directory = Path.home() / "snifferbuddy"
db_path = directory / "sniffer_data.duckdb"

# Create directories if they don't exist
directory.mkdir(parents=True, exist_ok=True)

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