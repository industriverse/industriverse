import sys
import os
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.maestro.conductor import MaestroConductor

def test_maestro():
    print("\n--- Testing Maestro Conductor ---")
    
    maestro = MaestroConductor()
    
    # Test Request
    prompt = "Make a lightweight precision bracket"
    result = maestro.process_request(prompt)
    
    # Verification
    if result['status'] == "SUCCESS":
        print("✅ Request processed successfully.")
    else:
        print(f"❌ Request failed: {result.get('reason')}")
        
    if result.get('capsule'):
        print(f"✅ Capsule selected: {result['capsule']}")
    else:
        print("❌ No capsule selected.")
        
    if result.get('price') > 0:
        print(f"✅ Price calculated: ${result['price']}")
    else:
        print("❌ Price calculation failed.")
        
    if "⊽0.1" in result['plan']['modifiers']:
        print("✅ Intent modifiers applied (Lightweight -> ⊽0.1).")
    else:
        print("❌ Intent modifiers missing.")

if __name__ == "__main__":
    test_maestro()
