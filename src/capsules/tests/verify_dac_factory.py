"""
Verification script for DAC Factory (Phase 6).
Checks generation of DAC assets for Fusion and Grid capsules.
"""

import os
import sys
import logging
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.capsules.core.sovereign_capsule import SovereignCapsule
from src.capsules.factory.dac_factory import dac_factory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DACVerifier")

def verify_dac_generation(capsule_path: str):
    capsule_id = os.path.basename(capsule_path)
    logger.info(f"--- Verifying DAC Generation: {capsule_id} ---")
    
    try:
        # 1. Load Capsule
        capsule = SovereignCapsule(capsule_path)
        
        # 2. Generate DAC
        dac = dac_factory.generate_dac(capsule)
        
        # 3. Verify Contents
        assert dac["capsule_id"] == capsule.capsule_id
        
        # Check UI Schema
        ui = dac["ui_schema"]
        assert ui["layout"] == "dashboard"
        component_types = [c["type"] for c in ui["components"]]
        assert "ReactorGauge" in component_types
        assert "TruthSigil" in component_types
        
        if "fusion" in capsule_id:
            assert "PlasmaVisualizer" in component_types
            assert "CoilControls" in component_types
            logger.info("✅ Fusion-specific UI components found")
            
        if "grid" in capsule_id:
            assert "NetworkGraph" in component_types
            logger.info("✅ Grid-specific UI components found")

        # Check Gesture Map
        gestures = dac["gesture_map"]
        assert "Open_Palm" in gestures
        if "fusion" in capsule_id:
            assert "Thumb_Up" in gestures
            logger.info("✅ Fusion gestures found")

        # Check Visual Config
        visuals = dac["visual_config"]
        assert visuals["engine"] == "TouchDesigner"
        if "fusion" in capsule_id:
            assert visuals["preset"] == "tokamak_core"
            
        logger.info(f"🎉 DAC GENERATION VERIFIED FOR {capsule_id}\n")
        return True

    except Exception as e:
        logger.error(f"❌ DAC Verification Failed for {capsule_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sovereign"))
    
    fusion_path = os.path.join(base_dir, "fusion_v1")
    grid_path = os.path.join(base_dir, "grid_v1")
    
    success = True
    success &= verify_dac_generation(fusion_path)
    success &= verify_dac_generation(grid_path)
    
    if success:
        logger.info("ALL DACS VERIFIED SUCCESSFULLY.")
        sys.exit(0)
    else:
        logger.error("SOME DACS FAILED VERIFICATION.")
        sys.exit(1)
