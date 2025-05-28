"""
Protocol Bridge Adapter for the Protocol Layer Integration.

This module provides the Protocol Bridge Adapter for integrating with
the Industriverse Protocol Bridge components, enabling communication
between MCP and A2A protocols.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union, Callable

from src.integration.base_integration_adapter import BaseIntegrationAdapter
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class ProtocolBridgeAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for the Protocol Bridge of the Industriverse Framework.
    
    This class provides integration with the Protocol Bridge components,
    enabling bidirectional communication between MCP and A2A protocols.
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
        Initialize the Protocol Bridge Adapter.
        
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
        super().__init__(
            adapter_id=adapter_id,
            adapter_type="protocol_bridge",
            manager=manager,
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            config=config,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize Protocol Bridge-specific resources
        self._context_to_capability_mappings = {}
        self._capability_to_context_mappings = {}
        self._transformation_rules = {}
        
        # Initialize metrics
        self._metrics = {
            "total_mcp_to_a2a_transformations": 0,
            "total_a2a_to_mcp_transformations": 0,
            "total_mapping_operations": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Protocol Bridge Adapter {adapter_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Protocol Bridge operations
        self.mcp_bridge.register_context_handler(
            context_type="protocol_layer.protocol_bridge",
            handler=self._handle_mcp_protocol_bridge_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Protocol Bridge operations
        self.mcp_bridge.unregister_context_handler(
            context_type="protocol_layer.protocol_bridge"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Protocol Bridge operations
        self.a2a_bridge.register_capability_handler(
            capability_type="protocol_bridge_integration",
            handler=self._handle_a2a_protocol_bridge_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Protocol Bridge operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="protocol_bridge_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Protocol Bridge-related events
        self.event_bus.subscribe(
            topic="protocol_layer.protocol_bridge.transformation_completed",
            handler=self._handle_transformation_completed_event
        )
        
        self.event_bus.subscribe(
            topic="protocol_layer.protocol_bridge.mapping_updated",
            handler=self._handle_mapping_updated_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Protocol Bridge-related events
        self.event_bus.unsubscribe(
            topic="protocol_layer.protocol_bridge.transformation_completed"
        )
        
        self.event_bus.unsubscribe(
            topic="protocol_layer.protocol_bridge.mapping_updated"
        )
    
    def _handle_mcp_protocol_bridge_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Protocol Bridge context.
        
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
            if action == "register_context_to_capability_mapping":
                context_type = context.get("context_type")
                if not context_type:
                    raise ValueError("context_type is required")
                
                capability_type = context.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                mapping_rules = context.get("mapping_rules")
                if not mapping_rules:
                    raise ValueError("mapping_rules is required")
                
                result = self.register_context_to_capability_mapping(
                    context_type=context_type,
                    capability_type=capability_type,
                    mapping_rules=mapping_rules
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_capability_to_context_mapping":
                capability_type = context.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                context_type = context.get("context_type")
                if not context_type:
                    raise ValueError("context_type is required")
                
                mapping_rules = context.get("mapping_rules")
                if not mapping_rules:
                    raise ValueError("mapping_rules is required")
                
                result = self.register_capability_to_context_mapping(
                    capability_type=capability_type,
                    context_type=context_type,
                    mapping_rules=mapping_rules
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_context_to_capability_mapping":
                context_type = context.get("context_type")
                if not context_type:
                    raise ValueError("context_type is required")
                
                capability_type = context.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                result = self.get_context_to_capability_mapping(
                    context_type=context_type,
                    capability_type=capability_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_capability_to_context_mapping":
                capability_type = context.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                context_type = context.get("context_type")
                if not context_type:
                    raise ValueError("context_type is required")
                
                result = self.get_capability_to_context_mapping(
                    capability_type=capability_type,
                    context_type=context_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "transform_context_to_capability":
                context_type = context.get("context_type")
                if not context_type:
                    raise ValueError("context_type is required")
                
                capability_type = context.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                context_data = context.get("context_data")
                if not context_data:
                    raise ValueError("context_data is required")
                
                result = self.transform_context_to_capability(
                    context_type=context_type,
                    capability_type=capability_type,
                    context_data=context_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "transform_capability_to_context":
                capability_type = context.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                context_type = context.get("context_type")
                if not context_type:
                    raise ValueError("context_type is required")
                
                capability_data = context.get("capability_data")
                if not capability_data:
                    raise ValueError("capability_data is required")
                
                result = self.transform_capability_to_context(
                    capability_type=capability_type,
                    context_type=context_type,
                    capability_data=capability_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_transformation_rule":
                rule_id = context.get("rule_id")
                if not rule_id:
                    raise ValueError("rule_id is required")
                
                rule_type = context.get("rule_type")
                if not rule_type:
                    raise ValueError("rule_type is required")
                
                rule_config = context.get("rule_config")
                if not rule_config:
                    raise ValueError("rule_config is required")
                
                result = self.register_transformation_rule(
                    rule_id=rule_id,
                    rule_type=rule_type,
                    rule_config=rule_config
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_transformation_rule":
                rule_id = context.get("rule_id")
                if not rule_id:
                    raise ValueError("rule_id is required")
                
                result = self.get_transformation_rule(
                    rule_id=rule_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Protocol Bridge context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_protocol_bridge_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Protocol Bridge capability.
        
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
            if action == "get_context_to_capability_mapping":
                context_type = capability_data.get("context_type")
                if not context_type:
                    raise ValueError("context_type is required")
                
                capability_type = capability_data.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                result = self.get_context_to_capability_mapping(
                    context_type=context_type,
                    capability_type=capability_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_capability_to_context_mapping":
                capability_type = capability_data.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                context_type = capability_data.get("context_type")
                if not context_type:
                    raise ValueError("context_type is required")
                
                result = self.get_capability_to_context_mapping(
                    capability_type=capability_type,
                    context_type=context_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "transform_capability_to_context":
                capability_type = capability_data.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                context_type = capability_data.get("context_type")
                if not context_type:
                    raise ValueError("context_type is required")
                
                capability_data_to_transform = capability_data.get("capability_data")
                if not capability_data_to_transform:
                    raise ValueError("capability_data is required")
                
                result = self.transform_capability_to_context(
                    capability_type=capability_type,
                    context_type=context_type,
                    capability_data=capability_data_to_transform
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Protocol Bridge capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_transformation_completed_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle transformation completed event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            transformation_type = event_data.get("transformation_type")
            source_type = event_data.get("source_type")
            target_type = event_data.get("target_type")
            status = event_data.get("status")
            
            # Validate required fields
            if not transformation_type:
                self.logger.warning("Received transformation completed event without transformation_type")
                return
            
            if not source_type:
                self.logger.warning(f"Received transformation completed event for transformation type {transformation_type} without source_type")
                return
            
            if not target_type:
                self.logger.warning(f"Received transformation completed event for transformation type {transformation_type} without target_type")
                return
            
            if not status:
                self.logger.warning(f"Received transformation completed event for transformation type {transformation_type} without status")
                return
            
            self.logger.info(f"Transformation of type {transformation_type} from {source_type} to {target_type} completed with status {status}")
        except Exception as e:
            self.logger.error(f"Error handling transformation completed event: {str(e)}")
    
    def _handle_mapping_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle mapping updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            mapping_type = event_data.get("mapping_type")
            source_type = event_data.get("source_type")
            target_type = event_data.get("target_type")
            
            # Validate required fields
            if not mapping_type:
                self.logger.warning("Received mapping updated event without mapping_type")
                return
            
            if not source_type:
                self.logger.warning(f"Received mapping updated event for mapping type {mapping_type} without source_type")
                return
            
            if not target_type:
                self.logger.warning(f"Received mapping updated event for mapping type {mapping_type} without target_type")
                return
            
            self.logger.info(f"Mapping of type {mapping_type} from {source_type} to {target_type} updated")
            
            # Update local mapping cache if available
            mapping_rules = event_data.get("mapping_rules")
            if mapping_rules:
                if mapping_type == "context_to_capability":
                    if source_type not in self._context_to_capability_mappings:
                        self._context_to_capability_mappings[source_type] = {}
                    
                    self._context_to_capability_mappings[source_type][target_type] = mapping_rules
                
                elif mapping_type == "capability_to_context":
                    if source_type not in self._capability_to_context_mappings:
                        self._capability_to_context_mappings[source_type] = {}
                    
                    self._capability_to_context_mappings[source_type][target_type] = mapping_rules
        except Exception as e:
            self.logger.error(f"Error handling mapping updated event: {str(e)}")
    
    def register_context_to_capability_mapping(self, context_type: str, capability_type: str, mapping_rules: Dict[str, Any]) -> bool:
        """
        Register a context to capability mapping.
        
        Args:
            context_type: Context type
            capability_type: Capability type
            mapping_rules: Mapping rules
        
        Returns:
            Success flag
        """
        try:
            # Initialize mappings for context type if not exists
            if context_type not in self._context_to_capability_mappings:
                self._context_to_capability_mappings[context_type] = {}
            
            # Register mapping
            self._context_to_capability_mappings[context_type][capability_type] = mapping_rules
            
            # Publish mapping updated event
            self.event_bus.publish(
                topic="protocol_layer.protocol_bridge.mapping_updated",
                data={
                    "mapping_type": "context_to_capability",
                    "source_type": context_type,
                    "target_type": capability_type,
                    "mapping_rules": mapping_rules
                }
            )
            
            self.logger.info(f"Registered context to capability mapping from {context_type} to {capability_type}")
            
            # Update metrics
            self._metrics["total_mapping_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering context to capability mapping from {context_type} to {capability_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_capability_to_context_mapping(self, capability_type: str, context_type: str, mapping_rules: Dict[str, Any]) -> bool:
        """
        Register a capability to context mapping.
        
        Args:
            capability_type: Capability type
            context_type: Context type
            mapping_rules: Mapping rules
        
        Returns:
            Success flag
        """
        try:
            # Initialize mappings for capability type if not exists
            if capability_type not in self._capability_to_context_mappings:
                self._capability_to_context_mappings[capability_type] = {}
            
            # Register mapping
            self._capability_to_context_mappings[capability_type][context_type] = mapping_rules
            
            # Publish mapping updated event
            self.event_bus.publish(
                topic="protocol_layer.protocol_bridge.mapping_updated",
                data={
                    "mapping_type": "capability_to_context",
                    "source_type": capability_type,
                    "target_type": context_type,
                    "mapping_rules": mapping_rules
                }
            )
            
            self.logger.info(f"Registered capability to context mapping from {capability_type} to {context_type}")
            
            # Update metrics
            self._metrics["total_mapping_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering capability to context mapping from {capability_type} to {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_context_to_capability_mapping(self, context_type: str, capability_type: str) -> Dict[str, Any]:
        """
        Get a context to capability mapping.
        
        Args:
            context_type: Context type
            capability_type: Capability type
        
        Returns:
            Mapping rules
        """
        try:
            # Check if mapping exists
            if context_type not in self._context_to_capability_mappings or capability_type not in self._context_to_capability_mappings[context_type]:
                raise ValueError(f"Context to capability mapping from {context_type} to {capability_type} not found")
            
            # Get mapping
            mapping_rules = self._context_to_capability_mappings[context_type][capability_type]
            
            # Update metrics
            self._metrics["total_mapping_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return mapping_rules
        except Exception as e:
            self.logger.error(f"Error getting context to capability mapping from {context_type} to {capability_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_capability_to_context_mapping(self, capability_type: str, context_type: str) -> Dict[str, Any]:
        """
        Get a capability to context mapping.
        
        Args:
            capability_type: Capability type
            context_type: Context type
        
        Returns:
            Mapping rules
        """
        try:
            # Check if mapping exists
            if capability_type not in self._capability_to_context_mappings or context_type not in self._capability_to_context_mappings[capability_type]:
                raise ValueError(f"Capability to context mapping from {capability_type} to {context_type} not found")
            
            # Get mapping
            mapping_rules = self._capability_to_context_mappings[capability_type][context_type]
            
            # Update metrics
            self._metrics["total_mapping_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return mapping_rules
        except Exception as e:
            self.logger.error(f"Error getting capability to context mapping from {capability_type} to {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def transform_context_to_capability(self, context_type: str, capability_type: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform context data to capability data.
        
        Args:
            context_type: Context type
            capability_type: Capability type
            context_data: Context data
        
        Returns:
            Capability data
        """
        try:
            # Get mapping
            mapping_rules = self.get_context_to_capability_mapping(
                context_type=context_type,
                capability_type=capability_type
            )
            
            # Transform context data to capability data
            # In a real implementation, this would apply the mapping rules
            # For now, we'll just create a simple transformation
            capability_data = {
                "type": capability_type,
                "source": {
                    "type": context_type,
                    "id": context_data.get("id", "unknown")
                },
                "data": context_data.get("data", {})
            }
            
            # Apply industry-specific metadata if available
            if "industryTags" in mapping_rules:
                capability_data["industryTags"] = mapping_rules["industryTags"]
            
            # Apply priority if available
            if "priority" in mapping_rules:
                capability_data["priority"] = mapping_rules["priority"]
            
            # Apply workflow templates if available
            if "workflowTemplates" in mapping_rules:
                capability_data["workflowTemplates"] = mapping_rules["workflowTemplates"]
            
            # Publish transformation completed event
            self.event_bus.publish(
                topic="protocol_layer.protocol_bridge.transformation_completed",
                data={
                    "transformation_type": "context_to_capability",
                    "source_type": context_type,
                    "target_type": capability_type,
                    "status": "success"
                }
            )
            
            # Update metrics
            self._metrics["total_mcp_to_a2a_transformations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return capability_data
        except Exception as e:
            self.logger.error(f"Error transforming context data from {context_type} to capability data of type {capability_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            
            # Publish transformation completed event with error
            self.event_bus.publish(
                topic="protocol_layer.protocol_bridge.transformation_completed",
                data={
                    "transformation_type": "context_to_capability",
                    "source_type": context_type,
                    "target_type": capability_type,
                    "status": "error",
                    "error": str(e)
                }
            )
            
            raise
    
    def transform_capability_to_context(self, capability_type: str, context_type: str, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform capability data to context data.
        
        Args:
            capability_type: Capability type
            context_type: Context type
            capability_data: Capability data
        
        Returns:
            Context data
        """
        try:
            # Get mapping
            mapping_rules = self.get_capability_to_context_mapping(
                capability_type=capability_type,
                context_type=context_type
            )
            
            # Transform capability data to context data
            # In a real implementation, this would apply the mapping rules
            # For now, we'll just create a simple transformation
            context_data = {
                "type": context_type,
                "source": {
                    "type": capability_type,
                    "id": capability_data.get("id", "unknown")
                },
                "data": capability_data.get("data", {})
            }
            
            # Publish transformation completed event
            self.event_bus.publish(
                topic="protocol_layer.protocol_bridge.transformation_completed",
                data={
                    "transformation_type": "capability_to_context",
                    "source_type": capability_type,
                    "target_type": context_type,
                    "status": "success"
                }
            )
            
            # Update metrics
            self._metrics["total_a2a_to_mcp_transformations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return context_data
        except Exception as e:
            self.logger.error(f"Error transforming capability data from {capability_type} to context data of type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            
            # Publish transformation completed event with error
            self.event_bus.publish(
                topic="protocol_layer.protocol_bridge.transformation_completed",
                data={
                    "transformation_type": "capability_to_context",
                    "source_type": capability_type,
                    "target_type": context_type,
                    "status": "error",
                    "error": str(e)
                }
            )
            
            raise
    
    def register_transformation_rule(self, rule_id: str, rule_type: str, rule_config: Dict[str, Any]) -> bool:
        """
        Register a transformation rule.
        
        Args:
            rule_id: Rule ID
            rule_type: Rule type
            rule_config: Rule configuration
        
        Returns:
            Success flag
        """
        try:
            # Register rule
            self._transformation_rules[rule_id] = {
                "type": rule_type,
                "config": rule_config
            }
            
            self.logger.info(f"Registered transformation rule {rule_id} of type {rule_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering transformation rule {rule_id} of type {rule_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_transformation_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        Get a transformation rule.
        
        Args:
            rule_id: Rule ID
        
        Returns:
            Rule data
        """
        try:
            # Check if rule exists
            if rule_id not in self._transformation_rules:
                raise ValueError(f"Transformation rule {rule_id} not found")
            
            # Get rule
            rule = self._transformation_rules[rule_id]
            
            return rule
        except Exception as e:
            self.logger.error(f"Error getting transformation rule {rule_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the adapter metrics.
        
        Returns:
            Adapter metrics
        """
        return self._metrics
    
    def reset_metrics(self) -> Dict[str, Any]:
        """
        Reset the adapter metrics.
        
        Returns:
            Reset adapter metrics
        """
        self._metrics = {
            "total_mcp_to_a2a_transformations": 0,
            "total_a2a_to_mcp_transformations": 0,
            "total_mapping_operations": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
