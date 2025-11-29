import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.visual_twin import VisualTwin
from src.vision.vision_delta_detector import VisionDeltaDetector

def test_vision_system():
    print("\n--- Testing Visual Twin & Delta Detector ---")
    
    twin = VisualTwin() # Mock Mode
    detector = VisionDeltaDetector(tolerance=5.0)
    
    # 1. Perceive (Mock)
    visual_state = twin.perceive("frame_001.jpg")
    print(f"Visual State: {visual_state['state_vector']}")
    
    # 2. Test Match (Good)
    sim_state_good = {
        "x": 100.0, 
        "y": 50.0, 
        "z": 0.0, 
        "temp": 212.0 # Within 10C tolerance of 210
    }
    result_good = detector.detect_delta(visual_state['state_vector'], sim_state_good)
    if not result_good['delta_detected']:
        print("✅ Match confirmed (No Delta).")
    else:
        print(f"❌ Match failed: {result_good['discrepancies']}")

    # 3. Test Mismatch (Bad Position)
    sim_state_bad_pos = {
        "x": 120.0, # > 5mm diff
        "y": 50.0, 
        "temp": 210.0
    }
    result_bad_pos = detector.detect_delta(visual_state['state_vector'], sim_state_bad_pos)
    if result_bad_pos['delta_detected'] and "Position X Mismatch" in result_bad_pos['discrepancies'][0]:
        print("✅ Position Mismatch detected.")
    else:
        print(f"❌ Position Mismatch NOT detected: {result_bad_pos}")

    # 4. Test Mismatch (Bad Temp)
    sim_state_bad_temp = {
        "x": 100.0, 
        "y": 50.0, 
        "temp": 250.0 # > 10C diff
    }
    result_bad_temp = detector.detect_delta(visual_state['state_vector'], sim_state_bad_temp)
    if result_bad_temp['delta_detected'] and "Thermal Mismatch" in result_bad_temp['discrepancies'][0]:
        print("✅ Thermal Mismatch detected.")
    else:
        print(f"❌ Thermal Mismatch NOT detected: {result_bad_temp}")

if __name__ == "__main__":
    test_vision_system()
