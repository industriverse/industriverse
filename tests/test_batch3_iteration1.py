import pytest
import asyncio
from src.tnn.predictor import TNNPredictor
from src.core_ai_layer.llm_service.llm_inference_service import TransparentUserLM

def test_nested_optimizer():
    tnn = TNNPredictor()
    initial_state = tnn.optimizer.get_state()
    
    # Simulate an update
    tnn.optimizer.update(1.0)
    new_state = tnn.optimizer.get_state()
    
    # Fast weights should change more than slow weights
    assert new_state['context_adaptation'] > initial_state['context_adaptation']
    assert new_state['global_knowledge'] > initial_state['global_knowledge']
    assert (new_state['context_adaptation'] - initial_state['context_adaptation']) > \
           (new_state['global_knowledge'] - initial_state['global_knowledge'])

@pytest.mark.asyncio
async def test_think_and_code():
    olmo = TransparentUserLM()
    result = await olmo.think_and_code("Optimize fusion reactor control loop")
    
    assert "Thinking about" in result['thought_process']
    assert "def solve():" in result['code']
    assert result['verified'] is True
    assert result['model'] == "OLMo-3-Coder"

if __name__ == "__main__":
    test_nested_optimizer()
    asyncio.run(test_think_and_code())
    print("Batch 3 Iteration 1 Verified.")
