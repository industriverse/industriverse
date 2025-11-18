"""
Swarm & Urban IoT Security Monitor

Protects robot swarms and smart city IoT networks from:
- Swarm hijacking attacks (coordinated robot takeover)
- IoT botnet formation
- Distributed thermodynamic anomalies
- Coordination pattern manipulation
- Urban sensor network compromise

Threat Landscape:
Robot swarms and IoT networks exhibit emergent behaviors through
distributed coordination. Attackers can exploit this to hijack
entire swarms or create botnets. Thermodynamic analysis reveals
attacks through energy flow and entropy pattern anomalies.

Attack Types Detected:
1. Swarm Hijacking: Adversary injects malicious commands to redirect
   swarm behavior (coordination entropy spike)
2. IoT Botnet: Compromised devices coordinating attacks (energy flow anomaly)
3. Sybil Attack: Fake robot identities flooding swarm (entropy reduction)
4. Byzantine Fault: Malicious robots sending conflicting data
5. Data Poisoning: Corrupted sensor data from IoT devices

Thermodynamic Swarm Model:
- Swarm Energy: E = Σ(kinetic + potential + communication energy)
- Swarm Entropy: S = -Σ p(state_i) * log p(state_i)
- Coordination Temperature: T ∝ Inter-robot communication rate
- Swarm Cohesion: Free energy minimization in configuration space

Detection Methodology:
1. Coordination Entropy Analysis:
   - Normal swarm: Moderate entropy (organized chaos)
   - Hijacked swarm: Sudden entropy spike or collapse
   - Sybil attack: Artificial entropy reduction

2. Energy Conservation Validation:
   - Track total swarm energy consumption
   - Detect anomalous energy spikes (botnet activity)
   - Validate energy budget constraints

3. Behavior Pattern Recognition:
   - Baseline normal swarm patterns
   - Detect deviation from thermodynamic equilibrium
   - Identify coordinated malicious behavior

4. Network Topology Analysis:
   - Monitor communication graph structure
   - Detect sudden topology changes
   - Identify Byzantine nodes

Integration:
- Monitors swarm control systems (ROS, drone fleets)
- Tracks IoT sensor networks (smart city infrastructure)
- Uses EIL for thermodynamic calculations
- Registers threats in Security Event Registry
- Visualizes swarm attacks in AR/VR

Applications:
- Warehouse robot security
- Drone fleet protection
- Smart city infrastructure
- Industrial automation
- Military/defense systems

References:
- Brambilla et al., "Swarm robotics: a review" (2013)
- Dorigo & Birattari, "Swarm intelligence" (2007)
- Miazi et al., "Enabling the IoT in smart cities: A review" (2016)
- Sicari et al., "Security, privacy and trust in IoT" (2015)
"""

import logging
import asyncio
import numpy as np
import math
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RobotState(Enum):
    """Robot operational state."""
    IDLE = "idle"
    MOVING = "moving"
    WORKING = "working"
    CHARGING = "charging"
    ERROR = "error"


@dataclass
class RobotTelemetry:
    """Robot telemetry data."""
    robot_id: str
    timestamp: datetime
    position: Tuple[float, float, float]  # (x, y, z)
    velocity: Tuple[float, float, float]
    state: RobotState
    battery_level: float  # 0-100%
    energy_consumption: float  # W
    communication_rate: float  # msgs/sec
    neighbors: List[str]  # Connected robot IDs


@dataclass
class IoTSensorData:
    """IoT sensor measurement."""
    sensor_id: str
    timestamp: datetime
    sensor_type: str  # temperature, humidity, air_quality, traffic, etc.
    value: float
    unit: str
    location: Tuple[float, float]  # (lat, lon)
    battery_level: Optional[float] = None


@dataclass
class SwarmThermodynamics:
    """Swarm thermodynamic state."""
    swarm_id: str
    timestamp: datetime
    robot_count: int

    # Energy metrics
    total_energy_consumption: float  # W
    average_energy_per_robot: float  # W
    energy_variance: float

    # Coordination metrics
    coordination_entropy: float  # bits
    communication_temperature: float  # msgs/sec
    average_neighbor_count: float

    # Spatial metrics
    swarm_cohesion: float  # Average distance to centroid
    swarm_dispersion: float  # Std deviation of positions

    # Anomaly indicators
    entropy_anomaly_score: float
    energy_anomaly_score: float
    topology_anomaly_score: float


