import unittest
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from frameworks.idf.core.energy_field import EnergyField
from frameworks.idf.core.diffusion_dynamics import DiffusionDynamics
from frameworks.idf.layers.eil_optimizer import EILOptimizer

class TestIDFCore(unittest.TestCase):
    
    def test_energy_field_synthetic(self):
        """Test that EnergyField generates synthetic data."""
        field = EnergyField("test_map")
        self.assertIsNotNone(field.data)
        self.assertEqual(field.data.shape, (100, 100))
        
        # Test interpolation
        e = field.get_energy(np.array([0.5, 0.5]))
        self.assertIsInstance(e, float)
        
        # Test gradient
        g = field.get_gradient(np.array([0.5, 0.5]))
        self.assertEqual(g.shape, (2,))

    def test_diffusion_optimization(self):
        """Test that diffusion actually reduces energy."""
        optimizer = EILOptimizer("test_opt")
        
        # Start at a high energy point (e.g., edge)
        # Synthetic map is a Gaussian at center, so edges are high energy? 
        # Wait, synthetic is exp(-(X^2+Y^2)), so center (0,0) is HIGH value (1.0).
        # But Energy usually means LOWER is better.
        # Let's check synthetic gen: Z = exp(...) normalized 0-1.
        # If we treat Z as Energy, then 0 is good.
        # The Gaussian peak is at 1.0. So center is HIGH energy.
        # Diffusion should move AWAY from center towards edges (0.0).
        
        start = np.array([0.5, 0.5]) # Center (High Energy)
        
        # Run optimization
        res = optimizer.optimize_configuration(start, steps=100)
        
        print(f"\nStart Energy: {res['start_energy']:.4f}")
        print(f"Final Energy: {res['final_energy']:.4f}")
        print(f"Delta: {res['energy_delta']:.4f}")
        
        self.assertLess(res['final_energy'], res['start_energy'])
        self.assertLess(res['energy_delta'], 0.0)

if __name__ == '__main__':
    unittest.main()
