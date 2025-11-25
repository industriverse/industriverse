"""
Simulated Snapshot Service - Production Ready

Extends Energy Atlas to store and manage simulated energy snapshots
from WorldModel and ThermalSampler services.

Enables:
1. Sim vs real comparison for calibration
2. Provenance tracking for ProofEconomy
3. Simulator versioning and catalog
4. Energy signature validation
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
import numpy as np

# ============================================================================
# TYPES & ENUMS
# ============================================================================

class SnapshotType(str, Enum):
    """Type of energy snapshot"""
    REAL_MEASUREMENT = "real_measurement"
    WORLD_MODEL_SIM = "world_model_sim"
    THERMAL_SIM = "thermal_sim"
    HYBRID = "hybrid"

class CalibrationStatus(str, Enum):
    """Calibration status"""
    UNCALIBRATED = "uncalibrated"
    CALIBRATING = "calibrating"
    CALIBRATED = "calibrated"
    DRIFT_DETECTED = "drift_detected"

@dataclass
class SimulatorMetadata:
    """Metadata for simulator"""
    simulator_id: str
    simulator_type: str  # "world_model", "thermal_sampler"
    version: str
    domain: str
    physics_params: Dict[str, float]
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SimulatedSnapshot:
    """Simulated energy snapshot"""
    snapshot_id: str
    snapshot_type: SnapshotType
    simulator_id: str
    energy_map: np.ndarray
    energy_signature: str
    timestamp: datetime
    real_snapshot_id: Optional[str] = None  # Link to real measurement
    calibration_status: CalibrationStatus = CalibrationStatus.UNCALIBRATED
    calibration_error: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CalibrationResult:
    """Result from calibration"""
    calibration_id: str
    sim_snapshot_id: str
    real_snapshot_id: str
    error_metrics: Dict[str, float]
    correction_factors: Dict[str, float]
    calibration_status: CalibrationStatus
    timestamp: datetime

# ============================================================================
# SIMULATED SNAPSHOT SERVICE
# ============================================================================

class SimulatedSnapshotService:
    """
    Production-ready service for managing simulated energy snapshots.
    
    Integrates with Energy Atlas to provide sim/real comparison.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Storage
        self.simulators: Dict[str, SimulatorMetadata] = {}
        self.snapshots: Dict[str, SimulatedSnapshot] = {}
        self.calibrations: Dict[str, CalibrationResult] = {}
        
        # Statistics
        self.total_snapshots = 0
        self.total_calibrations = 0
    
    # ========================================================================
    # SIMULATOR CATALOG
    # ========================================================================
    
    def register_simulator(
        self,
        simulator_type: str,
        version: str,
        domain: str,
        physics_params: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a simulator in the catalog.
        
        Returns simulator_id for future reference.
        """
        simulator_id = self._generate_simulator_id(simulator_type, version, domain)
        
        simulator = SimulatorMetadata(
            simulator_id=simulator_id,
            simulator_type=simulator_type,
            version=version,
            domain=domain,
            physics_params=physics_params,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.simulators[simulator_id] = simulator
        return simulator_id
    
    def _generate_simulator_id(self, simulator_type: str, version: str, domain: str) -> str:
        """Generate unique simulator ID"""
        data = f"{simulator_type}_{version}_{domain}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_simulator(self, simulator_id: str) -> Optional[SimulatorMetadata]:
        """Get simulator metadata"""
        return self.simulators.get(simulator_id)
    
    def list_simulators(
        self,
        simulator_type: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[SimulatorMetadata]:
        """List simulators with optional filtering"""
        simulators = list(self.simulators.values())
        
        if simulator_type:
            simulators = [s for s in simulators if s.simulator_type == simulator_type]
        
        if domain:
            simulators = [s for s in simulators if s.domain == domain]
        
        return simulators
    
    # ========================================================================
    # SNAPSHOT MANAGEMENT
    # ========================================================================
    
    async def store_snapshot(
        self,
        snapshot_type: SnapshotType,
        simulator_id: str,
        energy_map: np.ndarray,
        real_snapshot_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a simulated energy snapshot.
        
        Args:
            snapshot_type: Type of snapshot
            simulator_id: ID of simulator that generated this
            energy_map: Energy field data
            real_snapshot_id: Optional link to real measurement
            metadata: Additional metadata
            
        Returns:
            snapshot_id
        """
        snapshot_id = self._generate_snapshot_id()
        
        # Compute energy signature
        energy_signature = self._compute_energy_signature(energy_map)
        
        # Determine calibration status
        calibration_status = CalibrationStatus.UNCALIBRATED
        calibration_error = None
        
        if real_snapshot_id:
            # Will be calibrated later
            calibration_status = CalibrationStatus.CALIBRATING
        
        snapshot = SimulatedSnapshot(
            snapshot_id=snapshot_id,
            snapshot_type=snapshot_type,
            simulator_id=simulator_id,
            energy_map=energy_map,
            energy_signature=energy_signature,
            timestamp=datetime.now(),
            real_snapshot_id=real_snapshot_id,
            calibration_status=calibration_status,
            calibration_error=calibration_error,
            metadata=metadata or {}
        )
        
        self.snapshots[snapshot_id] = snapshot
        self.total_snapshots += 1
        
        return snapshot_id
    
    def _generate_snapshot_id(self) -> str:
        """Generate unique snapshot ID"""
        return f"simsnapshot-{datetime.now().timestamp()}-{np.random.randint(10000)}"
    
    def _compute_energy_signature(self, energy_map: np.ndarray) -> str:
        """Compute unique energy signature from map"""
        # Compute statistical features
        mean = float(np.mean(energy_map))
        std = float(np.std(energy_map))
        min_val = float(np.min(energy_map))
        max_val = float(np.max(energy_map))
        
        # Create signature
        signature_data = f"{mean:.6f}_{std:.6f}_{min_val:.6f}_{max_val:.6f}"
        return hashlib.sha256(signature_data.encode()).hexdigest()[:32]
    
    def get_snapshot(self, snapshot_id: str) -> Optional[SimulatedSnapshot]:
        """Get snapshot by ID"""
        return self.snapshots.get(snapshot_id)
    
    def list_snapshots(
        self,
        snapshot_type: Optional[SnapshotType] = None,
        simulator_id: Optional[str] = None,
        calibration_status: Optional[CalibrationStatus] = None
    ) -> List[SimulatedSnapshot]:
        """List snapshots with optional filtering"""
        snapshots = list(self.snapshots.values())
        
        if snapshot_type:
            snapshots = [s for s in snapshots if s.snapshot_type == snapshot_type]
        
        if simulator_id:
            snapshots = [s for s in snapshots if s.simulator_id == simulator_id]
        
        if calibration_status:
            snapshots = [s for s in snapshots if s.calibration_status == calibration_status]
        
        return snapshots
    
    # ========================================================================
    # CALIBRATION
    # ========================================================================
    
    async def calibrate(
        self,
        sim_snapshot_id: str,
        real_snapshot_id: str,
        real_energy_map: np.ndarray
    ) -> CalibrationResult:
        """
        Calibrate simulated snapshot against real measurement.
        
        Computes error metrics and correction factors.
        """
        sim_snapshot = self.snapshots.get(sim_snapshot_id)
        if not sim_snapshot:
            raise ValueError(f"Simulated snapshot not found: {sim_snapshot_id}")
        
        # Compute error metrics
        error_metrics = self._compute_error_metrics(
            sim_snapshot.energy_map,
            real_energy_map
        )
        
        # Compute correction factors
        correction_factors = self._compute_correction_factors(
            sim_snapshot.energy_map,
            real_energy_map
        )
        
        # Determine calibration status
        mae = error_metrics["mae"]
        if mae < 0.1:
            calibration_status = CalibrationStatus.CALIBRATED
        elif mae < 0.5:
            calibration_status = CalibrationStatus.DRIFT_DETECTED
        else:
            calibration_status = CalibrationStatus.UNCALIBRATED
        
        # Create calibration result
        calibration_id = f"calib-{sim_snapshot_id}-{real_snapshot_id}"
        calibration = CalibrationResult(
            calibration_id=calibration_id,
            sim_snapshot_id=sim_snapshot_id,
            real_snapshot_id=real_snapshot_id,
            error_metrics=error_metrics,
            correction_factors=correction_factors,
            calibration_status=calibration_status,
            timestamp=datetime.now()
        )
        
        self.calibrations[calibration_id] = calibration
        self.total_calibrations += 1
        
        # Update snapshot
        sim_snapshot.calibration_status = calibration_status
        sim_snapshot.calibration_error = mae
        sim_snapshot.real_snapshot_id = real_snapshot_id
        
        return calibration
    
    def _compute_error_metrics(
        self,
        sim_map: np.ndarray,
        real_map: np.ndarray
    ) -> Dict[str, float]:
        """Compute error metrics between sim and real"""
        # Ensure same shape
        if sim_map.shape != real_map.shape:
            # Resize if needed (simple interpolation)
            from scipy.ndimage import zoom
            scale_factors = np.array(real_map.shape) / np.array(sim_map.shape)
            sim_map = zoom(sim_map, scale_factors, order=1)
        
        # Mean Absolute Error
        mae = float(np.mean(np.abs(sim_map - real_map)))
        
        # Root Mean Square Error
        rmse = float(np.sqrt(np.mean((sim_map - real_map) ** 2)))
        
        # Relative Error
        relative_error = float(np.mean(np.abs(sim_map - real_map) / (np.abs(real_map) + 1e-10)))
        
        # Correlation
        sim_flat = sim_map.flatten()
        real_flat = real_map.flatten()
        correlation = float(np.corrcoef(sim_flat, real_flat)[0, 1])
        
        return {
            "mae": mae,
            "rmse": rmse,
            "relative_error": relative_error,
            "correlation": correlation
        }
    
    def _compute_correction_factors(
        self,
        sim_map: np.ndarray,
        real_map: np.ndarray
    ) -> Dict[str, float]:
        """Compute correction factors for calibration"""
        # Scale factor
        sim_mean = np.mean(sim_map)
        real_mean = np.mean(real_map)
        scale_factor = float(real_mean / (sim_mean + 1e-10))
        
        # Offset
        offset = float(real_mean - sim_mean)
        
        # Variance ratio
        sim_std = np.std(sim_map)
        real_std = np.std(real_map)
        variance_ratio = float(real_std / (sim_std + 1e-10))
        
        return {
            "scale_factor": scale_factor,
            "offset": offset,
            "variance_ratio": variance_ratio
        }
    
    async def apply_calibration(
        self,
        snapshot_id: str,
        calibration_id: str
    ) -> np.ndarray:
        """Apply calibration correction to snapshot"""
        snapshot = self.snapshots.get(snapshot_id)
        calibration = self.calibrations.get(calibration_id)
        
        if not snapshot or not calibration:
            raise ValueError("Snapshot or calibration not found")
        
        # Apply correction factors
        corrected_map = snapshot.energy_map.copy()
        corrected_map = corrected_map * calibration.correction_factors["scale_factor"]
        corrected_map = corrected_map + calibration.correction_factors["offset"]
        
        return corrected_map
    
    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================
    
    async def batch_calibrate(
        self,
        sim_snapshot_ids: List[str],
        real_snapshot_ids: List[str],
        real_energy_maps: List[np.ndarray]
    ) -> List[CalibrationResult]:
        """Calibrate multiple snapshots in parallel"""
        if len(sim_snapshot_ids) != len(real_snapshot_ids) or len(sim_snapshot_ids) != len(real_energy_maps):
            raise ValueError("Input lists must have same length")
        
        tasks = [
            self.calibrate(sim_id, real_id, real_map)
            for sim_id, real_id, real_map in zip(sim_snapshot_ids, real_snapshot_ids, real_energy_maps)
        ]
        
        return await asyncio.gather(*tasks)
    
    # ========================================================================
    # STATISTICS & MONITORING
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        # Calibration statistics
        calibrated_count = len([
            s for s in self.snapshots.values()
            if s.calibration_status == CalibrationStatus.CALIBRATED
        ])
        
        # Average calibration error
        calibrated_snapshots = [
            s for s in self.snapshots.values()
            if s.calibration_error is not None
        ]
        avg_error = np.mean([s.calibration_error for s in calibrated_snapshots]) if calibrated_snapshots else 0.0
        
        return {
            "total_simulators": len(self.simulators),
            "total_snapshots": self.total_snapshots,
            "total_calibrations": self.total_calibrations,
            "calibrated_snapshots": calibrated_count,
            "average_calibration_error": float(avg_error),
            "calibration_rate": calibrated_count / max(self.total_snapshots, 1)
        }
    
    def get_simulator_statistics(self, simulator_id: str) -> Dict[str, Any]:
        """Get statistics for specific simulator"""
        snapshots = [s for s in self.snapshots.values() if s.simulator_id == simulator_id]
        
        if not snapshots:
            return {}
        
        calibrated = [s for s in snapshots if s.calibration_status == CalibrationStatus.CALIBRATED]
        
        return {
            "total_snapshots": len(snapshots),
            "calibrated_snapshots": len(calibrated),
            "calibration_rate": len(calibrated) / len(snapshots),
            "average_error": np.mean([s.calibration_error for s in calibrated if s.calibration_error is not None])
        }
    
    # ========================================================================
    # SERIALIZATION
    # ========================================================================
    
    def snapshot_to_dict(self, snapshot: SimulatedSnapshot) -> Dict[str, Any]:
        """Convert snapshot to dictionary"""
        return {
            "snapshot_id": snapshot.snapshot_id,
            "snapshot_type": snapshot.snapshot_type.value,
            "simulator_id": snapshot.simulator_id,
            "energy_signature": snapshot.energy_signature,
            "timestamp": snapshot.timestamp.isoformat(),
            "real_snapshot_id": snapshot.real_snapshot_id,
            "calibration_status": snapshot.calibration_status.value,
            "calibration_error": snapshot.calibration_error,
            "metadata": snapshot.metadata
        }
    
    def calibration_to_dict(self, calibration: CalibrationResult) -> Dict[str, Any]:
        """Convert calibration to dictionary"""
        return {
            "calibration_id": calibration.calibration_id,
            "sim_snapshot_id": calibration.sim_snapshot_id,
            "real_snapshot_id": calibration.real_snapshot_id,
            "error_metrics": calibration.error_metrics,
            "correction_factors": calibration.correction_factors,
            "calibration_status": calibration.calibration_status.value,
            "timestamp": calibration.timestamp.isoformat()
        }

# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_simulated_snapshot_service(config: Optional[Dict[str, Any]] = None) -> SimulatedSnapshotService:
    """Factory function to create simulated snapshot service"""
    return SimulatedSnapshotService(config)
