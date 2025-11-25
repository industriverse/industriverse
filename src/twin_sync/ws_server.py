"""
WebSocket server skeleton for Shadow Twin telemetry.

Production:
- Use an ASGI server (e.g., FastAPI/Starlette) and broadcast events to clients.
- Add auth and rate limiting.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Set

logger = logging.getLogger(__name__)


class WSServer:
    def __init__(self) -> None:
        self.clients: Set[Any] = set()

    async def register(self, ws) -> None:
        self.clients.add(ws)

    async def unregister(self, ws) -> None:
        self.clients.discard(ws)

    async def broadcast(self, topic: str, payload: Dict[str, Any]) -> None:
        msg = json.dumps({"topic": topic, "payload": payload})
        for ws in list(self.clients):
            try:
                await ws.send_str(msg)
            except Exception:  # noqa: BLE001
                logger.debug("Dropping client")
                await self.unregister(ws)
