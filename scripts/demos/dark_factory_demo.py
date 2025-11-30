import time
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.orchestration.dark_factory import DarkFactoryController
from src.orchestration.factory_persona import FactoryPersonaManager
from src.orchestration.hydrator import ServiceHydrator

def run_demo():
    print("==================================================")
    print("🏭  DARK FACTORY ORCHESTRATION DEMO  🏭")
    print("==================================================")
    
    controller = DarkFactoryController()
    persona_mgr = FactoryPersonaManager()
    hydrator = ServiceHydrator()

    # Scenario 1: Morning Shift (Cheap Energy, High Volume)
    print("\n🌅 SCENARIO 1: MORNING SHIFT (06:00)")
    print("-------------------------------------")
    persona_mgr.set_persona("FOXCONN_SPEED")
    controller.emm.balance = 5000 # Reset budget
    
    # Simulate cheap energy
    controller.chronos.kairos.get_grid_price = lambda: 0.05 
    controller.run_cycle() # Should be AGGRESSIVE
    
    # Pre-warm Maintenance Bots (Edge Cache)
    print("\n[Demo] 📡 Pre-warming Maintenance Bots in us-east...")
    hydrator.hydrate("b2://capsules/maint-bot-v1.tar.gz", region="us-east")

    # Scenario 2: Peak Hours (Expensive Energy, Innovation Mode)
    print("\n☀️ SCENARIO 2: PEAK HOURS (14:00)")
    print("----------------------------------")
    persona_mgr.set_persona("TESLA_INNOVATION")
    
    # Simulate expensive energy
    controller.chronos.kairos.get_grid_price = lambda: 0.25
    controller.run_cycle() # Should be BALANCED/CONSERVATIVE depending on logic
    
    # Scenario 3: The Anomaly (Drift Detected)
    print("\n🚨 SCENARIO 3: THERMAL DRIFT DETECTED")
    print("-------------------------------------")
    # Inject Drift into Aletheia
    controller.aletheia.observe_reality = lambda task_id: {"temperature": 600, "vibration": 0.05, "visual_entropy": 0.2}
    
    # Run cycle and expect Aletheia to complain
    # (Note: In a full integration, this would halt execution. Here we see the log.)
    print("[Demo] Simulating high-temp task execution...")
    valid, drift, msg = controller.aletheia.validate({"name": "Fusion_Weld", "id": "task_999"}, {"temperature": 500})
    print(f"[Demo] Aletheia Verdict: {msg}")

    # Scenario 4: The Fix (Zero-Drift Manufacturing)
    print("\n🛠️  SCENARIO 4: ZERO-DRIFT CORRECTION ENGAGED")
    print("---------------------------------------------")
    from src.orchestration.drift_canceller import DriftCanceller
    canceller = DriftCanceller()
    
    telemetry = {"temperature": 600, "vibration": 0.05} # High temp
    target_pose = [100.0, 50.0, 25.0]
    
    print(f"[DriftCanceller] 🌡️  Input Telemetry: {telemetry}")
    print(f"[DriftCanceller] 🎯 Target Pose: {target_pose}")
    
    corrected_pose, est_drift = canceller.apply_correction(target_pose, telemetry)
    
    print(f"[DriftCanceller] 📉 Estimated Drift: {['%.4f' % x for x in est_drift]}")
    print(f"[DriftCanceller] ✅ Corrected Pose: {['%.4f' % x for x in corrected_pose]}")
    print("[DriftCanceller] 🚀 Execution Resumed with Compensation.")

    print("\n==================================================")
    print("✅ DEMO COMPLETE. The Dark Factory is Alive.")
    print("==================================================")

if __name__ == "__main__":
    run_demo()
