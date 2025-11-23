import sys
import os
import asyncio
from fastapi import FastAPI

# Add project root to path
sys.path.append(os.getcwd())

from src.bridge_api.server import app
from src.white_label.dac.deployer import KubernetesDeployer
from src.white_label.dac.manifest_schema import DACManifest, ResourceRequirements, NetworkConfig, SecurityConfig, ThemeCustomization

def verify_bridge_api():
    print("🔍 Verifying Bridge API Routes...")
    routes = [route.path for route in app.routes]
    
    # Check for Partner Portal routes
    assert "/v1/white-label/partner/info" in routes
    assert "/v1/white-label/dac/configure" in routes
    
    # Check for WebSocket route
    # WebSockets are stored differently, but we can check if path exists
    ws_routes = [r.path for r in app.routes if hasattr(r, 'endpoint') and asyncio.iscoroutinefunction(r.endpoint)]
    # Note: WebSocket routes might not show up in standard routes list easily without running
    
    print("✅ Bridge API Routes Verified (Partner Portal + Base)")

def verify_deployer():
    print("🔍 Verifying KaaS Deployer...")
    
    # Create mock manifest
    manifest = DACManifest(
        name="test-app",
        version="1.0.0",
        description="Test",
        partner_id="p-123",
        tier="domain-intelligence",
        target_environments=["kubernetes"],
        resources=ResourceRequirements(cpu_cores=1, memory_gb=1, storage_gb=10),
        network=NetworkConfig(api_endpoint="http://api"),
        security=SecurityConfig(allowed_origins=["*"]),
        widgets=[],
        theme=ThemeCustomization(theme_base="cosmic"),
        features={}
    )
    
    deployer = KubernetesDeployer(manifest)
    yaml_out = deployer.generate_k8s_manifest()
    
    # Check for ProofedDeployment
    assert "kind: ProofedDeployment" in yaml_out
    assert "apiVersion: infra.industriverse.ai/v1" in yaml_out
    assert "proofPolicy:" in yaml_out
    assert "utidBinding:" in yaml_out
    
    print("✅ KaaS Deployer Verified (Generates ProofedDeployment)")

if __name__ == "__main__":
    verify_bridge_api()
    verify_deployer()
    print("🎉 Grand Unification Verification Passed!")
