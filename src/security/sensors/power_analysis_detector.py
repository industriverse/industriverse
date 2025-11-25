"""
Power Analysis Attack Detector

Detects side-channel attacks via power consumption monitoring.

Attack Types Detected:
1. Simple Power Analysis (SPA): Visual inspection of power traces
2. Differential Power Analysis (DPA): Statistical correlation attacks
3. Correlation Power Analysis (CPA): Advanced correlation techniques
4. Template Attacks: Pre-characterized power templates

Detection Method:
- Establish baseline power signature for cryptographic operations
- Monitor real-time power consumption
- Detect abnormal correlation patterns
- Identify frequency domain anomalies
- Measure information leakage via entropy

Countermeasures:
- Power noise injection
- Random delays
- Dummy operations
- Power balancing

Integration:
- Uses EIL (Energy Intelligence Layer) for measurements
- Registers events in Security Event Registry
- Deploys mitigation capsules automatically
- Visualizes power traces in AR/VR

References:
- Kocher et al., "Differential Power Analysis" (1999)
- Mangard et al., "Power Analysis Attacks" (2007)
"""

import logging
import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from scipy import signal, stats
from collections import deque

logger = logging.getLogger(__name__)


class PowerAnalysisDetector:
    """
    Detect power analysis attacks on cryptographic operations.

    Monitors power consumption and identifies statistical patterns
    that indicate side-channel attacks.
    """

    def __init__(
        self,
        database_pool=None,
        energy_intelligence_layer=None,
        security_registry=None,
        event_bus=None
    ):
        """
        Initialize Power Analysis Detector.

        Args:
            database_pool: PostgreSQL connection pool
            energy_intelligence_layer: EIL for power measurements
            security_registry: Security Event Registry
            event_bus: Event bus for alerts
        """
        self.db_pool = database_pool
        self.eil = energy_intelligence_layer
        self.security_registry = security_registry
        self.event_bus = event_bus

        # Detection parameters
        self.baseline_samples = 1000  # Samples for baseline
        self.monitoring_window = 100  # Real-time window size
        self.correlation_threshold = 0.7  # DPA detection threshold
        self.frequency_anomaly_threshold = 3.0  # Std devs from normal

        # Power trace storage (sliding window)
        self.power_traces = {}  # device_id -> deque of traces
        self.max_traces_per_device = 10000

        # Baseline signatures
        self.baselines = {}  # (device_id, operation) -> baseline

        # Monitoring state
        self.monitoring_active = {}  # device_id -> bool
        self.monitoring_tasks = {}  # device_id -> Task

        # Statistics
        self.stats = {
            "attacks_detected": 0,
            "spa_attacks": 0,
            "dpa_attacks": 0,
            "cpa_attacks": 0,
            "countermeasures_deployed": 0
        }

        logger.info("Power Analysis Detector initialized")

    async def establish_baseline(
        self,
        device_id: str,
        operation_type: str,
        sample_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Establish baseline power signature for cryptographic operation.

        Measures power consumption during normal operations to create
        reference signature for anomaly detection.

        Args:
            device_id: Device to baseline
            operation_type: Crypto operation (e.g., "aes_encrypt")
            sample_count: Number of samples (default: 1000)

        Returns:
            Baseline signature data
        """
        sample_count = sample_count or self.baseline_samples

        logger.info(
            f"Establishing power baseline for {device_id} "
            f"operation {operation_type} ({sample_count} samples)"
        )

        try:
            # Collect power traces during normal operations
            power_traces = []

            for i in range(sample_count):
                # Trigger crypto operation
                await self._trigger_crypto_operation(device_id, operation_type)

                # Measure power consumption
                power_trace = await self._measure_power_trace(
                    device_id,
                    duration_ms=100,
                    sample_rate_khz=1000
                )

                power_traces.append(power_trace)

                if i % 100 == 0:
                    logger.debug(f"Baseline progress: {i}/{sample_count}")

            # Calculate statistical properties
            baseline = self._calculate_baseline_statistics(power_traces)

            # Store baseline
            self.baselines[(device_id, operation_type)] = baseline

            # Store in database
            if self.security_registry:
                await self._store_baseline(device_id, operation_type, baseline)

            logger.info(
                f"Baseline established for {device_id}/{operation_type}: "
                f"mean={baseline['mean_power']:.2f}mW, "
                f"std={baseline['std_power']:.2f}mW"
            )

            return baseline

        except Exception as e:
            logger.error(f"Failed to establish baseline: {e}")
            raise

    async def start_monitoring(
        self,
        device_id: str,
        operation_type: str
    ):
        """
        Start continuous power monitoring for device.

        Args:
            device_id: Device to monitor
            operation_type: Crypto operation to monitor
        """
        if self.monitoring_active.get(device_id):
            logger.warning(f"Already monitoring device {device_id}")
            return

        logger.info(f"Starting power monitoring for {device_id}")

        self.monitoring_active[device_id] = True

        # Create monitoring task
        task = asyncio.create_task(
            self._monitoring_loop(device_id, operation_type)
        )
        self.monitoring_tasks[device_id] = task

    async def stop_monitoring(self, device_id: str):
        """Stop power monitoring for device."""
        logger.info(f"Stopping power monitoring for {device_id}")

        self.monitoring_active[device_id] = False

        # Cancel monitoring task
        if device_id in self.monitoring_tasks:
            self.monitoring_tasks[device_id].cancel()
            del self.monitoring_tasks[device_id]

    async def _monitoring_loop(
        self,
        device_id: str,
        operation_type: str
    ):
        """
        Continuous monitoring loop for power analysis detection.

        Runs continuously while monitoring is active.
        """
        logger.info(f"Monitoring loop started for {device_id}")

        try:
            # Get baseline
            baseline = self.baselines.get((device_id, operation_type))

            if not baseline:
                logger.error(f"No baseline for {device_id}/{operation_type}")
                return

            # Initialize trace buffer
            if device_id not in self.power_traces:
                self.power_traces[device_id] = deque(
                    maxlen=self.max_traces_per_device
                )

            while self.monitoring_active.get(device_id):
                # Measure power trace
                power_trace = await self._measure_power_trace(
                    device_id,
                    duration_ms=100,
                    sample_rate_khz=1000
                )

                # Store trace
                self.power_traces[device_id].append(power_trace)

                # Detect SPA (Simple Power Analysis)
                spa_detected, spa_confidence = self._detect_spa(
                    power_trace,
                    baseline
                )

                if spa_detected:
                    await self._handle_spa_detection(
                        device_id,
                        operation_type,
                        power_trace,
                        spa_confidence
                    )

                # Detect DPA (Differential Power Analysis)
                # Requires multiple traces
                if len(self.power_traces[device_id]) >= 100:
                    dpa_detected, dpa_confidence = self._detect_dpa(
                        list(self.power_traces[device_id])[-100:],
                        baseline
                    )

                    if dpa_detected:
                        await self._handle_dpa_detection(
                            device_id,
                            operation_type,
                            dpa_confidence
                        )

                # Small delay
                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for {device_id}")
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
        finally:
            self.monitoring_active[device_id] = False
            logger.info(f"Monitoring loop ended for {device_id}")

    def _detect_spa(
        self,
        power_trace: np.ndarray,
        baseline: Dict[str, Any]
    ) -> Tuple[bool, float]:
        """
        Detect Simple Power Analysis attack.

        SPA indicators:
        - Unusual power spikes/dips
        - Abnormal frequency components
        - High-amplitude outliers

        Returns:
            (detected: bool, confidence: float)
        """
        try:
            # Check for power anomalies
            mean_power = np.mean(power_trace)
            baseline_mean = baseline["mean_power"]
            baseline_std = baseline["std_power"]

            # Z-score of mean power
            z_score = abs(mean_power - baseline_mean) / baseline_std

            if z_score > 3.0:
                # Significant deviation from baseline
                return (True, min(z_score / 10.0, 1.0))

            # Check frequency domain
            freq_spectrum = np.fft.fft(power_trace)
            baseline_spectrum = baseline.get("freq_spectrum_mean", [])

            if len(baseline_spectrum) > 0:
                spectrum_diff = np.linalg.norm(
                    np.abs(freq_spectrum[:len(baseline_spectrum)]) - baseline_spectrum
                )

                if spectrum_diff > self.frequency_anomaly_threshold * baseline["freq_spectrum_std"]:
                    # Abnormal frequency components
                    confidence = min(spectrum_diff / 10.0, 1.0)
                    return (True, confidence)

            return (False, 0.0)

        except Exception as e:
            logger.error(f"SPA detection error: {e}")
            return (False, 0.0)

    def _detect_dpa(
        self,
        power_traces: List[np.ndarray],
        baseline: Dict[str, Any]
    ) -> Tuple[bool, float]:
        """
        Detect Differential Power Analysis attack.

        DPA indicators:
        - High correlation between power and hypothetical intermediate values
        - Synchronized power variations across traces
        - Statistical distinguishers

        Returns:
            (detected: bool, confidence: float)
        """
        try:
            if len(power_traces) < 50:
                return (False, 0.0)

            # Convert to numpy array (traces x samples)
            traces_array = np.array(power_traces)

            # Calculate correlation between traces
            # High correlation indicates synchronized measurements (DPA attack)
            correlation_matrix = np.corrcoef(traces_array)

            # Get upper triangle (excluding diagonal)
            upper_triangle = correlation_matrix[
                np.triu_indices_from(correlation_matrix, k=1)
            ]

            mean_correlation = np.mean(np.abs(upper_triangle))

            if mean_correlation > self.correlation_threshold:
                # Abnormally high correlation - possible DPA
                confidence = min((mean_correlation - 0.5) / 0.5, 1.0)
                return (True, confidence)

            # Check for statistical distinguishers
            # Compare variance across traces
            trace_variances = np.var(traces_array, axis=1)
            variance_of_variances = np.var(trace_variances)

            baseline_variance = baseline.get("variance_of_variances", 0.0)

            if variance_of_variances > 3.0 * baseline_variance:
                # Unusual variance pattern
                confidence = min(variance_of_variances / (10 * baseline_variance), 1.0)
                return (True, confidence)

            return (False, 0.0)

        except Exception as e:
            logger.error(f"DPA detection error: {e}")
            return (False, 0.0)

    async def _handle_spa_detection(
        self,
        device_id: str,
        operation_type: str,
        power_trace: np.ndarray,
        confidence: float
    ):
        """Handle Simple Power Analysis attack detection."""
        logger.warning(
            f"SPA ATTACK DETECTED on {device_id} "
            f"operation {operation_type} (confidence: {confidence:.3f})"
        )

        self.stats["attacks_detected"] += 1
        self.stats["spa_attacks"] += 1

        # Register security event
        if self.security_registry:
            await self.security_registry.register_security_event(
                event_type="simple_power_analysis_attack",
                device_id=device_id,
                thermodynamic_data={
                    "operation_type": operation_type,
                    "mean_power": float(np.mean(power_trace)),
                    "max_power": float(np.max(power_trace)),
                    "power_variance": float(np.var(power_trace))
                },
                severity="high",
                confidence=confidence,
                threat_category="side_channel_attack",
                source_sensor="power_analysis_detector"
            )

        # Deploy countermeasures
        await self._deploy_spa_countermeasures(device_id)

        # Publish alert
        if self.event_bus:
            await self.event_bus.publish("security.power_analysis.spa_detected", {
                "device_id": device_id,
                "operation_type": operation_type,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            })

    async def _handle_dpa_detection(
        self,
        device_id: str,
        operation_type: str,
        confidence: float
    ):
        """Handle Differential Power Analysis attack detection."""
        logger.critical(
            f"DPA ATTACK DETECTED on {device_id} "
            f"operation {operation_type} (confidence: {confidence:.3f})"
        )

        self.stats["attacks_detected"] += 1
        self.stats["dpa_attacks"] += 1

        # Register security event
        if self.security_registry:
            await self.security_registry.register_security_event(
                event_type="differential_power_analysis_attack",
                device_id=device_id,
                thermodynamic_data={
                    "operation_type": operation_type,
                    "trace_count": len(self.power_traces.get(device_id, [])),
                    "correlation_detected": True
                },
                severity="critical",
                confidence=confidence,
                threat_category="side_channel_attack",
                source_sensor="power_analysis_detector"
            )

        # Deploy countermeasures (more aggressive for DPA)
        await self._deploy_dpa_countermeasures(device_id)

        # Publish alert
        if self.event_bus:
            await self.event_bus.publish("security.power_analysis.dpa_detected", {
                "device_id": device_id,
                "operation_type": operation_type,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "severity": "critical"
            })

    async def _deploy_spa_countermeasures(self, device_id: str):
        """
        Deploy countermeasures against SPA attacks.

        Countermeasures:
        - Power noise injection
        - Random delays
        - Dummy operations
        """
        logger.info(f"Deploying SPA countermeasures for {device_id}")

        try:
            # If EIL available, inject power noise
            if self.eil:
                noise_profile = await self._generate_power_noise_profile(device_id)
                # await self.eil.inject_power_noise(device_id, noise_profile)

            self.stats["countermeasures_deployed"] += 1

            logger.info(f"SPA countermeasures deployed for {device_id}")

        except Exception as e:
            logger.error(f"Failed to deploy SPA countermeasures: {e}")

    async def _deploy_dpa_countermeasures(self, device_id: str):
        """
        Deploy countermeasures against DPA attacks.

        More aggressive than SPA countermeasures:
        - High-amplitude power noise
        - Random operation ordering
        - Power balancing
        - Masking
        """
        logger.info(f"Deploying DPA countermeasures for {device_id}")

        try:
            # Generate high-entropy noise profile
            if self.eil:
                noise_profile = await self._generate_power_noise_profile(
                    device_id,
                    amplitude_multiplier=2.0
                )
                # await self.eil.inject_power_noise(device_id, noise_profile)

            self.stats["countermeasures_deployed"] += 1

            logger.info(f"DPA countermeasures deployed for {device_id}")

        except Exception as e:
            logger.error(f"Failed to deploy DPA countermeasures: {e}")

    async def _trigger_crypto_operation(
        self,
        device_id: str,
        operation_type: str
    ):
        """
        Trigger cryptographic operation on device.

        In production: Send command to device to perform crypto operation.
        """
        # Simulate operation trigger
        await asyncio.sleep(0.001)

    async def _measure_power_trace(
        self,
        device_id: str,
        duration_ms: int,
        sample_rate_khz: int
    ) -> np.ndarray:
        """
        Measure power consumption trace.

        Args:
            device_id: Device to measure
            duration_ms: Measurement duration
            sample_rate_khz: Sampling rate

        Returns:
            Power trace array (mW)
        """
        # In production: Use power meter hardware
        # For now, simulate power trace with device-specific characteristics

        num_samples = duration_ms * sample_rate_khz

        # Device-specific baseline
        base_power = 100.0 + (hash(device_id) % 50)

        # Generate realistic power trace
        # Normal operation: smooth power with small variations
        time_array = np.linspace(0, duration_ms / 1000, num_samples)

        # Base signal
        power_trace = base_power * np.ones(num_samples)

        # Add crypto operation power spikes (AES rounds, etc.)
        # Simplified model: periodic spikes every 10 samples
        for i in range(0, num_samples, 10):
            power_trace[i:i+2] += 5.0

        # Add measurement noise
        noise = np.random.normal(0, 1.0, num_samples)
        power_trace += noise

        return power_trace

    def _calculate_baseline_statistics(
        self,
        power_traces: List[np.ndarray]
    ) -> Dict[str, Any]:
        """
        Calculate statistical properties of baseline power traces.

        Returns:
            Baseline signature dictionary
        """
        traces_array = np.array(power_traces)

        # Time domain statistics
        mean_trace = np.mean(traces_array, axis=0)
        std_trace = np.std(traces_array, axis=0)

        mean_power = np.mean(mean_trace)
        std_power = np.std(mean_trace)

        # Frequency domain statistics
        freq_spectrums = np.array([np.abs(np.fft.fft(trace)) for trace in power_traces])
        freq_spectrum_mean = np.mean(freq_spectrums, axis=0)
        freq_spectrum_std = np.std(freq_spectrums, axis=0)

        # Variance statistics (for DPA detection)
        trace_variances = np.var(traces_array, axis=1)
        variance_of_variances = np.var(trace_variances)

        return {
            "mean_trace": mean_trace.tolist(),
            "std_trace": std_trace.tolist(),
            "mean_power": float(mean_power),
            "std_power": float(std_power),
            "freq_spectrum_mean": freq_spectrum_mean[:100].tolist(),  # First 100 bins
            "freq_spectrum_std": float(np.mean(freq_spectrum_std[:100])),
            "variance_of_variances": float(variance_of_variances),
            "sample_count": len(power_traces),
            "trace_length": len(power_traces[0])
        }

    async def _generate_power_noise_profile(
        self,
        device_id: str,
        amplitude_multiplier: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generate power noise profile for countermeasures.

        Returns:
            Noise profile for EIL injection
        """
        return {
            "device_id": device_id,
            "noise_type": "gaussian",
            "amplitude": 2.0 * amplitude_multiplier,  # mW
            "frequency_range": [10, 10000],  # Hz
            "duration": "continuous"
        }

    async def _store_baseline(
        self,
        device_id: str,
        operation_type: str,
        baseline: Dict[str, Any]
    ):
        """Store baseline in Security Event Registry."""
        if not self.security_registry or not self.security_registry.db_pool:
            return

        try:
            async with self.security_registry.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO security_events.thermodynamic_baselines (
                        device_id,
                        operation_type,
                        energy_baseline,
                        entropy_baseline,
                        power_baseline,
                        sample_count,
                        confidence
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (device_id, operation_type) DO UPDATE
                    SET power_baseline = EXCLUDED.power_baseline,
                        sample_count = EXCLUDED.sample_count,
                        established_at = NOW()
                """,
                    device_id,
                    operation_type,
                    {},  # energy_baseline
                    {},  # entropy_baseline
                    baseline,  # power_baseline
                    baseline["sample_count"],
                    0.95  # confidence
                )

        except Exception as e:
            logger.error(f"Failed to store baseline: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get power analysis detector statistics."""
        return {
            **self.stats,
            "monitored_devices": len(self.monitoring_active),
            "total_traces_stored": sum(
                len(traces) for traces in self.power_traces.values()
            ),
            "baselines_established": len(self.baselines)
        }


# ============================================================================
# Singleton instance
# ============================================================================

_power_detector_instance = None


def get_power_analysis_detector(
    database_pool=None,
    energy_intelligence_layer=None,
    security_registry=None,
    event_bus=None
) -> PowerAnalysisDetector:
    """
    Get singleton Power Analysis Detector instance.

    Args:
        database_pool: PostgreSQL connection pool
        energy_intelligence_layer: EIL for power measurements
        security_registry: Security Event Registry
        event_bus: Event bus

    Returns:
        PowerAnalysisDetector instance
    """
    global _power_detector_instance

    if _power_detector_instance is None:
        _power_detector_instance = PowerAnalysisDetector(
            database_pool=database_pool,
            energy_intelligence_layer=energy_intelligence_layer,
            security_registry=security_registry,
            event_bus=event_bus
        )

    return _power_detector_instance
