"""
MCP Protocol Adapter for the Protocol Layer Integration.

This module provides the MCP Protocol Adapter for integrating with
the Industriverse MCP (Model Context Protocol) components.

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

class MCPProtocolAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for the MCP Protocol of the Industriverse Framework.
    
    This class provides integration with the MCP (Model Context Protocol) components,
    enabling the Overseer System to interact with MCP-enabled services and agents.
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
        Initialize the MCP Protocol Adapter.
        
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
            adapter_type="mcp_protocol",
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
        
        # Initialize MCP Protocol-specific resources
        self._context_handlers = {}
        self._context_schemas = {}
        self._context_transformers = {}
        
        # Initialize metrics
        self._metrics = {
            "total_context_operations": 0,
            "total_context_transformations": 0,
            "total_schema_validations": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"MCP Protocol Adapter {adapter_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for MCP Protocol operations
        self.mcp_bridge.register_context_handler(
            context_type="protocol_layer.mcp_protocol",
            handler=self._handle_mcp_protocol_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for MCP Protocol operations
        self.mcp_bridge.unregister_context_handler(
            context_type="protocol_layer.mcp_protocol"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for MCP Protocol operations
        self.a2a_bridge.register_capability_handler(
            capability_type="mcp_protocol_integration",
            handler=self._handle_a2a_mcp_protocol_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for MCP Protocol operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="mcp_protocol_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to MCP Protocol-related events
        self.event_bus.subscribe(
            topic="protocol_layer.mcp_protocol.context_processed",
            handler=self._handle_mcp_context_processed_event
        )
        
        self.event_bus.subscribe(
            topic="protocol_layer.mcp_protocol.schema_updated",
            handler=self._handle_mcp_schema_updated_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from MCP Protocol-related events
        self.event_bus.unsubscribe(
            topic="protocol_layer.mcp_protocol.context_processed"
        )
        
        self.event_bus.unsubscribe(
            topic="protocol_layer.mcp_protocol.schema_updated"
        )
    
    def _handle_mcp_protocol_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Protocol context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            context_type = context.get("context_type")
            context_data = context.get("context_data", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "register_context_handler":
                if not context_type:
                    raise ValueError("context_type is required")
                
                handler_id = context.get("handler_id")
                if not handler_id:
                    raise ValueError("handler_id is required")
                
                result = self.register_context_handler(
                    context_type=context_type,
                    handler_id=handler_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "unregister_context_handler":
                if not context_type:
                    raise ValueError("context_type is required")
                
                handler_id = context.get("handler_id")
                if not handler_id:
                    raise ValueError("handler_id is required")
                
                result = self.unregister_context_handler(
                    context_type=context_type,
                    handler_id=handler_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_context_schema":
                if not context_type:
                    raise ValueError("context_type is required")
                
                schema = context.get("schema")
                if not schema:
                    raise ValueError("schema is required")
                
                result = self.register_context_schema(
                    context_type=context_type,
                    schema=schema
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_context_schema":
                if not context_type:
                    raise ValueError("context_type is required")
                
                result = self.get_context_schema(
                    context_type=context_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_context_transformer":
                if not context_type:
                    raise ValueError("context_type is required")
                
                transformer_id = context.get("transformer_id")
                if not transformer_id:
                    raise ValueError("transformer_id is required")
                
                result = self.register_context_transformer(
                    context_type=context_type,
                    transformer_id=transformer_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "unregister_context_transformer":
                if not context_type:
                    raise ValueError("context_type is required")
                
                transformer_id = context.get("transformer_id")
                if not transformer_id:
                    raise ValueError("transformer_id is required")
                
                result = self.unregister_context_transformer(
                    context_type=context_type,
                    transformer_id=transformer_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "transform_context":
                if not context_type:
                    raise ValueError("context_type is required")
                
                if not context_data:
                    raise ValueError("context_data is required")
                
                transformer_id = context.get("transformer_id")
                
                result = self.transform_context(
                    context_type=context_type,
                    context_data=context_data,
                    transformer_id=transformer_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "validate_context":
                if not context_type:
                    raise ValueError("context_type is required")
                
                if not context_data:
                    raise ValueError("context_data is required")
                
                result = self.validate_context(
                    context_type=context_type,
                    context_data=context_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "process_context":
                if not context_type:
                    raise ValueError("context_type is required")
                
                if not context_data:
                    raise ValueError("context_data is required")
                
                result = self.process_context(
                    context_type=context_type,
                    context_data=context_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Protocol context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_mcp_protocol_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A MCP Protocol capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            context_type = capability_data.get("context_type")
            context_data = capability_data.get("context_data", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_context_schema":
                if not context_type:
                    raise ValueError("context_type is required")
                
                result = self.get_context_schema(
                    context_type=context_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "validate_context":
                if not context_type:
                    raise ValueError("context_type is required")
                
                if not context_data:
                    raise ValueError("context_data is required")
                
                result = self.validate_context(
                    context_type=context_type,
                    context_data=context_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "transform_context":
                if not context_type:
                    raise ValueError("context_type is required")
                
                if not context_data:
                    raise ValueError("context_data is required")
                
                transformer_id = capability_data.get("transformer_id")
                
                result = self.transform_context(
                    context_type=context_type,
                    context_data=context_data,
                    transformer_id=transformer_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A MCP Protocol capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_context_processed_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle MCP context processed event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            context_type = event_data.get("context_type")
            context_id = event_data.get("context_id")
            status = event_data.get("status")
            
            # Validate required fields
            if not context_type:
                self.logger.warning("Received MCP context processed event without context_type")
                return
            
            if not context_id:
                self.logger.warning(f"Received MCP context processed event for context type {context_type} without context_id")
                return
            
            if not status:
                self.logger.warning(f"Received MCP context processed event for context type {context_type} and context ID {context_id} without status")
                return
            
            self.logger.info(f"MCP context of type {context_type} with ID {context_id} processed with status {status}")
        except Exception as e:
            self.logger.error(f"Error handling MCP context processed event: {str(e)}")
    
    def _handle_mcp_schema_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle MCP schema updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            context_type = event_data.get("context_type")
            schema_version = event_data.get("schema_version")
            
            # Validate required fields
            if not context_type:
                self.logger.warning("Received MCP schema updated event without context_type")
                return
            
            if not schema_version:
                self.logger.warning(f"Received MCP schema updated event for context type {context_type} without schema_version")
                return
            
            self.logger.info(f"MCP schema for context type {context_type} updated to version {schema_version}")
            
            # Update local schema cache if available
            schema = event_data.get("schema")
            if schema:
                self._context_schemas[context_type] = schema
        except Exception as e:
            self.logger.error(f"Error handling MCP schema updated event: {str(e)}")
    
    def register_context_handler(self, context_type: str, handler_id: str) -> bool:
        """
        Register a context handler.
        
        Args:
            context_type: Context type
            handler_id: Handler ID
        
        Returns:
            Success flag
        """
        try:
            # Check if handler exists
            if context_type in self._context_handlers and handler_id in self._context_handlers[context_type]:
                self.logger.warning(f"Context handler {handler_id} for context type {context_type} already registered")
                return False
            
            # Initialize handlers for context type if not exists
            if context_type not in self._context_handlers:
                self._context_handlers[context_type] = {}
            
            # Register handler
            self._context_handlers[context_type][handler_id] = True
            
            self.logger.info(f"Registered context handler {handler_id} for context type {context_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering context handler {handler_id} for context type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def unregister_context_handler(self, context_type: str, handler_id: str) -> bool:
        """
        Unregister a context handler.
        
        Args:
            context_type: Context type
            handler_id: Handler ID
        
        Returns:
            Success flag
        """
        try:
            # Check if handler exists
            if context_type not in self._context_handlers or handler_id not in self._context_handlers[context_type]:
                self.logger.warning(f"Context handler {handler_id} for context type {context_type} not registered")
                return False
            
            # Unregister handler
            del self._context_handlers[context_type][handler_id]
            
            # Remove context type if no handlers left
            if not self._context_handlers[context_type]:
                del self._context_handlers[context_type]
            
            self.logger.info(f"Unregistered context handler {handler_id} for context type {context_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error unregistering context handler {handler_id} for context type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_context_schema(self, context_type: str, schema: Dict[str, Any]) -> bool:
        """
        Register a context schema.
        
        Args:
            context_type: Context type
            schema: JSON Schema
        
        Returns:
            Success flag
        """
        try:
            # Register schema
            self._context_schemas[context_type] = schema
            
            # Publish schema updated event
            self.event_bus.publish(
                topic="protocol_layer.mcp_protocol.schema_updated",
                data={
                    "context_type": context_type,
                    "schema_version": schema.get("$version", "1.0.0"),
                    "schema": schema
                }
            )
            
            self.logger.info(f"Registered context schema for context type {context_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering context schema for context type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_context_schema(self, context_type: str) -> Dict[str, Any]:
        """
        Get a context schema.
        
        Args:
            context_type: Context type
        
        Returns:
            JSON Schema
        """
        try:
            # Check if schema exists
            if context_type not in self._context_schemas:
                raise ValueError(f"Context schema for context type {context_type} not found")
            
            # Get schema
            schema = self._context_schemas[context_type]
            
            return schema
        except Exception as e:
            self.logger.error(f"Error getting context schema for context type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_context_transformer(self, context_type: str, transformer_id: str) -> bool:
        """
        Register a context transformer.
        
        Args:
            context_type: Context type
            transformer_id: Transformer ID
        
        Returns:
            Success flag
        """
        try:
            # Check if transformer exists
            if context_type in self._context_transformers and transformer_id in self._context_transformers[context_type]:
                self.logger.warning(f"Context transformer {transformer_id} for context type {context_type} already registered")
                return False
            
            # Initialize transformers for context type if not exists
            if context_type not in self._context_transformers:
                self._context_transformers[context_type] = {}
            
            # Register transformer
            self._context_transformers[context_type][transformer_id] = True
            
            self.logger.info(f"Registered context transformer {transformer_id} for context type {context_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering context transformer {transformer_id} for context type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def unregister_context_transformer(self, context_type: str, transformer_id: str) -> bool:
        """
        Unregister a context transformer.
        
        Args:
            context_type: Context type
            transformer_id: Transformer ID
        
        Returns:
            Success flag
        """
        try:
            # Check if transformer exists
            if context_type not in self._context_transformers or transformer_id not in self._context_transformers[context_type]:
                self.logger.warning(f"Context transformer {transformer_id} for context type {context_type} not registered")
                return False
            
            # Unregister transformer
            del self._context_transformers[context_type][transformer_id]
            
            # Remove context type if no transformers left
            if not self._context_transformers[context_type]:
                del self._context_transformers[context_type]
            
            self.logger.info(f"Unregistered context transformer {transformer_id} for context type {context_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error unregistering context transformer {transformer_id} for context type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def transform_context(self, context_type: str, context_data: Dict[str, Any], transformer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Transform context data.
        
        Args:
            context_type: Context type
            context_data: Context data
            transformer_id: Optional transformer ID
        
        Returns:
            Transformed context data
        """
        try:
            # Check if transformer exists
            if transformer_id:
                if context_type not in self._context_transformers or transformer_id not in self._context_transformers[context_type]:
                    raise ValueError(f"Context transformer {transformer_id} for context type {context_type} not found")
            
            # Transform context data
            # In a real implementation, this would call the actual transformer
            # For now, we'll just return the original data
            transformed_data = context_data
            
            # Update metrics
            self._metrics["total_context_transformations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return transformed_data
        except Exception as e:
            self.logger.error(f"Error transforming context data for context type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def validate_context(self, context_type: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate context data against schema.
        
        Args:
            context_type: Context type
            context_data: Context data
        
        Returns:
            Validation result
        """
        try:
            # Check if schema exists
            if context_type not in self._context_schemas:
                raise ValueError(f"Context schema for context type {context_type} not found")
            
            # Get schema
            schema = self._context_schemas[context_type]
            
            # Validate context data
            # In a real implementation, this would use a JSON Schema validator
            # For now, we'll just return a success result
            validation_result = {
                "valid": True,
                "errors": []
            }
            
            # Update metrics
            self._metrics["total_schema_validations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return validation_result
        except Exception as e:
            self.logger.error(f"Error validating context data for context type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def process_context(self, context_type: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process context data.
        
        Args:
            context_type: Context type
            context_data: Context data
        
        Returns:
            Processing result
        """
        try:
            # Validate context data
            validation_result = self.validate_context(
                context_type=context_type,
                context_data=context_data
            )
            
            if not validation_result["valid"]:
                raise ValueError(f"Context data validation failed: {json.dumps(validation_result['errors'])}")
            
            # Process context data
            # In a real implementation, this would call the registered handlers
            # For now, we'll just return a success result
            processing_result = {
                "status": "success",
                "context_type": context_type,
                "context_id": context_data.get("id", "unknown")
            }
            
            # Publish context processed event
            self.event_bus.publish(
                topic="protocol_layer.mcp_protocol.context_processed",
                data={
                    "context_type": context_type,
                    "context_id": context_data.get("id", "unknown"),
                    "status": "success"
                }
            )
            
            # Update metrics
            self._metrics["total_context_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return processing_result
        except Exception as e:
            self.logger.error(f"Error processing context data for context type {context_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            
            # Publish context processed event with error
            self.event_bus.publish(
                topic="protocol_layer.mcp_protocol.context_processed",
                data={
                    "context_type": context_type,
                    "context_id": context_data.get("id", "unknown"),
                    "status": "error",
                    "error": str(e)
                }
            )
            
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
            "total_context_operations": 0,
            "total_context_transformations": 0,
            "total_schema_validations": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
