"""Service clients for Industriverse API"""

from typing import List, Dict, Optional, TYPE_CHECKING
from .models import *

if TYPE_CHECKING:
    from .client import IndustriverseClient


class ThermalSamplerClient:
    """Client for Thermal Sampler service"""
    
    def __init__(self, client: "IndustriverseClient"):
        self._client = client
    
    async def sample(
        self,
        problem_type: str,
        variables: int,
        constraints: List[Constraint] = None,
        num_samples: int = 100,
        temperature: float = 1.0,
    ) -> ThermalSampleResult:
        """Sample from thermal distribution"""
        data = await self._client._post(
            "/api/v1/thermodynamic/thermal/sample",
            {
                "problem_type": problem_type,
                "variables": variables,
                "constraints": [c.dict() for c in (constraints or [])],
                "num_samples": num_samples,
                "temperature": temperature,
            },
        )
        return ThermalSampleResult(**data)
    
    async def statistics(self) -> ThermalStatistics:
        """Get thermal sampler statistics"""
        data = await self._client._get("/api/v1/thermodynamic/thermal/statistics")
        return ThermalStatistics(**data)


class WorldModelClient:
    """Client for World Model service"""
    
    def __init__(self, client: "IndustriverseClient"):
        self._client = client
    
    async def simulate(
        self,
        domain: str,
        initial_state: List[float],
        parameters: Dict[str, float],
        time_steps: int = 100,
    ) -> SimulationResult:
        """Simulate physical process"""
        data = await self._client._post(
            "/api/v1/thermodynamic/worldmodel/simulate",
            {
                "domain": domain,
                "initial_state": initial_state,
                "parameters": parameters,
                "time_steps": time_steps,
            },
        )
        return SimulationResult(**data)
    
    async def rollout(
        self,
        domain: str,
        initial_state: List[float],
        actions: List[List[float]],
        horizon: int,
    ) -> RolloutResult:
        """Multi-step rollout prediction"""
        data = await self._client._post(
            f"/api/v1/thermodynamic/worldmodel/rollout?horizon={horizon}",
            {
                "domain": domain,
                "initial_state": initial_state,
                "actions": actions,
                "horizon": horizon,
            },
        )
        return RolloutResult(**data)
    
    async def statistics(self) -> WorldModelStatistics:
        """Get world model statistics"""
        data = await self._client._get("/api/v1/thermodynamic/worldmodel/statistics")
        return WorldModelStatistics(**data)


class MicroAdaptClient:
    """Client for MicroAdapt Edge service"""
    
    def __init__(self, client: "IndustriverseClient"):
        self._client = client
    
    async def update(
        self,
        timestamp: float,
        value: float,
        features: Optional[List[float]] = None,
    ) -> MicroAdaptUpdateResult:
        """Update model with new observation"""
        data = await self._client._post(
            "/api/v1/thermodynamic/microadapt/update",
            {
                "timestamp": timestamp,
                "value": value,
                "features": features,
            },
        )
        return MicroAdaptUpdateResult(**data)
    
    async def forecast(self, horizon: int) -> ForecastResult:
        """Forecast future values"""
        data = await self._client._post(
            "/api/v1/thermodynamic/microadapt/forecast",
            {"horizon": horizon},
        )
        return ForecastResult(**data)
    
    async def regime(self) -> RegimeInfo:
        """Get current regime information"""
        data = await self._client._get("/api/v1/thermodynamic/microadapt/regime")
        return RegimeInfo(**data)
    
    async def statistics(self) -> MicroAdaptStatistics:
        """Get MicroAdapt statistics"""
        data = await self._client._get("/api/v1/thermodynamic/microadapt/statistics")
        return MicroAdaptStatistics(**data)


class SimulatedSnapshotClient:
    """Client for Simulated Snapshot service"""
    
    def __init__(self, client: "IndustriverseClient"):
        self._client = client
    
    async def store(
        self,
        snapshot_type: str,
        simulator_id: str,
        real_data: Dict[str, float],
        simulated_data: Dict[str, float],
        metadata: Dict[str, str] = None,
    ) -> SnapshotStoreResult:
        """Store simulated snapshot"""
        data = await self._client._post(
            "/api/v1/thermodynamic/snapshot/store",
            {
                "snapshot_type": snapshot_type,
                "simulator_id": simulator_id,
                "real_data": real_data,
                "simulated_data": simulated_data,
                "metadata": metadata or {},
            },
        )
        return SnapshotStoreResult(**data)
    
    async def calibrate(
        self,
        snapshot_id: str,
        calibration_method: str = "least_squares",
    ) -> CalibrationResult:
        """Calibrate simulator"""
        data = await self._client._post(
            "/api/v1/thermodynamic/snapshot/calibrate",
            {
                "snapshot_id": snapshot_id,
                "calibration_method": calibration_method,
            },
        )
        return CalibrationResult(**data)
    
    async def statistics(self) -> SnapshotStatistics:
        """Get snapshot statistics"""
        data = await self._client._get("/api/v1/thermodynamic/snapshot/statistics")
        return SnapshotStatistics(**data)


class DACClient:
    """Client for DAC management"""
    
    def __init__(self, client: "IndustriverseClient"):
        self._client = client
    
    async def list(self) -> List[DACInfo]:
        """List available DACs"""
        data = await self._client._get("/api/v1/dac/list")
        return [DACInfo(**item) for item in data]
    
    async def get(self, id: str) -> DACDetails:
        """Get DAC details"""
        data = await self._client._get(f"/api/v1/dac/{id}")
        return DACDetails(**data)
