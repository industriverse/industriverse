"""
TouchDesigner WebSocket Bridge

Connects TouchDesigner to Three.js via WebSocket for real-time data visualization.

Architecture:
- Receives factory metrics from Capsule Gateway
- Generates procedural geometry in TouchDesigner
- Exports textures and geometry to Three.js
- Sends updates via WebSocket

Based on production patterns from:
- https://github.com/benjaminben/td-threejs-tutorial
- https://derivative.ca/community-post/tutorial/enhanced-web-workflows-touchdesigner-threejs/63831
"""

import asyncio
import websockets
import json
from typing import Dict, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime

# ============================================================================
# Types
# ============================================================================

@dataclass
class FactoryMetrics:
    temperature: float      # Celsius (0-100)
    pressure: float          # PSI (0-100)
    vibration: float         # Hz (0-100)
    production_rate: float   # Units/hour (0-100)
    noise: float             # dB (0-100)
    timestamp: int           # Unix timestamp

@dataclass
class CapsuleUpdate:
    capsule_id: str
    status: str  # 'critical', 'warning', 'active', 'resolved', 'dismissed'
    metrics: FactoryMetrics
    position: Dict[str, float]  # {x, y, z}

# ============================================================================
# TouchDesignerBridge
# ============================================================================

class TouchDesignerBridge:
    def __init__(self, host: str = "localhost", port: int = 9980):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.capsules: Dict[str, CapsuleUpdate] = {}
        
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        print(f"[TouchDesigner Bridge] Client connected: {websocket.remote_address}")
        
        # Send current state to new client
        for capsule_id, capsule in self.capsules.items():
            await self.send_metrics_update(websocket, capsule)
    
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister WebSocket client"""
        self.clients.remove(websocket)
        print(f"[TouchDesigner Bridge] Client disconnected: {websocket.remote_address}")
    
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle WebSocket client connection"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            if data.get('type') == 'capsule_update':
                await self.handle_capsule_update(data)
            elif data.get('type') == 'request_texture':
                await self.handle_texture_request(websocket, data)
            elif data.get('type') == 'request_geometry':
                await self.handle_geometry_request(websocket, data)
        except json.JSONDecodeError:
            print(f"[TouchDesigner Bridge] Invalid JSON: {message}")
    
    async def handle_capsule_update(self, data: Dict[str, Any]):
        """Handle capsule update from Capsule Gateway"""
        capsule_id = data.get('capsule_id')
        status = data.get('status')
        metrics_data = data.get('metrics', {})
        position = data.get('position', {'x': 0, 'y': 0, 'z': 0})
        
        # Create metrics object
        metrics = FactoryMetrics(
            temperature=metrics_data.get('temperature', 0),
            pressure=metrics_data.get('pressure', 0),
            vibration=metrics_data.get('vibration', 0),
            production_rate=metrics_data.get('production_rate', 0),
            noise=metrics_data.get('noise', 0),
            timestamp=int(datetime.now().timestamp())
        )
        
        # Create capsule update
        capsule = CapsuleUpdate(
            capsule_id=capsule_id,
            status=status,
            metrics=metrics,
            position=position
        )
        
        # Store capsule
        self.capsules[capsule_id] = capsule
        
        # Broadcast to all clients
        await self.broadcast_metrics_update(capsule)
    
    async def send_metrics_update(self, websocket: websockets.WebSocketServerProtocol, capsule: CapsuleUpdate):
        """Send metrics update to specific client"""
        message = {
            'type': 'metrics_update',
            'capsule_id': capsule.capsule_id,
            'metrics': asdict(capsule.metrics)
        }
        
        await websocket.send(json.dumps(message))
    
    async def broadcast_metrics_update(self, capsule: CapsuleUpdate):
        """Broadcast metrics update to all clients"""
        if not self.clients:
            return
        
        message = {
            'type': 'metrics_update',
            'capsule_id': capsule.capsule_id,
            'metrics': asdict(capsule.metrics)
        }
        
        await asyncio.gather(
            *[client.send(json.dumps(message)) for client in self.clients],
            return_exceptions=True
        )
    
    async def handle_texture_request(self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle texture request from client"""
        capsule_id = data.get('capsule_id')
        
        # In production, generate texture in TouchDesigner and export
        # For now, send placeholder URL
        texture_url = f"http://localhost:8080/textures/{capsule_id}.png"
        
        message = {
            'type': 'texture_update',
            'capsule_id': capsule_id,
            'texture_url': texture_url
        }
        
        await websocket.send(json.dumps(message))
    
    async def handle_geometry_request(self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle geometry request from client"""
        capsule_id = data.get('capsule_id')
        
        # In production, generate geometry in TouchDesigner and export
        # For now, send placeholder URL
        geometry_url = f"http://localhost:8080/geometry/{capsule_id}.obj"
        
        message = {
            'type': 'geometry_update',
            'capsule_id': capsule_id,
            'geometry_url': geometry_url
        }
        
        await websocket.send(json.dumps(message))
    
    async def start(self):
        """Start WebSocket server"""
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"[TouchDesigner Bridge] WebSocket server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    bridge = TouchDesignerBridge()
    asyncio.run(bridge.start())
