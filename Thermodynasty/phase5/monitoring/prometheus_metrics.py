"""
Prometheus Metrics - Phase 5 EIL Regime Tracking

Comprehensive metrics for monitoring:
1. Regime Detection (detections, confidence, transitions)
2. Proof Validation (tri-check results, quality scores)
3. Market Engine (CEU costs, PFT minting, AMM reserves)
4. Feedback Trainer (learning events, accuracy, fusion weights)
5. Performance (latency, throughput, errors)

Integrates with Prometheus/Grafana for observability.
"""

from typing import Dict, Optional
from dataclasses import dataclass
import time

# Try to import prometheus_client, fallback to mock if not available
try:
    from prometheus_client import Counter, Histogram, Gauge, Info, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # Mock implementations for testing without prometheus_client
    PROMETHEUS_AVAILABLE = False

    class MockMetric:
        def __init__(self, *args, **kwargs):
            self.name = kwargs.get('name', 'mock')
            self.labels_dict = {}

        def labels(self, **labels):
            key = tuple(sorted(labels.items()))
            if key not in self.labels_dict:
                self.labels_dict[key] = self
            return self.labels_dict[key]

        def inc(self, amount=1):
            pass

        def observe(self, amount):
            pass

        def set(self, value):
            pass

        def info(self, data):
            pass

    Counter = Histogram = Gauge = Info = Summary = MockMetric


@dataclass
class MetricsSnapshot:
    """Snapshot of current metrics state"""
    timestamp: float
    regime_detections_total: int
    proof_validations_total: int
    pft_minted_total: float
    avg_regime_confidence: float
    avg_proof_quality: float
    avg_latency_ms: float


