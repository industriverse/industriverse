import asyncio
from typing import Dict, Any
from datetime import datetime
# Mock NATS client for now
# from nats.aio.client import Client as NATS

class ACEMemoryLogger:
    """
    Logs agent trajectories to the 'Memory Stream'.
    Subscribes to NATS events and persists them for reflection.
    """
    
    def __init__(self):
        self.logs = []
        
    async def log_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Log an event to the memory stream.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "payload": payload
        }
        self.logs.append(entry)
        
        # In real implementation: await self.nc.publish(f"ace.memory.{event_type}", json.dumps(entry).encode())
        print(f"[ACE Memory] Logged: {event_type}")

    def get_recent_logs(self, limit: int = 10):
        return self.logs[-limit:]
