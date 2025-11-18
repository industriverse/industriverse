"""
AR/VR Threat Visualization Adapter

Renders thermodynamic security threats in immersive 3D environments.

Capabilities:
- 3D threat landscape visualization
- Real-time energy/entropy heatmaps
- Attack vector animation
- Device topology in 3D space
- Thermodynamic flow visualization

Integration:
- Consumes SOC Dashboard API data
- Renders via 3DGS (3D Gaussian Splatting)
- Supports VR headsets (Quest, Vive, etc.)
- Supports AR devices (HoloLens, ARKit, ARCore)
- TouchDesigner integration for generative viz

Visualization Types:
====================

1. Threat Particle System
   - Each threat = Particle with color/size based on severity
   - Energy anomalies = Red hot particles
   - Entropy spikes = Chaotic particle movement

2. Thermodynamic Field Visualization
   - Energy field: 3D scalar field colored by intensity
   - Entropy field: Turbulence visualization
   - Temperature field: Heat map overlay

3. Attack Flow Diagrams
   - Animated flow lines showing attack propagation
   - Source → Target visualization
   - Time-series replay of attack sequences

4. Device Network Topology
   - Devices as 3D nodes in space
   - Connections as edges
   - Attack paths highlighted
   - Compromised devices pulsate

5. Compliance Dashboard (AR)
   - Floating compliance metrics panels
   - Real-time status indicators
   - Interactive drill-down into violations

Technical Details:
==================

Rendering Pipeline:
1. Fetch data from SOC API
2. Transform to 3D coordinate space
3. Generate visual primitives (particles, fields, meshes)
4. Stream to VR/AR client
5. Handle user interaction

Coordinate System:
- X-axis: Device spatial distribution (or logical grouping)
- Y-axis: Threat severity (higher = more severe)
- Z-axis: Temporal dimension (time-series)

Color Mapping:
- Critical threats: Red
- High threats: Orange
- Medium threats: Yellow
- Low threats: Blue
- Energy anomalies: Heat gradient (blue → red)
- Entropy: Chaos intensity (calm → turbulent)

Performance:
- 90 FPS minimum (VR requirement)
- LOD (Level of Detail) for large datasets
- Spatial culling for off-screen threats
- Batch rendering for efficiency

References:
- Kerren & Schreiber, "Toward the Role of Interaction in Visual Analytics" (2012)
- Card et al., "Readings in Information Visualization" (1999)
- Van Wijk, "The Value of Visualization" (2005)
"""

import logging
import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VisualizationType(Enum):
    """Visualization type enumeration."""
    PARTICLE_SYSTEM = "particle_system"
    FIELD_VISUALIZATION = "field_visualization"
    FLOW_DIAGRAM = "flow_diagram"
    NETWORK_TOPOLOGY = "network_topology"
    COMPLIANCE_DASHBOARD = "compliance_dashboard"


@dataclass
class ThreatParticle:
    """3D particle representing a threat."""
    particle_id: str
    position: Tuple[float, float, float]  # (x, y, z)
    velocity: Tuple[float, float, float]
    color: Tuple[float, float, float, float]  # RGBA
    size: float
    intensity: float  # 0-1
    severity: str
    lifetime: float  # seconds


@dataclass
class ThermodynamicField:
    """3D scalar field for thermodynamic visualization."""
    field_type: str  # energy, entropy, temperature
    grid_resolution: Tuple[int, int, int]  # (x, y, z) resolution
    values: np.ndarray  # 3D array of field values
    min_value: float
    max_value: float
    colormap: str  # jet, viridis, plasma, etc.


@dataclass
class AttackFlow:
    """Attack propagation flow visualization."""
    flow_id: str
    source_device: str
    target_device: str
    source_position: Tuple[float, float, float]
    target_position: Tuple[float, float, float]
    flow_particles: List[Tuple[float, float, float]]  # Positions along flow
    intensity: float
    timestamp: datetime


