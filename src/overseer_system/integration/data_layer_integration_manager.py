"""
Data Layer Integration Manager for the Overseer System.

This module provides the integration manager for the Data Layer of the
Industriverse, enabling seamless communication and data exchange between
the Overseer System and the Data Layer components.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Callable, Type

from src.integration.integration_manager import BaseIntegrationManager
from src.integration.base_integration_adapter import BaseIntegrationAdapter
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

# Import adapters
from src.integration.data_layer.data_ingestion_adapter import DataIngestionAdapter
from src.integration.data_layer.data_processing_adapter import DataProcessingAdapter
from src.integration.data_layer.data_storage_adapter import DataStorageAdapter
from src.integration.data_layer.data_schema_adapter import DataSchemaAdapter

class DataLayerIntegrationManager(BaseIntegrationManager):
    """
    Integration Manager for the Data Layer of the Industriverse.
    
    This class manages the integration between the Overseer System and
    the Data Layer components, including data ingestion, processing,
    storage, and schema management.
    """
    
    def __init__(
        self,
        integration_id: str,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        config_service: ConfigService,
        auth_service: AuthService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Data Layer Integration Manager.
        
        Args:
            integration_id: Unique identifier for this integration manager
            mcp_bridge: MCP protocol bridge for internal communication
            a2a_bridge: A2A protocol bridge for external communication
            event_bus: Event bus client for event-driven communication
            data_access: Data access service for persistence
            config_service: Configuration service for settings
            auth_service: Authentication service for security
            logger: Optional logger instance
        """
        super().__init__(
            integration_id=integration_id,
            integration_name="Data Layer Integration Manager",
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize adapter registry with supported adapter types
        self._adapter_classes = {
            "data_ingestion": DataIngestionAdapter,
            "data_processing": DataProcessingAdapter,
            "data_storage": DataStorageAdapter,
            "data_schema": DataSchemaAdapter
        }
        
        # Initialize data layer specific resources
        self._data_layer_config = self.config_service.get_config(
            f"integration.{self.integration_id}.data_layer",
            {}
        )
        
        # Initialize data layer metrics
        self._metrics = {
            "data_ingestion_count": 0,
            "data_processing_count": 0,
            "data_storage_count": 0,
            "data_schema_updates": 0,
            "error_count": 0
        }
        
        self.logger.info(f"Data Layer Integration Manager {integration_id} initialized")
    
    def _get_supported_context_types(self) -> List[str]:
        """
        Get the MCP context types supported by this integration manager.
        
        Returns:
            List of supported context types
        """
        return [
            "data_layer",
            "data_layer.ingestion",
            "data_layer.processing",
            "data_layer.storage",
            "data_layer.schema"
        ]
    
    def _get_supported_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the A2A capabilities supported by this integration manager.
        
        Returns:
            List of supported capabilities
        """
        return [
            {
                "type": "data_ingestion",
                "description": "Ingest data from various sources",
                "parameters": {
                    "source_type": {
                        "type": "string",
                        "description": "Type of data source"
                    },
                    "source_config": {
                        "type": "object",
                        "description": "Configuration for the data source"
                    }
                }
            },
            {
                "type": "data_processing",
                "description": "Process data using various transformations",
                "parameters": {
                    "processing_type": {
                        "type": "string",
                        "description": "Type of data processing"
                    },
                    "processing_config": {
                        "type": "object",
                        "description": "Configuration for the data processing"
                    }
                }
            },
            {
                "type": "data_storage",
                "description": "Store data in various storage systems",
                "parameters": {
                    "storage_type": {
                        "type": "string",
                        "description": "Type of data storage"
                    },
                    "storage_config": {
                        "type": "object",
                        "description": "Configuration for the data storage"
                    }
                }
            },
            {
                "type": "data_schema",
                "description": "Manage data schemas",
                "parameters": {
                    "schema_type": {
                        "type": "string",
                        "description": "Type of data schema"
                    },
                    "schema_config": {
                        "type": "object",
                        "description": "Configuration for the data schema"
                    }
                }
            }
        ]
    
    def _get_adapter_class(self, adapter_type: str) -> Optional[Type]:
        """
        Get the adapter class for a specific adapter type.
        
        Args:
            adapter_type: Type of adapter
        
        Returns:
            Adapter class or None if not supported
        """
        return self._adapter_classes.get(adapter_type)
    
    def _handle_custom_command(self, command: str, event: Dict[str, Any]) -> None:
        """
        Handle a custom command event.
        
        Args:
            command: Command to handle
            event: Command event data
        """
        command_id = event.get("command_id", str(uuid.uuid4()))
        
        if command == "get_metrics":
            # Publish metrics
            self.event_bus.publish(
                topic=f"integration.{self.integration_id}.response",
                key=command_id,
                value={
                    "integration_id": self.integration_id,
                    "command_id": command_id,
                    "command": command,
                    "status": "success",
                    "metrics": self._metrics
                }
            )
        elif command == "reset_metrics":
            # Reset metrics
            self._metrics = {
                "data_ingestion_count": 0,
                "data_processing_count": 0,
                "data_storage_count": 0,
                "data_schema_updates": 0,
                "error_count": 0
            }
            
            # Publish response
            self.event_bus.publish(
                topic=f"integration.{self.integration_id}.response",
                key=command_id,
                value={
                    "integration_id": self.integration_id,
                    "command_id": command_id,
                    "command": command,
                    "status": "success"
                }
            )
        elif command == "update_data_layer_config":
            # Update data layer config
            config = event.get("config", {})
            self._data_layer_config.update(config)
            
            # Save to configuration service
            self.config_service.set_config(
                f"integration.{self.integration_id}.data_layer",
                self._data_layer_config
            )
            
            # Publish response
            self.event_bus.publish(
                topic=f"integration.{self.integration_id}.response",
                key=command_id,
                value={
                    "integration_id": self.integration_id,
                    "command_id": command_id,
                    "command": command,
                    "status": "success"
                }
            )
        elif command == "get_data_layer_config":
            # Publish data layer config
            self.event_bus.publish(
                topic=f"integration.{self.integration_id}.response",
                key=command_id,
                value={
                    "integration_id": self.integration_id,
                    "command_id": command_id,
                    "command": command,
                    "status": "success",
                    "config": self._data_layer_config
                }
            )
        else:
            # Unsupported command
            self.event_bus.publish(
                topic=f"integration.{self.integration_id}.response",
                key=command_id,
                value={
                    "integration_id": self.integration_id,
                    "command_id": command_id,
                    "command": command,
                    "status": "error",
                    "error": f"Unsupported command: {command}"
                }
            )
    
    def _is_target_type(self, target_type: str) -> bool:
        """
        Check if this integration manager is of a specific target type.
        
        Args:
            target_type: Target integration type
        
        Returns:
            True if this manager is of the target type, False otherwise
        """
        return target_type in ["data_layer", "all"]
    
    def update_metrics(self, metric_type: str, count: int = 1) -> None:
        """
        Update metrics for the data layer integration.
        
        Args:
            metric_type: Type of metric to update
            count: Count to add to the metric
        """
        if metric_type in self._metrics:
            self._metrics[metric_type] += count
            
            # Publish metrics update
            self.event_bus.publish(
                topic=f"integration.{self.integration_id}.metrics",
                key=metric_type,
                value={
                    "integration_id": self.integration_id,
                    "metric_type": metric_type,
                    "value": self._metrics[metric_type],
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
    
    def get_data_layer_config(self, config_key: str, default_value: Any = None) -> Any:
        """
        Get a configuration value for the data layer integration.
        
        Args:
            config_key: Configuration key
            default_value: Default value if key not found
        
        Returns:
            Configuration value
        """
        return self._data_layer_config.get(config_key, default_value)
    
    def set_data_layer_config(self, config_key: str, config_value: Any) -> None:
        """
        Set a configuration value for the data layer integration.
        
        Args:
            config_key: Configuration key
            config_value: Configuration value
        """
        self._data_layer_config[config_key] = config_value
        
        # Save to configuration service
        self.config_service.set_config(
            f"integration.{self.integration_id}.data_layer",
            self._data_layer_config
        )
        
        # Publish config update
        self.event_bus.publish(
            topic=f"integration.{self.integration_id}.config",
            key=config_key,
            value={
                "integration_id": self.integration_id,
                "config_key": config_key,
                "config_value": config_value,
                "timestamp": self.data_access.get_current_timestamp()
            }
        )
