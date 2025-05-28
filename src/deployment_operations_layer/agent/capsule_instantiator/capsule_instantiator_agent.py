"""
Capsule Instantiator Agent

This agent is responsible for translating deployment manifests into real capsules.
It coordinates with the capsule blueprint manager, factory, validator, and registry
to create, validate, and register capsules for deployment.

The agent ensures that capsules are created according to specifications, validated
against security and compliance requirements, and properly registered with lineage
tracking.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any

from .capsule_blueprint_manager import CapsuleBlueprintManager
from .capsule_factory import CapsuleFactory
from .capsule_validator import CapsuleValidator
from .capsule_registry_client import CapsuleRegistryClient

logger = logging.getLogger(__name__)

class CapsuleInstantiatorAgent:
    """
    Agent responsible for instantiating capsules from deployment manifests.
    """
    
    def __init__(self, 
                 blueprint_manager: Optional[CapsuleBlueprintManager] = None,
                 capsule_factory: Optional[CapsuleFactory] = None,
                 capsule_validator: Optional[CapsuleValidator] = None,
                 registry_client: Optional[CapsuleRegistryClient] = None):
        """
        Initialize the Capsule Instantiator Agent.
        
        Args:
            blueprint_manager: Manager for capsule blueprints
            capsule_factory: Factory for creating capsules
            capsule_validator: Validator for capsule configurations
            registry_client: Client for interacting with capsule registry
        """
        self.blueprint_manager = blueprint_manager or CapsuleBlueprintManager()
        self.capsule_factory = capsule_factory or CapsuleFactory()
        self.capsule_validator = capsule_validator or CapsuleValidator()
        self.registry_client = registry_client or CapsuleRegistryClient()
        self.instantiation_history = {}
        logger.info("Capsule Instantiator Agent initialized")
    
    def instantiate_capsule(self, 
                           manifest: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Instantiate a capsule from a deployment manifest.
        
        Args:
            manifest: Deployment manifest containing capsule specifications
            context: Deployment context including environment, trust zones, etc.
            
        Returns:
            Dict containing the instantiated capsule details
        """
        logger.info(f"Instantiating capsule from manifest: {manifest.get('name', 'unnamed')}")
        
        # Generate a unique ID for this instantiation
        instantiation_id = str(uuid.uuid4())
        self.instantiation_history[instantiation_id] = {
            "status": "started",
            "manifest": manifest,
            "context": context,
            "timestamp": {
                "start": self._get_timestamp()
            }
        }
        
        try:
            # Get the appropriate blueprint
            blueprint = self.blueprint_manager.get_blueprint(
                manifest.get("blueprint_type"),
                manifest.get("blueprint_version")
            )
            
            # Create the capsule from the blueprint
            capsule = self.capsule_factory.create_capsule(blueprint, manifest, context)
            
            # Validate the capsule
            validation_result = self.capsule_validator.validate_capsule(capsule, context)
            if not validation_result["valid"]:
                logger.error(f"Capsule validation failed: {validation_result['errors']}")
                self._update_instantiation_status(instantiation_id, "failed", {
                    "errors": validation_result["errors"]
                })
                return {
                    "success": False,
                    "instantiation_id": instantiation_id,
                    "errors": validation_result["errors"]
                }
            
            # Register the capsule
            registry_result = self.registry_client.register_capsule(capsule)
            
            # Update instantiation history
            self._update_instantiation_status(instantiation_id, "completed", {
                "capsule_id": registry_result["capsule_id"],
                "registry_result": registry_result
            })
            
            return {
                "success": True,
                "instantiation_id": instantiation_id,
                "capsule_id": registry_result["capsule_id"],
                "capsule": capsule
            }
            
        except Exception as e:
            logger.exception(f"Error instantiating capsule: {str(e)}")
            self._update_instantiation_status(instantiation_id, "failed", {
                "error": str(e)
            })
            return {
                "success": False,
                "instantiation_id": instantiation_id,
                "error": str(e)
            }
    
    def batch_instantiate_capsules(self, 
                                  manifests: List[Dict[str, Any]], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Instantiate multiple capsules from deployment manifests.
        
        Args:
            manifests: List of deployment manifests
            context: Deployment context
            
        Returns:
            Dict containing results of batch instantiation
        """
        logger.info(f"Batch instantiating {len(manifests)} capsules")
        
        results = {
            "success": True,
            "total": len(manifests),
            "successful": 0,
            "failed": 0,
            "capsules": []
        }
        
        for manifest in manifests:
            result = self.instantiate_capsule(manifest, context)
            results["capsules"].append(result)
            
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["success"] = False
        
        return results
    
    def get_instantiation_status(self, instantiation_id: str) -> Dict[str, Any]:
        """
        Get the status of a capsule instantiation.
        
        Args:
            instantiation_id: ID of the instantiation
            
        Returns:
            Dict containing the instantiation status
        """
        if instantiation_id not in self.instantiation_history:
            return {"error": "Instantiation ID not found"}
        
        return self.instantiation_history[instantiation_id]
    
    def _update_instantiation_status(self, 
                                    instantiation_id: str, 
                                    status: str, 
                                    details: Dict[str, Any] = None):
        """
        Update the status of a capsule instantiation.
        
        Args:
            instantiation_id: ID of the instantiation
            status: New status
            details: Additional details to add to the history
        """
        if instantiation_id in self.instantiation_history:
            self.instantiation_history[instantiation_id]["status"] = status
            
            if status in ["completed", "failed"]:
                self.instantiation_history[instantiation_id]["timestamp"]["end"] = self._get_timestamp()
            
            if details:
                self.instantiation_history[instantiation_id].update(details)
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
