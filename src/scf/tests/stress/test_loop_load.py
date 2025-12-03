import asyncio
import sys
import os
import time
from unittest.mock import MagicMock

# Mock dependencies
sys.modules["numpy"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["src.bridge_api.event_bus"] = MagicMock()
sys.modules["src.bridge_api.ai_shield.state"] = MagicMock()
sys.modules["src.bridge_api.telemetry.thermo"] = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.scf.trunk.trifecta_master_loop import TrifectaMasterLoop

async def test_loop_load():
    print("🔥 Stress Test: High Concurrency Loop Execution")
    
    # Mock Components
    context_root = MagicMock()
    context_root.get_context_slab.return_value = asyncio.Future()
    context_root.get_context_slab.return_value.set_result({"telemetry": {}, "memory": {}})
    
    intent_engine = MagicMock()
    intent_engine.generate.return_value = "Stress Test Intent"
    intent_engine.expand.return_value = {"goal": "Stress Test"}
    
    builder_engine = MagicMock()
    builder_engine.build.return_value = "pass"
    
    reviewer = MagicMock()
    reviewer.review.return_value = {"score": 1.0, "verdict": "APPROVE", "critique": "OK"}
    
    deployer = MagicMock()
    deployer.deploy.return_value = {"status": "deployed"}

    loop = TrifectaMasterLoop(context_root, intent_engine, builder_engine, reviewer, deployer)
    
    # Run 100 concurrent cycles
    start_time = time.time()
    tasks = [loop.cycle() for _ in range(100)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"✅ Completed 100 cycles in {duration:.4f} seconds")
    assert len(results) == 100
    assert all(r["status"] == "deployed" for r in results)

if __name__ == "__main__":
    asyncio.run(test_loop_load())
