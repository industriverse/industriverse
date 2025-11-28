import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class PowerTraceConverter:
    """
    Converts raw power traces (time-series) into thermodynamic energy vectors E(t).
    """
    def __init__(self, sampling_rate_hz=1000):
        self.sampling_rate = sampling_rate_hz

    def process(self, raw_trace):
        """
        Args:
            raw_trace (list or np.array): Raw power readings (Watts).
        Returns:
            dict: Energy vector containing E_total, dE/dt, and Entropy.
        """
        trace = np.array(raw_trace)
        dt = 1.0 / self.sampling_rate
        
        # 1. Energy (Joules) = Integral of Power * dt
        energy_total = np.sum(trace) * dt
        
        # 2. Power Flux (dE/dt) = Gradient of Energy (which is Power itself)
        # We'll use the variance of the power trace as a proxy for "flux volatility"
        flux_volatility = np.var(trace)
        
        # 3. Entropy (Shannon Entropy of the normalized power distribution)
        # Normalize trace to treat as probability distribution
        if np.sum(trace) > 0:
            p = trace / np.sum(trace)
            # Avoid log(0)
            p = p[p > 0]
            entropy = -np.sum(p * np.log(p))
        else:
            entropy = 0.0

        return {
            "E_total": energy_total,
            "dE_dt_volatility": flux_volatility,
            "Entropy": entropy,
            "samples": len(trace)
        }

class ConservationEnforcer:
    """
    Enforces the First Law of Thermodynamics: Energy In = Energy Out + Storage.
    Detects violations (anomalies).
    """
    def __init__(self, tolerance=0.01):
        self.tolerance = tolerance

    def check(self, e_in, e_out, e_stored):
        """
        Returns True if conservation holds, False otherwise.
        """
        balance = e_in - (e_out + e_stored)
        if abs(balance) > self.tolerance:
            logger.warning(f"VIOLATION: Energy imbalance detected! Delta: {balance:.4f}J")
            return False
        return True

class UniversalNormalizer:
    """
    Adapter pattern to normalize data from different domains (Industrial, Bio, Finance)
    into a standard 0-1 thermodynamic scale.
    """
    def __init__(self):
        self.adapters = {
            "industrial": self._normalize_industrial,
            "bio": self._normalize_bio,
            "finance": self._normalize_finance
        }

    def normalize(self, value, domain, context=None):
        if domain not in self.adapters:
            raise ValueError(f"Unknown domain: {domain}")
        return self.adapters[domain](value, context)

    def _normalize_industrial(self, value, context):
        # Example: Normalize temperature (0-2000C)
        max_val = context.get("max_temp", 2000) if context else 2000
        return min(max(value / max_val, 0.0), 1.0)

    def _normalize_bio(self, value, context):
        # Example: Normalize neurotransmitter concentration (0-100 nM)
        max_val = context.get("max_conc", 100) if context else 100
        return min(max(value / max_val, 0.0), 1.0)

    def _normalize_finance(self, value, context):
        # Example: Normalize trade volume (log scale)
        # value is raw volume
        return min(max(np.log1p(value) / 20.0, 0.0), 1.0)
