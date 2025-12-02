from typing import Callable, Dict, List, Any
import time
import uuid

class NATSEventBus:
    """
    A Mock NATS Client.
    Provides high-speed Publish-Subscribe messaging.
    """
    
    def __init__(self):
        self.subscriptions: Dict[str, List[Callable]] = {}
        print("   🚀 [NATS] Client Connected (URL: nats://localhost:4222)")
        
    def publish(self, subject: str, payload: Any):
        """
        Publishes a message to a subject.
        """
        # print(f"     -> 📤 [PUB] {subject}: {str(payload)[:50]}...")
        
        # Deliver to local subscribers (Mock)
        if subject in self.subscriptions:
            for callback in self.subscriptions[subject]:
                callback(payload)
                
        # Wildcard support (Simplified: 'usm.*')
        parts = subject.split('.')
        if len(parts) > 1:
            wildcard = f"{parts[0]}.*"
            if wildcard in self.subscriptions:
                for callback in self.subscriptions[wildcard]:
                    callback(payload)

    def subscribe(self, subject: str, callback: Callable):
        """
        Subscribes to a subject.
        """
        if subject not in self.subscriptions:
            self.subscriptions[subject] = []
        self.subscriptions[subject].append(callback)
        print(f"     -> 📥 [SUB] Subscribed to '{subject}'")
        
    def request(self, subject: str, payload: Any, timeout: float = 1.0) -> Any:
        """
        Simulates Request-Reply pattern.
        """
        print(f"     -> ❓ [REQ] {subject}")
        # Mock response
        return {"status": "OK", "reply_to": str(uuid.uuid4())}

# --- Verification ---
if __name__ == "__main__":
    bus = NATSEventBus()
    
    def on_msg(msg):
        print(f"Received: {msg}")
        
    bus.subscribe("test.subject", on_msg)
    bus.publish("test.subject", "Hello NATS")
