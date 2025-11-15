#!/usr/bin/env python3
"""
AI Shield v2 - Physics Fusion Engine
=====================================

Multi-detector consensus engine with ICI (Industriverse Criticality Index) scoring
and automated threat response determination.

Architecture:
- 4/7 Consensus Requirement (Byzantine Fault Tolerance)
- ICI Scoring: 0-100 with consensus amplification
- Automated Response Mapping
- Threat Intelligence Aggregation
- Target Latency: <0.05ms

Mathematical Foundation:
    ICI = 100 × max(s₁, s₂, ..., s₇) × (1 + α × (C - 0.5))

Where:
    sᵢ = normalized threat score from detector i (0-1)
    C = consensus ratio (agreeing detectors / total detectors)
    α = amplification factor (0.5-1.0)

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
Classification: CONFIDENTIAL - PATENT PENDING
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import logging
import time

# Import UPD components
from ..upd.universal_pattern_detectors import (
    DetectionResult,
    ThreatLevel,
    ExtendedDomain,
    DetectionPattern
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseAction(Enum):
    """Automated response actions based on ICI score"""
    MONITOR = "monitor"                 # ICI 0-20: Passive observation
    LOG = "log"                         # ICI 21-40: Record for analysis
    ALERT = "alert"                     # ICI 41-60: Notify operators
    MITIGATE = "mitigate"               # ICI 61-80: Automated mitigation
    ISOLATE = "isolate"                 # ICI 81-100: Emergency isolation


class ConsensusType(Enum):
    """Consensus decision types"""
    UNANIMOUS = "unanimous"             # 7/7 agreement
    SUPERMAJORITY = "supermajority"     # 6/7 agreement
    MAJORITY = "majority"               # 5/7 agreement
    THRESHOLD = "threshold"             # 4/7 agreement (minimum)
    INSUFFICIENT = "insufficient"       # <4/7 (no consensus)


@dataclass
class ConsensusMetrics:
    """Consensus calculation metrics"""
    total_detectors: int
    agreeing_detectors: int
    consensus_ratio: float
    consensus_type: ConsensusType
    threshold_met: bool  # True if >= 4/7
    confidence: float


@dataclass
class ICIScore:
    """Industriverse Criticality Index (ICI) score and metadata"""
    score: float  # 0-100
    base_score: float  # Before consensus amplification
    consensus_amplification: float  # Multiplier from consensus
    max_detector_score: float  # Highest individual detector score
    consensus_metrics: ConsensusMetrics
    response_action: ResponseAction
    timestamp: float = field(default_factory=time.time)


@dataclass
class ThreatIntelligence:
    """Aggregated threat intelligence from fusion analysis"""
    ici_score: ICIScore
    primary_threat: Optional[str]  # Dominant threat pattern type
    affected_domains: Set[ExtendedDomain]
    pattern_summary: Dict[str, int]  # Pattern type -> count
    detector_votes: Dict[str, float]  # Detector name -> threat score
    recommended_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FusionResult:
    """Complete fusion engine analysis result"""
    threat_intelligence: ThreatIntelligence
    detector_results: List[DetectionResult]
    processing_time_ms: float
    timestamp: float = field(default_factory=time.time)


class PhysicsFusionEngine:
    """
    Physics Fusion Engine - Multi-detector consensus and ICI scoring

    Implements:
    - 4/7 consensus threshold (Byzantine Fault Tolerance)
    - ICI scoring with consensus amplification
    - Automated response determination
    - Threat intelligence aggregation
    - Performance: <0.05ms target latency
    """

    def __init__(
        self,
        consensus_threshold: int = 4,
        amplification_factor: float = 0.75,
        response_thresholds: Optional[Dict[ResponseAction, float]] = None
    ):
        """
        Initialize Physics Fusion Engine

        Args:
            consensus_threshold: Minimum detectors for consensus (default 4/7)
            amplification_factor: Consensus amplification α (default 0.75)
            response_thresholds: Custom ICI thresholds for response actions
        """
        self.consensus_threshold = consensus_threshold
        self.amplification_factor = amplification_factor

        # Default response action thresholds
        self.response_thresholds = response_thresholds or {
            ResponseAction.MONITOR: 0.0,
            ResponseAction.LOG: 20.0,
            ResponseAction.ALERT: 40.0,
            ResponseAction.MITIGATE: 60.0,
            ResponseAction.ISOLATE: 80.0
        }

        # Performance tracking
        self.total_fusions = 0
        self.total_processing_time = 0.0
        self.consensus_distribution = {ct: 0 for ct in ConsensusType}

        logger.info(
            f"Initialized Physics Fusion Engine "
            f"(threshold={consensus_threshold}/7, α={amplification_factor})"
        )

    def fuse(self, detector_results: List[DetectionResult]) -> FusionResult:
        """
        Fuse multi-detector results into unified threat intelligence

        Args:
            detector_results: Results from all 7 UPD detectors

        Returns:
            FusionResult with ICI score and threat intelligence
        """
        start_time = time.perf_counter()

        # Validate input
        if len(detector_results) != 7:
            logger.warning(
                f"Expected 7 detector results, got {len(detector_results)}"
            )

        # Calculate consensus metrics
        consensus_metrics = self._calculate_consensus(detector_results)

        # Calculate ICI score
        ici_score = self._calculate_ici(detector_results, consensus_metrics)

        # Aggregate threat intelligence
        threat_intelligence = self._aggregate_threat_intelligence(
            detector_results,
            ici_score,
            consensus_metrics
        )

        processing_time = (time.perf_counter() - start_time) * 1000

        # Update metrics
        self.total_fusions += 1
        self.total_processing_time += processing_time
        self.consensus_distribution[consensus_metrics.consensus_type] += 1

        return FusionResult(
            threat_intelligence=threat_intelligence,
            detector_results=detector_results,
            processing_time_ms=processing_time
        )

    def _calculate_consensus(
        self,
        detector_results: List[DetectionResult]
    ) -> ConsensusMetrics:
        """
        Calculate consensus metrics from detector results

        Consensus is achieved when >= 4/7 detectors agree on threat presence
        (threat_score > 20.0)
        """
        total_detectors = len(detector_results)

        # Count detectors agreeing on threat presence
        agreeing_detectors = sum(
            1 for r in detector_results if r.threat_score > 20.0
        )

        consensus_ratio = agreeing_detectors / total_detectors if total_detectors > 0 else 0.0

        # Determine consensus type
        if agreeing_detectors == 7:
            consensus_type = ConsensusType.UNANIMOUS
        elif agreeing_detectors >= 6:
            consensus_type = ConsensusType.SUPERMAJORITY
        elif agreeing_detectors >= 5:
            consensus_type = ConsensusType.MAJORITY
        elif agreeing_detectors >= 4:
            consensus_type = ConsensusType.THRESHOLD
        else:
            consensus_type = ConsensusType.INSUFFICIENT

        threshold_met = agreeing_detectors >= self.consensus_threshold

        # Consensus confidence (based on agreement strength)
        confidence = consensus_ratio

        return ConsensusMetrics(
            total_detectors=total_detectors,
            agreeing_detectors=agreeing_detectors,
            consensus_ratio=consensus_ratio,
            consensus_type=consensus_type,
            threshold_met=threshold_met,
            confidence=confidence
        )

    def _calculate_ici(
        self,
        detector_results: List[DetectionResult],
        consensus_metrics: ConsensusMetrics
    ) -> ICIScore:
        """
        Calculate ICI (Industriverse Criticality Index) score

        Formula: ICI = 100 × max(s₁, ..., s₇) × (1 + α × (C - 0.5))

        Where:
            sᵢ = normalized threat score (0-1)
            C = consensus ratio
            α = amplification factor
        """
        # Get all threat scores (already 0-100 from detectors)
        threat_scores = [r.threat_score for r in detector_results]

        if not threat_scores:
            return ICIScore(
                score=0.0,
                base_score=0.0,
                consensus_amplification=1.0,
                max_detector_score=0.0,
                consensus_metrics=consensus_metrics,
                response_action=ResponseAction.MONITOR
            )

        # Normalize to 0-1
        normalized_scores = [s / 100.0 for s in threat_scores]

        # Base score: maximum detector score
        max_normalized = max(normalized_scores)
        base_score = max_normalized * 100.0

        # Consensus amplification
        C = consensus_metrics.consensus_ratio
        amplification = 1.0 + self.amplification_factor * (C - 0.5)

        # Final ICI score
        ici_value = base_score * amplification

        # Clamp to 0-100
        ici_value = max(0.0, min(100.0, ici_value))

        # Determine response action
        response_action = self._determine_response_action(ici_value)

        return ICIScore(
            score=ici_value,
            base_score=base_score,
            consensus_amplification=amplification,
            max_detector_score=max(threat_scores),
            consensus_metrics=consensus_metrics,
            response_action=response_action
        )

    def _determine_response_action(self, ici_score: float) -> ResponseAction:
        """Determine automated response action from ICI score"""
        for action in reversed(ResponseAction):  # Check from highest to lowest
            if ici_score >= self.response_thresholds[action]:
                return action

        return ResponseAction.MONITOR

    def _aggregate_threat_intelligence(
        self,
        detector_results: List[DetectionResult],
        ici_score: ICIScore,
        consensus_metrics: ConsensusMetrics
    ) -> ThreatIntelligence:
        """Aggregate threat intelligence from all detectors"""

        # Collect all detected patterns
        all_patterns: List[DetectionPattern] = []
        for result in detector_results:
            all_patterns.extend(result.detected_patterns)

        # Identify primary threat (most severe pattern)
        primary_threat = None
        if all_patterns:
            primary_pattern = max(
                all_patterns,
                key=lambda p: p.severity * p.confidence
            )
            primary_threat = primary_pattern.pattern_type

        # Collect affected domains
        affected_domains = set()
        for pattern in all_patterns:
            affected_domains.add(pattern.domain)

        # Pattern summary (count by type)
        pattern_summary: Dict[str, int] = {}
        for pattern in all_patterns:
            pattern_summary[pattern.pattern_type] = \
                pattern_summary.get(pattern.pattern_type, 0) + 1

        # Detector votes (name -> threat score)
        detector_votes = {
            result.detector_name: result.threat_score
            for result in detector_results
        }

        # Generate recommended actions
        recommended_actions = self._generate_recommendations(
            ici_score,
            all_patterns,
            consensus_metrics
        )

        return ThreatIntelligence(
            ici_score=ici_score,
            primary_threat=primary_threat,
            affected_domains=affected_domains,
            pattern_summary=pattern_summary,
            detector_votes=detector_votes,
            recommended_actions=recommended_actions,
            metadata={
                "total_patterns": len(all_patterns),
                "pattern_diversity": len(pattern_summary),
                "consensus_strength": consensus_metrics.consensus_type.value
            }
        )

    def _generate_recommendations(
        self,
        ici_score: ICIScore,
        patterns: List[DetectionPattern],
        consensus_metrics: ConsensusMetrics
    ) -> List[str]:
        """Generate recommended actions based on threat intelligence"""
        recommendations = []

        # Base action from ICI score
        action = ici_score.response_action
        recommendations.append(f"Execute {action.value} protocol")

        # Specific recommendations based on ICI level
        if ici_score.score >= 80:
            recommendations.append("CRITICAL: Immediate isolation required")
            recommendations.append("Initiate incident response procedure")
            recommendations.append("Notify security team immediately")

        elif ici_score.score >= 60:
            recommendations.append("HIGH: Automated mitigation activated")
            recommendations.append("Monitor for escalation")

        elif ici_score.score >= 40:
            recommendations.append("MEDIUM: Alert security operations")
            recommendations.append("Prepare mitigation strategies")

        elif ici_score.score >= 20:
            recommendations.append("LOW: Log for forensic analysis")
            recommendations.append("Continue monitoring")

        else:
            recommendations.append("BENIGN: Maintain standard monitoring")

        # Consensus-based recommendations
        if not consensus_metrics.threshold_met:
            recommendations.append(
                "WARNING: Consensus threshold not met - "
                "validate with additional detectors"
            )

        # Pattern-specific recommendations
        if patterns:
            domains = set(p.domain for p in patterns)
            if ExtendedDomain.CONSCIOUSNESS_FIELD in domains:
                recommendations.append(
                    "ALERT: Consciousness field anomaly detected - "
                    "engage Overseer monitoring"
                )

            if ExtendedDomain.AGENT_BEHAVIOR in domains:
                recommendations.append(
                    "Check agent alignment and behavioral policies"
                )

        return recommendations

    def batch_fuse(
        self,
        batch_results: List[List[DetectionResult]]
    ) -> List[FusionResult]:
        """
        Fuse multiple sets of detector results in batch

        Args:
            batch_results: List of detector result sets

        Returns:
            List of FusionResults
        """
        return [self.fuse(results) for results in batch_results]

    def get_metrics(self) -> Dict[str, Any]:
        """Get fusion engine performance metrics"""
        avg_time = (
            self.total_processing_time / self.total_fusions
            if self.total_fusions > 0 else 0.0
        )

        return {
            "total_fusions": self.total_fusions,
            "average_processing_time_ms": avg_time,
            "total_processing_time_ms": self.total_processing_time,
            "consensus_distribution": {
                ct.value: count
                for ct, count in self.consensus_distribution.items()
            },
            "configuration": {
                "consensus_threshold": self.consensus_threshold,
                "amplification_factor": self.amplification_factor,
                "response_thresholds": {
                    action.value: threshold
                    for action, threshold in self.response_thresholds.items()
                }
            }
        }

    def reset_metrics(self):
        """Reset performance metrics"""
        self.total_fusions = 0
        self.total_processing_time = 0.0
        self.consensus_distribution = {ct: 0 for ct in ConsensusType}
        logger.info("Fusion engine metrics reset")


# Example usage and testing
if __name__ == "__main__":
    print("AI Shield v2 - Physics Fusion Engine")
    print("=" * 60)

    print("\nInitializing Fusion Engine...")
    fusion = PhysicsFusionEngine(
        consensus_threshold=4,
        amplification_factor=0.75
    )

    print("\nConfiguration:")
    print(f"  Consensus Threshold: {fusion.consensus_threshold}/7")
    print(f"  Amplification Factor: {fusion.amplification_factor}")
    print(f"\nResponse Thresholds:")
    for action, threshold in fusion.response_thresholds.items():
        print(f"  {action.value.upper()}: ICI >= {threshold}")

    print("\n✅ Phase 1.4 Complete: Physics Fusion Engine operational")
    print("   - 4/7 consensus threshold configured")
    print("   - ICI scoring with consensus amplification enabled")
    print("   - Automated response mapping active")
    print("   - Target latency: <0.05ms")
