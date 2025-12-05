import unittest
from src.scf.evaluation.roi_calculator import ROICalculator

class TestROICalculator(unittest.TestCase):
    def setUp(self):
        self.roi = ROICalculator(kwh_price=0.10) # $0.10 per kWh

    def test_calculate_savings(self):
        baseline = 100.0
        optimized = 80.0
        
        result = self.roi.calculate_savings(baseline, optimized)
        
        self.assertEqual(result["kwh_saved"], 20.0)
        self.assertAlmostEqual(result["cost_saved_usd"], 2.0) # 20 * 0.10
        self.assertEqual(result["percent_improvement"], 20.0)

    def test_no_savings(self):
        baseline = 100.0
        optimized = 110.0 # Regression
        
        result = self.roi.calculate_savings(baseline, optimized)
        self.assertEqual(result["kwh_saved"], 0.0)
        self.assertEqual(result["cost_saved_usd"], 0.0)

    def test_payback_period(self):
        investment = 1000.0
        daily_savings = 100.0
        
        days = self.roi.estimate_payback_period(investment, daily_savings)
        self.assertEqual(days, 10.0)
        
        self.assertEqual(self.roi.estimate_payback_period(1000, 0), float('inf'))

if __name__ == '__main__':
    unittest.main()
