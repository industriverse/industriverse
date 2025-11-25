import os

def verify_frontend_refinement():
    print("--- Verifying Frontend Refinement (Phase 10) ---")
    
    files_to_check = [
        "frontend/src/components/visualizers/IndustrialWidgets/Heatmap3D.tsx",
        "frontend/src/components/visualizers/IndustrialWidgets/GeoMap.tsx",
        "frontend/src/components/visualizers/IndustrialWidgets/MoleculeViewer.tsx",
        "frontend/src/components/dashboard/GroupedCapsuleGrid.tsx",
        "frontend/src/components/ProofBadge.tsx",
        "frontend/src/components/CertificateViewer.tsx",
        "frontend/src/components/StreamlitContainer.tsx",
        "frontend/src/components/DACRenderer.tsx",
        "frontend/src/pages/Dashboard.tsx"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
            
    # Check for content integration in DACRenderer
    try:
        with open("frontend/src/components/DACRenderer.tsx", "r") as f:
            content = f.read()
            if "Heatmap3D" in content and "GeoMap" in content and "MoleculeViewer" in content:
                print("✅ DACRenderer: Widgets registered")
            else:
                print("❌ DACRenderer: Widgets NOT registered")
                all_exist = False
    except Exception as e:
        print(f"❌ Error reading DACRenderer: {e}")
        all_exist = False

    if all_exist:
        print("\n🎉 Frontend Refinement Verification Passed!")
    else:
        print("\n⚠️ Verification Failed.")

if __name__ == "__main__":
    verify_frontend_refinement()
