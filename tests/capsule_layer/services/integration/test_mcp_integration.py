"""
Test MCP Integration with Bridge API

Validates that FastAPI-MCP successfully exposes thermodynamic services
as context-aware MCP tools.
"""

import pytest
from src.capsule_layer.services.bridge_api import create_bridge_api, MCP_AVAILABLE

def test_mcp_available():
    """Test that fastapi-mcp is installed"""
    assert MCP_AVAILABLE, "fastapi-mcp package not installed"

def test_bridge_api_with_mcp():
    """Test Bridge API creation with MCP integration"""
    bridge = create_bridge_api(enable_mcp=True)
    
    # Check that MCP was initialized
    assert hasattr(bridge, '_mcp'), "MCP instance not created"
    assert hasattr(bridge, '_mcp_app'), "MCP FastAPI app not created"
    
    # Check that router is included
    assert bridge.router is not None
    
    print("✅ MCP integration successful")

def test_bridge_api_without_mcp():
    """Test Bridge API creation without MCP integration"""
    bridge = create_bridge_api(enable_mcp=False)
    
    # Check that MCP was not initialized
    assert not hasattr(bridge, '_mcp'), "MCP instance should not be created"
    
    # Router should still work
    assert bridge.router is not None
    
    print("✅ Bridge API works without MCP")

@pytest.mark.skipif(not MCP_AVAILABLE, reason="fastapi-mcp not installed")
def test_mcp_tool_exposure():
    """Test that MCP exposes FastAPI endpoints as tools"""
    bridge = create_bridge_api(enable_mcp=True)
    
    # Check that MCP app has routes
    assert len(bridge._mcp_app.routes) > 0, "No routes in MCP app"
    
    # Check for thermodynamic endpoints
    route_paths = [route.path for route in bridge._mcp_app.routes]
    
    # Should have our thermodynamic endpoints
    assert any("/thermal/" in path for path in route_paths), "Thermal endpoints not found"
    assert any("/worldmodel/" in path for path in route_paths), "WorldModel endpoints not found"
    assert any("/microadapt/" in path for path in route_paths), "MicroAdapt endpoints not found"
    assert any("/snapshot/" in path for path in route_paths), "Snapshot endpoints not found"
    
    print(f"✅ MCP exposing {len(route_paths)} endpoints as tools")

if __name__ == "__main__":
    print("Testing MCP Integration...")
    
    test_mcp_available()
    test_bridge_api_with_mcp()
    test_bridge_api_without_mcp()
    
    if MCP_AVAILABLE:
        test_mcp_tool_exposure()
    
    print("\n✅ All MCP integration tests passed!")
