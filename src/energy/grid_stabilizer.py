from src.energy.neural_battery import NeuralBattery

class GridStabilizer:
    """
    The Frequency Response Unit.
    Stabilizes the grid by modulating the Neural Battery.
    """
    
    def __init__(self, battery: NeuralBattery):
        self.battery = battery
        self.nominal_freq = 60.0 # Hz
        
    def on_frequency_change(self, current_freq: float):
        """
        Reacts to grid frequency deviations.
        """
        delta = current_freq - self.nominal_freq
        print(f"   ⚡ [GRID] Frequency: {current_freq:.3f} Hz (Delta: {delta:+.3f})")
        
        if delta < -0.05:
            # Under-frequency: Generation < Load. We must SHED LOAD.
            print("     -> 🚨 UNDER-FREQUENCY EVENT! Shedding Load...")
            self.battery.ramp_down(self.battery.min_mw)
            
        elif delta > 0.05:
            # Over-frequency: Generation > Load. We must ABSORB ENERGY.
            print("     -> 🌊 OVER-FREQUENCY EVENT! Absorbing Energy...")
            self.battery.ramp_up(self.battery.max_mw)
            
        else:
            # Normal Band
            print("     -> ✅ Grid Stable. Maintaining Baseline.")
            # Slowly return to 50% if needed, or just hold
            
# --- Verification ---
if __name__ == "__main__":
    nb = NeuralBattery("Test_Unit", 100.0, 10.0)
    stab = GridStabilizer(nb)
    
    stab.on_frequency_change(59.8) # Crisis
    stab.on_frequency_change(60.2) # Surplus
