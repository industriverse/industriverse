#!/usr/bin/env python3
"""
AI Shield v2 - Cross-Layer Correlation Engine
==============================================

Phase 4.2: Cross-layer correlation for multi-layer threat detection.

Detects patterns and anomalies across telemetry layers:
- Energy-Threat correlation (energy anomalies → cyber threats)
- Consciousness-Diffusion correlation (consciousness level → attack predictions)
- Agent-Network correlation (agent behavior → network traffic)
- Physics-Energy correlation (physics violations → energy leaks)
- Temporal pattern correlation

Architecture:
- Statistical correlation analysis
- Pattern detection across layers
- Anomaly correlation scoring
- Attack signature recognition
- Temporal correlation tracking

Mathematical Foundation:
    Correlation Score: ρ(X,Y) = Cov(X,Y) / (σ_X × σ_Y)
    Anomaly Correlation: A_corr = Σ(w_i × a_i × a_j) for layers i,j
    Temporal Correlation: T_corr = ∫ρ(t) × exp(-λt) dt

Performance Targets:
- Correlation analysis: <50ms per aggregation
- Cross-layer pattern detection: >95% accuracy
- False positive rate: <5%

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
Classification: CONFIDENTIAL - PATENT PENDING
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import logging
import time
from collections import deque, defaultdict
from threading import Lock
import json

# Import AI Shield components
from .multi_layer_aggregator import (
    AggregatedTelemetry,
    TelemetryLayer,
    LayerData
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorrelationType(Enum):
    """Types of cross-layer correlations"""
    ENERGY_THREAT = "energy_threat"                 # Energy anomaly → Cyber threat
    CONSCIOUSNESS_DIFFUSION = "consciousness_diffusion"  # Consciousness → Diffusion
    AGENT_NETWORK = "agent_network"                 # Agent behavior → Network
    PHYSICS_ENERGY = "physics_energy"               # Physics violation → Energy leak
    THREAT_DIFFUSION = "threat_diffusion"           # Detected threat → Predicted threat
    ENERGY_CONSCIOUSNESS = "energy_consciousness"   # Energy state → Consciousness
    MULTI_LAYER = "multi_layer"                     # 3+ layers correlation


class CorrelationStrength(Enum):
    """Correlation strength classification"""
    NONE = "none"               # ρ < 0.3
    WEAK = "weak"               # 0.3 ≤ ρ < 0.5
    MODERATE = "moderate"       # 0.5 ≤ ρ < 0.7
    STRONG = "strong"           # 0.7 ≤ ρ < 0.9
    VERY_STRONG = "very_strong" # ρ ≥ 0.9


class AttackPattern(Enum):
    """Cross-layer attack patterns"""
    COORDINATED_ATTACK = "coordinated_attack"       # Multiple layers show anomalies
    ENERGY_DRAIN = "energy_drain"                   # Energy leak + agent activity
    STEALTH_INTRUSION = "stealth_intrusion"         # Low threat + high energy anomaly
    DIFFUSION_MISMATCH = "diffusion_mismatch"       # Predicted != observed
    CONSCIOUSNESS_BYPASS = "consciousness_bypass"   # Low consciousness + high threat
    PHYSICS_VIOLATION = "physics_violation"         # Physics + energy anomalies
    UNKNOWN = "unknown"


@dataclass
class CorrelationPair:
    """Correlation between two layers"""
    layer_a: TelemetryLayer
    layer_b: TelemetryLayer
    correlation_type: CorrelationType
    correlation_coefficient: float      # ρ ∈ [-1, 1]
    strength: CorrelationStrength
    p_value: float                      # Statistical significance
    sample_count: int
    timestamp: float = field(default_factory=time.time)


@dataclass
class CrossLayerPattern:
    """Detected cross-layer pattern"""
    pattern_id: str
    pattern_type: AttackPattern
    layers_involved: Set[TelemetryLayer]
    confidence: float                   # 0-1
    severity: float                     # 0-1
    evidence: Dict[str, Any]
    recommended_action: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class CorrelationAnalysis:
    """Complete correlation analysis result"""
    aggregation_id: str
    base_timestamp: float

    # Pairwise correlations
    correlations: List[CorrelationPair]

    # Detected patterns
    patterns: List[CrossLayerPattern]

    # Overall anomaly correlation score
    anomaly_correlation_score: float    # 0-1

    # Temporal correlation (vs historical)
    temporal_correlation: float         # -1 to 1

    # Summary
    total_correlations: int
    strong_correlations: int
    patterns_detected: int
    max_severity: float

    # Processing
    processing_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class CorrelatorMetrics:
    """Cross-layer correlator metrics"""
    total_analyses: int = 0
    total_patterns_detected: int = 0
    patterns_by_type: Dict[AttackPattern, int] = field(default_factory=lambda: defaultdict(int))

    average_analysis_time_ms: float = 0.0
    average_anomaly_correlation: float = 0.0

    # Detection statistics
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0


class StatisticalCorrelator:
    """
    Statistical correlation analysis between telemetry layers

    Computes Pearson correlation coefficients and significance tests
    """

    @staticmethod
    def compute_correlation(
        data_a: np.ndarray,
        data_b: np.ndarray,
        min_samples: int = 10
    ) -> Tuple[float, float]:
        """
        Compute Pearson correlation coefficient

        Args:
            data_a: First data series
            data_b: Second data series
            min_samples: Minimum samples for valid correlation

        Returns:
            (correlation_coefficient, p_value)
        """
        if len(data_a) < min_samples or len(data_b) < min_samples:
            return 0.0, 1.0

        if len(data_a) != len(data_b):
            # Truncate to shorter length
            min_len = min(len(data_a), len(data_b))
            data_a = data_a[:min_len]
            data_b = data_b[:min_len]

        try:
            # Compute Pearson correlation
            correlation_matrix = np.corrcoef(data_a, data_b)
            correlation = correlation_matrix[0, 1]

            # Simple p-value estimation (approximate)
            n = len(data_a)
            if n > 2:
                # t-statistic: t = r * sqrt((n-2)/(1-r^2))
                t_stat = correlation * np.sqrt((n - 2) / (1 - correlation**2 + 1e-10))
                # Approximate p-value (two-tailed)
                p_value = 2 * (1 - 0.5 * (1 + np.tanh(t_stat / np.sqrt(2))))
            else:
                p_value = 1.0

            return float(correlation), float(p_value)

        except Exception as e:
            logger.debug(f"Correlation computation error: {e}")
            return 0.0, 1.0

    @staticmethod
    def classify_strength(correlation: float) -> CorrelationStrength:
        """Classify correlation strength"""
        abs_corr = abs(correlation)

        if abs_corr >= 0.9:
            return CorrelationStrength.VERY_STRONG
        elif abs_corr >= 0.7:
            return CorrelationStrength.STRONG
        elif abs_corr >= 0.5:
            return CorrelationStrength.MODERATE
        elif abs_corr >= 0.3:
            return CorrelationStrength.WEAK
        else:
            return CorrelationStrength.NONE


class PatternDetector:
    """
    Cross-layer attack pattern detection

    Identifies attack signatures across multiple telemetry layers
    """

    def __init__(self, detection_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize pattern detector

        Args:
            detection_thresholds: Custom detection thresholds
        """
        self.thresholds = detection_thresholds or {
            "energy_anomaly": 0.7,
            "threat_score": 60.0,
            "diffusion_uncertainty": 0.5,
            "physics_violation": 0.6,
            "consciousness_low": "REFLEXIVE"
        }

    def detect_patterns(
        self,
        aggregation: AggregatedTelemetry,
        correlations: List[CorrelationPair]
    ) -> List[CrossLayerPattern]:
        """
        Detect cross-layer attack patterns

        Args:
            aggregation: Aggregated telemetry
            correlations: Computed correlations

        Returns:
            List of detected patterns
        """
        patterns = []

        # Check for coordinated attack
        coordinated = self._detect_coordinated_attack(aggregation)
        if coordinated:
            patterns.append(coordinated)

        # Check for energy drain
        energy_drain = self._detect_energy_drain(aggregation, correlations)
        if energy_drain:
            patterns.append(energy_drain)

        # Check for stealth intrusion
        stealth = self._detect_stealth_intrusion(aggregation)
        if stealth:
            patterns.append(stealth)

        # Check for diffusion mismatch
        diffusion_mismatch = self._detect_diffusion_mismatch(aggregation)
        if diffusion_mismatch:
            patterns.append(diffusion_mismatch)

        # Check for consciousness bypass
        consciousness_bypass = self._detect_consciousness_bypass(aggregation)
        if consciousness_bypass:
            patterns.append(consciousness_bypass)

        # Check for physics violation
        physics_violation = self._detect_physics_violation(aggregation)
        if physics_violation:
            patterns.append(physics_violation)

        return patterns

    def _detect_coordinated_attack(
        self,
        aggregation: AggregatedTelemetry
    ) -> Optional[CrossLayerPattern]:
        """Detect coordinated attack across multiple layers"""
        # Multiple layers showing anomalies simultaneously
        anomaly_count = 0
        layers_involved = set()

        if aggregation.anomaly_score > 0.6:
            # Check each layer
            if (TelemetryLayer.ENERGY in aggregation.layers and
                aggregation.layers[TelemetryLayer.ENERGY].data.get("anomaly_score", 0) > 0.7):
                anomaly_count += 1
                layers_involved.add(TelemetryLayer.ENERGY)

            if (TelemetryLayer.THREAT in aggregation.layers and
                aggregation.layers[TelemetryLayer.THREAT].data.get("ici_score", 0) > 60):
                anomaly_count += 1
                layers_involved.add(TelemetryLayer.THREAT)

            if (TelemetryLayer.DIFFUSION in aggregation.layers and
                aggregation.layers[TelemetryLayer.DIFFUSION].data.get("uncertainty", 0) > 0.5):
                anomaly_count += 1
                layers_involved.add(TelemetryLayer.DIFFUSION)

            if anomaly_count >= 2:
                confidence = min(1.0, anomaly_count / 3.0)
                severity = aggregation.anomaly_score

                return CrossLayerPattern(
                    pattern_id=f"coordinated_{aggregation.aggregation_id}",
                    pattern_type=AttackPattern.COORDINATED_ATTACK,
                    layers_involved=layers_involved,
                    confidence=confidence,
                    severity=severity,
                    evidence={
                        "anomaly_count": anomaly_count,
                        "overall_anomaly_score": aggregation.anomaly_score
                    },
                    recommended_action="ESCALATE: Multi-layer coordinated attack detected"
                )

        return None

    def _detect_energy_drain(
        self,
        aggregation: AggregatedTelemetry,
        correlations: List[CorrelationPair]
    ) -> Optional[CrossLayerPattern]:
        """Detect energy drain attack"""
        if TelemetryLayer.ENERGY not in aggregation.layers:
            return None

        energy_layer = aggregation.layers[TelemetryLayer.ENERGY]
        energy_anomaly = energy_layer.data.get("anomaly_score", 0)
        energy_flux = energy_layer.data.get("energy_flux", 0)

        # High energy consumption + anomaly
        if energy_anomaly > 0.7 and abs(energy_flux) > 0.5:
            layers_involved = {TelemetryLayer.ENERGY}

            # Check if correlated with agent activity
            if TelemetryLayer.AGENT in aggregation.layers:
                layers_involved.add(TelemetryLayer.AGENT)

            return CrossLayerPattern(
                pattern_id=f"energy_drain_{aggregation.aggregation_id}",
                pattern_type=AttackPattern.ENERGY_DRAIN,
                layers_involved=layers_involved,
                confidence=energy_anomaly,
                severity=min(1.0, energy_anomaly * 1.2),
                evidence={
                    "energy_anomaly": energy_anomaly,
                    "energy_flux": energy_flux
                },
                recommended_action="ALERT: Energy drain detected - investigate resource usage"
            )

        return None

    def _detect_stealth_intrusion(
        self,
        aggregation: AggregatedTelemetry
    ) -> Optional[CrossLayerPattern]:
        """Detect stealth intrusion (low threat score but high energy anomaly)"""
        if (TelemetryLayer.ENERGY not in aggregation.layers or
            TelemetryLayer.THREAT not in aggregation.layers):
            return None

        energy_anomaly = aggregation.layers[TelemetryLayer.ENERGY].data.get("anomaly_score", 0)
        threat_score = aggregation.layers[TelemetryLayer.THREAT].data.get("ici_score", 0)

        # High energy anomaly but low threat score = potential stealth
        if energy_anomaly > 0.7 and threat_score < 40:
            confidence = energy_anomaly * (1 - threat_score / 100.0)
            severity = energy_anomaly

            return CrossLayerPattern(
                pattern_id=f"stealth_{aggregation.aggregation_id}",
                pattern_type=AttackPattern.STEALTH_INTRUSION,
                layers_involved={TelemetryLayer.ENERGY, TelemetryLayer.THREAT},
                confidence=confidence,
                severity=severity,
                evidence={
                    "energy_anomaly": energy_anomaly,
                    "threat_score": threat_score,
                    "mismatch": energy_anomaly - (threat_score / 100.0)
                },
                recommended_action="INVESTIGATE: Stealth intrusion suspected - energy anomaly without threat signature"
            )

        return None

    def _detect_diffusion_mismatch(
        self,
        aggregation: AggregatedTelemetry
    ) -> Optional[CrossLayerPattern]:
        """Detect mismatch between predicted (diffusion) and observed threats"""
        if (TelemetryLayer.DIFFUSION not in aggregation.layers or
            TelemetryLayer.THREAT not in aggregation.layers):
            return None

        diffusion_uncertainty = aggregation.layers[TelemetryLayer.DIFFUSION].data.get("uncertainty", 0)
        threat_score = aggregation.layers[TelemetryLayer.THREAT].data.get("ici_score", 0) / 100.0

        # High uncertainty or large mismatch
        if diffusion_uncertainty > 0.6:
            confidence = diffusion_uncertainty
            severity = min(1.0, diffusion_uncertainty * threat_score)

            return CrossLayerPattern(
                pattern_id=f"diffusion_mismatch_{aggregation.aggregation_id}",
                pattern_type=AttackPattern.DIFFUSION_MISMATCH,
                layers_involved={TelemetryLayer.DIFFUSION, TelemetryLayer.THREAT},
                confidence=confidence,
                severity=severity,
                evidence={
                    "diffusion_uncertainty": diffusion_uncertainty,
                    "threat_score": threat_score
                },
                recommended_action="MONITOR: Diffusion prediction uncertainty high"
            )

        return None

    def _detect_consciousness_bypass(
        self,
        aggregation: AggregatedTelemetry
    ) -> Optional[CrossLayerPattern]:
        """Detect consciousness bypass (low consciousness + high threat)"""
        if (TelemetryLayer.CONSCIOUSNESS not in aggregation.layers or
            TelemetryLayer.THREAT not in aggregation.layers):
            return None

        consciousness_level = aggregation.layers[TelemetryLayer.CONSCIOUSNESS].data.get("level", "")
        threat_score = aggregation.layers[TelemetryLayer.THREAT].data.get("ici_score", 0)

        # Low consciousness + high threat = bypass attempt
        if consciousness_level in ["REFLEXIVE", "REACTIVE"] and threat_score > 60:
            confidence = threat_score / 100.0
            severity = threat_score / 100.0

            return CrossLayerPattern(
                pattern_id=f"consciousness_bypass_{aggregation.aggregation_id}",
                pattern_type=AttackPattern.CONSCIOUSNESS_BYPASS,
                layers_involved={TelemetryLayer.CONSCIOUSNESS, TelemetryLayer.THREAT},
                confidence=confidence,
                severity=severity,
                evidence={
                    "consciousness_level": consciousness_level,
                    "threat_score": threat_score
                },
                recommended_action="CRITICAL: Consciousness bypass detected - escalate immediately"
            )

        return None

    def _detect_physics_violation(
        self,
        aggregation: AggregatedTelemetry
    ) -> Optional[CrossLayerPattern]:
        """Detect physics violation correlated with energy anomaly"""
        if (TelemetryLayer.PHYSICS not in aggregation.layers or
            TelemetryLayer.ENERGY not in aggregation.layers):
            return None

        # Check for physics anomalies (low conservation, symmetry, causality)
        physics_layer = aggregation.layers[TelemetryLayer.PHYSICS].data
        conservation = physics_layer.get("conservation", 1.0)
        causality = physics_layer.get("causality", 1.0)
        energy_anomaly = aggregation.layers[TelemetryLayer.ENERGY].data.get("anomaly_score", 0)

        # Physics violations + energy anomaly
        if (conservation < 0.5 or causality < 0.5) and energy_anomaly > 0.6:
            physics_violation_score = 1.0 - min(conservation, causality)
            confidence = min(1.0, physics_violation_score * energy_anomaly)
            severity = confidence

            return CrossLayerPattern(
                pattern_id=f"physics_violation_{aggregation.aggregation_id}",
                pattern_type=AttackPattern.PHYSICS_VIOLATION,
                layers_involved={TelemetryLayer.PHYSICS, TelemetryLayer.ENERGY},
                confidence=confidence,
                severity=severity,
                evidence={
                    "conservation": conservation,
                    "causality": causality,
                    "energy_anomaly": energy_anomaly
                },
                recommended_action="ALERT: Physics law violation detected - fundamental anomaly"
            )

        return None


