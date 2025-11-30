import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.models.ebdm_forecaster import EBDMForecaster
from src.economics.negentropy_ledger import NegentropyLedger

def verify_phase_113():
    print("==================================================")
    print("🧪 Phase 113 Verification: Challenges 7 & 10")
    print("==================================================")

    # 1. Verify EBDM Forecaster (Challenge #7)
    print("\n📉 1. Testing EBDM Failure Prediction...")
    forecaster = EBDMForecaster()
    
    # Simulate Degradation: Temp rises, Vibration increases
    scenarios = [
        {"temperature": 20.0, "vibration": 0.01}, # Nominal
        {"temperature": 25.0, "vibration": 0.05}, # Warming up
        {"temperature": 35.0, "vibration": 0.15}, # Warning
        {"temperature": 45.0, "vibration": 0.25}, # Critical
    ]
    
    for i, telemetry in enumerate(scenarios):
        result = forecaster.analyze(telemetry)
        print(f"   Step {i}: Temp={telemetry['temperature']}C -> Energy={result['energy_score']} | Prob={result['failure_probability']} | Status={result['status']}")

    # 2. Verify Negentropy Ledger (Challenge #10)
    print("\n🏦 2. Testing Negentropy Ledger...")
    ledger = NegentropyLedger()
    
    # Transaction 1
    tx1 = ledger.record_transaction("Agent_Welder_01", "Task_Weld_A", 5.0)
    print(f"   TX1: {tx1['hash']}")
    
    # Transaction 2
    tx2 = ledger.record_transaction("Agent_Inspector_02", "Task_Inspect_B", 2.5)
    print(f"   TX2: {tx2['hash']}")
    
    # Verify Chain
    if tx2['prev_hash'] == tx1['hash']:
        print("   ✅ Blockchain Integrity Verified (Hash Chaining works).")
    else:
        print("   ❌ Blockchain Integrity FAILED.")

    print("\n==================================================")
    print("✅ Verification Complete.")
    print("==================================================")

if __name__ == "__main__":
    verify_phase_113()
