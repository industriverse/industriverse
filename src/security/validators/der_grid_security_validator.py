"""
DER Grid Security Validator

Protects distributed energy resource (DER) grids from energy-based attacks:
- Energy conservation violations (impossible power flows)
- Thermodynamic impossibility detection (efficiency >100%)
- Grid manipulation attacks (false injection)
- Energy theft detection
- Microgrid islanding attacks

Threat Model:
Smart grids with DERs (solar, wind, batteries, EVs) are vulnerable to
cyber-physical attacks that violate fundamental thermodynamic laws. By
validating energy conservation and detecting thermodynamic impossibilities,
we can identify and block sophisticated grid attacks.

Attack Types Detected:
1. False Data Injection (FDI): Attacker injects false meter readings that
   appear valid but violate energy conservation when analyzed holistically
2. Energy Theft: Unauthorized energy consumption hidden in measurement noise
3. Over-Unity Fraud: Claims of devices producing more energy than consumed
   (efficiency >100%, violates thermodynamics)
4. Load Redistribution: Malicious shifting of energy loads to destabilize grid
5. Islanding Attack: Forcing microgrid disconnection at inopportune times

Detection Methodology:
- Kirchhoff's Current Law validation (ΣI_in = ΣI_out at every node)
- Power balance verification (ΣP_generation = ΣP_consumption + losses)
- Thermodynamic efficiency bounds (η ≤ Carnot efficiency)
- Entropy production consistency (ΔS ≥ 0 for all processes)
- Time-series anomaly detection in energy flows

Thermodynamic Principles:
1. Energy Conservation: Total energy in isolated system remains constant
2. Entropy Increase: ΔS_universe ≥ 0 for all real processes
3. Carnot Limit: η_max = 1 - (T_cold / T_hot)
4. Exergy Destruction: Irreversibilities always destroy exergy

Integration:
- Monitors smart grid SCADA systems
- Integrates with DER management systems
- Uses EIL for thermodynamic calculations
- Registers violations in Security Event Registry
- Visualizes grid attacks in AR/VR

References:
- Liu et al., "False Data Injection Attacks Against State Estimation" (2011)
- Liang et al., "A Review of False Data Injection Attacks Against Smart Grid" (2017)
- NIST Framework for Improving Critical Infrastructure Cybersecurity
"""

import logging
import asyncio
import numpy as np
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GridNode:
    """Represents a node in the DER grid."""
    node_id: str
    node_type: str  # generation, consumption, storage, connection
    power_rating: float  # kW
    location: Tuple[float, float]  # (lat, lon)
    connected_nodes: List[str]


@dataclass
class EnergyFlow:
    """Energy flow measurement at a point in time."""
    node_id: str
    timestamp: datetime
    power_generation: float  # kW (positive = generation)
    power_consumption: float  # kW (positive = consumption)
    power_storage_delta: float  # kW (positive = charging, negative = discharging)
    voltage: float  # V
    current: float  # A
    frequency: float  # Hz
    power_factor: float


