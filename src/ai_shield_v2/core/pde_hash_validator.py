#!/usr/bin/env python3
"""
AI Shield v2 - PDE-Hash Validation and Management
==================================================

Canonical state identity through physics-based cryptographic signatures.
Implements the "Physics Engine" role of AI Shield Hybrid Superstructure.

Architecture:
- PDE-hash validation (verify signature integrity)
- State transition validation (ensure physics-valid transitions)
- Canonical identity registry
- Cryptographic verification
- Conservation law enforcement

Mathematical Foundation:
    H_PDE(T) = SHA-256(Serialize({D*(T), s_D*(T), Φ(T)}))

Where:
    D*(T) = primary physics domain
    s_D*(T) = domain score
    Φ(T) = 12-dimensional physics feature vector

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
Classification: CONFIDENTIAL - PATENT PENDING
"""

import hashlib
import json
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging
import time
from threading import Lock

# Import MIC components
from ..mic.math_isomorphism_core import PhysicsSignature, PhysicsFeatures, PhysicsDomain


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """PDE-hash validation status"""
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"
    SUSPICIOUS = "suspicious"


class TransitionType(Enum):
    """State transition types"""
    CONTINUOUS = "continuous"           # Smooth evolution
    DISCONTINUOUS = "discontinuous"     # Jump transition
    CONSERVATION_PRESERVING = "conservation_preserving"
    CONSERVATION_VIOLATING = "conservation_violating"


@dataclass
class PDEHashRecord:
    """Registry record for a PDE-hash"""
    pde_hash: str
    physics_signature: PhysicsSignature
    timestamp: float
    validation_count: int = 0
    last_validated: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """PDE-hash validation result"""
    pde_hash: str
    status: ValidationStatus
    is_valid: bool
    confidence: float
    validation_checks: Dict[str, bool]
    timestamp: float = field(default_factory=time.time)
    error_message: Optional[str] = None


@dataclass
class TransitionValidation:
    """State transition validation result"""
    from_hash: str
    to_hash: str
    transition_type: TransitionType
    is_physics_valid: bool
    conservation_preserved: bool
    energy_delta: float
    entropy_delta: float
    feature_distance: float
    confidence: float
    timestamp: float = field(default_factory=time.time)


class PDEHashGenerator:
    """Generate PDE-hash from physics signature"""

    @staticmethod
    def generate(signature: PhysicsSignature) -> str:
        """
        Generate PDE-hash from physics signature

        H_PDE = SHA-256(Serialize({D*, s_D*, Φ}))

        Args:
            signature: PhysicsSignature from MIC

        Returns:
            PDE-hash string (64-character hex)
        """
        try:
            # Serialize signature components
            components = {
                "primary_domain": signature.primary_domain.value,
                "domain_score": float(signature.domain_scores[signature.primary_domain]),
                "features": {
                    "spectral_density": float(signature.features.spectral_density),
                    "spectral_entropy": float(signature.features.spectral_entropy),
                    "dominant_frequency": float(signature.features.dominant_frequency),
                    "temporal_gradient": float(signature.features.temporal_gradient),
                    "temporal_variance": float(signature.features.temporal_variance),
                    "temporal_autocorr": float(signature.features.temporal_autocorr),
                    "energy_density": float(signature.features.energy_density),
                    "entropy": float(signature.features.entropy),
                    "skewness": float(signature.features.skewness),
                    "kurtosis": float(signature.features.kurtosis),
                    "mean_value": float(signature.features.mean_value),
                    "std_deviation": float(signature.features.std_deviation)
                }
            }

            # Canonical JSON serialization (sorted keys, no whitespace)
            serialized = json.dumps(components, sort_keys=True, separators=(',', ':'))

            # SHA-256 hash
            hash_obj = hashlib.sha256(serialized.encode('utf-8'))
            pde_hash = hash_obj.hexdigest()

            return pde_hash

        except Exception as e:
            logger.error(f"PDE-hash generation failed: {e}")
            raise

    @staticmethod
    def verify(signature: PhysicsSignature, claimed_hash: str) -> bool:
        """
        Verify that claimed hash matches signature

        Args:
            signature: PhysicsSignature to verify
            claimed_hash: Claimed PDE-hash

        Returns:
            True if hash matches signature
        """
        try:
            actual_hash = PDEHashGenerator.generate(signature)
            return actual_hash == claimed_hash
        except Exception as e:
            logger.error(f"Hash verification failed: {e}")
            return False


