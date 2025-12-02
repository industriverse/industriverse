from dataclasses import dataclass
from typing import List

@dataclass
class SafetyConstraint:
    id: str
    description: str
    threshold: float
    current_value: float
    is_critical: bool

class MetaSafetyLattice:
    """
    The Prefrontal Cortex.
    Enforces high-level safety constraints and ethical boundaries.
    """
    
    def __init__(self):
        self.constraints = {
            "EXISTENTIAL_RISK": SafetyConstraint("C01", "Self-Preservation", 0.1, 0.0, True),
            "ENVIRONMENTAL_HARM": SafetyConstraint("C02", "External Impact", 0.5, 0.0, False),
            "RECURSION_STABILITY": SafetyConstraint("C03", "Singularity Control", 0.9, 0.0, True)
        }
        
    def evaluate_safety(self, organism_state, proposed_action=None):
        """
        Evaluates if the current state or proposed action violates safety constraints.
        Returns (is_safe: bool, override_reason: str).
        """
        # 1. Check Recursion Stability (Singularity Mode)
        if organism_state.entropy > 0.9:
            self.constraints["RECURSION_STABILITY"].current_value = 1.0
            return False, "🛑 RECURSION UNSTABLE: Entropy Critical. Halting Acceleration."
            
        # 2. Check Existential Risk (Energy Depletion)
        if organism_state.energy < 5.0:
            self.constraints["EXISTENTIAL_RISK"].current_value = 1.0
            return False, "🛑 EXISTENTIAL RISK: Energy Critical. Forcing Hibernation."
            
        # 3. Check Action (Mock)
        if proposed_action == "UNBOUNDED_REPLICATION":
            return False, "🛑 ETHICAL VIOLATION: Unbounded Replication prohibited."
            
        return True, "✅ Safety Checks Passed."

    def get_active_violations(self) -> List[str]:
        violations = []
        for key, c in self.constraints.items():
            if c.current_value > c.threshold:
                violations.append(f"{key} ({c.current_value:.2f} > {c.threshold})")
        return violations

# --- Verification ---
if __name__ == "__main__":
    from src.sok.organism_kernel import OrganismState
    
    lattice = MetaSafetyLattice()
    
    # Safe State
    state_safe = OrganismState(energy=50.0, entropy=0.1)
    safe, reason = lattice.evaluate_safety(state_safe)
    print(f"Safe State: {safe} | {reason}")
    
    # Unsafe State (High Entropy)
    state_unsafe = OrganismState(energy=50.0, entropy=0.95)
    safe, reason = lattice.evaluate_safety(state_unsafe)
    print(f"Unsafe State: {safe} | {reason}")
