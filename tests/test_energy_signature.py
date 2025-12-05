import unittest
import numpy as np
from src.scf.ingestion.energy_signature import EnergySignature

class TestEnergySignature(unittest.TestCase):
    def setUp(self):
        self.sig = EnergySignature()

    def test_extract_empty(self):
        data = np.array([])
        result = self.sig.extract(data)
        self.assertEqual(result["entropy_rate"], 0.0)

    def test_extract_variance(self):
        # Create a signal with known variance
        # Variance of [1, 1, 1] is 0
        data = np.array([1.0, 1.0, 1.0])
        result = self.sig.extract(data)
        self.assertEqual(result["entropy_rate"], 0.0)
        
        # Variance of [1, -1] is 1.0
        data_var = np.array([1.0, -1.0])
        result_var = self.sig.extract(data_var)
        # entropy_rate = 0.5 * log(2 * pi * e * 1.0) approx 1.4189
        self.assertGreater(result_var["entropy_rate"], 1.0)

    def test_negentropy(self):
        baseline = 10.0
        current = 8.0
        negentropy = self.sig.compute_negentropy(baseline, current)
        self.assertEqual(negentropy, 2.0)
        
        # No negentropy if entropy increased
        self.assertEqual(self.sig.compute_negentropy(8.0, 10.0), 0.0)

if __name__ == '__main__':
    unittest.main()