class PrometheusMetrics:
    """
    Prometheus metrics for Phase 5 EIL monitoring.

    Metrics Categories:
    1. Regime Detection
    2. Proof Validation
    3. Market Engine
    4. Feedback Trainer
    5. Performance
    """

    def __init__(self, namespace: str = "thermodynasty"):
        """
        Initialize Prometheus metrics

        Args:
            namespace: Metric namespace prefix
        """
        self.namespace = namespace

        # ====================================================================
        # REGIME DETECTION METRICS
        # ====================================================================

        self.regime_detections_total = Counter(
            f'{namespace}_regime_detections_total',
            'Total regime detections by type',
            ['regime', 'domain', 'cluster', 'approved']
        )

        self.regime_confidence = Histogram(
            f'{namespace}_regime_confidence',
            'Regime detection confidence scores',
            ['regime', 'domain'],
            buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
        )

        self.regime_transitions_total = Counter(
            f'{namespace}_regime_transitions_total',
            'Regime transition events',
            ['from_regime', 'to_regime', 'domain']
        )

        self.regime_entropy_rate = Histogram(
            f'{namespace}_regime_entropy_rate',
            'Entropy rate measurements',
            ['regime', 'domain'],
            buckets=[0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
        )

        self.regime_temperature = Histogram(
            f'{namespace}_regime_temperature',
            'Thermodynamic temperature measurements',
            ['regime', 'domain'],
            buckets=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 10.0]
        )

        # ====================================================================
        # PROOF VALIDATION METRICS
        # ====================================================================

        self.poe_validations_total = Counter(
            f'{namespace}_poe_validations_total',
            'Total proof validations',
            ['domain', 'passed', 'action']
        )

        self.poe_tri_check_results = Counter(
            f'{namespace}_poe_tri_check_results',
            'Tri-check validation results',
            ['check_type', 'passed']
        )

        self.poe_proof_quality = Histogram(
            f'{namespace}_poe_proof_quality',
            'Proof quality scores (avg of tri-check)',
            buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0]
        )

        self.poe_energy_fidelity = Histogram(
            f'{namespace}_poe_energy_fidelity',
            'Energy conservation check fidelity',
            buckets=[0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 0.999, 1.0]
        )

        self.poe_entropy_coherence = Histogram(
            f'{namespace}_poe_entropy_coherence',
            'Entropy coherence scores',
            buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
        )

        self.poe_spectral_similarity = Histogram(
            f'{namespace}_poe_spectral_similarity',
            'Spectral similarity scores',
            buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0]
        )

        # ====================================================================
        # MARKET ENGINE METRICS
        # ====================================================================

        self.market_ceu_cost = Histogram(
            f'{namespace}_market_ceu_cost',
            'CEU cost per inference',
            ['regime', 'approved'],
            buckets=[1, 2, 5, 10, 20, 50, 100, 200]
        )

        self.market_pft_minted_total = Counter(
            f'{namespace}_market_pft_minted_total',
            'Total PFT minted',
            ['regime', 'quality_tier']
        )

        self.market_pft_minted_amount = Summary(
            f'{namespace}_market_pft_minted_amount',
            'PFT minting amounts'
        )

        self.market_amm_ceu_reserve = Gauge(
            f'{namespace}_market_amm_ceu_reserve',
            'AMM CEU reserve level'
        )

        self.market_amm_pft_reserve = Gauge(
            f'{namespace}_market_amm_pft_reserve',
            'AMM PFT reserve level'
        )

        self.market_ceu_pft_rate = Gauge(
            f'{namespace}_market_ceu_pft_rate',
            'Current CEU/PFT exchange rate'
        )

        self.market_swap_volume_total = Counter(
            f'{namespace}_market_swap_volume_total',
            'Total swap volume',
            ['from_token', 'to_token']
        )

        # ====================================================================
        # FEEDBACK TRAINER METRICS
        # ====================================================================

        self.feedback_learning_events_total = Counter(
            f'{namespace}_feedback_learning_events_total',
            'Total learning events',
            ['adaptation_type']
        )

        self.feedback_regime_accuracy = Gauge(
            f'{namespace}_feedback_regime_accuracy',
            'Current regime prediction accuracy',
            ['domain']
        )

        self.feedback_forecast_error = Histogram(
            f'{namespace}_feedback_forecast_error',
            'Forecast error measurements',
            buckets=[0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
        )

        self.feedback_fusion_statistical_weight = Gauge(
            f'{namespace}_feedback_fusion_statistical_weight',
            'Current statistical branch fusion weight'
        )

        self.feedback_fusion_physics_weight = Gauge(
            f'{namespace}_feedback_fusion_physics_weight',
            'Current physics branch fusion weight'
        )

        # ====================================================================
        # PERFORMANCE METRICS
        # ====================================================================

        self.eil_process_latency = Histogram(
            f'{namespace}_eil_process_latency_seconds',
            'EIL processing latency',
            ['domain'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
        )

        self.eil_requests_total = Counter(
            f'{namespace}_eil_requests_total',
            'Total EIL requests',
            ['domain', 'status']
        )

        self.eil_errors_total = Counter(
            f'{namespace}_eil_errors_total',
            'Total EIL errors',
            ['error_type', 'component']
        )

        # ====================================================================
        # SYSTEM INFO
        # ====================================================================

        self.eil_info = Info(
            f'{namespace}_eil_info',
            'EIL system information'
        )

        # Statistics tracking (for testing without Prometheus)
        self.stats = {
            'regime_detections': 0,
            'proof_validations': 0,
            'pft_minted': 0.0,
            'total_requests': 0,
            'errors': 0
        }

        print(f"✅ PrometheusMetrics initialized (namespace: {namespace})")
        if not PROMETHEUS_AVAILABLE:
            print(f"⚠️  prometheus_client not available - using mock metrics")

    # ========================================================================
    # REGIME DETECTION TRACKING
    # ========================================================================

    def track_regime_detection(
        self,
        regime: str,
        domain: str,
        cluster: str,
        confidence: float,
        approved: bool,
        entropy_rate: float,
        temperature: float
    ):
        """Track regime detection event"""
        self.regime_detections_total.labels(
            regime=regime,
            domain=domain,
            cluster=cluster,
            approved=str(approved).lower()
        ).inc()

        self.regime_confidence.labels(
            regime=regime,
            domain=domain
        ).observe(confidence)

        self.regime_entropy_rate.labels(
            regime=regime,
            domain=domain
        ).observe(entropy_rate)

        self.regime_temperature.labels(
            regime=regime,
            domain=domain
        ).observe(temperature)

        self.stats['regime_detections'] += 1

    def track_regime_transition(
        self,
        from_regime: str,
        to_regime: str,
        domain: str
    ):
        """Track regime transition"""
        self.regime_transitions_total.labels(
            from_regime=from_regime,
            to_regime=to_regime,
            domain=domain
        ).inc()

    # ========================================================================
    # PROOF VALIDATION TRACKING
    # ========================================================================

    def track_proof_validation(
        self,
        domain: str,
        passed: bool,
        action: str,
        energy_fidelity: float,
        entropy_coherence: float,
        spectral_similarity: float,
        energy_check_passed: bool,
        entropy_check_passed: bool,
        spectral_check_passed: bool
    ):
        """Track proof validation event"""
        self.poe_validations_total.labels(
            domain=domain,
            passed=str(passed).lower(),
            action=action
        ).inc()

        # Tri-check results
        self.poe_tri_check_results.labels(
            check_type='energy',
            passed=str(energy_check_passed).lower()
        ).inc()

        self.poe_tri_check_results.labels(
            check_type='entropy',
            passed=str(entropy_check_passed).lower()
        ).inc()

        self.poe_tri_check_results.labels(
            check_type='spectral',
            passed=str(spectral_check_passed).lower()
        ).inc()

        # Quality metrics
        avg_quality = (energy_fidelity + entropy_coherence + spectral_similarity) / 3.0
        self.poe_proof_quality.observe(avg_quality)

        self.poe_energy_fidelity.observe(energy_fidelity)
        self.poe_entropy_coherence.observe(entropy_coherence)
        self.poe_spectral_similarity.observe(spectral_similarity)

        self.stats['proof_validations'] += 1

    # ========================================================================
    # MARKET ENGINE TRACKING
    # ========================================================================

    def track_ceu_cost(
        self,
        ceu_amount: float,
        regime: str,
        approved: bool
    ):
        """Track CEU cost"""
        self.market_ceu_cost.labels(
            regime=regime,
            approved=str(approved).lower()
        ).observe(ceu_amount)

    def track_pft_minting(
        self,
        pft_amount: float,
        regime: str,
        quality_tier: str  # exceptional|high|good|poor
    ):
        """Track PFT minting"""
        self.market_pft_minted_total.labels(
            regime=regime,
            quality_tier=quality_tier
        ).inc()

        self.market_pft_minted_amount.observe(pft_amount)

        self.stats['pft_minted'] += pft_amount

    def update_amm_reserves(
        self,
        ceu_reserve: float,
        pft_reserve: float,
        exchange_rate: float
    ):
        """Update AMM reserve gauges"""
        self.market_amm_ceu_reserve.set(ceu_reserve)
        self.market_amm_pft_reserve.set(pft_reserve)
        self.market_ceu_pft_rate.set(exchange_rate)

    def track_swap(
        self,
        from_token: str,
        to_token: str,
        amount: float
    ):
        """Track token swap"""
        self.market_swap_volume_total.labels(
            from_token=from_token,
            to_token=to_token
        ).inc()

    # ========================================================================
    # FEEDBACK TRAINER TRACKING
    # ========================================================================

    def track_learning_event(
        self,
        adaptation_type: str  # microadapt_boost|regime_calibration|fusion_update
    ):
        """Track feedback learning event"""
        self.feedback_learning_events_total.labels(
            adaptation_type=adaptation_type
        ).inc()

    def update_regime_accuracy(
        self,
        accuracy: float,
        domain: str = "overall"
    ):
        """Update regime accuracy gauge"""
        self.feedback_regime_accuracy.labels(domain=domain).set(accuracy)

    def track_forecast_error(
        self,
        error: float
    ):
        """Track forecast error"""
        self.feedback_forecast_error.observe(error)

    def update_fusion_weights(
        self,
        statistical_weight: float,
        physics_weight: float
    ):
        """Update fusion weight gauges"""
        self.feedback_fusion_statistical_weight.set(statistical_weight)
        self.feedback_fusion_physics_weight.set(physics_weight)

    # ========================================================================
    # PERFORMANCE TRACKING
    # ========================================================================

    def track_eil_request(
        self,
        domain: str,
        latency_seconds: float,
        status: str = "success"  # success|error
    ):
        """Track EIL request"""
        self.eil_process_latency.labels(domain=domain).observe(latency_seconds)

        self.eil_requests_total.labels(
            domain=domain,
            status=status
        ).inc()

        self.stats['total_requests'] += 1

    def track_error(
        self,
        error_type: str,
        component: str  # eil|regime_detector|microadapt|proof_validator|market_engine
    ):
        """Track error"""
        self.eil_errors_total.labels(
            error_type=error_type,
            component=component
        ).inc()

        self.stats['errors'] += 1

    def set_system_info(
        self,
        version: str,
        regime_detector_version: str,
        microadapt_version: str
    ):
        """Set system info"""
        self.eil_info.info({
            'version': version,
            'regime_detector_version': regime_detector_version,
            'microadapt_version': microadapt_version
        })

    # ========================================================================
    # SNAPSHOT
    # ========================================================================

    def get_snapshot(self) -> MetricsSnapshot:
        """Get current metrics snapshot"""
        return MetricsSnapshot(
            timestamp=time.time(),
            regime_detections_total=self.stats['regime_detections'],
            proof_validations_total=self.stats['proof_validations'],
            pft_minted_total=self.stats['pft_minted'],
            avg_regime_confidence=0.0,  # Would be calculated from histogram
            avg_proof_quality=0.0,  # Would be calculated from histogram
            avg_latency_ms=0.0  # Would be calculated from histogram
        )


# ============================================================================
# Singleton instance
# ============================================================================

_metrics_instance: Optional[PrometheusMetrics] = None


def get_metrics(namespace: str = "thermodynasty") -> PrometheusMetrics:
    """Get or create singleton metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PrometheusMetrics(namespace=namespace)
    return _metrics_instance


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PROMETHEUS METRICS - TEST")
    print("=" * 70)

    metrics = get_metrics("thermodynasty_test")

    # Set system info
    metrics.set_system_info(
        version="1.0.0-phase5",
        regime_detector_version="1.0.0",
        microadapt_version="2.0.0"
    )

    # Simulate regime detection
    print("\n[Test 1] Regime Detection")
    metrics.track_regime_detection(
        regime="stable_confirmed",
        domain="test_fluid",
        cluster="cluster-1",
        confidence=0.92,
        approved=True,
        entropy_rate=0.005,
        temperature=1.2
    )
    print("✅ Regime detection tracked")

    # Simulate proof validation
    print("\n[Test 2] Proof Validation")
    metrics.track_proof_validation(
        domain="test_fluid",
        passed=True,
        action="mint",
        energy_fidelity=0.98,
        entropy_coherence=0.94,
        spectral_similarity=0.90,
        energy_check_passed=True,
        entropy_check_passed=True,
        spectral_check_passed=True
    )
    print("✅ Proof validation tracked")

    # Simulate PFT minting
    print("\n[Test 3] PFT Minting")
    metrics.track_pft_minting(
        pft_amount=2.5,
        regime="stable_confirmed",
        quality_tier="high"
    )
    print("✅ PFT minting tracked")

    # Update AMM reserves
    print("\n[Test 4] AMM Reserves")
    metrics.update_amm_reserves(
        ceu_reserve=999900.0,
        pft_reserve=100100.0,
        exchange_rate=0.001
    )
    print("✅ AMM reserves updated")

    # Track learning
    print("\n[Test 5] Feedback Learning")
    metrics.track_learning_event("microadapt_boost")
    metrics.update_regime_accuracy(0.85, domain="test_fluid")
    metrics.update_fusion_weights(0.42, 0.58)
    print("✅ Learning events tracked")

    # Track performance
    print("\n[Test 6] Performance")
    metrics.track_eil_request(
        domain="test_fluid",
        latency_seconds=0.234,
        status="success"
    )
    print("✅ Performance tracked")

    # Get snapshot
    snapshot = metrics.get_snapshot()
    print("\n[Metrics Snapshot]")
    print(f"  Regime detections: {snapshot.regime_detections_total}")
    print(f"  Proof validations: {snapshot.proof_validations_total}")
    print(f"  PFT minted: {snapshot.pft_minted_total:.2f}")
    print(f"  Total requests: {metrics.stats['total_requests']}")

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
