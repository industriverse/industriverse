"""
ACE (Aspiration-Calibration-Execution) Cognitive Architecture
Phase 4 - Next Vector Prediction with Metacognition
"""

from .ace_agent import (
    ACEAgent,
    ACEConfig,
    AspirationConfig,
    CalibrationConfig,
    ExecutionConfig,
    AspirationLayer,
    CalibrationLayer,
    ExecutionLayer,
    PredictionResult
)

from .socratic_loop import (
    SocraticLoop,
    SocraticConfig,
    SocraticACEAgent,
    FailureMode,
    ErrorAnalysis
)

from .shadow_ensemble import (
    ShadowEnsemble,
    EnsembleConfig,
    EnsembleResult,
    EnsembleACEAgent
)

__all__ = [
    # Core ACE
    'ACEAgent',
    'ACEConfig',
    'AspirationConfig',
    'CalibrationConfig',
    'ExecutionConfig',
    'AspirationLayer',
    'CalibrationLayer',
    'ExecutionLayer',
    'PredictionResult',
    # Socratic Loop
    'SocraticLoop',
    'SocraticConfig',
    'SocraticACEAgent',
    'FailureMode',
    'ErrorAnalysis',
    # Shadow Ensemble
    'ShadowEnsemble',
    'EnsembleConfig',
    'EnsembleResult',
    'EnsembleACEAgent'
]
