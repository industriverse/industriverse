import sys
import os
import json
import time
import argparse

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import Modules
from src.integrations.energy_api import EnergyAPI
from src.core.a2a_protocol import A2AProtocol
from src.core.negotiation_engine import NegotiationEngine
from src.robotics.robocoin_client import RoboCOINClient
from src.vision.visual_twin import VisualTwin
from src.models.ebdm_forecaster import EBDMForecaster
from src.orchestration.telos_classifier import TelosClassifier
from src.orchestration.drift_canceller import DriftCanceller
from src.economics.negentropy_ledger import NegentropyLedger

class DemoFactory:
    """
    The 50-Capsule Demo Suite Factory.
    Dynamically generates and runs scenarios from demo_scenarios.json.
    """
    def __init__(self, scenarios_path="scripts/demos/demo_scenarios.json"):
        with open(scenarios_path, 'r') as f:
            self.scenarios = {d['id']: d for d in json.load(f)}

    def run_demo(self, demo_id):
        if demo_id not in self.scenarios:
            print(f"❌ Demo ID {demo_id} not found.")
            return

        scenario = self.scenarios[demo_id]
        print("\n############################################################")
        print(f"#   DEMO {scenario['id']}: {scenario['name']}")
        print(f"#   Category: {scenario['category']}")
        print(f"#   Modules: {', '.join(scenario['modules'])}")
        print("############################################################")
        print(f"📝 Description: {scenario['description']}\n")
        time.sleep(1)

        # Dynamic Execution Logic
        if "DriftCanceller" in scenario['modules']:
            self._run_drift_scenario(scenario)
        elif "EnergyAPI" in scenario['modules']:
            self._run_energy_scenario(scenario)
        elif "NegotiationEngine" in scenario['modules']:
            self._run_negotiation_scenario(scenario)
        elif "RoboCOIN" in scenario['modules']:
            self._run_robotics_scenario(scenario)
        elif "ALL" in scenario['modules']:
            self._run_full_autonomy(scenario)
        else:
            print("⚠️  Generic Simulation Mode (No specific logic mapped yet)")
            self._run_generic_simulation(scenario)

    def _run_drift_scenario(self, scenario):
        print("🔵 Initializing Physics Engine...")
        twin = VisualTwin()
        canceller = DriftCanceller()
        
        for step in scenario['telemetry_sequence']:
            print(f"\n[Sim] Telemetry: {step}")
            twin.ingest_multimodal(step)
            
            # Check for Drift
            if step['temperature'] > 35.0:
                print("⚠️  High Temperature Detected! Checking Drift...")
                target = [100.0, 50.0, 25.0]
                corrected, drift = canceller.apply_correction(target, step)
                print(f"[DriftCanceller] 🛠️  Correction Applied: {['%.4f'%x for x in drift]}")
            else:
                print("[Aletheia] Status: Nominal")
            time.sleep(0.5)

    def _run_energy_scenario(self, scenario):
        print("🔵 Initializing Thermodynamic Scheduler...")
        # Mocking EnergyAPI behavior based on sequence
        for step in scenario['telemetry_sequence']:
            price = step.get('grid_price', 0.0)
            print(f"\n[EnergyAPI] ⚡ Grid Price: ${price:.2f}/kWh (Load: {step.get('load')})")
            if price < 0.15:
                print("[Kairos] ✅ Price Optimal. Scheduling Tasks...")
            else:
                print("[Kairos] ⏸️  Price High. Pausing Execution.")
            time.sleep(0.5)

    def _run_negotiation_scenario(self, scenario):
        print("🔵 Initializing Negotiation Mesh...")
        engine = NegotiationEngine("Factory_01", ["WELDING"])
        for step in scenario['telemetry_sequence']:
            ask = step.get('ask_price')
            bid = step.get('bid_price')
            print(f"\n[Market] ASK: ${ask:.2f} | BID: ${bid:.2f}")
            if bid <= ask:
                print("[MCNP] 🤝 Contract Signed.")
            else:
                print("[MCNP] ❌ Bid Rejected (Too High).")
            time.sleep(0.5)

    def _run_robotics_scenario(self, scenario):
        print("🔵 Initializing RoboCOIN & VisualTwin...")
        client = RoboCOINClient()
        for step in scenario['telemetry_sequence']:
            print(f"\n[RoboCOIN] 📥 Ingesting: {step.get('video_chunk')}")
            print(f"[LeRobot] 🧠 Learned Action: {step.get('action')}")
            time.sleep(0.5)

    def _run_full_autonomy(self, scenario):
        print("🔵 Initializing DARK FACTORY MODE...")
        # Simplified simulation of the Giant Demo loop
        for step in scenario['telemetry_sequence']:
            print(f"\n[Orchestrator] Status: {step['status']} | Entropy: {step['entropy']}")
            if step['status'] == "DRIFT_DETECTED":
                print("[Telos] 🛠️  Self-Healing Triggered...")
            elif step['status'] == "CORRECTED":
                print("[Ledger] 💎 Minting Negentropy Credits...")
            time.sleep(0.5)

    def _run_generic_simulation(self, scenario):
        for step in scenario['telemetry_sequence']:
            print(f"[Sim] Processing Step: {step}")
            time.sleep(0.5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Empeiria Haus Demo Factory")
    parser.add_argument("--id", type=int, help="Demo ID to run (1-50)", required=True)
    args = parser.parse_args()

    factory = DemoFactory()
    factory.run_demo(args.id)
