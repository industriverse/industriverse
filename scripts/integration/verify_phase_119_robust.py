import sys
import os
import time
import threading
import json
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.oracle import Oracle
from src.api.websocket_server import run_server

class TestPhase119(unittest.TestCase):
    
    def setUp(self):
        self.oracle = Oracle()

    def test_oracle_valid_query(self):
        print("\n🔵 Testing Oracle with Valid Query...")
        result = self.oracle.query("Why is the metal expanding under heat?")
        print(f"   Result: {result['principle']}")
        self.assertEqual(result['principle'], "Linear Thermal Expansion")
        self.assertIn("ΔL = αLΔT", result['equation'])

    def test_oracle_unknown_query(self):
        print("\n🔵 Testing Oracle with Nonsense Query...")
        result = self.oracle.query("Why is the sky blue?")
        print(f"   Result: {result['principle']}")
        self.assertEqual(result['principle'], "Unknown Phenomenon")

    def test_websocket_server_mock(self):
        print("\n🔵 Testing WebSocket Server (Mock Mode)...")
        # We run the server in a separate thread to not block
        # However, the mock server in websocket_server.py is designed to run for a fixed time or loop
        # Let's verify we can import it and it has the expected attributes
        import src.api.websocket_server as ws
        self.assertTrue(hasattr(ws, 'run_server'))
        
        # We can't easily test the infinite loop of the real server in a unit test without complex async logic
        # But we can verify the data generator logic
        data = ws.generate_telemetry()
        print(f"   Generated Telemetry: {data}")
        self.assertIn('temperature', data)
        self.assertIn('entropy', data)
        self.assertEqual(data['status'], "NOMINAL")

if __name__ == '__main__':
    print("############################################################")
    print("#   PHASE 119 ROBUST VERIFICATION                          #")
    print("############################################################")
    unittest.main()
