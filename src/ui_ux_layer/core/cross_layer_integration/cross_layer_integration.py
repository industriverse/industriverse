"""
Cross-Layer Integration Module for the Industriverse UI/UX Layer.

This module provides integration between the UI/UX Layer and other layers
of the Industriverse ecosystem, ensuring seamless communication and data flow.

Author: Manus
"""

import logging
import json
import time
import threading
import queue
from typing import Dict, List, Optional, Any, Callable, Union, Set
from enum import Enum
from dataclasses import dataclass, field

class LayerType(Enum):
    """Enumeration of Industriverse layers."""
    DATA = "data"
    CORE_AI = "core_ai"
    GENERATIVE = "generative"
    APPLICATION = "application"
    PROTOCOL = "protocol"
    WORKFLOW = "workflow"
    UI_UX = "ui_ux"
    OVERSEER = "overseer"

class MessagePriority(Enum):
    """Enumeration of message priorities."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class MessageType(Enum):
    """Enumeration of message types."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    COMMAND = "command"
    NOTIFICATION = "notification"
    TELEMETRY = "telemetry"
    STATE = "state"
    ERROR = "error"

@dataclass
class CrossLayerMessage:
    """Data class representing a cross-layer message."""
    id: str
    source_layer: LayerType
    target_layer: LayerType
    message_type: MessageType
    priority: MessagePriority
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    ttl: Optional[int] = None  # Time to live in seconds
    routing_path: List[LayerType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return {
            "id": self.id,
            "source_layer": self.source_layer.value,
            "target_layer": self.target_layer.value,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "routing_path": [layer.value for layer in self.routing_path],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrossLayerMessage':
        """Create a message from a dictionary."""
        return cls(
            id=data["id"],
            source_layer=LayerType(data["source_layer"]),
            target_layer=LayerType(data["target_layer"]),
            message_type=MessageType(data["message_type"]),
            priority=MessagePriority(data["priority"]),
            payload=data["payload"],
            correlation_id=data.get("correlation_id"),
            timestamp=data.get("timestamp", time.time()),
            ttl=data.get("ttl"),
            routing_path=[LayerType(layer) for layer in data.get("routing_path", [])],
            metadata=data.get("metadata", {})
        )

class CrossLayerIntegration:
    """
    Provides integration between the UI/UX Layer and other layers of the Industriverse ecosystem.
    
    This class provides:
    - Real-time context bus for cross-layer communication
    - Message routing and delivery
    - Event subscription and publication
    - State synchronization
    - Integration with MCP and A2A protocols
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Cross-Layer Integration module.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.message_queue = queue.Queue()
        self.running = False
        self.worker_thread = None
        self.message_handlers: Dict[str, List[Callable[[CrossLayerMessage], None]]] = {}
        self.subscriptions: Dict[str, Set[Callable[[CrossLayerMessage], None]]] = {}
        self.pending_responses: Dict[str, Dict[str, Any]] = {}
        self.layer_states: Dict[LayerType, Dict[str, Any]] = {layer: {} for layer in LayerType}
        
        # Initialize from config if provided
        if config:
            pass
            
        self.logger.info("Cross-Layer Integration module initialized")
        
    def start(self) -> bool:
        """
        Start the Cross-Layer Integration module.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.logger.warning("Cross-Layer Integration module already running")
            return False
            
        self.running = True
        self.worker_thread = threading.Thread(target=self._message_worker, daemon=True)
        self.worker_thread.start()
        
        self.logger.info("Cross-Layer Integration module started")
        return True
        
    def stop(self) -> bool:
        """
        Stop the Cross-Layer Integration module.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.running:
            self.logger.warning("Cross-Layer Integration module not running")
            return False
            
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            
        self.logger.info("Cross-Layer Integration module stopped")
        return True
        
    def _message_worker(self) -> None:
        """
        Worker thread for processing messages.
        """
        self.logger.info("Message worker thread started")
        
        while self.running:
            try:
                message = self.message_queue.get(timeout=1.0)
                self._process_message(message)
                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                
        self.logger.info("Message worker thread stopped")
        
    def _process_message(self, message: CrossLayerMessage) -> None:
        """
        Process a message.
        
        Args:
            message: Message to process
        """
        # Check TTL
        if message.ttl is not None and message.ttl <= 0:
            self.logger.warning(f"Message {message.id} expired (TTL <= 0)")
            return
            
        # Update routing path
        if message.target_layer == LayerType.UI_UX and LayerType.UI_UX not in message.routing_path:
            message.routing_path.append(LayerType.UI_UX)
            
        # Handle response correlation
        if message.message_type == MessageType.RESPONSE and message.correlation_id:
            if message.correlation_id in self.pending_responses:
                callback_info = self.pending_responses.pop(message.correlation_id)
                if "callback" in callback_info and callable(callback_info["callback"]):
                    try:
                        callback_info["callback"](message)
                    except Exception as e:
                        self.logger.error(f"Error in response callback for message {message.id}: {e}")
                        
        # Dispatch to message handlers
        handler_key = f"{message.target_layer.value}.{message.message_type.value}"
        if handler_key in self.message_handlers:
            for handler in self.message_handlers[handler_key]:
                try:
                    handler(message)
                except Exception as e:
                    self.logger.error(f"Error in message handler for {handler_key}: {e}")
                    
        # Dispatch to subscriptions
        for topic, subscribers in self.subscriptions.items():
            if self._message_matches_topic(message, topic):
                for subscriber in subscribers:
                    try:
                        subscriber(message)
                    except Exception as e:
                        self.logger.error(f"Error in subscription handler for topic {topic}: {e}")
                        
        # Update layer state if state message
        if message.message_type == MessageType.STATE and message.source_layer in self.layer_states:
            self.layer_states[message.source_layer].update(message.payload)
            
    def _message_matches_topic(self, message: CrossLayerMessage, topic: str) -> bool:
        """
        Check if a message matches a subscription topic.
        
        Args:
            message: Message to check
            topic: Subscription topic
            
        Returns:
            True if the message matches the topic, False otherwise
        """
        # Topic format: source_layer.message_type.subtopic
        # Example: "data.event.data_updated"
        # Example: "*.notification.*"
        
        parts = topic.split(".")
        if len(parts) < 2:
            return False
            
        source_match = parts[0] == "*" or parts[0] == message.source_layer.value
        type_match = parts[1] == "*" or parts[1] == message.message_type.value
        
        if not (source_match and type_match):
            return False
            
        # Check subtopic if specified
        if len(parts) > 2:
            subtopic = parts[2]
            if subtopic != "*":
                # Check if subtopic exists in payload or metadata
                if "topic" in message.payload and message.payload["topic"] == subtopic:
                    return True
                elif "subtopic" in message.payload and message.payload["subtopic"] == subtopic:
                    return True
                elif "topic" in message.metadata and message.metadata["topic"] == subtopic:
                    return True
                else:
                    return False
                    
        return True
        
    def send_message(self, message: CrossLayerMessage) -> bool:
        """
        Send a message to another layer.
        
        Args:
            message: Message to send
            
        Returns:
            True if the message was queued successfully, False otherwise
        """
        if not self.running:
            self.logger.warning("Cannot send message: Cross-Layer Integration module not running")
            return False
            
        try:
            self.message_queue.put(message)
            self.logger.debug(f"Message {message.id} queued for delivery to {message.target_layer.value}")
            return True
        except Exception as e:
            self.logger.error(f"Error queueing message: {e}")
            return False
            
    def send_request(self, target_layer: LayerType, payload: Dict[str, Any], 
                    callback: Callable[[CrossLayerMessage], None], 
                    priority: MessagePriority = MessagePriority.NORMAL,
                    timeout: Optional[int] = 30) -> str:
        """
        Send a request to another layer and register a callback for the response.
        
        Args:
            target_layer: Target layer
            payload: Request payload
            callback: Callback function that will be called when the response is received
            priority: Message priority
            timeout: Timeout in seconds, or None for no timeout
            
        Returns:
            Request ID
        """
        request_id = f"req_{int(time.time() * 1000)}_{id(callback)}"
        
        message = CrossLayerMessage(
            id=request_id,
            source_layer=LayerType.UI_UX,
            target_layer=target_layer,
            message_type=MessageType.REQUEST,
            priority=priority,
            payload=payload,
            ttl=timeout
        )
        
        # Register callback for response
        self.pending_responses[request_id] = {
            "callback": callback,
            "timestamp": time.time(),
            "timeout": timeout
        }
        
        # Send the message
        self.send_message(message)
        
        return request_id
        
    def send_response(self, request_message: CrossLayerMessage, payload: Dict[str, Any],
                     priority: Optional[MessagePriority] = None) -> bool:
        """
        Send a response to a request.
        
        Args:
            request_message: Original request message
            payload: Response payload
            priority: Message priority, or None to use the same priority as the request
            
        Returns:
            True if the response was queued successfully, False otherwise
        """
        if priority is None:
            priority = request_message.priority
            
        response_id = f"resp_{request_message.id}"
        
        message = CrossLayerMessage(
            id=response_id,
            source_layer=LayerType.UI_UX,
            target_layer=request_message.source_layer,
            message_type=MessageType.RESPONSE,
            priority=priority,
            payload=payload,
            correlation_id=request_message.id,
            routing_path=list(reversed(request_message.routing_path)) if request_message.routing_path else []
        )
        
        # Send the message
        return self.send_message(message)
        
    def publish_event(self, event_type: str, payload: Dict[str, Any],
                     priority: MessagePriority = MessagePriority.NORMAL,
                     target_layers: Optional[List[LayerType]] = None) -> List[str]:
        """
        Publish an event to one or more layers.
        
        Args:
            event_type: Event type
            payload: Event payload
            priority: Message priority
            target_layers: Target layers, or None for all layers
            
        Returns:
            List of event message IDs
        """
        if target_layers is None:
            target_layers = [layer for layer in LayerType if layer != LayerType.UI_UX]
            
        event_ids = []
        
        # Add event type to payload
        event_payload = payload.copy()
        event_payload["event_type"] = event_type
        
        # Send event to each target layer
        for layer in target_layers:
            event_id = f"evt_{int(time.time() * 1000)}_{event_type}_{layer.value}"
            
            message = CrossLayerMessage(
                id=event_id,
                source_layer=LayerType.UI_UX,
                target_layer=layer,
                message_type=MessageType.EVENT,
                priority=priority,
                payload=event_payload
            )
            
            # Send the message
            if self.send_message(message):
                event_ids.append(event_id)
                
        return event_ids
        
    def send_command(self, target_layer: LayerType, command: str, params: Dict[str, Any],
                    priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """
        Send a command to another layer.
        
        Args:
            target_layer: Target layer
            command: Command name
            params: Command parameters
            priority: Message priority
            
        Returns:
            Command ID
        """
        command_id = f"cmd_{int(time.time() * 1000)}_{command}"
        
        # Create command payload
        payload = {
            "command": command,
            "params": params
        }
        
        message = CrossLayerMessage(
            id=command_id,
            source_layer=LayerType.UI_UX,
            target_layer=target_layer,
            message_type=MessageType.COMMAND,
            priority=priority,
            payload=payload
        )
        
        # Send the message
        self.send_message(message)
        
        return command_id
        
    def send_notification(self, target_layer: LayerType, notification_type: str, 
                         content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """
        Send a notification to another layer.
        
        Args:
            target_layer: Target layer
            notification_type: Notification type
            content: Notification content
            priority: Message priority
            
        Returns:
            Notification ID
        """
        notification_id = f"notif_{int(time.time() * 1000)}_{notification_type}"
        
        # Create notification payload
        payload = {
            "notification_type": notification_type,
            "content": content
        }
        
        message = CrossLayerMessage(
            id=notification_id,
            source_layer=LayerType.UI_UX,
            target_layer=target_layer,
            message_type=MessageType.NOTIFICATION,
            priority=priority,
            payload=payload
        )
        
        # Send the message
        self.send_message(message)
        
        return notification_id
        
    def update_state(self, state_data: Dict[str, Any], target_layers: Optional[List[LayerType]] = None) -> List[str]:
        """
        Update UI/UX Layer state and notify other layers.
        
        Args:
            state_data: State data to update
            target_layers: Target layers to notify, or None for all layers
            
        Returns:
            List of state message IDs
        """
        if target_layers is None:
            target_layers = [layer for layer in LayerType if layer != LayerType.UI_UX]
            
        # Update local state
        self.layer_states[LayerType.UI_UX].update(state_data)
        
        state_ids = []
        
        # Send state update to each target layer
        for layer in target_layers:
            state_id = f"state_{int(time.time() * 1000)}_{layer.value}"
            
            message = CrossLayerMessage(
                id=state_id,
                source_layer=LayerType.UI_UX,
                target_layer=layer,
                message_type=MessageType.STATE,
                priority=MessagePriority.NORMAL,
                payload=state_data
            )
            
            # Send the message
            if self.send_message(message):
                state_ids.append(state_id)
                
        return state_ids
        
    def get_layer_state(self, layer: LayerType) -> Dict[str, Any]:
        """
        Get the current state of a layer.
        
        Args:
            layer: Layer to get state for
            
        Returns:
            Current layer state
        """
        return self.layer_states.get(layer, {}).copy()
        
    def register_message_handler(self, message_type: MessageType, 
                               handler: Callable[[CrossLayerMessage], None]) -> bool:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Message type to handle
            handler: Handler function
            
        Returns:
            True if the handler was registered, False otherwise
        """
        handler_key = f"{LayerType.UI_UX.value}.{message_type.value}"
        
        if handler_key not in self.message_handlers:
            self.message_handlers[handler_key] = []
            
        self.message_handlers[handler_key].append(handler)
        self.logger.debug(f"Registered message handler for {handler_key}")
        
        return True
        
    def unregister_message_handler(self, message_type: MessageType,
                                 handler: Callable[[CrossLayerMessage], None]) -> bool:
        """
        Unregister a message handler.
        
        Args:
            message_type: Message type the handler was registered for
            handler: Handler function to unregister
            
        Returns:
            True if the handler was unregistered, False otherwise
        """
        handler_key = f"{LayerType.UI_UX.value}.{message_type.value}"
        
        if handler_key not in self.message_handlers:
            return False
            
        if handler in self.message_handlers[handler_key]:
            self.message_handlers[handler_key].remove(handler)
            self.logger.debug(f"Unregistered message handler for {handler_key}")
            return True
            
        return False
        
    def subscribe(self, topic: str, callback: Callable[[CrossLayerMessage], None]) -> bool:
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic to subscribe to (format: source_layer.message_type.subtopic)
            callback: Callback function that will be called when a matching message is received
            
        Returns:
            True if the subscription was added, False otherwise
        """
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
            
        self.subscriptions[topic].add(callback)
        self.logger.debug(f"Added subscription to topic: {topic}")
        
        return True
        
    def unsubscribe(self, topic: str, callback: Callable[[CrossLayerMessage], None]) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            callback: Callback function to unsubscribe
            
        Returns:
            True if the subscription was removed, False otherwise
        """
        if topic not in self.subscriptions:
            return False
            
        if callback in self.subscriptions[topic]:
            self.subscriptions[topic].remove(callback)
            self.logger.debug(f"Removed subscription from topic: {topic}")
            
            # Clean up empty subscription sets
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]
                
            return True
            
        return False
        
    def integrate_with_mcp(self, mcp_config: Dict[str, Any]) -> bool:
        """
        Integrate with the Model Context Protocol (MCP).
        
        Args:
            mcp_config: MCP configuration
            
        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # In a real implementation, this would integrate with the MCP protocol
            # For this implementation, we'll just log the integration
            self.logger.info(f"Integrating with MCP: {mcp_config}")
            
            # Register message handlers for MCP messages
            self.register_message_handler(MessageType.REQUEST, self._handle_mcp_request)
            self.register_message_handler(MessageType.EVENT, self._handle_mcp_event)
            
            return True
        except Exception as e:
            self.logger.error(f"Error integrating with MCP: {e}")
            return False
            
    def _handle_mcp_request(self, message: CrossLayerMessage) -> None:
        """
        Handle an MCP request message.
        
        Args:
            message: Message to handle
        """
        # In a real implementation, this would handle MCP request messages
        # For this implementation, we'll just log the message
        self.logger.debug(f"Handling MCP request: {message.id}")
        
    def _handle_mcp_event(self, message: CrossLayerMessage) -> None:
        """
        Handle an MCP event message.
        
        Args:
            message: Message to handle
        """
        # In a real implementation, this would handle MCP event messages
        # For this implementation, we'll just log the message
        self.logger.debug(f"Handling MCP event: {message.id}")
        
    def integrate_with_a2a(self, a2a_config: Dict[str, Any]) -> bool:
        """
        Integrate with the Agent-to-Agent (A2A) Protocol.
        
        Args:
            a2a_config: A2A configuration
            
        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # In a real implementation, this would integrate with the A2A protocol
            # For this implementation, we'll just log the integration
            self.logger.info(f"Integrating with A2A: {a2a_config}")
            
            # Register message handlers for A2A messages
            self.register_message_handler(MessageType.REQUEST, self._handle_a2a_request)
            self.register_message_handler(MessageType.EVENT, self._handle_a2a_event)
            
            return True
        except Exception as e:
            self.logger.error(f"Error integrating with A2A: {e}")
            return False
            
    def _handle_a2a_request(self, message: CrossLayerMessage) -> None:
        """
        Handle an A2A request message.
        
        Args:
            message: Message to handle
        """
        # In a real implementation, this would handle A2A request messages
        # For this implementation, we'll just log the message
        self.logger.debug(f"Handling A2A request: {message.id}")
        
    def _handle_a2a_event(self, message: CrossLayerMessage) -> None:
        """
        Handle an A2A event message.
        
        Args:
            message: Message to handle
        """
        # In a real implementation, this would handle A2A event messages
        # For this implementation, we'll just log the message
        self.logger.debug(f"Handling A2A event: {message.id}")
        
    def cleanup_expired_responses(self) -> int:
        """
        Clean up expired response callbacks.
        
        Returns:
            Number of expired callbacks removed
        """
        current_time = time.time()
        expired_ids = []
        
        for request_id, callback_info in self.pending_responses.items():
            if callback_info.get("timeout") is not None:
                elapsed = current_time - callback_info.get("timestamp", 0)
                if elapsed > callback_info["timeout"]:
                    expired_ids.append(request_id)
                    
        for request_id in expired_ids:
            self.pending_responses.pop(request_id, None)
            
        if expired_ids:
            self.logger.debug(f"Cleaned up {len(expired_ids)} expired response callbacks")
            
        return len(expired_ids)

class RealTimeContextBus:
    """
    Provides a real-time context bus for cross-layer communication.
    
    This class provides:
    - Real-time data streaming between layers
    - Context-aware message routing
    - Event-based communication
    - Integration with the Cross-Layer Integration module
    """
    
    def __init__(self, cross_layer_integration: CrossLayerIntegration, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Real-Time Context Bus.
        
        Args:
            cross_layer_integration: Cross-Layer Integration module
            config: Optional configuration dictionary
        """
        self.cross_layer_integration = cross_layer_integration
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.context_handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self.context_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize from config if provided
        if config:
            pass
            
        self.logger.info("Real-Time Context Bus initialized")
        
    def publish_context(self, context_type: str, context_data: Dict[str, Any],
                      target_layers: Optional[List[LayerType]] = None) -> str:
        """
        Publish context data to the bus.
        
        Args:
            context_type: Type of context data
            context_data: Context data
            target_layers: Target layers, or None for all layers
            
        Returns:
            Context message ID
        """
        # Update context cache
        if context_type not in self.context_cache:
            self.context_cache[context_type] = {}
            
        self.context_cache[context_type].update(context_data)
        
        # Create context payload
        payload = {
            "context_type": context_type,
            "context_data": context_data,
            "timestamp": time.time()
        }
        
        # Publish as event
        event_ids = self.cross_layer_integration.publish_event(
            event_type="context_updated",
            payload=payload,
            priority=MessagePriority.NORMAL,
            target_layers=target_layers
        )
        
        # Notify local context handlers
        if context_type in self.context_handlers:
            for handler in self.context_handlers[context_type]:
                try:
                    handler(context_data)
                except Exception as e:
                    self.logger.error(f"Error in context handler for {context_type}: {e}")
                    
        return event_ids[0] if event_ids else ""
        
    def get_context(self, context_type: str) -> Dict[str, Any]:
        """
        Get context data from the cache.
        
        Args:
            context_type: Type of context data
            
        Returns:
            Context data, or empty dict if not found
        """
        return self.context_cache.get(context_type, {}).copy()
        
    def register_context_handler(self, context_type: str, 
                               handler: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Register a handler for a specific context type.
        
        Args:
            context_type: Context type to handle
            handler: Handler function
            
        Returns:
            True if the handler was registered, False otherwise
        """
        if context_type not in self.context_handlers:
            self.context_handlers[context_type] = []
            
        self.context_handlers[context_type].append(handler)
        self.logger.debug(f"Registered context handler for {context_type}")
        
        # Subscribe to context events from other layers
        self.cross_layer_integration.subscribe(
            topic=f"*.event.context_updated",
            callback=self._handle_context_event
        )
        
        return True
        
    def unregister_context_handler(self, context_type: str,
                                 handler: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unregister a context handler.
        
        Args:
            context_type: Context type the handler was registered for
            handler: Handler function to unregister
            
        Returns:
            True if the handler was unregistered, False otherwise
        """
        if context_type not in self.context_handlers:
            return False
            
        if handler in self.context_handlers[context_type]:
            self.context_handlers[context_type].remove(handler)
            self.logger.debug(f"Unregistered context handler for {context_type}")
            return True
            
        return False
        
    def _handle_context_event(self, message: CrossLayerMessage) -> None:
        """
        Handle a context event message.
        
        Args:
            message: Message to handle
        """
        if message.message_type != MessageType.EVENT:
            return
            
        payload = message.payload
        if "context_type" not in payload or "context_data" not in payload:
            return
            
        context_type = payload["context_type"]
        context_data = payload["context_data"]
        
        # Update context cache
        if context_type not in self.context_cache:
            self.context_cache[context_type] = {}
            
        self.context_cache[context_type].update(context_data)
        
        # Notify context handlers
        if context_type in self.context_handlers:
            for handler in self.context_handlers[context_type]:
                try:
                    handler(context_data)
                except Exception as e:
                    self.logger.error(f"Error in context handler for {context_type}: {e}")

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create Cross-Layer Integration module
    cross_layer_integration = CrossLayerIntegration()
    cross_layer_integration.start()
    
    # Create Real-Time Context Bus
    context_bus = RealTimeContextBus(cross_layer_integration)
    
    # Register context handler
    def handle_user_context(context_data):
        print(f"Received user context: {context_data}")
        
    context_bus.register_context_handler("user", handle_user_context)
    
    # Publish context
    context_bus.publish_context(
        context_type="user",
        context_data={
            "user_id": "user123",
            "role": "admin",
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
    )
    
    # Clean up
    cross_layer_integration.stop()
