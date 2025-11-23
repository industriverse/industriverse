from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TelemetryVector(BaseModel):
    """
    Represents a single time-step telemetry vector for NVP.
    Vector: [Voltage, Current, Temperature, Utilization, ErrorRate]
    """
    timestamp: datetime = Field(default_factory=datetime.now)
    node_id: str
    voltage: float
    current: float
    temperature_c: float
    utilization: float = Field(..., ge=0.0, le=1.0, description="Normalized utilization (0-1)")
    error_rate: float = Field(0.0, ge=0.0, description="Errors per second")
    
    def to_vector(self) -> List[float]:
        """Returns the raw numerical vector for the model."""
        return [self.voltage, self.current, self.temperature_c, self.utilization, self.error_rate]

class PredictionResult(BaseModel):
    """
    Output of the NVP predictor.
    """
    timestamp: datetime
    predicted_vector: TelemetryVector
    confidence_interval: List[float] = Field(..., description="Uncertainty for each dimension")
    failure_probability: float = Field(..., ge=0.0, le=1.0)
