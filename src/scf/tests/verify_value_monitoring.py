import os
import json
from src.scf.fertilization.value_realization_engine import ValueRealizationEngine
from src.operations.dashboard_exporter import DashboardExporter

def verify_value_realization():
    print("💰 Verifying Value Realization Engine...")
    engine = ValueRealizationEngine()
    
    # Mock Deployment Result
    result = {
        "energy_trace_summary": {"joules_saved": 3600000.0}, # 1 kWh = 3.6 MJ
        "operational_impact": {"downtime_avoided_sec": 3600.0} # 1 Hour
    }
    
    value = engine.compute_value(result)
    
    # Assertions
    # 1 kWh @ $0.15 = $0.15
    # 1 Hour Downtime @ $1000 = $1000
    expected_usd = 0.15 + 1000.0
    assert abs(value["usd_value"] - expected_usd) < 0.01, f"USD Value mismatch: {value['usd_value']}"
    
    # 3.6 MJ = 3.6 Credits + 3600 * 0.1 = 360 + 3.6 = 363.6 Credits
    expected_credits = 3.6 + 360.0
    assert abs(value["negentropy_credits"] - expected_credits) < 0.01, f"Credits mismatch: {value['negentropy_credits']}"
    
    print(f"✅ Value Calculated: ${value['usd_value']:.2f} | {value['negentropy_credits']:.2f} Credits")

def verify_dashboard_exporter():
    print("📊 Verifying Dashboard Exporter...")
    metrics_file = "data/datahub/test_dashboard.json"
    exporter = DashboardExporter(metrics_file=metrics_file)
    
    # Update Metrics
    exporter.update_model_metrics(0.1, 0.05, 12.5)
    exporter.update_operational_metrics(1, 10.0)
    
    # Verify File Write
    assert os.path.exists(metrics_file), "Metrics file not created"
    
    with open(metrics_file, 'r') as f:
        data = json.load(f)
        
    assert data["models"]["ebdm_loss"] == 0.1
    assert data["operations"]["cfr_fossils_count"] == 1
    assert data["operations"]["negentropy_minted_total"] == 10.0
    
    print("✅ Dashboard Metrics Exported Successfully.")
    
    # Cleanup
    os.remove(metrics_file)

if __name__ == "__main__":
    verify_value_realization()
    verify_dashboard_exporter()
    print("\n🎉 VALUE & MONITORING VERIFIED")
