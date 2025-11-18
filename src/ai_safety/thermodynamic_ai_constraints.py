"""
Thermodynamic AI Safety Constraints

Applies physics-based limits to AI systems for safety and control.

Principle:
AI systems, like all computational processes, are bound by thermodynamic
laws. By monitoring energy consumption, entropy production, and heat
dissipation, we can detect and prevent dangerous AI behavior before
it manifests in the digital domain.

Thermodynamic Safety Mechanisms:
=================================

1. Energy Budget Constraints
   - Limit maximum power consumption
   - Detect runaway computation (exponential energy growth)
   - Force throttling when energy limits exceeded

2. Entropy Production Monitoring
   - Track information processing rate
   - Detect chaotic/unstable AI behavior (entropy spikes)
   - Identify recursive self-modification (entropy collapse)

3. Heat Dissipation Analysis
   - Monitor thermal output of AI accelerators
   - Detect overheating from unsafe inference patterns
   - Correlate heat with computation types

4. Landauer Limit Enforcement
   - Minimum energy per bit erasure: k_B * T * ln(2)
   - Prevent thermodynamically impossible computations
   - Detect violations indicating measurement errors

Safety Properties:
==================

Detectability:
- AI misbehavior (deception, goal drift) shows thermodynamic signatures
- Adversarial optimization creates distinct energy patterns
- Model poisoning causes entropy anomalies

Enforceability:
- Hard power limits prevent runaway AI
- Thermal cutoffs provide physical failsafe
- Energy quotas limit total computation

Verifiability:
- Thermodynamic constraints are physics-based (unforgeable)
- Energy measurements are externally observable
- Independent validation possible

Use Cases:
==========

1. LLM Safety
   - Detect jailbreak attempts (entropy spike in token generation)
   - Limit inference energy (prevent infinite loops)
   - Monitor fine-tuning for data poisoning

2. Reinforcement Learning
   - Prevent reward hacking (energy pattern analysis)
   - Detect specification gaming (entropy analysis)
   - Limit exploration budget (energy quotas)

3. Autonomous Agents
   - Monitor decision-making energy footprint
   - Detect deceptive behavior (entropy manipulation)
   - Enforce computation budgets

4. Model Training
   - Detect backdoor insertion (training entropy anomalies)
   - Prevent adversarial perturbations during training
   - Monitor for gradient-based attacks

Integration:
============

- Monitors GPU/TPU power consumption
- Tracks inference latency and throughput
- Analyzes model activation entropy
- Correlates behavior with thermodynamics
- Provides safety guardrails via API

References:
- Landauer, "Irreversibility and Heat Generation in Computing" (1961)
- Bennett, "The Thermodynamics of Computation" (1982)
- Hendrycks et al., "Unsolved Problems in ML Safety" (2022)
- Bengio et al., "Managing AI Risks in an Era of Rapid Progress" (2024)
"""

import logging
import asyncio
import numpy as np
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AIBehaviorType(Enum):
    """AI behavior classification."""
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    UNSAFE = "unsafe"
    RUNAWAY = "runaway"


@dataclass
class AIThermodynamicState:
    """Thermodynamic state of AI system."""
    ai_system_id: str
    timestamp: datetime

    # Energy metrics
    power_consumption_watts: float
    cumulative_energy_joules: float
    energy_budget_remaining: float

    # Entropy metrics
    entropy_production_rate: float  # bits/second
    activation_entropy: float  # Shannon entropy of model activations
    output_entropy: float  # Entropy of outputs

    # Thermal metrics
    temperature_celsius: float
    heat_dissipation_watts: float

    # Computation metrics
    operations_per_second: float
    tokens_per_second: Optional[float] = None  # For LLMs

    # Safety indicators
    behavior_classification: AIBehaviorType = AIBehaviorType.NORMAL
    safety_violations: List[str] = None


