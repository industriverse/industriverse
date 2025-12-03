import sys
import os
import asyncio
from unittest.mock import MagicMock

# Mock dependencies
sys.modules["numpy"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["src.bridge_api.event_bus"] = MagicMock()
sys.modules["src.bridge_api.ai_shield.state"] = MagicMock()
sys.modules["src.bridge_api.telemetry.thermo"] = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.scf.roots.context_root import ContextRoot
from src.scf.trunk.trifecta_master_loop import TrifectaMasterLoop
from src.scf.branches.intent.intent_engine import IntentEngine
from src.scf.branches.build.builder_engine import BuilderEngine
from src.scf.branches.verify.review_engine import ReviewEngine
from src.scf.canopy.deploy.bitnet_autodeploy import BitNetAutoDeploy

async def test_full_loop():
    print("Initializing SCF Components...")
    
    # Initialize components
    context_root = ContextRoot()
    intent_engine = IntentEngine(None, None)
    builder_engine = BuilderEngine(None, None)
    reviewer = ReviewEngine()
    deployer = BitNetAutoDeploy()
    
    # Mock internal methods to avoid external calls
    context_root.get_context_slab = MagicMock(return_value=asyncio.Future())
    context_root.get_context_slab.return_value.set_result({
        "telemetry": {"metrics": {"total_power_watts": 500}},
        "memory": {}
    })
    
    intent_engine.generate = MagicMock(return_value="Optimize Grid")
    intent_engine.expand = MagicMock(return_value={"goal": "Optimize Grid"})
    
    builder_engine.build = MagicMock(return_value="def optimize(): pass")
    
    # Reviewer returns valid result
    reviewer.review = MagicMock(return_value={
        "score": 0.85,
        "verdict": "APPROVE",
        "critique": "Good code."
    })
    
    deployer.deploy = MagicMock(return_value={"status": "deployed"})

    # Initialize Master Loop
    master_loop = TrifectaMasterLoop(
        context_root=context_root,
        intent_engine=intent_engine,
        builder_engine=builder_engine,
        reviewer=reviewer,
        deployer=deployer
    )
    
    print("Running Trifecta Master Loop Cycle...")
    result = await master_loop.cycle()
    
    print("Cycle Result:", result)
    
    assert result["status"] == "deployed"
    assert result["intent"] == "Optimize Grid"
    assert result["review"]["verdict"] == "APPROVE"
    
    print("✅ Full Loop Verification Passed!")

if __name__ == "__main__":
    asyncio.run(test_full_loop())
