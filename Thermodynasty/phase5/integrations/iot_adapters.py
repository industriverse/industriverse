"""
IoT Device Adapters

Production-grade IoT integration for energy sensors, industrial equipment,
and real-time telemetry collection from edge devices.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from enum import Enum
import json

try:
    import paho.mqtt.client as mqtt
    from paho.mqtt.client import MQTTMessage
except ImportError:
    mqtt = None
    MQTTMessage = None

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DeviceType(str, Enum):
    """IoT device types"""
    ENERGY_SENSOR = "energy_sensor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    PRESSURE_SENSOR = "pressure_sensor"
    FLOW_METER = "flow_meter"
    POWER_METER = "power_meter"
    VIBRATION_SENSOR = "vibration_sensor"
    INDUSTRIAL_CONTROLLER = "industrial_controller"
    GENERIC = "generic"


class Protocol(str, Enum):
    """Communication protocols"""
    MQTT = "mqtt"
    MODBUS = "modbus"
    OPCUA = "opcua"
    HTTP = "http"
    WEBSOCKET = "websocket"


class MQTTConfig(BaseModel):
    """MQTT broker configuration"""
    broker_host: str = Field(..., description="MQTT broker host")
    broker_port: int = Field(default=1883, description="MQTT broker port")
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: str = Field(default="eil_iot_adapter", description="MQTT client ID")
    keepalive: int = Field(default=60, description="Keep-alive interval (s)")
    qos: int = Field(default=1, description="QoS level (0, 1, 2)")
    clean_session: bool = Field(default=True, description="Clean session flag")
    tls_enabled: bool = Field(default=False, description="Enable TLS/SSL")
    tls_ca_certs: Optional[str] = None
    reconnect_delay_min: int = Field(default=1, description="Min reconnect delay (s)")
    reconnect_delay_max: int = Field(default=120, description="Max reconnect delay (s)")


class DeviceReading(BaseModel):
    """IoT device reading"""
    device_id: str
    device_type: DeviceType
    timestamp: datetime
    value: float
    unit: str
    metadata: Dict[str, Any] = {}
    quality: float = Field(default=1.0, ge=0.0, le=1.0, description="Reading quality (0-1)")


class Device(BaseModel):
    """IoT device registration"""
    device_id: str
    device_type: DeviceType
    protocol: Protocol
    topic: Optional[str] = None  # For MQTT
    address: Optional[str] = None  # For Modbus/OPC-UA
    polling_interval: int = Field(default=60, description="Polling interval (s)")
    metadata: Dict[str, Any] = {}
    enabled: bool = True


class MQTTAdapter:
    """
    MQTT adapter for IoT devices.

    Features:
    - Auto-reconnect with exponential backoff
    - QoS support
    - TLS/SSL encryption
    - Message buffering during disconnection
    - Wildcard topic subscriptions
    - Last Will and Testament
    """

    def __init__(self, config: MQTTConfig):
        """
        Initialize MQTT adapter.

        Args:
            config: MQTT configuration
        """
        if mqtt is None:
            raise ImportError(
                "paho-mqtt required for MQTT integration. "
                "Install with: pip install paho-mqtt"
            )

        self.config = config
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self.message_handlers: Dict[str, List[Callable]] = {}

        # Message buffer for offline storage
        self.message_buffer: List[Dict[str, Any]] = []
        self.max_buffer_size = 10000

        logger.info(
            f"MQTTAdapter initialized: broker={config.broker_host}:{config.broker_port}"
        )

    def connect(self):
        """Connect to MQTT broker"""
        self.client = mqtt.Client(
            client_id=self.config.client_id,
            clean_session=self.config.clean_session
        )

        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        # Authentication
        if self.config.username and self.config.password:
            self.client.username_pw_set(
                self.config.username,
                self.config.password
            )

        # TLS/SSL
        if self.config.tls_enabled:
            self.client.tls_set(ca_certs=self.config.tls_ca_certs)

        # Last Will and Testament
        self.client.will_set(
            topic=f"eil/iot/{self.config.client_id}/status",
            payload=json.dumps({"status": "offline", "timestamp": datetime.utcnow().isoformat()}),
            qos=self.config.qos,
            retain=True
        )

        # Connect
        try:
            self.client.connect(
                self.config.broker_host,
                self.config.broker_port,
                self.config.keepalive
            )

            # Start network loop
            self.client.loop_start()

            logger.info(f"Connecting to MQTT broker: {self.config.broker_host}:{self.config.broker_port}")

        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            raise

    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from MQTT broker")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for successful connection"""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker: {self.config.broker_host}")

            # Publish online status
            self.publish(
                topic=f"eil/iot/{self.config.client_id}/status",
                payload={"status": "online", "timestamp": datetime.utcnow().isoformat()},
                retain=True
            )

            # Resubscribe to topics
            for topic in self.message_handlers.keys():
                self.client.subscribe(topic, qos=self.config.qos)
                logger.info(f"Resubscribed to topic: {topic}")

            # Flush buffered messages
            self._flush_buffer()

        else:
            logger.error(f"MQTT connection failed with code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback for disconnection"""
        self.connected = False

        if rc == 0:
            logger.info("Disconnected from MQTT broker (clean)")
        else:
            logger.warning(f"Unexpected disconnection from MQTT broker (rc={rc})")

    def _on_message(self, client, userdata, msg: MQTTMessage):
        """Callback for incoming messages"""
        try:
            # Decode payload
            payload = json.loads(msg.payload.decode('utf-8'))

            logger.debug(f"Received message on {msg.topic}: {payload}")

            # Call handlers for this topic
            for topic_pattern, handlers in self.message_handlers.items():
                if mqtt.topic_matches_sub(topic_pattern, msg.topic):
                    for handler in handlers:
                        try:
                            handler(msg.topic, payload)
                        except Exception as e:
                            logger.error(f"Message handler failed: {e}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message payload: {e}")
        except Exception as e:
            logger.error(f"Message processing failed: {e}")

    def subscribe(self, topic: str, handler: Callable):
        """
        Subscribe to topic with message handler.

        Args:
            topic: MQTT topic (supports wildcards: +, #)
            handler: Message handler function(topic, payload)
        """
        if topic not in self.message_handlers:
            self.message_handlers[topic] = []

        self.message_handlers[topic].append(handler)

        if self.connected and self.client:
            self.client.subscribe(topic, qos=self.config.qos)
            logger.info(f"Subscribed to topic: {topic}")

    def unsubscribe(self, topic: str):
        """
        Unsubscribe from topic.

        Args:
            topic: MQTT topic
        """
        if topic in self.message_handlers:
            del self.message_handlers[topic]

        if self.connected and self.client:
            self.client.unsubscribe(topic)
            logger.info(f"Unsubscribed from topic: {topic}")

    def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        qos: Optional[int] = None,
        retain: bool = False
    ):
        """
        Publish message to topic.

        Args:
            topic: MQTT topic
            payload: Message payload (dict)
            qos: QoS level (default: config QoS)
            retain: Retain flag
        """
        message_json = json.dumps(payload)
        qos_level = qos if qos is not None else self.config.qos

        if self.connected and self.client:
            try:
                result = self.client.publish(
                    topic,
                    message_json,
                    qos=qos_level,
                    retain=retain
                )

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.debug(f"Published to {topic}: {payload}")
                else:
                    logger.error(f"Publish failed: {result.rc}")
                    self._buffer_message(topic, payload, qos_level, retain)

            except Exception as e:
                logger.error(f"Publish exception: {e}")
                self._buffer_message(topic, payload, qos_level, retain)
        else:
            # Buffer for later
            self._buffer_message(topic, payload, qos_level, retain)

    def _buffer_message(self, topic: str, payload: Dict[str, Any], qos: int, retain: bool):
        """Buffer message for offline delivery"""
        if len(self.message_buffer) < self.max_buffer_size:
            self.message_buffer.append({
                'topic': topic,
                'payload': payload,
                'qos': qos,
                'retain': retain,
                'timestamp': datetime.utcnow()
            })
            logger.debug(f"Buffered message: {topic} (buffer size: {len(self.message_buffer)})")
        else:
            logger.warning("Message buffer full, dropping message")

    def _flush_buffer(self):
        """Flush buffered messages"""
        if not self.message_buffer:
            return

        logger.info(f"Flushing {len(self.message_buffer)} buffered messages")

        for msg in self.message_buffer:
            self.publish(
                topic=msg['topic'],
                payload=msg['payload'],
                qos=msg['qos'],
                retain=msg['retain']
            )

        self.message_buffer.clear()