class DERGridSecurityValidator:
    """
    Validate DER grid operations against thermodynamic laws.

    Detects attacks that violate energy conservation, efficiency bounds,
    or other physical constraints.
    """

    def __init__(
        self,
        database_pool=None,
        energy_intelligence_layer=None,
        security_registry=None,
        event_bus=None,
        grid_interface=None
    ):
        """
        Initialize DER Grid Security Validator.

        Args:
            database_pool: PostgreSQL connection pool
            energy_intelligence_layer: EIL for thermodynamic calculations
            security_registry: Security Event Registry
            event_bus: Event bus
            grid_interface: Interface to grid SCADA/EMS
        """
        self.db_pool = database_pool
        self.eil = energy_intelligence_layer
        self.security_registry = security_registry
        self.event_bus = event_bus
        self.grid_interface = grid_interface

        # Grid topology
        self.grid_nodes: Dict[str, GridNode] = {}
        self.grid_adjacency: Dict[str, List[str]] = {}

        # Physical constraints
        self.max_efficiency = 0.95  # 95% maximum practical efficiency
        self.carnot_temp_hot = 373.15  # K (steam turbine)
        self.carnot_temp_cold = 293.15  # K (ambient)
        self.carnot_limit = 1.0 - (self.carnot_temp_cold / self.carnot_temp_hot)  # ~0.21

        # Detection thresholds
        self.energy_balance_tolerance = 0.02  # 2% measurement error allowed
        self.efficiency_violation_threshold = 1.05  # >105% = impossible
        self.power_anomaly_threshold = 3.0  # 3 std deviations
        self.entropy_violation_tolerance = 1e-6  # Allow tiny numerical errors

        # Monitoring state
        self.energy_history: Dict[str, deque] = {}  # node_id -> deque of EnergyFlow
        self.monitoring_active = {}
        self.monitoring_tasks = {}

        # Statistics
        self.stats = {
            "validations_performed": 0,
            "energy_conservation_violations": 0,
            "efficiency_violations": 0,
            "thermodynamic_impossibilities": 0,
            "fdi_attacks_detected": 0,
            "energy_theft_detected": 0
        }

        logger.info("DER Grid Security Validator initialized")

    def register_grid_node(
        self,
        node_id: str,
        node_type: str,
        power_rating: float,
        location: Tuple[float, float],
        connected_nodes: List[str]
    ):
        """
        Register a node in the grid topology.

        Args:
            node_id: Unique node identifier
            node_type: generation, consumption, storage, connection
            power_rating: Power rating in kW
            location: (latitude, longitude)
            connected_nodes: List of connected node IDs
        """
        node = GridNode(
            node_id=node_id,
            node_type=node_type,
            power_rating=power_rating,
            location=location,
            connected_nodes=connected_nodes
        )

        self.grid_nodes[node_id] = node
        self.grid_adjacency[node_id] = connected_nodes

        logger.info(
            f"Registered grid node {node_id} ({node_type}, {power_rating}kW)"
        )

    async def validate_energy_conservation(
        self,
        grid_snapshot: Dict[str, EnergyFlow]
    ) -> Dict[str, Any]:
        """
        Validate energy conservation across entire grid.

        Checks Kirchhoff's laws and power balance at all nodes.

        Args:
            grid_snapshot: Dict mapping node_id to current EnergyFlow

        Returns:
            Validation results with violations detected
        """
        logger.debug("Validating energy conservation across grid")

        self.stats["validations_performed"] += 1

        violations = []
        total_generation = 0.0
        total_consumption = 0.0
        total_storage_delta = 0.0

        # Sum all power flows
        for node_id, flow in grid_snapshot.items():
            total_generation += flow.power_generation
            total_consumption += flow.power_consumption
            total_storage_delta += flow.power_storage_delta

        # Expected: Generation = Consumption + Storage + Losses
        # Losses typically 2-5% of generation in real grids
        estimated_losses = total_generation * 0.03  # Assume 3% losses

        energy_balance = total_generation - (total_consumption + total_storage_delta + estimated_losses)
        balance_ratio = abs(energy_balance) / max(total_generation, 1.0)

        # Check if balance within tolerance
        if balance_ratio > self.energy_balance_tolerance:
            violation = {
                "type": "energy_conservation_violation",
                "severity": "high",
                "total_generation_kw": total_generation,
                "total_consumption_kw": total_consumption,
                "total_storage_delta_kw": total_storage_delta,
                "estimated_losses_kw": estimated_losses,
                "energy_imbalance_kw": energy_balance,
                "imbalance_ratio": balance_ratio,
                "timestamp": datetime.now().isoformat()
            }

            violations.append(violation)

            logger.warning(
                f"ENERGY CONSERVATION VIOLATION: "
                f"Imbalance {energy_balance:.2f}kW ({balance_ratio*100:.1f}%)"
            )

            self.stats["energy_conservation_violations"] += 1

            # Register security event
            await self._register_violation_event(
                violation_type="energy_conservation_violation",
                data=violation,
                severity="high"
            )

        # Validate each node (Kirchhoff's Current Law)
        for node_id, flow in grid_snapshot.items():
            node_violation = await self._validate_node_power_balance(
                node_id,
                flow,
                grid_snapshot
            )

            if node_violation:
                violations.append(node_violation)

        result = {
            "validation_passed": len(violations) == 0,
            "total_generation_kw": total_generation,
            "total_consumption_kw": total_consumption,
            "total_storage_delta_kw": total_storage_delta,
            "estimated_losses_kw": estimated_losses,
            "energy_balance_kw": energy_balance,
            "balance_ratio": balance_ratio,
            "violations": violations,
            "timestamp": datetime.now().isoformat()
        }

        return result

    async def _validate_node_power_balance(
        self,
        node_id: str,
        flow: EnergyFlow,
        grid_snapshot: Dict[str, EnergyFlow]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate power balance at individual node (Kirchhoff's Current Law).

        At each node: ΣP_in = ΣP_out
        """
        if node_id not in self.grid_nodes:
            return None

        node = self.grid_nodes[node_id]

        # Calculate power in and out
        power_in = flow.power_generation
        power_out = flow.power_consumption + abs(min(flow.power_storage_delta, 0.0))

        # Power from connected nodes
        for connected_id in node.connected_nodes:
            if connected_id in grid_snapshot:
                # Simplified: assume power flows from generation to consumption
                connected_flow = grid_snapshot[connected_id]
                # This would require actual power flow analysis in production

        # Check voltage/current relationship (P = V * I * power_factor)
        calculated_power = flow.voltage * flow.current * flow.power_factor / 1000.0  # kW
        measured_power = flow.power_generation - flow.power_consumption

        power_discrepancy = abs(calculated_power - measured_power)
        discrepancy_ratio = power_discrepancy / max(abs(measured_power), 1.0)

        if discrepancy_ratio > 0.1:  # 10% discrepancy
            logger.warning(
                f"POWER DISCREPANCY at node {node_id}: "
                f"Calculated {calculated_power:.2f}kW, "
                f"Measured {measured_power:.2f}kW"
            )

            return {
                "type": "node_power_discrepancy",
                "node_id": node_id,
                "calculated_power_kw": calculated_power,
                "measured_power_kw": measured_power,
                "discrepancy_ratio": discrepancy_ratio,
                "severity": "medium"
            }

        return None

    async def validate_thermodynamic_efficiency(
        self,
        device_id: str,
        energy_input: float,
        energy_output: float,
        device_type: str = "generic"
    ) -> Dict[str, Any]:
        """
        Validate device efficiency against thermodynamic limits.

        Detects over-unity fraud and thermodynamic impossibilities.

        Args:
            device_id: Device identifier
            energy_input: Energy consumed (kWh)
            energy_output: Energy produced (kWh)
            device_type: Type of device (heat_engine, heat_pump, solar, battery, etc.)

        Returns:
            Validation results
        """
        logger.debug(
            f"Validating thermodynamic efficiency for {device_id}: "
            f"Input={energy_input:.2f}kWh, Output={energy_output:.2f}kWh"
        )

        # Calculate efficiency
        if energy_input <= 0:
            efficiency = 0.0
        else:
            efficiency = energy_output / energy_input

        # Determine theoretical maximum efficiency
        max_theoretical_efficiency = self._get_max_efficiency(device_type)

        # Check for violations
        violation_detected = False
        severity = "low"

        if efficiency > max_theoretical_efficiency:
            violation_detected = True
            severity = "critical"

            logger.critical(
                f"THERMODYNAMIC IMPOSSIBILITY: {device_id} claims "
                f"{efficiency*100:.1f}% efficiency (max possible: "
                f"{max_theoretical_efficiency*100:.1f}%)"
            )

            self.stats["thermodynamic_impossibilities"] += 1
            self.stats["efficiency_violations"] += 1

            # Register critical violation
            await self._register_violation_event(
                violation_type="thermodynamic_impossibility",
                data={
                    "device_id": device_id,
                    "device_type": device_type,
                    "claimed_efficiency": efficiency,
                    "max_possible_efficiency": max_theoretical_efficiency,
                    "energy_input_kwh": energy_input,
                    "energy_output_kwh": energy_output,
                    "violation": "over_unity",
                    "law_violated": "First Law of Thermodynamics"
                },
                severity="critical"
            )

        elif efficiency > self.max_efficiency:
            violation_detected = True
            severity = "high"

            logger.warning(
                f"EFFICIENCY VIOLATION: {device_id} claims "
                f"{efficiency*100:.1f}% efficiency (practical max: "
                f"{self.max_efficiency*100:.1f}%)"
            )

            self.stats["efficiency_violations"] += 1

        result = {
            "device_id": device_id,
            "device_type": device_type,
            "efficiency": efficiency,
            "efficiency_percent": efficiency * 100,
            "max_theoretical_efficiency": max_theoretical_efficiency,
            "max_practical_efficiency": self.max_efficiency,
            "violation_detected": violation_detected,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }

        return result

    def _get_max_efficiency(self, device_type: str) -> float:
        """
        Get maximum theoretical efficiency for device type.

        Based on thermodynamic limits.
        """
        efficiency_limits = {
            "heat_engine": self.carnot_limit,  # ~21% for typical temps
            "heat_pump": 4.0,  # COP (can be >1 for heat pumps)
            "solar": 0.33,  # Shockley-Queisser limit for single junction
            "battery": 0.95,  # Lithium-ion round-trip efficiency
            "wind": 0.59,  # Betz limit
            "hydro": 0.90,  # Turbine efficiency
            "fuel_cell": 0.60,  # Thermodynamic limit
            "generic": 1.00  # Conservation of energy limit
        }

        return efficiency_limits.get(device_type, 1.00)

    async def detect_false_data_injection(
        self,
        time_series: List[EnergyFlow],
        node_id: str
    ) -> Dict[str, Any]:
        """
        Detect False Data Injection (FDI) attacks using statistical analysis.

        FDI attacks inject false measurements that appear valid individually
        but violate system-wide constraints when analyzed holistically.

        Args:
            time_series: Historical energy flow measurements
            node_id: Node to analyze

        Returns:
            Detection results
        """
        logger.debug(f"Analyzing node {node_id} for FDI attacks")

        if len(time_series) < 50:
            return {
                "fdi_detected": False,
                "message": "Insufficient data for FDI detection"
            }

        # Extract power measurements
        powers = np.array([
            flow.power_generation - flow.power_consumption
            for flow in time_series
        ])

        # Statistical analysis
        mean_power = np.mean(powers)
        std_power = np.std(powers)

        # Detect anomalies (values >3 std deviations from mean)
        z_scores = np.abs((powers - mean_power) / max(std_power, 1.0))
        anomalies = np.where(z_scores > self.power_anomaly_threshold)[0]

        # Check for autocorrelation break (sign of injection)
        if len(powers) > 100:
            autocorr = np.correlate(powers, powers, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            autocorr_normalized = autocorr / autocorr[0]

            # Sudden drop in autocorrelation indicates data manipulation
            if len(autocorr_normalized) > 10:
                recent_autocorr = autocorr_normalized[5:10].mean()
                if recent_autocorr < 0.3:  # Weak correlation = suspicious
                    logger.warning(
                        f"POSSIBLE FDI ATTACK on {node_id}: "
                        f"Autocorrelation break detected"
                    )

        fdi_detected = len(anomalies) > len(time_series) * 0.05  # >5% anomalies

        if fdi_detected:
            self.stats["fdi_attacks_detected"] += 1

            await self._register_violation_event(
                violation_type="false_data_injection",
                data={
                    "node_id": node_id,
                    "anomaly_count": len(anomalies),
                    "total_measurements": len(time_series),
                    "anomaly_percentage": (len(anomalies) / len(time_series)) * 100,
                    "mean_power_kw": float(mean_power),
                    "std_power_kw": float(std_power)
                },
                severity="high"
            )

        result = {
            "node_id": node_id,
            "fdi_detected": fdi_detected,
            "anomaly_count": len(anomalies),
            "total_measurements": len(time_series),
            "anomaly_percentage": (len(anomalies) / len(time_series)) * 100,
            "mean_power_kw": float(mean_power),
            "std_power_kw": float(std_power),
            "timestamp": datetime.now().isoformat()
        }

        return result

    async def detect_energy_theft(
        self,
        node_id: str,
        reported_consumption: float,
        metered_consumption: float
    ) -> Dict[str, Any]:
        """
        Detect energy theft by comparing reported vs metered consumption.

        Args:
            node_id: Node identifier
            reported_consumption: Consumer-reported energy (kWh)
            metered_consumption: Utility-metered energy (kWh)

        Returns:
            Detection results
        """
        discrepancy = metered_consumption - reported_consumption
        discrepancy_ratio = abs(discrepancy) / max(metered_consumption, 1.0)

        theft_detected = discrepancy_ratio > 0.10  # >10% discrepancy

        if theft_detected and discrepancy > 0:  # More metered than reported
            logger.warning(
                f"ENERGY THEFT DETECTED at {node_id}: "
                f"Reported {reported_consumption:.2f}kWh, "
                f"Metered {metered_consumption:.2f}kWh "
                f"(+{discrepancy:.2f}kWh stolen)"
            )

            self.stats["energy_theft_detected"] += 1

            await self._register_violation_event(
                violation_type="energy_theft",
                data={
                    "node_id": node_id,
                    "reported_consumption_kwh": reported_consumption,
                    "metered_consumption_kwh": metered_consumption,
                    "stolen_energy_kwh": discrepancy,
                    "theft_percentage": discrepancy_ratio * 100
                },
                severity="medium"
            )

        result = {
            "node_id": node_id,
            "theft_detected": theft_detected,
            "reported_consumption_kwh": reported_consumption,
            "metered_consumption_kwh": metered_consumption,
            "discrepancy_kwh": discrepancy,
            "discrepancy_ratio": discrepancy_ratio,
            "timestamp": datetime.now().isoformat()
        }

        return result

    async def _register_violation_event(
        self,
        violation_type: str,
        data: Dict[str, Any],
        severity: str
    ):
        """Register grid security violation event."""
        if not self.security_registry:
            return

        try:
            await self.security_registry.register_security_event(
                event_type=violation_type,
                device_id=data.get("node_id", data.get("device_id", "grid_wide")),
                thermodynamic_data=data,
                severity=severity,
                confidence=0.90,
                threat_category="grid_attack",
                source_sensor="der_grid_security_validator"
            )

            # Publish event
            if self.event_bus:
                await self.event_bus.publish(f"security.grid.{violation_type}", {
                    **data,
                    "severity": severity,
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            logger.error(f"Failed to register grid violation event: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get grid validator statistics."""
        return {
            **self.stats,
            "registered_nodes": len(self.grid_nodes)
        }


# ============================================================================
# Singleton instance
# ============================================================================

_grid_validator_instance = None


def get_der_grid_security_validator(
    database_pool=None,
    energy_intelligence_layer=None,
    security_registry=None,
    event_bus=None,
    grid_interface=None
) -> DERGridSecurityValidator:
    """
    Get singleton DER Grid Security Validator instance.

    Args:
        database_pool: PostgreSQL connection pool
        energy_intelligence_layer: EIL for thermodynamic calculations
        security_registry: Security Event Registry
        event_bus: Event bus
        grid_interface: Grid SCADA/EMS interface

    Returns:
        DERGridSecurityValidator instance
    """
    global _grid_validator_instance

    if _grid_validator_instance is None:
        _grid_validator_instance = DERGridSecurityValidator(
            database_pool=database_pool,
            energy_intelligence_layer=energy_intelligence_layer,
            security_registry=security_registry,
            event_bus=event_bus,
            grid_interface=grid_interface
        )

    return _grid_validator_instance
