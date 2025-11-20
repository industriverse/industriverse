"""ModelUnitSearch: Regime Identification and Future Prediction"""
import numpy as np
from typing import List, Tuple
from ..models.model_unit import ModelUnit
from ..models.window import WindowSet
from ..models.regime import RegimeAssignment
from ..core.config import config

class ModelUnitSearch:
    """
    Finds optimal model units and predicts future values.

    Sub-algorithms:
    1. RegimeAssignment: Identify which regime best fits current data
    2. FuturePrediction: Forecast future values using assigned regime
    """

    def __init__(self, top_k: int = None):
        self.top_k = top_k or config.top_k

    def assign_regime(
        self,
        current_window: WindowSet,
        model_units: List[ModelUnit]
    ) -> RegimeAssignment:
        """
        Assign regime based on fitness of model units.

        Returns:
            RegimeAssignment with probabilities and top-K units
        """
        M = len(model_units)

        # Compute fitness vector for all model units
        fitness_vector = np.array([
            self._compute_fitness(current_window, unit)
            for unit in model_units
        ])

        # Find top-K optimal model units
        top_k_indices = np.argsort(fitness_vector)[-self.top_k:][::-1]
        top_k_units = [model_units[i] for i in top_k_indices]

        # Compute regime probabilities using logistic growth model
        regime_probs = self._compute_regime_probabilities(
            fitness_vector,
            top_k_indices
        )

        # Generate regime ID (use best unit's ID)
        best_unit_idx = top_k_indices[0]
        regime_id = model_units[best_unit_idx].unit_id

        # Compute overall confidence
        confidence = float(np.max(regime_probs))

        return RegimeAssignment(
            regime_id=regime_id,
            probabilities=regime_probs,
            top_k_indices=top_k_indices.tolist(),
            model_unit_ids=[unit.unit_id for unit in top_k_units],
            confidence=confidence,
            fitness_scores=fitness_vector
        )

    def forecast(
        self,
        current_window: WindowSet,
        regime_assignment: RegimeAssignment,
        model_units: List[ModelUnit],
        forecast_steps: int = 60
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Forecast future values using assigned regime.

        Returns:
            (predictions, confidence_intervals)
        """
        # Get top-K model units
        top_k_units = [model_units[i] for i in regime_assignment.top_k_indices]

        # Weighted ensemble prediction
        predictions = np.zeros(forecast_steps)

        for i, unit in enumerate(top_k_units):
            weight = regime_assignment.probabilities[i]

            # Predict using this model unit
            unit_predictions = self._predict_forward(
                unit,
                current_window,
                forecast_steps
            )

            predictions += unit_predictions * weight

        # Compute confidence intervals (simplified)
        std_dev = np.std(predictions) * 0.1  # 10% uncertainty
        confidence_intervals = np.array([
            [pred - 1.96 * std_dev, pred + 1.96 * std_dev]
            for pred in predictions
        ])

        return predictions, confidence_intervals

    def _compute_fitness(self, window: WindowSet, unit: ModelUnit) -> float:
        """Compute fitness of model unit for current window"""
        actual_data = window.windows[0].data
        predicted = unit.predict_energy(actual_data)
        mse = np.mean((actual_data - predicted) ** 2)
        return 1.0 / (1.0 + mse)

    def _compute_regime_probabilities(
        self,
        fitness_vector: np.ndarray,
        top_k_indices: np.ndarray
    ) -> np.ndarray:
        """
        Compute regime probabilities using logistic growth model.

        dp(t)/dt = α * p(t) * (f(t) · A - p(t))
        """
        # Simplified: Use softmax of fitness scores
        top_k_fitness = fitness_vector[top_k_indices]

        # Softmax to get probabilities
        exp_fitness = np.exp(top_k_fitness - np.max(top_k_fitness))
        probabilities = exp_fitness / np.sum(exp_fitness)

        return probabilities

    def _predict_forward(
        self,
        unit: ModelUnit,
        current_window: WindowSet,
        steps: int
    ) -> np.ndarray:
        """Predict forward using model unit's differential equations"""
        # Simplified prediction: linear extrapolation
        current_energy = unit.predict_energy(current_window.windows[0].data)
        energy_derivative = unit.predict_energy_derivative(current_window.windows[0].data)

        # Linear prediction: E(t+k) = E(t) + k * dE/dt
        predictions = np.array([
            current_energy + k * energy_derivative
            for k in range(steps)
        ])

        return predictions
