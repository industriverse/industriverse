from dataclasses import dataclass
import time

@dataclass
class BatteryState:
    current_load_mw: float
    max_load_mw: float
    min_load_mw: float
    mode: str # CHARGING (Low Load), DISCHARGING (High Load), IDLE

class NeuralBattery:
    """
    A Virtual Power Plant built from Flexible Compute.
    """
    
    def __init__(self, name: str, max_mw: float, min_mw: float):
        self.name = name
        self.max_mw = max_mw
        self.min_mw = min_mw
        self.current_mw = (max_mw + min_mw) / 2 # Start at 50%
        self.mode = "IDLE"
        
    def ramp_up(self, target_mw: float):
        """
        'Discharging' the battery: Consuming excess grid energy for useful work.
        """
        target = min(target_mw, self.max_mw)
        print(f"   🔋 [BATTERY] Ramping UP to {target:.1f} MW (Absorbing Energy)...")
        self.current_mw = target
        self.mode = "DISCHARGING"
        
    def ramp_down(self, target_mw: float):
        """
        'Charging' the battery: Reducing load to support the grid.
        """
        target = max(target_mw, self.min_mw)
        print(f"   🔋 [BATTERY] Ramping DOWN to {target:.1f} MW (Shedding Load)...")
        self.current_mw = target
        self.mode = "CHARGING"
        
    def get_status(self):
        pct = (self.current_mw - self.min_mw) / (self.max_mw - self.min_mw) * 100
        print(f"   📊 [{self.name}] Load: {self.current_mw:.1f} MW ({pct:.1f}%) | Mode: {self.mode}")

# --- Verification ---
if __name__ == "__main__":
    nb = NeuralBattery("DataCenter_Alpha", 100.0, 10.0)
    nb.ramp_up(90.0)
    nb.ramp_down(20.0)
