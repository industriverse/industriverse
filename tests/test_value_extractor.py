import pytest
import os
import json
from src.agentops.value_extractor import ValueExtractorAgent

def test_report_generation():
    agent = ValueExtractorAgent(energy_price=0.10)
    report = agent.generate_weekly_report("Week-17", baseline_kwh=100, actual_kwh=90)
    
    assert report["week_id"] == "Week-17"
    assert report["cost_saved_usd"] == 1.0 # 10 kWh * $0.10
    assert "Positive Impact" in report["message"]

def test_export_history():
    agent = ValueExtractorAgent()
    agent.generate_weekly_report("W1", 100, 90)
    agent.generate_weekly_report("W2", 100, 80)
    
    export_path = "test_reports.jsonl"
    agent.export_reports(export_path)
    
    assert os.path.exists(export_path)
    with open(export_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 2
        
    os.remove(export_path)