class IoTDeviceManager:
    """
    IoT device manager for EIL platform.

    Features:
    - Multi-protocol support (MQTT, Modbus, OPC-UA)
    - Device registration and discovery
    - Automatic data collection
    - Reading validation and quality assessment
    - Data transformation and normalization
    - Event-driven architecture
    """

    def __init__(self, mqtt_config: Optional[MQTTConfig] = None):
        """
        Initialize IoT device manager.

        Args:
            mqtt_config: MQTT configuration
        """
        self.devices: Dict[str, Device] = {}
        self.mqtt_adapter: Optional[MQTTAdapter] = None
        self.reading_handlers: List[Callable] = []

        # Initialize MQTT if configured
        if mqtt_config:
            self.mqtt_adapter = MQTTAdapter(mqtt_config)
            self.mqtt_adapter.connect()

        logger.info("IoTDeviceManager initialized")

    def register_device(self, device: Device):
        """
        Register IoT device.

        Args:
            device: Device configuration
        """
        self.devices[device.device_id] = device

        # Subscribe to MQTT topic if applicable
        if device.protocol == Protocol.MQTT and device.topic and self.mqtt_adapter:
            self.mqtt_adapter.subscribe(
                device.topic,
                lambda topic, payload: self._handle_mqtt_reading(device.device_id, topic, payload)
            )

        logger.info(f"Registered device: {device.device_id} ({device.device_type.value})")

    def unregister_device(self, device_id: str):
        """
        Unregister IoT device.

        Args:
            device_id: Device identifier
        """
        if device_id in self.devices:
            device = self.devices[device_id]

            # Unsubscribe from MQTT
            if device.protocol == Protocol.MQTT and device.topic and self.mqtt_adapter:
                self.mqtt_adapter.unsubscribe(device.topic)

            del self.devices[device_id]
            logger.info(f"Unregistered device: {device_id}")

    def _handle_mqtt_reading(self, device_id: str, topic: str, payload: Dict[str, Any]):
        """Handle incoming MQTT reading"""
        device = self.devices.get(device_id)
        if not device:
            logger.warning(f"Reading from unknown device: {device_id}")
            return

        try:
            # Parse reading
            reading = DeviceReading(
                device_id=device_id,
                device_type=device.device_type,
                timestamp=datetime.fromisoformat(payload.get('timestamp', datetime.utcnow().isoformat())),
                value=float(payload['value']),
                unit=payload.get('unit', 'unknown'),
                metadata=payload.get('metadata', {}),
                quality=float(payload.get('quality', 1.0))
            )

            # Validate reading
            if self._validate_reading(reading):
                # Notify handlers
                for handler in self.reading_handlers:
                    try:
                        handler(reading)
                    except Exception as e:
                        logger.error(f"Reading handler failed: {e}")
            else:
                logger.warning(f"Invalid reading from {device_id}: {reading}")

        except Exception as e:
            logger.error(f"Failed to process reading from {device_id}: {e}")

    def _validate_reading(self, reading: DeviceReading) -> bool:
        """
        Validate device reading.

        Args:
            reading: Device reading

        Returns:
            True if valid
        """
        # Quality threshold
        if reading.quality < 0.5:
            logger.warning(f"Low quality reading: {reading.quality}")
            return False

        # Value sanity checks
        if not np.isfinite(reading.value):
            logger.warning(f"Invalid reading value: {reading.value}")
            return False

        # Timestamp reasonableness
        now = datetime.utcnow()
        time_diff = abs((now - reading.timestamp).total_seconds())
        if time_diff > 3600:  # More than 1 hour old
            logger.warning(f"Stale reading: {time_diff}s old")
            return False

        return True

    def subscribe_to_readings(self, handler: Callable):
        """
        Subscribe to device readings.

        Args:
            handler: Callback function(reading: DeviceReading)
        """
        self.reading_handlers.append(handler)
        logger.info("Subscribed to device readings")

    def publish_command(self, device_id: str, command: str, parameters: Dict[str, Any] = None):
        """
        Send command to device.

        Args:
            device_id: Device identifier
            command: Command name
            parameters: Command parameters
        """
        device = self.devices.get(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            return

        if device.protocol == Protocol.MQTT and self.mqtt_adapter:
            command_topic = f"eil/iot/{device_id}/command"
            payload = {
                'command': command,
                'parameters': parameters or {},
                'timestamp': datetime.utcnow().isoformat()
            }

            self.mqtt_adapter.publish(command_topic, payload)
            logger.info(f"Sent command '{command}' to device {device_id}")

        else:
            logger.warning(f"Command not supported for protocol: {device.protocol.value}")

    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get device status.

        Args:
            device_id: Device identifier

        Returns:
            Device status
        """
        device = self.devices.get(device_id)
        if not device:
            return {'error': 'Device not found'}

        return {
            'device_id': device.device_id,
            'device_type': device.device_type.value,
            'protocol': device.protocol.value,
            'enabled': device.enabled,
            'metadata': device.metadata
        }

    def list_devices(self, device_type: Optional[DeviceType] = None) -> List[Device]:
        """
        List registered devices.

        Args:
            device_type: Filter by device type

        Returns:
            List of devices
        """
        devices = list(self.devices.values())

        if device_type:
            devices = [d for d in devices if d.device_type == device_type]

        return devices

    def close(self):
        """Shutdown IoT manager"""
        if self.mqtt_adapter:
            self.mqtt_adapter.disconnect()

        logger.info("IoTDeviceManager closed")


# ============================================================================
# Energy Sensor Integration
# ============================================================================

class EnergySensorAdapter:
    """Specialized adapter for energy sensors"""

    def __init__(self, iot_manager: IoTDeviceManager):
        """
        Initialize energy sensor adapter.

        Args:
            iot_manager: IoT device manager
        """
        self.iot_manager = iot_manager
        self.energy_readings: List[DeviceReading] = []
        self.max_readings = 1000

        # Subscribe to readings
        iot_manager.subscribe_to_readings(self._handle_reading)

        logger.info("EnergySensorAdapter initialized")

    def _handle_reading(self, reading: DeviceReading):
        """Handle energy sensor reading"""
        if reading.device_type == DeviceType.ENERGY_SENSOR:
            # Store reading
            self.energy_readings.append(reading)

            # Maintain buffer size
            if len(self.energy_readings) > self.max_readings:
                self.energy_readings = self.energy_readings[-self.max_readings:]

            logger.debug(f"Energy reading: {reading.device_id} = {reading.value} {reading.unit}")

    def get_current_energy(self, device_id: str) -> Optional[float]:
        """
        Get current energy reading.

        Args:
            device_id: Device identifier

        Returns:
            Current energy value
        """
        # Find most recent reading
        for reading in reversed(self.energy_readings):
            if reading.device_id == device_id:
                return reading.value

        return None

    def get_energy_history(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DeviceReading]:
        """
        Get energy reading history.

        Args:
            device_id: Device identifier
            start_time: Filter start time
            limit: Maximum readings

        Returns:
            Energy readings
        """
        readings = [
            r for r in self.energy_readings
            if r.device_id == device_id and
               (start_time is None or r.timestamp >= start_time)
        ]

        return readings[-limit:]


# ============================================================================
# Global IoT Manager
# ============================================================================

_iot_manager: Optional[IoTDeviceManager] = None


def get_iot_manager(mqtt_config: Optional[MQTTConfig] = None) -> IoTDeviceManager:
    """Get global IoT device manager instance"""
    global _iot_manager
    if _iot_manager is None:
        _iot_manager = IoTDeviceManager(mqtt_config)
    return _iot_manager


# ============================================================================
# Convenience Functions
# ============================================================================

def register_energy_sensor(
    device_id: str,
    mqtt_topic: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """Register energy sensor (convenience function)"""
    manager = get_iot_manager()

    device = Device(
        device_id=device_id,
        device_type=DeviceType.ENERGY_SENSOR,
        protocol=Protocol.MQTT,
        topic=mqtt_topic,
        metadata=metadata or {}
    )

    manager.register_device(device)
    logger.info(f"Registered energy sensor: {device_id}")
