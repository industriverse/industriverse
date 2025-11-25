import sys
import os
import logging
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch

# Add src and project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bridge_api.server import app
from infra.operator.kaa_operator.controllers.capsule_controller import CapsuleController
from capsule_layer.capsule_definitions import CAPSULE_REGISTRY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyPhase4")

def test_end_to_end_integration():
    logger.info("=== Starting Phase 4 End-to-End Verification ===")
    
    # Mock UTID Verification
    with patch("src.bridge_api.security.real_utid_service.RealUTIDService.verify", return_value=True):
        client = TestClient(app, headers={"X-UTID": "UTID:REAL:MOCK:TEST"})
    
        # 1. Verify BridgeAPI Capsule Listing
        logger.info("Step 1: Testing BridgeAPI List Capsules...")
        response = client.get("/v1/capsules/")
        logger.info(f"Response Status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Response Content: {response.text}")
        assert response.status_code == 200
        capsules = response.json()
        assert len(capsules) == 27
        logger.info(f"Successfully listed {len(capsules)} capsules.")
        
        # 2. Verify Specific Capsule Topology
        target_capsule = "capsule:rawmat:v1"
        logger.info(f"Step 2: Verifying Topology for {target_capsule}...")
        response = client.get(f"/v1/capsules/{target_capsule}/topology")
        assert response.status_code == 200
        topology = response.json()
        assert "physics_topology" in topology
        assert "energy_prior" in topology
        logger.info("Topology verification successful.")
        
        # 3. Verify Capsule Execution (Trigger ACE + UTID)
        logger.info(f"Step 3: Triggering Execution for {target_capsule}...")
        payload = {
            "capsule_id": target_capsule,
            "payload": {"query": "optimize_extraction"},
            "priority": "high"
        }
        response = client.post("/v1/capsules/execute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "utid" in data
        assert data["utid"].startswith("UTID:REAL")
        logger.info(f"Execution triggered. UTID: {data['utid']}")
        
        # 4. Verify Kube Operator Controller
        logger.info("Step 4: Verifying Kube Operator Controller...")
        controller = CapsuleController()
        manifest = {
            "metadata": {"name": "rawmat-capsule-prod"},
            "spec": {
                "capsule_id": target_capsule,
                "image": "industriverse/capsule-rawmat:v1",
                "replicas": 3,
                "energy_budget": "1000J"
            }
        }
        result = controller.reconcile(manifest)
        assert result["status"] == "Ready"
        assert result["replicas"] == 3
        logger.info("Controller reconciliation successful.")
        
        logger.info("=== Phase 4 Verification COMPLETE: ALL SYSTEMS GO ===")
    print("VERIFICATION SUCCESS")

if __name__ == "__main__":
    test_end_to_end_integration()
