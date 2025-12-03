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

async def test_grid_optimization_scenario():
    print("🧪 Scenario: Microgrid Energy Optimization")
    
    # Mock Components
    context_root = MagicMock()
    context_root.get_context_slab.return_value = asyncio.Future()
    context_root.get_context_slab.return_value.set_result({
        "telemetry": {"metrics": {"total_power_watts": 850.0, "grid_stability": 0.7}},
        "memory": {"previous_optimizations": []}
    })
    
    intent_engine = MagicMock()
    intent_engine.generate.return_value = "Stabilize Microgrid Voltage"
    intent_engine.expand.return_value = {"goal": "Stabilize Voltage", "target": "Microgrid A"}
    
    builder_engine = MagicMock()
    builder_engine.build.return_value = "def stabilize_voltage(): adjust_inverters(0.95)"
    
    reviewer = MagicMock()
    reviewer.review.return_value = {
        "score": 0.92,
        "verdict": "APPROVE",
        "critique": "Physically sound and safe."
    }
    
    deployer = MagicMock()
    deployer.deploy.return_value = {"status": "deployed", "node": "edge_controller_01"}

    # Initialize Loop
    loop = TrifectaMasterLoop(context_root, intent_engine, builder_engine, reviewer, deployer)
    
    # Run Cycle
    result = await loop.cycle()
    
    # Assertions
    assert result["status"] == "deployed"
    assert result["intent"] == "Stabilize Microgrid Voltage"
    print("✅ Grid Optimization Scenario Passed")

if __name__ == "__main__":
    asyncio.run(test_grid_optimization_scenario())
