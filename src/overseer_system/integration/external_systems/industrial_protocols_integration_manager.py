"""
Industrial Protocols Integration Manager for the Overseer System.

This module provides the Industrial Protocols Integration Manager for integrating with
various industrial protocols including Modbus, OPC UA, MQTT, PROFINET, and others,
enabling communication with industrial equipment and systems.

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

class IndustrialProtocolsIntegrationManager(IntegrationManager):
    """
    Integration Manager for Industrial Protocols.
    
    This class provides integration with various industrial protocols including
    Modbus, OPC UA, MQTT, PROFINET, and others, enabling communication with
    industrial equipment and systems.
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
        Initialize the Industrial Protocols Integration Manager.
        
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
            manager_type="industrial_protocols",
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            config=config,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize protocol-specific resources
        self._protocol_adapters = {}
        self._device_connections = {}
        self._data_points = {}
        self._subscriptions = {}
        
        # Initialize metrics
        self._metrics = {
            "total_device_connections": 0,
            "total_active_connections": 0,
            "total_data_points": 0,
            "total_data_reads": 0,
            "total_data_writes": 0,
            "total_subscriptions": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Industrial Protocols Integration Manager {manager_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Industrial Protocol operations
        self.mcp_bridge.register_context_handler(
            context_type="industrial_protocols.device",
            handler=self._handle_mcp_device_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="industrial_protocols.data_point",
            handler=self._handle_mcp_data_point_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="industrial_protocols.subscription",
            handler=self._handle_mcp_subscription_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Industrial Protocol operations
        self.mcp_bridge.unregister_context_handler(
            context_type="industrial_protocols.device"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="industrial_protocols.data_point"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="industrial_protocols.subscription"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Industrial Protocol operations
        self.a2a_bridge.register_capability_handler(
            capability_type="device_management",
            handler=self._handle_a2a_device_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="data_point_management",
            handler=self._handle_a2a_data_point_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="subscription_management",
            handler=self._handle_a2a_subscription_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Industrial Protocol operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="device_management"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="data_point_management"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="subscription_management"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Industrial Protocol-related events
        self.event_bus.subscribe(
            topic="industrial_protocols.device.device_connected",
            handler=self._handle_device_connected_event
        )
        
        self.event_bus.subscribe(
            topic="industrial_protocols.device.device_disconnected",
            handler=self._handle_device_disconnected_event
        )
        
        self.event_bus.subscribe(
            topic="industrial_protocols.data_point.data_point_created",
            handler=self._handle_data_point_created_event
        )
        
        self.event_bus.subscribe(
            topic="industrial_protocols.data_point.data_point_updated",
            handler=self._handle_data_point_updated_event
        )
        
        self.event_bus.subscribe(
            topic="industrial_protocols.data_point.data_point_deleted",
            handler=self._handle_data_point_deleted_event
        )
        
        self.event_bus.subscribe(
            topic="industrial_protocols.data_point.data_point_value_changed",
            handler=self._handle_data_point_value_changed_event
        )
        
        self.event_bus.subscribe(
            topic="industrial_protocols.subscription.subscription_created",
            handler=self._handle_subscription_created_event
        )
        
        self.event_bus.subscribe(
            topic="industrial_protocols.subscription.subscription_deleted",
            handler=self._handle_subscription_deleted_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Industrial Protocol-related events
        self.event_bus.unsubscribe(
            topic="industrial_protocols.device.device_connected"
        )
        
        self.event_bus.unsubscribe(
            topic="industrial_protocols.device.device_disconnected"
        )
        
        self.event_bus.unsubscribe(
            topic="industrial_protocols.data_point.data_point_created"
        )
        
        self.event_bus.unsubscribe(
            topic="industrial_protocols.data_point.data_point_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="industrial_protocols.data_point.data_point_deleted"
        )
        
        self.event_bus.unsubscribe(
            topic="industrial_protocols.data_point.data_point_value_changed"
        )
        
        self.event_bus.unsubscribe(
            topic="industrial_protocols.subscription.subscription_created"
        )
        
        self.event_bus.unsubscribe(
            topic="industrial_protocols.subscription.subscription_deleted"
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
            if action == "connect_device":
                protocol_type = context.get("protocol_type")
                if not protocol_type:
                    raise ValueError("protocol_type is required")
                
                device_config = context.get("device_config")
                if not device_config:
                    raise ValueError("device_config is required")
                
                result = self.connect_device(
                    protocol_type=protocol_type,
                    device_config=device_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "disconnect_device":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                result = self.disconnect_device(
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
                protocol_type = context.get("protocol_type")
                
                result = self.list_devices(
                    protocol_type=protocol_type
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
    
    def _handle_mcp_data_point_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Data Point context.
        
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
            if action == "create_data_point":
                device_id = context.get("device_id")
                if not device_id:
                    raise ValueError("device_id is required")
                
                data_point_config = context.get("data_point_config")
                if not data_point_config:
                    raise ValueError("data_point_config is required")
                
                result = self.create_data_point(
                    device_id=device_id,
                    data_point_config=data_point_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "update_data_point":
                data_point_id = context.get("data_point_id")
                if not data_point_id:
                    raise ValueError("data_point_id is required")
                
                data_point_config = context.get("data_point_config")
                if not data_point_config:
                    raise ValueError("data_point_config is required")
                
                result = self.update_data_point(
                    data_point_id=data_point_id,
                    data_point_config=data_point_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "delete_data_point":
                data_point_id = context.get("data_point_id")
                if not data_point_id:
                    raise ValueError("data_point_id is required")
                
                result = self.delete_data_point(
                    data_point_id=data_point_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "read_data_point":
                data_point_id = context.get("data_point_id")
                if not data_point_id:
                    raise ValueError("data_point_id is required")
                
                result = self.read_data_point(
                    data_point_id=data_point_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "write_data_point":
                data_point_id = context.get("data_point_id")
                if not data_point_id:
                    raise ValueError("data_point_id is required")
                
                value = context.get("value")
                if value is None:
                    raise ValueError("value is required")
                
                result = self.write_data_point(
                    data_point_id=data_point_id,
                    value=value
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_data_point":
                data_point_id = context.get("data_point_id")
                if not data_point_id:
                    raise ValueError("data_point_id is required")
                
                result = self.get_data_point(
                    data_point_id=data_point_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_data_points":
                device_id = context.get("device_id")
                
                result = self.list_data_points(
                    device_id=device_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Data Point context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_subscription_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Subscription context.
        
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
            if action == "create_subscription":
                data_point_id = context.get("data_point_id")
                if not data_point_id:
                    raise ValueError("data_point_id is required")
                
                subscription_config = context.get("subscription_config")
                if not subscription_config:
                    raise ValueError("subscription_config is required")
                
                result = self.create_subscription(
                    data_point_id=data_point_id,
                    subscription_config=subscription_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "delete_subscription":
                subscription_id = context.get("subscription_id")
                if not subscription_id:
                    raise ValueError("subscription_id is required")
                
                result = self.delete_subscription(
                    subscription_id=subscription_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_subscription":
                subscription_id = context.get("subscription_id")
                if not subscription_id:
                    raise ValueError("subscription_id is required")
                
                result = self.get_subscription(
                    subscription_id=subscription_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_subscriptions":
                data_point_id = context.get("data_point_id")
                
                result = self.list_subscriptions(
                    data_point_id=data_point_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Subscription context: {str(e)}")
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
                protocol_type = capability_data.get("protocol_type")
                
                result = self.list_devices(
                    protocol_type=protocol_type
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
    
    def _handle_a2a_data_point_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Data Point capability.
        
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
            if action == "read_data_point":
                data_point_id = capability_data.get("data_point_id")
                if not data_point_id:
                    raise ValueError("data_point_id is required")
                
                result = self.read_data_point(
                    data_point_id=data_point_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_data_point":
                data_point_id = capability_data.get("data_point_id")
                if not data_point_id:
                    raise ValueError("data_point_id is required")
                
                result = self.get_data_point(
                    data_point_id=data_point_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_data_points":
                device_id = capability_data.get("device_id")
                
                result = self.list_data_points(
                    device_id=device_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Data Point capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_subscription_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Subscription capability.
        
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
            if action == "get_subscription":
                subscription_id = capability_data.get("subscription_id")
                if not subscription_id:
                    raise ValueError("subscription_id is required")
                
                result = self.get_subscription(
                    subscription_id=subscription_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_subscriptions":
                data_point_id = capability_data.get("data_point_id")
                
                result = self.list_subscriptions(
                    data_point_id=data_point_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Subscription capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_device_connected_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle device connected event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            device_id = event_data.get("device_id")
            protocol_type = event_data.get("protocol_type")
            device_config = event_data.get("device_config")
            
            # Validate required fields
            if not device_id:
                self.logger.warning("Received device connected event without device_id")
                return
            
            if not protocol_type:
                self.logger.warning(f"Received device connected event for device {device_id} without protocol_type")
                return
            
            if not device_config:
                self.logger.warning(f"Received device connected event for device {device_id} without device_config")
                return
            
            self.logger.info(f"Device {device_id} connected using protocol {protocol_type}")
            
            # Store device connection data
            self._device_connections[device_id] = {
                "protocol_type": protocol_type,
                "device_config": device_config,
                "status": "connected",
                "connected_at": self.data_access.get_current_timestamp(),
                "disconnected_at": None
            }
            
            # Update metrics
            self._metrics["total_device_connections"] += 1
            self._metrics["total_active_connections"] += 1
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
            if device_id not in self._device_connections:
                self.logger.warning(f"Received device disconnected event for non-existent device {device_id}")
                return
            
            self.logger.info(f"Device {device_id} disconnected")
            
            # Update device connection data
            self._device_connections[device_id]["status"] = "disconnected"
            self._device_connections[device_id]["disconnected_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["total_active_connections"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling device disconnected event: {str(e)}")
    
    def _handle_data_point_created_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle data point created event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            data_point_id = event_data.get("data_point_id")
            device_id = event_data.get("device_id")
            data_point_config = event_data.get("data_point_config")
            
            # Validate required fields
            if not data_point_id:
                self.logger.warning("Received data point created event without data_point_id")
                return
            
            if not device_id:
                self.logger.warning(f"Received data point created event for data point {data_point_id} without device_id")
                return
            
            if not data_point_config:
                self.logger.warning(f"Received data point created event for data point {data_point_id} without data_point_config")
                return
            
            self.logger.info(f"Data point {data_point_id} created for device {device_id}")
            
            # Store data point data
            self._data_points[data_point_id] = {
                "device_id": device_id,
                "data_point_config": data_point_config,
                "current_value": None,
                "last_read_time": None,
                "last_write_time": None,
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_data_points"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling data point created event: {str(e)}")
    
    def _handle_data_point_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle data point updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            data_point_id = event_data.get("data_point_id")
            data_point_config = event_data.get("data_point_config")
            
            # Validate required fields
            if not data_point_id:
                self.logger.warning("Received data point updated event without data_point_id")
                return
            
            if not data_point_config:
                self.logger.warning(f"Received data point updated event for data point {data_point_id} without data_point_config")
                return
            
            # Check if data point exists
            if data_point_id not in self._data_points:
                self.logger.warning(f"Received data point updated event for non-existent data point {data_point_id}")
                return
            
            self.logger.info(f"Data point {data_point_id} updated")
            
            # Update data point data
            self._data_points[data_point_id]["data_point_config"] = data_point_config
            self._data_points[data_point_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling data point updated event: {str(e)}")
    
    def _handle_data_point_deleted_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle data point deleted event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            data_point_id = event_data.get("data_point_id")
            
            # Validate required fields
            if not data_point_id:
                self.logger.warning("Received data point deleted event without data_point_id")
                return
            
            # Check if data point exists
            if data_point_id not in self._data_points:
                self.logger.warning(f"Received data point deleted event for non-existent data point {data_point_id}")
                return
            
            self.logger.info(f"Data point {data_point_id} deleted")
            
            # Remove data point data
            del self._data_points[data_point_id]
            
            # Update metrics
            self._metrics["total_data_points"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling data point deleted event: {str(e)}")
    
    def _handle_data_point_value_changed_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle data point value changed event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            data_point_id = event_data.get("data_point_id")
            value = event_data.get("value")
            source = event_data.get("source")
            
            # Validate required fields
            if not data_point_id:
                self.logger.warning("Received data point value changed event without data_point_id")
                return
            
            if value is None:
                self.logger.warning(f"Received data point value changed event for data point {data_point_id} without value")
                return
            
            # Check if data point exists
            if data_point_id not in self._data_points:
                self.logger.warning(f"Received data point value changed event for non-existent data point {data_point_id}")
                return
            
            self.logger.info(f"Data point {data_point_id} value changed to {value} from {source}")
            
            # Update data point data
            self._data_points[data_point_id]["current_value"] = value
            
            if source == "read":
                self._data_points[data_point_id]["last_read_time"] = self.data_access.get_current_timestamp()
                self._metrics["total_data_reads"] += 1
            elif source == "write":
                self._data_points[data_point_id]["last_write_time"] = self.data_access.get_current_timestamp()
                self._metrics["total_data_writes"] += 1
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            # Notify subscribers
            self._notify_subscribers(data_point_id, value)
        except Exception as e:
            self.logger.error(f"Error handling data point value changed event: {str(e)}")
    
    def _handle_subscription_created_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle subscription created event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            subscription_id = event_data.get("subscription_id")
            data_point_id = event_data.get("data_point_id")
            subscription_config = event_data.get("subscription_config")
            
            # Validate required fields
            if not subscription_id:
                self.logger.warning("Received subscription created event without subscription_id")
                return
            
            if not data_point_id:
                self.logger.warning(f"Received subscription created event for subscription {subscription_id} without data_point_id")
                return
            
            if not subscription_config:
                self.logger.warning(f"Received subscription created event for subscription {subscription_id} without subscription_config")
                return
            
            self.logger.info(f"Subscription {subscription_id} created for data point {data_point_id}")
            
            # Store subscription data
            self._subscriptions[subscription_id] = {
                "data_point_id": data_point_id,
                "subscription_config": subscription_config,
                "created_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_subscriptions"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling subscription created event: {str(e)}")
    
    def _handle_subscription_deleted_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle subscription deleted event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            subscription_id = event_data.get("subscription_id")
            
            # Validate required fields
            if not subscription_id:
                self.logger.warning("Received subscription deleted event without subscription_id")
                return
            
            # Check if subscription exists
            if subscription_id not in self._subscriptions:
                self.logger.warning(f"Received subscription deleted event for non-existent subscription {subscription_id}")
                return
            
            self.logger.info(f"Subscription {subscription_id} deleted")
            
            # Remove subscription data
            del self._subscriptions[subscription_id]
            
            # Update metrics
            self._metrics["total_subscriptions"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
        except Exception as e:
            self.logger.error(f"Error handling subscription deleted event: {str(e)}")
    
    def _notify_subscribers(self, data_point_id: str, value: Any) -> None:
        """
        Notify subscribers of data point value change.
        
        Args:
            data_point_id: Data point ID
            value: New value
        """
        try:
            # Find subscriptions for this data point
            for subscription_id, subscription_data in self._subscriptions.items():
                if subscription_data["data_point_id"] == data_point_id:
                    # Get subscription config
                    subscription_config = subscription_data["subscription_config"]
                    
                    # Check if notification should be sent
                    should_notify = True
                    
                    # Apply filters if configured
                    if "filter" in subscription_config:
                        filter_type = subscription_config["filter"].get("type")
                        filter_value = subscription_config["filter"].get("value")
                        
                        if filter_type == "threshold":
                            # Threshold filter
                            operator = subscription_config["filter"].get("operator", "gt")
                            
                            if operator == "gt" and not (value > filter_value):
                                should_notify = False
                            elif operator == "lt" and not (value < filter_value):
                                should_notify = False
                            elif operator == "eq" and not (value == filter_value):
                                should_notify = False
                            elif operator == "ne" and not (value != filter_value):
                                should_notify = False
                            elif operator == "ge" and not (value >= filter_value):
                                should_notify = False
                            elif operator == "le" and not (value <= filter_value):
                                should_notify = False
                        
                        elif filter_type == "change":
                            # Change filter
                            # Not implemented in this example
                            pass
                    
                    # Send notification if should notify
                    if should_notify:
                        # Get notification target
                        target = subscription_config.get("target", {})
                        target_type = target.get("type")
                        
                        if target_type == "event_bus":
                            # Send notification to event bus
                            topic = target.get("topic", "industrial_protocols.notification")
                            
                            self.event_bus.publish(
                                topic=topic,
                                data={
                                    "subscription_id": subscription_id,
                                    "data_point_id": data_point_id,
                                    "value": value,
                                    "timestamp": self.data_access.get_current_timestamp()
                                }
                            )
                        
                        elif target_type == "webhook":
                            # Send notification to webhook
                            # Not implemented in this example
                            pass
                        
                        elif target_type == "mcp":
                            # Send notification via MCP
                            context_type = target.get("context_type", "industrial_protocols.notification")
                            
                            self.mcp_bridge.send_context(
                                context_type=context_type,
                                context_data={
                                    "subscription_id": subscription_id,
                                    "data_point_id": data_point_id,
                                    "value": value,
                                    "timestamp": self.data_access.get_current_timestamp()
                                }
                            )
                        
                        elif target_type == "a2a":
                            # Send notification via A2A
                            capability_type = target.get("capability_type", "notification")
                            
                            self.a2a_bridge.send_capability(
                                capability_type=capability_type,
                                capability_data={
                                    "subscription_id": subscription_id,
                                    "data_point_id": data_point_id,
                                    "value": value,
                                    "timestamp": self.data_access.get_current_timestamp()
                                }
                            )
        except Exception as e:
            self.logger.error(f"Error notifying subscribers for data point {data_point_id}: {str(e)}")
    
    def connect_device(self, protocol_type: str, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connect to a device.
        
        Args:
            protocol_type: Protocol type
            device_config: Device configuration
        
        Returns:
            Connected device data
        """
        try:
            # Check if protocol adapter exists
            if protocol_type not in self._protocol_adapters:
                # In a real implementation, this would check if the protocol adapter is registered
                # For now, we'll just create a placeholder adapter
                self._protocol_adapters[protocol_type] = {
                    "type": protocol_type,
                    "name": f"{protocol_type} Adapter",
                    "version": "1.0.0"
                }
            
            # Generate device ID
            device_id = f"device-{self.data_access.generate_id()}"
            
            # In a real implementation, this would connect to the device using the protocol adapter
            # For now, we'll just simulate it
            
            # Publish device connected event
            self.event_bus.publish(
                topic="industrial_protocols.device.device_connected",
                data={
                    "device_id": device_id,
                    "protocol_type": protocol_type,
                    "device_config": device_config
                }
            )
            
            # Store device connection data
            self._device_connections[device_id] = {
                "protocol_type": protocol_type,
                "device_config": device_config,
                "status": "connected",
                "connected_at": self.data_access.get_current_timestamp(),
                "disconnected_at": None
            }
            
            # Update metrics
            self._metrics["total_device_connections"] += 1
            self._metrics["total_active_connections"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Connected to device {device_id} using protocol {protocol_type}")
            
            return {
                "device_id": device_id,
                "protocol_type": protocol_type,
                "device_config": device_config,
                "status": "connected"
            }
        except Exception as e:
            self.logger.error(f"Error connecting to device: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def disconnect_device(self, device_id: str) -> Dict[str, Any]:
        """
        Disconnect from a device.
        
        Args:
            device_id: Device ID
        
        Returns:
            Disconnection result
        """
        try:
            # Check if device exists
            if device_id not in self._device_connections:
                raise ValueError(f"Device {device_id} not found")
            
            # In a real implementation, this would disconnect from the device using the protocol adapter
            # For now, we'll just simulate it
            
            # Publish device disconnected event
            self.event_bus.publish(
                topic="industrial_protocols.device.device_disconnected",
                data={
                    "device_id": device_id
                }
            )
            
            # Update device connection data
            self._device_connections[device_id]["status"] = "disconnected"
            self._device_connections[device_id]["disconnected_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["total_active_connections"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Disconnected from device {device_id}")
            
            return {
                "device_id": device_id,
                "status": "disconnected"
            }
        except Exception as e:
            self.logger.error(f"Error disconnecting from device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_device(self, device_id: str) -> Dict[str, Any]:
        """
        Get a device.
        
        Args:
            device_id: Device ID
        
        Returns:
            Device data
        """
        try:
            # Check if device exists
            if device_id not in self._device_connections:
                raise ValueError(f"Device {device_id} not found")
            
            # Get device data
            device_data = self._device_connections[device_id]
            
            return {
                "device_id": device_id,
                "protocol_type": device_data["protocol_type"],
                "device_config": device_data["device_config"],
                "status": device_data["status"],
                "connected_at": device_data["connected_at"],
                "disconnected_at": device_data["disconnected_at"]
            }
        except Exception as e:
            self.logger.error(f"Error getting device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_devices(self, protocol_type: str = None) -> List[Dict[str, Any]]:
        """
        List devices.
        
        Args:
            protocol_type: Optional protocol type filter
        
        Returns:
            List of device data
        """
        try:
            # Apply filters
            devices = []
            
            for device_id, device_data in self._device_connections.items():
                # Apply protocol filter if provided
                if protocol_type and device_data["protocol_type"] != protocol_type:
                    continue
                
                # Add device to results
                devices.append({
                    "device_id": device_id,
                    "protocol_type": device_data["protocol_type"],
                    "device_config": device_data["device_config"],
                    "status": device_data["status"],
                    "connected_at": device_data["connected_at"],
                    "disconnected_at": device_data["disconnected_at"]
                })
            
            return devices
        except Exception as e:
            self.logger.error(f"Error listing devices: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def create_data_point(self, device_id: str, data_point_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a data point.
        
        Args:
            device_id: Device ID
            data_point_config: Data point configuration
        
        Returns:
            Created data point data
        """
        try:
            # Check if device exists
            if device_id not in self._device_connections:
                raise ValueError(f"Device {device_id} not found")
            
            # Check if device is connected
            if self._device_connections[device_id]["status"] != "connected":
                raise ValueError(f"Device {device_id} is not connected")
            
            # Generate data point ID
            data_point_id = f"data-point-{self.data_access.generate_id()}"
            
            # In a real implementation, this would create the data point using the protocol adapter
            # For now, we'll just simulate it
            
            # Publish data point created event
            self.event_bus.publish(
                topic="industrial_protocols.data_point.data_point_created",
                data={
                    "data_point_id": data_point_id,
                    "device_id": device_id,
                    "data_point_config": data_point_config
                }
            )
            
            # Store data point data
            self._data_points[data_point_id] = {
                "device_id": device_id,
                "data_point_config": data_point_config,
                "current_value": None,
                "last_read_time": None,
                "last_write_time": None,
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_data_points"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Created data point {data_point_id} for device {device_id}")
            
            return {
                "data_point_id": data_point_id,
                "device_id": device_id,
                "data_point_config": data_point_config
            }
        except Exception as e:
            self.logger.error(f"Error creating data point for device {device_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def update_data_point(self, data_point_id: str, data_point_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a data point.
        
        Args:
            data_point_id: Data point ID
            data_point_config: Data point configuration
        
        Returns:
            Updated data point data
        """
        try:
            # Check if data point exists
            if data_point_id not in self._data_points:
                raise ValueError(f"Data point {data_point_id} not found")
            
            # Get device ID
            device_id = self._data_points[data_point_id]["device_id"]
            
            # Check if device is connected
            if self._device_connections[device_id]["status"] != "connected":
                raise ValueError(f"Device {device_id} is not connected")
            
            # In a real implementation, this would update the data point using the protocol adapter
            # For now, we'll just simulate it
            
            # Publish data point updated event
            self.event_bus.publish(
                topic="industrial_protocols.data_point.data_point_updated",
                data={
                    "data_point_id": data_point_id,
                    "data_point_config": data_point_config
                }
            )
            
            # Update data point data
            self._data_points[data_point_id]["data_point_config"] = data_point_config
            self._data_points[data_point_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Updated data point {data_point_id}")
            
            return {
                "data_point_id": data_point_id,
                "device_id": device_id,
                "data_point_config": data_point_config
            }
        except Exception as e:
            self.logger.error(f"Error updating data point {data_point_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def delete_data_point(self, data_point_id: str) -> Dict[str, Any]:
        """
        Delete a data point.
        
        Args:
            data_point_id: Data point ID
        
        Returns:
            Deletion result
        """
        try:
            # Check if data point exists
            if data_point_id not in self._data_points:
                raise ValueError(f"Data point {data_point_id} not found")
            
            # Get device ID
            device_id = self._data_points[data_point_id]["device_id"]
            
            # In a real implementation, this would delete the data point using the protocol adapter
            # For now, we'll just simulate it
            
            # Publish data point deleted event
            self.event_bus.publish(
                topic="industrial_protocols.data_point.data_point_deleted",
                data={
                    "data_point_id": data_point_id
                }
            )
            
            # Remove data point data
            del self._data_points[data_point_id]
            
            # Update metrics
            self._metrics["total_data_points"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Deleted data point {data_point_id}")
            
            return {
                "data_point_id": data_point_id,
                "device_id": device_id,
                "status": "deleted"
            }
        except Exception as e:
            self.logger.error(f"Error deleting data point {data_point_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def read_data_point(self, data_point_id: str) -> Dict[str, Any]:
        """
        Read a data point.
        
        Args:
            data_point_id: Data point ID
        
        Returns:
            Data point value
        """
        try:
            # Check if data point exists
            if data_point_id not in self._data_points:
                raise ValueError(f"Data point {data_point_id} not found")
            
            # Get device ID
            device_id = self._data_points[data_point_id]["device_id"]
            
            # Check if device is connected
            if self._device_connections[device_id]["status"] != "connected":
                raise ValueError(f"Device {device_id} is not connected")
            
            # In a real implementation, this would read the data point using the protocol adapter
            # For now, we'll just simulate it
            
            # Generate a simulated value
            # In a real implementation, this would be the actual value read from the device
            value = self._generate_simulated_value(data_point_id)
            
            # Publish data point value changed event
            self.event_bus.publish(
                topic="industrial_protocols.data_point.data_point_value_changed",
                data={
                    "data_point_id": data_point_id,
                    "value": value,
                    "source": "read"
                }
            )
            
            # Update data point data
            self._data_points[data_point_id]["current_value"] = value
            self._data_points[data_point_id]["last_read_time"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["total_data_reads"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Read data point {data_point_id} with value {value}")
            
            return {
                "data_point_id": data_point_id,
                "device_id": device_id,
                "value": value,
                "timestamp": self.data_access.get_current_timestamp()
            }
        except Exception as e:
            self.logger.error(f"Error reading data point {data_point_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def write_data_point(self, data_point_id: str, value: Any) -> Dict[str, Any]:
        """
        Write a data point.
        
        Args:
            data_point_id: Data point ID
            value: Value to write
        
        Returns:
            Write result
        """
        try:
            # Check if data point exists
            if data_point_id not in self._data_points:
                raise ValueError(f"Data point {data_point_id} not found")
            
            # Get device ID
            device_id = self._data_points[data_point_id]["device_id"]
            
            # Check if device is connected
            if self._device_connections[device_id]["status"] != "connected":
                raise ValueError(f"Device {device_id} is not connected")
            
            # Check if data point is writable
            data_point_config = self._data_points[data_point_id]["data_point_config"]
            if not data_point_config.get("writable", True):
                raise ValueError(f"Data point {data_point_id} is not writable")
            
            # In a real implementation, this would write the data point using the protocol adapter
            # For now, we'll just simulate it
            
            # Publish data point value changed event
            self.event_bus.publish(
                topic="industrial_protocols.data_point.data_point_value_changed",
                data={
                    "data_point_id": data_point_id,
                    "value": value,
                    "source": "write"
                }
            )
            
            # Update data point data
            self._data_points[data_point_id]["current_value"] = value
            self._data_points[data_point_id]["last_write_time"] = self.data_access.get_current_timestamp()
            
            # Update metrics
            self._metrics["total_data_writes"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Wrote data point {data_point_id} with value {value}")
            
            return {
                "data_point_id": data_point_id,
                "device_id": device_id,
                "value": value,
                "timestamp": self.data_access.get_current_timestamp()
            }
        except Exception as e:
            self.logger.error(f"Error writing data point {data_point_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_data_point(self, data_point_id: str) -> Dict[str, Any]:
        """
        Get a data point.
        
        Args:
            data_point_id: Data point ID
        
        Returns:
            Data point data
        """
        try:
            # Check if data point exists
            if data_point_id not in self._data_points:
                raise ValueError(f"Data point {data_point_id} not found")
            
            # Get data point data
            data_point_data = self._data_points[data_point_id]
            
            return {
                "data_point_id": data_point_id,
                "device_id": data_point_data["device_id"],
                "data_point_config": data_point_data["data_point_config"],
                "current_value": data_point_data["current_value"],
                "last_read_time": data_point_data["last_read_time"],
                "last_write_time": data_point_data["last_write_time"],
                "created_at": data_point_data["created_at"],
                "updated_at": data_point_data["updated_at"]
            }
        except Exception as e:
            self.logger.error(f"Error getting data point {data_point_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_data_points(self, device_id: str = None) -> List[Dict[str, Any]]:
        """
        List data points.
        
        Args:
            device_id: Optional device ID filter
        
        Returns:
            List of data point data
        """
        try:
            # Apply filters
            data_points = []
            
            for data_point_id, data_point_data in self._data_points.items():
                # Apply device filter if provided
                if device_id and data_point_data["device_id"] != device_id:
                    continue
                
                # Add data point to results
                data_points.append({
                    "data_point_id": data_point_id,
                    "device_id": data_point_data["device_id"],
                    "data_point_config": data_point_data["data_point_config"],
                    "current_value": data_point_data["current_value"],
                    "last_read_time": data_point_data["last_read_time"],
                    "last_write_time": data_point_data["last_write_time"],
                    "created_at": data_point_data["created_at"],
                    "updated_at": data_point_data["updated_at"]
                })
            
            return data_points
        except Exception as e:
            self.logger.error(f"Error listing data points: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def create_subscription(self, data_point_id: str, subscription_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a subscription.
        
        Args:
            data_point_id: Data point ID
            subscription_config: Subscription configuration
        
        Returns:
            Created subscription data
        """
        try:
            # Check if data point exists
            if data_point_id not in self._data_points:
                raise ValueError(f"Data point {data_point_id} not found")
            
            # Generate subscription ID
            subscription_id = f"subscription-{self.data_access.generate_id()}"
            
            # In a real implementation, this would create the subscription using the protocol adapter
            # For now, we'll just simulate it
            
            # Publish subscription created event
            self.event_bus.publish(
                topic="industrial_protocols.subscription.subscription_created",
                data={
                    "subscription_id": subscription_id,
                    "data_point_id": data_point_id,
                    "subscription_config": subscription_config
                }
            )
            
            # Store subscription data
            self._subscriptions[subscription_id] = {
                "data_point_id": data_point_id,
                "subscription_config": subscription_config,
                "created_at": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["total_subscriptions"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Created subscription {subscription_id} for data point {data_point_id}")
            
            return {
                "subscription_id": subscription_id,
                "data_point_id": data_point_id,
                "subscription_config": subscription_config
            }
        except Exception as e:
            self.logger.error(f"Error creating subscription for data point {data_point_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def delete_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Delete a subscription.
        
        Args:
            subscription_id: Subscription ID
        
        Returns:
            Deletion result
        """
        try:
            # Check if subscription exists
            if subscription_id not in self._subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            # Get data point ID
            data_point_id = self._subscriptions[subscription_id]["data_point_id"]
            
            # In a real implementation, this would delete the subscription using the protocol adapter
            # For now, we'll just simulate it
            
            # Publish subscription deleted event
            self.event_bus.publish(
                topic="industrial_protocols.subscription.subscription_deleted",
                data={
                    "subscription_id": subscription_id
                }
            )
            
            # Remove subscription data
            del self._subscriptions[subscription_id]
            
            # Update metrics
            self._metrics["total_subscriptions"] -= 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Deleted subscription {subscription_id}")
            
            return {
                "subscription_id": subscription_id,
                "data_point_id": data_point_id,
                "status": "deleted"
            }
        except Exception as e:
            self.logger.error(f"Error deleting subscription {subscription_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get a subscription.
        
        Args:
            subscription_id: Subscription ID
        
        Returns:
            Subscription data
        """
        try:
            # Check if subscription exists
            if subscription_id not in self._subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            # Get subscription data
            subscription_data = self._subscriptions[subscription_id]
            
            return {
                "subscription_id": subscription_id,
                "data_point_id": subscription_data["data_point_id"],
                "subscription_config": subscription_data["subscription_config"],
                "created_at": subscription_data["created_at"]
            }
        except Exception as e:
            self.logger.error(f"Error getting subscription {subscription_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_subscriptions(self, data_point_id: str = None) -> List[Dict[str, Any]]:
        """
        List subscriptions.
        
        Args:
            data_point_id: Optional data point ID filter
        
        Returns:
            List of subscription data
        """
        try:
            # Apply filters
            subscriptions = []
            
            for subscription_id, subscription_data in self._subscriptions.items():
                # Apply data point filter if provided
                if data_point_id and subscription_data["data_point_id"] != data_point_id:
                    continue
                
                # Add subscription to results
                subscriptions.append({
                    "subscription_id": subscription_id,
                    "data_point_id": subscription_data["data_point_id"],
                    "subscription_config": subscription_data["subscription_config"],
                    "created_at": subscription_data["created_at"]
                })
            
            return subscriptions
        except Exception as e:
            self.logger.error(f"Error listing subscriptions: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _generate_simulated_value(self, data_point_id: str) -> Any:
        """
        Generate a simulated value for a data point.
        
        Args:
            data_point_id: Data point ID
        
        Returns:
            Simulated value
        """
        # Get data point config
        data_point_config = self._data_points[data_point_id]["data_point_config"]
        
        # Get data type
        data_type = data_point_config.get("data_type", "float")
        
        # Generate value based on data type
        if data_type == "boolean":
            # Generate random boolean
            import random
            return random.choice([True, False])
        
        elif data_type == "integer":
            # Generate random integer within range
            import random
            min_value = data_point_config.get("min_value", 0)
            max_value = data_point_config.get("max_value", 100)
            return random.randint(min_value, max_value)
        
        elif data_type == "float":
            # Generate random float within range
            import random
            min_value = data_point_config.get("min_value", 0.0)
            max_value = data_point_config.get("max_value", 100.0)
            return round(random.uniform(min_value, max_value), 2)
        
        elif data_type == "string":
            # Generate random string from list
            import random
            values = data_point_config.get("values", ["ON", "OFF", "ERROR"])
            return random.choice(values)
        
        else:
            # Default to None
            return None
    
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
            "total_device_connections": 0,
            "total_active_connections": 0,
            "total_data_points": 0,
            "total_data_reads": 0,
            "total_data_writes": 0,
            "total_subscriptions": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
