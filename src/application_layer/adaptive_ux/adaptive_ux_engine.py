"""
Adaptive UX Engine for Dynamic Capsule Personalization.

This module implements the Adaptive UX Engine that dynamically reconfigures
capsule layouts, data density, and interaction patterns based on user behavioral
vectors. Week 10 deliverable.

Features:
- Dynamic capsule layout adjustments
- Data density tuning (novice → power user)
- Action priority reweighting
- Context-aware UX adaptation
- A/B testing integration
- Real-time UX optimization
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LayoutType(Enum):
    """Capsule layout types."""
    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"
    GRID = "grid"
    LIST = "list"
    CARD = "card"


class DataDensity(Enum):
    """Data density levels."""
    MINIMAL = "minimal"      # Novice users
    LOW = "low"              # Intermediate users
    MEDIUM = "medium"        # Proficient users
    HIGH = "high"            # Advanced users
    MAXIMUM = "maximum"      # Power users


class AnimationSpeed(Enum):
    """Animation speed preferences."""
    NONE = "none"
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


@dataclass
class UXConfiguration:
    """UX configuration for a user."""
    user_id: str
    generated_at: str
    
    # Layout configuration
    layout_type: str
    layout_density: str
    grid_columns: int
    card_size: str  # small, medium, large
    
    # Data display
    data_density: str
    show_details: bool
    show_metadata: bool
    show_timestamps: bool
    show_icons: bool
    
    # Interaction
    animation_speed: str
    haptic_feedback: bool
    sound_effects: bool
    confirmation_dialogs: bool
    
    # Action priorities
    primary_actions: List[str]
    secondary_actions: List[str]
    hidden_actions: List[str]
    
    # Capsule-specific
    capsule_type_configs: Dict[str, Dict[str, Any]]
    
    # A/B testing
    experiment_id: Optional[str] = None
    variant: Optional[str] = None
    
    # Metadata
    confidence_score: float = 1.0
    last_updated: Optional[str] = None


@dataclass
class UXAdjustment:
    """A specific UX adjustment to apply."""
    adjustment_id: str
    user_id: str
    timestamp: str
    
    # What to adjust
    target_component: str  # layout, density, actions, etc.
    adjustment_type: str   # increase, decrease, enable, disable, reorder
    
    # Adjustment details
    from_value: Any
    to_value: Any
    reason: str
    
    # Context
    triggered_by: str  # bv_update, user_feedback, experiment, manual
    confidence: float


class AdaptiveUXEngine:
    """
    Adaptive UX Engine that personalizes capsule interfaces based on user behavior.
    
    Analyzes behavioral vectors and dynamically adjusts:
    - Layout and spacing
    - Data density and detail levels
    - Action priorities and visibility
    - Animation and interaction patterns
    """
    
    def __init__(self):
        """Initialize the Adaptive UX Engine."""
        self.adjustment_history: List[UXAdjustment] = []
        self.active_experiments: Dict[str, Dict[str, Any]] = {}
        logger.info("AdaptiveUXEngine initialized")
    
    async def generate_ux_config(
        self,
        user_id: str,
        behavioral_vector: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> UXConfiguration:
        """
        Generate personalized UX configuration from behavioral vector.
        
        Args:
            user_id: User identifier
            behavioral_vector: User's behavioral vector
            context: Optional context (device, time, location)
        
        Returns:
            UXConfiguration tailored to the user
        """
        logger.info(f"Generating UX config for user {user_id}")
        
        # Extract key metrics from BV
        expertise_level = behavioral_vector.get("expertise_level", "intermediate")
        preferences = behavioral_vector.get("user_preferences", {})
        proficiency = behavioral_vector.get("proficiency_indicators", {})
        usage_patterns = behavioral_vector.get("usage_patterns", {})
        
        # Determine layout based on expertise
        layout_type = self._determine_layout(expertise_level, preferences)
        
        # Determine data density
        data_density = self._determine_data_density(expertise_level, proficiency)
        
        # Determine animation speed
        animation_speed = self._determine_animation_speed(expertise_level, proficiency)
        
        # Prioritize actions based on usage patterns
        action_priorities = self._prioritize_actions(usage_patterns, proficiency)
        
        # Generate capsule-specific configs
        capsule_configs = self._generate_capsule_configs(
            expertise_level,
            usage_patterns
        )
        
        # Check if user is in an A/B test
        experiment_id, variant = self._check_experiments(user_id)
        
        config = UXConfiguration(
            user_id=user_id,
            generated_at=datetime.utcnow().isoformat(),
            layout_type=layout_type,
            layout_density=self._get_layout_density(expertise_level),
            grid_columns=self._get_grid_columns(expertise_level),
            card_size=self._get_card_size(expertise_level),
            data_density=data_density,
            show_details=(expertise_level in ["advanced", "power_user"]),
            show_metadata=(expertise_level in ["proficient", "advanced", "power_user"]),
            show_timestamps=(expertise_level != "novice"),
            show_icons=True,
            animation_speed=animation_speed,
            haptic_feedback=(expertise_level != "power_user"),
            sound_effects=(expertise_level == "novice"),
            confirmation_dialogs=(expertise_level in ["novice", "intermediate"]),
            primary_actions=action_priorities["primary"],
            secondary_actions=action_priorities["secondary"],
            hidden_actions=action_priorities["hidden"],
            capsule_type_configs=capsule_configs,
            experiment_id=experiment_id,
            variant=variant,
            confidence_score=self._calculate_confidence(behavioral_vector),
            last_updated=datetime.utcnow().isoformat()
        )
        
        logger.info(
            f"Generated UX config for {user_id}: "
            f"layout={layout_type}, density={data_density}, "
            f"expertise={expertise_level}"
        )
        
        return config
    
    def _determine_layout(
        self,
        expertise_level: str,
        preferences: Dict[str, Any]
    ) -> str:
        """Determine optimal layout type."""
        # Check explicit preference first
        if "layout_preference" in preferences:
            return preferences["layout_preference"]
        
        # Default based on expertise
        layout_map = {
            "novice": LayoutType.LIST.value,
            "intermediate": LayoutType.CARD.value,
            "proficient": LayoutType.GRID.value,
            "advanced": LayoutType.COMPACT.value,
            "power_user": LayoutType.COMPACT.value
        }
        
        return layout_map.get(expertise_level, LayoutType.CARD.value)
    
    def _determine_data_density(
        self,
        expertise_level: str,
        proficiency: Dict[str, float]
    ) -> str:
        """Determine optimal data density."""
        density_map = {
            "novice": DataDensity.MINIMAL.value,
            "intermediate": DataDensity.LOW.value,
            "proficient": DataDensity.MEDIUM.value,
            "advanced": DataDensity.HIGH.value,
            "power_user": DataDensity.MAXIMUM.value
        }
        
        base_density = density_map.get(expertise_level, DataDensity.MEDIUM.value)
        
        # Adjust based on error rate
        error_rate = proficiency.get("error_rate", 0.1)
        if error_rate > 0.15:
            # High error rate → reduce density
            density_levels = list(DataDensity)
            current_idx = density_levels.index(DataDensity(base_density))
            if current_idx > 0:
                return density_levels[current_idx - 1].value
        
        return base_density
    
    def _determine_animation_speed(
        self,
        expertise_level: str,
        proficiency: Dict[str, float]
    ) -> str:
        """Determine optimal animation speed."""
        # Power users prefer minimal animations
        if expertise_level == "power_user":
            return AnimationSpeed.FAST.value
        
        # Novices benefit from slower, clearer animations
        if expertise_level == "novice":
            return AnimationSpeed.SLOW.value
        
        return AnimationSpeed.NORMAL.value
    
    def _prioritize_actions(
        self,
        usage_patterns: Dict[str, Any],
        proficiency: Dict[str, float]
    ) -> Dict[str, List[str]]:
        """Prioritize actions based on usage patterns."""
        # Get action frequency from usage patterns
        action_freq = usage_patterns.get("action_frequency", {})
        
        # Sort actions by frequency
        sorted_actions = sorted(
            action_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Determine thresholds based on proficiency
        completion_rate = proficiency.get("completion_rate", 0.5)
        
        if completion_rate > 0.8:
            # High proficiency → show more actions
            primary_count = 5
            secondary_count = 5
        elif completion_rate > 0.5:
            # Medium proficiency → balanced
            primary_count = 3
            secondary_count = 4
        else:
            # Low proficiency → fewer actions
            primary_count = 2
            secondary_count = 3
        
        primary_actions = [a[0] for a in sorted_actions[:primary_count]]
        secondary_actions = [a[0] for a in sorted_actions[primary_count:primary_count+secondary_count]]
        hidden_actions = [a[0] for a in sorted_actions[primary_count+secondary_count:]]
        
        return {
            "primary": primary_actions,
            "secondary": secondary_actions,
            "hidden": hidden_actions
        }
    
    def _generate_capsule_configs(
        self,
        expertise_level: str,
        usage_patterns: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Generate capsule-type-specific configurations."""
        capsule_type_dist = usage_patterns.get("capsule_type_distribution", {})
        
        configs = {}
        
        # Configure each capsule type based on usage
        for capsule_type, frequency in capsule_type_dist.items():
            if frequency > 0.3:
                # Frequently used → optimize for speed
                configs[capsule_type] = {
                    "expand_on_hover": (expertise_level in ["advanced", "power_user"]),
                    "auto_collapse": False,
                    "show_quick_actions": True,
                    "enable_keyboard_shortcuts": (expertise_level in ["proficient", "advanced", "power_user"])
                }
            elif frequency > 0.1:
                # Moderately used → balanced
                configs[capsule_type] = {
                    "expand_on_hover": False,
                    "auto_collapse": True,
                    "show_quick_actions": True,
                    "enable_keyboard_shortcuts": False
                }
            else:
                # Rarely used → helpful
                configs[capsule_type] = {
                    "expand_on_hover": False,
                    "auto_collapse": True,
                    "show_quick_actions": False,
                    "enable_keyboard_shortcuts": False,
                    "show_help_text": True
                }
        
        return configs
    
    def _get_layout_density(self, expertise_level: str) -> str:
        """Get layout density (spacing)."""
        density_map = {
            "novice": "spacious",
            "intermediate": "comfortable",
            "proficient": "comfortable",
            "advanced": "compact",
            "power_user": "compact"
        }
        return density_map.get(expertise_level, "comfortable")
    
    def _get_grid_columns(self, expertise_level: str) -> int:
        """Get number of grid columns."""
        columns_map = {
            "novice": 1,
            "intermediate": 2,
            "proficient": 3,
            "advanced": 4,
            "power_user": 5
        }
        return columns_map.get(expertise_level, 3)
    
    def _get_card_size(self, expertise_level: str) -> str:
        """Get card size."""
        size_map = {
            "novice": "large",
            "intermediate": "medium",
            "proficient": "medium",
            "advanced": "small",
            "power_user": "small"
        }
        return size_map.get(expertise_level, "medium")
    
    def _check_experiments(self, user_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Check if user is in an active A/B test."""
        # TODO: Implement actual experiment assignment
        return None, None
    
    def _calculate_confidence(self, behavioral_vector: Dict[str, Any]) -> float:
        """Calculate confidence score for the UX configuration."""
        total_interactions = behavioral_vector.get("total_interactions", 0)
        
        # Confidence increases with more data
        if total_interactions < 10:
            return 0.3
        elif total_interactions < 50:
            return 0.5
        elif total_interactions < 100:
            return 0.7
        elif total_interactions < 500:
            return 0.85
        else:
            return 0.95
    
    async def apply_ux_adjustment(
        self,
        user_id: str,
        current_config: UXConfiguration,
        adjustment: UXAdjustment
    ) -> UXConfiguration:
        """
        Apply a specific UX adjustment to the current configuration.
        
        Args:
            user_id: User identifier
            current_config: Current UX configuration
            adjustment: Adjustment to apply
        
        Returns:
            Updated UX configuration
        """
        logger.info(
            f"Applying UX adjustment for {user_id}: "
            f"{adjustment.target_component} {adjustment.adjustment_type}"
        )
        
        # Clone current config
        updated_config = UXConfiguration(**asdict(current_config))
        
        # Apply adjustment based on target
        if adjustment.target_component == "data_density":
            updated_config.data_density = adjustment.to_value
        elif adjustment.target_component == "layout_type":
            updated_config.layout_type = adjustment.to_value
        elif adjustment.target_component == "animation_speed":
            updated_config.animation_speed = adjustment.to_value
        elif adjustment.target_component == "primary_actions":
            updated_config.primary_actions = adjustment.to_value
        
        updated_config.last_updated = datetime.utcnow().isoformat()
        
        # Record adjustment
        self.adjustment_history.append(adjustment)
        
        return updated_config
    
    async def optimize_for_context(
        self,
        config: UXConfiguration,
        context: Dict[str, Any]
    ) -> UXConfiguration:
        """
        Optimize UX configuration for specific context.
        
        Context can include:
        - Device type (mobile, tablet, desktop)
        - Screen size
        - Time of day
        - Network conditions
        - Battery level
        
        Args:
            config: Base UX configuration
            context: Context information
        
        Returns:
            Context-optimized UX configuration
        """
        optimized_config = UXConfiguration(**asdict(config))
        
        # Device-specific optimizations
        device_type = context.get("device_type", "web")
        if device_type == "mobile":
            # Mobile → larger touch targets, simpler layout
            optimized_config.card_size = "large"
            optimized_config.grid_columns = min(optimized_config.grid_columns, 2)
        
        # Network-specific optimizations
        network_speed = context.get("network_speed", "fast")
        if network_speed == "slow":
            # Slow network → disable animations, reduce data
            optimized_config.animation_speed = AnimationSpeed.NONE.value
            optimized_config.show_metadata = False
        
        # Battery-specific optimizations
        battery_level = context.get("battery_level", 100)
        if battery_level < 20:
            # Low battery → reduce animations and effects
            optimized_config.animation_speed = AnimationSpeed.NONE.value
            optimized_config.haptic_feedback = False
            optimized_config.sound_effects = False
        
        return optimized_config
    
    def get_adjustment_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get adjustment history, optionally filtered by user."""
        history = self.adjustment_history
        
        if user_id:
            history = [a for a in history if a.user_id == user_id]
        
        return [asdict(a) for a in history[-limit:]]


# Singleton instance
adaptive_ux_engine = AdaptiveUXEngine()
