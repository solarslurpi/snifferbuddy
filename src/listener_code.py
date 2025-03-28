import json
import math
from datetime import datetime
import paho.mqtt.client as mqtt
from typing import Optional

from src.database_code import SCD4XSensorReading
from src.common import setup_logging



class SensorListener:
    def __init__(self, config, callback=None):
        self.config = config
        self.logger = setup_logging(__name__)
        # Use a callback to send the reading to the caller
        self.callback = callback 

    def on_connect(self, client, userdata, flags, rc, properties=None):  
        self.logger.info("Connected with result code {0}".format(str(rc)))  
        self.client.subscribe(self.config.mqtt.readings_topic )

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages.""" 
        self.logger.info(f"Message received on {msg.topic}")
        
        try:
            # Process the message
            reading = self._process_message(msg)
            
            # Only call the callback if we have a valid reading
            if reading is not None and self.callback:
                self.callback(reading)
            elif reading is None:
                self.logger.info("Skipping invalid message (no SCD40 data)")
            
        except Exception as e:
            self.logger.error(f"Error in on_message: {e}", exc_info=True)

    def start(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        host = self.config.mqtt.host
        port = self.config.mqtt.port
        self.client.connect(host, port, 60)
        self.logger.info(f"Connecting to {host} on port {port}")
        self.client.loop_forever()
    
    def stop(self):
        """Disconnect from the MQTT broker and stop the network loop."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.logger.info("Disconnected from MQTT broker")
        self.running = False

    def _process_message(self, msg:str) -> Optional[SCD4XSensorReading]:
        """Process an MQTT message into a SCD4XSensorReading."""
        self.logger.info(f"DEBUG: Processing message with topic: {msg.topic}")
        
        try:
            # Decode the payload first
            payload = msg.payload
            if isinstance(payload, bytes):
                payload_str = payload.decode('utf-8')
            else:
                payload_str = str(payload)
            
            # Parse JSON data
            data = json.loads(payload_str)
            
            # Check if SCD40 data is present
            if 'SCD40' not in data:
                self.logger.warning("Message missing SCD40 data")
                return None
            
            # Parse topic parts from "tele/snifferbuddy/<location>/<name>/SENSOR"
            topic_parts = msg.topic.split('/')
            tent_name = topic_parts[2] if len(topic_parts) > 2 else "unknown"
            device_name = topic_parts[3] if len(topic_parts) > 3 else "unknown"
            
            # Extract values from the data
            scd40_data = data.get('SCD40', {})
            time_str = data.get('Time')
            timestamp = datetime.fromisoformat(time_str)
            temperature = scd40_data.get('Temperature', 0.0)
            humidity = scd40_data.get('Humidity', 0.0)
            temp_unit = data.get('TempUnit', 'C')
            temp_in_celsius = temperature if temp_unit == 'C' else (temperature - 32) * 5/9
            vpd = self._calculate_vpd(temp_in_celsius, humidity)
            
            # Convert analog reading to light state
            analog_data = data.get('ANALOG', {})
            a0_value = analog_data.get('A0', 0) 
            light_on = a0_value > self.config.mqtt.light_threshold
            
            # Create reading
            reading = SCD4XSensorReading(
                timestamp=timestamp,
                device_name=device_name,
                tent_name=tent_name,
                light_on=light_on,
                CO2=scd40_data.get('CarbonDioxide', 0),
                temperature=temperature,
                humidity=humidity,
                vpd=vpd,
                dew_point=scd40_data.get('DewPoint', 0.0),
                temp_unit=temp_unit
            )
            
            return reading
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)
            return None

    def _calculate_vpd(self, temperature:float, humidity:float) -> float:
        """Calculate VPD (Vapor Pressure Deficit) using temperature and humidity. 
            2 degrees C less is assumed to be the leaf temperature.
        """
        leaf_temperature = temperature - 2
        saturation_vapor_pressure = 0.6108 * math.exp(17.27 * leaf_temperature / (leaf_temperature + 237.3))
        actual_vapor_pressure = (humidity/100) * saturation_vapor_pressure
        vpd = saturation_vapor_pressure - actual_vapor_pressure
        return vpd


  
