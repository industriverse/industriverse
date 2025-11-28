"""
Data Density Tuner for Progressive Information Disclosure.

This module dynamically adjusts the amount of information shown in capsules
based on user expertise, cognitive load, and task context. Week 10 Day 3-4 deliverable.

Key Concepts:
- 5-tier density system (minimal → maximum)
- Progressive disclosure based on engagement
- Cognitive load monitoring
- Error-rate feedback loop
- Capsule-type-specific density rules

Philosophy:
- Novices: Show only what's essential (reduce overwhelm)
- Experts: Show everything (maximize efficiency)
- Adapt: If errors increase, reduce density
- Context: Task-critical info always visible
"""

import logging
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DensityLevel(Enum):
    """Data density levels from minimal to maximum."""
    MINIMAL = 1      # Novice: Title + primary action only
    LOW = 2          # Intermediate: + status + timestamp
    MEDIUM = 3       # Proficient: + metadata + secondary actions
    HIGH = 4         # Advanced: + all details + shortcuts
    MAXIMUM = 5      # Power user: Everything, minimal chrome


class InformationPriority(Enum):
    """Priority levels for information elements."""
    CRITICAL = 1     # Always show (title, primary action)
    HIGH = 2         # Show at LOW+ density
    MEDIUM = 3       # Show at MEDIUM+ density
    LOW = 4          # Show at HIGH+ density
    OPTIONAL = 5     # Show only at MAXIMUM density


@dataclass
class InformationElement:
    """An information element that can be shown/hidden."""
    element_id: str
    element_name: str
    element_type: str  # text, icon, button, metadata, timestamp
    priority: int      # InformationPriority value
    
    # Visibility rules
    min_density_level: int  # Minimum density to show
    capsule_types: Optional[List[str]] = None  # Specific capsule types, None = all
    
    # Context
    task_critical: bool = False  # Always show if task-critical
    
    # Metadata
    avg_interaction_rate: float = 0.0  # How often users interact with this


@dataclass
class DensityConfiguration:
    """Configuration for a specific density level."""
    density_level: int
    density_name: str
    
    # What to show
    visible_elements: List[str]
    hidden_elements: List[str]
    
    # Layout adjustments
    spacing: str  # tight, normal, comfortable, spacious
    font_size: str  # small, normal, large
    icon_size: str  # small, medium, large
    
    # Interaction
    show_tooltips: bool
    show_help_text: bool
    show_keyboard_shortcuts: bool
    
    # Metadata
    target_expertise: List[str]  # User archetypes for this density


@dataclass
class DensityAdjustment:
    """A density adjustment to apply."""
    adjustment_id: str
    user_id: str
    timestamp: str
    capsule_id: Optional[str]  # None = global adjustment
    
    # Change
    from_density: int
    to_density: int
    reason: str
    
    # Elements affected
    elements_shown: List[str]
    elements_hidden: List[str]
    
    # Tracking
    applied: bool = False
    user_accepted: Optional[bool] = None
    error_rate_before: float = 0.0
    error_rate_after: Optional[float] = None


