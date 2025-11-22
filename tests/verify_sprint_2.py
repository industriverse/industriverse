import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.core.dynamic_loader import DynamicLoaderService
from src.core.dynamic_loader.scheduler import TokenScheduler

async def verify_sprint_2():
    print("=== Verifying Sprint 2: Optimization & Adapters ===")
    
    loader = DynamicLoaderService()
    await loader.start()
    
    # 1. Verify LoRA Adapter Load
    print("\n--- Testing LoRA Adapter Load ---")
    await loader.load_model("userlm-8b")
    success = await loader.load_adapter("userlm-8b", "lithium-expert", context={"intent": "refine"})
    if success:
        print("✅ Adapter 'lithium-expert' loaded.")
        adapters = loader.get_active_adapters("userlm-8b")
        print(f"Active Adapters: {adapters}")
    else:
        print("❌ Adapter load failed.")

    # 2. Verify Rollback Mechanism
    print("\n--- Testing Hot-Swap Rollback ---")
    # Attempt to load with simulated failure
    success = await loader.load_model("rnd1-phi4", context={"simulate_failure": True})
    if not success:
        print("✅ Load failed as expected.")
        # Check events for rollback
        events = loader.event_emitter.get_mock_events()
        rollback_event = next((e for e in reversed(events) if e["event_type"] == "rollback"), None)
        if rollback_event:
            print(f"✅ Rollback event detected: {rollback_event['context']['reason']}")
        else:
            print("❌ Rollback event NOT found.")
    else:
        print("❌ Load succeeded unexpectedly.")

    await loader.stop()

    # 3. Verify Scheduler Prototype
    print("\n--- Testing Token Scheduler ---")
    scheduler = TokenScheduler(time_slice_ms=10)
    
    # Submit requests
    await scheduler.submit_request("userlm-8b", "Hello", priority=1)
    await scheduler.submit_request("rnd1-phi4", "Compute X", priority=2)
    
    # Run loop briefly
    task = asyncio.create_task(scheduler.start_loop())
    await asyncio.sleep(0.2)
    scheduler.stop()
    await task

    print("\n=== Sprint 2 Verification Complete ===")

if __name__ == "__main__":
    asyncio.run(verify_sprint_2())
