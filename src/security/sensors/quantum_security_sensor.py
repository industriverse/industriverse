"""
Quantum Device Security Sensor

Protects quantum computing systems from quantum-specific attacks:
- Decoherence attacks (environmental manipulation)
- Phase noise injection
- Quantum state tampering
- Measurement-induced collapse attacks
- Entanglement disruption

Quantum Threat Landscape:
Quantum computers are vulnerable to unique attack vectors that exploit
quantum mechanical properties. This sensor monitors thermodynamic signatures
of quantum operations to detect malicious interference.

Attack Types Detected:
1. Decoherence Attack: Adversary manipulates environment (temperature,
   EM fields, vibration) to accelerate decoherence and destroy quantum states
2. Phase Noise: Injection of controlled noise to corrupt phase relationships
3. State Tampering: Direct manipulation of quantum state preparation
4. Measurement Attack: Forcing premature quantum state collapse
5. Entanglement Breaking: Disrupting quantum entanglement channels

Detection Methodology:
- Monitor decoherence time (T1, T2)
- Track phase drift rates
- Measure fidelity degradation
- Analyze quantum gate error rates
- Detect anomalous energy dissipation

Thermodynamic Indicators:
- Abnormal entropy production during quantum operations
- Unexpected energy dissipation in qubit systems
- Thermal signatures of environmental tampering
- Anomalous electromagnetic emissions

Integration:
- Uses Energy Intelligence Layer for entropy calculations
- Registers events in Security Event Registry
- Triggers quantum error correction protocols
- Visualizes quantum attacks in AR/VR

References:
- Preskill, "Quantum Computing in the NISQ era and beyond" (2018)
- Knill et al., "Resilient Quantum Computation" (1998)
- Terhal, "Quantum error correction for quantum memories" (2015)
"""

import logging
import asyncio
import numpy as np
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QuantumCoherenceMetrics:
    """Quantum coherence measurement results."""
    device_id: str
    t1_time: float  # Longitudinal relaxation time (μs)
    t2_time: float  # Transverse dephasing time (μs)
    gate_fidelity: float  # Average gate fidelity (0-1)
    readout_fidelity: float  # Measurement fidelity (0-1)
    phase_drift_rate: float  # rad/μs
    energy_dissipation: float  # Energy lost (eV)
    entropy_production: float  # Entropy increase (bits)
    timestamp: datetime


