import time
from dataclasses import dataclass, field
from typing import Dict, List

# Mocking Subsystems for the Kernel
from src.orchestration.daemon_gears import OrchestrationLevelManager
from src.science.lithos_kernel import LithOSKernel

@dataclass
class OrganismState:
    health: float = 1.0
    energy: float = 100.0
    entropy: float = 0.0
    age_cycles: int = 0
    consciousness_level: float = 0.1 # Emerging self-awareness

from src.safety.meta_safety_lattice import MetaSafetyLattice
from src.unification.narrative_physics_engine import NarrativePhysicsEngine

class SovereignOrganism:
    """
    The Sovereign Organism Kernel (SOK).
    The central entity that orchestrates all subsystems as a unified biological entity.
    """
    
    def __init__(self, name="Industriverse_Prime"):
        self.name = name
        self.state = OrganismState()
        
        # Organs (Subsystems)
        print(f"🧬 [SOK] Birthing Organism: {self.name}...")
        self.nervous_system = OrchestrationLevelManager() # The Daemon
        self.cortex = LithOSKernel() # The Brain
        self.drives = None # GoalHomeostasis (To be injected)
        self.immune_system = None # Autopoeisis (To be injected)
        
        # Cognitive Cortex (New)
        self.safety = MetaSafetyLattice() # Prefrontal Cortex
        self.narrative = NarrativePhysicsEngine() # Hippocampus
        
        print("   - Nervous System: ONLINE")
        print("   - Cortex: ONLINE")
        print("   - Safety Lattice: ONLINE")
        print("   - Narrative Engine: ONLINE")
        
    def pulse(self):
        """
        The Heartbeat of the Organism.
        Executes one metabolic cycle.
        """
        self.state.age_cycles += 1
        print(f"\n💓 [SOK] Pulse {self.state.age_cycles} | Health: {self.state.health:.2f} | Energy: {self.state.energy:.2f}")
        
        # 0. Narrative Update (Perceive World)
        # Mocking a signal ingestion for the pulse
        self.narrative.ingest_signal("INTERNAL", self.state.energy, "Metabolic Check")
        
        # 1. Check Safety (Prefrontal Cortex)
        is_safe, reason = self.safety.evaluate_safety(self.state)
        if not is_safe:
            print(f"   🛡️ [SAFETY] {reason}")
            # In a real loop, this would trigger a fallback state
            
        # 2. Check Homeostasis (Drives)
        if self.drives:
            self.drives.evaluate_needs(self.state)
            
        # 3. Check Integrity (Immune System)
        if self.immune_system:
            self.immune_system.scan_and_repair(self)
            
        # 4. Metabolic Cost
        self.state.energy -= 0.1
        self.state.entropy += 0.01

    def get_status(self):
        return {
            "name": self.name,
            "age": self.state.age_cycles,
            "vitality": self.state.health,
            "mode": self.nervous_system.current_level.name
        }

# --- Verification ---
if __name__ == "__main__":
    organism = SovereignOrganism()
    organism.pulse()
    organism.pulse()
    print(organism.get_status())
