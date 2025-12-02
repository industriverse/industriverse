from dataclasses import dataclass
from typing import List, Optional

@dataclass
class MobileTelemetry:
    """
    Standardized Telemetry Schema for the Mobile Defense Suite.
    This tuple represents the 'Thermodynamic State' of a device.
    """
    device_id: str
    timestamp: float
    
    # Physics Metrics
    battery_level: float
    battery_current_ma: float
    battery_temp_c: float
    cpu_usage_percent: float
    
    # Network Metrics
    wifi_tx_bytes: int
    wifi_rx_bytes: int
    mobile_tx_bytes: int
    mobile_rx_bytes: int
    active_connections: int
    
    # Security Metrics
    screen_state: str # "ON", "OFF", "DOZE"
    foreground_app: str
    active_permissions: List[str] # ["CAMERA", "MIC", "LOCATION"]
    wake_lock_count: int
    
    # Identity
    esim_signature: Optional[str] = None # Cryptographic proof of identity
