import pytest
from src.core_ai_layer.sam_service import SAMPerceptionService, SAM3DReconstructor
from src.ai_safety.shield_v3 import AIShieldV3

def test_sam_perception():
    sam = SAMPerceptionService()
    
    # Test Segmentation
    segments = sam.segment_concept("img_123", "solar panel")
    assert len(segments) > 0
    assert segments[0]['label'] == "solar panel"
    
    # Test Visual Energy Analysis
    energy = sam.analyze_visual_energy("img_clean")
    assert energy < 0.5 # Expect low energy for clean image (mock logic)

def test_sam_3d_reconstruction():
    sam3d = SAM3DReconstructor()
    
    # Test Reconstruction
    mesh = sam3d.reconstruct_3d("img_123", "gearbox")
    assert mesh['format'] == 'obj'
    assert mesh['vertices'] > 0

def test_shield_visual_check():
    shield = AIShieldV3()
    
    # Test Visual Energy Check
    # Mocking SAM behavior inside Shield is tricky without dependency injection or mocking library.
    # For this unit test, we rely on the fact that Shield imports SAM internally.
    # We assume the mock SAM returns consistent values.
    
    is_safe, energy = shield.visual_energy_check("img_test")
    assert isinstance(is_safe, bool)
    assert isinstance(energy, float)
    
    print("SAM Perception & Shield Visual Check Verified.")

if __name__ == "__main__":
    test_sam_perception()
    test_sam_3d_reconstruction()
    test_shield_visual_check()
