import unittest
from src.scf.ingestion.fossil_schema import Fossil
import time

class TestFossilIntegrity(unittest.TestCase):
    def test_fossil_hashing(self):
        fossil_data = {
            "id": "test-id-123",
            "source": "test_source",
            "timestamp": time.time(),
            "data": {"value": 42},
            "meta": {"type": "test"}
        }
        fossil = Fossil(**fossil_data)
        
        # Initial state
        self.assertIsNone(fossil.hash)
        
        # Sign
        fossil.sign()
        self.assertIsNotNone(fossil.hash)
        print(f"Fossil Hash: {fossil.hash}")
        
        # Verify determinism
        hash1 = fossil.hash
        fossil.sign()
        self.assertEqual(hash1, fossil.hash)
        
        # Verify change sensitivity
        fossil.data["value"] = 43
        new_hash = fossil.compute_hash()
        self.assertNotEqual(hash1, new_hash)

if __name__ == '__main__':
    unittest.main()
