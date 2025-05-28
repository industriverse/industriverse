"""
Generative Layer Adapter for the Deployment Operations Layer.

This module provides integration with the Generative Layer, enabling the Deployment Operations Layer
to instantiate capsule-generators with scope-limited permissions per client.
"""

import os
import json
import logging
import requests
import time
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GenerativeLayerAdapter:
    """
    Adapter for integration with the Generative Layer.
    
    This class provides methods for interacting with the Generative Layer, including
    instantiating capsule-generators, managing permissions, and validating outputs.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Generative Layer Adapter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.endpoint = config.get("endpoint", "http://localhost:8003")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.enabled = config.get("enabled", True)
        
        logger.info("Generative Layer Adapter initialized")
    
    def check_health(self) -> Dict:
        """
        Check the health of the Generative Layer.
        
        Returns:
            Dict: Health status information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/health")
            return response
        except Exception as e:
            logger.error(f"Error checking Generative Layer health: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_version(self) -> Dict:
        """
        Get the version of the Generative Layer.
        
        Returns:
            Dict: Version information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/version")
            return response
        except Exception as e:
            logger.error(f"Error getting Generative Layer version: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities of the Generative Layer.
        
        Returns:
            Dict: Capabilities information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/capabilities")
            return response
        except Exception as e:
            logger.error(f"Error getting Generative Layer capabilities: {e}")
            return {"status": "error", "message": str(e)}
    
    def instantiate_capsule_generator(self, generator_config: Dict) -> Dict:
        """
        Instantiate a capsule generator in the Generative Layer.
        
        Args:
            generator_config: Generator configuration
            
        Returns:
            Dict: Instantiation results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/generators/instantiate", json=generator_config)
            return response
        except Exception as e:
            logger.error(f"Error instantiating capsule generator: {e}")
            return {"status": "error", "message": str(e)}
    
    def terminate_capsule_generator(self, generator_id: str) -> Dict:
        """
        Terminate a capsule generator in the Generative Layer.
        
        Args:
            generator_id: ID of the generator to terminate
            
        Returns:
            Dict: Termination results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", f"/generators/{generator_id}/terminate")
            return response
        except Exception as e:
            logger.error(f"Error terminating capsule generator: {e}")
            return {"status": "error", "message": str(e)}
    
    def set_generator_permissions(self, generator_id: str, permissions: Dict) -> Dict:
        """
        Set permissions for a capsule generator.
        
        Args:
            generator_id: ID of the generator
            permissions: Permission configuration
            
        Returns:
            Dict: Permission update results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request(
                "POST", 
                f"/generators/{generator_id}/permissions", 
                json=permissions
            )
            return response
        except Exception as e:
            logger.error(f"Error setting generator permissions: {e}")
            return {"status": "error", "message": str(e)}
    
    def validate_generator_output(self, output_config: Dict) -> Dict:
        """
        Validate output from a capsule generator.
        
        Args:
            output_config: Output validation configuration
            
        Returns:
            Dict: Validation results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/generators/validate-output", json=output_config)
            return response
        except Exception as e:
            logger.error(f"Error validating generator output: {e}")
            return {"status": "error", "message": str(e)}
    
    def deploy(self, config: Dict) -> Dict:
        """
        Deploy Generative Layer components.
        
        Args:
            config: Deployment configuration
            
        Returns:
            Dict: Deployment results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            # Instantiate capsule generators
            generator_results = {}
            for generator in config.get("generators", []):
                generator_result = self.instantiate_capsule_generator(generator)
                generator_results[generator.get("name", "unnamed")] = generator_result
                
                # Set permissions if provided
                if "permissions" in generator and generator_result.get("status") == "success":
                    generator_id = generator_result.get("generator_id")
                    permission_result = self.set_generator_permissions(
                        generator_id, 
                        generator["permissions"]
                    )
                    generator_results[generator.get("name", "unnamed")]["permissions"] = permission_result
            
            return {
                "status": "success",
                "message": "Generative Layer deployment completed",
                "deployment_id": f"generative-layer-{int(time.time())}",
                "results": {
                    "generators": generator_results
                }
            }
        except Exception as e:
            logger.error(f"Error deploying Generative Layer components: {e}")
            return {"status": "error", "message": str(e)}
    
    def rollback(self, deployment_id: Optional[str] = None) -> Dict:
        """
        Rollback a Generative Layer deployment.
        
        Args:
            deployment_id: ID of the deployment to rollback
            
        Returns:
            Dict: Rollback results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/rollback", json={"deployment_id": deployment_id})
            return response
        except Exception as e:
            logger.error(f"Error rolling back Generative Layer deployment: {e}")
            return {"status": "error", "message": str(e)}
    
    def update(self, config: Dict) -> Dict:
        """
        Update Generative Layer components.
        
        Args:
            config: Update configuration
            
        Returns:
            Dict: Update results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/update", json=config)
            return response
        except Exception as e:
            logger.error(f"Error updating Generative Layer components: {e}")
            return {"status": "error", "message": str(e)}
    
    def rollback_update(self, update_id: str) -> Dict:
        """
        Rollback a Generative Layer update.
        
        Args:
            update_id: ID of the update to rollback
            
        Returns:
            Dict: Rollback results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/rollback-update", json={"update_id": update_id})
            return response
        except Exception as e:
            logger.error(f"Error rolling back Generative Layer update: {e}")
            return {"status": "error", "message": str(e)}
    
    def sync(self, params: Dict) -> Dict:
        """
        Synchronize with the Generative Layer.
        
        Args:
            params: Synchronization parameters
            
        Returns:
            Dict: Synchronization results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Generative Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/sync", json=params)
            return response
        except Exception as e:
            logger.error(f"Error synchronizing with Generative Layer: {e}")
            return {"status": "error", "message": str(e)}
    
    def _make_request(self, method: str, path: str, **kwargs) -> Dict:
        """
        Make an HTTP request to the Generative Layer API.
        
        Args:
            method: HTTP method
            path: API path
            **kwargs: Additional request parameters
            
        Returns:
            Dict: Response data
            
        Raises:
            Exception: If request fails after all retry attempts
        """
        url = f"{self.endpoint}{path}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == self.retry_attempts - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
