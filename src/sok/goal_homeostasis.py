from dataclasses import dataclass

@dataclass
class DriveStrength:
    survival: float = 1.0
    curiosity: float = 0.5
    expansion: float = 0.2

class GoalHomeostasis:
    """
    The Drive System.
    Manages the Organism's internal motivations and meta-goals.
    """
    
    def __init__(self):
        self.drives = DriveStrength()
        
    def evaluate_needs(self, state):
        """
        Adjusts drives based on current OrganismState.
        """
        # 1. Survival Logic
        if state.energy < 20.0 or state.health < 0.5:
            self.drives.survival = 2.0 # Panic Mode
            print("   ⚠️ [DRIVE] SURVIVAL CRITICAL. Prioritizing Energy.")
        else:
            self.drives.survival = 1.0
            
        # 2. Curiosity Logic (Inverse to Entropy)
        if state.entropy > 0.5:
            self.drives.curiosity = 1.5 # Need to organize/discover
            print("   💡 [DRIVE] High Entropy detected. Increasing Curiosity.")
            
        # 3. Expansion Logic (Resource Abundance)
        if state.energy > 80.0:
            self.drives.expansion = 1.5
            print("   🌱 [DRIVE] Energy Surplus. Ready to Expand.")
            
    def get_dominant_drive(self):
        """
        Returns the currently strongest drive.
        """
        drives = {
            "SURVIVAL": self.drives.survival,
            "CURIOSITY": self.drives.curiosity,
            "EXPANSION": self.drives.expansion
        }
        return max(drives, key=drives.get)

# --- Verification ---
if __name__ == "__main__":
    from src.sok.organism_kernel import OrganismState
    
    gh = GoalHomeostasis()
    
    # Healthy State
    state_healthy = OrganismState(energy=90.0, entropy=0.1)
    gh.evaluate_needs(state_healthy)
    print(f"Dominant Drive: {gh.get_dominant_drive()}")
    
    # Critical State
    state_critical = OrganismState(energy=10.0, entropy=0.8)
    gh.evaluate_needs(state_critical)
    print(f"Dominant Drive: {gh.get_dominant_drive()}")
