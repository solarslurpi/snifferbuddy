# SnifferBuddy Puck Firmware
The firmware is [Tasmota](https://tasmota.github.io/docs/), a popular open-source firmware for ESP8266/ESP32 devices. Tasmota provides:
- A robust web interface for configuration.
- Built-in MQTT support.
- Over-the-air (OTA) updates.
- Support for a variety of Sensors.
- Support to add drivers for additional sensors.
- Automatic reconnection handling for both WiFi and MQTT.
## Installation
Installation assumes you have a [SnifferBuddy Puck](snifferbuddy_puck.md).
- Before you begin, make sure:
    - you have a USB data cable.  Cheaper USB cables do not support data transfer.
    - your OS has a CH340/CH341 driver installed.  I run on Windows 10 and use the CH340 driver. [This documentation gives install info for Windows, Mac, and Linux](https://sparks.gogo.co.nz/ch340.html).

## Customizing the Tasmota build
Not all sensor drivers can be installed on the ESP2866 at the same time.  The SCD4X sensor driver is one of the drivers that is not installed by default.  A custom build is needed to add the SCD4X driver.
### Compiling in the SCD4X Driver

[Compile your build](https://tasmota.github.io/docs/Compile-your-build/) provides the documentation on how to compile a custom build.  Choose the `Gitpod` method.  It is a very simple and fast way to get started.  Follow the guide up and through compiling the firmware.


When done, the firmware files are in the folder `/Tasmota/build_output/firmware/`.

Download the `.bin` file.

Navigate to [the Tasmota Install URL](https://tasmota.github.io/install/). Look towards the bottom of the page to upload the `.bin` file.  The button say `Upload factory.bin`.  This is where you upload the `.bin` file you just downloaded. 

Install the firmware. Once the install is successful, the UI will navigate through entering wifi credentials.  The final UI has a button to `Visit Device`. Click this button to open the device's interface. 

Go the the `Console` and type `i2cdriver`.  The `SCD4X` driver's i2c address is `62`.


## Accessing the UI
- Connect to your network and locate your SnifferBuddy's IP address. I use the AngryIP Scanner tool for this.
- Once you find the IP address, enter it in a web browser

The main page displays current sensor readings and device status.
<figure style="text-align: center; margin: auto;">
    <img src="images/Tasmota_main_screen.jpg" width="200" alt="Image of Tasmota's main screen showing SCD40 readings.">
    <figcaption style="text-align: center">Tasmota main screen showing SCD40 readings</figcaption>
</figure>

## Configuration Settings

The configuration for the Sensor Monitoring System is managed through a combination of a Python module (`config.py`) and a YAML file (`config.yaml`). This setup allows for flexible and easy-to-manage configuration settings that can be adjusted without modifying the application code.

### Configuration Files

1. **`config.py`**: This Python module defines the structure and default values for the application's configuration using Pydantic, a data validation and settings management library. It provides a programmatic way to load and validate configuration data, ensuring that all required fields are present and correctly typed.


2. **`config.yaml`**: This YAML file contains the actual configuration settings for the application. It is designed to be user-editable, allowing you to customize the application's behavior by changing the values in this file. If the file is not present, the application will fall back to default settings defined in `config.py`.

### Configuration Properties

The configuration is divided into two main sections:

#### MQTT Configuration

- **`host`**: The hostname or IP address of the MQTT broker. This is where the application will connect to receive sensor data. Default is `"localhost"`.
- **`port`**: The port number on which the MQTT broker is listening. The default port for MQTT is `1883`.
- **`topic_prefix`**: The prefix for MQTT topics that the application will subscribe to. This allows the application to filter messages based on topic hierarchy. Default is `"sensors/#"`, which subscribes to all topics under `sensors`.
#### Database Configuration
- **`database_path`**: The file path to the SQLite database where sensor readings will be stored. This path can be absolute or relative, and it defaults to a hidden directory in the user's home folder: `"~/.sensor_monitor/readings.db"`.
### How to Use
1. **Edit `config.yaml`**: Open the `config.yaml` file in a text editor and modify the values as needed to match your environment and requirements.

## Docker

```
docker build -t solarslurpie/snifferbuddy:latest .
```

```bash
docker run -v $(pwd)/config.yaml:/usr/app/config.yaml --name snifferbuddy -d  --restart always solarslurpie/snifferbuddy:latest
```
