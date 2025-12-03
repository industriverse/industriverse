import time
import json
import random
import logging
from typing import Dict, Any

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MobileTelemetryAgent")

class MobileTelemetryAgent:
    """
    The First Pilot: A Mobile Telemetry Agent.
    Captures 'Device Entropy' and 'Energy Signatures' from a mobile device (simulated).
    This data feeds the Energy Atlas.
    """
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.state = {
            "battery_level": 100.0,
            "cpu_temp_c": 35.0,
            "entropy_accumulated": 0.0
        }
        logger.info(f"📱 Mobile Agent Online: {self.device_id}")

    def sense_environment(self) -> Dict[str, Any]:
        """
        Reads sensors (Battery, CPU, GPS, Gyro).
        """
        # Simulate sensor drift and entropy
        load = random.uniform(0.1, 1.0)
        self.state["battery_level"] -= load * 0.01
        self.state["cpu_temp_c"] += (load * 0.5) - 0.2 # Heat up/cool down
        
        # Calculate 'Device Entropy' (Variance in sensor readings)
        entropy = abs(load - 0.5) * 2.0 
        self.state["entropy_accumulated"] += entropy
        
        telemetry = {
            "device_id": self.device_id,
            "timestamp": time.time(),
            "sensors": {
                "battery": self.state["battery_level"],
                "cpu_temp": self.state["cpu_temp_c"],
                "load": load
            },
            "physics_metrics": {
                "thermal_variance": self.state["cpu_temp_c"] - 35.0,
                "entropy_score": entropy
            }
        }
        return telemetry

    def transmit_packet(self, telemetry: Dict[str, Any]):
        """
        Transmits the telemetry packet to the Sovereign Cloud (Mock).
        """
        # In a real scenario, this would POST to an API
        # Here we just log it as a 'Fossil' candidate
        logger.info(f"📡 Transmitting Packet: {telemetry['device_id']} | Temp: {telemetry['sensors']['cpu_temp']:.1f}C | Entropy: {telemetry['physics_metrics']['entropy_score']:.2f}")
        return True

    def run_cycle(self):
        """
        Runs one sensing cycle.
        """
        data = self.sense_environment()
        self.transmit_packet(data)
        return data

if __name__ == "__main__":
    agent = MobileTelemetryAgent(device_id="ANDROID_PILOT_001")
    for _ in range(5):
        agent.run_cycle()
        time.sleep(0.5)
