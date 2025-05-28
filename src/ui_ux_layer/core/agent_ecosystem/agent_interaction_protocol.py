"""
Agent Interaction Protocol for the UI/UX Layer

This module implements the interaction protocol between UI components and agents
in the Industriverse ecosystem. It handles message formatting, routing, state
synchronization, and event handling for agent-UI communications.

The Agent Interaction Protocol:
1. Defines message formats for UI-agent communication
2. Manages bidirectional event routing
3. Handles state synchronization between UI and agents
4. Implements request-response patterns
5. Provides real-time updates and notifications
6. Supports both local and remote agent interactions

Author: Manus
"""

import logging
import json
import uuid
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import threading
import queue

# Local imports
from ..protocol_bridge.a2a_integration_manager import A2AIntegrationManager
from ..protocol_bridge.mcp_integration_manager import MCPIntegrationManager

# Configure logging
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Enumeration of agent interaction message types."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    STATE_UPDATE = "state_update"
    COMMAND = "command"
    NOTIFICATION = "notification"
    ERROR = "error"

class AgentInteractionProtocol:
    """
    Implements the interaction protocol between UI components and agents.
    
    This class handles message formatting, routing, state synchronization,
    and event handling for agent-UI communications in the Industriverse ecosystem.
    """
    
    def __init__(
        self,
        a2a_manager: A2AIntegrationManager,
        mcp_manager: MCPIntegrationManager,
        config: Dict = None
    ):
        """
        Initialize the Agent Interaction Protocol.
        
        Args:
            a2a_manager: A2A Integration Manager instance
            mcp_manager: MCP Integration Manager instance
            config: Optional configuration dictionary
        """
        self.a2a_manager = a2a_manager
        self.mcp_manager = mcp_manager
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "message_timeout": 30,  # seconds
            "retry_attempts": 3,
            "retry_delay": 1.0,  # seconds
            "batch_size": 10,
            "queue_size": 100,
            "enable_compression": True,
            "compression_threshold": 1024,  # bytes
            "enable_encryption": True,
            "enable_batching": True,
            "enable_prioritization": True,
            "enable_local_cache": True,
            "cache_ttl": 300,  # seconds
            "heartbeat_interval": 30,  # seconds
            "connection_check_interval": 60,  # seconds
            "log_messages": True,
            "log_level": "INFO"
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Message handlers by type
        self.message_handlers = {
            MessageType.REQUEST.value: {},
            MessageType.RESPONSE.value: {},
            MessageType.EVENT.value: {},
            MessageType.STATE_UPDATE.value: {},
            MessageType.COMMAND.value: {},
            MessageType.NOTIFICATION.value: {},
            MessageType.ERROR.value: {}
        }
        
        # Pending requests (request_id -> callback)
        self.pending_requests = {}
        
        # Message queues
        self.outgoing_queue = queue.PriorityQueue(maxsize=self.config["queue_size"])
        self.incoming_queue = queue.Queue(maxsize=self.config["queue_size"])
        
        # Local cache for state and responses
        self.local_cache = {}
        self.cache_timestamps = {}
        
        # Connection state
        self.connected = False
        self.last_heartbeat = 0
        
        # Start worker threads
        self.running = True
        self.outgoing_thread = threading.Thread(target=self._outgoing_worker, daemon=True)
        self.incoming_thread = threading.Thread(target=self._incoming_worker, daemon=True)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)
        
        self.outgoing_thread.start()
        self.incoming_thread.start()
        self.heartbeat_thread.start()
        
        # Register with protocol managers
        self._register_protocol_handlers()
        
        logger.info("Agent Interaction Protocol initialized")
    
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
    
    def _register_protocol_handlers(self) -> None:
        """Register handlers with protocol managers."""
        # Register with A2A manager
        self.a2a_manager.register_message_handler(self._handle_a2a_message)
        
        # Register with MCP manager
        self.mcp_manager.register_message_handler(self._handle_mcp_message)
    
    def _handle_a2a_message(self, message: Dict) -> None:
        """
        Handle incoming A2A message.
        
        Args:
            message: A2A message
        """
        try:
            # Convert A2A message to internal format
            internal_message = self._convert_a2a_to_internal(message)
            
            # Add to incoming queue
            if internal_message:
                self.incoming_queue.put(internal_message)
                
                if self.config["log_messages"] and logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Received A2A message: {json.dumps(internal_message)}")
        except Exception as e:
            logger.error(f"Error handling A2A message: {str(e)}")
    
    def _handle_mcp_message(self, message: Dict) -> None:
        """
        Handle incoming MCP message.
        
        Args:
            message: MCP message
        """
        try:
            # Convert MCP message to internal format
            internal_message = self._convert_mcp_to_internal(message)
            
            # Add to incoming queue
            if internal_message:
                self.incoming_queue.put(internal_message)
                
                if self.config["log_messages"] and logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Received MCP message: {json.dumps(internal_message)}")
        except Exception as e:
            logger.error(f"Error handling MCP message: {str(e)}")
    
    def _convert_a2a_to_internal(self, a2a_message: Dict) -> Optional[Dict]:
        """
        Convert A2A message to internal format.
        
        Args:
            a2a_message: A2A message
            
        Returns:
            Internal message or None if conversion failed
        """
        try:
            # Extract A2A message components
            message_type = self._determine_message_type_from_a2a(a2a_message)
            
            # Create internal message
            internal_message = {
                "id": a2a_message.get("id", str(uuid.uuid4())),
                "type": message_type,
                "timestamp": a2a_message.get("timestamp", int(time.time() * 1000)),
                "source": {
                    "type": "agent",
                    "id": a2a_message.get("agent_id", "unknown"),
                    "protocol": "a2a"
                },
                "target": {
                    "type": "ui",
                    "id": a2a_message.get("target_id", "ui")
                },
                "payload": a2a_message.get("payload", {}),
                "metadata": {
                    "original_protocol": "a2a",
                    "original_message": a2a_message if self.config["log_messages"] else None
                }
            }
            
            # Add correlation ID if present
            if "correlation_id" in a2a_message:
                internal_message["correlation_id"] = a2a_message["correlation_id"]
            
            return internal_message
        except Exception as e:
            logger.error(f"Error converting A2A message to internal format: {str(e)}")
            return None
    
    def _determine_message_type_from_a2a(self, a2a_message: Dict) -> str:
        """
        Determine message type from A2A message.
        
        Args:
            a2a_message: A2A message
            
        Returns:
            Message type string
        """
        # Check for explicit type
        if "message_type" in a2a_message:
            a2a_type = a2a_message["message_type"]
            
            # Map A2A types to internal types
            type_mapping = {
                "request": MessageType.REQUEST.value,
                "response": MessageType.RESPONSE.value,
                "event": MessageType.EVENT.value,
                "state_update": MessageType.STATE_UPDATE.value,
                "command": MessageType.COMMAND.value,
                "notification": MessageType.NOTIFICATION.value,
                "error": MessageType.ERROR.value
            }
            
            return type_mapping.get(a2a_type, MessageType.EVENT.value)
        
        # Infer type from message structure
        if "error" in a2a_message and a2a_message["error"]:
            return MessageType.ERROR.value
        elif "response" in a2a_message:
            return MessageType.RESPONSE.value
        elif "request" in a2a_message:
            return MessageType.REQUEST.value
        elif "event" in a2a_message:
            return MessageType.EVENT.value
        elif "state" in a2a_message:
            return MessageType.STATE_UPDATE.value
        elif "command" in a2a_message:
            return MessageType.COMMAND.value
        elif "notification" in a2a_message:
            return MessageType.NOTIFICATION.value
        else:
            return MessageType.EVENT.value
    
    def _convert_mcp_to_internal(self, mcp_message: Dict) -> Optional[Dict]:
        """
        Convert MCP message to internal format.
        
        Args:
            mcp_message: MCP message
            
        Returns:
            Internal message or None if conversion failed
        """
        try:
            # Extract MCP message components
            message_type = self._determine_message_type_from_mcp(mcp_message)
            
            # Create internal message
            internal_message = {
                "id": mcp_message.get("message_id", str(uuid.uuid4())),
                "type": message_type,
                "timestamp": mcp_message.get("timestamp", int(time.time() * 1000)),
                "source": {
                    "type": "model",
                    "id": mcp_message.get("model_id", "unknown"),
                    "protocol": "mcp"
                },
                "target": {
                    "type": "ui",
                    "id": mcp_message.get("target_id", "ui")
                },
                "payload": mcp_message.get("content", {}),
                "metadata": {
                    "original_protocol": "mcp",
                    "original_message": mcp_message if self.config["log_messages"] else None,
                    "context": mcp_message.get("context", {})
                }
            }
            
            # Add correlation ID if present
            if "correlation_id" in mcp_message:
                internal_message["correlation_id"] = mcp_message["correlation_id"]
            
            return internal_message
        except Exception as e:
            logger.error(f"Error converting MCP message to internal format: {str(e)}")
            return None
    
    def _determine_message_type_from_mcp(self, mcp_message: Dict) -> str:
        """
        Determine message type from MCP message.
        
        Args:
            mcp_message: MCP message
            
        Returns:
            Message type string
        """
        # Check for explicit type
        if "message_type" in mcp_message:
            mcp_type = mcp_message["message_type"]
            
            # Map MCP types to internal types
            type_mapping = {
                "request": MessageType.REQUEST.value,
                "response": MessageType.RESPONSE.value,
                "event": MessageType.EVENT.value,
                "state_update": MessageType.STATE_UPDATE.value,
                "command": MessageType.COMMAND.value,
                "notification": MessageType.NOTIFICATION.value,
                "error": MessageType.ERROR.value
            }
            
            return type_mapping.get(mcp_type, MessageType.EVENT.value)
        
        # Infer type from message structure
        if "error" in mcp_message and mcp_message["error"]:
            return MessageType.ERROR.value
        elif "response_to" in mcp_message:
            return MessageType.RESPONSE.value
        elif "request" in mcp_message:
            return MessageType.REQUEST.value
        elif "event_type" in mcp_message:
            return MessageType.EVENT.value
        elif "state_update" in mcp_message:
            return MessageType.STATE_UPDATE.value
        elif "command" in mcp_message:
            return MessageType.COMMAND.value
        elif "notification" in mcp_message:
            return MessageType.NOTIFICATION.value
        else:
            return MessageType.EVENT.value
    
    def _convert_internal_to_a2a(self, internal_message: Dict) -> Dict:
        """
        Convert internal message to A2A format.
        
        Args:
            internal_message: Internal message
            
        Returns:
            A2A message
        """
        message_type = internal_message["type"]
        payload = internal_message["payload"]
        
        # Create base A2A message
        a2a_message = {
            "id": internal_message["id"],
            "timestamp": internal_message["timestamp"],
            "agent_id": internal_message["source"]["id"],
            "target_id": internal_message["target"]["id"],
            "message_type": message_type
        }
        
        # Add correlation ID if present
        if "correlation_id" in internal_message:
            a2a_message["correlation_id"] = internal_message["correlation_id"]
        
        # Add type-specific fields
        if message_type == MessageType.REQUEST.value:
            a2a_message["request"] = payload
        elif message_type == MessageType.RESPONSE.value:
            a2a_message["response"] = payload
        elif message_type == MessageType.EVENT.value:
            a2a_message["event"] = payload
        elif message_type == MessageType.STATE_UPDATE.value:
            a2a_message["state"] = payload
        elif message_type == MessageType.COMMAND.value:
            a2a_message["command"] = payload
        elif message_type == MessageType.NOTIFICATION.value:
            a2a_message["notification"] = payload
        elif message_type == MessageType.ERROR.value:
            a2a_message["error"] = payload
        
        return a2a_message
    
    def _convert_internal_to_mcp(self, internal_message: Dict) -> Dict:
        """
        Convert internal message to MCP format.
        
        Args:
            internal_message: Internal message
            
        Returns:
            MCP message
        """
        message_type = internal_message["type"]
        payload = internal_message["payload"]
        
        # Create base MCP message
        mcp_message = {
            "message_id": internal_message["id"],
            "timestamp": internal_message["timestamp"],
            "model_id": internal_message["target"]["id"] if internal_message["target"]["type"] == "model" else "ui",
            "target_id": internal_message["target"]["id"],
            "message_type": message_type,
            "content": payload
        }
        
        # Add correlation ID if present
        if "correlation_id" in internal_message:
            mcp_message["correlation_id"] = internal_message["correlation_id"]
        
        # Add context if present in metadata
        if "metadata" in internal_message and "context" in internal_message["metadata"]:
            mcp_message["context"] = internal_message["metadata"]["context"]
        
        # Add type-specific fields
        if message_type == MessageType.RESPONSE.value and "request_id" in internal_message:
            mcp_message["response_to"] = internal_message["request_id"]
        elif message_type == MessageType.EVENT.value and "event_type" in payload:
            mcp_message["event_type"] = payload["event_type"]
        
        return mcp_message
    
    def _outgoing_worker(self) -> None:
        """Worker thread for processing outgoing messages."""
        while self.running:
            try:
                # Get message from queue (with priority)
                priority, message = self.outgoing_queue.get(timeout=1.0)
                
                # Process message
                self._process_outgoing_message(message)
                
                # Mark task as done
                self.outgoing_queue.task_done()
            except queue.Empty:
                # Queue is empty, continue
                pass
            except Exception as e:
                logger.error(f"Error in outgoing worker: {str(e)}")
    
    def _process_outgoing_message(self, message: Dict) -> None:
        """
        Process an outgoing message.
        
        Args:
            message: Message to process
        """
        try:
            # Determine target protocol
            target_type = message["target"]["type"]
            target_protocol = message["target"].get("protocol")
            
            if not target_protocol:
                # Determine protocol based on target type
                if target_type == "agent":
                    target_protocol = "a2a"
                elif target_type == "model":
                    target_protocol = "mcp"
                else:
                    # Default to A2A for unknown targets
                    target_protocol = "a2a"
            
            # Convert and send message
            if target_protocol == "a2a":
                a2a_message = self._convert_internal_to_a2a(message)
                self.a2a_manager.send_message(a2a_message)
                
                if self.config["log_messages"] and logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Sent A2A message: {json.dumps(a2a_message)}")
            elif target_protocol == "mcp":
                mcp_message = self._convert_internal_to_mcp(message)
                self.mcp_manager.send_message(mcp_message)
                
                if self.config["log_messages"] and logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Sent MCP message: {json.dumps(mcp_message)}")
            else:
                logger.warning(f"Unknown target protocol: {target_protocol}")
        except Exception as e:
            logger.error(f"Error processing outgoing message: {str(e)}")
            
            # Send error response for requests
            if message["type"] == MessageType.REQUEST.value:
                self._send_error_response(
                    message["id"],
                    f"Failed to send message: {str(e)}",
                    message["source"]
                )
    
    def _incoming_worker(self) -> None:
        """Worker thread for processing incoming messages."""
        while self.running:
            try:
                # Get message from queue
                message = self.incoming_queue.get(timeout=1.0)
                
                # Process message
                self._process_incoming_message(message)
                
                # Mark task as done
                self.incoming_queue.task_done()
            except queue.Empty:
                # Queue is empty, continue
                pass
            except Exception as e:
                logger.error(f"Error in incoming worker: {str(e)}")
    
    def _process_incoming_message(self, message: Dict) -> None:
        """
        Process an incoming message.
        
        Args:
            message: Message to process
        """
        try:
            message_type = message["type"]
            message_id = message["id"]
            
            # Update connection state
            self.connected = True
            self.last_heartbeat = time.time()
            
            # Handle responses to pending requests
            if message_type == MessageType.RESPONSE.value and "correlation_id" in message:
                correlation_id = message["correlation_id"]
                if correlation_id in self.pending_requests:
                    # Get callback
                    callback = self.pending_requests.pop(correlation_id)
                    
                    # Call callback with response
                    callback(message)
                    
                    # Cache response if enabled
                    if self.config["enable_local_cache"]:
                        cache_key = f"response:{correlation_id}"
                        self.local_cache[cache_key] = message
                        self.cache_timestamps[cache_key] = time.time()
                    
                    return
            
            # Handle state updates
            if message_type == MessageType.STATE_UPDATE.value:
                # Cache state if enabled
                if self.config["enable_local_cache"]:
                    source_id = message["source"]["id"]
                    cache_key = f"state:{source_id}"
                    self.local_cache[cache_key] = message["payload"]
                    self.cache_timestamps[cache_key] = time.time()
            
            # Dispatch to registered handlers
            if message_type in self.message_handlers:
                handlers = self.message_handlers[message_type]
                
                # Check for specific handler
                if message_id in handlers:
                    handler = handlers[message_id]
                    handler(message)
                
                # Check for wildcard handlers
                if "*" in handlers:
                    wildcard_handler = handlers["*"]
                    wildcard_handler(message)
        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")
    
    def _heartbeat_worker(self) -> None:
        """Worker thread for sending heartbeats and checking connection."""
        while self.running:
            try:
                current_time = time.time()
                
                # Send heartbeat if needed
                if current_time - self.last_heartbeat > self.config["heartbeat_interval"]:
                    self._send_heartbeat()
                
                # Check connection if needed
                if current_time - self.last_heartbeat > self.config["connection_check_interval"]:
                    if not self._check_connection():
                        # Connection lost, try to reconnect
                        self._reconnect()
                
                # Clean up cache if enabled
                if self.config["enable_local_cache"]:
                    self._clean_cache()
                
                # Sleep for a while
                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Error in heartbeat worker: {str(e)}")
    
    def _send_heartbeat(self) -> None:
        """Send heartbeat message."""
        try:
            # Create heartbeat message
            heartbeat_message = {
                "id": str(uuid.uuid4()),
                "type": MessageType.EVENT.value,
                "timestamp": int(time.time() * 1000),
                "source": {
                    "type": "ui",
                    "id": "ui"
                },
                "target": {
                    "type": "system",
                    "id": "system",
                    "protocol": "a2a"
                },
                "payload": {
                    "event_type": "heartbeat",
                    "status": "alive"
                }
            }
            
            # Send heartbeat to both protocols
            a2a_message = self._convert_internal_to_a2a(heartbeat_message)
            self.a2a_manager.send_message(a2a_message)
            
            mcp_message = self._convert_internal_to_mcp(heartbeat_message)
            self.mcp_manager.send_message(mcp_message)
            
            # Update last heartbeat time
            self.last_heartbeat = time.time()
            
            logger.debug("Sent heartbeat")
        except Exception as e:
            logger.error(f"Error sending heartbeat: {str(e)}")
    
    def _check_connection(self) -> bool:
        """
        Check if connection is still active.
        
        Returns:
            Boolean indicating if connection is active
        """
        try:
            # Create ping message
            ping_message = {
                "id": str(uuid.uuid4()),
                "type": MessageType.REQUEST.value,
                "timestamp": int(time.time() * 1000),
                "source": {
                    "type": "ui",
                    "id": "ui"
                },
                "target": {
                    "type": "system",
                    "id": "system",
                    "protocol": "a2a"
                },
                "payload": {
                    "request_type": "ping"
                }
            }
            
            # Send ping to A2A manager
            a2a_message = self._convert_internal_to_a2a(ping_message)
            response = self.a2a_manager.send_message_sync(a2a_message, timeout=5.0)
            
            # Check response
            if response and "response" in response:
                # Update last heartbeat time
                self.last_heartbeat = time.time()
                self.connected = True
                return True
            
            # No valid response
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Error checking connection: {str(e)}")
            self.connected = False
            return False
    
    def _reconnect(self) -> bool:
        """
        Attempt to reconnect.
        
        Returns:
            Boolean indicating if reconnection was successful
        """
        try:
            logger.info("Attempting to reconnect...")
            
            # Try to reconnect A2A manager
            a2a_reconnected = self.a2a_manager.reconnect()
            
            # Try to reconnect MCP manager
            mcp_reconnected = self.mcp_manager.reconnect()
            
            # Update connection state
            self.connected = a2a_reconnected or mcp_reconnected
            
            if self.connected:
                logger.info("Reconnection successful")
                self.last_heartbeat = time.time()
            else:
                logger.warning("Reconnection failed")
            
            return self.connected
        except Exception as e:
            logger.error(f"Error during reconnection: {str(e)}")
            self.connected = False
            return False
    
    def _clean_cache(self) -> None:
        """Clean expired items from cache."""
        try:
            current_time = time.time()
            expired_keys = []
            
            # Find expired items
            for key, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > self.config["cache_ttl"]:
                    expired_keys.append(key)
            
            # Remove expired items
            for key in expired_keys:
                self.local_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
            
            if expired_keys:
                logger.debug(f"Cleaned {len(expired_keys)} expired items from cache")
        except Exception as e:
            logger.error(f"Error cleaning cache: {str(e)}")
    
    def _send_error_response(self, request_id: str, error_message: str, target: Dict) -> None:
        """
        Send error response for a request.
        
        Args:
            request_id: Request ID
            error_message: Error message
            target: Target information
        """
        try:
            # Create error response
            error_response = {
                "id": str(uuid.uuid4()),
                "type": MessageType.ERROR.value,
                "timestamp": int(time.time() * 1000),
                "correlation_id": request_id,
                "source": {
                    "type": "ui",
                    "id": "ui"
                },
                "target": target,
                "payload": {
                    "error": True,
                    "error_message": error_message,
                    "request_id": request_id
                }
            }
            
            # Add to outgoing queue with high priority
            self.outgoing_queue.put((0, error_response))
        except Exception as e:
            logger.error(f"Error sending error response: {str(e)}")
    
    def register_message_handler(
        self,
        message_type: str,
        handler: Callable[[Dict], None],
        message_id: str = "*"
    ) -> None:
        """
        Register a message handler.
        
        Args:
            message_type: Message type
            handler: Handler function
            message_id: Specific message ID or "*" for all messages of this type
        """
        if message_type in self.message_handlers:
            self.message_handlers[message_type][message_id] = handler
            logger.debug(f"Registered handler for {message_type} messages (ID: {message_id})")
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    def unregister_message_handler(self, message_type: str, message_id: str = "*") -> None:
        """
        Unregister a message handler.
        
        Args:
            message_type: Message type
            message_id: Specific message ID or "*" for all messages of this type
        """
        if message_type in self.message_handlers and message_id in self.message_handlers[message_type]:
            del self.message_handlers[message_type][message_id]
            logger.debug(f"Unregistered handler for {message_type} messages (ID: {message_id})")
    
    def send_message(
        self,
        message_type: str,
        payload: Dict,
        target: Dict,
        priority: int = 5,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Send a message.
        
        Args:
            message_type: Message type
            payload: Message payload
            target: Target information
            priority: Message priority (0-9, lower is higher priority)
            correlation_id: Optional correlation ID for responses
            
        Returns:
            Message ID
        """
        try:
            # Create message
            message_id = str(uuid.uuid4())
            message = {
                "id": message_id,
                "type": message_type,
                "timestamp": int(time.time() * 1000),
                "source": {
                    "type": "ui",
                    "id": "ui"
                },
                "target": target,
                "payload": payload
            }
            
            # Add correlation ID if provided
            if correlation_id:
                message["correlation_id"] = correlation_id
            
            # Add to outgoing queue with priority
            self.outgoing_queue.put((priority, message))
            
            return message_id
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return ""
    
    def send_request(
        self,
        request_payload: Dict,
        target: Dict,
        callback: Callable[[Dict], None],
        priority: int = 5,
        timeout: Optional[float] = None
    ) -> str:
        """
        Send a request and register callback for response.
        
        Args:
            request_payload: Request payload
            target: Target information
            callback: Callback function for response
            priority: Message priority (0-9, lower is higher priority)
            timeout: Optional timeout in seconds
            
        Returns:
            Request ID
        """
        try:
            # Create request ID
            request_id = str(uuid.uuid4())
            
            # Register callback
            self.pending_requests[request_id] = callback
            
            # Set timeout if provided
            if timeout:
                threading.Timer(timeout, self._handle_request_timeout, args=[request_id]).start()
            
            # Send request
            message_id = self.send_message(
                MessageType.REQUEST.value,
                request_payload,
                target,
                priority,
                request_id
            )
            
            return message_id
        except Exception as e:
            logger.error(f"Error sending request: {str(e)}")
            return ""
    
    def _handle_request_timeout(self, request_id: str) -> None:
        """
        Handle request timeout.
        
        Args:
            request_id: Request ID
        """
        if request_id in self.pending_requests:
            # Get callback
            callback = self.pending_requests.pop(request_id)
            
            # Create timeout response
            timeout_response = {
                "id": str(uuid.uuid4()),
                "type": MessageType.ERROR.value,
                "timestamp": int(time.time() * 1000),
                "correlation_id": request_id,
                "source": {
                    "type": "system",
                    "id": "system"
                },
                "target": {
                    "type": "ui",
                    "id": "ui"
                },
                "payload": {
                    "error": True,
                    "error_message": "Request timed out",
                    "request_id": request_id
                }
            }
            
            # Call callback with timeout response
            callback(timeout_response)
            
            logger.warning(f"Request timed out: {request_id}")
    
    async def send_request_async(
        self,
        request_payload: Dict,
        target: Dict,
        priority: int = 5,
        timeout: Optional[float] = None
    ) -> Dict:
        """
        Send a request and wait for response asynchronously.
        
        Args:
            request_payload: Request payload
            target: Target information
            priority: Message priority (0-9, lower is higher priority)
            timeout: Optional timeout in seconds
            
        Returns:
            Response message
        """
        # Create future for response
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        # Define callback
        def response_callback(response: Dict) -> None:
            if not future.done():
                loop.call_soon_threadsafe(future.set_result, response)
        
        # Send request
        request_id = self.send_request(
            request_payload,
            target,
            response_callback,
            priority,
            timeout or self.config["message_timeout"]
        )
        
        if not request_id:
            raise Exception("Failed to send request")
        
        # Wait for response
        try:
            response = await asyncio.wait_for(future, timeout or self.config["message_timeout"])
            return response
        except asyncio.TimeoutError:
            # Remove pending request
            self.pending_requests.pop(request_id, None)
            
            # Create timeout response
            timeout_response = {
                "id": str(uuid.uuid4()),
                "type": MessageType.ERROR.value,
                "timestamp": int(time.time() * 1000),
                "correlation_id": request_id,
                "source": {
                    "type": "system",
                    "id": "system"
                },
                "target": {
                    "type": "ui",
                    "id": "ui"
                },
                "payload": {
                    "error": True,
                    "error_message": "Request timed out",
                    "request_id": request_id
                }
            }
            
            return timeout_response
    
    def send_request_sync(
        self,
        request_payload: Dict,
        target: Dict,
        priority: int = 5,
        timeout: Optional[float] = None
    ) -> Dict:
        """
        Send a request and wait for response synchronously.
        
        Args:
            request_payload: Request payload
            target: Target information
            priority: Message priority (0-9, lower is higher priority)
            timeout: Optional timeout in seconds
            
        Returns:
            Response message
        """
        # Create event for synchronization
        response_event = threading.Event()
        response_container = [None]
        
        # Define callback
        def response_callback(response: Dict) -> None:
            response_container[0] = response
            response_event.set()
        
        # Send request
        request_id = self.send_request(
            request_payload,
            target,
            response_callback,
            priority,
            timeout or self.config["message_timeout"]
        )
        
        if not request_id:
            raise Exception("Failed to send request")
        
        # Wait for response
        if response_event.wait(timeout or self.config["message_timeout"]):
            return response_container[0]
        else:
            # Timeout occurred
            self.pending_requests.pop(request_id, None)
            
            # Create timeout response
            timeout_response = {
                "id": str(uuid.uuid4()),
                "type": MessageType.ERROR.value,
                "timestamp": int(time.time() * 1000),
                "correlation_id": request_id,
                "source": {
                    "type": "system",
                    "id": "system"
                },
                "target": {
                    "type": "ui",
                    "id": "ui"
                },
                "payload": {
                    "error": True,
                    "error_message": "Request timed out",
                    "request_id": request_id
                }
            }
            
            return timeout_response
    
    def send_response(
        self,
        response_payload: Dict,
        request_id: str,
        target: Dict,
        priority: int = 3
    ) -> str:
        """
        Send a response to a request.
        
        Args:
            response_payload: Response payload
            request_id: Request ID
            target: Target information
            priority: Message priority (0-9, lower is higher priority)
            
        Returns:
            Response ID
        """
        try:
            # Create response
            response_id = str(uuid.uuid4())
            response = {
                "id": response_id,
                "type": MessageType.RESPONSE.value,
                "timestamp": int(time.time() * 1000),
                "correlation_id": request_id,
                "source": {
                    "type": "ui",
                    "id": "ui"
                },
                "target": target,
                "payload": response_payload
            }
            
            # Add to outgoing queue with priority
            self.outgoing_queue.put((priority, response))
            
            return response_id
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")
            return ""
    
    def send_event(
        self,
        event_payload: Dict,
        target: Dict,
        priority: int = 5
    ) -> str:
        """
        Send an event.
        
        Args:
            event_payload: Event payload
            target: Target information
            priority: Message priority (0-9, lower is higher priority)
            
        Returns:
            Event ID
        """
        return self.send_message(
            MessageType.EVENT.value,
            event_payload,
            target,
            priority
        )
    
    def send_state_update(
        self,
        state_payload: Dict,
        target: Dict,
        priority: int = 4
    ) -> str:
        """
        Send a state update.
        
        Args:
            state_payload: State payload
            target: Target information
            priority: Message priority (0-9, lower is higher priority)
            
        Returns:
            Update ID
        """
        return self.send_message(
            MessageType.STATE_UPDATE.value,
            state_payload,
            target,
            priority
        )
    
    def send_command(
        self,
        command_payload: Dict,
        target: Dict,
        priority: int = 2
    ) -> str:
        """
        Send a command.
        
        Args:
            command_payload: Command payload
            target: Target information
            priority: Message priority (0-9, lower is higher priority)
            
        Returns:
            Command ID
        """
        return self.send_message(
            MessageType.COMMAND.value,
            command_payload,
            target,
            priority
        )
    
    def send_notification(
        self,
        notification_payload: Dict,
        target: Dict,
        priority: int = 4
    ) -> str:
        """
        Send a notification.
        
        Args:
            notification_payload: Notification payload
            target: Target information
            priority: Message priority (0-9, lower is higher priority)
            
        Returns:
            Notification ID
        """
        return self.send_message(
            MessageType.NOTIFICATION.value,
            notification_payload,
            target,
            priority
        )
    
    def get_cached_state(self, source_id: str) -> Optional[Dict]:
        """
        Get cached state for a source.
        
        Args:
            source_id: Source identifier
            
        Returns:
            Cached state or None if not found
        """
        if not self.config["enable_local_cache"]:
            return None
        
        cache_key = f"state:{source_id}"
        if cache_key in self.local_cache:
            # Check if expired
            if time.time() - self.cache_timestamps[cache_key] <= self.config["cache_ttl"]:
                return self.local_cache[cache_key]
            else:
                # Remove expired item
                self.local_cache.pop(cache_key, None)
                self.cache_timestamps.pop(cache_key, None)
        
        return None
    
    def get_cached_response(self, request_id: str) -> Optional[Dict]:
        """
        Get cached response for a request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Cached response or None if not found
        """
        if not self.config["enable_local_cache"]:
            return None
        
        cache_key = f"response:{request_id}"
        if cache_key in self.local_cache:
            # Check if expired
            if time.time() - self.cache_timestamps[cache_key] <= self.config["cache_ttl"]:
                return self.local_cache[cache_key]
            else:
                # Remove expired item
                self.local_cache.pop(cache_key, None)
                self.cache_timestamps.pop(cache_key, None)
        
        return None
    
    def clear_cache(self) -> None:
        """Clear the local cache."""
        self.local_cache.clear()
        self.cache_timestamps.clear()
        logger.debug("Cache cleared")
    
    def is_connected(self) -> bool:
        """
        Check if connected to protocol managers.
        
        Returns:
            Boolean indicating connection status
        """
        return self.connected
    
    def shutdown(self) -> None:
        """Shutdown the Agent Interaction Protocol."""
        logger.info("Shutting down Agent Interaction Protocol")
        
        # Stop worker threads
        self.running = False
        
        # Wait for threads to finish
        self.outgoing_thread.join(timeout=2.0)
        self.incoming_thread.join(timeout=2.0)
        self.heartbeat_thread.join(timeout=2.0)
        
        # Clear pending requests
        self.pending_requests.clear()
        
        # Clear cache
        self.clear_cache()