class DataDensityTuner:
    """
    Data Density Tuner that progressively discloses information.
    
    Automatically adjusts information density based on:
    - User expertise level
    - Error rate (cognitive load indicator)
    - Engagement patterns
    - Task context
    - Capsule type
    
    Philosophy: Show just enough information to be effective,
    but not so much that it overwhelms.
    """
    
    def __init__(self):
        """Initialize the Data Density Tuner."""
        self.information_elements: Dict[str, InformationElement] = {}
        self.density_configs: Dict[int, DensityConfiguration] = {}
        self.adjustments: List[DensityAdjustment] = []
        
        # Initialize default elements and configurations
        self._initialize_information_elements()
        self._initialize_density_configurations()
        
        logger.info("DataDensityTuner initialized")
    
    def _initialize_information_elements(self):
        """Define all information elements that can be shown/hidden."""
        
        # CRITICAL elements (always show)
        self.add_element(InformationElement(
            element_id="title",
            element_name="Capsule Title",
            element_type="text",
            priority=InformationPriority.CRITICAL.value,
            min_density_level=DensityLevel.MINIMAL.value,
            task_critical=True
        ))
        
        self.add_element(InformationElement(
            element_id="primary_action",
            element_name="Primary Action Button",
            element_type="button",
            priority=InformationPriority.CRITICAL.value,
            min_density_level=DensityLevel.MINIMAL.value,
            task_critical=True
        ))
        
        # HIGH priority elements (show at LOW+ density)
        self.add_element(InformationElement(
            element_id="status_indicator",
            element_name="Status Indicator",
            element_type="icon",
            priority=InformationPriority.HIGH.value,
            min_density_level=DensityLevel.LOW.value
        ))
        
        self.add_element(InformationElement(
            element_id="timestamp",
            element_name="Timestamp",
            element_type="text",
            priority=InformationPriority.HIGH.value,
            min_density_level=DensityLevel.LOW.value
        ))
        
        self.add_element(InformationElement(
            element_id="category_tag",
            element_name="Category Tag",
            element_type="text",
            priority=InformationPriority.HIGH.value,
            min_density_level=DensityLevel.LOW.value
        ))
        
        # MEDIUM priority elements (show at MEDIUM+ density)
        self.add_element(InformationElement(
            element_id="metadata_panel",
            element_name="Metadata Panel",
            element_type="metadata",
            priority=InformationPriority.MEDIUM.value,
            min_density_level=DensityLevel.MEDIUM.value
        ))
        
        self.add_element(InformationElement(
            element_id="secondary_actions",
            element_name="Secondary Action Buttons",
            element_type="button",
            priority=InformationPriority.MEDIUM.value,
            min_density_level=DensityLevel.MEDIUM.value
        ))
        
        self.add_element(InformationElement(
            element_id="description",
            element_name="Description Text",
            element_type="text",
            priority=InformationPriority.MEDIUM.value,
            min_density_level=DensityLevel.MEDIUM.value
        ))
        
        self.add_element(InformationElement(
            element_id="assignee",
            element_name="Assignee",
            element_type="text",
            priority=InformationPriority.MEDIUM.value,
            min_density_level=DensityLevel.MEDIUM.value,
            capsule_types=["task", "workflow"]
        ))
        
        # LOW priority elements (show at HIGH+ density)
        self.add_element(InformationElement(
            element_id="tags",
            element_name="Tags",
            element_type="text",
            priority=InformationPriority.LOW.value,
            min_density_level=DensityLevel.HIGH.value
        ))
        
        self.add_element(InformationElement(
            element_id="related_capsules",
            element_name="Related Capsules",
            element_type="metadata",
            priority=InformationPriority.LOW.value,
            min_density_level=DensityLevel.HIGH.value
        ))
        
        self.add_element(InformationElement(
            element_id="history",
            element_name="Change History",
            element_type="metadata",
            priority=InformationPriority.LOW.value,
            min_density_level=DensityLevel.HIGH.value
        ))
        
        self.add_element(InformationElement(
            element_id="keyboard_shortcuts",
            element_name="Keyboard Shortcuts",
            element_type="text",
            priority=InformationPriority.LOW.value,
            min_density_level=DensityLevel.HIGH.value
        ))
        
        # OPTIONAL elements (show only at MAXIMUM density)
        self.add_element(InformationElement(
            element_id="debug_info",
            element_name="Debug Information",
            element_type="metadata",
            priority=InformationPriority.OPTIONAL.value,
            min_density_level=DensityLevel.MAXIMUM.value
        ))
        
        self.add_element(InformationElement(
            element_id="api_details",
            element_name="API Details",
            element_type="metadata",
            priority=InformationPriority.OPTIONAL.value,
            min_density_level=DensityLevel.MAXIMUM.value
        ))
    
    def _initialize_density_configurations(self):
        """Define configurations for each density level."""
        
        # MINIMAL density (Novice users)
        self.add_density_config(DensityConfiguration(
            density_level=DensityLevel.MINIMAL.value,
            density_name="Minimal",
            visible_elements=["title", "primary_action"],
            hidden_elements=[
                "status_indicator", "timestamp", "category_tag",
                "metadata_panel", "secondary_actions", "description",
                "assignee", "tags", "related_capsules", "history",
                "keyboard_shortcuts", "debug_info", "api_details"
            ],
            spacing="spacious",
            font_size="large",
            icon_size="large",
            show_tooltips=True,
            show_help_text=True,
            show_keyboard_shortcuts=False,
            target_expertise=["novice"]
        ))
        
        # LOW density (Intermediate users)
        self.add_density_config(DensityConfiguration(
            density_level=DensityLevel.LOW.value,
            density_name="Low",
            visible_elements=[
                "title", "primary_action", "status_indicator",
                "timestamp", "category_tag"
            ],
            hidden_elements=[
                "metadata_panel", "secondary_actions", "description",
                "assignee", "tags", "related_capsules", "history",
                "keyboard_shortcuts", "debug_info", "api_details"
            ],
            spacing="comfortable",
            font_size="normal",
            icon_size="medium",
            show_tooltips=True,
            show_help_text=True,
            show_keyboard_shortcuts=False,
            target_expertise=["intermediate"]
        ))
        
        # MEDIUM density (Proficient users)
        self.add_density_config(DensityConfiguration(
            density_level=DensityLevel.MEDIUM.value,
            density_name="Medium",
            visible_elements=[
                "title", "primary_action", "status_indicator",
                "timestamp", "category_tag", "metadata_panel",
                "secondary_actions", "description", "assignee"
            ],
            hidden_elements=[
                "tags", "related_capsules", "history",
                "keyboard_shortcuts", "debug_info", "api_details"
            ],
            spacing="normal",
            font_size="normal",
            icon_size="medium",
            show_tooltips=False,
            show_help_text=False,
            show_keyboard_shortcuts=False,
            target_expertise=["proficient"]
        ))
        
        # HIGH density (Advanced users)
        self.add_density_config(DensityConfiguration(
            density_level=DensityLevel.HIGH.value,
            density_name="High",
            visible_elements=[
                "title", "primary_action", "status_indicator",
                "timestamp", "category_tag", "metadata_panel",
                "secondary_actions", "description", "assignee",
                "tags", "related_capsules", "history", "keyboard_shortcuts"
            ],
            hidden_elements=["debug_info", "api_details"],
            spacing="tight",
            font_size="small",
            icon_size="small",
            show_tooltips=False,
            show_help_text=False,
            show_keyboard_shortcuts=True,
            target_expertise=["advanced"]
        ))
        
        # MAXIMUM density (Power users)
        self.add_density_config(DensityConfiguration(
            density_level=DensityLevel.MAXIMUM.value,
            density_name="Maximum",
            visible_elements=[
                "title", "primary_action", "status_indicator",
                "timestamp", "category_tag", "metadata_panel",
                "secondary_actions", "description", "assignee",
                "tags", "related_capsules", "history",
                "keyboard_shortcuts", "debug_info", "api_details"
            ],
            hidden_elements=[],
            spacing="tight",
            font_size="small",
            icon_size="small",
            show_tooltips=False,
            show_help_text=False,
            show_keyboard_shortcuts=True,
            target_expertise=["power_user"]
        ))
    
    def add_element(self, element: InformationElement):
        """Add an information element."""
        self.information_elements[element.element_id] = element
    
    def add_density_config(self, config: DensityConfiguration):
        """Add a density configuration."""
        self.density_configs[config.density_level] = config
    
    async def determine_optimal_density(
        self,
        user_id: str,
        behavioral_vector: Dict[str, Any],
        capsule_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Determine optimal density level for a user.
        
        Args:
            user_id: User identifier
            behavioral_vector: User's behavioral vector
            capsule_type: Specific capsule type (optional)
            context: Additional context (optional)
        
        Returns:
            Optimal density level (1-5)
        """
        # Start with expertise-based density
        expertise_level = behavioral_vector.get("expertise_level", "intermediate")
        
        expertise_to_density = {
            "novice": DensityLevel.MINIMAL.value,
            "intermediate": DensityLevel.LOW.value,
            "proficient": DensityLevel.MEDIUM.value,
            "advanced": DensityLevel.HIGH.value,
            "power_user": DensityLevel.MAXIMUM.value
        }
        
        base_density = expertise_to_density.get(expertise_level, DensityLevel.MEDIUM.value)
        
        # Adjust based on error rate (cognitive load indicator)
        proficiency = behavioral_vector.get("proficiency_indicators", {})
        error_rate = proficiency.get("error_rate", 0.0)
        
        if error_rate > 0.15:
            # High error rate → reduce density by 2 levels
            base_density = max(DensityLevel.MINIMAL.value, base_density - 2)
            logger.info(f"Reduced density for {user_id} due to high error rate ({error_rate:.2%})")
        elif error_rate > 0.10:
            # Moderate error rate → reduce density by 1 level
            base_density = max(DensityLevel.MINIMAL.value, base_density - 1)
        
        # Adjust based on device type (from context)
        if context:
            device_type = context.get("device_type")
            if device_type == "mobile":
                # Mobile → reduce density (smaller screen)
                base_density = min(base_density, DensityLevel.LOW.value)
            elif device_type == "tablet":
                # Tablet → cap at medium
                base_density = min(base_density, DensityLevel.MEDIUM.value)
        
        # Adjust based on capsule type
        if capsule_type:
            # Alerts need minimal density (quick glance)
            if capsule_type == "alert":
                base_density = min(base_density, DensityLevel.LOW.value)
            # Workflows need more detail
            elif capsule_type == "workflow":
                base_density = max(base_density, DensityLevel.MEDIUM.value)
        
        logger.info(
            f"Determined optimal density for {user_id}: "
            f"level {base_density} ({DensityLevel(base_density).name})"
        )
        
        return base_density
    
    async def generate_density_adjustment(
        self,
        user_id: str,
        current_density: int,
        target_density: int,
        reason: str,
        capsule_id: Optional[str] = None
    ) -> DensityAdjustment:
        """Generate a density adjustment."""
        current_config = self.density_configs[current_density]
        target_config = self.density_configs[target_density]
        
        # Determine what elements change
        elements_shown = [
            e for e in target_config.visible_elements
            if e not in current_config.visible_elements
        ]
        
        elements_hidden = [
            e for e in current_config.visible_elements
            if e not in target_config.visible_elements
        ]
        
        adjustment = DensityAdjustment(
            adjustment_id=f"dens_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            capsule_id=capsule_id,
            from_density=current_density,
            to_density=target_density,
            reason=reason,
            elements_shown=elements_shown,
            elements_hidden=elements_hidden
        )
        
        return adjustment
    
    async def apply_density_adjustment(
        self,
        adjustment: DensityAdjustment
    ) -> Dict[str, Any]:
        """
        Apply a density adjustment and return configuration.
        
        Returns:
            Configuration dict to send to frontend
        """
        target_config = self.density_configs[adjustment.to_density]
        
        adjustment.applied = True
        self.adjustments.append(adjustment)
        
        logger.info(
            f"Applied density adjustment for {adjustment.user_id}: "
            f"{DensityLevel(adjustment.from_density).name} → "
            f"{DensityLevel(adjustment.to_density).name}"
        )
        
        return {
            "density_level": adjustment.to_density,
            "density_name": target_config.density_name,
            "visible_elements": target_config.visible_elements,
            "hidden_elements": target_config.hidden_elements,
            "spacing": target_config.spacing,
            "font_size": target_config.font_size,
            "icon_size": target_config.icon_size,
            "show_tooltips": target_config.show_tooltips,
            "show_help_text": target_config.show_help_text,
            "show_keyboard_shortcuts": target_config.show_keyboard_shortcuts
        }
    
    async def progressive_disclosure(
        self,
        user_id: str,
        capsule_id: str,
        current_density: int,
        engagement_duration_seconds: int
    ) -> Optional[int]:
        """
        Progressively disclose more information as user engages.
        
        If user spends significant time with a capsule, gradually
        reveal more details.
        
        Args:
            user_id: User identifier
            capsule_id: Capsule being viewed
            current_density: Current density level
            engagement_duration_seconds: How long user has been engaged
        
        Returns:
            New density level if adjustment needed, None otherwise
        """
        # Thresholds for progressive disclosure
        thresholds = {
            DensityLevel.MINIMAL.value: 10,   # 10 seconds → LOW
            DensityLevel.LOW.value: 20,       # 20 seconds → MEDIUM
            DensityLevel.MEDIUM.value: 30,    # 30 seconds → HIGH
            DensityLevel.HIGH.value: 45       # 45 seconds → MAXIMUM
        }
        
        if current_density >= DensityLevel.MAXIMUM.value:
            return None  # Already at maximum
        
        threshold = thresholds.get(current_density, 999)
        
        if engagement_duration_seconds >= threshold:
            new_density = current_density + 1
            logger.info(
                f"Progressive disclosure for {user_id} on {capsule_id}: "
                f"{DensityLevel(current_density).name} → {DensityLevel(new_density).name}"
            )
            return new_density
        
        return None
    
    def get_density_config(self, density_level: int) -> Dict[str, Any]:
        """Get configuration for a density level."""
        config = self.density_configs.get(density_level)
        if not config:
            return {}
        return asdict(config)
    
    def get_adjustment_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get density adjustment history."""
        adjustments = self.adjustments
        
        if user_id:
            adjustments = [a for a in adjustments if a.user_id == user_id]
        
        return [asdict(a) for a in adjustments[-limit:]]


# Singleton instance
data_density_tuner = DataDensityTuner()
