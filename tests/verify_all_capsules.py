import sys
import os
import requests
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/v1/capsules"
HEADERS = {
    "X-UTID": "UTID:REAL:BROWSER:DASHBOARD:20251124:nonce"
}

def verify_capsules():
    logger.info("Starting Comprehensive Capsule Verification...")

    # 1. List all capsules
    try:
        response = requests.get(f"{BASE_URL}/", headers=HEADERS)
        response.raise_for_status()
        capsules = response.json()
        logger.info(f"✅ Successfully fetched capsule list. Total count: {len(capsules)}")
        
        if len(capsules) != 27:
            logger.error(f"❌ Expected 27 capsules, found {len(capsules)}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Failed to list capsules: {e}")
        sys.exit(1)

    # 2. Verify each capsule
    success_count = 0
    for cap in capsules:
        cap_id = cap['id']
        name = cap['name']
        logger.info(f"Verifying {name} ({cap_id})...")
        
        # A. Check Topology
        try:
            topo_res = requests.get(f"{BASE_URL}/{cap_id}/topology", headers=HEADERS)
            topo_res.raise_for_status()
            logger.info(f"  - Topology: OK")
        except Exception as e:
            logger.error(f"  - Topology: FAILED ({e})")
            continue

        # B. Trigger Execution (Ignite)
        try:
            payload = {
                "capsule_id": cap_id,
                "payload": {"action": "test_verification"},
                "priority": "normal"
            }
            exec_res = requests.post(f"{BASE_URL}/execute", json=payload, headers=HEADERS)
            exec_res.raise_for_status()
            data = exec_res.json()
            
            if data['status'] == 'queued' and 'utid' in data:
                logger.info(f"  - Execution: OK (UTID: {data['utid']})")
                success_count += 1
            else:
                logger.error(f"  - Execution: FAILED (Invalid response: {data})")
                
        except Exception as e:
            logger.error(f"  - Execution: FAILED ({e})")

    logger.info("-" * 40)
    if success_count == 27:
        logger.info("✅ ALL 27 CAPSULES VERIFIED SUCCESSFULLY")
    else:
        logger.error(f"❌ VERIFICATION INCOMPLETE: {success_count}/27 passed")
        sys.exit(1)

if __name__ == "__main__":
    verify_capsules()
