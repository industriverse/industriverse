"""
Cross-Layer Integration Manager for the Deployment Operations Layer.

This module provides advanced orchestration capabilities across all Industriverse layers,
enabling complex cross-layer operations, dependency management, and coordinated deployments.
"""

import os
import json
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CrossLayerIntegrationManager:
    """
    Advanced manager for cross-layer integration and orchestration.
    
    This class provides sophisticated capabilities for managing operations that span
    multiple Industriverse layers, including dependency resolution, coordinated
    deployments, and cross-layer data flow.
    """
    
    def __init__(self, layer_integration_manager=None, config_path: Optional[str] = None):
        """
        Initialize the Cross-Layer Integration Manager.
        
        Args:
            layer_integration_manager: Instance of LayerIntegrationManager
            config_path: Path to the configuration file. If None, uses default path.
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), 
            ".deployment_ops", 
            "config", 
            "cross_layer_integration.json"
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Store reference to layer integration manager
        self.layer_manager = layer_integration_manager
        
        # Cross-layer operation locks
        self.operation_locks = defaultdict(threading.RLock)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize dependency graph
        self.dependency_graph = self._build_dependency_graph()
        
        logger.info("Cross-Layer Integration Manager initialized")
    
    def _load_config(self) -> Dict:
        """
        Load configuration from file or create default if not exists.
        
        Returns:
            Dict: Configuration dictionary
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """
        Create default configuration.
        
        Returns:
            Dict: Default configuration dictionary
        """
        default_config = {
            "dependencies": {
                "data_layer": [],
                "core_ai_layer": ["data_layer"],
                "generative_layer": ["core_ai_layer", "data_layer"],
                "application_layer": ["generative_layer", "core_ai_layer"],
                "protocol_layer": ["data_layer"],
                "workflow_layer": ["protocol_layer", "application_layer"],
                "ui_ux_layer": ["application_layer", "workflow_layer"],
                "security_compliance_layer": [],
                "native_app_layer": ["ui_ux_layer", "application_layer"]
            },
            "cross_layer_operations": {
                "full_system_deployment": {
                    "description": "Deploy all layers in dependency order",
                    "timeout": 3600,
                    "retry_attempts": 1
                },
                "system_health_check": {
                    "description": "Check health of all layers",
                    "timeout": 300,
                    "retry_attempts": 3
                },
                "system_update": {
                    "description": "Update all layers in dependency order",
                    "timeout": 3600,
                    "retry_attempts": 1
                },
                "system_rollback": {
                    "description": "Rollback all layers in reverse dependency order",
                    "timeout": 1800,
                    "retry_attempts": 1
                }
            },
            "data_flow_mappings": {
                "data_to_core_ai": {
                    "source": "data_layer",
                    "destination": "core_ai_layer",
                    "data_types": ["training_data", "inference_data", "validation_data"]
                },
                "core_ai_to_generative": {
                    "source": "core_ai_layer",
                    "destination": "generative_layer",
                    "data_types": ["model_outputs", "embeddings", "predictions"]
                },
                "generative_to_application": {
                    "source": "generative_layer",
                    "destination": "application_layer",
                    "data_types": ["generated_content", "application_logic", "ui_components"]
                },
                "application_to_ui": {
                    "source": "application_layer",
                    "destination": "ui_ux_layer",
                    "data_types": ["ui_definitions", "interaction_models", "visualization_data"]
                }
            }
        }
        
        # Save default config
        try:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving default configuration: {e}")
        
        return default_config
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Build the layer dependency graph from configuration.
        
        Returns:
            Dict[str, List[str]]: Dependency graph
        """
        return self.config.get("dependencies", {})
    
    def get_deployment_order(self, layers: Optional[List[str]] = None) -> List[str]:
        """
        Determine the correct deployment order based on dependencies.
        
        Args:
            layers: List of layers to deploy. If None, includes all layers.
            
        Returns:
            List[str]: Ordered list of layer names
        """
        if layers is None:
            layers = list(self.dependency_graph.keys())
        
        # Filter to only include specified layers
        filtered_graph = {
            layer: [dep for dep in deps if dep in layers]
            for layer, deps in self.dependency_graph.items()
            if layer in layers
        }
        
        # Topological sort
        result = []
        visited = set()
        temp_visited = set()
        
        def visit(node):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected involving {node}")
            if node in visited:
                return
            
            temp_visited.add(node)
            for dep in filtered_graph.get(node, []):
                visit(dep)
            
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
        
        for layer in filtered_graph:
            if layer not in visited:
                visit(layer)
        
        return result
    
    def get_rollback_order(self, layers: Optional[List[str]] = None) -> List[str]:
        """
        Determine the correct rollback order (reverse of deployment order).
        
        Args:
            layers: List of layers to rollback. If None, includes all layers.
            
        Returns:
            List[str]: Ordered list of layer names for rollback
        """
        deployment_order = self.get_deployment_order(layers)
        return list(reversed(deployment_order))
    
    def execute_cross_layer_operation(self, operation_name: str, params: Dict) -> Dict:
        """
        Execute a predefined cross-layer operation.
        
        Args:
            operation_name: Name of the operation to execute
            params: Operation parameters
            
        Returns:
            Dict: Operation results
        """
        if operation_name not in self.config.get("cross_layer_operations", {}):
            raise ValueError(f"Unknown cross-layer operation: {operation_name}")
        
        with self.operation_locks[operation_name]:
            logger.info(f"Executing cross-layer operation: {operation_name}")
            
            operation_config = self.config["cross_layer_operations"][operation_name]
            
            if operation_name == "full_system_deployment":
                return self._execute_full_system_deployment(params, operation_config)
            
            elif operation_name == "system_health_check":
                return self._execute_system_health_check(params, operation_config)
            
            elif operation_name == "system_update":
                return self._execute_system_update(params, operation_config)
            
            elif operation_name == "system_rollback":
                return self._execute_system_rollback(params, operation_config)
            
            else:
                # Custom operation handling
                return self._execute_custom_operation(operation_name, params, operation_config)
    
    def _execute_full_system_deployment(self, params: Dict, operation_config: Dict) -> Dict:
        """
        Execute full system deployment across all layers.
        
        Args:
            params: Deployment parameters
            operation_config: Operation configuration
            
        Returns:
            Dict: Deployment results
        """
        # Get layers to deploy
        layers = params.get("layers", list(self.dependency_graph.keys()))
        
        # Get deployment order
        try:
            deployment_order = self.get_deployment_order(layers)
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        
        # Prepare deployment configuration
        deployment_config = {
            "name": params.get("name", "full_system_deployment"),
            "description": params.get("description", "Full system deployment"),
            "rollback_on_error": params.get("rollback_on_error", True),
            "layers": {}
        }
        
        # Add layer-specific configurations
        for layer in deployment_order:
            if layer in params.get("layer_configs", {}):
                deployment_config["layers"][layer] = params["layer_configs"][layer]
            else:
                deployment_config["layers"][layer] = {"default_deployment": True}
        
        # Execute deployment through layer integration manager
        if self.layer_manager:
            return self.layer_manager.orchestrate_deployment(deployment_config)
        else:
            return {
                "status": "error",
                "message": "Layer Integration Manager not available"
            }
    
    def _execute_system_health_check(self, params: Dict, operation_config: Dict) -> Dict:
        """
        Execute system health check across all layers.
        
        Args:
            params: Health check parameters
            operation_config: Operation configuration
            
        Returns:
            Dict: Health check results
        """
        # Get layers to check
        layers = params.get("layers", list(self.dependency_graph.keys()))
        
        results = {}
        all_healthy = True
        
        # Check each layer
        for layer in layers:
            if self.layer_manager:
                try:
                    layer_status = self.layer_manager.get_layer_status(layer)
                    results[layer] = layer_status
                    
                    if layer_status["status"] != "healthy":
                        all_healthy = False
                except Exception as e:
                    logger.error(f"Error checking health for {layer}: {e}")
                    results[layer] = {
                        "status": "error",
                        "message": str(e)
                    }
                    all_healthy = False
            else:
                results[layer] = {
                    "status": "error",
                    "message": "Layer Integration Manager not available"
                }
                all_healthy = False
        
        return {
            "status": "success" if all_healthy else "warning",
            "message": "All layers healthy" if all_healthy else "Some layers unhealthy",
            "results": results
        }
    
    def _execute_system_update(self, params: Dict, operation_config: Dict) -> Dict:
        """
        Execute system update across all layers.
        
        Args:
            params: Update parameters
            operation_config: Operation configuration
            
        Returns:
            Dict: Update results
        """
        # Get layers to update
        layers = params.get("layers", list(self.dependency_graph.keys()))
        
        # Get deployment order
        try:
            update_order = self.get_deployment_order(layers)
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        
        results = {}
        success = True
        
        # Update each layer in order
        for layer in update_order:
            if self.layer_manager:
                try:
                    adapter = self.layer_manager.get_adapter(layer)
                    layer_params = params.get("layer_configs", {}).get(layer, {})
                    
                    results[layer] = adapter.update(layer_params)
                    
                    if results[layer].get("status") != "success":
                        success = False
                        
                        # Handle rollback if needed
                        if params.get("rollback_on_error", True):
                            self._rollback_updates(results, update_order, layer)
                            return {
                                "status": "error",
                                "message": f"Update failed at {layer}",
                                "results": results
                            }
                except Exception as e:
                    logger.error(f"Error updating {layer}: {e}")
                    results[layer] = {
                        "status": "error",
                        "message": str(e)
                    }
                    success = False
                    
                    # Handle rollback if needed
                    if params.get("rollback_on_error", True):
                        self._rollback_updates(results, update_order, layer)
                        return {
                            "status": "error",
                            "message": f"Update failed at {layer}: {str(e)}",
                            "results": results
                        }
            else:
                results[layer] = {
                    "status": "error",
                    "message": "Layer Integration Manager not available"
                }
                success = False
        
        return {
            "status": "success" if success else "partial_success",
            "message": "System update completed" + ("" if success else " with some errors"),
            "results": results
        }
    
    def _rollback_updates(self, results: Dict, update_order: List[str], failed_layer: str):
        """
        Rollback updates after a failure.
        
        Args:
            results: Current update results
            update_order: Ordered list of layer names
            failed_layer: Layer where update failed
        """
        logger.info(f"Rolling back updates after failure in {failed_layer}")
        
        # Get index of failed layer
        failed_index = update_order.index(failed_layer)
        
        # Rollback in reverse order up to the failed layer
        for layer in reversed(update_order[:failed_index]):
            if layer in results and results[layer].get("status") == "success":
                try:
                    if self.layer_manager:
                        adapter = self.layer_manager.get_adapter(layer)
                        rollback_result = adapter.rollback_update(
                            results[layer].get("update_id")
                        )
                        results[layer]["rollback"] = rollback_result
                except Exception as e:
                    logger.error(f"Error rolling back update for {layer}: {e}")
                    results[layer]["rollback"] = {
                        "status": "error",
                        "message": str(e)
                    }
    
    def _execute_system_rollback(self, params: Dict, operation_config: Dict) -> Dict:
        """
        Execute system rollback across all layers.
        
        Args:
            params: Rollback parameters
            operation_config: Operation configuration
            
        Returns:
            Dict: Rollback results
        """
        # Get layers to rollback
        layers = params.get("layers", list(self.dependency_graph.keys()))
        
        # Get rollback order (reverse of deployment order)
        try:
            rollback_order = self.get_rollback_order(layers)
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        
        results = {}
        success = True
        
        # Rollback each layer in order
        for layer in rollback_order:
            if self.layer_manager:
                try:
                    adapter = self.layer_manager.get_adapter(layer)
                    layer_params = params.get("layer_configs", {}).get(layer, {})
                    
                    results[layer] = adapter.rollback(layer_params)
                    
                    if results[layer].get("status") != "success":
                        success = False
                except Exception as e:
                    logger.error(f"Error rolling back {layer}: {e}")
                    results[layer] = {
                        "status": "error",
                        "message": str(e)
                    }
                    success = False
            else:
                results[layer] = {
                    "status": "error",
                    "message": "Layer Integration Manager not available"
                }
                success = False
        
        return {
            "status": "success" if success else "partial_success",
            "message": "System rollback completed" + ("" if success else " with some errors"),
            "results": results
        }
    
    def _execute_custom_operation(self, operation_name: str, params: Dict, operation_config: Dict) -> Dict:
        """
        Execute a custom cross-layer operation.
        
        Args:
            operation_name: Name of the operation
            params: Operation parameters
            operation_config: Operation configuration
            
        Returns:
            Dict: Operation results
        """
        logger.info(f"Executing custom cross-layer operation: {operation_name}")
        
        # Custom operation implementation would go here
        return {
            "status": "error",
            "message": f"Custom operation {operation_name} not implemented"
        }
    
    def map_data_flow(self, source_layer: str, destination_layer: str, data_type: str, data: Any) -> Dict:
        """
        Map and transform data flowing between layers.
        
        Args:
            source_layer: Source layer name
            destination_layer: Destination layer name
            data_type: Type of data being mapped
            data: Data to map
            
        Returns:
            Dict: Mapping results
        """
        # Check if mapping exists
        mapping_key = f"{source_layer}_to_{destination_layer}"
        if mapping_key not in self.config.get("data_flow_mappings", {}):
            return {
                "status": "error",
                "message": f"No data flow mapping defined for {source_layer} to {destination_layer}"
            }
        
        mapping = self.config["data_flow_mappings"][mapping_key]
        
        # Check if data type is supported
        if data_type not in mapping.get("data_types", []):
            return {
                "status": "error",
                "message": f"Data type {data_type} not supported for {source_layer} to {destination_layer} mapping"
            }
        
        # Apply mapping transformation
        try:
            # In a real implementation, this would apply specific transformations
            # based on the source, destination, and data type
            transformed_data = self._transform_data(data, source_layer, destination_layer, data_type)
            
            return {
                "status": "success",
                "message": f"Data mapped from {source_layer} to {destination_layer}",
                "data": transformed_data
            }
        except Exception as e:
            logger.error(f"Error mapping data: {e}")
            return {
                "status": "error",
                "message": f"Error mapping data: {str(e)}"
            }
    
    def _transform_data(self, data: Any, source_layer: str, destination_layer: str, data_type: str) -> Any:
        """
        Transform data between layers.
        
        Args:
            data: Data to transform
            source_layer: Source layer name
            destination_layer: Destination layer name
            data_type: Type of data being transformed
            
        Returns:
            Transformed data
        """
        # This is a placeholder for actual transformation logic
        # In a real implementation, this would apply specific transformations
        # based on the source, destination, and data type
        
        # For now, just return the data unchanged
        return data
    
    def register_custom_operation(self, operation_name: str, operation_config: Dict) -> Dict:
        """
        Register a new custom cross-layer operation.
        
        Args:
            operation_name: Name of the operation
            operation_config: Operation configuration
            
        Returns:
            Dict: Registration results
        """
        if operation_name in self.config.get("cross_layer_operations", {}):
            return {
                "status": "error",
                "message": f"Operation {operation_name} already exists"
            }
        
        # Validate operation configuration
        required_fields = ["description", "timeout", "retry_attempts"]
        for field in required_fields:
            if field not in operation_config:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }
        
        # Add operation to configuration
        self.config.setdefault("cross_layer_operations", {})[operation_name] = operation_config
        
        # Save configuration
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return {
                "status": "error",
                "message": f"Error saving configuration: {str(e)}"
            }
        
        return {
            "status": "success",
            "message": f"Operation {operation_name} registered successfully"
        }
    
    def register_data_flow_mapping(self, source_layer: str, destination_layer: str, data_types: List[str]) -> Dict:
        """
        Register a new data flow mapping between layers.
        
        Args:
            source_layer: Source layer name
            destination_layer: Destination layer name
            data_types: List of supported data types
            
        Returns:
            Dict: Registration results
        """
        mapping_key = f"{source_layer}_to_{destination_layer}"
        
        # Validate layers
        valid_layers = list(self.dependency_graph.keys())
        if source_layer not in valid_layers:
            return {
                "status": "error",
                "message": f"Invalid source layer: {source_layer}"
            }
        
        if destination_layer not in valid_layers:
            return {
                "status": "error",
                "message": f"Invalid destination layer: {destination_layer}"
            }
        
        # Add mapping to configuration
        self.config.setdefault("data_flow_mappings", {})[mapping_key] = {
            "source": source_layer,
            "destination": destination_layer,
            "data_types": data_types
        }
        
        # Save configuration
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return {
                "status": "error",
                "message": f"Error saving configuration: {str(e)}"
            }
        
        return {
            "status": "success",
            "message": f"Data flow mapping from {source_layer} to {destination_layer} registered successfully"
        }
