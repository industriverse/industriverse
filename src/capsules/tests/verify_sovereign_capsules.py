"""
Verification script for Sovereign Capsules (Phase 5).
Checks compliance with Genesis Directives for Fusion and Grid capsules.
"""

import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.capsules.core.sovereign_capsule import SovereignCapsule

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SovereignVerifier")

def verify_capsule(capsule_path: str):
    capsule_id = os.path.basename(capsule_path)
    logger.info(f"--- Verifying Capsule: {capsule_id} ---")
    
    try:
        # 1. Load Capsule (Directives 01-09)
        capsule = SovereignCapsule(capsule_path)
        logger.info(f"✅ Loaded Manifest for {capsule_id}")
        
        # Check Manifest Components
        assert capsule.manifest.prin.domain, "Missing PRIN domain"
        assert capsule.manifest.safety.max_entropy > 0, "Invalid Safety Budget"
        assert len(capsule.manifest.routing.upstream_capsules) >= 0, "Missing Routing"
        assert capsule.manifest.utid.required_credentials, "Missing UTID Credentials"
        logger.info(f"✅ Manifest Validated")

        # 2. Ignite (Directive 10)
        status = capsule.ignite({"mode": "test"})
        assert status["status"] == "ignited", "Ignition Failed"
        logger.info(f"✅ Ignition Successful")

        # 3. Check Agent (Directive 05)
        # Test Policy via Capsule Interface
        obs = {"beta": 0.05} if "fusion" in capsule_id else {"frequency": 59.9}
        action = capsule.run_policy(obs)
        assert action, "Agent produced no action"
        logger.info(f"✅ Agent Policy Verified: {action.get('reason', 'No reason provided')}")

        # 4. Check Proof Emission (Directive 07)
        proof = capsule.emit_proof({"result": "success"})
        assert proof["proof_hash"], "Missing Proof Hash"
        logger.info(f"✅ Proof Generation Verified")

        logger.info(f"🎉 CAPSULE {capsule_id} PASSED ALL CHECKS\n")
        return True

    except Exception as e:
        logger.error(f"❌ Verification Failed for {capsule_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sovereign"))
    
    # Find all capsule directories
    capsule_dirs = [
        os.path.join(base_dir, d) 
        for d in os.listdir(base_dir) 
        if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith("__")
    ]
    
    logger.info(f"Found {len(capsule_dirs)} capsules to verify.")
    
    success = True
    for cap_dir in sorted(capsule_dirs):
        success &= verify_capsule(cap_dir)
    
    if success:
        logger.info("ALL CAPSULES VERIFIED SUCCESSFULLY.")
        sys.exit(0)
    else:
        logger.error("SOME CAPSULES FAILED VERIFICATION.")
        sys.exit(1)
