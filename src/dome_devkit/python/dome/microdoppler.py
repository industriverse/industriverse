import logging
import numpy as np

logger = logging.getLogger(__name__)

class MicroDopplerExtractor:
    """
    Extracts Micro-Doppler features from STFT spectrograms.
    """
    def __init__(self):
        logger.info("MicroDopplerExtractor initialized")

    def extract(self, spectrogram: np.ndarray) -> np.ndarray:
        """
        Extract features (e.g., torso, limb velocity).
        """
        # Mock feature extraction
        # Returns [velocity_mean, velocity_std, energy, entropy, ...]
        return np.random.rand(8)
