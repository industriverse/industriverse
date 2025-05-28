"""
Dynamic Agent Capsule UI Component

This module implements the Dynamic Agent Capsule UI component for the Workflow Automation Layer.
It provides a floating, adaptive UI node that represents live agent instances and digital twins,
offering contextual information and micro-interactions.

The component follows the "Universal Skin" concept inspired by iPhone's Dynamic Island,
allowing for decentralized access and contextual interaction with workflow agents.
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CapsuleState(Enum):
    """Enum representing possible states of a Dynamic Agent Capsule."""
    IDLE = "idle"
    ACTIVE = "active"
    WORKING = "working"
    WAITING = "waiting"
    ALERT = "alert"
    ERROR = "error"
    SUCCESS = "success"


class CapsuleSize(Enum):
    """Enum representing possible sizes of a Dynamic Agent Capsule."""
    COMPACT = "compact"  # Minimal information, icon only
    NORMAL = "normal"    # Standard size with basic info
    EXPANDED = "expanded"  # Full details and controls
    FULLSCREEN = "fullscreen"  # Maximum detail for focused interaction


@dataclass
class CapsuleAction:
    """Represents an action that can be performed on/by a capsule."""
    id: str
    name: str
    icon: str
    description: str
    enabled: bool = True
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None


@dataclass
class CapsuleAvatar:
    """Represents the visual avatar for an agent in the capsule."""
    image_url: str
    animation_states: Dict[str, str] = field(default_factory=dict)
    expression: str = "neutral"
    color_theme: Dict[str, str] = field(default_factory=dict)


@dataclass
class CapsuleContext:
    """Represents the contextual information for a capsule."""
    workflow_id: str
    task_id: Optional[str] = None
    source_context: Optional[str] = None
    trust_score: float = 0.0
    confidence_score: float = 0.0
    execution_mode: str = "reactive"
    progress: float = 0.0
    time_remaining: Optional[int] = None  # in seconds
    related_entities: List[str] = field(default_factory=list)


@dataclass
class CapsuleMetrics:
    """Represents key metrics to be displayed in the capsule."""
    primary_metric: Dict[str, Any] = field(default_factory=dict)
    secondary_metrics: List[Dict[str, Any]] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    trends: Dict[str, List[float]] = field(default_factory=dict)


class DynamicAgentCapsule:
    """
    Main class for the Dynamic Agent Capsule UI component.
    
    This component provides a floating, adaptive UI node that represents
    live agent instances and digital twins, offering contextual information
    and micro-interactions.
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        initial_state: CapsuleState = CapsuleState.IDLE,
        initial_size: CapsuleSize = CapsuleSize.NORMAL
    ):
        """
        Initialize a new Dynamic Agent Capsule.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Display name for the agent
            agent_type: Type of agent (e.g., "workflow_trigger", "human_intervention")
            initial_state: Initial state of the capsule
            initial_size: Initial size of the capsule
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.state = initial_state
        self.size = initial_size
        self.avatar = None
        self.context = None
        self.metrics = CapsuleMetrics()
        self.actions = []
        self.debug_trace = []
        self.creation_time = None
        self.last_update_time = None
        self.pin_status = {
            "is_pinned": False,
            "pin_location": None
        }
        self.ui_preferences = {
            "theme": "system",
            "animations_enabled": True,
            "notifications_enabled": True,
            "sound_enabled": False
        }
        
        logger.info(f"Created new Dynamic Agent Capsule for agent {agent_id} ({agent_name})")
    
    def set_avatar(self, avatar: CapsuleAvatar) -> None:
        """Set the avatar for this capsule."""
        self.avatar = avatar
        logger.debug(f"Avatar set for capsule {self.agent_id}")
    
    def set_context(self, context: CapsuleContext) -> None:
        """Set the context for this capsule."""
        self.context = context
        logger.debug(f"Context updated for capsule {self.agent_id}")
    
    def add_action(self, action: CapsuleAction) -> None:
        """Add an action to this capsule."""
        self.actions.append(action)
        logger.debug(f"Action {action.id} added to capsule {self.agent_id}")
    
    def remove_action(self, action_id: str) -> bool:
        """Remove an action from this capsule by ID."""
        initial_count = len(self.actions)
        self.actions = [a for a in self.actions if a.id != action_id]
        removed = len(self.actions) < initial_count
        if removed:
            logger.debug(f"Action {action_id} removed from capsule {self.agent_id}")
        return removed
    
    def update_state(self, new_state: CapsuleState) -> None:
        """Update the state of this capsule."""
        old_state = self.state
        self.state = new_state
        logger.debug(f"Capsule {self.agent_id} state changed from {old_state} to {new_state}")
        
        # Update avatar expression based on state
        if self.avatar:
            if new_state == CapsuleState.ACTIVE:
                self.avatar.expression = "attentive"
            elif new_state == CapsuleState.WORKING:
                self.avatar.expression = "focused"
            elif new_state == CapsuleState.WAITING:
                self.avatar.expression = "patient"
            elif new_state == CapsuleState.ALERT:
                self.avatar.expression = "concerned"
            elif new_state == CapsuleState.ERROR:
                self.avatar.expression = "troubled"
            elif new_state == CapsuleState.SUCCESS:
                self.avatar.expression = "satisfied"
            else:
                self.avatar.expression = "neutral"
    
    def update_size(self, new_size: CapsuleSize) -> None:
        """Update the size of this capsule."""
        old_size = self.size
        self.size = new_size
        logger.debug(f"Capsule {self.agent_id} size changed from {old_size} to {new_size}")
    
    def update_metrics(self, metrics: CapsuleMetrics) -> None:
        """Update the metrics for this capsule."""
        self.metrics = metrics
        logger.debug(f"Metrics updated for capsule {self.agent_id}")
    
    def add_debug_trace(self, trace_entry: Dict[str, Any]) -> None:
        """Add a debug trace entry to this capsule."""
        self.debug_trace.append({
            **trace_entry,
            "timestamp": "current_timestamp_here"  # Would use actual timestamp in real implementation
        })
        logger.debug(f"Debug trace entry added to capsule {self.agent_id}")
    
    def pin_to_location(self, location: str) -> None:
        """Pin this capsule to a specific location."""
        self.pin_status["is_pinned"] = True
        self.pin_status["pin_location"] = location
        logger.info(f"Capsule {self.agent_id} pinned to {location}")
    
    def unpin(self) -> None:
        """Unpin this capsule."""
        self.pin_status["is_pinned"] = False
        self.pin_status["pin_location"] = None
        logger.info(f"Capsule {self.agent_id} unpinned")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this capsule to a dictionary representation."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "state": self.state.value,
            "size": self.size.value,
            "avatar": vars(self.avatar) if self.avatar else None,
            "context": vars(self.context) if self.context else None,
            "metrics": {
                "primary_metric": self.metrics.primary_metric,
                "secondary_metrics": self.metrics.secondary_metrics,
                "alerts": self.metrics.alerts,
                "trends": self.metrics.trends
            },
            "actions": [vars(action) for action in self.actions],
            "pin_status": self.pin_status,
            "ui_preferences": self.ui_preferences
        }
    
    def to_json(self) -> str:
        """Convert this capsule to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DynamicAgentCapsule':
        """Create a capsule from a dictionary representation."""
        capsule = cls(
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            agent_type=data["agent_type"],
            initial_state=CapsuleState(data["state"]),
            initial_size=CapsuleSize(data["size"])
        )
        
        if data.get("avatar"):
            capsule.avatar = CapsuleAvatar(**data["avatar"])
        
        if data.get("context"):
            capsule.context = CapsuleContext(**data["context"])
        
        if data.get("metrics"):
            metrics = CapsuleMetrics(
                primary_metric=data["metrics"].get("primary_metric", {}),
                secondary_metrics=data["metrics"].get("secondary_metrics", []),
                alerts=data["metrics"].get("alerts", []),
                trends=data["metrics"].get("trends", {})
            )
            capsule.metrics = metrics
        
        for action_data in data.get("actions", []):
            capsule.add_action(CapsuleAction(**action_data))
        
        capsule.pin_status = data.get("pin_status", {"is_pinned": False, "pin_location": None})
        capsule.ui_preferences = data.get("ui_preferences", {})
        
        return capsule
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DynamicAgentCapsule':
        """Create a capsule from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class CapsuleManager:
    """
    Manager class for handling multiple Dynamic Agent Capsules.
    
    This class provides methods for creating, retrieving, updating, and
    managing the lifecycle of Dynamic Agent Capsules.
    """
    
    def __init__(self):
        """Initialize a new Capsule Manager."""
        self.capsules = {}
        logger.info("Initialized new Capsule Manager")
    
    def create_capsule(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        initial_state: CapsuleState = CapsuleState.IDLE,
        initial_size: CapsuleSize = CapsuleSize.NORMAL
    ) -> DynamicAgentCapsule:
        """Create a new capsule and register it with the manager."""
        if agent_id in self.capsules:
            logger.warning(f"Capsule with ID {agent_id} already exists, returning existing capsule")
            return self.capsules[agent_id]
        
        capsule = DynamicAgentCapsule(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            initial_state=initial_state,
            initial_size=initial_size
        )
        
        self.capsules[agent_id] = capsule
        logger.info(f"Created and registered new capsule for agent {agent_id}")
        return capsule
    
    def get_capsule(self, agent_id: str) -> Optional[DynamicAgentCapsule]:
        """Get a capsule by agent ID."""
        capsule = self.capsules.get(agent_id)
        if not capsule:
            logger.warning(f"No capsule found for agent {agent_id}")
        return capsule
    
    def update_capsule(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        """Update a capsule with the provided updates."""
        capsule = self.get_capsule(agent_id)
        if not capsule:
            return False
        
        if "state" in updates:
            capsule.update_state(CapsuleState(updates["state"]))
        
        if "size" in updates:
            capsule.update_size(CapsuleSize(updates["size"]))
        
        if "avatar" in updates:
            capsule.set_avatar(CapsuleAvatar(**updates["avatar"]))
        
        if "context" in updates:
            capsule.set_context(CapsuleContext(**updates["context"]))
        
        if "metrics" in updates:
            metrics = CapsuleMetrics(
                primary_metric=updates["metrics"].get("primary_metric", {}),
                secondary_metrics=updates["metrics"].get("secondary_metrics", []),
                alerts=updates["metrics"].get("alerts", []),
                trends=updates["metrics"].get("trends", {})
            )
            capsule.update_metrics(metrics)
        
        if "actions" in updates:
            # Clear existing actions and add new ones
            capsule.actions = []
            for action_data in updates["actions"]:
                capsule.add_action(CapsuleAction(**action_data))
        
        if "pin_status" in updates:
            capsule.pin_status = updates["pin_status"]
        
        if "ui_preferences" in updates:
            capsule.ui_preferences.update(updates["ui_preferences"])
        
        logger.info(f"Updated capsule for agent {agent_id}")
        return True
    
    def remove_capsule(self, agent_id: str) -> bool:
        """Remove a capsule from the manager."""
        if agent_id not in self.capsules:
            logger.warning(f"Cannot remove: no capsule found for agent {agent_id}")
            return False
        
        del self.capsules[agent_id]
        logger.info(f"Removed capsule for agent {agent_id}")
        return True
    
    def get_all_capsules(self) -> Dict[str, DynamicAgentCapsule]:
        """Get all capsules managed by this manager."""
        return self.capsules
    
    def get_capsules_by_type(self, agent_type: str) -> List[DynamicAgentCapsule]:
        """Get all capsules of a specific agent type."""
        return [c for c in self.capsules.values() if c.agent_type == agent_type]
    
    def get_capsules_by_state(self, state: CapsuleState) -> List[DynamicAgentCapsule]:
        """Get all capsules in a specific state."""
        return [c for c in self.capsules.values() if c.state == state]
    
    def get_pinned_capsules(self) -> List[DynamicAgentCapsule]:
        """Get all pinned capsules."""
        return [c for c in self.capsules.values() if c.pin_status["is_pinned"]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this manager to a dictionary representation."""
        return {
            "capsules": {
                agent_id: capsule.to_dict()
                for agent_id, capsule in self.capsules.items()
            }
        }
    
    def to_json(self) -> str:
        """Convert this manager to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapsuleManager':
        """Create a manager from a dictionary representation."""
        manager = cls()
        
        for agent_id, capsule_data in data.get("capsules", {}).items():
            capsule = DynamicAgentCapsule.from_dict(capsule_data)
            manager.capsules[agent_id] = capsule
        
        return manager
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CapsuleManager':
        """Create a manager from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


