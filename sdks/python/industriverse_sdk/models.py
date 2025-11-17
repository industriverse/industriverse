"""Pydantic models for Industriverse API"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


# Thermal Sampler Models
class Constraint(BaseModel):
    type: str
    expression: str
    value: Optional[float] = None


class ThermalMetadata(BaseModel):
    problem_type: str
    variables: int
    num_samples: int
    temperature: float
    sampling_time: float


class ThermalSampleResult(BaseModel):
    samples: List[List[float]]
    energies: List[float]
    best_sample: List[float]
    best_energy: float
    convergence_history: List[float]
    metadata: ThermalMetadata


class ThermalStatistics(BaseModel):
    total_samples: int
    total_problems: int
    average_energy: float
    average_sampling_time: float


# World Model Models
class SimulationMetadata(BaseModel):
    domain: str
    time_steps: int
    simulation_time: float


class SimulationResult(BaseModel):
    trajectory: List[List[float]]
    final_state: List[float]
    metadata: SimulationMetadata


class RolloutMetadata(BaseModel):
    domain: str
    horizon: int
    rollout_time: float


class RolloutResult(BaseModel):
    predictions: List[List[float]]
    rewards: List[float]
    metadata: RolloutMetadata


class WorldModelStatistics(BaseModel):
    total_simulations: int
    total_rollouts: int
    average_simulation_time: float


# MicroAdapt Models
class MicroAdaptUpdateResult(BaseModel):
    updated: bool
    current_regime: str
    regime_confidence: float
    prediction_error: float


class ForecastResult(BaseModel):
    predictions: List[float]
    confidence_intervals: List[List[float]]
    regime_sequence: List[str]


class RegimeInfo(BaseModel):
    current_regime: str
    regime_confidence: float
    regime_history: List[str]
    regime_duration: int


class MicroAdaptStatistics(BaseModel):
    total_updates: int
    total_forecasts: int
    average_prediction_error: float
    regime_changes: int


# Snapshot Models
class SnapshotStoreResult(BaseModel):
    snapshot_id: str
    stored: bool


class CalibrationResult(BaseModel):
    correction_factors: Dict[str, float]
    error_metrics: Dict[str, float]
    calibrated: bool


class SnapshotStatistics(BaseModel):
    total_snapshots: int
    total_calibrations: int
    average_error: float


# DAC Models
class DACInfo(BaseModel):
    id: str
    name: str
    description: str
    version: str
    platforms: List[str]
    status: str


class DACFunction(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, str]
    output_schema: Dict[str, str]


class Deployment(BaseModel):
    id: str
    platform: str
    status: str
    endpoint: Optional[str]
    created_at: str


class DACDetails(BaseModel):
    id: str
    name: str
    description: str
    version: str
    platforms: List[str]
    functions: List[DACFunction]
    deployments: List[Deployment]
    metadata: Dict[str, str]
