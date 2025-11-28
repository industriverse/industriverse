import asyncio
import logging
from typing import Callable, Awaitable
from gmqtt import Client as MQTTClient

logger = logging.getLogger(__name__)

class MQTTConnector:
    def __init__(self, client_id: str, broker_host: str = "localhost", broker_port: int = 1883):
        self.client = MQTTClient(client_id)
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic_handlers = {}

    async def connect(self):
        """Connect to the MQTT broker."""
        try:
            await self.client.connect(self.broker_host, self.broker_port)
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

    async def disconnect(self):
        """Disconnect from the broker."""
        await self.client.disconnect()
        logger.info("Disconnected from MQTT broker")

    def on_message(self, client, topic, payload, qos, properties):
        """Handle incoming messages."""
        handler = self.topic_handlers.get(topic)
        if handler:
            asyncio.create_task(handler(payload.decode()))
        else:
            # Handle wildcard matches if needed
            pass

    async def subscribe(self, topic: str, handler: Callable[[str], Awaitable[None]]):
        """Subscribe to a topic with a handler."""
        self.client.on_message = self.on_message
        self.topic_handlers[topic] = handler
        self.client.subscribe(topic)
        logger.info(f"Subscribed to topic: {topic}")

    async def publish(self, topic: str, payload: str):
        """Publish a message."""
        self.client.publish(topic, payload)

# Example usage
if __name__ == "__main__":
    connector = MQTTConnector("test_client")
    # await connector.connect()
