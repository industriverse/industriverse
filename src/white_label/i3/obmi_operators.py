"""
OBMI Operators - Thermodynamic Knowledge Operations

Five core operators for I³ (Industrial Internet of Intelligence) that enable
thermodynamic reasoning over knowledge graphs:

1. AESP - Ambient Energy-Space Projection
2. QERO - Quantum Entanglement Resonance Operator
3. PRIN - Physics-Resolved Information Navigator
4. AIEO - AI Evolution Operator
5. AROE - Adaptive Reality Optimization Engine

These operators transform and navigate the 6D embedding space using
thermodynamic principles.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class OBMIResult:
    """Result from OBMI operator"""
    operator_name: str
    input_embeddings: List[str]  # IDs of input embeddings
    output_embedding: np.ndarray
    thermodynamic_energy: float
    entropy_change: float
    metadata: Dict[str, Any]


class AESPOperator:
    """
    Ambient Energy-Space Projection (AESP)

    Projects knowledge embeddings into ambient energy-space where
    thermodynamic potential reveals hidden relationships.

    Use case: Finding latent connections between seemingly unrelated research
    """

    def __init__(self):
        self.name = "AESP"

    def project(
        self,
        embeddings: List[np.ndarray],
        temperature: float = 1.0
    ) -> Tuple[np.ndarray, float]:
        """
        Project embeddings into energy-space

        Args:
            embeddings: List of 6D embedding vectors
            temperature: Thermodynamic temperature (controls projection strength)

        Returns:
            (projected_embedding, energy)
        """
        if not embeddings:
            return np.zeros(896), 0.0  # 6D embedding size

        # Stack embeddings
        stacked = np.stack(embeddings)

        # Compute energy-weighted average
        # Higher energy embeddings have more influence
        energies = np.array([self._compute_energy(emb) for emb in embeddings])
        weights = np.exp(energies / temperature)
        weights /= weights.sum()

        # Weighted projection
        projected = np.average(stacked, axis=0, weights=weights)

        # Compute projection energy
        total_energy = np.sum(energies * weights)

        return projected, total_energy

    def _compute_energy(self, embedding: np.ndarray) -> float:
        """Compute thermodynamic energy of embedding"""
        # Use L2 norm as energy proxy
        return np.linalg.norm(embedding)

    def find_ambient_connections(
        self,
        query_embedding: np.ndarray,
        corpus_embeddings: List[Tuple[str, np.ndarray]],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find connections in ambient energy-space

        Returns documents with similar thermodynamic potential
        """
        query_energy = self._compute_energy(query_embedding)

        # Compute energy similarity
        similarities = []
        for doc_id, emb in corpus_embeddings:
            emb_energy = self._compute_energy(emb)

            # Thermodynamic similarity (energy + direction)
            cosine_sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb) + 1e-10
            )

            energy_sim = 1.0 - abs(query_energy - emb_energy) / max(query_energy, emb_energy, 1.0)

            # Combined thermodynamic similarity
            thermo_sim = 0.7 * cosine_sim + 0.3 * energy_sim

            similarities.append((doc_id, thermo_sim))

        # Sort and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


class QEROOperator:
    """
    Quantum Entanglement Resonance Operator (QERO)

    Identifies quantum-like entanglement patterns in knowledge embeddings
    where concepts are non-locally correlated.

    Use case: Discovering non-obvious interdependencies in research domains
    """

    def __init__(self):
        self.name = "QERO"

    def compute_entanglement(
        self,
        embedding_a: np.ndarray,
        embedding_b: np.ndarray
    ) -> float:
        """
        Compute entanglement measure between embeddings

        Based on quantum mutual information analogy
        """
        # Normalize embeddings
        a_norm = embedding_a / (np.linalg.norm(embedding_a) + 1e-10)
        b_norm = embedding_b / (np.linalg.norm(embedding_b) + 1e-10)

        # Compute "entanglement entropy"
        # High entanglement = strong correlation
        correlation = np.abs(np.dot(a_norm, b_norm))

        # Entanglement measure (0 to 1)
        entanglement = correlation ** 2

        return float(entanglement)

    def find_entangled_clusters(
        self,
        embeddings: List[Tuple[str, np.ndarray]],
        threshold: float = 0.7
    ) -> List[List[str]]:
        """
        Find clusters of highly entangled concepts

        Args:
            embeddings: List of (id, embedding) tuples
            threshold: Minimum entanglement for cluster membership

        Returns:
            List of clusters (each cluster is list of IDs)
        """
        clusters = []
        visited = set()

        for i, (id_a, emb_a) in enumerate(embeddings):
            if id_a in visited:
                continue

            # Start new cluster
            cluster = [id_a]
            visited.add(id_a)

            # Find all entangled partners
            for id_b, emb_b in embeddings[i+1:]:
                if id_b in visited:
                    continue

                entanglement = self.compute_entanglement(emb_a, emb_b)

                if entanglement >= threshold:
                    cluster.append(id_b)
                    visited.add(id_b)

            if len(cluster) > 1:
                clusters.append(cluster)

        return clusters


