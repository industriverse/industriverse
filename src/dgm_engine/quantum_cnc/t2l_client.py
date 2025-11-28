import requests
from typing import Dict, Any

class T2LClient:
    """
    Client for T2L Molecular Design Service (Port 8114).
    """
    def __init__(self, base_url: str = "http://localhost:8114"):
        self.base_url = base_url
        self.is_connected = False
        self._check_connection()

    def _check_connection(self):
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=2)
            if resp.status_code == 200:
                self.is_connected = True
                print(f"Connected to T2L Service at {self.base_url}")
            else:
                print(f"T2L Service returned status {resp.status_code}")
        except Exception as e:
            print(f"Could not connect to T2L Service: {e}")
            self.is_connected = False

    def generate_lora(self, task_description: str, domain: str) -> Dict[str, Any]:
        """Request LoRA generation from text description"""
        if not self.is_connected:
            return {"error": "T2L Service Offline", "mock": True}
            
        payload = {
            "task_description": task_description,
            "domain": domain,
            "quantum_enhanced": True
        }
        
        try:
            resp = requests.post(f"{self.base_url}/api/v1/text-to-lora", json=payload)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
