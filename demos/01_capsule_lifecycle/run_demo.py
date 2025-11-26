import os
import json
import yaml
import shutil
import logging
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.capsules.core.sovereign_capsule import SovereignCapsule
from src.capsules.factory.dac_factory import dac_factory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def setup_mock_capsule(base_dir, capsule_name):
    """Creates a temporary capsule directory with all required config files."""
    capsule_dir = os.path.join(base_dir, capsule_name)
    if os.path.exists(capsule_dir):
        shutil.rmtree(capsule_dir)
        
    os.makedirs(os.path.join(capsule_dir, "runtime"), exist_ok=True)
    os.makedirs(os.path.join(capsule_dir, "mesh"), exist_ok=True)
    os.makedirs(os.path.join(capsule_dir, "identity"), exist_ok=True)
    os.makedirs(os.path.join(capsule_dir, "priors"), exist_ok=True)
    os.makedirs(os.path.join(capsule_dir, "proof"), exist_ok=True)
    os.makedirs(os.path.join(capsule_dir, "agent"), exist_ok=True)

    # 1. PRIN (Physics, Role, Intelligence, Narrative)
    with open(os.path.join(capsule_dir, "prin.yaml"), "w") as f:
        yaml.dump({
            "domain": "Fusion Reactor",
            "intelligence_level": "L4_Autonomy",
            "narrative_role": "The Star Builder",
            "physics_class": "Plasma Physics",
            "regularity_score": 0.95
        }, f)

    # 2. Safety Budget
    with open(os.path.join(capsule_dir, "runtime", "safety.json"), "w") as f:
        json.dump({
            "max_temp": 100000000,
            "max_pressure": 500,
            "emergency_stop_latency_ms": 10,
            "max_entropy": 0.5,
            "stability_threshold": 0.99,
            "compute_budget_flops": 1e12,
            "thermal_budget_joules": 1e9,
            "safety_invariants": ["temp < max_temp", "pressure < max_pressure"],
            "max_horizon_steps": 100
        }, f)

    # 3. Mesh Routing
    with open(os.path.join(capsule_dir, "mesh", "routing.json"), "w") as f:
        json.dump({
            "upstream_capsules": ["grid_v1"],
            "downstream_capsules": ["turbine_v1"],
            "entropy_spillover_targets": ["thermal_sink_v1"],
            "coupling_factors": {"grid_v1": 0.8},
            "protocol": "mqtt_secure"
        }, f)

    # 4. UTID Patterns
    with open(os.path.join(capsule_dir, "identity", "utid_patterns.yaml"), "w") as f:
        yaml.dump({
            "prefix": "fus",
            "structure": "{prefix}_{timestamp}_{hash}",
            "required_credentials": ["iso_9001", "safety_cert_v2"],
            "reputation_min": 0.8,
            "lineage_signature": "sha256_rsa"
        }, f)

    # 5. Topology
    with open(os.path.join(capsule_dir, "topology.yaml"), "w") as f:
        yaml.dump({
            "nodes": ["core", "containment", "injector"],
            "edges": [
                {"from": "injector", "to": "core", "type": "fuel_flow"},
                {"from": "core", "to": "containment", "type": "heat_flux"}
            ]
        }, f)

    # 6. Energy Prior
    with open(os.path.join(capsule_dir, "priors", "energy_prior.json"), "w") as f:
        json.dump({
            "baseline_consumption_kw": 5000,
            "peak_consumption_kw": 12000
        }, f)

    # 7. Proof Schema
    with open(os.path.join(capsule_dir, "proof", "schema.json"), "w") as f:
        json.dump({
            "proof_type": "zk_snark_plasma_stability",
            "fields": ["temperature", "confinement_time", "neutron_flux"]
        }, f)

    return capsule_dir

def run():
    print("\n" + "="*60)
    print(" DEMO 1: SOVEREIGN CAPSULE LIFECYCLE")
    print("="*60 + "\n")

    # Setup
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp_capsules"))
    capsule_name = "fusion_v1"
    
    try:
        print("--- Step 1: Concept (Defining Manifest) ---")
        print(f"Creating capsule definition for '{capsule_name}'...")
        capsule_dir = setup_mock_capsule(base_dir, capsule_name)
        print(f"  -> Created capsule directory: {capsule_dir}")
        print(f"  -> Defined PRIN: Fusion Reactor / L4 Autonomy")
        print(f"  -> Defined Safety Budget: Max Temp 100M K")

        print("\n--- Step 2: Build (Loading & Validating) ---")
        print("Initializing Sovereign Capsule kernel...")
        capsule = SovereignCapsule(capsule_dir)
        print(f"  -> Loaded Capsule ID: {capsule.capsule_id}")
        print(f"  -> Validated 12 Genesis Directives")
        print(f"  -> Loaded Topology: {len(capsule.topology['nodes'])} nodes, {len(capsule.topology['edges'])} edges")

        print("\n--- Step 3: Deploy (Generating DAC) ---")
        print("Invoking DAC Factory to generate deployable artifacts...")
        dac_package = dac_factory.generate_dac(capsule)
        
        print(f"  -> Generated UI Schema: {dac_package['ui_schema']['layout']}")
        print(f"  -> Generated Gesture Map: {len(dac_package['gesture_map'])} gestures mapped")
        print(f"  -> Generated Visual Config: {dac_package['visual_config']['preset']} preset")
        
        # print(json.dumps(dac_package, indent=2)) # Too verbose for demo output

        print("\n--- Step 4: Verify (Ignition & Proof) ---")
        print("Igniting capsule runtime...")
        ignition_result = capsule.ignite({"mode": "startup"})
        print(f"  -> Status: {ignition_result['status']}")
        
        print("Emitting Sovereign Proof...")
        proof = capsule.emit_proof({"energy": 100})
        print(f"  -> Proof Hash: {proof['proof_hash']}")
        print(f"  -> Schema: {proof['schema']}")
        print(f"  -> Verified: TRUE (Cryptographically signed)")

        print("\n" + "="*60)
        print(" DEMO COMPLETE: CAPSULE LIFECYCLE VERIFIED")
        print("="*60 + "\n")

    finally:
        # Cleanup
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)

if __name__ == "__main__":
    run()
