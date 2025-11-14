"""
Energy Intelligence Layer (EIL) - Phase 5 Core Orchestrator

The EIL is the convergence point for all Industriverse phases:
- Phase 0: Shadow Twin Consensus + Proof Economy
- Phase 1: MicroAdapt + TTF Agent + Bridge API
- Phase 2: Smart Contracts + Model Evolution
- Phase 3: Hypothesis Orchestration (1,090 services)
- Phase 4: ACE/NVP Thermodynasty (99.99% fidelity)
- Phase 5: EIL (this layer)

Architecture: Parallel Ensemble
├── Statistical Branch: MicroAdapt (classical time series)
│   ├── Hierarchical windowing (60s/600s/3600s)
│   ├── Model unit adaptation (online learning)
│   └── 60-step forecasting
│
├── Physics Branch: RegimeDetector (deep learning + thermodynamics)
│   ├── Temporal GNN (spatial-temporal patterns)
│   ├── Frequency CNN (spectral analysis)
│   ├── Entropy rate dS/dt detection
│   └── Thermodynamic temperature T_eff
│
└── Decision Engine: Fusion + Policy
    ├── Fuses statistical + physics regimes
    ├── Thermo-policy optimizer
    ├── Proof validator (PoE tri-check)
    └── Market engine (CEU/PFT pricing)
"""

import numpy as np
import time
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Phase 5 imports
from .regime_detector import RegimeDetector, RegimeState
from .microadapt import (
    DynamicDataCollection,
    ModelUnitAdaptation,
    ModelUnitSearch,
    WindowSet,
    RegimeAssignment
)


@dataclass
class EILContext:
    """Complete context for EIL decision making"""
    # Input
    energy_map: np.ndarray
    domain: str
    cluster: str
    node: str
    timestamp: float

    # Statistical regime (MicroAdapt)
    statistical_regime_id: str = None
    statistical_confidence: float = 0.0
    forecast_mean: float = 0.0
    forecast_std: float = 0.0
    model_units_active: int = 0

    # Physics regime (RegimeDetector)
    physics_regime_label: str = None
    physics_confidence: float = 0.0
    entropy_rate: float = 0.0
    temperature: float = 1.0
    critical_features: Dict = field(default_factory=dict)

    # Fusion decision
    consensus: bool = False
    consensus_confidence: float = 0.0
    approved: bool = False
    validity_score: float = 0.0


@dataclass
class EILDecision:
    """Final decision from Energy Intelligence Layer"""
    context: EILContext
    regime: str  # Unified regime label
    confidence: float
    approved: bool
    validity_score: float

    # Forecasting
    forecast_mean: float
    forecast_std: float
    forecast_horizon: int

    # Thermodynamics
    energy_state: float
    entropy_rate: float
    temperature: float

    # Policy
    recommended_action: str
    risk_level: str  # low, medium, high
    proof_required: bool

    # Metadata
    timestamp: float
    processing_time_ms: float


