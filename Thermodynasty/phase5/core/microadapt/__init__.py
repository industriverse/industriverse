"""MicroAdaptEdge: Self-Evolutionary Dynamic Modeling Framework

Ported from Phase 1 TTF Inference system to Phase 5 EIL.
Provides hierarchical windowing, online model adaptation, and regime-based forecasting.
"""

from .core.config import config, MicroAdaptConfig
from .models.model_unit import ModelUnit, ModelUnitParameters
from .models.window import HierarchicalWindow, WindowSet
from .models.regime import RegimeAssignment, RegimeTransition
from .algorithms.data_collection import DynamicDataCollection
from .algorithms.model_adaptation import ModelUnitAdaptation
from .algorithms.model_search import ModelUnitSearch

__all__ = [
    'config',
    'MicroAdaptConfig',
    'ModelUnit',
    'ModelUnitParameters',
    'HierarchicalWindow',
    'WindowSet',
    'RegimeAssignment',
    'RegimeTransition',
    'DynamicDataCollection',
    'ModelUnitAdaptation',
    'ModelUnitSearch',
]

__version__ = '2.0.0'  # Phase 5 EIL version
