"""
Overseer Capsule Orchestrator for Personalized Launchpad.

This module orchestrates capsule visibility, priority, and lifecycle based on
user behavior, role, and context. Week 12 deliverable.

Key Concepts:
- User Launchpad: Personalized dashboard showing relevant capsules
- Role-Based Visibility: Different roles see different capsules
- Contextual Spawning: Spawn capsules based on user context
- Lifecycle Management: Create, update, archive capsules automatically

Architecture:
  User Context → Orchestrator → Capsule Selection → Launchpad
                      ↓
              Lifecycle Management
                      ↓
              Spawn/Archive Capsules
"""

import logging
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CapsuleState(Enum):
    """Lifecycle states for capsules."""
    DRAFT = "draft"
    ACTIVE = "active"
    SNOOZED = "snoozed"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class VisibilityRule(Enum):
    """Rules for capsule visibility."""
    ALWAYS_VISIBLE = "always_visible"
    ROLE_BASED = "role_based"
    CONTEXT_BASED = "context_based"
    BEHAVIOR_BASED = "behavior_based"
    TIME_BASED = "time_based"


@dataclass
class Capsule:
    """A capsule in the system."""
    capsule_id: str
    capsule_type: str
    title: str
    description: str
    
    # State
    state: str  # CapsuleState value
    priority: int  # 1-10, higher = more important
    
    # Visibility
    visibility_rule: str  # VisibilityRule value
    visible_to_roles: List[str]
    visible_to_users: Optional[List[str]] = None
    
    # Context
    context_tags: List[str] = field(default_factory=list)
    
    # Lifecycle
    created_at: str = ""
    updated_at: str = ""
    completed_at: Optional[str] = None
    archived_at: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserLaunchpad:
    """A user's personalized launchpad."""
    user_id: str
    user_role: str
    
    # Capsules
    visible_capsules: List[str]  # Capsule IDs
    pinned_capsules: List[str]
    hidden_capsules: List[str]
    
    # Layout (from Week 10)
    layout_config: Dict[str, Any]
    
    # Generated
    generated_at: str
    expires_at: str


@dataclass
class SpawnRule:
    """Rule for automatically spawning capsules."""
    rule_id: str
    rule_name: str
    description: str
    
    # Trigger conditions
    trigger_type: str  # event, schedule, behavior
    trigger_conditions: Dict[str, Any]
    
    # Capsule template
    capsule_template: Dict[str, Any]
    
    # Metadata
    enabled: bool = True
    spawn_count: int = 0
    last_spawned_at: Optional[str] = None


