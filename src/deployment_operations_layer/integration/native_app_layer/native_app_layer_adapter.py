"""
Native App Layer Adapter for the Deployment Operations Layer.

This module provides integration with the Native App Layer, enabling the Deployment Operations Layer
to bridge to mobile/edge capsules with push-channel registry management.
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

class NativeAppLayerAdapter:
    """
    Adapter for integration with the Native App Layer.
    
    This class provides methods for interacting with the Native App Layer, including
    bridging to mobile/edge capsules, managing push-channel registry, and configuring
    escalation routes.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Native App Layer Adapter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.endpoint = config.get("endpoint", "http://localhost:8009")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.enabled = config.get("enabled", True)
        
        logger.info("Native App Layer Adapter initialized")
    
    def check_health(self) -> Dict:
        """
        Check the health of the Native App Layer.
        
        Returns:
            Dict: Health status information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/health")
            return response
        except Exception as e:
            logger.error(f"Error checking Native App Layer health: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_version(self) -> Dict:
        """
        Get the version of the Native App Layer.
        
        Returns:
            Dict: Version information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/version")
            return response
        except Exception as e:
            logger.error(f"Error getting Native App Layer version: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities of the Native App Layer.
        
        Returns:
            Dict: Capabilities information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/capabilities")
            return response
        except Exception as e:
            logger.error(f"Error getting Native App Layer capabilities: {e}")
            return {"status": "error", "message": str(e)}
    
    def bridge_mobile_capsule(self, capsule_config: Dict) -> Dict:
        """
        Bridge to a mobile capsule.
        
        Args:
            capsule_config: Mobile capsule configuration
            
        Returns:
            Dict: Bridging results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/capsules/mobile/bridge", json=capsule_config)
            return response
        except Exception as e:
            logger.error(f"Error bridging mobile capsule: {e}")
            return {"status": "error", "message": str(e)}
    
    def bridge_edge_capsule(self, capsule_config: Dict) -> Dict:
        """
        Bridge to an edge capsule.
        
        Args:
            capsule_config: Edge capsule configuration
            
        Returns:
            Dict: Bridging results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/capsules/edge/bridge", json=capsule_config)
            return response
        except Exception as e:
            logger.error(f"Error bridging edge capsule: {e}")
            return {"status": "error", "message": str(e)}
    
    def unbridged_capsule(self, capsule_id: str) -> Dict:
        """
        Unbridge a capsule.
        
        Args:
            capsule_id: ID of the capsule to unbridge
            
        Returns:
            Dict: Unbridging results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", f"/capsules/{capsule_id}/unbridge")
            return response
        except Exception as e:
            logger.error(f"Error unbridging capsule: {e}")
            return {"status": "error", "message": str(e)}
    
    def register_push_channel(self, channel_config: Dict) -> Dict:
        """
        Register a push channel.
        
        Args:
            channel_config: Push channel configuration
            
        Returns:
            Dict: Registration results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/push-channels/register", json=channel_config)
            return response
        except Exception as e:
            logger.error(f"Error registering push channel: {e}")
            return {"status": "error", "message": str(e)}
    
    def unregister_push_channel(self, channel_id: str) -> Dict:
        """
        Unregister a push channel.
        
        Args:
            channel_id: ID of the push channel to unregister
            
        Returns:
            Dict: Unregistration results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", f"/push-channels/{channel_id}/unregister")
            return response
        except Exception as e:
            logger.error(f"Error unregistering push channel: {e}")
            return {"status": "error", "message": str(e)}
    
    def configure_escalation_route(self, route_config: Dict) -> Dict:
        """
        Configure an escalation route.
        
        Args:
            route_config: Escalation route configuration
            
        Returns:
            Dict: Configuration results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/escalation-routes/configure", json=route_config)
            return response
        except Exception as e:
            logger.error(f"Error configuring escalation route: {e}")
            return {"status": "error", "message": str(e)}
    
    def delete_escalation_route(self, route_id: str) -> Dict:
        """
        Delete an escalation route.
        
        Args:
            route_id: ID of the escalation route to delete
            
        Returns:
            Dict: Deletion results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("DELETE", f"/escalation-routes/{route_id}")
            return response
        except Exception as e:
            logger.error(f"Error deleting escalation route: {e}")
            return {"status": "error", "message": str(e)}
    
    def configure_offline_sync(self, sync_config: Dict) -> Dict:
        """
        Configure offline synchronization.
        
        Args:
            sync_config: Offline synchronization configuration
            
        Returns:
            Dict: Configuration results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/offline-sync/configure", json=sync_config)
            return response
        except Exception as e:
            logger.error(f"Error configuring offline synchronization: {e}")
            return {"status": "error", "message": str(e)}
    
    def deploy(self, config: Dict) -> Dict:
        """
        Deploy Native App Layer components.
        
        Args:
            config: Deployment configuration
            
        Returns:
            Dict: Deployment results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            # Bridge mobile capsules
            mobile_results = {}
            for capsule in config.get("mobile_capsules", []):
                capsule_result = self.bridge_mobile_capsule(capsule)
                mobile_results[capsule.get("name", "unnamed")] = capsule_result
            
            # Bridge edge capsules
            edge_results = {}
            for capsule in config.get("edge_capsules", []):
                capsule_result = self.bridge_edge_capsule(capsule)
                edge_results[capsule.get("name", "unnamed")] = capsule_result
            
            # Register push channels
            channel_results = {}
            for channel in config.get("push_channels", []):
                channel_result = self.register_push_channel(channel)
                channel_results[channel.get("name", "unnamed")] = channel_result
            
            # Configure escalation routes
            route_results = {}
            for route in config.get("escalation_routes", []):
                route_result = self.configure_escalation_route(route)
                route_results[route.get("name", "unnamed")] = route_result
            
            # Configure offline synchronization
            sync_results = {}
            for sync in config.get("offline_syncs", []):
                sync_result = self.configure_offline_sync(sync)
                sync_results[sync.get("name", "unnamed")] = sync_result
            
            return {
                "status": "success",
                "message": "Native App Layer deployment completed",
                "deployment_id": f"native-app-layer-{int(time.time())}",
                "results": {
                    "mobile_capsules": mobile_results,
                    "edge_capsules": edge_results,
                    "push_channels": channel_results,
                    "escalation_routes": route_results,
                    "offline_syncs": sync_results
                }
            }
        except Exception as e:
            logger.error(f"Error deploying Native App Layer components: {e}")
            return {"status": "error", "message": str(e)}
    
    def rollback(self, deployment_id: Optional[str] = None) -> Dict:
        """
        Rollback a Native App Layer deployment.
        
        Args:
            deployment_id: ID of the deployment to rollback
            
        Returns:
            Dict: Rollback results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/rollback", json={"deployment_id": deployment_id})
            return response
        except Exception as e:
            logger.error(f"Error rolling back Native App Layer deployment: {e}")
            return {"status": "error", "message": str(e)}
    
    def update(self, config: Dict) -> Dict:
        """
        Update Native App Layer components.
        
        Args:
            config: Update configuration
            
        Returns:
            Dict: Update results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/update", json=config)
            return response
        except Exception as e:
            logger.error(f"Error updating Native App Layer components: {e}")
            return {"status": "error", "message": str(e)}
    
    def rollback_update(self, update_id: str) -> Dict:
        """
        Rollback a Native App Layer update.
        
        Args:
            update_id: ID of the update to rollback
            
        Returns:
            Dict: Rollback results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/rollback-update", json={"update_id": update_id})
            return response
        except Exception as e:
            logger.error(f"Error rolling back Native App Layer update: {e}")
            return {"status": "error", "message": str(e)}
    
    def sync(self, params: Dict) -> Dict:
        """
        Synchronize with the Native App Layer.
        
        Args:
            params: Synchronization parameters
            
        Returns:
            Dict: Synchronization results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Native App Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/sync", json=params)
            return response
        except Exception as e:
            logger.error(f"Error synchronizing with Native App Layer: {e}")
            return {"status": "error", "message": str(e)}
    
    def _make_request(self, method: str, path: str, **kwargs) -> Dict:
        """
        Make an HTTP request to the Native App Layer API.
        
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
