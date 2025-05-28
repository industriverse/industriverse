"""
Kafka Client Wrapper for the Overseer System.

This module provides a wrapper around the Kafka client for use by Overseer System components.
It handles connection management, message serialization/deserialization, and error handling.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError

class KafkaClientWrapper:
    """Wrapper for Kafka client operations."""
    
    def __init__(
        self, 
        bootstrap_servers: str = "kafka:9092",
        client_id: str = "overseer-client",
        group_id: str = "overseer-group"
    ):
        """
        Initialize the Kafka client wrapper.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            client_id: Client ID for Kafka
            group_id: Consumer group ID
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.group_id = group_id
        self.producer = None
        self.consumers = {}
        self.logger = logging.getLogger("kafka_client")
        
    async def initialize(self):
        """Initialize the Kafka client."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8')
            )
            await self.producer.start()
            self.logger.info("Kafka producer initialized")
        except Exception as e:
            self.logger.error(f"Error initializing Kafka producer: {e}")
            raise
            
    async def shutdown(self):
        """Shutdown the Kafka client."""
        if self.producer:
            await self.producer.stop()
            self.logger.info("Kafka producer stopped")
            
        for consumer in self.consumers.values():
            await consumer.stop()
        self.logger.info("Kafka consumers stopped")
            
    async def send(self, topic: str, value: Any, key: Optional[str] = None) -> bool:
        """
        Send a message to a Kafka topic.
        
        Args:
            topic: Topic to send to
            value: Message value
            key: Message key
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.producer:
            self.logger.error("Kafka producer not initialized")
            return False
            
        try:
            await self.producer.send_and_wait(topic, value, key)
            return True
        except Exception as e:
            self.logger.error(f"Error sending message to {topic}: {e}")
            return False
            
    async def subscribe(
        self, 
        topics: Union[str, List[str]], 
        handler: Callable[[str, Any, Optional[str]], None],
        group_id: Optional[str] = None
    ) -> bool:
        """
        Subscribe to Kafka topics.
        
        Args:
            topics: Topic or list of topics to subscribe to
            handler: Function to call when a message is received
            group_id: Consumer group ID (defaults to self.group_id)
            
        Returns:
            True if subscribed successfully, False otherwise
        """
        if isinstance(topics, str):
            topics = [topics]
            
        consumer_key = ",".join(topics)
        if consumer_key in self.consumers:
            self.logger.warning(f"Already subscribed to {consumer_key}")
            return True
            
        try:
            consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id or self.group_id,
                client_id=f"{self.client_id}-{consumer_key}",
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None
            )
            await consumer.start()
            self.consumers[consumer_key] = consumer
            
            # Start consumer task
            asyncio.create_task(self._consume(consumer, handler))
            
            self.logger.info(f"Subscribed to {consumer_key}")
            return True
        except Exception as e:
            self.logger.error(f"Error subscribing to {consumer_key}: {e}")
            return False
            
    async def _consume(
        self, 
        consumer: AIOKafkaConsumer, 
        handler: Callable[[str, Any, Optional[str]], None]
    ):
        """
        Consume messages from Kafka.
        
        Args:
            consumer: Kafka consumer
            handler: Function to call when a message is received
        """
        try:
            async for message in consumer:
                try:
                    await handler(message.topic, message.value, message.key)
                except Exception as e:
                    self.logger.error(f"Error handling message: {e}")
        except Exception as e:
            self.logger.error(f"Error consuming messages: {e}")
            
    async def unsubscribe(self, topics: Union[str, List[str]]) -> bool:
        """
        Unsubscribe from Kafka topics.
        
        Args:
            topics: Topic or list of topics to unsubscribe from
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        if isinstance(topics, str):
            topics = [topics]
            
        consumer_key = ",".join(topics)
        if consumer_key not in self.consumers:
            self.logger.warning(f"Not subscribed to {consumer_key}")
            return True
            
        try:
            consumer = self.consumers[consumer_key]
            await consumer.stop()
            del self.consumers[consumer_key]
            self.logger.info(f"Unsubscribed from {consumer_key}")
            return True
        except Exception as e:
            self.logger.error(f"Error unsubscribing from {consumer_key}: {e}")
            return False
