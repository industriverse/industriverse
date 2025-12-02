import sys
import os
import time
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.infrastructure.nats_event_bus import NATSEventBus
from src.infrastructure.stream_manager import StreamManager

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_nats_integration():
    print_header("DEMO: THE GLOBAL EVENT BUS (NATS JETSTREAM)")
    print("Scenario: High-Speed Sensor Telemetry & Time Travel")
    
    # 1. Initialize Infrastructure
    bus = NATSEventBus()
    mgr = StreamManager(bus)
    
    # 2. Create Stream
    print("\n>> STEP 1: Creating Persistent Stream...")
    mgr.create_stream("USM_TELEMETRY", ["usm.*"])
    
    # 3. The Firehose (Publishing)
    print("\n>> STEP 2: Unleashing the Firehose (100 Events)...")
    start_time = time.time()
    
    for i in range(100):
        sensor_type = random.choice(["thermal", "vibration", "power"])
        value = random.uniform(0, 100)
        payload = {"id": i, "val": f"{value:.2f}"}
        bus.publish(f"usm.sensor.{sensor_type}", payload)
        
    duration = time.time() - start_time
    print(f"   ✅ Published 100 events in {duration:.4f}s")
    
    # 4. Verification
    print("\n>> STEP 3: Verifying Persistence...")
    stored_count = len(mgr.streams["USM_TELEMETRY"])
    print(f"   Stream 'USM_TELEMETRY' contains {stored_count} events.")
    
    if stored_count == 100:
        print("   ✅ All events captured.")
    else:
        print("   ❌ Data Loss Detected.")
        
    # 5. Replay (Time Travel)
    print("\n>> STEP 4: Time Travel (Replay)...")
    print("   Replaying last 5 events for debugging...")
    stream = mgr.streams["USM_TELEMETRY"]
    for msg in stream[-5:]:
        print(f"   ⏪ [REPLAY] {msg}")
        
    print_header("DEMO COMPLETE: NERVOUS SYSTEM OPERATIONAL")

if __name__ == "__main__":
    demo_nats_integration()
