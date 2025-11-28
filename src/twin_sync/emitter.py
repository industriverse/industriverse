"""
Simple telemetry emitter stub for Twin Sync.

In production, replace with websocket/bus publisher.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class TelemetryEmitter:
    def __init__(self, sink=None):
        """
        sink: callable accepting (topic: str, payload: dict)
        """
        self.sink = sink

    def emit(self, event: Dict[str, Any]) -> None:
        topic = event.get("topic")
        payload = event.get("payload", {})
        if self.sink:
            self.sink(topic, payload)
        else:
            logger.debug("Telemetry event %s: %s", topic, payload)
