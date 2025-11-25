import requests
import json
import os
import sys

def verify_grand_unification():
    print("--- 🌌 Verifying Grand Unification 🌌 ---")
    
    # 1. Backend API Check
    try:
        print("Checking Backend API...", end=" ")
        r = requests.get("http://localhost:8000/health")
        if r.status_code == 200:
            print("✅ ONLINE")
        else:
            print(f"❌ FAILED ({r.status_code})")
    except:
        print("❌ UNREACHABLE (Is uvicorn running?)")

    # 2. Capsule Blueprint Check (Magnet Assembly)
    print("Checking Magnet Blueprint...", end=" ")
    blueprint_path = "src/capsules/blueprints/factory_ops/magnet_assembly_v1.json"
    if os.path.exists(blueprint_path):
        with open(blueprint_path, 'r') as f:
            data = json.load(f)
            if "pilot_config" in data and data["pilot_config"]["enabled"]:
                print("✅ VALID (Pilot Enabled)")
            else:
                print("❌ INVALID (Missing pilot_config)")
    else:
        print("❌ MISSING")

    # 3. Streamlit Pilot App Check
    try:
        print("Checking Streamlit Pilot...", end=" ")
        # Streamlit health check usually at /_stcore/health
        r = requests.get("http://localhost:8501/_stcore/health") 
        if r.status_code == 200:
            print("✅ ONLINE")
        else:
            print(f"⚠️ WARNING (Status {r.status_code} - App might be loading)")
    except:
        print("⚠️ WARNING (Not running on port 8501 - Launch script needed?)")

    # 4. Frontend Component Check
    print("Checking Frontend Components...", end=" ")
    dac_renderer_path = "frontend/src/components/DACRenderer.tsx"
    with open(dac_renderer_path, 'r') as f:
        content = f.read()
        if "StreamlitContainer" in content and "StreamlitView" in content:
            print("✅ INTEGRATED")
        else:
            print("❌ MISSING INTEGRATION")

    print("\n--- Verification Summary ---")
    print("If all checks passed (or warnings are expected), the system is unified.")
    print("Ready for: git commit && git push")

if __name__ == "__main__":
    verify_grand_unification()
