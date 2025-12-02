from typing import List, Dict
from src.metaverse.industrial_metaverse import TwinObject

class RealityStreamVisualizer:
    """
    The Lens of the Metaverse.
    Translates Digital Twin state into visual rendering commands (AR/VR/Web).
    """
    
    def render_frame(self, objects: List[TwinObject]):
        """
        Simulates rendering a frame of the Industrial Metaverse.
        """
        print(f"\n   🎥 [RENDER] Frame Generated ({len(objects)} Objects)")
        
        for obj in objects:
            # 1. Determine Visual Style based on Status
            color = "GREEN"
            effect = "NONE"
            
            if obj.status == "WARNING":
                color = "YELLOW"
                effect = "PULSING_GLOW"
            elif obj.status == "ERROR":
                color = "RED"
                effect = "STROBE_ALARM"
                
            # 2. Render Object
            print(f"     -> [OBJ] {obj.name} | Pos: {obj.position} | Color: {color} | Effect: {effect}")
            
            # 3. Render Telemetry Overlay (AR)
            if obj.telemetry:
                print(f"        [AR] Overlay: {obj.telemetry}")

# --- Verification ---
if __name__ == "__main__":
    from src.metaverse.industrial_metaverse import TwinObject
    
    objs = [
        TwinObject("Robot_1", "Robot_1", "ROBOT", (10, 0, 0), "NORMAL", {"speed": "1.2m/s"}),
        TwinObject("Press_A", "Press_A", "MACHINE", (20, 0, 0), "ERROR", {"pressure": "CRITICAL"})
    ]
    
    viz = RealityStreamVisualizer()
    viz.render_frame(objs)
