import logging
import time
import json
import os
import random
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Import Gaussian Splatting Trainer (or mock if dependencies missing)
try:
    from frontend.src.ar_vr.gaussian_splatting.gaussian_splatting_trainer import GaussianSplattingTrainer, TrainingOutput
except ImportError:
    GaussianSplattingTrainer = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TwinState:
    timestamp: datetime
    metrics: Dict[str, float]
    status: str

class DigitalTwinService:
    """
    Core service for managing Digital Twins, Shadow Projections, and 3D Visualizations.
    """

    def __init__(self, storage_path: str = "data/digital_twins"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        self.twins = {}
        self.gs_trainer = GaussianSplattingTrainer() if GaussianSplattingTrainer else None

    def create_twin(self, twin_id: str, twin_type: str, initial_config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a new Digital Twin."""
        twin = {
            "id": twin_id,
            "type": twin_type,
            "config": initial_config,
            "created_at": datetime.now().isoformat(),
            "current_state": self._get_initial_state(twin_type),
            "shadow_projections": []
        }
        self.twins[twin_id] = twin
        self._save_twin(twin_id)
        logger.info(f"Created Digital Twin: {twin_id} ({twin_type})")
        return twin

    def _get_initial_state(self, twin_type: str) -> Dict[str, float]:
        """Get initial metrics based on twin type."""
        if twin_type == "fusion_reactor":
            return {"plasma_temp": 150.0, "magnetic_field": 12.5, "stability": 0.99}
        elif twin_type == "grid_substation":
            return {"load": 45.0, "voltage": 110.0, "frequency": 60.0}
        elif twin_type == "supply_chain_node":
            return {"inventory": 1000.0, "throughput": 50.0, "delay": 0.0}
        else:
            return {"metric_1": 0.0}

    def run_shadow_projection(self, twin_id: str, horizon_minutes: int = 60) -> List[TwinState]:
        """
        Run a Shadow Twin simulation to project the state into the future (1s to 60m).
        Uses a physics-based simulation model.
        """
        if twin_id not in self.twins:
            raise ValueError(f"Twin {twin_id} not found")

        twin = self.twins[twin_id]
        current_metrics = twin["current_state"]
        twin_type = twin["type"]
        
        logger.info(f"Running Shadow Projection for {twin_id} (Horizon: {horizon_minutes}m)...")
        
        projections = []
        start_time = datetime.now()
        
        # Simulation Loop (1 minute steps)
        current_sim_state = current_metrics.copy()
        
        for i in range(1, horizon_minutes + 1):
            future_time = start_time + timedelta(minutes=i)
            
            # Physics Simulation Logic
            next_state = self._simulate_step(twin_type, current_sim_state, i)
            current_sim_state = next_state
            
            # Determine Status
            status = "NOMINAL"
            if twin_type == "fusion_reactor" and next_state["stability"] < 0.8:
                status = "WARNING"
            if twin_type == "fusion_reactor" and next_state["stability"] < 0.5:
                status = "CRITICAL"
                
            projections.append(TwinState(
                timestamp=future_time,
                metrics=next_state,
                status=status
            ))

        # Store projections
        twin["shadow_projections"] = [
            {"timestamp": p.timestamp.isoformat(), "metrics": p.metrics, "status": p.status}
            for p in projections
        ]
        self._save_twin(twin_id)
        
        return projections

    def _simulate_step(self, twin_type: str, current_state: Dict[str, float], step_index: int) -> Dict[str, float]:
        """
        Simulate one time step based on physics/logic.
        """
        next_state = current_state.copy()
        
        # Add some entropy/drift
        noise = random.gauss(0, 0.01)
        
        if twin_type == "fusion_reactor":
            # Plasma instability grows over time if unchecked
            decay = 0.005 * step_index
            next_state["stability"] = max(0.0, min(1.0, current_state["stability"] - decay + noise))
            next_state["plasma_temp"] += noise * 10
            
        elif twin_type == "grid_substation":
            # Load fluctuates
            load_change = math.sin(step_index / 10.0) * 5
            next_state["load"] = max(0.0, current_state["load"] + load_change + noise)
            
        return next_state

    def generate_visualization(self, twin_id: str) -> str:
        """
        Generate or retrieve the 3D Gaussian Splatting visualization.
        """
        logger.info(f"Generating 3D Visualization for {twin_id}...")
        
        # In a real system, this would call self.gs_trainer.train_from_shadow_twin(...)
        # For this demo, we will mock the artifact generation if the trainer isn't fully set up
        
        artifact_path = os.path.join(self.storage_path, twin_id, f"{twin_id}.spx")
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        
        if not os.path.exists(artifact_path):
            with open(artifact_path, 'w') as f:
                f.write("MOCK_SPX_DATA") # Placeholder
            logger.info(f"Generated Mock Visualization at {artifact_path}")
            
        return artifact_path

    def _save_twin(self, twin_id: str):
        path = os.path.join(self.storage_path, f"{twin_id}.json")
        with open(path, 'w') as f:
            json.dump(self.twins[twin_id], f, indent=2)

    def get_twin(self, twin_id: str) -> Dict[str, Any]:
        return self.twins.get(twin_id)
