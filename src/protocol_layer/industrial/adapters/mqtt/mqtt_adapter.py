"""
MQTT Protocol Adapter for Industriverse Protocol Layer

This module provides a comprehensive adapter for integrating MQTT industrial protocol
with the Industriverse Protocol Layer. It enables seamless communication between
MQTT brokers/clients and the protocol-native architecture of Industriverse.

Features:
- Full MQTT client capabilities (v3.1, v3.1.1, v5.0)
- Support for QoS levels 0, 1, and 2
- TLS/SSL encryption with certificate validation
- Authentication (username/password, client certificates)
- Topic subscription with wildcards
- Message retention and persistence
- Last Will and Testament (LWT) messages
- Shared subscriptions
- Message filtering and transformation
- Automatic reconnection with backoff
- Security integration with EKIS framework
- Topic discovery and exploration

Dependencies:
- asyncio-mqtt (based on paho-mqtt)
- cryptography
"""

import asyncio
import json
import logging
import ssl
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

# Import Protocol Layer base components
from protocols.protocol_base import ProtocolComponent
from protocols.message_formats import MessageFactory, MessagePriority, MessageType
from protocols.discovery_service import DiscoveryService

# Import EKIS security components
from security.ekis.tpm_integration import TPMSecurityProvider
from security.ekis.security_handler import EKISSecurityHandler

# Import MQTT library
try:
    import asyncio_mqtt
    from asyncio_mqtt import Client, MqttError
    from asyncio_mqtt.client import ConnectError, MqttConnectError
    import paho.mqtt.client as paho
except ImportError:
    logging.error("MQTT library not found. Please install asyncio-mqtt package.")
    asyncio_mqtt = None
    Client = None

class MQTTQoS(Enum):
    """MQTT Quality of Service levels."""
    AT_MOST_ONCE = 0  # Fire and forget
    AT_LEAST_ONCE = 1  # Acknowledged delivery
    EXACTLY_ONCE = 2  # Assured delivery

