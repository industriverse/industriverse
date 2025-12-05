import pytest
from src.scf.evaluation.roi_calculator import ROICalculator

def test_basic_savings():
    calc = ROICalculator(electricity_price_usd_per_kwh=0.10)
    # 100 kWh -> 80 kWh (20 saved)
    metrics = calc.calculate_roi(baseline_kwh_per_day=100.0, optimized_kwh_per_day=80.0)
    
    assert metrics.energy_saved_kwh == 20.0
    assert metrics.cost_saved_usd == 2.0 # 20 * 0.10
    assert metrics.payback_period_days == 0.0 # No cost
    assert metrics.roi_percentage == float('inf')

def test_payback_period():
    calc = ROICalculator(electricity_price_usd_per_kwh=0.20)
    # Save 10 kWh/day = $2/day
    # Cost = $100
    metrics = calc.calculate_roi(
        baseline_kwh_per_day=50.0, 
        optimized_kwh_per_day=40.0, 
        implementation_cost_usd=100.0
    )
    
    assert metrics.cost_saved_usd == 2.0
    assert metrics.payback_period_days == 50.0 # 100 / 2

def test_negative_savings_handled():
    calc = ROICalculator()
    # Optimization made it worse? Should handle gracefully
    metrics = calc.calculate_roi(baseline_kwh_per_day=50.0, optimized_kwh_per_day=60.0)
    
    assert metrics.energy_saved_kwh == 0.0
    assert metrics.cost_saved_usd == 0.0

def test_fleet_projection():
    calc = ROICalculator(electricity_price_usd_per_kwh=0.10)
    metrics = calc.calculate_roi(baseline_kwh_per_day=10.0, optimized_kwh_per_day=5.0) # Save $0.50
    
    projection = calc.project_fleet_savings(metrics, fleet_size=1000)
    
    assert projection["daily_fleet_savings_usd"] == 500.0 # 0.50 * 1000
    assert projection["annual_fleet_savings_usd"] == 500.0 * 365.0
