import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.core.dynamic_loader import DynamicLoaderService
from src.core.dynamic_loader.k8s_operator import DynamicLoaderOperator

async def verify_sprint_3():
    print("=== Verifying Sprint 3: Scale & Infrastructure ===")
    
    loader = DynamicLoaderService()
    await loader.start()
    
    # 1. Verify ZK Proof Generation
    print("\n--- Testing ZK Proof Integration ---")
    await loader.load_model("userlm-8b", context={"timestamp": 1234567890})
    
    # Check events for proof
    events = loader.event_emitter.get_mock_events()
    load_event = next((e for e in reversed(events) if e["event_type"] == "model_load"), None)
    
    if load_event and "zk_proof" in load_event["context"]:
        proof = load_event["context"]["zk_proof"]
        print(f"✅ ZK Proof generated: {proof.get('type', 'unknown')} | ID: {proof.get('id')}")
    else:
        print("❌ ZK Proof NOT found in load event.")

    # 2. Verify Visualization Update
    print("\n--- Testing Real3Dviewer Integration ---")
    viz_event = next((e for e in reversed(events) if e["event_type"] == "visualization_update"), None)
    if viz_event:
        payload = viz_event["context"]["payload"]
        print(f"✅ Visualization update emitted: {len(payload['models'])} models active.")
        print(f"   Payload: {payload}")
    else:
        print("❌ Visualization update NOT emitted.")

    # 3. Verify Kubernetes Operator
    print("\n--- Testing Kubernetes Operator ---")
    operator = DynamicLoaderOperator(loader)
    
    # Mock a CRD
    await operator.apply_crd("rnd1-phi4", {"context": {"priority": "high"}})
    
    # Run reconcile
    await operator.reconcile()
    
    # Check if model loaded
    if "rnd1-phi4" in loader.get_active_models():
        print("✅ Operator successfully reconciled CRD -> Model Load.")
    else:
        print("❌ Operator failed to load model from CRD.")
        
    # Mock CRD deletion
    await operator.delete_crd("rnd1-phi4")
    await operator.reconcile()
    
    if "rnd1-phi4" not in loader.get_active_models():
        print("✅ Operator successfully reconciled CRD Deletion -> Model Unload.")
    else:
        print("❌ Operator failed to unload model after CRD deletion.")

    await loader.stop()
    print("\n=== Sprint 3 Verification Complete ===")

if __name__ == "__main__":
    asyncio.run(verify_sprint_3())
