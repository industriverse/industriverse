import pytest
import asyncio
from src.unified_loop.orchestrator import UnifiedLoopOrchestrator
from src.unified_loop.client_config import ClientConfiguration

# Mock RDR/LLM components are handled inside DiscoveryLoop mocks in previous tests
# But we need to ensure they work here too.
# Since Orchestrator instantiates DiscoveryLoop, we might need to patch it or rely on its internal mocks if they were default.
# In DiscoveryLoopV4, we passed llm_model=None, embedding_model=None.
# We should ensure that doesn't crash.
# In DiscoveryLoopV4 code: 
# self.rdr_physics = PhysicsRDRPipeline(llm_model, embedding_model)
# If llm_model is None, RDR might fail if it tries to call methods on None.
# Let's check RDR implementation.
# In RDR ingestion/reasoning/etc, we did: if hasattr(self.llm, 'generate')... else mock.
# So passing None is safe! It will use internal mocks.

@pytest.mark.asyncio
async def test_unified_loop_end_to_end():
    orchestrator = UnifiedLoopOrchestrator()
    
    client_id = "test_client_001"
    datasets = ["dataset_A"]
    config = {
        "client_id": client_id,
        "targets": ["Minimize Energy"],
        "guardrails": {
            "max_energy": 10.0,
            "safety_mode": "strict"
        }
    }
    
    results = await orchestrator.run_campaign(client_id, datasets, config)
    
    assert len(results) > 0
    # Check if result is a Capsule object (or behaves like one)
    capsule = results[0]
    assert hasattr(capsule, 'uri')
    assert str(capsule.uri) == "capsule://fusion/plasma_control/v1"
    assert "design_id" in capsule.content["design"]
    
    # Check if economics ran (logs would show, but we can check side effects if we had access to state)
    # For now, just ensuring it runs without error and returns results is good.
