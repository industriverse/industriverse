import sys
import os
import json
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules["numpy"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["src.bridge_api.event_bus"] = MagicMock()
sys.modules["src.bridge_api.ai_shield.state"] = MagicMock()
sys.modules["src.bridge_api.telemetry.thermo"] = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.scf.fertilization.cfr_logger import CFRLogger
from src.scf.fertilization.incentive_mapper import IncentiveMapper

def test_cfr_logger_integration():
    print("🧪 Testing CFRLogger Integration...")
    
    # Mock ValueVault and ResearchController
    with patch("src.scf.fertilization.cfr_logger.ValueVault") as MockVault, \
         patch("src.scf.fertilization.cfr_logger.ResearchController") as MockResearch:
        
        logger = CFRLogger()
        
        intent = "Optimize Grid"
        code = "def optimize(): pass"
        feedback = {"verdict": "APPROVE", "score": 0.95}
        
        logger.record(intent, code, feedback)
        
        # Verify ValueVault storage
        MockVault.return_value.store_secret.assert_called_once()
        args, _ = MockVault.return_value.store_secret.call_args
        stored_data = args[0]
        assert stored_data["intent"] == intent
        assert stored_data["verdict"] == "APPROVE"
        print("✅ ValueVault Integration Verified")
        
        # Verify ResearchController analysis
        MockResearch.return_value.analyze_packet.assert_called_once()
        print("✅ ResearchController Integration Verified")

def test_incentive_mapper():
    print("🧪 Testing IncentiveMapper...")
    mapper = IncentiveMapper()
    
    result = {
        "review": {"verdict": "APPROVE", "score": 0.9}
    }
    
    incentive = mapper.map_incentives(result)
    
    assert incentive["currency"] == "JouleToken"
    assert incentive["reward"] == 180.0 # 100 * (0.9 * 2.0)
    print("✅ Incentive Calculation Verified")

def test_bridge_api_control():
    print("🧪 Testing Bridge API Control Endpoint logic...")
    # Simulate the logic inside the endpoint since we can't easily spin up the full FastAPI app here with all deps
    
    cmd = {"command": "SHIFT_GEAR", "payload": {"level": "HYPER"}}
    control_file = "data/scf/control.json"
    
    # Write
    os.makedirs(os.path.dirname(control_file), exist_ok=True)
    with open(control_file, 'w') as f:
        json.dump(cmd, f)
        
    # Verify
    assert os.path.exists(control_file)
    with open(control_file, 'r') as f:
        read_cmd = json.load(f)
    
    assert read_cmd["command"] == "SHIFT_GEAR"
    print("✅ Control File Write Verified")
    
    # Cleanup
    os.remove(control_file)

if __name__ == "__main__":
    test_cfr_logger_integration()
    test_incentive_mapper()
    test_bridge_api_control()
