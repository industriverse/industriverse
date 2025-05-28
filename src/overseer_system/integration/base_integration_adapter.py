"""
Base Integration Adapter for the Overseer System.

This module provides the base integration adapter class that all specific
integration adapters will inherit from. It defines common functionality
for integrating with Industriverse layers and external systems.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Callable

# Import MCP and A2A integration
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class BaseIntegrationAdapter(ABC):
    """
    Base class for all integration adapters in the Overseer System.
    
    This class provides common functionality for integrating with
    Industriverse layers and external systems, including MCP/A2A protocol
    integration, event bus integration, and configuration management.
    """
    
    def __init__(
        self,
        adapter_id: str,
        manager: Any,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        config_service: ConfigService,
        auth_service: AuthService,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the base integration adapter.
        
        Args:
            adapter_id: Unique identifier for this adapter
            manager: Parent integration manager
            mcp_bridge: MCP protocol bridge for internal communication
            a2a_bridge: A2A protocol bridge for external communication
            event_bus: Event bus client for event-driven communication
            data_access: Data access service for persistence
            config_service: Configuration service for settings
            auth_service: Authentication service for security
            config: Adapter-specific configuration
            logger: Optional logger instance
        """
        self.adapter_id = adapter_id
        self.manager = manager
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus
        self.data_access = data_access
        self.config_service = config_service
        self.auth_service = auth_service
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize status
        self.status = "initialized"
        self.health = "unknown"
        
        # Initialize event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        self.logger.info(f"Integration adapter {adapter_id} initialized")
    
    def initialize(self) -> None:
        """Initialize this adapter."""
        try:
            # Register with MCP
            self._register_with_mcp()
            
            # Register with A2A
            self._register_with_a2a()
            
            # Subscribe to events
            self._subscribe_to_events()
            
            # Initialize adapter-specific resources
            self._initialize_resources()
            
            self.logger.info(f"Integration adapter {self.adapter_id} initialized")
        except Exception as e:
            self.logger.error(f"Error initializing adapter {self.adapter_id}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def _register_with_mcp(self) -> None:
        """Register this adapter with the MCP protocol."""
        try:
            self.mcp_bridge.register_context_provider(
                provider_id=self.adapter_id,
                provider_name=f"{self.manager.integration_name} - {self.adapter_id}",
                provider_type="integration_adapter",
                context_types=self._get_supported_context_types()
            )
            self.logger.info(f"Registered adapter {self.adapter_id} with MCP")
        except Exception as e:
            self.logger.error(f"Failed to register adapter {self.adapter_id} with MCP: {str(e)}")
            raise
    
    def _register_with_a2a(self) -> None:
        """Register this adapter with the A2A protocol."""
        try:
            self.a2a_bridge.register_agent(
                agent_id=self.adapter_id,
                agent_name=f"{self.manager.integration_name} - {self.adapter_id}",
                agent_type="integration_adapter",
                capabilities=self._get_supported_capabilities()
            )
            self.logger.info(f"Registered adapter {self.adapter_id} with A2A")
        except Exception as e:
            self.logger.error(f"Failed to register adapter {self.adapter_id} with A2A: {str(e)}")
            raise
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events on the event bus."""
        try:
            # Subscribe to adapter-specific events
            self.event_bus.subscribe(
                topic=f"integration.adapter.{self.adapter_id}.command",
                group_id=f"{self.adapter_id}-command-handler",
                callback=self._handle_command_event
            )
            
            # Subscribe to adapter-specific events from the integration manager
            self.event_bus.subscribe(
                topic=f"integration.{self.manager.integration_id}.adapter.command",
                group_id=f"{self.adapter_id}-manager-command-handler",
                callback=self._handle_manager_command_event
            )
            
            # Subscribe to additional events
            self._subscribe_to_additional_events()
            
            self.logger.info(f"Subscribed adapter {self.adapter_id} to events")
        except Exception as e:
            self.logger.error(f"Failed to subscribe adapter {self.adapter_id} to events: {str(e)}")
            raise
    
    def _handle_command_event(self, event: Dict[str, Any]) -> None:
        """
        Handle adapter-specific command events.
        
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
            elif command == "configure":
                config = event.get("config", {})
                self.configure(config)
                self._publish_command_response(command_id, command, "success")
            else:
                # Handle custom commands
                result = self._handle_custom_command(command, event)
                self._publish_command_response(command_id, command, "success", result)
        except Exception as e:
            self.logger.error(f"Error handling command event: {str(e)}")
            
            # Publish error response
            self._publish_command_response(
                command_id=event.get("command_id", str(uuid.uuid4())),
                command=event.get("command"),
                status="error",
                result={"error": str(e)}
            )
    
    def _handle_manager_command_event(self, event: Dict[str, Any]) -> None:
        """
        Handle command events from the integration manager.
        
        Args:
            event: Command event data
        """
        try:
            # Check if this event is for this adapter
            target_adapter = event.get("adapter_id")
            if target_adapter and target_adapter != self.adapter_id:
                return
            
            # Process the command
            self._handle_command_event(event)
        except Exception as e:
            self.logger.error(f"Error handling manager command event: {str(e)}")
    
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
                topic=f"integration.adapter.{self.adapter_id}.response",
                key=command_id,
                value={
                    "adapter_id": self.adapter_id,
                    "integration_id": self.manager.integration_id,
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
        Publish the current status of this adapter.
        
        Args:
            command_id: Command ID for correlation
        """
        try:
            # Get adapter status
            status_data = self._get_status_data()
            
            # Publish status
            self.event_bus.publish(
                topic=f"integration.adapter.{self.adapter_id}.status",
                key=command_id,
                value={
                    "adapter_id": self.adapter_id,
                    "integration_id": self.manager.integration_id,
                    "command_id": command_id,
                    "status": self.status,
                    "health": self.health,
                    "data": status_data,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
        except Exception as e:
            self.logger.error(f"Error publishing status: {str(e)}")
            
            # Publish error status
            self.event_bus.publish(
                topic=f"integration.adapter.{self.adapter_id}.status",
                key=command_id,
                value={
                    "adapter_id": self.adapter_id,
                    "integration_id": self.manager.integration_id,
                    "command_id": command_id,
                    "status": "error",
                    "error": str(e),
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
    
    def start(self) -> None:
        """Start this adapter."""
        try:
            self.logger.info(f"Starting adapter {self.adapter_id}")
            
            # Start adapter-specific resources
            self._start_resources()
            
            # Update status
            self.status = "running"
            
            # Publish status update
            self.event_bus.publish(
                topic=f"integration.adapter.{self.adapter_id}.event",
                key="status_update",
                value={
                    "adapter_id": self.adapter_id,
                    "integration_id": self.manager.integration_id,
                    "event_type": "status_update",
                    "status": self.status,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Adapter {self.adapter_id} started")
        except Exception as e:
            self.logger.error(f"Error starting adapter {self.adapter_id}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def stop(self) -> None:
        """Stop this adapter."""
        try:
            self.logger.info(f"Stopping adapter {self.adapter_id}")
            
            # Stop adapter-specific resources
            self._stop_resources()
            
            # Update status
            self.status = "stopped"
            
            # Publish status update
            self.event_bus.publish(
                topic=f"integration.adapter.{self.adapter_id}.event",
                key="status_update",
                value={
                    "adapter_id": self.adapter_id,
                    "integration_id": self.manager.integration_id,
                    "event_type": "status_update",
                    "status": self.status,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Adapter {self.adapter_id} stopped")
        except Exception as e:
            self.logger.error(f"Error stopping adapter {self.adapter_id}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def restart(self) -> None:
        """Restart this adapter."""
        try:
            self.logger.info(f"Restarting adapter {self.adapter_id}")
            
            # Stop adapter
            self.stop()
            
            # Start adapter
            self.start()
            
            self.logger.info(f"Adapter {self.adapter_id} restarted")
        except Exception as e:
            self.logger.error(f"Error restarting adapter {self.adapter_id}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def shutdown(self) -> None:
        """Shutdown this adapter and release all resources."""
        try:
            self.logger.info(f"Shutting down adapter {self.adapter_id}")
            
            # Stop adapter if running
            if self.status == "running":
                self.stop()
            
            # Unsubscribe from events
            self._unsubscribe_from_events()
            
            # Unregister from MCP
            self._unregister_from_mcp()
            
            # Unregister from A2A
            self._unregister_from_a2a()
            
            # Release adapter-specific resources
            self._release_resources()
            
            # Update status
            self.status = "shutdown"
            
            self.logger.info(f"Adapter {self.adapter_id} shut down")
        except Exception as e:
            self.logger.error(f"Error shutting down adapter {self.adapter_id}: {str(e)}")
            self.status = "error"
            self.health = "unhealthy"
            raise
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events on the event bus."""
        try:
            # Unsubscribe from adapter-specific events
            self.event_bus.unsubscribe(
                topic=f"integration.adapter.{self.adapter_id}.command",
                group_id=f"{self.adapter_id}-command-handler"
            )
            
            # Unsubscribe from adapter-specific events from the integration manager
            self.event_bus.unsubscribe(
                topic=f"integration.{self.manager.integration_id}.adapter.command",
                group_id=f"{self.adapter_id}-manager-command-handler"
            )
            
            # Unsubscribe from additional events
            self._unsubscribe_from_additional_events()
            
            self.logger.info(f"Unsubscribed adapter {self.adapter_id} from events")
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe adapter {self.adapter_id} from events: {str(e)}")
            raise
    
    def _unregister_from_mcp(self) -> None:
        """Unregister this adapter from the MCP protocol."""
        try:
            self.mcp_bridge.unregister_context_provider(
                provider_id=self.adapter_id
            )
            self.logger.info(f"Unregistered adapter {self.adapter_id} from MCP")
        except Exception as e:
            self.logger.error(f"Failed to unregister adapter {self.adapter_id} from MCP: {str(e)}")
            raise
    
    def _unregister_from_a2a(self) -> None:
        """Unregister this adapter from the A2A protocol."""
        try:
            self.a2a_bridge.unregister_agent(
                agent_id=self.adapter_id
            )
            self.logger.info(f"Unregistered adapter {self.adapter_id} from A2A")
        except Exception as e:
            self.logger.error(f"Failed to unregister adapter {self.adapter_id} from A2A: {str(e)}")
            raise
    
    def check_health(self) -> str:
        """
        Check the health of this adapter.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        try:
            self.logger.info(f"Checking health of adapter {self.adapter_id}")
            
            # Check adapter-specific health
            health = self._check_resource_health()
            
            # Update health status
            self.health = health
            
            self.logger.info(f"Health of adapter {self.adapter_id}: {health}")
            
            return health
        except Exception as e:
            self.logger.error(f"Error checking health of adapter {self.adapter_id}: {str(e)}")
            self.health = "unhealthy"
            return "unhealthy"
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure this adapter with new settings.
        
        Args:
            config: New configuration settings
        """
        try:
            self.logger.info(f"Configuring adapter {self.adapter_id}")
            
            # Update configuration
            self.config.update(config)
            
            # Apply configuration changes
            self._apply_configuration()
            
            self.logger.info(f"Adapter {self.adapter_id} configured")
        except Exception as e:
            self.logger.error(f"Error configuring adapter {self.adapter_id}: {str(e)}")
            raise
    
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
            topic=f"integration.adapter.{self.adapter_id}.event",
            key=event_type,
            value={
                "adapter_id": self.adapter_id,
                "integration_id": self.manager.integration_id,
                "event_type": event_type,
                **event_data,
                "timestamp": self.data_access.get_current_timestamp()
            }
        )
    
    @abstractmethod
    def _get_supported_context_types(self) -> List[str]:
        """
        Get the MCP context types supported by this adapter.
        
        Returns:
            List of supported context types
        """
        pass
    
    @abstractmethod
    def _get_supported_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the A2A capabilities supported by this adapter.
        
        Returns:
            List of supported capabilities
        """
        pass
    
    @abstractmethod
    def _initialize_resources(self) -> None:
        """Initialize adapter-specific resources."""
        pass
    
    @abstractmethod
    def _start_resources(self) -> None:
        """Start adapter-specific resources."""
        pass
    
    @abstractmethod
    def _stop_resources(self) -> None:
        """Stop adapter-specific resources."""
        pass
    
    @abstractmethod
    def _release_resources(self) -> None:
        """Release adapter-specific resources."""
        pass
    
    @abstractmethod
    def _check_resource_health(self) -> str:
        """
        Check the health of adapter-specific resources.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        pass
    
    @abstractmethod
    def _apply_configuration(self) -> None:
        """Apply configuration changes."""
        pass
    
    @abstractmethod
    def _get_status_data(self) -> Dict[str, Any]:
        """
        Get adapter-specific status data.
        
        Returns:
            Adapter-specific status data
        """
        pass
    
    @abstractmethod
    def _handle_custom_command(self, command: str, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle a custom command event.
        
        Args:
            command: Command to handle
            event: Command event data
        
        Returns:
            Optional result data
        """
        pass
    
    @abstractmethod
    def _subscribe_to_additional_events(self) -> None:
        """Subscribe to additional events specific to this adapter."""
        pass
    
    @abstractmethod
    def _unsubscribe_from_additional_events(self) -> None:
        """Unsubscribe from additional events specific to this adapter."""
        pass
