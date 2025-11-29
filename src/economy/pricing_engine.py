import json
import sys

class ExergyPricingEngine:
    """
    AI Shield v3 - Gate 4: Exergy Pricing Engine.
    Calculates the 'True Cost' of manufacturing based on physics.
    Price = Energy + Time + Material + Entropy Risk.
    """
    def __init__(self):
        # Base Rates (USD)
        self.rate_energy_j = 0.00005  # ~$0.18/kWh
        self.rate_time_s = 0.008      # ~$30/hour (Machine + Labor)
        self.rate_material_g = 0.05   # ~$50/kg (Premium PLA)
        
        # Risk Multipliers
        self.risk_base = 1.0
        self.risk_high_entropy = 1.5  # Complex/Chaotic prints

    def calculate_price(self, simulation_result):
        """
        Input: { energy_j: 1000, time_s: 60, avg_power_w: 100 }
        Output: { total_price: 5.50, breakdown: {} }
        """
        energy_j = simulation_result.get("energy_j", 0)
        time_s = simulation_result.get("time_s", 0)
        
        # 1. Component Costs
        cost_energy = energy_j * self.rate_energy_j
        cost_time = time_s * self.rate_time_s
        
        # Estimate Material (Mock: 1g per 100J of energy is a rough heuristic for FDM)
        material_g = energy_j / 100.0 
        cost_material = material_g * self.rate_material_g
        
        # 2. Risk Assessment
        # High power density = High Risk
        avg_power = simulation_result.get("avg_power_w", 0)
        risk_multiplier = self.risk_base
        if avg_power > 200: # High load
            risk_multiplier = self.risk_high_entropy
            
        # 3. Total Calculation
        subtotal = cost_energy + cost_time + cost_material
        total_price = subtotal * risk_multiplier
        
        return {
            "total_price": round(total_price, 2),
            "currency": "USD",
            "breakdown": {
                "energy_cost": round(cost_energy, 4),
                "time_cost": round(cost_time, 4),
                "material_cost": round(cost_material, 4),
                "risk_multiplier": risk_multiplier
            },
            "thermodynamic_score": int(energy_j / time_s) if time_s > 0 else 0
        }

if __name__ == "__main__":
    engine = ExergyPricingEngine()
    # Test Case
    sim_result = {"energy_j": 5000, "time_s": 300, "avg_power_w": 120}
    print(json.dumps(engine.calculate_price(sim_result)))
