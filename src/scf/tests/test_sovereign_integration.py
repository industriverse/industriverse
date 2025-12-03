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

# Mock Security Sensors to avoid heavy imports
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

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.scf.trunk.trifecta_master_loop import TrifectaMasterLoop
from src.scf.fertilization.cfr_logger import CFRLogger
from src.security.uzkl_ledger import UnifiedZKLedger
from src.anthropology.cognitive_fossil_record import FossilRecord

async def test_sovereign_integration():
    print("🧪 Testing Sovereign Integration...")
    
    # 1. Setup Trifecta Loop
    mock_context = MagicMock()
    # Mock async get_context_slab
    f = asyncio.Future()
    f.set_result({})
    mock_context.get_context_slab.return_value = f
    
    mock_intent = MagicMock()
    mock_intent.generate.return_value = "Integrate Sovereign Components"
    mock_builder = MagicMock()
    mock_builder.build.return_value = "print('Sovereign')"
    mock_reviewer = MagicMock()
    mock_reviewer.review.return_value = {"verdict": "APPROVE", "score": 0.95}
    mock_deployer = MagicMock()
    mock_deployer.deploy.return_value = {"status": "success"}
    
    loop = TrifectaMasterLoop(mock_context, mock_intent, mock_builder, mock_reviewer, mock_deployer)
    
    # Mock Voice
    loop.voice = MagicMock()
    
    # 2. Run Cycle
    print("   Running Cycle...")
    result = await loop.cycle()
    
    # 3. Verify UZKL Proof
    assert "proof_id" in result
    print(f"   ✅ UZKL Proof Minted: {result['proof_id']}")
    
    # 4. Verify CFR Logging
    assert len(loop.cfr.fossil_record.fossils) > 0
    print("   ✅ Fossil Preserved in Anthropological Layer")
    
    print("🎉 Sovereign Integration Verified!")

if __name__ == "__main__":
    asyncio.run(test_sovereign_integration())
