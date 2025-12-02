import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.mobile.agent.core import ThermodynamicAgent, ThreatSignature
from src.mobile.backend.collector import MobileCollector
from src.mobile.swarm.client import SwarmClient
from src.mobile.security.esim import eSIMAnchor
from src.mobile.analysis.network import NetworkAnalyzer, NetworkFlow

def verify_mobile_defense():
    print("🛡️ Starting Mobile Defense Verification (Full Suite)...")
    
    # 1. Initialize Components
    collector = MobileCollector()
    agent = ThermodynamicAgent("DEVICE_ALPHA")
    swarm = SwarmClient("DEVICE_ALPHA")
    esim = eSIMAnchor("ICCID_123456789")
    net_analyzer = NetworkAnalyzer()
    
    # 2. Verify eSIM Integrity
    print("\n--- Phase 1: eSIM Security ---")
    is_safe = esim.verify_network_integrity("310-410-1234", 10)
    if is_safe:
        print("✅ eSIM: Network Integrity Verified.")
    
    # 3. Verify Network Forensics
    print("\n--- Phase 2: Network Forensics ---")
    # Simulate a heartbeat
    target_ip = "192.168.1.50"
    for i in range(4):
        flow = NetworkFlow(time.time() + i, target_ip, 80, 500, "TCP", False)
        risk = net_analyzer.analyze_flow(flow)
    
    if risk > 0:
        print(f"✅ Network: Detected Heartbeat Risk ({risk:.2f})")
    else:
        print("❌ Network: Failed to detect heartbeat.")

    # 4. Verify Swarm Gossip
    print("\n--- Phase 3: Swarm Gossip ---")
    swarm.discover_peers()
    threat = ThreatSignature("SpyApp_v2", 0.95, [600.0, 5000.0, 3.0], "hash_spy")
    swarm.broadcast_threat(threat)
    
    # Simulate receiving gossip
    swarm.receive_gossip({
        "type": "THREAT_ANNOUNCEMENT",
        "source": "DEVICE_BETA",
        "threat": {
            "app_name": "Malware_X",
            "risk_score": 0.99,
            "behavior_vector": [],
            "evidence_hash": "hash_x"
        }
    })
    
    if "Malware_X" in swarm.known_threats:
        print("✅ Swarm: Successfully learned about 'Malware_X' from peer.")

    print("\n✅ FULL SUITE VERIFICATION COMPLETE.")

if __name__ == "__main__":
    verify_mobile_defense()
