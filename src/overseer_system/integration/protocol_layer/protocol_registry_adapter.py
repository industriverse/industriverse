"""
Protocol Registry Adapter for the Protocol Layer Integration.

This module provides the Protocol Registry Adapter for integrating with
the Industriverse Protocol Registry components, enabling protocol discovery
and management.

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

class ProtocolRegistryAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for the Protocol Registry of the Industriverse Framework.
    
    This class provides integration with the Protocol Registry components,
    enabling protocol discovery and management.
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
        Initialize the Protocol Registry Adapter.
        
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
            adapter_type="protocol_registry",
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
        
        # Initialize Protocol Registry-specific resources
        self._registered_protocols = {}
        self._protocol_versions = {}
        self._protocol_schemas = {}
        self._protocol_dependencies = {}
        
        # Initialize metrics
        self._metrics = {
            "total_protocol_registrations": 0,
            "total_protocol_lookups": 0,
            "total_schema_validations": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Protocol Registry Adapter {adapter_id} initialized")
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Protocol Registry operations
        self.mcp_bridge.register_context_handler(
            context_type="protocol_layer.protocol_registry",
            handler=self._handle_mcp_protocol_registry_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Protocol Registry operations
        self.mcp_bridge.unregister_context_handler(
            context_type="protocol_layer.protocol_registry"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Protocol Registry operations
        self.a2a_bridge.register_capability_handler(
            capability_type="protocol_registry_integration",
            handler=self._handle_a2a_protocol_registry_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Protocol Registry operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="protocol_registry_integration"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Protocol Registry-related events
        self.event_bus.subscribe(
            topic="protocol_layer.protocol_registry.protocol_registered",
            handler=self._handle_protocol_registered_event
        )
        
        self.event_bus.subscribe(
            topic="protocol_layer.protocol_registry.protocol_updated",
            handler=self._handle_protocol_updated_event
        )
        
        self.event_bus.subscribe(
            topic="protocol_layer.protocol_registry.schema_updated",
            handler=self._handle_protocol_schema_updated_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Protocol Registry-related events
        self.event_bus.unsubscribe(
            topic="protocol_layer.protocol_registry.protocol_registered"
        )
        
        self.event_bus.unsubscribe(
            topic="protocol_layer.protocol_registry.protocol_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="protocol_layer.protocol_registry.schema_updated"
        )
    
    def _handle_mcp_protocol_registry_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP Protocol Registry context.
        
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
            if action == "register_protocol":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                protocol_data = context.get("protocol_data")
                if not protocol_data:
                    raise ValueError("protocol_data is required")
                
                result = self.register_protocol(
                    protocol_id=protocol_id,
                    protocol_data=protocol_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_protocol":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                result = self.get_protocol(
                    protocol_id=protocol_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_protocols":
                filter_criteria = context.get("filter_criteria", {})
                
                result = self.list_protocols(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_protocol_version":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                version = context.get("version")
                if not version:
                    raise ValueError("version is required")
                
                version_data = context.get("version_data")
                if not version_data:
                    raise ValueError("version_data is required")
                
                result = self.register_protocol_version(
                    protocol_id=protocol_id,
                    version=version,
                    version_data=version_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_protocol_version":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                version = context.get("version")
                if not version:
                    raise ValueError("version is required")
                
                result = self.get_protocol_version(
                    protocol_id=protocol_id,
                    version=version
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_protocol_versions":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                result = self.list_protocol_versions(
                    protocol_id=protocol_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_protocol_schema":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                version = context.get("version")
                if not version:
                    raise ValueError("version is required")
                
                schema = context.get("schema")
                if not schema:
                    raise ValueError("schema is required")
                
                result = self.register_protocol_schema(
                    protocol_id=protocol_id,
                    version=version,
                    schema=schema
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_protocol_schema":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                version = context.get("version")
                if not version:
                    raise ValueError("version is required")
                
                result = self.get_protocol_schema(
                    protocol_id=protocol_id,
                    version=version
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "register_protocol_dependency":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                dependency_id = context.get("dependency_id")
                if not dependency_id:
                    raise ValueError("dependency_id is required")
                
                dependency_data = context.get("dependency_data", {})
                
                result = self.register_protocol_dependency(
                    protocol_id=protocol_id,
                    dependency_id=dependency_id,
                    dependency_data=dependency_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_protocol_dependencies":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                result = self.get_protocol_dependencies(
                    protocol_id=protocol_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "validate_protocol_data":
                protocol_id = context.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                version = context.get("version")
                if not version:
                    raise ValueError("version is required")
                
                data = context.get("data")
                if not data:
                    raise ValueError("data is required")
                
                result = self.validate_protocol_data(
                    protocol_id=protocol_id,
                    version=version,
                    data=data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP Protocol Registry context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_protocol_registry_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A Protocol Registry capability.
        
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
            if action == "get_protocol":
                protocol_id = capability_data.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                result = self.get_protocol(
                    protocol_id=protocol_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_protocols":
                filter_criteria = capability_data.get("filter_criteria", {})
                
                result = self.list_protocols(
                    filter_criteria=filter_criteria
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_protocol_version":
                protocol_id = capability_data.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                version = capability_data.get("version")
                if not version:
                    raise ValueError("version is required")
                
                result = self.get_protocol_version(
                    protocol_id=protocol_id,
                    version=version
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "list_protocol_versions":
                protocol_id = capability_data.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                result = self.list_protocol_versions(
                    protocol_id=protocol_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_protocol_schema":
                protocol_id = capability_data.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                version = capability_data.get("version")
                if not version:
                    raise ValueError("version is required")
                
                result = self.get_protocol_schema(
                    protocol_id=protocol_id,
                    version=version
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "get_protocol_dependencies":
                protocol_id = capability_data.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                result = self.get_protocol_dependencies(
                    protocol_id=protocol_id
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            elif action == "validate_protocol_data":
                protocol_id = capability_data.get("protocol_id")
                if not protocol_id:
                    raise ValueError("protocol_id is required")
                
                version = capability_data.get("version")
                if not version:
                    raise ValueError("version is required")
                
                data = capability_data.get("data")
                if not data:
                    raise ValueError("data is required")
                
                result = self.validate_protocol_data(
                    protocol_id=protocol_id,
                    version=version,
                    data=data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A Protocol Registry capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_protocol_registered_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle protocol registered event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            protocol_id = event_data.get("protocol_id")
            
            # Validate required fields
            if not protocol_id:
                self.logger.warning("Received protocol registered event without protocol_id")
                return
            
            self.logger.info(f"Protocol {protocol_id} registered")
            
            # Update local protocol cache if available
            protocol_data = event_data.get("protocol_data")
            if protocol_data:
                self._registered_protocols[protocol_id] = protocol_data
        except Exception as e:
            self.logger.error(f"Error handling protocol registered event: {str(e)}")
    
    def _handle_protocol_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle protocol updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            protocol_id = event_data.get("protocol_id")
            version = event_data.get("version")
            
            # Validate required fields
            if not protocol_id:
                self.logger.warning("Received protocol updated event without protocol_id")
                return
            
            if not version:
                self.logger.warning(f"Received protocol updated event for protocol {protocol_id} without version")
                return
            
            self.logger.info(f"Protocol {protocol_id} version {version} updated")
            
            # Update local protocol version cache if available
            version_data = event_data.get("version_data")
            if version_data:
                if protocol_id not in self._protocol_versions:
                    self._protocol_versions[protocol_id] = {}
                
                self._protocol_versions[protocol_id][version] = version_data
        except Exception as e:
            self.logger.error(f"Error handling protocol updated event: {str(e)}")
    
    def _handle_protocol_schema_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle protocol schema updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            protocol_id = event_data.get("protocol_id")
            version = event_data.get("version")
            
            # Validate required fields
            if not protocol_id:
                self.logger.warning("Received protocol schema updated event without protocol_id")
                return
            
            if not version:
                self.logger.warning(f"Received protocol schema updated event for protocol {protocol_id} without version")
                return
            
            self.logger.info(f"Protocol {protocol_id} version {version} schema updated")
            
            # Update local protocol schema cache if available
            schema = event_data.get("schema")
            if schema:
                if protocol_id not in self._protocol_schemas:
                    self._protocol_schemas[protocol_id] = {}
                
                self._protocol_schemas[protocol_id][version] = schema
        except Exception as e:
            self.logger.error(f"Error handling protocol schema updated event: {str(e)}")
    
    def register_protocol(self, protocol_id: str, protocol_data: Dict[str, Any]) -> bool:
        """
        Register a protocol.
        
        Args:
            protocol_id: Protocol ID
            protocol_data: Protocol data
        
        Returns:
            Success flag
        """
        try:
            # Validate protocol data
            # In a real implementation, this would validate against a schema
            # For now, we'll just check for required fields
            if "name" not in protocol_data:
                raise ValueError("Protocol data must have a name field")
            
            if "description" not in protocol_data:
                raise ValueError("Protocol data must have a description field")
            
            # Add schema versioning if not present
            if "schemaVersion" not in protocol_data:
                protocol_data["schemaVersion"] = "1.0.0"
            
            # Register protocol
            self._registered_protocols[protocol_id] = protocol_data
            
            # Initialize protocol versions if not exists
            if protocol_id not in self._protocol_versions:
                self._protocol_versions[protocol_id] = {}
            
            # Initialize protocol schemas if not exists
            if protocol_id not in self._protocol_schemas:
                self._protocol_schemas[protocol_id] = {}
            
            # Initialize protocol dependencies if not exists
            if protocol_id not in self._protocol_dependencies:
                self._protocol_dependencies[protocol_id] = {}
            
            # Publish protocol registered event
            self.event_bus.publish(
                topic="protocol_layer.protocol_registry.protocol_registered",
                data={
                    "protocol_id": protocol_id,
                    "protocol_data": protocol_data
                }
            )
            
            self.logger.info(f"Registered protocol {protocol_id}")
            
            # Update metrics
            self._metrics["total_protocol_registrations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering protocol {protocol_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get a protocol.
        
        Args:
            protocol_id: Protocol ID
        
        Returns:
            Protocol data
        """
        try:
            # Check if protocol exists
            if protocol_id not in self._registered_protocols:
                raise ValueError(f"Protocol {protocol_id} not found")
            
            # Get protocol
            protocol_data = self._registered_protocols[protocol_id]
            
            # Update metrics
            self._metrics["total_protocol_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return protocol_data
        except Exception as e:
            self.logger.error(f"Error getting protocol {protocol_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_protocols(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List protocols.
        
        Args:
            filter_criteria: Optional filter criteria
        
        Returns:
            List of protocol data
        """
        try:
            # Apply filters if provided
            if filter_criteria:
                # In a real implementation, this would apply the filter criteria
                # For now, we'll just return all protocols
                protocols = [
                    {
                        "id": protocol_id,
                        "data": protocol_data
                    }
                    for protocol_id, protocol_data in self._registered_protocols.items()
                ]
            else:
                protocols = [
                    {
                        "id": protocol_id,
                        "data": protocol_data
                    }
                    for protocol_id, protocol_data in self._registered_protocols.items()
                ]
            
            # Update metrics
            self._metrics["total_protocol_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return protocols
        except Exception as e:
            self.logger.error(f"Error listing protocols: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_protocol_version(self, protocol_id: str, version: str, version_data: Dict[str, Any]) -> bool:
        """
        Register a protocol version.
        
        Args:
            protocol_id: Protocol ID
            version: Version
            version_data: Version data
        
        Returns:
            Success flag
        """
        try:
            # Check if protocol exists
            if protocol_id not in self._registered_protocols:
                raise ValueError(f"Protocol {protocol_id} not found")
            
            # Validate version data
            # In a real implementation, this would validate against a schema
            # For now, we'll just check for required fields
            if "releaseDate" not in version_data:
                raise ValueError("Version data must have a releaseDate field")
            
            if "changes" not in version_data:
                raise ValueError("Version data must have a changes field")
            
            # Register version
            if protocol_id not in self._protocol_versions:
                self._protocol_versions[protocol_id] = {}
            
            self._protocol_versions[protocol_id][version] = version_data
            
            # Publish protocol updated event
            self.event_bus.publish(
                topic="protocol_layer.protocol_registry.protocol_updated",
                data={
                    "protocol_id": protocol_id,
                    "version": version,
                    "version_data": version_data
                }
            )
            
            self.logger.info(f"Registered protocol {protocol_id} version {version}")
            
            # Update metrics
            self._metrics["total_protocol_registrations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering protocol {protocol_id} version {version}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_protocol_version(self, protocol_id: str, version: str) -> Dict[str, Any]:
        """
        Get a protocol version.
        
        Args:
            protocol_id: Protocol ID
            version: Version
        
        Returns:
            Version data
        """
        try:
            # Check if protocol exists
            if protocol_id not in self._registered_protocols:
                raise ValueError(f"Protocol {protocol_id} not found")
            
            # Check if version exists
            if protocol_id not in self._protocol_versions or version not in self._protocol_versions[protocol_id]:
                raise ValueError(f"Protocol {protocol_id} version {version} not found")
            
            # Get version
            version_data = self._protocol_versions[protocol_id][version]
            
            # Update metrics
            self._metrics["total_protocol_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return version_data
        except Exception as e:
            self.logger.error(f"Error getting protocol {protocol_id} version {version}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_protocol_versions(self, protocol_id: str) -> List[Dict[str, Any]]:
        """
        List protocol versions.
        
        Args:
            protocol_id: Protocol ID
        
        Returns:
            List of version data
        """
        try:
            # Check if protocol exists
            if protocol_id not in self._registered_protocols:
                raise ValueError(f"Protocol {protocol_id} not found")
            
            # Get versions
            if protocol_id not in self._protocol_versions:
                return []
            
            versions = [
                {
                    "version": version,
                    "data": version_data
                }
                for version, version_data in self._protocol_versions[protocol_id].items()
            ]
            
            # Update metrics
            self._metrics["total_protocol_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return versions
        except Exception as e:
            self.logger.error(f"Error listing protocol {protocol_id} versions: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_protocol_schema(self, protocol_id: str, version: str, schema: Dict[str, Any]) -> bool:
        """
        Register a protocol schema.
        
        Args:
            protocol_id: Protocol ID
            version: Version
            schema: Schema
        
        Returns:
            Success flag
        """
        try:
            # Check if protocol exists
            if protocol_id not in self._registered_protocols:
                raise ValueError(f"Protocol {protocol_id} not found")
            
            # Check if version exists
            if protocol_id not in self._protocol_versions or version not in self._protocol_versions[protocol_id]:
                raise ValueError(f"Protocol {protocol_id} version {version} not found")
            
            # Register schema
            if protocol_id not in self._protocol_schemas:
                self._protocol_schemas[protocol_id] = {}
            
            self._protocol_schemas[protocol_id][version] = schema
            
            # Publish protocol schema updated event
            self.event_bus.publish(
                topic="protocol_layer.protocol_registry.schema_updated",
                data={
                    "protocol_id": protocol_id,
                    "version": version,
                    "schema": schema
                }
            )
            
            self.logger.info(f"Registered protocol {protocol_id} version {version} schema")
            
            # Update metrics
            self._metrics["total_protocol_registrations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering protocol {protocol_id} version {version} schema: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_protocol_schema(self, protocol_id: str, version: str) -> Dict[str, Any]:
        """
        Get a protocol schema.
        
        Args:
            protocol_id: Protocol ID
            version: Version
        
        Returns:
            Schema
        """
        try:
            # Check if protocol exists
            if protocol_id not in self._registered_protocols:
                raise ValueError(f"Protocol {protocol_id} not found")
            
            # Check if version exists
            if protocol_id not in self._protocol_versions or version not in self._protocol_versions[protocol_id]:
                raise ValueError(f"Protocol {protocol_id} version {version} not found")
            
            # Check if schema exists
            if protocol_id not in self._protocol_schemas or version not in self._protocol_schemas[protocol_id]:
                raise ValueError(f"Protocol {protocol_id} version {version} schema not found")
            
            # Get schema
            schema = self._protocol_schemas[protocol_id][version]
            
            # Update metrics
            self._metrics["total_protocol_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return schema
        except Exception as e:
            self.logger.error(f"Error getting protocol {protocol_id} version {version} schema: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_protocol_dependency(self, protocol_id: str, dependency_id: str, dependency_data: Dict[str, Any] = None) -> bool:
        """
        Register a protocol dependency.
        
        Args:
            protocol_id: Protocol ID
            dependency_id: Dependency protocol ID
            dependency_data: Optional dependency data
        
        Returns:
            Success flag
        """
        try:
            # Check if protocol exists
            if protocol_id not in self._registered_protocols:
                raise ValueError(f"Protocol {protocol_id} not found")
            
            # Check if dependency exists
            if dependency_id not in self._registered_protocols:
                raise ValueError(f"Dependency protocol {dependency_id} not found")
            
            # Initialize dependency data if not provided
            if dependency_data is None:
                dependency_data = {}
            
            # Register dependency
            if protocol_id not in self._protocol_dependencies:
                self._protocol_dependencies[protocol_id] = {}
            
            self._protocol_dependencies[protocol_id][dependency_id] = dependency_data
            
            self.logger.info(f"Registered protocol {protocol_id} dependency on {dependency_id}")
            
            # Update metrics
            self._metrics["total_protocol_registrations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return True
        except Exception as e:
            self.logger.error(f"Error registering protocol {protocol_id} dependency on {dependency_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_protocol_dependencies(self, protocol_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get protocol dependencies.
        
        Args:
            protocol_id: Protocol ID
        
        Returns:
            Dependencies
        """
        try:
            # Check if protocol exists
            if protocol_id not in self._registered_protocols:
                raise ValueError(f"Protocol {protocol_id} not found")
            
            # Get dependencies
            if protocol_id not in self._protocol_dependencies:
                return {}
            
            dependencies = self._protocol_dependencies[protocol_id]
            
            # Update metrics
            self._metrics["total_protocol_lookups"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return dependencies
        except Exception as e:
            self.logger.error(f"Error getting protocol {protocol_id} dependencies: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def validate_protocol_data(self, protocol_id: str, version: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate protocol data against schema.
        
        Args:
            protocol_id: Protocol ID
            version: Version
            data: Data to validate
        
        Returns:
            Validation result
        """
        try:
            # Check if protocol exists
            if protocol_id not in self._registered_protocols:
                raise ValueError(f"Protocol {protocol_id} not found")
            
            # Check if version exists
            if protocol_id not in self._protocol_versions or version not in self._protocol_versions[protocol_id]:
                raise ValueError(f"Protocol {protocol_id} version {version} not found")
            
            # Check if schema exists
            if protocol_id not in self._protocol_schemas or version not in self._protocol_schemas[protocol_id]:
                raise ValueError(f"Protocol {protocol_id} version {version} schema not found")
            
            # Get schema
            schema = self._protocol_schemas[protocol_id][version]
            
            # Validate data
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
            self.logger.error(f"Error validating protocol {protocol_id} version {version} data: {str(e)}")
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
            "total_protocol_registrations": 0,
            "total_protocol_lookups": 0,
            "total_schema_validations": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
