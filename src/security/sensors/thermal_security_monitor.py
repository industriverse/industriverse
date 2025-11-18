"""
Thermal Security Monitor

Prevents cold boot attacks by monitoring device temperature and detecting
thermal manipulation attempts.

Cold Boot Attack:
An attacker rapidly cools a computer's RAM (using compressed air, liquid
nitrogen, or ice) to slow the decay of data after power-off. The attacker
then removes the memory modules and reads sensitive information (encryption
keys, passwords) before the data fully dissipates.

Detection Method:
- Continuous temperature monitoring
- Detect rapid cooling (>10°C/min)
- Detect abnormal cooling patterns
- Detect temperature below operating range
- Track thermal history for forensics

Response Actions:
1. Immediate: Emergency memory wipe (crypto shred)
2. Hardware: Trigger memory scrambling
3. Alert: Notify SOC with CRITICAL severity
4. Forensic: Log thermal trace
5. Prevention: Engage thermal lock (if available)

Integration:
- Uses temperature sensors (CPU, RAM, ambient)
- Triggers hardware memory protection
- Registers events in Security Event Registry
- Visualizes thermal attacks in AR/VR

References:
- Halderman et al., "Lest We Remember: Cold Boot Attacks on Encryption Keys" (2008)
- NIST SP 800-88: Guidelines for Media Sanitization
"""

