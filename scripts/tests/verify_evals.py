import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

def verify_evals():
    print("Verifying Evals...")
    try:
        from src.scf.eval.tests.test_energy_conservation import test_energy_conservation
        from src.scf.eval.tests.test_entropy_bounds import test_entropy_bounds
        from src.scf.eval.tests.test_stability import test_stability
        from src.scf.eval.tests.test_novelty import test_novelty
        from src.scf.eval.tests.test_performance import test_performance
        from src.scf.eval.runner.eval_runner import run_eval
        from src.scf.monitoring.leaderboard import Leaderboard
        
        print("✅ Eval modules imported.")
        
        # Test Leaderboard
        lb = Leaderboard()
        print("✅ Leaderboard instantiated.")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_evals()
