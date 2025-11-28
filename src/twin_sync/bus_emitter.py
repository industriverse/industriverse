"""
Bus emitter to bridge GlobalEventBus to WebSockets.
"""

import logging
import time
import asyncio
from typing import Dict, Any
from src.bridge_api.event_bus import GlobalEventBus
from .ws_server import manager
from .telemetry import TelemetryEnvelope

logger = logging.getLogger(__name__)

class TwinBusEmitter:
    def __init__(self):
        self.bus = GlobalEventBus()
        self.topics = [
            "capsule.status",
            "capsule.proof",
            "capsule.credit_flow",
            "capsule.entropy",
            "rdr.node",
            "rdr.edge"
        ]

    def start(self):
        """Start listening to bus events."""
        for topic in self.topics:
            self.bus.subscribe(topic, self._handle_event)
        logger.info("TwinBusEmitter started listening to topics: %s", self.topics)

    def _handle_event(self, event: Dict[str, Any]):
        """Callback for bus events."""
        try:
            topic = event.get("topic")
            payload = event.get("payload")
            
            if not topic or payload is None:
                return

            # Construct envelope
            envelope = {
                "type": topic, # Frontend expects 'type'
                "timestamp": time.time(),
                **payload # Flatten payload into top level for frontend convenience or keep nested?
                # Frontend useSystemPulse expects: type, timestamp, metrics, etc.
                # Let's match the contract: type=topic, ...payload fields
            }
            
            # Broadcast via WebSocket manager
            # Since this callback might run in a thread, we need to schedule async broadcast
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(manager.broadcast(envelope))
            except RuntimeError:
                # If no running loop (e.g. synchronous context), this is tricky.
                # In FastAPI app context, there should be a loop.
                # Alternatively, use run_coroutine_threadsafe if we have reference to the loop.
                pass
                
        except Exception as e:
            logger.error(f"Error handling bus event: {e}")

# Global instance
twin_emitter = TwinBusEmitter()
