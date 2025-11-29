import sys
import os
import time
import threading
import io
from contextlib import redirect_stdout

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.loop.agi_controller import AGIController

def test_agi_loop():
    print("\n--- Testing AGI Controller Loop ---")
    
    controller = AGIController()
    controller.add_intent("Make a lightweight precision bracket")
    
    # Capture output
    f = io.StringIO()
    
    def run_loop():
        with redirect_stdout(f):
            controller.start()
            
    t = threading.Thread(target=run_loop)
    t.start()
    
    time.sleep(5) # Allow time for processing
    controller.stop()
    t.join()
    
    output = f.getvalue()
    print(output) # Show output
    
    # Verification
    if "Booting Manufacturing AGI Loop" in output:
        print("✅ Loop Booted.")
    else:
        print("❌ Loop Boot failed.")
        
    if "Processing New Intent" in output:
        print("✅ Intent Picked Up.")
    else:
        print("❌ Intent NOT Picked Up.")
        
    if "Job Complete" in output:
        print("✅ Job Completed Successfully.")
    else:
        print("❌ Job Failed.")

if __name__ == "__main__":
    test_agi_loop()
