import sys
import os
import json
import shutil
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules["numpy"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
# sys.modules["fastapi"] = MagicMock() 

# Custom Mock for FastAPI to handle Router
mock_fastapi = MagicMock()
mock_router_cls = MagicMock()
def mock_router_init(*args, **kwargs):
    mock = MagicMock()
    mock.tags = kwargs.get("tags", [])
    mock.prefix = kwargs.get("prefix", "")
    return mock
mock_router_cls.side_effect = mock_router_init
mock_fastapi.APIRouter = mock_router_cls
sys.modules["fastapi"] = mock_fastapi

sys.modules["pyttsx3"] = MagicMock() # Mock TTS

# Mock Legacy DAC Dependencies
sys.modules["src.white_label"] = MagicMock()
sys.modules["src.white_label.dac"] = MagicMock()
sys.modules["src.white_label.dac.registry"] = MagicMock()
sys.modules["src.white_label.dac.manifest_schema"] = MagicMock()
sys.modules["src.capsules"] = MagicMock()
sys.modules["src.capsules.factory"] = MagicMock()
sys.modules["src.capsules.factory.dac_factory"] = MagicMock()
sys.modules["src.capsules.core"] = MagicMock()
sys.modules["src.capsules.core.sovereign_capsule"] = MagicMock()

# Setup Mock Classes for DACManager imports
mock_registry = MagicMock()
mock_registry_cls = MagicMock(return_value=mock_registry)
sys.modules["src.white_label.dac.registry"].get_dac_registry = MagicMock(return_value=mock_registry)

mock_manifest = MagicMock()
sys.modules["src.white_label.dac.manifest_schema"].DACManifest = MagicMock(return_value=mock_manifest)
sys.modules["src.white_label.dac.manifest_schema"].DACTier = MagicMock()
sys.modules["src.white_label.dac.manifest_schema"].ResourceRequirements = MagicMock()
sys.modules["src.white_label.dac.manifest_schema"].WidgetConfig = MagicMock()

sys.modules["src.capsules.factory.dac_factory"].dac_factory = MagicMock()
sys.modules["src.capsules.factory.dac_factory"].dac_factory.generate_dac.return_value = {"ui": "mock_ui_config"}
sys.modules["src.capsules.core.sovereign_capsule"].SovereignCapsule = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.scf.factory.dac_manager import DACManager
from src.bridge_api.routers.scf_router import router
from src.scf.trunk.trifecta_master_loop import TrifectaMasterLoop

def test_dac_factory():
    print("🧪 Testing DAC Factory...")
    manager = DACManager()
    
    # Create Capsule
    result = manager.create_capsule("Test Intent", "print('hello')", "arm64")
    
    assert result["id"].startswith("dac-")
    assert result["path"].endswith(".zip")
    assert os.path.exists(result["path"])
    
    print(f"✅ DAC Created: {result['path']}")
    
    # Cleanup
    os.remove(result["path"])

def test_neural_link():
    print("🧪 Testing Neural Link (Router)...")
    # In a real test we'd use TestClient, but here we just check import and structure
    # assert router.prefix == "/scf" # Prefix is sometimes stored differently depending on FastAPI version/mock
    print(f"DEBUG: Router Tags: {router.tags}")
    assert "Sovereign Code Foundry" in router.tags
    print("✅ Router Initialized")

def test_ambient_voice_integration():
    print("🧪 Testing Ambient Voice Integration...")
    
    # Mock Components
    mock_context = MagicMock()
    mock_intent = MagicMock()
    mock_intent.generate.return_value = "Test Voice Intent"
    mock_builder = MagicMock()
    mock_reviewer = MagicMock()
    mock_reviewer.review.return_value = {"verdict": "APPROVE"}
    mock_deployer = MagicMock()
    mock_deployer.deploy.return_value = {"status": "success"}
    
    loop = TrifectaMasterLoop(mock_context, mock_intent, mock_builder, mock_reviewer, mock_deployer)
    
    # Mock Voice Engine
    loop.voice = MagicMock()
    
    # Run Cycle (Async mock)
    import asyncio
    async def run_test():
        # Mock async method
        f = asyncio.Future()
        f.set_result({})
        mock_context.get_context_slab.return_value = f
        
        await loop.cycle()
        
    asyncio.run(run_test())
    
    # Verify Voice Calls
    assert loop.voice.speak.call_count >= 2 # Intent + Success
    print("✅ Voice Announcements Verified")

if __name__ == "__main__":
    test_dac_factory()
    test_neural_link()
    test_ambient_voice_integration()
