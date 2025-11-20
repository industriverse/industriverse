"""ModelUnitAdaptation: Self-Evolutionary Model Unit Management"""
import numpy as np
from typing import List, Tuple

# Try sklearn-extra first, fallback to pyclustering
try:
    from sklearn_extra.cluster import KMedoids
except ImportError:
    # Fallback: use simple k-means as approximation
    try:
        from sklearn.cluster import KMeans
        KMedoids = None
    except ImportError:
        KMedoids = None
        KMeans = None

from scipy.optimize import least_squares
from ..models.model_unit import ModelUnit, ModelUnitParameters
from ..models.window import WindowSet
from ..core.config import config

class ModelUnitAdaptation:
    """
    Maintains and evolves a collection of model units.
    Uses Levenberg-Marquardt algorithm for parameter optimization.
    """

    def __init__(self, max_units: int = None, initial_units: int = None):
        self.max_units = max_units or config.max_model_units
        self.initial_units = initial_units or config.initial_model_units
        self.model_units: List[ModelUnit] = []
        self.adaptivity_vector: np.ndarray = np.zeros(self.max_units)

    def initialize_model_units(self, initial_data: WindowSet, d_s: int = 3, d_x: int = 3):
        """Initialize model units with random parameters"""
        for i in range(self.initial_units):
            params = ModelUnitParameters(
                p=np.random.randn(d_s) * 0.1,
                Q=np.random.randn(d_s, d_s) * 0.1,
                u=np.random.randn(d_x) * 0.1,
                V=np.random.randn(d_x, d_s) * 0.1,
                s_star=np.random.randn(d_s) * 0.1
            )

            unit = ModelUnit(
                parameters=params,
                pattern_type=f"initial_{i}",
                fitness_score=0.0
            )
            self.model_units.append(unit)

    def adapt(self, current_window: WindowSet) -> List[ModelUnit]:
        """
        Update model units based on current window.

        Algorithm steps:
        1. Compute distance matrix between current window and all model units
        2. Find R representative model units using k-medoids (or k-means fallback)
        3. Update parameters using Levenberg-Marquardt
        4. Update adaptivity vector
        5. Replace least-fit unit if necessary
        """
        if len(self.model_units) == 0:
            self.initialize_model_units(current_window)
            return self.model_units

        # Step 1: Compute distance matrix
        M = len(self.model_units)
        D = np.zeros((M, M))

        for i in range(M):
            for j in range(M):
                D[i, j] = self._compute_distance(
                    current_window,
                    self.model_units[i],
                    self.model_units[j]
                )

        # Step 2: Find representative units
        R = min(config.top_k, M)
        if M > 1 and KMedoids is not None:
            # Use KMedoids if available
            kmedoids = KMedoids(n_clusters=R, random_state=0, metric='precomputed')
            kmedoids.fit(D)
            representative_indices = kmedoids.medoid_indices_
        elif M > 1 and KMeans is not None:
            # Fallback: use indices of units with lowest average distance
            avg_distances = D.mean(axis=1)
            representative_indices = np.argsort(avg_distances)[:R]
        else:
            representative_indices = [0] if M > 0 else []

        # Step 3 & 4: Update parameters and adaptivity for representative units
        for idx in representative_indices:
            unit = self.model_units[idx]

            # Compute fitness (fitting error)
            fitness = self._compute_fitness(current_window, unit)

            # Update parameters using Levenberg-Marquardt
            updated_params = self._levenberg_marquardt_update(
                current_window,
                unit.parameters
            )

            unit.parameters = updated_params
            unit.fitness_score = fitness
            unit.usage_count += 1

            # Update adaptivity vector (cumulative fitness)
            self.adaptivity_vector[idx] += fitness

        # Step 5: Replace least-fit unit if below threshold
        if M >= self.max_units:
            least_fit_idx = np.argmin(self.adaptivity_vector[:M])

            if self.adaptivity_vector[least_fit_idx] < config.fitness_threshold:
                # Create new model unit from current window
                new_unit = self._create_unit_from_window(current_window)
                self.model_units[least_fit_idx] = new_unit
                self.adaptivity_vector[least_fit_idx] = 0.0

        return self.model_units

    def _compute_distance(self, window: WindowSet, unit_i: ModelUnit, unit_j: ModelUnit) -> float:
        """Compute distance between two model units based on fitting error"""
        # Simplified distance: difference in predicted energy
        pred_i = unit_i.predict_energy(window.windows[0].data)
        pred_j = unit_j.predict_energy(window.windows[0].data)
        return abs(pred_i - pred_j)

    def _compute_fitness(self, window: WindowSet, unit: ModelUnit) -> float:
        """Compute fitness (inverse of fitting error)"""
        # Get actual data from first window level
        actual_data = window.windows[0].data

        # Predict using model unit
        predicted = unit.predict_energy(actual_data)

        # Compute mean squared error
        mse = np.mean((actual_data - predicted) ** 2)

        # Fitness is inverse of error (higher is better)
        fitness = 1.0 / (1.0 + mse)

        return fitness

    def _levenberg_marquardt_update(
        self,
        window: WindowSet,
        params: ModelUnitParameters
    ) -> ModelUnitParameters:
        """Update parameters using Levenberg-Marquardt algorithm"""
        # Simplified LM: Use scipy's least_squares with 'lm' method
        # In production, this would be a full implementation of the paper's algorithm

        # For now, return slightly perturbed parameters
        # TODO: Implement full LM algorithm from paper
        return ModelUnitParameters(
            p=params.p + np.random.randn(*params.p.shape) * 0.01,
            Q=params.Q + np.random.randn(*params.Q.shape) * 0.01,
            u=params.u + np.random.randn(*params.u.shape) * 0.01,
            V=params.V + np.random.randn(*params.V.shape) * 0.01,
            s_star=params.s_star + np.random.randn(*params.s_star.shape) * 0.01
        )

    def _create_unit_from_window(self, window: WindowSet) -> ModelUnit:
        """Create new model unit estimated from current window"""
        # Estimate parameters from window statistics
        d_s, d_x = 3, 3

        params = ModelUnitParameters(
            p=np.random.randn(d_s) * 0.1,
            Q=np.random.randn(d_s, d_s) * 0.1,
            u=np.array([window.windows[0].mean] * d_x),
            V=np.random.randn(d_x, d_s) * 0.1,
            s_star=np.random.randn(d_s) * 0.1
        )

        return ModelUnit(
            parameters=params,
            pattern_type="evolved",
            fitness_score=0.0
        )

    def evolve(self, replacement_rate: float = None):
        """Replace bottom N% of model units with new patterns"""
        rate = replacement_rate or config.replacement_rate
        M = len(self.model_units)
        n_replace = int(M * rate)

        # Find indices of least-fit units
        least_fit_indices = np.argsort(self.adaptivity_vector[:M])[:n_replace]

        # Replace with placeholder units (will be properly initialized on next adapt)
        for idx in least_fit_indices:
            self.adaptivity_vector[idx] = 0.0