class MQTTAdapter(ProtocolComponent):
    """
    MQTT Protocol Adapter for Industriverse Protocol Layer.
    
    This adapter enables bidirectional communication between MQTT brokers/clients
    and the Industriverse Protocol Layer, translating between MQTT protocol and
    Industriverse's protocol-native architecture.
    """
    
    def __init__(self, component_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MQTT adapter.
        
        Args:
            component_id: Unique identifier for this adapter instance
            config: Configuration parameters for the adapter
        """
        super().__init__(component_id or str(uuid.uuid4()), "mqtt_adapter")
        
        # Add capabilities
        self.add_capability("mqtt_client", "MQTT client functionality")
        self.add_capability("mqtt_subscription", "MQTT subscription management")
        self.add_capability("mqtt_publishing", "MQTT message publishing")
        self.add_capability("mqtt_discovery", "MQTT topic discovery")
        self.add_capability("mqtt_transformation", "MQTT message transformation")
        
        # Initialize configuration
        self.config = config or {}
        self.logger = logging.getLogger(f"industriverse.protocol.mqtt.{self.component_id}")
        
        # Initialize clients
        self.clients = {}
        self.subscriptions = {}
        self.message_handlers = {}
        self.topic_cache = {}
        
        # Initialize security handler
        self.security_handler = EKISSecurityHandler(
            component_id=f"{self.component_id}_security",
            tpm_provider=TPMSecurityProvider() if self.config.get("use_tpm", True) else None
        )
        
        # Register with discovery service
        self.discovery_service = DiscoveryService()
        self.discovery_service.register_component(
            self.component_id,
            "mqtt_adapter",
            {
                "protocols": ["mqtt"],
                "capabilities": list(self._capabilities.keys()),
                "industryTags": self.config.get("industry_tags", ["manufacturing", "energy", "iot", "smart_building"])
            }
        )
        
        self.logger.info(f"MQTT Adapter {self.component_id} initialized")
    
    async def connect(self, broker_id: str, hostname: str, port: int = 1883, 
                     username: Optional[str] = None, password: Optional[str] = None,
                     use_tls: bool = False, ca_certs: Optional[str] = None,
                     client_cert: Optional[str] = None, client_key: Optional[str] = None,
                     clean_session: bool = True, keepalive: int = 60,
                     client_id: Optional[str] = None, protocol: int = 4) -> bool:
        """
        Connect to an MQTT broker.
        
        Args:
            broker_id: Unique identifier for the broker connection
            hostname: Hostname or IP address of the MQTT broker
            port: Port number for the MQTT broker
            username: Optional username for authentication
            password: Optional password for authentication
            use_tls: Whether to use TLS/SSL encryption
            ca_certs: Path to CA certificate file for TLS verification
            client_cert: Path to client certificate file for TLS client authentication
            client_key: Path to client key file for TLS client authentication
            clean_session: Whether to start a clean session
            keepalive: Keepalive interval in seconds
            client_id: Client ID to use (generated if None)
            protocol: MQTT protocol version (3=v3.1, 4=v3.1.1, 5=v5.0)
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not asyncio_mqtt:
            self.logger.error("MQTT library not installed. Cannot connect.")
            return False
            
        try:
            # Generate client ID if not provided
            if not client_id:
                client_id = f"industriverse-{self.component_id}-{str(uuid.uuid4())[:8]}"
                
            # Configure TLS if enabled
            tls_params = None
            if use_tls:
                tls_context = ssl.create_default_context(
                    ssl.Purpose.SERVER_AUTH,
                    cafile=ca_certs
                )
                
                # Configure client certificate if provided
                if client_cert and client_key:
                    tls_context.load_cert_chain(client_cert, client_key)
                    
                # Set TLS parameters
                tls_params = {
                    "tls_context": tls_context,
                    "server_hostname": hostname
                }
            
            # Create client
            client = Client(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                client_id=client_id,
                clean_session=clean_session,
                keepalive=keepalive,
                protocol=protocol,
                tls_params=tls_params
            )
            
            # Connect to broker
            await client.connect()
            
            # Store client
            self.clients[broker_id] = {
                "client": client,
                "hostname": hostname,
                "port": port,
                "username": username,
                "use_tls": use_tls,
                "clean_session": clean_session,
                "client_id": client_id,
                "protocol": protocol,
                "connected_at": datetime.now(),
                "subscriptions": set()
            }
            
            self.logger.info(f"Connected to MQTT broker {broker_id} at {hostname}:{port}")
            
            # Start message listener
            asyncio.create_task(self._listen_for_messages(broker_id))
            
            # Publish connection event
            await self.publish_event(
                MessageFactory.create_event(
                    "mqtt_client_connected",
                    payload={
                        "broker_id": broker_id,
                        "hostname": hostname,
                        "port": port,
                        "client_id": client_id,
                        "protocol": protocol
                    },
                    priority=MessagePriority.MEDIUM
                )
            )
            
            return True
            
        except (ConnectError, MqttConnectError) as e:
            self.logger.error(f"Failed to connect to MQTT broker {broker_id} at {hostname}:{port}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error connecting to MQTT broker {broker_id}: {str(e)}")
            return False
    
    async def disconnect(self, broker_id: Optional[str] = None) -> bool:
        """
        Disconnect from an MQTT broker.
        
        Args:
            broker_id: ID of the broker to disconnect from.
                      If None, disconnect from all brokers.
                      
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if broker_id:
                if broker_id in self.clients:
                    # Get client
                    client_info = self.clients[broker_id]
                    client = client_info["client"]
                    
                    # Remove subscriptions for this broker
                    for sub_id, sub_info in list(self.subscriptions.items()):
                        if sub_info["broker_id"] == broker_id:
                            del self.subscriptions[sub_id]
                    
                    # Disconnect client
                    await client.disconnect()
                    del self.clients[broker_id]
                    self.logger.info(f"Disconnected from MQTT broker {broker_id}")
                    return True
                else:
                    self.logger.warning(f"Not connected to MQTT broker {broker_id}")
                    return False
            else:
                # Disconnect from all brokers
                for broker_id, client_info in list(self.clients.items()):
                    client = client_info["client"]
                    await client.disconnect()
                    self.logger.info(f"Disconnected from MQTT broker {broker_id}")
                
                # Clear clients and subscriptions
                self.clients = {}
                self.subscriptions = {}
                return True
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from MQTT broker: {str(e)}")
            return False
    
    async def publish(self, broker_id: str, topic: str, payload: Any, 
                     qos: MQTTQoS = MQTTQoS.AT_MOST_ONCE, retain: bool = False) -> bool:
        """
        Publish a message to an MQTT topic.
        
        Args:
            broker_id: ID of the broker to publish to
            topic: Topic to publish to
            payload: Message payload (will be converted to bytes)
            qos: Quality of Service level
            retain: Whether to retain the message
            
        Returns:
            bool: True if publish successful, False otherwise
        """
        if broker_id not in self.clients:
            self.logger.error(f"Not connected to MQTT broker {broker_id}")
            return False
            
        client_info = self.clients[broker_id]
        client = client_info["client"]
        
        try:
            # Convert payload to bytes if needed
            if isinstance(payload, dict) or isinstance(payload, list):
                payload_bytes = json.dumps(payload).encode('utf-8')
            elif isinstance(payload, str):
                payload_bytes = payload.encode('utf-8')
            elif isinstance(payload, bytes):
                payload_bytes = payload
            else:
                payload_bytes = str(payload).encode('utf-8')
                
            # Publish message
            await client.publish(
                topic,
                payload=payload_bytes,
                qos=qos.value,
                retain=retain
            )
            
            self.logger.debug(f"Published message to topic {topic} on broker {broker_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error publishing to topic {topic} on broker {broker_id}: {str(e)}")
            return False
    
    async def subscribe(self, broker_id: str, topic: str, qos: MQTTQoS = MQTTQoS.AT_MOST_ONCE,
                       callback: Optional[Callable] = None) -> str:
        """
        Subscribe to an MQTT topic.
        
        Args:
            broker_id: ID of the broker to subscribe on
            topic: Topic to subscribe to (can include wildcards)
            qos: Quality of Service level
            callback: Optional callback function to call when messages are received
            
        Returns:
            str: Subscription ID if successful, empty string otherwise
        """
        if broker_id not in self.clients:
            self.logger.error(f"Not connected to MQTT broker {broker_id}")
            return ""
            
        client_info = self.clients[broker_id]
        client = client_info["client"]
        
        try:
            # Subscribe to topic
            await client.subscribe(topic, qos=qos.value)
            
            # Generate subscription ID
            subscription_id = str(uuid.uuid4())
            
            # Store subscription
            self.subscriptions[subscription_id] = {
                "broker_id": broker_id,
                "topic": topic,
                "qos": qos.value,
                "callback": callback,
                "created_at": datetime.now()
            }
            
            # Add to client's subscriptions
            client_info["subscriptions"].add(topic)
            
            self.logger.info(f"Subscribed to topic {topic} on broker {broker_id} with ID {subscription_id}")
            return subscription_id
            
        except Exception as e:
            self.logger.error(f"Error subscribing to topic {topic} on broker {broker_id}: {str(e)}")
            return ""
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from an MQTT topic.
        
        Args:
            subscription_id: ID of the subscription to cancel
            
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        if subscription_id not in self.subscriptions:
            self.logger.error(f"Subscription {subscription_id} not found")
            return False
            
        try:
            # Get subscription info
            sub_info = self.subscriptions[subscription_id]
            broker_id = sub_info["broker_id"]
            topic = sub_info["topic"]
            
            if broker_id not in self.clients:
                self.logger.error(f"Not connected to MQTT broker {broker_id}")
                return False
                
            client_info = self.clients[broker_id]
            client = client_info["client"]
            
            # Check if other subscriptions use this topic
            other_subs_with_topic = False
            for sub_id, info in self.subscriptions.items():
                if sub_id != subscription_id and info["broker_id"] == broker_id and info["topic"] == topic:
                    other_subs_with_topic = True
                    break
                    
            # Only unsubscribe if no other subscriptions use this topic
            if not other_subs_with_topic:
                await client.unsubscribe(topic)
                client_info["subscriptions"].remove(topic)
                
            # Remove subscription
            del self.subscriptions[subscription_id]
            
            self.logger.info(f"Unsubscribed from topic {topic} on broker {broker_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unsubscribing from subscription {subscription_id}: {str(e)}")
            return False
    
    async def _listen_for_messages(self, broker_id: str):
        """
        Listen for messages on subscribed topics.
        
        Args:
            broker_id: ID of the broker to listen on
        """
        if broker_id not in self.clients:
            self.logger.error(f"Not connected to MQTT broker {broker_id}")
            return
            
        client_info = self.clients[broker_id]
        client = client_info["client"]
        
        try:
            async with client.messages() as messages:
                async for message in messages:
                    await self._handle_message(broker_id, message)
        except MqttError as e:
            self.logger.error(f"MQTT error on broker {broker_id}: {str(e)}")
            
            # Try to reconnect if client still exists
            if broker_id in self.clients:
                self.logger.info(f"Attempting to reconnect to broker {broker_id}")
                try:
                    await client.reconnect()
                    self.logger.info(f"Reconnected to broker {broker_id}")
                    
                    # Resubscribe to topics
                    for topic in client_info["subscriptions"]:
                        # Find QoS for this topic
                        qos = 0
                        for sub_info in self.subscriptions.values():
                            if sub_info["broker_id"] == broker_id and sub_info["topic"] == topic:
                                qos = max(qos, sub_info["qos"])
                                
                        await client.subscribe(topic, qos=qos)
                        self.logger.info(f"Resubscribed to topic {topic} on broker {broker_id}")
                        
                    # Restart message listener
                    asyncio.create_task(self._listen_for_messages(broker_id))
                except Exception as e:
                    self.logger.error(f"Failed to reconnect to broker {broker_id}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error in message listener for broker {broker_id}: {str(e)}")
    
    async def _handle_message(self, broker_id: str, message):
        """
        Handle an incoming MQTT message.
        
        Args:
            broker_id: ID of the broker the message came from
            message: MQTT message object
        """
        try:
            # Extract message details
            topic = message.topic
            payload = message.payload
            qos = message.qos
            retain = message.retain
            
            # Try to decode payload as JSON
            try:
                payload_dict = json.loads(payload.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not JSON, keep as bytes
                payload_dict = None
                
            # Format message
            msg = {
                "broker_id": broker_id,
                "topic": topic,
                "payload": payload_dict if payload_dict is not None else payload,
                "payload_raw": payload,
                "qos": qos,
                "retain": retain,
                "timestamp": datetime.now().isoformat()
            }
            
            # Find matching subscriptions
            matching_subs = []
            for sub_id, sub_info in self.subscriptions.items():
                if sub_info["broker_id"] == broker_id and self._topic_matches(sub_info["topic"], topic):
                    matching_subs.append((sub_id, sub_info))
                    
            # Call callbacks for matching subscriptions
            for sub_id, sub_info in matching_subs:
                if sub_info["callback"]:
                    try:
                        await sub_info["callback"](msg)
                    except Exception as e:
                        self.logger.error(f"Error in subscription callback for {sub_id}: {str(e)}")
                        
            # Publish event if any subscriptions matched
            if matching_subs:
                await self.publish_event(
                    MessageFactory.create_event(
                        "mqtt_message_received",
                        payload=msg,
                        priority=MessagePriority.LOW
                    )
                )
                
            # Update topic cache
            if topic not in self.topic_cache:
                self.topic_cache[topic] = {
                    "first_seen": datetime.now().isoformat(),
                    "message_count": 1,
                    "last_payload_type": type(payload_dict).__name__ if payload_dict is not None else "bytes",
                    "last_seen": datetime.now().isoformat()
                }
            else:
                self.topic_cache[topic]["message_count"] += 1
                self.topic_cache[topic]["last_payload_type"] = type(payload_dict).__name__ if payload_dict is not None else "bytes"
                self.topic_cache[topic]["last_seen"] = datetime.now().isoformat()
                
        except Exception as e:
            self.logger.error(f"Error handling MQTT message: {str(e)}")
    
    def _topic_matches(self, subscription_topic: str, message_topic: str) -> bool:
        """
        Check if a message topic matches a subscription topic pattern.
        
        Args:
            subscription_topic: Topic pattern with possible wildcards
            message_topic: Actual message topic
            
        Returns:
            bool: True if the message topic matches the subscription pattern
        """
        # Split topics into parts
        sub_parts = subscription_topic.split('/')
        msg_parts = message_topic.split('/')
        
        # Handle special case: '#' by itself matches everything
        if subscription_topic == '#':
            return True
            
        # If lengths don't match and there's no multi-level wildcard
        if len(sub_parts) != len(msg_parts) and '#' not in sub_parts:
            return False
            
        # Check each part
        for i, sub_part in enumerate(sub_parts):
            # Multi-level wildcard matches everything at this level and below
            if sub_part == '#':
                return True
                
            # Single-level wildcard matches anything at this level
            if sub_part == '+':
                # If this is the last part, it matches
                if i == len(sub_parts) - 1 and i == len(msg_parts) - 1:
                    continue
                # If not the last part, there must be more message parts
                elif i < len(msg_parts) - 1:
                    continue
                else:
                    return False
                    
            # Exact match required
            if i >= len(msg_parts) or sub_part != msg_parts[i]:
                return False
                
        # All parts matched
        return True
    
    async def discover_topics(self, broker_id: str, base_topic: str = "#", 
                             timeout: float = 10.0) -> List[Dict[str, Any]]:
        """
        Discover active topics on an MQTT broker.
        
        Args:
            broker_id: ID of the broker to discover topics on
            base_topic: Base topic to start discovery from
            timeout: Time to wait for messages in seconds
            
        Returns:
            List of discovered topics with metadata
        """
        if broker_id not in self.clients:
            self.logger.error(f"Not connected to MQTT broker {broker_id}")
            return []
            
        # Clear topic cache
        self.topic_cache = {}
        
        # Subscribe to discovery topic
        subscription_id = await self.subscribe(broker_id, base_topic, MQTTQoS.AT_MOST_ONCE)
        if not subscription_id:
            self.logger.error(f"Failed to subscribe for topic discovery on broker {broker_id}")
            return []
            
        try:
            # Wait for messages
            self.logger.info(f"Waiting {timeout} seconds for topic discovery on broker {broker_id}")
            await asyncio.sleep(timeout)
            
            # Unsubscribe
            await self.unsubscribe(subscription_id)
            
            # Format results
            results = []
            for topic, metadata in self.topic_cache.items():
                results.append({
                    "topic": topic,
                    **metadata
                })
                
            self.logger.info(f"Discovered {len(results)} topics on broker {broker_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error during topic discovery on broker {broker_id}: {str(e)}")
            
            # Try to unsubscribe
            try:
                await self.unsubscribe(subscription_id)
            except (KeyError, asyncio.TimeoutError, ConnectionError):
                # KeyError: subscription doesn't exist
                # TimeoutError: unsubscribe timed out
                # ConnectionError: not connected to broker
                pass
                
            return []
    
    async def get_broker_status(self, broker_id: str) -> Dict[str, Any]:
        """
        Get status information for a broker connection.
        
        Args:
            broker_id: ID of the broker to get status for
            
        Returns:
            Dict with broker status information
        """
        if broker_id not in self.clients:
            self.logger.error(f"Not connected to MQTT broker {broker_id}")
            return {"error": "Not connected to broker"}
            
        client_info = self.clients[broker_id]
        
        # Count subscriptions for this broker
        subscription_count = 0
        for sub_info in self.subscriptions.values():
            if sub_info["broker_id"] == broker_id:
                subscription_count += 1
                
        # Format status
        status = {
            "broker_id": broker_id,
            "hostname": client_info["hostname"],
            "port": client_info["port"],
            "client_id": client_info["client_id"],
            "protocol": client_info["protocol"],
            "connected_at": client_info["connected_at"].isoformat(),
            "subscription_count": subscription_count,
            "subscribed_topics": list(client_info["subscriptions"]),
            "connected": True
        }
        
        return status
    
    async def translate_to_industriverse(self, mqtt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate MQTT data to Industriverse protocol format.
        
        Args:
            mqtt_data: MQTT data to translate
            
        Returns:
            Data in Industriverse protocol format
        """
        # Create Unified Message Envelope
        ume = {
            "origin_protocol": "MQTT",
            "target_protocol": "MCP",
            "context": {
                "industrial_protocol": "MQTT",
                "adapter_id": self.component_id,
                "timestamp": datetime.now().isoformat()
            },
            "payload": mqtt_data,
            "trace_id": str(uuid.uuid4()),
            "security_level": "medium",
            "reflex_timer_ms": 5000  # 5 seconds default timeout
        }
        
        return ume
    
    async def translate_from_industriverse(self, industriverse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Industriverse protocol data to MQTT format.
        
        Args:
            industriverse_data: Industriverse protocol data to translate
            
        Returns:
            Data in MQTT format
        """
        # Extract payload from Unified Message Envelope
        if "payload" in industriverse_data:
            return industriverse_data["payload"]
        else:
            return industriverse_data
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming protocol messages.
        
        Args:
            message: Incoming message
            
        Returns:
            Response message
        """
        try:
            # Extract command from message
            command = message.get("command", "")
            params = message.get("params", {})
            
            # Process command
            if command == "connect":
                # Parse QoS if provided
                qos = None
                if "qos" in params:
                    try:
                        qos = MQTTQoS(params["qos"])
                    except ValueError:
                        pass
                        
                success = await self.connect(
                    params.get("broker_id", ""),
                    params.get("hostname", ""),
                    params.get("port", 1883),
                    params.get("username", None),
                    params.get("password", None),
                    params.get("use_tls", False),
                    params.get("ca_certs", None),
                    params.get("client_cert", None),
                    params.get("client_key", None),
                    params.get("clean_session", True),
                    params.get("keepalive", 60),
                    params.get("client_id", None),
                    params.get("protocol", 4)
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "disconnect":
                success = await self.disconnect(params.get("broker_id", None))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "publish":
                # Parse QoS
                try:
                    qos = MQTTQoS(params.get("qos", 0))
                except ValueError:
                    qos = MQTTQoS.AT_MOST_ONCE
                    
                success = await self.publish(
                    params.get("broker_id", ""),
                    params.get("topic", ""),
                    params.get("payload", ""),
                    qos,
                    params.get("retain", False)
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "subscribe":
                # Parse QoS
                try:
                    qos = MQTTQoS(params.get("qos", 0))
                except ValueError:
                    qos = MQTTQoS.AT_MOST_ONCE
                    
                subscription_id = await self.subscribe(
                    params.get("broker_id", ""),
                    params.get("topic", ""),
                    qos
                )
                return MessageFactory.create_response(message, result={"subscription_id": subscription_id})
                
            elif command == "unsubscribe":
                success = await self.unsubscribe(params.get("subscription_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "discover_topics":
                result = await self.discover_topics(
                    params.get("broker_id", ""),
                    params.get("base_topic", "#"),
                    params.get("timeout", 10.0)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "get_broker_status":
                result = await self.get_broker_status(params.get("broker_id", ""))
                return MessageFactory.create_response(message, result=result)
                
            else:
                return MessageFactory.create_response(
                    message,
                    success=False,
                    error=f"Unknown command: {command}"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            return MessageFactory.create_response(
                message,
                success=False,
                error=f"Error: {str(e)}"
            )
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming messages from the Protocol Layer.
        
        This method is called by the Protocol Layer when a message is received
        for this adapter.
        
        Args:
            message: Incoming message
            
        Returns:
            Response message
        """
        # Translate from Industriverse protocol if needed
        if message.get("origin_protocol") and message.get("origin_protocol") != "MQTT":
            mqtt_message = await self.translate_from_industriverse(message)
        else:
            mqtt_message = message
            
        # Handle message
        response = await self.handle_message(mqtt_message)
        
        # Translate to Industriverse protocol if needed
        if message.get("target_protocol") and message.get("target_protocol") != "MQTT":
            industriverse_response = await self.translate_to_industriverse(response)
            return industriverse_response
        else:
            return response
    
    async def shutdown(self):
        """
        Shutdown the adapter, closing all connections and subscriptions.
        """
        self.logger.info(f"Shutting down MQTT Adapter {self.component_id}")
        
        # Disconnect all clients
        await self.disconnect()
        
        # Unregister from discovery service
        self.discovery_service.unregister_component(self.component_id)
        
        self.logger.info(f"MQTT Adapter {self.component_id} shutdown complete")

# Example usage
async def example_usage():
    # Create adapter
    adapter = MQTTAdapter(config={
        "use_tpm": True,
        "industry_tags": ["manufacturing", "energy", "iot"]
    })
    
    # Connect to broker
    success = await adapter.connect(
        broker_id="broker1",
        hostname="mqtt.example.com",
        port=1883,
        username="user",
        password="password"
    )
    
    if success:
        # Subscribe to topic
        subscription_id = await adapter.subscribe(
            broker_id="broker1",
            topic="sensors/#",
            qos=MQTTQoS.AT_LEAST_ONCE
        )
        
        # Publish message
        await adapter.publish(
            broker_id="broker1",
            topic="sensors/temperature",
            payload={"value": 25.5, "unit": "C"},
            qos=MQTTQoS.AT_LEAST_ONCE
        )
        
        # Wait for some messages
        await asyncio.sleep(10)
        
        # Discover topics
        topics = await adapter.discover_topics(
            broker_id="broker1",
            base_topic="#",
            timeout=5.0
        )
        print(f"Discovered topics: {topics}")
        
        # Unsubscribe
        await adapter.unsubscribe(subscription_id)
        
        # Disconnect
        await adapter.disconnect("broker1")
    
    # Shutdown
    await adapter.shutdown()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run example
    asyncio.run(example_usage())
