import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import asyncio

try:
    import nats
    from nats.aio.client import Client as NATS
    from nats.js.api import StreamConfig
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False

class DynamicLoaderEventEmitter:
    def __init__(self, nats_url: str = "nats://localhost:4222", stream_name: str = "loader_events"):
        self.nats_url = nats_url
        self.stream_name = stream_name
        self.nc: Optional[NATS] = None
        self.js = None
        self._mock_events = []

    async def connect(self):
        """Connect to NATS JetStream."""
        if not NATS_AVAILABLE:
            print("WARNING: NATS client library not found. Running in MOCK mode.")
            return

        try:
            self.nc = await nats.connect(self.nats_url)
            self.js = self.nc.jetstream()
            
            # Ensure stream exists
            await self.js.add_stream(name=self.stream_name, subjects=[f"{self.stream_name}.*"])
            print(f"Connected to NATS JetStream: {self.stream_name}")
        except Exception as e:
            print(f"WARNING: Could not connect to NATS: {e}. Running in MOCK mode.")
            self.nc = None

    async def emit_event(self, event_type: str, model_hash: str, context: Dict[str, Any], utid: Optional[str] = None):
        """Emit a signed dynamic loader event."""
        if not utid:
            utid = str(uuid.uuid4())
            
        timestamp = datetime.now(timezone.utc).isoformat()
        
        payload = {
            "event_type": event_type,
            "utid": utid,
            "timestamp": timestamp,
            "model_hash": model_hash,
            "context": context
        }
        
        # Sign the payload (Mock signature for now)
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(payload_str.encode()).hexdigest() # Placeholder for real crypto signature
        payload["signature"] = signature
        
        data = json.dumps(payload).encode()
        
        if self.nc and self.js:
            try:
                subject = f"{self.stream_name}.{event_type}"
                await self.js.publish(subject, data)
                print(f"Published event to {subject}: {utid}")
            except Exception as e:
                print(f"Error publishing to NATS: {e}")
        else:
            self._mock_events.append(payload)
            print(f"[MOCK] Emitted Event: {event_type} - {utid}")

    async def close(self):
        if self.nc:
            await self.nc.close()

    # Helper for testing
    def get_mock_events(self):
        return self._mock_events
