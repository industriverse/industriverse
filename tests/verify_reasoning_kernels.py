import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.expansion_packs.tse.solvers.diffusion_solver import DiffusionSolver
from src.expansion_packs.tse.solvers.turbulence import TurbulenceFingerprint
from src.expansion_packs.til.anchoring.semantic_grid import SemanticGrid
from src.expansion_packs.use_cases.industrial_domain import IndustrialPumpAdapter

def verify_kernels():
    print("🧠 Starting Reasoning Kernels Verification...")
    
    # 1. Test TSE Diffusion
    solver = DiffusionSolver()
    data = [1.0, 0.5, 0.2]
    noisy = solver.forward_diffusion(data, 0.1)
    print(f"✅ TSE Forward Diffusion: {data} -> {noisy}")
    
    # 2. Test Turbulence
    turb = TurbulenceFingerprint()
    fp = turb.generate_micro_turbulence("seed_123")
    print(f"✅ TSE Turbulence Fingerprint: {fp[:16]}...")
    assert len(fp) == 64
    
    # 3. Test TIL Semantic Grid
    grid = SemanticGrid()
    assert grid.validate_term("pump") == True
    assert grid.validate_term("unicorn_dust") == False
    print("✅ TIL Semantic Grid Validation Passed")
    
    # 4. Test Industrial Domain Adapter
    adapter = IndustrialPumpAdapter()
    telemetry = {"pump": "P-101", "rpm": 1200.0, "vibration": 0.05, "magic_level": 99.9}
    result = adapter.process_telemetry(telemetry)
    
    assert result["rpm"]["verified"] == True
    assert result["magic_level"]["verified"] == False
    assert "physics_check" in result
    print("✅ Industrial Domain Adapter Integration Passed")
    
    print("🎉 Reasoning Kernels Verification Passed!")

if __name__ == "__main__":
    verify_kernels()
