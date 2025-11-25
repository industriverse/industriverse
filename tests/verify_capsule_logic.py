import sys
import os
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from capsule_layer.capsule_definitions import CAPSULE_REGISTRY
from capsule_layer.ace_reasoning import ACEReasoningTemplate
from capsule_layer.domain_equations import DomainEquationPack
from capsule_layer.dgm_auto_lora import DGMAutoLoRA
from capsule_layer.thermo_runtime import ThermodynamicRuntimeMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyCapsuleLogic")

def test_capsule_logic():
    # 1. Pick a capsule (e.g., MHD/Fusion)
    capsule_id = "capsule:rawmat:v1" # Category A
    capsule = CAPSULE_REGISTRY[capsule_id]
    logger.info(f"Testing Capsule: {capsule.name} ({capsule.capsule_id})")
    
    # 2. Initialize ACE Context
    ace = ACEReasoningTemplate(capsule)
    logger.info("ACE Context Initialized.")
    
    # 3. Test Prompt Generation
    prompt = ace.generate_prompt_context()
    logger.info(f"Generated Prompt Context (excerpt):\n{prompt[:200]}...")
    
    # 4. Test Domain Equations
    equations = DomainEquationPack()
    # Try a relevant equation
    if "Granular stress models" in capsule.domain_equations:
        result = equations.solve("Granular stress models", sigma=100, phi=30)
        logger.info(f"Solved 'Granular stress models': {result}")
        
    # 5. Test Auto-LoRA
    auto_lora = DGMAutoLoRA()
    adapter = auto_lora.select_adapter(capsule.category.value, ["mining", "flow"])
    logger.info(f"Selected LoRA Adapter: {adapter.name}")
    
    # 6. Test Runtime Monitor & Safety
    monitor = ThermodynamicRuntimeMonitor(capsule, ace)
    
    # Simulate energy usage
    ace.record_usage(50.0) # Within limits
    assert monitor.check_status() == True, "Status should be OK"
    logger.info("Runtime Check 1: OK")
    
    ace.record_usage(5000.0) # Exceeds hard limit (500.0)
    status = monitor.check_status()
    if not status:
        logger.info("Runtime Check 2: Correctly flagged violation.")
        monitor.trigger_tumix_intervention()
    else:
        logger.error("Runtime Check 2: FAILED to flag violation.")

    # 7. Test PRIN Validation
    score = ace.validate_hypothesis(
        hypothesis={"idea": "test"},
        p_physics=0.9,
        p_coherence=0.8,
        p_novelty=0.1
    )
    logger.info(f"PRIN Score: {score.value} ({score.verdict})")

if __name__ == "__main__":
    test_capsule_logic()
