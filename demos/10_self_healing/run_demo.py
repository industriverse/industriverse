import time
import threading
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class Service:
    def __init__(self, name):
        self.name = name
        self.running = False
        self.health = 100

    def start(self):
        self.running = True
        self.health = 100
        logger.info(f"[{self.name}] Started.")

    def crash(self):
        self.running = False
        self.health = 0
        logger.error(f"[{self.name}] CRASHED!")

class AIShield:
    def __init__(self, services):
        self.services = services
        self.monitoring = True

    def monitor(self):
        logger.info("[AI Shield] Monitoring active...")
        while self.monitoring:
            for svc in self.services:
                if not svc.running:
                    logger.warning(f"[AI Shield] Detected failure in {svc.name}!")
                    self.heal(svc)
            time.sleep(1)

    def heal(self, service):
        logger.info(f"[AI Shield] Initiating recovery protocol for {service.name}...")
        time.sleep(0.5) # Analyze logs
        logger.info(f"[AI Shield] Diagnosis: Memory Leak. Action: Restart.")
        service.start()
        logger.info(f"[AI Shield] {service.name} restored to full health.")

def run():
    print("\n" + "="*60)
    print(" DEMO 10: SELF-HEALING (AI SHIELD V2)")
    print("="*60 + "\n")

    # Setup
    api_gateway = Service("API_Gateway")
    data_ingest = Service("Data_Ingest")
    
    api_gateway.start()
    data_ingest.start()

    shield = AIShield([api_gateway, data_ingest])
    
    # Start Shield in background
    t = threading.Thread(target=shield.monitor)
    t.start()

    time.sleep(2)

    print("\n--- Injecting Failure ---")
    data_ingest.crash()

    time.sleep(3)

    print("\n--- Verifying Restoration ---")
    if data_ingest.running:
        print("SUCCESS: Service is running.")
    else:
        print("FAILURE: Service is still down.")

    # Cleanup
    shield.monitoring = False
    t.join()

    print("\n" + "="*60)
    print(" DEMO COMPLETE: SYSTEM HEALED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
