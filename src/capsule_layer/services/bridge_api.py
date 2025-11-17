"""
Bridge API - Production Ready

Integrates thermodynamic computing services with Capsule Gateway:
1. ThermalSampler (thrml energy-based optimization)
2. WorldModel (JAX physics simulation)
3. SimulatedSnapshot (sim/real calibration)
4. MicroAdaptEdge (self-evolutionary adaptive modeling)

Provides unified REST API endpoints for:
- Energy-aware optimization
- Physics-accurate simulation
- Sim/real calibration
- Edge-native adaptive forecasting
"""

import asyncio

# MCP Integration - Context-Aware Ecosystem
try:
    from fastapi_mcp import FastApiMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np

# Import our thermodynamic services
from src.capsule_layer.services.thermal_sampler.thermal_sampler_service import (
    create_thermal_sampler,
    ThermalSamplerService
)
from src.capsule_layer.services.world_model.world_model_service import (
    create_world_model,
    WorldModelService,
    DomainType,
    SimulationConfig,
    PhysicsState,
    SimulationResult
)
from src.capsule_layer.services.energy_atlas_ext.simulated_snapshot_service import (
    create_simulated_snapshot_service,
    SimulatedSnapshotService,
    SnapshotType,
    CalibrationResult
)
from src.capsule_layer.services.microadapt_edge.microadapt_service import (
    create_microadapt_edge,
    MicroAdaptEdgeService,
    ForecastResult
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ThermalSamplingRequest(BaseModel):
    """Request for thermal sampling"""
    problem_type: str = Field(..., description="Type of optimization problem")
    variables: Dict[str, Any] = Field(..., description="Problem variables")
    constraints: List[Dict[str, Any]] = Field(default_factory=list, description="Constraints")
    num_samples: int = Field(1000, description="Number of samples")
    temperature: float = Field(1.0, description="Sampling temperature")
    
class ThermalSamplingResponse(BaseModel):
    """Response from thermal sampling"""
    sampling_id: str
    solutions: List[Dict[str, float]]
    energies: List[float]
    best_solution: Dict[str, float]
    best_energy: float
    proof_hash: str
    timestamp: str

class WorldModelSimulationRequest(BaseModel):
    """Request for world model simulation"""
    domain: str = Field(..., description="Physics domain (lithography, plasma, etc.)")
    grid_size: List[int] = Field(..., description="Spatial grid size")
    time_steps: int = Field(..., description="Number of simulation steps")
    dt: float = Field(0.01, description="Time step size")
    initial_state: Dict[str, Any] = Field(..., description="Initial physical state")
    physics_params: Dict[str, float] = Field(default_factory=dict, description="Physics parameters")

class WorldModelSimulationResponse(BaseModel):
    """Response from world model simulation"""
    simulation_id: str
    domain: str
    final_state: Dict[str, Any]
    energy_trajectory: List[float]
    metrics: Dict[str, float]
    timestamp: str

class SimulatedSnapshotRequest(BaseModel):
    """Request to store simulated snapshot"""
    snapshot_type: str = Field(..., description="Type of snapshot")
    simulator_id: str = Field(..., description="Simulator ID")
    energy_map: List[List[float]] = Field(..., description="Energy field data")
    real_snapshot_id: Optional[str] = Field(None, description="Link to real measurement")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class SimulatedSnapshotResponse(BaseModel):
    """Response from storing simulated snapshot"""
    snapshot_id: str
    energy_signature: str
    calibration_status: str
    timestamp: str

class CalibrationRequest(BaseModel):
    """Request for calibration"""
    sim_snapshot_id: str = Field(..., description="Simulated snapshot ID")
    real_snapshot_id: str = Field(..., description="Real measurement ID")
    real_energy_map: List[List[float]] = Field(..., description="Real energy field data")

class CalibrationResponse(BaseModel):
    """Response from calibration"""
    calibration_id: str
    error_metrics: Dict[str, float]
    correction_factors: Dict[str, float]
    calibration_status: str
    timestamp: str

class MicroAdaptUpdateRequest(BaseModel):
    """Request to update MicroAdapt with new data"""
    data_point: List[float] = Field(..., description="New data point")

class MicroAdaptForecastRequest(BaseModel):
    """Request for MicroAdapt forecast"""
    forecast_horizon: int = Field(..., description="Number of steps to forecast")

class MicroAdaptForecastResponse(BaseModel):
    """Response from MicroAdapt forecast"""
    forecast_id: str
    forecast_values: List[List[float]]
    forecast_horizon: int
    regime_info: Dict[str, Any]
    timestamp: str

# ============================================================================
# BRIDGE API ROUTER
# ============================================================================

class BridgeAPI:
    """
    Bridge API for thermodynamic computing services.
    
    Integrates ThermalSampler, WorldModel, SimulatedSnapshot, and MicroAdaptEdge.
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1/thermodynamic", tags=["thermodynamic"])
        
        # Initialize services
        self.thermal_sampler = create_thermal_sampler()
        self.world_model = create_world_model()
        self.simulated_snapshot = create_simulated_snapshot_service()
        self.microadapt_edge = create_microadapt_edge()
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all API routes"""
        
        # ====================================================================
        # THERMAL SAMPLER ENDPOINTS
        # ====================================================================
        
        @self.router.post("/thermal/sample", response_model=ThermalSamplingResponse)
        async def thermal_sample(request: ThermalSamplingRequest):
            """
            Solve optimization problem using thermal sampling.
            
            Uses thrml library for energy-based optimization.
            """
            try:
                # Import required types
                from src.capsule_layer.services.thermal_sampler.thermal_sampler_service import ProblemType, Constraint
                
                # Convert constraints
                constraints = []
                for c in request.constraints:
                    constraint = Constraint(
                        name=c.get("name", "constraint"),
                        type=c.get("type", "equality"),
                        weight=c.get("weight", 1.0),
                        function=c.get("expression", "")
                    )
                    constraints.append(constraint)
                
                # Create landscape
                landscape_id = self.thermal_sampler.create_landscape(
                    problem_type=ProblemType(request.problem_type),
                    dimensions=len(request.variables),
                    constraints=constraints,
                    bounds=[request.variables[k] for k in sorted(request.variables.keys())]
                )
                
                # Run thermal sampling
                results = await self.thermal_sampler.sample(
                    landscape_id=landscape_id,
                    num_samples=request.num_samples
                )
                
                # Extract best solution
                best_idx = 0
                best_energy = results[0].energy if results else float('inf')
                for i, r in enumerate(results):
                    if r.energy < best_energy:
                        best_energy = r.energy
                        best_idx = i
                
                return ThermalSamplingResponse(
                    sampling_id=landscape_id,
                    solutions=[{f"x{i}": float(v) for i, v in enumerate(r.state)} for r in results],
                    energies=[float(r.energy) for r in results],
                    best_solution={f"x{i}": float(v) for i, v in enumerate(results[best_idx].state)} if results else {},
                    best_energy=float(best_energy),
                    proof_hash=results[best_idx].proof_hash if results else "",
                    timestamp=results[best_idx].timestamp.isoformat() if results else datetime.now().isoformat()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/thermal/statistics")
        async def thermal_statistics():
            """Get thermal sampler statistics"""
            return self.thermal_sampler.get_statistics()
        
        # ====================================================================
        # WORLD MODEL ENDPOINTS
        # ====================================================================
        
        @self.router.post("/worldmodel/simulate", response_model=WorldModelSimulationResponse)
        async def worldmodel_simulate(request: WorldModelSimulationRequest):
            """
            Run physics simulation using JAX world model.
            
            Supports lithography, plasma, resist chemistry, etc.
            """
            try:
                # Parse domain
                domain = DomainType(request.domain)
                
                # Create initial state
                initial_grid = np.array(request.initial_state.get("spatial_grid", []))
                initial_state = PhysicsState(
                    domain=domain,
                    spatial_grid=initial_grid,
                    temperature=np.array(request.initial_state.get("temperature")) if "temperature" in request.initial_state else None,
                    velocity=np.array(request.initial_state.get("velocity")) if "velocity" in request.initial_state else None
                )
                
                # Create simulation config
                config = SimulationConfig(
                    domain=domain,
                    grid_size=tuple(request.grid_size),
                    time_steps=request.time_steps,
                    dt=request.dt,
                    physics_params=request.physics_params
                )
                
                # Run simulation
                result = await self.world_model.simulate(config, initial_state)
                
                return WorldModelSimulationResponse(
                    simulation_id=result.simulation_id,
                    domain=result.initial_state.domain.value,
                    final_state={
                        "spatial_grid": result.final_state.spatial_grid.tolist(),
                        "metadata": result.final_state.metadata
                    },
                    energy_trajectory=result.energy_trajectory,
                    metrics=result.metrics,
                    timestamp=result.timestamp.isoformat()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/worldmodel/rollout")
        async def worldmodel_rollout(
            request: WorldModelSimulationRequest,
            horizon: int = 100
        ):
            """Generate multi-step rollout prediction"""
            try:
                domain = DomainType(request.domain)
                initial_grid = np.array(request.initial_state.get("spatial_grid", []))
                initial_state = PhysicsState(
                    domain=domain,
                    spatial_grid=initial_grid
                )
                
                config = SimulationConfig(
                    domain=domain,
                    grid_size=tuple(request.grid_size),
                    time_steps=request.time_steps,
                    dt=request.dt,
                    physics_params=request.physics_params
                )
                
                trajectory = await self.world_model.rollout(config, initial_state, horizon)
                
                return {
                    "trajectory_length": len(trajectory),
                    "trajectory": [
                        {
                            "spatial_grid": state.spatial_grid.tolist(),
                            "metadata": state.metadata
                        }
                        for state in trajectory[::10]  # Sample every 10 steps
                    ]
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/worldmodel/statistics")
        async def worldmodel_statistics():
            """Get world model statistics"""
            return self.world_model.get_statistics()
        
        # ====================================================================
        # SIMULATED SNAPSHOT ENDPOINTS
        # ====================================================================
        
        @self.router.post("/snapshot/store", response_model=SimulatedSnapshotResponse)
        async def snapshot_store(request: SimulatedSnapshotRequest):
            """Store simulated energy snapshot"""
            try:
                snapshot_type = SnapshotType(request.snapshot_type)
                energy_map = np.array(request.energy_map)
                
                snapshot_id = await self.simulated_snapshot.store_snapshot(
                    snapshot_type=snapshot_type,
                    simulator_id=request.simulator_id,
                    energy_map=energy_map,
                    real_snapshot_id=request.real_snapshot_id,
                    metadata=request.metadata
                )
                
                snapshot = self.simulated_snapshot.get_snapshot(snapshot_id)
                
                return SimulatedSnapshotResponse(
                    snapshot_id=snapshot.snapshot_id,
                    energy_signature=snapshot.energy_signature,
                    calibration_status=snapshot.calibration_status.value,
                    timestamp=snapshot.timestamp.isoformat()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/snapshot/calibrate", response_model=CalibrationResponse)
        async def snapshot_calibrate(request: CalibrationRequest):
            """Calibrate simulated snapshot against real measurement"""
            try:
                real_energy_map = np.array(request.real_energy_map)
                
                calibration = await self.simulated_snapshot.calibrate(
                    sim_snapshot_id=request.sim_snapshot_id,
                    real_snapshot_id=request.real_snapshot_id,
                    real_energy_map=real_energy_map
                )
                
                return CalibrationResponse(
                    calibration_id=calibration.calibration_id,
                    error_metrics=calibration.error_metrics,
                    correction_factors=calibration.correction_factors,
                    calibration_status=calibration.calibration_status.value,
                    timestamp=calibration.timestamp.isoformat()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/snapshot/statistics")
        async def snapshot_statistics():
            """Get simulated snapshot statistics"""
            return self.simulated_snapshot.get_statistics()
        
        # ====================================================================
        # MICROADAPT EDGE ENDPOINTS
        # ====================================================================
        
        @self.router.post("/microadapt/update")
        async def microadapt_update(request: MicroAdaptUpdateRequest):
            """Update MicroAdapt with new data point (O(1) time)"""
            try:
                data_point = np.array(request.data_point)
                await self.microadapt_edge.update(data_point)
                
                return {
                    "status": "updated",
                    "current_time": self.microadapt_edge.current_time,
                    "num_model_units": len(self.microadapt_edge.model_units)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/microadapt/forecast", response_model=MicroAdaptForecastResponse)
        async def microadapt_forecast(request: MicroAdaptForecastRequest):
            """Generate lF-steps-ahead forecast"""
            try:
                # Get current window
                X_current = self.microadapt_edge._get_current_window()
                
                if len(X_current) == 0:
                    raise HTTPException(status_code=400, detail="Not enough data for forecasting")
                
                # Generate forecast
                result = await self.microadapt_edge.search_and_forecast(
                    X_current=X_current,
                    forecast_horizon=request.forecast_horizon
                )
                
                return MicroAdaptForecastResponse(
                    forecast_id=result.forecast_id,
                    forecast_values=result.forecast_values.tolist(),
                    forecast_horizon=result.forecast_horizon,
                    regime_info=self.microadapt_edge.get_regime_info(),
                    timestamp=result.timestamp.isoformat()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/microadapt/statistics")
        async def microadapt_statistics():
            """Get MicroAdapt statistics"""
            return self.microadapt_edge.get_statistics()
        
        @self.router.get("/microadapt/regime")
        async def microadapt_regime():
            """Get current regime information"""
            return self.microadapt_edge.get_regime_info()
        
        # ====================================================================
        # COMBINED ENDPOINTS
        # ====================================================================
        
        @self.router.post("/combined/simulate_and_optimize")
        async def simulate_and_optimize(
            simulation_request: WorldModelSimulationRequest,
            optimization_request: ThermalSamplingRequest
        ):
            """
            Combined workflow: Simulate with WorldModel, then optimize with ThermalSampler.
            
            Useful for process optimization in semiconductor manufacturing.
            """
            try:
                # Step 1: Run simulation
                domain = DomainType(simulation_request.domain)
                initial_grid = np.array(simulation_request.initial_state.get("spatial_grid", []))
                initial_state = PhysicsState(domain=domain, spatial_grid=initial_grid)
                
                config = SimulationConfig(
                    domain=domain,
                    grid_size=tuple(simulation_request.grid_size),
                    time_steps=simulation_request.time_steps,
                    dt=simulation_request.dt,
                    physics_params=simulation_request.physics_params
                )
                
                sim_result = await self.world_model.simulate(config, initial_state)
                
                # Step 2: Use simulation results to inform optimization
                # (In production, would extract features from simulation)
                
                # Step 3: Run thermal optimization
                thermal_result = await self.thermal_sampler.sample(
                    problem_type=optimization_request.problem_type,
                    variables=optimization_request.variables,
                    constraints=[],
                    num_samples=optimization_request.num_samples,
                    temperature=optimization_request.temperature
                )
                
                return {
                    "simulation": {
                        "simulation_id": sim_result.simulation_id,
                        "metrics": sim_result.metrics
                    },
                    "optimization": {
                        "sampling_id": thermal_result.sampling_id,
                        "best_solution": dict(thermal_result.best_solution),
                        "best_energy": thermal_result.best_energy
                    }
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/health")
        async def health_check():
            """Health check for all thermodynamic services"""
            return {
                "status": "healthy",
                "services": {
                    "thermal_sampler": self.thermal_sampler.get_statistics(),
                    "world_model": self.world_model.get_statistics(),
                    "simulated_snapshot": self.simulated_snapshot.get_statistics(),
                    "microadapt_edge": self.microadapt_edge.get_statistics()
                },
                "timestamp": datetime.now().isoformat()
            }

# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_bridge_api(enable_mcp: bool = True) -> BridgeAPI:
    """
    Factory function to create Bridge API with optional MCP integration
    
    Args:
        enable_mcp: Enable Model Context Protocol integration for context-aware ecosystem
    
    Returns:
        BridgeAPI instance with MCP integration if available
    """
    bridge = BridgeAPI()
    
    # Add MCP integration for context-aware ecosystem
    if enable_mcp and MCP_AVAILABLE:
        try:
            # Create FastAPI app from router
            from fastapi import FastAPI
            app = FastAPI(
                title="Industriverse Thermodynamic Bridge",
                description="Context-aware thermodynamic computing services",
                version="1.0.0"
            )
            app.include_router(bridge.router, prefix="/api/v1/thermodynamic")
            
            # Initialize MCP - exposes all endpoints as MCP tools
            mcp = FastApiMCP(app)
            mcp.mount_http()
            
            # Store MCP instance for later use
            bridge._mcp = mcp
            bridge._mcp_app = app
            
            print("✅ MCP integration enabled - all thermodynamic services now context-aware")
        except Exception as e:
            print(f"⚠️ MCP integration failed: {e}")
    elif enable_mcp and not MCP_AVAILABLE:
        print("⚠️ MCP not available - install fastapi-mcp to enable context-aware ecosystem")
    
    return bridge
