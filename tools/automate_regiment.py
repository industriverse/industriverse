import argparse
import os
import sys
import time
import json
import subprocess

def run_step(step_name, command):
    print(f"\n🚀 [STEP] {step_name}...")
    try:
        # Use the current python executable to run sub-scripts
        if command.startswith("python "):
             command = f"{sys.executable} {command[7:]}"
        
        # Execute
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {step_name} Complete.")
        # print(result.stdout) # Optional: print output
    except subprocess.CalledProcessError as e:
        print(f"❌ {step_name} Failed!")
        print(e.stderr)
        sys.exit(1)

def automate_regiment(domain, input_file=None):
    print(f"🏭 STARTING INDUSTRIVERSE REGIMENT FOR DOMAIN: {domain.upper()}")
    print("===========================================================")
    
    # 1. Ingestion (Mocked via Digital Twin Generator)
    if input_file:
        run_step("Ingestion & Twin Generation", f"scripts/digital_twin_generator.py {input_file}")
    else:
        print("ℹ️  No input file provided, using synthetic seed.")

    # 2. Scaffolding (Ensure capsule exists)
    # We use a targeted scaffold function here or just run the bulk scaffolder and check
    # For this demo, we'll assume the bulk scaffolder covers it or we'd add a flag to scaffold_capsules.py
    # Let's run the bulk scaffolder to be safe (it's idempotent-ish)
    run_step("Capsule Scaffolding", "python tools/scaffold_capsules.py")
    
    # 3. Schema Generation
    run_step("UI Schema Generation", "python tools/generate_dac_schemas.py")
    
    # 4. Simulation & Verification
    # We need a way to run just ONE capsule in run_all_demos_extended.py
    # For now, we'll run the full suite as it's fast enough, or we could modify the script.
    # Let's run the full suite for verification assurance.
    run_step("Simulation & Proof Minting", "python tools/run_all_demos_extended.py")
    
    # 5. Delivery
    artifact_path = os.path.join("artifacts", "ebm_tnn_runs", f"{domain}_v1.json")
    if os.path.exists(artifact_path):
        print(f"\n📦 ASSET DELIVERED: {artifact_path}")
        with open(artifact_path) as f:
            data = json.load(f)
            print(f"   Proof Hash: {data['proof']['run_id']}")
            print(f"   Final Energy: {data['ebm']['final_energy']:.4f}")
            print(f"   Dashboard: http://localhost:3000/dac/{domain}_v1")
    else:
        print(f"\n⚠️  Asset generation verified, but specific artifact {artifact_path} not found (maybe domain name mismatch?)")

    print("\n✅ REGIMENT CYCLE COMPLETE.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Industriverse Regiment Orchestrator")
    parser.add_argument("--domain", type=str, required=True, help="Target domain (e.g., fusion, grid)")
    parser.add_argument("--input", type=str, help="Path to input log file")
    
    args = parser.parse_args()
    
    automate_regiment(args.domain, args.input)
