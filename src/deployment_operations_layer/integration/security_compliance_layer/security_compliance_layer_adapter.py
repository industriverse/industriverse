"""
Security & Compliance Layer Adapter for the Deployment Operations Layer.

This module provides integration with the Security & Compliance Layer, enabling the Deployment Operations Layer
to pre-validate capsule lineage and crypto zone compliance.
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

class SecurityComplianceLayerAdapter:
    """
    Adapter for integration with the Security & Compliance Layer.
    
    This class provides methods for interacting with the Security & Compliance Layer, including
    pre-validating capsule lineage, verifying crypto zone compliance, and monitoring trust scores.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Security & Compliance Layer Adapter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.endpoint = config.get("endpoint", "http://localhost:8008")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.enabled = config.get("enabled", True)
        
        logger.info("Security & Compliance Layer Adapter initialized")
    
    def check_health(self) -> Dict:
        """
        Check the health of the Security & Compliance Layer.
        
        Returns:
            Dict: Health status information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/health")
            return response
        except Exception as e:
            logger.error(f"Error checking Security & Compliance Layer health: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_version(self) -> Dict:
        """
        Get the version of the Security & Compliance Layer.
        
        Returns:
            Dict: Version information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/version")
            return response
        except Exception as e:
            logger.error(f"Error getting Security & Compliance Layer version: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities of the Security & Compliance Layer.
        
        Returns:
            Dict: Capabilities information
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("GET", "/capabilities")
            return response
        except Exception as e:
            logger.error(f"Error getting Security & Compliance Layer capabilities: {e}")
            return {"status": "error", "message": str(e)}
    
    def validate_capsule_lineage(self, lineage_config: Dict) -> Dict:
        """
        Pre-validate capsule lineage.
        
        Args:
            lineage_config: Lineage configuration
            
        Returns:
            Dict: Validation results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/capsules/validate-lineage", json=lineage_config)
            return response
        except Exception as e:
            logger.error(f"Error validating capsule lineage: {e}")
            return {"status": "error", "message": str(e)}
    
    def verify_crypto_zone_compliance(self, compliance_config: Dict) -> Dict:
        """
        Verify crypto zone compliance.
        
        Args:
            compliance_config: Compliance configuration
            
        Returns:
            Dict: Verification results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/crypto-zones/verify-compliance", json=compliance_config)
            return response
        except Exception as e:
            logger.error(f"Error verifying crypto zone compliance: {e}")
            return {"status": "error", "message": str(e)}
    
    def monitor_trust_score(self, trust_config: Dict) -> Dict:
        """
        Monitor trust score.
        
        Args:
            trust_config: Trust configuration
            
        Returns:
            Dict: Monitoring results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/trust/monitor", json=trust_config)
            return response
        except Exception as e:
            logger.error(f"Error monitoring trust score: {e}")
            return {"status": "error", "message": str(e)}
    
    def verify_zero_knowledge_attestation(self, attestation_config: Dict) -> Dict:
        """
        Verify zero-knowledge attestation.
        
        Args:
            attestation_config: Attestation configuration
            
        Returns:
            Dict: Verification results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/zk-attestation/verify", json=attestation_config)
            return response
        except Exception as e:
            logger.error(f"Error verifying zero-knowledge attestation: {e}")
            return {"status": "error", "message": str(e)}
    
    def configure_security_policy(self, policy_config: Dict) -> Dict:
        """
        Configure security policy.
        
        Args:
            policy_config: Policy configuration
            
        Returns:
            Dict: Configuration results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/policies/configure", json=policy_config)
            return response
        except Exception as e:
            logger.error(f"Error configuring security policy: {e}")
            return {"status": "error", "message": str(e)}
    
    def delete_security_policy(self, policy_id: str) -> Dict:
        """
        Delete security policy.
        
        Args:
            policy_id: ID of the policy to delete
            
        Returns:
            Dict: Deletion results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("DELETE", f"/policies/{policy_id}")
            return response
        except Exception as e:
            logger.error(f"Error deleting security policy: {e}")
            return {"status": "error", "message": str(e)}
    
    def deploy(self, config: Dict) -> Dict:
        """
        Deploy Security & Compliance Layer components.
        
        Args:
            config: Deployment configuration
            
        Returns:
            Dict: Deployment results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            # Pre-validate capsule lineage
            lineage_results = {}
            for lineage in config.get("capsule_lineages", []):
                lineage_result = self.validate_capsule_lineage(lineage)
                lineage_results[lineage.get("name", "unnamed")] = lineage_result
                
                # Check if validation was successful
                if lineage_result.get("status") != "success":
                    return {
                        "status": "error",
                        "message": f"Capsule lineage validation failed for {lineage.get('name', 'unnamed')}",
                        "lineage_results": lineage_results
                    }
            
            # Verify crypto zone compliance
            compliance_results = {}
            for compliance in config.get("crypto_zone_compliances", []):
                compliance_result = self.verify_crypto_zone_compliance(compliance)
                compliance_results[compliance.get("name", "unnamed")] = compliance_result
                
                # Check if verification was successful
                if compliance_result.get("status") != "success":
                    return {
                        "status": "error",
                        "message": f"Crypto zone compliance verification failed for {compliance.get('name', 'unnamed')}",
                        "compliance_results": compliance_results
                    }
            
            # Configure security policies
            policy_results = {}
            for policy in config.get("security_policies", []):
                policy_result = self.configure_security_policy(policy)
                policy_results[policy.get("name", "unnamed")] = policy_result
            
            # Set up trust score monitoring
            trust_results = {}
            for trust in config.get("trust_monitors", []):
                trust_result = self.monitor_trust_score(trust)
                trust_results[trust.get("name", "unnamed")] = trust_result
            
            # Verify zero-knowledge attestations
            attestation_results = {}
            for attestation in config.get("zk_attestations", []):
                attestation_result = self.verify_zero_knowledge_attestation(attestation)
                attestation_results[attestation.get("name", "unnamed")] = attestation_result
            
            return {
                "status": "success",
                "message": "Security & Compliance Layer deployment completed",
                "deployment_id": f"security-compliance-layer-{int(time.time())}",
                "results": {
                    "capsule_lineages": lineage_results,
                    "crypto_zone_compliances": compliance_results,
                    "security_policies": policy_results,
                    "trust_monitors": trust_results,
                    "zk_attestations": attestation_results
                }
            }
        except Exception as e:
            logger.error(f"Error deploying Security & Compliance Layer components: {e}")
            return {"status": "error", "message": str(e)}
    
    def rollback(self, deployment_id: Optional[str] = None) -> Dict:
        """
        Rollback a Security & Compliance Layer deployment.
        
        Args:
            deployment_id: ID of the deployment to rollback
            
        Returns:
            Dict: Rollback results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/rollback", json={"deployment_id": deployment_id})
            return response
        except Exception as e:
            logger.error(f"Error rolling back Security & Compliance Layer deployment: {e}")
            return {"status": "error", "message": str(e)}
    
    def update(self, config: Dict) -> Dict:
        """
        Update Security & Compliance Layer components.
        
        Args:
            config: Update configuration
            
        Returns:
            Dict: Update results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/update", json=config)
            return response
        except Exception as e:
            logger.error(f"Error updating Security & Compliance Layer components: {e}")
            return {"status": "error", "message": str(e)}
    
    def rollback_update(self, update_id: str) -> Dict:
        """
        Rollback a Security & Compliance Layer update.
        
        Args:
            update_id: ID of the update to rollback
            
        Returns:
            Dict: Rollback results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/deployment/rollback-update", json={"update_id": update_id})
            return response
        except Exception as e:
            logger.error(f"Error rolling back Security & Compliance Layer update: {e}")
            return {"status": "error", "message": str(e)}
    
    def sync(self, params: Dict) -> Dict:
        """
        Synchronize with the Security & Compliance Layer.
        
        Args:
            params: Synchronization parameters
            
        Returns:
            Dict: Synchronization results
        """
        if not self.enabled:
            return {"status": "disabled", "message": "Security & Compliance Layer integration is disabled"}
        
        try:
            response = self._make_request("POST", "/sync", json=params)
            return response
        except Exception as e:
            logger.error(f"Error synchronizing with Security & Compliance Layer: {e}")
            return {"status": "error", "message": str(e)}
    
    def _make_request(self, method: str, path: str, **kwargs) -> Dict:
        """
        Make an HTTP request to the Security & Compliance Layer API.
        
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
