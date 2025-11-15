"""
AI Shield v2 - Autonomous Operations Module
============================================

Autonomous decision-making and response execution based on ICI scores.

Phase 5: Autonomous Operations

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

from .decision_engine import (
    # Main engine
    AutonomousDecisionEngine,
    ICIClassifier,
    ActionPlanner,

    # Enums
    ThreatLevel,
    DecisionType,
    AutonomyLevel,

    # Data classes
    DecisionContext,
    AutonomousDecision,
    DecisionMetrics
)

from .response_executor import (
    # Main executor
    AutomatedResponseExecutor,
    ActionExecutor,
    RollbackManager,

    # Enums
    ExecutionStatus,
    ExecutionMode,

    # Data classes
    ExecutionResult,
    ExecutionMetrics
)

from .self_healing import (
    # Main system
    SelfHealingSystem,
    HealthMonitor,
    RecoveryPlanner,
    AdaptiveMitigationEngine,

    # Enums
    HealthStatus,
    RecoveryStrategy,

    # Data classes
    HealthAssessment,
    RecoveryPlan,
    RecoveryResult,
    AdaptiveStrategy,
    FeedbackLoop
)

__all__ = [
    # Decision engine
    "AutonomousDecisionEngine",
    "ICIClassifier",
    "ActionPlanner",
    "ThreatLevel",
    "DecisionType",
    "AutonomyLevel",
    "DecisionContext",
    "AutonomousDecision",
    "DecisionMetrics",

    # Response executor
    "AutomatedResponseExecutor",
    "ActionExecutor",
    "RollbackManager",
    "ExecutionStatus",
    "ExecutionMode",
    "ExecutionResult",
    "ExecutionMetrics",

    # Self-healing
    "SelfHealingSystem",
    "HealthMonitor",
    "RecoveryPlanner",
    "AdaptiveMitigationEngine",
    "HealthStatus",
    "RecoveryStrategy",
    "HealthAssessment",
    "RecoveryPlan",
    "RecoveryResult",
    "AdaptiveStrategy",
    "FeedbackLoop"
]
