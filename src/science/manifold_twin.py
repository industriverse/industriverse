from src.science.physics_capsule import PhysicsCapsule, TensorState
import random

class ManifoldTwin:
    """
    A Digital Twin of a Spacetime Manifold (or Material Surface).
    Manages a network of Physics Capsules.
    """
    
    def __init__(self, dimension_size=10):
        self.capsules = []
        self.time = 0.0
        
        # Initialize a Grid of Capsules
        for x in range(dimension_size):
            for y in range(dimension_size):
                # Random initial energy state
                energy = random.uniform(0, 10)
                cap = PhysicsCapsule(
                    f"CAP_{x}_{y}", 
                    (x, y, 0), 
                    TensorState([energy], 0)
                )
                self.capsules.append(cap)
                
    def step_simulation(self, dt=0.1):
        """
        Advances the manifold time.
        """
        self.time += dt
        
        # Naive O(N^2) interaction for demo (Spatial Partitioning would be used in prod)
        for cap in self.capsules:
            # Find neighbors (simplified: just random sample for demo speed)
            neighbors = random.sample(self.capsules, min(5, len(self.capsules)))
            cap.evolve(neighbors, dt)
            
    def get_total_entropy(self) -> float:
        """
        Calculates the entropy of the manifold state.
        """
        total_energy = sum(c.get_curvature() for c in self.capsules)
        if total_energy == 0: return 0
        
        entropy = 0
        for c in self.capsules:
            p = c.get_curvature() / total_energy
            if p > 0:
                import math
                entropy -= p * math.log(p)
        return entropy

# --- Verification ---
if __name__ == "__main__":
    manifold = ManifoldTwin(dimension_size=5) # 5x5 Grid
    
    print("🕸️ Initializing Manifold Twin...")
    print(f"   Capsules: {len(manifold.capsules)}")
    print(f"   Initial Entropy: {manifold.get_total_entropy():.4f}")
    
    print("\n⏳ Running Simulation Steps...")
    for i in range(3):
        manifold.step_simulation()
        print(f"   Step {i+1}: Entropy = {manifold.get_total_entropy():.4f}")
