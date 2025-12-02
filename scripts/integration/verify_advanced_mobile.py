import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.mobile.advanced.bio_thermal import BioThermalMonitor, BioMetrics
from src.mobile.advanced.reality_anchor import RealityAnchor
from src.mobile.advanced.ghost_protocol import GhostProtocol
from src.mobile.advanced.neural_battery import NeuralBattery
from src.mobile.advanced.haptic_feedback import HapticImmuneResponse

def verify_advanced_features():
    print("🚀 Starting Advanced Mobile Features Verification...")
    
    # 1. Bio-Thermal Fever
    print("\n--- 1. Bio-Thermal Fever ---")
    monitor = BioThermalMonitor()
    # Simulate: Hot phone (38C) but User is Still (0.05) -> FEVER
    metrics = BioMetrics(time.time(), 38.0, 0.05, 5.0)
    score = monitor.check_for_fever(metrics)
    if score > 0.5:
        print(f"✅ Fever Detected (Score: {score})")
    else:
        print("❌ Fever Detection Failed")

    # 2. Reality Anchor
    print("\n--- 2. Reality Anchor ---")
    anchor = RealityAnchor("KEY_DEVICE_001")
    proof = anchor.sign_reality_proof("37.7749,-122.4194")
    if proof["signature"]:
        print(f"✅ Proof Signed: {proof['signature'][:10]}...")

    # 3. Ghost Protocol
    print("\n--- 3. Ghost Protocol ---")
    ghost = GhostProtocol()
    ghost.activate()
    gps = ghost.generate_fake_gps()
    contact = ghost.generate_fake_contact()
    if gps and contact:
        print("✅ Chaff Generated Successfully")

    # 4. Neural Battery
    print("\n--- 4. Neural Battery ---")
    neural = NeuralBattery()
    # Simulate Charging + WiFi + Full Battery
    if neural.check_conditions(True, 0.95, True):
        neural.run_training_slice()
        print("✅ Training Cycle Complete")

    # 5. Haptic Feedback
    print("\n--- 5. Haptic Feedback ---")
    haptic = HapticImmuneResponse()
    haptic.trigger_heartbeat_warning()
    print("✅ Haptic Pattern Triggered")

if __name__ == "__main__":
    verify_advanced_features()
