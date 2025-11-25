import sys
import os
import json
import logging
from datetime import datetime
import hashlib

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from capsule_layer.capsule_definitions import ALL_CAPSULES
from thermodynamic_layer.energy_atlas import EnergyAtlas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TopologyGenerator")

def generate_signature(capsule, energy_atlas):
    """Generate a topology signature for a capsule."""
    
    # Ensure energy map exists (triggers mock generation if needed)
    energy_map = energy_atlas.get_map(capsule.energy_prior_file)
    map_shape = energy_map.shape if energy_map is not None else "UNKNOWN"
    
    # Create signature payload
    payload = {
        "capsule_id": capsule.capsule_id,
        "name": capsule.name,
        "category": capsule.category.value,
        "physics_topology": capsule.physics_topology,
        "domain_equations": capsule.domain_equations,
        "energy_prior": {
            "file": capsule.energy_prior_file,
            "shape": str(map_shape)
        },
        "prin_config": capsule.prin_config.dict(),
        "generated_at": datetime.utcnow().isoformat(),
        "version": "1.0"
    }
    
    # Calculate hash (simulating a signature)
    payload_str = json.dumps(payload, sort_keys=True)
    sig_hash = hashlib.sha256(payload_str.encode()).hexdigest()
    
    payload["signature"] = f"sig:{sig_hash[:16]}"
    
    return payload

def main():
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    energy_atlas = EnergyAtlas()
    signatures = []
    
    logger.info(f"Generating signatures for {len(ALL_CAPSULES)} capsules...")
    
    for capsule in ALL_CAPSULES:
        logger.info(f"Processing {capsule.capsule_id}...")
        sig = generate_signature(capsule, energy_atlas)
        signatures.append(sig)
        
    output_file = os.path.join(output_dir, "topology_signatures.json")
    with open(output_file, 'w') as f:
        json.dump(signatures, f, indent=2)
        
    logger.info(f"Successfully generated {len(signatures)} signatures in {output_file}")

if __name__ == "__main__":
    main()
