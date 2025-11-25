import unittest
import tempfile
import os
import json
from src.core.energy_atlas.hardware_loader import HardwareLoader
from src.core.energy_atlas.hardware_schema import HardwareNode

class TestHardwareLoader(unittest.TestCase):
    
    def setUp(self):
        self.loader = HardwareLoader()
        self.test_manifest = {
            "version": "1.0",
            "nodes": [
                {
                    "node_id": "test_node_1",
                    "node_type": "test_chip",
                    "electrical": {
                        "capacitance_gate": 1.0e-9,
                        "capacitance_wire": 1.0e-9,
                        "capacitance_fringe": 0.0,
                        "voltage_min": 0.8,
                        "voltage_max": 1.2,
                        "leakage_current_base": 0.01,
                        "thermal_resistance": 0.5
                    },
                    "location": {"x": 0, "y": 0}
                }
            ]
        }
        
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
        json.dump(self.test_manifest, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_load_manifest(self):
        nodes = self.loader.load_manifest(self.temp_file.name)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].node_id, "test_node_1")
        self.assertEqual(nodes[0].electrical.total_capacitance, 2.0e-9)

    def test_energy_calculation(self):
        self.loader.load_manifest(self.temp_file.name)
        # E = 0.5 * C * V^2
        # C = 2.0e-9, V = 1.0
        # E = 0.5 * 2.0e-9 * 1.0 = 1.0e-9 Joules
        energy = self.loader.calculate_energy_per_op("test_node_1", 1.0)
        self.assertAlmostEqual(energy, 1.0e-9)

    def test_leakage_calculation(self):
        self.loader.load_manifest(self.temp_file.name)
        # T = 25C (base) -> I_leak = base = 0.01
        # P = V * I = 1.0 * 0.01 = 0.01 Watts
        power_25c = self.loader.calculate_static_power("test_node_1", 1.0, 25.0)
        self.assertAlmostEqual(power_25c, 0.01)
        
        # T = 40C -> delta = 15C -> I_leak doubles (approx)
        # P should be approx 0.02
        power_40c = self.loader.calculate_static_power("test_node_1", 1.0, 40.0)
        self.assertTrue(power_40c > power_25c)

if __name__ == '__main__':
    unittest.main()
