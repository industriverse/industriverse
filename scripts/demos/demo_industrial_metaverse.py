import sys
import os
import time
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.metaverse.industrial_metaverse import IndustrialMetaverse
from src.metaverse.reality_stream_visualizer import RealityStreamVisualizer

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_industrial_metaverse():
    print_header("DEMO: THE INDUSTRIAL METAVERSE")
    print("Scenario: Real-Time Anomaly Visualization (God's Eye View)")
    
    # 1. Initialize World
    meta = IndustrialMetaverse()
    viz = RealityStreamVisualizer()
    
    # Assets
    robot_id = meta.register_asset("Kuka_Arm_01", "ROBOT", (10, 5, 0))
    cnc_id = meta.register_asset("Haas_CNC_04", "MACHINE", (20, 5, 0))
    agv_id = meta.register_asset("AGV_Transporter", "VEHICLE", (15, 10, 0))
    
    # 2. Simulation Loop
    print_header("LIVE REALITY STREAM")
    
    # Frame 1: Normal
    print("\n>> FRAME 1: Normal Operations")
    meta.update_telemetry(robot_id, {"status": "Active", "temp": 45})
    meta.update_telemetry(cnc_id, {"rpm": 12000, "vibration": 12})
    viz.render_frame(meta.get_world_state())
    time.sleep(1)
    
    # Frame 2: Warning
    print("\n>> FRAME 2: Vibration Increasing")
    meta.update_telemetry(cnc_id, {"rpm": 12500, "vibration": 45, "temp": 80})
    viz.render_frame(meta.get_world_state())
    time.sleep(1)
    
    # Frame 3: Critical Failure
    print("\n>> FRAME 3: CRITICAL FAILURE DETECTED")
    meta.update_telemetry(cnc_id, {"rpm": 0, "vibration": 150, "ERROR": "SPINDLE_FRACTURE"})
    viz.render_frame(meta.get_world_state())
    time.sleep(1)
    
    print_header("DEMO COMPLETE: VISUALIZATION SYNCHRONIZED")

if __name__ == "__main__":
    demo_industrial_metaverse()