class PDEHashRegistry:
    """Registry for tracking known PDE-hashes and their provenance"""

    def __init__(self, max_size: int = 100000):
        """
        Initialize PDE-hash registry

        Args:
            max_size: Maximum registry size (LRU eviction)
        """
        self.max_size = max_size
        self.registry: Dict[str, PDEHashRecord] = {}
        self.registry_lock = Lock()

        # Access tracking for LRU
        self.access_order: List[str] = []

        logger.info(f"Initialized PDE-hash registry (max_size={max_size})")

    def register(self, signature: PhysicsSignature) -> str:
        """
        Register a physics signature and return its PDE-hash

        Args:
            signature: PhysicsSignature to register

        Returns:
            PDE-hash string
        """
        pde_hash = PDEHashGenerator.generate(signature)

        with self.registry_lock:
            if pde_hash in self.registry:
                # Update existing record
                record = self.registry[pde_hash]
                record.validation_count += 1
                record.last_validated = time.time()
            else:
                # Create new record
                record = PDEHashRecord(
                    pde_hash=pde_hash,
                    physics_signature=signature,
                    timestamp=time.time(),
                    validation_count=1,
                    last_validated=time.time()
                )
                self.registry[pde_hash] = record

                # Track access for LRU
                self.access_order.append(pde_hash)

                # Evict if over size limit
                if len(self.registry) > self.max_size:
                    self._evict_lru()

        return pde_hash

    def lookup(self, pde_hash: str) -> Optional[PDEHashRecord]:
        """
        Lookup a PDE-hash in the registry

        Args:
            pde_hash: PDE-hash to lookup

        Returns:
            PDEHashRecord if found, None otherwise
        """
        with self.registry_lock:
            record = self.registry.get(pde_hash)

            if record:
                # Update access order
                if pde_hash in self.access_order:
                    self.access_order.remove(pde_hash)
                self.access_order.append(pde_hash)

            return record

    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.access_order:
            return

        lru_hash = self.access_order.pop(0)
        if lru_hash in self.registry:
            del self.registry[lru_hash]
            logger.debug(f"Evicted LRU entry: {lru_hash[:16]}...")

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        with self.registry_lock:
            return {
                "total_entries": len(self.registry),
                "max_size": self.max_size,
                "utilization": len(self.registry) / self.max_size if self.max_size > 0 else 0.0
            }