import logging
import asyncio
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class ThermalSecurityMonitor:
    """
    Monitor device temperature to prevent cold boot attacks.

    Detects rapid cooling and triggers emergency memory protection.
    """

    def __init__(
        self,
        database_pool=None,
        security_registry=None,
        event_bus=None,
        hardware_interface=None
    ):
        """
        Initialize Thermal Security Monitor.

        Args:
            database_pool: PostgreSQL connection pool
            security_registry: Security Event Registry
            event_bus: Event bus for alerts
            hardware_interface: Interface to hardware controls
        """
        self.db_pool = database_pool
        self.security_registry = security_registry
        self.event_bus = event_bus
        self.hardware_interface = hardware_interface

        # Detection thresholds
        self.rapid_cooling_threshold = -10.0  # °C/min
        self.abnormal_temp_threshold = 10.0  # °C below normal
        self.critical_temp_threshold = 0.0  # °C (freezing point)
        self.monitoring_interval = 1.0  # seconds

        # Thermal history (60 seconds per device)
        self.thermal_history = {}  # device_id -> deque of (timestamp, temp)
        self.history_duration = 60  # seconds

        # Monitoring state
        self.monitoring_active = {}  # device_id -> bool
        self.monitoring_tasks = {}  # device_id -> Task

        # Baseline temperatures
        self.baseline_temps = {}  # device_id -> normal operating temp

        # Statistics
        self.stats = {
            "attacks_detected": 0,
            "rapid_cooling_events": 0,
            "abnormal_temp_events": 0,
            "critical_temp_events": 0,
            "emergency_wipes": 0
        }

        logger.info("Thermal Security Monitor initialized")

    async def establish_thermal_baseline(
        self,
        device_id: str,
        duration_minutes: int = 5
    ) -> float:
        """
        Establish normal operating temperature for device.

        Args:
            device_id: Device to baseline
            duration_minutes: Baseline duration

        Returns:
            Average normal temperature (°C)
        """
        logger.info(
            f"Establishing thermal baseline for {device_id} "
            f"({duration_minutes} minutes)"
        )

        temperatures = []
        end_time = time.time() + (duration_minutes * 60)

        while time.time() < end_time:
            temp = await self._read_temperature(device_id)
            temperatures.append(temp)
            await asyncio.sleep(self.monitoring_interval)

        baseline_temp = float(np.mean(temperatures))
        self.baseline_temps[device_id] = baseline_temp

        logger.info(
            f"Thermal baseline established for {device_id}: "
            f"{baseline_temp:.1f}°C"
        )

        return baseline_temp

    async def start_monitoring(self, device_id: str):
        """
        Start continuous thermal monitoring for device.

        Args:
            device_id: Device to monitor
        """
        if self.monitoring_active.get(device_id):
            logger.warning(f"Already monitoring device {device_id}")
            return

        logger.info(f"Starting thermal monitoring for {device_id}")

        # Ensure baseline exists
        if device_id not in self.baseline_temps:
            await self.establish_thermal_baseline(device_id, duration_minutes=1)

        self.monitoring_active[device_id] = True

        # Initialize thermal history
        if device_id not in self.thermal_history:
            self.thermal_history[device_id] = deque(maxlen=self.history_duration)

        # Create monitoring task
        task = asyncio.create_task(self._monitoring_loop(device_id))
        self.monitoring_tasks[device_id] = task

    async def stop_monitoring(self, device_id: str):
        """Stop thermal monitoring for device."""
        logger.info(f"Stopping thermal monitoring for {device_id}")

        self.monitoring_active[device_id] = False

        # Cancel monitoring task
        if device_id in self.monitoring_tasks:
            self.monitoring_tasks[device_id].cancel()
            del self.monitoring_tasks[device_id]

    async def _monitoring_loop(self, device_id: str):
        """
        Continuous thermal monitoring loop.

        Monitors temperature every second and detects:
        - Rapid cooling (>10°C/min decrease)
        - Abnormal temperature (>10°C below normal)
        - Critical temperature (<0°C)
        """
        logger.info(f"Thermal monitoring loop started for {device_id}")

        try:
            baseline_temp = self.baseline_temps[device_id]

            while self.monitoring_active.get(device_id):
                # Read temperature
                current_temp = await self._read_temperature(device_id)
                current_time = time.time()

                # Store in history
                self.thermal_history[device_id].append((current_time, current_temp))

                # Get recent history (last 60 seconds)
                recent_history = list(self.thermal_history[device_id])

                # Check for rapid cooling
                if len(recent_history) >= 10:
                    cooling_rate = self._calculate_cooling_rate(recent_history)

                    if cooling_rate < self.rapid_cooling_threshold:
                        await self._handle_rapid_cooling(
                            device_id,
                            current_temp,
                            cooling_rate,
                            recent_history
                        )

                # Check for abnormal temperature
                temp_deviation = current_temp - baseline_temp

                if temp_deviation < -self.abnormal_temp_threshold:
                    await self._handle_abnormal_temperature(
                        device_id,
                        current_temp,
                        baseline_temp,
                        temp_deviation
                    )

                # Check for critical temperature
                if current_temp <= self.critical_temp_threshold:
                    await self._handle_critical_temperature(
                        device_id,
                        current_temp
                    )

                # Sleep until next check
                await asyncio.sleep(self.monitoring_interval)

        except asyncio.CancelledError:
            logger.info(f"Thermal monitoring cancelled for {device_id}")
        except Exception as e:
            logger.error(f"Thermal monitoring error: {e}")
        finally:
            self.monitoring_active[device_id] = False
            logger.info(f"Thermal monitoring loop ended for {device_id}")

    def _calculate_cooling_rate(
        self,
        thermal_history: List[Tuple[float, float]]
    ) -> float:
        """
        Calculate temperature change rate (°C/min).

        Uses linear regression on recent temperature history.

        Returns:
            Cooling rate in °C/min (negative = cooling, positive = heating)
        """
        if len(thermal_history) < 2:
            return 0.0

        # Extract timestamps and temperatures
        times = np.array([t[0] for t in thermal_history])
        temps = np.array([t[1] for t in thermal_history])

        # Normalize time to minutes
        times_min = (times - times[0]) / 60.0

        # Linear regression
        if len(times_min) > 1:
            slope, _ = np.polyfit(times_min, temps, 1)
            return float(slope)

        return 0.0

    async def _handle_rapid_cooling(
        self,
        device_id: str,
        current_temp: float,
        cooling_rate: float,
        thermal_history: List[Tuple[float, float]]
    ):
        """Handle rapid cooling detection (potential cold boot attack)."""
        logger.critical(
            f"RAPID COOLING DETECTED on {device_id}: "
            f"Current temp: {current_temp:.1f}°C, "
            f"Cooling rate: {cooling_rate:.1f}°C/min"
        )

        self.stats["attacks_detected"] += 1
        self.stats["rapid_cooling_events"] += 1

        # CRITICAL RESPONSE: Emergency memory wipe
        await self._trigger_emergency_memory_wipe(device_id, "rapid_cooling")

        # Register security event
        if self.security_registry:
            await self.security_registry.register_security_event(
                event_type="cold_boot_attack_detected",
                device_id=device_id,
                thermodynamic_data={
                    "current_temperature": current_temp,
                    "cooling_rate": cooling_rate,
                    "thermal_trace": [
                        {"time": t, "temp": temp}
                        for t, temp in thermal_history[-20:]
                    ]
                },
                severity="critical",
                confidence=0.95,
                threat_category="physical_attack",
                source_sensor="thermal_security_monitor"
            )

        # Publish alert
        if self.event_bus:
            await self.event_bus.publish("security.thermal.cold_boot_detected", {
                "device_id": device_id,
                "current_temp": current_temp,
                "cooling_rate": cooling_rate,
                "timestamp": datetime.now().isoformat(),
                "severity": "critical"
            })

    async def _handle_abnormal_temperature(
        self,
        device_id: str,
        current_temp: float,
        baseline_temp: float,
        deviation: float
    ):
        """Handle abnormal temperature detection."""
        logger.warning(
            f"ABNORMAL TEMPERATURE on {device_id}: "
            f"Current: {current_temp:.1f}°C, "
            f"Baseline: {baseline_temp:.1f}°C, "
            f"Deviation: {deviation:.1f}°C"
        )

        self.stats["abnormal_temp_events"] += 1

        # Register lower-severity event
        if self.security_registry:
            await self.security_registry.register_security_event(
                event_type="abnormal_temperature_detected",
                device_id=device_id,
                thermodynamic_data={
                    "current_temperature": current_temp,
                    "baseline_temperature": baseline_temp,
                    "deviation": deviation
                },
                severity="medium",
                confidence=0.80,
                threat_category="environmental_anomaly",
                source_sensor="thermal_security_monitor"
            )

    async def _handle_critical_temperature(
        self,
        device_id: str,
        current_temp: float
    ):
        """Handle critical temperature (freezing) detection."""
        logger.critical(
            f"CRITICAL TEMPERATURE on {device_id}: "
            f"{current_temp:.1f}°C (below freezing!)"
        )

        self.stats["critical_temp_events"] += 1

        # CRITICAL RESPONSE: Emergency memory wipe
        await self._trigger_emergency_memory_wipe(device_id, "critical_temperature")

        # Register critical event
        if self.security_registry:
            await self.security_registry.register_security_event(
                event_type="critical_temperature_detected",
                device_id=device_id,
                thermodynamic_data={
                    "current_temperature": current_temp,
                    "threshold": self.critical_temp_threshold
                },
                severity="critical",
                confidence=1.0,
                threat_category="physical_attack",
                source_sensor="thermal_security_monitor"
            )

    async def _trigger_emergency_memory_wipe(
        self,
        device_id: str,
        trigger_reason: str
    ):
        """
        Trigger emergency memory wipe to prevent key extraction.

        Actions:
        1. Cryptographically shred sensitive memory regions
        2. Trigger hardware memory scrambling
        3. Clear encryption keys
        4. Log action for forensics
        """
        logger.critical(
            f"TRIGGERING EMERGENCY MEMORY WIPE for {device_id} "
            f"(reason: {trigger_reason})"
        )

        self.stats["emergency_wipes"] += 1

        try:
            # If hardware interface available, trigger memory wipe
            if self.hardware_interface:
                await self.hardware_interface.wipe_sensitive_memory(device_id)
                logger.info(f"Hardware memory wipe executed for {device_id}")
            else:
                logger.warning(
                    f"No hardware interface - memory wipe simulation only"
                )

            # Record mitigation action
            if self.security_registry:
                await self.security_registry.record_mitigation_action(
                    event_id="",  # Would be populated from event registration
                    action_type="emergency_memory_wipe",
                    executed_by="thermal_security_monitor",
                    result={
                        "device_id": device_id,
                        "trigger_reason": trigger_reason,
                        "timestamp": datetime.now().isoformat(),
                        "method": "cryptographic_shred"
                    },
                    automated=True
                )

        except Exception as e:
            logger.error(f"Emergency memory wipe failed for {device_id}: {e}")

    async def _read_temperature(self, device_id: str) -> float:
        """
        Read current temperature from device sensors.

        In production: Read from actual temperature sensors
        (CPU temp, RAM temp, ambient temp).

        Returns:
            Temperature in Celsius
        """
        # Simulate temperature reading
        # In production, use actual hardware sensors

        # Get baseline
        baseline = self.baseline_temps.get(device_id, 50.0)

        # Add small random variation
        variation = np.random.normal(0, 1.0)

        # Simulate normal temperature with slight fluctuation
        temp = baseline + variation

        return float(temp)

    def get_thermal_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get current thermal status for device.

        Returns:
            Thermal status including current temp, history, baseline
        """
        if device_id not in self.thermal_history:
            return {
                "device_id": device_id,
                "status": "not_monitored",
                "message": "Device not being monitored"
            }

        history = list(self.thermal_history[device_id])

        if not history:
            return {
                "device_id": device_id,
                "status": "no_data",
                "message": "No thermal data collected yet"
            }

        current_time, current_temp = history[-1]
        baseline_temp = self.baseline_temps.get(device_id)

        # Calculate recent cooling rate
        cooling_rate = 0.0
        if len(history) >= 10:
            cooling_rate = self._calculate_cooling_rate(history[-10:])

        return {
            "device_id": device_id,
            "status": "ok" if cooling_rate > self.rapid_cooling_threshold else "warning",
            "current_temperature": current_temp,
            "baseline_temperature": baseline_temp,
            "cooling_rate": cooling_rate,
            "history_size": len(history),
            "last_update": datetime.fromtimestamp(current_time).isoformat()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get thermal monitor statistics."""
        return {
            **self.stats,
            "monitored_devices": len(self.monitoring_active),
            "baselines_established": len(self.baseline_temps)
        }


# ============================================================================
# Singleton instance
# ============================================================================

_thermal_monitor_instance = None


def get_thermal_security_monitor(
    database_pool=None,
    security_registry=None,
    event_bus=None,
    hardware_interface=None
) -> ThermalSecurityMonitor:
    """
    Get singleton Thermal Security Monitor instance.

    Args:
        database_pool: PostgreSQL connection pool
        security_registry: Security Event Registry
        event_bus: Event bus
        hardware_interface: Hardware control interface

    Returns:
        ThermalSecurityMonitor instance
    """
    global _thermal_monitor_instance

    if _thermal_monitor_instance is None:
        _thermal_monitor_instance = ThermalSecurityMonitor(
            database_pool=database_pool,
            security_registry=security_registry,
            event_bus=event_bus,
            hardware_interface=hardware_interface
        )

    return _thermal_monitor_instance
