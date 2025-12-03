import asyncio
import sys
import os
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

async def test_agent_spawn_scenario():
    print("🧪 Scenario: Autonomous Agent Spawning")
    
    # Mock Components
    context_root = MagicMock()
    context_root.get_context_slab.return_value = asyncio.Future()
    context_root.get_context_slab.return_value.set_result({
        "telemetry": {"metrics": {"workload": "HIGH"}},
        "memory": {"agent_population": 10}
    })
    
    intent_engine = MagicMock()
    intent_engine.generate.return_value = "Spawn Load Balancer Agent"
    intent_engine.expand.return_value = {"goal": "Spawn Agent", "role": "LoadBalancer"}
    
    builder_engine = MagicMock()
    builder_engine.build.return_value = "class LoadBalancerAgent: pass"
    
    reviewer = MagicMock()
    reviewer.review.return_value = {
        "score": 0.88,
        "verdict": "APPROVE",
        "critique": "Agent genome is stable."
    }
    
    deployer = MagicMock()
    deployer.deploy.return_value = {"status": "deployed", "agent_id": "agent_lb_01"}

    # Initialize Loop
    loop = TrifectaMasterLoop(context_root, intent_engine, builder_engine, reviewer, deployer)
    
    # Run Cycle
    result = await loop.cycle()
    
    # Assertions
    assert result["status"] == "deployed"
    assert result["result"]["agent_id"] == "agent_lb_01"
    print("✅ Agent Spawn Scenario Passed")

if __name__ == "__main__":
    asyncio.run(test_agent_spawn_scenario())