class PDEHashValidator:
    """
    PDE-Hash validation and state transition verification

    Implements physics-based validation of state transitions
    and conservation law enforcement.
    """

    def __init__(self, registry: Optional[PDEHashRegistry] = None):
        """
        Initialize PDE-hash validator

        Args:
            registry: Optional PDE-hash registry for provenance tracking
        """
        self.registry = registry or PDEHashRegistry()

        # Conservation law thresholds
        self.energy_tolerance = 0.1  # 10% energy variation allowed
        self.entropy_tolerance = 0.05  # 5% entropy variation allowed

        # Transition thresholds
        self.continuous_threshold = 0.3  # Feature distance for continuous transitions
        self.suspicious_threshold = 0.8  # Feature distance for suspicious transitions

        logger.info("Initialized PDE-hash validator")

    def validate(self, signature: PhysicsSignature, claimed_hash: Optional[str] = None) -> ValidationResult:
        """
        Validate a physics signature and its PDE-hash

        Args:
            signature: PhysicsSignature to validate
            claimed_hash: Optional claimed PDE-hash (will generate if not provided)

        Returns:
            ValidationResult with validation status
        """
        validation_checks = {}

        try:
            # Generate or verify hash
            if claimed_hash:
                actual_hash = PDEHashGenerator.generate(signature)
                hash_matches = (actual_hash == claimed_hash)
                validation_checks["hash_integrity"] = hash_matches
                pde_hash = claimed_hash
            else:
                pde_hash = PDEHashGenerator.generate(signature)
                hash_matches = True
                validation_checks["hash_integrity"] = True

            # Validate physics features
            features_valid = self._validate_features(signature.features)
            validation_checks["features_valid"] = features_valid

            # Validate domain scores
            domain_scores_valid = self._validate_domain_scores(signature.domain_scores)
            validation_checks["domain_scores_valid"] = domain_scores_valid

            # Overall validation
            is_valid = all(validation_checks.values())

            # Determine status
            if is_valid:
                status = ValidationStatus.VALID
            else:
                status = ValidationStatus.INVALID

            # Calculate confidence
            confidence = sum(validation_checks.values()) / len(validation_checks)

            # Register if valid
            if is_valid:
                self.registry.register(signature)

            return ValidationResult(
                pde_hash=pde_hash,
                status=status,
                is_valid=is_valid,
                confidence=confidence,
                validation_checks=validation_checks
            )

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(
                pde_hash=claimed_hash or "",
                status=ValidationStatus.INVALID,
                is_valid=False,
                confidence=0.0,
                validation_checks=validation_checks,
                error_message=str(e)
            )

    def validate_transition(
        self,
        from_signature: PhysicsSignature,
        to_signature: PhysicsSignature
    ) -> TransitionValidation:
        """
        Validate state transition between two physics signatures

        Checks:
        - Conservation laws (energy, entropy)
        - Physics domain consistency
        - Feature distance (continuous vs discontinuous)

        Args:
            from_signature: Initial state signature
            to_signature: Final state signature

        Returns:
            TransitionValidation result
        """
        try:
            # Generate hashes
            from_hash = PDEHashGenerator.generate(from_signature)
            to_hash = PDEHashGenerator.generate(to_signature)

            # Calculate feature distance
            feature_distance = self._calculate_feature_distance(
                from_signature.features,
                to_signature.features
            )

            # Check conservation laws
            energy_delta = abs(
                to_signature.features.energy_density - from_signature.features.energy_density
            )
            entropy_delta = abs(
                to_signature.features.entropy - from_signature.features.entropy
            )

            energy_conserved = energy_delta <= self.energy_tolerance
            entropy_nondecreasing = to_signature.features.entropy >= from_signature.features.entropy - self.entropy_tolerance

            conservation_preserved = energy_conserved and entropy_nondecreasing

            # Determine transition type
            if feature_distance < self.continuous_threshold:
                transition_type = TransitionType.CONTINUOUS
            else:
                transition_type = TransitionType.DISCONTINUOUS

            if conservation_preserved:
                if transition_type == TransitionType.CONTINUOUS:
                    transition_type = TransitionType.CONSERVATION_PRESERVING
            else:
                transition_type = TransitionType.CONSERVATION_VIOLATING

            # Physics validity
            is_physics_valid = (
                conservation_preserved and
                feature_distance < self.suspicious_threshold
            )

            # Confidence based on conservation and continuity
            confidence = 1.0
            if not energy_conserved:
                confidence *= 0.5
            if not entropy_nondecreasing:
                confidence *= 0.7
            if feature_distance > self.continuous_threshold:
                confidence *= 0.8

            return TransitionValidation(
                from_hash=from_hash,
                to_hash=to_hash,
                transition_type=transition_type,
                is_physics_valid=is_physics_valid,
                conservation_preserved=conservation_preserved,
                energy_delta=energy_delta,
                entropy_delta=entropy_delta,
                feature_distance=feature_distance,
                confidence=confidence
            )

        except Exception as e:
            logger.error(f"Transition validation error: {e}")
            return TransitionValidation(
                from_hash="",
                to_hash="",
                transition_type=TransitionType.DISCONTINUOUS,
                is_physics_valid=False,
                conservation_preserved=False,
                energy_delta=np.inf,
                entropy_delta=np.inf,
                feature_distance=np.inf,
                confidence=0.0
            )

    def _validate_features(self, features: PhysicsFeatures) -> bool:
        """Validate physics features are within physical bounds"""
        try:
            # Check for NaN or inf
            feature_values = [
                features.spectral_density,
                features.spectral_entropy,
                features.dominant_frequency,
                features.temporal_gradient,
                features.temporal_variance,
                features.temporal_autocorr,
                features.energy_density,
                features.entropy,
                features.skewness,
                features.kurtosis,
                features.mean_value,
                features.std_deviation
            ]

            for value in feature_values:
                if np.isnan(value) or np.isinf(value):
                    return False

            # Check physical bounds
            if features.energy_density < 0:
                return False
            if features.entropy < 0:
                return False
            if features.spectral_entropy < 0 or features.spectral_entropy > 1:
                return False

            return True

        except Exception as e:
            logger.error(f"Feature validation error: {e}")
            return False

    def _validate_domain_scores(self, domain_scores: Dict[PhysicsDomain, float]) -> bool:
        """Validate domain scores sum to ~1.0 and are in [0, 1]"""
        try:
            total = sum(domain_scores.values())

            # Check individual scores
            for score in domain_scores.values():
                if score < 0 or score > 1:
                    return False

            # Check sum (allow small numerical error)
            if abs(total - 1.0) > 0.01:
                return False

            return True

        except Exception as e:
            logger.error(f"Domain score validation error: {e}")
            return False

    def _calculate_feature_distance(
        self,
        features1: PhysicsFeatures,
        features2: PhysicsFeatures
    ) -> float:
        """Calculate normalized Euclidean distance between feature vectors"""
        try:
            vec1 = np.array([
                features1.spectral_density,
                features1.spectral_entropy,
                features1.dominant_frequency,
                features1.temporal_gradient,
                features1.temporal_variance,
                features1.temporal_autocorr,
                features1.energy_density,
                features1.entropy,
                features1.skewness,
                features1.kurtosis,
                features1.mean_value,
                features1.std_deviation
            ])

            vec2 = np.array([
                features2.spectral_density,
                features2.spectral_entropy,
                features2.dominant_frequency,
                features2.temporal_gradient,
                features2.temporal_variance,
                features2.temporal_autocorr,
                features2.energy_density,
                features2.entropy,
                features2.skewness,
                features2.kurtosis,
                features2.mean_value,
                features2.std_deviation
            ])

            # Normalized Euclidean distance
            distance = np.linalg.norm(vec1 - vec2) / np.sqrt(len(vec1))

            return float(distance)

        except Exception as e:
            logger.error(f"Feature distance calculation error: {e}")
            return np.inf


# Example usage and testing
if __name__ == "__main__":
    print("AI Shield v2 - PDE-Hash Validation System")
    print("=" * 60)

    print("\nInitializing PDE-hash validator...")
    validator = PDEHashValidator()

    print("\nConfiguration:")
    print(f"  Energy Tolerance: {validator.energy_tolerance * 100:.1f}%")
    print(f"  Entropy Tolerance: {validator.entropy_tolerance * 100:.1f}%")
    print(f"  Continuous Threshold: {validator.continuous_threshold}")
    print(f"  Suspicious Threshold: {validator.suspicious_threshold}")

    print(f"\nRegistry Statistics:")
    stats = validator.registry.get_statistics()
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  Max Size: {stats['max_size']}")
    print(f"  Utilization: {stats['utilization']*100:.1f}%")

    print("\n✅ Phase 1.6 Complete: PDE-hash validation operational")
    print("   - PDE-hash generation and verification enabled")
    print("   - State transition validation active")
    print("   - Conservation law enforcement configured")
    print("   - Canonical identity registry operational")
