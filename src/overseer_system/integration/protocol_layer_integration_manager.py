"""
Protocol Layer Integration Manager for the Overseer System.

This module provides the Protocol Layer Integration Manager for integrating with
the Industriverse Protocol Layer components, including MCP and A2A protocols.

Author: Manus AI
Date: May 25, 2025
"""

import logging
from typing import Dict, List, Optional, Any, Union

from src.integration.integration_manager import IntegrationManager
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class ProtocolLayerIntegrationManager(IntegrationManager):
    """
    Integration Manager for the Protocol Layer of the Industriverse Framework.
    
    This class manages the integration with Protocol Layer components, including
    MCP (Model Context Protocol) and A2A (Agent to Agent) protocols.
    """
    
    def __init__(
        self,
        manager_id: str,
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
        Initialize the Protocol Layer Integration Manager.
        
        Args:
            manager_id: Unique identifier for this manager
            mcp_bridge: MCP protocol bridge for internal communication
            a2a_bridge: A2A protocol bridge for external communication
            event_bus: Event bus client for event-driven communication
            data_access: Data access service for persistence
            config_service: Configuration service for settings
            auth_service: Authentication service for security
            config: Manager-specific configuration
            logger: Optional logger instance
        """
        super().__init__(
            manager_id=manager_id,
            manager_type="protocol_layer",
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            config=config,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize Protocol Layer-specific resources
        self._protocol_adapters = {}
        
        # Initialize metrics
        self._metrics = {
            "total_protocol_operations": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Protocol Layer Integration Manager {manager_id} initialized")
    
    def _initialize_adapters(self) -> None:
        """Initialize integration adapters."""
        try:
            # Initialize MCP Protocol Adapter
            from src.integration.protocol_layer.mcp_protocol_adapter import MCPProtocolAdapter
            mcp_adapter = MCPProtocolAdapter(
                adapter_id=f"{self.manager_id}.mcp",
                manager=self,
                mcp_bridge=self.mcp_bridge,
                a2a_bridge=self.a2a_bridge,
                event_bus=self.event_bus,
                data_access=self.data_access,
                config_service=self.config_service,
                auth_service=self.auth_service,
                config=self.config.get("mcp", {})
            )
            self._adapters["mcp"] = mcp_adapter
            self._protocol_adapters["mcp"] = mcp_adapter
            
            # Initialize A2A Protocol Adapter
            from src.integration.protocol_layer.a2a_protocol_adapter import A2AProtocolAdapter
            a2a_adapter = A2AProtocolAdapter(
                adapter_id=f"{self.manager_id}.a2a",
                manager=self,
                mcp_bridge=self.mcp_bridge,
                a2a_bridge=self.a2a_bridge,
                event_bus=self.event_bus,
                data_access=self.data_access,
                config_service=self.config_service,
                auth_service=self.auth_service,
                config=self.config.get("a2a", {})
            )
            self._adapters["a2a"] = a2a_adapter
            self._protocol_adapters["a2a"] = a2a_adapter
            
            # Initialize Protocol Bridge Adapter
            from src.integration.protocol_layer.protocol_bridge_adapter import ProtocolBridgeAdapter
            bridge_adapter = ProtocolBridgeAdapter(
                adapter_id=f"{self.manager_id}.bridge",
                manager=self,
                mcp_bridge=self.mcp_bridge,
                a2a_bridge=self.a2a_bridge,
                event_bus=self.event_bus,
                data_access=self.data_access,
                config_service=self.config_service,
                auth_service=self.auth_service,
                config=self.config.get("bridge", {})
            )
            self._adapters["bridge"] = bridge_adapter
            self._protocol_adapters["bridge"] = bridge_adapter
            
            # Initialize Protocol Registry Adapter
            from src.integration.protocol_layer.protocol_registry_adapter import ProtocolRegistryAdapter
            registry_adapter = ProtocolRegistryAdapter(
                adapter_id=f"{self.manager_id}.registry",
                manager=self,
                mcp_bridge=self.mcp_bridge,
                a2a_bridge=self.a2a_bridge,
                event_bus=self.event_bus,
                data_access=self.data_access,
                config_service=self.config_service,
                auth_service=self.auth_service,
                config=self.config.get("registry", {})
            )
            self._adapters["registry"] = registry_adapter
            self._protocol_adapters["registry"] = registry_adapter
            
            self.logger.info(f"Initialized Protocol Layer adapters for manager {self.manager_id}")
        except Exception as e:
            self.logger.error(f"Error initializing Protocol Layer adapters for manager {self.manager_id}: {str(e)}")
            raise
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Protocol Layer operations
        self.mcp_bridge.register_context_handler(
            context_type="protocol_layer.integration",
            handler=self._handle_mcp_protocol_layer_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Protocol Layer operations
        self.mcp_bridge.unregister_context_handler(
            context_type="protocol_layer.integration"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Protocol Layer operations
        self.a2a_bridge.register_capability_handler(
            capability_type="protocol_layer_integration",
            handler=self._handle_a2a_protocol_layer_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Protocol Layer operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="protocol_layer_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Protocol Layer-related events
        self.event_bus.subscribe(
            topic="protocol_layer.integration.status_updated",
            handler=self._handle_protocol_layer_status_updated_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Protocol Layer-related events
        self.event_bus.unsubscribe(
            topic="protocol_layer.integration.status_updated"
        )
    
    def _handle_mcp_protocol_layer_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Protocol Layer context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            adapter_id = context.get("adapter_id")
            operation = context.get("operation")
            parameters = context.get("parameters", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_status":
                result = self.get_status()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_metrics":
                result = self.get_metrics()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "reset_metrics":
                result = self.reset_metrics()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "adapter_operation":
                if not adapter_id:
                    raise ValueError("adapter_id is required")
                
                if not operation:
                    raise ValueError("operation is required")
                
                if adapter_id not in self._protocol_adapters:
                    raise ValueError(f"Adapter {adapter_id} not found")
                
                adapter = self._protocol_adapters[adapter_id]
                
                if not hasattr(adapter, operation) or not callable(getattr(adapter, operation)):
                    raise ValueError(f"Operation {operation} not supported by adapter {adapter_id}")
                
                result = getattr(adapter, operation)(**parameters)
                
                # Update metrics
                self._metrics["total_protocol_operations"] += 1
                self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
                
                return {
                    "status": "success",
                    "adapter_id": adapter_id,
                    "operation": operation,
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Protocol Layer context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_protocol_layer_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Protocol Layer capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            adapter_id = capability_data.get("adapter_id")
            operation = capability_data.get("operation")
            parameters = capability_data.get("parameters", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_status":
                result = self.get_status()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_metrics":
                result = self.get_metrics()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "adapter_operation":
                if not adapter_id:
                    raise ValueError("adapter_id is required")
                
                if not operation:
                    raise ValueError("operation is required")
                
                if adapter_id not in self._protocol_adapters:
                    raise ValueError(f"Adapter {adapter_id} not found")
                
                adapter = self._protocol_adapters[adapter_id]
                
                if not hasattr(adapter, operation) or not callable(getattr(adapter, operation)):
                    raise ValueError(f"Operation {operation} not supported by adapter {adapter_id}")
                
                result = getattr(adapter, operation)(**parameters)
                
                # Update metrics
                self._metrics["total_protocol_operations"] += 1
                self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
                
                return {
                    "status": "success",
                    "adapter_id": adapter_id,
                    "operation": operation,
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Protocol Layer capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_protocol_layer_status_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle Protocol Layer status updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            adapter_id = event_data.get("adapter_id")
            status = event_data.get("status")
            
            # Validate required fields
            if not adapter_id:
                self.logger.warning("Received Protocol Layer status updated event without adapter_id")
                return
            
            if not status:
                self.logger.warning(f"Received Protocol Layer status updated event for adapter {adapter_id} without status")
                return
            
            self.logger.info(f"Protocol Layer adapter {adapter_id} status updated to {status}")
        except Exception as e:
            self.logger.error(f"Error handling Protocol Layer status updated event: {str(e)}")
    
    def get_protocol_adapter(self, adapter_id: str) -> Any:
        """
        Get a Protocol Layer adapter.
        
        Args:
            adapter_id: Adapter ID
        
        Returns:
            Protocol Layer adapter
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._protocol_adapters:
                raise ValueError(f"Adapter {adapter_id} not found")
            
            # Get adapter
            adapter = self._protocol_adapters[adapter_id]
            
            return adapter
        except Exception as e:
            self.logger.error(f"Error getting Protocol Layer adapter {adapter_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_protocol_adapters(self) -> List[Dict[str, Any]]:
        """
        List all Protocol Layer adapters.
        
        Returns:
            List of Protocol Layer adapter data
        """
        try:
            # Get all adapter data
            adapter_data_list = [
                {
                    "id": adapter_id,
                    "type": adapter.adapter_type,
                    "status": adapter.get_status()
                }
                for adapter_id, adapter in self._protocol_adapters.items()
            ]
            
            return adapter_data_list
        except Exception as e:
            self.logger.error(f"Error listing Protocol Layer adapters: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the manager metrics.
        
        Returns:
            Manager metrics
        """
        try:
            # Get adapter metrics
            adapter_metrics = {
                adapter_id: adapter.get_metrics()
                for adapter_id, adapter in self._protocol_adapters.items()
            }
            
            # Combine with manager metrics
            metrics = {
                "manager": self._metrics,
                "adapters": adapter_metrics
            }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting Protocol Layer Integration Manager metrics: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def reset_metrics(self) -> Dict[str, Any]:
        """
        Reset the manager metrics.
        
        Returns:
            Reset manager metrics
        """
        try:
            # Reset manager metrics
            self._metrics = {
                "total_protocol_operations": 0,
                "total_errors": 0,
                "last_operation_timestamp": None
            }
            
            # Reset adapter metrics
            for adapter in self._protocol_adapters.values():
                adapter.reset_metrics()
            
            # Get updated metrics
            return self.get_metrics()
        except Exception as e:
            self.logger.error(f"Error resetting Protocol Layer Integration Manager metrics: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
