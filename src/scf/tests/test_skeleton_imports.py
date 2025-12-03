import sys
import os
from unittest.mock import MagicMock

# Mock numpy and pydantic
sys.modules["numpy"] = MagicMock()
sys.modules["pydantic"] = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

def test_imports():
    modules = [
        "src.scf.roots.context_root",
        "src.scf.roots.memory_stem",
        "src.scf.roots.intent_memory_bridge",
        "src.scf.roots.contextual_regulator",
        "src.scf.trunk.trifecta_master_loop",
        "src.scf.trunk.state_machine",
        "src.scf.trunk.logic_router",
        "src.scf.branches.intent.intent_engine",
        "src.scf.branches.intent.intent_shaper",
        "src.scf.branches.intent.intent_verifier",
        "src.scf.branches.intent.intent_composer",
        "src.scf.branches.build.builder_engine",
        "src.scf.branches.build.architecture_generator",
        "src.scf.branches.build.simulation_harness",
        "src.scf.branches.build.static_analyzer",
        "src.scf.branches.build.mutation_engine",
        "src.scf.branches.build.refinement_cycle",
        "src.scf.branches.verify.review_engine",
        "src.scf.branches.verify.deep_verification",
        "src.scf.branches.verify.zk_verification_bridge",
        "src.scf.canopy.deploy.deployment_strategy",
        "src.scf.canopy.deploy.bitnet_autodeploy",
        "src.scf.canopy.deploy.agent_instantiator",
        "src.scf.fertilization.cfr_logger",
        "src.scf.fertilization.incentive_mapper",
        "src.scf.governance.safety_regulator",
        "src.scf.governance.ethics_limiter",
        "src.scf.governance.zk_compliance_auditor",
        "src.scf.core_models.ebdm",
        "src.scf.core_models.tnn",
        "src.scf.core_models.gen_n",
        "src.scf.core_models.nvp_adapter",
        "src.scf.core_models.prin_adapter"
    ]

    print("Verifying SCF Skeleton Imports...")
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✅ Imported: {module}")
        except ImportError as e:
            print(f"❌ Failed: {module} - {e}")
            failed.append(module)
        except Exception as e:
            print(f"❌ Error: {module} - {e}")
            failed.append(module)

    if failed:
        print(f"\nFAILED: {len(failed)} modules could not be imported.")
        sys.exit(1)
    else:
        print("\nSUCCESS: All 28 SCF modules imported correctly.")

if __name__ == "__main__":
    test_imports()
