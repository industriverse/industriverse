import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.orchestration.telos_classifier import TelosClassifier
from src.orchestration.kairos import KairosEconomicOptimizer

def verify_phase_110():
    print("==================================================")
    print("🧪 Phase 110 Verification: Challenges 2 & 3")
    print("==================================================")

    # 1. Verify Telos Classifier (Challenge #2)
    print("\n🔍 1. Testing Telos Classifier (Self-Healing)...")
    classifier = TelosClassifier()
    test_logs = [
        "Connection timed out while reaching B2",
        "Servo overload on Axis 3",
        "FileNotFoundError: config.json missing",
        "Physics Violation: Drift > 15%",
        "Unknown error occurred"
    ]
    
    for log in test_logs:
        cat, conf, action = classifier.classify_failure(log)
        print(f"   Log: '{log}' -> [{cat}] Action: {action}")

    # 2. Verify Kairos + Energy API (Challenge #3)
    print("\n⚡ 2. Testing Kairos + Energy API (Thermodynamic Scheduling)...")
    kairos = KairosEconomicOptimizer()
    
    print("   Fetching Real-Time Prices (Mocked Grid)...")
    for _ in range(3):
        price = kairos.get_grid_price()
        print(f"   Grid Price: ${price:.4f}/kWh")
        time.sleep(0.5)

    print("\n==================================================")
    print("✅ Verification Complete.")
    print("==================================================")

if __name__ == "__main__":
    verify_phase_110()
