"""
Dynamic Layout Adjuster for Real-Time UX Adaptation.

This module automatically adjusts capsule layouts based on user behavior patterns,
device context, and interaction feedback. Week 10 Day 3-4 deliverable.

Key Concepts:
- Layout rules engine with trigger conditions
- Smooth animated transitions between layouts
- User override capability with preference learning
- Feedback loop for continuous improvement

Architecture:
  User Interaction → Trigger Detection → Layout Adjustment → Smooth Transition
                                              ↓
                                    Track Effectiveness
                                              ↓
                                    Update Rules (Learning)
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of triggers that can cause layout adjustments."""
    BEHAVIOR_PATTERN = "behavior_pattern"      # User behavior indicates need
    CONTEXT_CHANGE = "context_change"          # Device/environment changed
    ERROR_RATE = "error_rate"                  # Too many errors
    ENGAGEMENT_DROP = "engagement_drop"        # User disengaging
    MANUAL_OVERRIDE = "manual_override"        # User manually changed
    TIME_BASED = "time_based"                  # Scheduled adjustment
    EXPERIMENT = "experiment"                  # A/B test variant


class AdjustmentStrategy(Enum):
    """Strategies for applying layout adjustments."""
    IMMEDIATE = "immediate"        # Apply instantly
    ANIMATED = "animated"          # Smooth transition
    NEXT_SESSION = "next_session"  # Apply on next login
    GRADUAL = "gradual"            # Progressive over time


@dataclass
class LayoutRule:
    """A rule that triggers layout adjustments."""
    rule_id: str
    rule_name: str
    description: str
    
    # Trigger conditions
    trigger_type: str
    trigger_conditions: Dict[str, Any]
    
    # Actions to take
    layout_changes: Dict[str, Any]
    
    # Execution
    strategy: str
    priority: int  # Higher = more important
    
    # Metadata
    enabled: bool = True
    created_at: Optional[str] = None
    last_triggered: Optional[str] = None
    trigger_count: int = 0


@dataclass
class LayoutAdjustment:
    """A specific layout adjustment to be applied."""
    adjustment_id: str
    user_id: str
    timestamp: str
    
    # What triggered this
    triggered_by: str
    trigger_details: Dict[str, Any]
    
    # What to change
    from_layout: Dict[str, Any]
    to_layout: Dict[str, Any]
    changes: List[Dict[str, str]]  # List of specific changes
    
    # How to apply
    strategy: str
    animation_duration_ms: int = 300
    
    # Tracking
    applied: bool = False
    applied_at: Optional[str] = None
    user_accepted: Optional[bool] = None
    effectiveness_score: Optional[float] = None


