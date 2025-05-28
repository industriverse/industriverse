"""
Core AI Layer Integration Manager for the Overseer System.

This module provides the integration manager for Core AI Layer components
of the Industriverse Framework, enabling seamless integration with
LLMs, VQ-VAE models, and other Core AI components.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Callable

from src.integration.integration_manager import BaseIntegrationManager
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

# Import Core AI Layer adapters
from src.integration.core_ai_layer.llm_adapter import LLMAdapter
from src.integration.core_ai_layer.vq_vae_adapter import VQVAEAdapter
from src.integration.core_ai_layer.model_registry_adapter import ModelRegistryAdapter
from src.integration.core_ai_layer.inference_engine_adapter import InferenceEngineAdapter
from src.integration.core_ai_layer.training_pipeline_adapter import TrainingPipelineAdapter

class CoreAILayerIntegrationManager(BaseIntegrationManager):
    """
    Integration Manager for Core AI Layer components of the Industriverse Framework.
    
    This class manages the integration with Core AI Layer components, including
    LLMs, VQ-VAE models, model registry, inference engines, and training pipelines.
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
        Initialize the Core AI Layer Integration Manager.
        
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
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            config=config,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize Core AI Layer specific resources
        self._llm_adapters = {}
        self._vq_vae_adapters = {}
        self._model_registry_adapters = {}
        self._inference_engine_adapters = {}
        self._training_pipeline_adapters = {}
        
        # Initialize metrics
        self._metrics = {
            "total_llm_requests": 0,
            "total_vq_vae_requests": 0,
            "total_model_registry_operations": 0,
            "total_inference_requests": 0,
            "total_training_jobs": 0,
            "total_errors": 0,
            "last_operation_timestamp": None
        }
        
        self.logger.info(f"Core AI Layer Integration Manager {manager_id} initialized")
    
    def _get_supported_context_types(self) -> List[str]:
        """
        Get the MCP context types supported by this manager.
        
        Returns:
            List of supported context types
        """
        return [
            "core_ai_layer",
            "core_ai_layer.llm",
            "core_ai_layer.vq_vae",
            "core_ai_layer.model_registry",
            "core_ai_layer.inference_engine",
            "core_ai_layer.training_pipeline"
        ]
    
    def _get_supported_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the A2A capabilities supported by this manager.
        
        Returns:
            List of supported capabilities
        """
        return [
            {
                "type": "core_ai_management",
                "description": "Manage Core AI Layer components",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "component_type": {
                        "type": "string",
                        "description": "Type of component (llm, vq_vae, model_registry, inference_engine, training_pipeline)"
                    },
                    "component_id": {
                        "type": "string",
                        "description": "ID of the component"
                    },
                    "component_config": {
                        "type": "object",
                        "description": "Configuration for the component"
                    }
                }
            },
            {
                "type": "llm_inference",
                "description": "Perform inference with LLM models",
                "parameters": {
                    "model_id": {
                        "type": "string",
                        "description": "ID of the LLM model"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Prompt for the LLM"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Inference parameters"
                    }
                }
            },
            {
                "type": "vq_vae_inference",
                "description": "Perform inference with VQ-VAE models",
                "parameters": {
                    "model_id": {
                        "type": "string",
                        "description": "ID of the VQ-VAE model"
                    },
                    "input_data": {
                        "type": "object",
                        "description": "Input data for the VQ-VAE"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Inference parameters"
                    }
                }
            },
            {
                "type": "model_registry_operation",
                "description": "Perform operations on the model registry",
                "parameters": {
                    "operation": {
                        "type": "string",
                        "description": "Operation to perform (register, update, delete, list, get)"
                    },
                    "model_id": {
                        "type": "string",
                        "description": "ID of the model"
                    },
                    "model_data": {
                        "type": "object",
                        "description": "Model data"
                    }
                }
            },
            {
                "type": "training_job_management",
                "description": "Manage training jobs",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list, get)"
                    },
                    "job_id": {
                        "type": "string",
                        "description": "ID of the training job"
                    },
                    "job_config": {
                        "type": "object",
                        "description": "Configuration for the training job"
                    }
                }
            }
        ]
    
    def _initialize_resources(self) -> None:
        """Initialize manager-specific resources."""
        try:
            # Create LLM adapters
            llm_adapters_config = self.config.get("llm_adapters", {})
            for adapter_id, adapter_config in llm_adapters_config.items():
                self._create_llm_adapter(adapter_id, adapter_config)
            
            # Create VQ-VAE adapters
            vq_vae_adapters_config = self.config.get("vq_vae_adapters", {})
            for adapter_id, adapter_config in vq_vae_adapters_config.items():
                self._create_vq_vae_adapter(adapter_id, adapter_config)
            
            # Create model registry adapters
            model_registry_adapters_config = self.config.get("model_registry_adapters", {})
            for adapter_id, adapter_config in model_registry_adapters_config.items():
                self._create_model_registry_adapter(adapter_id, adapter_config)
            
            # Create inference engine adapters
            inference_engine_adapters_config = self.config.get("inference_engine_adapters", {})
            for adapter_id, adapter_config in inference_engine_adapters_config.items():
                self._create_inference_engine_adapter(adapter_id, adapter_config)
            
            # Create training pipeline adapters
            training_pipeline_adapters_config = self.config.get("training_pipeline_adapters", {})
            for adapter_id, adapter_config in training_pipeline_adapters_config.items():
                self._create_training_pipeline_adapter(adapter_id, adapter_config)
            
            self.logger.info(f"Initialized resources for Core AI Layer Integration Manager {self.manager_id}")
        except Exception as e:
            self.logger.error(f"Error initializing resources for Core AI Layer Integration Manager {self.manager_id}: {str(e)}")
            raise
    
    def _start_resources(self) -> None:
        """Start manager-specific resources."""
        try:
            # Start LLM adapters
            for adapter_id, adapter in self._llm_adapters.items():
                adapter.start()
            
            # Start VQ-VAE adapters
            for adapter_id, adapter in self._vq_vae_adapters.items():
                adapter.start()
            
            # Start model registry adapters
            for adapter_id, adapter in self._model_registry_adapters.items():
                adapter.start()
            
            # Start inference engine adapters
            for adapter_id, adapter in self._inference_engine_adapters.items():
                adapter.start()
            
            # Start training pipeline adapters
            for adapter_id, adapter in self._training_pipeline_adapters.items():
                adapter.start()
            
            self.logger.info(f"Started resources for Core AI Layer Integration Manager {self.manager_id}")
        except Exception as e:
            self.logger.error(f"Error starting resources for Core AI Layer Integration Manager {self.manager_id}: {str(e)}")
            raise
    
    def _stop_resources(self) -> None:
        """Stop manager-specific resources."""
        try:
            # Stop LLM adapters
            for adapter_id, adapter in self._llm_adapters.items():
                adapter.stop()
            
            # Stop VQ-VAE adapters
            for adapter_id, adapter in self._vq_vae_adapters.items():
                adapter.stop()
            
            # Stop model registry adapters
            for adapter_id, adapter in self._model_registry_adapters.items():
                adapter.stop()
            
            # Stop inference engine adapters
            for adapter_id, adapter in self._inference_engine_adapters.items():
                adapter.stop()
            
            # Stop training pipeline adapters
            for adapter_id, adapter in self._training_pipeline_adapters.items():
                adapter.stop()
            
            self.logger.info(f"Stopped resources for Core AI Layer Integration Manager {self.manager_id}")
        except Exception as e:
            self.logger.error(f"Error stopping resources for Core AI Layer Integration Manager {self.manager_id}: {str(e)}")
            raise
    
    def _release_resources(self) -> None:
        """Release manager-specific resources."""
        try:
            # Release LLM adapters
            for adapter_id, adapter in self._llm_adapters.items():
                adapter.release()
            self._llm_adapters = {}
            
            # Release VQ-VAE adapters
            for adapter_id, adapter in self._vq_vae_adapters.items():
                adapter.release()
            self._vq_vae_adapters = {}
            
            # Release model registry adapters
            for adapter_id, adapter in self._model_registry_adapters.items():
                adapter.release()
            self._model_registry_adapters = {}
            
            # Release inference engine adapters
            for adapter_id, adapter in self._inference_engine_adapters.items():
                adapter.release()
            self._inference_engine_adapters = {}
            
            # Release training pipeline adapters
            for adapter_id, adapter in self._training_pipeline_adapters.items():
                adapter.release()
            self._training_pipeline_adapters = {}
            
            self.logger.info(f"Released resources for Core AI Layer Integration Manager {self.manager_id}")
        except Exception as e:
            self.logger.error(f"Error releasing resources for Core AI Layer Integration Manager {self.manager_id}: {str(e)}")
            raise
    
    def _check_resource_health(self) -> str:
        """
        Check the health of manager-specific resources.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        try:
            # Check LLM adapters
            llm_adapter_statuses = [adapter.check_health() for adapter in self._llm_adapters.values()]
            
            # Check VQ-VAE adapters
            vq_vae_adapter_statuses = [adapter.check_health() for adapter in self._vq_vae_adapters.values()]
            
            # Check model registry adapters
            model_registry_adapter_statuses = [adapter.check_health() for adapter in self._model_registry_adapters.values()]
            
            # Check inference engine adapters
            inference_engine_adapter_statuses = [adapter.check_health() for adapter in self._inference_engine_adapters.values()]
            
            # Check training pipeline adapters
            training_pipeline_adapter_statuses = [adapter.check_health() for adapter in self._training_pipeline_adapters.values()]
            
            # Combine all statuses
            all_statuses = (
                llm_adapter_statuses +
                vq_vae_adapter_statuses +
                model_registry_adapter_statuses +
                inference_engine_adapter_statuses +
                training_pipeline_adapter_statuses
            )
            
            # Determine overall health
            if not all_statuses:
                # No adapters, consider healthy
                return "healthy"
            
            if "unhealthy" in all_statuses:
                # At least one adapter is unhealthy
                return "unhealthy"
            
            if "degraded" in all_statuses:
                # At least one adapter is degraded
                return "degraded"
            
            # All adapters are healthy
            return "healthy"
        except Exception as e:
            self.logger.error(f"Error checking resource health for Core AI Layer Integration Manager {self.manager_id}: {str(e)}")
            return "unhealthy"
    
    def _apply_configuration(self) -> None:
        """Apply configuration changes."""
        try:
            # Apply LLM adapter configuration changes
            llm_adapters_config = self.config.get("llm_adapters", {})
            
            # Remove deleted LLM adapters
            for adapter_id in list(self._llm_adapters.keys()):
                if adapter_id not in llm_adapters_config:
                    self._delete_llm_adapter(adapter_id)
            
            # Add or update LLM adapters
            for adapter_id, adapter_config in llm_adapters_config.items():
                if adapter_id in self._llm_adapters:
                    self._update_llm_adapter(adapter_id, adapter_config)
                else:
                    self._create_llm_adapter(adapter_id, adapter_config)
            
            # Apply VQ-VAE adapter configuration changes
            vq_vae_adapters_config = self.config.get("vq_vae_adapters", {})
            
            # Remove deleted VQ-VAE adapters
            for adapter_id in list(self._vq_vae_adapters.keys()):
                if adapter_id not in vq_vae_adapters_config:
                    self._delete_vq_vae_adapter(adapter_id)
            
            # Add or update VQ-VAE adapters
            for adapter_id, adapter_config in vq_vae_adapters_config.items():
                if adapter_id in self._vq_vae_adapters:
                    self._update_vq_vae_adapter(adapter_id, adapter_config)
                else:
                    self._create_vq_vae_adapter(adapter_id, adapter_config)
            
            # Apply model registry adapter configuration changes
            model_registry_adapters_config = self.config.get("model_registry_adapters", {})
            
            # Remove deleted model registry adapters
            for adapter_id in list(self._model_registry_adapters.keys()):
                if adapter_id not in model_registry_adapters_config:
                    self._delete_model_registry_adapter(adapter_id)
            
            # Add or update model registry adapters
            for adapter_id, adapter_config in model_registry_adapters_config.items():
                if adapter_id in self._model_registry_adapters:
                    self._update_model_registry_adapter(adapter_id, adapter_config)
                else:
                    self._create_model_registry_adapter(adapter_id, adapter_config)
            
            # Apply inference engine adapter configuration changes
            inference_engine_adapters_config = self.config.get("inference_engine_adapters", {})
            
            # Remove deleted inference engine adapters
            for adapter_id in list(self._inference_engine_adapters.keys()):
                if adapter_id not in inference_engine_adapters_config:
                    self._delete_inference_engine_adapter(adapter_id)
            
            # Add or update inference engine adapters
            for adapter_id, adapter_config in inference_engine_adapters_config.items():
                if adapter_id in self._inference_engine_adapters:
                    self._update_inference_engine_adapter(adapter_id, adapter_config)
                else:
                    self._create_inference_engine_adapter(adapter_id, adapter_config)
            
            # Apply training pipeline adapter configuration changes
            training_pipeline_adapters_config = self.config.get("training_pipeline_adapters", {})
            
            # Remove deleted training pipeline adapters
            for adapter_id in list(self._training_pipeline_adapters.keys()):
                if adapter_id not in training_pipeline_adapters_config:
                    self._delete_training_pipeline_adapter(adapter_id)
            
            # Add or update training pipeline adapters
            for adapter_id, adapter_config in training_pipeline_adapters_config.items():
                if adapter_id in self._training_pipeline_adapters:
                    self._update_training_pipeline_adapter(adapter_id, adapter_config)
                else:
                    self._create_training_pipeline_adapter(adapter_id, adapter_config)
            
            self.logger.info(f"Applied configuration changes for Core AI Layer Integration Manager {self.manager_id}")
        except Exception as e:
            self.logger.error(f"Error applying configuration changes for Core AI Layer Integration Manager {self.manager_id}: {str(e)}")
            raise
    
    def _get_status_data(self) -> Dict[str, Any]:
        """
        Get manager-specific status data.
        
        Returns:
            Manager-specific status data
        """
        return {
            "llm_adapters": {
                adapter_id: {
                    "status": adapter.get_status(),
                    "model_count": len(adapter.get_models())
                }
                for adapter_id, adapter in self._llm_adapters.items()
            },
            "vq_vae_adapters": {
                adapter_id: {
                    "status": adapter.get_status(),
                    "model_count": len(adapter.get_models())
                }
                for adapter_id, adapter in self._vq_vae_adapters.items()
            },
            "model_registry_adapters": {
                adapter_id: {
                    "status": adapter.get_status(),
                    "model_count": adapter.get_model_count()
                }
                for adapter_id, adapter in self._model_registry_adapters.items()
            },
            "inference_engine_adapters": {
                adapter_id: {
                    "status": adapter.get_status(),
                    "active_sessions": adapter.get_active_session_count()
                }
                for adapter_id, adapter in self._inference_engine_adapters.items()
            },
            "training_pipeline_adapters": {
                adapter_id: {
                    "status": adapter.get_status(),
                    "active_jobs": adapter.get_active_job_count()
                }
                for adapter_id, adapter in self._training_pipeline_adapters.items()
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
        if command == "create_llm_adapter":
            adapter_id = event.get("adapter_id", str(uuid.uuid4()))
            adapter_config = event.get("adapter_config", {})
            self._create_llm_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "update_llm_adapter":
            adapter_id = event.get("adapter_id")
            adapter_config = event.get("adapter_config", {})
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._update_llm_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "delete_llm_adapter":
            adapter_id = event.get("adapter_id")
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._delete_llm_adapter(adapter_id)
            return {"adapter_id": adapter_id}
        
        elif command == "list_llm_adapters":
            return {
                "llm_adapters": {
                    adapter_id: {
                        "status": adapter.get_status(),
                        "model_count": len(adapter.get_models())
                    }
                    for adapter_id, adapter in self._llm_adapters.items()
                }
            }
        
        elif command == "create_vq_vae_adapter":
            adapter_id = event.get("adapter_id", str(uuid.uuid4()))
            adapter_config = event.get("adapter_config", {})
            self._create_vq_vae_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "update_vq_vae_adapter":
            adapter_id = event.get("adapter_id")
            adapter_config = event.get("adapter_config", {})
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._update_vq_vae_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "delete_vq_vae_adapter":
            adapter_id = event.get("adapter_id")
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._delete_vq_vae_adapter(adapter_id)
            return {"adapter_id": adapter_id}
        
        elif command == "list_vq_vae_adapters":
            return {
                "vq_vae_adapters": {
                    adapter_id: {
                        "status": adapter.get_status(),
                        "model_count": len(adapter.get_models())
                    }
                    for adapter_id, adapter in self._vq_vae_adapters.items()
                }
            }
        
        elif command == "create_model_registry_adapter":
            adapter_id = event.get("adapter_id", str(uuid.uuid4()))
            adapter_config = event.get("adapter_config", {})
            self._create_model_registry_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "update_model_registry_adapter":
            adapter_id = event.get("adapter_id")
            adapter_config = event.get("adapter_config", {})
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._update_model_registry_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "delete_model_registry_adapter":
            adapter_id = event.get("adapter_id")
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._delete_model_registry_adapter(adapter_id)
            return {"adapter_id": adapter_id}
        
        elif command == "list_model_registry_adapters":
            return {
                "model_registry_adapters": {
                    adapter_id: {
                        "status": adapter.get_status(),
                        "model_count": adapter.get_model_count()
                    }
                    for adapter_id, adapter in self._model_registry_adapters.items()
                }
            }
        
        elif command == "create_inference_engine_adapter":
            adapter_id = event.get("adapter_id", str(uuid.uuid4()))
            adapter_config = event.get("adapter_config", {})
            self._create_inference_engine_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "update_inference_engine_adapter":
            adapter_id = event.get("adapter_id")
            adapter_config = event.get("adapter_config", {})
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._update_inference_engine_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "delete_inference_engine_adapter":
            adapter_id = event.get("adapter_id")
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._delete_inference_engine_adapter(adapter_id)
            return {"adapter_id": adapter_id}
        
        elif command == "list_inference_engine_adapters":
            return {
                "inference_engine_adapters": {
                    adapter_id: {
                        "status": adapter.get_status(),
                        "active_sessions": adapter.get_active_session_count()
                    }
                    for adapter_id, adapter in self._inference_engine_adapters.items()
                }
            }
        
        elif command == "create_training_pipeline_adapter":
            adapter_id = event.get("adapter_id", str(uuid.uuid4()))
            adapter_config = event.get("adapter_config", {})
            self._create_training_pipeline_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "update_training_pipeline_adapter":
            adapter_id = event.get("adapter_id")
            adapter_config = event.get("adapter_config", {})
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._update_training_pipeline_adapter(adapter_id, adapter_config)
            return {"adapter_id": adapter_id}
        
        elif command == "delete_training_pipeline_adapter":
            adapter_id = event.get("adapter_id")
            if not adapter_id:
                raise ValueError("adapter_id is required")
            self._delete_training_pipeline_adapter(adapter_id)
            return {"adapter_id": adapter_id}
        
        elif command == "list_training_pipeline_adapters":
            return {
                "training_pipeline_adapters": {
                    adapter_id: {
                        "status": adapter.get_status(),
                        "active_jobs": adapter.get_active_job_count()
                    }
                    for adapter_id, adapter in self._training_pipeline_adapters.items()
                }
            }
        
        elif command == "llm_inference":
            adapter_id = event.get("adapter_id")
            model_id = event.get("model_id")
            prompt = event.get("prompt")
            parameters = event.get("parameters", {})
            
            if not adapter_id:
                # Find the first available LLM adapter
                if not self._llm_adapters:
                    raise ValueError("No LLM adapters available")
                adapter_id = next(iter(self._llm_adapters.keys()))
            
            if adapter_id not in self._llm_adapters:
                raise ValueError(f"LLM adapter {adapter_id} does not exist")
            
            if not model_id:
                raise ValueError("model_id is required")
            
            if not prompt:
                raise ValueError("prompt is required")
            
            # Perform LLM inference
            adapter = self._llm_adapters[adapter_id]
            result = adapter.perform_inference(model_id, prompt, parameters)
            
            # Update metrics
            self._metrics["total_llm_requests"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return {
                "adapter_id": adapter_id,
                "model_id": model_id,
                "result": result
            }
        
        elif command == "vq_vae_inference":
            adapter_id = event.get("adapter_id")
            model_id = event.get("model_id")
            input_data = event.get("input_data")
            parameters = event.get("parameters", {})
            
            if not adapter_id:
                # Find the first available VQ-VAE adapter
                if not self._vq_vae_adapters:
                    raise ValueError("No VQ-VAE adapters available")
                adapter_id = next(iter(self._vq_vae_adapters.keys()))
            
            if adapter_id not in self._vq_vae_adapters:
                raise ValueError(f"VQ-VAE adapter {adapter_id} does not exist")
            
            if not model_id:
                raise ValueError("model_id is required")
            
            if input_data is None:
                raise ValueError("input_data is required")
            
            # Perform VQ-VAE inference
            adapter = self._vq_vae_adapters[adapter_id]
            result = adapter.perform_inference(model_id, input_data, parameters)
            
            # Update metrics
            self._metrics["total_vq_vae_requests"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return {
                "adapter_id": adapter_id,
                "model_id": model_id,
                "result": result
            }
        
        elif command == "model_registry_operation":
            adapter_id = event.get("adapter_id")
            operation = event.get("operation")
            model_id = event.get("model_id")
            model_data = event.get("model_data")
            
            if not adapter_id:
                # Find the first available model registry adapter
                if not self._model_registry_adapters:
                    raise ValueError("No model registry adapters available")
                adapter_id = next(iter(self._model_registry_adapters.keys()))
            
            if adapter_id not in self._model_registry_adapters:
                raise ValueError(f"Model registry adapter {adapter_id} does not exist")
            
            if not operation:
                raise ValueError("operation is required")
            
            # Perform model registry operation
            adapter = self._model_registry_adapters[adapter_id]
            
            if operation == "register":
                if not model_id:
                    raise ValueError("model_id is required")
                if model_data is None:
                    raise ValueError("model_data is required")
                result = adapter.register_model(model_id, model_data)
            
            elif operation == "update":
                if not model_id:
                    raise ValueError("model_id is required")
                if model_data is None:
                    raise ValueError("model_data is required")
                result = adapter.update_model(model_id, model_data)
            
            elif operation == "delete":
                if not model_id:
                    raise ValueError("model_id is required")
                result = adapter.delete_model(model_id)
            
            elif operation == "list":
                result = adapter.list_models()
            
            elif operation == "get":
                if not model_id:
                    raise ValueError("model_id is required")
                result = adapter.get_model(model_id)
            
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Update metrics
            self._metrics["total_model_registry_operations"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return {
                "adapter_id": adapter_id,
                "operation": operation,
                "model_id": model_id,
                "result": result
            }
        
        elif command == "training_job_management":
            adapter_id = event.get("adapter_id")
            action = event.get("action")
            job_id = event.get("job_id")
            job_config = event.get("job_config")
            
            if not adapter_id:
                # Find the first available training pipeline adapter
                if not self._training_pipeline_adapters:
                    raise ValueError("No training pipeline adapters available")
                adapter_id = next(iter(self._training_pipeline_adapters.keys()))
            
            if adapter_id not in self._training_pipeline_adapters:
                raise ValueError(f"Training pipeline adapter {adapter_id} does not exist")
            
            if not action:
                raise ValueError("action is required")
            
            # Perform training job management action
            adapter = self._training_pipeline_adapters[adapter_id]
            
            if action == "create":
                if not job_config:
                    raise ValueError("job_config is required")
                job_id = job_id or str(uuid.uuid4())
                result = adapter.create_job(job_id, job_config)
            
            elif action == "update":
                if not job_id:
                    raise ValueError("job_id is required")
                if not job_config:
                    raise ValueError("job_config is required")
                result = adapter.update_job(job_id, job_config)
            
            elif action == "delete":
                if not job_id:
                    raise ValueError("job_id is required")
                result = adapter.delete_job(job_id)
            
            elif action == "list":
                result = adapter.list_jobs()
            
            elif action == "get":
                if not job_id:
                    raise ValueError("job_id is required")
                result = adapter.get_job(job_id)
            
            elif action == "start":
                if not job_id:
                    raise ValueError("job_id is required")
                result = adapter.start_job(job_id)
            
            elif action == "stop":
                if not job_id:
                    raise ValueError("job_id is required")
                result = adapter.stop_job(job_id)
            
            else:
                raise ValueError(f"Unsupported action: {action}")
            
            # Update metrics
            self._metrics["total_training_jobs"] += 1
            self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
            
            return {
                "adapter_id": adapter_id,
                "action": action,
                "job_id": job_id,
                "result": result
            }
        
        elif command == "get_metrics":
            return {"metrics": self._metrics}
        
        elif command == "reset_metrics":
            self._metrics = {
                "total_llm_requests": 0,
                "total_vq_vae_requests": 0,
                "total_model_registry_operations": 0,
                "total_inference_requests": 0,
                "total_training_jobs": 0,
                "total_errors": 0,
                "last_operation_timestamp": None
            }
            return {"metrics": self._metrics}
        
        else:
            raise ValueError(f"Unsupported command: {command}")
    
    def _create_llm_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Create a new LLM adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Create LLM adapter
            adapter = LLMAdapter(
                adapter_id=adapter_id,
                manager=self,
                mcp_bridge=self.mcp_bridge,
                a2a_bridge=self.a2a_bridge,
                event_bus=self.event_bus,
                data_access=self.data_access,
                config_service=self.config_service,
                auth_service=self.auth_service,
                config=adapter_config,
                logger=self.logger.getChild(f"llm_adapter.{adapter_id}")
            )
            
            # Store adapter
            self._llm_adapters[adapter_id] = adapter
            
            # Initialize adapter
            adapter.initialize()
            
            # Save to configuration
            self.config["llm_adapters"] = self.config.get("llm_adapters", {})
            self.config["llm_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Created LLM adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error creating LLM adapter {adapter_id}: {str(e)}")
            raise
    
    def _update_llm_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Update an existing LLM adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._llm_adapters:
                raise ValueError(f"LLM adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._llm_adapters[adapter_id]
            
            # Update adapter configuration
            adapter.update_config(adapter_config)
            
            # Save to configuration
            self.config["llm_adapters"] = self.config.get("llm_adapters", {})
            self.config["llm_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Updated LLM adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error updating LLM adapter {adapter_id}: {str(e)}")
            raise
    
    def _delete_llm_adapter(self, adapter_id: str) -> None:
        """
        Delete an LLM adapter.
        
        Args:
            adapter_id: Adapter ID
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._llm_adapters:
                raise ValueError(f"LLM adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._llm_adapters[adapter_id]
            
            # Release adapter
            adapter.release()
            
            # Remove adapter
            del self._llm_adapters[adapter_id]
            
            # Remove from configuration
            if "llm_adapters" in self.config and adapter_id in self.config["llm_adapters"]:
                del self.config["llm_adapters"][adapter_id]
            
            self.logger.info(f"Deleted LLM adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error deleting LLM adapter {adapter_id}: {str(e)}")
            raise
    
    def _create_vq_vae_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Create a new VQ-VAE adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Create VQ-VAE adapter
            adapter = VQVAEAdapter(
                adapter_id=adapter_id,
                manager=self,
                mcp_bridge=self.mcp_bridge,
                a2a_bridge=self.a2a_bridge,
                event_bus=self.event_bus,
                data_access=self.data_access,
                config_service=self.config_service,
                auth_service=self.auth_service,
                config=adapter_config,
                logger=self.logger.getChild(f"vq_vae_adapter.{adapter_id}")
            )
            
            # Store adapter
            self._vq_vae_adapters[adapter_id] = adapter
            
            # Initialize adapter
            adapter.initialize()
            
            # Save to configuration
            self.config["vq_vae_adapters"] = self.config.get("vq_vae_adapters", {})
            self.config["vq_vae_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Created VQ-VAE adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error creating VQ-VAE adapter {adapter_id}: {str(e)}")
            raise
    
    def _update_vq_vae_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Update an existing VQ-VAE adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._vq_vae_adapters:
                raise ValueError(f"VQ-VAE adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._vq_vae_adapters[adapter_id]
            
            # Update adapter configuration
            adapter.update_config(adapter_config)
            
            # Save to configuration
            self.config["vq_vae_adapters"] = self.config.get("vq_vae_adapters", {})
            self.config["vq_vae_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Updated VQ-VAE adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error updating VQ-VAE adapter {adapter_id}: {str(e)}")
            raise
    
    def _delete_vq_vae_adapter(self, adapter_id: str) -> None:
        """
        Delete a VQ-VAE adapter.
        
        Args:
            adapter_id: Adapter ID
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._vq_vae_adapters:
                raise ValueError(f"VQ-VAE adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._vq_vae_adapters[adapter_id]
            
            # Release adapter
            adapter.release()
            
            # Remove adapter
            del self._vq_vae_adapters[adapter_id]
            
            # Remove from configuration
            if "vq_vae_adapters" in self.config and adapter_id in self.config["vq_vae_adapters"]:
                del self.config["vq_vae_adapters"][adapter_id]
            
            self.logger.info(f"Deleted VQ-VAE adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error deleting VQ-VAE adapter {adapter_id}: {str(e)}")
            raise
    
    def _create_model_registry_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Create a new model registry adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Create model registry adapter
            adapter = ModelRegistryAdapter(
                adapter_id=adapter_id,
                manager=self,
                mcp_bridge=self.mcp_bridge,
                a2a_bridge=self.a2a_bridge,
                event_bus=self.event_bus,
                data_access=self.data_access,
                config_service=self.config_service,
                auth_service=self.auth_service,
                config=adapter_config,
                logger=self.logger.getChild(f"model_registry_adapter.{adapter_id}")
            )
            
            # Store adapter
            self._model_registry_adapters[adapter_id] = adapter
            
            # Initialize adapter
            adapter.initialize()
            
            # Save to configuration
            self.config["model_registry_adapters"] = self.config.get("model_registry_adapters", {})
            self.config["model_registry_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Created model registry adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error creating model registry adapter {adapter_id}: {str(e)}")
            raise
    
    def _update_model_registry_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Update an existing model registry adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._model_registry_adapters:
                raise ValueError(f"Model registry adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._model_registry_adapters[adapter_id]
            
            # Update adapter configuration
            adapter.update_config(adapter_config)
            
            # Save to configuration
            self.config["model_registry_adapters"] = self.config.get("model_registry_adapters", {})
            self.config["model_registry_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Updated model registry adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error updating model registry adapter {adapter_id}: {str(e)}")
            raise
    
    def _delete_model_registry_adapter(self, adapter_id: str) -> None:
        """
        Delete a model registry adapter.
        
        Args:
            adapter_id: Adapter ID
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._model_registry_adapters:
                raise ValueError(f"Model registry adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._model_registry_adapters[adapter_id]
            
            # Release adapter
            adapter.release()
            
            # Remove adapter
            del self._model_registry_adapters[adapter_id]
            
            # Remove from configuration
            if "model_registry_adapters" in self.config and adapter_id in self.config["model_registry_adapters"]:
                del self.config["model_registry_adapters"][adapter_id]
            
            self.logger.info(f"Deleted model registry adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error deleting model registry adapter {adapter_id}: {str(e)}")
            raise
    
    def _create_inference_engine_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Create a new inference engine adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Create inference engine adapter
            adapter = InferenceEngineAdapter(
                adapter_id=adapter_id,
                manager=self,
                mcp_bridge=self.mcp_bridge,
                a2a_bridge=self.a2a_bridge,
                event_bus=self.event_bus,
                data_access=self.data_access,
                config_service=self.config_service,
                auth_service=self.auth_service,
                config=adapter_config,
                logger=self.logger.getChild(f"inference_engine_adapter.{adapter_id}")
            )
            
            # Store adapter
            self._inference_engine_adapters[adapter_id] = adapter
            
            # Initialize adapter
            adapter.initialize()
            
            # Save to configuration
            self.config["inference_engine_adapters"] = self.config.get("inference_engine_adapters", {})
            self.config["inference_engine_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Created inference engine adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error creating inference engine adapter {adapter_id}: {str(e)}")
            raise
    
    def _update_inference_engine_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Update an existing inference engine adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._inference_engine_adapters:
                raise ValueError(f"Inference engine adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._inference_engine_adapters[adapter_id]
            
            # Update adapter configuration
            adapter.update_config(adapter_config)
            
            # Save to configuration
            self.config["inference_engine_adapters"] = self.config.get("inference_engine_adapters", {})
            self.config["inference_engine_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Updated inference engine adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error updating inference engine adapter {adapter_id}: {str(e)}")
            raise
    
    def _delete_inference_engine_adapter(self, adapter_id: str) -> None:
        """
        Delete an inference engine adapter.
        
        Args:
            adapter_id: Adapter ID
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._inference_engine_adapters:
                raise ValueError(f"Inference engine adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._inference_engine_adapters[adapter_id]
            
            # Release adapter
            adapter.release()
            
            # Remove adapter
            del self._inference_engine_adapters[adapter_id]
            
            # Remove from configuration
            if "inference_engine_adapters" in self.config and adapter_id in self.config["inference_engine_adapters"]:
                del self.config["inference_engine_adapters"][adapter_id]
            
            self.logger.info(f"Deleted inference engine adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error deleting inference engine adapter {adapter_id}: {str(e)}")
            raise
    
    def _create_training_pipeline_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Create a new training pipeline adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Create training pipeline adapter
            adapter = TrainingPipelineAdapter(
                adapter_id=adapter_id,
                manager=self,
                mcp_bridge=self.mcp_bridge,
                a2a_bridge=self.a2a_bridge,
                event_bus=self.event_bus,
                data_access=self.data_access,
                config_service=self.config_service,
                auth_service=self.auth_service,
                config=adapter_config,
                logger=self.logger.getChild(f"training_pipeline_adapter.{adapter_id}")
            )
            
            # Store adapter
            self._training_pipeline_adapters[adapter_id] = adapter
            
            # Initialize adapter
            adapter.initialize()
            
            # Save to configuration
            self.config["training_pipeline_adapters"] = self.config.get("training_pipeline_adapters", {})
            self.config["training_pipeline_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Created training pipeline adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error creating training pipeline adapter {adapter_id}: {str(e)}")
            raise
    
    def _update_training_pipeline_adapter(self, adapter_id: str, adapter_config: Dict[str, Any]) -> None:
        """
        Update an existing training pipeline adapter.
        
        Args:
            adapter_id: Adapter ID
            adapter_config: Adapter configuration
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._training_pipeline_adapters:
                raise ValueError(f"Training pipeline adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._training_pipeline_adapters[adapter_id]
            
            # Update adapter configuration
            adapter.update_config(adapter_config)
            
            # Save to configuration
            self.config["training_pipeline_adapters"] = self.config.get("training_pipeline_adapters", {})
            self.config["training_pipeline_adapters"][adapter_id] = adapter_config
            
            self.logger.info(f"Updated training pipeline adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error updating training pipeline adapter {adapter_id}: {str(e)}")
            raise
    
    def _delete_training_pipeline_adapter(self, adapter_id: str) -> None:
        """
        Delete a training pipeline adapter.
        
        Args:
            adapter_id: Adapter ID
        """
        try:
            # Check if adapter exists
            if adapter_id not in self._training_pipeline_adapters:
                raise ValueError(f"Training pipeline adapter {adapter_id} does not exist")
            
            # Get adapter
            adapter = self._training_pipeline_adapters[adapter_id]
            
            # Release adapter
            adapter.release()
            
            # Remove adapter
            del self._training_pipeline_adapters[adapter_id]
            
            # Remove from configuration
            if "training_pipeline_adapters" in self.config and adapter_id in self.config["training_pipeline_adapters"]:
                del self.config["training_pipeline_adapters"][adapter_id]
            
            self.logger.info(f"Deleted training pipeline adapter {adapter_id}")
        except Exception as e:
            self.logger.error(f"Error deleting training pipeline adapter {adapter_id}: {str(e)}")
            raise
    
    def update_metrics(self, metric_name: str, value: int) -> None:
        """
        Update metrics from adapters.
        
        Args:
            metric_name: Metric name
            value: Metric value
        """
        if metric_name in self._metrics:
            self._metrics[metric_name] += value
        
        self._metrics["last_operation_timestamp"] = self.data_access.get_current_timestamp()
