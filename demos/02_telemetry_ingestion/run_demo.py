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
    """
    Simulates an MQTT Broker in memory to demonstrate pub/sub mechanics
    without requiring an external service like Mosquitto.
    """
    def __init__(self):
        self.topics = {} # topic -> list of callback queues
        self.lock = threading.Lock()

    def subscribe(self, topic, q):
        with self.lock:
            if topic not in self.topics:
                self.topics[topic] = []
            self.topics[topic].append(q)
            logger.info(f"  -> [Broker] New subscription on topic: {topic}")

    def publish(self, topic, payload):
        with self.lock:
            if topic in self.topics:
                for q in self.topics[topic]:
                    q.put((topic, payload))

broker = MockMQTTBroker()

def furnace_capsule_simulator(stop_event):
    """
    Simulates a 'Furnace' capsule emitting high-frequency telemetry.
    """
    logger.info("[Furnace] Booting up sensor array...")
    time.sleep(1)
    
    topic = "capsules/furnace_v1/telemetry"
    
    while not stop_event.is_set():
        # Simulate physics
        temp = 1500 + random.uniform(-20, 50) # Base 1500K
        pressure = 100 + random.uniform(-5, 5) # Base 100 Bar
        vibration = random.uniform(0, 0.5)
        
        # Create payload
        payload = {
            "capsule_id": "furnace_v1",
            "timestamp": time.time(),
            "sensors": {
                "core_temp_k": round(temp, 2),
                "chamber_pressure_bar": round(pressure, 2),
                "vibration_mm": round(vibration, 4)
            },
            "status": "NOMINAL" if temp < 1540 else "WARNING"
        }
        
        msg = json.dumps(payload)
        broker.publish(topic, msg)
        # logger.info(f"[Furnace] -> PUB {topic}: {msg}") # Commented out to reduce noise, dashboard will show it
        
        time.sleep(0.2) # 5Hz update rate

def dashboard_subscriber(stop_event):
    """
    Simulates the 'God View' dashboard ingesting data.
    """
    q = queue.Queue()
    topic = "capsules/furnace_v1/telemetry"
    broker.subscribe(topic, q)
    
    logger.info("[Dashboard] Connected to telemetry stream.")
    
    while not stop_event.is_set():
        try:
            # Non-blocking get
            _, payload_str = q.get(timeout=0.1)
            data = json.loads(payload_str)
            
            # Visualize
            temp = data['sensors']['core_temp_k']
            status = data['status']
            
            # Simple ASCII visualization
            bar_len = int((temp - 1400) / 5)
            bar = "█" * max(0, min(bar_len, 40))
            
            color = "\033[92m" if status == "NOMINAL" else "\033[91m" # Green or Red
            reset = "\033[0m"
            
            print(f"[Dashboard] {color}{status}{reset} | Temp: {temp}K {bar}")
            
        except queue.Empty:
            continue

def run():
    print("\n" + "="*60)
    print(" DEMO 2: REAL-TIME TELEMETRY INGESTION")
    print("="*60 + "\n")

    stop_event = threading.Event()

    # Start Subscriber (Dashboard)
    sub_thread = threading.Thread(target=dashboard_subscriber, args=(stop_event,))
    sub_thread.start()
    
    # Start Publisher (Furnace)
    pub_thread = threading.Thread(target=furnace_capsule_simulator, args=(stop_event,))
    pub_thread.start()

    try:
        # Run for 5 seconds
        time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nStopping simulation...")
        stop_event.set()
        pub_thread.join()
        sub_thread.join()
        
        print("\n" + "="*60)
        print(" DEMO COMPLETE: TELEMETRY STREAM VERIFIED")
        print("="*60 + "\n")

if __name__ == "__main__":
    run()
