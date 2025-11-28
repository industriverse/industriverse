import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

def verify_libraries():
    print("Verifying Prerequisite Libraries...")
    
    # 1. Signal Processing
    try:
        from src.thermodynamic_layer.signal_processing import PowerTraceConverter, ConservationEnforcer, UniversalNormalizer
        converter = PowerTraceConverter()
        res = converter.process([10, 12, 15, 12, 10])
        print(f"✅ Signal Processing: E_total={res['E_total']:.2f}")
    except Exception as e:
        print(f"❌ Signal Processing Failed: {e}")

    # 2. Semantics
    try:
        from src.core_ai_layer.semantic_translator import ThermodynamicTranslator, NarrativeEngine
        translator = ThermodynamicTranslator()
        narrator = NarrativeEngine()
        tags = translator.translate({"E_total": 5000, "Entropy": 2.5, "dE_dt_volatility": 10})
        report = narrator.generate_report("node_test", tags)
        print(f"✅ Semantics: Report Generated -> {report.splitlines()[1]}")
    except Exception as e:
        print(f"❌ Semantics Failed: {e}")

    # 3. Energy Governor
    try:
        from src.overseer_system.energy_governor import EnergyGovernor
        gov = EnergyGovernor(max_joules_budget=100)
        approved = gov.request_action("test_action", 50)
        print(f"✅ Energy Governor: Action Approved? {approved}")
    except Exception as e:
        print(f"❌ Energy Governor Failed: {e}")

    # 4. Hybrid Solver
    try:
        from src.expansion_packs.tse.hybrid_solver import HybridSolver
        solver = HybridSolver(grid_size=5)
        solver.initialize([0, 1, 2, 1, 0])
        new_state = solver.step()
        print(f"✅ Hybrid Solver: Step complete. Max val: {max(new_state):.2f}")
    except Exception as e:
        print(f"❌ Hybrid Solver Failed: {e}")

if __name__ == "__main__":
    verify_libraries()
