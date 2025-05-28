"""
Edge Systems Integration Manager for the Overseer System.

This module provides the Edge Systems Integration Manager for integrating with
various edge devices, IoT systems, and industrial equipment at the network edge,
enabling communication with distributed edge computing environments.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union, Callable

from src.integration.integration_manager import IntegrationManager
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class EdgeSystemsIntegrationManager(IntegrationManager):
    """
    Integration Manager for Edge Systems.
    
    This class provides integration with various edge devices, IoT systems, and
    industrial equipment at the network edge, enabling communication with
    distributed edge computing environments.
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
        Initialize the Edge Systems Integration Manager.
        
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
            manager_type="edge_systems",
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            config=config,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize edge-specific resources
        self._edge_devices = {}
        self._edge_gateways = {}
        self._device_groups = {}
        self._telemetry_streams = {}
        self._command_queues = {}
        
        # Initialize metrics
        self._metrics = {
            "total_edge_devices": 0,
            "total_active_devices": 0,
            "total_edge_gateways": 0,
            "total_device_groups": 0,
            "total_telemetry_streams": 0,
            "total_command_queues": 0,
            "total_telemetry_messages": 0,
            "total_commands_sent": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Edge Systems Integration Manager {manager_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Edge System operations
        self.mcp_bridge.register_context_handler(
            context_type="edge_systems.device",
            handler=self._handle_mcp_device_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="edge_systems.gateway",
            handler=self._handle_mcp_gateway_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="edge_systems.device_group",
            handler=self._handle_mcp_device_group_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="edge_systems.telemetry",
            handler=self._handle_mcp_telemetry_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="edge_systems.command",
            handler=self._handle_mcp_command_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Edge System operations
        self.mcp_bridge.unregister_context_handler(
            context_type="edge_systems.device"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="edge_systems.gateway"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="edge_systems.device_group"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="edge_systems.telemetry"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="edge_systems.command"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Edge System operations
        self.a2a_bridge.register_capability_handler(
            capability_type="device_management",
            handler=self._handle_a2a_device_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="gateway_management",
            handler=self._handle_a2a_gateway_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="device_group_management",
            handler=self._handle_a2a_device_group_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="telemetry_management",
            handler=self._handle_a2a_telemetry_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="command_management",
            handler=self._handle_a2a_command_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Edge System operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="device_management"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="gateway_management"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="device_group_management"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="telemetry_management"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="command_management"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Edge System-related events
        self.event_bus.subscribe(
            topic="edge_systems.device.device_registered",
            handler=self._handle_device_registered_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.device.device_updated",
            handler=self._handle_device_updated_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.device.device_deregistered",
            handler=self._handle_device_deregistered_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.device.device_connected",
            handler=self._handle_device_connected_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.device.device_disconnected",
            handler=self._handle_device_disconnected_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.gateway.gateway_registered",
            handler=self._handle_gateway_registered_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.gateway.gateway_updated",
            handler=self._handle_gateway_updated_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.gateway.gateway_deregistered",
            handler=self._handle_gateway_deregistered_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.device_group.device_group_created",
            handler=self._handle_device_group_created_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.device_group.device_group_updated",
            handler=self._handle_device_group_updated_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.device_group.device_group_deleted",
            handler=self._handle_device_group_deleted_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.telemetry.telemetry_received",
            handler=self._handle_telemetry_received_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.command.command_sent",
            handler=self._handle_command_sent_event
        )
        
        self.event_bus.subscribe(
            topic="edge_systems.command.command_result_received",
            handler=self._handle_command_result_received_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Edge System-related events
        self.event_bus.unsubscribe(
            topic="edge_systems.device.device_registered"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.device.device_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.device.device_deregistered"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.device.device_connected"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.device.device_disconnected"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.gateway.gateway_registered"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.gateway.gateway_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.gateway.gateway_deregistered"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.device_group.device_group_created"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.device_group.device_group_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.device_group.device_group_deleted"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.telemetry.telemetry_received"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.command.command_sent"
        )
        
        self.event_bus.unsubscribe(
            topic="edge_systems.command.command_result_received"
        )
    
    def _handle_mcp_device_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Device context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "register_device":
                device_type = context.get("device_type")
                if not device_type:
                    raise ValueError("device_type is required")
                
                device_config = context.get("device_config")
                if not device_config:
                    raise ValueError("device_config is required")
                
                gateway_id = context.get("gateway_id")
                
                result = self.register_device(
                    device_type=device_type,
                    device_config=device_config,
                    gateway_id=gateway_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "update_device":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                device_config = context.get("device_config")
                if not device_config:
                    raise ValueError("device_config is required")
                
                result = self.update_device(
                    device_id=device_id,
                    device_config=device_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "deregister_device":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                result = self.deregister_device(
                    device_id=device_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_device":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                result = self.get_device(
                    device_id=device_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_devices":
                device_type = context.get("device_type")
                gateway_id = context.get("gateway_id")
                device_group_id = context.get("device_group_id")
                
                result = self.list_devices(
                    device_type=device_type,
                    gateway_id=gateway_id,
                    device_group_id=device_group_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Device context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_gateway_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Gateway context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "register_gateway":
                gateway_type = context.get("gateway_type")
                if not gateway_type:
                    raise ValueError("gateway_type is required")
                
                gateway_config = context.get("gateway_config")
                if not gateway_config:
                    raise ValueError("gateway_config is required")
                
                result = self.register_gateway(
                    gateway_type=gateway_type,
                    gateway_config=gateway_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "update_gateway":
                gateway_id = context.get("gateway_id")
                if not gateway_id:
                    raise ValueError("gateway_id is required")
                
                gateway_config = context.get("gateway_config")
                if not gateway_config:
                    raise ValueError("gateway_config is required")
                
                result = self.update_gateway(
                    gateway_id=gateway_id,
                    gateway_config=gateway_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "deregister_gateway":
                gateway_id = context.get("gateway_id")
                if not gateway_id:
                    raise ValueError("gateway_id is required")
                
                result = self.deregister_gateway(
                    gateway_id=gateway_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_gateway":
                gateway_id = context.get("gateway_id")
                if not gateway_id:
                    raise ValueError("gateway_id is required")
                
                result = self.get_gateway(
                    gateway_id=gateway_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_gateways":
                gateway_type = context.get("gateway_type")
                
                result = self.list_gateways(
                    gateway_type=gateway_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Gateway context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_device_group_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Device Group context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "create_device_group":
                group_name = context.get("group_name")
                if not group_name:
                    raise ValueError("group_name is required")
                
                group_config = context.get("group_config")
                if not group_config:
                    raise ValueError("group_config is required")
                
                result = self.create_device_group(
                    group_name=group_name,
                    group_config=group_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "update_device_group":
                group_id = context.get("group_id")
                if not group_id:
                    raise ValueError("group_id is required")
                
                group_config = context.get("group_config")
                if not group_config:
                    raise ValueError("group_config is required")
                
                result = self.update_device_group(
                    group_id=group_id,
                    group_config=group_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "delete_device_group":
                group_id = context.get("group_id")
                if not group_id:
                    raise ValueError("group_id is required")
                
                result = self.delete_device_group(
                    group_id=group_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "add_device_to_group":
                group_id = context.get("group_id")
                if not group_id:
                    raise ValueError("group_id is required")
                
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                result = self.add_device_to_group(
                    group_id=group_id,
                    device_id=device_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "remove_device_from_group":
                group_id = context.get("group_id")
                if not group_id:
                    raise ValueError("group_id is required")
                
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                result = self.remove_device_from_group(
                    group_id=group_id,
                    device_id=device_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_device_group":
                group_id = context.get("group_id")
                if not group_id:
                    raise ValueError("group_id is required")
                
                result = self.get_device_group(
                    group_id=group_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_device_groups":
                result = self.list_device_groups()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Device Group context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_telemetry_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Telemetry context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_telemetry":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                telemetry_type = context.get("telemetry_type")
                
                result = self.get_telemetry(
                    device_id=device_id,
                    telemetry_type=telemetry_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_telemetry_history":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                telemetry_type = context.get("telemetry_type")
                start_time = context.get("start_time")
                end_time = context.get("end_time")
                limit = context.get("limit")
                
                result = self.get_telemetry_history(
                    device_id=device_id,
                    telemetry_type=telemetry_type,
                    start_time=start_time,
                    end_time=end_time,
                    limit=limit
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "subscribe_to_telemetry":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                telemetry_type = context.get("telemetry_type")
                
                result = self.subscribe_to_telemetry(
                    device_id=device_id,
                    telemetry_type=telemetry_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "unsubscribe_from_telemetry":
                subscription_id = context.get("subscription_id")
                if not subscription_id:
                    raise ValueError("subscription_id is required")
                
                result = self.unsubscribe_from_telemetry(
                    subscription_id=subscription_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Telemetry context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_command_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Command context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "send_command":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                command_type = context.get("command_type")
                if not command_type:
                    raise ValueError("command_type is required")
                
                command_payload = context.get("command_payload")
                if not command_payload:
                    raise ValueError("command_payload is required")
                
                result = self.send_command(
                    device_id=device_id,
                    command_type=command_type,
                    command_payload=command_payload
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "send_group_command":
                group_id = context.get("group_id")
                if not group_id:
                    raise ValueError("group_id is required")
                
                command_type = context.get("command_type")
                if not command_type:
                    raise ValueError("command_type is required")
                
                command_payload = context.get("command_payload")
                if not command_payload:
                    raise ValueError("command_payload is required")
                
                result = self.send_group_command(
                    group_id=group_id,
                    command_type=command_type,
                    command_payload=command_payload
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_command_status":
                command_id = context.get("command_id")
                if not command_id:
                    raise ValueError("command_id is required")
                
                result = self.get_command_status(
                    command_id=command_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_command_history":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                command_type = context.get("command_type")
                start_time = context.get("start_time")
                end_time = context.get("end_time")
                limit = context.get("limit")
                
                result = self.get_command_history(
                    device_id=device_id,
                    command_type=command_type,
                    start_time=start_time,
                    end_time=end_time,
                    limit=limit
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Command context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_device_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Device capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_device":
                device_id = capability_data.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                result = self.get_device(
                    device_id=device_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_devices":
                device_type = capability_data.get("device_type")
                gateway_id = capability_data.get("gateway_id")
                device_group_id = capability_data.get("device_group_id")
                
                result = self.list_devices(
                    device_type=device_type,
                    gateway_id=gateway_id,
                    device_group_id=device_group_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Device capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_gateway_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Gateway capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_gateway":
                gateway_id = capability_data.get("gateway_id")
                if not gateway_id:
                    raise ValueError("gateway_id is required")
                
                result = self.get_gateway(
                    gateway_id=gateway_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_gateways":
                gateway_type = capability_data.get("gateway_type")
                
                result = self.list_gateways(
                    gateway_type=gateway_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Gateway capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_device_group_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Device Group capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_device_group":
                group_id = capability_data.get("group_id")
                if not group_id:
                    raise ValueError("group_id is required")
                
                result = self.get_device_group(
                    group_id=group_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_device_groups":
                result = self.list_device_groups()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Device Group capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_telemetry_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Telemetry capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_telemetry":
                device_id = capability_data.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                telemetry_type = capability_data.get("telemetry_type")
                
                result = self.get_telemetry(
                    device_id=device_id,
                    telemetry_type=telemetry_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_telemetry_history":
                device_id = capability_data.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                telemetry_type = capability_data.get("telemetry_type")
                start_time = capability_data.get("start_time")
                end_time = capability_data.get("end_time")
                limit = capability_data.get("limit")
                
                result = self.get_telemetry_history(
                    device_id=device_id,
                    telemetry_type=telemetry_type,
                    start_time=start_time,
                    end_time=end_time,
                    limit=limit
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Telemetry capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_command_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Command capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_command_status":
                command_id = capability_data.get("command_id")
                if not command_id:
                    raise ValueError("command_id is required")
                
                result = self.get_command_status(
                    command_id=command_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_command_history":
                device_id = capability_data.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                command_type = capability_data.get("command_type")
                start_time = capability_data.get("start_time")
                end_time = capability_data.get("end_time")
                limit = capability_data.get("limit")
                
                result = self.get_command_history(
                    device_id=device_id,
                    command_type=command_type,
                    start_time=start_time,
                    end_time=end_time,
                    limit=limit
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Command capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_device_registered_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle device registered event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            device_id = event_data.get("device_id")
            device_type = event_data.get("device_type")
            device_config = event_data.get("device_config")
            gateway_id = event_data.get("gateway_id")
            
            # Validate required fields
            if not device_id:
                self.logger.warning("Received device registered event without device_id")
                return
            
            if not device_type:
                self.logger.warning(f"Received device registered event for device {device_id} without device_type")
                return
            
            if not device_config:
                self.logger.warning(f"Received device registered event for device {device_id} without device_config")
                return
            
            self.logger.info(f"Device {device_id} registered with type {device_type}")
            
            # Store device data
            self._edge_devices[device_id] = {
                "device_type": device_type,
                "device_config": device_config,
                "gateway_id": gateway_id,
                "status": "registered",
                "connected": False,
                "last_connected_at": None,
                "last_disconnected_at": None,
                "registered_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_edge_devices"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling device registered event: {str(e)}")
    
    def _handle_device_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle device updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            device_id = event_data.get("device_id")
            device_config = event_data.get("device_config")
            
            # Validate required fields
            if not device_id:
                self.logger.warning("Received device updated event without device_id")
                return
            
            if not device_config:
                self.logger.warning(f"Received device updated event for device {device_id} without device_config")
                return
            
            # Check if device exists
            if device_id not in self._edge_devices:
                self.logger.warning(f"Received device updated event for non-existent device {device_id}")
                return
            
            self.logger.info(f"Device {device_id} updated")
            
            # Update device data
            self._edge_devices[device_id]["device_config"] = device_config
            self._edge_devices[device_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling device updated event: {str(e)}")
    
    def _handle_device_deregistered_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle device deregistered event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            device_id = event_data.get("device_id")
            
            # Validate required fields
            if not device_id:
                self.logger.warning("Received device deregistered event without device_id")
                return
            
            # Check if device exists
            if device_id not in self._edge_devices:
                self.logger.warning(f"Received device deregistered event for non-existent device {device_id}")
                return
            
            self.logger.info(f"Device {device_id} deregistered")
            
            # Update device data
            self._edge_devices[device_id]["status"] = "deregistered"
            
            # Remove device from device groups
            for group_id, group_data in self._device_groups.items():
                if device_id in group_data["devices"]:
                    group_data["devices"].remove(device_id)
            
            # Remove device data
            del self._edge_devices[device_id]
            
            # Update metrics
            self._metrics["total_edge_devices"] -= 1
            if self._edge_devices[device_id]["connected"]:
                self._metrics["total_active_devices"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling device deregistered event: {str(e)}")
    
    def _handle_device_connected_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle device connected event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            device_id = event_data.get("device_id")
            
            # Validate required fields
            if not device_id:
                self.logger.warning("Received device connected event without device_id")
                return
            
            # Check if device exists
            if device_id not in self._edge_devices:
                self.logger.warning(f"Received device connected event for non-existent device {device_id}")
                return
            
            self.logger.info(f"Device {device_id} connected")
            
            # Update device data
            self._edge_devices[device_id]["connected"] = True
            self._edge_devices[device_id]["last_connected_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["total_active_devices"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling device connected event: {str(e)}")
    
    def _handle_device_disconnected_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle device disconnected event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            device_id = event_data.get("device_id")
            
            # Validate required fields
            if not device_id:
                self.logger.warning("Received device disconnected event without device_id")
                return
            
            # Check if device exists
            if device_id not in self._edge_devices:
                self.logger.warning(f"Received device disconnected event for non-existent device {device_id}")
                return
            
            self.logger.info(f"Device {device_id} disconnected")
            
            # Update device data
            self._edge_devices[device_id]["connected"] = False
            self._edge_devices[device_id]["last_disconnected_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["total_active_devices"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling device disconnected event: {str(e)}")
    
    def _handle_gateway_registered_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle gateway registered event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            gateway_id = event_data.get("gateway_id")
            gateway_type = event_data.get("gateway_type")
            gateway_config = event_data.get("gateway_config")
            
            # Validate required fields
            if not gateway_id:
                self.logger.warning("Received gateway registered event without gateway_id")
                return
            
            if not gateway_type:
                self.logger.warning(f"Received gateway registered event for gateway {gateway_id} without gateway_type")
                return
            
            if not gateway_config:
                self.logger.warning(f"Received gateway registered event for gateway {gateway_id} without gateway_config")
                return
            
            self.logger.info(f"Gateway {gateway_id} registered with type {gateway_type}")
            
            # Store gateway data
            self._edge_gateways[gateway_id] = {
                "gateway_type": gateway_type,
                "gateway_config": gateway_config,
                "status": "registered",
                "registered_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_edge_gateways"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling gateway registered event: {str(e)}")
    
    def _handle_gateway_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle gateway updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            gateway_id = event_data.get("gateway_id")
            gateway_config = event_data.get("gateway_config")
            
            # Validate required fields
            if not gateway_id:
                self.logger.warning("Received gateway updated event without gateway_id")
                return
            
            if not gateway_config:
                self.logger.warning(f"Received gateway updated event for gateway {gateway_id} without gateway_config")
                return
            
            # Check if gateway exists
            if gateway_id not in self._edge_gateways:
                self.logger.warning(f"Received gateway updated event for non-existent gateway {gateway_id}")
                return
            
            self.logger.info(f"Gateway {gateway_id} updated")
            
            # Update gateway data
            self._edge_gateways[gateway_id]["gateway_config"] = gateway_config
            self._edge_gateways[gateway_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling gateway updated event: {str(e)}")
    
    def _handle_gateway_deregistered_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle gateway deregistered event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            gateway_id = event_data.get("gateway_id")
            
            # Validate required fields
            if not gateway_id:
                self.logger.warning("Received gateway deregistered event without gateway_id")
                return
            
            # Check if gateway exists
            if gateway_id not in self._edge_gateways:
                self.logger.warning(f"Received gateway deregistered event for non-existent gateway {gateway_id}")
                return
            
            self.logger.info(f"Gateway {gateway_id} deregistered")
            
            # Update gateway data
            self._edge_gateways[gateway_id]["status"] = "deregistered"
            
            # Remove gateway data
            del self._edge_gateways[gateway_id]
            
            # Update metrics
            self._metrics["total_edge_gateways"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling gateway deregistered event: {str(e)}")
    
    def _handle_device_group_created_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle device group created event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            group_id = event_data.get("group_id")
            group_name = event_data.get("group_name")
            group_config = event_data.get("group_config")
            
            # Validate required fields
            if not group_id:
                self.logger.warning("Received device group created event without group_id")
                return
            
            if not group_name:
                self.logger.warning(f"Received device group created event for group {group_id} without group_name")
                return
            
            if not group_config:
                self.logger.warning(f"Received device group created event for group {group_id} without group_config")
                return
            
            self.logger.info(f"Device group {group_id} created with name {group_name}")
            
            # Store device group data
            self._device_groups[group_id] = {
                "group_name": group_name,
                "group_config": group_config,
                "devices": [],
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_device_groups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling device group created event: {str(e)}")
    
    def _handle_device_group_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle device group updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            group_id = event_data.get("group_id")
            group_config = event_data.get("group_config")
            
            # Validate required fields
            if not group_id:
                self.logger.warning("Received device group updated event without group_id")
                return
            
            if not group_config:
                self.logger.warning(f"Received device group updated event for group {group_id} without group_config")
                return
            
            # Check if device group exists
            if group_id not in self._device_groups:
                self.logger.warning(f"Received device group updated event for non-existent group {group_id}")
                return
            
            self.logger.info(f"Device group {group_id} updated")
            
            # Update device group data
            self._device_groups[group_id]["group_config"] = group_config
            self._device_groups[group_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling device group updated event: {str(e)}")
    
    def _handle_device_group_deleted_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle device group deleted event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            group_id = event_data.get("group_id")
            
            # Validate required fields
            if not group_id:
                self.logger.warning("Received device group deleted event without group_id")
                return
            
            # Check if device group exists
            if group_id not in self._device_groups:
                self.logger.warning(f"Received device group deleted event for non-existent group {group_id}")
                return
            
            self.logger.info(f"Device group {group_id} deleted")
            
            # Remove device group data
            del self._device_groups[group_id]
            
            # Update metrics
            self._metrics["total_device_groups"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling device group deleted event: {str(e)}")
    
    def _handle_telemetry_received_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle telemetry received event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            device_id = event_data.get("device_id")
            telemetry_type = event_data.get("telemetry_type")
            telemetry_data = event_data.get("telemetry_data")
            timestamp = event_data.get("timestamp")
            
            # Validate required fields
            if not device_id:
                self.logger.warning("Received telemetry received event without device_id")
                return
            
            if not telemetry_type:
                self.logger.warning(f"Received telemetry received event for device {device_id} without telemetry_type")
                return
            
            if not telemetry_data:
                self.logger.warning(f"Received telemetry received event for device {device_id} without telemetry_data")
                return
            
            if not timestamp:
                timestamp = self.data_access.get_current_timestamp()
            
            self.logger.debug(f"Telemetry received from device {device_id} with type {telemetry_type}")
            
            # Store telemetry data
            telemetry_key = f"{device_id}:{telemetry_type}"
            if telemetry_key not in self._telemetry_streams:
                self._telemetry_streams[telemetry_key] = []
                self._metrics["total_telemetry_streams"] += 1
            
            # Add telemetry data to stream
            self._telemetry_streams[telemetry_key].append({
                "device_id": device_id,
                "telemetry_type": telemetry_type,
                "telemetry_data": telemetry_data,
                "timestamp": timestamp
            })
            
            # Limit telemetry stream size
            max_stream_size = 100  # In a real implementation, this would be configurable
            if len(self._telemetry_streams[telemetry_key]) > max_stream_size:
                self._telemetry_streams[telemetry_key] = self._telemetry_streams[telemetry_key][-max_stream_size:]
            
            # Update metrics
            self._metrics["total_telemetry_messages"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling telemetry received event: {str(e)}")
    
    def _handle_command_sent_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle command sent event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            command_id = event_data.get("command_id")
            device_id = event_data.get("device_id")
            command_type = event_data.get("command_type")
            command_payload = event_data.get("command_payload")
            
            # Validate required fields
            if not command_id:
                self.logger.warning("Received command sent event without command_id")
                return
            
            if not device_id:
                self.logger.warning(f"Received command sent event for command {command_id} without device_id")
                return
            
            if not command_type:
                self.logger.warning(f"Received command sent event for command {command_id} without command_type")
                return
            
            if not command_payload:
                self.logger.warning(f"Received command sent event for command {command_id} without command_payload")
                return
            
            self.logger.info(f"Command {command_id} sent to device {device_id} with type {command_type}")
            
            # Store command data
            command_key = f"{device_id}:{command_type}"
            if command_key not in self._command_queues:
                self._command_queues[command_key] = []
                self._metrics["total_command_queues"] += 1
            
            # Add command data to queue
            self._command_queues[command_key].append({
                "command_id": command_id,
                "device_id": device_id,
                "command_type": command_type,
                "command_payload": command_payload,
                "status": "sent",
                "result": None,
                "sent_at": self.data_access.get_current_timestamp(),
                "completed_at": None
            })
            
            # Limit command queue size
            max_queue_size = 100  # In a real implementation, this would be configurable
            if len(self._command_queues[command_key]) > max_queue_size:
                self._command_queues[command_key] = self._command_queues[command_key][-max_queue_size:]
            
            # Update metrics
            self._metrics["total_commands_sent"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling command sent event: {str(e)}")
    
    def _handle_command_result_received_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle command result received event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            command_id = event_data.get("command_id")
            device_id = event_data.get("device_id")
            command_type = event_data.get("command_type")
            result = event_data.get("result")
            
            # Validate required fields
            if not command_id:
                self.logger.warning("Received command result received event without command_id")
                return
            
            if not device_id:
                self.logger.warning(f"Received command result received event for command {command_id} without device_id")
                return
            
            if not command_type:
                self.logger.warning(f"Received command result received event for command {command_id} without command_type")
                return
            
            if not result:
                self.logger.warning(f"Received command result received event for command {command_id} without result")
                return
            
            self.logger.info(f"Command {command_id} result received from device {device_id} with type {command_type}")
            
            # Update command data
            command_key = f"{device_id}:{command_type}"
            if command_key in self._command_queues:
                for command in self._command_queues[command_key]:
                    if command["command_id"] == command_id:
                        command["status"] = "completed"
                        command["result"] = result
                        command["completed_at"] = self.data_access.get_current_timestamp()
                        break
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling command result received event: {str(e)}")
    
    def register_device(self, device_type: str, device_config: Dict[str, Any], gateway_id: str = None) -> Dict[str, Any]:
        """
        Register an edge device.
        
        Args:
            device_type: Device type
            device_config: Device configuration
            gateway_id: Optional gateway ID
        
        Returns:
            Registered device data
        """
        try:
            # Check if gateway exists if provided
            if gateway_id and gateway_id not in self._edge_gateways:
                raise ValueError(f"Gateway {gateway_id} not found")
            
            # Generate device ID
            device_id = f"device-{self.data_access.generate_id()}"
            
            # In a real implementation, this would register the device using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish device registered event
            self.event_bus.publish(
                topic="edge_systems.device.device_registered",
                data={
                    "device_id": device_id,
                    "device_type": device_type,
                    "device_config": device_config,
                    "gateway_id": gateway_id
                }
            )
            
            # Store device data
            self._edge_devices[device_id] = {
                "device_type": device_type,
                "device_config": device_config,
                "gateway_id": gateway_id,
                "status": "registered",
                "connected": False,
                "last_connected_at": None,
                "last_disconnected_at": None,
                "registered_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_edge_devices"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Registered device {device_id} with type {device_type}")
            
            return {
                "device_id": device_id,
                "device_type": device_type,
                "device_config": device_config,
                "gateway_id": gateway_id,
                "status": "registered"
            }
        except Exception as e:
            self.logger.error(f"Error registering device: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def update_device(self, device_id: str, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an edge device.
        
        Args:
            device_id: Device ID
            device_config: Device configuration
        
        Returns:
            Updated device data
        """
        try:
            # Check if device exists
            if device_id not in self._edge_devices:
                raise ValueError(f"Device {device_id} not found")
            
            # In a real implementation, this would update the device using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish device updated event
            self.event_bus.publish(
                topic="edge_systems.device.device_updated",
                data={
                    "device_id": device_id,
                    "device_config": device_config
                }
            )
            
            # Update device data
            self._edge_devices[device_id]["device_config"] = device_config
            self._edge_devices[device_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Updated device {device_id}")
            
            return {
                "device_id": device_id,
                "device_type": self._edge_devices[device_id]["device_type"],
                "device_config": device_config,
                "gateway_id": self._edge_devices[device_id]["gateway_id"],
                "status": self._edge_devices[device_id]["status"]
            }
        except Exception as e:
            self.logger.error(f"Error updating device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def deregister_device(self, device_id: str) -> Dict[str, Any]:
        """
        Deregister an edge device.
        
        Args:
            device_id: Device ID
        
        Returns:
            Deregistration result
        """
        try:
            # Check if device exists
            if device_id not in self._edge_devices:
                raise ValueError(f"Device {device_id} not found")
            
            # In a real implementation, this would deregister the device using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish device deregistered event
            self.event_bus.publish(
                topic="edge_systems.device.device_deregistered",
                data={
                    "device_id": device_id
                }
            )
            
            # Update device data
            device_data = self._edge_devices[device_id].copy()
            device_data["status"] = "deregistered"
            
            # Remove device from device groups
            for group_id, group_data in self._device_groups.items():
                if device_id in group_data["devices"]:
                    group_data["devices"].remove(device_id)
            
            # Remove device data
            del self._edge_devices[device_id]
            
            # Update metrics
            self._metrics["total_edge_devices"] -= 1
            if device_data["connected"]:
                self._metrics["total_active_devices"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Deregistered device {device_id}")
            
            return {
                "device_id": device_id,
                "status": "deregistered"
            }
        except Exception as e:
            self.logger.error(f"Error deregistering device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_device(self, device_id: str) -> Dict[str, Any]:
        """
        Get an edge device.
        
        Args:
            device_id: Device ID
        
        Returns:
            Device data
        """
        try:
            # Check if device exists
            if device_id not in self._edge_devices:
                raise ValueError(f"Device {device_id} not found")
            
            # Get device data
            device_data = self._edge_devices[device_id]
            
            return {
                "device_id": device_id,
                "device_type": device_data["device_type"],
                "device_config": device_data["device_config"],
                "gateway_id": device_data["gateway_id"],
                "status": device_data["status"],
                "connected": device_data["connected"],
                "last_connected_at": device_data["last_connected_at"],
                "last_disconnected_at": device_data["last_disconnected_at"],
                "registered_at": device_data["registered_at"],
                "updated_at": device_data["updated_at"]
            }
        except Exception as e:
            self.logger.error(f"Error getting device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_devices(self, device_type: str = None, gateway_id: str = None, device_group_id: str = None) -> List[Dict[str, Any]]:
        """
        List edge devices.
        
        Args:
            device_type: Optional device type filter
            gateway_id: Optional gateway ID filter
            device_group_id: Optional device group ID filter
        
        Returns:
            List of device data
        """
        try:
            # Apply filters
            devices = []
            
            # If device group filter is provided, get devices from group
            if device_group_id:
                if device_group_id not in self._device_groups:
                    raise ValueError(f"Device group {device_group_id} not found")
                
                device_ids = self._device_groups[device_group_id]["devices"]
            else:
                device_ids = list(self._edge_devices.keys())
            
            for device_id in device_ids:
                # Skip if device doesn't exist (could happen if device was deregistered)
                if device_id not in self._edge_devices:
                    continue
                
                device_data = self._edge_devices[device_id]
                
                # Apply device type filter if provided
                if device_type and device_data["device_type"] != device_type:
                    continue
                
                # Apply gateway filter if provided
                if gateway_id and device_data["gateway_id"] != gateway_id:
                    continue
                
                # Add device to results
                devices.append({
                    "device_id": device_id,
                    "device_type": device_data["device_type"],
                    "device_config": device_data["device_config"],
                    "gateway_id": device_data["gateway_id"],
                    "status": device_data["status"],
                    "connected": device_data["connected"],
                    "last_connected_at": device_data["last_connected_at"],
                    "last_disconnected_at": device_data["last_disconnected_at"],
                    "registered_at": device_data["registered_at"],
                    "updated_at": device_data["updated_at"]
                })
            
            return devices
        except Exception as e:
            self.logger.error(f"Error listing devices: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_gateway(self, gateway_type: str, gateway_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register an edge gateway.
        
        Args:
            gateway_type: Gateway type
            gateway_config: Gateway configuration
        
        Returns:
            Registered gateway data
        """
        try:
            # Generate gateway ID
            gateway_id = f"gateway-{self.data_access.generate_id()}"
            
            # In a real implementation, this would register the gateway using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish gateway registered event
            self.event_bus.publish(
                topic="edge_systems.gateway.gateway_registered",
                data={
                    "gateway_id": gateway_id,
                    "gateway_type": gateway_type,
                    "gateway_config": gateway_config
                }
            )
            
            # Store gateway data
            self._edge_gateways[gateway_id] = {
                "gateway_type": gateway_type,
                "gateway_config": gateway_config,
                "status": "registered",
                "registered_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_edge_gateways"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Registered gateway {gateway_id} with type {gateway_type}")
            
            return {
                "gateway_id": gateway_id,
                "gateway_type": gateway_type,
                "gateway_config": gateway_config,
                "status": "registered"
            }
        except Exception as e:
            self.logger.error(f"Error registering gateway: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def update_gateway(self, gateway_id: str, gateway_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an edge gateway.
        
        Args:
            gateway_id: Gateway ID
            gateway_config: Gateway configuration
        
        Returns:
            Updated gateway data
        """
        try:
            # Check if gateway exists
            if gateway_id not in self._edge_gateways:
                raise ValueError(f"Gateway {gateway_id} not found")
            
            # In a real implementation, this would update the gateway using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish gateway updated event
            self.event_bus.publish(
                topic="edge_systems.gateway.gateway_updated",
                data={
                    "gateway_id": gateway_id,
                    "gateway_config": gateway_config
                }
            )
            
            # Update gateway data
            self._edge_gateways[gateway_id]["gateway_config"] = gateway_config
            self._edge_gateways[gateway_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Updated gateway {gateway_id}")
            
            return {
                "gateway_id": gateway_id,
                "gateway_type": self._edge_gateways[gateway_id]["gateway_type"],
                "gateway_config": gateway_config,
                "status": self._edge_gateways[gateway_id]["status"]
            }
        except Exception as e:
            self.logger.error(f"Error updating gateway {gateway_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def deregister_gateway(self, gateway_id: str) -> Dict[str, Any]:
        """
        Deregister an edge gateway.
        
        Args:
            gateway_id: Gateway ID
        
        Returns:
            Deregistration result
        """
        try:
            # Check if gateway exists
            if gateway_id not in self._edge_gateways:
                raise ValueError(f"Gateway {gateway_id} not found")
            
            # Check if gateway has devices
            for device_id, device_data in self._edge_devices.items():
                if device_data["gateway_id"] == gateway_id:
                    raise ValueError(f"Gateway {gateway_id} has devices, deregister devices first")
            
            # In a real implementation, this would deregister the gateway using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish gateway deregistered event
            self.event_bus.publish(
                topic="edge_systems.gateway.gateway_deregistered",
                data={
                    "gateway_id": gateway_id
                }
            )
            
            # Update gateway data
            gateway_data = self._edge_gateways[gateway_id].copy()
            gateway_data["status"] = "deregistered"
            
            # Remove gateway data
            del self._edge_gateways[gateway_id]
            
            # Update metrics
            self._metrics["total_edge_gateways"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Deregistered gateway {gateway_id}")
            
            return {
                "gateway_id": gateway_id,
                "status": "deregistered"
            }
        except Exception as e:
            self.logger.error(f"Error deregistering gateway {gateway_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_gateway(self, gateway_id: str) -> Dict[str, Any]:
        """
        Get an edge gateway.
        
        Args:
            gateway_id: Gateway ID
        
        Returns:
            Gateway data
        """
        try:
            # Check if gateway exists
            if gateway_id not in self._edge_gateways:
                raise ValueError(f"Gateway {gateway_id} not found")
            
            # Get gateway data
            gateway_data = self._edge_gateways[gateway_id]
            
            return {
                "gateway_id": gateway_id,
                "gateway_type": gateway_data["gateway_type"],
                "gateway_config": gateway_data["gateway_config"],
                "status": gateway_data["status"],
                "registered_at": gateway_data["registered_at"],
                "updated_at": gateway_data["updated_at"]
            }
        except Exception as e:
            self.logger.error(f"Error getting gateway {gateway_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_gateways(self, gateway_type: str = None) -> List[Dict[str, Any]]:
        """
        List edge gateways.
        
        Args:
            gateway_type: Optional gateway type filter
        
        Returns:
            List of gateway data
        """
        try:
            # Apply filters
            gateways = []
            
            for gateway_id, gateway_data in self._edge_gateways.items():
                # Apply gateway type filter if provided
                if gateway_type and gateway_data["gateway_type"] != gateway_type:
                    continue
                
                # Add gateway to results
                gateways.append({
                    "gateway_id": gateway_id,
                    "gateway_type": gateway_data["gateway_type"],
                    "gateway_config": gateway_data["gateway_config"],
                    "status": gateway_data["status"],
                    "registered_at": gateway_data["registered_at"],
                    "updated_at": gateway_data["updated_at"]
                })
            
            return gateways
        except Exception as e:
            self.logger.error(f"Error listing gateways: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def create_device_group(self, group_name: str, group_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a device group.
        
        Args:
            group_name: Group name
            group_config: Group configuration
        
        Returns:
            Created device group data
        """
        try:
            # Generate group ID
            group_id = f"group-{self.data_access.generate_id()}"
            
            # In a real implementation, this would create the device group using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish device group created event
            self.event_bus.publish(
                topic="edge_systems.device_group.device_group_created",
                data={
                    "group_id": group_id,
                    "group_name": group_name,
                    "group_config": group_config
                }
            )
            
            # Store device group data
            self._device_groups[group_id] = {
                "group_name": group_name,
                "group_config": group_config,
                "devices": [],
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_device_groups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Created device group {group_id} with name {group_name}")
            
            return {
                "group_id": group_id,
                "group_name": group_name,
                "group_config": group_config,
                "devices": []
            }
        except Exception as e:
            self.logger.error(f"Error creating device group: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def update_device_group(self, group_id: str, group_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a device group.
        
        Args:
            group_id: Group ID
            group_config: Group configuration
        
        Returns:
            Updated device group data
        """
        try:
            # Check if device group exists
            if group_id not in self._device_groups:
                raise ValueError(f"Device group {group_id} not found")
            
            # In a real implementation, this would update the device group using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish device group updated event
            self.event_bus.publish(
                topic="edge_systems.device_group.device_group_updated",
                data={
                    "group_id": group_id,
                    "group_config": group_config
                }
            )
            
            # Update device group data
            self._device_groups[group_id]["group_config"] = group_config
            self._device_groups[group_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Updated device group {group_id}")
            
            return {
                "group_id": group_id,
                "group_name": self._device_groups[group_id]["group_name"],
                "group_config": group_config,
                "devices": self._device_groups[group_id]["devices"]
            }
        except Exception as e:
            self.logger.error(f"Error updating device group {group_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def delete_device_group(self, group_id: str) -> Dict[str, Any]:
        """
        Delete a device group.
        
        Args:
            group_id: Group ID
        
        Returns:
            Deletion result
        """
        try:
            # Check if device group exists
            if group_id not in self._device_groups:
                raise ValueError(f"Device group {group_id} not found")
            
            # In a real implementation, this would delete the device group using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish device group deleted event
            self.event_bus.publish(
                topic="edge_systems.device_group.device_group_deleted",
                data={
                    "group_id": group_id
                }
            )
            
            # Update device group data
            group_data = self._device_groups[group_id].copy()
            
            # Remove device group data
            del self._device_groups[group_id]
            
            # Update metrics
            self._metrics["total_device_groups"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Deleted device group {group_id}")
            
            return {
                "group_id": group_id,
                "status": "deleted"
            }
        except Exception as e:
            self.logger.error(f"Error deleting device group {group_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def add_device_to_group(self, group_id: str, device_id: str) -> Dict[str, Any]:
        """
        Add a device to a device group.
        
        Args:
            group_id: Group ID
            device_id: Device ID
        
        Returns:
            Addition result
        """
        try:
            # Check if device group exists
            if group_id not in self._device_groups:
                raise ValueError(f"Device group {group_id} not found")
            
            # Check if device exists
            if device_id not in self._edge_devices:
                raise ValueError(f"Device {device_id} not found")
            
            # Check if device is already in group
            if device_id in self._device_groups[group_id]["devices"]:
                raise ValueError(f"Device {device_id} is already in group {group_id}")
            
            # In a real implementation, this would add the device to the group using the appropriate adapter
            # For now, we'll just simulate it
            
            # Add device to group
            self._device_groups[group_id]["devices"].append(device_id)
            self._device_groups[group_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Added device {device_id} to group {group_id}")
            
            return {
                "group_id": group_id,
                "device_id": device_id,
                "status": "added"
            }
        except Exception as e:
            self.logger.error(f"Error adding device {device_id} to group {group_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def remove_device_from_group(self, group_id: str, device_id: str) -> Dict[str, Any]:
        """
        Remove a device from a device group.
        
        Args:
            group_id: Group ID
            device_id: Device ID
        
        Returns:
            Removal result
        """
        try:
            # Check if device group exists
            if group_id not in self._device_groups:
                raise ValueError(f"Device group {group_id} not found")
            
            # Check if device is in group
            if device_id not in self._device_groups[group_id]["devices"]:
                raise ValueError(f"Device {device_id} is not in group {group_id}")
            
            # In a real implementation, this would remove the device from the group using the appropriate adapter
            # For now, we'll just simulate it
            
            # Remove device from group
            self._device_groups[group_id]["devices"].remove(device_id)
            self._device_groups[group_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Removed device {device_id} from group {group_id}")
            
            return {
                "group_id": group_id,
                "device_id": device_id,
                "status": "removed"
            }
        except Exception as e:
            self.logger.error(f"Error removing device {device_id} from group {group_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_device_group(self, group_id: str) -> Dict[str, Any]:
        """
        Get a device group.
        
        Args:
            group_id: Group ID
        
        Returns:
            Device group data
        """
        try:
            # Check if device group exists
            if group_id not in self._device_groups:
                raise ValueError(f"Device group {group_id} not found")
            
            # Get device group data
            group_data = self._device_groups[group_id]
            
            return {
                "group_id": group_id,
                "group_name": group_data["group_name"],
                "group_config": group_data["group_config"],
                "devices": group_data["devices"],
                "created_at": group_data["created_at"],
                "updated_at": group_data["updated_at"]
            }
        except Exception as e:
            self.logger.error(f"Error getting device group {group_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_device_groups(self) -> List[Dict[str, Any]]:
        """
        List device groups.
        
        Returns:
            List of device group data
        """
        try:
            # Get all device groups
            groups = []
            
            for group_id, group_data in self._device_groups.items():
                # Add group to results
                groups.append({
                    "group_id": group_id,
                    "group_name": group_data["group_name"],
                    "group_config": group_data["group_config"],
                    "devices": group_data["devices"],
                    "created_at": group_data["created_at"],
                    "updated_at": group_data["updated_at"]
                })
            
            return groups
        except Exception as e:
            self.logger.error(f"Error listing device groups: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_telemetry(self, device_id: str, telemetry_type: str = None) -> Dict[str, Any]:
        """
        Get telemetry data for a device.
        
        Args:
            device_id: Device ID
            telemetry_type: Optional telemetry type filter
        
        Returns:
            Telemetry data
        """
        try:
            # Check if device exists
            if device_id not in self._edge_devices:
                raise ValueError(f"Device {device_id} not found")
            
            # Get telemetry data
            telemetry = {}
            
            for telemetry_key, telemetry_stream in self._telemetry_streams.items():
                # Parse telemetry key
                key_device_id, key_telemetry_type = telemetry_key.split(":", 1)
                
                # Skip if not for the requested device
                if key_device_id != device_id:
                    continue
                
                # Skip if telemetry type filter is provided and doesn't match
                if telemetry_type and key_telemetry_type != telemetry_type:
                    continue
                
                # Get latest telemetry data
                if telemetry_stream:
                    telemetry[key_telemetry_type] = telemetry_stream[-1]
            
            return {
                "device_id": device_id,
                "telemetry": telemetry
            }
        except Exception as e:
            self.logger.error(f"Error getting telemetry for device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_telemetry_history(self, device_id: str, telemetry_type: str = None, start_time: str = None, end_time: str = None, limit: int = None) -> Dict[str, Any]:
        """
        Get telemetry history for a device.
        
        Args:
            device_id: Device ID
            telemetry_type: Optional telemetry type filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Optional limit filter
        
        Returns:
            Telemetry history data
        """
        try:
            # Check if device exists
            if device_id not in self._edge_devices:
                raise ValueError(f"Device {device_id} not found")
            
            # Get telemetry history
            telemetry_history = {}
            
            for telemetry_key, telemetry_stream in self._telemetry_streams.items():
                # Parse telemetry key
                key_device_id, key_telemetry_type = telemetry_key.split(":", 1)
                
                # Skip if not for the requested device
                if key_device_id != device_id:
                    continue
                
                # Skip if telemetry type filter is provided and doesn't match
                if telemetry_type and key_telemetry_type != telemetry_type:
                    continue
                
                # Filter telemetry data
                filtered_stream = []
                
                for telemetry_data in telemetry_stream:
                    # Apply start time filter if provided
                    if start_time and telemetry_data["timestamp"] < start_time:
                        continue
                    
                    # Apply end time filter if provided
                    if end_time and telemetry_data["timestamp"] > end_time:
                        continue
                    
                    # Add telemetry data to filtered stream
                    filtered_stream.append(telemetry_data)
                
                # Apply limit filter if provided
                if limit and len(filtered_stream) > limit:
                    filtered_stream = filtered_stream[-limit:]
                
                # Add filtered stream to telemetry history
                telemetry_history[key_telemetry_type] = filtered_stream
            
            return {
                "device_id": device_id,
                "telemetry_history": telemetry_history
            }
        except Exception as e:
            self.logger.error(f"Error getting telemetry history for device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def subscribe_to_telemetry(self, device_id: str, telemetry_type: str = None) -> Dict[str, Any]:
        """
        Subscribe to telemetry data for a device.
        
        Args:
            device_id: Device ID
            telemetry_type: Optional telemetry type filter
        
        Returns:
            Subscription data
        """
        try:
            # Check if device exists
            if device_id not in self._edge_devices:
                raise ValueError(f"Device {device_id} not found")
            
            # In a real implementation, this would subscribe to telemetry data using the appropriate adapter
            # For now, we'll just simulate it
            
            # Generate subscription ID
            subscription_id = f"subscription-{self.data_access.generate_id()}"
            
            self.logger.info(f"Subscribed to telemetry for device {device_id}")
            
            return {
                "subscription_id": subscription_id,
                "device_id": device_id,
                "telemetry_type": telemetry_type,
                "status": "subscribed"
            }
        except Exception as e:
            self.logger.error(f"Error subscribing to telemetry for device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def unsubscribe_from_telemetry(self, subscription_id: str) -> Dict[str, Any]:
        """
        Unsubscribe from telemetry data.
        
        Args:
            subscription_id: Subscription ID
        
        Returns:
            Unsubscription result
        """
        try:
            # In a real implementation, this would unsubscribe from telemetry data using the appropriate adapter
            # For now, we'll just simulate it
            
            self.logger.info(f"Unsubscribed from telemetry with subscription {subscription_id}")
            
            return {
                "subscription_id": subscription_id,
                "status": "unsubscribed"
            }
        except Exception as e:
            self.logger.error(f"Error unsubscribing from telemetry with subscription {subscription_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def send_command(self, device_id: str, command_type: str, command_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to a device.
        
        Args:
            device_id: Device ID
            command_type: Command type
            command_payload: Command payload
        
        Returns:
            Command data
        """
        try:
            # Check if device exists
            if device_id not in self._edge_devices:
                raise ValueError(f"Device {device_id} not found")
            
            # Check if device is connected
            if not self._edge_devices[device_id]["connected"]:
                raise ValueError(f"Device {device_id} is not connected")
            
            # Generate command ID
            command_id = f"command-{self.data_access.generate_id()}"
            
            # In a real implementation, this would send the command using the appropriate adapter
            # For now, we'll just simulate it
            
            # Publish command sent event
            self.event_bus.publish(
                topic="edge_systems.command.command_sent",
                data={
                    "command_id": command_id,
                    "device_id": device_id,
                    "command_type": command_type,
                    "command_payload": command_payload
                }
            )
            
            # Store command data
            command_key = f"{device_id}:{command_type}"
            if command_key not in self._command_queues:
                self._command_queues[command_key] = []
                self._metrics["total_command_queues"] += 1
            
            # Add command data to queue
            self._command_queues[command_key].append({
                "command_id": command_id,
                "device_id": device_id,
                "command_type": command_type,
                "command_payload": command_payload,
                "status": "sent",
                "result": None,
                "sent_at": self.data_access.get_current_timestamp(),
                "completed_at": None
            })
            
            # Limit command queue size
            max_queue_size = 100  # In a real implementation, this would be configurable
            if len(self._command_queues[command_key]) > max_queue_size:
                self._command_queues[command_key] = self._command_queues[command_key][-max_queue_size:]
            
            # Update metrics
            self._metrics["total_commands_sent"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Sent command {command_id} to device {device_id} with type {command_type}")
            
            # Simulate command result
            import random
            import threading
            import time
            
            def simulate_command_result():
                # Simulate processing time
                time.sleep(random.uniform(0.5, 2.0))
                
                # Generate result
                result = {
                    "status": random.choice(["success", "partial_success", "failure"]),
                    "message": f"Command {command_type} executed",
                    "data": {}
                }
                
                # Publish command result received event
                self.event_bus.publish(
                    topic="edge_systems.command.command_result_received",
                    data={
                        "command_id": command_id,
                        "device_id": device_id,
                        "command_type": command_type,
                        "result": result
                    }
                )
            
            # Start simulation thread
            threading.Thread(target=simulate_command_result).start()
            
            return {
                "command_id": command_id,
                "device_id": device_id,
                "command_type": command_type,
                "command_payload": command_payload,
                "status": "sent"
            }
        except Exception as e:
            self.logger.error(f"Error sending command to device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def send_group_command(self, group_id: str, command_type: str, command_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to a device group.
        
        Args:
            group_id: Group ID
            command_type: Command type
            command_payload: Command payload
        
        Returns:
            Group command data
        """
        try:
            # Check if device group exists
            if group_id not in self._device_groups:
                raise ValueError(f"Device group {group_id} not found")
            
            # Get devices in group
            device_ids = self._device_groups[group_id]["devices"]
            
            # Check if group has devices
            if not device_ids:
                raise ValueError(f"Device group {group_id} has no devices")
            
            # Send command to each device
            command_results = []
            
            for device_id in device_ids:
                try:
                    # Skip if device doesn't exist
                    if device_id not in self._edge_devices:
                        command_results.append({
                            "device_id": device_id,
                            "status": "error",
                            "error": "Device not found"
                        })
                        continue
                    
                    # Skip if device is not connected
                    if not self._edge_devices[device_id]["connected"]:
                        command_results.append({
                            "device_id": device_id,
                            "status": "error",
                            "error": "Device not connected"
                        })
                        continue
                    
                    # Send command to device
                    result = self.send_command(
                        device_id=device_id,
                        command_type=command_type,
                        command_payload=command_payload
                    )
                    
                    # Add result to command results
                    command_results.append({
                        "device_id": device_id,
                        "command_id": result["command_id"],
                        "status": "sent"
                    })
                except Exception as e:
                    # Add error to command results
                    command_results.append({
                        "device_id": device_id,
                        "status": "error",
                        "error": str(e)
                    })
            
            self.logger.info(f"Sent group command to group {group_id} with type {command_type}")
            
            return {
                "group_id": group_id,
                "command_type": command_type,
                "command_payload": command_payload,
                "results": command_results
            }
        except Exception as e:
            self.logger.error(f"Error sending group command to group {group_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_command_status(self, command_id: str) -> Dict[str, Any]:
        """
        Get the status of a command.
        
        Args:
            command_id: Command ID
        
        Returns:
            Command status data
        """
        try:
            # Find command
            for command_key, command_queue in self._command_queues.items():
                for command in command_queue:
                    if command["command_id"] == command_id:
                        return {
                            "command_id": command_id,
                            "device_id": command["device_id"],
                            "command_type": command["command_type"],
                            "command_payload": command["command_payload"],
                            "status": command["status"],
                            "result": command["result"],
                            "sent_at": command["sent_at"],
                            "completed_at": command["completed_at"]
                        }
            
            # Command not found
            raise ValueError(f"Command {command_id} not found")
        except Exception as e:
            self.logger.error(f"Error getting command status for command {command_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_command_history(self, device_id: str, command_type: str = None, start_time: str = None, end_time: str = None, limit: int = None) -> Dict[str, Any]:
        """
        Get command history for a device.
        
        Args:
            device_id: Device ID
            command_type: Optional command type filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Optional limit filter
        
        Returns:
            Command history data
        """
        try:
            # Check if device exists
            if device_id not in self._edge_devices:
                raise ValueError(f"Device {device_id} not found")
            
            # Get command history
            command_history = {}
            
            for command_key, command_queue in self._command_queues.items():
                # Parse command key
                key_device_id, key_command_type = command_key.split(":", 1)
                
                # Skip if not for the requested device
                if key_device_id != device_id:
                    continue
                
                # Skip if command type filter is provided and doesn't match
                if command_type and key_command_type != command_type:
                    continue
                
                # Filter command data
                filtered_queue = []
                
                for command in command_queue:
                    # Apply start time filter if provided
                    if start_time and command["sent_at"] < start_time:
                        continue
                    
                    # Apply end time filter if provided
                    if end_time and command["sent_at"] > end_time:
                        continue
                    
                    # Add command to filtered queue
                    filtered_queue.append(command)
                
                # Apply limit filter if provided
                if limit and len(filtered_queue) > limit:
                    filtered_queue = filtered_queue[-limit:]
                
                # Add filtered queue to command history
                command_history[key_command_type] = filtered_queue
            
            return {
                "device_id": device_id,
                "command_history": command_history
            }
        except Exception as e:
            self.logger.error(f"Error getting command history for device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the manager metrics.
        
        Returns:
            Manager metrics
        """
        return self._metrics
    
    def reset_metrics(self) -> Dict[str, Any]:
        """
        Reset the manager metrics.
        
        Returns:
            Reset manager metrics
        """
        self._metrics = {
            "total_edge_devices": 0,
            "total_active_devices": 0,
            "total_edge_gateways": 0,
            "total_device_groups": 0,
            "total_telemetry_streams": 0,
            "total_command_queues": 0,
            "total_telemetry_messages": 0,
            "total_commands_sent": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
