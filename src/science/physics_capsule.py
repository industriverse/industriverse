import random
import math
from dataclasses import dataclass
from typing import List

@dataclass
class TensorState:
    """Represents a local field value (Scalar, Vector, or Tensor)."""
    components: List[float]
    rank: int # 0=Scalar, 1=Vector, 2=Tensor

class PhysicsCapsule:
    """
    A 'Smart Particle' or 'Field Patch' in the LithOS simulation.
    It obeys local laws of physics but can be 'programmed' via simulation forks.
    """
    
    def __init__(self, capsule_id: str, position: tuple, initial_state: TensorState):
        self.id = capsule_id
        self.position = list(position)
        self.state = initial_state
        self.history = []
        
    def evolve(self, neighbors: List['PhysicsCapsule'], dt: float):
        """
        Evolves the capsule's state based on local interactions (Geometrodynamics).
        """
        # 1. Calculate Field Gradient (simplified)
        gradient = [0.0] * len(self.state.components)
        for neighbor in neighbors:
            dist = math.sqrt(sum((p1-p2)**2 for p1, p2 in zip(self.position, neighbor.position)))
            if dist == 0: continue
            
            # Interaction Strength (Inverse Square Law + Quantum Noise)
            strength = 1.0 / (dist ** 2)
            noise = random.gauss(0, 0.01) # Quantum Fluctuations
            
            for i in range(len(self.state.components)):
                # Simple diffusion/attraction logic
                delta = (neighbor.state.components[i] - self.state.components[i]) * strength
                gradient[i] += delta + noise
                
        # 2. Update State (Time Evolution)
        for i in range(len(self.state.components)):
            self.state.components[i] += gradient[i] * dt
            
        # 3. Log History (Trust Trail)
        self.history.append((self.state.components[:], dt))

    def get_curvature(self) -> float:
        """
        Returns a scalar metric of local 'curvature' or 'energy density'.
        """
        return sum(x**2 for x in self.state.components)

# --- Verification ---
if __name__ == "__main__":
    # Create two interacting capsules (e.g., Binary Star System or QFT Excitations)
    c1 = PhysicsCapsule("CAP_A", (0, 0, 0), TensorState([10.0], 0))
    c2 = PhysicsCapsule("CAP_B", (1, 0, 0), TensorState([5.0], 0))
    
    print("🌌 Evolving Physics Capsules...")
    for t in range(5):
        c1.evolve([c2], 0.1)
        c2.evolve([c1], 0.1)
        print(f"   T={t}: Cap_A={c1.state.components[0]:.2f}, Cap_B={c2.state.components[0]:.2f}")
