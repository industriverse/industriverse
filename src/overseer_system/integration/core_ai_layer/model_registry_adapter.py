"""
Model Registry Adapter for the Core AI Layer Integration.

This module provides the Model Registry adapter for integrating with model registry components
of the Industriverse Core AI Layer, enabling seamless model versioning, storage, and retrieval.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Callable

from src.integration.base_integration_adapter import BaseIntegrationAdapter
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class ModelRegistryAdapter(BaseIntegrationAdapter):
    """
    Adapter for integrating with Model Registry components of the Industriverse Core AI Layer.
    
    This class provides the interface for model versioning, storage, and retrieval operations,
    enabling seamless model lifecycle management across the Overseer System.
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
        Initialize the Model Registry adapter.
        
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
            adapter_type="model_registry",
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
        
        # Initialize Model Registry-specific resources
        self._models = {}
        self._model_versions = {}
        self._model_artifacts = {}
        self._model_deployments = {}
        
        # Initialize metrics
        self._metrics = {
            "total_model_registrations": 0,
            "total_model_retrievals": 0,
            "total_model_deployments": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Model Registry adapter {adapter_id} initialized")
    
    def _initialize_resources(self) -> None:
        """Initialize adapter-specific resources."""
        try:
            # Load models from configuration
            models_config = self.config.get("models", {})
            for model_id, model_config in models_config.items():
                self._register_model(model_id, model_config)
            
            # Register MCP context handlers
            self._register_mcp_context_handlers()
            
            # Register A2A capability handlers
            self._register_a2a_capability_handlers()
            
            # Subscribe to events
            self._subscribe_to_events()
            
            self.logger.info(f"Initialized resources for Model Registry adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error initializing resources for Model Registry adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _start_resources(self) -> None:
        """Start adapter-specific resources."""
        try:
            # No specific resources to start for Model Registry
            self.logger.info(f"Started resources for Model Registry adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error starting resources for Model Registry adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _stop_resources(self) -> None:
        """Stop adapter-specific resources."""
        try:
            # No specific resources to stop for Model Registry
            self.logger.info(f"Stopped resources for Model Registry adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error stopping resources for Model Registry adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _release_resources(self) -> None:
        """Release adapter-specific resources."""
        try:
            # Clear model data
            self._models = {}
            self._model_versions = {}
            self._model_artifacts = {}
            self._model_deployments = {}
            
            # Unregister MCP context handlers
            self._unregister_mcp_context_handlers()
            
            # Unregister A2A capability handlers
            self._unregister_a2a_capability_handlers()
            
            # Unsubscribe from events
            self._unsubscribe_from_events()
            
            self.logger.info(f"Released resources for Model Registry adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error releasing resources for Model Registry adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _check_resource_health(self) -> str:
        """
        Check the health of adapter-specific resources.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        try:
            # Model Registry is a stateless service, so it's healthy if it's running
            return "healthy"
        except Exception as e:
            self.logger.error(f"Error checking resource health for Model Registry adapter {self.adapter_id}: {str(e)}")
            return "unhealthy"
    
    def _apply_configuration(self) -> None:
        """Apply configuration changes."""
        try:
            # Apply model configuration changes
            models_config = self.config.get("models", {})
            
            # Remove deleted models
            for model_id in list(self._models.keys()):
                if model_id not in models_config:
                    self._unregister_model(model_id)
            
            # Add or update models
            for model_id, model_config in models_config.items():
                if model_id in self._models:
                    # Update existing model
                    self._update_model(model_id, model_config)
                else:
                    # Register new model
                    self._register_model(model_id, model_config)
            
            self.logger.info(f"Applied configuration changes for Model Registry adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error applying configuration changes for Model Registry adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _get_status_data(self) -> Dict[str, Any]:
        """
        Get adapter-specific status data.
        
        Returns:
            Adapter-specific status data
        """
        return {
            "models": {
                model_id: {
                    "name": model.get("name", "unknown"),
                    "type": model.get("type", "unknown"),
                    "versions": len(self._get_model_versions(model_id)),
                    "latest_version": self._get_latest_model_version(model_id),
                    "deployments": len(self._get_model_deployments(model_id))
                }
                for model_id, model in self._models.items()
            },
            "total_models": len(self._models),
            "total_versions": len(self._model_versions),
            "total_artifacts": len(self._model_artifacts),
            "total_deployments": len(self._model_deployments),
            "metrics": self._metrics
        }
    
    def _register_mcp_context_handlers(self) -> None:
        """Register MCP context handlers."""
        # Register context handlers for Model Registry operations
        self.mcp_bridge.register_context_handler(
            context_type="core_ai_layer.model_registry.model_management",
            handler=self._handle_mcp_model_management_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="core_ai_layer.model_registry.version_management",
            handler=self._handle_mcp_version_management_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="core_ai_layer.model_registry.artifact_management",
            handler=self._handle_mcp_artifact_management_context
        )
        
        self.mcp_bridge.register_context_handler(
            context_type="core_ai_layer.model_registry.deployment_management",
            handler=self._handle_mcp_deployment_management_context
        )
    
    def _unregister_mcp_context_handlers(self) -> None:
        """Unregister MCP context handlers."""
        # Unregister context handlers for Model Registry operations
        self.mcp_bridge.unregister_context_handler(
            context_type="core_ai_layer.model_registry.model_management"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="core_ai_layer.model_registry.version_management"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="core_ai_layer.model_registry.artifact_management"
        )
        
        self.mcp_bridge.unregister_context_handler(
            context_type="core_ai_layer.model_registry.deployment_management"
        )
    
    def _register_a2a_capability_handlers(self) -> None:
        """Register A2A capability handlers."""
        # Register capability handlers for Model Registry operations
        self.a2a_bridge.register_capability_handler(
            capability_type="model_registry_model_management",
            handler=self._handle_a2a_model_management_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="model_registry_version_management",
            handler=self._handle_a2a_version_management_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="model_registry_artifact_management",
            handler=self._handle_a2a_artifact_management_capability
        )
        
        self.a2a_bridge.register_capability_handler(
            capability_type="model_registry_deployment_management",
            handler=self._handle_a2a_deployment_management_capability
        )
    
    def _unregister_a2a_capability_handlers(self) -> None:
        """Unregister A2A capability handlers."""
        # Unregister capability handlers for Model Registry operations
        self.a2a_bridge.unregister_capability_handler(
            capability_type="model_registry_model_management"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="model_registry_version_management"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="model_registry_artifact_management"
        )
        
        self.a2a_bridge.unregister_capability_handler(
            capability_type="model_registry_deployment_management"
        )
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to events."""
        # Subscribe to Model Registry-related events
        self.event_bus.subscribe(
            topic="core_ai_layer.model_registry.model_updated",
            handler=self._handle_model_updated_event
        )
        
        self.event_bus.subscribe(
            topic="core_ai_layer.model_registry.version_updated",
            handler=self._handle_version_updated_event
        )
        
        self.event_bus.subscribe(
            topic="core_ai_layer.model_registry.artifact_updated",
            handler=self._handle_artifact_updated_event
        )
        
        self.event_bus.subscribe(
            topic="core_ai_layer.model_registry.deployment_updated",
            handler=self._handle_deployment_updated_event
        )
    
    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        # Unsubscribe from Model Registry-related events
        self.event_bus.unsubscribe(
            topic="core_ai_layer.model_registry.model_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="core_ai_layer.model_registry.version_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="core_ai_layer.model_registry.artifact_updated"
        )
        
        self.event_bus.unsubscribe(
            topic="core_ai_layer.model_registry.deployment_updated"
        )
    
    def _handle_mcp_model_management_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP model management context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            model_id = context.get("model_id")
            model_data = context.get("model_data", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "register":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not model_data:
                    raise ValueError("model_data is required")
                
                result = self.register_model(model_id, model_data)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            elif action == "update":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not model_data:
                    raise ValueError("model_data is required")
                
                result = self.update_model(model_id, model_data)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            elif action == "unregister":
                if not model_id:
                    raise ValueError("model_id is required")
                
                result = self.unregister_model(model_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            elif action == "get":
                if not model_id:
                    raise ValueError("model_id is required")
                
                result = self.get_model(model_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            elif action == "list":
                result = self.list_models()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP model management context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_version_management_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP version management context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            model_id = context.get("model_id")
            version_id = context.get("version_id")
            version_data = context.get("version_data", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "create":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_data:
                    raise ValueError("version_data is required")
                
                version_id = version_id or str(uuid.uuid4())
                result = self.create_model_version(model_id, version_id, version_data)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "result": result
                }
            
            elif action == "update":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                if not version_data:
                    raise ValueError("version_data is required")
                
                result = self.update_model_version(model_id, version_id, version_data)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "result": result
                }
            
            elif action == "delete":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                result = self.delete_model_version(model_id, version_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "result": result
                }
            
            elif action == "get":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                result = self.get_model_version(model_id, version_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "result": result
                }
            
            elif action == "list":
                if not model_id:
                    raise ValueError("model_id is required")
                
                result = self.list_model_versions(model_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            elif action == "get_latest":
                if not model_id:
                    raise ValueError("model_id is required")
                
                result = self.get_latest_model_version(model_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP version management context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_artifact_management_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP artifact management context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            model_id = context.get("model_id")
            version_id = context.get("version_id")
            artifact_id = context.get("artifact_id")
            artifact_data = context.get("artifact_data", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "upload":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                if not artifact_data:
                    raise ValueError("artifact_data is required")
                
                artifact_id = artifact_id or str(uuid.uuid4())
                result = self.upload_model_artifact(model_id, version_id, artifact_id, artifact_data)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "artifact_id": artifact_id,
                    "result": result
                }
            
            elif action == "download":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                if not artifact_id:
                    raise ValueError("artifact_id is required")
                
                result = self.download_model_artifact(model_id, version_id, artifact_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "artifact_id": artifact_id,
                    "result": result
                }
            
            elif action == "delete":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                if not artifact_id:
                    raise ValueError("artifact_id is required")
                
                result = self.delete_model_artifact(model_id, version_id, artifact_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "artifact_id": artifact_id,
                    "result": result
                }
            
            elif action == "get":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                if not artifact_id:
                    raise ValueError("artifact_id is required")
                
                result = self.get_model_artifact(model_id, version_id, artifact_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "artifact_id": artifact_id,
                    "result": result
                }
            
            elif action == "list":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                result = self.list_model_artifacts(model_id, version_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP artifact management context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_mcp_deployment_management_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP deployment management context.
        
        Args:
            context: MCP context data
        
        Returns:
            Context result data
        """
        try:
            # Extract context data
            action = context.get("action")
            model_id = context.get("model_id")
            version_id = context.get("version_id")
            deployment_id = context.get("deployment_id")
            deployment_data = context.get("deployment_data", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "create":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                if not deployment_data:
                    raise ValueError("deployment_data is required")
                
                deployment_id = deployment_id or str(uuid.uuid4())
                result = self.create_model_deployment(model_id, version_id, deployment_id, deployment_data)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "deployment_id": deployment_id,
                    "result": result
                }
            
            elif action == "update":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not deployment_id:
                    raise ValueError("deployment_id is required")
                
                if not deployment_data:
                    raise ValueError("deployment_data is required")
                
                result = self.update_model_deployment(model_id, deployment_id, deployment_data)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "deployment_id": deployment_id,
                    "result": result
                }
            
            elif action == "delete":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not deployment_id:
                    raise ValueError("deployment_id is required")
                
                result = self.delete_model_deployment(model_id, deployment_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "deployment_id": deployment_id,
                    "result": result
                }
            
            elif action == "get":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not deployment_id:
                    raise ValueError("deployment_id is required")
                
                result = self.get_model_deployment(model_id, deployment_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "deployment_id": deployment_id,
                    "result": result
                }
            
            elif action == "list":
                if not model_id:
                    raise ValueError("model_id is required")
                
                result = self.list_model_deployments(model_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling MCP deployment management context: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_model_management_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A model management capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            model_id = capability_data.get("model_id")
            model_data = capability_data.get("model_data", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "register":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not model_data:
                    raise ValueError("model_data is required")
                
                result = self.register_model(model_id, model_data)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            elif action == "get":
                if not model_id:
                    raise ValueError("model_id is required")
                
                result = self.get_model(model_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            elif action == "list":
                result = self.list_models()
                
                return {
                    "status": "success",
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A model management capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_version_management_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A version management capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            model_id = capability_data.get("model_id")
            version_id = capability_data.get("version_id")
            version_data = capability_data.get("version_data", {})
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "create":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_data:
                    raise ValueError("version_data is required")
                
                version_id = version_id or str(uuid.uuid4())
                result = self.create_model_version(model_id, version_id, version_data)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "result": result
                }
            
            elif action == "get":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                result = self.get_model_version(model_id, version_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "result": result
                }
            
            elif action == "list":
                if not model_id:
                    raise ValueError("model_id is required")
                
                result = self.list_model_versions(model_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            elif action == "get_latest":
                if not model_id:
                    raise ValueError("model_id is required")
                
                result = self.get_latest_model_version(model_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A version management capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_artifact_management_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A artifact management capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            model_id = capability_data.get("model_id")
            version_id = capability_data.get("version_id")
            artifact_id = capability_data.get("artifact_id")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "download":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                if not artifact_id:
                    raise ValueError("artifact_id is required")
                
                result = self.download_model_artifact(model_id, version_id, artifact_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "artifact_id": artifact_id,
                    "result": result
                }
            
            elif action == "get":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                if not artifact_id:
                    raise ValueError("artifact_id is required")
                
                result = self.get_model_artifact(model_id, version_id, artifact_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "artifact_id": artifact_id,
                    "result": result
                }
            
            elif action == "list":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not version_id:
                    raise ValueError("version_id is required")
                
                result = self.list_model_artifacts(model_id, version_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "version_id": version_id,
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A artifact management capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_a2a_deployment_management_capability(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A deployment management capability.
        
        Args:
            capability_data: A2A capability data
        
        Returns:
            Capability result data
        """
        try:
            # Extract capability data
            action = capability_data.get("action")
            model_id = capability_data.get("model_id")
            deployment_id = capability_data.get("deployment_id")
            
            # Validate required fields
            if not action:
                raise ValueError("action is required")
            
            # Perform action
            if action == "get":
                if not model_id:
                    raise ValueError("model_id is required")
                
                if not deployment_id:
                    raise ValueError("deployment_id is required")
                
                result = self.get_model_deployment(model_id, deployment_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "deployment_id": deployment_id,
                    "result": result
                }
            
            elif action == "list":
                if not model_id:
                    raise ValueError("model_id is required")
                
                result = self.list_model_deployments(model_id)
                
                return {
                    "status": "success",
                    "model_id": model_id,
                    "result": result
                }
            
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            self.logger.error(f"Error handling A2A deployment management capability: {str(e)}")
            self._metrics["total_errors"] += 1
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_model_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle model updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            model_id = event_data.get("model_id")
            model_data = event_data.get("model_data")
            
            # Validate required fields
            if not model_id:
                self.logger.warning("Received model updated event without model_id")
                return
            
            if not model_data:
                self.logger.warning(f"Received model updated event for model {model_id} without model_data")
                return
            
            # Update model if it exists
            if model_id in self._models:
                self._models[model_id].update(model_data)
                self.logger.info(f"Updated model {model_id} from event")
        except Exception as e:
            self.logger.error(f"Error handling model updated event: {str(e)}")
    
    def _handle_version_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle version updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            model_id = event_data.get("model_id")
            version_id = event_data.get("version_id")
            version_data = event_data.get("version_data")
            
            # Validate required fields
            if not model_id:
                self.logger.warning("Received version updated event without model_id")
                return
            
            if not version_id:
                self.logger.warning(f"Received version updated event for model {model_id} without version_id")
                return
            
            if not version_data:
                self.logger.warning(f"Received version updated event for model {model_id} version {version_id} without version_data")
                return
            
            # Update version if it exists
            version_key = f"{model_id}:{version_id}"
            if version_key in self._model_versions:
                self._model_versions[version_key].update(version_data)
                self.logger.info(f"Updated model {model_id} version {version_id} from event")
        except Exception as e:
            self.logger.error(f"Error handling version updated event: {str(e)}")
    
    def _handle_artifact_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle artifact updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            model_id = event_data.get("model_id")
            version_id = event_data.get("version_id")
            artifact_id = event_data.get("artifact_id")
            artifact_data = event_data.get("artifact_data")
            
            # Validate required fields
            if not model_id:
                self.logger.warning("Received artifact updated event without model_id")
                return
            
            if not version_id:
                self.logger.warning(f"Received artifact updated event for model {model_id} without version_id")
                return
            
            if not artifact_id:
                self.logger.warning(f"Received artifact updated event for model {model_id} version {version_id} without artifact_id")
                return
            
            if not artifact_data:
                self.logger.warning(f"Received artifact updated event for model {model_id} version {version_id} artifact {artifact_id} without artifact_data")
                return
            
            # Update artifact if it exists
            artifact_key = f"{model_id}:{version_id}:{artifact_id}"
            if artifact_key in self._model_artifacts:
                self._model_artifacts[artifact_key].update(artifact_data)
                self.logger.info(f"Updated model {model_id} version {version_id} artifact {artifact_id} from event")
        except Exception as e:
            self.logger.error(f"Error handling artifact updated event: {str(e)}")
    
    def _handle_deployment_updated_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle deployment updated event.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract event data
            model_id = event_data.get("model_id")
            deployment_id = event_data.get("deployment_id")
            deployment_data = event_data.get("deployment_data")
            
            # Validate required fields
            if not model_id:
                self.logger.warning("Received deployment updated event without model_id")
                return
            
            if not deployment_id:
                self.logger.warning(f"Received deployment updated event for model {model_id} without deployment_id")
                return
            
            if not deployment_data:
                self.logger.warning(f"Received deployment updated event for model {model_id} deployment {deployment_id} without deployment_data")
                return
            
            # Update deployment if it exists
            deployment_key = f"{model_id}:{deployment_id}"
            if deployment_key in self._model_deployments:
                self._model_deployments[deployment_key].update(deployment_data)
                self.logger.info(f"Updated model {model_id} deployment {deployment_id} from event")
        except Exception as e:
            self.logger.error(f"Error handling deployment updated event: {str(e)}")
    
    def _register_model(self, model_id: str, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a model.
        
        Args:
            model_id: Model ID
            model_data: Model data
        
        Returns:
            Model data
        """
        try:
            # Check if model already exists
            if model_id in self._models:
                self.logger.warning(f"Model {model_id} already exists, updating instead")
                return self._update_model(model_id, model_data)
            
            # Create model data
            model_data_with_metadata = {
                "id": model_id,
                "name": model_data.get("name", model_id),
                "description": model_data.get("description", ""),
                "type": model_data.get("type", "unknown"),
                "tags": model_data.get("tags", []),
                "metadata": model_data.get("metadata", {}),
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Store model data
            self._models[model_id] = model_data_with_metadata
            
            # Publish model updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.model_updated",
                data={
                    "model_id": model_id,
                    "model_data": model_data_with_metadata,
                    "action": "registered"
                }
            )
            
            # Update metrics
            self._metrics["total_model_registrations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Registered model {model_id}")
            
            return model_data_with_metadata
        except Exception as e:
            self.logger.error(f"Error registering model {model_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _update_model(self, model_id: str, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model.
        
        Args:
            model_id: Model ID
            model_data: Model data
        
        Returns:
            Model data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Get current model data
            current_model_data = self._models[model_id]
            
            # Update model data
            updated_model_data = {
                **current_model_data,
                "name": model_data.get("name", current_model_data.get("name")),
                "description": model_data.get("description", current_model_data.get("description")),
                "type": model_data.get("type", current_model_data.get("type")),
                "tags": model_data.get("tags", current_model_data.get("tags")),
                "metadata": {
                    **current_model_data.get("metadata", {}),
                    **model_data.get("metadata", {})
                },
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Store updated model data
            self._models[model_id] = updated_model_data
            
            # Publish model updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.model_updated",
                data={
                    "model_id": model_id,
                    "model_data": updated_model_data,
                    "action": "updated"
                }
            )
            
            self.logger.info(f"Updated model {model_id}")
            
            return updated_model_data
        except Exception as e:
            self.logger.error(f"Error updating model {model_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _unregister_model(self, model_id: str) -> Dict[str, Any]:
        """
        Unregister a model.
        
        Args:
            model_id: Model ID
        
        Returns:
            Model data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Get model data
            model_data = self._models[model_id]
            
            # Delete all model versions
            for version_id in self._get_model_versions(model_id):
                self._delete_model_version(model_id, version_id)
            
            # Delete all model deployments
            for deployment_id in self._get_model_deployments(model_id):
                self._delete_model_deployment(model_id, deployment_id)
            
            # Delete model
            del self._models[model_id]
            
            # Publish model updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.model_updated",
                data={
                    "model_id": model_id,
                    "model_data": model_data,
                    "action": "unregistered"
                }
            )
            
            self.logger.info(f"Unregistered model {model_id}")
            
            return model_data
        except Exception as e:
            self.logger.error(f"Error unregistering model {model_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _create_model_version(self, model_id: str, version_id: str, version_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a model version.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            version_data: Version data
        
        Returns:
            Version data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version already exists
            version_key = f"{model_id}:{version_id}"
            if version_key in self._model_versions:
                self.logger.warning(f"Model {model_id} version {version_id} already exists, updating instead")
                return self._update_model_version(model_id, version_id, version_data)
            
            # Create version data
            version_data_with_metadata = {
                "id": version_id,
                "model_id": model_id,
                "version": version_data.get("version", "1.0.0"),
                "description": version_data.get("description", ""),
                "source": version_data.get("source", ""),
                "metrics": version_data.get("metrics", {}),
                "metadata": version_data.get("metadata", {}),
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Store version data
            self._model_versions[version_key] = version_data_with_metadata
            
            # Publish version updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.version_updated",
                data={
                    "model_id": model_id,
                    "version_id": version_id,
                    "version_data": version_data_with_metadata,
                    "action": "created"
                }
            )
            
            self.logger.info(f"Created model {model_id} version {version_id}")
            
            return version_data_with_metadata
        except Exception as e:
            self.logger.error(f"Error creating model {model_id} version {version_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _update_model_version(self, model_id: str, version_id: str, version_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model version.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            version_data: Version data
        
        Returns:
            Version data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Get current version data
            current_version_data = self._model_versions[version_key]
            
            # Update version data
            updated_version_data = {
                **current_version_data,
                "version": version_data.get("version", current_version_data.get("version")),
                "description": version_data.get("description", current_version_data.get("description")),
                "source": version_data.get("source", current_version_data.get("source")),
                "metrics": {
                    **current_version_data.get("metrics", {}),
                    **version_data.get("metrics", {})
                },
                "metadata": {
                    **current_version_data.get("metadata", {}),
                    **version_data.get("metadata", {})
                },
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Store updated version data
            self._model_versions[version_key] = updated_version_data
            
            # Publish version updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.version_updated",
                data={
                    "model_id": model_id,
                    "version_id": version_id,
                    "version_data": updated_version_data,
                    "action": "updated"
                }
            )
            
            self.logger.info(f"Updated model {model_id} version {version_id}")
            
            return updated_version_data
        except Exception as e:
            self.logger.error(f"Error updating model {model_id} version {version_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _delete_model_version(self, model_id: str, version_id: str) -> Dict[str, Any]:
        """
        Delete a model version.
        
        Args:
            model_id: Model ID
            version_id: Version ID
        
        Returns:
            Version data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Get version data
            version_data = self._model_versions[version_key]
            
            # Delete all version artifacts
            for artifact_id in self._get_version_artifacts(model_id, version_id):
                self._delete_model_artifact(model_id, version_id, artifact_id)
            
            # Delete version
            del self._model_versions[version_key]
            
            # Publish version updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.version_updated",
                data={
                    "model_id": model_id,
                    "version_id": version_id,
                    "version_data": version_data,
                    "action": "deleted"
                }
            )
            
            self.logger.info(f"Deleted model {model_id} version {version_id}")
            
            return version_data
        except Exception as e:
            self.logger.error(f"Error deleting model {model_id} version {version_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _upload_model_artifact(self, model_id: str, version_id: str, artifact_id: str, artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload a model artifact.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            artifact_id: Artifact ID
            artifact_data: Artifact data
        
        Returns:
            Artifact data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Check if artifact already exists
            artifact_key = f"{model_id}:{version_id}:{artifact_id}"
            if artifact_key in self._model_artifacts:
                self.logger.warning(f"Model {model_id} version {version_id} artifact {artifact_id} already exists, updating instead")
                return self._update_model_artifact(model_id, version_id, artifact_id, artifact_data)
            
            # Create artifact data
            artifact_data_with_metadata = {
                "id": artifact_id,
                "model_id": model_id,
                "version_id": version_id,
                "name": artifact_data.get("name", artifact_id),
                "description": artifact_data.get("description", ""),
                "type": artifact_data.get("type", "unknown"),
                "size": artifact_data.get("size", 0),
                "uri": artifact_data.get("uri", ""),
                "metadata": artifact_data.get("metadata", {}),
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Store artifact data
            self._model_artifacts[artifact_key] = artifact_data_with_metadata
            
            # Publish artifact updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.artifact_updated",
                data={
                    "model_id": model_id,
                    "version_id": version_id,
                    "artifact_id": artifact_id,
                    "artifact_data": artifact_data_with_metadata,
                    "action": "uploaded"
                }
            )
            
            self.logger.info(f"Uploaded model {model_id} version {version_id} artifact {artifact_id}")
            
            return artifact_data_with_metadata
        except Exception as e:
            self.logger.error(f"Error uploading model {model_id} version {version_id} artifact {artifact_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _update_model_artifact(self, model_id: str, version_id: str, artifact_id: str, artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model artifact.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            artifact_id: Artifact ID
            artifact_data: Artifact data
        
        Returns:
            Artifact data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Check if artifact exists
            artifact_key = f"{model_id}:{version_id}:{artifact_id}"
            if artifact_key not in self._model_artifacts:
                raise ValueError(f"Model {model_id} version {version_id} artifact {artifact_id} does not exist")
            
            # Get current artifact data
            current_artifact_data = self._model_artifacts[artifact_key]
            
            # Update artifact data
            updated_artifact_data = {
                **current_artifact_data,
                "name": artifact_data.get("name", current_artifact_data.get("name")),
                "description": artifact_data.get("description", current_artifact_data.get("description")),
                "type": artifact_data.get("type", current_artifact_data.get("type")),
                "size": artifact_data.get("size", current_artifact_data.get("size")),
                "uri": artifact_data.get("uri", current_artifact_data.get("uri")),
                "metadata": {
                    **current_artifact_data.get("metadata", {}),
                    **artifact_data.get("metadata", {})
                },
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Store updated artifact data
            self._model_artifacts[artifact_key] = updated_artifact_data
            
            # Publish artifact updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.artifact_updated",
                data={
                    "model_id": model_id,
                    "version_id": version_id,
                    "artifact_id": artifact_id,
                    "artifact_data": updated_artifact_data,
                    "action": "updated"
                }
            )
            
            self.logger.info(f"Updated model {model_id} version {version_id} artifact {artifact_id}")
            
            return updated_artifact_data
        except Exception as e:
            self.logger.error(f"Error updating model {model_id} version {version_id} artifact {artifact_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _delete_model_artifact(self, model_id: str, version_id: str, artifact_id: str) -> Dict[str, Any]:
        """
        Delete a model artifact.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            artifact_id: Artifact ID
        
        Returns:
            Artifact data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Check if artifact exists
            artifact_key = f"{model_id}:{version_id}:{artifact_id}"
            if artifact_key not in self._model_artifacts:
                raise ValueError(f"Model {model_id} version {version_id} artifact {artifact_id} does not exist")
            
            # Get artifact data
            artifact_data = self._model_artifacts[artifact_key]
            
            # Delete artifact
            del self._model_artifacts[artifact_key]
            
            # Publish artifact updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.artifact_updated",
                data={
                    "model_id": model_id,
                    "version_id": version_id,
                    "artifact_id": artifact_id,
                    "artifact_data": artifact_data,
                    "action": "deleted"
                }
            )
            
            self.logger.info(f"Deleted model {model_id} version {version_id} artifact {artifact_id}")
            
            return artifact_data
        except Exception as e:
            self.logger.error(f"Error deleting model {model_id} version {version_id} artifact {artifact_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _create_model_deployment(self, model_id: str, version_id: str, deployment_id: str, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a model deployment.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            deployment_id: Deployment ID
            deployment_data: Deployment data
        
        Returns:
            Deployment data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Check if deployment already exists
            deployment_key = f"{model_id}:{deployment_id}"
            if deployment_key in self._model_deployments:
                self.logger.warning(f"Model {model_id} deployment {deployment_id} already exists, updating instead")
                return self._update_model_deployment(model_id, deployment_id, deployment_data)
            
            # Create deployment data
            deployment_data_with_metadata = {
                "id": deployment_id,
                "model_id": model_id,
                "version_id": version_id,
                "name": deployment_data.get("name", deployment_id),
                "description": deployment_data.get("description", ""),
                "environment": deployment_data.get("environment", "production"),
                "status": deployment_data.get("status", "pending"),
                "endpoint": deployment_data.get("endpoint", ""),
                "metadata": deployment_data.get("metadata", {}),
                "created_at": self.data_access.get_current_timestamp(),
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Store deployment data
            self._model_deployments[deployment_key] = deployment_data_with_metadata
            
            # Publish deployment updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.deployment_updated",
                data={
                    "model_id": model_id,
                    "deployment_id": deployment_id,
                    "deployment_data": deployment_data_with_metadata,
                    "action": "created"
                }
            )
            
            # Update metrics
            self._metrics["total_model_deployments"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            self.logger.info(f"Created model {model_id} deployment {deployment_id}")
            
            return deployment_data_with_metadata
        except Exception as e:
            self.logger.error(f"Error creating model {model_id} deployment {deployment_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _update_model_deployment(self, model_id: str, deployment_id: str, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model deployment.
        
        Args:
            model_id: Model ID
            deployment_id: Deployment ID
            deployment_data: Deployment data
        
        Returns:
            Deployment data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if deployment exists
            deployment_key = f"{model_id}:{deployment_id}"
            if deployment_key not in self._model_deployments:
                raise ValueError(f"Model {model_id} deployment {deployment_id} does not exist")
            
            # Get current deployment data
            current_deployment_data = self._model_deployments[deployment_key]
            
            # Update deployment data
            updated_deployment_data = {
                **current_deployment_data,
                "name": deployment_data.get("name", current_deployment_data.get("name")),
                "description": deployment_data.get("description", current_deployment_data.get("description")),
                "environment": deployment_data.get("environment", current_deployment_data.get("environment")),
                "status": deployment_data.get("status", current_deployment_data.get("status")),
                "endpoint": deployment_data.get("endpoint", current_deployment_data.get("endpoint")),
                "metadata": {
                    **current_deployment_data.get("metadata", {}),
                    **deployment_data.get("metadata", {})
                },
                "updated_at": self.data_access.get_current_timestamp()
            }
            
            # Store updated deployment data
            self._model_deployments[deployment_key] = updated_deployment_data
            
            # Publish deployment updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.deployment_updated",
                data={
                    "model_id": model_id,
                    "deployment_id": deployment_id,
                    "deployment_data": updated_deployment_data,
                    "action": "updated"
                }
            )
            
            self.logger.info(f"Updated model {model_id} deployment {deployment_id}")
            
            return updated_deployment_data
        except Exception as e:
            self.logger.error(f"Error updating model {model_id} deployment {deployment_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _delete_model_deployment(self, model_id: str, deployment_id: str) -> Dict[str, Any]:
        """
        Delete a model deployment.
        
        Args:
            model_id: Model ID
            deployment_id: Deployment ID
        
        Returns:
            Deployment data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if deployment exists
            deployment_key = f"{model_id}:{deployment_id}"
            if deployment_key not in self._model_deployments:
                raise ValueError(f"Model {model_id} deployment {deployment_id} does not exist")
            
            # Get deployment data
            deployment_data = self._model_deployments[deployment_key]
            
            # Delete deployment
            del self._model_deployments[deployment_key]
            
            # Publish deployment updated event
            self.event_bus.publish(
                topic="core_ai_layer.model_registry.deployment_updated",
                data={
                    "model_id": model_id,
                    "deployment_id": deployment_id,
                    "deployment_data": deployment_data,
                    "action": "deleted"
                }
            )
            
            self.logger.info(f"Deleted model {model_id} deployment {deployment_id}")
            
            return deployment_data
        except Exception as e:
            self.logger.error(f"Error deleting model {model_id} deployment {deployment_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _get_model_versions(self, model_id: str) -> List[str]:
        """
        Get all version IDs for a model.
        
        Args:
            model_id: Model ID
        
        Returns:
            List of version IDs
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Get all version IDs for the model
            version_ids = []
            for version_key in self._model_versions.keys():
                if version_key.startswith(f"{model_id}:"):
                    version_id = version_key.split(":", 1)[1]
                    version_ids.append(version_id)
            
            return version_ids
        except Exception as e:
            self.logger.error(f"Error getting model {model_id} versions: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _get_version_artifacts(self, model_id: str, version_id: str) -> List[str]:
        """
        Get all artifact IDs for a model version.
        
        Args:
            model_id: Model ID
            version_id: Version ID
        
        Returns:
            List of artifact IDs
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Get all artifact IDs for the model version
            artifact_ids = []
            for artifact_key in self._model_artifacts.keys():
                if artifact_key.startswith(f"{model_id}:{version_id}:"):
                    artifact_id = artifact_key.split(":", 2)[2]
                    artifact_ids.append(artifact_id)
            
            return artifact_ids
        except Exception as e:
            self.logger.error(f"Error getting model {model_id} version {version_id} artifacts: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _get_model_deployments(self, model_id: str) -> List[str]:
        """
        Get all deployment IDs for a model.
        
        Args:
            model_id: Model ID
        
        Returns:
            List of deployment IDs
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Get all deployment IDs for the model
            deployment_ids = []
            for deployment_key in self._model_deployments.keys():
                if deployment_key.startswith(f"{model_id}:"):
                    deployment_id = deployment_key.split(":", 1)[1]
                    deployment_ids.append(deployment_id)
            
            return deployment_ids
        except Exception as e:
            self.logger.error(f"Error getting model {model_id} deployments: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def _get_latest_model_version(self, model_id: str) -> Optional[str]:
        """
        Get the latest version ID for a model.
        
        Args:
            model_id: Model ID
        
        Returns:
            Latest version ID or None if no versions exist
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Get all version IDs for the model
            version_ids = self._get_model_versions(model_id)
            
            if not version_ids:
                return None
            
            # Get all version data for the model
            versions = []
            for version_id in version_ids:
                version_key = f"{model_id}:{version_id}"
                version_data = self._model_versions[version_key]
                versions.append(version_data)
            
            # Sort versions by created_at timestamp (descending)
            versions.sort(key=lambda v: v.get("created_at", 0), reverse=True)
            
            # Return the latest version ID
            return versions[0]["id"]
        except Exception as e:
            self.logger.error(f"Error getting latest model {model_id} version: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def register_model(self, model_id: str, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a model.
        
        Args:
            model_id: Model ID
            model_data: Model data
        
        Returns:
            Model data
        """
        return self._register_model(model_id, model_data)
    
    def update_model(self, model_id: str, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model.
        
        Args:
            model_id: Model ID
            model_data: Model data
        
        Returns:
            Model data
        """
        return self._update_model(model_id, model_data)
    
    def unregister_model(self, model_id: str) -> Dict[str, Any]:
        """
        Unregister a model.
        
        Args:
            model_id: Model ID
        
        Returns:
            Model data
        """
        return self._unregister_model(model_id)
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get a model.
        
        Args:
            model_id: Model ID
        
        Returns:
            Model data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Get model data
            model_data = self._models[model_id]
            
            # Update metrics
            self._metrics["total_model_retrievals"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return model_data
        except Exception as e:
            self.logger.error(f"Error getting model {model_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all models.
        
        Returns:
            List of model data
        """
        try:
            # Get all model data
            model_data_list = list(self._models.values())
            
            # Update metrics
            self._metrics["total_model_retrievals"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return model_data_list
        except Exception as e:
            self.logger.error(f"Error listing models: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def create_model_version(self, model_id: str, version_id: str, version_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a model version.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            version_data: Version data
        
        Returns:
            Version data
        """
        return self._create_model_version(model_id, version_id, version_data)
    
    def update_model_version(self, model_id: str, version_id: str, version_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model version.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            version_data: Version data
        
        Returns:
            Version data
        """
        return self._update_model_version(model_id, version_id, version_data)
    
    def delete_model_version(self, model_id: str, version_id: str) -> Dict[str, Any]:
        """
        Delete a model version.
        
        Args:
            model_id: Model ID
            version_id: Version ID
        
        Returns:
            Version data
        """
        return self._delete_model_version(model_id, version_id)
    
    def get_model_version(self, model_id: str, version_id: str) -> Dict[str, Any]:
        """
        Get a model version.
        
        Args:
            model_id: Model ID
            version_id: Version ID
        
        Returns:
            Version data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Get version data
            version_data = self._model_versions[version_key]
            
            return version_data
        except Exception as e:
            self.logger.error(f"Error getting model {model_id} version {version_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_model_versions(self, model_id: str) -> List[Dict[str, Any]]:
        """
        List all versions for a model.
        
        Args:
            model_id: Model ID
        
        Returns:
            List of version data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Get all version IDs for the model
            version_ids = self._get_model_versions(model_id)
            
            # Get all version data for the model
            version_data_list = []
            for version_id in version_ids:
                version_key = f"{model_id}:{version_id}"
                version_data = self._model_versions[version_key]
                version_data_list.append(version_data)
            
            return version_data_list
        except Exception as e:
            self.logger.error(f"Error listing model {model_id} versions: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_latest_model_version(self, model_id: str) -> Dict[str, Any]:
        """
        Get the latest version for a model.
        
        Args:
            model_id: Model ID
        
        Returns:
            Latest version data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Get the latest version ID
            version_id = self._get_latest_model_version(model_id)
            
            if not version_id:
                raise ValueError(f"Model {model_id} has no versions")
            
            # Get the latest version data
            version_key = f"{model_id}:{version_id}"
            version_data = self._model_versions[version_key]
            
            return version_data
        except Exception as e:
            self.logger.error(f"Error getting latest model {model_id} version: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def upload_model_artifact(self, model_id: str, version_id: str, artifact_id: str, artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload a model artifact.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            artifact_id: Artifact ID
            artifact_data: Artifact data
        
        Returns:
            Artifact data
        """
        return self._upload_model_artifact(model_id, version_id, artifact_id, artifact_data)
    
    def download_model_artifact(self, model_id: str, version_id: str, artifact_id: str) -> Dict[str, Any]:
        """
        Download a model artifact.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            artifact_id: Artifact ID
        
        Returns:
            Artifact data with content
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Check if artifact exists
            artifact_key = f"{model_id}:{version_id}:{artifact_id}"
            if artifact_key not in self._model_artifacts:
                raise ValueError(f"Model {model_id} version {version_id} artifact {artifact_id} does not exist")
            
            # Get artifact data
            artifact_data = self._model_artifacts[artifact_key]
            
            # Simulate downloading artifact content
            # In a real implementation, this would involve downloading the artifact from storage
            artifact_data_with_content = {
                **artifact_data,
                "content": "Simulated artifact content"
            }
            
            return artifact_data_with_content
        except Exception as e:
            self.logger.error(f"Error downloading model {model_id} version {version_id} artifact {artifact_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def delete_model_artifact(self, model_id: str, version_id: str, artifact_id: str) -> Dict[str, Any]:
        """
        Delete a model artifact.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            artifact_id: Artifact ID
        
        Returns:
            Artifact data
        """
        return self._delete_model_artifact(model_id, version_id, artifact_id)
    
    def get_model_artifact(self, model_id: str, version_id: str, artifact_id: str) -> Dict[str, Any]:
        """
        Get a model artifact.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            artifact_id: Artifact ID
        
        Returns:
            Artifact data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Check if artifact exists
            artifact_key = f"{model_id}:{version_id}:{artifact_id}"
            if artifact_key not in self._model_artifacts:
                raise ValueError(f"Model {model_id} version {version_id} artifact {artifact_id} does not exist")
            
            # Get artifact data
            artifact_data = self._model_artifacts[artifact_key]
            
            return artifact_data
        except Exception as e:
            self.logger.error(f"Error getting model {model_id} version {version_id} artifact {artifact_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_model_artifacts(self, model_id: str, version_id: str) -> List[Dict[str, Any]]:
        """
        List all artifacts for a model version.
        
        Args:
            model_id: Model ID
            version_id: Version ID
        
        Returns:
            List of artifact data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if version exists
            version_key = f"{model_id}:{version_id}"
            if version_key not in self._model_versions:
                raise ValueError(f"Model {model_id} version {version_id} does not exist")
            
            # Get all artifact IDs for the model version
            artifact_ids = self._get_version_artifacts(model_id, version_id)
            
            # Get all artifact data for the model version
            artifact_data_list = []
            for artifact_id in artifact_ids:
                artifact_key = f"{model_id}:{version_id}:{artifact_id}"
                artifact_data = self._model_artifacts[artifact_key]
                artifact_data_list.append(artifact_data)
            
            return artifact_data_list
        except Exception as e:
            self.logger.error(f"Error listing model {model_id} version {version_id} artifacts: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def create_model_deployment(self, model_id: str, version_id: str, deployment_id: str, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a model deployment.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            deployment_id: Deployment ID
            deployment_data: Deployment data
        
        Returns:
            Deployment data
        """
        return self._create_model_deployment(model_id, version_id, deployment_id, deployment_data)
    
    def update_model_deployment(self, model_id: str, deployment_id: str, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model deployment.
        
        Args:
            model_id: Model ID
            deployment_id: Deployment ID
            deployment_data: Deployment data
        
        Returns:
            Deployment data
        """
        return self._update_model_deployment(model_id, deployment_id, deployment_data)
    
    def delete_model_deployment(self, model_id: str, deployment_id: str) -> Dict[str, Any]:
        """
        Delete a model deployment.
        
        Args:
            model_id: Model ID
            deployment_id: Deployment ID
        
        Returns:
            Deployment data
        """
        return self._delete_model_deployment(model_id, deployment_id)
    
    def get_model_deployment(self, model_id: str, deployment_id: str) -> Dict[str, Any]:
        """
        Get a model deployment.
        
        Args:
            model_id: Model ID
            deployment_id: Deployment ID
        
        Returns:
            Deployment data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Check if deployment exists
            deployment_key = f"{model_id}:{deployment_id}"
            if deployment_key not in self._model_deployments:
                raise ValueError(f"Model {model_id} deployment {deployment_id} does not exist")
            
            # Get deployment data
            deployment_data = self._model_deployments[deployment_key]
            
            return deployment_data
        except Exception as e:
            self.logger.error(f"Error getting model {model_id} deployment {deployment_id}: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def list_model_deployments(self, model_id: str) -> List[Dict[str, Any]]:
        """
        List all deployments for a model.
        
        Args:
            model_id: Model ID
        
        Returns:
            List of deployment data
        """
        try:
            # Check if model exists
            if model_id not in self._models:
                raise ValueError(f"Model {model_id} does not exist")
            
            # Get all deployment IDs for the model
            deployment_ids = self._get_model_deployments(model_id)
            
            # Get all deployment data for the model
            deployment_data_list = []
            for deployment_id in deployment_ids:
                deployment_key = f"{model_id}:{deployment_id}"
                deployment_data = self._model_deployments[deployment_key]
                deployment_data_list.append(deployment_data)
            
            return deployment_data_list
        except Exception as e:
            self.logger.error(f"Error listing model {model_id} deployments: {str(e)}")
            self._metrics["total_errors"] += 1
            raise
    
    def get_status(self) -> str:
        """
        Get the adapter status.
        
        Returns:
            Adapter status
        """
        return self._check_resource_health()
    
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
            "total_model_registrations": 0,
            "total_model_retrievals": 0,
            "total_model_deployments": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        return self._metrics
