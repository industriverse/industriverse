import sys
import os
import importlib

# Add project root to path
sys.path.append(os.getcwd())

def verify_operator():
    print("🔍 Starting KaaS Operator Verification...")
    
    components = [
        "src.infra.operator.kaa_operator.main",
        "src.infra.operator.kaa_operator.controllers.deployment_controller",
        "src.infra.operator.kaa_operator.webhooks.admission",
        "src.infra.operator.kaa_operator.proof_validators.validator"
    ]
    
    failed = False
    for component in components:
        try:
            importlib.import_module(component)
            print(f"✅ Successfully imported {component}")
        except ImportError as e:
            print(f"❌ Failed to import {component}: {e}")
            failed = True
        except Exception as e:
            print(f"❌ Error loading {component}: {e}")
            failed = True

    if failed:
        print("❌ Verification Failed")
        sys.exit(1)
    else:
        print("🎉 KaaS Operator Verification Passed!")

if __name__ == "__main__":
    verify_operator()
