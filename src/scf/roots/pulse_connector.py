import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from src.bridge_api.event_bus import GlobalEventBus

class PulseConnector:
    """
    Connects the SCF to the System Pulse (Real-time Telemetry).
    Uses GlobalEventBus for in-process communication.
    """
    def __init__(self):
        self.connected = False
        self.latest_pulse = {}
        self.logger = logging.getLogger("PulseConnector")

    async def connect(self):
        """
        Establishes connection to the Pulse (Event Bus).
        """
        if self.connected:
            return
            
        self.logger.info("🔌 Connecting to Pulse (GlobalEventBus)...")
        
        # Subscribe to updates
        GlobalEventBus.subscribe(self._on_pulse_event)
        self.connected = True
        self.logger.info("✅ Connected to Pulse.")

    async def _on_pulse_event(self, event: Dict[str, Any]):
        """
        Callback for incoming pulse events.
        """
        if event.get("type") == "system_heartbeat":
            self.latest_pulse = event

    async def fetch_latest(self) -> Dict[str, Any]:
        """
        Returns the latest aggregated telemetry snapshot.
        Includes automatic reconnection logic.
        """
        if not self.connected:
            await self.connect()
            
        # Return latest received pulse, or a fallback if empty
        if self.latest_pulse:
            return self.latest_pulse
            
        # Fallback/Initial State
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_power_watts": 0.0,
                "avg_temperature_c": 0.0,
                "system_entropy": 0.0
            },
            "shield_state": "UNKNOWN",
            "status": "WAITING_FOR_PULSE"
        }

    async def close(self):
        if self.connected:
            GlobalEventBus.unsubscribe(self._on_pulse_event)
            self.connected = False
        self.logger.info("Disconnected from Pulse.")