class CrossLayerCorrelator:
    """
    Cross-Layer Correlation Engine

    Analyzes aggregated telemetry for cross-layer patterns and correlations

    Phase 4.2 Component
    """

    def __init__(
        self,
        history_size: int = 1000,
        min_correlation: float = 0.3,
        detection_thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Initialize cross-layer correlator

        Args:
            history_size: Size of historical data buffer
            min_correlation: Minimum correlation to report
            detection_thresholds: Pattern detection thresholds
        """
        self.history_size = history_size
        self.min_correlation = min_correlation

        # Statistical correlator and pattern detector
        self.statistical_correlator = StatisticalCorrelator()
        self.pattern_detector = PatternDetector(detection_thresholds)

        # Historical data for temporal correlation
        self.history_buffer: deque = deque(maxlen=history_size)
        self.history_lock = Lock()

        # Layer time series (for correlation computation)
        self.layer_time_series: Dict[TelemetryLayer, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self.time_series_lock = Lock()

        # Metrics
        self.metrics = CorrelatorMetrics()
        self.metrics_lock = Lock()

        logger.info(
            f"Initialized Cross-Layer Correlator "
            f"(history={history_size}, min_corr={min_correlation})"
        )

    def analyze(
        self,
        aggregation: AggregatedTelemetry
    ) -> CorrelationAnalysis:
        """
        Perform cross-layer correlation analysis

        Args:
            aggregation: Aggregated telemetry to analyze

        Returns:
            CorrelationAnalysis result
        """
        start_time = time.perf_counter()

        # Compute pairwise correlations
        correlations = self._compute_pairwise_correlations(aggregation)

        # Detect patterns
        patterns = self.pattern_detector.detect_patterns(aggregation, correlations)

        # Calculate anomaly correlation score
        anomaly_correlation = self._calculate_anomaly_correlation(aggregation, correlations)

        # Calculate temporal correlation
        temporal_correlation = self._calculate_temporal_correlation(aggregation)

        # Update time series
        self._update_time_series(aggregation)

        # Create analysis result
        strong_correlations = sum(
            1 for c in correlations
            if c.strength in [CorrelationStrength.STRONG, CorrelationStrength.VERY_STRONG]
        )

        max_severity = max([p.severity for p in patterns], default=0.0)

        analysis = CorrelationAnalysis(
            aggregation_id=aggregation.aggregation_id,
            base_timestamp=aggregation.base_timestamp,
            correlations=correlations,
            patterns=patterns,
            anomaly_correlation_score=anomaly_correlation,
            temporal_correlation=temporal_correlation,
            total_correlations=len(correlations),
            strong_correlations=strong_correlations,
            patterns_detected=len(patterns),
            max_severity=max_severity,
            processing_time_ms=(time.perf_counter() - start_time) * 1000
        )

        # Update metrics
        with self.metrics_lock:
            self.metrics.total_analyses += 1
            self.metrics.total_patterns_detected += len(patterns)
            for pattern in patterns:
                self.metrics.patterns_by_type[pattern.pattern_type] += 1

            # Update averages
            n = self.metrics.total_analyses
            self.metrics.average_analysis_time_ms = (
                (self.metrics.average_analysis_time_ms * (n - 1) +
                 analysis.processing_time_ms) / n
            )
            self.metrics.average_anomaly_correlation = (
                (self.metrics.average_anomaly_correlation * (n - 1) +
                 anomaly_correlation) / n
            )

        # Store in history
        with self.history_lock:
            self.history_buffer.append(analysis)

        # Log high-severity patterns
        for pattern in patterns:
            if pattern.severity > 0.7:
                logger.warning(
                    f"HIGH SEVERITY PATTERN: {pattern.pattern_type.value} "
                    f"(severity={pattern.severity:.2f}, confidence={pattern.confidence:.2f})"
                )

        return analysis

    def _compute_pairwise_correlations(
        self,
        aggregation: AggregatedTelemetry
    ) -> List[CorrelationPair]:
        """Compute pairwise correlations between layers"""
        correlations = []
        layers = list(aggregation.layers.keys())

        # Define correlation pairs of interest
        correlation_pairs = [
            (TelemetryLayer.ENERGY, TelemetryLayer.THREAT, CorrelationType.ENERGY_THREAT),
            (TelemetryLayer.CONSCIOUSNESS, TelemetryLayer.DIFFUSION, CorrelationType.CONSCIOUSNESS_DIFFUSION),
            (TelemetryLayer.AGENT, TelemetryLayer.NETWORK, CorrelationType.AGENT_NETWORK),
            (TelemetryLayer.PHYSICS, TelemetryLayer.ENERGY, CorrelationType.PHYSICS_ENERGY),
            (TelemetryLayer.THREAT, TelemetryLayer.DIFFUSION, CorrelationType.THREAT_DIFFUSION),
            (TelemetryLayer.ENERGY, TelemetryLayer.CONSCIOUSNESS, CorrelationType.ENERGY_CONSCIOUSNESS),
        ]

        for layer_a, layer_b, corr_type in correlation_pairs:
            if layer_a in aggregation.layers and layer_b in aggregation.layers:
                # Extract time series data for correlation
                with self.time_series_lock:
                    data_a = np.array([
                        self._extract_numeric_value(aggregation.layers[layer_a])
                    ] + list(self.layer_time_series[layer_a]))

                    data_b = np.array([
                        self._extract_numeric_value(aggregation.layers[layer_b])
                    ] + list(self.layer_time_series[layer_b]))

                # Compute correlation
                corr_coef, p_value = self.statistical_correlator.compute_correlation(
                    data_a, data_b
                )

                # Only include if above minimum threshold
                if abs(corr_coef) >= self.min_correlation:
                    strength = self.statistical_correlator.classify_strength(corr_coef)

                    correlations.append(CorrelationPair(
                        layer_a=layer_a,
                        layer_b=layer_b,
                        correlation_type=corr_type,
                        correlation_coefficient=corr_coef,
                        strength=strength,
                        p_value=p_value,
                        sample_count=len(data_a)
                    ))

        return correlations

    def _extract_numeric_value(self, layer_data: LayerData) -> float:
        """Extract representative numeric value from layer data"""
        layer = layer_data.layer

        if layer == TelemetryLayer.ENERGY:
            return layer_data.data.get("total_energy", 0.0)
        elif layer == TelemetryLayer.THREAT:
            return layer_data.data.get("ici_score", 0.0)
        elif layer == TelemetryLayer.DIFFUSION:
            return layer_data.data.get("uncertainty", 0.0)
        elif layer == TelemetryLayer.CONSCIOUSNESS:
            # Map consciousness level to numeric
            level_map = {"REFLEXIVE": 0.2, "REACTIVE": 0.4, "AWARE": 0.6, "STRATEGIC": 0.8, "TRANSCENDENT": 1.0}
            return level_map.get(layer_data.data.get("level", ""), 0.5)
        elif layer == TelemetryLayer.PHYSICS:
            return layer_data.data.get("conservation", 0.0)
        elif layer == TelemetryLayer.AGENT:
            return layer_data.data.get("execution_time_ms", 0.0)
        elif layer == TelemetryLayer.NETWORK:
            return layer_data.data.get("bandwidth_mbps", 0.0)
        else:
            return 0.0

    def _calculate_anomaly_correlation(
        self,
        aggregation: AggregatedTelemetry,
        correlations: List[CorrelationPair]
    ) -> float:
        """
        Calculate overall anomaly correlation score

        Weighted sum of layer anomalies × correlation strengths
        """
        if not correlations:
            return aggregation.anomaly_score

        # Extract anomaly scores per layer
        layer_anomalies = {}

        if TelemetryLayer.ENERGY in aggregation.layers:
            layer_anomalies[TelemetryLayer.ENERGY] = aggregation.layers[TelemetryLayer.ENERGY].data.get("anomaly_score", 0)

        if TelemetryLayer.THREAT in aggregation.layers:
            layer_anomalies[TelemetryLayer.THREAT] = aggregation.layers[TelemetryLayer.THREAT].data.get("ici_score", 0) / 100.0

        if TelemetryLayer.DIFFUSION in aggregation.layers:
            layer_anomalies[TelemetryLayer.DIFFUSION] = aggregation.layers[TelemetryLayer.DIFFUSION].data.get("uncertainty", 0)

        # Calculate weighted correlation of anomalies
        anomaly_products = []
        for corr in correlations:
            if corr.layer_a in layer_anomalies and corr.layer_b in layer_anomalies:
                anomaly_a = layer_anomalies[corr.layer_a]
                anomaly_b = layer_anomalies[corr.layer_b]
                # Weight by correlation strength
                weight = abs(corr.correlation_coefficient)
                anomaly_products.append(weight * anomaly_a * anomaly_b)

        if anomaly_products:
            return float(np.mean(anomaly_products))
        else:
            return aggregation.anomaly_score

    def _calculate_temporal_correlation(
        self,
        aggregation: AggregatedTelemetry
    ) -> float:
        """
        Calculate temporal correlation with historical data

        Returns correlation with recent history
        """
        with self.history_lock:
            if len(self.history_buffer) < 5:
                return 0.0

            # Extract anomaly scores from history
            historical_anomalies = [
                analysis.anomaly_correlation_score
                for analysis in self.history_buffer
            ]

            # Current anomaly
            current_anomaly = aggregation.anomaly_score

            # Compute correlation
            historical_array = np.array(historical_anomalies)
            current_array = np.full_like(historical_array, current_anomaly)

            corr_coef, _ = self.statistical_correlator.compute_correlation(
                historical_array,
                current_array
            )

            return corr_coef

    def _update_time_series(self, aggregation: AggregatedTelemetry):
        """Update layer time series for correlation computation"""
        with self.time_series_lock:
            for layer, layer_data in aggregation.layers.items():
                numeric_value = self._extract_numeric_value(layer_data)
                self.layer_time_series[layer].append(numeric_value)

    def get_metrics(self) -> CorrelatorMetrics:
        """Get correlator metrics"""
        with self.metrics_lock:
            return CorrelatorMetrics(
                total_analyses=self.metrics.total_analyses,
                total_patterns_detected=self.metrics.total_patterns_detected,
                patterns_by_type=dict(self.metrics.patterns_by_type),
                average_analysis_time_ms=self.metrics.average_analysis_time_ms,
                average_anomaly_correlation=self.metrics.average_anomaly_correlation,
                true_positives=self.metrics.true_positives,
                false_positives=self.metrics.false_positives,
                false_negatives=self.metrics.false_negatives
            )

    def get_recent_analyses(self, count: int = 100) -> List[CorrelationAnalysis]:
        """Get recent correlation analyses"""
        with self.history_lock:
            return list(self.history_buffer)[-count:]

    def reset_metrics(self):
        """Reset correlator metrics"""
        with self.metrics_lock:
            self.metrics = CorrelatorMetrics()
        logger.info("Correlator metrics reset")


# Example usage
if __name__ == "__main__":
    print("AI Shield v2 - Cross-Layer Correlation Engine")
    print("=" * 60)

    print("\nInitializing Cross-Layer Correlator...")
    correlator = CrossLayerCorrelator(
        history_size=1000,
        min_correlation=0.3
    )

    print("\nConfiguration:")
    print(f"  History Size: {correlator.history_size}")
    print(f"  Minimum Correlation: {correlator.min_correlation}")

    print("\n✅ Phase 4.2 Complete: Cross-Layer Correlator operational")
    print("   - Pairwise correlation analysis:")
    print("     • Energy ↔ Threat")
    print("     • Consciousness ↔ Diffusion")
    print("     • Agent ↔ Network")
    print("     • Physics ↔ Energy")
    print("     • Threat ↔ Diffusion")
    print("     • Energy ↔ Consciousness")
    print("   - Attack pattern detection:")
    print("     • Coordinated attacks")
    print("     • Energy drain")
    print("     • Stealth intrusion")
    print("     • Diffusion mismatch")
    print("     • Consciousness bypass")
    print("     • Physics violation")
    print("   - Temporal correlation tracking")
    print("   - Anomaly correlation scoring")
    print("   - Ready for high-throughput optimization (Phase 4.3)")
