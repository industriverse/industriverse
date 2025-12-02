import time
from dataclasses import dataclass

@dataclass
class PermissionEvent:
    process_name: str
    permission_type: str # MIC, CAM, LOC, SCREEN
    timestamp: float
    energy_cost_joules: float

class PermissionGraph:
    """
    SCDS Pillar II: Permission & Identity.
    Maps 'Who did What' to 'What it Cost'.
    """
    def __init__(self):
        self.events = []
        
    def log_event(self, process: str, permission: str, energy: float):
        event = PermissionEvent(process, permission, time.time(), energy)
        self.events.append(event)
        print(f"🛡️ [PermGraph] Logged: {process} used {permission} (Cost: {energy:.4f} J)")
        
    def analyze_anomalies(self):
        """
        Detects suspicious permission/energy patterns.
        """
        print("🔍 [PermGraph] Analyzing Anomalies...")
        for event in self.events:
            # Heuristic: Background process using Camera
            if "updater" in event.process_name and event.permission_type == "CAM":
                print(f"   🚨 ALERT: {event.process_name} accessed CAMERA!")
                
            # Heuristic: High energy mic usage
            if event.permission_type == "MIC" and event.energy_cost_joules > 5.0:
                print(f"   ⚠️ WARNING: High Energy Mic Usage by {event.process_name}")
