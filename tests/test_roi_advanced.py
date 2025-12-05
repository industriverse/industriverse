import pytest
import os
from src.scf.evaluation.roi_calculator import ROICalculator
from src.scf.evaluation.investor_report_gen import InvestorReportGenerator

def test_npv_calculation():
    calc = ROICalculator()
    # Invest 1000, Save 300/year for 5 years. Discount 10%.
    # NPV should be positive (~137)
    npv = calc.calculate_npv(annual_savings=300, capex=1000, years=5, discount_rate=0.10)
    assert npv > 0
    assert 130 < npv < 145

def test_carbon_credits():
    calc = ROICalculator()
    # 1000 kWh saved -> 400 kg CO2 -> 0.4 tons
    credits = calc.calculate_carbon_credits(1000)
    assert credits == 0.4

def test_report_generation():
    gen = InvestorReportGenerator()
    report = gen.generate_report(
        client_name="Test Corp",
        energy_saved_kwh=1000, # Weekly
        capex=5000
    )
    
    assert "# 📊 Sovereign Energy Intelligence Report" in report
    assert "Test Corp" in report
    assert "Net Present Value" in report
    
    # Test Save
    gen.save_report(report, "test_report.md")
    assert os.path.exists("test_report.md")
    os.remove("test_report.md")
