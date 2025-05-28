"""
Protocol-to-Native App Bridge for Industriverse Protocol Layer

This module implements the Protocol-to-Native App Bridge, enabling seamless
integration between protocol-native components and traditional native applications
across various platforms and environments.

Features:
1. Protocol-to-Native translation layer
2. Native API adapters for common platforms
3. Bidirectional communication channels
4. Event synchronization between protocol and native worlds
5. Automatic protocol envelope wrapping/unwrapping
6. Native app discovery and capability mapping
"""

import uuid
import time
import asyncio
import logging
import json
import base64
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Types of native application platforms."""
    WEB = "web"
    MOBILE_ANDROID = "mobile_android"
    MOBILE_IOS = "mobile_ios"
    DESKTOP_WINDOWS = "desktop_windows"
    DESKTOP_MACOS = "desktop_macos"
    DESKTOP_LINUX = "desktop_linux"
    EMBEDDED = "embedded"
    CLOUD = "cloud"
    CUSTOM = "custom"


class IntegrationType(Enum):
    """Types of integration methods."""
    REST_API = "rest_api"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    MESSAGE_QUEUE = "message_queue"
    SHARED_MEMORY = "shared_memory"
    FILE_BASED = "file_based"
    CUSTOM_PROTOCOL = "custom_protocol"


@dataclass
class NativeAppRegistration:
    """
    Represents a registered native application.
    """
    app_id: str
    name: str
    platform: PlatformType
    integration_type: IntegrationType
    connection_info: Dict[str, Any]
    capabilities: List[str]
    status: str = "registered"  # registered, connected, disconnected, error
    last_seen: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "app_id": self.app_id,
            "name": self.name,
            "platform": self.platform.value,
            "integration_type": self.integration_type.value,
            "connection_info": self.connection_info,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_seen": self.last_seen,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NativeAppRegistration':
        """Create from dictionary representation."""
        return cls(
            app_id=data["app_id"],
            name=data["name"],
            platform=PlatformType(data["platform"]),
            integration_type=IntegrationType(data["integration_type"]),
            connection_info=data["connection_info"],
            capabilities=data["capabilities"],
            status=data.get("status", "registered"),
            last_seen=data.get("last_seen", time.time()),
            metadata=data.get("metadata", {})
        )


class NativeAdapter:
    """
    Base class for native application adapters.
    """
    def __init__(
        self,
        adapter_id: str,
        integration_type: IntegrationType,
        config: Dict[str, Any] = None
    ):
        self.adapter_id = adapter_id
        self.integration_type = integration_type
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.NativeAdapter.{self.adapter_id[:8]}")
    
    async def initialize(self) -> bool:
        """Initialize the adapter."""
        self.logger.info(f"Initializing {self.integration_type.value} adapter")
        return True
    
    async def shutdown(self) -> None:
        """Shutdown the adapter."""
        self.logger.info(f"Shutting down {self.integration_type.value} adapter")
    
    async def send_to_native(self, app_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to a native application."""
        raise NotImplementedError("Subclasses must implement send_to_native()")
    
    async def receive_from_native(self, app_id: str, native_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message received from a native application."""
        raise NotImplementedError("Subclasses must implement receive_from_native()")


class RestApiAdapter(NativeAdapter):
    """
    Adapter for REST API integration with native applications.
    """
    def __init__(self, adapter_id: str, config: Dict[str, Any] = None):
        super().__init__(adapter_id, IntegrationType.REST_API, config)
        self.http_client = None  # Would be initialized with aiohttp or similar
    
    async def initialize(self) -> bool:
        """Initialize the REST API adapter."""
        await super().initialize()
        # In a real implementation, would initialize HTTP client here
        # self.http_client = aiohttp.ClientSession()
        return True
    
    async def shutdown(self) -> None:
        """Shutdown the REST API adapter."""
        # In a real implementation, would close HTTP client here
        # await self.http_client.close()
        await super().shutdown()
    
    async def send_to_native(self, app_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to a native application via REST API."""
        # In a real implementation, would make HTTP request to app's endpoint
        self.logger.debug(f"Sending message to native app {app_id} via REST API")
        
        # Simulate HTTP request
        # Actual implementation would use self.http_client.post() or similar
        try:
            # Simulated response
            response = {
                "status": "success",
                "message_id": message.get("message_id", "unknown"),
                "timestamp": time.time()
            }
            return response
        except Exception as e:
            self.logger.error(f"Error sending message to native app {app_id}: {e}")
            return None
    
    async def receive_from_native(self, app_id: str, native_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message received from a native application via REST API."""
        self.logger.debug(f"Received message from native app {app_id} via REST API")
        
        # Convert native message format to protocol message format
        try:
            # Extract message content
            content = native_message.get("content", {})
            message_type = native_message.get("type", "command")
            
            # Create protocol message
            if message_type == "command":
                protocol_message = MessageFactory.create_command(
                    command=content.get("command", "unknown"),
                    params=content.get("params", {}),
                    sender_id=f"native:{app_id}",
                    receiver_id=content.get("target", "protocol_bridge")
                )
            elif message_type == "query":
                protocol_message = MessageFactory.create_query(
                    query=content.get("query", "unknown"),
                    params=content.get("params", {}),
                    sender_id=f"native:{app_id}",
                    receiver_id=content.get("target", "protocol_bridge")
                )
            elif message_type == "event":
                protocol_message = MessageFactory.create_event(
                    event_type=content.get("event_type", "unknown"),
                    payload=content.get("payload", {}),
                    sender_id=f"native:{app_id}",
                    metadata=content.get("metadata", {})
                )
            else:
                self.logger.warning(f"Unknown message type from native app {app_id}: {message_type}")
                return None
            
            return protocol_message.to_dict()
        except Exception as e:
            self.logger.error(f"Error processing message from native app {app_id}: {e}")
            return None


class WebSocketAdapter(NativeAdapter):
    """
    Adapter for WebSocket integration with native applications.
    """
    def __init__(self, adapter_id: str, config: Dict[str, Any] = None):
        super().__init__(adapter_id, IntegrationType.WEBSOCKET, config)
        self.active_connections: Dict[str, Any] = {}  # app_id -> connection
    
    async def initialize(self) -> bool:
        """Initialize the WebSocket adapter."""
        await super().initialize()
        # In a real implementation, would initialize WebSocket server here
        return True
    
    async def shutdown(self) -> None:
        """Shutdown the WebSocket adapter."""
        # In a real implementation, would close all WebSocket connections
        for app_id, connection in self.active_connections.items():
            self.logger.info(f"Closing WebSocket connection for app {app_id}")
            # await connection.close()
        
        self.active_connections.clear()
        await super().shutdown()
    
    async def send_to_native(self, app_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to a native application via WebSocket."""
        if app_id not in self.active_connections:
            self.logger.warning(f"No active WebSocket connection for app {app_id}")
            return None
        
        # In a real implementation, would send message over WebSocket
        self.logger.debug(f"Sending message to native app {app_id} via WebSocket")
        
        # Simulate WebSocket send
        try:
            # connection = self.active_connections[app_id]
            # await connection.send_json(message)
            
            # WebSocket is typically fire-and-forget, so no response
            return {
                "status": "sent",
                "message_id": message.get("message_id", "unknown"),
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.error(f"Error sending message to native app {app_id} via WebSocket: {e}")
            return None
    
    async def receive_from_native(self, app_id: str, native_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message received from a native application via WebSocket."""
        self.logger.debug(f"Received message from native app {app_id} via WebSocket")
        
        # Convert native message format to protocol message format
        try:
            # Extract message content
            message_type = native_message.get("type", "command")
            content = native_message.get("content", {})
            
            # Create protocol message (similar to REST adapter)
            if message_type == "command":
                protocol_message = MessageFactory.create_command(
                    command=content.get("command", "unknown"),
                    params=content.get("params", {}),
                    sender_id=f"native:{app_id}",
                    receiver_id=content.get("target", "protocol_bridge")
                )
            elif message_type == "query":
                protocol_message = MessageFactory.create_query(
                    query=content.get("query", "unknown"),
                    params=content.get("params", {}),
                    sender_id=f"native:{app_id}",
                    receiver_id=content.get("target", "protocol_bridge")
                )
            elif message_type == "event":
                protocol_message = MessageFactory.create_event(
                    event_type=content.get("event_type", "unknown"),
                    payload=content.get("payload", {}),
                    sender_id=f"native:{app_id}",
                    metadata=content.get("metadata", {})
                )
            else:
                self.logger.warning(f"Unknown message type from native app {app_id}: {message_type}")
                return None
            
            return protocol_message.to_dict()
        except Exception as e:
            self.logger.error(f"Error processing message from native app {app_id}: {e}")
            return None


class GrpcAdapter(NativeAdapter):
    """
    Adapter for gRPC integration with native applications.
    """
    def __init__(self, adapter_id: str, config: Dict[str, Any] = None):
        super().__init__(adapter_id, IntegrationType.GRPC, config)
        # Would initialize gRPC server and client here
    
    async def initialize(self) -> bool:
        """Initialize the gRPC adapter."""
        await super().initialize()
        # In a real implementation, would initialize gRPC server here
        return True
    
    async def shutdown(self) -> None:
        """Shutdown the gRPC adapter."""
        # In a real implementation, would shutdown gRPC server here
        await super().shutdown()
    
    async def send_to_native(self, app_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to a native application via gRPC."""
        # In a real implementation, would make gRPC call to app's service
        self.logger.debug(f"Sending message to native app {app_id} via gRPC")
        
        # Simulate gRPC call
        try:
            # Simulated response
            response = {
                "status": "success",
                "message_id": message.get("message_id", "unknown"),
                "timestamp": time.time()
            }
            return response
        except Exception as e:
            self.logger.error(f"Error sending message to native app {app_id} via gRPC: {e}")
            return None
    
    async def receive_from_native(self, app_id: str, native_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message received from a native application via gRPC."""
        self.logger.debug(f"Received message from native app {app_id} via gRPC")
        
        # Convert native message format to protocol message format
        # Similar to other adapters, but with gRPC-specific handling
        try:
            # Extract message content
            message_type = native_message.get("type", "command")
            content = native_message.get("content", {})
            
            # Create protocol message (similar to other adapters)
            if message_type == "command":
                protocol_message = MessageFactory.create_command(
                    command=content.get("command", "unknown"),
                    params=content.get("params", {}),
                    sender_id=f"native:{app_id}",
                    receiver_id=content.get("target", "protocol_bridge")
                )
            elif message_type == "query":
                protocol_message = MessageFactory.create_query(
                    query=content.get("query", "unknown"),
                    params=content.get("params", {}),
                    sender_id=f"native:{app_id}",
                    receiver_id=content.get("target", "protocol_bridge")
                )
            elif message_type == "event":
                protocol_message = MessageFactory.create_event(
                    event_type=content.get("event_type", "unknown"),
                    payload=content.get("payload", {}),
                    sender_id=f"native:{app_id}",
                    metadata=content.get("metadata", {})
                )
            else:
                self.logger.warning(f"Unknown message type from native app {app_id}: {message_type}")
                return None
            
            return protocol_message.to_dict()
        except Exception as e:
            self.logger.error(f"Error processing message from native app {app_id}: {e}")
            return None


class MessageQueueAdapter(NativeAdapter):
    """
    Adapter for message queue integration with native applications.
    """
    def __init__(self, adapter_id: str, config: Dict[str, Any] = None):
        super().__init__(adapter_id, IntegrationType.MESSAGE_QUEUE, config)
        # Would initialize message queue client here
    
    async def initialize(self) -> bool:
        """Initialize the message queue adapter."""
        await super().initialize()
        # In a real implementation, would connect to message queue here
        return True
    
    async def shutdown(self) -> None:
        """Shutdown the message queue adapter."""
        # In a real implementation, would disconnect from message queue here
        await super().shutdown()
    
    async def send_to_native(self, app_id: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to a native application via message queue."""
        # In a real implementation, would publish message to app's queue
        self.logger.debug(f"Sending message to native app {app_id} via message queue")
        
        # Simulate message queue publish
        try:
            # Simulated response (message queues typically don't provide immediate responses)
            return {
                "status": "published",
                "message_id": message.get("message_id", "unknown"),
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.error(f"Error sending message to native app {app_id} via message queue: {e}")
            return None
    
    async def receive_from_native(self, app_id: str, native_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message received from a native application via message queue."""
        self.logger.debug(f"Received message from native app {app_id} via message queue")
        
        # Convert native message format to protocol message format
        # Similar to other adapters, but with message queue-specific handling
        try:
            # Extract message content
            message_type = native_message.get("type", "command")
            content = native_message.get("content", {})
            
            # Create protocol message (similar to other adapters)
            if message_type == "command":
                protocol_message = MessageFactory.create_command(
                    command=content.get("command", "unknown"),
                    params=content.get("params", {}),
                    sender_id=f"native:{app_id}",
                    receiver_id=content.get("target", "protocol_bridge")
                )
            elif message_type == "query":
                protocol_message = MessageFactory.create_query(
                    query=content.get("query", "unknown"),
                    params=content.get("params", {}),
                    sender_id=f"native:{app_id}",
                    receiver_id=content.get("target", "protocol_bridge")
                )
            elif message_type == "event":
                protocol_message = MessageFactory.create_event(
                    event_type=content.get("event_type", "unknown"),
                    payload=content.get("payload", {}),
                    sender_id=f"native:{app_id}",
                    metadata=content.get("metadata", {})
                )
            else:
                self.logger.warning(f"Unknown message type from native app {app_id}: {message_type}")
                return None
            
            return protocol_message.to_dict()
        except Exception as e:
            self.logger.error(f"Error processing message from native app {app_id}: {e}")
            return None


class ProtocolNativeBridge(ProtocolService):
    """
    Bridge service for connecting protocol-native components with traditional native applications.
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "protocol_native_bridge")
        self.config = config or {}
        
        # Initialize native app registrations
        self.native_apps: Dict[str, NativeAppRegistration] = {}
        
        # Initialize adapters
        self.adapters: Dict[IntegrationType, NativeAdapter] = {}
        
        # State
        self.is_async = True
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"{__name__}.ProtocolNativeBridge.{self.component_id[:8]}")
        self.logger.info(f"Protocol-to-Native App Bridge initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("native_app_integration", "Integrate with native applications")
        self.add_capability("protocol_translation", "Translate between protocol and native formats")
        self.add_capability("bidirectional_communication", "Enable bidirectional communication")
        self.add_capability("event_synchronization", "Synchronize events between protocol and native worlds")

    async def initialize(self) -> bool:
        """Initialize the bridge service."""
        self.logger.info("Initializing Protocol-to-Native App Bridge")
        
        # Initialize adapters based on configuration
        adapter_configs = self.config.get("adapters", {})
        
        # REST API adapter
        if adapter_configs.get("rest_api", {}).get("enabled", True):
            rest_config = adapter_configs.get("rest_api", {})
            rest_adapter = RestApiAdapter(f"{self.component_id}_rest", rest_config)
            if await rest_adapter.initialize():
                self.adapters[IntegrationType.REST_API] = rest_adapter
        
        # WebSocket adapter
        if adapter_configs.get("websocket", {}).get("enabled", True):
            ws_config = adapter_configs.get("websocket", {})
            ws_adapter = WebSocketAdapter(f"{self.component_id}_ws", ws_config)
            if await ws_adapter.initialize():
                self.adapters[IntegrationType.WEBSOCKET] = ws_adapter
        
        # gRPC adapter
        if adapter_configs.get("grpc", {}).get("enabled", False):
            grpc_config = adapter_configs.get("grpc", {})
            grpc_adapter = GrpcAdapter(f"{self.component_id}_grpc", grpc_config)
            if await grpc_adapter.initialize():
                self.adapters[IntegrationType.GRPC] = grpc_adapter
        
        # Message Queue adapter
        if adapter_configs.get("message_queue", {}).get("enabled", False):
            mq_config = adapter_configs.get("message_queue", {})
            mq_adapter = MessageQueueAdapter(f"{self.component_id}_mq", mq_config)
            if await mq_adapter.initialize():
                self.adapters[IntegrationType.MESSAGE_QUEUE] = mq_adapter
        
        # Load initial app registrations if any
        initial_apps = self.config.get("initial_apps", [])
        for app_data in initial_apps:
            await self.register_native_app(app_data)
        
        self.logger.info(f"Protocol-to-Native App Bridge initialized with {len(self.adapters)} adapters")
        return True

    async def shutdown(self) -> None:
        """Shutdown the bridge service."""
        self.logger.info("Shutting down Protocol-to-Native App Bridge")
        
        # Shutdown all adapters
        for adapter_type, adapter in self.adapters.items():
            self.logger.info(f"Shutting down {adapter_type.value} adapter")
            await adapter.shutdown()
        
        self.adapters.clear()
        self.logger.info("Protocol-to-Native App Bridge shutdown complete")

    # --- Native App Management ---

    async def register_native_app(self, app_data: Dict[str, Any]) -> str:
        """Register a native application."""
        app_id = app_data.get("app_id", str(uuid.uuid4()))
        
        async with self.lock:
            if app_id in self.native_apps:
                self.logger.warning(f"Native app {app_id} already registered, updating registration")
            
            # Create registration
            registration = NativeAppRegistration(
                app_id=app_id,
                name=app_data.get("name", f"App-{app_id[:8]}"),
                platform=PlatformType(app_data.get("platform", "custom")),
                integration_type=IntegrationType(app_data.get("integration_type", "rest_api")),
                connection_info=app_data.get("connection_info", {}),
                capabilities=app_data.get("capabilities", []),
                metadata=app_data.get("metadata", {})
            )
            
            self.native_apps[app_id] = registration
            self.logger.info(f"Registered native app {app_id} ({registration.name}) using {registration.integration_type.value}")
        
        # Publish registration event
        await self._publish_bridge_event("app_registered", {
            "app_id": app_id,
            "name": registration.name,
            "platform": registration.platform.value,
            "integration_type": registration.integration_type.value
        })
        
        return app_id

    async def unregister_native_app(self, app_id: str) -> bool:
        """Unregister a native application."""
        async with self.lock:
            if app_id not in self.native_apps:
                self.logger.warning(f"Native app {app_id} not found for unregistration")
                return False
            
            app = self.native_apps.pop(app_id)
            self.logger.info(f"Unregistered native app {app_id} ({app.name})")
        
        # Publish unregistration event
        await self._publish_bridge_event("app_unregistered", {
            "app_id": app_id,
            "name": app.name
        })
        
        return True

    async def update_native_app_status(self, app_id: str, status: str, details: Dict[str, Any] = None) -> bool:
        """Update the status of a native application."""
        details = details or {}
        
        async with self.lock:
            if app_id not in self.native_apps:
                self.logger.warning(f"Native app {app_id} not found for status update")
                return False
            
            app = self.native_apps[app_id]
            old_status = app.status
            app.status = status
            app.last_seen = time.time()
            
            if details:
                app.metadata.update(details)
            
            self.logger.debug(f"Updated native app {app_id} status from {old_status} to {status}")
        
        # Publish status change event if significant
        if old_status != status:
            await self._publish_bridge_event("app_status_changed", {
                "app_id": app_id,
                "old_status": old_status,
                "new_status": status,
                "details": details
            })
        
        return True

    async def get_native_app(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get a native application by ID."""
        async with self.lock:
            if app_id not in self.native_apps:
                self.logger.error(f"Native app {app_id} not found")
                return None
            
            return self.native_apps[app_id].to_dict()

    async def list_native_apps(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List native applications with optional filtering."""
        filters = filters or {}
        
        async with self.lock:
            apps = list(self.native_apps.values())
        
        # Apply filters
        if "platform" in filters:
            platform = PlatformType(filters["platform"])
            apps = [app for app in apps if app.platform == platform]
        
        if "integration_type" in filters:
            integration_type = IntegrationType(filters["integration_type"])
            apps = [app for app in apps if app.integration_type == integration_type]
        
        if "status" in filters:
            status = filters["status"]
            apps = [app for app in apps if app.status == status]
        
        if "capability" in filters:
            capability = filters["capability"]
            apps = [app for app in apps if capability in app.capabilities]
        
        # Convert to dict representation
        return [app.to_dict() for app in apps]

    # --- Message Handling ---

    async def send_to_native_app(self, app_id: str, protocol_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a protocol message to a native application."""
        async with self.lock:
            if app_id not in self.native_apps:
                self.logger.error(f"Native app {app_id} not found")
                return None
            
            app = self.native_apps[app_id]
            integration_type = app.integration_type
            
            if integration_type not in self.adapters:
                self.logger.error(f"No adapter available for integration type {integration_type.value}")
                return None
        
        # Convert protocol message to native format
        native_message = await self._protocol_to_native(protocol_message, app)
        
        # Send via appropriate adapter
        adapter = self.adapters[integration_type]
        response = await adapter.send_to_native(app_id, native_message)
        
        # Update app status based on response
        if response:
            await self.update_native_app_status(app_id, "connected")
        else:
            await self.update_native_app_status(app_id, "error", {"error": "Failed to send message"})
        
        return response

    async def receive_from_native_app(self, app_id: str, native_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message received from a native application."""
        async with self.lock:
            if app_id not in self.native_apps:
                self.logger.error(f"Native app {app_id} not found")
                return None
            
            app = self.native_apps[app_id]
            integration_type = app.integration_type
            
            if integration_type not in self.adapters:
                self.logger.error(f"No adapter available for integration type {integration_type.value}")
                return None
        
        # Process via appropriate adapter
        adapter = self.adapters[integration_type]
        protocol_message = await adapter.receive_from_native(app_id, native_message)
        
        # Update app status
        await self.update_native_app_status(app_id, "connected")
        
        return protocol_message

    async def _protocol_to_native(self, protocol_message: Dict[str, Any], app: NativeAppRegistration) -> Dict[str, Any]:
        """Convert a protocol message to native format."""
        # Create a message object for easier handling
        msg_obj = MessageFactory.create_from_dict(protocol_message)
        if not msg_obj:
            self.logger.error("Invalid protocol message")
            return {"error": "Invalid protocol message"}
        
        # Basic native message structure
        native_message = {
            "id": msg_obj.message_id,
            "timestamp": time.time(),
            "source": msg_obj.sender_id
        }
        
        # Convert based on message type
        if isinstance(msg_obj, CommandMessage):
            native_message["type"] = "command"
            native_message["content"] = {
                "command": msg_obj.command,
                "params": msg_obj.params
            }
        
        elif isinstance(msg_obj, QueryMessage):
            native_message["type"] = "query"
            native_message["content"] = {
                "query": msg_obj.query,
                "params": msg_obj.params
            }
        
        elif isinstance(msg_obj, EventMessage):
            native_message["type"] = "event"
            native_message["content"] = {
                "event_type": msg_obj.event_type,
                "payload": msg_obj.payload
            }
        
        elif isinstance(msg_obj, ResponseMessage):
            native_message["type"] = "response"
            native_message["content"] = {
                "correlation_id": msg_obj.correlation_id,
                "status": msg_obj.status.value,
                "payload": msg_obj.payload
            }
        
        else:
            native_message["type"] = "unknown"
            native_message["content"] = protocol_message
        
        # Add platform-specific formatting if needed
        if app.platform == PlatformType.WEB:
            # Web apps typically use JSON directly
            pass
        elif app.platform in (PlatformType.MOBILE_ANDROID, PlatformType.MOBILE_IOS):
            # Mobile apps might need additional metadata
            native_message["mobile_metadata"] = {
                "notification": msg_obj.metadata.get("notification", False),
                "priority": msg_obj.priority.value if hasattr(msg_obj, "priority") else "normal"
            }
        
        return native_message

    async def _native_to_protocol(self, native_message: Dict[str, Any], app_id: str) -> Optional[Dict[str, Any]]:
        """Convert a native message to protocol format."""
        # This is handled by the specific adapters in receive_from_native
        # This method is a placeholder for any common processing
        return None

    # --- Event Publishing ---

    async def _publish_bridge_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Publish a bridge-related event."""
        data = data or {}
        
        # Create event message
        event = {
            "event_type": f"bridge.{event_type}",
            "timestamp": time.time(),
            "data": data
        }
        
        # In a real implementation, this would publish to an event bus or message broker
        self.logger.debug(f"Published bridge event: {event_type}")

    # --- ProtocolService Methods ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "register_native_app":
                app_id = await self.register_native_app(msg_obj.params)
                response_payload = {"app_id": app_id}
            
            elif msg_obj.command == "unregister_native_app":
                params = msg_obj.params
                if "app_id" in params:
                    success = await self.unregister_native_app(params["app_id"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id"}
            
            elif msg_obj.command == "update_native_app_status":
                params = msg_obj.params
                if "app_id" in params and "status" in params:
                    success = await self.update_native_app_status(
                        params["app_id"],
                        params["status"],
                        params.get("details")
                    )
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or status"}
            
            elif msg_obj.command == "send_to_native_app":
                params = msg_obj.params
                if "app_id" in params and "message" in params:
                    response = await self.send_to_native_app(params["app_id"], params["message"])
                    if response:
                        response_payload = response
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Failed to send message to native app"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or message"}
            
            elif msg_obj.command == "receive_from_native_app":
                params = msg_obj.params
                if "app_id" in params and "native_message" in params:
                    protocol_message = await self.receive_from_native_app(
                        params["app_id"],
                        params["native_message"]
                    )
                    if protocol_message:
                        response_payload = {"protocol_message": protocol_message}
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Failed to process native message"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or native_message"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_native_app":
                params = msg_obj.params
                if "app_id" in params:
                    app = await self.get_native_app(params["app_id"])
                    if app:
                        response_payload = app
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Native app not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id"}
            
            elif msg_obj.query == "list_native_apps":
                apps = await self.list_native_apps(msg_obj.params.get("filters"))
                response_payload = {"apps": apps}
            
            elif msg_obj.query == "get_supported_integration_types":
                response_payload = {
                    "integration_types": [it.value for it in IntegrationType],
                    "available_adapters": [it.value for it in self.adapters.keys()]
                }
            
            elif msg_obj.query == "get_supported_platforms":
                response_payload = {
                    "platforms": [pt.value for pt in PlatformType]
                }
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        else:
            # Forward message to native app if it's addressed to one
            receiver_id = msg_obj.receiver_id
            if receiver_id and receiver_id.startswith("native:"):
                app_id = receiver_id.split(":", 1)[1]
                response = await self.send_to_native_app(app_id, message)
                if response:
                    return response
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": f"Failed to forward message to native app {app_id}"}
            else:
                # Ignore other message types
                return None

        # Create response
        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message (synchronous wrapper)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check."""
        async with self.lock:
            num_apps = len(self.native_apps)
            num_connected = sum(1 for app in self.native_apps.values() if app.status == "connected")
            num_error = sum(1 for app in self.native_apps.values() if app.status == "error")
            num_adapters = len(self.adapters)
        
        return {
            "status": "healthy" if num_error == 0 else "degraded",
            "native_apps": {
                "total": num_apps,
                "connected": num_connected,
                "error": num_error
            },
            "adapters": {
                "total": num_adapters,
                "types": [adapter_type.value for adapter_type in self.adapters.keys()]
            }
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
