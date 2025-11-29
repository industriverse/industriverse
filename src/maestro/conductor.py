import sys
import os
import json
import time

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.intent.glyph_intent_fuser import GlyphIntentFuser
from src.capsules.capsule_manager import CapsuleManager
from src.shield.threat_identifier import ThreatIdentifier
from src.simulation.simulation_oracle import SimulationOracle
from src.economy.pricing_engine import ExergyPricingEngine
from src.twin.shadow_runtime import ShadowRuntime

class MaestroConductor:
    """
    AI Shield v3 - Gate 11: Maestro Conductor.
    The 'Brain' of the Manufacturing AGI Loop.
    Orchestrates Intent -> Glyphs -> Safety -> Simulation -> Price -> Execution.
    """
    def __init__(self):
        print("Initializing Maestro AGI Conductor...")
        self.fuser = GlyphIntentFuser()
        self.capsule_manager = CapsuleManager()
        self.shield = ThreatIdentifier()
        self.oracle = SimulationOracle()
        self.pricing = ExergyPricingEngine()
        self.runtime = ShadowRuntime()

    def process_request(self, natural_language_prompt):
        """
        Full AGI Loop Pipeline.
        """
        print(f"\n[1] Intent: Processing '{natural_language_prompt}'...")
        
        # 1. Fuse Intent
        intent_plan = self.fuser.fuse(natural_language_prompt)
        print(f"    -> Intent Vector: {intent_plan['intent_vector'][:3]}...")
        print(f"    -> Modifiers: {intent_plan['modifiers']}")
        
        # 2. Dispatch (Capsule Selection)
        print("\n[2] Dispatch: Requesting Bids...")
        bids = self.capsule_manager.request_bids(intent_plan['intent_vector'])
        if not bids:
            return {"status": "FAILED", "reason": "No capable capsules found."}
        
        best_bid = bids[0]
        print(f"    -> Selected: {best_bid['name']} (Score: {best_bid['score']})")
        
        # 3. Plan Generation (Mock Bytecode for now)
        # In real system, Capsule would generate bytecode from Glyphs
        print("\n[3] Planning: Generating Bytecode...")
        bytecode = [
            {"op": "OP_SPINDLE", "params": {"rpm": 10000}},
            {"op": "OP_MOVE", "params": {"x": 100, "y": 50, "f": 3000}}
        ]
        
        # 4. Safety Scan
        print("\n[4] Safety: Scanning Plan...")
        scan_result = self.shield.scan_plan(intent_plan['modifiers'], bytecode)
        if not scan_result['safe']:
            print(f"    -> RISKS DETECTED: {scan_result['risks']}")
            # If sanitizable, proceed with mitigated bytecode
            if scan_result['mitigated_bytecode']:
                print("    -> Applied Mitigations.")
                bytecode = scan_result['mitigated_bytecode']
            else:
                return {"status": "REJECTED", "reason": "Unsafe Plan"}
        else:
            print("    -> Plan Certified Safe.")
            
        # 5. Simulation & Pricing
        print("\n[5] Oracle: Simulating Physics...")
        sim_result = self.oracle.simulate(bytecode)
        price_result = self.pricing.calculate_price(sim_result)
        print(f"    -> Energy: {sim_result['energy_j']}J, Time: {sim_result['time_s']}s")
        print(f"    -> Quote: ${price_result['total_price']} (Risk: {price_result['breakdown']['risk_multiplier']}x)")
        
        # 6. Execution (Shadow Runtime)
        print("\n[6] Execution: Starting Shadow Twin...")
        # In a real app, this would be async or handed off to a job queue
        # self.runtime.run_shadow_loop(bytecode, best_bid['capsule_id'])
        
        return {
            "status": "SUCCESS",
            "capsule": best_bid['name'],
            "price": price_result['total_price'],
            "energy": sim_result['energy_j'],
            "plan": intent_plan
        }

if __name__ == "__main__":
    maestro = MaestroConductor()
    result = maestro.process_request("Make a lightweight precision bracket")
    print("\nFinal Result:")
    print(json.dumps(result, indent=2))
