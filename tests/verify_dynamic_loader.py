import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.core.dynamic_loader import DynamicLoaderService
from src.core.persona import PersonaRegistry
from src.core.userlm import UserLMService

async def verify_sprint_1():
    print("=== Verifying Sprint 1: Foundation & UX ===")
    
    # 1. Verify Dynamic Loader Events
    print("\n--- Testing Dynamic Loader Events ---")
    loader = DynamicLoaderService()
    await loader.start()
    
    success = await loader.load_model("userlm-8b", context={"intent": "test_load"})
    if success:
        print("✅ Model loaded successfully.")
    else:
        print("❌ Model load failed.")
        
    # Check emitted events (Mock)
    events = loader.event_emitter.get_mock_events()
    if len(events) > 0:
        last_event = events[-1]
        print(f"✅ Event emitted: {last_event['event_type']} | Hash: {last_event['model_hash']}")
        if "signature" in last_event:
            print("✅ Event is signed.")
    else:
        print("❌ No events emitted.")
        
    await loader.stop()

    # 2. Verify Persona Registry
    print("\n--- Testing Persona Registry ---")
    registry = PersonaRegistry()
    personas = registry.list_personas()
    print(f"Found {len(personas)} default personas.")
    
    expert = registry.get_persona("Expert Engineer")
    if expert:
        print(f"✅ Retrieved persona: {expert.name}")
    else:
        print("❌ Failed to retrieve 'Expert Engineer' persona.")

    # 3. Verify UserLM Streaming
    print("\n--- Testing UserLM Streaming ---")
    user_lm = UserLMService(timeout_seconds=5.0)
    persona_dict = {"name": "TestUser"}
    
    print("Streaming response: ", end="", flush=True)
    token_count = 0
    async for token in user_lm.generate_turn_stream("Test Intent", [], persona_dict):
        print(token, end="", flush=True)
        token_count += 1
    print("\n")
    
    if token_count > 0:
        print(f"✅ Received {token_count} tokens.")
    else:
        print("❌ No tokens received.")

    print("\n=== Sprint 1 Verification Complete ===")

if __name__ == "__main__":
    asyncio.run(verify_sprint_1())
