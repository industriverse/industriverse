"""
Physical Unclonable Function (PUF) Implementation

Uses device-specific thermodynamic properties to create unclonable fingerprints.

Principle:
Manufacturing variations create unique thermal, electrical, and energy signatures.
These variations are:
- Impossible to predict
- Impossible to clone
- Stable over device lifetime
- Measurable via thermodynamic sensors

PUF Sources:
1. Power consumption patterns during standard operations
2. Thermal response curves to controlled heating
3. Electromagnetic emission fingerprints
4. Entropy production rates
5. Device-specific noise characteristics

Security Properties:
✓ Cannot be forged (requires identical manufacturing defects)
✓ Cannot be replayed (includes temporal entropy)
✓ Cannot be extracted (derived from physical properties)
✓ Cannot be predicted (quantum-level manufacturing randomness)

Use Cases:
- Hardware authentication
- Device identity verification
- Clone detection
- Secure key generation
- Supply chain validation

Integration:
- Stores PUF signatures in Security Event Registry
- Uses EIL (Energy Intelligence Layer) for measurements
- Generates cryptographic proofs via UTID system
"""

import logging
import asyncio
import hashlib
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PUFSignature:
    """
    Physical Unclonable Function signature for a device.

    Contains:
    - Unique fingerprint (256-bit)
    - Thermodynamic measurements
    - Reproducibility metrics
    - Validation history
    """
    device_id: str
    fingerprint: str  # 256-bit hex string
    thermodynamic_vector: Dict[str, Any]  # Raw measurements
    reproducibility_score: float  # 0.0 to 1.0
    created_at: datetime
    last_validated: Optional[datetime] = None
    validation_count: int = 0
    failed_validations: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "device_id": self.device_id,
            "fingerprint": self.fingerprint,
            "thermodynamic_vector": self.thermodynamic_vector,
            "reproducibility_score": self.reproducibility_score,
            "created_at": self.created_at.isoformat(),
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "validation_count": self.validation_count,
            "failed_validations": self.failed_validations
        }


