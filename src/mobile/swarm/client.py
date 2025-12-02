import json
import random
import time
from typing import List, Dict, Optional
from dataclasses import asdict
from ..agent.core import ThreatSignature

class SwarmClient:
    """
    The 'Gossip' engine that shares threat signatures between devices.
    Implements a mock P2P protocol for 'Herd Immunity'.
    """
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.peers: List[str] = []
        self.known_threats: Dict[str, ThreatSignature] = {}
        
    def discover_peers(self):
        """
        Simulates finding other devices on the local network or mesh.
        """
        # In a real app, this would use mDNS or Bluetooth LE
        self.peers = [f"DEVICE_{random.randint(100, 999)}" for _ in range(3)]
        print(f"📡 [Swarm] {self.device_id} discovered peers: {self.peers}")
        
    def broadcast_threat(self, threat: ThreatSignature):
        """
        Sends a detected threat to all known peers.
        """
        payload = {
            "type": "THREAT_ANNOUNCEMENT",
            "source": self.device_id,
            "timestamp": time.time(),
            "threat": asdict(threat)
        }
        print(f"📤 [Swarm] Broadcasting threat '{threat.app_name}' to {len(self.peers)} peers.")
        # Simulate network transmission
        time.sleep(0.1)
        
    def receive_gossip(self, payload: dict):
        """
        Handles an incoming threat report from a peer.
        """
        if payload["type"] == "THREAT_ANNOUNCEMENT":
            threat_data = payload["threat"]
            app_name = threat_data["app_name"]
            print(f"📥 [Swarm] Received warning about '{app_name}' from {payload['source']}")
            
            # Update local knowledge base
            if app_name not in self.known_threats:
                # In a real system, we would verify the signature here
                print(f"   🛡️ [Swarm] BLOCKING '{app_name}' based on peer intelligence.")
                self.known_threats[app_name] = threat_data
