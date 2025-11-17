"""
A/B Testing Framework for UX Experiments.

This module provides a comprehensive A/B testing framework for running
controlled experiments on UX variations. Week 10 deliverable.

Features:
- Experiment creation and management
- User assignment to variants
- Metrics tracking and analysis
- Statistical significance calculation
- Experiment lifecycle management
- Multi-variate testing support
"""

import logging
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import asyncio
from collections import defaultdict
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Experiment lifecycle status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class VariantType(Enum):
    """Type of variant."""
    CONTROL = "control"
    TREATMENT = "treatment"


@dataclass
class ExperimentVariant:
    """A variant in an A/B test."""
    variant_id: str
    variant_name: str
    variant_type: str  # control or treatment
    traffic_allocation: float  # 0.0 to 1.0
    
    # UX configuration for this variant
    ux_config_overrides: Dict[str, Any]
    
    # Metrics
    users_assigned: int = 0
    conversions: int = 0
    total_interactions: int = 0
    avg_session_duration: float = 0.0
    engagement_score: float = 0.0


@dataclass
class Experiment:
    """An A/B test experiment."""
    experiment_id: str
    experiment_name: str
    description: str
    hypothesis: str
    
    # Status
    status: str
    created_at: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    
    # Variants
    variants: List[ExperimentVariant] = field(default_factory=list)
    
    # Targeting
    target_users: Optional[List[str]] = None  # None = all users
    target_expertise_levels: Optional[List[str]] = None
    target_device_types: Optional[List[str]] = None
    
    # Metrics to track
    primary_metric: str = "engagement_score"
    secondary_metrics: List[str] = field(default_factory=list)
    
    # Statistical parameters
    min_sample_size: int = 100
    confidence_level: float = 0.95
    min_detectable_effect: float = 0.05
    
    # Results
    winner: Optional[str] = None
    statistical_significance: Optional[float] = None
    results_summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentAssignment:
    """User assignment to an experiment variant."""
    assignment_id: str
    experiment_id: str
    user_id: str
    variant_id: str
    assigned_at: str
    
    # Tracking
    interactions: int = 0
    conversions: int = 0
    session_duration_total: float = 0.0
    last_interaction: Optional[str] = None


