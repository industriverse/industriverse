import os
import sys

def verify_ui_structure():
    required_files = [
        "src/frontend/styles/dyson_sphere.css",
        "src/frontend/components/DysonSphere/DysonShell.jsx",
        "src/frontend/components/DysonSphere/IntentionStar.jsx",
        "src/frontend/components/DysonSphere/CapsulePortal.jsx",
        "src/frontend/components/DysonSphere/AuraRing.jsx",
        "src/frontend/pages/DysonSphereDemo.jsx"
    ]
    
    missing = []
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)
            
    if missing:
        print("❌ UI Verification Failed. Missing files:")
        for m in missing:
            print(f"   - {m}")
        sys.exit(1)
    else:
        print("✅ UI Structure Verified. All Dyson Sphere components present.")
        
        # Check imports in DysonShell
        with open("src/frontend/components/DysonSphere/DysonShell.jsx", "r") as f:
            content = f.read()
            if "import IntentionStar" in content and "import CapsulePortal" in content:
                print("   ✅ DysonShell imports verified.")
            else:
                print("   ❌ DysonShell missing imports.")

if __name__ == "__main__":
    verify_ui_structure()
