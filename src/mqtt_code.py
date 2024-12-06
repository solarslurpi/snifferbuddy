"""This code focuses on receiving messages from SnifferBuddies. When it receives a message, it places it into a SQLite database.

The MQTTListener maintains a persistent connection to the MQTT broker and listens for messages from SnifferBuddy devices.
These devices publish environmental sensor data (like temperature, humidity, etc.) to specific MQTT topics.
When a message is received, it is decoded and stored in a SQLite database for later analysis and tracking.

The listener automatically handles connection issues common to Raspberry Pi deployments, including network interruptions
and broker disconnections, ensuring reliable data collection over long periods.
"""
from dotenv import load_dotenv
import json
import logging

import paho.mqtt.client as mqtt
import anyio
from anyio.streams.memory import MemoryObjectSendStream

from config import AppConfig
from src.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

class MQTTListener:
    def __init__(self, config: AppConfig, send_stream: MemoryObjectSendStream):
        """Initialize the MQTT listener with configuration and send stream."""
        self.light_threshold = config.mqtt.light_threshold
        self.mqtt_host = config.mqtt.host
        self.mqtt_port = config.mqtt.port
        # We will receive LWT messages. SnifferBuddy sets up the LWT message that should be sent if disconnects occur.
        self.mqtt_readings_topic = config.mqtt.readings_topic
        self.mqtt_lwt_topic = config.mqtt.lwt_topic
        self.send_stream = send_stream
        self._portal = None  # Initialize the portal as None

        # Config mqtt client
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback for when the client receives a CONNACK response from the server."""
        if rc == 0:
            logger.info("Connected to MQTT Broker")
            # Subscribe with QoS 1 to ensure reliable delivery
            result1 = self.client.subscribe(self.mqtt_readings_topic, qos=1)
            result2 = self.client.subscribe(self.mqtt_lwt_topic, qos=1)

            # Log subscription details
            logger.debug(f"Subscription attempts:")
            logger.debug(f"  Readings topic: {self.mqtt_readings_topic} -> {result1}")
            logger.debug(f"  LWT topic: {self.mqtt_lwt_topic} -> {result2}")
        else:
            connection_errors = {
                1: "incorrect protocol version",
                2: "invalid client identifier",
                3: "server unavailable",
                4: "bad username or password",
                5: "not authorized"
            }
            error_msg = connection_errors.get(rc, f"unknown error code {rc}")
            logger.error(f"Connection failed: {error_msg}")

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        topic = msg.topic
        try:
            payload = msg.payload.decode()
            logger.info("Received message:")
            logger.info(f"  Topic: {topic}")
            logger.info(f"  Payload: {payload}")
            logger.info(f"  QoS: {msg.qos}")
            logger.info(f"  Retain: {msg.retain}")

            if topic.endswith('/LWT'):
                data = payload
                logger.debug("Processing as LWT message")
            else:
                data = json.loads(payload)
                logger.debug("Processing as JSON message")

            # Use the portal to send messages from the MQTT thread
            if self._portal:
                self._portal.call(self.send_stream.send_nowait, data)
                logger.debug("Successfully forwarded message through portal")
            else:
                logger.warning("Portal not available for message forwarding")

        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from topic {topic}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)

    def connect(self):
        """Connect to the MQTT broker and start the network loop.

        This method establishes the connection to the MQTT broker using the configured
        host and port from the environment variables. It also starts the background
        network loop to handle MQTT communication.
        """
        try:
            self.client.connect(self.mqtt_host, int(self.mqtt_port))
            self.client.loop_start()  # Starts background thread for network loop
            logger.debug(f"Attempting connection to {self.mqtt_host}:{self.mqtt_port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            raise

    async def disconnect(self):
        """Disconnect from the MQTT broker and stop the network loop."""
        if self.client:
            self.client.loop_stop()  # Stop the background thread
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")

    async def run(self):
        """Run the MQTT client."""
        with anyio.from_thread.start_blocking_portal() as portal:
            self._portal = portal
            self.client.connect(self.mqtt_host, self.mqtt_port)
            self.client.loop_start()
            try:
                # Don't block the task group
                while True:
                    await anyio.sleep(1)
            except Exception as e:
                logger.error(f"MQTT error: {e}")
                raise
            finally:
                self.client.loop_stop()
                self.client.disconnect()

    async def parse_message(self, message):
        try:
            return json.loads(message.payload)
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON")
            return None