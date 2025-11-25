# Minimal NATS -> WebSocket bridge for local HUD testing.
import asyncio
import json
import websockets
from nats.aio.client import Client as NATS

NATS_URL = "nats://nats:4222"
WS_PORT = 8765
clients = set()


async def nats_to_ws():
    nc = NATS()
    await nc.connect(NATS_URL)

    async def cb(msg):
        data = msg.data.decode()
        for ws in clients.copy():
            try:
                await ws.send(data)
            except Exception:
                pass

    await nc.subscribe("telemetry.*", cb)
    await asyncio.Future()  # run forever


async def ws_handler(ws):
    clients.add(ws)
    try:
        async for _ in ws:
            pass
    finally:
        clients.discard(ws)


async def main():
    server = await websockets.serve(ws_handler, "0.0.0.0", WS_PORT)
    await asyncio.gather(server.wait_closed(), nats_to_ws())


if __name__ == "__main__":
    asyncio.run(main())
