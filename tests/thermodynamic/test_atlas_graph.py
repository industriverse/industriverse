import unittest
import tempfile
import os
import json
from src.core.energy_atlas.atlas_core import EnergyAtlas, MockNeo4jDriver

class TestEnergyAtlas(unittest.TestCase):
    
    def setUp(self):
        self.atlas = EnergyAtlas(use_mock=True)
        
        self.test_manifest = {
            "version": "1.0",
            "nodes": [
                {
                    "node_id": "atlas_test_node",
                    "node_type": "test_core",
                    "electrical": {
                        "capacitance_gate": 1e-9,
                        "capacitance_wire": 1e-9,
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
        self.atlas.close()
        os.unlink(self.temp_file.name)

    def test_load_and_sync(self):
        self.atlas.load_manifest(self.temp_file.name)
        
        # Check in-memory state
        self.assertIn("atlas_test_node", self.atlas.nodes)
        
        # Check mock driver state
        driver = self.atlas.driver
        self.assertIsInstance(driver, MockNeo4jDriver)
        self.assertIn("atlas_test_node", driver.nodes)
        
        # Verify stored properties
        stored_node = driver.nodes["atlas_test_node"]
        self.assertEqual(stored_node["node_type"], "test_core")
        self.assertEqual(stored_node["c_gate"], 1e-9)

    def test_get_energy_map(self):
        self.atlas.load_manifest(self.temp_file.name)
        emap = self.atlas.get_energy_map()
        
        self.assertEqual(emap["node_count"], 1)
        self.assertIn("atlas_test_node", emap["nodes"])

if __name__ == '__main__':
    unittest.main()
