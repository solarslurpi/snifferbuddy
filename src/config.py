from pathlib import Path

# Store database in a data directory within the package
package_dir = Path(__file__).parent
data_dir = package_dir / "data"
db_path = data_dir / "sniffer_data.duckdb"
db_path.parent.mkdir(parents=True, exist_ok=True)

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