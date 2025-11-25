"""
Production-oriented emitter placeholder that can publish to a message bus.
Swap sink with Kafka/NATS/etc. in deployment.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


class BusEmitter:
    def __init__(self, publish_fn: Callable[[str, bytes], None]):
        self.publish_fn = publish_fn

    def emit(self, event: Dict[str, Any]) -> None:
        topic = event.get("topic")
        payload = event.get("payload", {})
        if not topic:
            return
        try:
            self.publish_fn(topic, json.dumps(payload).encode("utf-8"))
        except Exception:  # noqa: BLE001
            logger.exception("Failed to publish telemetry topic=%s", topic)
