from typing import Dict, List, Any
from src.infrastructure.nats_event_bus import NATSEventBus

class StreamManager:
    """
    The JetStream Controller.
    Manages persistent event streams and consumers.
    """
    
    def __init__(self, bus: NATSEventBus):
        self.bus = bus
        self.streams: Dict[str, List[Any]] = {} # Stream Name -> List of Messages
        print("   🌪️ [JETSTREAM] Manager Initialized.")
        
    def create_stream(self, name: str, subjects: List[str]):
        """
        Creates a persistent stream consuming specific subjects.
        """
        self.streams[name] = []
        
        # Hook into the bus to capture messages
        def capture(msg):
            self.streams[name].append(msg)
            # print(f"       [STREAM] {name} captured event.")
            
        for subject in subjects:
            self.bus.subscribe(subject, capture)
            
        print(f"     -> 🌊 Created Stream '{name}' listening on {subjects}")
        
    def replay_stream(self, name: str):
        """
        Replays all messages in a stream.
        """
        if name in self.streams:
            print(f"     -> ⏪ Replaying Stream '{name}' ({len(self.streams[name])} events)...")
            for msg in self.streams[name]:
                print(f"        [REPLAY] {msg}")
        else:
            print(f"     -> ❌ Stream '{name}' not found.")

# --- Verification ---
if __name__ == "__main__":
    bus = NATSEventBus()
    mgr = StreamManager(bus)
    mgr.create_stream("TEST_STREAM", ["test.*"])
    
    bus.publish("test.1", "Event 1")
    bus.publish("test.2", "Event 2")
    
    mgr.replay_stream("TEST_STREAM")
