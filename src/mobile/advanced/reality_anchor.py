import hashlib
import time
import random

class RealityAnchor:
    """
    Signs 'Proof of Reality' using local entropy.
    Used to verify that the device is physically present in a specific environment.
    """
    def __init__(self, device_key: str):
        self.device_key = device_key
        
    def capture_local_entropy(self) -> str:
        """
        Simulates sampling local environmental noise (Wi-Fi, Mag, Light).
        """
        # In real app: WifiScanner.getScanResults() + SensorManager.getMagneticField()
        wifi_noise = random.randint(0, 100000)
        mag_field = random.uniform(30.0, 60.0)
        light_lux = random.uniform(0.0, 1000.0)
        
        entropy_string = f"{wifi_noise}:{mag_field}:{light_lux}"
        return hashlib.sha256(entropy_string.encode()).hexdigest()
        
    def sign_reality_proof(self, location_lat_lon: str) -> dict:
        """
        Creates a signed proof linking Location to Local Entropy.
        """
        entropy_hash = self.capture_local_entropy()
        timestamp = time.time()
        
        # The "Proof" binds Time + Location + Entropy
        payload = f"{timestamp}:{location_lat_lon}:{entropy_hash}"
        signature = hashlib.sha256((payload + self.device_key).encode()).hexdigest()
        
        print(f"⚓ [Reality] Signed Proof for {location_lat_lon} at {timestamp}")
        
        return {
            "timestamp": timestamp,
            "location": location_lat_lon,
            "entropy_hash": entropy_hash,
            "signature": signature
        }