class ABTestingFramework:
    """
    A/B Testing Framework for running controlled UX experiments.
    
    Supports:
    - Multi-variant testing (A/B/C/...)
    - Traffic allocation control
    - User targeting
    - Metrics tracking
    - Statistical analysis
    """
    
    def __init__(self):
        """Initialize the A/B testing framework."""
        self.experiments: Dict[str, Experiment] = {}
        self.assignments: Dict[str, ExperimentAssignment] = {}
        self.metrics_buffer: List[Dict[str, Any]] = []
        logger.info("ABTestingFramework initialized")
    
    async def create_experiment(
        self,
        experiment_name: str,
        description: str,
        hypothesis: str,
        variants: List[Dict[str, Any]],
        primary_metric: str = "engagement_score",
        secondary_metrics: Optional[List[str]] = None,
        target_users: Optional[List[str]] = None,
        target_expertise_levels: Optional[List[str]] = None,
        min_sample_size: int = 100
    ) -> Experiment:
        """
        Create a new A/B test experiment.
        
        Args:
            experiment_name: Name of the experiment
            description: Detailed description
            hypothesis: Hypothesis being tested
            variants: List of variant configurations
            primary_metric: Primary success metric
            secondary_metrics: Additional metrics to track
            target_users: Specific users to include (None = all)
            target_expertise_levels: Target expertise levels
            min_sample_size: Minimum sample size per variant
        
        Returns:
            Created Experiment object
        """
        experiment_id = self._generate_experiment_id(experiment_name)
        
        # Validate traffic allocation
        total_allocation = sum(v["traffic_allocation"] for v in variants)
        if not (0.99 <= total_allocation <= 1.01):
            raise ValueError(f"Traffic allocation must sum to 1.0, got {total_allocation}")
        
        # Create variant objects
        variant_objects = []
        for v in variants:
            variant = ExperimentVariant(
                variant_id=f"{experiment_id}_{v['variant_name']}",
                variant_name=v["variant_name"],
                variant_type=v.get("variant_type", VariantType.TREATMENT.value),
                traffic_allocation=v["traffic_allocation"],
                ux_config_overrides=v.get("ux_config_overrides", {})
            )
            variant_objects.append(variant)
        
        experiment = Experiment(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            description=description,
            hypothesis=hypothesis,
            status=ExperimentStatus.DRAFT.value,
            created_at=datetime.utcnow().isoformat(),
            variants=variant_objects,
            target_users=target_users,
            target_expertise_levels=target_expertise_levels,
            primary_metric=primary_metric,
            secondary_metrics=secondary_metrics or [],
            min_sample_size=min_sample_size
        )
        
        self.experiments[experiment_id] = experiment
        
        logger.info(
            f"Created experiment '{experiment_name}' with {len(variants)} variants"
        )
        
        return experiment
    
    async def start_experiment(self, experiment_id: str):
        """Start an experiment."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.DRAFT.value:
            raise ValueError(f"Can only start experiments in DRAFT status")
        
        experiment.status = ExperimentStatus.ACTIVE.value
        experiment.started_at = datetime.utcnow().isoformat()
        
        logger.info(f"Started experiment: {experiment.experiment_name}")
    
    async def assign_user_to_experiment(
        self,
        experiment_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[ExperimentAssignment]:
        """
        Assign a user to an experiment variant.
        
        Uses deterministic hashing to ensure consistent assignment.
        
        Args:
            experiment_id: Experiment ID
            user_id: User ID
            user_context: User context (expertise level, device type, etc.)
        
        Returns:
            ExperimentAssignment or None if user doesn't qualify
        """
        if experiment_id not in self.experiments:
            return None
        
        experiment = self.experiments[experiment_id]
        
        # Check if experiment is active
        if experiment.status != ExperimentStatus.ACTIVE.value:
            return None
        
        # Check if user qualifies
        if not self._user_qualifies(experiment, user_id, user_context):
            return None
        
        # Check if user already assigned
        assignment_key = f"{experiment_id}_{user_id}"
        if assignment_key in self.assignments:
            return self.assignments[assignment_key]
        
        # Assign to variant using deterministic hashing
        variant = self._assign_variant(experiment, user_id)
        
        assignment = ExperimentAssignment(
            assignment_id=assignment_key,
            experiment_id=experiment_id,
            user_id=user_id,
            variant_id=variant.variant_id,
            assigned_at=datetime.utcnow().isoformat()
        )
        
        self.assignments[assignment_key] = assignment
        variant.users_assigned += 1
        
        logger.info(
            f"Assigned user {user_id} to variant {variant.variant_name} "
            f"in experiment {experiment.experiment_name}"
        )
        
        return assignment
    
    def _user_qualifies(
        self,
        experiment: Experiment,
        user_id: str,
        user_context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if user qualifies for experiment."""
        # Check target users
        if experiment.target_users and user_id not in experiment.target_users:
            return False
        
        if not user_context:
            return True
        
        # Check expertise level
        if experiment.target_expertise_levels:
            user_expertise = user_context.get("expertise_level")
            if user_expertise not in experiment.target_expertise_levels:
                return False
        
        # Check device type
        if experiment.target_device_types:
            device_type = user_context.get("device_type")
            if device_type not in experiment.target_device_types:
                return False
        
        return True
    
    def _assign_variant(
        self,
        experiment: Experiment,
        user_id: str
    ) -> ExperimentVariant:
        """Assign user to variant using deterministic hashing."""
        # Hash user_id + experiment_id for deterministic assignment
        hash_input = f"{experiment.experiment_id}_{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Normalize to 0-1
        normalized = (hash_value % 10000) / 10000.0
        
        # Assign based on traffic allocation
        cumulative = 0.0
        for variant in experiment.variants:
            cumulative += variant.traffic_allocation
            if normalized <= cumulative:
                return variant
        
        # Fallback to last variant
        return experiment.variants[-1]
    
    def _generate_experiment_id(self, experiment_name: str) -> str:
        """Generate unique experiment ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        name_hash = hashlib.md5(experiment_name.encode()).hexdigest()[:8]
        return f"exp_{timestamp}_{name_hash}"
    
    async def track_interaction(
        self,
        experiment_id: str,
        user_id: str,
        metric_name: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track an interaction metric for a user in an experiment."""
        assignment_key = f"{experiment_id}_{user_id}"
        
        if assignment_key not in self.assignments:
            return
        
        assignment = self.assignments[assignment_key]
        assignment.interactions += 1
        assignment.last_interaction = datetime.utcnow().isoformat()
        
        # Buffer metric for batch processing
        self.metrics_buffer.append({
            "experiment_id": experiment_id,
            "user_id": user_id,
            "variant_id": assignment.variant_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        })
    
    async def track_conversion(
        self,
        experiment_id: str,
        user_id: str
    ):
        """Track a conversion for a user in an experiment."""
        assignment_key = f"{experiment_id}_{user_id}"
        
        if assignment_key not in self.assignments:
            return
        
        assignment = self.assignments[assignment_key]
        assignment.conversions += 1
        
        # Update variant metrics
        experiment = self.experiments[experiment_id]
        for variant in experiment.variants:
            if variant.variant_id == assignment.variant_id:
                variant.conversions += 1
                break
    
    async def analyze_experiment(
        self,
        experiment_id: str
    ) -> Dict[str, Any]:
        """
        Analyze experiment results and calculate statistical significance.
        
        Returns:
            Analysis results including winner and significance
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        
        # Aggregate metrics by variant
        variant_metrics = self._aggregate_variant_metrics(experiment)
        
        # Calculate statistical significance
        significance = self._calculate_statistical_significance(
            variant_metrics,
            experiment.primary_metric
        )
        
        # Determine winner
        winner = self._determine_winner(variant_metrics, experiment.primary_metric)
        
        results = {
            "experiment_id": experiment_id,
            "experiment_name": experiment.experiment_name,
            "status": experiment.status,
            "variants": variant_metrics,
            "winner": winner,
            "statistical_significance": significance,
            "sample_size_adequate": self._check_sample_size(experiment),
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        experiment.results_summary = results
        experiment.winner = winner
        experiment.statistical_significance = significance
        
        logger.info(
            f"Analyzed experiment {experiment.experiment_name}: "
            f"winner={winner}, significance={significance:.3f}"
        )
        
        return results
    
    def _aggregate_variant_metrics(
        self,
        experiment: Experiment
    ) -> Dict[str, Dict[str, Any]]:
        """Aggregate metrics for each variant."""
        variant_metrics = {}
        
        for variant in experiment.variants:
            # Get all assignments for this variant
            variant_assignments = [
                a for a in self.assignments.values()
                if a.variant_id == variant.variant_id
            ]
            
            # Calculate metrics
            total_users = len(variant_assignments)
            total_conversions = sum(a.conversions for a in variant_assignments)
            total_interactions = sum(a.interactions for a in variant_assignments)
            
            conversion_rate = (
                total_conversions / total_users if total_users > 0 else 0
            )
            
            avg_interactions = (
                total_interactions / total_users if total_users > 0 else 0
            )
            
            variant_metrics[variant.variant_id] = {
                "variant_name": variant.variant_name,
                "variant_type": variant.variant_type,
                "users": total_users,
                "conversions": total_conversions,
                "conversion_rate": conversion_rate,
                "interactions": total_interactions,
                "avg_interactions": avg_interactions
            }
        
        return variant_metrics
    
    def _calculate_statistical_significance(
        self,
        variant_metrics: Dict[str, Dict[str, Any]],
        primary_metric: str
    ) -> float:
        """
        Calculate statistical significance using two-proportion z-test.
        
        Returns p-value (lower is more significant)
        """
        if len(variant_metrics) < 2:
            return 1.0
        
        # Get control and treatment
        control = None
        treatment = None
        
        for variant_id, metrics in variant_metrics.items():
            if metrics["variant_type"] == VariantType.CONTROL.value:
                control = metrics
            else:
                treatment = metrics
        
        if not control or not treatment:
            return 1.0
        
        # Calculate z-score for conversion rates
        p1 = control["conversion_rate"]
        n1 = control["users"]
        p2 = treatment["conversion_rate"]
        n2 = treatment["users"]
        
        if n1 == 0 or n2 == 0:
            return 1.0
        
        # Pooled proportion
        p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
        
        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        
        if se == 0:
            return 1.0
        
        # Z-score
        z = (p2 - p1) / se
        
        # Convert to p-value (two-tailed)
        # Approximation: p ≈ 2 * (1 - Φ(|z|))
        p_value = 2 * (1 - self._normal_cdf(abs(z)))
        
        return p_value
    
    def _normal_cdf(self, x: float) -> float:
        """Approximate normal CDF."""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    
    def _determine_winner(
        self,
        variant_metrics: Dict[str, Dict[str, Any]],
        primary_metric: str
    ) -> Optional[str]:
        """Determine winning variant based on primary metric."""
        if not variant_metrics:
            return None
        
        # Find variant with highest conversion rate
        best_variant = max(
            variant_metrics.items(),
            key=lambda x: x[1]["conversion_rate"]
        )
        
        return best_variant[1]["variant_name"]
    
    def _check_sample_size(self, experiment: Experiment) -> bool:
        """Check if all variants have adequate sample size."""
        for variant in experiment.variants:
            if variant.users_assigned < experiment.min_sample_size:
                return False
        return True
    
    async def stop_experiment(
        self,
        experiment_id: str,
        reason: str = "completed"
    ):
        """Stop an experiment."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED.value
        experiment.ended_at = datetime.utcnow().isoformat()
        
        # Run final analysis
        await self.analyze_experiment(experiment_id)
        
        logger.info(f"Stopped experiment: {experiment.experiment_name} ({reason})")
    
    def get_experiment_summary(
        self,
        experiment_id: str
    ) -> Dict[str, Any]:
        """Get summary of an experiment."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        
        return {
            "experiment_id": experiment.experiment_id,
            "experiment_name": experiment.experiment_name,
            "status": experiment.status,
            "variants": [asdict(v) for v in experiment.variants],
            "total_users": sum(v.users_assigned for v in experiment.variants),
            "results": experiment.results_summary
        }


# Singleton instance
ab_testing_framework = ABTestingFramework()