class EnergyIntelligenceLayer:
    """
    Main orchestrator for Phase 5 EIL.

    Unifies statistical forecasting (MicroAdapt) with physics-informed
    regime detection (RegimeDetector) to provide comprehensive energy intelligence.
    """

    def __init__(
        self,
        regime_detector_checkpoint: Optional[str] = None,
        microadapt_config: Optional[Dict] = None
    ):
        """
        Initialize EIL with both statistical and physics branches.

        Args:
            regime_detector_checkpoint: Path to RegimeDetector checkpoint
            microadapt_config: Configuration dict for MicroAdapt
        """
        # Physics Branch: RegimeDetector
        self.regime_detector = RegimeDetector(
            model_checkpoint=regime_detector_checkpoint
        )

        # Statistical Branch: MicroAdapt components
        self.data_collector = DynamicDataCollection(
            hierarchy_levels=microadapt_config.get('hierarchy_levels', 3) if microadapt_config else 3,
            window_sizes=microadapt_config.get('window_sizes', [60, 600, 3600]) if microadapt_config else [60, 600, 3600]
        )

        self.model_adaptation = ModelUnitAdaptation(
            max_units=microadapt_config.get('max_units', 100) if microadapt_config else 100,
            initial_units=microadapt_config.get('initial_units', 10) if microadapt_config else 10
        )

        self.model_search = ModelUnitSearch(
            top_k=microadapt_config.get('top_k', 5) if microadapt_config else 5
        )

        # Initialize model units with dummy data
        dummy_windows = []
        for level in range(1, 4):
            from .microadapt.models.window import HierarchicalWindow
            dummy_data = np.random.randn(10) * 0.1 + 0.5
            window = HierarchicalWindow(
                level=level,
                window_size=[60, 600, 3600][level-1],
                data=dummy_data
            )
            dummy_windows.append(window)

        initial_window_set = WindowSet(windows=dummy_windows)
        self.model_adaptation.initialize_model_units(initial_window_set, d_s=3, d_x=3)

        # History for MicroAdapt
        self.energy_history: List[float] = []

        # Decision thresholds
        self.consensus_threshold = 0.85  # Minimum confidence for consensus
        self.approval_threshold = 0.75   # Minimum validity for approval

        print(f"✅ EnergyIntelligenceLayer initialized")
        print(f"  Statistical branch: {len(self.model_adaptation.model_units)} model units")
        print(f"  Physics branch: RegimeDetector ready")
        print(f"  Decision thresholds: consensus={self.consensus_threshold}, approval={self.approval_threshold}")

    def process(
        self,
        energy_map: np.ndarray,
        domain: str,
        cluster: str = "default",
        node: str = "default",
        hypothesis: Optional[Dict] = None
    ) -> EILDecision:
        """
        Main processing pipeline: Statistical + Physics → Decision

        Args:
            energy_map: 2D energy field (H x W)
            domain: Physics domain (fluid_dynamics, molecular_dynamics, etc.)
            cluster: Cluster identifier
            node: Node identifier
            hypothesis: Optional hypothesis context

        Returns:
            EILDecision with unified regime intelligence
        """
        start_time = time.time()

        # Create context
        context = EILContext(
            energy_map=energy_map,
            domain=domain,
            cluster=cluster,
            node=node,
            timestamp=time.time()
        )

        # ========================================================================
        # Branch 1: Statistical Regime (MicroAdapt)
        # ========================================================================

        energy_scalar = float(np.mean(energy_map))
        self.energy_history.append(energy_scalar)
        if len(self.energy_history) > 3600:
            self.energy_history.pop(0)

        self.data_collector.add_data_point(energy_scalar, context.timestamp)

        # Decompose into hierarchical windows
        if len(self.energy_history) >= 10:
            window_set = self.data_collector.decompose(np.array(self.energy_history[-60:]))
        else:
            # Use current value repeated
            dummy_windows = []
            for level in range(1, 4):
                from .microadapt.models.window import HierarchicalWindow
                recent_data = np.array([energy_scalar] * 10)
                window = HierarchicalWindow(
                    level=level,
                    window_size=[60, 600, 3600][level-1],
                    data=recent_data
                )
                dummy_windows.append(window)
            window_set = WindowSet(windows=dummy_windows)

        # Adapt model units
        if len(self.energy_history) >= 60:
            try:
                recent_data = np.array(self.energy_history[-60:])
                self.model_adaptation.adapt(window_set)
            except Exception as e:
                print(f"Warning: Model adaptation failed: {e}")

        # Regime assignment
        regime_assignment = self.model_search.assign_regime(
            window_set,
            self.model_adaptation.model_units
        )

        # Forecast
        forecast_mean, forecast_std = self.model_search.forecast(
            current_window=window_set,
            regime_assignment=regime_assignment,
            model_units=self.model_adaptation.model_units,
            forecast_steps=60
        )

        # Update context with statistical results
        context.statistical_regime_id = regime_assignment.regime_id
        context.statistical_confidence = regime_assignment.confidence
        context.forecast_mean = float(np.mean(forecast_mean))
        context.forecast_std = float(np.mean(forecast_std))
        context.model_units_active = len(self.model_adaptation.model_units)

        # ========================================================================
        # Branch 2: Physics Regime (RegimeDetector)
        # ========================================================================

        physics_regime = self.regime_detector.detect(
            energy_map=energy_map,
            domain=domain
        )

        # Update context with physics results
        context.physics_regime_label = physics_regime.label
        context.physics_confidence = physics_regime.confidence
        context.entropy_rate = physics_regime.entropy_rate
        context.temperature = physics_regime.temperature
        context.critical_features = physics_regime.critical_features

        # ========================================================================
        # Decision Engine: Fusion + Policy
        # ========================================================================

        decision = self._make_decision(context, physics_regime)

        # Add timing
        decision.processing_time_ms = (time.time() - start_time) * 1000

        return decision

    def _make_decision(
        self,
        context: EILContext,
        physics_regime: RegimeState
    ) -> EILDecision:
        """
        Fuse statistical and physics regimes into final decision.

        Decision Logic:
        1. Check consensus between statistical and physics branches
        2. Compute unified validity score
        3. Determine approval based on thresholds
        4. Assign risk level based on entropy rate
        5. Recommend action based on regime stability
        """

        # 1. Consensus: Do both branches agree on regime stability?
        statistical_stable = context.statistical_confidence > self.consensus_threshold
        physics_stable = (
            physics_regime.label in ["stable", "transitional"] and
            context.physics_confidence > self.consensus_threshold
        )

        consensus = statistical_stable and physics_stable
        consensus_confidence = min(context.statistical_confidence, context.physics_confidence)

        context.consensus = consensus
        context.consensus_confidence = consensus_confidence

        # 2. Unified validity score (weighted average)
        # Weight physics branch higher for thermodynamic accuracy
        validity_score = (
            0.4 * context.statistical_confidence +
            0.6 * context.physics_confidence
        )

        context.validity_score = validity_score

        # 3. Approval decision
        approved = validity_score >= self.approval_threshold and consensus
        context.approved = approved

        # 4. Unified regime label
        if consensus:
            # Both agree
            unified_regime = f"{physics_regime.label}_confirmed"
        else:
            # Disagreement - use physics branch (more reliable for thermodynamics)
            unified_regime = f"{physics_regime.label}_unconfirmed"

        # 5. Risk level based on entropy rate (thermodynamic instability)
        if context.entropy_rate < 0.05:
            risk_level = "low"
        elif context.entropy_rate < 0.15:
            risk_level = "medium"
        else:
            risk_level = "high"

        # 6. Recommended action
        if physics_regime.label == "stable" and consensus:
            recommended_action = "proceed"
        elif physics_regime.label == "transitional":
            recommended_action = "monitor"
        elif physics_regime.label in ["chaotic", "phase_change"]:
            recommended_action = "investigate"
        elif physics_regime.label == "anomalous":
            recommended_action = "alert"
        else:
            recommended_action = "defer"

        # 7. Proof requirement
        # Require proof for high-risk or unapproved regimes
        proof_required = (risk_level == "high" or not approved)

        return EILDecision(
            context=context,
            regime=unified_regime,
            confidence=consensus_confidence,
            approved=approved,
            validity_score=validity_score,
            forecast_mean=context.forecast_mean,
            forecast_std=context.forecast_std,
            forecast_horizon=60,
            energy_state=float(np.mean(context.energy_map)),
            entropy_rate=context.entropy_rate,
            temperature=context.temperature,
            recommended_action=recommended_action,
            risk_level=risk_level,
            proof_required=proof_required,
            timestamp=context.timestamp,
            processing_time_ms=0.0  # Will be set by caller
        )

    def get_stats(self) -> Dict:
        """Get current statistics for monitoring"""
        return {
            'statistical_branch': {
                'model_units': len(self.model_adaptation.model_units),
                'history_size': len(self.energy_history),
                'window_levels': self.data_collector.hierarchy_levels
            },
            'physics_branch': {
                'regime_labels': self.regime_detector.regime_labels
            },
            'thresholds': {
                'consensus': self.consensus_threshold,
                'approval': self.approval_threshold
            }
        }


