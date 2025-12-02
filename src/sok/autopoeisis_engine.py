import random

class AutopoeisisEngine:
    """
    The Immune & Repair System.
    Ensures the Organism maintains structural integrity (Self-Creation/Maintenance).
    """
    
    def scan_and_repair(self, organism):
        """
        Scans the organism for defects and repairs them.
        """
        # 1. Check Vitality
        if organism.state.health < 1.0:
            print("   🚑 [AUTOPOEISIS] Detected Tissue Damage. Initiating Repair...")
            repair_cost = 5.0
            if organism.state.energy >= repair_cost:
                organism.state.energy -= repair_cost
                organism.state.health = min(1.0, organism.state.health + 0.1)
                print("     -> Repair Complete. Health Restored.")
            else:
                print("     -> ❌ Insufficient Energy for Repair.")
                
        # 2. Check Subsystems (Mock Check)
        if not organism.nervous_system:
            print("   🚨 [AUTOPOEISIS] CRITICAL: Nervous System Offline. Attempting Reboot...")
            # In real logic, would re-instantiate the class
            
        # 3. Entropy Management
        if organism.state.entropy > 0.8:
            print("   🧹 [AUTOPOEISIS] High Entropy. Flushing Cache...")
            organism.state.entropy -= 0.2

# --- Verification ---
if __name__ == "__main__":
    from src.sok.organism_kernel import SovereignOrganism
    
    organism = SovereignOrganism()
    auto = AutopoeisisEngine()
    
    # Damage the organism
    organism.state.health = 0.8
    organism.state.energy = 50.0
    
    print("\n--- Before Repair ---")
    print(organism.get_status())
    
    auto.scan_and_repair(organism)
    
    print("\n--- After Repair ---")
    print(organism.get_status())
