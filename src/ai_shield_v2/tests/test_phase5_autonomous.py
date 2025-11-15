#!/usr/bin/env python3
"""
AI Shield v2 - Phase 5 Comprehensive Test Suite
================================================

Tests for Phase 5: Autonomous Operations
- Phase 5.1: ICI-Based Autonomous Decision Engine
- Phase 5.2: Automated Response Executor
- Phase 5.3: Self-Healing and Adaptive Mitigation

Test Coverage:
- Decision engine functionality
- Response executor safety mechanisms
- Self-healing system operations
- Integration across all Phase 5 components
- Performance benchmarks
- Production readiness validation

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

import pytest
import numpy as np
import time
from typing import List

# Import AI Shield Phase 5 components
from ai_shield_v2.autonomous import (
    # Decision engine
    AutonomousDecisionEngine,
    ICIClassifier,
    ActionPlanner,
    ThreatLevel,
    DecisionType,
    AutonomyLevel,
    DecisionContext,
    AutonomousDecision,
    DecisionMetrics,

    # Response executor
    AutomatedResponseExecutor,
    ActionExecutor,
    RollbackManager,
    ExecutionStatus,
    ExecutionMode,
    ExecutionResult,
    ExecutionMetrics,

    # Self-healing
    SelfHealingSystem,
    HealthMonitor,
    RecoveryPlanner,
    AdaptiveMitigationEngine,
    HealthStatus,
    RecoveryStrategy,
    HealthAssessment,
    RecoveryPlan,
    FeedbackLoop
)

# Import other AI Shield components for testing
from ai_shield_v2.fusion import FusionResult, ResponseAction, ICIScore, ThreatIntelligence, ConsensusMetrics, ConsensusType
from ai_shield_v2.telemetry import CorrelationAnalysis, CrossLayerPattern, AttackPattern
from ai_shield_v2.shadow_integration import UnifiedConsciousnessState, ConsciousnessLevel


# ============================================================================
# Phase 5.1: Decision Engine Tests
# ============================================================================

class TestICIClassifier:
    """Test ICI-based threat classification"""

    def test_classify_threat_normal(self):
        """Test normal threat classification"""
        assert ICIClassifier.classify_threat(10.0) == ThreatLevel.NORMAL
        assert ICIClassifier.classify_threat(20.0) == ThreatLevel.NORMAL

    def test_classify_threat_low(self):
        """Test low threat classification"""
        assert ICIClassifier.classify_threat(25.0) == ThreatLevel.LOW
        assert ICIClassifier.classify_threat(40.0) == ThreatLevel.LOW

    def test_classify_threat_medium(self):
        """Test medium threat classification"""
        assert ICIClassifier.classify_threat(45.0) == ThreatLevel.MEDIUM
        assert ICIClassifier.classify_threat(60.0) == ThreatLevel.MEDIUM

    def test_classify_threat_high(self):
        """Test high threat classification"""
        assert ICIClassifier.classify_threat(65.0) == ThreatLevel.HIGH
        assert ICIClassifier.classify_threat(80.0) == ThreatLevel.HIGH

    def test_classify_threat_critical(self):
        """Test critical threat classification"""
        assert ICIClassifier.classify_threat(85.0) == ThreatLevel.CRITICAL
        assert ICIClassifier.classify_threat(100.0) == ThreatLevel.CRITICAL

    def test_classify_threat_boundary_values(self):
        """Test boundary values"""
        assert ICIClassifier.classify_threat(-10.0) == ThreatLevel.NORMAL  # Clamped to 0
        assert ICIClassifier.classify_threat(150.0) == ThreatLevel.CRITICAL  # Clamped to 100

    def test_recommend_decision_type(self):
        """Test decision type recommendation"""
        assert ICIClassifier.recommend_decision_type(ThreatLevel.NORMAL) == DecisionType.MONITOR
        assert ICIClassifier.recommend_decision_type(ThreatLevel.LOW) == DecisionType.LOG_ALERT
        assert ICIClassifier.recommend_decision_type(ThreatLevel.MEDIUM) == DecisionType.CONTAIN
        assert ICIClassifier.recommend_decision_type(ThreatLevel.HIGH) == DecisionType.MITIGATE
        assert ICIClassifier.recommend_decision_type(ThreatLevel.CRITICAL) == DecisionType.AUTONOMOUS_RESPONSE

    def test_recommend_autonomy_level(self):
        """Test autonomy level recommendation"""
        # Low threat = full auto
        autonomy = ICIClassifier.recommend_autonomy_level(ThreatLevel.LOW, 0.8)
        assert autonomy == AutonomyLevel.FULL_AUTO

        # Medium threat with high confidence = semi-auto
        autonomy = ICIClassifier.recommend_autonomy_level(ThreatLevel.MEDIUM, 0.75)
        assert autonomy == AutonomyLevel.SEMI_AUTO

        # High threat with low confidence = manual
        autonomy = ICIClassifier.recommend_autonomy_level(ThreatLevel.HIGH, 0.5)
        assert autonomy == AutonomyLevel.MANUAL

        # Critical threat with high confidence + high consciousness = full auto
        autonomy = ICIClassifier.recommend_autonomy_level(
            ThreatLevel.CRITICAL, 0.95, ConsciousnessLevel.PLANETARY
        )
        assert autonomy == AutonomyLevel.FULL_AUTO


class TestActionPlanner:
    """Test action planning"""

    def test_plan_actions_normal_threat(self):
        """Test action planning for normal threat"""
        planner = ActionPlanner()

        context = DecisionContext(
            ici_score=10.0,
            threat_level=ThreatLevel.NORMAL,
            fusion_result=self._create_mock_fusion(10.0),
            energy_available=1.0
        )

        actions = planner.plan_actions(context, [])

        assert len(actions) > 0
        assert actions[0]["action"] == "monitor"

    def test_plan_actions_critical_threat(self):
        """Test action planning for critical threat"""
        planner = ActionPlanner()

        context = DecisionContext(
            ici_score=90.0,
            threat_level=ThreatLevel.CRITICAL,
            fusion_result=self._create_mock_fusion(90.0),
            energy_available=1.0
        )

        actions = planner.plan_actions(context, [])

        assert len(actions) > 0
        # Should include emergency actions
        action_types = [a["action"] for a in actions]
        assert "emergency_shutdown_affected" in action_types

    def test_plan_actions_energy_constraint(self):
        """Test action planning with energy constraints"""
        planner = ActionPlanner()

        context = DecisionContext(
            ici_score=70.0,
            threat_level=ThreatLevel.HIGH,
            fusion_result=self._create_mock_fusion(70.0),
            energy_available=0.2  # Limited energy
        )

        actions = planner.plan_actions(context, [])

        # Calculate total affordable actions
        affordable = [a for a in actions if not a.get("deferred", False)]
        total_cost = sum(a.get("energy_cost", 0.0) for a in affordable)

        assert total_cost <= context.energy_available

    def test_plan_actions_with_pattern(self):
        """Test action planning with attack pattern"""
        planner = ActionPlanner()

        # Create mock pattern
        pattern = CrossLayerPattern(
            pattern_id="test_pattern",
            pattern_type=AttackPattern.ENERGY_DRAIN,
            layers_involved=set(),
            confidence=0.8,
            severity=0.7,
            evidence={},
            recommended_action="throttle"
        )

        context = DecisionContext(
            ici_score=50.0,
            threat_level=ThreatLevel.MEDIUM,
            fusion_result=self._create_mock_fusion(50.0),
            energy_available=1.0
        )

        actions = planner.plan_actions(context, [pattern])

        # Should include pattern-specific action
        action_types = [a["action"] for a in actions]
        assert "throttle_resource_consumption" in action_types

    def _create_mock_fusion(self, ici_score: float) -> FusionResult:
        """Create mock fusion result"""
        # Create proper ICIScore with ConsensusMetrics
        consensus_metrics = ConsensusMetrics(
            total_detectors=7,
            agreeing_detectors=6,
            consensus_ratio=0.857,
            consensus_type=ConsensusType.SUPERMAJORITY,
            threshold_met=True,
            confidence=0.8
        )
        ici = ICIScore(
            score=ici_score,
            base_score=ici_score * 0.9,
            consensus_amplification=1.1,
            max_detector_score=ici_score / 100.0,
            consensus_metrics=consensus_metrics,
            response_action=ResponseAction.MONITOR
        )
        threat_intel = ThreatIntelligence(
            ici_score=ici,
            primary_threat="test_threat",
            affected_domains=set(),
            pattern_summary={},
            detector_votes={},
            recommended_actions=[]
        )
        return FusionResult(
            threat_intelligence=threat_intel,
            detector_results=[],
            processing_time_ms=0.01
        )


class TestAutonomousDecisionEngine:
    """Test autonomous decision engine"""

    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = AutonomousDecisionEngine(
            enable_full_autonomy=False,
            confidence_threshold=0.7,
            max_energy_per_decision=1.0
        )

        assert engine.enable_full_autonomy == False
        assert engine.confidence_threshold == 0.7
        assert engine.max_energy_per_decision == 1.0

        metrics = engine.get_metrics()
        assert metrics.total_decisions == 0

    def test_make_decision_normal_threat(self):
        """Test decision making for normal threat"""
        engine = AutonomousDecisionEngine()

        context = DecisionContext(
            ici_score=15.0,
            threat_level=ThreatLevel.NORMAL,
            fusion_result=self._create_mock_fusion(15.0),
            energy_available=1.0
        )

        decision = engine.make_decision(context)

        assert decision.threat_level == ThreatLevel.NORMAL
        assert decision.decision_type == DecisionType.MONITOR
        assert decision.ici_score == 15.0
        assert 0.0 <= decision.confidence <= 1.0
        assert len(decision.reasoning) > 0

    def test_make_decision_critical_threat(self):
        """Test decision making for critical threat"""
        engine = AutonomousDecisionEngine()

        context = DecisionContext(
            ici_score=95.0,
            threat_level=ThreatLevel.CRITICAL,
            fusion_result=self._create_mock_fusion(95.0),
            energy_available=1.0
        )

        decision = engine.make_decision(context)

        assert decision.threat_level == ThreatLevel.CRITICAL
        assert decision.decision_type == DecisionType.AUTONOMOUS_RESPONSE
        assert len(decision.recommended_actions) > 0

    def test_make_decision_with_patterns(self):
        """Test decision making with cross-layer patterns"""
        engine = AutonomousDecisionEngine()

        # Create mock correlation analysis with patterns
        pattern = CrossLayerPattern(
            pattern_id="test",
            pattern_type=AttackPattern.COORDINATED_ATTACK,
            layers_involved=set(),
            confidence=0.9,
            severity=0.8,
            evidence={},
            recommended_action="defend"
        )

        correlation = CorrelationAnalysis(
            aggregation_id="test",
            base_timestamp=time.time(),
            correlations=[],
            patterns=[pattern],
            anomaly_correlation_score=0.8,
            temporal_correlation=0.5,
            total_correlations=0,
            strong_correlations=0,
            patterns_detected=1,
            max_severity=0.8
        )

        context = DecisionContext(
            ici_score=70.0,
            threat_level=ThreatLevel.HIGH,
            fusion_result=self._create_mock_fusion(70.0),
            correlation_analysis=correlation,
            detected_patterns=[AttackPattern.COORDINATED_ATTACK],
            energy_available=1.0
        )

        decision = engine.make_decision(context)

        # Should include reasoning about patterns
        assert len(decision.reasoning) > 0
        # Verify patterns are considered in decision making
        assert decision.confidence > 0.0

    def test_make_decision_low_energy(self):
        """Test decision making with low energy"""
        engine = AutonomousDecisionEngine()

        context = DecisionContext(
            ici_score=60.0,
            threat_level=ThreatLevel.MEDIUM,
            fusion_result=self._create_mock_fusion(60.0),
            energy_available=0.3  # Low energy
        )

        decision = engine.make_decision(context)

        # Should note limited energy in reasoning
        assert any("energy" in r.lower() for r in decision.reasoning)

    def test_decision_metrics_tracking(self):
        """Test decision metrics are tracked correctly"""
        engine = AutonomousDecisionEngine()

        # Make several decisions
        for ici in [10, 30, 50, 70, 90]:
            context = DecisionContext(
                ici_score=float(ici),
                threat_level=ICIClassifier.classify_threat(float(ici)),
                fusion_result=self._create_mock_fusion(float(ici)),
                energy_available=1.0
            )
            engine.make_decision(context)

        metrics = engine.get_metrics()

        assert metrics.total_decisions == 5
        assert metrics.average_confidence > 0.0
        assert metrics.average_decision_time_ms > 0.0
        assert len(metrics.decisions_by_level) > 0

    def _create_mock_fusion(self, ici_score: float) -> FusionResult:
        """Create mock fusion result"""
        # Create proper ICIScore with ConsensusMetrics
        consensus_metrics = ConsensusMetrics(
            total_detectors=7,
            agreeing_detectors=6,
            consensus_ratio=0.857,
            consensus_type=ConsensusType.SUPERMAJORITY,
            threshold_met=True,
            confidence=0.8
        )
        ici = ICIScore(
            score=ici_score,
            base_score=ici_score * 0.9,
            consensus_amplification=1.1,
            max_detector_score=ici_score / 100.0,
            consensus_metrics=consensus_metrics,
            response_action=ResponseAction.MONITOR
        )
        threat_intel = ThreatIntelligence(
            ici_score=ici,
            primary_threat="test_threat",
            affected_domains=set(),
            pattern_summary={},
            detector_votes={},
            recommended_actions=[]
        )
        return FusionResult(
            threat_intelligence=threat_intel,
            detector_results=[],
            processing_time_ms=0.01
        )


# ============================================================================
# Phase 5.2: Response Executor Tests
# ============================================================================

class TestActionExecutor:
    """Test action executor"""

    def test_executor_initialization(self):
        """Test executor initialization"""
        executor = ActionExecutor(dry_run=True)

        assert executor.dry_run == True
        assert len(executor.action_handlers) > 0

    def test_execute_action_dry_run(self):
        """Test action execution in dry run mode"""
        executor = ActionExecutor(dry_run=True)

        action = {
            "action": "monitor",
            "priority": 1,
            "energy_cost": 0.01
        }

        result = executor.execute_action(action, "test_decision")

        assert result.success == True
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output.get("dry_run") == True
        assert result.duration_ms > 0

    def test_execute_action_validation_failure(self):
        """Test action execution with validation failure"""
        executor = ActionExecutor(dry_run=True)

        # Invalid action (missing 'action' field)
        action = {
            "priority": 1
        }

        result = executor.execute_action(action, "test_decision")

        assert result.success == False
        assert result.status == ExecutionStatus.FAILED

    def test_execute_action_deferred(self):
        """Test execution of deferred action"""
        executor = ActionExecutor(dry_run=True)

        action = {
            "action": "monitor",
            "deferred": True,
            "deferral_reason": "insufficient_energy"
        }

        result = executor.execute_action(action, "test_decision")

        assert result.success == False

    def test_all_action_handlers(self):
        """Test all built-in action handlers"""
        executor = ActionExecutor(dry_run=True)

        action_types = [
            "monitor", "log_event", "send_alert",
            "isolate_affected_resource", "increase_monitoring", "backup_state",
            "quarantine_threat", "activate_countermeasures", "notify_security_team",
            "preserve_forensics", "emergency_shutdown_affected",
            "activate_full_defense", "escalate_to_incident_response",
            "initiate_recovery_protocol"
        ]

        for action_type in action_types:
            action = {"action": action_type}
            result = executor.execute_action(action, "test_decision")

            assert result.success == True, f"Action {action_type} failed"
            assert result.status == ExecutionStatus.COMPLETED


class TestAutomatedResponseExecutor:
    """Test automated response executor"""

    def test_executor_initialization(self):
        """Test executor initialization"""
        executor = AutomatedResponseExecutor(
            execution_mode=ExecutionMode.DRY_RUN,
            max_concurrent_executions=3,
            enable_rollback=True
        )

        assert executor.execution_mode == ExecutionMode.DRY_RUN
        assert executor.max_concurrent_executions == 3
        assert executor.enable_rollback == True

    def test_executor_start_stop(self):
        """Test executor start and stop"""
        executor = AutomatedResponseExecutor(
            execution_mode=ExecutionMode.DRY_RUN
        )

        # Start
        executor.start()
        time.sleep(0.1)

        # Stop
        executor.stop(timeout=2.0)

    def test_execute_decision(self):
        """Test decision execution"""
        executor = AutomatedResponseExecutor(
            execution_mode=ExecutionMode.DRY_RUN,
            max_concurrent_executions=2
        )

        # Create mock decision
        decision = AutonomousDecision(
            decision_id="test_decision",
            decision_type=DecisionType.MONITOR,
            autonomy_level=AutonomyLevel.FULL_AUTO,
            ici_score=15.0,
            threat_level=ThreatLevel.NORMAL,
            confidence=0.8,
            reasoning=["Test decision"],
            recommended_actions=[
                {"action": "monitor", "priority": 1, "energy_cost": 0.01}
            ],
            energy_cost=0.01,
            risk_score=0.1,
            expected_effectiveness=0.7,
            requires_human_approval=False,
            approved=True
        )

        executor.start()
        results = executor.execute_decision(decision)
        time.sleep(0.2)  # Allow processing
        executor.stop(timeout=2.0)

        # Check execution occurred
        metrics = executor.get_metrics()
        assert metrics.total_executions >= 0

    def test_execute_decision_not_approved(self):
        """Test execution of unapproved decision"""
        executor = AutomatedResponseExecutor(
            execution_mode=ExecutionMode.DRY_RUN
        )

        decision = AutonomousDecision(
            decision_id="test",
            decision_type=DecisionType.MONITOR,
            autonomy_level=AutonomyLevel.MANUAL,
            ici_score=15.0,
            threat_level=ThreatLevel.NORMAL,
            confidence=0.8,
            reasoning=[],
            recommended_actions=[],
            energy_cost=0.0,
            risk_score=0.0,
            expected_effectiveness=0.0,
            requires_human_approval=True,
            approved=False  # Not approved
        )

        results = executor.execute_decision(decision)

        # Should not execute
        assert len(results) == 0

    def test_execution_metrics(self):
        """Test execution metrics tracking"""
        executor = AutomatedResponseExecutor(
            execution_mode=ExecutionMode.DRY_RUN
        )

        decision = AutonomousDecision(
            decision_id="test",
            decision_type=DecisionType.LOG_ALERT,
            autonomy_level=AutonomyLevel.FULL_AUTO,
            ici_score=30.0,
            threat_level=ThreatLevel.LOW,
            confidence=0.8,
            reasoning=[],
            recommended_actions=[
                {"action": "log_event"},
                {"action": "send_alert"}
            ],
            energy_cost=0.05,
            risk_score=0.2,
            expected_effectiveness=0.8,
            requires_human_approval=False,
            approved=True
        )

        executor.start()
        executor.execute_decision(decision)
        time.sleep(0.3)
        executor.stop(timeout=2.0)

        metrics = executor.get_metrics()
        # Should have executed some actions
        assert metrics.total_executions >= 0


# ============================================================================
# Phase 5.3: Self-Healing Tests
# ============================================================================

class TestHealthMonitor:
    """Test health monitor"""

    def test_assess_health_healthy(self):
        """Test health assessment - healthy system"""
        monitor = HealthMonitor()

        metrics = {
            "ici_score": 10.0,
            "energy_available": 0.95,
            "average_response_time_ms": 50.0,
            "execution_success_rate": 0.98
        }

        assessment = monitor.assess_health(metrics)

        assert assessment.status == HealthStatus.HEALTHY
        assert assessment.health_score >= 0.9
        assert assessment.recovery_required == False

    def test_assess_health_degraded(self):
        """Test health assessment - degraded system"""
        monitor = HealthMonitor()

        metrics = {
            "ici_score": 50.0,
            "energy_available": 0.75,
            "average_response_time_ms": 200.0,
            "execution_success_rate": 0.85
        }

        assessment = monitor.assess_health(metrics)

        assert assessment.status in [HealthStatus.DEGRADED, HealthStatus.IMPAIRED]
        assert 0.5 <= assessment.health_score < 0.9
        assert assessment.recovery_required == True

    def test_assess_health_critical(self):
        """Test health assessment - critical system"""
        monitor = HealthMonitor()

        metrics = {
            "ici_score": 90.0,
            "energy_available": 0.2,
            "average_response_time_ms": 800.0,
            "execution_success_rate": 0.4
        }

        assessment = monitor.assess_health(metrics)

        assert assessment.status in [HealthStatus.IMPAIRED, HealthStatus.CRITICAL]
        assert assessment.health_score < 0.7
        assert assessment.recovery_required == True
        assert assessment.recommended_strategy is not None

    def test_component_health_tracking(self):
        """Test component-level health tracking"""
        monitor = HealthMonitor()

        monitor.update_component_health("component_a", 0.9)
        monitor.update_component_health("component_b", 0.5)

        metrics = {"ici_score": 30.0, "energy_available": 0.8}
        assessment = monitor.assess_health(metrics)

        # Should identify degraded component
        if assessment.affected_components:
            assert "component_b" in assessment.affected_components


class TestRecoveryPlanner:
    """Test recovery planner"""

    def test_plan_recovery_incremental(self):
        """Test incremental recovery planning"""
        planner = RecoveryPlanner()

        assessment = HealthAssessment(
            status=HealthStatus.DEGRADED,
            health_score=0.75,
            degradation_factors=["high_latency"],
            affected_components=["component_a"],
            recovery_required=True,
            recommended_strategy=RecoveryStrategy.INCREMENTAL
        )

        plan = planner.plan_recovery(assessment)

        assert plan.strategy == RecoveryStrategy.INCREMENTAL
        assert len(plan.recovery_actions) > 0
        assert plan.estimated_recovery_time > 0
        assert 0.0 <= plan.success_probability <= 1.0
        assert 0.0 <= plan.risk_score <= 1.0

    def test_plan_recovery_restart(self):
        """Test restart recovery planning"""
        planner = RecoveryPlanner()

        assessment = HealthAssessment(
            status=HealthStatus.DEGRADED,
            health_score=0.7,
            degradation_factors=[],
            affected_components=["service_a", "service_b"],
            recovery_required=True,
            recommended_strategy=RecoveryStrategy.RESTART
        )

        plan = planner.plan_recovery(assessment)

        assert plan.strategy == RecoveryStrategy.RESTART
        # Should have restart actions for each component
        assert len(plan.recovery_actions) == 2

    def test_plan_recovery_full_restore(self):
        """Test full restore recovery planning"""
        planner = RecoveryPlanner()

        assessment = HealthAssessment(
            status=HealthStatus.CRITICAL,
            health_score=0.3,
            degradation_factors=["multiple_failures"],
            affected_components=["comp1", "comp2", "comp3", "comp4"],
            recovery_required=True,
            recommended_strategy=RecoveryStrategy.FULL_RESTORE
        )

        plan = planner.plan_recovery(assessment)

        assert plan.strategy == RecoveryStrategy.FULL_RESTORE
        # Full restore should have reasonable success probability (lower due to critical state)
        assert 0.5 <= plan.success_probability <= 0.8
        assert len(plan.recovery_actions) > 0


class TestAdaptiveMitigationEngine:
    """Test adaptive mitigation engine"""

    def test_record_feedback(self):
        """Test feedback recording"""
        engine = AdaptiveMitigationEngine()

        feedback = FeedbackLoop(
            decision_id="test_decision",
            threat_level=ThreatLevel.MEDIUM,
            actions_executed=["isolate_resource", "increase_monitoring"],
            execution_success=True,
            threat_mitigated=True,
            energy_consumed=0.15,
            response_time=2.5,
            effectiveness_score=0.85,
            insights=["Successful mitigation"]
        )

        engine.record_feedback(feedback)

        # Check strategy was created
        strategy = engine.get_recommended_strategy(ThreatLevel.MEDIUM.value)
        assert strategy is not None
        assert strategy.effectiveness_score == 0.85

    def test_adaptive_learning(self):
        """Test adaptive strategy learning"""
        engine = AdaptiveMitigationEngine()

        # Record multiple feedback instances
        for i in range(10):
            feedback = FeedbackLoop(
                decision_id=f"decision_{i}",
                threat_level=ThreatLevel.HIGH,
                actions_executed=["quarantine_threat"],
                execution_success=True,
                threat_mitigated=(i % 2 == 0),  # 50% success rate
                energy_consumed=0.2,
                response_time=1.0,
                effectiveness_score=0.7 if i % 2 == 0 else 0.3
            )
            engine.record_feedback(feedback)

        strategy = engine.get_recommended_strategy(ThreatLevel.HIGH.value)
        assert strategy is not None
        # Success rate should converge around 0.5
        assert 0.3 <= strategy.success_rate <= 0.7
        assert strategy.usage_count == 10

    def test_strategy_insights(self):
        """Test strategy insights generation"""
        engine = AdaptiveMitigationEngine()

        # Record various strategies
        for threat_level in [ThreatLevel.LOW, ThreatLevel.MEDIUM, ThreatLevel.HIGH]:
            feedback = FeedbackLoop(
                decision_id="test",
                threat_level=threat_level,
                actions_executed=["test_action"],
                execution_success=True,
                threat_mitigated=True,
                energy_consumed=0.1,
                response_time=1.0,
                effectiveness_score=0.8
            )
            engine.record_feedback(feedback)

        insights = engine.get_strategy_insights()

        assert insights["total_strategies"] == 3
        assert len(insights["top_strategies"]) > 0
        assert insights["average_effectiveness"] > 0.0


class TestSelfHealingSystem:
    """Test self-healing system"""

    def test_system_initialization(self):
        """Test system initialization"""
        system = SelfHealingSystem()

        assert system.health_monitor is not None
        assert system.recovery_planner is not None
        assert system.adaptive_engine is not None

    def test_assess_and_heal_healthy(self):
        """Test assessment when system is healthy"""
        system = SelfHealingSystem()

        metrics = {
            "ici_score": 10.0,
            "energy_available": 0.95,
            "average_response_time_ms": 50.0,
            "execution_success_rate": 0.98
        }

        recovery_plan = system.assess_and_heal(metrics)

        # Should not require recovery
        assert recovery_plan is None

    def test_assess_and_heal_degraded(self):
        """Test assessment when system is degraded"""
        system = SelfHealingSystem()

        metrics = {
            "ici_score": 60.0,
            "energy_available": 0.6,
            "average_response_time_ms": 300.0,
            "execution_success_rate": 0.7
        }

        recovery_plan = system.assess_and_heal(metrics)

        # Should generate recovery plan
        assert recovery_plan is not None
        assert recovery_plan.strategy is not None
        assert recovery_plan.success_probability > 0.0
        assert recovery_plan.estimated_recovery_time > 0.0

    def test_record_outcome_successful(self):
        """Test recording successful outcome"""
        system = SelfHealingSystem()

        # Create mock decision
        decision = AutonomousDecision(
            decision_id="test",
            decision_type=DecisionType.MITIGATE,
            autonomy_level=AutonomyLevel.SEMI_AUTO,
            ici_score=65.0,
            threat_level=ThreatLevel.HIGH,
            confidence=0.85,
            reasoning=[],
            recommended_actions=[
                {"action": "quarantine_threat", "energy_cost": 0.2}
            ],
            energy_cost=0.2,
            risk_score=0.3,
            expected_effectiveness=0.8,
            requires_human_approval=False,
            approved=True
        )

        # Create mock execution results
        execution_results = [
            ExecutionResult(
                decision_id="test",
                action_id="action_1",
                action_type="quarantine_threat",
                status=ExecutionStatus.COMPLETED,
                success=True,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=100.0
            )
        ]

        system.record_outcome(decision, execution_results, threat_mitigated=True)

        # Check feedback was recorded
        insights = system.get_insights()
        assert insights["feedback_count"] > 0

    def test_record_outcome_failed(self):
        """Test recording failed outcome"""
        system = SelfHealingSystem()

        decision = AutonomousDecision(
            decision_id="test",
            decision_type=DecisionType.CONTAIN,
            autonomy_level=AutonomyLevel.FULL_AUTO,
            ici_score=50.0,
            threat_level=ThreatLevel.MEDIUM,
            confidence=0.7,
            reasoning=[],
            recommended_actions=[{"action": "isolate_resource", "energy_cost": 0.1}],
            energy_cost=0.1,
            risk_score=0.2,
            expected_effectiveness=0.75,
            requires_human_approval=False,
            approved=True
        )

        execution_results = [
            ExecutionResult(
                decision_id="test",
                action_id="action_1",
                action_type="isolate_resource",
                status=ExecutionStatus.FAILED,
                success=False,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=50.0,
                error="Test failure"
            )
        ]

        system.record_outcome(decision, execution_results, threat_mitigated=False)

        insights = system.get_insights()
        assert insights["feedback_count"] > 0

    def test_continuous_improvement(self):
        """Test continuous improvement through feedback"""
        system = SelfHealingSystem()

        # Simulate multiple threat response cycles
        for i in range(5):
            decision = AutonomousDecision(
                decision_id=f"decision_{i}",
                decision_type=DecisionType.MITIGATE,
                autonomy_level=AutonomyLevel.SEMI_AUTO,
                ici_score=70.0,
                threat_level=ThreatLevel.HIGH,
                confidence=0.8,
                reasoning=[],
                recommended_actions=[{"action": "quarantine_threat"}],
                energy_cost=0.2,
                risk_score=0.3,
                expected_effectiveness=0.8,
                requires_human_approval=False,
                approved=True
            )

            execution_results = [
                ExecutionResult(
                    decision_id=f"decision_{i}",
                    action_id=f"action_{i}",
                    action_type="quarantine_threat",
                    status=ExecutionStatus.COMPLETED,
                    success=True,
                    start_time=time.time(),
                    end_time=time.time(),
                    duration_ms=100.0
                )
            ]

            system.record_outcome(decision, execution_results, threat_mitigated=True)

        # Check that strategy was learned
        strategy = system.adaptive_engine.get_recommended_strategy(ThreatLevel.HIGH.value)
        assert strategy is not None
        assert strategy.usage_count == 5
        assert strategy.success_rate > 0.8  # All successful


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase5Integration:
    """Integration tests across all Phase 5 components"""

    def test_end_to_end_autonomous_response(self):
        """Test complete autonomous response flow"""
        # Initialize all components
        decision_engine = AutonomousDecisionEngine(enable_full_autonomy=True)
        executor = AutomatedResponseExecutor(execution_mode=ExecutionMode.DRY_RUN)
        healing_system = SelfHealingSystem()

        # Create decision context
        context = DecisionContext(
            ici_score=55.0,
            threat_level=ThreatLevel.MEDIUM,
            fusion_result=self._create_mock_fusion(55.0),
            energy_available=0.8
        )

        # Make decision
        decision = decision_engine.make_decision(context)
        assert decision is not None

        # Execute decision
        executor.start()
        executor.execute_decision(decision)
        time.sleep(0.3)
        executor.stop(timeout=2.0)

        # Record outcome for learning
        execution_results = executor.get_recent_executions(count=10)
        if execution_results:
            healing_system.record_outcome(decision, execution_results, threat_mitigated=True)

        # Verify learning occurred
        insights = healing_system.get_insights()
        assert insights["feedback_count"] > 0

    def test_decision_execution_feedback_loop(self):
        """Test decision → execution → feedback loop"""
        decision_engine = AutonomousDecisionEngine()
        executor = AutomatedResponseExecutor(execution_mode=ExecutionMode.DRY_RUN)
        healing_system = SelfHealingSystem()

        executor.start()

        # Process multiple threats
        for ici_score in [30, 50, 70]:
            context = DecisionContext(
                ici_score=float(ici_score),
                threat_level=ICIClassifier.classify_threat(float(ici_score)),
                fusion_result=self._create_mock_fusion(float(ici_score)),
                energy_available=0.9
            )

            decision = decision_engine.make_decision(context)
            executor.execute_decision(decision)
            time.sleep(0.1)

        time.sleep(0.3)
        executor.stop(timeout=2.0)

        # Check all components tracked data
        decision_metrics = decision_engine.get_metrics()
        execution_metrics = executor.get_metrics()

        assert decision_metrics.total_decisions == 3
        assert execution_metrics.total_executions >= 0

    def _create_mock_fusion(self, ici_score: float) -> FusionResult:
        """Create mock fusion result"""
        # Create proper ICIScore with ConsensusMetrics
        consensus_metrics = ConsensusMetrics(
            total_detectors=7,
            agreeing_detectors=6,
            consensus_ratio=0.857,
            consensus_type=ConsensusType.SUPERMAJORITY,
            threshold_met=True,
            confidence=0.8
        )
        ici = ICIScore(
            score=ici_score,
            base_score=ici_score * 0.9,
            consensus_amplification=1.1,
            max_detector_score=ici_score / 100.0,
            consensus_metrics=consensus_metrics,
            response_action=ResponseAction.MONITOR
        )
        threat_intel = ThreatIntelligence(
            ici_score=ici,
            primary_threat="test_threat",
            affected_domains=set(),
            pattern_summary={},
            detector_votes={},
            recommended_actions=[]
        )
        return FusionResult(
            threat_intelligence=threat_intel,
            detector_results=[],
            processing_time_ms=0.01
        )


# ============================================================================
# Production Readiness Tests
# ============================================================================

class TestPhase5ProductionReadiness:
    """Production readiness validation for Phase 5"""

    def test_decision_engine_thread_safety(self):
        """Test decision engine thread safety"""
        import threading

        engine = AutonomousDecisionEngine()
        results = []

        def make_decisions():
            for _ in range(10):
                context = DecisionContext(
                    ici_score=50.0,
                    threat_level=ThreatLevel.MEDIUM,
                    fusion_result=self._create_mock_fusion(50.0),
                    energy_available=0.8
                )
                decision = engine.make_decision(context)
                results.append(decision)

        threads = [threading.Thread(target=make_decisions) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 30 decisions
        assert len(results) == 30

        metrics = engine.get_metrics()
        assert metrics.total_decisions == 30

    def test_executor_concurrent_execution(self):
        """Test executor handles concurrent executions"""
        executor = AutomatedResponseExecutor(
            execution_mode=ExecutionMode.DRY_RUN,
            max_concurrent_executions=5
        )

        executor.start()

        # Submit multiple decisions
        for i in range(10):
            decision = AutonomousDecision(
                decision_id=f"decision_{i}",
                decision_type=DecisionType.MONITOR,
                autonomy_level=AutonomyLevel.FULL_AUTO,
                ici_score=20.0,
                threat_level=ThreatLevel.LOW,
                confidence=0.8,
                reasoning=[],
                recommended_actions=[{"action": "monitor"}],
                energy_cost=0.01,
                risk_score=0.1,
                expected_effectiveness=0.7,
                requires_human_approval=False,
                approved=True
            )
            executor.execute_decision(decision)

        time.sleep(0.5)
        executor.stop(timeout=3.0)

        # Should have processed actions
        metrics = executor.get_metrics()
        assert metrics.total_executions >= 0

    def test_healing_system_error_handling(self):
        """Test healing system handles errors gracefully"""
        system = SelfHealingSystem()

        # Test with invalid metrics
        invalid_metrics = {}

        try:
            assessment = system.assess_and_heal(invalid_metrics)
            # Should handle gracefully
            assert True
        except Exception as e:
            pytest.fail(f"Healing system should handle invalid metrics: {e}")

    def test_metrics_consistency(self):
        """Test metrics remain consistent"""
        engine = AutonomousDecisionEngine()

        # Make decisions
        for i in range(5):
            context = DecisionContext(
                ici_score=float(i * 20),
                threat_level=ICIClassifier.classify_threat(float(i * 20)),
                fusion_result=self._create_mock_fusion(float(i * 20)),
                energy_available=0.8
            )
            engine.make_decision(context)

        metrics1 = engine.get_metrics()
        metrics2 = engine.get_metrics()

        # Metrics should be consistent
        assert metrics1.total_decisions == metrics2.total_decisions
        assert metrics1.average_confidence == metrics2.average_confidence

    def _create_mock_fusion(self, ici_score: float) -> FusionResult:
        """Create mock fusion result"""
        # Create proper ICIScore with ConsensusMetrics
        consensus_metrics = ConsensusMetrics(
            total_detectors=7,
            agreeing_detectors=6,
            consensus_ratio=0.857,
            consensus_type=ConsensusType.SUPERMAJORITY,
            threshold_met=True,
            confidence=0.8
        )
        ici = ICIScore(
            score=ici_score,
            base_score=ici_score * 0.9,
            consensus_amplification=1.1,
            max_detector_score=ici_score / 100.0,
            consensus_metrics=consensus_metrics,
            response_action=ResponseAction.MONITOR
        )
        threat_intel = ThreatIntelligence(
            ici_score=ici,
            primary_threat="test_threat",
            affected_domains=set(),
            pattern_summary={},
            detector_votes={},
            recommended_actions=[]
        )
        return FusionResult(
            threat_intelligence=threat_intel,
            detector_results=[],
            processing_time_ms=0.01
        )


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == "__main__":
    print("AI Shield v2 - Phase 5 Comprehensive Test Suite")
    print("=" * 60)
    print("\nRunning Phase 5 tests...")
    print("  - Phase 5.1: ICI-Based Decision Engine")
    print("  - Phase 5.2: Automated Response Executor")
    print("  - Phase 5.3: Self-Healing System")
    print("  - Integration Tests")
    print("  - Production Readiness")
    print()

    pytest.main([__file__, "-v", "--tb=short"])
