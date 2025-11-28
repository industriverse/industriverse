"""
WebSocket emitter stub for Shadow Twin.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class WebSocketEmitter:
    def __init__(self, send_coroutine):
        """
        send_coroutine: async callable accepting (topic: str, payload: dict)
        """
        self.send = send_coroutine

    async def emit(self, event: Dict[str, Any]) -> None:
        topic = event.get("topic")
        payload = event.get("payload", {})
        if not topic:
            return
        try:
            await self.send(topic, payload)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to send websocket telemetry topic=%s", topic)
