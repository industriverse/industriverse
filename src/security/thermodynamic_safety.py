import logging
import time
from typing import Dict, List

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ThermoSafety")

class ThermodynamicSafetyLayer:
    """
    Physics-Native Intrusion Detection System (IDS).
    Detects anomalies in energy flow, heat signatures, and entropy gradients.
    """
    def __init__(self, energy_threshold_joules: float = 10000.0, entropy_limit: float = 0.8):
        self.energy_threshold = energy_threshold_joules
        self.entropy_limit = entropy_limit
        self.anomalies = []

    def monitor_energy_flux(self, current_flux_joules: float) -> bool:
        """
        Checks if the current energy flux exceeds safety thresholds.
        Returns True if safe, False if anomaly detected.
        """
        if current_flux_joules > self.energy_threshold:
            logger.warning(f"🚨 ENERGY SPIKE DETECTED: {current_flux_joules}J > {self.energy_threshold}J")
            self._record_anomaly("ENERGY_SPIKE", current_flux_joules)
            return False
        return True

    def monitor_entropy_state(self, current_entropy: float) -> bool:
        """
        Checks if the system entropy is within stable bounds.
        """
        if current_entropy > self.entropy_limit:
            logger.warning(f"🚨 ENTROPY CRITICAL: {current_entropy} > {self.entropy_limit}")
            self._record_anomaly("ENTROPY_CRITICAL", current_entropy)
            return False
        return True

    def detect_intrusion(self, telemetry: Dict[str, float]) -> bool:
        """
        Analyzes a telemetry packet for thermodynamic signatures of intrusion.
        """
        # Example: Sudden heat spike without load increase = Malware/Mining
        cpu_temp = telemetry.get("cpu_temp", 0.0)
        load = telemetry.get("load", 0.0)
        
        if cpu_temp > 80.0 and load < 0.2:
            logger.critical("🛡️ INTRUSION DETECTED: High Heat / Low Load Signature (Potential Crypto-Mining)")
            self._record_anomaly("PHANTOM_HEAT", cpu_temp)
            return True
            
        return False

    def _record_anomaly(self, type: str, value: float):
        self.anomalies.append({
            "type": type,
            "value": value,
            "timestamp": time.time()
        })

    def get_anomalies(self) -> List[Dict]:
        return self.anomalies
