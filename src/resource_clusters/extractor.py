import numpy as np
from scipy.stats import entropy

class FeatureExtractor:
    """
    Extracts thermodynamic features from raw telemetry.
    """
    def extract_features(self, telemetry_window: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Computes Entropy, Gradient, and Stability from a window of data.
        """
        if not telemetry_window:
            return {}

        # 1. Extract raw arrays
        temps = [d.get('temperature', 0) for d in telemetry_window]
        vibs = [d.get('vibration', 0) for d in telemetry_window]
        
        # 2. Compute Shannon Entropy (of the distribution of values)
        # Normalize to probability distribution
        temp_dist = self._to_distribution(temps)
        h_temp = entropy(temp_dist) if len(temp_dist) > 0 else 0.0
        
        # 3. Compute Gradient (Rate of Change)
        grad_temp = np.mean(np.abs(np.gradient(temps))) if len(temps) > 1 else 0.0
        
        # 4. Compute Stability (Inverse of Variance)
        var_temp = np.var(temps) if len(temps) > 0 else 1.0
        stability = 1.0 / (1.0 + var_temp) # Normalized 0-1
        
        # 5. Compute Spectral Energy (FFT) - Deep Feature
        # Detects periodic anomalies (vibration/oscillation)
        spectral_energy = 0.0
        if len(vibs) > 1:
            fft_vals = np.fft.fft(vibs)
            # Sum of magnitudes of non-DC components
            spectral_energy = np.sum(np.abs(fft_vals[1:])) / len(vibs)
        
        return {
            "entropy": float(h_temp),
            "gradient": float(grad_temp),
            "stability": float(stability),
            "avg_temp": float(np.mean(temps)) if temps else 0.0,
            "avg_vib": float(np.mean(vibs)) if vibs else 0.0,
            "spectral_energy": float(spectral_energy)
        }

    def _to_distribution(self, values, bins=10):
        if not values:
            return []
        hist, _ = np.histogram(values, bins=bins, density=True)
        return hist
