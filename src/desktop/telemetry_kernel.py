import time
import random
from dataclasses import dataclass
from typing import List

@dataclass
class DesktopTelemetry:
    timestamp: float
    cpu_temps: List[float]
    gpu_temp: float
    cpu_power_w: float
    gpu_power_w: float
    disk_io_ops: int
    net_entropy: float

class TelemetryKernel:
    """
    SCDS Pillar I: Thermodynamic Forensics.
    Gathers low-level energy and thermal data from the Desktop OS (Windows/macOS).
    """
    def __init__(self, os_type: str = "macOS"):
        self.os_type = os_type
        
    def poll_sensors(self) -> DesktopTelemetry:
        """
        Simulates reading hardware sensors (SMC on Mac, WMI on Windows).
        """
        # Mock Data Generation
        cpu_temps = [random.uniform(45.0, 75.0) for _ in range(8)] # 8 Cores
        gpu_temp = random.uniform(40.0, 70.0)
        
        cpu_power = sum(cpu_temps) * 0.5 # Rough correlation
        gpu_power = gpu_temp * 1.2
        
        return DesktopTelemetry(
            timestamp=time.time(),
            cpu_temps=cpu_temps,
            gpu_temp=gpu_temp,
            cpu_power_w=cpu_power,
            gpu_power_w=gpu_power,
            disk_io_ops=random.randint(0, 1000),
            net_entropy=random.uniform(0.8, 1.0) # High entropy = Encrypted/Normal
        )

    def detect_thermal_anomaly(self, telemetry: DesktopTelemetry) -> bool:
        """
        Detects 'Hidden Workload': High Heat but Low User Activity (implied).
        """
        avg_cpu = sum(telemetry.cpu_temps) / len(telemetry.cpu_temps)
        if avg_cpu > 70.0 and telemetry.disk_io_ops < 10:
            print(f"🔥 [SCDS] Thermal Anomaly! CPU Hot ({avg_cpu:.1f}C) but Disk Idle.")
            return True
        return False
