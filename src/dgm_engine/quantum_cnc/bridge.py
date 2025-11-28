import requests
from typing import Dict, Any, Optional

class QuantumBridge:
    """
    Bridge to the Quantum Darwin-Gödel CNC Service (Port 8220).
    """
    def __init__(self, base_url: str = "http://localhost:8220"):
        self.base_url = base_url
        self.is_connected = False
        self._check_connection()

    def _check_connection(self):
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=2)
            if resp.status_code == 200:
                self.is_connected = True
                print(f"Connected to Quantum Cloud at {self.base_url}")
            else:
                print(f"Quantum Cloud returned status {resp.status_code}")
        except Exception as e:
            print(f"Could not connect to Quantum Cloud: {e}")
            self.is_connected = False

    def optimize_toolpath(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Request quantum optimization for a toolpath task"""
        if not self.is_connected:
            return {"error": "Quantum Service Offline", "mock": True}
        
        try:
            resp = requests.post(f"{self.base_url}/api/v1/optimize", json=task)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def evolve_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Offload evolution step to Quantum DGM"""
        if not self.is_connected:
            return {"error": "Quantum Service Offline", "mock": True}
            
        try:
            resp = requests.post(f"{self.base_url}/api/v1/evolve", json=agent_config)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
