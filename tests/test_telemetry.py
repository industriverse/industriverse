import pytest
import os
import time
from src.scf.telemetry.collector import TelemetryCollector
from src.scf.telemetry.kwh_meter import KWhMeter
from src.scf.telemetry.dashboard_api import DashboardAPI

def test_collector_logging():
    collector = TelemetryCollector(log_dir="test_logs")
    collector.log_metric("cpu_usage", 50.0)
    
    logs = collector.get_recent_metrics(limit=1)
    assert len(logs) == 1
    assert logs[0]['metric'] == "cpu_usage"
    assert logs[0]['value'] == 50.0
    
    # Cleanup
    for f in os.listdir("test_logs"):
        os.remove(os.path.join("test_logs", f))
    os.rmdir("test_logs")

def test_kwh_meter():
    meter = KWhMeter(baseline_power_w=100.0, max_power_w=200.0)
    
    # Measure with 0 load (should be ~100W)
    p1 = meter.measure(0.0)
    assert 95.0 < p1 < 105.0
    
    # Measure with 100% load (should be ~200W)
    p2 = meter.measure(1.0)
    assert 190.0 < p2 < 210.0
    
    assert meter.get_total_kwh() > 0.0

def test_dashboard_api():
    api = DashboardAPI()
    status = api.get_system_status()
    
    assert status['status'] == "ONLINE"
    assert 'power_usage_w' in status
    assert 'total_energy_kwh' in status
