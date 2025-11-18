"""
Thermodynamic Security Sensors

Physical measurement systems for threat detection:
- Power analysis detector (SPA/DPA attacks)
- Thermal security monitor (cold boot attacks)
- EM emission analyzer (electromagnetic side channels)
- Information leakage analyzer (entropy-based leakage measurement)
- Timing attack detector
"""

from .power_analysis_detector import (
    PowerAnalysisDetector,
    get_power_analysis_detector
)

__all__ = [
    "PowerAnalysisDetector",
    "get_power_analysis_detector"
]