# Example usage
if __name__ == "__main__":
    # Create a capsule manager
    manager = CapsuleManager()
    
    # Create a workflow trigger agent capsule
    trigger_capsule = manager.create_capsule(
        agent_id="wf-trigger-001",
        agent_name="Manufacturing Workflow Trigger",
        agent_type="workflow_trigger",
        initial_state=CapsuleState.ACTIVE
    )
    
    # Set avatar for the capsule
    trigger_capsule.set_avatar(CapsuleAvatar(
        image_url="/assets/avatars/workflow-trigger.svg",
        animation_states={
            "idle": "/assets/animations/trigger-idle.json",
            "active": "/assets/animations/trigger-active.json"
        },
        expression="attentive",
        color_theme={
            "primary": "#3498db",
            "secondary": "#2980b9",
            "accent": "#e74c3c"
        }
    ))
    
    # Set context for the capsule
    trigger_capsule.set_context(CapsuleContext(
        workflow_id="mfg-pm-001",
        source_context="Manufacturing/PredictiveMaintenance",
        trust_score=0.85,
        confidence_score=0.92,
        execution_mode="proactive",
        progress=0.0
    ))
    
    # Add actions to the capsule
    trigger_capsule.add_action(CapsuleAction(
        id="start-workflow",
        name="Start Workflow",
        icon="play-circle",
        description="Start the predictive maintenance workflow",
        enabled=True
    ))
    
    trigger_capsule.add_action(CapsuleAction(
        id="configure",
        name="Configure",
        icon="settings",
        description="Configure workflow trigger parameters",
        enabled=True
    ))
    
    # Update metrics for the capsule
    trigger_capsule.update_metrics(CapsuleMetrics(
        primary_metric={
            "name": "Equipment Health",
            "value": 87,
            "unit": "%",
            "trend": "stable"
        },
        secondary_metrics=[
            {
                "name": "Anomalies",
                "value": 3,
                "unit": "count",
                "trend": "increasing"
            },
            {
                "name": "Last Check",
                "value": "2h ago",
                "unit": "",
                "trend": "neutral"
            }
        ],
        alerts=[
            {
                "level": "warning",
                "message": "Vibration levels increasing on pump #3"
            }
        ],
        trends={
            "temperature": [68, 70, 72, 75, 73, 74, 76],
            "vibration": [0.2, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        }
    ))
    
    # Print the capsule as JSON
    print(trigger_capsule.to_json())
    
    # Create a human intervention agent capsule
    human_capsule = manager.create_capsule(
        agent_id="human-int-001",
        agent_name="Maintenance Approval Agent",
        agent_type="human_intervention",
        initial_state=CapsuleState.WAITING
    )
    
    # Set context for the human intervention capsule
    human_capsule.set_context(CapsuleContext(
        workflow_id="mfg-pm-001",
        task_id="human_approval",
        source_context="Manufacturing/PredictiveMaintenance/HumanApproval",
        trust_score=0.95,
        confidence_score=0.90,
        execution_mode="reactive",
        progress=0.5,
        time_remaining=3600,  # 1 hour
        related_entities=["equipment-pump-003", "maintenance-team-alpha"]
    ))
    
    # Print all capsules as JSON
    print(manager.to_json())