class PRINOperator:
    """
    Physics-Resolved Information Navigator (PRIN)

    Navigates knowledge graphs using physics-informed pathfinding where
    paths minimize action (energy × time) analogous to Lagrangian mechanics.

    Use case: Finding optimal research paths between concepts
    """

    def __init__(self):
        self.name = "PRIN"

    def find_minimum_action_path(
        self,
        start_id: str,
        end_id: str,
        knowledge_graph: Dict[str, Any],
        embeddings: Dict[str, np.ndarray]
    ) -> Tuple[List[str], float]:
        """
        Find minimum-action path using physics principles

        Action = Σ(energy × distance) along path
        """
        # A* search with thermodynamic cost
        from heapq import heappush, heappop

        # Priority queue: (cost, current_id, path)
        queue = [(0.0, start_id, [start_id])]
        visited = {start_id: 0.0}

        while queue:
            cost, current_id, path = heappop(queue)

            if current_id == end_id:
                return path, cost

            # Explore neighbors
            if current_id in knowledge_graph:
                neighbors = knowledge_graph[current_id]

                for neighbor_id in neighbors:
                    if neighbor_id not in embeddings:
                        continue

                    # Compute action cost
                    edge_cost = self._compute_action(
                        embeddings[current_id],
                        embeddings[neighbor_id]
                    )

                    new_cost = cost + edge_cost

                    # Update if better path found
                    if neighbor_id not in visited or new_cost < visited[neighbor_id]:
                        visited[neighbor_id] = new_cost
                        heappush(queue, (new_cost, neighbor_id, path + [neighbor_id]))

        return [], float('inf')  # No path found

    def _compute_action(self, emb_a: np.ndarray, emb_b: np.ndarray) -> float:
        """
        Compute action integral between embeddings

        Action = Energy × Distance
        """
        # Energy: average of embedding norms
        energy_a = np.linalg.norm(emb_a)
        energy_b = np.linalg.norm(emb_b)
        avg_energy = (energy_a + energy_b) / 2.0

        # Distance: Euclidean distance
        distance = np.linalg.norm(emb_a - emb_b)

        # Action
        action = avg_energy * distance

        return action


class AIEOOperator:
    """
    AI Evolution Operator (AIEO)

    Evolves embeddings over time using genetic algorithm inspired by
    thermodynamic evolution (variation + selection under energy constraints).

    Use case: Predicting future research directions
    """

    def __init__(self, mutation_rate: float = 0.1):
        self.name = "AIEO"
        self.mutation_rate = mutation_rate

    def evolve_embedding(
        self,
        embedding: np.ndarray,
        fitness_function: Any,
        generations: int = 10
    ) -> np.ndarray:
        """
        Evolve embedding using thermodynamic evolution

        Args:
            embedding: Initial embedding
            fitness_function: Function that scores embedding quality
            generations: Number of evolution iterations

        Returns:
            Evolved embedding
        """
        current = embedding.copy()
        current_fitness = fitness_function(current)

        for gen in range(generations):
            # Mutate
            mutated = self._mutate(current)

            # Evaluate
            mutated_fitness = fitness_function(mutated)

            # Selection (Boltzmann selection)
            temp = 1.0 / (gen + 1)  # Temperature decreases over time
            delta_fitness = mutated_fitness - current_fitness

            # Accept if better, or probabilistically if worse
            if delta_fitness > 0 or np.random.rand() < np.exp(delta_fitness / temp):
                current = mutated
                current_fitness = mutated_fitness

        return current

    def _mutate(self, embedding: np.ndarray) -> np.ndarray:
        """Apply thermodynamic mutation"""
        mutated = embedding.copy()

        # Random perturbations
        mask = np.random.rand(len(embedding)) < self.mutation_rate
        perturbations = np.random.randn(len(embedding)) * 0.1

        mutated[mask] += perturbations[mask]

        return mutated

    def predict_trend(
        self,
        historical_embeddings: List[np.ndarray],
        steps_ahead: int = 1
    ) -> np.ndarray:
        """
        Predict future embedding based on historical trajectory

        Uses linear extrapolation with thermodynamic damping
        """
        if len(historical_embeddings) < 2:
            return historical_embeddings[-1] if historical_embeddings else np.zeros(896)

        # Compute velocity (change over time)
        recent = np.array(historical_embeddings[-5:])  # Last 5 timesteps
        velocities = np.diff(recent, axis=0)

        # Average velocity with decay
        avg_velocity = np.mean(velocities, axis=0)

        # Damping factor (thermodynamic cooling)
        damping = 0.95 ** steps_ahead

        # Predict
        predicted = historical_embeddings[-1] + avg_velocity * steps_ahead * damping

        return predicted


