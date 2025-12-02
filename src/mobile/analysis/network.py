import time
from dataclasses import dataclass
from typing import List

@dataclass
class NetworkFlow:
    timestamp: float
    dest_ip: str
    dest_port: int
    bytes_sent: int
    protocol: str
    is_burst: bool

class NetworkAnalyzer:
    """
    Analyzes network traffic metadata for surveillance patterns.
    Focuses on 'Heartbeats' and 'Burst Exfiltration'.
    """
    def __init__(self):
        self.flow_history: List[NetworkFlow] = []
        
    def analyze_flow(self, flow: NetworkFlow) -> float:
        """
        Returns a Risk Score (0.0 - 1.0) for a given flow.
        """
        risk = 0.0
        self.flow_history.append(flow)
        
        # 1. Check for "Heartbeat" (Periodic small uploads)
        if self._detect_heartbeat(flow.dest_ip):
            print(f"   💓 [Net] Detected Heartbeat to {flow.dest_ip}")
            risk += 0.4
            
        # 2. Check for "Burst Exfil" (Large upload at odd hours)
        if flow.bytes_sent > 10000 and flow.is_burst:
            print(f"   🌊 [Net] Detected Burst Exfiltration ({flow.bytes_sent} bytes) to {flow.dest_ip}")
            risk += 0.5
            
        return min(risk, 1.0)
        
    def _detect_heartbeat(self, dest_ip: str) -> bool:
        """
        Checks if we have seen regular connections to this IP.
        """
        # Get all flows to this IP
        flows = [f for f in self.flow_history if f.dest_ip == dest_ip]
        if len(flows) < 3:
            return False
            
        # Check time intervals
        timestamps = sorted([f.timestamp for f in flows])
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        # If intervals are consistent (variance is low), it's a machine heartbeat
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        
        return variance < 1.0 # Very regular
