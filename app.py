"""Main application that connects MQTT listener with database storage."""
import logging
from contextlib import asynccontextmanager
import anyio
from typing import  AsyncGenerator
from anyio import Event


from config import AppConfig
from src.mqtt_code import MQTTListener
from src.database_code import SensorDatabase
from src.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class SensorMonitor:
    def __init__(self):
        self.config = AppConfig.from_yaml('config.yaml')
        # Create the stream pair that connects MQTT to Database
        self.send_stream, self.receive_stream = anyio.create_memory_object_stream(100)
        self._latest_reading = None
        self._reading_event = Event()

    async def get_readings(self) -> AsyncGenerator:
        """Yield sensor readings as they arrive."""
        while True:
            await self._reading_event.wait()
            yield self._latest_reading
            self._reading_event = Event()

    async def handle_message(self, message):
        """Process incoming MQTT messages and store them in the database."""
        try:
            # Handle LWT (Last Will and Testament) messages
            if message.topic.endswith('/LWT'):
                logger.debug(f"Device status change: {message.topic} - {message.payload}")
                return

            data = await self.mqtt_listener.parse_message(message)
            if data:
                await self.db.store_reading(data)
                # Update latest reading and notify waiters
                self._latest_reading = data
                self._reading_event.set()
                logger.debug(f"Successfully stored reading from {message.topic}")
            else:
                logger.warning(f"Received invalid data on topic {message.topic}")

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    @asynccontextmanager
    async def lifespan(self):
        """Manage application lifecycle."""
        try:
            # Initialize components with their respective stream ends
            self.db = SensorDatabase(self.config,receive_stream=self.receive_stream)
            self.mqtt_listener = MQTTListener(self.config, send_stream=self.send_stream)
            yield self
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Clean shutdown of all services."""
        if self.mqtt_listener:
            await self.mqtt_listener.disconnect()
        logger.info("Sensor Monitoring System stopped")

    async def run(self):
        """Main application run loop."""
        logger.debug("Starting application run loop")
        async with anyio.create_task_group() as tg:
            # Spawn MQTT listener
            logger.debug("Starting MQTT listener task")
            tg.start_soon(self.mqtt_listener.run)
            logger.info("MQTT listener initialized and connected")

            # Start the database run loop
            logger.debug("Starting database processor task")
            tg.start_soon(self.db.run)
            logger.info("Database processor started")

            try:
                while True:
                    await anyio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received interrupt")

async def main():
    """Application entry point."""
    monitor = SensorMonitor()
    try:
        async with monitor.lifespan() as monitor:
            await monitor.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == "__main__":
    anyio.run(main)