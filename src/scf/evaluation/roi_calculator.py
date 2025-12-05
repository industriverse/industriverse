from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ROIMetrics:
    energy_saved_kwh: float
    cost_saved_usd: float
    payback_period_days: float
    roi_percentage: float
    carbon_saved_kg: float

class ROICalculator:
    """
    The Financial Engine of the Sovereign Stack.
    Converts Joules/kWh into Dollars and ROI.
    """
    def __init__(self, electricity_price_usd_per_kwh: float = 0.12, 
                 carbon_intensity_kg_per_kwh: float = 0.4):
        self.price_per_kwh = electricity_price_usd_per_kwh
        self.carbon_per_kwh = carbon_intensity_kg_per_kwh

    def calculate_roi(self, 
                      baseline_kwh_per_day: float, 
                      optimized_kwh_per_day: float, 
                      implementation_cost_usd: float = 0.0) -> ROIMetrics:
        """
        Calculate ROI for a given optimization.
        
        Args:
            baseline_kwh_per_day: Energy usage before optimization.
            optimized_kwh_per_day: Energy usage after optimization.
            implementation_cost_usd: One-time cost of the optimization (hardware/software).
        """
        daily_kwh_saved = max(0.0, baseline_kwh_per_day - optimized_kwh_per_day)
        daily_usd_saved = daily_kwh_saved * self.price_per_kwh
        daily_carbon_saved = daily_kwh_saved * self.carbon_per_kwh
        
        # Annualized projections
        annual_usd_saved = daily_usd_saved * 365.0
        
        # Payback Period
        if daily_usd_saved > 0:
            payback_days = implementation_cost_usd / daily_usd_saved
        else:
            payback_days = float('inf')
            
        # ROI % (1 Year Horizon)
        # ROI = (Net Profit / Cost) * 100
        # Net Profit = Savings - Cost
        if implementation_cost_usd > 0:
            net_profit = annual_usd_saved - implementation_cost_usd
            roi_pct = (net_profit / implementation_cost_usd) * 100.0
        else:
            # If no cost, ROI is infinite (or just defined by savings)
            roi_pct = float('inf') if annual_usd_saved > 0 else 0.0

        return ROIMetrics(
            energy_saved_kwh=daily_kwh_saved,
            cost_saved_usd=daily_usd_saved,
            payback_period_days=payback_days,
            roi_percentage=roi_pct,
            carbon_saved_kg=daily_carbon_saved
        )

    def project_fleet_savings(self, 
                              single_unit_metrics: ROIMetrics, 
                              fleet_size: int) -> Dict[str, float]:
        """
        Project savings for a fleet of devices.
        """
        return {
            "daily_fleet_savings_usd": single_unit_metrics.cost_saved_usd * fleet_size,
            "annual_fleet_savings_usd": single_unit_metrics.cost_saved_usd * fleet_size * 365.0,
            "annual_carbon_reduction_tons": (single_unit_metrics.carbon_saved_kg * fleet_size * 365.0) / 1000.0
        }