class DynamicLayoutAdjuster:
    """
    Dynamic Layout Adjuster that automatically optimizes capsule layouts.
    
    Monitors user behavior and context to trigger layout adjustments that
    improve usability, engagement, and task completion.
    
    Key Features:
    - Rule-based trigger system
    - Smooth animated transitions
    - User override with preference learning
    - Effectiveness tracking and optimization
    """
    
    def __init__(self):
        """Initialize the Dynamic Layout Adjuster."""
        self.rules: Dict[str, LayoutRule] = {}
        self.adjustments: List[LayoutAdjustment] = []
        self.user_overrides: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info("DynamicLayoutAdjuster initialized with default rules")
    
    def _initialize_default_rules(self):
        """Initialize default layout adjustment rules."""
        
        # Rule 1: Frequent expanders want more space
        self.add_rule(LayoutRule(
            rule_id="frequent_expand",
            rule_name="Frequent Expanders",
            description="Users who frequently expand capsules prefer spacious layouts",
            trigger_type=TriggerType.BEHAVIOR_PATTERN.value,
            trigger_conditions={
                "expand_rate": {"min": 0.6},  # 60%+ of interactions are expands
                "min_interactions": 20
            },
            layout_changes={
                "layout_type": "spacious",
                "card_size": "large",
                "layout_density": "comfortable"
            },
            strategy=AdjustmentStrategy.ANIMATED.value,
            priority=8
        ))
        
        # Rule 2: Power users want compact
        self.add_rule(LayoutRule(
            rule_id="power_user_compact",
            rule_name="Power User Compact",
            description="Power users prefer compact, information-dense layouts",
            trigger_type=TriggerType.BEHAVIOR_PATTERN.value,
            trigger_conditions={
                "expertise_level": "power_user",
                "avg_interaction_duration_ms": {"max": 1000},  # Fast interactions
                "error_rate": {"max": 0.05}
            },
            layout_changes={
                "layout_type": "compact",
                "card_size": "small",
                "layout_density": "compact",
                "grid_columns": 5
            },
            strategy=AdjustmentStrategy.ANIMATED.value,
            priority=9
        ))
        
        # Rule 3: Mobile device optimization
        self.add_rule(LayoutRule(
            rule_id="mobile_optimization",
            rule_name="Mobile Device Optimization",
            description="Optimize layout for mobile devices",
            trigger_type=TriggerType.CONTEXT_CHANGE.value,
            trigger_conditions={
                "device_type": "mobile",
                "screen_width": {"max": 768}
            },
            layout_changes={
                "layout_type": "list",
                "card_size": "large",
                "grid_columns": 1,
                "show_details": False
            },
            strategy=AdjustmentStrategy.IMMEDIATE.value,
            priority=10  # Highest priority
        ))
        
        # Rule 4: High error rate → simplify
        self.add_rule(LayoutRule(
            rule_id="high_error_simplify",
            rule_name="High Error Rate Simplification",
            description="Simplify layout when user makes many errors",
            trigger_type=TriggerType.ERROR_RATE.value,
            trigger_conditions={
                "error_rate": {"min": 0.15},  # 15%+ error rate
                "recent_errors": {"min": 5, "window_minutes": 10}
            },
            layout_changes={
                "data_density": "low",
                "show_details": False,
                "confirmation_dialogs": True,
                "animation_speed": "slow"
            },
            strategy=AdjustmentStrategy.ANIMATED.value,
            priority=9
        ))
        
        # Rule 5: Engagement drop → re-engage
        self.add_rule(LayoutRule(
            rule_id="engagement_drop",
            rule_name="Re-engagement on Drop",
            description="Adjust layout when user engagement drops",
            trigger_type=TriggerType.ENGAGEMENT_DROP.value,
            trigger_conditions={
                "engagement_score_drop": {"min": 0.2},  # 20% drop
                "session_duration_drop": {"min": 0.3}   # 30% shorter sessions
            },
            layout_changes={
                "layout_type": "card",  # More visual
                "show_icons": True,
                "animation_speed": "normal",
                "haptic_feedback": True
            },
            strategy=AdjustmentStrategy.NEXT_SESSION.value,
            priority=6
        ))
        
        # Rule 6: Tablet optimization
        self.add_rule(LayoutRule(
            rule_id="tablet_optimization",
            rule_name="Tablet Device Optimization",
            description="Optimize layout for tablet devices",
            trigger_type=TriggerType.CONTEXT_CHANGE.value,
            trigger_conditions={
                "device_type": "tablet",
                "screen_width": {"min": 768, "max": 1024}
            },
            layout_changes={
                "layout_type": "grid",
                "grid_columns": 3,
                "card_size": "medium"
            },
            strategy=AdjustmentStrategy.IMMEDIATE.value,
            priority=10
        ))
    
    def add_rule(self, rule: LayoutRule):
        """Add a layout adjustment rule."""
        if not rule.created_at:
            rule.created_at = datetime.utcnow().isoformat()
        
        self.rules[rule.rule_id] = rule
        logger.info(f"Added layout rule: {rule.rule_name}")
    
    async def evaluate_triggers(
        self,
        user_id: str,
        behavioral_vector: Dict[str, Any],
        current_layout: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[LayoutAdjustment]:
        """
        Evaluate all rules and generate layout adjustments.
        
        Args:
            user_id: User identifier
            behavioral_vector: User's behavioral vector
            current_layout: Current layout configuration
            context: Current context (device, network, etc.)
        
        Returns:
            List of layout adjustments to apply
        """
        adjustments = []
        
        # Check user overrides first
        if user_id in self.user_overrides:
            logger.info(f"User {user_id} has manual overrides, skipping auto-adjustments")
            return []
        
        # Evaluate each rule
        for rule in sorted(self.rules.values(), key=lambda r: r.priority, reverse=True):
            if not rule.enabled:
                continue
            
            # Check if rule conditions are met
            if self._check_rule_conditions(rule, behavioral_vector, context):
                # Generate adjustment
                adjustment = self._generate_adjustment(
                    user_id,
                    rule,
                    current_layout,
                    behavioral_vector,
                    context
                )
                
                if adjustment:
                    adjustments.append(adjustment)
                    rule.last_triggered = datetime.utcnow().isoformat()
                    rule.trigger_count += 1
                    
                    logger.info(
                        f"Rule '{rule.rule_name}' triggered for user {user_id}"
                    )
        
        return adjustments
    
    def _check_rule_conditions(
        self,
        rule: LayoutRule,
        behavioral_vector: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check if rule conditions are satisfied."""
        conditions = rule.trigger_conditions
        
        # Behavior pattern triggers
        if rule.trigger_type == TriggerType.BEHAVIOR_PATTERN.value:
            return self._check_behavior_conditions(conditions, behavioral_vector)
        
        # Context change triggers
        elif rule.trigger_type == TriggerType.CONTEXT_CHANGE.value:
            return self._check_context_conditions(conditions, context)
        
        # Error rate triggers
        elif rule.trigger_type == TriggerType.ERROR_RATE.value:
            return self._check_error_conditions(conditions, behavioral_vector)
        
        # Engagement drop triggers
        elif rule.trigger_type == TriggerType.ENGAGEMENT_DROP.value:
            return self._check_engagement_conditions(conditions, behavioral_vector)
        
        return False
    
    def _check_behavior_conditions(
        self,
        conditions: Dict[str, Any],
        behavioral_vector: Dict[str, Any]
    ) -> bool:
        """Check behavior pattern conditions."""
        # Check expertise level
        if "expertise_level" in conditions:
            if behavioral_vector.get("expertise_level") != conditions["expertise_level"]:
                return False
        
        # Check expand rate
        if "expand_rate" in conditions:
            usage_patterns = behavioral_vector.get("usage_patterns", {})
            action_freq = usage_patterns.get("action_frequency", {})
            total_actions = sum(action_freq.values())
            expand_count = action_freq.get("expand", 0)
            expand_rate = expand_count / total_actions if total_actions > 0 else 0
            
            min_rate = conditions["expand_rate"].get("min", 0)
            if expand_rate < min_rate:
                return False
        
        # Check minimum interactions
        if "min_interactions" in conditions:
            total = behavioral_vector.get("total_interactions", 0)
            if total < conditions["min_interactions"]:
                return False
        
        # Check interaction duration
        if "avg_interaction_duration_ms" in conditions:
            proficiency = behavioral_vector.get("proficiency_indicators", {})
            duration = proficiency.get("avg_interaction_duration_ms", 0)
            
            if "min" in conditions["avg_interaction_duration_ms"]:
                if duration < conditions["avg_interaction_duration_ms"]["min"]:
                    return False
            if "max" in conditions["avg_interaction_duration_ms"]:
                if duration > conditions["avg_interaction_duration_ms"]["max"]:
                    return False
        
        # Check error rate
        if "error_rate" in conditions:
            proficiency = behavioral_vector.get("proficiency_indicators", {})
            error_rate = proficiency.get("error_rate", 0)
            
            if "min" in conditions["error_rate"]:
                if error_rate < conditions["error_rate"]["min"]:
                    return False
            if "max" in conditions["error_rate"]:
                if error_rate > conditions["error_rate"]["max"]:
                    return False
        
        return True
    
    def _check_context_conditions(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check context change conditions."""
        # Check device type
        if "device_type" in conditions:
            if context.get("device_type") != conditions["device_type"]:
                return False
        
        # Check screen width
        if "screen_width" in conditions:
            width = context.get("screen_width", 1920)
            
            if "min" in conditions["screen_width"]:
                if width < conditions["screen_width"]["min"]:
                    return False
            if "max" in conditions["screen_width"]:
                if width > conditions["screen_width"]["max"]:
                    return False
        
        return True
    
    def _check_error_conditions(
        self,
        conditions: Dict[str, Any],
        behavioral_vector: Dict[str, Any]
    ) -> bool:
        """Check error rate conditions."""
        proficiency = behavioral_vector.get("proficiency_indicators", {})
        error_rate = proficiency.get("error_rate", 0)
        
        if "error_rate" in conditions:
            if "min" in conditions["error_rate"]:
                if error_rate < conditions["error_rate"]["min"]:
                    return False
        
        # TODO: Check recent errors in time window
        
        return True
    
    def _check_engagement_conditions(
        self,
        conditions: Dict[str, Any],
        behavioral_vector: Dict[str, Any]
    ) -> bool:
        """Check engagement drop conditions."""
        # TODO: Implement engagement drop detection
        # Requires historical engagement data
        return False
    
    def _generate_adjustment(
        self,
        user_id: str,
        rule: LayoutRule,
        current_layout: Dict[str, Any],
        behavioral_vector: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[LayoutAdjustment]:
        """Generate a layout adjustment from a triggered rule."""
        # Build new layout by applying rule changes
        new_layout = current_layout.copy()
        changes = []
        
        for key, value in rule.layout_changes.items():
            if key in new_layout and new_layout[key] != value:
                changes.append({
                    "property": key,
                    "from": str(new_layout[key]),
                    "to": str(value)
                })
                new_layout[key] = value
        
        if not changes:
            return None  # No actual changes needed
        
        adjustment = LayoutAdjustment(
            adjustment_id=f"adj_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            triggered_by=rule.rule_name,
            trigger_details={
                "rule_id": rule.rule_id,
                "trigger_type": rule.trigger_type,
                "priority": rule.priority
            },
            from_layout=current_layout,
            to_layout=new_layout,
            changes=changes,
            strategy=rule.strategy,
            animation_duration_ms=self._get_animation_duration(rule.strategy)
        )
        
        return adjustment
    
    def _get_animation_duration(self, strategy: str) -> int:
        """Get animation duration for strategy."""
        durations = {
            AdjustmentStrategy.IMMEDIATE.value: 0,
            AdjustmentStrategy.ANIMATED.value: 300,
            AdjustmentStrategy.GRADUAL.value: 1000,
            AdjustmentStrategy.NEXT_SESSION.value: 0
        }
        return durations.get(strategy, 300)
    
    async def apply_adjustment(
        self,
        adjustment: LayoutAdjustment
    ) -> bool:
        """
        Apply a layout adjustment.
        
        Args:
            adjustment: The adjustment to apply
        
        Returns:
            True if successfully applied
        """
        logger.info(
            f"Applying layout adjustment for user {adjustment.user_id}: "
            f"{len(adjustment.changes)} changes"
        )
        
        # Mark as applied
        adjustment.applied = True
        adjustment.applied_at = datetime.utcnow().isoformat()
        
        # Store adjustment
        self.adjustments.append(adjustment)
        
        # TODO: Send adjustment to frontend via WebSocket
        # await self._send_to_frontend(adjustment)
        
        return True
    
    async def record_user_override(
        self,
        user_id: str,
        overridden_property: str,
        original_value: Any,
        user_value: Any
    ):
        """
        Record when a user manually overrides an automatic adjustment.
        
        This helps us learn user preferences and avoid unwanted adjustments.
        """
        if user_id not in self.user_overrides:
            self.user_overrides[user_id] = {}
        
        self.user_overrides[user_id][overridden_property] = {
            "original_value": original_value,
            "user_value": user_value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"User {user_id} overrode {overridden_property}: "
            f"{original_value} → {user_value}"
        )
    
    async def track_effectiveness(
        self,
        adjustment_id: str,
        engagement_before: float,
        engagement_after: float,
        user_accepted: bool
    ):
        """
        Track the effectiveness of a layout adjustment.
        
        Args:
            adjustment_id: Adjustment identifier
            engagement_before: Engagement score before adjustment
            engagement_after: Engagement score after adjustment
            user_accepted: Whether user kept the adjustment
        """
        # Find adjustment
        adjustment = next(
            (a for a in self.adjustments if a.adjustment_id == adjustment_id),
            None
        )
        
        if not adjustment:
            return
        
        # Calculate effectiveness
        improvement = engagement_after - engagement_before
        effectiveness = improvement / engagement_before if engagement_before > 0 else 0
        
        adjustment.user_accepted = user_accepted
        adjustment.effectiveness_score = effectiveness
        
        logger.info(
            f"Adjustment {adjustment_id} effectiveness: {effectiveness:.2%} "
            f"(accepted: {user_accepted})"
        )
        
        # If adjustment was rejected, disable the rule temporarily
        if not user_accepted and effectiveness < -0.1:
            rule_id = adjustment.trigger_details.get("rule_id")
            if rule_id in self.rules:
                logger.warning(f"Disabling rule {rule_id} due to negative feedback")
                # TODO: Implement adaptive rule disabling
    
    def get_adjustment_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get adjustment history."""
        adjustments = self.adjustments
        
        if user_id:
            adjustments = [a for a in adjustments if a.user_id == user_id]
        
        return [asdict(a) for a in adjustments[-limit:]]


# Singleton instance
dynamic_layout_adjuster = DynamicLayoutAdjuster()