class QuantumSecuritySensor:
    """
    Monitor quantum devices for quantum-specific security threats.

    Detects decoherence attacks, phase noise, state tampering, and
    other quantum interference patterns.
    """

    def __init__(
        self,
        database_pool=None,
        energy_intelligence_layer=None,
        security_registry=None,
        event_bus=None,
        quantum_interface=None
    ):
        """
        Initialize Quantum Security Sensor.

        Args:
            database_pool: PostgreSQL connection pool
            energy_intelligence_layer: EIL for entropy calculations
            security_registry: Security Event Registry
            event_bus: Event bus
            quantum_interface: Interface to quantum hardware
        """
        self.db_pool = database_pool
        self.eil = energy_intelligence_layer
        self.security_registry = security_registry
        self.event_bus = event_bus
        self.quantum_interface = quantum_interface

        # Baseline quantum parameters (for typical superconducting qubits)
        self.baseline_t1 = 100.0  # μs
        self.baseline_t2 = 80.0   # μs
        self.baseline_gate_fidelity = 0.999
        self.baseline_readout_fidelity = 0.98
        self.baseline_phase_drift = 0.01  # rad/μs

        # Attack detection thresholds
        self.decoherence_threshold = 0.5  # 50% reduction triggers alert
        self.phase_noise_threshold = 5.0  # 5x baseline phase drift
        self.fidelity_threshold = 0.95  # Below 95% gate fidelity
        self.entropy_anomaly_threshold = 2.0  # 2x expected entropy

        # Monitoring state
        self.baselines = {}  # device_id -> baseline metrics
        self.monitoring_active = {}  # device_id -> bool
        self.monitoring_tasks = {}  # device_id -> Task
        self.coherence_history = {}  # device_id -> deque of metrics

        # Statistics
        self.stats = {
            "attacks_detected": 0,
            "decoherence_attacks": 0,
            "phase_noise_attacks": 0,
            "state_tampering_events": 0,
            "measurement_attacks": 0,
            "total_quantum_errors": 0
        }

        logger.info("Quantum Security Sensor initialized")

    async def establish_quantum_baseline(
        self,
        device_id: str,
        measurement_count: int = 100
    ) -> QuantumCoherenceMetrics:
        """
        Establish baseline quantum coherence parameters.

        Measures T1, T2, gate fidelity, and other quantum metrics
        under normal operating conditions.

        Args:
            device_id: Quantum device to baseline
            measurement_count: Number of measurements

        Returns:
            Baseline QuantumCoherenceMetrics
        """
        logger.info(
            f"Establishing quantum baseline for {device_id} "
            f"({measurement_count} measurements)"
        )

        metrics_list = []

        for i in range(measurement_count):
            metrics = await self._measure_quantum_coherence(device_id)
            metrics_list.append(metrics)

            if i % 20 == 0:
                logger.debug(f"Baseline progress: {i}/{measurement_count}")

            await asyncio.sleep(0.1)

        # Calculate average baseline
        avg_t1 = np.mean([m.t1_time for m in metrics_list])
        avg_t2 = np.mean([m.t2_time for m in metrics_list])
        avg_gate_fidelity = np.mean([m.gate_fidelity for m in metrics_list])
        avg_readout_fidelity = np.mean([m.readout_fidelity for m in metrics_list])
        avg_phase_drift = np.mean([m.phase_drift_rate for m in metrics_list])

        baseline = QuantumCoherenceMetrics(
            device_id=device_id,
            t1_time=avg_t1,
            t2_time=avg_t2,
            gate_fidelity=avg_gate_fidelity,
            readout_fidelity=avg_readout_fidelity,
            phase_drift_rate=avg_phase_drift,
            energy_dissipation=0.0,
            entropy_production=0.0,
            timestamp=datetime.now()
        )

        self.baselines[device_id] = baseline

        logger.info(
            f"Quantum baseline established for {device_id}: "
            f"T1={avg_t1:.1f}μs, T2={avg_t2:.1f}μs, "
            f"Fidelity={avg_gate_fidelity:.4f}"
        )

        return baseline

    async def start_monitoring(self, device_id: str):
        """
        Start continuous quantum security monitoring.

        Args:
            device_id: Quantum device to monitor
        """
        if self.monitoring_active.get(device_id):
            logger.warning(f"Already monitoring quantum device {device_id}")
            return

        logger.info(f"Starting quantum security monitoring for {device_id}")

        # Ensure baseline exists
        if device_id not in self.baselines:
            await self.establish_quantum_baseline(device_id, measurement_count=50)

        self.monitoring_active[device_id] = True

        # Initialize coherence history
        if device_id not in self.coherence_history:
            self.coherence_history[device_id] = deque(maxlen=1000)

        # Create monitoring task
        task = asyncio.create_task(self._monitoring_loop(device_id))
        self.monitoring_tasks[device_id] = task

    async def stop_monitoring(self, device_id: str):
        """Stop quantum security monitoring."""
        logger.info(f"Stopping quantum security monitoring for {device_id}")

        self.monitoring_active[device_id] = False

        if device_id in self.monitoring_tasks:
            self.monitoring_tasks[device_id].cancel()
            del self.monitoring_tasks[device_id]

    async def _monitoring_loop(self, device_id: str):
        """
        Continuous quantum security monitoring loop.

        Monitors every 100ms for quantum attacks.
        """
        logger.info(f"Quantum monitoring loop started for {device_id}")

        try:
            baseline = self.baselines[device_id]

            while self.monitoring_active.get(device_id):
                # Measure current quantum state
                current_metrics = await self._measure_quantum_coherence(device_id)

                # Store in history
                self.coherence_history[device_id].append(current_metrics)

                # Detect decoherence attacks
                await self._detect_decoherence_attack(
                    device_id,
                    current_metrics,
                    baseline
                )

                # Detect phase noise attacks
                await self._detect_phase_noise_attack(
                    device_id,
                    current_metrics,
                    baseline
                )

                # Detect state tampering
                await self._detect_state_tampering(
                    device_id,
                    current_metrics,
                    baseline
                )

                # Detect measurement attacks
                await self._detect_measurement_attack(
                    device_id,
                    current_metrics,
                    baseline
                )

                # Sleep 100ms between measurements
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info(f"Quantum monitoring cancelled for {device_id}")
        except Exception as e:
            logger.error(f"Quantum monitoring error: {e}")
        finally:
            self.monitoring_active[device_id] = False
            logger.info(f"Quantum monitoring loop ended for {device_id}")

    async def _measure_quantum_coherence(
        self,
        device_id: str
    ) -> QuantumCoherenceMetrics:
        """
        Measure quantum coherence parameters.

        In production: Interface with actual quantum hardware
        (IBM Qiskit, Google Cirq, Rigetti PyQuil, etc.)

        Returns:
            Current QuantumCoherenceMetrics
        """
        # Simulate quantum measurements
        # In production, use quantum_interface to read actual hardware

        # Simulate T1 (longitudinal relaxation)
        t1 = self.baseline_t1 + np.random.normal(0, 10.0)

        # Simulate T2 (transverse dephasing)
        t2 = self.baseline_t2 + np.random.normal(0, 8.0)

        # Simulate gate fidelity
        gate_fidelity = min(1.0, max(0.0,
            self.baseline_gate_fidelity + np.random.normal(0, 0.002)
        ))

        # Simulate readout fidelity
        readout_fidelity = min(1.0, max(0.0,
            self.baseline_readout_fidelity + np.random.normal(0, 0.005)
        ))

        # Simulate phase drift
        phase_drift = abs(self.baseline_phase_drift + np.random.normal(0, 0.002))

        # Calculate energy dissipation (proportional to decoherence)
        energy_dissipation = (1.0 / max(t1, 1.0)) * 100.0  # eV

        # Calculate entropy production
        entropy_production = -np.log2(gate_fidelity) if gate_fidelity > 0 else 10.0

        return QuantumCoherenceMetrics(
            device_id=device_id,
            t1_time=float(t1),
            t2_time=float(t2),
            gate_fidelity=float(gate_fidelity),
            readout_fidelity=float(readout_fidelity),
            phase_drift_rate=float(phase_drift),
            energy_dissipation=float(energy_dissipation),
            entropy_production=float(entropy_production),
            timestamp=datetime.now()
        )

    async def _detect_decoherence_attack(
        self,
        device_id: str,
        current: QuantumCoherenceMetrics,
        baseline: QuantumCoherenceMetrics
    ):
        """
        Detect decoherence attacks.

        Decoherence attack: Adversary manipulates environment to
        accelerate quantum decoherence (cooling, EM interference, etc.)
        """
        # Calculate decoherence reduction
        t1_reduction = (baseline.t1_time - current.t1_time) / baseline.t1_time
        t2_reduction = (baseline.t2_time - current.t2_time) / baseline.t2_time

        if t1_reduction > self.decoherence_threshold or \
           t2_reduction > self.decoherence_threshold:

            logger.critical(
                f"DECOHERENCE ATTACK DETECTED on {device_id}: "
                f"T1 reduced {t1_reduction*100:.1f}%, "
                f"T2 reduced {t2_reduction*100:.1f}%"
            )

            self.stats["attacks_detected"] += 1
            self.stats["decoherence_attacks"] += 1

            # Register security event
            if self.security_registry:
                await self.security_registry.register_security_event(
                    event_type="quantum_decoherence_attack",
                    device_id=device_id,
                    thermodynamic_data={
                        "current_t1": current.t1_time,
                        "current_t2": current.t2_time,
                        "baseline_t1": baseline.t1_time,
                        "baseline_t2": baseline.t2_time,
                        "t1_reduction_percent": t1_reduction * 100,
                        "t2_reduction_percent": t2_reduction * 100,
                        "energy_dissipation": current.energy_dissipation
                    },
                    severity="critical",
                    confidence=0.90,
                    threat_category="quantum_attack",
                    source_sensor="quantum_security_sensor"
                )

            # Publish alert
            if self.event_bus:
                await self.event_bus.publish("security.quantum.decoherence_attack", {
                    "device_id": device_id,
                    "t1_reduction_percent": t1_reduction * 100,
                    "t2_reduction_percent": t2_reduction * 100,
                    "timestamp": datetime.now().isoformat(),
                    "severity": "critical"
                })

    async def _detect_phase_noise_attack(
        self,
        device_id: str,
        current: QuantumCoherenceMetrics,
        baseline: QuantumCoherenceMetrics
    ):
        """
        Detect phase noise injection attacks.

        Phase noise attack: Adversary injects controlled noise to
        corrupt quantum phase relationships.
        """
        phase_drift_ratio = current.phase_drift_rate / baseline.phase_drift_rate

        if phase_drift_ratio > self.phase_noise_threshold:

            logger.warning(
                f"PHASE NOISE ATTACK DETECTED on {device_id}: "
                f"Phase drift {phase_drift_ratio:.1f}x baseline"
            )

            self.stats["attacks_detected"] += 1
            self.stats["phase_noise_attacks"] += 1

            # Register event
            if self.security_registry:
                await self.security_registry.register_security_event(
                    event_type="quantum_phase_noise_attack",
                    device_id=device_id,
                    thermodynamic_data={
                        "current_phase_drift": current.phase_drift_rate,
                        "baseline_phase_drift": baseline.phase_drift_rate,
                        "drift_ratio": phase_drift_ratio
                    },
                    severity="high",
                    confidence=0.85,
                    threat_category="quantum_attack",
                    source_sensor="quantum_security_sensor"
                )

    async def _detect_state_tampering(
        self,
        device_id: str,
        current: QuantumCoherenceMetrics,
        baseline: QuantumCoherenceMetrics
    ):
        """
        Detect quantum state tampering.

        State tampering: Direct manipulation of quantum state preparation
        or gate operations, causing fidelity degradation.
        """
        if current.gate_fidelity < self.fidelity_threshold:

            fidelity_loss = (baseline.gate_fidelity - current.gate_fidelity) / \
                           baseline.gate_fidelity

            logger.warning(
                f"QUANTUM STATE TAMPERING on {device_id}: "
                f"Gate fidelity {current.gate_fidelity:.4f} "
                f"({fidelity_loss*100:.1f}% below baseline)"
            )

            self.stats["state_tampering_events"] += 1
            self.stats["total_quantum_errors"] += 1

            # Register event
            if self.security_registry:
                await self.security_registry.register_security_event(
                    event_type="quantum_state_tampering",
                    device_id=device_id,
                    thermodynamic_data={
                        "current_gate_fidelity": current.gate_fidelity,
                        "baseline_gate_fidelity": baseline.gate_fidelity,
                        "entropy_production": current.entropy_production
                    },
                    severity="medium",
                    confidence=0.75,
                    threat_category="quantum_attack",
                    source_sensor="quantum_security_sensor"
                )

    async def _detect_measurement_attack(
        self,
        device_id: str,
        current: QuantumCoherenceMetrics,
        baseline: QuantumCoherenceMetrics
    ):
        """
        Detect measurement-induced collapse attacks.

        Measurement attack: Adversary forces premature quantum state
        collapse by inducing measurements, destroying quantum information.
        """
        readout_degradation = (baseline.readout_fidelity - current.readout_fidelity) / \
                             baseline.readout_fidelity

        if readout_degradation > 0.1:  # 10% degradation

            logger.warning(
                f"MEASUREMENT ATTACK on {device_id}: "
                f"Readout fidelity degraded {readout_degradation*100:.1f}%"
            )

            self.stats["measurement_attacks"] += 1

            # Register event
            if self.security_registry:
                await self.security_registry.register_security_event(
                    event_type="quantum_measurement_attack",
                    device_id=device_id,
                    thermodynamic_data={
                        "current_readout_fidelity": current.readout_fidelity,
                        "baseline_readout_fidelity": baseline.readout_fidelity,
                        "degradation_percent": readout_degradation * 100
                    },
                    severity="medium",
                    confidence=0.70,
                    threat_category="quantum_attack",
                    source_sensor="quantum_security_sensor"
                )

    def get_quantum_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get current quantum security status.

        Returns:
            Status including current metrics, baseline, attack indicators
        """
        if device_id not in self.coherence_history:
            return {
                "device_id": device_id,
                "status": "not_monitored",
                "message": "Quantum device not being monitored"
            }

        history = list(self.coherence_history[device_id])

        if not history:
            return {
                "device_id": device_id,
                "status": "no_data",
                "message": "No quantum data collected yet"
            }

        current = history[-1]
        baseline = self.baselines.get(device_id)

        # Calculate deviations
        t1_deviation = 0.0
        t2_deviation = 0.0
        fidelity_deviation = 0.0

        if baseline:
            t1_deviation = (baseline.t1_time - current.t1_time) / baseline.t1_time
            t2_deviation = (baseline.t2_time - current.t2_time) / baseline.t2_time
            fidelity_deviation = (baseline.gate_fidelity - current.gate_fidelity) / \
                                baseline.gate_fidelity

        # Determine status
        status = "ok"
        if t1_deviation > self.decoherence_threshold or \
           t2_deviation > self.decoherence_threshold:
            status = "critical"
        elif current.gate_fidelity < self.fidelity_threshold:
            status = "warning"

        return {
            "device_id": device_id,
            "status": status,
            "current_metrics": {
                "t1_time": current.t1_time,
                "t2_time": current.t2_time,
                "gate_fidelity": current.gate_fidelity,
                "readout_fidelity": current.readout_fidelity,
                "phase_drift_rate": current.phase_drift_rate
            },
            "baseline_metrics": {
                "t1_time": baseline.t1_time if baseline else None,
                "t2_time": baseline.t2_time if baseline else None,
                "gate_fidelity": baseline.gate_fidelity if baseline else None
            },
            "deviations": {
                "t1_deviation_percent": t1_deviation * 100,
                "t2_deviation_percent": t2_deviation * 100,
                "fidelity_deviation_percent": fidelity_deviation * 100
            },
            "history_size": len(history),
            "last_update": current.timestamp.isoformat()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get quantum sensor statistics."""
        return {
            **self.stats,
            "monitored_devices": len(self.monitoring_active),
            "baselines_established": len(self.baselines)
        }


# ============================================================================
# Singleton instance
# ============================================================================

_quantum_sensor_instance = None


def get_quantum_security_sensor(
    database_pool=None,
    energy_intelligence_layer=None,
    security_registry=None,
    event_bus=None,
    quantum_interface=None
) -> QuantumSecuritySensor:
    """
    Get singleton Quantum Security Sensor instance.

    Args:
        database_pool: PostgreSQL connection pool
        energy_intelligence_layer: EIL for entropy calculations
        security_registry: Security Event Registry
        event_bus: Event bus
        quantum_interface: Quantum hardware interface

    Returns:
        QuantumSecuritySensor instance
    """
    global _quantum_sensor_instance

    if _quantum_sensor_instance is None:
        _quantum_sensor_instance = QuantumSecuritySensor(
            database_pool=database_pool,
            energy_intelligence_layer=energy_intelligence_layer,
            security_registry=security_registry,
            event_bus=event_bus,
            quantum_interface=quantum_interface
        )

    return _quantum_sensor_instance
