"""
Protocol Bridge - Enables protocol-native communication between UI/UX Layer and other layers

This module implements the core functionality for bridging between the UI/UX Layer
and other layers of the Industrial Foundry Framework using protocol-native communication.
It serves as the central integration point for MCP/A2A protocols and ensures seamless
interaction between layers.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable

# Initialize logger
logger = logging.getLogger(__name__)

class ProtocolBridge:
    """
    Bridges between UI/UX Layer and other layers using protocol-native communication.
    """
    
    # Protocol constants
    PROTOCOL_MCP = "mcp"
    PROTOCOL_A2A = "a2a"
    
    # Message type constants
    MESSAGE_TYPE_REQUEST = "request"
    MESSAGE_TYPE_RESPONSE = "response"
    MESSAGE_TYPE_EVENT = "event"
    MESSAGE_TYPE_COMMAND = "command"
    MESSAGE_TYPE_QUERY = "query"
    MESSAGE_TYPE_NOTIFICATION = "notification"
    
    # Layer constants
    LAYER_DATA = "data_layer"
    LAYER_CORE_AI = "core_ai_layer"
    LAYER_GENERATIVE = "generative_layer"
    LAYER_APPLICATION = "application_layer"
    LAYER_PROTOCOL = "protocol_layer"
    LAYER_WORKFLOW = "workflow_layer"
    LAYER_UI_UX = "ui_ux_layer"
    LAYER_SECURITY = "security_layer"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Protocol Bridge with optional configuration."""
        self.config = config or {}
        self.protocol_handlers = {}
        self.layer_endpoints = {}
        self.message_handlers = {}
        self.event_subscribers = {}
        self.active_connections = {}
        self.message_queue = {}
        
        logger.info("Protocol Bridge initialized with config: %s", self.config)
    
    def initialize(self):
        """Initialize the Protocol Bridge and all its components."""
        logger.info("Initializing Protocol Bridge components")
        
        # Import dependencies here to avoid circular imports
        from .mcp_protocol_handler import MCPProtocolHandler
        from .a2a_protocol_handler import A2AProtocolHandler
        from .message_router import MessageRouter
        from .connection_manager import ConnectionManager
        from .protocol_event_bus import ProtocolEventBus
        
        # Initialize components
        self.mcp_handler = MCPProtocolHandler(self.config.get('mcp_handler', {}))
        self.a2a_handler = A2AProtocolHandler(self.config.get('a2a_handler', {}))
        self.message_router = MessageRouter(self.config.get('message_router', {}))
        self.connection_manager = ConnectionManager(self.config.get('connection_manager', {}))
        self.event_bus = ProtocolEventBus(self.config.get('event_bus', {}))
        
        # Initialize each component
        self.mcp_handler.initialize()
        self.a2a_handler.initialize()
        self.message_router.initialize()
        self.connection_manager.initialize()
        self.event_bus.initialize()
        
        # Register protocol handlers
        self.protocol_handlers[self.PROTOCOL_MCP] = self.mcp_handler
        self.protocol_handlers[self.PROTOCOL_A2A] = self.a2a_handler
        
        # Register default layer endpoints
        self._register_default_layer_endpoints()
        
        # Subscribe to event bus
        self.event_bus.subscribe('message_received', self._handle_message_received)
        self.event_bus.subscribe('message_sent', self._handle_message_sent)
        self.event_bus.subscribe('connection_established', self._handle_connection_established)
        self.event_bus.subscribe('connection_closed', self._handle_connection_closed)
        
        logger.info("Protocol Bridge initialization complete")
        return True
    
    def _register_default_layer_endpoints(self):
        """Register default layer endpoints."""
        default_endpoints = self.config.get('default_layer_endpoints', {})
        
        for layer, endpoint_config in default_endpoints.items():
            self.register_layer_endpoint(layer, endpoint_config)
        
        logger.info("Registered %d default layer endpoints", len(default_endpoints))
    
    def register_layer_endpoint(self, layer: str, endpoint_config: Dict[str, Any]) -> bool:
        """
        Register an endpoint for a specific layer.
        
        Args:
            layer: Layer identifier
            endpoint_config: Endpoint configuration
                - url: URL of the endpoint
                - protocol: Protocol to use for communication
                - auth: Authentication information
                - options: Additional options
        
        Returns:
            bool: True if registration was successful, False otherwise
        """
        logger.info("Registering endpoint for layer: %s", layer)
        
        # Register with connection manager
        if self.connection_manager:
            success = self.connection_manager.register_endpoint(layer, endpoint_config)
            if success:
                self.layer_endpoints[layer] = endpoint_config
            return success
        
        # Simple endpoint storage if connection manager not available
        self.layer_endpoints[layer] = endpoint_config
        return True
    
    def unregister_layer_endpoint(self, layer: str) -> bool:
        """
        Unregister an endpoint for a specific layer.
        
        Args:
            layer: Layer identifier
        
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        logger.info("Unregistering endpoint for layer: %s", layer)
        
        # Unregister from connection manager
        if self.connection_manager:
            success = self.connection_manager.unregister_endpoint(layer)
            if success and layer in self.layer_endpoints:
                del self.layer_endpoints[layer]
            return success
        
        # Simple endpoint removal if connection manager not available
        if layer in self.layer_endpoints:
            del self.layer_endpoints[layer]
            return True
        
        logger.warning("Endpoint not found for layer: %s", layer)
        return False
    
    def send_message(self, message: Dict[str, Any]) -> str:
        """
        Send a message to a specific layer.
        
        Args:
            message: Message to send
                - id: Unique identifier for the message (optional, will be generated if not provided)
                - protocol: Protocol to use for sending the message
                - type: Type of message
                - source: Source layer or component
                - target: Target layer or component
                - payload: Message payload
                - metadata: Additional metadata
        
        Returns:
            str: Message ID
        """
        # Generate message ID if not provided
        message_id = message.get('id')
        if not message_id:
            message_id = self._generate_message_id(message)
            message['id'] = message_id
        
        logger.info("Sending message: %s to %s using %s protocol", 
                   message_id, message.get('target'), message.get('protocol'))
        
        # Set timestamp if not provided
        if 'timestamp' not in message:
            message['timestamp'] = self._get_current_timestamp()
        
        # Get protocol handler
        protocol = message.get('protocol', self.PROTOCOL_MCP)
        handler = self.protocol_handlers.get(protocol)
        
        if not handler:
            logger.warning("No handler found for protocol: %s", protocol)
            return ""
        
        # Route message
        if self.message_router:
            routed_message = self.message_router.route_message(message)
            if not routed_message:
                logger.warning("Message routing failed: %s", message_id)
                return ""
            message = routed_message
        
        # Get target layer
        target = message.get('target')
        if not target:
            logger.warning("No target specified for message: %s", message_id)
            return ""
        
        # Check if target layer endpoint is registered
        if target not in self.layer_endpoints and not self.connection_manager:
            logger.warning("No endpoint registered for layer: %s", target)
            return ""
        
        try:
            # Send message using protocol handler
            result = handler.send_message(message)
            
            if not result:
                logger.warning("Failed to send message: %s", message_id)
                return ""
            
            # Publish event
            self.event_bus.publish('message_sent', {
                'message_id': message_id,
                'message': message
            })
            
            # Notify subscribers
            self._notify_subscribers('message_sent', {
                'message_id': message_id,
                'message': message
            })
            
            logger.info("Message sent: %s", message_id)
            return message_id
        
        except Exception as e:
            logger.error("Error sending message: %s", e)
            return ""
    
    def receive_message(self, message: Dict[str, Any]) -> bool:
        """
        Receive a message from another layer.
        
        Args:
            message: Received message
        
        Returns:
            bool: True if message was processed successfully, False otherwise
        """
        message_id = message.get('id')
        if not message_id:
            message_id = self._generate_message_id(message)
            message['id'] = message_id
        
        logger.info("Received message: %s from %s using %s protocol", 
                   message_id, message.get('source'), message.get('protocol'))
        
        # Set timestamp if not provided
        if 'timestamp' not in message:
            message['timestamp'] = self._get_current_timestamp()
        
        # Get protocol handler
        protocol = message.get('protocol', self.PROTOCOL_MCP)
        handler = self.protocol_handlers.get(protocol)
        
        if not handler:
            logger.warning("No handler found for protocol: %s", protocol)
            return False
        
        try:
            # Process message using protocol handler
            processed_message = handler.process_message(message)
            
            if not processed_message:
                logger.warning("Failed to process message: %s", message_id)
                return False
            
            # Route message
            if self.message_router:
                routed_message = self.message_router.route_message(processed_message)
                if not routed_message:
                    logger.warning("Message routing failed: %s", message_id)
                    return False
                processed_message = routed_message
            
            # Get message type and target
            message_type = processed_message.get('type')
            target = processed_message.get('target')
            
            # Handle message based on type
            if message_type in self.message_handlers:
                for handler_func in self.message_handlers[message_type]:
                    try:
                        handler_func(processed_message)
                    except Exception as e:
                        logger.error("Error in message handler: %s", e)
            
            # Publish event
            self.event_bus.publish('message_received', {
                'message_id': message_id,
                'message': processed_message
            })
            
            # Notify subscribers
            self._notify_subscribers('message_received', {
                'message_id': message_id,
                'message': processed_message
            })
            
            logger.info("Message processed: %s", message_id)
            return True
        
        except Exception as e:
            logger.error("Error receiving message: %s", e)
            return False
    
    def register_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Handler function
        
        Returns:
            bool: True if registration was successful, False otherwise
        """
        logger.info("Registering handler for message type: %s", message_type)
        
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        
        self.message_handlers[message_type].append(handler)
        return True
    
    def unregister_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unregister a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Handler function
        
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        logger.info("Unregistering handler for message type: %s", message_type)
        
        if message_type in self.message_handlers and handler in self.message_handlers[message_type]:
            self.message_handlers[message_type].remove(handler)
            return True
        
        logger.warning("Handler not found for message type: %s", message_type)
        return False
    
    def connect_to_layer(self, layer: str) -> bool:
        """
        Establish a connection to a specific layer.
        
        Args:
            layer: Layer to connect to
        
        Returns:
            bool: True if connection was established successfully, False otherwise
        """
        logger.info("Connecting to layer: %s", layer)
        
        if layer not in self.layer_endpoints:
            logger.warning("No endpoint registered for layer: %s", layer)
            return False
        
        # Connect using connection manager
        if self.connection_manager:
            return self.connection_manager.connect(layer)
        
        # Simple connection tracking if connection manager not available
        self.active_connections[layer] = {
            'status': 'connected',
            'timestamp': self._get_current_timestamp()
        }
        
        # Publish event
        self.event_bus.publish('connection_established', {
            'layer': layer,
            'endpoint': self.layer_endpoints[layer]
        })
        
        # Notify subscribers
        self._notify_subscribers('connection_established', {
            'layer': layer,
            'endpoint': self.layer_endpoints[layer]
        })
        
        logger.info("Connected to layer: %s", layer)
        return True
    
    def disconnect_from_layer(self, layer: str) -> bool:
        """
        Close a connection to a specific layer.
        
        Args:
            layer: Layer to disconnect from
        
        Returns:
            bool: True if disconnection was successful, False otherwise
        """
        logger.info("Disconnecting from layer: %s", layer)
        
        # Disconnect using connection manager
        if self.connection_manager:
            return self.connection_manager.disconnect(layer)
        
        # Simple connection tracking if connection manager not available
        if layer in self.active_connections:
            self.active_connections[layer] = {
                'status': 'disconnected',
                'timestamp': self._get_current_timestamp()
            }
            
            # Publish event
            self.event_bus.publish('connection_closed', {
                'layer': layer
            })
            
            # Notify subscribers
            self._notify_subscribers('connection_closed', {
                'layer': layer
            })
            
            logger.info("Disconnected from layer: %s", layer)
            return True
        
        logger.warning("No active connection for layer: %s", layer)
        return False
    
    def get_connection_status(self, layer: str) -> str:
        """
        Get the connection status for a specific layer.
        
        Args:
            layer: Layer to get status for
        
        Returns:
            str: Connection status
        """
        # Get status from connection manager
        if self.connection_manager:
            return self.connection_manager.get_status(layer)
        
        # Simple status lookup if connection manager not available
        if layer in self.active_connections:
            return self.active_connections[layer].get('status', 'unknown')
        
        return 'unknown'
    
    def subscribe_to_events(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to protocol bridge events.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Callback function to be called when event occurs
        
        Returns:
            bool: True if subscription was successful, False otherwise
        """
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        
        self.event_subscribers[event_type].append(callback)
        return True
    
    def unsubscribe_from_events(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unsubscribe from protocol bridge events.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to be removed
        
        Returns:
            bool: True if unsubscription was successful, False otherwise
        """
        if event_type in self.event_subscribers and callback in self.event_subscribers[event_type]:
            self.event_subscribers[event_type].remove(callback)
            return True
        
        return False
    
    def _handle_message_received(self, event_data: Dict[str, Any]):
        """
        Handle message received event.
        
        Args:
            event_data: Event data
        """
        message_id = event_data.get('message_id')
        message = event_data.get('message', {})
        
        logger.debug("Handling message received event: %s", message_id)
        
        # Notify subscribers
        self._notify_subscribers('message_received', event_data)
    
    def _handle_message_sent(self, event_data: Dict[str, Any]):
        """
        Handle message sent event.
        
        Args:
            event_data: Event data
        """
        message_id = event_data.get('message_id')
        message = event_data.get('message', {})
        
        logger.debug("Handling message sent event: %s", message_id)
        
        # Notify subscribers
        self._notify_subscribers('message_sent', event_data)
    
    def _handle_connection_established(self, event_data: Dict[str, Any]):
        """
        Handle connection established event.
        
        Args:
            event_data: Event data
        """
        layer = event_data.get('layer')
        
        logger.debug("Handling connection established event for layer: %s", layer)
        
        # Update connection status
        if layer not in self.active_connections:
            self.active_connections[layer] = {}
        
        self.active_connections[layer]['status'] = 'connected'
        self.active_connections[layer]['timestamp'] = self._get_current_timestamp()
        
        # Notify subscribers
        self._notify_subscribers('connection_established', event_data)
    
    def _handle_connection_closed(self, event_data: Dict[str, Any]):
        """
        Handle connection closed event.
        
        Args:
            event_data: Event data
        """
        layer = event_data.get('layer')
        
        logger.debug("Handling connection closed event for layer: %s", layer)
        
        # Update connection status
        if layer in self.active_connections:
            self.active_connections[layer]['status'] = 'disconnected'
            self.active_connections[layer]['timestamp'] = self._get_current_timestamp()
        
        # Notify subscribers
        self._notify_subscribers('connection_closed', event_data)
    
    def _notify_subscribers(self, event_type: str, event_data: Dict[str, Any]):
        """
        Notify subscribers of an event.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        if event_type in self.event_subscribers:
            for callback in self.event_subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    logger.error("Error in event subscriber callback: %s", e)
    
    def _generate_message_id(self, message: Dict[str, Any]) -> str:
        """
        Generate a unique message ID.
        
        Args:
            message: Message
        
        Returns:
            str: Unique message ID
        """
        import uuid
        import hashlib
        
        # Use type, source, and target if available
        message_type = message.get('type', '')
        source = message.get('source', '')
        target = message.get('target', '')
        
        if message_type and source and target:
            # Create a deterministic ID based on type, source, and target
            hash_input = f"{message_type}:{source}:{target}:{uuid.uuid4()}"
            return f"msg-{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"
        
        # Otherwise, generate a random ID
        return f"msg-{uuid.uuid4().hex[:8]}"
    
    def _get_current_timestamp(self) -> int:
        """
        Get current timestamp.
        
        Returns:
            int: Current timestamp in milliseconds
        """
        import time
        return int(time.time() * 1000)
    
    def to_json(self) -> str:
        """
        Serialize protocol bridge state to JSON.
        
        Returns:
            str: JSON string representation of protocol bridge state
        """
        state = {
            'layer_endpoints': self.layer_endpoints,
            'active_connections': self.active_connections
        }
        
        return json.dumps(state)
    
    def from_json(self, json_str: str) -> bool:
        """
        Deserialize protocol bridge state from JSON.
        
        Args:
            json_str: JSON string representation of protocol bridge state
        
        Returns:
            bool: True if deserialization was successful, False otherwise
        """
        try:
            state = json.loads(json_str)
            
            self.layer_endpoints = state.get('layer_endpoints', {})
            self.active_connections = state.get('active_connections', {})
            
            return True
        except Exception as e:
            logger.error("Error deserializing protocol bridge state: %s", e)
            return False
