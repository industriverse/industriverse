from typing import Dict, List, Any
from dataclasses import dataclass, field
import uuid
import time

# Mocking integration with existing components
# from src.white_label.i3.shadow_twin_backend import ShadowTwinBackend
# from src.vision.visual_twin import VisualTwin

@dataclass
class TwinObject:
    id: str
    name: str
    type: str # FACTORY, ROBOT, PRODUCT
    position: tuple # (x, y, z)
    status: str # NORMAL, WARNING, ERROR
    telemetry: Dict[str, Any] = field(default_factory=dict)

class IndustrialMetaverse:
    """
    The Mirror World.
    Integrates Shadow Twins and Visual Twins into a unified spatial reality.
    """
    
    def __init__(self):
        self.objects: Dict[str, TwinObject] = {}
        print("   🌐 [METAVERSE] Initializing Industrial Mirror World...")
        
    def register_asset(self, name: str, asset_type: str, position: tuple) -> str:
        obj = TwinObject(
            id=str(uuid.uuid4()),
            name=name,
            type=asset_type,
            position=position,
            status="NORMAL"
        )
        self.objects[obj.id] = obj
        print(f"     -> Registered Twin: {name} ({asset_type}) at {position}")
        return obj.id
        
    def update_telemetry(self, object_id: str, data: Dict[str, Any]):
        """
        Updates the digital state based on physical sensors (USM).
        """
        if object_id in self.objects:
            obj = self.objects[object_id]
            obj.telemetry.update(data)
            
            # Simple Status Logic
            if data.get("temperature", 0) > 100:
                obj.status = "WARNING"
            elif data.get("vibration", 0) > 50:
                obj.status = "ERROR"
            else:
                obj.status = "NORMAL"
                
    def get_world_state(self) -> List[TwinObject]:
        return list(self.objects.values())

# --- Verification ---
if __name__ == "__main__":
    meta = IndustrialMetaverse()
    fid = meta.register_asset("Gigafactory_Texas", "FACTORY", (0, 0, 0))
    meta.update_telemetry(fid, {"temperature": 105})
    print(meta.get_world_state())