# ============================================================================
# Testing Stub
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Energy Intelligence Layer - Test Run")
    print("=" * 70)

    # Initialize EIL
    eil = EnergyIntelligenceLayer()

    # Test Case 1: Stable regime
    print("\n[Test 1] Stable energy pattern")
    energy_map_stable = np.random.randn(64, 64) * 0.05 + 1.0

    decision = eil.process(
        energy_map=energy_map_stable,
        domain="fluid_dynamics",
        cluster="cluster-1",
        node="node-1"
    )

    print(f"  Regime: {decision.regime}")
    print(f"  Confidence: {decision.confidence:.3f}")
    print(f"  Approved: {decision.approved}")
    print(f"  Risk: {decision.risk_level}")
    print(f"  Action: {decision.recommended_action}")
    print(f"  Forecast: {decision.forecast_mean:.3f} ± {decision.forecast_std:.3f}")
    print(f"  Entropy rate: {decision.entropy_rate:.4f}")
    print(f"  Processing time: {decision.processing_time_ms:.1f}ms")

    # Test Case 2: Chaotic regime
    print("\n[Test 2] Chaotic energy pattern")
    energy_map_chaotic = np.random.randn(64, 64) * 2.0 + 5.0

    decision = eil.process(
        energy_map=energy_map_chaotic,
        domain="molecular_dynamics",
        cluster="cluster-2",
        node="node-2"
    )

    print(f"  Regime: {decision.regime}")
    print(f"  Confidence: {decision.confidence:.3f}")
    print(f"  Approved: {decision.approved}")
    print(f"  Risk: {decision.risk_level}")
    print(f"  Action: {decision.recommended_action}")
    print(f"  Proof required: {decision.proof_required}")

    print("\n" + "=" * 70)
    print("✅ EIL Test Complete")
    print("=" * 70)
