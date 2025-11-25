import asyncio
import json
from typing import Dict, Any
from .event_emitter import DynamicLoaderEventEmitter

class VisualizationService:
    """
    Service to stream Dynamic Loader state to Real3Dviewer.
    """
    def __init__(self, event_emitter: DynamicLoaderEventEmitter):
        self.event_emitter = event_emitter
        self.clients = [] # Mock WebSocket clients

    async def broadcast_state(self, active_models: Dict[str, Any]):
        """
        Broadcast current state to all connected 3D viewers.
        """
        state_payload = {
            "type": "loader_state_update",
            "models": [
                {
                    "name": name,
                    "status": data["status"],
                    "hash": data["info"]["hash"],
                    "position": self._calculate_3d_position(i) # Mock 3D positioning
                }
                for i, (name, data) in enumerate(active_models.items())
            ]
        }
        
        # Simulate broadcast
        # print(f"Visualizer: Broadcasting state to {len(self.clients)} clients: {json.dumps(state_payload)}")
        
        # Emit as a special event for verification
        await self.event_emitter.emit_event(
            event_type="visualization_update",
            model_hash="N/A",
            context={"payload": state_payload}
        )

    def _calculate_3d_position(self, index: int) -> Dict[str, float]:
        """
        Mock logic to place models in a 3D rack.
        """
        return {"x": 0, "y": index * 1.5, "z": 0}

    async def connect_client(self, client_id: str):
        self.clients.append(client_id)
        print(f"Visualizer: Client {client_id} connected.")

    async def disconnect_client(self, client_id: str):
        if client_id in self.clients:
            self.clients.remove(client_id)
