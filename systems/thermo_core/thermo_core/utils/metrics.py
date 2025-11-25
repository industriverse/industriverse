import numpy as np

def deltaE(energy_trace: np.ndarray):
    return float(np.sum(energy_trace))

def entropy_from_field(field: np.ndarray):
    # simple Shannon-style on normalized power spectrum (placeholder)
    p = np.abs(np.fft.rfft(field.ravel()))**2
    p = p / (p.sum() + 1e-12)
    return float(-np.sum(p * np.log(p + 1e-12)))
