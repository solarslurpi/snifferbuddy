# Data Collection Guide

The SnifferBuddy project comes with software that listens for the SnifferBuddy readings coming in over mqtt and:
- calculates the vpd.
- stores the reading into a SQLite database. 

This way, any UI that can read/write SQLite tables (e.g.: DB Browser) can be used to view the data.

SnifferBuddy is one of the Buddies being built for a grow tent.  There are others - like MistBuddy that maintains the vpd level, and CO2Buddy - that maintains the CO2 level.  In order to have the buddies always running and centrally located, we run the software of the Buddies on what we call a [GrowBase](https://github.com/solarslurpi/GrowBase).


# How the Code Works

<p align="center">
  <img src="images/data_collection_flow.png" width="500" alt="Snifferbuddy wiring">
</p>

The workflow for handling SnifferBuddy readings involves the following steps:

1. **Starting the Workflow**  
    The process begins with the `start_capture.py` script, which initializes the capture and processing of readings.
    
2. **Listening for Readings**  
    The `mqtt_code.py` script uses MQTT to listen for SnifferBuddy readings. It receives the data and processes it.
    
3. **Processing the Readings**  
    The readings are transformed into a `SCD4XSensorReading` Pydantic model, which includes the calculation of `vpd` (vapor pressure deficit).
    - **VPD Calculation**: The `vpd` is derived using the temperature and relative humidity from the reading.
    - **Assumption**: Leaf temperature is assumed to be 2°C lower than the air temperature.
4. **Storing the Processed Data**  
    The processed reading is passed to `database_code.py`, which saves it into the `sniffer_data.sqlite` database file.
## Database Schema: The `readings` table

The schema consists of one table, the `readings` table.

Below is a detailed description of each column in the schema:

| **Column Name** | **Data Type** | **Description**                                                                  |
| --------------- | ------------- | -------------------------------------------------------------------------------- |
| `timestamp`     | `TIMESTAMP`   | The primary key. Indicates the time the reading was taken.                       |
| `device_name`   | `TEXT`        | The name or identifier of the SnifferBuddy device providing the reading.         |
| `light_on`      | `INTEGER`     | Indicates whether the light was on (`TRUE`) or off (`FALSE`) during the reading. |
| `CO2`           | `INTEGER`     | The CO2 concentration level measured in parts per million (ppm).                 |
| `temperature`   | `REAL`        | The air temperature at the time of the reading.                                  |
| `humidity`      | `REAL`        | The relative humidity percentage recorded.                                       |
| `vpd`           | `REAL`        | The calculated vapor pressure deficit (in kPa).                                  |
| `dew_point`     | `REAL`        | The dew point temperature.                                                       |
| `temp_unit`     | `TEXT`        | The unit of the temperature reading,  `"C"` (Celsius) or `"F"` (Fahrenheit).     |
# Installation

## Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) is the recommended way to install snifferbuddy. It creates an isolated environment for the application and its dependencies.

1. First, install pipx:

On Debian/Ubuntu/Raspberry Pi:
```bash
sudo apt update && sudo apt install pipx
```

On other systems:
```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

2. Install snifferbuddy:
```bash
pipx install git+https://github.com/solarslurpi/snifferbuddy
```

To update to the latest version:
```bash
pipx install --force git+https://github.com/solarslurpi/snifferbuddy
```

The `--force` flag ensures a clean reinstall, which is useful when updating or troubleshooting.

## What This Does

The installation command:
- Clones the snifferbuddy repository
- Creates an isolated virtual environment
- Installs all dependencies
- Makes the `snifferbuddy` command available system-wide

After installation, you can run snifferbuddy from any directory using:
```bash
snifferbuddy
```
## Running as a Background Service

On Linux-based systems like the [GrowBase](https://github.com/solarslurpi/GrowBase), snifferbuddy leverages `systemd` for service management.  By leveraging `systemd`, snifferbuddy can run as a background service, continuously monitoring `SCD4X` readings, automatically starting on boot, gracefully recovers from any failures, and operating silently without requiring an open terminal session.  System logging captures all runtime events and sensor data, allowing for easy troubleshooting and historical analysis through standard Linux logging tools like `journalctl`.

1. Copy the `systemd` service file.
```
sudo curl -o /etc/systemd/system/snifferbuddy.service https://raw.githubusercontent.com/solarslurpi/snifferbuddy/main/snifferbuddy.service
```

2. Enable and start the service
```
sudo systemctl daemon-reload
sudo systemctl enable snifferbuddy
sudo systemctl start snifferbuddy
```

3. Verify snifferbuddy is running
```
sudo systemctl status snifferbuddy
```

4. View the logfile

```
sudo journalctl -u snifferbuddy -f
```
The -f flag (follow) displays live log entries as they occur. Press Ctrl+C to exit the real-time monitoring view.

5. Stop the service
To stop the service:
```
sudo systemctl stop snifferbuddy
```

6. After updating snifferbuddy
```
sudo systemctl stop snifferbuddy
sudo systemctl daemon-reload
sudo systemctl start snifferbuddy
```


## Installation Location

pipx installs applications in isolated environments:
- Virtual environments: `~/.local/pipx/venvs/snifferbuddy/`
- Executable links: `~/.local/bin/`