class AROEOperator:
    """
    Adaptive Reality Optimization Engine (AROE)

    Optimizes knowledge embeddings to maximize coherence with observed reality
    (experimental data, simulation results, validated insights).

    Use case: Refining embeddings based on validation feedback
    """

    def __init__(self, learning_rate: float = 0.01):
        self.name = "AROE"
        self.learning_rate = learning_rate

    def optimize_embedding(
        self,
        embedding: np.ndarray,
        ground_truth: Dict[str, Any],
        iterations: int = 100
    ) -> np.ndarray:
        """
        Optimize embedding to match ground truth

        Uses gradient descent with thermodynamic regularization
        """
        optimized = embedding.copy()

        for _ in range(iterations):
            # Compute loss (distance from ground truth)
            loss = self._compute_loss(optimized, ground_truth)

            # Compute gradient (numerical)
            gradient = self._compute_gradient(optimized, ground_truth)

            # Update with regularization
            update = self.learning_rate * gradient

            # Thermodynamic regularization (limit energy growth)
            energy = np.linalg.norm(optimized)
            if energy > 100.0:  # Energy threshold
                regularization = 0.01 * optimized
                update -= regularization

            optimized -= update

        return optimized

    def _compute_loss(self, embedding: np.ndarray, ground_truth: Dict[str, Any]) -> float:
        """Compute loss against ground truth"""
        # Mock implementation - would use actual validation data
        target_energy = ground_truth.get('target_energy', 50.0)
        current_energy = np.linalg.norm(embedding)

        loss = (current_energy - target_energy) ** 2

        return loss

    def _compute_gradient(self, embedding: np.ndarray, ground_truth: Dict[str, Any]) -> np.ndarray:
        """Compute gradient of loss"""
        epsilon = 1e-5
        gradient = np.zeros_like(embedding)

        base_loss = self._compute_loss(embedding, ground_truth)

        # Numerical gradient
        for i in range(min(len(embedding), 100)):  # Approximate for efficiency
            perturbed = embedding.copy()
            perturbed[i] += epsilon

            perturbed_loss = self._compute_loss(perturbed, ground_truth)

            gradient[i] = (perturbed_loss - base_loss) / epsilon

        return gradient


class OBMIOrchestrator:
    """
    Orchestrator for all OBMI operators

    Coordinates the five operators to perform complex knowledge operations
    """

    def __init__(self):
        self.aesp = AESPOperator()
        self.qero = QEROOperator()
        self.prin = PRINOperator()
        self.aieo = AIEOOperator()
        self.aroe = AROEOperator()

    def analyze_research_landscape(
        self,
        paper_embeddings: List[Tuple[str, np.ndarray]]
    ) -> Dict[str, Any]:
        """
        Comprehensive research landscape analysis using all operators

        Returns:
            Analysis results with clusters, paths, predictions
        """
        # 1. QERO: Find entangled clusters
        clusters = self.qero.find_entangled_clusters(paper_embeddings, threshold=0.7)

        # 2. AESP: Identify ambient connections
        if paper_embeddings:
            query_emb = paper_embeddings[0][1]
            ambient_connections = self.aesp.find_ambient_connections(
                query_emb, paper_embeddings, top_k=10
            )
        else:
            ambient_connections = []

        # 3. AIEO: Predict future trends
        if len(paper_embeddings) >= 5:
            historical = [emb for _, emb in paper_embeddings[-10:]]
            trend_prediction = self.aieo.predict_trend(historical, steps_ahead=3)
        else:
            trend_prediction = None

        return {
            'clusters': clusters,
            'cluster_count': len(clusters),
            'ambient_connections': ambient_connections,
            'trend_prediction': trend_prediction.tolist() if trend_prediction is not None else None,
            'operators_used': ['QERO', 'AESP', 'AIEO']
        }


# Global OBMI orchestrator
_obmi: Optional[OBMIOrchestrator] = None


def get_obmi_orchestrator() -> OBMIOrchestrator:
    """Get or create global OBMI orchestrator"""
    global _obmi
    if _obmi is None:
        _obmi = OBMIOrchestrator()
    return _obmi
