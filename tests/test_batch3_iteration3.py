import pytest
from src.core.dac_factory import LoRAFactory
from src.unified_loop.orchestrator import UnifiedLoopOrchestrator

def test_lora_factory():
    factory = LoRAFactory()
    
    # Test Math Adapter Generation
    math_adapter = factory.generate_adapter("Solve complex calculus problems")
    assert math_adapter['rank'] == 16
    assert math_adapter['alpha'] == 32
    assert "calculus" in math_adapter['task'].lower()
    
    # Test Creative Adapter Generation
    creative_adapter = factory.generate_adapter("Write a creative poem")
    assert creative_adapter['rank'] == 4
    assert creative_adapter['alpha'] == 8

def test_orchestrator_integration():
    orchestrator = UnifiedLoopOrchestrator()
    assert orchestrator.lora_factory is not None
    
    adapter = orchestrator.lora_factory.generate_adapter("Test Task")
    assert adapter['status'] == "generated"

if __name__ == "__main__":
    test_lora_factory()
    test_orchestrator_integration()
    print("Batch 3 Iteration 3 Verified.")
