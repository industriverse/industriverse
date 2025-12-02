from typing import List, Dict
import time
from ..agent.core import ThreatSignature

class MobileCollector:
    """
    The Cloud/Local Collector that aggregates telemetry from millions of devices.
    Implements 'Herd Immunity' by identifying common threat signatures.
    """
    def __init__(self):
        self.threat_db: Dict[str, List[ThreatSignature]] = {} # Map app_name -> threats
        self.global_blocklist: List[str] = []

    def ingest_threat(self, device_id: str, threat: ThreatSignature):
        """
        Receives a threat report from a device.
        """
        print(f"📥 [Collector] Received Threat from {device_id}: {threat.app_name} (Risk: {threat.risk_score})")
        
        if threat.app_name not in self.threat_db:
            self.threat_db[threat.app_name] = []
        
        self.threat_db[threat.app_name].append(threat)
        self.analyze_herd_immunity(threat.app_name)

    def analyze_herd_immunity(self, app_name: str):
        """
        If enough devices report the same app, mark it as a Global Threat.
        """
        reports = self.threat_db.get(app_name, [])
        count = len(reports)
        avg_risk = sum(t.risk_score for t in reports) / count
        
        print(f"   🔍 Analyzing {app_name}: {count} reports, Avg Risk {avg_risk:.2f}")
        
        # Threshold for "Herd Immunity" trigger
        if count >= 3 and avg_risk > 0.7:
            if app_name not in self.global_blocklist:
                self.global_blocklist.append(app_name)
                print(f"   🚫 GLOBAL BLOCKLIST: {app_name} has been marked as hostile by the swarm!")
                self.broadcast_immunity(app_name)

    def broadcast_immunity(self, app_name: str):
        """
        Simulates sending a push notification to all devices to block the app.
        """
        print(f"   📡 BROADCAST: Protecting all devices from {app_name}...")

if __name__ == "__main__":
    # Simulation
    collector = MobileCollector()
    
    # Simulating 3 devices reporting the same threat
    from ..agent.core import ThreatSignature
    
    t1 = ThreatSignature("SpyApp_v1", 0.9, [500.0, 10000.0, 2.0], "hash1")
    t2 = ThreatSignature("SpyApp_v1", 0.85, [480.0, 12000.0, 2.0], "hash2")
    t3 = ThreatSignature("SpyApp_v1", 0.92, [510.0, 9000.0, 2.0], "hash3")
    
    collector.ingest_threat("DEVICE_001", t1)
    collector.ingest_threat("DEVICE_002", t2)
    collector.ingest_threat("DEVICE_003", t3)
