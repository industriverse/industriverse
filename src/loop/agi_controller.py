import sys
import os
import time
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.maestro.conductor import MaestroConductor
from src.loop.intent_queue import IntentQueue

class AGIController:
    """
    Manufacturing AGI Loop Controller (Phase 65).
    Orchestrates the Perceive -> Plan -> Act -> Verify loop.
    """
    def __init__(self):
        self.maestro = MaestroConductor()
        self.is_running = False
        self.intent_queue = IntentQueue() # Persistent Queue (SQLite)

    def start(self):
        self.is_running = True
        print("AGI Loop Active. Waiting for intents...")
        
        while self.is_running:
            # 1. Poll for Intents
            if self.intent_queue:
                intent = self.intent_queue.pop(0)
                print(f"\n>>> Processing New Intent: '{intent}'")
                
                try:
                    result = self.maestro.process_request(intent)
                    self._log_result(result)
                except Exception as e:
                    print(f"CRITICAL ERROR: {e}")
            
            # 2. Idle Monitoring
            # In real system, check telemetry, health, etc.
            time.sleep(1)

    def stop(self):
        self.is_running = False
        print("AGI Loop Shutdown.")

    def add_intent(self, intent):
        self.intent_queue.append(intent)

    def _log_result(self, result):
        if result['status'] == "SUCCESS":
            print(f"✅ Job Complete. Cost: ${result['price']}")
        else:
            print(f"❌ Job Failed. Reason: {result.get('reason')}")

if __name__ == "__main__":
    controller = AGIController()
    
    # Simulate incoming requests
    controller.add_intent("Make a lightweight precision bracket")
    controller.add_intent("Make a fast gear")
    
    # Run loop briefly
    import threading
    t = threading.Thread(target=controller.start)
    t.start()
    
    time.sleep(10)
    controller.stop()
    t.join()