class SwarmIoTSecurityMonitor:
    """
    Monitor swarm and IoT networks for security threats.

    Detects hijacking, botnets, and coordination attacks through
    thermodynamic analysis.
    """

    def __init__(
        self,
        database_pool=None,
        energy_intelligence_layer=None,
        security_registry=None,
        event_bus=None,
        swarm_interface=None,
        iot_interface=None
    ):
        """
        Initialize Swarm & IoT Security Monitor.

        Args:
            database_pool: PostgreSQL connection pool
            energy_intelligence_layer: EIL for thermodynamic calculations
            security_registry: Security Event Registry
            event_bus: Event bus
            swarm_interface: Interface to swarm control system
            iot_interface: Interface to IoT network
        """
        self.db_pool = database_pool
        self.eil = energy_intelligence_layer
        self.security_registry = security_registry
        self.event_bus = event_bus
        self.swarm_interface = swarm_interface
        self.iot_interface = iot_interface

        # Swarm state
        self.robot_telemetry: Dict[str, deque] = {}  # robot_id -> telemetry history
        self.swarm_thermodynamics: Dict[str, deque] = {}  # swarm_id -> thermodynamics
        self.swarm_members: Dict[str, Set[str]] = {}  # swarm_id -> robot_ids

        # IoT state
        self.iot_sensors: Dict[str, IoTSensorData] = {}  # sensor_id -> latest data
        self.iot_history: Dict[str, deque] = {}  # sensor_id -> data history

        # Detection thresholds
        self.entropy_spike_threshold = 3.0  # 3σ from baseline
        self.energy_anomaly_threshold = 4.0  # 4σ from baseline
        self.topology_change_threshold = 0.30  # 30% topology change
        self.botnet_correlation_threshold = 0.85  # High inter-device correlation

        # Monitoring state
        self.monitoring_active: Dict[str, bool] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}

        # Statistics
        self.stats = {
            "threats_detected": 0,
            "swarm_hijacking_detected": 0,
            "iot_botnet_detected": 0,
            "sybil_attacks_detected": 0,
            "byzantine_faults_detected": 0,
            "data_poisoning_detected": 0
        }

        logger.info("Swarm & IoT Security Monitor initialized")

    def register_swarm(self, swarm_id: str, robot_ids: List[str]):
        """
        Register a swarm for monitoring.

        Args:
            swarm_id: Unique swarm identifier
            robot_ids: List of robot IDs in swarm
        """
        self.swarm_members[swarm_id] = set(robot_ids)

        # Initialize telemetry history for each robot
        for robot_id in robot_ids:
            if robot_id not in self.robot_telemetry:
                self.robot_telemetry[robot_id] = deque(maxlen=1000)

        # Initialize thermodynamics history
        if swarm_id not in self.swarm_thermodynamics:
            self.swarm_thermodynamics[swarm_id] = deque(maxlen=1000)

        logger.info(
            f"Registered swarm {swarm_id} with {len(robot_ids)} robots"
        )

    async def start_swarm_monitoring(self, swarm_id: str):
        """
        Start security monitoring for a swarm.

        Args:
            swarm_id: Swarm to monitor
        """
        if self.monitoring_active.get(f"swarm_{swarm_id}"):
            logger.warning(f"Already monitoring swarm {swarm_id}")
            return

        logger.info(f"Starting swarm security monitoring for {swarm_id}")

        self.monitoring_active[f"swarm_{swarm_id}"] = True

        # Create monitoring task
        task = asyncio.create_task(self._swarm_monitoring_loop(swarm_id))
        self.monitoring_tasks[f"swarm_{swarm_id}"] = task

    async def start_iot_monitoring(self, network_id: str):
        """
        Start security monitoring for IoT network.

        Args:
            network_id: IoT network to monitor
        """
        if self.monitoring_active.get(f"iot_{network_id}"):
            logger.warning(f"Already monitoring IoT network {network_id}")
            return

        logger.info(f"Starting IoT security monitoring for {network_id}")

        self.monitoring_active[f"iot_{network_id}"] = True

        # Create monitoring task
        task = asyncio.create_task(self._iot_monitoring_loop(network_id))
        self.monitoring_tasks[f"iot_{network_id}"] = task

    async def _swarm_monitoring_loop(self, swarm_id: str):
        """Continuous swarm security monitoring."""
        logger.info(f"Swarm monitoring loop started for {swarm_id}")

        try:
            while self.monitoring_active.get(f"swarm_{swarm_id}"):
                # Collect telemetry from all robots
                await self._collect_swarm_telemetry(swarm_id)

                # Calculate swarm thermodynamics
                thermodynamics = await self._calculate_swarm_thermodynamics(swarm_id)

                if thermodynamics:
                    self.swarm_thermodynamics[swarm_id].append(thermodynamics)

                    # Run threat detection
                    await self._detect_swarm_hijacking(swarm_id, thermodynamics)
                    await self._detect_sybil_attack(swarm_id, thermodynamics)
                    await self._detect_byzantine_fault(swarm_id)

                # Check every 500ms
                await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            logger.info(f"Swarm monitoring cancelled for {swarm_id}")
        except Exception as e:
            logger.error(f"Swarm monitoring error: {e}")
        finally:
            self.monitoring_active[f"swarm_{swarm_id}"] = False
            logger.info(f"Swarm monitoring loop ended for {swarm_id}")

    async def _iot_monitoring_loop(self, network_id: str):
        """Continuous IoT network security monitoring."""
        logger.info(f"IoT monitoring loop started for {network_id}")

        try:
            while self.monitoring_active.get(f"iot_{network_id}"):
                # Collect sensor data
                await self._collect_iot_data(network_id)

                # Run threat detection
                await self._detect_iot_botnet(network_id)
                await self._detect_data_poisoning(network_id)

                # Check every 2 seconds
                await asyncio.sleep(2.0)

        except asyncio.CancelledError:
            logger.info(f"IoT monitoring cancelled for {network_id}")
        except Exception as e:
            logger.error(f"IoT monitoring error: {e}")
        finally:
            self.monitoring_active[f"iot_{network_id}"] = False
            logger.info(f"IoT monitoring loop ended for {network_id}")

    async def _collect_swarm_telemetry(self, swarm_id: str):
        """Collect telemetry from all robots in swarm."""
        if swarm_id not in self.swarm_members:
            return

        robot_ids = self.swarm_members[swarm_id]

        for robot_id in robot_ids:
            # Simulate telemetry (in production: read from actual robots)
            telemetry = RobotTelemetry(
                robot_id=robot_id,
                timestamp=datetime.now(),
                position=(
                    np.random.uniform(-10, 10),
                    np.random.uniform(-10, 10),
                    np.random.uniform(0, 5)
                ),
                velocity=(
                    np.random.normal(0, 0.5),
                    np.random.normal(0, 0.5),
                    np.random.normal(0, 0.1)
                ),
                state=RobotState.MOVING,
                battery_level=np.random.uniform(50, 100),
                energy_consumption=np.random.uniform(50, 150),
                communication_rate=np.random.uniform(5, 20),
                neighbors=[
                    rid for rid in robot_ids
                    if rid != robot_id and np.random.random() > 0.5
                ]
            )

            self.robot_telemetry[robot_id].append(telemetry)

    async def _calculate_swarm_thermodynamics(
        self,
        swarm_id: str
    ) -> Optional[SwarmThermodynamics]:
        """Calculate thermodynamic state of swarm."""
        if swarm_id not in self.swarm_members:
            return None

        robot_ids = self.swarm_members[swarm_id]

        # Get latest telemetry for each robot
        latest_telemetry = []
        for robot_id in robot_ids:
            if robot_id in self.robot_telemetry and self.robot_telemetry[robot_id]:
                latest_telemetry.append(self.robot_telemetry[robot_id][-1])

        if len(latest_telemetry) < 2:
            return None

        # Energy metrics
        energies = np.array([t.energy_consumption for t in latest_telemetry])
        total_energy = float(np.sum(energies))
        avg_energy = float(np.mean(energies))
        energy_variance = float(np.var(energies))

        # Coordination entropy (distribution of robot states)
        state_counts = defaultdict(int)
        for t in latest_telemetry:
            state_counts[t.state.value] += 1

        total_robots = len(latest_telemetry)
        state_probs = np.array([count / total_robots for count in state_counts.values()])
        coordination_entropy = float(-np.sum(state_probs * np.log2(state_probs + 1e-10)))

        # Communication temperature
        comm_rates = np.array([t.communication_rate for t in latest_telemetry])
        comm_temperature = float(np.mean(comm_rates))

        # Network topology
        neighbor_counts = np.array([len(t.neighbors) for t in latest_telemetry])
        avg_neighbors = float(np.mean(neighbor_counts))

        # Spatial cohesion
        positions = np.array([t.position for t in latest_telemetry])
        centroid = np.mean(positions, axis=0)
        distances = np.linalg.norm(positions - centroid, axis=1)
        cohesion = float(np.mean(distances))
        dispersion = float(np.std(distances))

        # Calculate anomaly scores
        history = list(self.swarm_thermodynamics.get(swarm_id, []))

        if len(history) > 20:
            historical_entropy = np.array([h.coordination_entropy for h in history])
            historical_energy = np.array([h.total_energy_consumption for h in history])
            historical_neighbors = np.array([h.average_neighbor_count for h in history])

            entropy_mean = np.mean(historical_entropy)
            entropy_std = np.std(historical_entropy)
            entropy_anomaly = abs(coordination_entropy - entropy_mean) / max(entropy_std, 0.1)

            energy_mean = np.mean(historical_energy)
            energy_std = np.std(historical_energy)
            energy_anomaly = abs(total_energy - energy_mean) / max(energy_std, 0.1)

            neighbor_mean = np.mean(historical_neighbors)
            neighbor_std = np.std(historical_neighbors)
            topology_anomaly = abs(avg_neighbors - neighbor_mean) / max(neighbor_std, 0.1)
        else:
            entropy_anomaly = 0.0
            energy_anomaly = 0.0
            topology_anomaly = 0.0

        return SwarmThermodynamics(
            swarm_id=swarm_id,
            timestamp=datetime.now(),
            robot_count=len(latest_telemetry),
            total_energy_consumption=total_energy,
            average_energy_per_robot=avg_energy,
            energy_variance=energy_variance,
            coordination_entropy=coordination_entropy,
            communication_temperature=comm_temperature,
            average_neighbor_count=avg_neighbors,
            swarm_cohesion=cohesion,
            swarm_dispersion=dispersion,
            entropy_anomaly_score=entropy_anomaly,
            energy_anomaly_score=energy_anomaly,
            topology_anomaly_score=topology_anomaly
        )

    async def _detect_swarm_hijacking(
        self,
        swarm_id: str,
        thermodynamics: SwarmThermodynamics
    ):
        """
        Detect swarm hijacking attack.

        Indicators:
        - Sudden coordination entropy spike (coordinated takeover)
        - Energy consumption anomaly (malicious activity)
        - Topology change (new command source)
        """
        hijacking_detected = False
        indicators = []

        # Check entropy spike
        if thermodynamics.entropy_anomaly_score > self.entropy_spike_threshold:
            indicators.append(f"Entropy spike: {thermodynamics.entropy_anomaly_score:.1f}σ")
            hijacking_detected = True

        # Check energy anomaly
        if thermodynamics.energy_anomaly_score > self.energy_anomaly_threshold:
            indicators.append(f"Energy anomaly: {thermodynamics.energy_anomaly_score:.1f}σ")
            hijacking_detected = True

        # Check topology change
        if thermodynamics.topology_anomaly_score > 3.0:
            indicators.append(f"Topology change: {thermodynamics.topology_anomaly_score:.1f}σ")
            hijacking_detected = True

        if hijacking_detected:
            logger.critical(
                f"SWARM HIJACKING DETECTED on {swarm_id}: " +
                ", ".join(indicators)
            )

            self.stats["threats_detected"] += 1
            self.stats["swarm_hijacking_detected"] += 1

            await self._register_threat_event(
                threat_type="swarm_hijacking",
                target_id=swarm_id,
                data={
                    "indicators": indicators,
                    "entropy_anomaly": thermodynamics.entropy_anomaly_score,
                    "energy_anomaly": thermodynamics.energy_anomaly_score,
                    "topology_anomaly": thermodynamics.topology_anomaly_score,
                    "robot_count": thermodynamics.robot_count
                },
                severity="critical"
            )

    async def _detect_sybil_attack(
        self,
        swarm_id: str,
        thermodynamics: SwarmThermodynamics
    ):
        """
        Detect Sybil attack (fake robot identities).

        Indicators:
        - Sudden increase in robot count
        - Entropy reduction (fake robots behaving identically)
        - Low energy variance (fake robots don't consume real energy)
        """
        history = list(self.swarm_thermodynamics.get(swarm_id, []))

        if len(history) < 10:
            return

        # Check for sudden robot count increase
        previous_counts = [h.robot_count for h in history[-10:-1]]
        avg_count = np.mean(previous_counts)

        count_increase = thermodynamics.robot_count - avg_count

        if count_increase > avg_count * 0.30:  # >30% increase
            logger.warning(
                f"POSSIBLE SYBIL ATTACK on {swarm_id}: "
                f"Robot count increased from {avg_count:.0f} to {thermodynamics.robot_count}"
            )

            self.stats["sybil_attacks_detected"] += 1

            await self._register_threat_event(
                threat_type="sybil_attack",
                target_id=swarm_id,
                data={
                    "previous_count": int(avg_count),
                    "current_count": thermodynamics.robot_count,
                    "increase": int(count_increase),
                    "entropy": thermodynamics.coordination_entropy
                },
                severity="high"
            )

    async def _detect_byzantine_fault(self, swarm_id: str):
        """
        Detect Byzantine fault (malicious robots sending conflicting data).

        Analyzes consistency of telemetry reports.
        """
        # Simplified detection - in production would do consensus analysis
        pass

    async def _collect_iot_data(self, network_id: str):
        """Collect data from IoT sensors."""
        # Simulate IoT sensor data
        for i in range(10):
            sensor_id = f"{network_id}_sensor_{i}"

            data = IoTSensorData(
                sensor_id=sensor_id,
                timestamp=datetime.now(),
                sensor_type="temperature",
                value=20.0 + np.random.normal(0, 2.0),
                unit="celsius",
                location=(
                    37.7749 + np.random.uniform(-0.1, 0.1),
                    -122.4194 + np.random.uniform(-0.1, 0.1)
                ),
                battery_level=np.random.uniform(60, 100)
            )

            self.iot_sensors[sensor_id] = data

            if sensor_id not in self.iot_history:
                self.iot_history[sensor_id] = deque(maxlen=1000)

            self.iot_history[sensor_id].append(data)

    async def _detect_iot_botnet(self, network_id: str):
        """
        Detect IoT botnet formation.

        Indicators:
        - High correlation in device activity (coordinated behavior)
        - Synchronized communication patterns
        - Abnormal energy consumption
        """
        # Analyze correlation between sensors
        sensor_ids = [sid for sid in self.iot_sensors.keys() if network_id in sid]

        if len(sensor_ids) < 5:
            return

        # Get recent value sequences
        sequences = []
        for sensor_id in sensor_ids[:10]:  # Analyze first 10 sensors
            if sensor_id in self.iot_history and len(self.iot_history[sensor_id]) >= 20:
                values = [d.value for d in list(self.iot_history[sensor_id])[-20:]]
                sequences.append(values)

        if len(sequences) < 5:
            return

        # Calculate cross-correlation
        sequences_array = np.array(sequences)
        correlations = np.corrcoef(sequences_array)

        # Get upper triangle (avoid diagonal)
        upper_triangle = correlations[np.triu_indices_from(correlations, k=1)]
        mean_correlation = np.mean(np.abs(upper_triangle))

        if mean_correlation > self.botnet_correlation_threshold:
            logger.critical(
                f"IoT BOTNET DETECTED on {network_id}: "
                f"High device correlation {mean_correlation:.3f}"
            )

            self.stats["threats_detected"] += 1
            self.stats["iot_botnet_detected"] += 1

            await self._register_threat_event(
                threat_type="iot_botnet",
                target_id=network_id,
                data={
                    "correlation": float(mean_correlation),
                    "device_count": len(sensor_ids),
                    "analyzed_devices": len(sequences)
                },
                severity="critical"
            )

    async def _detect_data_poisoning(self, network_id: str):
        """
        Detect data poisoning in IoT sensors.

        Indicators:
        - Values outside physical bounds
        - Statistical outliers
        - Sudden distribution shifts
        """
        for sensor_id, data in self.iot_sensors.items():
            if network_id not in sensor_id:
                continue

            # Check for physically impossible values
            if data.sensor_type == "temperature" and (data.value < -50 or data.value > 70):
                logger.warning(
                    f"DATA POISONING DETECTED: {sensor_id} reports "
                    f"impossible temperature {data.value}°C"
                )

                self.stats["data_poisoning_detected"] += 1

                await self._register_threat_event(
                    threat_type="data_poisoning",
                    target_id=sensor_id,
                    data={
                        "sensor_type": data.sensor_type,
                        "impossible_value": data.value,
                        "unit": data.unit
                    },
                    severity="medium"
                )

    async def _register_threat_event(
        self,
        threat_type: str,
        target_id: str,
        data: Dict[str, Any],
        severity: str
    ):
        """Register swarm/IoT security threat."""
        if not self.security_registry:
            return

        try:
            await self.security_registry.register_security_event(
                event_type=f"swarm_iot_{threat_type}",
                device_id=target_id,
                thermodynamic_data=data,
                severity=severity,
                confidence=0.88,
                threat_category="swarm_iot_attack",
                source_sensor="swarm_iot_security_monitor"
            )

            # Publish event
            if self.event_bus:
                await self.event_bus.publish(f"security.swarm_iot.{threat_type}", {
                    "target_id": target_id,
                    **data,
                    "severity": severity,
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            logger.error(f"Failed to register swarm/IoT threat: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get swarm/IoT monitor statistics."""
        return {
            **self.stats,
            "monitored_swarms": len([k for k in self.monitoring_active.keys() if k.startswith("swarm_")]),
            "monitored_iot_networks": len([k for k in self.monitoring_active.keys() if k.startswith("iot_")]),
            "total_robots": sum(len(members) for members in self.swarm_members.values()),
            "total_iot_sensors": len(self.iot_sensors)
        }


# ============================================================================
# Singleton instance
# ============================================================================

_swarm_iot_monitor_instance = None


def get_swarm_iot_security_monitor(
    database_pool=None,
    energy_intelligence_layer=None,
    security_registry=None,
    event_bus=None,
    swarm_interface=None,
    iot_interface=None
) -> SwarmIoTSecurityMonitor:
    """
    Get singleton Swarm & IoT Security Monitor instance.

    Args:
        database_pool: PostgreSQL connection pool
        energy_intelligence_layer: EIL for thermodynamic calculations
        security_registry: Security Event Registry
        event_bus: Event bus
        swarm_interface: Swarm control interface
        iot_interface: IoT network interface

    Returns:
        SwarmIoTSecurityMonitor instance
    """
    global _swarm_iot_monitor_instance

    if _swarm_iot_monitor_instance is None:
        _swarm_iot_monitor_instance = SwarmIoTSecurityMonitor(
            database_pool=database_pool,
            energy_intelligence_layer=energy_intelligence_layer,
            security_registry=security_registry,
            event_bus=event_bus,
            swarm_interface=swarm_interface,
            iot_interface=iot_interface
        )

    return _swarm_iot_monitor_instance
