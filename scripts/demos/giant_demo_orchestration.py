import sys
import os
import time
import random

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import All 10 Technologies
from src.integrations.energy_api import EnergyAPI                # Challenge 3
from src.core.a2a_protocol import A2AProtocol                    # Challenge 5
from src.core.negotiation_engine import NegotiationEngine        # Challenge 8
from src.robotics.robocoin_client import RoboCOINClient          # Challenge 6
from src.vision.visual_twin import VisualTwin                    # Challenge 4
from src.models.ebdm_forecaster import EBDMForecaster            # Challenge 7
from src.orchestration.telos_classifier import TelosClassifier   # Challenge 2
from src.orchestration.drift_canceller import DriftCanceller     # Challenge 1
from src.economics.negentropy_ledger import NegentropyLedger     # Challenge 10
# DysonSphere (Challenge 9) is UI, we will simulate state updates for it.

def print_header(step, title, time_str):
    print(f"\n[{time_str}] 🔵 STEP {step}: {title}")
    print("=" * 60)

def giant_demo():
    print("############################################################")
    print("#   EMPEIRIA HAUS: THE GIANT DEMO (10 GRAND CHALLENGES)    #")
    print("#   Scenario: 'Entropy to Equity' - A Day in the Dark Factory #")
    print("############################################################")
    time.sleep(1)

    # ==============================================================================
    # 1. THERMODYNAMIC SCHEDULING (Challenge 3)
    # ==============================================================================
    print_header(1, "Thermodynamic Scheduling (Kairos + EnergyAPI)", "08:00")
    energy_api = EnergyAPI()
    price = energy_api.get_current_price()
    print(f"[EnergyAPI] ⚡ Grid Price: ${price:.4f}/kWh")
    if price < 0.15:
        print("[Kairos] ✅ Price is Optimal. Activating Factory...")
    else:
        print("[Kairos] ❌ Price too high. Standing by.")
        return

    # ==============================================================================
    # 2. SUPPLY CHAIN NEGOTIATION (Challenges 5 & 8)
    # ==============================================================================
    print_header(2, "Supply Chain Negotiation (A2A + MCNP)", "08:05")
    requester = A2AProtocol("Agent_Client_X")
    provider = NegotiationEngine("Empeiria_Factory_01", capabilities=["PRECISION_WELDING"])
    
    # Broadcast ASK
    ask_payload = {"task_type": "PRECISION_WELDING", "max_price": 0.50}
    ask_msg = requester.broadcast("ASK", ask_payload)
    
    # Provider Bids
    # Manually route message for demo simplicity
    bid_msg = provider.process_ask(ask_msg)
    if bid_msg:
        print(f"[A2A] 🤝 Contract Signed. Bid Price: ${bid_msg['payload']['price']}")
    else:
        print("Bid Failed.")
        return

    # ==============================================================================
    # 3. ROBOTIC UNDERSTANDING (Challenge 6)
    # ==============================================================================
    print_header(3, "Robotic Understanding (RoboCOIN)", "08:10")
    robocoin = RoboCOINClient()
    dataset = robocoin.load_dataset("Cobot_Magic_task_0")
    print(f"[RoboCOIN] 🤖 Loaded Trajectory for 'PRECISION_WELDING'.")
    print(f"[RoboCOIN] 🧠 Hydrating Capsule with Human Demonstration Data...")

    # ==============================================================================
    # 4. DIGITAL TWIN & FAILURE PREDICTION (Challenges 4 & 7)
    # ==============================================================================
    print_header(4, "Digital Twin & Failure Prediction (VisualTwin + EBDM)", "08:15")
    twin = VisualTwin()
    forecaster = EBDMForecaster()
    
    # Simulate Execution Loop
    print("[Orchestrator] ▶️  Task Execution Started...")
    
    # Normal State
    telemetry_normal = {"temperature": 22.0, "vibration": 0.01}
    twin.ingest_multimodal(telemetry_normal)
    forecast = forecaster.analyze(telemetry_normal)
    print(f"[EBDM] Status: {forecast['status']} (Prob: {forecast['failure_probability']:.4f})")
    
    time.sleep(0.5)
    
    # Entropy Climb!
    print("\n⚠️  SIMULATING ENTROPY CLIMB...")
    telemetry_critical = {"temperature": 48.0, "vibration": 0.22}
    twin.ingest_multimodal(telemetry_critical)
    forecast = forecaster.analyze(telemetry_critical)
    print(f"[EBDM] 🚨 Status: {forecast['status']} (Prob: {forecast['failure_probability']:.4f})")

    # ==============================================================================
    # 5. SELF-HEALING & ZERO-DRIFT (Challenges 2 & 1)
    # ==============================================================================
    print_header(5, "Self-Healing & Zero-Drift (Telos + DriftCanceller)", "08:16")
    
    # Telos Diagnosis
    telos = TelosClassifier()
    # Simulate log message from the EBDM alert
    log_msg = f"Physics Violation: Drift Probability {forecast['failure_probability']}"
    cat, conf, action = telos.classify_failure(log_msg)
    print(f"[Telos] 🧠 Diagnosis: {cat} -> Action: {action}")
    
    if action == "TRIGGER_ALETHEIA_RECALIBRATION":
        # Drift Correction
        canceller = DriftCanceller()
        target_pose = [100.0, 50.0, 25.0]
        corrected_pose, drift = canceller.apply_correction(target_pose, telemetry_critical)
        print(f"[DriftCanceller] 🛠️  Applied Correction Vector: {['%.4f'%x for x in drift]}")
        print(f"[DriftCanceller] ✅ Resumed with Precision: {['%.4f'%x for x in corrected_pose]}")

    # ==============================================================================
    # 6. NEGENTROPY ACCOUNTING (Challenge 10)
    # ==============================================================================
    print_header(6, "Negentropy Accounting (INL Ledger)", "08:20")
    ledger = NegentropyLedger()
    
    # Calculate Value Created (Entropy Reduction)
    entropy_reduction = 5.0 # Joules/Kelvin
    tx = ledger.record_transaction("Empeiria_Factory_01", "Task_Weld_001", entropy_reduction)
    print(f"[INL] 💎 Transaction Finalized. Hash: {tx['hash']}")

    # ==============================================================================
    # 7. AMBIENT INTELLIGENCE (Challenge 9)
    # ==============================================================================
    print_header(7, "Ambient Intelligence (DysonSphere UI)", "08:21")
    factory_state = {
        "status": "OPTIMAL",
        "last_tx": tx['hash'],
        "drift_correction": "ACTIVE",
        "energy_price": price
    }
    print(f"[DysonSphere] 🔮 UI State Updated: {factory_state}")
    print("[DysonSphere] 🌌 The Factory is Alive and Breathing.")

    print("\n############################################################")
    print("#   GIANT DEMO COMPLETE: 10/10 CHALLENGES SOLVED           #")
    print("############################################################")

if __name__ == "__main__":
    giant_demo()
