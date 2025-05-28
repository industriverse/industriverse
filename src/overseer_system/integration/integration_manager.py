"""
Base Integration Manager for the Overseer System.

This module provides the base integration manager class that all specific
integration managers will inherit from. It defines common functionality
for managing integrations with Industriverse layers and external systems.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Callable, Type

# Import MCP and A2A integration
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class BaseIntegrationManager(ABC):
    """
    Base class for all integration managers in the Overseer System.
    
    This class provides common functionality for managing integrations with
    Industriverse layers and external systems, including MCP/A2A protocol
    integration, event bus integration, and configuration management.
    """
    
    def __init__(
        self,
        integration_id: str,
        integration_name: str,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        config_service: ConfigService,
        auth_service: AuthService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the base integration manager.
        
        Args:
            integration_id: Unique identifier for this integration
            integration_name: Human-readable name for this integration
            mcp_bridge: MCP protocol bridge for internal communication
            a2a_bridge: A2A protocol bridge for external communication
            event_bus: Event bus client for event-driven communication
            data_access: Data access service for persistence
            config_service: Configuration service for settings
            auth_service: Authentication service for security
            logger: Optional logger instance
        """
        self.integration_id = integration_id
        self.integration_name = integration_name
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus
        self.data_access = data_access
        self.config_service = config_service
        self.auth_service = auth_service
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize adapters registry
        self._adapters: Dict[str, Any] = {}
        
        # Initialize event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Initialize status
        self._status = "initialized"
        self._health = "unknown"
        
        # Register with MCP
        self._register_with_mcp()
        
        # Register with A2A
        self._register_with_a2a()
        
        # Subscribe to events
        self._subscribe_to_events()
        
        self.logger.info(f"Integration manager {integration_name} ({integration_id}) initialized")
    
    def _register_with_mcp(self) -> None:
        """Register this integration manager with the MCP protocol."""
        try:
            self.mcp_bridge.register_context_provider(
                provider_id=self.integration_id,
                provider_name=self.integration_name,
                provider_type="integration_manager",
                context_types=self._get_supported_context_types()
            )
            self.logger.info(f"Registered {self.integration_name} with MCP")
        except Exception as e:
            self.logger.error(f"Failed to register {self.integration_name} with MCP: {str(e)}")
    
    def _register_with_a2a(self) -> None:
        """Register this integration manager with the A2A protocol."""
        try:
            self.a2a_bridge.register_agent(
                agent_id=self.integration_id,
                agent_name=self.integration_name,
                agent_type="integration_manager",
                capabilities=self._get_supported_capabilities()
            )
            self.logger.info(f"Registered {self.integration_name} with A2A")
        except Exception as e:
            self.logger.error(f"Failed to register {self.integration_name} with A2A: {str(e)}")
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events on the event bus."""
        try:
            # Subscribe to integration-specific events
            self.event_bus.subscribe(
                topic=f"integration.{self.integration_id}.command",
                group_id=f"{self.integration_id}-command-handler",
                callback=self._handle_command_event
            )
            
            # Subscribe to general integration events
            self.event_bus.subscribe(
                topic="integration.command",
                group_id=f"{self.integration_id}-general-command-handler",
                callback=self._handle_general_command_event
            )
            
            # Subscribe to health check events
            self.event_bus.subscribe(
                topic="system.health.check",
                group_id=f"{self.integration_id}-health-check-handler",
                callback=self._handle_health_check_event
            )
            
            self.logger.info(f"Subscribed {self.integration_name} to events")
        except Exception as e:
            self.logger.error(f"Failed to subscribe {self.integration_name} to events: {str(e)}")
    
    def _handle_command_event(self, event: Dict[str, Any]) -> None:
        """
        Handle integration-specific command events.
        
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
            elif command == "stop":
                self.stop()
            elif command == "restart":
                self.restart()
            elif command == "status":
                self._publish_status(command_id)
            elif command == "register_adapter":
                adapter_id = event.get("adapter_id")
                adapter_type = event.get("adapter_type")
                if adapter_id and adapter_type:
                    self.register_adapter(adapter_id, adapter_type, event.get("adapter_config", {}))
                else:
                    self.logger.warning(f"Invalid register_adapter command: {event}")
            elif command == "unregister_adapter":
                adapter_id = event.get("adapter_id")
                if adapter_id:
                    self.unregister_adapter(adapter_id)
                else:
                    self.logger.warning(f"Invalid unregister_adapter command: {event}")
            else:
                # Handle custom commands
                self._handle_custom_command(command, event)
        except Exception as e:
            self.logger.error(f"Error handling command event: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic=f"integration.{self.integration_id}.response",
                key=event.get("command_id", str(uuid.uuid4())),
                value={
                    "integration_id": self.integration_id,
                    "command_id": event.get("command_id", str(uuid.uuid4())),
                    "command": event.get("command"),
                    "status": "error",
                    "error": str(e)
                }
            )
    
    def _handle_general_command_event(self, event: Dict[str, Any]) -> None:
        """
        Handle general integration command events.
        
        Args:
            event: Command event data
        """
        try:
            # Check if this event is for all integrations or a specific integration type
            target_type = event.get("integration_type")
            if target_type and not self._is_target_type(target_type):
                return
            
            # Process the command
            self._handle_command_event(event)
        except Exception as e:
            self.logger.error(f"Error handling general command event: {str(e)}")
    
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
                    "integration_id": self.integration_id,
                    "integration_name": self.integration_name,
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
                    "integration_id": self.integration_id,
                    "integration_name": self.integration_name,
                    "check_id": event.get("check_id", str(uuid.uuid4())),
                    "status": "error",
                    "error": str(e),
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
    
    def _publish_status(self, command_id: str) -> None:
        """
        Publish the current status of this integration manager.
        
        Args:
            command_id: Command ID for correlation
        """
        try:
            # Get adapter statuses
            adapter_statuses = {}
            for adapter_id, adapter in self._adapters.items():
                adapter_statuses[adapter_id] = {
                    "status": getattr(adapter, "status", "unknown"),
                    "health": getattr(adapter, "health", "unknown"),
                    "type": adapter.__class__.__name__
                }
            
            # Publish status
            self.event_bus.publish(
                topic=f"integration.{self.integration_id}.status",
                key=command_id,
                value={
                    "integration_id": self.integration_id,
                    "integration_name": self.integration_name,
                    "command_id": command_id,
                    "status": self._status,
                    "health": self._health,
                    "adapters": adapter_statuses,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
        except Exception as e:
            self.logger.error(f"Error publishing status: {str(e)}")
            
            # Publish error status
            self.event_bus.publish(
                topic=f"integration.{self.integration_id}.status",
                key=command_id,
                value={
                    "integration_id": self.integration_id,
                    "integration_name": self.integration_name,
                    "command_id": command_id,
                    "status": "error",
                    "error": str(e),
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
    
    def register_adapter(self, adapter_id: str, adapter_type: str, adapter_config: Dict[str, Any]) -> None:
        """
        Register an integration adapter with this manager.
        
        Args:
            adapter_id: Unique identifier for the adapter
            adapter_type: Type of adapter to register
            adapter_config: Configuration for the adapter
        
        Raises:
            ValueError: If adapter_id is already registered or adapter_type is invalid
        """
        if adapter_id in self._adapters:
            raise ValueError(f"Adapter {adapter_id} is already registered")
        
        # Get adapter class
        adapter_class = self._get_adapter_class(adapter_type)
        if not adapter_class:
            raise ValueError(f"Invalid adapter type: {adapter_type}")
        
        # Create adapter instance
        adapter = adapter_class(
            adapter_id=adapter_id,
            manager=self,
            mcp_bridge=self.mcp_bridge,
            a2a_bridge=self.a2a_bridge,
            event_bus=self.event_bus,
            data_access=self.data_access,
            config_service=self.config_service,
            auth_service=self.auth_service,
            config=adapter_config,
            logger=self.logger.getChild(f"adapter.{adapter_id}")
        )
        
        # Register adapter
        self._adapters[adapter_id] = adapter
        
        self.logger.info(f"Registered adapter {adapter_id} of type {adapter_type}")
        
        # Initialize adapter
        adapter.initialize()
    
    def unregister_adapter(self, adapter_id: str) -> None:
        """
        Unregister an integration adapter from this manager.
        
        Args:
            adapter_id: Unique identifier for the adapter
        
        Raises:
            ValueError: If adapter_id is not registered
        """
        if adapter_id not in self._adapters:
            raise ValueError(f"Adapter {adapter_id} is not registered")
        
        # Get adapter
        adapter = self._adapters[adapter_id]
        
        # Shutdown adapter
        try:
            adapter.shutdown()
        except Exception as e:
            self.logger.error(f"Error shutting down adapter {adapter_id}: {str(e)}")
        
        # Unregister adapter
        del self._adapters[adapter_id]
        
        self.logger.info(f"Unregistered adapter {adapter_id}")
    
    def get_adapter(self, adapter_id: str) -> Any:
        """
        Get an integration adapter by ID.
        
        Args:
            adapter_id: Unique identifier for the adapter
        
        Returns:
            The adapter instance
        
        Raises:
            ValueError: If adapter_id is not registered
        """
        if adapter_id not in self._adapters:
            raise ValueError(f"Adapter {adapter_id} is not registered")
        
        return self._adapters[adapter_id]
    
    def get_adapters_by_type(self, adapter_type: str) -> List[Any]:
        """
        Get all integration adapters of a specific type.
        
        Args:
            adapter_type: Type of adapters to get
        
        Returns:
            List of adapter instances
        """
        return [
            adapter for adapter in self._adapters.values()
            if adapter.__class__.__name__ == adapter_type
        ]
    
    def start(self) -> None:
        """Start this integration manager and all registered adapters."""
        self.logger.info(f"Starting integration manager {self.integration_name}")
        
        # Start all adapters
        for adapter_id, adapter in self._adapters.items():
            try:
                adapter.start()
                self.logger.info(f"Started adapter {adapter_id}")
            except Exception as e:
                self.logger.error(f"Error starting adapter {adapter_id}: {str(e)}")
        
        # Update status
        self._status = "running"
        
        # Publish status update
        self.event_bus.publish(
            topic=f"integration.{self.integration_id}.event",
            key="status_update",
            value={
                "integration_id": self.integration_id,
                "integration_name": self.integration_name,
                "event_type": "status_update",
                "status": self._status,
                "timestamp": self.data_access.get_current_timestamp()
            }
        )
        
        self.logger.info(f"Integration manager {self.integration_name} started")
    
    def stop(self) -> None:
        """Stop this integration manager and all registered adapters."""
        self.logger.info(f"Stopping integration manager {self.integration_name}")
        
        # Stop all adapters
        for adapter_id, adapter in self._adapters.items():
            try:
                adapter.stop()
                self.logger.info(f"Stopped adapter {adapter_id}")
            except Exception as e:
                self.logger.error(f"Error stopping adapter {adapter_id}: {str(e)}")
        
        # Update status
        self._status = "stopped"
        
        # Publish status update
        self.event_bus.publish(
            topic=f"integration.{self.integration_id}.event",
            key="status_update",
            value={
                "integration_id": self.integration_id,
                "integration_name": self.integration_name,
                "event_type": "status_update",
                "status": self._status,
                "timestamp": self.data_access.get_current_timestamp()
            }
        )
        
        self.logger.info(f"Integration manager {self.integration_name} stopped")
    
    def restart(self) -> None:
        """Restart this integration manager and all registered adapters."""
        self.logger.info(f"Restarting integration manager {self.integration_name}")
        
        # Stop all adapters
        self.stop()
        
        # Start all adapters
        self.start()
        
        self.logger.info(f"Integration manager {self.integration_name} restarted")
    
    def check_health(self) -> str:
        """
        Check the health of this integration manager and all registered adapters.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        self.logger.info(f"Checking health of integration manager {self.integration_name}")
        
        # Check adapter health
        adapter_health = {}
        for adapter_id, adapter in self._adapters.items():
            try:
                adapter_health[adapter_id] = adapter.check_health()
            except Exception as e:
                self.logger.error(f"Error checking health of adapter {adapter_id}: {str(e)}")
                adapter_health[adapter_id] = "unhealthy"
        
        # Determine overall health
        if not adapter_health:
            # No adapters registered
            health = "healthy"
        elif all(status == "healthy" for status in adapter_health.values()):
            # All adapters healthy
            health = "healthy"
        elif any(status == "unhealthy" for status in adapter_health.values()):
            # At least one adapter unhealthy
            health = "unhealthy"
        else:
            # Some adapters degraded
            health = "degraded"
        
        # Update health status
        self._health = health
        
        self.logger.info(f"Health of integration manager {self.integration_name}: {health}")
        
        return health
    
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
            topic=f"integration.{self.integration_id}.event",
            key=event_type,
            value={
                "integration_id": self.integration_id,
                "integration_name": self.integration_name,
                "event_type": event_type,
                **event_data,
                "timestamp": self.data_access.get_current_timestamp()
            }
        )
    
    @abstractmethod
    def _get_supported_context_types(self) -> List[str]:
        """
        Get the MCP context types supported by this integration manager.
        
        Returns:
            List of supported context types
        """
        pass
    
    @abstractmethod
    def _get_supported_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the A2A capabilities supported by this integration manager.
        
        Returns:
            List of supported capabilities
        """
        pass
    
    @abstractmethod
    def _get_adapter_class(self, adapter_type: str) -> Optional[Type]:
        """
        Get the adapter class for a specific adapter type.
        
        Args:
            adapter_type: Type of adapter
        
        Returns:
            Adapter class or None if not supported
        """
        pass
    
    @abstractmethod
    def _handle_custom_command(self, command: str, event: Dict[str, Any]) -> None:
        """
        Handle a custom command event.
        
        Args:
            command: Command to handle
            event: Command event data
        """
        pass
    
    @abstractmethod
    def _is_target_type(self, target_type: str) -> bool:
        """
        Check if this integration manager is of a specific target type.
        
        Args:
            target_type: Target integration type
        
        Returns:
            True if this manager is of the target type, False otherwise
        """
        pass
