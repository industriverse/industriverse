import time
import random
from dataclasses import dataclass

# Mock dependencies if not available
try:
    from src.economics.negentropy_ledger import NegentropyLedger
except ImportError:
    class NegentropyLedger:
        def record_transaction(self, agent, task, value):
            print(f"[Ledger] {agent} -> {task}: {value}")

@dataclass
class HeatCaptureState:
    flow_rate_lpm: float
    temp_in_c: float
    temp_out_c: float
    pump_power_kw: float

class HaaSCaptureCapsule:
    """
    The Heat-as-a-Service (HaaS) DAC.
    Manages the physical capture loop, optimizes for Negentropy, and bills the offtaker.
    """
    def __init__(self, facility_id, ppa_price_per_mwh=50.0):
        self.facility_id = facility_id
        self.ppa_price = ppa_price_per_mwh
        self.ledger = NegentropyLedger()
        self.state = HeatCaptureState(0, 0, 0, 0)
        print(f"🔥 HaaS DAC Online: {self.facility_id} (PPA: ${self.ppa_price}/MWh)")

    def read_telemetry(self):
        """
        Simulates reading sensors from the physical loop.
        """
        # In reality, this would query the PLC / Edge Node
        # Simulating a 1MW facility with liquid cooling
        self.state.temp_in_c = random.uniform(45.0, 48.0)  # Hot water from racks
        self.state.temp_out_c = random.uniform(30.0, 32.0) # Cooled return
        self.state.flow_rate_lpm = random.uniform(800, 900)
        self.state.pump_power_kw = 15.0 # Parasitic load

    def calculate_thermal_power(self):
        """
        Q = m_dot * Cp * delta_T
        Water Cp ~ 4.18 kJ/kg.K
        1 LPM ~ 0.0167 kg/s
        """
        mass_flow_kg_s = self.state.flow_rate_lpm * (1.0 / 60.0) # Approx 1kg/L
        delta_t = self.state.temp_in_c - self.state.temp_out_c
        cp_water = 4.18 # kJ/kg.K
        
        thermal_power_kw = mass_flow_kg_s * cp_water * delta_t
        return thermal_power_kw

    def optimize_flow(self, spot_price_electricity):
        """
        Decides whether to pump harder based on electricity cost vs heat value.
        """
        print(f"   ⚙️ Optimizing flow for spot price: ${spot_price_electricity}/kWh...")
        # Simple logic: If electricity is cheap, pump harder to capture more heat
        if spot_price_electricity < 0.15:
            self.state.flow_rate_lpm *= 1.1
            print("   -> Boosting pumps (Cheap Power)")
        else:
            self.state.flow_rate_lpm *= 0.9
            print("   -> Throttling pumps (Expensive Power)")

    def run_cycle(self, duration_hours=1.0):
        """
        Executes one control cycle: Read -> Optimize -> Bill.
        """
        self.read_telemetry()
        
        # 1. Calculate Physics
        thermal_kw = self.calculate_thermal_power()
        net_energy_kwh = (thermal_kw - self.state.pump_power_kw) * duration_hours
        
        # 2. Calculate Economics
        revenue = (net_energy_kwh / 1000.0) * self.ppa_price
        carbon_saved_kg = net_energy_kwh * 0.2 # Approx gas boiler displacement
        
        print(f"   🌡️ Captured {thermal_kw:.2f} kW_th | Net: {net_energy_kwh:.2f} kWh")
        print(f"   💰 Revenue: ${revenue:.4f} | 🌿 CO2 Avoided: {carbon_saved_kg:.2f} kg")
        
        # 3. Mint Value
        self.ledger.record_transaction(self.facility_id, "HeatDelivery", revenue)
        self.ledger.record_transaction(self.facility_id, "CarbonCredit", carbon_saved_kg * 0.05) # $50/ton

if __name__ == "__main__":
    dac = HaaSCaptureCapsule("DC-PILOT-01")
    dac.run_cycle()
    dac.optimize_flow(0.10)
    dac.run_cycle()
