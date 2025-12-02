import time
import random
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class TelemetryFrame:
    timestamp: float
    battery_current_ma: float
    cpu_load_percent: float
    network_tx_bytes: int
    network_rx_bytes: int
    screen_on: bool
    active_permissions: List[str]
    wake_lock_count: int

@dataclass
class ThreatSignature:
    app_name: str
    risk_score: float
    behavior_vector: List[float]
    evidence_hash: str

class ThermodynamicAgent:
    """
    The On-Device Agent that monitors physics to detect surveillance.
    """
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.baseline_energy = 150.0  # mA (Idle)
        self.suspicion_threshold = 0.8
        self.telemetry_log: List[TelemetryFrame] = []
        
    def capture_telemetry(self) -> TelemetryFrame:
        """
        Simulates capturing hardware telemetry from Android/iOS HAL.
        """
        # In a real app, this would call Android APIs (BatteryManager, TrafficStats)
        # Here we simulate a "Surveillance Scenario" randomly
        is_surveillance_active = random.random() < 0.3
        
        frame = TelemetryFrame(
            timestamp=time.time(),
            battery_current_ma=self.baseline_energy + (random.uniform(200, 500) if is_surveillance_active else random.uniform(0, 50)),
            cpu_load_percent=random.uniform(10, 40) if is_surveillance_active else random.uniform(1, 5),
            network_tx_bytes=random.randint(1000, 50000) if is_surveillance_active else random.randint(0, 100),
            network_rx_bytes=random.randint(0, 1000),
            screen_on=False, # Surveillance happens in the dark
            active_permissions=["CAMERA", "MIC"] if is_surveillance_active else [],
            wake_lock_count=1 if is_surveillance_active else 0
        )
        self.telemetry_log.append(frame)
        return frame

    def analyze_frame(self, frame: TelemetryFrame) -> Optional[ThreatSignature]:
        """
        Analyzes a single frame for thermodynamic anomalies.
        """
        # 1. Energy Anomaly: High current while screen is off
        energy_anomaly = frame.battery_current_ma > (self.baseline_energy * 2) and not frame.screen_on
        
        # 2. Network Anomaly: Uploading data while screen is off
        network_anomaly = frame.network_tx_bytes > 1000 and not frame.screen_on
        
        # 3. Permission Anomaly: Camera/Mic active in background
        perm_anomaly = ("CAMERA" in frame.active_permissions or "MIC" in frame.active_permissions) and not frame.screen_on
        
        if energy_anomaly or network_anomaly or perm_anomaly:
            risk = 0.0
            if energy_anomaly: risk += 0.4
            if network_anomaly: risk += 0.3
            if perm_anomaly: risk += 0.3
            
            # Generate Evidence Hash (ZKP Stub)
            evidence = f"{frame.timestamp}:{frame.battery_current_ma}:{frame.active_permissions}"
            evidence_hash = hashlib.sha256(evidence.encode()).hexdigest()
            
            return ThreatSignature(
                app_name="SuspiciousApp_v1", # In real life, we'd identify the PID
                risk_score=min(risk, 1.0),
                behavior_vector=[frame.battery_current_ma, float(frame.network_tx_bytes), float(len(frame.active_permissions))],
                evidence_hash=evidence_hash
            )
        return None

    def run_cycle(self, duration_sec: int = 10):
        """
        Runs the monitoring loop for a set duration.
        """
        print(f"🕵️‍♂️ [Agent {self.device_id}] Starting Watchdog Cycle...")
        threats = []
        for _ in range(duration_sec):
            frame = self.capture_telemetry()
            threat = self.analyze_frame(frame)
            if threat:
                print(f"🚨 THREAT DETECTED: {threat.app_name} (Risk: {threat.risk_score:.2f})")
                print(f"   - Energy: {frame.battery_current_ma:.1f}mA | Net: {frame.network_tx_bytes}B | Perms: {frame.active_permissions}")
                threats.append(threat)
            else:
                print(f"✅ Normal: {frame.battery_current_ma:.1f}mA (Idle)")
            time.sleep(1)
        return threats

if __name__ == "__main__":
    agent = ThermodynamicAgent(device_id="DEVICE_001")
    agent.run_cycle(5)
