import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules["numpy"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["src.bridge_api.ai_shield.state"] = MagicMock()
sys.modules["src.bridge_api.telemetry.thermo"] = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.scf.roots.context_root import ContextRoot
from src.scf.roots.pulse_connector import PulseConnector
from src.scf.canopy.deploy.bitnet_autodeploy import BitNetAutoDeploy
from src.bridge_api.event_bus import GlobalEventBus

def test_context_root_ace_integration():
    print("🧪 Testing ContextRoot -> ACE Integration...")
    
    with patch("src.scf.roots.context_root.ACEService") as MockACE:
        # Setup Mock ACE Response
        mock_response = MagicMock()
        mock_response.reflection.dict.return_value = {"analysis": "Deep Thought"}
        
        # Create a future attached to the current loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        future = asyncio.Future()
        future.set_result(mock_response)
        
        MockACE.return_value.process_request = MagicMock(return_value=future)
        
        root = ContextRoot()
        
        # Run
        slab = loop.run_until_complete(root.get_context_slab())
        
        # Verify
        MockACE.return_value.process_request.assert_called_once()
        assert slab["ace_reflection"]["analysis"] == "Deep Thought"
        print("✅ ACE Integration Verified")

def test_pulse_connector_event_bus():
    print("🧪 Testing PulseConnector -> GlobalEventBus Integration...")
    
    connector = PulseConnector()
    
    # Mock Event Bus Subscription
    with patch.object(GlobalEventBus, 'subscribe') as mock_sub:
        asyncio.run(connector.connect())
        mock_sub.assert_called_once()
        
        # Simulate Event
        callback = mock_sub.call_args[0][0]
        event = {"type": "system_heartbeat", "metrics": {"power": 100}}
        asyncio.run(callback(event))
        
        assert connector.latest_pulse == event
        print("✅ Pulse Event Bus Integration Verified")

def test_bitnet_deployer_integration():
    print("🧪 Testing BitNetAutoDeploy -> BitNetDeployer Integration...")
    
    with patch("src.scf.canopy.deploy.bitnet_autodeploy.BitNetDeployer") as MockDeployer, \
         patch("src.scf.canopy.deploy.bitnet_autodeploy.EdgeNodeManager") as MockManager:
        
        deployer = BitNetAutoDeploy()
        
        # Run Deploy
        result = deployer.deploy("some_code")
        
        # Verify
        MockDeployer.return_value.deploy_model.assert_called_once()
        assert result["status"] == "success"
        print("✅ BitNet Deployer Integration Verified")

if __name__ == "__main__":
    test_context_root_ace_integration()
    test_pulse_connector_event_bus()
    test_bitnet_deployer_integration()
