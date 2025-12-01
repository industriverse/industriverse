import numpy as np
from typing import List, Dict

class HilbertMetrics:
    """
    Advanced Metrics using Hilbert Space concepts.
    Maps system states to vectors to measure evolutionary distance and orthogonality.
    """
    
    def state_to_vector(self, state: Dict[str, float]) -> np.ndarray:
        """
        Converts a state dictionary (metrics) to a normalized vector in Hilbert Space.
        Expected keys: 'roi', 'latency', 'stability', 'entropy', 'complexity'
        """
        # Define standard basis
        keys = ['roi', 'latency', 'stability', 'entropy', 'complexity']
        vector = np.array([state.get(k, 0.0) for k in keys])
        
        # Normalize (L2 norm)
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def calculate_evolutionary_distance(self, state_a: Dict[str, float], state_b: Dict[str, float]) -> float:
        """
        Calculates the Euclidean distance between two normalized state vectors.
        """
        v_a = self.state_to_vector(state_a)
        v_b = self.state_to_vector(state_b)
        return float(np.linalg.norm(v_a - v_b))

    def calculate_orthogonality(self, state_a: Dict[str, float], state_b: Dict[str, float]) -> float:
        """
        Calculates the 'Angle of Evolution' (Cosine Similarity).
        0.0 = Orthogonal (Completely new direction/capability)
        1.0 = Parallel (Optimization of existing direction)
        -1.0 = Opposite (Regression)
        """
        v_a = self.state_to_vector(state_a)
        v_b = self.state_to_vector(state_b)
        
        # Dot product of normalized vectors is cosine similarity
        return float(np.dot(v_a, v_b))

    def analyze_evolution(self, baseline: Dict[str, float], new_state: Dict[str, float]):
        """
        Full analysis of a change.
        """
        dist = self.calculate_evolutionary_distance(baseline, new_state)
        angle = self.calculate_orthogonality(baseline, new_state)
        
        # Interpretation
        interpretation = "Optimization"
        if angle < 0.7:
            interpretation = "Structural Shift (Innovation)"
        if angle < 0.1:
            interpretation = "Orthogonal Breakthrough"
            
        return {
            "distance": dist,
            "orthogonality": angle,
            "interpretation": interpretation
        }

if __name__ == "__main__":
    # Test
    hm = HilbertMetrics()
    
    # Baseline State
    s1 = {'roi': 1.0, 'latency': 0.5, 'stability': 0.9, 'entropy': 0.2, 'complexity': 0.5}
    
    # Optimization (Better ROI, same structure)
    s2 = {'roi': 1.2, 'latency': 0.4, 'stability': 0.9, 'entropy': 0.2, 'complexity': 0.5}
    
    # Innovation (Higher Complexity, Higher Entropy, New Capability)
    s3 = {'roi': 1.5, 'latency': 0.6, 'stability': 0.8, 'entropy': 0.8, 'complexity': 0.9}
    
    print("Optimization:", hm.analyze_evolution(s1, s2))
    print("Innovation:", hm.analyze_evolution(s1, s3))
