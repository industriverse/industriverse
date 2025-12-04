import sys
import os
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path.cwd()))

from src.economics.manifests.haas_capture_capsule import HaaSCaptureCapsule

class NightlyCanary:
    """
    Simple framework for nightly regression tests.
    """
    def __init__(self):
        self.missions = []

    def add_mission(self, name, func):
        self.missions.append((name, func))

    def run_all(self):
        print("🐤 Nightly Canary: Starting Patrol...")
        results = {}
        for name, func in self.missions:
            print(f"\n🔎 Running Mission: {name}")
            try:
                success = func()
                results[name] = "PASS" if success else "FAIL"
                print(f"   -> {results[name]}")
            except Exception as e:
                results[name] = f"ERROR: {e}"
                print(f"   -> ERROR: {e}")
        
        print("\n=== Canary Report ===")
        for name, status in results.items():
            print(f"{name}: {status}")
        return results

def mission_heat_capture_perf():
    """
    Validates that the HaaS DAC physics model is within expected bounds.
    """
    print("   [Mission] Initializing HaaS DAC...")
    dac = HaaSCaptureCapsule("TEST-FACILITY")
    
    # Run a cycle
    dac.read_telemetry()
    thermal_kw = dac.calculate_thermal_power()
    
    # Bounds check (Mock 1MW facility)
    # Flow ~850 LPM, dT ~15C -> ~880 kW
    expected_min = 500.0
    expected_max = 1500.0
    
    print(f"   [Mission] Measured Thermal Power: {thermal_kw:.2f} kW")
    
    if expected_min <= thermal_kw <= expected_max:
        print("   [Mission] ✅ Physics within bounds.")
        return True
    else:
        print(f"   [Mission] ❌ Physics OUT OF BOUNDS ({expected_min}-{expected_max})")
        return False

if __name__ == "__main__":
    canary = NightlyCanary()
    canary.add_mission("HEAT_CAPTURE_PERF", mission_heat_capture_perf)
    canary.run_all()
