import json
from datetime import datetime
from typing import Dict, List
from src.scf.evaluation.roi_calculator import ROICalculator, ROIMetrics

class ValueExtractorAgent:
    """
    An agent that monitors energy savings and produces value reports.
    """
    def __init__(self, energy_price: float = 0.12):
        self.roi_calc = ROICalculator(electricity_price_usd_per_kwh=energy_price)
        self.report_history = []

    def generate_weekly_report(self, 
                               week_id: str,
                               baseline_kwh: float, 
                               actual_kwh: float,
                               fleet_size: int = 1) -> Dict:
        """
        Generate a report for a specific week.
        """
        metrics = self.roi_calc.calculate_roi(baseline_kwh, actual_kwh)
        fleet_metrics = self.roi_calc.project_fleet_savings(metrics, fleet_size)
        
        report = {
            "week_id": week_id,
            "timestamp": datetime.now().isoformat(),
            "energy_saved_kwh": metrics.energy_saved_kwh,
            "cost_saved_usd": metrics.cost_saved_usd,
            "fleet_savings_usd": fleet_metrics["daily_fleet_savings_usd"], # Assuming daily input for now, or we scale
            "carbon_saved_kg": metrics.carbon_saved_kg,
            "message": self._generate_message(metrics.cost_saved_usd)
        }
        
        self.report_history.append(report)
        return report

    def _generate_message(self, saved_usd: float) -> str:
        if saved_usd > 100:
            return f"🚀 High Impact! Saved ${saved_usd:.2f} today."
        elif saved_usd > 0:
            return f"✅ Positive Impact. Saved ${saved_usd:.2f} today."
        else:
            return "⚠️ No savings detected. Optimization required."

    def export_reports(self, filepath: str):
        with open(filepath, 'w') as f:
            for report in self.report_history:
                f.write(json.dumps(report) + "\n")