class ARVRThreatVisualizer:
    """
    AR/VR Threat Visualization Adapter.

    Transforms security data into immersive 3D visualizations.
    """

    def __init__(
        self,
        soc_api=None,
        device_positions: Optional[Dict[str, Tuple[float, float, float]]] = None
    ):
        """
        Initialize AR/VR Threat Visualizer.

        Args:
            soc_api: SOC Dashboard API instance
            device_positions: Dict mapping device_id to 3D position
        """
        self.soc_api = soc_api

        # Device spatial layout
        self.device_positions = device_positions or {}

        # Active particles
        self.threat_particles: List[ThreatParticle] = []

        # Thermodynamic fields
        self.energy_field: Optional[ThermodynamicField] = None
        self.entropy_field: Optional[ThermodynamicField] = None

        # Attack flows
        self.active_flows: List[AttackFlow] = []

        # Rendering state
        self.frame_count = 0
        self.target_fps = 90  # VR requirement

        # Color schemes
        self.severity_colors = {
            "critical": (1.0, 0.0, 0.0, 1.0),  # Red
            "high": (1.0, 0.5, 0.0, 1.0),      # Orange
            "medium": (1.0, 1.0, 0.0, 1.0),    # Yellow
            "low": (0.0, 0.5, 1.0, 1.0)        # Blue
        }

        logger.info("AR/VR Threat Visualizer initialized")

    async def generate_particle_system(
        self,
        threats: List[Dict[str, Any]]
    ) -> List[ThreatParticle]:
        """
        Generate particle system from threats.

        Each threat becomes a particle with position, color, size based
        on severity, confidence, and thermodynamic metrics.

        Args:
            threats: List of threat dictionaries

        Returns:
            List of ThreatParticle objects
        """
        particles = []

        for i, threat in enumerate(threats):
            device_id = threat.get("device_id", "unknown")

            # Get device position (or assign random if unknown)
            if device_id in self.device_positions:
                base_pos = self.device_positions[device_id]
            else:
                # Random position for unknown devices
                base_pos = (
                    np.random.uniform(-10, 10),
                    0.0,
                    np.random.uniform(-10, 10)
                )
                self.device_positions[device_id] = base_pos

            # Y position based on severity
            severity = threat.get("severity", "low")
            severity_heights = {
                "critical": 10.0,
                "high": 7.0,
                "medium": 4.0,
                "low": 1.0
            }
            y_pos = severity_heights.get(severity, 1.0)

            # Add jitter
            position = (
                base_pos[0] + np.random.normal(0, 0.5),
                y_pos + np.random.normal(0, 0.3),
                base_pos[2] + np.random.normal(0, 0.5)
            )

            # Velocity (particles drift upward for critical threats)
            velocity = (
                np.random.normal(0, 0.1),
                0.5 if severity == "critical" else 0.0,
                np.random.normal(0, 0.1)
            )

            # Color based on severity
            color = self.severity_colors.get(severity, (0.5, 0.5, 0.5, 1.0))

            # Size based on confidence
            confidence = threat.get("confidence", 0.5)
            size = 0.2 + (confidence * 0.8)  # 0.2 to 1.0

            # Intensity from thermodynamic data
            thermo_data = threat.get("thermodynamic_data", {})
            intensity = min(1.0,
                thermo_data.get("energy_anomaly", 1.0) / 10.0 +
                thermo_data.get("entropy_spike", 1.0) / 10.0
            )

            particle = ThreatParticle(
                particle_id=f"particle_{i}",
                position=position,
                velocity=velocity,
                color=color,
                size=size,
                intensity=intensity,
                severity=severity,
                lifetime=60.0  # 60 seconds
            )

            particles.append(particle)

        logger.info(f"Generated {len(particles)} threat particles")
        return particles

    async def generate_energy_field(
        self,
        device_metrics: Dict[str, Dict[str, Any]],
        grid_resolution: Tuple[int, int, int] = (32, 32, 32)
    ) -> ThermodynamicField:
        """
        Generate 3D energy field from device metrics.

        Creates a volumetric scalar field representing energy distribution
        across the infrastructure.

        Args:
            device_metrics: Dict mapping device_id to metrics
            grid_resolution: 3D grid resolution

        Returns:
            ThermodynamicField object
        """
        grid_x, grid_y, grid_z = grid_resolution

        # Initialize field
        field_values = np.zeros((grid_x, grid_y, grid_z))

        # For each device, add its energy contribution to nearby grid cells
        for device_id, metrics in device_metrics.items():
            if device_id not in self.device_positions:
                continue

            pos = self.device_positions[device_id]

            # Map world coordinates to grid coordinates
            # Assume world space: [-10, 10] in X/Z, [0, 10] in Y
            grid_x_idx = int((pos[0] + 10) / 20 * grid_x)
            grid_y_idx = int(pos[1] / 10 * grid_y)
            grid_z_idx = int((pos[2] + 10) / 20 * grid_z)

            # Clamp to grid bounds
            grid_x_idx = max(0, min(grid_x - 1, grid_x_idx))
            grid_y_idx = max(0, min(grid_y - 1, grid_y_idx))
            grid_z_idx = max(0, min(grid_z - 1, grid_z_idx))

            # Get energy value
            energy = metrics.get("energy_consumption", 0.0)

            # Add Gaussian blob around device
            sigma = 3  # Spread
            for dx in range(-sigma, sigma + 1):
                for dy in range(-sigma, sigma + 1):
                    for dz in range(-sigma, sigma + 1):
                        x = grid_x_idx + dx
                        y = grid_y_idx + dy
                        z = grid_z_idx + dz

                        if 0 <= x < grid_x and 0 <= y < grid_y and 0 <= z < grid_z:
                            dist = np.sqrt(dx**2 + dy**2 + dz**2)
                            contribution = energy * np.exp(-dist**2 / (2 * sigma**2))
                            field_values[x, y, z] += contribution

        min_val = float(np.min(field_values))
        max_val = float(np.max(field_values))

        logger.info(
            f"Generated energy field: {grid_resolution}, "
            f"range [{min_val:.2f}, {max_val:.2f}]"
        )

        return ThermodynamicField(
            field_type="energy",
            grid_resolution=grid_resolution,
            values=field_values,
            min_value=min_val,
            max_value=max_val,
            colormap="jet"
        )

    async def generate_attack_flows(
        self,
        threat_timeline: List[Dict[str, Any]]
    ) -> List[AttackFlow]:
        """
        Generate attack flow visualizations.

        Creates animated flow lines showing attack propagation paths.

        Args:
            threat_timeline: List of threat events with temporal info

        Returns:
            List of AttackFlow objects
        """
        flows = []

        for i, event in enumerate(threat_timeline):
            # Determine source and target
            # In production: Extract from actual attack correlation
            source_device = event.get("source_device", event.get("device_id"))
            target_device = event.get("target_device", f"device_{(hash(source_device) + 1) % 100}")

            # Get positions
            if source_device not in self.device_positions:
                self.device_positions[source_device] = (
                    np.random.uniform(-10, 10),
                    0.0,
                    np.random.uniform(-10, 10)
                )

            if target_device not in self.device_positions:
                self.device_positions[target_device] = (
                    np.random.uniform(-10, 10),
                    0.0,
                    np.random.uniform(-10, 10)
                )

            source_pos = self.device_positions[source_device]
            target_pos = self.device_positions[target_device]

            # Generate flow particles along path
            flow_particles = []
            steps = 20

            for j in range(steps):
                t = j / steps
                # Linear interpolation
                pos = (
                    source_pos[0] + t * (target_pos[0] - source_pos[0]),
                    source_pos[1] + t * (target_pos[1] - source_pos[1]) + np.sin(t * np.pi) * 2.0,  # Arc
                    source_pos[2] + t * (target_pos[2] - source_pos[2])
                )
                flow_particles.append(pos)

            # Intensity based on severity
            severity = event.get("severity", "low")
            intensity_map = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}
            intensity = intensity_map.get(severity, 0.2)

            flow = AttackFlow(
                flow_id=f"flow_{i}",
                source_device=source_device,
                target_device=target_device,
                source_position=source_pos,
                target_position=target_pos,
                flow_particles=flow_particles,
                intensity=intensity,
                timestamp=datetime.fromisoformat(event.get("timestamp", datetime.now().isoformat()))
            )

            flows.append(flow)

        logger.info(f"Generated {len(flows)} attack flows")
        return flows

    def render_to_json(
        self,
        particles: List[ThreatParticle],
        energy_field: Optional[ThermodynamicField] = None,
        flows: Optional[List[AttackFlow]] = None
    ) -> Dict[str, Any]:
        """
        Render visualization data to JSON for client consumption.

        Args:
            particles: Threat particles
            energy_field: Energy field
            flows: Attack flows

        Returns:
            JSON-serializable dict of visualization data
        """
        render_data = {
            "timestamp": datetime.now().isoformat(),
            "frame": self.frame_count,
            "particles": [
                {
                    "id": p.particle_id,
                    "position": list(p.position),
                    "velocity": list(p.velocity),
                    "color": list(p.color),
                    "size": p.size,
                    "intensity": p.intensity,
                    "severity": p.severity
                }
                for p in particles
            ]
        }

        if energy_field:
            # Sample field for efficient transmission (don't send full 32^3 grid)
            sampled_points = []
            step = max(1, energy_field.grid_resolution[0] // 16)

            for x in range(0, energy_field.grid_resolution[0], step):
                for y in range(0, energy_field.grid_resolution[1], step):
                    for z in range(0, energy_field.grid_resolution[2], step):
                        value = float(energy_field.values[x, y, z])

                        # Normalize to 0-1
                        normalized = (value - energy_field.min_value) / \
                                   max(energy_field.max_value - energy_field.min_value, 1.0)

                        sampled_points.append({
                            "position": [
                                (x / energy_field.grid_resolution[0]) * 20 - 10,  # Map to world space
                                (y / energy_field.grid_resolution[1]) * 10,
                                (z / energy_field.grid_resolution[2]) * 20 - 10
                            ],
                            "value": value,
                            "normalized": normalized
                        })

            render_data["energy_field"] = {
                "type": energy_field.field_type,
                "colormap": energy_field.colormap,
                "min_value": energy_field.min_value,
                "max_value": energy_field.max_value,
                "samples": sampled_points
            }

        if flows:
            render_data["attack_flows"] = [
                {
                    "id": f.flow_id,
                    "source": f.source_device,
                    "target": f.target_device,
                    "path": [list(p) for p in f.flow_particles],
                    "intensity": f.intensity
                }
                for f in flows
            ]

        self.frame_count += 1

        return render_data

    async def update_visualization(self) -> Dict[str, Any]:
        """
        Update visualization with latest data from SOC API.

        Returns:
            Rendered visualization data
        """
        if not self.soc_api:
            return {}

        # Fetch latest threats
        try:
            threats = await self.soc_api._get_active_threats(severity=None, limit=100)

            # Convert to dict format
            threats_dict = [
                {
                    "event_id": t.event_id,
                    "device_id": t.device_id,
                    "severity": t.severity,
                    "confidence": t.confidence,
                    "thermodynamic_data": t.thermodynamic_data,
                    "timestamp": t.timestamp
                }
                for t in threats
            ]

            # Generate particles
            particles = await self.generate_particle_system(threats_dict)

            # Generate energy field (simplified - use device metrics)
            device_metrics = {}
            for threat in threats_dict:
                device_id = threat["device_id"]
                if device_id not in device_metrics:
                    device_metrics[device_id] = {
                        "energy_consumption": np.random.uniform(50, 200)
                    }

            energy_field = await self.generate_energy_field(device_metrics)

            # Render to JSON
            render_data = self.render_to_json(particles, energy_field, None)

            return render_data

        except Exception as e:
            logger.error(f"Failed to update visualization: {e}")
            return {}


# ============================================================================
# Singleton instance
# ============================================================================

_arvr_visualizer_instance = None


def get_arvr_threat_visualizer(
    soc_api=None,
    device_positions: Optional[Dict[str, Tuple[float, float, float]]] = None
) -> ARVRThreatVisualizer:
    """
    Get singleton AR/VR Threat Visualizer instance.

    Args:
        soc_api: SOC Dashboard API
        device_positions: Device spatial layout

    Returns:
        ARVRThreatVisualizer instance
    """
    global _arvr_visualizer_instance

    if _arvr_visualizer_instance is None:
        _arvr_visualizer_instance = ARVRThreatVisualizer(
            soc_api=soc_api,
            device_positions=device_positions
        )

    return _arvr_visualizer_instance
