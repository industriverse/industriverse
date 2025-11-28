import pytest
from src.generative_layer.ebdm import EBDMGeneratorV2
from src.generative_layer.diffusion_explorer import DiffusionExplorer

def test_ebdm_v2():
    ebdm = EBDMGeneratorV2()
    result = ebdm.generate_latent("Optimize quantum lattice")
    
    assert "latent_vector" in result
    assert result['energy'] <= ebdm.energy_threshold
    assert result['status'] == "converged"

def test_diffusion_explorer():
    explorer = DiffusionExplorer()
    
    # Simulate a path
    for i in range(5):
        explorer.track_step(i, [0.1 * i] * 10, 1.0 - 0.2 * i)
        
    viz = explorer.visualize_path()
    assert "Diffusion Path Visualization" in viz
    assert "Step | Energy" in viz
    assert "0.2000" in viz # Check for final energy

if __name__ == "__main__":
    test_ebdm_v2()
    test_diffusion_explorer()
    print("Batch 3 Iteration 4 Verified.")
