import pytest
import asyncio
from src.unified_loop.orchestrator import UnifiedLoopOrchestrator

@pytest.mark.asyncio
async def test_batch1_integration():
    orchestrator = UnifiedLoopOrchestrator()
    
    # Verify agents are instantiated
    assert orchestrator.math_oracle is not None
    assert orchestrator.transparent_user_lm is not None
    assert orchestrator.fara_agent is not None
    
    # Verify MathOracle
    proof = orchestrator.math_oracle.generate_proof("E=mc^2")
    assert "FORMAL PROOF" in proof
    
    # Verify TransparentUserLM
    response = await orchestrator.transparent_user_lm.generate_response("model", "hypothesis")
    assert "HYPOTHESIS" in response
    trace = orchestrator.transparent_user_lm.trace_source(response)
    assert trace['source_documents'] is not None
    
    # Verify FaraComputerAgent
    screenshot = orchestrator.fara_agent.take_screenshot()
    assert "screenshot" in screenshot
    action = orchestrator.fara_agent.predict_action("click submit", screenshot)
    assert action['action'] == 'click'
    
    print("Batch 1 Agents Verified Successfully.")

if __name__ == "__main__":
    asyncio.run(test_batch1_integration())
