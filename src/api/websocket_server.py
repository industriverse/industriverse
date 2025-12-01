import asyncio
import json
import random
import time
import sys
import os

# Try to import FastAPI/Uvicorn
try:
    from fastapi import FastAPI, WebSocket
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️  FastAPI/Uvicorn not found. Using Mock Server for demonstration.")

# Mock Data Generator
def generate_telemetry():
    return {
        "timestamp": time.time(),
        "temperature": 20.0 + random.random() * 5.0,
        "vibration": random.random() * 0.1,
        "entropy": 10.0 + random.random(),
        "status": "NOMINAL"
    }

if FASTAPI_AVAILABLE:
    app = FastAPI()

    @app.websocket("/ws/telemetry")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        print("🔵 Client Connected to Holographic Stream")
        try:
            while True:
                data = generate_telemetry()
                await websocket.send_json(data)
                await asyncio.sleep(0.1) # 10Hz
        except Exception as e:
            print(f"🔴 Client Disconnected: {e}")

    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=8000)

else:
    # Mock Server Logic
    class MockWebSocketServer:
        def run(self):
            print("🔵 [Mock] Holographic Server Started on ws://localhost:8000")
            print("   Streaming Telemetry (Ctrl+C to stop)...")
            try:
                for _ in range(5):
                    data = generate_telemetry()
                    print(f"   📤 Sending: {json.dumps(data)}")
                    time.sleep(0.5)
                print("✅ [Mock] Stream Complete.")
            except KeyboardInterrupt:
                pass

    def run_server():
        server = MockWebSocketServer()
        server.run()

if __name__ == "__main__":
    run_server()
