# Firmware Guide

SnifferBuddy uses [Tasmota](https://tasmota.github.io/docs/), a popular open-source firmware for ESP8266/ESP32 devices. Tasmota provides:

- A robust web interface for configuration.
- Built-in MQTT support.
- Over-the-air (OTA) updates.
- Support for a variety of Sensors.
- Support to add drivers for additional sensors.
- Automatic reconnection handling for both WiFi and MQTT.
## Install Tasmota

### Prerequisites
You will need:

- a Wemos D1 mini.
- a USB data cable.  Cheaper USB cables do not support data transfer. Make sure to have a cable that does support data transfer. The Wemos D1 mini requires the CH340/341 driver.  I started using Windows 11 which comes with default CH341 driver support. The problem is the installed driver will most like NOT work with the Wemos D1 mini.  If this is the case, refer to the Troubleshooting section.
### Install

- Go to the [tasmota install page](https://tasmota.github.io/install/).
- Choose `Upload factory.bin` and navigate to `tasmota_builds`.  Choose the `tasmota-sensors.bin` binary.
- Click on the Connect button and connect to the USB port that will communicate with the ESP8266.  Go to the Troubleshooting section if you can't connect.
- When asked, click the checkbox to erase the device.
- Go to the next dialog screen and click on `Install`.
- Once the install completes, click on next to set up the wifi.
- Click on `Visit Device`.
- Click on `Console`.
- To verify the SC4x driver is in the build type `i2cdriver`.  The number 0x62 should be in the list.
### Configure
While a Tasmota device can be configured through the UI, we'll be using the `Console`. First, we send a template plus attached commands.  Next, we set the timezone.
####  Install The Template
Tasmota has the concept of a [template](https://tasmota.github.io/docs/Templates/) that we will use to configure the ESP8266.
```
template {"NAME":"wemos_d1_scd40","GPIO":[1,1,1,1,640,608,1,1,1,1,1,1,1,4704],"FLAG":0,"BASE":18 }
```
The template configures the GPIO pins.  This includes the two I2C lines as well as the Analog pin.

To install the template, 
- go to the `Console` and copy/paste the above `template` line onto the command line. Then hit enter to execute. The console should display the values of the template.  
- restart the device by executing `module 0`.

Next, we will use the `template` action to set the mqtt host, mqtt topic, whether to display temperatures in Fahrenheit or Celsius (so8 1 = Fahrenheit, 0 = Celsius)

```
template {"CMND":"mqtthost beanie.local|topic snifferbuddy/tent_one/moon_beam|so8 1|teleperiod 20"}
```
- 
- `[SetOption8](https://tasmota.github.io/docs/Commands/#setoptions) 1` is to get readings into Fahrenheit.  By default, the readings are in Celsius.
- `teleperiod 20` sets the number of seconds between sending `mqtt` messages to 20 seconds.
#### Customize the Template
- Change the mqtthost to the hostname or host ip of the machine running the mqtt broker.
- Change the topic to a topic that is of the form `snifferbuddy/<location>/<name>`
- Change the `teleperiod` to the number of seconds you would like to have Tasmota send readings.
- Go to the Tasmota UI and click on `Console`.
- On the command line type `template` followed by a copy/paste of the following JSON:
```
template {"NAME":"wemos_d1_scd40","GPIO":[1,1,1,1,640,608,1,1,1,1,1,1,1,4704],"FLAG":0,"BASE":18, "CMND":"mqtthost <MQTT HOST>|topic <MQTT TOPIC>|so8 <0 for temperature readings in Celscius, 1 for Fahrenheit |teleperiod <num seconds between sending readings>"}
```

Replace the `<value>` with values that are unique to your environment.

_Note: Sometimes the teleperiod and/or so8 commands don't "stick".  To check, on the `command line` type teleperiod. It should show 20. And so8 should show "ON". If this is not the case, redo the `template command`._
#### Set the Timezone
To set the timezone, execute the command found in the [timezone table](https://tasmota.github.io/docs/Timezone-Table/) on the `console`'s command line to set the  timezone.  For example, to set the time to the US/Pacific timezone, the command is:
```
Backlog0 Timezone 99; TimeStd 0,1,11,1,2,-480; TimeDst 0,2,3,1,2,-420
```

To make sure Tasmota restarts, execute the following command from the `Console`: `module 0`.
The Tasmota firmware is now configured.


```
{'Time': '2024-12-28T15:43:17', 'ANALOG': {'A0': 999}, 'SCD40': {'CarbonDioxide': 502, 'eCO2': 510, 'Temperature': 75.3, 'Humidity': 58.1, 'DewPoint': 59.5}, 'TempUnit': 'F'}
```

## Adjusting Light ON/OFF threshold

A photoresistor detects whether the light is on or off. The `light_threshold` value in [`config.py`](src/config.py) defines the photoresistor reading that triggers the "light on" state. Analog readings range from 0 to 1023, with higher values indicating brighter light in the grow environment. The default threshold is 500; readings at or below this value indicate the light is off.  Change the threshold if the `light_on` state is not working as expected.
___________________________________________________________

# Appendix - Tasmota Sensor Build with SCD4x Support

The Tasmota Sensors build for the ESP8266 does not include support for the SCD4x.  To include support, Tasmota needs to be recompiled with the SCD4x configuration enabled.  To do this:
- Start a [Gitpod session](https://gitpod.io/#https://github.com/arendst/Tasmota/tree/development) and continue to open the VS Code cloud session.
- Open the `tasmota` folder.
- Open the `user_config_override.h` file.
- Scroll to the bottom of the file.
- Before the last `#endif`, add:
```
#ifndef USE_SCD40
#define USE_SCD40
#endif
```
- Save the file.
- Compile with `platformio run -e tasmota-sensors`
- Wait for the compilation to complete.
- When done, the firmware file is located in the folder `/tasmota/build_output/firmware`.
- Download the `tasmota-sensors.bin` file.  This will be loaded into the Wemos mini D1.
## Sources
- [Tasmota's page on Gitpod](https://tasmota.github.io/docs/Gitpod/)
- A [livestream video by digiblurDIY](https://www.youtube.com/watch?v=vod3Woj_vrs) of compiling Tasmota using Gitpod.