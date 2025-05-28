"""
Data Schema Adapter for the Overseer System.

This module provides the integration adapter for data schema components
of the Industriverse Data Layer, enabling seamless schema management
within the Overseer System.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Callable

from src.integration.base_integration_adapter import BaseIntegrationAdapter
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class DataSchemaAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for Data Schema components of the Industriverse Data Layer.
    
    This class provides integration with data schema components, enabling
    seamless schema management within the Overseer System.
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
        Initialize the Data Schema Adapter.
        
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
        
        # Initialize data schema specific resources
        self._schemas = {}
        self._schema_versions = {}
        self._schema_mappings = {}
        self._active_schema_operations = {}
        
        # Initialize metrics
        self._metrics = {
            "total_schemas": 0,
            "total_schema_versions": 0,
            "total_schema_mappings": 0,
            "total_schema_operations": 0,
            "total_schema_errors": 0,
            "active_schema_operations": 0,
            "last_schema_operation_timestamp": None
        }
        
        self.logger.info(f"Data Schema Adapter {adapter_id} initialized")
    
    def _get_supported_context_types(self) -> List[str]:
        """
        Get the MCP context types supported by this adapter.
        
        Returns:
            List of supported context types
        """
        return [
            "data_layer.schema",
            "data_layer.schema.definition",
            "data_layer.schema.version",
            "data_layer.schema.mapping",
            "data_layer.schema.operation"
        ]
    
    def _get_supported_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the A2A capabilities supported by this adapter.
        
        Returns:
            List of supported capabilities
        """
        return [
            {
                "type": "schema_management",
                "description": "Manage data schemas",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "schema_id": {
                        "type": "string",
                        "description": "ID of the schema"
                    },
                    "schema_definition": {
                        "type": "object",
                        "description": "Definition of the schema"
                    }
                }
            },
            {
                "type": "schema_version_management",
                "description": "Manage data schema versions",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "schema_id": {
                        "type": "string",
                        "description": "ID of the schema"
                    },
                    "version": {
                        "type": "string",
                        "description": "Version of the schema"
                    },
                    "schema_definition": {
                        "type": "object",
                        "description": "Definition of the schema version"
                    }
                }
            },
            {
                "type": "schema_mapping_management",
                "description": "Manage data schema mappings",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "mapping_id": {
                        "type": "string",
                        "description": "ID of the mapping"
                    },
                    "source_schema_id": {
                        "type": "string",
                        "description": "ID of the source schema"
                    },
                    "target_schema_id": {
                        "type": "string",
                        "description": "ID of the target schema"
                    },
                    "mapping_definition": {
                        "type": "object",
                        "description": "Definition of the mapping"
                    }
                }
            },
            {
                "type": "schema_validation",
                "description": "Validate data against a schema",
                "parameters": {
                    "schema_id": {
                        "type": "string",
                        "description": "ID of the schema"
                    },
                    "version": {
                        "type": "string",
                        "description": "Version of the schema"
                    },
                    "data": {
                        "type": "object",
                        "description": "Data to validate"
                    }
                }
            },
            {
                "type": "schema_transformation",
                "description": "Transform data from one schema to another",
                "parameters": {
                    "mapping_id": {
                        "type": "string",
                        "description": "ID of the mapping"
                    },
                    "data": {
                        "type": "object",
                        "description": "Data to transform"
                    }
                }
            }
        ]
    
    def _initialize_resources(self) -> None:
        """Initialize adapter-specific resources."""
        try:
            # Load schemas from configuration
            schemas_config = self.config.get("schemas", {})
            for schema_id, schema_config in schemas_config.items():
                self._create_schema(schema_id, schema_config)
            
            # Load schema versions from configuration
            schema_versions_config = self.config.get("schema_versions", {})
            for schema_id, versions in schema_versions_config.items():
                for version, version_config in versions.items():
                    self._create_schema_version(schema_id, version, version_config)
            
            # Load schema mappings from configuration
            schema_mappings_config = self.config.get("schema_mappings", {})
            for mapping_id, mapping_config in schema_mappings_config.items():
                self._create_schema_mapping(mapping_id, mapping_config)
            
            self.logger.info(f"Initialized resources for Data Schema Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error initializing resources for Data Schema Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _start_resources(self) -> None:
        """Start adapter-specific resources."""
        try:
            # Nothing to start for schemas
            self.logger.info(f"Started resources for Data Schema Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error starting resources for Data Schema Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _stop_resources(self) -> None:
        """Stop adapter-specific resources."""
        try:
            # Stop all active schema operations
            for operation_id in list(self._active_schema_operations.keys()):
                self._cancel_schema_operation(operation_id)
            
            self.logger.info(f"Stopped resources for Data Schema Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error stopping resources for Data Schema Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _release_resources(self) -> None:
        """Release adapter-specific resources."""
        try:
            # Clear all resources
            self._schemas = {}
            self._schema_versions = {}
            self._schema_mappings = {}
            self._active_schema_operations = {}
            
            self.logger.info(f"Released resources for Data Schema Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error releasing resources for Data Schema Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _check_resource_health(self) -> str:
        """
        Check the health of adapter-specific resources.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        try:
            # Check active schema operations
            unhealthy_operations = 0
            for operation_id, operation in self._active_schema_operations.items():
                if operation.get("status") == "error":
                    unhealthy_operations += 1
            
            # Determine overall health
            total_operations = len(self._active_schema_operations)
            
            if unhealthy_operations > 0:
                # At least one operation is unhealthy
                if unhealthy_operations / max(total_operations, 1) > 0.5:
                    # More than 50% of operations are unhealthy
                    return "unhealthy"
                else:
                    # Less than 50% of operations are unhealthy
                    return "degraded"
            else:
                # All operations are healthy
                return "healthy"
        except Exception as e:
            self.logger.error(f"Error checking resource health for Data Schema Adapter {self.adapter_id}: {str(e)}")
            return "unhealthy"
    
    def _apply_configuration(self) -> None:
        """Apply configuration changes."""
        try:
            # Apply schema configuration changes
            schemas_config = self.config.get("schemas", {})
            
            # Remove deleted schemas
            for schema_id in list(self._schemas.keys()):
                if schema_id not in schemas_config:
                    self._delete_schema(schema_id)
            
            # Add or update schemas
            for schema_id, schema_config in schemas_config.items():
                if schema_id in self._schemas:
                    self._update_schema(schema_id, schema_config)
                else:
                    self._create_schema(schema_id, schema_config)
            
            # Apply schema version configuration changes
            schema_versions_config = self.config.get("schema_versions", {})
            
            # Remove deleted schema versions
            for schema_id in list(self._schema_versions.keys()):
                if schema_id not in schema_versions_config:
                    # Remove all versions for this schema
                    for version in list(self._schema_versions[schema_id].keys()):
                        self._delete_schema_version(schema_id, version)
                else:
                    # Remove deleted versions for this schema
                    for version in list(self._schema_versions[schema_id].keys()):
                        if version not in schema_versions_config[schema_id]:
                            self._delete_schema_version(schema_id, version)
            
            # Add or update schema versions
            for schema_id, versions in schema_versions_config.items():
                for version, version_config in versions.items():
                    if schema_id in self._schema_versions and version in self._schema_versions[schema_id]:
                        self._update_schema_version(schema_id, version, version_config)
                    else:
                        self._create_schema_version(schema_id, version, version_config)
            
            # Apply schema mapping configuration changes
            schema_mappings_config = self.config.get("schema_mappings", {})
            
            # Remove deleted schema mappings
            for mapping_id in list(self._schema_mappings.keys()):
                if mapping_id not in schema_mappings_config:
                    self._delete_schema_mapping(mapping_id)
            
            # Add or update schema mappings
            for mapping_id, mapping_config in schema_mappings_config.items():
                if mapping_id in self._schema_mappings:
                    self._update_schema_mapping(mapping_id, mapping_config)
                else:
                    self._create_schema_mapping(mapping_id, mapping_config)
            
            self.logger.info(f"Applied configuration changes for Data Schema Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error applying configuration changes for Data Schema Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _get_status_data(self) -> Dict[str, Any]:
        """
        Get adapter-specific status data.
        
        Returns:
            Adapter-specific status data
        """
        return {
            "schemas": {
                schema_id: {
                    "name": schema.get("name"),
                    "type": schema.get("type"),
                    "version_count": len(self._schema_versions.get(schema_id, {}))
                }
                for schema_id, schema in self._schemas.items()
            },
            "schema_mappings": {
                mapping_id: {
                    "source_schema_id": mapping.get("source_schema_id"),
                    "target_schema_id": mapping.get("target_schema_id")
                }
                for mapping_id, mapping in self._schema_mappings.items()
            },
            "active_schema_operations": {
                operation_id: {
                    "operation_type": operation.get("operation_type"),
                    "status": operation.get("status"),
                    "start_time": operation.get("start_time")
                }
                for operation_id, operation in self._active_schema_operations.items()
            },
            "metrics": self._metrics
        }
    
    def _handle_custom_command(self, command: str, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle a custom command event.
        
        Args:
            command: Command to handle
            event: Command event data
        
        Returns:
            Optional result data
        """
        if command == "create_schema":
            schema_id = event.get("schema_id", str(uuid.uuid4()))
            schema_config = event.get("schema_config", {})
            self._create_schema(schema_id, schema_config)
            return {"schema_id": schema_id}
        
        elif command == "update_schema":
            schema_id = event.get("schema_id")
            schema_config = event.get("schema_config", {})
            if not schema_id:
                raise ValueError("schema_id is required")
            self._update_schema(schema_id, schema_config)
            return {"schema_id": schema_id}
        
        elif command == "delete_schema":
            schema_id = event.get("schema_id")
            if not schema_id:
                raise ValueError("schema_id is required")
            self._delete_schema(schema_id)
            return {"schema_id": schema_id}
        
        elif command == "list_schemas":
            return {
                "schemas": {
                    schema_id: {
                        "name": schema.get("name"),
                        "type": schema.get("type"),
                        "version_count": len(self._schema_versions.get(schema_id, {}))
                    }
                    for schema_id, schema in self._schemas.items()
                }
            }
        
        elif command == "create_schema_version":
            schema_id = event.get("schema_id")
            version = event.get("version", "1.0.0")
            version_config = event.get("version_config", {})
            if not schema_id:
                raise ValueError("schema_id is required")
            self._create_schema_version(schema_id, version, version_config)
            return {"schema_id": schema_id, "version": version}
        
        elif command == "update_schema_version":
            schema_id = event.get("schema_id")
            version = event.get("version")
            version_config = event.get("version_config", {})
            if not schema_id:
                raise ValueError("schema_id is required")
            if not version:
                raise ValueError("version is required")
            self._update_schema_version(schema_id, version, version_config)
            return {"schema_id": schema_id, "version": version}
        
        elif command == "delete_schema_version":
            schema_id = event.get("schema_id")
            version = event.get("version")
            if not schema_id:
                raise ValueError("schema_id is required")
            if not version:
                raise ValueError("version is required")
            self._delete_schema_version(schema_id, version)
            return {"schema_id": schema_id, "version": version}
        
        elif command == "list_schema_versions":
            schema_id = event.get("schema_id")
            if not schema_id:
                raise ValueError("schema_id is required")
            return {
                "schema_id": schema_id,
                "versions": {
                    version: {
                        "created_at": version_data.get("created_at"),
                        "updated_at": version_data.get("updated_at")
                    }
                    for version, version_data in self._schema_versions.get(schema_id, {}).items()
                }
            }
        
        elif command == "create_schema_mapping":
            mapping_id = event.get("mapping_id", str(uuid.uuid4()))
            mapping_config = event.get("mapping_config", {})
            self._create_schema_mapping(mapping_id, mapping_config)
            return {"mapping_id": mapping_id}
        
        elif command == "update_schema_mapping":
            mapping_id = event.get("mapping_id")
            mapping_config = event.get("mapping_config", {})
            if not mapping_id:
                raise ValueError("mapping_id is required")
            self._update_schema_mapping(mapping_id, mapping_config)
            return {"mapping_id": mapping_id}
        
        elif command == "delete_schema_mapping":
            mapping_id = event.get("mapping_id")
            if not mapping_id:
                raise ValueError("mapping_id is required")
            self._delete_schema_mapping(mapping_id)
            return {"mapping_id": mapping_id}
        
        elif command == "list_schema_mappings":
            return {
                "schema_mappings": {
                    mapping_id: {
                        "source_schema_id": mapping.get("source_schema_id"),
                        "target_schema_id": mapping.get("target_schema_id")
                    }
                    for mapping_id, mapping in self._schema_mappings.items()
                }
            }
        
        elif command == "validate_data":
            schema_id = event.get("schema_id")
            version = event.get("version")
            data = event.get("data")
            if not schema_id:
                raise ValueError("schema_id is required")
            if not version:
                raise ValueError("version is required")
            if data is None:
                raise ValueError("data is required")
            operation_id = self._validate_data(schema_id, version, data)
            return {"operation_id": operation_id, "schema_id": schema_id, "version": version}
        
        elif command == "transform_data":
            mapping_id = event.get("mapping_id")
            data = event.get("data")
            if not mapping_id:
                raise ValueError("mapping_id is required")
            if data is None:
                raise ValueError("data is required")
            operation_id = self._transform_data(mapping_id, data)
            return {"operation_id": operation_id, "mapping_id": mapping_id}
        
        elif command == "cancel_schema_operation":
            operation_id = event.get("operation_id")
            if not operation_id:
                raise ValueError("operation_id is required")
            self._cancel_schema_operation(operation_id)
            return {"operation_id": operation_id}
        
        elif command == "list_schema_operations":
            return {
                "active_schema_operations": {
                    operation_id: {
                        "operation_type": operation.get("operation_type"),
                        "status": operation.get("status"),
                        "start_time": operation.get("start_time")
                    }
                    for operation_id, operation in self._active_schema_operations.items()
                }
            }
        
        elif command == "get_metrics":
            return {"metrics": self._metrics}
        
        elif command == "reset_metrics":
            self._metrics = {
                "total_schemas": len(self._schemas),
                "total_schema_versions": sum(len(versions) for versions in self._schema_versions.values()),
                "total_schema_mappings": len(self._schema_mappings),
                "total_schema_operations": 0,
                "total_schema_errors": 0,
                "active_schema_operations": 0,
                "last_schema_operation_timestamp": None
            }
            return {"metrics": self._metrics}
        
        else:
            raise ValueError(f"Unsupported command: {command}")
    
    def _subscribe_to_additional_events(self) -> None:
        """Subscribe to additional events specific to this adapter."""
        try:
            # Subscribe to data schema events
            self.event_bus.subscribe(
                topic="data_layer.schema.event",
                group_id=f"{self.adapter_id}-schema-event-handler",
                callback=self._handle_schema_event
            )
            
            self.logger.info(f"Subscribed to additional events for Data Schema Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error subscribing to additional events for Data Schema Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _unsubscribe_from_additional_events(self) -> None:
        """Unsubscribe from additional events specific to this adapter."""
        try:
            # Unsubscribe from data schema events
            self.event_bus.unsubscribe(
                topic="data_layer.schema.event",
                group_id=f"{self.adapter_id}-schema-event-handler"
            )
            
            self.logger.info(f"Unsubscribed from additional events for Data Schema Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error unsubscribing from additional events for Data Schema Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _handle_schema_event(self, event: Dict[str, Any]) -> None:
        """
        Handle data schema events.
        
        Args:
            event: Event data
        """
        try:
            event_type = event.get("event_type")
            
            if event_type == "validation_complete":
                operation_id = event.get("operation_id")
                is_valid = event.get("is_valid", False)
                errors = event.get("errors", [])
                
                # Update operation status
                if operation_id in self._active_schema_operations:
                    operation = self._active_schema_operations[operation_id]
                    operation["status"] = "completed"
                    operation["is_valid"] = is_valid
                    operation["errors"] = errors
                    operation["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active operations
                    del self._active_schema_operations[operation_id]
                    self._metrics["active_schema_operations"] = len(self._active_schema_operations)
                
                # Update metrics
                self._metrics["total_schema_operations"] += 1
                self._metrics["last_schema_operation_timestamp"] = self.data_access.get_current_timestamp()
                
                self.logger.info(f"Validation operation {operation_id} completed: valid={is_valid}, errors={len(errors)}")
            
            elif event_type == "transformation_complete":
                operation_id = event.get("operation_id")
                transformed_data = event.get("transformed_data")
                
                # Update operation status
                if operation_id in self._active_schema_operations:
                    operation = self._active_schema_operations[operation_id]
                    operation["status"] = "completed"
                    operation["transformed_data"] = transformed_data
                    operation["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active operations
                    del self._active_schema_operations[operation_id]
                    self._metrics["active_schema_operations"] = len(self._active_schema_operations)
                
                # Update metrics
                self._metrics["total_schema_operations"] += 1
                self._metrics["last_schema_operation_timestamp"] = self.data_access.get_current_timestamp()
                
                self.logger.info(f"Transformation operation {operation_id} completed")
            
            elif event_type == "schema_error":
                operation_id = event.get("operation_id")
                error = event.get("error")
                
                # Update operation status
                if operation_id in self._active_schema_operations:
                    operation = self._active_schema_operations[operation_id]
                    operation["status"] = "error"
                    operation["error"] = error
                    operation["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active operations
                    del self._active_schema_operations[operation_id]
                    self._metrics["active_schema_operations"] = len(self._active_schema_operations)
                
                # Update metrics
                self._metrics["total_schema_operations"] += 1
                self._metrics["total_schema_errors"] += 1
                self._metrics["last_schema_operation_timestamp"] = self.data_access.get_current_timestamp()
                
                # Notify manager
                if hasattr(self.manager, "update_metrics"):
                    self.manager.update_metrics("error_count", 1)
                
                self.logger.error(f"Schema operation {operation_id} error: {error}")
        except Exception as e:
            self.logger.error(f"Error handling schema event: {str(e)}")
    
    def _create_schema(self, schema_id: str, schema_config: Dict[str, Any]) -> None:
        """
        Create a new schema.
        
        Args:
            schema_id: Schema ID
            schema_config: Schema configuration
        """
        try:
            # Validate schema configuration
            schema_name = schema_config.get("name")
            schema_type = schema_config.get("type")
            if not schema_name:
                raise ValueError("Schema name is required")
            if not schema_type:
                raise ValueError("Schema type is required")
            
            # Create schema
            self._schemas[schema_id] = {
                "id": schema_id,
                "name": schema_name,
                "type": schema_type,
                "config": schema_config,
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Initialize schema versions
            if schema_id not in self._schema_versions:
                self._schema_versions[schema_id] = {}
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.schema.{schema_id}",
                provider_name=f"Schema: {schema_name}",
                provider_type="schema",
                context_types=[
                    "data_layer.schema.definition",
                    f"data_layer.schema.definition.{schema_type}"
                ]
            )
            
            # Save to configuration
            self.config["schemas"] = self.config.get("schemas", {})
            self.config["schemas"][schema_id] = schema_config
            
            # Update metrics
            self._metrics["total_schemas"] = len(self._schemas)
            
            self.logger.info(f"Created schema {schema_id} of type {schema_type}")
        except Exception as e:
            self.logger.error(f"Error creating schema {schema_id}: {str(e)}")
            raise
    
    def _update_schema(self, schema_id: str, schema_config: Dict[str, Any]) -> None:
        """
        Update an existing schema.
        
        Args:
            schema_id: Schema ID
            schema_config: Schema configuration
        """
        try:
            # Check if schema exists
            if schema_id not in self._schemas:
                raise ValueError(f"Schema {schema_id} does not exist")
            
            # Validate schema configuration
            schema_name = schema_config.get("name")
            schema_type = schema_config.get("type")
            if not schema_name:
                raise ValueError("Schema name is required")
            if not schema_type:
                raise ValueError("Schema type is required")
            
            # Update schema
            self._schemas[schema_id]["name"] = schema_name
            self._schemas[schema_id]["type"] = schema_type
            self._schemas[schema_id]["config"] = schema_config
            self._schemas[schema_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update MCP registration if type changed
            if self._schemas[schema_id]["type"] != schema_type:
                # Unregister old context provider
                self.mcp_bridge.unregister_context_provider(
                    provider_id=f"{self.adapter_id}.schema.{schema_id}"
                )
                
                # Register new context provider
                self.mcp_bridge.register_context_provider(
                    provider_id=f"{self.adapter_id}.schema.{schema_id}",
                    provider_name=f"Schema: {schema_name}",
                    provider_type="schema",
                    context_types=[
                        "data_layer.schema.definition",
                        f"data_layer.schema.definition.{schema_type}"
                    ]
                )
            
            # Save to configuration
            self.config["schemas"] = self.config.get("schemas", {})
            self.config["schemas"][schema_id] = schema_config
            
            self.logger.info(f"Updated schema {schema_id} of type {schema_type}")
        except Exception as e:
            self.logger.error(f"Error updating schema {schema_id}: {str(e)}")
            raise
    
    def _delete_schema(self, schema_id: str) -> None:
        """
        Delete a schema.
        
        Args:
            schema_id: Schema ID
        """
        try:
            # Check if schema exists
            if schema_id not in self._schemas:
                raise ValueError(f"Schema {schema_id} does not exist")
            
            # Check if schema has versions
            if schema_id in self._schema_versions and self._schema_versions[schema_id]:
                raise ValueError(f"Schema {schema_id} has versions, delete them first")
            
            # Check if schema is used by any mapping
            for mapping_id, mapping in self._schema_mappings.items():
                if mapping.get("source_schema_id") == schema_id or mapping.get("target_schema_id") == schema_id:
                    raise ValueError(f"Schema {schema_id} is used by mapping {mapping_id}")
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.schema.{schema_id}"
            )
            
            # Delete schema
            del self._schemas[schema_id]
            
            # Delete schema versions
            if schema_id in self._schema_versions:
                del self._schema_versions[schema_id]
            
            # Remove from configuration
            if "schemas" in self.config and schema_id in self.config["schemas"]:
                del self.config["schemas"][schema_id]
            
            # Update metrics
            self._metrics["total_schemas"] = len(self._schemas)
            
            self.logger.info(f"Deleted schema {schema_id}")
        except Exception as e:
            self.logger.error(f"Error deleting schema {schema_id}: {str(e)}")
            raise
    
    def _create_schema_version(self, schema_id: str, version: str, version_config: Dict[str, Any]) -> None:
        """
        Create a new schema version.
        
        Args:
            schema_id: Schema ID
            version: Version string
            version_config: Version configuration
        """
        try:
            # Check if schema exists
            if schema_id not in self._schemas:
                raise ValueError(f"Schema {schema_id} does not exist")
            
            # Initialize schema versions
            if schema_id not in self._schema_versions:
                self._schema_versions[schema_id] = {}
            
            # Check if version already exists
            if version in self._schema_versions[schema_id]:
                raise ValueError(f"Version {version} already exists for schema {schema_id}")
            
            # Create schema version
            self._schema_versions[schema_id][version] = {
                "schema_id": schema_id,
                "version": version,
                "config": version_config,
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Register with MCP
            schema_name = self._schemas[schema_id]["name"]
            schema_type = self._schemas[schema_id]["type"]
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.schema.{schema_id}.version.{version}",
                provider_name=f"Schema Version: {schema_name} {version}",
                provider_type="schema_version",
                context_types=[
                    "data_layer.schema.version",
                    f"data_layer.schema.version.{schema_type}"
                ]
            )
            
            # Save to configuration
            self.config["schema_versions"] = self.config.get("schema_versions", {})
            if schema_id not in self.config["schema_versions"]:
                self.config["schema_versions"][schema_id] = {}
            self.config["schema_versions"][schema_id][version] = version_config
            
            # Update metrics
            self._metrics["total_schema_versions"] = sum(len(versions) for versions in self._schema_versions.values())
            
            self.logger.info(f"Created version {version} for schema {schema_id}")
        except Exception as e:
            self.logger.error(f"Error creating version {version} for schema {schema_id}: {str(e)}")
            raise
    
    def _update_schema_version(self, schema_id: str, version: str, version_config: Dict[str, Any]) -> None:
        """
        Update an existing schema version.
        
        Args:
            schema_id: Schema ID
            version: Version string
            version_config: Version configuration
        """
        try:
            # Check if schema exists
            if schema_id not in self._schemas:
                raise ValueError(f"Schema {schema_id} does not exist")
            
            # Check if schema version exists
            if schema_id not in self._schema_versions or version not in self._schema_versions[schema_id]:
                raise ValueError(f"Version {version} does not exist for schema {schema_id}")
            
            # Update schema version
            self._schema_versions[schema_id][version]["config"] = version_config
            self._schema_versions[schema_id][version]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Save to configuration
            self.config["schema_versions"] = self.config.get("schema_versions", {})
            if schema_id not in self.config["schema_versions"]:
                self.config["schema_versions"][schema_id] = {}
            self.config["schema_versions"][schema_id][version] = version_config
            
            self.logger.info(f"Updated version {version} for schema {schema_id}")
        except Exception as e:
            self.logger.error(f"Error updating version {version} for schema {schema_id}: {str(e)}")
            raise
    
    def _delete_schema_version(self, schema_id: str, version: str) -> None:
        """
        Delete a schema version.
        
        Args:
            schema_id: Schema ID
            version: Version string
        """
        try:
            # Check if schema exists
            if schema_id not in self._schemas:
                raise ValueError(f"Schema {schema_id} does not exist")
            
            # Check if schema version exists
            if schema_id not in self._schema_versions or version not in self._schema_versions[schema_id]:
                raise ValueError(f"Version {version} does not exist for schema {schema_id}")
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.schema.{schema_id}.version.{version}"
            )
            
            # Delete schema version
            del self._schema_versions[schema_id][version]
            
            # Remove from configuration
            if "schema_versions" in self.config and schema_id in self.config["schema_versions"] and version in self.config["schema_versions"][schema_id]:
                del self.config["schema_versions"][schema_id][version]
            
            # Update metrics
            self._metrics["total_schema_versions"] = sum(len(versions) for versions in self._schema_versions.values())
            
            self.logger.info(f"Deleted version {version} for schema {schema_id}")
        except Exception as e:
            self.logger.error(f"Error deleting version {version} for schema {schema_id}: {str(e)}")
            raise
    
    def _create_schema_mapping(self, mapping_id: str, mapping_config: Dict[str, Any]) -> None:
        """
        Create a new schema mapping.
        
        Args:
            mapping_id: Mapping ID
            mapping_config: Mapping configuration
        """
        try:
            # Validate mapping configuration
            source_schema_id = mapping_config.get("source_schema_id")
            target_schema_id = mapping_config.get("target_schema_id")
            if not source_schema_id:
                raise ValueError("Source schema ID is required")
            if not target_schema_id:
                raise ValueError("Target schema ID is required")
            
            # Check if schemas exist
            if source_schema_id not in self._schemas:
                raise ValueError(f"Source schema {source_schema_id} does not exist")
            if target_schema_id not in self._schemas:
                raise ValueError(f"Target schema {target_schema_id} does not exist")
            
            # Create schema mapping
            self._schema_mappings[mapping_id] = {
                "id": mapping_id,
                "source_schema_id": source_schema_id,
                "target_schema_id": target_schema_id,
                "config": mapping_config,
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Register with MCP
            source_schema_name = self._schemas[source_schema_id]["name"]
            target_schema_name = self._schemas[target_schema_id]["name"]
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.mapping.{mapping_id}",
                provider_name=f"Schema Mapping: {source_schema_name} to {target_schema_name}",
                provider_type="schema_mapping",
                context_types=[
                    "data_layer.schema.mapping"
                ]
            )
            
            # Save to configuration
            self.config["schema_mappings"] = self.config.get("schema_mappings", {})
            self.config["schema_mappings"][mapping_id] = mapping_config
            
            # Update metrics
            self._metrics["total_schema_mappings"] = len(self._schema_mappings)
            
            self.logger.info(f"Created schema mapping {mapping_id} from {source_schema_id} to {target_schema_id}")
        except Exception as e:
            self.logger.error(f"Error creating schema mapping {mapping_id}: {str(e)}")
            raise
    
    def _update_schema_mapping(self, mapping_id: str, mapping_config: Dict[str, Any]) -> None:
        """
        Update an existing schema mapping.
        
        Args:
            mapping_id: Mapping ID
            mapping_config: Mapping configuration
        """
        try:
            # Check if mapping exists
            if mapping_id not in self._schema_mappings:
                raise ValueError(f"Schema mapping {mapping_id} does not exist")
            
            # Validate mapping configuration
            source_schema_id = mapping_config.get("source_schema_id")
            target_schema_id = mapping_config.get("target_schema_id")
            if not source_schema_id:
                raise ValueError("Source schema ID is required")
            if not target_schema_id:
                raise ValueError("Target schema ID is required")
            
            # Check if schemas exist
            if source_schema_id not in self._schemas:
                raise ValueError(f"Source schema {source_schema_id} does not exist")
            if target_schema_id not in self._schemas:
                raise ValueError(f"Target schema {target_schema_id} does not exist")
            
            # Update schema mapping
            self._schema_mappings[mapping_id]["source_schema_id"] = source_schema_id
            self._schema_mappings[mapping_id]["target_schema_id"] = target_schema_id
            self._schema_mappings[mapping_id]["config"] = mapping_config
            self._schema_mappings[mapping_id]["updated_at"] = self.data_access.get_current_timestamp()
            
            # Update MCP registration if schemas changed
            if (self._schema_mappings[mapping_id]["source_schema_id"] != source_schema_id or
                self._schema_mappings[mapping_id]["target_schema_id"] != target_schema_id):
                # Unregister old context provider
                self.mcp_bridge.unregister_context_provider(
                    provider_id=f"{self.adapter_id}.mapping.{mapping_id}"
                )
                
                # Register new context provider
                source_schema_name = self._schemas[source_schema_id]["name"]
                target_schema_name = self._schemas[target_schema_id]["name"]
                self.mcp_bridge.register_context_provider(
                    provider_id=f"{self.adapter_id}.mapping.{mapping_id}",
                    provider_name=f"Schema Mapping: {source_schema_name} to {target_schema_name}",
                    provider_type="schema_mapping",
                    context_types=[
                        "data_layer.schema.mapping"
                    ]
                )
            
            # Save to configuration
            self.config["schema_mappings"] = self.config.get("schema_mappings", {})
            self.config["schema_mappings"][mapping_id] = mapping_config
            
            self.logger.info(f"Updated schema mapping {mapping_id} from {source_schema_id} to {target_schema_id}")
        except Exception as e:
            self.logger.error(f"Error updating schema mapping {mapping_id}: {str(e)}")
            raise
    
    def _delete_schema_mapping(self, mapping_id: str) -> None:
        """
        Delete a schema mapping.
        
        Args:
            mapping_id: Mapping ID
        """
        try:
            # Check if mapping exists
            if mapping_id not in self._schema_mappings:
                raise ValueError(f"Schema mapping {mapping_id} does not exist")
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.mapping.{mapping_id}"
            )
            
            # Delete schema mapping
            del self._schema_mappings[mapping_id]
            
            # Remove from configuration
            if "schema_mappings" in self.config and mapping_id in self.config["schema_mappings"]:
                del self.config["schema_mappings"][mapping_id]
            
            # Update metrics
            self._metrics["total_schema_mappings"] = len(self._schema_mappings)
            
            self.logger.info(f"Deleted schema mapping {mapping_id}")
        except Exception as e:
            self.logger.error(f"Error deleting schema mapping {mapping_id}: {str(e)}")
            raise
    
    def _validate_data(self, schema_id: str, version: str, data: Any) -> str:
        """
        Validate data against a schema version.
        
        Args:
            schema_id: Schema ID
            version: Version string
            data: Data to validate
        
        Returns:
            Operation ID
        """
        try:
            # Check if schema exists
            if schema_id not in self._schemas:
                raise ValueError(f"Schema {schema_id} does not exist")
            
            # Check if schema version exists
            if schema_id not in self._schema_versions or version not in self._schema_versions[schema_id]:
                raise ValueError(f"Version {version} does not exist for schema {schema_id}")
            
            # Create operation ID
            operation_id = str(uuid.uuid4())
            
            # Create validation operation
            self._active_schema_operations[operation_id] = {
                "id": operation_id,
                "operation_type": "validate",
                "schema_id": schema_id,
                "version": version,
                "status": "running",
                "start_time": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["active_schema_operations"] = len(self._active_schema_operations)
            
            # Register with MCP
            schema_name = self._schemas[schema_id]["name"]
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.operation.{operation_id}",
                provider_name=f"Schema Operation: Validate against {schema_name} {version}",
                provider_type="schema_operation",
                context_types=[
                    "data_layer.schema.operation",
                    "data_layer.schema.operation.validate"
                ]
            )
            
            # Publish operation start event
            self.event_bus.publish(
                topic="data_layer.schema.operation",
                key=operation_id,
                value={
                    "operation_id": operation_id,
                    "schema_id": schema_id,
                    "version": version,
                    "operation_type": "validate",
                    "event_type": "operation_start",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Start validation operation (simulated for now)
            # In a real implementation, this would start an actual validation process
            # For now, we'll simulate it with a simple event
            self.event_bus.publish(
                topic="data_layer.schema.event",
                key=operation_id,
                value={
                    "event_type": "validation_complete",
                    "operation_id": operation_id,
                    "is_valid": True,  # Simulated value
                    "errors": [],
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Started validation operation {operation_id} for schema {schema_id} version {version}")
            
            return operation_id
        except Exception as e:
            self.logger.error(f"Error validating data against schema {schema_id} version {version}: {str(e)}")
            raise
    
    def _transform_data(self, mapping_id: str, data: Any) -> str:
        """
        Transform data using a schema mapping.
        
        Args:
            mapping_id: Mapping ID
            data: Data to transform
        
        Returns:
            Operation ID
        """
        try:
            # Check if mapping exists
            if mapping_id not in self._schema_mappings:
                raise ValueError(f"Schema mapping {mapping_id} does not exist")
            
            # Get mapping
            mapping = self._schema_mappings[mapping_id]
            source_schema_id = mapping["source_schema_id"]
            target_schema_id = mapping["target_schema_id"]
            
            # Create operation ID
            operation_id = str(uuid.uuid4())
            
            # Create transformation operation
            self._active_schema_operations[operation_id] = {
                "id": operation_id,
                "operation_type": "transform",
                "mapping_id": mapping_id,
                "source_schema_id": source_schema_id,
                "target_schema_id": target_schema_id,
                "status": "running",
                "start_time": self.data_access.get_current_timestamp()
            }
            
            # Update metrics
            self._metrics["active_schema_operations"] = len(self._active_schema_operations)
            
            # Register with MCP
            source_schema_name = self._schemas[source_schema_id]["name"]
            target_schema_name = self._schemas[target_schema_id]["name"]
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.operation.{operation_id}",
                provider_name=f"Schema Operation: Transform from {source_schema_name} to {target_schema_name}",
                provider_type="schema_operation",
                context_types=[
                    "data_layer.schema.operation",
                    "data_layer.schema.operation.transform"
                ]
            )
            
            # Publish operation start event
            self.event_bus.publish(
                topic="data_layer.schema.operation",
                key=operation_id,
                value={
                    "operation_id": operation_id,
                    "mapping_id": mapping_id,
                    "source_schema_id": source_schema_id,
                    "target_schema_id": target_schema_id,
                    "operation_type": "transform",
                    "event_type": "operation_start",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Start transformation operation (simulated for now)
            # In a real implementation, this would start an actual transformation process
            # For now, we'll simulate it with a simple event
            self.event_bus.publish(
                topic="data_layer.schema.event",
                key=operation_id,
                value={
                    "event_type": "transformation_complete",
                    "operation_id": operation_id,
                    "transformed_data": data,  # Simulated value (just returning the input data)
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Started transformation operation {operation_id} for mapping {mapping_id}")
            
            return operation_id
        except Exception as e:
            self.logger.error(f"Error transforming data using mapping {mapping_id}: {str(e)}")
            raise
    
    def _cancel_schema_operation(self, operation_id: str) -> None:
        """
        Cancel a schema operation.
        
        Args:
            operation_id: Operation ID
        """
        try:
            # Check if operation exists
            if operation_id not in self._active_schema_operations:
                raise ValueError(f"Schema operation {operation_id} does not exist")
            
            # Get operation
            operation = self._active_schema_operations[operation_id]
            
            # Update operation status
            operation["status"] = "cancelled"
            operation["end_time"] = self.data_access.get_current_timestamp()
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.operation.{operation_id}"
            )
            
            # Publish operation cancel event
            self.event_bus.publish(
                topic="data_layer.schema.operation",
                key=operation_id,
                value={
                    "operation_id": operation_id,
                    "operation_type": operation.get("operation_type"),
                    "event_type": "operation_cancel",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Remove from active operations
            del self._active_schema_operations[operation_id]
            
            # Update metrics
            self._metrics["active_schema_operations"] = len(self._active_schema_operations)
            
            self.logger.info(f"Cancelled schema operation {operation_id}")
        except Exception as e:
            self.logger.error(f"Error cancelling schema operation {operation_id}: {str(e)}")
            raise
