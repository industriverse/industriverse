"""
Protocol Bridge for the Integration Layer.

This module provides protocol bridge functionality for the Integration Layer,
enabling seamless communication between different protocols and systems.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Callable

# Import MCP and A2A integration
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class ProtocolBridge:
    """
    Protocol Bridge for the Integration Layer.
    
    This class provides protocol translation and bridging functionality,
    enabling seamless communication between different protocols and systems.
    """
    
    def __init__(
        self,
        bridge_id: str,
        bridge_name: str,
        source_protocol: str,
        target_protocol: str,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        config_service: ConfigService,
        auth_service: AuthService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the protocol bridge.
        
        Args:
            bridge_id: Unique identifier for this bridge
            bridge_name: Human-readable name for this bridge
            source_protocol: Source protocol identifier
            target_protocol: Target protocol identifier
            mcp_bridge: MCP protocol bridge for internal communication
            a2a_bridge: A2A protocol bridge for external communication
            event_bus: Event bus client for event-driven communication
            data_access: Data access service for persistence
            config_service: Configuration service for settings
            auth_service: Authentication service for security
            logger: Optional logger instance
        """
        self.bridge_id = bridge_id
        self.bridge_name = bridge_name
        self.source_protocol = source_protocol
        self.target_protocol = target_protocol
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus
        self.data_access = data_access
        self.config_service = config_service
        self.auth_service = auth_service
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize status
        self.status = "initialized"
        self.health = "unknown"
        
        # Initialize translation mappings
        self._source_to_target_mappings: Dict[str, Dict[str, Any]] = {}
        self._target_to_source_mappings: Dict[str, Dict[str, Any]] = {}
        
        # Initialize event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Initialize message queues
        self._source_message_queue: List[Dict[str, Any]] = []
        self._target_message_queue: List[Dict[str, Any]] = []
        
        # Initialize statistics
        self._statistics = {
            "source_to_target_messages": 0,
            "target_to_source_messages": 0,
            "source_to_target_errors": 0,
            "target_to_source_errors": 0,
            "last_source_to_target_timestamp": None,
            "last_target_to_source_timestamp": None
        }
        
        self.logger.info(f"Protocol bridge {bridge_name} ({bridge_id}) initialized")
    
    def initialize(self) -> None:
        """Initialize this protocol bridge."""
        try:
            # Register with MCP
            self._register_with_mcp()
            
            # Register with A2A
            self._register_with_a2a()
            
            # Subscribe to events
            self._subscribe_to_events()
            
            # Load translation mappings
            self._load_translation_mappings()
            
            self.logger.info(f"Protocol bridge {self.bridge_name} initialized")
        except Exception as e:
            self.logger.error(f"Error initializing protocol bridge {self.bridge_name}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def _register_with_mcp(self) -> None:
        """Register this protocol bridge with the MCP protocol."""
        try:
            self.mcp_bridge.register_context_provider(
                provider_id=self.bridge_id,
                provider_name=self.bridge_name,
                provider_type="protocol_bridge",
                context_types=[
                    "protocol_bridge",
                    f"protocol_bridge.{self.source_protocol}",
                    f"protocol_bridge.{self.target_protocol}"
                ]
            )
            self.logger.info(f"Registered protocol bridge {self.bridge_name} with MCP")
        except Exception as e:
            self.logger.error(f"Failed to register protocol bridge {self.bridge_name} with MCP: {str(e)}")
            raise
    
    def _register_with_a2a(self) -> None:
        """Register this protocol bridge with the A2A protocol."""
        try:
            self.a2a_bridge.register_agent(
                agent_id=self.bridge_id,
                agent_name=self.bridge_name,
                agent_type="protocol_bridge",
                capabilities=[
                    {
                        "type": "protocol_translation",
                        "source_protocol": self.source_protocol,
                        "target_protocol": self.target_protocol,
                        "description": f"Translates between {self.source_protocol} and {self.target_protocol} protocols"
                    }
                ]
            )
            self.logger.info(f"Registered protocol bridge {self.bridge_name} with A2A")
        except Exception as e:
            self.logger.error(f"Failed to register protocol bridge {self.bridge_name} with A2A: {str(e)}")
            raise
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events on the event bus."""
        try:
            # Subscribe to bridge-specific events
            self.event_bus.subscribe(
                topic=f"integration.protocol_bridge.{self.bridge_id}.command",
                group_id=f"{self.bridge_id}-command-handler",
                callback=self._handle_command_event
            )
            
            # Subscribe to source protocol events
            self.event_bus.subscribe(
                topic=f"protocol.{self.source_protocol}.message",
                group_id=f"{self.bridge_id}-source-message-handler",
                callback=self._handle_source_message
            )
            
            # Subscribe to target protocol events
            self.event_bus.subscribe(
                topic=f"protocol.{self.target_protocol}.message",
                group_id=f"{self.bridge_id}-target-message-handler",
                callback=self._handle_target_message
            )
            
            # Subscribe to health check events
            self.event_bus.subscribe(
                topic="system.health.check",
                group_id=f"{self.bridge_id}-health-check-handler",
                callback=self._handle_health_check_event
            )
            
            self.logger.info(f"Subscribed protocol bridge {self.bridge_name} to events")
        except Exception as e:
            self.logger.error(f"Failed to subscribe protocol bridge {self.bridge_name} to events: {str(e)}")
            raise
    
    def _load_translation_mappings(self) -> None:
        """Load translation mappings from configuration."""
        try:
            # Load source-to-target mappings
            source_to_target_config = self.config_service.get_config(
                f"protocol_bridge.{self.bridge_id}.source_to_target_mappings",
                {}
            )
            self._source_to_target_mappings = source_to_target_config
            
            # Load target-to-source mappings
            target_to_source_config = self.config_service.get_config(
                f"protocol_bridge.{self.bridge_id}.target_to_source_mappings",
                {}
            )
            self._target_to_source_mappings = target_to_source_config
            
            self.logger.info(f"Loaded translation mappings for protocol bridge {self.bridge_name}")
        except Exception as e:
            self.logger.error(f"Failed to load translation mappings for protocol bridge {self.bridge_name}: {str(e)}")
            raise
    
    def _handle_command_event(self, event: Dict[str, Any]) -> None:
        """
        Handle bridge-specific command events.
        
        Args:
            event: Command event data
        """
        try:
            command = event.get("command")
            if not command:
                self.logger.warning(f"Received command event without command: {event}")
                return
            
            command_id = event.get("command_id", str(uuid.uuid4()))
            
            self.logger.info(f"Handling command {command} ({command_id})")
            
            if command == "start":
                self.start()
                self._publish_command_response(command_id, command, "success")
            elif command == "stop":
                self.stop()
                self._publish_command_response(command_id, command, "success")
            elif command == "restart":
                self.restart()
                self._publish_command_response(command_id, command, "success")
            elif command == "status":
                self._publish_status(command_id)
            elif command == "update_mappings":
                source_to_target = event.get("source_to_target_mappings")
                target_to_source = event.get("target_to_source_mappings")
                self.update_mappings(source_to_target, target_to_source)
                self._publish_command_response(command_id, command, "success")
            elif command == "translate_message":
                source_protocol = event.get("source_protocol")
                target_protocol = event.get("target_protocol")
                message = event.get("message")
                
                if source_protocol == self.source_protocol and target_protocol == self.target_protocol:
                    translated_message = self.translate_source_to_target(message)
                    self._publish_command_response(command_id, command, "success", {"translated_message": translated_message})
                elif source_protocol == self.target_protocol and target_protocol == self.source_protocol:
                    translated_message = self.translate_target_to_source(message)
                    self._publish_command_response(command_id, command, "success", {"translated_message": translated_message})
                else:
                    self._publish_command_response(
                        command_id,
                        command,
                        "error",
                        {"error": f"Unsupported protocol translation: {source_protocol} to {target_protocol}"}
                    )
            else:
                self._publish_command_response(
                    command_id,
                    command,
                    "error",
                    {"error": f"Unsupported command: {command}"}
                )
        except Exception as e:
            self.logger.error(f"Error handling command event: {str(e)}")
            
            # Publish error response
            self._publish_command_response(
                command_id=event.get("command_id", str(uuid.uuid4())),
                command=event.get("command"),
                status="error",
                result={"error": str(e)}
            )
    
    def _handle_source_message(self, event: Dict[str, Any]) -> None:
        """
        Handle messages from the source protocol.
        
        Args:
            event: Message event data
        """
        try:
            # Check if bridge is running
            if self.status != "running":
                self.logger.warning(f"Received source message while bridge is not running: {event}")
                return
            
            # Add message to queue
            self._source_message_queue.append(event)
            
            # Process message
            self._process_source_message_queue()
        except Exception as e:
            self.logger.error(f"Error handling source message: {str(e)}")
            self._statistics["source_to_target_errors"] += 1
    
    def _handle_target_message(self, event: Dict[str, Any]) -> None:
        """
        Handle messages from the target protocol.
        
        Args:
            event: Message event data
        """
        try:
            # Check if bridge is running
            if self.status != "running":
                self.logger.warning(f"Received target message while bridge is not running: {event}")
                return
            
            # Add message to queue
            self._target_message_queue.append(event)
            
            # Process message
            self._process_target_message_queue()
        except Exception as e:
            self.logger.error(f"Error handling target message: {str(e)}")
            self._statistics["target_to_source_errors"] += 1
    
    def _handle_health_check_event(self, event: Dict[str, Any]) -> None:
        """
        Handle health check events.
        
        Args:
            event: Health check event data
        """
        try:
            check_id = event.get("check_id", str(uuid.uuid4()))
            
            # Perform health check
            health_status = self.check_health()
            
            # Publish health status
            self.event_bus.publish(
                topic="system.health.status",
                key=check_id,
                value={
                    "bridge_id": self.bridge_id,
                    "bridge_name": self.bridge_name,
                    "check_id": check_id,
                    "status": health_status,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
        except Exception as e:
            self.logger.error(f"Error handling health check event: {str(e)}")
            
            # Publish error status
            self.event_bus.publish(
                topic="system.health.status",
                key=event.get("check_id", str(uuid.uuid4())),
                value={
                    "bridge_id": self.bridge_id,
                    "bridge_name": self.bridge_name,
                    "check_id": event.get("check_id", str(uuid.uuid4())),
                    "status": "error",
                    "error": str(e),
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
    
    def _publish_command_response(
        self,
        command_id: str,
        command: str,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Publish a command response event.
        
        Args:
            command_id: Command ID for correlation
            command: Command that was executed
            status: Status of the command execution
            result: Optional result data
        """
        try:
            self.event_bus.publish(
                topic=f"integration.protocol_bridge.{self.bridge_id}.response",
                key=command_id,
                value={
                    "bridge_id": self.bridge_id,
                    "bridge_name": self.bridge_name,
                    "command_id": command_id,
                    "command": command,
                    "status": status,
                    "result": result or {},
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
        except Exception as e:
            self.logger.error(f"Error publishing command response: {str(e)}")
    
    def _publish_status(self, command_id: str) -> None:
        """
        Publish the current status of this protocol bridge.
        
        Args:
            command_id: Command ID for correlation
        """
        try:
            # Publish status
            self.event_bus.publish(
                topic=f"integration.protocol_bridge.{self.bridge_id}.status",
                key=command_id,
                value={
                    "bridge_id": self.bridge_id,
                    "bridge_name": self.bridge_name,
                    "command_id": command_id,
                    "status": self.status,
                    "health": self.health,
                    "source_protocol": self.source_protocol,
                    "target_protocol": self.target_protocol,
                    "statistics": self._statistics,
                    "source_queue_size": len(self._source_message_queue),
                    "target_queue_size": len(self._target_message_queue),
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
        except Exception as e:
            self.logger.error(f"Error publishing status: {str(e)}")
            
            # Publish error status
            self.event_bus.publish(
                topic=f"integration.protocol_bridge.{self.bridge_id}.status",
                key=command_id,
                value={
                    "bridge_id": self.bridge_id,
                    "bridge_name": self.bridge_name,
                    "command_id": command_id,
                    "status": "error",
                    "error": str(e),
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
    
    def _process_source_message_queue(self) -> None:
        """Process messages in the source message queue."""
        while self._source_message_queue:
            # Get next message
            message = self._source_message_queue.pop(0)
            
            try:
                # Translate message
                translated_message = self.translate_source_to_target(message)
                
                # Publish translated message
                self.event_bus.publish(
                    topic=f"protocol.{self.target_protocol}.message",
                    key=message.get("message_id", str(uuid.uuid4())),
                    value=translated_message
                )
                
                # Update statistics
                self._statistics["source_to_target_messages"] += 1
                self._statistics["last_source_to_target_timestamp"] = self.data_access.get_current_timestamp()
            except Exception as e:
                self.logger.error(f"Error translating source message: {str(e)}")
                self._statistics["source_to_target_errors"] += 1
    
    def _process_target_message_queue(self) -> None:
        """Process messages in the target message queue."""
        while self._target_message_queue:
            # Get next message
            message = self._target_message_queue.pop(0)
            
            try:
                # Translate message
                translated_message = self.translate_target_to_source(message)
                
                # Publish translated message
                self.event_bus.publish(
                    topic=f"protocol.{self.source_protocol}.message",
                    key=message.get("message_id", str(uuid.uuid4())),
                    value=translated_message
                )
                
                # Update statistics
                self._statistics["target_to_source_messages"] += 1
                self._statistics["last_target_to_source_timestamp"] = self.data_access.get_current_timestamp()
            except Exception as e:
                self.logger.error(f"Error translating target message: {str(e)}")
                self._statistics["target_to_source_errors"] += 1
    
    def start(self) -> None:
        """Start this protocol bridge."""
        try:
            self.logger.info(f"Starting protocol bridge {self.bridge_name}")
            
            # Update status
            self.status = "running"
            
            # Publish status update
            self.event_bus.publish(
                topic=f"integration.protocol_bridge.{self.bridge_id}.event",
                key="status_update",
                value={
                    "bridge_id": self.bridge_id,
                    "bridge_name": self.bridge_name,
                    "event_type": "status_update",
                    "status": self.status,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Protocol bridge {self.bridge_name} started")
        except Exception as e:
            self.logger.error(f"Error starting protocol bridge {self.bridge_name}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def stop(self) -> None:
        """Stop this protocol bridge."""
        try:
            self.logger.info(f"Stopping protocol bridge {self.bridge_name}")
            
            # Update status
            self.status = "stopped"
            
            # Publish status update
            self.event_bus.publish(
                topic=f"integration.protocol_bridge.{self.bridge_id}.event",
                key="status_update",
                value={
                    "bridge_id": self.bridge_id,
                    "bridge_name": self.bridge_name,
                    "event_type": "status_update",
                    "status": self.status,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Protocol bridge {self.bridge_name} stopped")
        except Exception as e:
            self.logger.error(f"Error stopping protocol bridge {self.bridge_name}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def restart(self) -> None:
        """Restart this protocol bridge."""
        try:
            self.logger.info(f"Restarting protocol bridge {self.bridge_name}")
            
            # Stop bridge
            self.stop()
            
            # Start bridge
            self.start()
            
            self.logger.info(f"Protocol bridge {self.bridge_name} restarted")
        except Exception as e:
            self.logger.error(f"Error restarting protocol bridge {self.bridge_name}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def shutdown(self) -> None:
        """Shutdown this protocol bridge and release all resources."""
        try:
            self.logger.info(f"Shutting down protocol bridge {self.bridge_name}")
            
            # Stop bridge if running
            if self.status == "running":
                self.stop()
            
            # Unsubscribe from events
            self._unsubscribe_from_events()
            
            # Unregister from MCP
            self._unregister_from_mcp()
            
            # Unregister from A2A
            self._unregister_from_a2a()
            
            # Update status
            self.status = "shutdown"
            
            self.logger.info(f"Protocol bridge {self.bridge_name} shut down")
        except Exception as e:
            self.logger.error(f"Error shutting down protocol bridge {self.bridge_name}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events on the event bus."""
        try:
            # Unsubscribe from bridge-specific events
            self.event_bus.unsubscribe(
                topic=f"integration.protocol_bridge.{self.bridge_id}.command",
                group_id=f"{self.bridge_id}-command-handler"
            )
            
            # Unsubscribe from source protocol events
            self.event_bus.unsubscribe(
                topic=f"protocol.{self.source_protocol}.message",
                group_id=f"{self.bridge_id}-source-message-handler"
            )
            
            # Unsubscribe from target protocol events
            self.event_bus.unsubscribe(
                topic=f"protocol.{self.target_protocol}.message",
                group_id=f"{self.bridge_id}-target-message-handler"
            )
            
            # Unsubscribe from health check events
            self.event_bus.unsubscribe(
                topic="system.health.check",
                group_id=f"{self.bridge_id}-health-check-handler"
            )
            
            self.logger.info(f"Unsubscribed protocol bridge {self.bridge_name} from events")
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe protocol bridge {self.bridge_name} from events: {str(e)}")
            raise
    
    def _unregister_from_mcp(self) -> None:
        """Unregister this protocol bridge from the MCP protocol."""
        try:
            self.mcp_bridge.unregister_context_provider(
                provider_id=self.bridge_id
            )
            self.logger.info(f"Unregistered protocol bridge {self.bridge_name} from MCP")
        except Exception as e:
            self.logger.error(f"Failed to unregister protocol bridge {self.bridge_name} from MCP: {str(e)}")
            raise
    
    def _unregister_from_a2a(self) -> None:
        """Unregister this protocol bridge from the A2A protocol."""
        try:
            self.a2a_bridge.unregister_agent(
                agent_id=self.bridge_id
            )
            self.logger.info(f"Unregistered protocol bridge {self.bridge_name} from A2A")
        except Exception as e:
            self.logger.error(f"Failed to unregister protocol bridge {self.bridge_name} from A2A: {str(e)}")
            raise
    
    def check_health(self) -> str:
        """
        Check the health of this protocol bridge.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        try:
            self.logger.info(f"Checking health of protocol bridge {self.bridge_name}")
            
            # Check if bridge is running
            if self.status != "running":
                self.health = "degraded"
                return "degraded"
            
            # Check error rates
            total_messages = (
                self._statistics["source_to_target_messages"] +
                self._statistics["target_to_source_messages"]
            )
            total_errors = (
                self._statistics["source_to_target_errors"] +
                self._statistics["target_to_source_errors"]
            )
            
            if total_messages == 0:
                # No messages processed yet
                health = "healthy"
            elif total_errors / total_messages > 0.1:
                # Error rate > 10%
                health = "unhealthy"
            elif total_errors / total_messages > 0.01:
                # Error rate > 1%
                health = "degraded"
            else:
                # Error rate <= 1%
                health = "healthy"
            
            # Update health status
            self.health = health
            
            self.logger.info(f"Health of protocol bridge {self.bridge_name}: {health}")
            
            return health
        except Exception as e:
            self.logger.error(f"Error checking health of protocol bridge {self.bridge_name}: {str(e)}")
            self.health = "unhealthy"
            return "unhealthy"
    
    def update_mappings(
        self,
        source_to_target_mappings: Optional[Dict[str, Dict[str, Any]]] = None,
        target_to_source_mappings: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """
        Update translation mappings.
        
        Args:
            source_to_target_mappings: Source-to-target translation mappings
            target_to_source_mappings: Target-to-source translation mappings
        """
        try:
            self.logger.info(f"Updating translation mappings for protocol bridge {self.bridge_name}")
            
            # Update source-to-target mappings
            if source_to_target_mappings is not None:
                self._source_to_target_mappings.update(source_to_target_mappings)
                
                # Save to configuration
                self.config_service.set_config(
                    f"protocol_bridge.{self.bridge_id}.source_to_target_mappings",
                    self._source_to_target_mappings
                )
            
            # Update target-to-source mappings
            if target_to_source_mappings is not None:
                self._target_to_source_mappings.update(target_to_source_mappings)
                
                # Save to configuration
                self.config_service.set_config(
                    f"protocol_bridge.{self.bridge_id}.target_to_source_mappings",
                    self._target_to_source_mappings
                )
            
            self.logger.info(f"Updated translation mappings for protocol bridge {self.bridge_name}")
        except Exception as e:
            self.logger.error(f"Error updating translation mappings for protocol bridge {self.bridge_name}: {str(e)}")
            raise
    
    def translate_source_to_target(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate a message from the source protocol to the target protocol.
        
        Args:
            message: Source protocol message
        
        Returns:
            Translated target protocol message
        
        Raises:
            ValueError: If message cannot be translated
        """
        try:
            # Get message type
            message_type = message.get("type")
            if not message_type:
                raise ValueError("Message has no type")
            
            # Get mapping for this message type
            mapping = self._source_to_target_mappings.get(message_type)
            if not mapping:
                raise ValueError(f"No mapping for message type: {message_type}")
            
            # Create translated message
            translated_message = {
                "message_id": message.get("message_id", str(uuid.uuid4())),
                "type": mapping.get("target_type"),
                "source_message_id": message.get("message_id"),
                "source_protocol": self.source_protocol,
                "target_protocol": self.target_protocol,
                "timestamp": self.data_access.get_current_timestamp()
            }
            
            # Apply field mappings
            for source_field, target_field in mapping.get("field_mappings", {}).items():
                if source_field in message:
                    translated_message[target_field] = message[source_field]
            
            # Apply transformations
            for target_field, transform in mapping.get("transformations", {}).items():
                if transform["type"] == "constant":
                    translated_message[target_field] = transform["value"]
                elif transform["type"] == "template":
                    template = transform["template"]
                    for placeholder, source_field in transform.get("placeholders", {}).items():
                        if source_field in message:
                            template = template.replace(f"{{{placeholder}}}", str(message[source_field]))
                    translated_message[target_field] = template
                elif transform["type"] == "function":
                    function_name = transform["function"]
                    if hasattr(self, function_name) and callable(getattr(self, function_name)):
                        function = getattr(self, function_name)
                        translated_message[target_field] = function(message, transform.get("params", {}))
            
            return translated_message
        except Exception as e:
            self.logger.error(f"Error translating source message: {str(e)}")
            raise ValueError(f"Error translating source message: {str(e)}")
    
    def translate_target_to_source(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate a message from the target protocol to the source protocol.
        
        Args:
            message: Target protocol message
        
        Returns:
            Translated source protocol message
        
        Raises:
            ValueError: If message cannot be translated
        """
        try:
            # Get message type
            message_type = message.get("type")
            if not message_type:
                raise ValueError("Message has no type")
            
            # Get mapping for this message type
            mapping = self._target_to_source_mappings.get(message_type)
            if not mapping:
                raise ValueError(f"No mapping for message type: {message_type}")
            
            # Create translated message
            translated_message = {
                "message_id": message.get("message_id", str(uuid.uuid4())),
                "type": mapping.get("source_type"),
                "source_message_id": message.get("message_id"),
                "source_protocol": self.target_protocol,
                "target_protocol": self.source_protocol,
                "timestamp": self.data_access.get_current_timestamp()
            }
            
            # Apply field mappings
            for target_field, source_field in mapping.get("field_mappings", {}).items():
                if target_field in message:
                    translated_message[source_field] = message[target_field]
            
            # Apply transformations
            for source_field, transform in mapping.get("transformations", {}).items():
                if transform["type"] == "constant":
                    translated_message[source_field] = transform["value"]
                elif transform["type"] == "template":
                    template = transform["template"]
                    for placeholder, target_field in transform.get("placeholders", {}).items():
                        if target_field in message:
                            template = template.replace(f"{{{placeholder}}}", str(message[target_field]))
                    translated_message[source_field] = template
                elif transform["type"] == "function":
                    function_name = transform["function"]
                    if hasattr(self, function_name) and callable(getattr(self, function_name)):
                        function = getattr(self, function_name)
                        translated_message[source_field] = function(message, transform.get("params", {}))
            
            return translated_message
        except Exception as e:
            self.logger.error(f"Error translating target message: {str(e)}")
            raise ValueError(f"Error translating target message: {str(e)}")
    
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Add an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Event handler function
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        self._event_handlers[event_type].append(handler)
        
        self.logger.debug(f"Added event handler for {event_type}")
    
    def remove_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Remove an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Event handler function
        """
        if event_type in self._event_handlers:
            if handler in self._event_handlers[event_type]:
                self._event_handlers[event_type].remove(handler)
                self.logger.debug(f"Removed event handler for {event_type}")
    
    def trigger_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Trigger an event and call all registered handlers.
        
        Args:
            event_type: Type of event to trigger
            event_data: Event data
        """
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {str(e)}")
        
        # Publish event to event bus
        self.event_bus.publish(
            topic=f"integration.protocol_bridge.{self.bridge_id}.event",
            key=event_type,
            value={
                "bridge_id": self.bridge_id,
                "bridge_name": self.bridge_name,
                "event_type": event_type,
                **event_data,
                "timestamp": self.data_access.get_current_timestamp()
            }
        )
