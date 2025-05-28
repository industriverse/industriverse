"""
Data Storage Adapter for the Overseer System.

This module provides the integration adapter for data storage components
of the Industriverse Data Layer, enabling seamless data storage and
retrieval within the Overseer System.

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

class DataStorageAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for Data Storage components of the Industriverse Data Layer.
    
    This class provides integration with data storage components, enabling
    seamless data storage and retrieval within the Overseer System.
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
        Initialize the Data Storage Adapter.
        
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
        
        # Initialize data storage specific resources
        self._storage_providers = {}
        self._storage_containers = {}
        self._active_storage_operations = {}
        
        # Initialize metrics
        self._metrics = {
            "total_stored_records": 0,
            "total_retrieved_records": 0,
            "total_storage_errors": 0,
            "active_storage_operations": 0,
            "last_storage_timestamp": None,
            "last_retrieval_timestamp": None
        }
        
        self.logger.info(f"Data Storage Adapter {adapter_id} initialized")
    
    def _get_supported_context_types(self) -> List[str]:
        """
        Get the MCP context types supported by this adapter.
        
        Returns:
            List of supported context types
        """
        return [
            "data_layer.storage",
            "data_layer.storage.provider",
            "data_layer.storage.container",
            "data_layer.storage.operation"
        ]
    
    def _get_supported_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the A2A capabilities supported by this adapter.
        
        Returns:
            List of supported capabilities
        """
        return [
            {
                "type": "data_storage",
                "description": "Store data in various storage systems",
                "parameters": {
                    "storage_type": {
                        "type": "string",
                        "description": "Type of data storage (e.g., file, database, object, time_series)"
                    },
                    "storage_config": {
                        "type": "object",
                        "description": "Configuration for the data storage"
                    },
                    "container_id": {
                        "type": "string",
                        "description": "ID of the storage container to use"
                    }
                }
            },
            {
                "type": "data_retrieval",
                "description": "Retrieve data from various storage systems",
                "parameters": {
                    "container_id": {
                        "type": "string",
                        "description": "ID of the storage container to retrieve from"
                    },
                    "query": {
                        "type": "object",
                        "description": "Query parameters for data retrieval"
                    }
                }
            },
            {
                "type": "storage_provider_management",
                "description": "Manage data storage providers",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "provider_id": {
                        "type": "string",
                        "description": "ID of the storage provider"
                    },
                    "provider_config": {
                        "type": "object",
                        "description": "Configuration for the storage provider"
                    }
                }
            },
            {
                "type": "storage_container_management",
                "description": "Manage data storage containers",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "container_id": {
                        "type": "string",
                        "description": "ID of the storage container"
                    },
                    "container_config": {
                        "type": "object",
                        "description": "Configuration for the storage container"
                    }
                }
            }
        ]
    
    def _initialize_resources(self) -> None:
        """Initialize adapter-specific resources."""
        try:
            # Load storage providers from configuration
            storage_providers_config = self.config.get("storage_providers", {})
            for provider_id, provider_config in storage_providers_config.items():
                self._create_storage_provider(provider_id, provider_config)
            
            # Load storage containers from configuration
            storage_containers_config = self.config.get("storage_containers", {})
            for container_id, container_config in storage_containers_config.items():
                self._create_storage_container(container_id, container_config)
            
            self.logger.info(f"Initialized resources for Data Storage Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error initializing resources for Data Storage Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _start_resources(self) -> None:
        """Start adapter-specific resources."""
        try:
            # Nothing to start for storage providers and containers
            self.logger.info(f"Started resources for Data Storage Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error starting resources for Data Storage Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _stop_resources(self) -> None:
        """Stop adapter-specific resources."""
        try:
            # Stop all active storage operations
            for operation_id in list(self._active_storage_operations.keys()):
                self._cancel_storage_operation(operation_id)
            
            self.logger.info(f"Stopped resources for Data Storage Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error stopping resources for Data Storage Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _release_resources(self) -> None:
        """Release adapter-specific resources."""
        try:
            # Clear all resources
            self._storage_providers = {}
            self._storage_containers = {}
            self._active_storage_operations = {}
            
            self.logger.info(f"Released resources for Data Storage Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error releasing resources for Data Storage Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _check_resource_health(self) -> str:
        """
        Check the health of adapter-specific resources.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        try:
            # Check storage providers
            unhealthy_providers = 0
            for provider_id, provider in self._storage_providers.items():
                if provider.get("status") == "error":
                    unhealthy_providers += 1
            
            # Check storage containers
            unhealthy_containers = 0
            for container_id, container in self._storage_containers.items():
                if container.get("status") == "error":
                    unhealthy_containers += 1
            
            # Check active storage operations
            unhealthy_operations = 0
            for operation_id, operation in self._active_storage_operations.items():
                if operation.get("status") == "error":
                    unhealthy_operations += 1
            
            # Determine overall health
            total_providers = len(self._storage_providers)
            total_containers = len(self._storage_containers)
            total_operations = len(self._active_storage_operations)
            
            if unhealthy_providers > 0 or unhealthy_containers > 0 or unhealthy_operations > 0:
                # At least one component is unhealthy
                if (unhealthy_providers / max(total_providers, 1) > 0.5 or
                    unhealthy_containers / max(total_containers, 1) > 0.5 or
                    unhealthy_operations / max(total_operations, 1) > 0.5):
                    # More than 50% of components are unhealthy
                    return "unhealthy"
                else:
                    # Less than 50% of components are unhealthy
                    return "degraded"
            else:
                # All components are healthy
                return "healthy"
        except Exception as e:
            self.logger.error(f"Error checking resource health for Data Storage Adapter {self.adapter_id}: {str(e)}")
            return "unhealthy"
    
    def _apply_configuration(self) -> None:
        """Apply configuration changes."""
        try:
            # Apply storage provider configuration changes
            storage_providers_config = self.config.get("storage_providers", {})
            
            # Remove deleted storage providers
            for provider_id in list(self._storage_providers.keys()):
                if provider_id not in storage_providers_config:
                    self._delete_storage_provider(provider_id)
            
            # Add or update storage providers
            for provider_id, provider_config in storage_providers_config.items():
                if provider_id in self._storage_providers:
                    self._update_storage_provider(provider_id, provider_config)
                else:
                    self._create_storage_provider(provider_id, provider_config)
            
            # Apply storage container configuration changes
            storage_containers_config = self.config.get("storage_containers", {})
            
            # Remove deleted storage containers
            for container_id in list(self._storage_containers.keys()):
                if container_id not in storage_containers_config:
                    self._delete_storage_container(container_id)
            
            # Add or update storage containers
            for container_id, container_config in storage_containers_config.items():
                if container_id in self._storage_containers:
                    self._update_storage_container(container_id, container_config)
                else:
                    self._create_storage_container(container_id, container_config)
            
            self.logger.info(f"Applied configuration changes for Data Storage Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error applying configuration changes for Data Storage Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _get_status_data(self) -> Dict[str, Any]:
        """
        Get adapter-specific status data.
        
        Returns:
            Adapter-specific status data
        """
        return {
            "storage_providers": {
                provider_id: {
                    "type": provider.get("type"),
                    "status": provider.get("status")
                }
                for provider_id, provider in self._storage_providers.items()
            },
            "storage_containers": {
                container_id: {
                    "status": container.get("status"),
                    "provider_id": container.get("provider_id")
                }
                for container_id, container in self._storage_containers.items()
            },
            "active_storage_operations": {
                operation_id: {
                    "container_id": operation.get("container_id"),
                    "operation_type": operation.get("operation_type"),
                    "status": operation.get("status"),
                    "start_time": operation.get("start_time")
                }
                for operation_id, operation in self._active_storage_operations.items()
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
        if command == "create_storage_provider":
            provider_id = event.get("provider_id", str(uuid.uuid4()))
            provider_config = event.get("provider_config", {})
            self._create_storage_provider(provider_id, provider_config)
            return {"provider_id": provider_id}
        
        elif command == "update_storage_provider":
            provider_id = event.get("provider_id")
            provider_config = event.get("provider_config", {})
            if not provider_id:
                raise ValueError("provider_id is required")
            self._update_storage_provider(provider_id, provider_config)
            return {"provider_id": provider_id}
        
        elif command == "delete_storage_provider":
            provider_id = event.get("provider_id")
            if not provider_id:
                raise ValueError("provider_id is required")
            self._delete_storage_provider(provider_id)
            return {"provider_id": provider_id}
        
        elif command == "list_storage_providers":
            return {
                "storage_providers": {
                    provider_id: {
                        "type": provider.get("type"),
                        "status": provider.get("status")
                    }
                    for provider_id, provider in self._storage_providers.items()
                }
            }
        
        elif command == "create_storage_container":
            container_id = event.get("container_id", str(uuid.uuid4()))
            container_config = event.get("container_config", {})
            self._create_storage_container(container_id, container_config)
            return {"container_id": container_id}
        
        elif command == "update_storage_container":
            container_id = event.get("container_id")
            container_config = event.get("container_config", {})
            if not container_id:
                raise ValueError("container_id is required")
            self._update_storage_container(container_id, container_config)
            return {"container_id": container_id}
        
        elif command == "delete_storage_container":
            container_id = event.get("container_id")
            if not container_id:
                raise ValueError("container_id is required")
            self._delete_storage_container(container_id)
            return {"container_id": container_id}
        
        elif command == "list_storage_containers":
            return {
                "storage_containers": {
                    container_id: {
                        "status": container.get("status"),
                        "provider_id": container.get("provider_id")
                    }
                    for container_id, container in self._storage_containers.items()
                }
            }
        
        elif command == "store_data":
            container_id = event.get("container_id")
            data = event.get("data")
            options = event.get("options", {})
            if not container_id:
                raise ValueError("container_id is required")
            if data is None:
                raise ValueError("data is required")
            operation_id = self._store_data(container_id, data, options)
            return {"operation_id": operation_id, "container_id": container_id}
        
        elif command == "retrieve_data":
            container_id = event.get("container_id")
            query = event.get("query", {})
            options = event.get("options", {})
            if not container_id:
                raise ValueError("container_id is required")
            operation_id = self._retrieve_data(container_id, query, options)
            return {"operation_id": operation_id, "container_id": container_id}
        
        elif command == "cancel_storage_operation":
            operation_id = event.get("operation_id")
            if not operation_id:
                raise ValueError("operation_id is required")
            self._cancel_storage_operation(operation_id)
            return {"operation_id": operation_id}
        
        elif command == "list_storage_operations":
            return {
                "active_storage_operations": {
                    operation_id: {
                        "container_id": operation.get("container_id"),
                        "operation_type": operation.get("operation_type"),
                        "status": operation.get("status"),
                        "start_time": operation.get("start_time")
                    }
                    for operation_id, operation in self._active_storage_operations.items()
                }
            }
        
        elif command == "get_metrics":
            return {"metrics": self._metrics}
        
        elif command == "reset_metrics":
            self._metrics = {
                "total_stored_records": 0,
                "total_retrieved_records": 0,
                "total_storage_errors": 0,
                "active_storage_operations": 0,
                "last_storage_timestamp": None,
                "last_retrieval_timestamp": None
            }
            return {"metrics": self._metrics}
        
        else:
            raise ValueError(f"Unsupported command: {command}")
    
    def _subscribe_to_additional_events(self) -> None:
        """Subscribe to additional events specific to this adapter."""
        try:
            # Subscribe to data storage events
            self.event_bus.subscribe(
                topic="data_layer.storage.event",
                group_id=f"{self.adapter_id}-storage-event-handler",
                callback=self._handle_storage_event
            )
            
            self.logger.info(f"Subscribed to additional events for Data Storage Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error subscribing to additional events for Data Storage Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _unsubscribe_from_additional_events(self) -> None:
        """Unsubscribe from additional events specific to this adapter."""
        try:
            # Unsubscribe from data storage events
            self.event_bus.unsubscribe(
                topic="data_layer.storage.event",
                group_id=f"{self.adapter_id}-storage-event-handler"
            )
            
            self.logger.info(f"Unsubscribed from additional events for Data Storage Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error unsubscribing from additional events for Data Storage Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _handle_storage_event(self, event: Dict[str, Any]) -> None:
        """
        Handle data storage events.
        
        Args:
            event: Event data
        """
        try:
            event_type = event.get("event_type")
            
            if event_type == "storage_complete":
                operation_id = event.get("operation_id")
                records_stored = event.get("records_stored", 0)
                
                # Update metrics
                self._metrics["total_stored_records"] += records_stored
                self._metrics["last_storage_timestamp"] = self.data_access.get_current_timestamp()
                
                # Update operation status
                if operation_id in self._active_storage_operations:
                    operation = self._active_storage_operations[operation_id]
                    operation["status"] = "completed"
                    operation["records_stored"] = records_stored
                    operation["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active operations
                    del self._active_storage_operations[operation_id]
                    self._metrics["active_storage_operations"] = len(self._active_storage_operations)
                
                # Notify manager
                if hasattr(self.manager, "update_metrics"):
                    self.manager.update_metrics("data_storage_count", records_stored)
                
                self.logger.info(f"Storage operation {operation_id} completed: {records_stored} records stored")
            
            elif event_type == "retrieval_complete":
                operation_id = event.get("operation_id")
                records_retrieved = event.get("records_retrieved", 0)
                
                # Update metrics
                self._metrics["total_retrieved_records"] += records_retrieved
                self._metrics["last_retrieval_timestamp"] = self.data_access.get_current_timestamp()
                
                # Update operation status
                if operation_id in self._active_storage_operations:
                    operation = self._active_storage_operations[operation_id]
                    operation["status"] = "completed"
                    operation["records_retrieved"] = records_retrieved
                    operation["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active operations
                    del self._active_storage_operations[operation_id]
                    self._metrics["active_storage_operations"] = len(self._active_storage_operations)
                
                self.logger.info(f"Retrieval operation {operation_id} completed: {records_retrieved} records retrieved")
            
            elif event_type == "storage_error":
                operation_id = event.get("operation_id")
                error = event.get("error")
                
                # Update metrics
                self._metrics["total_storage_errors"] += 1
                
                # Update operation status
                if operation_id in self._active_storage_operations:
                    operation = self._active_storage_operations[operation_id]
                    operation["status"] = "error"
                    operation["error"] = error
                    operation["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active operations
                    del self._active_storage_operations[operation_id]
                    self._metrics["active_storage_operations"] = len(self._active_storage_operations)
                
                # Notify manager
                if hasattr(self.manager, "update_metrics"):
                    self.manager.update_metrics("error_count", 1)
                
                self.logger.error(f"Storage operation {operation_id} error: {error}")
            
            elif event_type == "storage_progress":
                operation_id = event.get("operation_id")
                records_processed = event.get("records_processed", 0)
                
                # Update operation status
                if operation_id in self._active_storage_operations:
                    operation = self._active_storage_operations[operation_id]
                    operation["records_processed"] = records_processed
                
                self.logger.debug(f"Storage operation {operation_id} progress: {records_processed} records processed")
        except Exception as e:
            self.logger.error(f"Error handling storage event: {str(e)}")
    
    def _create_storage_provider(self, provider_id: str, provider_config: Dict[str, Any]) -> None:
        """
        Create a new storage provider.
        
        Args:
            provider_id: Storage provider ID
            provider_config: Storage provider configuration
        """
        try:
            # Validate provider configuration
            provider_type = provider_config.get("type")
            if not provider_type:
                raise ValueError("Provider type is required")
            
            # Create storage provider
            self._storage_providers[provider_id] = {
                "id": provider_id,
                "type": provider_type,
                "config": provider_config,
                "status": "initialized"
            }
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.provider.{provider_id}",
                provider_name=f"Storage Provider: {provider_id}",
                provider_type="storage_provider",
                context_types=[
                    "data_layer.storage.provider",
                    f"data_layer.storage.provider.{provider_type}"
                ]
            )
            
            # Save to configuration
            self.config["storage_providers"] = self.config.get("storage_providers", {})
            self.config["storage_providers"][provider_id] = provider_config
            
            self.logger.info(f"Created storage provider {provider_id} of type {provider_type}")
        except Exception as e:
            self.logger.error(f"Error creating storage provider {provider_id}: {str(e)}")
            raise
    
    def _update_storage_provider(self, provider_id: str, provider_config: Dict[str, Any]) -> None:
        """
        Update an existing storage provider.
        
        Args:
            provider_id: Storage provider ID
            provider_config: Storage provider configuration
        """
        try:
            # Check if storage provider exists
            if provider_id not in self._storage_providers:
                raise ValueError(f"Storage provider {provider_id} does not exist")
            
            # Validate provider configuration
            provider_type = provider_config.get("type")
            if not provider_type:
                raise ValueError("Provider type is required")
            
            # Update storage provider
            self._storage_providers[provider_id]["type"] = provider_type
            self._storage_providers[provider_id]["config"] = provider_config
            self._storage_providers[provider_id]["status"] = "initialized"
            
            # Update MCP registration if type changed
            if self._storage_providers[provider_id]["type"] != provider_type:
                # Unregister old context provider
                self.mcp_bridge.unregister_context_provider(
                    provider_id=f"{self.adapter_id}.provider.{provider_id}"
                )
                
                # Register new context provider
                self.mcp_bridge.register_context_provider(
                    provider_id=f"{self.adapter_id}.provider.{provider_id}",
                    provider_name=f"Storage Provider: {provider_id}",
                    provider_type="storage_provider",
                    context_types=[
                        "data_layer.storage.provider",
                        f"data_layer.storage.provider.{provider_type}"
                    ]
                )
            
            # Save to configuration
            self.config["storage_providers"] = self.config.get("storage_providers", {})
            self.config["storage_providers"][provider_id] = provider_config
            
            self.logger.info(f"Updated storage provider {provider_id} of type {provider_type}")
        except Exception as e:
            self.logger.error(f"Error updating storage provider {provider_id}: {str(e)}")
            raise
    
    def _delete_storage_provider(self, provider_id: str) -> None:
        """
        Delete a storage provider.
        
        Args:
            provider_id: Storage provider ID
        """
        try:
            # Check if storage provider exists
            if provider_id not in self._storage_providers:
                raise ValueError(f"Storage provider {provider_id} does not exist")
            
            # Check if storage provider is used by any container
            for container_id, container in self._storage_containers.items():
                if container.get("provider_id") == provider_id:
                    raise ValueError(f"Storage provider {provider_id} is used by container {container_id}")
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.provider.{provider_id}"
            )
            
            # Delete storage provider
            del self._storage_providers[provider_id]
            
            # Remove from configuration
            if "storage_providers" in self.config and provider_id in self.config["storage_providers"]:
                del self.config["storage_providers"][provider_id]
            
            self.logger.info(f"Deleted storage provider {provider_id}")
        except Exception as e:
            self.logger.error(f"Error deleting storage provider {provider_id}: {str(e)}")
            raise
    
    def _create_storage_container(self, container_id: str, container_config: Dict[str, Any]) -> None:
        """
        Create a new storage container.
        
        Args:
            container_id: Storage container ID
            container_config: Storage container configuration
        """
        try:
            # Validate container configuration
            provider_id = container_config.get("provider_id")
            if not provider_id:
                raise ValueError("Provider ID is required")
            
            # Check if storage provider exists
            if provider_id not in self._storage_providers:
                raise ValueError(f"Storage provider {provider_id} does not exist")
            
            # Create storage container
            self._storage_containers[container_id] = {
                "id": container_id,
                "provider_id": provider_id,
                "config": container_config,
                "status": "initialized"
            }
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.container.{container_id}",
                provider_name=f"Storage Container: {container_id}",
                provider_type="storage_container",
                context_types=[
                    "data_layer.storage.container"
                ]
            )
            
            # Save to configuration
            self.config["storage_containers"] = self.config.get("storage_containers", {})
            self.config["storage_containers"][container_id] = container_config
            
            self.logger.info(f"Created storage container {container_id} for provider {provider_id}")
        except Exception as e:
            self.logger.error(f"Error creating storage container {container_id}: {str(e)}")
            raise
    
    def _update_storage_container(self, container_id: str, container_config: Dict[str, Any]) -> None:
        """
        Update an existing storage container.
        
        Args:
            container_id: Storage container ID
            container_config: Storage container configuration
        """
        try:
            # Check if storage container exists
            if container_id not in self._storage_containers:
                raise ValueError(f"Storage container {container_id} does not exist")
            
            # Validate container configuration
            provider_id = container_config.get("provider_id")
            if not provider_id:
                raise ValueError("Provider ID is required")
            
            # Check if storage provider exists
            if provider_id not in self._storage_providers:
                raise ValueError(f"Storage provider {provider_id} does not exist")
            
            # Update storage container
            self._storage_containers[container_id]["provider_id"] = provider_id
            self._storage_containers[container_id]["config"] = container_config
            self._storage_containers[container_id]["status"] = "initialized"
            
            # Save to configuration
            self.config["storage_containers"] = self.config.get("storage_containers", {})
            self.config["storage_containers"][container_id] = container_config
            
            self.logger.info(f"Updated storage container {container_id} for provider {provider_id}")
        except Exception as e:
            self.logger.error(f"Error updating storage container {container_id}: {str(e)}")
            raise
    
    def _delete_storage_container(self, container_id: str) -> None:
        """
        Delete a storage container.
        
        Args:
            container_id: Storage container ID
        """
        try:
            # Check if storage container exists
            if container_id not in self._storage_containers:
                raise ValueError(f"Storage container {container_id} does not exist")
            
            # Check if storage container is used by any active operation
            for operation_id, operation in self._active_storage_operations.items():
                if operation.get("container_id") == container_id:
                    raise ValueError(f"Storage container {container_id} is used by operation {operation_id}")
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.container.{container_id}"
            )
            
            # Delete storage container
            del self._storage_containers[container_id]
            
            # Remove from configuration
            if "storage_containers" in self.config and container_id in self.config["storage_containers"]:
                del self.config["storage_containers"][container_id]
            
            self.logger.info(f"Deleted storage container {container_id}")
        except Exception as e:
            self.logger.error(f"Error deleting storage container {container_id}: {str(e)}")
            raise
    
    def _store_data(self, container_id: str, data: Any, options: Dict[str, Any] = None) -> str:
        """
        Store data in a storage container.
        
        Args:
            container_id: Storage container ID
            data: Data to store
            options: Optional storage options
        
        Returns:
            Operation ID
        """
        try:
            # Check if storage container exists
            if container_id not in self._storage_containers:
                raise ValueError(f"Storage container {container_id} does not exist")
            
            # Create operation ID
            operation_id = str(uuid.uuid4())
            
            # Get container and provider
            container = self._storage_containers[container_id]
            provider_id = container.get("provider_id")
            provider = self._storage_providers.get(provider_id)
            
            if not provider:
                raise ValueError(f"Storage provider {provider_id} does not exist")
            
            # Create storage operation
            self._active_storage_operations[operation_id] = {
                "id": operation_id,
                "container_id": container_id,
                "provider_id": provider_id,
                "operation_type": "store",
                "status": "running",
                "start_time": self.data_access.get_current_timestamp(),
                "options": options or {}
            }
            
            # Update metrics
            self._metrics["active_storage_operations"] = len(self._active_storage_operations)
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.operation.{operation_id}",
                provider_name=f"Storage Operation: {operation_id}",
                provider_type="storage_operation",
                context_types=[
                    "data_layer.storage.operation",
                    "data_layer.storage.operation.store"
                ]
            )
            
            # Publish operation start event
            self.event_bus.publish(
                topic="data_layer.storage.operation",
                key=operation_id,
                value={
                    "operation_id": operation_id,
                    "container_id": container_id,
                    "provider_id": provider_id,
                    "operation_type": "store",
                    "event_type": "operation_start",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Start storage operation (simulated for now)
            # In a real implementation, this would start an actual storage process
            # For now, we'll simulate it with a simple event
            self.event_bus.publish(
                topic="data_layer.storage.event",
                key=operation_id,
                value={
                    "event_type": "storage_complete",
                    "operation_id": operation_id,
                    "records_stored": 100,  # Simulated value
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Started storage operation {operation_id} for container {container_id}")
            
            return operation_id
        except Exception as e:
            self.logger.error(f"Error storing data in container {container_id}: {str(e)}")
            raise
    
    def _retrieve_data(self, container_id: str, query: Dict[str, Any], options: Dict[str, Any] = None) -> str:
        """
        Retrieve data from a storage container.
        
        Args:
            container_id: Storage container ID
            query: Query parameters for data retrieval
            options: Optional retrieval options
        
        Returns:
            Operation ID
        """
        try:
            # Check if storage container exists
            if container_id not in self._storage_containers:
                raise ValueError(f"Storage container {container_id} does not exist")
            
            # Create operation ID
            operation_id = str(uuid.uuid4())
            
            # Get container and provider
            container = self._storage_containers[container_id]
            provider_id = container.get("provider_id")
            provider = self._storage_providers.get(provider_id)
            
            if not provider:
                raise ValueError(f"Storage provider {provider_id} does not exist")
            
            # Create retrieval operation
            self._active_storage_operations[operation_id] = {
                "id": operation_id,
                "container_id": container_id,
                "provider_id": provider_id,
                "operation_type": "retrieve",
                "status": "running",
                "start_time": self.data_access.get_current_timestamp(),
                "query": query,
                "options": options or {}
            }
            
            # Update metrics
            self._metrics["active_storage_operations"] = len(self._active_storage_operations)
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.operation.{operation_id}",
                provider_name=f"Storage Operation: {operation_id}",
                provider_type="storage_operation",
                context_types=[
                    "data_layer.storage.operation",
                    "data_layer.storage.operation.retrieve"
                ]
            )
            
            # Publish operation start event
            self.event_bus.publish(
                topic="data_layer.storage.operation",
                key=operation_id,
                value={
                    "operation_id": operation_id,
                    "container_id": container_id,
                    "provider_id": provider_id,
                    "operation_type": "retrieve",
                    "event_type": "operation_start",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Start retrieval operation (simulated for now)
            # In a real implementation, this would start an actual retrieval process
            # For now, we'll simulate it with a simple event
            self.event_bus.publish(
                topic="data_layer.storage.event",
                key=operation_id,
                value={
                    "event_type": "retrieval_complete",
                    "operation_id": operation_id,
                    "records_retrieved": 100,  # Simulated value
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Started retrieval operation {operation_id} for container {container_id}")
            
            return operation_id
        except Exception as e:
            self.logger.error(f"Error retrieving data from container {container_id}: {str(e)}")
            raise
    
    def _cancel_storage_operation(self, operation_id: str) -> None:
        """
        Cancel a storage operation.
        
        Args:
            operation_id: Storage operation ID
        """
        try:
            # Check if storage operation exists
            if operation_id not in self._active_storage_operations:
                raise ValueError(f"Storage operation {operation_id} does not exist")
            
            # Get operation
            operation = self._active_storage_operations[operation_id]
            
            # Update operation status
            operation["status"] = "cancelled"
            operation["end_time"] = self.data_access.get_current_timestamp()
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.operation.{operation_id}"
            )
            
            # Publish operation cancel event
            self.event_bus.publish(
                topic="data_layer.storage.operation",
                key=operation_id,
                value={
                    "operation_id": operation_id,
                    "container_id": operation.get("container_id"),
                    "provider_id": operation.get("provider_id"),
                    "operation_type": operation.get("operation_type"),
                    "event_type": "operation_cancel",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Remove from active operations
            del self._active_storage_operations[operation_id]
            
            # Update metrics
            self._metrics["active_storage_operations"] = len(self._active_storage_operations)
            
            self.logger.info(f"Cancelled storage operation {operation_id}")
        except Exception as e:
            self.logger.error(f"Error cancelling storage operation {operation_id}: {str(e)}")
            raise
