from src.security.immune_system import ImmuneSystem, ServiceHealth
import time

class AutoHealer:
    """
    The Automated Doctor.
    Applies cures to sick services.
    """
    
    def __init__(self, immune_system: ImmuneSystem):
        self.immune = immune_system
        print("   🚑 [HEALER] Auto-Remediation Online.")
        
    def scan_and_heal(self):
        """
        Checks for sick services and applies fixes.
        """
        for svc_id, svc in self.immune.services.items():
            if svc.status == "CRITICAL":
                self.apply_cure(svc, "RESTART")
            elif svc.status == "SICK":
                self.apply_cure(svc, "SCALE_UP")
                
    def apply_cure(self, service: ServiceHealth, action: str):
        print(f"     -> 💉 [CURE] Applying {action} to {service.service_id}...")
        
        # Simulate Cure Effect
        if action == "RESTART":
            time.sleep(0.5) # Reboot time
            service.error_rate = 0.0
            service.cpu_usage = 10.0
            service.status = "HEALTHY"
            print(f"     -> ✅ {service.service_id} Restarted. Vitals Stabilized.")
            
        elif action == "SCALE_UP":
            service.cpu_usage = service.cpu_usage / 2
            service.status = "HEALTHY"
            print(f"     -> ✅ {service.service_id} Scaled Up. Load Reduced.")

# --- Verification ---
if __name__ == "__main__":
    sys = ImmuneSystem()
    healer = AutoHealer(sys)
    
    sys.register_service("DB_Shard_01")
    sys.update_vitals("DB_Shard_01", 99.0, 0.2) # Critical
    
    healer.scan_and_heal()
