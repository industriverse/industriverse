from src.scf.telemetry.collector import TelemetryCollector
from src.scf.telemetry.kwh_meter import KWhMeter

class DashboardAPI:
    """
    Simple API to serve metrics to a dashboard.
    """
    def __init__(self):
        self.collector = TelemetryCollector()
        self.meter = KWhMeter()

    def get_system_status(self):
        """
        Get high-level system status.
        """
        # Mock load
        current_power = self.meter.measure(load_percent=0.5)
        
        return {
            "status": "ONLINE",
            "power_usage_w": current_power,
            "total_energy_kwh": self.meter.get_total_kwh(),
            "recent_logs": self.collector.get_recent_metrics(limit=5)
        }

    def log_event(self, event_name: str, value: float):
        self.collector.log_metric(event_name, value)
