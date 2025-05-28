"""
Layer Integration Manager for the Deployment Operations Layer.

This module provides centralized management of integration with all Industriverse layers,
enabling the Deployment Operations Layer to function as the command center with full
control over the entire ecosystem.
"""

import os
import json
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LayerIntegrationManager:
    """
    Centralized manager for integration with all Industriverse layers.
    
    This class provides comprehensive orchestration capabilities across all layers,
    enabling the Deployment Operations Layer to function as the command center for
    the entire Industriverse ecosystem.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Layer Integration Manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses default path.
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), 
            ".deployment_ops", 
            "config", 
            "layer_integration.json"
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Layer adapters
        self.adapters = {}
        
        # Layer status tracking
        self.layer_status = {}
        
        # Integration locks for thread safety
        self.locks = {
            "data_layer": threading.RLock(),
            "core_ai_layer": threading.RLock(),
            "generative_layer": threading.RLock(),
            "application_layer": threading.RLock(),
            "protocol_layer": threading.RLock(),
            "workflow_layer": threading.RLock(),
            "ui_ux_layer": threading.RLock(),
            "security_compliance_layer": threading.RLock(),
            "native_app_layer": threading.RLock(),
        }
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize adapters
        self._initialize_adapters()
        
        logger.info("Layer Integration Manager initialized")
    
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
            "data_layer": {
                "endpoint": "http://localhost:8001",
                "auth_token": "",
                "timeout": 30,
                "retry_attempts": 3,
                "enabled": True
            },
            "core_ai_layer": {
                "endpoint": "http://localhost:8002",
                "auth_token": "",
                "timeout": 30,
                "retry_attempts": 3,
                "enabled": True
            },
            "generative_layer": {
                "endpoint": "http://localhost:8003",
                "auth_token": "",
                "timeout": 30,
                "retry_attempts": 3,
                "enabled": True
            },
            "application_layer": {
                "endpoint": "http://localhost:8004",
                "auth_token": "",
                "timeout": 30,
                "retry_attempts": 3,
                "enabled": True
            },
            "protocol_layer": {
                "endpoint": "http://localhost:8005",
                "auth_token": "",
                "timeout": 30,
                "retry_attempts": 3,
                "enabled": True
            },
            "workflow_layer": {
                "endpoint": "http://localhost:8006",
                "auth_token": "",
                "timeout": 30,
                "retry_attempts": 3,
                "enabled": True
            },
            "ui_ux_layer": {
                "endpoint": "http://localhost:8007",
                "auth_token": "",
                "timeout": 30,
                "retry_attempts": 3,
                "enabled": True
            },
            "security_compliance_layer": {
                "endpoint": "http://localhost:8008",
                "auth_token": "",
                "timeout": 30,
                "retry_attempts": 3,
                "enabled": True
            },
            "native_app_layer": {
                "endpoint": "http://localhost:8009",
                "auth_token": "",
                "timeout": 30,
                "retry_attempts": 3,
                "enabled": True
            }
        }
        
        # Save default config
        try:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving default configuration: {e}")
        
        return default_config
    
    def _initialize_adapters(self):
        """Initialize all layer adapters."""
        try:
            # Import adapters
            from integration.data_layer.data_layer_adapter import DataLayerAdapter
            from integration.core_ai_layer.core_ai_layer_adapter import CoreAILayerAdapter
            from integration.generative_layer.generative_layer_adapter import GenerativeLayerAdapter
            from integration.application_layer.application_layer_adapter import ApplicationLayerAdapter
            from integration.protocol_layer.protocol_layer_adapter import ProtocolLayerAdapter
            from integration.workflow_layer.workflow_layer_adapter import WorkflowLayerAdapter
            from integration.ui_ux_layer.ui_ux_layer_adapter import UIUXLayerAdapter
            from integration.security_compliance_layer.security_compliance_layer_adapter import SecurityComplianceLayerAdapter
            from integration.native_app_layer.native_app_layer_adapter import NativeAppLayerAdapter
            
            # Initialize adapters with configuration
            self.adapters["data_layer"] = DataLayerAdapter(self.config["data_layer"])
            self.adapters["core_ai_layer"] = CoreAILayerAdapter(self.config["core_ai_layer"])
            self.adapters["generative_layer"] = GenerativeLayerAdapter(self.config["generative_layer"])
            self.adapters["application_layer"] = ApplicationLayerAdapter(self.config["application_layer"])
            self.adapters["protocol_layer"] = ProtocolLayerAdapter(self.config["protocol_layer"])
            self.adapters["workflow_layer"] = WorkflowLayerAdapter(self.config["workflow_layer"])
            self.adapters["ui_ux_layer"] = UIUXLayerAdapter(self.config["ui_ux_layer"])
            self.adapters["security_compliance_layer"] = SecurityComplianceLayerAdapter(self.config["security_compliance_layer"])
            self.adapters["native_app_layer"] = NativeAppLayerAdapter(self.config["native_app_layer"])
            
            # Initialize layer status
            for layer in self.adapters:
                self.layer_status[layer] = {
                    "status": "initializing",
                    "last_check": time.time(),
                    "health": None,
                    "version": None,
                    "capabilities": None
                }
            
            # Start health check thread
            self._start_health_check_thread()
            
        except Exception as e:
            logger.error(f"Error initializing adapters: {e}")
            raise
    
    def _start_health_check_thread(self):
        """Start a background thread for periodic health checks."""
        def health_check_worker():
            while True:
                try:
                    self.check_all_layers_health()
                except Exception as e:
                    logger.error(f"Error in health check worker: {e}")
                time.sleep(60)  # Check every minute
        
        thread = threading.Thread(target=health_check_worker, daemon=True)
        thread.start()
    
    def check_all_layers_health(self) -> Dict[str, Dict]:
        """
        Check the health of all layers.
        
        Returns:
            Dict[str, Dict]: Health status for all layers
        """
        results = {}
        for layer, adapter in self.adapters.items():
            try:
                with self.locks[layer]:
                    health = adapter.check_health()
                    self.layer_status[layer] = {
                        "status": "healthy" if health["status"] == "ok" else "unhealthy",
                        "last_check": time.time(),
                        "health": health,
                        "version": adapter.get_version(),
                        "capabilities": adapter.get_capabilities()
                    }
                    results[layer] = self.layer_status[layer]
            except Exception as e:
                logger.error(f"Error checking health for {layer}: {e}")
                self.layer_status[layer] = {
                    "status": "error",
                    "last_check": time.time(),
                    "health": {"status": "error", "message": str(e)},
                    "version": None,
                    "capabilities": None
                }
                results[layer] = self.layer_status[layer]
        
        return results
    
    def get_layer_status(self, layer: str) -> Dict:
        """
        Get the status of a specific layer.
        
        Args:
            layer: Layer name
            
        Returns:
            Dict: Layer status information
        """
        if layer not in self.layer_status:
            raise ValueError(f"Unknown layer: {layer}")
        
        return self.layer_status[layer]
    
    def get_all_layers_status(self) -> Dict[str, Dict]:
        """
        Get the status of all layers.
        
        Returns:
            Dict[str, Dict]: Status information for all layers
        """
        return self.layer_status
    
    def orchestrate_deployment(self, deployment_config: Dict) -> Dict:
        """
        Orchestrate a deployment across all required layers.
        
        Args:
            deployment_config: Deployment configuration
            
        Returns:
            Dict: Deployment results
        """
        logger.info(f"Orchestrating deployment: {deployment_config.get('name', 'unnamed')}")
        
        # Validate deployment configuration
        self._validate_deployment_config(deployment_config)
        
        # Determine deployment order based on dependencies
        deployment_order = self._determine_deployment_order(deployment_config)
        
        # Execute deployment in order
        results = {}
        for layer in deployment_order:
            if layer in deployment_config.get("layers", {}):
                try:
                    with self.locks[layer]:
                        logger.info(f"Deploying to {layer}")
                        layer_config = deployment_config["layers"][layer]
                        results[layer] = self.adapters[layer].deploy(layer_config)
                except Exception as e:
                    logger.error(f"Error deploying to {layer}: {e}")
                    results[layer] = {"status": "error", "message": str(e)}
                    
                    # Handle rollback if needed
                    if deployment_config.get("rollback_on_error", True):
                        self._rollback_deployment(results, deployment_order, layer)
                        return {
                            "status": "error",
                            "message": f"Deployment failed at {layer}: {str(e)}",
                            "results": results
                        }
        
        return {
            "status": "success",
            "message": "Deployment completed successfully",
            "results": results
        }
    
    def _validate_deployment_config(self, config: Dict):
        """
        Validate deployment configuration.
        
        Args:
            config: Deployment configuration to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(config, dict):
            raise ValueError("Deployment configuration must be a dictionary")
        
        if "name" not in config:
            raise ValueError("Deployment configuration must include a name")
        
        if "layers" not in config or not isinstance(config["layers"], dict):
            raise ValueError("Deployment configuration must include a layers dictionary")
        
        for layer in config["layers"]:
            if layer not in self.adapters:
                raise ValueError(f"Unknown layer: {layer}")
    
    def _determine_deployment_order(self, config: Dict) -> List[str]:
        """
        Determine the order in which layers should be deployed based on dependencies.
        
        Args:
            config: Deployment configuration
            
        Returns:
            List[str]: Ordered list of layer names
        """
        # Default deployment order
        default_order = [
            "security_compliance_layer",
            "data_layer",
            "core_ai_layer",
            "protocol_layer",
            "generative_layer",
            "workflow_layer",
            "application_layer",
            "ui_ux_layer",
            "native_app_layer"
        ]
        
        # Filter to only include layers in the deployment config
        return [layer for layer in default_order if layer in config.get("layers", {})]
    
    def _rollback_deployment(self, results: Dict, deployment_order: List[str], failed_layer: str):
        """
        Rollback a failed deployment.
        
        Args:
            results: Current deployment results
            deployment_order: Ordered list of layer names
            failed_layer: Layer where deployment failed
        """
        logger.info(f"Rolling back deployment after failure in {failed_layer}")
        
        # Get index of failed layer
        failed_index = deployment_order.index(failed_layer)
        
        # Rollback in reverse order up to the failed layer
        for layer in reversed(deployment_order[:failed_index]):
            if layer in results and results[layer].get("status") == "success":
                try:
                    with self.locks[layer]:
                        logger.info(f"Rolling back {layer}")
                        rollback_result = self.adapters[layer].rollback(
                            results[layer].get("deployment_id")
                        )
                        results[layer]["rollback"] = rollback_result
                except Exception as e:
                    logger.error(f"Error rolling back {layer}: {e}")
                    results[layer]["rollback"] = {
                        "status": "error",
                        "message": str(e)
                    }
    
    def update_layer_configuration(self, layer: str, config: Dict) -> Dict:
        """
        Update configuration for a specific layer.
        
        Args:
            layer: Layer name
            config: New configuration
            
        Returns:
            Dict: Updated configuration
        """
        if layer not in self.adapters:
            raise ValueError(f"Unknown layer: {layer}")
        
        with self.locks[layer]:
            # Update configuration
            self.config[layer].update(config)
            
            # Save configuration
            try:
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving configuration: {e}")
            
            # Reinitialize adapter
            adapter_class = self.adapters[layer].__class__
            self.adapters[layer] = adapter_class(self.config[layer])
            
            return self.config[layer]
    
    def execute_cross_layer_operation(self, operation: str, params: Dict) -> Dict:
        """
        Execute an operation that spans multiple layers.
        
        Args:
            operation: Operation name
            params: Operation parameters
            
        Returns:
            Dict: Operation results
        """
        logger.info(f"Executing cross-layer operation: {operation}")
        
        if operation == "health_check":
            return {"status": "success", "results": self.check_all_layers_health()}
        
        elif operation == "version_check":
            results = {}
            for layer, adapter in self.adapters.items():
                try:
                    with self.locks[layer]:
                        results[layer] = adapter.get_version()
                except Exception as e:
                    logger.error(f"Error getting version for {layer}: {e}")
                    results[layer] = {"status": "error", "message": str(e)}
            
            return {"status": "success", "results": results}
        
        elif operation == "capability_check":
            results = {}
            for layer, adapter in self.adapters.items():
                try:
                    with self.locks[layer]:
                        results[layer] = adapter.get_capabilities()
                except Exception as e:
                    logger.error(f"Error getting capabilities for {layer}: {e}")
                    results[layer] = {"status": "error", "message": str(e)}
            
            return {"status": "success", "results": results}
        
        elif operation == "sync_all":
            results = {}
            for layer, adapter in self.adapters.items():
                try:
                    with self.locks[layer]:
                        results[layer] = adapter.sync(params.get(layer, {}))
                except Exception as e:
                    logger.error(f"Error syncing {layer}: {e}")
                    results[layer] = {"status": "error", "message": str(e)}
            
            return {"status": "success", "results": results}
        
        else:
            raise ValueError(f"Unknown cross-layer operation: {operation}")
    
    def get_adapter(self, layer: str):
        """
        Get the adapter for a specific layer.
        
        Args:
            layer: Layer name
            
        Returns:
            Adapter instance for the specified layer
        """
        if layer not in self.adapters:
            raise ValueError(f"Unknown layer: {layer}")
        
        return self.adapters[layer]
