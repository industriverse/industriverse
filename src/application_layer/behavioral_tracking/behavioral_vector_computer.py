"""
Behavioral Vector Computation Service.

This module computes Behavioral Vectors (BV) from user interaction events.
BVs enable adaptive UX personalization. Part of Week 9: Behavioral Tracking Infrastructure.

Components:
- UsagePatternAnalyzer: Analyzes usage patterns
- PreferenceInferencer: Infers user preferences
- ExpertiseLevelCalculator: Calculates expertise level
- BehavioralVectorComputer: Main BV computation service
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class UsagePatterns:
    """Usage pattern metrics."""
    total_interactions: int
    avg_session_duration_minutes: float
    interactions_per_session: float
    capsule_type_distribution: Dict[str, float]
    interaction_type_distribution: Dict[str, float]
    time_of_day_distribution: Dict[str, float]
    day_of_week_distribution: Dict[str, float]


@dataclass
class UserPreferences:
    """User preferences inferred from behavior."""
    preferred_capsule_types: List[str]
    preferred_interaction_modes: List[str]
    layout_preference: str  # compact, comfortable, spacious
    density_preference: str  # minimal, balanced, detailed
    animation_preference: str  # none, subtle, full


@dataclass
class ProficiencyIndicators:
    """Detailed proficiency indicators."""
    avg_interaction_duration_ms: float
    error_rate: float
    completion_rate: float
    advanced_feature_usage_rate: float
    shortcut_usage_rate: float


@dataclass
class ExpertiseLevel:
    """User expertise level metrics."""
    overall_score: float
    category_scores: Dict[str, float]
    proficiency_indicators: ProficiencyIndicators
    archetype: str  # novice, intermediate, advanced, expert, power_user


@dataclass
class EngagementMetrics:
    """Engagement and retention metrics."""
    engagement_score: float
    recency_days: float
    frequency_per_week: float
    session_count: int
    retention_indicators: Dict[str, bool]


@dataclass
class AdaptiveUXConfig:
    """Adaptive UX configuration recommendations."""
    recommended_layout: str
    recommended_density: str
    recommended_features: List[str]
    recommended_shortcuts: List[str]
    capsule_priority_weights: Dict[str, float]


@dataclass
class BVMetadata:
    """Metadata about BV computation."""
    sample_size: int
    time_window_days: int
    confidence_score: float
    last_event_timestamp: str


@dataclass
class BehavioralVector:
    """Complete Behavioral Vector for a user."""
    user_id: str
    computed_at: str
    version: int
    usage_patterns: UsagePatterns
    preferences: UserPreferences
    expertise_level: ExpertiseLevel
    engagement_metrics: EngagementMetrics
    adaptive_ux_config: AdaptiveUXConfig
    metadata: BVMetadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        return result


class UsagePatternAnalyzer:
    """Analyzes user interaction patterns."""

    def analyze(self, events: List[Any], sessions: Dict[str, Any]) -> UsagePatterns:
        """
        Analyze usage patterns from events.

        Args:
            events: List of interaction events
            sessions: Session data dictionary

        Returns:
            UsagePatterns object
        """
        if not events:
            return UsagePatterns(
                total_interactions=0,
                avg_session_duration_minutes=0.0,
                interactions_per_session=0.0,
                capsule_type_distribution={},
                interaction_type_distribution={},
                time_of_day_distribution={},
                day_of_week_distribution={}
            )

        total_interactions = len(events)

        # Calculate session metrics
        session_count = len(sessions)
        interactions_per_session = total_interactions / session_count if session_count > 0 else 0

        # Calculate average session duration
        session_durations = []
        for session_id, session in sessions.items():
            if "started_at" in session and "last_interaction_at" in session:
                start = datetime.fromisoformat(session["started_at"])
                end = datetime.fromisoformat(session["last_interaction_at"])
                duration_minutes = (end - start).total_seconds() / 60
                session_durations.append(duration_minutes)

        avg_session_duration = statistics.mean(session_durations) if session_durations else 0.0

        # Analyze capsule type distribution
        capsule_types = [e.capsule_type for e in events if hasattr(e, 'capsule_type')]
        capsule_type_counts = Counter(capsule_types)
        capsule_type_distribution = {
            ct: count / total_interactions
            for ct, count in capsule_type_counts.items()
        }

        # Analyze interaction type distribution
        interaction_types = [e.event_type for e in events if hasattr(e, 'event_type')]
        interaction_type_counts = Counter(interaction_types)
        interaction_type_distribution = {
            it: count / total_interactions
            for it, count in interaction_type_counts.items()
        }

        # Analyze time of day distribution
        time_of_day_counts = defaultdict(int)
        for event in events:
            if hasattr(event, 'timestamp'):
                dt = datetime.fromisoformat(event.timestamp)
                hour = dt.hour
                time_of_day_counts[str(hour)] += 1

        time_of_day_distribution = {
            hour: count / total_interactions
            for hour, count in time_of_day_counts.items()
        }

        # Analyze day of week distribution
        day_of_week_counts = defaultdict(int)
        for event in events:
            if hasattr(event, 'timestamp'):
                dt = datetime.fromisoformat(event.timestamp)
                dow = dt.weekday()  # 0 = Monday, 6 = Sunday
                day_of_week_counts[str(dow)] += 1

        day_of_week_distribution = {
            dow: count / total_interactions
            for dow, count in day_of_week_counts.items()
        }

        return UsagePatterns(
            total_interactions=total_interactions,
            avg_session_duration_minutes=round(avg_session_duration, 2),
            interactions_per_session=round(interactions_per_session, 2),
            capsule_type_distribution=capsule_type_distribution,
            interaction_type_distribution=interaction_type_distribution,
            time_of_day_distribution=time_of_day_distribution,
            day_of_week_distribution=day_of_week_distribution
        )


class PreferenceInferencer:
    """Infers user preferences from behavior."""

    def infer(self, usage_patterns: UsagePatterns, events: List[Any]) -> UserPreferences:
        """
        Infer user preferences from usage patterns.

        Args:
            usage_patterns: Analyzed usage patterns
            events: List of interaction events

        Returns:
            UserPreferences object
        """
        # Get preferred capsule types (top 5 by frequency)
        preferred_capsule_types = sorted(
            usage_patterns.capsule_type_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        preferred_capsule_types = [ct for ct, _ in preferred_capsule_types]

        # Get preferred interaction modes (top 5 by frequency)
        preferred_interaction_modes = sorted(
            usage_patterns.interaction_type_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        preferred_interaction_modes = [it for it, _ in preferred_interaction_modes]

        # Infer layout preference based on resize/drag patterns
        layout_preference = self._infer_layout_preference(events)

        # Infer density preference based on expand/collapse patterns
        density_preference = self._infer_density_preference(events)

        # Infer animation preference based on interaction speed
        animation_preference = self._infer_animation_preference(events)

        return UserPreferences(
            preferred_capsule_types=preferred_capsule_types,
            preferred_interaction_modes=preferred_interaction_modes,
            layout_preference=layout_preference,
            density_preference=density_preference,
            animation_preference=animation_preference
        )

    def _infer_layout_preference(self, events: List[Any]) -> str:
        """Infer layout preference from resize/drag events."""
        resize_events = [e for e in events if hasattr(e, 'event_type') and e.event_type == 'resize']

        if not resize_events:
            return "comfortable"  # Default

        # Count size preferences from resize events
        size_counts = defaultdict(int)
        for event in resize_events:
            if hasattr(event, 'interaction_data') and 'size' in event.interaction_data:
                size = event.interaction_data['size']
                if size == 'small':
                    size_counts['compact'] += 1
                elif size == 'large':
                    size_counts['spacious'] += 1
                else:
                    size_counts['comfortable'] += 1

        if not size_counts:
            return "comfortable"

        return max(size_counts, key=size_counts.get)

    def _infer_density_preference(self, events: List[Any]) -> str:
        """Infer density preference from expand/collapse events."""
        expand_events = [e for e in events if hasattr(e, 'event_type') and e.event_type == 'expand']
        collapse_events = [e for e in events if hasattr(e, 'event_type') and e.event_type == 'collapse']

        total_expand_collapse = len(expand_events) + len(collapse_events)

        if total_expand_collapse == 0:
            return "balanced"  # Default

        # If user expands a lot, they want detailed view
        expand_rate = len(expand_events) / total_expand_collapse

        if expand_rate > 0.7:
            return "detailed"
        elif expand_rate < 0.3:
            return "minimal"
        else:
            return "balanced"

    def _infer_animation_preference(self, events: List[Any]) -> str:
        """Infer animation preference from interaction speed."""
        if not events:
            return "subtle"  # Default

        # Calculate average time between interactions
        interaction_times = []
        for i in range(1, len(events)):
            if hasattr(events[i], 'time_since_last_interaction_ms') and events[i].time_since_last_interaction_ms:
                interaction_times.append(events[i].time_since_last_interaction_ms)

        if not interaction_times:
            return "subtle"

        avg_time_ms = statistics.mean(interaction_times)

        # Fast interactions suggest user wants minimal animations
        if avg_time_ms < 1000:  # < 1 second
            return "none"
        elif avg_time_ms < 3000:  # < 3 seconds
            return "subtle"
        else:
            return "full"


class ExpertiseLevelCalculator:
    """Calculates user expertise level."""

    def calculate(self, events: List[Any], usage_patterns: UsagePatterns) -> ExpertiseLevel:
        """
        Calculate user expertise level.

        Args:
            events: List of interaction events
            usage_patterns: Analyzed usage patterns

        Returns:
            ExpertiseLevel object
        """
        if not events:
            return ExpertiseLevel(
                overall_score=0.0,
                category_scores={},
                proficiency_indicators=ProficiencyIndicators(
                    avg_interaction_duration_ms=0.0,
                    error_rate=0.0,
                    completion_rate=0.0,
                    advanced_feature_usage_rate=0.0,
                    shortcut_usage_rate=0.0
                ),
                archetype="novice"
            )

        # Calculate proficiency indicators
        proficiency = self._calculate_proficiency_indicators(events)

        # Calculate overall expertise score
        overall_score = self._calculate_overall_score(proficiency, usage_patterns)

        # Calculate category-specific scores
        category_scores = self._calculate_category_scores(events)

        # Determine user archetype
        archetype = self._determine_archetype(overall_score, proficiency)

        return ExpertiseLevel(
            overall_score=round(overall_score, 3),
            category_scores=category_scores,
            proficiency_indicators=proficiency,
            archetype=archetype
        )

    def _calculate_proficiency_indicators(self, events: List[Any]) -> ProficiencyIndicators:
        """Calculate proficiency indicators."""
        # Average interaction duration
        durations = [e.duration_ms for e in events if hasattr(e, 'duration_ms') and e.duration_ms is not None]
        avg_duration = statistics.mean(durations) if durations else 0.0

        # Error rate
        success_events = [e for e in events if hasattr(e, 'success')]
        if success_events:
            error_rate = 1.0 - (sum(1 for e in success_events if e.success) / len(success_events))
        else:
            error_rate = 0.0

        # Completion rate (tasks/workflows completed)
        completable_events = [
            e for e in events
            if hasattr(e, 'capsule_type') and e.capsule_type in ['task', 'workflow']
        ]
        complete_events = [
            e for e in completable_events
            if hasattr(e, 'event_type') and e.event_type == 'complete'
        ]
        completion_rate = len(complete_events) / len(completable_events) if completable_events else 0.0

        # Advanced feature usage (actions beyond basic interactions)
        advanced_interactions = ['resize', 'drag', 'decision', 'action']
        advanced_events = [
            e for e in events
            if hasattr(e, 'event_type') and e.event_type in advanced_interactions
        ]
        advanced_rate = len(advanced_events) / len(events) if events else 0.0

        # Shortcut usage (interaction targets that are actions)
        shortcut_events = [
            e for e in events
            if hasattr(e, 'interaction_target') and e.interaction_target == 'action'
        ]
        shortcut_rate = len(shortcut_events) / len(events) if events else 0.0

        return ProficiencyIndicators(
            avg_interaction_duration_ms=round(avg_duration, 2),
            error_rate=round(error_rate, 3),
            completion_rate=round(completion_rate, 3),
            advanced_feature_usage_rate=round(advanced_rate, 3),
            shortcut_usage_rate=round(shortcut_rate, 3)
        )

    def _calculate_overall_score(
        self,
        proficiency: ProficiencyIndicators,
        usage_patterns: UsagePatterns
    ) -> float:
        """Calculate overall expertise score (0.0 to 1.0)."""
        # Normalize and weight different factors

        # Duration score (faster = more expert, normalized to 0-1)
        # Assume 5000ms is novice, 1000ms is expert
        duration_score = max(0, min(1, 1 - (proficiency.avg_interaction_duration_ms - 1000) / 4000))

        # Error score (fewer errors = more expert)
        error_score = 1 - proficiency.error_rate

        # Completion score
        completion_score = proficiency.completion_rate

        # Advanced feature score
        advanced_score = proficiency.advanced_feature_usage_rate

        # Shortcut score
        shortcut_score = proficiency.shortcut_usage_rate

        # Diversity score (more capsule types = more expert)
        diversity_score = min(1.0, len(usage_patterns.capsule_type_distribution) / 5)

        # Weighted average
        overall_score = (
            duration_score * 0.20 +
            error_score * 0.25 +
            completion_score * 0.20 +
            advanced_score * 0.15 +
            shortcut_score * 0.10 +
            diversity_score * 0.10
        )

        return overall_score

    def _calculate_category_scores(self, events: List[Any]) -> Dict[str, float]:
        """Calculate expertise scores by capsule category."""
        category_events = defaultdict(list)

        for event in events:
            if hasattr(event, 'capsule_category') and event.capsule_category:
                category_events[event.capsule_category].append(event)

        category_scores = {}
        for category, cat_events in category_events.items():
            # Calculate a simple score based on interactions and success rate
            total = len(cat_events)
            successful = sum(1 for e in cat_events if hasattr(e, 'success') and e.success)
            score = (successful / total) if total > 0 else 0.0
            category_scores[category] = round(score, 3)

        return category_scores

    def _determine_archetype(
        self,
        overall_score: float,
        proficiency: ProficiencyIndicators
    ) -> str:
        """Determine user archetype based on overall score."""
        if overall_score >= 0.8 and proficiency.shortcut_usage_rate > 0.3:
            return "power_user"
        elif overall_score >= 0.7:
            return "expert"
        elif overall_score >= 0.5:
            return "advanced"
        elif overall_score >= 0.3:
            return "intermediate"
        else:
            return "novice"


class BehavioralVectorComputer:
    """Main service for computing Behavioral Vectors."""

    def __init__(self):
        """Initialize the BV computer."""
        self.usage_analyzer = UsagePatternAnalyzer()
        self.preference_inferencer = PreferenceInferencer()
        self.expertise_calculator = ExpertiseLevelCalculator()
        logger.info("Behavioral Vector Computer initialized")

    def compute(
        self,
        user_id: str,
        events: List[Any],
        sessions: Dict[str, Any],
        time_window_days: int = 30
    ) -> BehavioralVector:
        """
        Compute Behavioral Vector for a user.

        Args:
            user_id: User identifier
            events: List of interaction events
            sessions: Session data dictionary
            time_window_days: Time window for analysis (days)

        Returns:
            BehavioralVector object
        """
        logger.info(f"Computing Behavioral Vector for user {user_id} with {len(events)} events")

        # Analyze usage patterns
        usage_patterns = self.usage_analyzer.analyze(events, sessions)

        # Infer preferences
        preferences = self.preference_inferencer.infer(usage_patterns, events)

        # Calculate expertise level
        expertise_level = self.expertise_calculator.calculate(events, usage_patterns)

        # Calculate engagement metrics
        engagement_metrics = self._calculate_engagement_metrics(events, sessions)

        # Generate adaptive UX config
        adaptive_ux_config = self._generate_adaptive_ux_config(
            usage_patterns,
            preferences,
            expertise_level
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(len(events), time_window_days)

        # Create metadata
        metadata = BVMetadata(
            sample_size=len(events),
            time_window_days=time_window_days,
            confidence_score=confidence_score,
            last_event_timestamp=events[-1].timestamp if events else datetime.utcnow().isoformat()
        )

        # Create Behavioral Vector
        bv = BehavioralVector(
            user_id=user_id,
            computed_at=datetime.utcnow().isoformat(),
            version=1,
            usage_patterns=usage_patterns,
            preferences=preferences,
            expertise_level=expertise_level,
            engagement_metrics=engagement_metrics,
            adaptive_ux_config=adaptive_ux_config,
            metadata=metadata
        )

        logger.info(
            f"Computed BV for user {user_id}: expertise={expertise_level.archetype}, "
            f"engagement={engagement_metrics.engagement_score:.3f}, "
            f"confidence={confidence_score:.3f}"
        )

        return bv

    def _calculate_engagement_metrics(
        self,
        events: List[Any],
        sessions: Dict[str, Any]
    ) -> EngagementMetrics:
        """Calculate engagement and retention metrics."""
        if not events:
            return EngagementMetrics(
                engagement_score=0.0,
                recency_days=999.0,
                frequency_per_week=0.0,
                session_count=0,
                retention_indicators={
                    "weekly_active": False,
                    "monthly_active": False,
                    "at_risk": True
                }
            )

        # Recency (days since last interaction)
        last_event_time = datetime.fromisoformat(events[-1].timestamp)
        recency_days = (datetime.utcnow() - last_event_time).total_seconds() / 86400

        # Frequency (interactions per week)
        first_event_time = datetime.fromisoformat(events[0].timestamp)
        time_span_weeks = max(1, (datetime.utcnow() - first_event_time).total_seconds() / (7 * 86400))
        frequency_per_week = len(events) / time_span_weeks

        # Session count
        session_count = len(sessions)

        # Calculate engagement score (0.0 to 1.0)
        recency_score = max(0, 1 - (recency_days / 30))  # 30 days = 0 score
        frequency_score = min(1.0, frequency_per_week / 20)  # 20 interactions/week = max
        engagement_score = (recency_score * 0.5 + frequency_score * 0.5)

        # Retention indicators
        weekly_active = recency_days <= 7
        monthly_active = recency_days <= 30
        at_risk = recency_days > 14 and frequency_per_week < 2

        return EngagementMetrics(
            engagement_score=round(engagement_score, 3),
            recency_days=round(recency_days, 2),
            frequency_per_week=round(frequency_per_week, 2),
            session_count=session_count,
            retention_indicators={
                "weekly_active": weekly_active,
                "monthly_active": monthly_active,
                "at_risk": at_risk
            }
        )

    def _generate_adaptive_ux_config(
        self,
        usage_patterns: UsagePatterns,
        preferences: UserPreferences,
        expertise_level: ExpertiseLevel
    ) -> AdaptiveUXConfig:
        """Generate adaptive UX configuration recommendations."""
        # Recommended layout based on preferences
        recommended_layout = preferences.layout_preference

        # Recommended density based on expertise and preferences
        if expertise_level.archetype in ["expert", "power_user"]:
            recommended_density = "detailed"
        else:
            recommended_density = preferences.density_preference

        # Recommended features based on expertise
        recommended_features = []
        if expertise_level.archetype in ["advanced", "expert", "power_user"]:
            recommended_features.extend(["keyboard_shortcuts", "advanced_filters", "bulk_actions"])
        if expertise_level.archetype == "power_user":
            recommended_features.extend(["custom_workflows", "api_access", "automation"])

        # Recommended shortcuts based on usage patterns
        recommended_shortcuts = []
        top_interactions = sorted(
            usage_patterns.interaction_type_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        for interaction, _ in top_interactions:
            if interaction in ["expand", "collapse"]:
                recommended_shortcuts.append("space")
            elif interaction == "complete":
                recommended_shortcuts.append("ctrl+enter")
            elif interaction == "decision":
                recommended_shortcuts.append("1-9")

        # Capsule priority weights based on usage frequency
        capsule_priority_weights = dict(usage_patterns.capsule_type_distribution)

        return AdaptiveUXConfig(
            recommended_layout=recommended_layout,
            recommended_density=recommended_density,
            recommended_features=recommended_features,
            recommended_shortcuts=recommended_shortcuts,
            capsule_priority_weights=capsule_priority_weights
        )

    def _calculate_confidence_score(self, sample_size: int, time_window_days: int) -> float:
        """Calculate confidence score for BV accuracy."""
        # More events and longer time window = higher confidence

        # Sample size score (50+ events = max confidence from sample size)
        sample_score = min(1.0, sample_size / 50)

        # Time window score (30+ days = max confidence from time window)
        time_score = min(1.0, time_window_days / 30)

        # Combined confidence
        confidence = (sample_score * 0.7 + time_score * 0.3)

        return round(confidence, 3)


# Singleton instance
_bv_computer_instance = None


def get_bv_computer() -> BehavioralVectorComputer:
    """
    Get or create the singleton BehavioralVectorComputer instance.

    Returns:
        BehavioralVectorComputer instance
    """
    global _bv_computer_instance

    if _bv_computer_instance is None:
        _bv_computer_instance = BehavioralVectorComputer()

    return _bv_computer_instance
