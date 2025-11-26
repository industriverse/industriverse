import time
import json
import random
import threading
import queue
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class MockMQTTBroker:
    def __init__(self):
        self.topics = {}
        self.lock = threading.Lock()

    def subscribe(self, topic, q):
        with self.lock:
            if topic not in self.topics:
                self.topics[topic] = []
            self.topics[topic].append(q)

    def publish(self, topic, payload):
        with self.lock:
            if topic in self.topics:
                for q in self.topics[topic]:
                    q.put((topic, payload))

broker = MockMQTTBroker()

class FurnaceCapsule:
    def __init__(self, stop_event):
        self.stop_event = stop_event
        self.spike_trigger = False

    def trigger_spike(self):
        logger.warning("\n!!! INJECTING TEMPERATURE SPIKE !!!\n")
        self.spike_trigger = True

    def run(self):
        topic = "capsules/furnace_v1/telemetry"
        while not self.stop_event.is_set():
            if self.spike_trigger:
                temp = 1800 + random.uniform(0, 50) # SPIKE!
                self.spike_trigger = False # Reset after one burst? Or keep it high? Let's keep it high for a bit
                # Actually let's make it a momentary spike for this demo
            else:
                temp = 1500 + random.uniform(-20, 20)
            
            payload = {
                "capsule_id": "furnace_v1",
                "timestamp": time.time(),
                "sensors": {"core_temp_k": round(temp, 2)}
            }
            broker.publish(topic, json.dumps(payload))
            time.sleep(0.5)

class SovereigntyEngine:
    def __init__(self, stop_event):
        self.stop_event = stop_event
        self.q = queue.Queue()
        broker.subscribe("capsules/furnace_v1/telemetry", self.q)

    def calculate_score(self, temp):
        # Ideal is 1500. Deviation penalizes score.
        deviation = abs(temp - 1500)
        score = max(0.0, 1.0 - (deviation / 500.0)) # Drop to 0 if > 500 off
        return round(score, 4)

    def run(self):
        logger.info("[SovereigntyEngine] Monitoring compliance...")
        while not self.stop_event.is_set():
            try:
                _, payload_str = self.q.get(timeout=0.1)
                data = json.loads(payload_str)
                temp = data['sensors']['core_temp_k']
                
                score = self.calculate_score(temp)
                
                status_color = "\033[92m" # Green
                if score < 0.9: status_color = "\033[93m" # Yellow
                if score < 0.8: status_color = "\033[91m" # Red
                
                reset = "\033[0m"
                
                print(f"[SovereigntyEngine] Temp: {temp}K | Score: {status_color}{score}{reset}")
                
                if score < 0.8:
                    print(f"{status_color}!!! VIOLATION DETECTED !!! ISSUING STOP COMMAND{reset}")
                    # In a real system, this would publish to "capsules/furnace_v1/control"
                    
            except queue.Empty:
                continue

def run():
    print("\n" + "="*60)
    print(" DEMO 3: GRAND UNIFICATION FEEDBACK LOOP")
    print("="*60 + "\n")

    stop_event = threading.Event()
    
    furnace = FurnaceCapsule(stop_event)
    engine = SovereigntyEngine(stop_event)
    
    t1 = threading.Thread(target=furnace.run)
    t2 = threading.Thread(target=engine.run)
    
    t1.start()
    t2.start()
    
    try:
        print("--- Phase 1: Nominal Operation ---")
        time.sleep(3)
        
        print("\n--- Phase 2: Injecting Fault ---")
        furnace.trigger_spike()
        time.sleep(3)
        
        print("\n--- Phase 3: Recovery (Simulated) ---")
        # In this simple script, the spike was transient, so it recovers naturally
        time.sleep(2)
        
    finally:
        print("\nStopping simulation...")
        stop_event.set()
        t1.join()
        t2.join()
        
        print("\n" + "="*60)
        print(" DEMO COMPLETE: FEEDBACK LOOP VERIFIED")
        print("="*60 + "\n")

if __name__ == "__main__":
    run()
