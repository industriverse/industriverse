import sys
import os
import asyncio
from unittest.mock import MagicMock

# Mock dependencies
sys.modules["numpy"] = MagicMock()
sys.modules["scipy"] = MagicMock()
sys.modules["scipy.signal"] = MagicMock()
sys.modules["scipy.stats"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["pyttsx3"] = MagicMock()

# Mock Security Sensors
sys.modules["src.security.thermodynamic_primitives"] = MagicMock()
sys.modules["src.security.thermodynamic_primitives.puf"] = MagicMock()
sys.modules["src.security.sensors"] = MagicMock()
sys.modules["src.security.sensors.power_analysis_detector"] = MagicMock()
sys.modules["src.security.sensors.thermal_security_monitor"] = MagicMock()
sys.modules["src.security.sensors.quantum_security_sensor"] = MagicMock()
sys.modules["src.security.analyzers"] = MagicMock()
sys.modules["src.security.analyzers.information_leakage_analyzer"] = MagicMock()
sys.modules["src.security.security_event_registry"] = MagicMock()
sys.modules["src.security.validators"] = MagicMock()
sys.modules["src.security.validators.der_grid_security_validator"] = MagicMock()
sys.modules["src.security.detectors"] = MagicMock()
sys.modules["src.security.detectors.financial_fraud_detector"] = MagicMock()
sys.modules["src.security.monitors"] = MagicMock()
sys.modules["src.security.monitors.swarm_iot_security_monitor"] = MagicMock()

# Mock SOK Dependencies
sys.modules["src.sok"] = MagicMock()
sys.modules["src.sok.goal_homeostasis"] = MagicMock()
sys.modules["src.sok.autopoeisis_engine"] = MagicMock()
sys.modules["src.safety.meta_safety_lattice"] = MagicMock()
sys.modules["src.unification.narrative_physics_engine"] = MagicMock()
sys.modules["src.economics.incentive_gradient_engine"] = MagicMock()
sys.modules["src.unification.cross_domain_inference"] = MagicMock()
sys.modules["src.overseer.overseer_stratiform"] = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.scf.trunk.trifecta_master_loop import TrifectaMasterLoop

async def test_defense_integration():
    print("🛡️ Testing Sovereign Defense Integration...")
    
    # 1. Setup Trifecta Loop
    mock_context = MagicMock()
    f = asyncio.Future()
    f.set_result({})
    mock_context.get_context_slab.return_value = f
    
    mock_intent = MagicMock()
    mock_intent.generate.return_value = "Optimize System"
    mock_builder = MagicMock()
    mock_reviewer = MagicMock()
    mock_deployer = MagicMock()
    
    loop = TrifectaMasterLoop(mock_context, mock_intent, mock_builder, mock_reviewer, mock_deployer)
    loop.voice = MagicMock()
    
    # 2. Test Unsafe Environment
    print("   Testing Unsafe Environment...")
    # Mock Defense Adapter to return unsafe
    loop.defense = MagicMock()
    loop.defense.check_environment_integrity.return_value = {
        "integrity_score": 0.5,
        "threats": ["Active Spyware Detected"],
        "safe_to_deploy": False
    }
    
    result = await loop.cycle()
    assert result["status"] == "aborted"
    assert "unsafe_environment" in result["reason"]
    print("   ✅ Loop Aborted Correctly on Threat Detection")
    
    # 3. Test Safe Environment
    print("   Testing Safe Environment...")
    loop.defense.check_environment_integrity.return_value = {
        "integrity_score": 1.0,
        "threats": [],
        "safe_to_deploy": True
    }
    
    # Mock successful cycle parts
    mock_builder.build.return_value = "print('Safe')"
    mock_reviewer.review.return_value = {"verdict": "APPROVE", "score": 0.9}
    mock_deployer.deploy.return_value = {"status": "success"}
    
    # Mock UZKL and CFR
    loop.ledger = MagicMock()
    loop.ledger.generate_proof.return_value = MagicMock(id="PROOF_123")
    loop.cfr = MagicMock()
    
    result = await loop.cycle()
    assert result["status"] == "deployed"
    print("   ✅ Loop Deployed Correctly in Safe Environment")
    
    print("🎉 Sovereign Defense Integration Verified!")

if __name__ == "__main__":
    asyncio.run(test_defense_integration())
