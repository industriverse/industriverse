import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.social.micro_gesture import MicroGestureAnalyzer
from src.social.attention_acceleration import AttentionAccelerationDetector
from src.social.resonance_scanner import ResonanceScanner
from src.social.zk_influence_engine import ZKInfluenceEngine

def verify_deep_spi():
    print("🕵️ Starting Deep Social Physics Verification...")
    
    zk_engine = ZKInfluenceEngine()
    
    # 1. Micro-Gesture (Bot Scroll)
    print("\n--- 1. Micro-Gesture Analyzer (MGIA) ---")
    mgia = MicroGestureAnalyzer()
    bot_gestures = mgia.simulate_bot_scroll()
    mg_score = mgia.analyze_session(bot_gestures)
    if mg_score > 0.8:
        print("✅ Robotic Scrolling Detected.")
        zk_engine.add_evidence("MGIA", mg_score, {"type": "scroll_variance"})
        
    # 2. Attention Acceleration (View Spike)
    print("\n--- 2. Attention Acceleration (AAD) ---")
    aad = AttentionAccelerationDetector()
    # Simulate: 100 views -> 1000 views -> 100,000 views (Impossible Jump)
    views = [
        (0.0, 100),
        (1.0, 1000),
        (2.0, 100000)
    ]
    aad_score = aad.analyze_growth_curve(views)
    if aad_score > 0.8:
        print("✅ Impossible Acceleration Detected.")
        zk_engine.add_evidence("AAD", aad_score, {"max_acc": "99000.0"})
        
    # 3. Resonance Scanner (Fake Virality)
    print("\n--- 3. Resonance Scanner (RSPS) ---")
    rsps = ResonanceScanner()
    # Simulate periodic bursts (Resonance)
    fake_shares = []
    for i in range(50):
        fake_shares.append(float(i * 10)) # Every 10 seconds exactly
    
    res_score = rsps.scan_amplification_pattern(fake_shares)
    if res_score > 0.8:
        print("✅ Artificial Resonance Detected.")
        zk_engine.add_evidence("RSPS", res_score, {"ratio": "high"})
        
    # 4. ZK Evidence Bundle
    print("\n--- 4. ZK Influence Engine (ZK-IFE) ---")
    bundle = zk_engine.compose_bundle()
    if bundle:
        print(f"✅ Evidence Bundle Created: {bundle.fingerprint_id}")
        print("📜 Report Preview:")
        print(bundle.public_report)

    print("\n✅ DEEP SPI VERIFICATION COMPLETE.")

if __name__ == "__main__":
    verify_deep_spi()
