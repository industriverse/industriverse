import time
from dataclasses import dataclass

@dataclass
class OptimizationOpportunity:
    type: str # 'THROTTLING', 'ZOMBIE', 'COOLING'
    severity: float # 0.0 to 1.0
    potential_savings_joules: float
    recommendation: str

class FoundryOptimizer:
    """
    The 'Foundry' Lens for SCDS.
    Analyzes thermodynamic telemetry for EFFICIENCY, not just SECURITY.
    """
    
    def __init__(self):
        self.thermal_threshold_c = 80.0
        self.idle_power_threshold_w = 5.0
        
    def analyze_node(self, telemetry: dict) -> list[OptimizationOpportunity]:
        """
        Input: SCDS Telemetry Dict (Temps, Power, Process List)
        Output: List of Efficiency Opportunities
        """
        opportunities = []
        
        # 1. Detect Thermal Throttling (Wasted Performance)
        # If temp is high but clock speed (implied) or power is capped
        avg_temp = sum(telemetry.get('core_temps', [])) / len(telemetry.get('core_temps', [1]))
        if avg_temp > self.thermal_threshold_c:
            opportunities.append(OptimizationOpportunity(
                type="THROTTLING",
                severity=(avg_temp - self.thermal_threshold_c) / 20.0,
                potential_savings_joules=0.0, # Performance gain, not energy savings
                recommendation="Thermal Throttling Detected. Improve cooling or migrate workload."
            ))
            
        # 2. Detect Zombie Processes (Wasted Energy)
        # High power draw but low 'useful' work (entropy/IO)
        for proc in telemetry.get('processes', []):
            if proc['power_w'] > self.idle_power_threshold_w and proc['useful_work_metric'] < 0.1:
                opportunities.append(OptimizationOpportunity(
                    type="ZOMBIE",
                    severity=0.8,
                    potential_savings_joules=proc['power_w'] * 3600, # Joules per hour
                    recommendation=f"Zombie Process '{proc['name']}' detected. Kill to save energy."
                ))
                
        # 3. Cooling Efficiency Analysis
        # (Mock logic: If fans are 100% but temp isn't dropping)
        if telemetry.get('fan_speed_pct', 0) > 90 and avg_temp > 70:
             opportunities.append(OptimizationOpportunity(
                type="COOLING_INEFFICIENCY",
                severity=0.6,
                potential_savings_joules=5000.0,
                recommendation="Cooling system saturated. Check airflow or thermal paste."
            ))
            
        return opportunities

# --- Verification ---
if __name__ == "__main__":
    optimizer = FoundryOptimizer()
    
    # Simulate a "Hot, Inefficient" Node
    mock_telemetry = {
        'core_temps': [85, 84, 86, 85],
        'fan_speed_pct': 100,
        'processes': [
            {'name': 'stuck_miner', 'power_w': 50.0, 'useful_work_metric': 0.05}, # Zombie
            {'name': 'valid_job', 'power_w': 120.0, 'useful_work_metric': 0.9}
        ]
    }
    
    print("🏭 Running Foundry Optimizer Analysis...")
    ops = optimizer.analyze_node(mock_telemetry)
    
    for op in ops:
        print(f"\n💡 OPPORTUNITY: {op.type}")
        print(f"   Severity: {op.severity:.2f}")
        print(f"   Savings: {op.potential_savings_joules:.2f} J")
        print(f"   Action: {op.recommendation}")
