"""
MCP Integration Manager for Protocol Bridge

This module manages the Model Context Protocol (MCP) integration within the Protocol Bridge
of the Industriverse UI/UX Layer. It implements bidirectional communication, message routing,
and context synchronization using the MCP protocol.

The MCP Integration Manager:
1. Implements MCP message formatting and parsing
2. Handles bidirectional communication with other layers
3. Manages context synchronization across the system
4. Provides an API for sending and receiving MCP messages
5. Integrates with the Context Engine for context-aware operations

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import uuid
import threading
import queue
import websocket
import requests

# Local imports
from ..context_engine.context_awareness_engine import ContextAwarenessEngine

# Configure logging
logger = logging.getLogger(__name__)

class MCPMessageType(Enum):
    """Enumeration of MCP message types."""
    CONTEXT_UPDATE = "context_update"
    CONTEXT_REQUEST = "context_request"
    CONTEXT_RESPONSE = "context_response"
    COMMAND = "command"
    COMMAND_RESPONSE = "command_response"
    EVENT = "event"
    STATE_UPDATE = "state_update"
    STATE_REQUEST = "state_request"
    STATE_RESPONSE = "state_response"
    HEARTBEAT = "heartbeat"
    ERROR = "error"

class MCPIntegrationManager:
    """
    Manages the Model Context Protocol (MCP) integration within the Protocol Bridge.
    
    This class is responsible for implementing bidirectional communication, message routing,
    and context synchronization using the MCP protocol.
    """
    
    def __init__(
        self, 
        context_engine: ContextAwarenessEngine,
        config: Dict = None
    ):
        """
        Initialize the MCP Integration Manager.
        
        Args:
            context_engine: The Context Awareness Engine instance
            config: Optional configuration dictionary
        """
        self.context_engine = context_engine
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "mcp_version": "1.0",
            "source_id": "ui_ux_layer",
            "heartbeat_interval": 30,  # seconds
            "reconnect_interval": 5,   # seconds
            "max_reconnect_attempts": 10,
            "message_timeout": 30,     # seconds
            "max_queue_size": 1000,
            "endpoints": {
                "data_layer": "ws://localhost:8001/mcp",
                "core_ai_layer": "ws://localhost:8002/mcp",
                "generative_layer": "ws://localhost:8003/mcp",
                "application_layer": "ws://localhost:8004/mcp",
                "protocol_layer": "ws://localhost:8005/mcp",
                "workflow_layer": "ws://localhost:8006/mcp",
                "overseer_layer": "ws://localhost:8007/mcp"
            },
            "http_endpoints": {
                "data_layer": "http://localhost:8001/mcp/http",
                "core_ai_layer": "http://localhost:8002/mcp/http",
                "generative_layer": "http://localhost:8003/mcp/http",
                "application_layer": "http://localhost:8004/mcp/http",
                "protocol_layer": "http://localhost:8005/mcp/http",
                "workflow_layer": "http://localhost:8006/mcp/http",
                "overseer_layer": "http://localhost:8007/mcp/http"
            }
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # WebSocket connections by destination
        self.ws_connections = {}
        
        # Message handlers by message type
        self.message_handlers = {}
        
        # Default message handlers
        self.default_handlers = self._create_default_handlers()
        
        # Pending responses by message ID
        self.pending_responses = {}
        
        # Response events by message ID
        self.response_events = {}
        
        # Outgoing message queue
        self.outgoing_queue = queue.Queue(maxsize=self.config["max_queue_size"])
        
        # Connection status by destination
        self.connection_status = {}
        
        # Message sequence numbers by destination
        self.sequence_numbers = {}
        
        # Register as context listener
        self.context_engine.register_context_listener(self._handle_context_change)
        
        # Start worker threads
        self.running = True
        self.outgoing_thread = threading.Thread(target=self._outgoing_worker)
        self.outgoing_thread.daemon = True
        self.outgoing_thread.start()
        
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        
        # Initialize connections
        self._initialize_connections()
        
        logger.info("MCP Integration Manager initialized")
    
    def _merge_config(self) -> None:
        """Merge provided configuration with defaults."""
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                # Merge nested dictionaries
                for nested_key, nested_value in value.items():
                    if nested_key not in self.config[key]:
                        self.config[key][nested_key] = nested_value
    
    def _create_default_handlers(self) -> Dict:
        """
        Create default message handlers.
        
        Returns:
            Dictionary of default handlers by message type
        """
        return {
            MCPMessageType.CONTEXT_UPDATE.value: self._handle_context_update,
            MCPMessageType.CONTEXT_REQUEST.value: self._handle_context_request,
            MCPMessageType.CONTEXT_RESPONSE.value: self._handle_context_response,
            MCPMessageType.COMMAND.value: self._handle_command,
            MCPMessageType.COMMAND_RESPONSE.value: self._handle_command_response,
            MCPMessageType.EVENT.value: self._handle_event,
            MCPMessageType.STATE_UPDATE.value: self._handle_state_update,
            MCPMessageType.STATE_REQUEST.value: self._handle_state_request,
            MCPMessageType.STATE_RESPONSE.value: self._handle_state_response,
            MCPMessageType.HEARTBEAT.value: self._handle_heartbeat,
            MCPMessageType.ERROR.value: self._handle_error
        }
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        # Propagate context changes to other layers via MCP
        context_type = event.get("type")
        context_data = event.get("data", {})
        
        # Only propagate certain context types
        if context_type in ["user", "system", "task", "device"]:
            # Create MCP context update message
            message = {
                "protocol": "mcp",
                "version": self.config["mcp_version"],
                "message_id": str(uuid.uuid4()),
                "message_type": MCPMessageType.CONTEXT_UPDATE.value,
                "source": self.config["source_id"],
                "destination": "all",  # Broadcast to all layers
                "timestamp": time.time(),
                "payload": {
                    "context_type": context_type,
                    "context_data": context_data
                }
            }
            
            # Send message
            self.send_mcp_message(message)
    
    def _initialize_connections(self) -> None:
        """Initialize WebSocket connections to other layers."""
        for layer, endpoint in self.config["endpoints"].items():
            # Skip self-connection
            if layer == self.config["source_id"]:
                continue
            
            # Initialize connection status
            self.connection_status[layer] = {
                "connected": False,
                "last_attempt": 0,
                "attempts": 0,
                "last_heartbeat": 0
            }
            
            # Initialize sequence number
            self.sequence_numbers[layer] = 0
            
            # Start connection thread
            thread = threading.Thread(target=self._connect_to_layer, args=(layer, endpoint))
            thread.daemon = True
            thread.start()
    
    def _connect_to_layer(self, layer: str, endpoint: str) -> None:
        """
        Connect to a layer via WebSocket.
        
        Args:
            layer: Layer ID to connect to
            endpoint: WebSocket endpoint URL
        """
        # Update connection status
        self.connection_status[layer]["last_attempt"] = time.time()
        self.connection_status[layer]["attempts"] += 1
        
        try:
            # Create WebSocket connection
            ws = websocket.WebSocketApp(
                endpoint,
                on_open=lambda ws: self._on_ws_open(ws, layer),
                on_message=lambda ws, msg: self._on_ws_message(ws, msg, layer),
                on_error=lambda ws, err: self._on_ws_error(ws, err, layer),
                on_close=lambda ws, code, reason: self._on_ws_close(ws, code, reason, layer)
            )
            
            # Store connection
            self.ws_connections[layer] = ws
            
            # Start WebSocket connection
            ws.run_forever()
        except Exception as e:
            logger.error(f"Error connecting to {layer} at {endpoint}: {str(e)}")
            
            # Schedule reconnection if needed
            self._schedule_reconnection(layer)
    
    def _on_ws_open(self, ws: websocket.WebSocketApp, layer: str) -> None:
        """
        Handle WebSocket connection open.
        
        Args:
            ws: WebSocket connection
            layer: Layer ID
        """
        logger.info(f"Connected to {layer}")
        
        # Update connection status
        self.connection_status[layer]["connected"] = True
        self.connection_status[layer]["attempts"] = 0
        
        # Send initial heartbeat
        self._send_heartbeat(layer)
    
    def _on_ws_message(self, ws: websocket.WebSocketApp, message: str, layer: str) -> None:
        """
        Handle WebSocket message received.
        
        Args:
            ws: WebSocket connection
            message: Message received
            layer: Layer ID
        """
        try:
            # Parse message
            msg_data = json.loads(message)
            
            # Process message
            self._process_incoming_message(msg_data, layer)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from {layer}: {message}")
        except Exception as e:
            logger.error(f"Error processing message from {layer}: {str(e)}")
    
    def _on_ws_error(self, ws: websocket.WebSocketApp, error: Exception, layer: str) -> None:
        """
        Handle WebSocket error.
        
        Args:
            ws: WebSocket connection
            error: Error that occurred
            layer: Layer ID
        """
        logger.error(f"WebSocket error for {layer}: {str(error)}")
    
    def _on_ws_close(
        self, 
        ws: websocket.WebSocketApp, 
        close_code: int, 
        close_reason: str, 
        layer: str
    ) -> None:
        """
        Handle WebSocket connection close.
        
        Args:
            ws: WebSocket connection
            close_code: Close code
            close_reason: Close reason
            layer: Layer ID
        """
        logger.info(f"Disconnected from {layer}: {close_code} - {close_reason}")
        
        # Update connection status
        self.connection_status[layer]["connected"] = False
        
        # Schedule reconnection if needed
        self._schedule_reconnection(layer)
    
    def _schedule_reconnection(self, layer: str) -> None:
        """
        Schedule reconnection to a layer.
        
        Args:
            layer: Layer ID to reconnect to
        """
        # Check if max attempts reached
        if (self.connection_status[layer]["attempts"] >= 
            self.config["max_reconnect_attempts"]):
            logger.warning(
                f"Max reconnection attempts reached for {layer}, "
                "will not attempt further reconnections"
            )
            return
        
        # Calculate backoff time
        backoff = min(
            self.config["reconnect_interval"] * (2 ** (self.connection_status[layer]["attempts"] - 1)),
            60  # Max 60 seconds
        )
        
        logger.info(f"Scheduling reconnection to {layer} in {backoff:.1f} seconds")
        
        # Schedule reconnection
        threading.Timer(
            backoff,
            self._reconnect_to_layer,
            args=(layer,)
        ).start()
    
    def _reconnect_to_layer(self, layer: str) -> None:
        """
        Reconnect to a layer.
        
        Args:
            layer: Layer ID to reconnect to
        """
        # Skip if already connected
        if self.connection_status[layer]["connected"]:
            return
        
        # Get endpoint
        endpoint = self.config["endpoints"].get(layer)
        if not endpoint:
            logger.error(f"No endpoint configured for {layer}")
            return
        
        # Start connection thread
        thread = threading.Thread(target=self._connect_to_layer, args=(layer, endpoint))
        thread.daemon = True
        thread.start()
    
    def _process_incoming_message(self, message: Dict, source_layer: str) -> None:
        """
        Process an incoming MCP message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        # Validate message
        if not self._validate_mcp_message(message):
            logger.error(f"Invalid MCP message from {source_layer}: {message}")
            return
        
        # Extract message details
        message_id = message.get("message_id")
        message_type = message.get("message_type")
        
        # Check if this is a response to a pending request
        if message_id in self.pending_responses:
            # Store response
            self.pending_responses[message_id] = message
            
            # Signal response received
            if message_id in self.response_events:
                self.response_events[message_id].set()
            
            return
        
        # Find appropriate handler
        handler = self._get_message_handler(message_type)
        
        # Handle message
        try:
            handler(message, source_layer)
        except Exception as e:
            logger.error(f"Error handling message type {message_type}: {str(e)}")
    
    def _validate_mcp_message(self, message: Dict) -> bool:
        """
        Validate an MCP message.
        
        Args:
            message: MCP message to validate
            
        Returns:
            Boolean indicating validity
        """
        # Check required fields
        required_fields = [
            "protocol", "version", "message_id", "message_type",
            "source", "destination", "timestamp"
        ]
        
        for field in required_fields:
            if field not in message:
                logger.error(f"Missing required field in MCP message: {field}")
                return False
        
        # Check protocol
        if message["protocol"] != "mcp":
            logger.error(f"Invalid protocol in message: {message['protocol']}")
            return False
        
        # Check version compatibility
        if message["version"] != self.config["mcp_version"]:
            logger.warning(
                f"MCP version mismatch: message={message['version']}, "
                f"local={self.config['mcp_version']}"
            )
            # Continue processing despite version mismatch
        
        # Check message type
        if not any(t.value == message["message_type"] for t in MCPMessageType):
            logger.error(f"Invalid message type: {message['message_type']}")
            return False
        
        return True
    
    def _get_message_handler(self, message_type: str) -> callable:
        """
        Get the appropriate message handler for a message type.
        
        Args:
            message_type: Message type to get handler for
            
        Returns:
            Handler function
        """
        # Check for registered handler
        if message_type in self.message_handlers:
            return self.message_handlers[message_type]
        
        # Fall back to default handler
        return self.default_handlers.get(
            message_type,
            lambda msg, src: logger.warning(f"No handler for message type: {message_type}")
        )
    
    def _outgoing_worker(self) -> None:
        """Background thread for sending outgoing messages."""
        while self.running:
            try:
                # Get next message from queue
                message, destination = self.outgoing_queue.get(timeout=1.0)
                
                # Send message
                self._send_message_to_destination(message, destination)
                
                # Mark task as done
                self.outgoing_queue.task_done()
            except queue.Empty:
                # Queue empty, continue
                pass
            except Exception as e:
                logger.error(f"Error in outgoing worker: {str(e)}")
                time.sleep(1)  # Avoid tight loop on error
    
    def _send_message_to_destination(self, message: Dict, destination: str) -> bool:
        """
        Send a message to a specific destination.
        
        Args:
            message: Message to send
            destination: Destination to send to
            
        Returns:
            Boolean indicating success
        """
        # Handle broadcast
        if destination == "all":
            success = True
            
            # Send to all connected layers
            for layer, ws in self.ws_connections.items():
                if self.connection_status[layer]["connected"]:
                    # Update destination
                    msg_copy = message.copy()
                    msg_copy["destination"] = layer
                    
                    # Update sequence number
                    self.sequence_numbers[layer] += 1
                    msg_copy["sequence"] = self.sequence_numbers[layer]
                    
                    # Send message
                    layer_success = self._send_websocket_message(ws, msg_copy)
                    success = success and layer_success
            
            return success
        
        # Handle specific destination
        if "." in destination:
            # Destination includes sub-component (e.g., "data_layer.storage")
            parts = destination.split(".", 1)
            layer = parts[0]
        else:
            # Simple destination
            layer = destination
        
        # Check if connected to destination
        if layer in self.ws_connections and self.connection_status[layer]["connected"]:
            # Update sequence number
            self.sequence_numbers[layer] += 1
            message["sequence"] = self.sequence_numbers[layer]
            
            # Send via WebSocket
            return self._send_websocket_message(self.ws_connections[layer], message)
        else:
            # Not connected, try HTTP fallback
            return self._send_http_message(layer, message)
    
    def _send_websocket_message(self, ws: websocket.WebSocketApp, message: Dict) -> bool:
        """
        Send a message via WebSocket.
        
        Args:
            ws: WebSocket connection
            message: Message to send
            
        Returns:
            Boolean indicating success
        """
        try:
            # Convert message to JSON
            message_json = json.dumps(message)
            
            # Send message
            ws.send(message_json)
            
            return True
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {str(e)}")
            return False
    
    def _send_http_message(self, layer: str, message: Dict) -> bool:
        """
        Send a message via HTTP fallback.
        
        Args:
            layer: Destination layer
            message: Message to send
            
        Returns:
            Boolean indicating success
        """
        # Check if HTTP endpoint is configured
        if layer not in self.config["http_endpoints"]:
            logger.error(f"No HTTP endpoint configured for {layer}")
            return False
        
        endpoint = self.config["http_endpoints"][layer]
        
        try:
            # Send HTTP POST request
            response = requests.post(
                endpoint,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Check response
            if response.status_code == 200:
                return True
            else:
                logger.error(
                    f"HTTP error sending to {layer}: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error sending HTTP message to {layer}: {str(e)}")
            return False
    
    def _heartbeat_worker(self) -> None:
        """Background thread for sending heartbeat messages."""
        while self.running:
            try:
                # Send heartbeats to all connected layers
                for layer in self.ws_connections.keys():
                    if self.connection_status[layer]["connected"]:
                        # Check if heartbeat is due
                        last_heartbeat = self.connection_status[layer]["last_heartbeat"]
                        if time.time() - last_heartbeat >= self.config["heartbeat_interval"]:
                            self._send_heartbeat(layer)
                
                # Sleep until next check
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in heartbeat worker: {str(e)}")
                time.sleep(5)  # Avoid tight loop on error
    
    def _send_heartbeat(self, layer: str) -> None:
        """
        Send a heartbeat message to a layer.
        
        Args:
            layer: Layer ID to send heartbeat to
        """
        # Create heartbeat message
        message = {
            "protocol": "mcp",
            "version": self.config["mcp_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": MCPMessageType.HEARTBEAT.value,
            "source": self.config["source_id"],
            "destination": layer,
            "timestamp": time.time(),
            "payload": {
                "status": "active"
            }
        }
        
        # Send message
        if self._send_message_to_destination(message, layer):
            # Update last heartbeat time
            self.connection_status[layer]["last_heartbeat"] = time.time()
    
    # Default message handlers
    
    def _handle_context_update(self, message: Dict, source_layer: str) -> None:
        """
        Handle context update message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        payload = message.get("payload", {})
        context_type = payload.get("context_type")
        context_data = payload.get("context_data", {})
        
        if not context_type:
            logger.error("Missing context_type in context update message")
            return
        
        # Update local context
        self.context_engine.update_context(context_type, context_data, source=source_layer)
        
        logger.debug(f"Updated {context_type} context from {source_layer}")
    
    def _handle_context_request(self, message: Dict, source_layer: str) -> None:
        """
        Handle context request message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        message_id = message.get("message_id")
        payload = message.get("payload", {})
        context_type = payload.get("context_type")
        
        if not context_type:
            logger.error("Missing context_type in context request message")
            return
        
        # Get requested context
        context_data = self.context_engine.get_context(context_type)
        
        # Create response message
        response = {
            "protocol": "mcp",
            "version": self.config["mcp_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": MCPMessageType.CONTEXT_RESPONSE.value,
            "source": self.config["source_id"],
            "destination": source_layer,
            "timestamp": time.time(),
            "in_response_to": message_id,
            "payload": {
                "context_type": context_type,
                "context_data": context_data
            }
        }
        
        # Send response
        self.send_mcp_message(response)
        
        logger.debug(f"Sent {context_type} context to {source_layer}")
    
    def _handle_context_response(self, message: Dict, source_layer: str) -> None:
        """
        Handle context response message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        # This is handled by the pending responses mechanism
        # No additional processing needed here
        pass
    
    def _handle_command(self, message: Dict, source_layer: str) -> None:
        """
        Handle command message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        message_id = message.get("message_id")
        payload = message.get("payload", {})
        command = payload.get("command")
        params = payload.get("params", {})
        
        if not command:
            logger.error("Missing command in command message")
            return
        
        # Process command
        result = None
        error = None
        
        try:
            # Handle different commands
            if command == "get_status":
                result = self._handle_get_status_command()
            elif command == "update_config":
                result = self._handle_update_config_command(params)
            elif command == "reconnect":
                result = self._handle_reconnect_command(params)
            else:
                error = f"Unknown command: {command}"
        except Exception as e:
            error = str(e)
        
        # Create response message
        response = {
            "protocol": "mcp",
            "version": self.config["mcp_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": MCPMessageType.COMMAND_RESPONSE.value,
            "source": self.config["source_id"],
            "destination": source_layer,
            "timestamp": time.time(),
            "in_response_to": message_id,
            "payload": {
                "command": command,
                "result": result,
                "error": error
            }
        }
        
        # Send response
        self.send_mcp_message(response)
        
        if error:
            logger.error(f"Error handling command {command} from {source_layer}: {error}")
        else:
            logger.debug(f"Handled command {command} from {source_layer}")
    
    def _handle_get_status_command(self) -> Dict:
        """
        Handle get_status command.
        
        Returns:
            Status information
        """
        return {
            "connections": self.connection_status,
            "queue_size": self.outgoing_queue.qsize(),
            "pending_responses": len(self.pending_responses)
        }
    
    def _handle_update_config_command(self, params: Dict) -> Dict:
        """
        Handle update_config command.
        
        Args:
            params: Command parameters
            
        Returns:
            Updated configuration
        """
        # Update configuration
        for key, value in params.items():
            if key in self.config:
                self.config[key] = value
        
        return {
            "updated_keys": list(params.keys()),
            "config": self.config
        }
    
    def _handle_reconnect_command(self, params: Dict) -> Dict:
        """
        Handle reconnect command.
        
        Args:
            params: Command parameters
            
        Returns:
            Reconnection status
        """
        layer = params.get("layer")
        
        if not layer:
            # Reconnect all
            for layer_id in self.ws_connections.keys():
                self._reconnect_to_layer(layer_id)
            
            return {
                "reconnecting": list(self.ws_connections.keys())
            }
        elif layer in self.ws_connections:
            # Reconnect specific layer
            self._reconnect_to_layer(layer)
            
            return {
                "reconnecting": [layer]
            }
        else:
            raise ValueError(f"Unknown layer: {layer}")
    
    def _handle_command_response(self, message: Dict, source_layer: str) -> None:
        """
        Handle command response message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        # This is handled by the pending responses mechanism
        # No additional processing needed here
        pass
    
    def _handle_event(self, message: Dict, source_layer: str) -> None:
        """
        Handle event message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        payload = message.get("payload", {})
        event_type = payload.get("event_type")
        event_data = payload.get("event_data", {})
        
        if not event_type:
            logger.error("Missing event_type in event message")
            return
        
        # Log event
        logger.info(f"Received {event_type} event from {source_layer}")
        
        # Update context if relevant
        if event_type in ["user_action", "system_change", "task_update"]:
            context_type = event_type.split("_")[0]  # Extract context type
            self.context_engine.update_context(context_type, event_data, source=source_layer)
    
    def _handle_state_update(self, message: Dict, source_layer: str) -> None:
        """
        Handle state update message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        payload = message.get("payload", {})
        state_type = payload.get("state_type")
        state_data = payload.get("state_data", {})
        
        if not state_type:
            logger.error("Missing state_type in state update message")
            return
        
        # Log state update
        logger.debug(f"Received {state_type} state update from {source_layer}")
        
        # Update context with state information
        self.context_engine.update_context(
            "layer_state",
            {
                "layer": source_layer,
                "state_type": state_type,
                "state_data": state_data
            },
            source=source_layer
        )
    
    def _handle_state_request(self, message: Dict, source_layer: str) -> None:
        """
        Handle state request message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        message_id = message.get("message_id")
        payload = message.get("payload", {})
        state_type = payload.get("state_type")
        
        if not state_type:
            logger.error("Missing state_type in state request message")
            return
        
        # Get requested state
        state_data = {}
        
        # Handle different state types
        if state_type == "ui_state":
            state_data = self._get_ui_state()
        elif state_type == "connection_state":
            state_data = self.connection_status
        
        # Create response message
        response = {
            "protocol": "mcp",
            "version": self.config["mcp_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": MCPMessageType.STATE_RESPONSE.value,
            "source": self.config["source_id"],
            "destination": source_layer,
            "timestamp": time.time(),
            "in_response_to": message_id,
            "payload": {
                "state_type": state_type,
                "state_data": state_data
            }
        }
        
        # Send response
        self.send_mcp_message(response)
        
        logger.debug(f"Sent {state_type} state to {source_layer}")
    
    def _get_ui_state(self) -> Dict:
        """
        Get current UI state.
        
        Returns:
            UI state information
        """
        # In a real implementation, this would get actual UI state
        # For now, return a placeholder
        return {
            "active_view": "dashboard",
            "active_capsules": 3,
            "notifications": 2
        }
    
    def _handle_state_response(self, message: Dict, source_layer: str) -> None:
        """
        Handle state response message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        # This is handled by the pending responses mechanism
        # No additional processing needed here
        pass
    
    def _handle_heartbeat(self, message: Dict, source_layer: str) -> None:
        """
        Handle heartbeat message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        # Update connection status
        if source_layer in self.connection_status:
            self.connection_status[source_layer]["last_heartbeat"] = time.time()
        
        # No response needed for heartbeats
    
    def _handle_error(self, message: Dict, source_layer: str) -> None:
        """
        Handle error message.
        
        Args:
            message: MCP message
            source_layer: Source layer ID
        """
        payload = message.get("payload", {})
        error_code = payload.get("error_code")
        error_message = payload.get("error_message")
        in_response_to = message.get("in_response_to")
        
        logger.error(
            f"Received error from {source_layer}: "
            f"[{error_code}] {error_message} "
            f"(in response to: {in_response_to})"
        )
    
    # Public API
    
    def register_message_handler(self, message_type: str, handler: callable) -> bool:
        """
        Register a message handler.
        
        Args:
            message_type: Message type to handle
            handler: Handler function
            
        Returns:
            Boolean indicating success
        """
        # Verify message type
        if not any(t.value == message_type for t in MCPMessageType):
            logger.error(f"Invalid message type: {message_type}")
            return False
        
        # Register handler
        self.message_handlers[message_type] = handler
        
        logger.debug(f"Registered handler for {message_type} messages")
        return True
    
    def unregister_message_handler(self, message_type: str) -> bool:
        """
        Unregister a message handler.
        
        Args:
            message_type: Message type to unregister
            
        Returns:
            Boolean indicating success
        """
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]
            logger.debug(f"Unregistered handler for {message_type} messages")
            return True
        
        return False
    
    def send_mcp_message(self, message: Dict) -> bool:
        """
        Send an MCP message.
        
        Args:
            message: MCP message to send
            
        Returns:
            Boolean indicating success
        """
        # Validate message
        if not self._validate_mcp_message(message):
            return False
        
        # Get destination
        destination = message.get("destination")
        
        try:
            # Add to outgoing queue
            self.outgoing_queue.put((message, destination), timeout=1.0)
            return True
        except queue.Full:
            logger.error("Outgoing message queue full, message dropped")
            return False
    
    def send_mcp_message_sync(self, message: Dict, timeout: float = None) -> Optional[Dict]:
        """
        Send an MCP message and wait for response.
        
        Args:
            message: MCP message to send
            timeout: Optional timeout in seconds
            
        Returns:
            Response message or None on timeout/error
        """
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.config["message_timeout"]
        
        # Validate message
        if not self._validate_mcp_message(message):
            return None
        
        # Get message ID and destination
        message_id = message.get("message_id")
        destination = message.get("destination")
        
        # Create response event
        response_event = threading.Event()
        self.response_events[message_id] = response_event
        
        # Initialize pending response
        self.pending_responses[message_id] = None
        
        try:
            # Send message
            if not self.send_mcp_message(message):
                logger.error("Failed to send message")
                return None
            
            # Wait for response
            if response_event.wait(timeout):
                # Response received
                return self.pending_responses[message_id]
            else:
                # Timeout
                logger.warning(f"Timeout waiting for response to {message_id}")
                return None
        finally:
            # Clean up
            if message_id in self.response_events:
                del self.response_events[message_id]
            
            if message_id in self.pending_responses:
                del self.pending_responses[message_id]
    
    def request_context(self, context_type: str, layer: str, timeout: float = None) -> Optional[Dict]:
        """
        Request context from another layer.
        
        Args:
            context_type: Type of context to request
            layer: Layer to request from
            timeout: Optional timeout in seconds
            
        Returns:
            Context data or None on timeout/error
        """
        # Create context request message
        message = {
            "protocol": "mcp",
            "version": self.config["mcp_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": MCPMessageType.CONTEXT_REQUEST.value,
            "source": self.config["source_id"],
            "destination": layer,
            "timestamp": time.time(),
            "payload": {
                "context_type": context_type
            }
        }
        
        # Send message and wait for response
        response = self.send_mcp_message_sync(message, timeout)
        
        if response:
            return response.get("payload", {}).get("context_data")
        else:
            return None
    
    def send_command(
        self, 
        command: str, 
        params: Dict, 
        layer: str, 
        timeout: float = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Send a command to another layer.
        
        Args:
            command: Command to send
            params: Command parameters
            layer: Layer to send to
            timeout: Optional timeout in seconds
            
        Returns:
            Tuple of (success, result, error)
        """
        # Create command message
        message = {
            "protocol": "mcp",
            "version": self.config["mcp_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": MCPMessageType.COMMAND.value,
            "source": self.config["source_id"],
            "destination": layer,
            "timestamp": time.time(),
            "payload": {
                "command": command,
                "params": params
            }
        }
        
        # Send message and wait for response
        response = self.send_mcp_message_sync(message, timeout)
        
        if response:
            payload = response.get("payload", {})
            result = payload.get("result")
            error = payload.get("error")
            
            return (error is None, result, error)
        else:
            return (False, None, "Timeout or communication error")
    
    def send_event(self, event_type: str, event_data: Dict, destination: str = "all") -> bool:
        """
        Send an event to other layers.
        
        Args:
            event_type: Type of event
            event_data: Event data
            destination: Destination layer or "all" for broadcast
            
        Returns:
            Boolean indicating success
        """
        # Create event message
        message = {
            "protocol": "mcp",
            "version": self.config["mcp_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": MCPMessageType.EVENT.value,
            "source": self.config["source_id"],
            "destination": destination,
            "timestamp": time.time(),
            "payload": {
                "event_type": event_type,
                "event_data": event_data
            }
        }
        
        # Send message
        return self.send_mcp_message(message)
    
    def send_state_update(self, state_type: str, state_data: Dict, destination: str = "all") -> bool:
        """
        Send a state update to other layers.
        
        Args:
            state_type: Type of state
            state_data: State data
            destination: Destination layer or "all" for broadcast
            
        Returns:
            Boolean indicating success
        """
        # Create state update message
        message = {
            "protocol": "mcp",
            "version": self.config["mcp_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": MCPMessageType.STATE_UPDATE.value,
            "source": self.config["source_id"],
            "destination": destination,
            "timestamp": time.time(),
            "payload": {
                "state_type": state_type,
                "state_data": state_data
            }
        }
        
        # Send message
        return self.send_mcp_message(message)
    
    def request_state(self, state_type: str, layer: str, timeout: float = None) -> Optional[Dict]:
        """
        Request state from another layer.
        
        Args:
            state_type: Type of state to request
            layer: Layer to request from
            timeout: Optional timeout in seconds
            
        Returns:
            State data or None on timeout/error
        """
        # Create state request message
        message = {
            "protocol": "mcp",
            "version": self.config["mcp_version"],
            "message_id": str(uuid.uuid4()),
            "message_type": MCPMessageType.STATE_REQUEST.value,
            "source": self.config["source_id"],
            "destination": layer,
            "timestamp": time.time(),
            "payload": {
                "state_type": state_type
            }
        }
        
        # Send message and wait for response
        response = self.send_mcp_message_sync(message, timeout)
        
        if response:
            return response.get("payload", {}).get("state_data")
        else:
            return None
    
    def get_connection_status(self, layer: str = None) -> Dict:
        """
        Get connection status.
        
        Args:
            layer: Optional layer to get status for
            
        Returns:
            Connection status information
        """
        if layer:
            return self.connection_status.get(layer, {})
        else:
            return self.connection_status
    
    def shutdown(self) -> None:
        """Shutdown the MCP Integration Manager."""
        logger.info("Shutting down MCP Integration Manager")
        
        # Stop worker threads
        self.running = False
        
        # Close all WebSocket connections
        for layer, ws in self.ws_connections.items():
            try:
                ws.close()
            except Exception:
                pass
        
        # Clear connections
        self.ws_connections.clear()
        
        # Wait for threads to exit
        if self.outgoing_thread.is_alive():
            self.outgoing_thread.join(timeout=2)
        
        if self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=2)
"""
