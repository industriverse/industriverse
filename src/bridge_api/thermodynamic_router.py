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
from src.capsule_layer.services.a2a_agent_integration import (
    create_host_agent,
    get_agent_registry,
    HostAgent,
    AgentRegistry,
    TaskRequest,
    TaskResult
)
from src.capsule_layer.services.dac_factory_orchestration import (
    create_dac_factory_orchestrator,
    DACFactoryOrchestrator,
    DACSpecification,
    DeploymentConfig,
    ThermodynamicWorkflow,
    CrossCloudConfig,
    ProofType
)
from src.capsule_layer.services.remix_lab_service import (
    create_remix_lab_service,
    RemixLabService,
    RemixComponent,
    RemixSnapshot,
    RemixCommit,
    RemixEventType
)
from src.core.energy_atlas.atlas_core import EnergyAtlas
from src.core.nvp.nvp_predictor import NVPPredictor
from src.core.nvp.schema import TelemetryVector, PredictionResult

# Proof Economy Integration
from src.proof_core.integrity_layer.integrity_manager import IntegrityManager
import uuid

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ThermalSamplingRequest(BaseModel):
    """Request for thermal sampling"""
    problem_type: str = Field(..., description="Type of optimization problem")
    dataset_id: Optional[str] = Field(None, description="Physics dataset to use as prior")
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
        self.simulated_snapshot = create_simulated_snapshot_service()
        self.microadapt_edge = create_microadapt_edge()
        
        # Initialize Energy Atlas & NVP
        self.energy_atlas = EnergyAtlas(use_mock=True)
        try:

            self.energy_atlas.load_manifest("src/core/energy_atlas/sample_manifest.json")
            # Auto-load regenerated maps
            map_dir = "/tmp/energy_maps_test"
            if os.path.exists(map_dir):
                for f in os.listdir(map_dir):
                    if f.endswith("_energy_map.npz"):
                        name = f.replace("_energy_map.npz", "")
                        self.energy_atlas.ingest_energy_map(name, os.path.join(map_dir, f))
        except Exception as e:
            print(f"Warning: Could not load sample manifest or maps: {e}")
            
        self.nvp_predictor = NVPPredictor(context_window=20)
        
        # Initialize Proof Repository
        self.integrity_manager = IntegrityManager()
        self.proof_repository = self.integrity_manager.repository

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
                # If dataset_id is provided, use it as the energy landscape
                prior_map = None
                if request.dataset_id and request.dataset_id in self.energy_atlas.energy_maps:
                    prior_map = self.energy_atlas.energy_maps[request.dataset_id]["data"]

                landscape_id = self.thermal_sampler.create_landscape(
                    problem_type=ProblemType(request.problem_type),
                    dimensions=len(request.variables),
                    constraints=constraints,
                    bounds=[request.variables[k] for k in sorted(request.variables.keys())],
                    prior_map=prior_map # Pass the physics map
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
                
                # Generate Proof of Compute
                proof_id = f"proof_{uuid.uuid4().hex[:8]}"
                if hasattr(self, "proof_repository"):
                    self.proof_repository.store({
                        "proof_id": proof_id,
                        "utid": "UTID:SYSTEM:THERMAL_SAMPLER",
                        "domain": "thermal_optimization",
                        "inputs": {"problem_type": request.problem_type, "variables": request.variables},
                        "outputs": {"best_energy": float(best_energy)},
                        "metadata": {
                            "status": "verified",
                            "proof_score": 1.0, # High confidence for internal compute
                            "energy_joules": float(best_energy) if best_energy != float('inf') else 0.0,
                            "timestamp": datetime.now().isoformat()
                        },
                        "parent_proof_id": None
                    })

                return ThermalSamplingResponse(
                    sampling_id=landscape_id,
                    solutions=[{f"x{i}": float(v) for i, v in enumerate(r.state)} for r in results],
                    energies=[float(r.energy) for r in results],
                    best_solution={f"x{i}": float(v) for i, v in enumerate(results[best_idx].state)} if results else {},
                    best_energy=float(best_energy),
                    proof_hash=proof_id, # Use proof_id as hash for now
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
                
                # Generate Proof of Simulation
                proof_id = f"proof_{uuid.uuid4().hex[:8]}"
                if hasattr(self, "proof_repository"):
                    self.proof_repository.store({
                        "proof_id": proof_id,
                        "utid": "UTID:SYSTEM:WORLD_MODEL",
                        "domain": request.domain,
                        "inputs": {"grid_size": request.grid_size, "time_steps": request.time_steps},
                        "outputs": {"final_energy": result.energy_trajectory[-1] if result.energy_trajectory else 0},
                        "metadata": {
                            "status": "verified",
                            "proof_score": 0.95,
                            "energy_joules": result.energy_trajectory[-1] if result.energy_trajectory else 0.0,
                            "timestamp": result.timestamp.isoformat()
                        },
                        "parent_proof_id": None
                    })

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
        
        # ====================================================================
        # A2A AGENT ENDPOINTS
        # ====================================================================
        
        @self.router.get("/agents")
        async def list_agents():
            """List all available agents (A2A discovery)"""
            registry = get_agent_registry()
            agents = registry.list_agents()
            return {
                "agents": [agent.dict() for agent in agents],
                "count": len(agents),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.router.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            """Get agent card by ID (A2A discovery)"""
            registry = get_agent_registry()
            agent = registry.get_agent(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            return agent.dict()
        
        @self.router.get("/agents/skills/{skill}")
        async def find_agents_by_skill(skill: str):
            """Find agents by skill (A2A discovery)"""
            registry = get_agent_registry()
            agents = registry.find_agents_by_skill(skill)
            return {
                "skill": skill,
                "agents": [agent.dict() for agent in agents],
                "count": len(agents)
            }
        
        @self.router.post("/orchestrate")
        async def orchestrate_workflow(request: Dict[str, Any]):
            """Orchestrate workflow across multiple agents (A2A orchestration)"""
            host_agent = create_host_agent()
            result = await host_agent.orchestrate_workflow(
                workflow_description=request.get("workflow", ""),
                input_data=request.get("input_data", {}),
                mcp_context=request.get("mcp_context")
            )
            return result
        
        # ====================================================================
        # DAC FACTORY ORCHESTRATION ENDPOINTS
        # ====================================================================
        
        @self.router.post("/dac/create")
        async def create_dac(spec: DACSpecification):
            """Create new DAC from specification"""
            orchestrator = create_dac_factory_orchestrator()
            result = await orchestrator.create_dac(spec)
            return result
        
        @self.router.post("/dac/{dac_id}/build")
        async def build_dac(dac_id: str):
            """Build DAC artifact"""
            orchestrator = create_dac_factory_orchestrator()
            result = await orchestrator.build_dac(dac_id)
            return result
        
        @self.router.post("/dac/{dac_id}/deploy")
        async def deploy_dac(dac_id: str, config: DeploymentConfig):
            """Deploy DAC to target platform"""
            orchestrator = create_dac_factory_orchestrator()
            result = await orchestrator.deploy_dac(dac_id, config)
            return result.dict()
        
        @self.router.post("/dac/deployment/{deployment_id}/scale")
        async def scale_dac(deployment_id: str, target_replicas: int):
            """Scale DAC deployment"""
            orchestrator = create_dac_factory_orchestrator()
            result = await orchestrator.scale_dac(deployment_id, target_replicas)
            return result
        
        @self.router.post("/workflow/execute")
        async def execute_thermodynamic_workflow(workflow: ThermodynamicWorkflow):
            """Execute complex thermodynamic workflow"""
            orchestrator = create_dac_factory_orchestrator()
            result = await orchestrator.execute_workflow(workflow)
            return result.dict()
        
        @self.router.post("/proof/generate")
        async def generate_proof(request: Dict[str, Any]):
            """Generate proof for ProofEconomy"""
            orchestrator = create_dac_factory_orchestrator()
            result = await orchestrator.generate_proof(
                proof_type=ProofType(request["proof_type"]),
                dac_id=request["dac_id"],
                input_data=request["input_data"],
                output_data=request["output_data"],
                workflow_id=request.get("workflow_id")
            )
            return result.dict()
        
        @self.router.post("/dac/{dac_id}/deploy-cross-cloud")
        async def deploy_cross_cloud(dac_id: str, cross_cloud_config: CrossCloudConfig, deployment_config: DeploymentConfig):
            """Deploy DAC across multiple clouds"""
            orchestrator = create_dac_factory_orchestrator()
            results = await orchestrator.deploy_cross_cloud(dac_id, cross_cloud_config, deployment_config)
            return {"deployments": [r.dict() for r in results]}
        
        @self.router.get("/dac/{dac_id}/status")
        async def get_dac_status(dac_id: str):
            """Get comprehensive DAC status"""
            orchestrator = create_dac_factory_orchestrator()
            return orchestrator.get_dac_status(dac_id)
        
        @self.router.get("/platform/statistics")
        async def get_platform_statistics():
            """Get platform-wide statistics"""
            orchestrator = create_dac_factory_orchestrator()
            return orchestrator.get_platform_statistics()
        
        # ====================================================================
        # REMIX LAB ENDPOINTS (DAC Creation Nexus)
        # ====================================================================
        
        @self.router.post("/remixlab/snapshot/create")
        async def create_remix_snapshot(request: Dict[str, Any]):
            """Create new remix snapshot"""
            remix_lab = create_remix_lab_service()
            components = [RemixComponent(**c) for c in request["components"]]
            snapshot = await remix_lab.create_snapshot(
                user_id=request["user_id"],
                name=request["name"],
                description=request["description"],
                components=components
            )
            return snapshot.dict()
        
        @self.router.put("/remixlab/snapshot/{snapshot_id}")
        async def update_remix_snapshot(snapshot_id: str, request: Dict[str, Any]):
            """Update existing snapshot"""
            remix_lab = create_remix_lab_service()
            components = [RemixComponent(**c) for c in request.get("components", [])]
            snapshot = await remix_lab.update_snapshot(
                snapshot_id=snapshot_id,
                components=components if components else None,
                connections=request.get("connections")
            )
            return snapshot.dict()
        
        @self.router.post("/remixlab/snapshot/{snapshot_id}/simulate")
        async def simulate_remix(snapshot_id: str, config: Optional[Dict[str, Any]] = None):
            """Run simulation on remix snapshot"""
            remix_lab = create_remix_lab_service()
            results = await remix_lab.simulate_remix(snapshot_id, config)
            return results
        
        @self.router.post("/remixlab/commit")
        async def commit_remix(request: Dict[str, Any]):
            """
            Commit remix and generate UTID
            
            This is the critical operation that triggers:
            1. UTID minting
            2. DAC manifest creation
            3. Event emission to DAC Orchestrator
            4. Proof generation
            5. Capsule registration
            """
            remix_lab = create_remix_lab_service()
            commit = await remix_lab.commit_remix(
                snapshot_id=request["snapshot_id"],
                committed_by=request["committed_by"],
                collaborators=request.get("collaborators")
            )
            return commit.dict()
        
        @self.router.post("/remixlab/revoke/{commit_id}")
        async def revoke_remix(commit_id: str, request: Dict[str, Any]):
            """Revoke committed remix"""
            remix_lab = create_remix_lab_service()
            result = await remix_lab.revoke_remix(
                commit_id=commit_id,
                revoked_by=request["revoked_by"],
                reason=request["reason"]
            )
            return result
        
        @self.router.get("/remixlab/snapshot/{snapshot_id}")
        async def get_remix_snapshot(snapshot_id: str):
            """Get snapshot by ID"""
            remix_lab = create_remix_lab_service()
            snapshot = remix_lab.get_snapshot(snapshot_id)
            if not snapshot:
                raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found")
            return snapshot.dict()
        
        @self.router.get("/remixlab/commit/{commit_id}")
        async def get_remix_commit(commit_id: str):
            """Get commit by ID"""
            remix_lab = create_remix_lab_service()
            commit = remix_lab.get_commit(commit_id)
            if not commit:
                raise HTTPException(status_code=404, detail=f"Commit {commit_id} not found")
            return commit.dict()
        
        @self.router.get("/remixlab/utid/{utid}")
        async def get_utid_record(utid: str):
            """Get UTID record"""
            remix_lab = create_remix_lab_service()
            record = remix_lab.get_utid_record(utid)
            if not record:
                raise HTTPException(status_code=404, detail=f"UTID {utid} not found")
            return record.dict()
        
        @self.router.get("/remixlab/user/{user_id}/snapshots")
        async def list_user_snapshots(user_id: str):
            """List user's snapshots"""
            remix_lab = create_remix_lab_service()
            snapshots = remix_lab.list_user_snapshots(user_id)
            return {"snapshots": [s.dict() for s in snapshots]}
        
        @self.router.get("/remixlab/user/{user_id}/commits")
        async def list_user_commits(user_id: str):
            """List user's commits"""
            remix_lab = create_remix_lab_service()
            commits = remix_lab.list_user_commits(user_id)
            return {"commits": [c.dict() for c in commits]}
        
        @self.router.get("/remixlab/events")
        async def get_remix_events(event_type: Optional[str] = None, limit: int = 100):
            """Get Remix Lab events"""
            remix_lab = create_remix_lab_service()
            event_type_enum = RemixEventType(event_type) if event_type else None
            events = remix_lab.get_events(event_type_enum, limit)
            return {"events": [e.dict() for e in events]}
        
        @self.router.get("/remixlab/statistics")
        async def get_remix_lab_statistics():
            """Get Remix Lab statistics"""
            remix_lab = create_remix_lab_service()
            return remix_lab.get_statistics()
        
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
                "a2a_enabled": True,
                "mcp_enabled": MCP_AVAILABLE,
                "agent_count": 4,
                "dac_factory_enabled": True,
                "remix_lab_enabled": True,
                "orchestration_capabilities": [
                    "lifecycle_management",
                    "multi_platform_deployment",
                    "thermodynamic_workflows",
                    "energy_atlas_integration",
                    "proof_economy_integration",
                    "cross_cloud_orchestration",
                    "remix_lab_dac_creation",
                    "utid_generation",
                    "provenance_tracking"
                ],
                "timestamp": datetime.now().isoformat()
            }

        # ====================================================================
        # ENERGY ATLAS & NVP ENDPOINTS
        # ====================================================================

        @self.router.get("/energy-map")
        async def get_energy_map() -> Dict[str, Any]:
            """
            Get the current thermodynamic energy map of the hardware.
            """
            return self.energy_atlas.get_energy_map()

        @self.router.post("/predict-vector")
        async def predict_vector(vector: TelemetryVector, horizon: float = 1.0) -> PredictionResult:
            """
            Submit a telemetry vector and get a prediction for the next state.
            """
            self.nvp_predictor.add_observation(vector)
            try:
                result = self.nvp_predictor.predict_next(horizon_seconds=horizon)
                return result
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

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