class CapsuleOrchestrator:
    """
    Overseer Capsule Orchestrator that manages personalized launchpads.
    
    Responsibilities:
    - Determine which capsules a user should see
    - Calculate capsule priority based on context
    - Spawn new capsules based on rules
    - Manage capsule lifecycle (create → complete → archive)
    - Generate personalized launchpad
    
    Integrates with:
    - Week 9: Behavioral tracking (user patterns)
    - Week 10: Adaptive UX (layout configuration)
    - Week 11: ASAL (global policies)
    """
    
    def __init__(self):
        """Initialize the Capsule Orchestrator."""
        self.capsules: Dict[str, Capsule] = {}
        self.spawn_rules: Dict[str, SpawnRule] = {}
        self.user_launchpads: Dict[str, UserLaunchpad] = {}
        
        # Role definitions
        self.role_hierarchy = {
            "admin": 100,
            "manager": 80,
            "operator": 60,
            "analyst": 40,
            "viewer": 20
        }
        
        logger.info("CapsuleOrchestrator initialized")
    
    async def generate_launchpad(
        self,
        user_id: str,
        user_role: str,
        behavioral_vector: Dict[str, Any],
        context: Dict[str, Any],
        layout_config: Optional[Dict[str, Any]] = None
    ) -> UserLaunchpad:
        """
        Generate a personalized launchpad for a user.
        
        Args:
            user_id: User identifier
            user_role: User's role
            behavioral_vector: User's BV (from Week 9)
            context: Current context (device, time, location, etc.)
            layout_config: UX configuration (from Week 10)
        
        Returns:
            UserLaunchpad with personalized capsule selection
        """
        # Step 1: Get all active capsules
        active_capsules = [
            c for c in self.capsules.values()
            if c.state == CapsuleState.ACTIVE.value
        ]
        
        # Step 2: Filter by visibility rules
        visible_capsules = await self._filter_by_visibility(
            capsules=active_capsules,
            user_id=user_id,
            user_role=user_role,
            context=context
        )
        
        # Step 3: Calculate priority for each capsule
        prioritized_capsules = await self._calculate_priorities(
            capsules=visible_capsules,
            user_id=user_id,
            behavioral_vector=behavioral_vector,
            context=context
        )
        
        # Step 4: Apply behavioral preferences
        personalized_capsules = await self._apply_behavioral_preferences(
            capsules=prioritized_capsules,
            behavioral_vector=behavioral_vector
        )
        
        # Step 5: Get user's pinned/hidden capsules
        pinned = await self._get_pinned_capsules(user_id)
        hidden = await self._get_hidden_capsules(user_id)
        
        # Step 6: Generate launchpad
        launchpad = UserLaunchpad(
            user_id=user_id,
            user_role=user_role,
            visible_capsules=[c.capsule_id for c in personalized_capsules],
            pinned_capsules=pinned,
            hidden_capsules=hidden,
            layout_config=layout_config or {},
            generated_at=datetime.utcnow().isoformat(),
            expires_at=(datetime.utcnow() + timedelta(minutes=5)).isoformat()
        )
        
        self.user_launchpads[user_id] = launchpad
        
        logger.info(
            f"Generated launchpad for {user_id} ({user_role}): "
            f"{len(personalized_capsules)} capsules"
        )
        
        return launchpad
    
    async def _filter_by_visibility(
        self,
        capsules: List[Capsule],
        user_id: str,
        user_role: str,
        context: Dict[str, Any]
    ) -> List[Capsule]:
        """Filter capsules by visibility rules."""
        visible = []
        
        for capsule in capsules:
            rule = capsule.visibility_rule
            
            if rule == VisibilityRule.ALWAYS_VISIBLE.value:
                visible.append(capsule)
            
            elif rule == VisibilityRule.ROLE_BASED.value:
                if user_role in capsule.visible_to_roles:
                    visible.append(capsule)
            
            elif rule == VisibilityRule.CONTEXT_BASED.value:
                # Check if user's context matches capsule's context tags
                user_context_tags = context.get("tags", [])
                if any(tag in capsule.context_tags for tag in user_context_tags):
                    visible.append(capsule)
            
            elif rule == VisibilityRule.BEHAVIOR_BASED.value:
                # Would check behavioral patterns here
                visible.append(capsule)  # Simplified
            
            elif rule == VisibilityRule.TIME_BASED.value:
                # Check if current time matches capsule's time window
                current_hour = datetime.utcnow().hour
                time_window = capsule.metadata.get("time_window", [0, 23])
                if time_window[0] <= current_hour <= time_window[1]:
                    visible.append(capsule)
        
        return visible
    
    async def _calculate_priorities(
        self,
        capsules: List[Capsule],
        user_id: str,
        behavioral_vector: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Capsule]:
        """Calculate dynamic priority for each capsule."""
        prioritized = []
        
        for capsule in capsules:
            base_priority = capsule.priority
            
            # Adjust based on user expertise
            expertise = behavioral_vector.get("expertise_level", "intermediate")
            if capsule.capsule_type == "tutorial" and expertise in ["advanced", "power_user"]:
                base_priority -= 3  # Lower priority for tutorials if expert
            elif capsule.capsule_type == "advanced_feature" and expertise == "novice":
                base_priority -= 2  # Lower priority for advanced features if novice
            
            # Adjust based on engagement patterns
            engagement = behavioral_vector.get("engagement_patterns", {})
            preferred_types = engagement.get("preferred_capsule_types", [])
            if capsule.capsule_type in preferred_types:
                base_priority += 2  # Boost priority for preferred types
            
            # Adjust based on time of day
            current_hour = datetime.utcnow().hour
            if capsule.capsule_type == "alert" and 9 <= current_hour <= 17:
                base_priority += 1  # Boost alerts during work hours
            
            # Clamp priority to 1-10
            capsule.priority = max(1, min(10, base_priority))
            prioritized.append(capsule)
        
        # Sort by priority (descending)
        prioritized.sort(key=lambda c: c.priority, reverse=True)
        
        return prioritized
    
    async def _apply_behavioral_preferences(
        self,
        capsules: List[Capsule],
        behavioral_vector: Dict[str, Any]
    ) -> List[Capsule]:
        """Apply user's behavioral preferences to capsule selection."""
        # Get user's interaction history
        interaction_history = behavioral_vector.get("interaction_history", {})
        
        # Filter out capsule types user never interacts with
        ignored_types = interaction_history.get("ignored_capsule_types", [])
        filtered = [
            c for c in capsules
            if c.capsule_type not in ignored_types
        ]
        
        return filtered
    
    async def _get_pinned_capsules(self, user_id: str) -> List[str]:
        """Get user's pinned capsules."""
        # Would query database in production
        return []
    
    async def _get_hidden_capsules(self, user_id: str) -> List[str]:
        """Get user's hidden capsules."""
        # Would query database in production
        return []
    
    async def spawn_capsule(
        self,
        capsule_template: Dict[str, Any],
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Capsule:
        """
        Spawn a new capsule from a template.
        
        Args:
            capsule_template: Template defining capsule properties
            user_id: User to spawn capsule for (optional)
            context: Context for spawning (optional)
        
        Returns:
            Newly created Capsule
        """
        capsule_id = f"capsule_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(self.capsules)}"
        
        capsule = Capsule(
            capsule_id=capsule_id,
            capsule_type=capsule_template.get("capsule_type", "generic"),
            title=capsule_template.get("title", "Untitled Capsule"),
            description=capsule_template.get("description", ""),
            state=CapsuleState.ACTIVE.value,
            priority=capsule_template.get("priority", 5),
            visibility_rule=capsule_template.get("visibility_rule", VisibilityRule.ALWAYS_VISIBLE.value),
            visible_to_roles=capsule_template.get("visible_to_roles", ["admin", "manager", "operator"]),
            visible_to_users=[user_id] if user_id else None,
            context_tags=capsule_template.get("context_tags", []),
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            metadata=capsule_template.get("metadata", {})
        )
        
        self.capsules[capsule_id] = capsule
        
        logger.info(
            f"Spawned capsule {capsule_id} (type={capsule.capsule_type}, "
            f"priority={capsule.priority})"
        )
        
        return capsule
    
    async def evaluate_spawn_rules(
        self,
        user_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ):
        """
        Evaluate spawn rules and spawn capsules if conditions are met.
        
        Args:
            user_id: User identifier
            event_type: Type of event that triggered evaluation
            event_data: Event data
        """
        for rule in self.spawn_rules.values():
            if not rule.enabled:
                continue
            
            if rule.trigger_type != event_type:
                continue
            
            # Check trigger conditions
            conditions_met = await self._check_spawn_conditions(
                rule.trigger_conditions,
                event_data
            )
            
            if conditions_met:
                # Spawn capsule
                capsule = await self.spawn_capsule(
                    capsule_template=rule.capsule_template,
                    user_id=user_id,
                    context=event_data
                )
                
                # Update rule
                rule.spawn_count += 1
                rule.last_spawned_at = datetime.utcnow().isoformat()
                
                logger.info(
                    f"Rule {rule.rule_id} triggered: Spawned {capsule.capsule_id}"
                )
    
    async def _check_spawn_conditions(
        self,
        conditions: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> bool:
        """Check if spawn conditions are met."""
        for key, expected_value in conditions.items():
            actual_value = event_data.get(key)
            
            if isinstance(expected_value, dict):
                # Range check
                if "min" in expected_value and actual_value < expected_value["min"]:
                    return False
                if "max" in expected_value and actual_value > expected_value["max"]:
                    return False
            else:
                # Exact match
                if actual_value != expected_value:
                    return False
        
        return True
    
    async def update_capsule_state(
        self,
        capsule_id: str,
        new_state: str,
        user_id: Optional[str] = None
    ):
        """Update capsule lifecycle state."""
        capsule = self.capsules.get(capsule_id)
        if not capsule:
            logger.warning(f"Capsule {capsule_id} not found")
            return
        
        old_state = capsule.state
        capsule.state = new_state
        capsule.updated_at = datetime.utcnow().isoformat()
        
        if new_state == CapsuleState.COMPLETED.value:
            capsule.completed_at = datetime.utcnow().isoformat()
        elif new_state == CapsuleState.ARCHIVED.value:
            capsule.archived_at = datetime.utcnow().isoformat()
        
        logger.info(
            f"Capsule {capsule_id} state: {old_state} → {new_state} "
            f"(user={user_id})"
        )
    
    def add_spawn_rule(self, rule: SpawnRule):
        """Add a spawn rule."""
        self.spawn_rules[rule.rule_id] = rule
        logger.info(f"Added spawn rule: {rule.rule_name}")
    
    def get_capsule(self, capsule_id: str) -> Optional[Capsule]:
        """Get a specific capsule."""
        return self.capsules.get(capsule_id)
    
    def get_user_launchpad(self, user_id: str) -> Optional[UserLaunchpad]:
        """Get a user's launchpad."""
        return self.user_launchpads.get(user_id)


# Singleton instance
capsule_orchestrator = CapsuleOrchestrator()
