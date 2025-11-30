import math

class EntropyOracle:
    """
    The Entropy Oracle: Calculating the Thermodynamic Value.
    This defines the 'Thermodynamic Niche' by quantifying Negentropy.
    """
    def __init__(self):
        pass

    def calculate_thermodynamic_value(self, trinity_packet: dict) -> dict:
        """
        Analyzes the Trinity Packet to compute high-level physics metrics.
        """
        components = trinity_packet.get("components", {})
        os_data = components.get("industriverse", {})
        hw_data = components.get("thermodynasty", {})
        
        # Extract raw metrics
        capsules = os_data.get("capsule_count", 0)
        power = hw_data.get("power_draw_w", 1.0)
        temp = hw_data.get("edcoc_temp_c", 25.0)
        
        # 1. Negentropy Score (Order created per Watt)
        # Higher capsules (complexity) + Lower Power = Higher Negentropy
        negentropy_score = (capsules * 10) / (power * (temp / 20.0))
        
        # 2. Thermal Efficiency (Compute per Degree Celsius)
        thermal_efficiency = capsules / temp
        
        # 3. Innovation Potential (Probability of breakthrough)
        # Based on system load and complexity
        innovation_potential = min(0.99, (capsules / 1000.0) + 0.1)
        
        return {
            "negentropy_score": round(negentropy_score, 4),
            "thermal_efficiency": round(thermal_efficiency, 4),
            "innovation_potential": round(innovation_potential, 4),
            "unit": "J/K (Information Entropy)"
        }
