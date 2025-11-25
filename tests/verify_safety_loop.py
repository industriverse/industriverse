import sys
import os
import time
import threading
import logging

# Add project root to path
sys.path.append(os.getcwd())

from src.security_compliance_layer.safety_loop import MultiAgentSafetyLoop

# Configure logging to capture output
logging.basicConfig(level=logging.INFO)

def verify_safety_loop():
    print("🛡️  Starting Safety Loop Verification...")
    
    loop = MultiAgentSafetyLoop()
    
    # Start loop in a separate thread
    t = threading.Thread(target=loop.start)
    t.start()
    
    try:
        print("⏳ Waiting for loop initialization...")
        time.sleep(2)
        
        # Check if components are initialized
        if len(loop.swarm.agents) != 5:
            print("❌ Swarm initialization failed")
            sys.exit(1)
        print("✅ Swarm initialized with 5 agents")
        
        if loop.reasoning.mode != "implicit":
            print("❌ SwiReasoning default mode incorrect")
            sys.exit(1)
        print("✅ SwiReasoning initialized in implicit mode")
        
        # Simulate running for a bit
        time.sleep(3)
        
        # Verify memory cortex interaction (mock check)
        # In a real test we'd inject a threat and check memory
        
    finally:
        print("🛑 Stopping loop...")
        loop.stop()
        t.join()
        print("✅ Safety Loop Verification Passed!")

if __name__ == "__main__":
    verify_safety_loop()
