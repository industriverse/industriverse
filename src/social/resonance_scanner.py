import numpy as np

class ResonanceScanner:
    """
    SPI Module 8: Resonance & Social Proof Scanner (RSPS).
    Detects 'Fake Virality' via spectral analysis.
    Organic virality is noisy (Brownian). Artificial amplification resonates (Harmonics).
    """
    def __init__(self):
        pass
        
    def scan_amplification_pattern(self, share_timestamps: list[float]) -> float:
        """
        Returns 'Resonance Score' (0.0 to 1.0).
        """
        if len(share_timestamps) < 20:
            return 0.0
            
        # Bin the data into a time series histogram
        duration = max(share_timestamps) - min(share_timestamps)
        bins = 50
        hist, _ = np.histogram(share_timestamps, bins=bins)
        
        # FFT Analysis
        spectrum = np.fft.fft(hist)
        magnitudes = np.abs(spectrum)
        
        # Remove DC component
        magnitudes[0] = 0
        
        peak_energy = np.max(magnitudes)
        total_energy = np.sum(magnitudes)
        
        resonance_ratio = peak_energy / (total_energy + 1e-9)
        
        print(f"🔔 [RSPS] Resonance Ratio: {resonance_ratio:.4f}")
        
        if resonance_ratio > 0.3: # Strong single frequency dominant
            print("   🚨 ALERT: Artificial Resonance Detected!")
            return 0.9
        return 0.1
