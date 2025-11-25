import asyncio
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.bridge_api.thermodynamic_router import create_bridge_api
from src.bridge_api.models.orchestrator_models import DeploymentRequest
from src.bridge_api.services.orchestrator_service import OrchestratorService
from src.white_label.credit_protocol.utid_marketplace import get_utid_marketplace
from src.capsule_layer.services.remix_lab_service import create_remix_lab_service, RemixComponent, ComponentType

async def verify_grand_unification():
    print("🌌 Starting Grand Unification Verification...")
    
    # Clean up
    if os.path.exists("data/marketplace_storage.json"):
        os.remove("data/marketplace_storage.json")
    if os.path.exists("data/asal_behavior_log.jsonl"):
        os.remove("data/asal_behavior_log.jsonl")

    # 1. Initialize Bridge API (starts all services)
    print("\n1. Initializing Bridge API...")
    bridge = create_bridge_api(enable_mcp=False)
    
    # 2. Deploy Package (Simulate)
    print("\n2. Deploying 'AI Services' Package...")
    orchestrator = OrchestratorService() # In reality, bridge would have this, but for test we instantiate
    
    req = DeploymentRequest(
        package_id="pkg-02-ai",
        tenant_id="tenant_001",
        user_id="user_grand_unified",
        target_cluster="cluster-01",
        configuration={}
    )
    
    # Trigger deployment
    resp = await orchestrator.deploy_package(req)
    print(f"   Deployment Initiated: {resp.deployment_id}")
    
    # Wait for simulation to complete (it has sleeps)
    # We'll wait a bit longer than the sum of sleeps (13s)
    print("   Waiting for deployment simulation (approx 15s)...")
    await asyncio.sleep(15)
    
    # 3. Verify Widget Unlock
    print("\n3. Verifying Widget Unlock...")
    marketplace = get_utid_marketplace()
    access_grants = marketplace.get_user_insights("user_grand_unified")
    
    ai_shield_unlocked = False
    for grant in access_grants:
        if grant.insight_id == "WIDGET-AI_SHIELD":
            ai_shield_unlocked = True
            print(f"✅ Widget Unlocked: {grant.insight_id}")
            
    if not ai_shield_unlocked:
        print("❌ AI Shield Widget NOT Unlocked")
        return

    # 4. Remix Capsule (using the unlocked widget capability)
    print("\n4. Remixing Capsule...")
    remix_lab = create_remix_lab_service()
    
    comp1 = RemixComponent(
        component_id="cap_ai_shield_v1",
        component_type=ComponentType.CAPSULE,
        name="AI Shield Core",
        version="2.1.0",
        manifest_hash="hash_shield",
        signature="sig_shield",
        provenance={"source": "pkg-02-ai"}
    )
    
    snapshot = await remix_lab.create_snapshot(
        user_id="user_grand_unified",
        name="Shielded Battery Remix",
        description="Battery capsule with AI Shielding",
        components=[comp1]
    )
    
    commit = await remix_lab.commit_remix(
        snapshot.snapshot_id,
        committed_by="user_grand_unified"
    )
    print(f"✅ Remix Committed: {commit.utid}")
    
    # 5. Verify ASAL Log
    print("\n5. Verifying ASAL Governance Log...")
    if os.path.exists("data/asal_behavior_log.jsonl"):
        with open("data/asal_behavior_log.jsonl", "r") as f:
            logs = [json.loads(line) for line in f]
            
        found_deployment = False
        found_remix = False
        
        for log in logs:
            if log["event_type"] == "deployment_complete":
                found_deployment = True
            if log["event_type"] == "remix_committed":
                found_remix = True
                
        if found_deployment:
            print("✅ ASAL Logged: Deployment Complete")
        else:
            print("❌ ASAL Missing: Deployment Complete")
            
        if found_remix:
            print("✅ ASAL Logged: Remix Committed")
        else:
            print("❌ ASAL Missing: Remix Committed")
    else:
        print("❌ ASAL Log File NOT Found")

    print("\n🎉 Grand Unification Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_grand_unification())
