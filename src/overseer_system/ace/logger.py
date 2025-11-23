import json
import asyncio
import os
from typing import Optional, Dict, Any
from datetime import datetime
from .schema import TrajectoryLog, StepType, Outcome, LogMetrics

# Try to import nats, but handle failure gracefully for dev environments
try:
    import nats
    from nats.aio.client import Client as NATS
    from nats.js.api import StreamConfig
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False

class ACEMemoryLogger:
    def __init__(self, nats_url: str = "nats://localhost:4222", stream_name: str = "ace_logs"):
        self.nats_url = nats_url
        self.stream_name = stream_name
        self.nc: Optional[NATS] = None
        self.js = None
        self.connected = False
        self._mock_logs = [] # For testing/dev when NATS is offline

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
            self.connected = True
            print(f"Connected to NATS JetStream: {self.stream_name}")
        except Exception as e:
            print(f"WARNING: Could not connect to NATS: {e}. Running in MOCK mode.")
            self.connected = False

    async def log(self, 
                  agent_id: str, 
                  step_type: StepType, 
                  content: str, 
                  outcome: Outcome = Outcome.UNKNOWN,
                  metrics: Optional[LogMetrics] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> TrajectoryLog:
        """
        Log an event to the ACE memory stream.
        """
        if metrics is None:
            metrics = LogMetrics()
        if metadata is None:
            metadata = {}

        log_entry = TrajectoryLog(
            agent_id=agent_id,
            step_type=step_type,
            content=content,
            outcome=outcome,
            metrics=metrics,
            metadata=metadata
        )

        # Serialize
        payload = log_entry.json().encode()
        subject = f"{self.stream_name}.{agent_id}"

        if self.connected and self.js:
            try:
                await self.js.publish(subject, payload)
            except Exception as e:
                print(f"Error publishing to NATS: {e}")
        else:
            # Mock behavior
            self._mock_logs.append(log_entry)
            # print(f"[MOCK ACE LOG] {subject}: {log_entry.json()[:100]}...")

        return log_entry

    async def close(self):
        if self.nc:
            await self.nc.close()

    async def get_recent_logs(self, limit: int = 100):
        """Retrieve recent logs (Mock implementation for now, real one would query NATS/DB)."""
        if self.connected:
            # In a real implementation, we'd query a consumer or a materialized view
            # For now, we return empty or implement a basic fetch if needed
            return [] 
        return self._mock_logs[-limit:]
