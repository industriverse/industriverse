import time
import json
from pathlib import Path
from typing import Dict, Any
from src.scf.ingestion.atlas_builder import AtlasBuilder
from src.scf.integrations.twin_bridge import TwinBridge
from src.scf.evaluation.roi_calculator import ROICalculator

class DarkFactoryPilot:
    """
    Pilot Agent for Milestone B.
    Connects to a Twin, optimizes energy using the Atlas, and tracks Financial ROI.
    """
    def __init__(self, atlas_db: str = "energy_atlas.db"):
        self.atlas = AtlasBuilder("mock_vault", db_path=atlas_db)
        self.twin = TwinBridge()
        self.roi_calc = ROICalculator()
        self.decision_log = Path("pilot_pov_log.jsonl")
        
        # Clear previous log for fresh pilot
        if self.decision_log.exists():
            self.decision_log.unlink()
            
        print("🏭 Dark Factory Pilot (Milestone B) Online.")
        print(f"   Target: {self.twin.asset_id}")

    def run_pilot(self, duration_seconds: int = 60):
        """
        Runs the pilot loop for a specified duration.
        """
        print(f"   🚀 Starting {duration_seconds}s Pilot Run...")
        start_time = time.time()
        steps = 0
        
        total_kwh_saved = 0.0
        baseline_power = 0.0
        
        while (time.time() - start_time) < duration_seconds:
            # 1. Observe
            state = self.twin.read_sensors()
            current_entropy = state['entropy_rate']
            current_power = state['power_w']
            
            if steps == 0: baseline_power = current_power
            
            print(f"   [{steps}] T={state['temperature_c']:.1f}C | P={current_power:.0f}W | S={current_entropy:.4f}")
            
            # 2. Recall (Find lower entropy states)
            target_entropy = current_entropy * 0.95
            recommendations = self.atlas.query(max_entropy=target_entropy, limit=1)
            
            # 3. Act
            action = "MAINTAIN"
            if recommendations:
                # Simple Logic: If we found a better state, try to mimic it (reduce fan speed if temp is safe)
                # In a real TNN, this would be a policy network.
                # Here we simulate the optimization:
                if state['temperature_c'] < 70.0 and state['fan_speed'] > 0.3:
                    new_speed = state['fan_speed'] * 0.9 # Reduce speed by 10%
                    self.twin.write_setpoint("fan_speed", new_speed)
                    action = "OPTIMIZE"
            
            # 4. Audit & ROI
            # Calculate savings vs initial baseline
            savings = self.roi_calc.calculate_savings(baseline_power, current_power, 1.0) # 1 sec step
            total_kwh_saved += savings['kwh_saved']
            
            log_entry = {
                "timestamp": time.time(),
                "state": state,
                "action": action,
                "savings_step": savings
            }
            self._log_decision(log_entry)
            
            time.sleep(1.0)
            steps += 1
            
        # Final Financial Audit
        financials = self.roi_calc.calculate_financials(total_kwh_saved, time_period_days=duration_seconds/(3600*24))
        print("\n✅ Pilot Complete.")
        print(f"   💰 Cost Saved: ${financials['cost_saved_usd']:.6f}")
        print(f"   🔋 kWh Saved: {financials['kwh_saved']:.6f}")
        print(f"   📜 Audit Proof: {financials['audit_proof']}")
        
        # Append financials to log
        with open(self.decision_log, 'a') as f:
            f.write(json.dumps({"type": "FINANCIAL_AUDIT", "data": financials}) + "\n")

    def _log_decision(self, entry: Dict[str, Any]):
        with open(self.decision_log, 'a') as f:
            f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    pilot = DarkFactoryPilot()
    pilot.run_pilot(duration_seconds=30) # Short run for demo
