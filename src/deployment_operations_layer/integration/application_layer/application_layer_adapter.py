"""
Application Layer Adapter for the Deployment Operations Layer.

This module provides integration with the Application Layer, enabling the Deployment Operations Layer
to deploy UI/UX capsules based on role maps and user personas.
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

class ApplicationLayerAdapter:
    """
    Adapter for integration with the Application Layer.
    
    This class provides methods for interacting with the Application Layer, including
    deploying UI/UX capsules, managing role maps, and configuring user personas.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Application Layer Adapter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.endpoint = config.get("endpoint", "http://localhost:8004")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.enabled = config.get("enabled", True)
        
        logger.info("Application Layer Adapter initialized")
    
    def check_health(self) -> Dict:
        """
        Check the health of the Application Layer.
        
        Returns:
            Dict: Health status information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/health")
            return response
        except Exception as e:
            logger.error(f"Error checking Application Layer health: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_version(self) -> Dict:
        """
        Get the version of the Application Layer.
        
        Returns:
            Dict: Version information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/version")
            return response
        except Exception as e:
            logger.error(f"Error getting Application Layer version: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities of the Application Layer.
        
        Returns:
            Dict: Capabilities information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/capabilities")
            return response
        except Exception as e:
            logger.error(f"Error getting Application Layer capabilities: {e}")
            return {"status": "error", "message": str(e)}
    
    def deploy_ui_capsule(self, capsule_config: Dict) -> Dict:
        """
        Deploy a UI capsule in the Application Layer.
        
        Args:
            capsule_config: UI capsule configuration
            
        Returns:
            Dict: Deployment results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/capsules/ui/deploy", json=capsule_config)
            return response
        except Exception as e:
            logger.error(f"Error deploying UI capsule: {e}")
            return {"status": "error", "message": str(e)}
    
    def undeploy_ui_capsule(self, capsule_id: str) -> Dict:
        """
        Undeploy a UI capsule from the Application Layer.
        
        Args:
            capsule_id: ID of the UI capsule to undeploy
            
        Returns:
            Dict: Undeployment results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", f"/capsules/ui/{capsule_id}/undeploy")
            return response
        except Exception as e:
            logger.error(f"Error undeploying UI capsule: {e}")
            return {"status": "error", "message": str(e)}
    
    def configure_role_map(self, role_map_config: Dict) -> Dict:
        """
        Configure a role map in the Application Layer.
        
        Args:
            role_map_config: Role map configuration
            
        Returns:
            Dict: Configuration results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/role-maps/configure", json=role_map_config)
            return response
        except Exception as e:
            logger.error(f"Error configuring role map: {e}")
            return {"status": "error", "message": str(e)}
    
    def delete_role_map(self, role_map_id: str) -> Dict:
        """
        Delete a role map from the Application Layer.
        
        Args:
            role_map_id: ID of the role map to delete
            
        Returns:
            Dict: Deletion results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("DELETE", f"/role-maps/{role_map_id}")
            return response
        except Exception as e:
            logger.error(f"Error deleting role map: {e}")
            return {"status": "error", "message": str(e)}
    
    def configure_user_persona(self, persona_config: Dict) -> Dict:
        """
        Configure a user persona in the Application Layer.
        
        Args:
            persona_config: User persona configuration
            
        Returns:
            Dict: Configuration results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/personas/configure", json=persona_config)
            return response
        except Exception as e:
            logger.error(f"Error configuring user persona: {e}")
            return {"status": "error", "message": str(e)}
    
    def delete_user_persona(self, persona_id: str) -> Dict:
        """
        Delete a user persona from the Application Layer.
        
        Args:
            persona_id: ID of the user persona to delete
            
        Returns:
            Dict: Deletion results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("DELETE", f"/personas/{persona_id}")
            return response
        except Exception as e:
            logger.error(f"Error deleting user persona: {e}")
            return {"status": "error", "message": str(e)}
    
    def deploy(self, config: Dict) -> Dict:
        """
        Deploy Application Layer components.
        
        Args:
            config: Deployment configuration
            
        Returns:
            Dict: Deployment results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            # Configure role maps
            role_map_results = {}
            for role_map in config.get("role_maps", []):
                role_map_result = self.configure_role_map(role_map)
                role_map_results[role_map.get("name", "unnamed")] = role_map_result
            
            # Configure user personas
            persona_results = {}
            for persona in config.get("personas", []):
                persona_result = self.configure_user_persona(persona)
                persona_results[persona.get("name", "unnamed")] = persona_result
            
            # Deploy UI capsules
            capsule_results = {}
            for capsule in config.get("ui_capsules", []):
                capsule_result = self.deploy_ui_capsule(capsule)
                capsule_results[capsule.get("name", "unnamed")] = capsule_result
            
            return {
                "status": "success",
                "message": "Application Layer deployment completed",
                "deployment_id": f"application-layer-{int(time.time())}",
                "results": {
                    "role_maps": role_map_results,
                    "personas": persona_results,
                    "ui_capsules": capsule_results
                }
            }
        except Exception as e:
            logger.error(f"Error deploying Application Layer components: {e}")
            return {"status": "error", "message": str(e)}
    
    def rollback(self, deployment_id: Optional[str] = None) -> Dict:
        """
        Rollback an Application Layer deployment.
        
        Args:
            deployment_id: ID of the deployment to rollback
            
        Returns:
            Dict: Rollback results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/rollback", json={"deployment_id": deployment_id})
            return response
        except Exception as e:
            logger.error(f"Error rolling back Application Layer deployment: {e}")
            return {"status": "error", "message": str(e)}
    
    def update(self, config: Dict) -> Dict:
        """
        Update Application Layer components.
        
        Args:
            config: Update configuration
            
        Returns:
            Dict: Update results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/update", json=config)
            return response
        except Exception as e:
            logger.error(f"Error updating Application Layer components: {e}")
            return {"status": "error", "message": str(e)}
    
    def rollback_update(self, update_id: str) -> Dict:
        """
        Rollback an Application Layer update.
        
        Args:
            update_id: ID of the update to rollback
            
        Returns:
            Dict: Rollback results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/rollback-update", json={"update_id": update_id})
            return response
        except Exception as e:
            logger.error(f"Error rolling back Application Layer update: {e}")
            return {"status": "error", "message": str(e)}
    
    def sync(self, params: Dict) -> Dict:
        """
        Synchronize with the Application Layer.
        
        Args:
            params: Synchronization parameters
            
        Returns:
            Dict: Synchronization results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Application Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/sync", json=params)
            return response
        except Exception as e:
            logger.error(f"Error synchronizing with Application Layer: {e}")
            return {"status": "error", "message": str(e)}
    
    def _make_request(self, method: str, path: str, **kwargs) -> Dict:
        """
        Make an HTTP request to the Application Layer API.
        
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
