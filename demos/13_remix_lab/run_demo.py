import json
import hashlib
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class RemixEngine:
    def __init__(self):
        pass

    def remix(self, parent_a, parent_b, new_name):
        logger.info(f"Remixing '{parent_a['name']}' + '{parent_b['name']}' -> '{new_name}'")
        
        # 1. Merge Capabilities
        capabilities = list(set(parent_a['capabilities'] + parent_b['capabilities']))
        
        # 2. Merge Requirements
        requirements = list(set(parent_a.get('requirements', []) + parent_b.get('requirements', [])))
        
        # 3. Generate Lineage Proof
        lineage_data = f"{parent_a['utid']}:{parent_b['utid']}:{time.time()}"
        lineage_hash = hashlib.sha256(lineage_data.encode()).hexdigest()
        
        # 4. Create New Manifest
        new_manifest = {
            "name": new_name,
            "utid": f"remix_{lineage_hash[:8]}",
            "version": "1.0.0",
            "parents": [parent_a['utid'], parent_b['utid']],
            "capabilities": capabilities,
            "requirements": requirements,
            "lineage_proof": lineage_hash,
            "remixed_at": time.time()
        }
        
        return new_manifest

def run():
    print("\n" + "="*60)
    print(" DEMO 13: THE REMIX LAB")
    print("="*60 + "\n")

    engine = RemixEngine()

    # Define Parent Capsules
    sensor_capsule = {
        "name": "Industrial Thermometer",
        "utid": "capsule_sensor_v1_123",
        "capabilities": ["measure_temp", "emit_telemetry"],
        "requirements": ["power_5v"]
    }
    
    logger_capsule = {
        "name": "Secure Logger",
        "utid": "capsule_logger_v1_456",
        "capabilities": ["log_to_blockchain", "encrypt_data"],
        "requirements": ["network_access"]
    }

    print("--- Source Capsules ---")
    print(f"Parent A: {sensor_capsule['name']} ({sensor_capsule['capabilities']})")
    print(f"Parent B: {logger_capsule['name']} ({logger_capsule['capabilities']})")

    print("\n--- Executing Remix ---")
    remixed_capsule = engine.remix(sensor_capsule, logger_capsule, "Smart Secure Thermometer")

    print("\n--- Resulting Capsule ---")
    print(json.dumps(remixed_capsule, indent=2))

    print("\n--- Verification ---")
    if "measure_temp" in remixed_capsule['capabilities'] and "log_to_blockchain" in remixed_capsule['capabilities']:
        print("SUCCESS: Capabilities merged.")
    
    if len(remixed_capsule['parents']) == 2:
        print("SUCCESS: Lineage preserved.")
        
    print(f"SUCCESS: New UTID generated: {remixed_capsule['utid']}")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: REMIX SUCCESSFUL")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
