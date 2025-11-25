import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.capsule_layer.services.remix_lab_service import (
    create_remix_lab_service,
    RemixComponent,
    ComponentType,
    RemixEventType
)

async def verify_remix_lab_flow():
    print("🧪 Starting Remix Lab Verification...")
    
    service = create_remix_lab_service()
    
    # 1. Create Components
    print("\n1. Creating Components...")
    comp1 = RemixComponent(
        component_id="cap_battery_v1",
        component_type=ComponentType.CAPSULE,
        name="Lithium Battery Capsule",
        version="1.0.0",
        manifest_hash="hash_123",
        signature="sig_123",
        provenance={"source": "core_registry"}
    )
    
    comp2 = RemixComponent(
        component_id="algo_opt_v1",
        component_type=ComponentType.FUNCTION,
        name="Optimization Algorithm",
        version="1.2.0",
        manifest_hash="hash_456",
        signature="sig_456",
        provenance={"source": "user_upload"}
    )
    
    # 2. Create Snapshot
    print("\n2. Creating Snapshot...")
    snapshot = await service.create_snapshot(
        user_id="user_test_001",
        name="Battery Optimizer Remix",
        description="Optimizing battery thermal management",
        components=[comp1, comp2]
    )
    print(f"✅ Snapshot Created: {snapshot.snapshot_id}")
    
    # 3. Simulate
    print("\n3. Simulating Remix...")
    results = await service.simulate_remix(snapshot.snapshot_id)
    print(f"✅ Simulation Results: {results['status']}")
    print(f"   Energy Estimate: {results['energy_estimate_joules']} J")
    
    # 4. Commit
    print("\n4. Committing Remix...")
    commit = await service.commit_remix(
        snapshot.snapshot_id,
        committed_by="user_test_001"
    )
    print(f"✅ Remix Committed: {commit.commit_id}")
    print(f"   UTID: {commit.utid}")
    print(f"   Remix Hash: {commit.remix_hash}")
    
    # 5. Verify UTID Registry
    print("\n5. Verifying UTID Registry...")
    utid_record = service.get_utid_record(commit.utid)
    if utid_record:
        print(f"✅ UTID Record Found: {utid_record.utid}")
    else:
        print("❌ UTID Record NOT Found")
        
    # 6. Verify Events
    print("\n6. Verifying Events...")
    events = service.get_events()
    print(f"✅ Total Events: {len(events)}")
    for evt in events:
        print(f"   - {evt.event_type.value}: {evt.payload.keys()}")

    print("\n🎉 Remix Lab Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_remix_lab_flow())
