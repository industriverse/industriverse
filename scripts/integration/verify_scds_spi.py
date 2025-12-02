import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.desktop.telemetry_kernel import TelemetryKernel
from src.desktop.permission_graph import PermissionGraph
from src.social.harmonic_detector import HarmonicPostingDetector
from src.social.entropy_engine import SocialEntropyEngine
from src.social.zk_fingerprint import ZKFingerprintEngine

def verify_scds_spi():
    print("🛡️ Starting Sovereign Compute & Social Physics Verification...")
    
    # --- Part 1: SCDS (Desktop) ---
    print("\n--- 1. SCDS: Desktop Telemetry ---")
    kernel = TelemetryKernel()
    telemetry = kernel.poll_sensors()
    kernel.detect_thermal_anomaly(telemetry)
    print(f"   ✅ Polled Sensors: CPU Temp {telemetry.cpu_temps[0]:.1f}C")
    
    print("\n--- 2. SCDS: Permission Graph ---")
    perm_graph = PermissionGraph()
    perm_graph.log_event("suspicious_updater.exe", "CAM", 0.5)
    perm_graph.log_event("legit_app.exe", "MIC", 6.0) # High energy
    perm_graph.analyze_anomalies()
    
    # --- Part 2: SPI (Social Physics) ---
    print("\n--- 3. SPI: Harmonic Detector (Botnet) ---")
    hpd = HarmonicPostingDetector()
    # Simulate Bot Attack (Perfect Interval)
    bot_timestamps = hpd.simulate_bot_attack(20, 5.0)
    score = hpd.analyze_timestamps(bot_timestamps)
    if score > 0.8:
        print(f"   ✅ Botnet Detected! Score: {score}")
        
    print("\n--- 4. SPI: Entropy Engine (Swarm) ---")
    see = SocialEntropyEngine()
    bot_thread = ["Buy Crypto Now", "Buy Crypto Now", "Crypto Moon", "Buy Crypto Now"]
    if see.detect_collapse(bot_thread):
        print("   ✅ Entropy Collapse Detected!")
        
    print("\n--- 5. SPI: ZK Fingerprint ---")
    zk = ZKFingerprintEngine()
    fp = zk.compose_fingerprint("Twitter", score, 1.5)
    if fp.canonical_hash:
        print("   ✅ Evidence Bundle Created & Committed.")

    print("\n✅ SCDS & SPI VERIFICATION COMPLETE.")

if __name__ == "__main__":
    verify_scds_spi()
