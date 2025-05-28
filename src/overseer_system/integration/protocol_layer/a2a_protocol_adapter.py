"""
A2A Protocol Adapter for the Protocol Layer Integration.

This module provides the A2A Protocol Adapter for integrating with
the Industriverse A2A (Agent to Agent) protocol components.

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

class A2AProtocolAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for the A2A Protocol of the Industriverse Framework.
    
    This class provides integration with the A2A (Agent to Agent) protocol components,
    enabling the Overseer System to interact with A2A-enabled services and agents.
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
        Initialize the A2A Protocol Adapter.
        
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
            adapter_type="a2a_protocol",
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
        
        # Initialize A2A Protocol-specific resources
        self._capability_handlers = {}
        self._capability_schemas = {}
        self._agent_cards = {}
        self._agent_capabilities = {}
        
        # Initialize metrics
        self._metrics = {
            "total_capability_operations": 0,
            "total_agent_card_operations": 0,
            "total_schema_validations": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"A2A Protocol Adapter {adapter_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for A2A Protocol operations
        self.mcp_bridge.register_context_handler(
            context_type="protocol_layer.a2a_protocol",
            handler=self._handle_mcp_a2a_protocol_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for A2A Protocol operations
        self.mcp_bridge.unregister_context_handler(
            context_type="protocol_layer.a2a_protocol"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for A2A Protocol operations
        self.a2a_bridge.register_capability_handler(
            capability_type="a2a_protocol_integration",
            handler=self._handle_a2a_protocol_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for A2A Protocol operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="a2a_protocol_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to A2A Protocol-related events
        self.event_bus.subscribe(
            topic="protocol_layer.a2a_protocol.capability_processed",
            handler=self._handle_a2a_capability_processed_event
        )
        
        self.event_bus.subscribe(
            topic="protocol_layer.a2a_protocol.schema_updated",
            handler=self._handle_a2a_schema_updated_event
        )
        
        self.event_bus.subscribe(
            topic="protocol_layer.a2a_protocol.agent_card_updated",
            handler=self._handle_a2a_agent_card_updated_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from A2A Protocol-related events
        self.event_bus.unsubscribe(
            topic="protocol_layer.a2a_protocol.capability_processed"
        )
        
        self.event_bus.unsubscribe(
            topic="protocol_layer.a2a_protocol.schema_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="protocol_layer.a2a_protocol.agent_card_updated"
        )
    
    def _handle_mcp_a2a_protocol_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP A2A Protocol context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            capability_type = context.get("capability_type")
            capability_data = context.get("capability_data", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "register_capability_handler":
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                handler_id = context.get("handler_id")
                if not handler_id:
                    raise ValueError("handler_id is required")
                
                result = self.register_capability_handler(
                    capability_type=capability_type,
                    handler_id=handler_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "unregister_capability_handler":
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                handler_id = context.get("handler_id")
                if not handler_id:
                    raise ValueError("handler_id is required")
                
                result = self.unregister_capability_handler(
                    capability_type=capability_type,
                    handler_id=handler_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_capability_schema":
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                schema = context.get("schema")
                if not schema:
                    raise ValueError("schema is required")
                
                result = self.register_capability_schema(
                    capability_type=capability_type,
                    schema=schema
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_capability_schema":
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                result = self.get_capability_schema(
                    capability_type=capability_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_agent_card":
                agent_id = context.get("agent_id")
                if not agent_id:
                    raise ValueError("agent_id is required")
                
                agent_card = context.get("agent_card")
                if not agent_card:
                    raise ValueError("agent_card is required")
                
                result = self.register_agent_card(
                    agent_id=agent_id,
                    agent_card=agent_card
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_agent_card":
                agent_id = context.get("agent_id")
                if not agent_id:
                    raise ValueError("agent_id is required")
                
                result = self.get_agent_card(
                    agent_id=agent_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_agent_capability":
                agent_id = context.get("agent_id")
                if not agent_id:
                    raise ValueError("agent_id is required")
                
                capability_type = context.get("capability_type")
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                capability_data = context.get("capability_data")
                if not capability_data:
                    raise ValueError("capability_data is required")
                
                result = self.register_agent_capability(
                    agent_id=agent_id,
                    capability_type=capability_type,
                    capability_data=capability_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_agent_capabilities":
                agent_id = context.get("agent_id")
                if not agent_id:
                    raise ValueError("agent_id is required")
                
                result = self.get_agent_capabilities(
                    agent_id=agent_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "validate_capability":
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                if not capability_data:
                    raise ValueError("capability_data is required")
                
                result = self.validate_capability(
                    capability_type=capability_type,
                    capability_data=capability_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "process_capability":
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                if not capability_data:
                    raise ValueError("capability_data is required")
                
                result = self.process_capability(
                    capability_type=capability_type,
                    capability_data=capability_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP A2A Protocol context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_protocol_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Protocol capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            capability_type = capability_data.get("capability_type")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get_capability_schema":
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                result = self.get_capability_schema(
                    capability_type=capability_type
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_agent_card":
                agent_id = capability_data.get("agent_id")
                if not agent_id:
                    raise ValueError("agent_id is required")
                
                result = self.get_agent_card(
                    agent_id=agent_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_agent_capabilities":
                agent_id = capability_data.get("agent_id")
                if not agent_id:
                    raise ValueError("agent_id is required")
                
                result = self.get_agent_capabilities(
                    agent_id=agent_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "validate_capability":
                if not capability_type:
                    raise ValueError("capability_type is required")
                
                capability_data_to_validate = capability_data.get("capability_data")
                if not capability_data_to_validate:
                    raise ValueError("capability_data is required")
                
                result = self.validate_capability(
                    capability_type=capability_type,
                    capability_data=capability_data_to_validate
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Protocol capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_capability_processed_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle A2A capability processed event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            capability_type = event_data.get("capability_type")
            capability_id = event_data.get("capability_id")
            status = event_data.get("status")
            
            # Validate required fields
            if not capability_type:
                self.logger.warning("Received A2A capability processed event without capability_type")
                return
            
            if not capability_id:
                self.logger.warning(f"Received A2A capability processed event for capability type {capability_type} without capability_id")
                return
            
            if not status:
                self.logger.warning(f"Received A2A capability processed event for capability type {capability_type} and capability ID {capability_id} without status")
                return
            
            self.logger.info(f"A2A capability of type {capability_type} with ID {capability_id} processed with status {status}")
        except Exception as e:
            self.logger.error(f"Error handling A2A capability processed event: {str(e)}")
    
    def _handle_a2a_schema_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle A2A schema updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            capability_type = event_data.get("capability_type")
            schema_version = event_data.get("schema_version")
            
            # Validate required fields
            if not capability_type:
                self.logger.warning("Received A2A schema updated event without capability_type")
                return
            
            if not schema_version:
                self.logger.warning(f"Received A2A schema updated event for capability type {capability_type} without schema_version")
                return
            
            self.logger.info(f"A2A schema for capability type {capability_type} updated to version {schema_version}")
            
            # Update local schema cache if available
            schema = event_data.get("schema")
            if schema:
                self._capability_schemas[capability_type] = schema
        except Exception as e:
            self.logger.error(f"Error handling A2A schema updated event: {str(e)}")
    
    def _handle_a2a_agent_card_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle A2A agent card updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            agent_id = event_data.get("agent_id")
            
            # Validate required fields
            if not agent_id:
                self.logger.warning("Received A2A agent card updated event without agent_id")
                return
            
            self.logger.info(f"A2A agent card for agent {agent_id} updated")
            
            # Update local agent card cache if available
            agent_card = event_data.get("agent_card")
            if agent_card:
                self._agent_cards[agent_id] = agent_card
        except Exception as e:
            self.logger.error(f"Error handling A2A agent card updated event: {str(e)}")
    
    def register_capability_handler(self, capability_type: str, handler_id: str) -> bool:
        """
        Register a capability handler.
        
        Args:
            capability_type: Capability type
            handler_id: Handler ID
        
        Returns:
            Success flag
        """
        try:
            # Check if handler exists
            if capability_type in self._capability_handlers and handler_id in self._capability_handlers[capability_type]:
                self.logger.warning(f"Capability handler {handler_id} for capability type {capability_type} already registered")
                return False
            
            # Initialize handlers for capability type if not exists
            if capability_type not in self._capability_handlers:
                self._capability_handlers[capability_type] = {}
            
            # Register handler
            self._capability_handlers[capability_type][handler_id] = True
            
            self.logger.info(f"Registered capability handler {handler_id} for capability type {capability_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering capability handler {handler_id} for capability type {capability_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def unregister_capability_handler(self, capability_type: str, handler_id: str) -> bool:
        """
        Unregister a capability handler.
        
        Args:
            capability_type: Capability type
            handler_id: Handler ID
        
        Returns:
            Success flag
        """
        try:
            # Check if handler exists
            if capability_type not in self._capability_handlers or handler_id not in self._capability_handlers[capability_type]:
                self.logger.warning(f"Capability handler {handler_id} for capability type {capability_type} not registered")
                return False
            
            # Unregister handler
            del self._capability_handlers[capability_type][handler_id]
            
            # Remove capability type if no handlers left
            if not self._capability_handlers[capability_type]:
                del self._capability_handlers[capability_type]
            
            self.logger.info(f"Unregistered capability handler {handler_id} for capability type {capability_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error unregistering capability handler {handler_id} for capability type {capability_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_capability_schema(self, capability_type: str, schema: Dict[str, Any]) -> bool:
        """
        Register a capability schema.
        
        Args:
            capability_type: Capability type
            schema: JSON Schema
        
        Returns:
            Success flag
        """
        try:
            # Register schema
            self._capability_schemas[capability_type] = schema
            
            # Publish schema updated event
            self.event_bus.publish(
                topic="protocol_layer.a2a_protocol.schema_updated",
                data={
                    "capability_type": capability_type,
                    "schema_version": schema.get("$version", "1.0.0"),
                    "schema": schema
                }
            )
            
            self.logger.info(f"Registered capability schema for capability type {capability_type}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering capability schema for capability type {capability_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_capability_schema(self, capability_type: str) -> Dict[str, Any]:
        """
        Get a capability schema.
        
        Args:
            capability_type: Capability type
        
        Returns:
            JSON Schema
        """
        try:
            # Check if schema exists
            if capability_type not in self._capability_schemas:
                raise ValueError(f"Capability schema for capability type {capability_type} not found")
            
            # Get schema
            schema = self._capability_schemas[capability_type]
            
            return schema
        except Exception as e:
            self.logger.error(f"Error getting capability schema for capability type {capability_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_agent_card(self, agent_id: str, agent_card: Dict[str, Any]) -> bool:
        """
        Register an agent card.
        
        Args:
            agent_id: Agent ID
            agent_card: Agent card data
        
        Returns:
            Success flag
        """
        try:
            # Validate agent card
            # In a real implementation, this would validate against a schema
            # For now, we'll just check for required fields
            if "name" not in agent_card:
                raise ValueError("Agent card must have a name field")
            
            if "description" not in agent_card:
                raise ValueError("Agent card must have a description field")
            
            # Add industry-specific metadata if not present
            if "industryTags" not in agent_card:
                agent_card["industryTags"] = []
            
            # Register agent card
            self._agent_cards[agent_id] = agent_card
            
            # Initialize agent capabilities if not exists
            if agent_id not in self._agent_capabilities:
                self._agent_capabilities[agent_id] = {}
            
            # Publish agent card updated event
            self.event_bus.publish(
                topic="protocol_layer.a2a_protocol.agent_card_updated",
                data={
                    "agent_id": agent_id,
                    "agent_card": agent_card
                }
            )
            
            self.logger.info(f"Registered agent card for agent {agent_id}")
            
            # Update metrics
            self._metrics["total_agent_card_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering agent card for agent {agent_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_agent_card(self, agent_id: str) -> Dict[str, Any]:
        """
        Get an agent card.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent card data
        """
        try:
            # Check if agent card exists
            if agent_id not in self._agent_cards:
                raise ValueError(f"Agent card for agent {agent_id} not found")
            
            # Get agent card
            agent_card = self._agent_cards[agent_id]
            
            # Update metrics
            self._metrics["total_agent_card_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return agent_card
        except Exception as e:
            self.logger.error(f"Error getting agent card for agent {agent_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_agent_capability(self, agent_id: str, capability_type: str, capability_data: Dict[str, Any]) -> bool:
        """
        Register an agent capability.
        
        Args:
            agent_id: Agent ID
            capability_type: Capability type
            capability_data: Capability data
        
        Returns:
            Success flag
        """
        try:
            # Check if agent exists
            if agent_id not in self._agent_cards:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Validate capability data
            validation_result = self.validate_capability(
                capability_type=capability_type,
                capability_data=capability_data
            )
            
            if not validation_result["valid"]:
                raise ValueError(f"Capability data validation failed: {json.dumps(validation_result['errors'])}")
            
            # Initialize agent capabilities if not exists
            if agent_id not in self._agent_capabilities:
                self._agent_capabilities[agent_id] = {}
            
            # Register capability
            self._agent_capabilities[agent_id][capability_type] = capability_data
            
            # Add workflow templates if not present
            if "workflowTemplates" not in capability_data:
                capability_data["workflowTemplates"] = []
            
            self.logger.info(f"Registered capability {capability_type} for agent {agent_id}")
            
            # Update metrics
            self._metrics["total_capability_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering capability {capability_type} for agent {agent_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_agent_capabilities(self, agent_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get agent capabilities.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent capabilities
        """
        try:
            # Check if agent exists
            if agent_id not in self._agent_cards:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Get agent capabilities
            if agent_id not in self._agent_capabilities:
                return {}
            
            capabilities = self._agent_capabilities[agent_id]
            
            # Update metrics
            self._metrics["total_capability_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return capabilities
        except Exception as e:
            self.logger.error(f"Error getting capabilities for agent {agent_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def validate_capability(self, capability_type: str, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate capability data against schema.
        
        Args:
            capability_type: Capability type
            capability_data: Capability data
        
        Returns:
            Validation result
        """
        try:
            # Check if schema exists
            if capability_type not in self._capability_schemas:
                raise ValueError(f"Capability schema for capability type {capability_type} not found")
            
            # Get schema
            schema = self._capability_schemas[capability_type]
            
            # Validate capability data
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
            self.logger.error(f"Error validating capability data for capability type {capability_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def process_capability(self, capability_type: str, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process capability data.
        
        Args:
            capability_type: Capability type
            capability_data: Capability data
        
        Returns:
            Processing result
        """
        try:
            # Validate capability data
            validation_result = self.validate_capability(
                capability_type=capability_type,
                capability_data=capability_data
            )
            
            if not validation_result["valid"]:
                raise ValueError(f"Capability data validation failed: {json.dumps(validation_result['errors'])}")
            
            # Process capability data
            # In a real implementation, this would call the registered handlers
            # For now, we'll just return a success result
            processing_result = {
                "status": "success",
                "capability_type": capability_type,
                "capability_id": capability_data.get("id", "unknown")
            }
            
            # Publish capability processed event
            self.event_bus.publish(
                topic="protocol_layer.a2a_protocol.capability_processed",
                data={
                    "capability_type": capability_type,
                    "capability_id": capability_data.get("id", "unknown"),
                    "status": "success"
                }
            )
            
            # Update metrics
            self._metrics["total_capability_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return processing_result
        except Exception as e:
            self.logger.error(f"Error processing capability data for capability type {capability_type}: {str(e)}")
            self._metrics["total_errors"] += 1
            
            # Publish capability processed event with error
            self.event_bus.publish(
                topic="protocol_layer.a2a_protocol.capability_processed",
                data={
                    "capability_type": capability_type,
                    "capability_id": capability_data.get("id", "unknown"),
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
            "total_capability_operations": 0,
            "total_agent_card_operations": 0,
            "total_schema_validations": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
