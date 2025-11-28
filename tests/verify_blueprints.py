import json
import glob
import os

def verify_blueprints():
    print("--- Verifying FactoryOps Blueprints ---")
    
    blueprint_path = "src/capsules/blueprints/factory_ops/*.json"
    files = glob.glob(blueprint_path)
    
    if not files:
        print("❌ No blueprints found in src/capsules/blueprints/factory_ops/")
        return

    all_valid = True
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Basic schema check
            required_keys = ["capsule_id", "version", "area_code", "name", "connectors", "models", "proofs"]
            missing_keys = [k for k in required_keys if k not in data]
            
            if missing_keys:
                print(f"❌ {os.path.basename(file_path)}: Missing keys {missing_keys}")
                all_valid = False
            else:
                print(f"✅ {os.path.basename(file_path)}: Valid JSON & Schema")
                
        except json.JSONDecodeError as e:
            print(f"❌ {os.path.basename(file_path)}: Invalid JSON - {e}")
            all_valid = False
            
    if all_valid:
        print("\n🎉 All blueprints are valid!")
    else:
        print("\n⚠️ Some blueprints have errors.")

if __name__ == "__main__":
    verify_blueprints()
