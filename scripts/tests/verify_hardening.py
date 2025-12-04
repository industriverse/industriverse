import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

def verify_imports():
    print("Verifying imports...")
    try:
        from src.scf.daemon.state.checkpoint_manager import CheckpointManager
        from src.scf.daemon.executors.resume_executor import ResumeExecutor
        from src.scf.data.fossils.shard_map import FossilShardMap
        from src.scf.daemon.safety.gpu_stall_guard import GPUStallGuard
        from src.scf.data.fossils.guards.integrity_guard import FossilIntegrityGuard
        from src.scf.data.fossils.provenance.certificate import FossilProvenanceCertificate
        from src.scf.training.loss.physics_coupler import PhysicsConstrainedLoss
        from src.scf.training.engines.cotraining_engine import CoTrainingEngine
        from src.scf.daemon.autoopt.hparam_evolver import HParamEvolver
        from src.scf.daemon.state.carbonite import Carbonite
        from src.scf.eval.runner.eval_runner import run_eval
        
        print("✅ All core modules imported successfully.")
        
        # Instantiate a few to check init logic
        cm = CheckpointManager()
        fsm = FossilShardMap()
        pcl = PhysicsConstrainedLoss()
        
        print("✅ Instantiation checks passed.")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_imports()