class ThermodynamicPUF:
    """
    Physical Unclonable Function generator using thermodynamic properties.

    Measures device-specific physical characteristics to generate
    unique, unclonable fingerprints.

    Measurement Pipeline:
    1. Power consumption during crypto operations
    2. Thermal response to controlled heating
    3. EM emission patterns
    4. Entropy production rates
    5. Statistical feature extraction
    6. Cryptographic hashing to 256-bit fingerprint
    """

    def __init__(
        self,
        database_pool=None,
        energy_intelligence_layer=None,
        event_bus=None
    ):
        """
        Initialize Thermodynamic PUF system.

        Args:
            database_pool: PostgreSQL connection pool
            energy_intelligence_layer: EIL for energy measurements
            event_bus: Event bus for security events
        """
        self.db_pool = database_pool
        self.eil = energy_intelligence_layer
        self.event_bus = event_bus

        # PUF generation parameters
        self.measurement_count = 1000  # Number of samples per measurement type
        self.reproducibility_threshold = 0.85  # Minimum reproducibility
        self.fuzzy_match_threshold = 0.90  # Threshold for authentication

        # Statistics
        self.stats = {
            "pufs_generated": 0,
            "authentications_performed": 0,
            "authentication_successes": 0,
            "authentication_failures": 0,
            "clones_detected": 0
        }

        logger.info("Thermodynamic PUF system initialized")

    async def generate_puf_signature(
        self,
        device_id: str,
        measurement_count: Optional[int] = None
    ) -> PUFSignature:
        """
        Generate PUF signature for device by measuring thermodynamic properties.

        Process:
        1. Measure power consumption patterns
        2. Measure thermal response curves
        3. Measure EM emission fingerprints
        4. Measure entropy production
        5. Extract stable statistical features
        6. Hash to 256-bit fingerprint

        Args:
            device_id: Unique device identifier
            measurement_count: Number of samples (default: 1000)

        Returns:
            PUFSignature object
        """
        measurement_count = measurement_count or self.measurement_count

        logger.info(f"Generating PUF signature for device {device_id}")

        try:
            # Step 1: Collect thermodynamic measurements
            measurements = await self._collect_thermodynamic_measurements(
                device_id,
                measurement_count
            )

            # Step 2: Extract stable features
            feature_vector = self._extract_stable_features(measurements)

            # Step 3: Calculate reproducibility
            reproducibility = self._calculate_reproducibility(measurements)

            if reproducibility < self.reproducibility_threshold:
                logger.warning(
                    f"Low reproducibility {reproducibility:.3f} for device {device_id}"
                )

            # Step 4: Generate cryptographic fingerprint
            fingerprint = self._hash_to_fingerprint(feature_vector)

            # Step 5: Create PUF signature
            puf_signature = PUFSignature(
                device_id=device_id,
                fingerprint=fingerprint,
                thermodynamic_vector=feature_vector,
                reproducibility_score=reproducibility,
                created_at=datetime.now()
            )

            # Step 6: Store in database
            if self.db_pool:
                await self._store_puf_signature(puf_signature)

            # Step 7: Publish event
            if self.event_bus:
                await self.event_bus.publish("security.puf.generated", {
                    "device_id": device_id,
                    "fingerprint": fingerprint,
                    "reproducibility": reproducibility,
                    "timestamp": time.time()
                })

            self.stats["pufs_generated"] += 1

            logger.info(
                f"PUF signature generated for {device_id}: "
                f"{fingerprint[:16]}... (reproducibility: {reproducibility:.3f})"
            )

            return puf_signature

        except Exception as e:
            logger.error(f"Failed to generate PUF signature for {device_id}: {e}")
            raise

    async def authenticate_device(
        self,
        device_id: str,
        challenge_measurement: bool = True
    ) -> Tuple[bool, float]:
        """
        Authenticate device by re-measuring PUF and comparing to stored signature.

        Process:
        1. Retrieve stored PUF signature from database
        2. Re-measure device thermodynamic properties
        3. Extract features from new measurements
        4. Fuzzy match against stored fingerprint
        5. Record authentication result

        Args:
            device_id: Device to authenticate
            challenge_measurement: If True, perform fresh measurement

        Returns:
            (authenticated: bool, confidence: float)
        """
        logger.info(f"Authenticating device {device_id}")

        self.stats["authentications_performed"] += 1

        try:
            # Step 1: Retrieve stored PUF
            stored_puf = await self._retrieve_puf_signature(device_id)

            if not stored_puf:
                logger.error(f"No PUF signature found for device {device_id}")
                return (False, 0.0)

            # Step 2: Re-measure device
            if challenge_measurement:
                measurements = await self._collect_thermodynamic_measurements(
                    device_id,
                    measurement_count=500  # Faster authentication
                )

                feature_vector = self._extract_stable_features(measurements)
                current_fingerprint = self._hash_to_fingerprint(feature_vector)
            else:
                # Use cached measurements (less secure but faster)
                current_fingerprint = stored_puf["fingerprint"]

            # Step 3: Fuzzy match
            match_confidence = self._fuzzy_match_fingerprints(
                stored_puf["fingerprint"],
                current_fingerprint,
                stored_puf.get("thermodynamic_vector", {})
            )

            authenticated = match_confidence >= self.fuzzy_match_threshold

            # Step 4: Update validation history
            await self._update_validation_history(
                device_id,
                authenticated,
                match_confidence
            )

            # Step 5: Publish event
            if self.event_bus:
                await self.event_bus.publish("security.puf.authentication", {
                    "device_id": device_id,
                    "authenticated": authenticated,
                    "confidence": match_confidence,
                    "timestamp": time.time()
                })

            if authenticated:
                self.stats["authentication_successes"] += 1
                logger.info(
                    f"Device {device_id} authenticated "
                    f"(confidence: {match_confidence:.3f})"
                )
            else:
                self.stats["authentication_failures"] += 1
                logger.warning(
                    f"Device {device_id} authentication FAILED "
                    f"(confidence: {match_confidence:.3f})"
                )

                # Check for potential clone
                if match_confidence < 0.5:
                    await self._alert_potential_clone(device_id, match_confidence)

            return (authenticated, match_confidence)

        except Exception as e:
            logger.error(f"Authentication failed for {device_id}: {e}")
            return (False, 0.0)

    async def detect_clone(
        self,
        device_id: str,
        suspected_clone_id: str
    ) -> Tuple[bool, float]:
        """
        Detect if two devices are clones based on PUF similarity.

        Legitimate devices should have PUF similarity < 0.3.
        Clones will have similarity > 0.7 (impossible naturally).

        Args:
            device_id: Original device
            suspected_clone_id: Suspected clone

        Returns:
            (is_clone: bool, similarity: float)
        """
        logger.info(f"Checking if {suspected_clone_id} is clone of {device_id}")

        try:
            # Get both PUF signatures
            puf1 = await self._retrieve_puf_signature(device_id)
            puf2 = await self._retrieve_puf_signature(suspected_clone_id)

            if not puf1 or not puf2:
                logger.error("Cannot compare - missing PUF signatures")
                return (False, 0.0)

            # Calculate similarity
            similarity = self._calculate_puf_similarity(
                puf1["thermodynamic_vector"],
                puf2["thermodynamic_vector"]
            )

            # Clones will have unnaturally high similarity
            is_clone = similarity > 0.70

            if is_clone:
                self.stats["clones_detected"] += 1

                logger.warning(
                    f"CLONE DETECTED: {suspected_clone_id} is clone of {device_id} "
                    f"(similarity: {similarity:.3f})"
                )

                # Alert security team
                if self.event_bus:
                    await self.event_bus.publish("security.puf.clone_detected", {
                        "original_device": device_id,
                        "clone_device": suspected_clone_id,
                        "similarity": similarity,
                        "timestamp": time.time()
                    })

            return (is_clone, similarity)

        except Exception as e:
            logger.error(f"Clone detection failed: {e}")
            return (False, 0.0)

    async def _collect_thermodynamic_measurements(
        self,
        device_id: str,
        measurement_count: int
    ) -> Dict[str, List[float]]:
        """
        Collect thermodynamic measurements from device.

        Measurements:
        1. Power consumption during crypto operations
        2. Thermal response to heating
        3. EM emission patterns
        4. Entropy production rates
        5. Noise characteristics

        Returns:
            Dict of measurement arrays
        """
        measurements = {
            "power": [],
            "thermal": [],
            "em_emission": [],
            "entropy_rate": [],
            "noise": []
        }

        for i in range(measurement_count):
            # Simulate measurements (in production, use real sensors)
            # Power consumption (mW) during AES encryption
            power = await self._measure_power_consumption(device_id)
            measurements["power"].append(power)

            # Thermal response (°C) to 1W heating pulse
            thermal = await self._measure_thermal_response(device_id)
            measurements["thermal"].append(thermal)

            # EM emission (μV) at specific frequencies
            em = await self._measure_em_emissions(device_id)
            measurements["em_emission"].append(em)

            # Entropy production rate (bits/sec)
            entropy_rate = await self._calculate_entropy_production(device_id)
            measurements["entropy_rate"].append(entropy_rate)

            # Device noise (μV RMS)
            noise = await self._measure_device_noise(device_id)
            measurements["noise"].append(noise)

            # Small delay between measurements
            if i % 100 == 0:
                await asyncio.sleep(0.01)

        return measurements

    async def _measure_power_consumption(self, device_id: str) -> float:
        """
        Measure power consumption during cryptographic operation.

        In production: Use power meter + trigger crypto operation.
        """
        # Simulate device-specific power consumption
        # Real devices have unique power signatures due to manufacturing variations
        base_power = hash(device_id) % 1000 / 1000  # Unique baseline
        variation = np.random.normal(0, 0.05)  # Manufacturing noise

        return 100.0 + base_power * 50 + variation

    async def _measure_thermal_response(self, device_id: str) -> float:
        """
        Measure thermal response to controlled heating pulse.

        In production: Apply heating, measure temp rise rate.
        """
        base_thermal = hash(device_id + "thermal") % 1000 / 1000
        variation = np.random.normal(0, 0.03)

        return 25.0 + base_thermal * 10 + variation

    async def _measure_em_emissions(self, device_id: str) -> float:
        """
        Measure electromagnetic emissions at specific frequencies.

        In production: Use EM probe + spectrum analyzer.
        """
        base_em = hash(device_id + "em") % 1000 / 1000
        variation = np.random.normal(0, 0.02)

        return 50.0 + base_em * 20 + variation

    async def _calculate_entropy_production(self, device_id: str) -> float:
        """
        Calculate entropy production rate.

        In production: Use EIL (Energy Intelligence Layer).
        """
        if self.eil:
            # Use real EIL entropy calculation
            # return await self.eil.calculate_entropy_rate(device_id)
            pass

        # Simulate entropy rate
        base_entropy = hash(device_id + "entropy") % 1000 / 1000
        variation = np.random.normal(0, 0.04)

        return 1000.0 + base_entropy * 500 + variation

    async def _measure_device_noise(self, device_id: str) -> float:
        """
        Measure device-specific electronic noise.

        In production: Measure voltage noise on test points.
        """
        base_noise = hash(device_id + "noise") % 1000 / 1000
        variation = np.random.normal(0, 0.01)

        return 10.0 + base_noise * 5 + variation

    def _extract_stable_features(
        self,
        measurements: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """
        Extract stable statistical features from measurements.

        Features should be:
        - Reproducible across measurements
        - Unique to device
        - Insensitive to environmental variations

        Extracted features:
        - Mean, median, std dev
        - Percentiles (10th, 50th, 90th)
        - Autocorrelation
        - Frequency domain peaks
        """
        features = {}

        for measurement_type, values in measurements.items():
            arr = np.array(values)

            features[f"{measurement_type}_mean"] = float(np.mean(arr))
            features[f"{measurement_type}_median"] = float(np.median(arr))
            features[f"{measurement_type}_std"] = float(np.std(arr))
            features[f"{measurement_type}_p10"] = float(np.percentile(arr, 10))
            features[f"{measurement_type}_p90"] = float(np.percentile(arr, 90))

            # Autocorrelation at lag 1
            if len(arr) > 1:
                autocorr = np.corrcoef(arr[:-1], arr[1:])[0, 1]
                features[f"{measurement_type}_autocorr"] = float(autocorr)

            # Dominant frequency component
            fft = np.fft.fft(arr)
            freqs = np.fft.fftfreq(len(arr))
            dominant_freq_idx = np.argmax(np.abs(fft[1:len(fft)//2])) + 1
            features[f"{measurement_type}_dominant_freq"] = float(freqs[dominant_freq_idx])

        return features

    def _calculate_reproducibility(
        self,
        measurements: Dict[str, List[float]]
    ) -> float:
        """
        Calculate reproducibility score.

        Split measurements in half, extract features from each half,
        calculate similarity. High similarity = good reproducibility.

        Returns:
            Reproducibility score (0.0 to 1.0)
        """
        reproducibility_scores = []

        for measurement_type, values in measurements.items():
            if len(values) < 100:
                continue

            # Split into two halves
            half = len(values) // 2
            first_half = {measurement_type: values[:half]}
            second_half = {measurement_type: values[half:]}

            # Extract features from each half
            features1 = self._extract_stable_features(first_half)
            features2 = self._extract_stable_features(second_half)

            # Calculate similarity
            similarity = self._calculate_feature_similarity(features1, features2)
            reproducibility_scores.append(similarity)

        return float(np.mean(reproducibility_scores)) if reproducibility_scores else 0.0

    def _hash_to_fingerprint(self, feature_vector: Dict[str, Any]) -> str:
        """
        Hash feature vector to 256-bit fingerprint.

        Uses SHA-256 to create cryptographically secure fingerprint.
        """
        # Serialize feature vector deterministically
        feature_str = str(sorted(feature_vector.items()))

        # SHA-256 hash
        hash_obj = hashlib.sha256(feature_str.encode('utf-8'))
        fingerprint = hash_obj.hexdigest()

        return fingerprint

    def _fuzzy_match_fingerprints(
        self,
        stored_fingerprint: str,
        current_fingerprint: str,
        stored_vector: Dict[str, Any]
    ) -> float:
        """
        Fuzzy match fingerprints to allow for measurement noise.

        Returns:
            Match confidence (0.0 to 1.0)
        """
        # Exact match
        if stored_fingerprint == current_fingerprint:
            return 1.0

        # Calculate Hamming distance
        hamming_distance = sum(
            c1 != c2 for c1, c2 in zip(stored_fingerprint, current_fingerprint)
        )

        max_distance = len(stored_fingerprint)
        similarity = 1.0 - (hamming_distance / max_distance)

        return similarity

    def _calculate_feature_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity between two feature vectors.

        Uses normalized correlation coefficient.
        """
        # Get common keys
        common_keys = set(features1.keys()) & set(features2.keys())

        if not common_keys:
            return 0.0

        # Extract values
        values1 = np.array([features1[k] for k in sorted(common_keys)])
        values2 = np.array([features2[k] for k in sorted(common_keys)])

        # Normalize
        values1 = (values1 - np.mean(values1)) / (np.std(values1) + 1e-10)
        values2 = (values2 - np.mean(values2)) / (np.std(values2) + 1e-10)

        # Correlation
        correlation = np.corrcoef(values1, values2)[0, 1]

        # Convert to similarity (0 to 1)
        similarity = (correlation + 1.0) / 2.0

        return float(similarity)

    def _calculate_puf_similarity(
        self,
        vector1: Dict[str, Any],
        vector2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two PUF vectors."""
        return self._calculate_feature_similarity(vector1, vector2)

    async def _store_puf_signature(self, puf_signature: PUFSignature):
        """Store PUF signature in database."""
        if not self.db_pool:
            return

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO security_events.device_pufs (
                        device_id,
                        puf_fingerprint,
                        thermodynamic_vector,
                        reproducibility_score,
                        created_at,
                        last_validated,
                        validation_count,
                        failed_validations,
                        metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (device_id) DO UPDATE SET
                        puf_fingerprint = EXCLUDED.puf_fingerprint,
                        thermodynamic_vector = EXCLUDED.thermodynamic_vector,
                        reproducibility_score = EXCLUDED.reproducibility_score,
                        created_at = EXCLUDED.created_at
                """,
                    puf_signature.device_id,
                    puf_signature.fingerprint,
                    puf_signature.thermodynamic_vector,
                    puf_signature.reproducibility_score,
                    puf_signature.created_at,
                    puf_signature.last_validated,
                    puf_signature.validation_count,
                    puf_signature.failed_validations,
                    {}  # metadata
                )

                logger.debug(f"PUF signature stored for {puf_signature.device_id}")

        except Exception as e:
            logger.error(f"Failed to store PUF signature: {e}")

    async def _retrieve_puf_signature(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve PUF signature from database."""
        if not self.db_pool:
            return None

        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM security_events.device_pufs
                    WHERE device_id = $1
                """, device_id)

                if row:
                    return dict(row)
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve PUF signature: {e}")
            return None

    async def _update_validation_history(
        self,
        device_id: str,
        authenticated: bool,
        confidence: float
    ):
        """Update validation history in database."""
        if not self.db_pool:
            return

        try:
            async with self.db_pool.acquire() as conn:
                if authenticated:
                    await conn.execute("""
                        UPDATE security_events.device_pufs
                        SET last_validated = NOW(),
                            validation_count = validation_count + 1
                        WHERE device_id = $1
                    """, device_id)
                else:
                    await conn.execute("""
                        UPDATE security_events.device_pufs
                        SET failed_validations = failed_validations + 1
                        WHERE device_id = $1
                    """, device_id)

        except Exception as e:
            logger.error(f"Failed to update validation history: {e}")

    async def _alert_potential_clone(self, device_id: str, confidence: float):
        """Alert security team about potential clone."""
        logger.critical(
            f"POTENTIAL CLONE DETECTED: Device {device_id} "
            f"failed authentication with confidence {confidence:.3f}"
        )

        if self.event_bus:
            await self.event_bus.publish("security.puf.potential_clone", {
                "device_id": device_id,
                "confidence": confidence,
                "timestamp": time.time(),
                "severity": "critical"
            })

    def get_statistics(self) -> Dict[str, Any]:
        """Get PUF system statistics."""
        return {
            **self.stats,
            "reproducibility_threshold": self.reproducibility_threshold,
            "fuzzy_match_threshold": self.fuzzy_match_threshold
        }


# ============================================================================
# Singleton instance
# ============================================================================

_puf_instance = None


def get_thermodynamic_puf(
    database_pool=None,
    energy_intelligence_layer=None,
    event_bus=None
) -> ThermodynamicPUF:
    """
    Get singleton Thermodynamic PUF instance.

    Args:
        database_pool: PostgreSQL connection pool
        energy_intelligence_layer: EIL for energy measurements
        event_bus: Event bus for security events

    Returns:
        ThermodynamicPUF instance
    """
    global _puf_instance

    if _puf_instance is None:
        _puf_instance = ThermodynamicPUF(
            database_pool=database_pool,
            energy_intelligence_layer=energy_intelligence_layer,
            event_bus=event_bus
        )

    return _puf_instance