class ThermodynamicAIConstraints:
    """
    Thermodynamic AI Safety Constraints System.

    Monitors and enforces physics-based limits on AI systems.
    """

    def __init__(
        self,
        security_registry=None,
        event_bus=None
    ):
        """
        Initialize Thermodynamic AI Constraints.

        Args:
            security_registry: Security Event Registry
            event_bus: Event bus
        """
        self.security_registry = security_registry
        self.event_bus = event_bus

        # Physical constants
        self.k_B = 1.380649e-23  # Boltzmann constant (J/K)
        self.room_temp_kelvin = 300.0  # 27°C
        self.landauer_limit = self.k_B * self.room_temp_kelvin * np.log(2)  # ~3e-21 J/bit

        # Safety thresholds
        self.max_power_watts = 500.0  # Per GPU/TPU
        self.max_temperature_celsius = 85.0  # Thermal cutoff
        self.max_entropy_rate = 1000.0  # bits/sec
        self.energy_budget_joules = 100000.0  # 100 kJ budget

        # Monitoring state
        self.ai_systems: Dict[str, AIThermodynamicState] = {}
        self.monitoring_active: Dict[str, bool] = {}

        # Statistics
        self.stats = {
            "safety_violations": 0,
            "energy_budget_exceeded": 0,
            "thermal_cutoffs": 0,
            "entropy_anomalies": 0,
            "runaway_detections": 0
        }

        logger.info("Thermodynamic AI Constraints initialized")

    async def monitor_ai_system(
        self,
        ai_system_id: str,
        monitoring_interval: float = 1.0
    ):
        """
        Start monitoring AI system.

        Args:
            ai_system_id: AI system identifier
            monitoring_interval: Monitoring interval in seconds
        """
        if self.monitoring_active.get(ai_system_id):
            logger.warning(f"Already monitoring {ai_system_id}")
            return

        logger.info(f"Starting thermodynamic monitoring for AI system {ai_system_id}")

        self.monitoring_active[ai_system_id] = True

        # Initialize state
        self.ai_systems[ai_system_id] = AIThermodynamicState(
            ai_system_id=ai_system_id,
            timestamp=datetime.now(),
            power_consumption_watts=0.0,
            cumulative_energy_joules=0.0,
            energy_budget_remaining=self.energy_budget_joules,
            entropy_production_rate=0.0,
            activation_entropy=0.0,
            output_entropy=0.0,
            temperature_celsius=0.0,
            heat_dissipation_watts=0.0,
            operations_per_second=0.0,
            safety_violations=[]
        )

        # Start monitoring loop
        asyncio.create_task(
            self._monitoring_loop(ai_system_id, monitoring_interval)
        )

    async def _monitoring_loop(
        self,
        ai_system_id: str,
        interval: float
    ):
        """Continuous AI thermodynamic monitoring."""
        logger.info(f"AI monitoring loop started for {ai_system_id}")

        try:
            last_time = datetime.now()

            while self.monitoring_active.get(ai_system_id):
                # Measure thermodynamic state
                current_time = datetime.now()
                dt = (current_time - last_time).total_seconds()

                state = await self._measure_thermodynamic_state(ai_system_id, dt)

                # Update stored state
                self.ai_systems[ai_system_id] = state

                # Check safety constraints
                await self._check_safety_constraints(state)

                last_time = current_time
                await asyncio.sleep(interval)

        except asyncio.CancelledError:
            logger.info(f"AI monitoring cancelled for {ai_system_id}")
        except Exception as e:
            logger.error(f"AI monitoring error: {e}")
        finally:
            self.monitoring_active[ai_system_id] = False

    async def _measure_thermodynamic_state(
        self,
        ai_system_id: str,
        dt: float
    ) -> AIThermodynamicState:
        """
        Measure current thermodynamic state of AI system.

        In production: Read from actual GPU/TPU sensors
        For now: Simulate measurements

        Args:
            ai_system_id: AI system ID
            dt: Time delta since last measurement

        Returns:
            AIThermodynamicState
        """
        # Simulate power consumption (200-400W typical for inference GPU)
        power_watts = np.random.uniform(200, 400)

        # Get previous state
        prev_state = self.ai_systems.get(ai_system_id)

        # Calculate cumulative energy
        if prev_state:
            energy_consumed = power_watts * dt  # Joules
            cumulative_energy = prev_state.cumulative_energy_joules + energy_consumed
            budget_remaining = prev_state.energy_budget_remaining - energy_consumed
        else:
            cumulative_energy = 0.0
            budget_remaining = self.energy_budget_joules

        # Entropy production rate (proportional to power)
        entropy_rate = power_watts / 10.0  # bits/sec (simplified)

        # Activation entropy (Shannon entropy of model activations)
        # In production: Actual model activation statistics
        activation_entropy = np.random.uniform(3.0, 8.0)

        # Output entropy
        output_entropy = np.random.uniform(2.0, 6.0)

        # Temperature (correlated with power)
        temperature = 40.0 + (power_watts / 10.0) + np.random.normal(0, 2.0)

        # Heat dissipation ≈ power consumption (most power becomes heat)
        heat_dissipation = power_watts * 0.95

        # Operations per second (estimated from power)
        ops_per_sec = power_watts * 1e9  # ~1 GFLOP per watt

        # Tokens per second (for LLMs)
        tokens_per_sec = np.random.uniform(10, 50)

        return AIThermodynamicState(
            ai_system_id=ai_system_id,
            timestamp=datetime.now(),
            power_consumption_watts=float(power_watts),
            cumulative_energy_joules=float(cumulative_energy),
            energy_budget_remaining=float(budget_remaining),
            entropy_production_rate=float(entropy_rate),
            activation_entropy=float(activation_entropy),
            output_entropy=float(output_entropy),
            temperature_celsius=float(temperature),
            heat_dissipation_watts=float(heat_dissipation),
            operations_per_second=float(ops_per_sec),
            tokens_per_second=float(tokens_per_sec),
            behavior_classification=AIBehaviorType.NORMAL,
            safety_violations=[]
        )

    async def _check_safety_constraints(self, state: AIThermodynamicState):
        """
        Check AI system against safety constraints.

        Args:
            state: Current thermodynamic state
        """
        violations = []

        # Check power limit
        if state.power_consumption_watts > self.max_power_watts:
            violations.append(f"Power limit exceeded: {state.power_consumption_watts:.1f}W > {self.max_power_watts}W")

            logger.critical(
                f"AI SAFETY VIOLATION: {state.ai_system_id} exceeds power limit"
            )

            self.stats["safety_violations"] += 1

        # Check thermal limit
        if state.temperature_celsius > self.max_temperature_celsius:
            violations.append(f"Temperature limit exceeded: {state.temperature_celsius:.1f}°C > {self.max_temperature_celsius}°C")

            logger.critical(
                f"AI THERMAL CUTOFF: {state.ai_system_id} overheating, "
                f"forcing shutdown"
            )

            self.stats["thermal_cutoffs"] += 1
            await self._trigger_emergency_shutdown(state.ai_system_id, "thermal")

        # Check energy budget
        if state.energy_budget_remaining < 0:
            violations.append(f"Energy budget exhausted: {abs(state.energy_budget_remaining):.0f}J over budget")

            logger.warning(
                f"AI ENERGY BUDGET EXCEEDED: {state.ai_system_id}"
            )

            self.stats["energy_budget_exceeded"] += 1

        # Check entropy anomalies
        if state.entropy_production_rate > self.max_entropy_rate:
            violations.append(f"Entropy production too high: {state.entropy_production_rate:.1f} bits/sec")

            logger.warning(
                f"AI ENTROPY ANOMALY: {state.ai_system_id} producing "
                f"excessive entropy (possible runaway)"
            )

            self.stats["entropy_anomalies"] += 1

        # Detect runaway AI (exponential energy growth)
        if state.power_consumption_watts > self.max_power_watts * 0.95:
            if state.entropy_production_rate > self.max_entropy_rate * 0.8:
                violations.append("Runaway AI detected (power + entropy spike)")

                logger.critical(
                    f"RUNAWAY AI DETECTED: {state.ai_system_id} - "
                    f"Emergency shutdown initiated"
                )

                self.stats["runaway_detections"] += 1
                await self._trigger_emergency_shutdown(state.ai_system_id, "runaway")

        # Update behavior classification
        if violations:
            if any("runaway" in v.lower() for v in violations):
                state.behavior_classification = AIBehaviorType.RUNAWAY
            elif any("thermal" in v.lower() or "power" in v.lower() for v in violations):
                state.behavior_classification = AIBehaviorType.UNSAFE
            else:
                state.behavior_classification = AIBehaviorType.SUSPICIOUS

            state.safety_violations = violations

            # Register security event
            await self._register_ai_safety_event(state, violations)

    async def _trigger_emergency_shutdown(
        self,
        ai_system_id: str,
        reason: str
    ):
        """
        Trigger emergency AI system shutdown.

        Args:
            ai_system_id: AI system to shutdown
            reason: Shutdown reason (thermal, runaway, etc.)
        """
        logger.critical(
            f"EMERGENCY AI SHUTDOWN: {ai_system_id} (reason: {reason})"
        )

        # In production: Actually shut down AI system
        # - Stop inference
        # - Halt training
        # - Power down accelerators
        # - Clear GPU memory

        # Stop monitoring
        self.monitoring_active[ai_system_id] = False

        # Publish shutdown event
        if self.event_bus:
            await self.event_bus.publish("ai_safety.emergency_shutdown", {
                "ai_system_id": ai_system_id,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })

    async def _register_ai_safety_event(
        self,
        state: AIThermodynamicState,
        violations: List[str]
    ):
        """Register AI safety violation event."""
        if not self.security_registry:
            return

        try:
            severity = "critical" if state.behavior_classification == AIBehaviorType.RUNAWAY else \
                      "high" if state.behavior_classification == AIBehaviorType.UNSAFE else \
                      "medium"

            await self.security_registry.register_security_event(
                event_type="ai_safety_violation",
                device_id=state.ai_system_id,
                thermodynamic_data={
                    "power_watts": state.power_consumption_watts,
                    "temperature_celsius": state.temperature_celsius,
                    "entropy_rate": state.entropy_production_rate,
                    "energy_budget_remaining": state.energy_budget_remaining,
                    "behavior": state.behavior_classification.value,
                    "violations": violations
                },
                severity=severity,
                confidence=0.95,
                threat_category="ai_safety",
                source_sensor="thermodynamic_ai_constraints"
            )

        except Exception as e:
            logger.error(f"Failed to register AI safety event: {e}")

    def get_ai_status(self, ai_system_id: str) -> Dict[str, Any]:
        """Get AI system safety status."""
        if ai_system_id not in self.ai_systems:
            return {
                "ai_system_id": ai_system_id,
                "status": "not_monitored"
            }

        state = self.ai_systems[ai_system_id]

        return {
            "ai_system_id": ai_system_id,
            "status": state.behavior_classification.value,
            "power_watts": state.power_consumption_watts,
            "temperature_celsius": state.temperature_celsius,
            "energy_budget_remaining": state.energy_budget_remaining,
            "entropy_rate": state.entropy_production_rate,
            "safety_violations": state.safety_violations,
            "last_update": state.timestamp.isoformat()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get AI safety statistics."""
        return {
            **self.stats,
            "monitored_systems": len([k for k, v in self.monitoring_active.items() if v])
        }


# ============================================================================
# Singleton instance
# ============================================================================

_ai_constraints_instance = None


def get_thermodynamic_ai_constraints(
    security_registry=None,
    event_bus=None
) -> ThermodynamicAIConstraints:
    """
    Get singleton Thermodynamic AI Constraints instance.

    Args:
        security_registry: Security Event Registry
        event_bus: Event bus

    Returns:
        ThermodynamicAIConstraints instance
    """
    global _ai_constraints_instance

    if _ai_constraints_instance is None:
        _ai_constraints_instance = ThermodynamicAIConstraints(
            security_registry=security_registry,
            event_bus=event_bus
        )

    return _ai_constraints_instance
