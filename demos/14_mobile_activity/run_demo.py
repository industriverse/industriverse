import time
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class MobileSimulator:
    def __init__(self):
        pass

    def update_live_activity(self, activity_id, state):
        """
        Simulates sending a push notification to update an iOS Live Activity.
        """
        # ASCII Art representation of an iPhone Lock Screen Live Activity
        
        progress = state.get("progress", 0)
        status = state.get("status", "Unknown")
        eta = state.get("eta", "--:--")
        
        bar_len = int(progress * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        
        print("\n" + "-"*30)
        print(f" 📱 iPhone Lock Screen Notification")
        print("-" * 30)
        print(f" 🏭 Batch Refining: {activity_id}")
        print(f" Status: {status}")
        print(f" Progress: [{bar}] {int(progress*100)}%")
        print(f" ETA: {eta}")
        print("-" * 30)

def run():
    print("\n" + "="*60)
    print(" DEMO 14: MOBILE LIVE ACTIVITY SIMULATION")
    print("="*60 + "\n")

    sim = MobileSimulator()
    activity_id = "BATCH-4492"

    print("Starting long-running process...")
    
    steps = [
        {"progress": 0.0, "status": "Initializing", "eta": "5m"},
        {"progress": 0.2, "status": "Heating", "eta": "4m"},
        {"progress": 0.4, "status": "Refining", "eta": "3m"},
        {"progress": 0.6, "status": "Refining", "eta": "2m"},
        {"progress": 0.8, "status": "Cooling", "eta": "1m"},
        {"progress": 1.0, "status": "Complete", "eta": "Now"}
    ]

    for step in steps:
        sim.update_live_activity(activity_id, step)
        time.sleep(1)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: MOBILE UPDATE SENT")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
