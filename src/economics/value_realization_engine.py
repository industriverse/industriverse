from dataclasses import dataclass
import time

@dataclass
class ValueReport:
    period_start: float
    period_end: float
    energy_saved_kwh: float
    downtime_prevented_min: float
    total_value_usd: float
    roi_multiple: float # Value / Cost

class ValueRealizationEngine:
    """
    Translates Technical Telemetry -> Financial Value.
    Supports the 'Value-Based Pricing' strategy.
    """
    
    def __init__(self, energy_cost_per_kwh=0.15, downtime_cost_per_min=1000.0, subscription_cost_monthly=5000.0):
        self.energy_cost = energy_cost_per_kwh
        self.downtime_cost = downtime_cost_per_min
        self.monthly_cost = subscription_cost_monthly
        
    def calculate_roi(self, optimization_events: list) -> ValueReport:
        """
        Input: List of OptimizationOpportunity objects (from FoundryOptimizer)
        Output: Financial Report
        """
        total_joules_saved = 0.0
        total_downtime_prevented_min = 0.0
        
        for event in optimization_events:
            # Energy Savings
            if hasattr(event, 'potential_savings_joules'):
                total_joules_saved += event.potential_savings_joules
            
            # Downtime Prevention (Mock logic based on severity)
            # If we prevented a "Critical" throttling event, we assume we saved downtime.
            if event.type == "THROTTLING" and event.severity > 0.8:
                total_downtime_prevented_min += 5.0 # Assume 5 mins of downtime saved
                
            if event.type == "COOLING_INEFFICIENCY" and event.severity > 0.9:
                total_downtime_prevented_min += 10.0 # Prevent hardware failure
                
        # Conversions
        kwh_saved = total_joules_saved / 3600000.0
        energy_value = kwh_saved * self.energy_cost
        downtime_value = total_downtime_prevented_min * self.downtime_cost
        
        total_value = energy_value + downtime_value
        
        # Simple ROI (assuming this is a daily snapshot, scaled to month for rough multiple)
        # This is a simplification for the demo.
        roi = (total_value * 30) / self.monthly_cost if self.monthly_cost > 0 else 0
        
        return ValueReport(
            period_start=time.time(),
            period_end=time.time(),
            energy_saved_kwh=kwh_saved,
            downtime_prevented_min=total_downtime_prevented_min,
            total_value_usd=total_value,
            roi_multiple=roi
        )

# --- Verification ---
if __name__ == "__main__":
    # Mock specific event class to avoid dependency import issues in standalone run
    @dataclass
    class MockEvent:
        type: str
        severity: float
        potential_savings_joules: float
        
    engine = ValueRealizationEngine()
    
    # Simulate a day of "Foundry" work
    events = [
        MockEvent("ZOMBIE", 0.8, 5000000.0), # Killed a big zombie
        MockEvent("THROTTLING", 0.9, 0.0),   # Prevented a crash
        MockEvent("COOLING_INEFFICIENCY", 0.5, 100000.0)
    ]
    
    print("💰 Calculating Value Realization...")
    report = engine.calculate_roi(events)
    
    print(f"   - Energy Saved: {report.energy_saved_kwh:.4f} kWh")
    print(f"   - Downtime Prevented: {report.downtime_prevented_min:.1f} min")
    print(f"   - Total Value Generated: ${report.total_value_usd:.2f}")
    print(f"   - Implied Monthly ROI: {report.roi_multiple:.1f}x")
