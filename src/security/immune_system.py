from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time

@dataclass
class ServiceHealth:
    service_id: str
    status: str # HEALTHY, SICK, CRITICAL
    cpu_usage: float
    error_rate: float
    last_check: float

class ImmuneSystem:
    """
    The Organism's Defense Mechanism.
    Monitors services and flags anomalies.
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        print("   🛡️ [IMMUNE] System Active. Monitoring Vitals...")
        
    def register_service(self, service_id: str):
        self.services[service_id] = ServiceHealth(
            service_id=service_id,
            status="HEALTHY",
            cpu_usage=0.0,
            error_rate=0.0,
            last_check=time.time()
        )
        
    def update_vitals(self, service_id: str, cpu: float, error_rate: float):
        if service_id in self.services:
            svc = self.services[service_id]
            svc.cpu_usage = cpu
            svc.error_rate = error_rate
            svc.last_check = time.time()
            
            # Diagnosis Logic
            if error_rate > 0.05: # 5% Error Rate
                svc.status = "CRITICAL"
                print(f"     -> 🚨 [ALERT] {service_id} is CRITICAL (Error Rate: {error_rate:.1%})")
            elif cpu > 80.0:
                svc.status = "SICK"
                print(f"     -> ⚠️ [WARN] {service_id} is SICK (CPU: {cpu:.1f}%)")
            else:
                if svc.status != "HEALTHY":
                    print(f"     -> ✅ [RECOVERY] {service_id} is HEALTHY again.")
                svc.status = "HEALTHY"

# --- Verification ---
if __name__ == "__main__":
    immune = ImmuneSystem()
    immune.register_service("AuthService")
    immune.update_vitals("AuthService", 10.0, 0.0) # Healthy
    immune.update_vitals("AuthService", 90.0, 0.0) # Sick
    immune.update_vitals("AuthService", 95.0, 0.1) # Critical
