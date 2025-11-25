import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CapsuleController:
    """
    Kubernetes Controller for 'SovereignCapsule' CRDs.
    Reconciles the desired state of capsules in the cluster.
    """
    
    def __init__(self):
        self.capsule_cache: Dict[str, Any] = {}

    def reconcile(self, capsule_manifest: Dict[str, Any]):
        """
        Reconcile a single capsule manifest.
        """
        metadata = capsule_manifest.get("metadata", {})
        spec = capsule_manifest.get("spec", {})
        name = metadata.get("name")
        
        logger.info(f"Reconciling Capsule: {name}")
        
        # 1. Validate Spec
        if not self._validate_spec(spec):
            logger.error(f"Invalid spec for {name}")
            return {"status": "Error", "message": "Invalid Spec"}
            
        # 2. Check if Deployment exists (Mock K8s API call)
        # In real code: k8s_client.read_namespaced_deployment(...)
        deployment_exists = self._mock_check_deployment(name)
        
        if not deployment_exists:
            logger.info(f"Creating Deployment for {name}...")
            self._mock_create_deployment(name, spec)
        else:
            logger.info(f"Updating Deployment for {name}...")
            self._mock_update_deployment(name, spec)
            
        # 3. Update Status
        return {"status": "Ready", "replicas": spec.get("replicas", 1)}

    def _validate_spec(self, spec: Dict[str, Any]) -> bool:
        required = ["image", "capsule_id", "energy_budget"]
        return all(k in spec for k in required)

    def _mock_check_deployment(self, name: str) -> bool:
        return name in self.capsule_cache

    def _mock_create_deployment(self, name: str, spec: Dict[str, Any]):
        self.capsule_cache[name] = spec
        logger.info(f"Deployment {name} created with image {spec.get('image')}")

    def _mock_update_deployment(self, name: str, spec: Dict[str, Any]):
        self.capsule_cache[name] = spec
        logger.info(f"Deployment {name} updated.")
