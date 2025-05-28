"""
Swarm Intuition Engine for the Industriverse UI/UX Layer.

This module provides intuitive visualization and interaction with agent swarms,
enabling users to "feel" swarm health and intent through micro-interactions,
visual cues, and ambient audio signals.

Author: Manus
"""

import logging
import time
import math
import random
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
import uuid
import json

class SwarmState(Enum):
    """Enumeration of swarm states."""
    FORMING = "forming"
    ACTIVE = "active"
    DISPERSING = "dispersing"
    IDLE = "idle"
    BUSY = "busy"
    FOCUSED = "focused"
    SEARCHING = "searching"
    LEARNING = "learning"
    COLLABORATING = "collaborating"
    CONFLICTED = "conflicted"
    ERROR = "error"
    CUSTOM = "custom"

class SwarmIntent(Enum):
    """Enumeration of swarm intents."""
    EXPLORE = "explore"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    MONITOR = "monitor"
    PREDICT = "predict"
    RESPOND = "respond"
    LEARN = "learn"
    COLLABORATE = "collaborate"
    NEGOTIATE = "negotiate"
    CUSTOM = "custom"

class SwarmHealth(Enum):
    """Enumeration of swarm health levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class SwarmVisualizationMode(Enum):
    """Enumeration of swarm visualization modes."""
    PARTICLES = "particles"
    NETWORK = "network"
    HEATMAP = "heatmap"
    FLOW = "flow"
    PULSE = "pulse"
    AMBIENT = "ambient"
    CUSTOM = "custom"

class SwarmAudioMode(Enum):
    """Enumeration of swarm audio modes."""
    NONE = "none"
    AMBIENT = "ambient"
    PULSE = "pulse"
    ALERT = "alert"
    HARMONY = "harmony"
    CUSTOM = "custom"

class SwarmAgent:
    """Represents an agent within a swarm."""
    
    def __init__(self,
                 agent_id: str,
                 agent_type: str,
                 state: str = "idle",
                 position: Optional[Tuple[float, float, float]] = None,
                 velocity: Optional[Tuple[float, float, float]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a swarm agent.
        
        Args:
            agent_id: Unique identifier for this agent
            agent_type: Type of agent
            state: Current state of the agent
            position: 3D position of the agent (x, y, z)
            velocity: 3D velocity of the agent (vx, vy, vz)
            metadata: Additional metadata for this agent
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state = state
        self.position = position or (0.0, 0.0, 0.0)
        self.velocity = velocity or (0.0, 0.0, 0.0)
        self.metadata = metadata or {}
        self.connections: Set[str] = set()  # IDs of connected agents
        self.last_update = time.time()
        self.health = 1.0  # 0.0 to 1.0
        self.energy = 1.0  # 0.0 to 1.0
        self.focus = 0.5   # 0.0 to 1.0
        
    def update_position(self, 
                      dt: float, 
                      bounds: Optional[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]] = None) -> None:
        """
        Update the agent's position based on its velocity.
        
        Args:
            dt: Time step in seconds
            bounds: Optional 3D bounds as ((min_x, max_x), (min_y, max_y), (min_z, max_z))
        """
        x, y, z = self.position
        vx, vy, vz = self.velocity
        
        # Update position
        x += vx * dt
        y += vy * dt
        z += vz * dt
        
        # Apply bounds if provided
        if bounds is not None:
            (min_x, max_x), (min_y, max_y), (min_z, max_z) = bounds
            
            # Bounce off boundaries
            if x < min_x:
                x = min_x
                vx = -vx * 0.8  # Damping factor
            elif x > max_x:
                x = max_x
                vx = -vx * 0.8
                
            if y < min_y:
                y = min_y
                vy = -vy * 0.8
            elif y > max_y:
                y = max_y
                vy = -vy * 0.8
                
            if z < min_z:
                z = min_z
                vz = -vz * 0.8
            elif z > max_z:
                z = max_z
                vz = -vz * 0.8
                
            self.velocity = (vx, vy, vz)
            
        self.position = (x, y, z)
        self.last_update = time.time()
        
    def apply_force(self, force: Tuple[float, float, float], dt: float) -> None:
        """
        Apply a force to the agent, changing its velocity.
        
        Args:
            force: 3D force vector (fx, fy, fz)
            dt: Time step in seconds
        """
        vx, vy, vz = self.velocity
        fx, fy, fz = force
        
        # Update velocity (F = ma, assuming mass = 1)
        vx += fx * dt
        vy += fy * dt
        vz += fz * dt
        
        # Apply damping
        damping = 0.98
        vx *= damping
        vy *= damping
        vz *= damping
        
        self.velocity = (vx, vy, vz)
        
    def distance_to(self, other: 'SwarmAgent') -> float:
        """
        Calculate the distance to another agent.
        
        Args:
            other: The other agent
            
        Returns:
            Distance between the agents
        """
        x1, y1, z1 = self.position
        x2, y2, z2 = other.position
        
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
        
    def connect_to(self, other_id: str) -> None:
        """
        Connect this agent to another agent.
        
        Args:
            other_id: ID of the other agent
        """
        self.connections.add(other_id)
        
    def disconnect_from(self, other_id: str) -> None:
        """
        Disconnect this agent from another agent.
        
        Args:
            other_id: ID of the other agent
        """
        if other_id in self.connections:
            self.connections.remove(other_id)
            
    def is_connected_to(self, other_id: str) -> bool:
        """
        Check if this agent is connected to another agent.
        
        Args:
            other_id: ID of the other agent
            
        Returns:
            True if connected, False otherwise
        """
        return other_id in self.connections
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this agent to a dictionary representation."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state,
            "position": self.position,
            "velocity": self.velocity,
            "connections": list(self.connections),
            "health": self.health,
            "energy": self.energy,
            "focus": self.focus,
            "metadata": self.metadata,
            "last_update": self.last_update
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SwarmAgent':
        """Create a swarm agent from a dictionary representation."""
        agent = cls(
            agent_id=data["agent_id"],
            agent_type=data["agent_type"],
            state=data["state"],
            position=data["position"],
            velocity=data["velocity"],
            metadata=data["metadata"]
        )
        
        agent.connections = set(data.get("connections", []))
        agent.health = data.get("health", 1.0)
        agent.energy = data.get("energy", 1.0)
        agent.focus = data.get("focus", 0.5)
        agent.last_update = data.get("last_update", time.time())
        
        return agent

class SwarmBehavior:
    """Defines a behavior for a swarm."""
    
    def __init__(self,
                 behavior_id: str,
                 name: str,
                 update_func: Callable[[Dict[str, SwarmAgent], float, Dict[str, Any]], None],
                 parameters: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a swarm behavior.
        
        Args:
            behavior_id: Unique identifier for this behavior
            name: Name of the behavior
            update_func: Function to update the swarm agents
            parameters: Parameters for this behavior
            metadata: Additional metadata for this behavior
        """
        self.behavior_id = behavior_id
        self.name = name
        self.update_func = update_func
        self.parameters = parameters or {}
        self.metadata = metadata or {}
        
    def update(self, 
             agents: Dict[str, SwarmAgent], 
             dt: float, 
             context: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the swarm agents according to this behavior.
        
        Args:
            agents: Dictionary of agent ID to agent
            dt: Time step in seconds
            context: Optional context for the update
        """
        self.update_func(agents, dt, context or {})
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this behavior to a dictionary representation."""
        return {
            "behavior_id": self.behavior_id,
            "name": self.name,
            "parameters": self.parameters,
            "metadata": self.metadata
        }

class SwarmIntuitionEngine:
    """
    Provides intuitive visualization and interaction with agent swarms.
    
    This class enables users to "feel" swarm health and intent through:
    - Visual representations of swarm dynamics
    - Micro-interactions that reflect swarm behavior
    - Ambient audio signals that convey swarm state
    - Haptic feedback for physical devices
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Swarm Intuition Engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.swarms: Dict[str, Dict[str, Any]] = {}
        self.agents: Dict[str, SwarmAgent] = {}
        self.behaviors: Dict[str, SwarmBehavior] = {}
        self.visualization_mode = SwarmVisualizationMode(self.config.get("visualization_mode", "particles"))
        self.audio_mode = SwarmAudioMode(self.config.get("audio_mode", "ambient"))
        self.haptic_enabled = self.config.get("haptic_enabled", True)
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        
        # Initialize default behaviors
        self._initialize_default_behaviors()
        
    def _initialize_default_behaviors(self) -> None:
        """Initialize default swarm behaviors."""
        # Cohesion behavior (agents move toward the center of mass)
        self.register_behavior(
            behavior_id="cohesion",
            name="Cohesion",
            update_func=self._cohesion_behavior,
            parameters={"strength": 0.5}
        )
        
        # Separation behavior (agents avoid crowding)
        self.register_behavior(
            behavior_id="separation",
            name="Separation",
            update_func=self._separation_behavior,
            parameters={"min_distance": 0.5, "strength": 0.3}
        )
        
        # Alignment behavior (agents align velocity with neighbors)
        self.register_behavior(
            behavior_id="alignment",
            name="Alignment",
            update_func=self._alignment_behavior,
            parameters={"neighborhood_radius": 2.0, "strength": 0.2}
        )
        
        # Goal-seeking behavior (agents move toward a goal)
        self.register_behavior(
            behavior_id="goal_seeking",
            name="Goal Seeking",
            update_func=self._goal_seeking_behavior,
            parameters={"strength": 0.8}
        )
        
        # Wandering behavior (agents move randomly)
        self.register_behavior(
            behavior_id="wandering",
            name="Wandering",
            update_func=self._wandering_behavior,
            parameters={"strength": 0.1, "change_direction_probability": 0.05}
        )
        
        # Flocking behavior (combination of cohesion, separation, and alignment)
        self.register_behavior(
            behavior_id="flocking",
            name="Flocking",
            update_func=self._flocking_behavior,
            parameters={
                "cohesion_strength": 0.5,
                "separation_strength": 0.3,
                "alignment_strength": 0.2,
                "min_distance": 0.5,
                "neighborhood_radius": 2.0
            }
        )
        
    def register_behavior(self,
                        behavior_id: str,
                        name: str,
                        update_func: Callable[[Dict[str, SwarmAgent], float, Dict[str, Any]], None],
                        parameters: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a swarm behavior.
        
        Args:
            behavior_id: Unique identifier for this behavior
            name: Name of the behavior
            update_func: Function to update the swarm agents
            parameters: Parameters for this behavior
        """
        if behavior_id in self.behaviors:
            self.logger.warning(f"Behavior with ID {behavior_id} already exists, overwriting")
            
        self.behaviors[behavior_id] = SwarmBehavior(
            behavior_id=behavior_id,
            name=name,
            update_func=update_func,
            parameters=parameters
        )
        
    def unregister_behavior(self, behavior_id: str) -> bool:
        """
        Unregister a swarm behavior.
        
        Args:
            behavior_id: ID of the behavior to unregister
            
        Returns:
            True if the behavior was unregistered, False if not found
        """
        if behavior_id not in self.behaviors:
            return False
            
        del self.behaviors[behavior_id]
        return True
    
    def create_swarm(self,
                   swarm_id: str,
                   name: str,
                   intent: SwarmIntent = SwarmIntent.EXPLORE,
                   state: SwarmState = SwarmState.FORMING,
                   behaviors: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new swarm.
        
        Args:
            swarm_id: Unique identifier for this swarm
            name: Name of the swarm
            intent: Intent of the swarm
            state: Initial state of the swarm
            behaviors: List of behavior IDs to apply to this swarm
            metadata: Additional metadata for this swarm
            
        Returns:
            ID of the created swarm
        """
        if swarm_id in self.swarms:
            self.logger.warning(f"Swarm with ID {swarm_id} already exists, overwriting")
            
        # Create swarm
        self.swarms[swarm_id] = {
            "swarm_id": swarm_id,
            "name": name,
            "intent": intent.value,
            "state": state.value,
            "behaviors": behaviors or ["wandering"],
            "agent_ids": [],
            "creation_time": time.time(),
            "last_update": time.time(),
            "health": SwarmHealth.GOOD.value,
            "metadata": metadata or {},
            "visualization": {
                "mode": self.visualization_mode.value,
                "color": "#2196F3",
                "opacity": 0.8,
                "size": 1.0,
                "pulse_rate": 1.0
            },
            "audio": {
                "mode": self.audio_mode.value,
                "volume": 0.5,
                "pitch": 0.5,
                "tempo": 1.0
            },
            "haptic": {
                "enabled": self.haptic_enabled,
                "intensity": 0.5,
                "pattern": "pulse"
            }
        }
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "swarm_created",
            "swarm_id": swarm_id,
            "name": name,
            "intent": intent.value,
            "state": state.value
        })
        
        return swarm_id
    
    def delete_swarm(self, swarm_id: str) -> bool:
        """
        Delete a swarm.
        
        Args:
            swarm_id: ID of the swarm to delete
            
        Returns:
            True if the swarm was deleted, False if not found
        """
        if swarm_id not in self.swarms:
            return False
            
        # Get agent IDs
        agent_ids = self.swarms[swarm_id]["agent_ids"]
        
        # Delete swarm
        del self.swarms[swarm_id]
        
        # Delete agents
        for agent_id in agent_ids:
            if agent_id in self.agents:
                del self.agents[agent_id]
                
        # Dispatch event
        self._dispatch_event({
            "event_type": "swarm_deleted",
            "swarm_id": swarm_id
        })
        
        return True
    
    def add_agent_to_swarm(self,
                         swarm_id: str,
                         agent_id: str,
                         agent_type: str,
                         state: str = "idle",
                         position: Optional[Tuple[float, float, float]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add an agent to a swarm.
        
        Args:
            swarm_id: ID of the swarm
            agent_id: Unique identifier for the agent
            agent_type: Type of agent
            state: Initial state of the agent
            position: Initial 3D position of the agent
            metadata: Additional metadata for the agent
            
        Returns:
            True if the agent was added, False if the swarm was not found
        """
        if swarm_id not in self.swarms:
            return False
            
        # Create agent
        agent = SwarmAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            state=state,
            position=position,
            metadata=metadata
        )
        
        # Add agent to swarm
        self.agents[agent_id] = agent
        self.swarms[swarm_id]["agent_ids"].append(agent_id)
        self.swarms[swarm_id]["last_update"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "agent_added",
            "swarm_id": swarm_id,
            "agent_id": agent_id,
            "agent_type": agent_type
        })
        
        return True
    
    def remove_agent_from_swarm(self, swarm_id: str, agent_id: str) -> bool:
        """
        Remove an agent from a swarm.
        
        Args:
            swarm_id: ID of the swarm
            agent_id: ID of the agent to remove
            
        Returns:
            True if the agent was removed, False if the swarm or agent was not found
        """
        if swarm_id not in self.swarms or agent_id not in self.agents:
            return False
            
        # Remove agent from swarm
        if agent_id in self.swarms[swarm_id]["agent_ids"]:
            self.swarms[swarm_id]["agent_ids"].remove(agent_id)
            self.swarms[swarm_id]["last_update"] = time.time()
            
        # Delete agent
        del self.agents[agent_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "agent_removed",
            "swarm_id": swarm_id,
            "agent_id": agent_id
        })
        
        return True
    
    def update_swarm_state(self, swarm_id: str, state: SwarmState) -> bool:
        """
        Update the state of a swarm.
        
        Args:
            swarm_id: ID of the swarm
            state: New state of the swarm
            
        Returns:
            True if the state was updated, False if the swarm was not found
        """
        if swarm_id not in self.swarms:
            return False
            
        old_state = self.swarms[swarm_id]["state"]
        self.swarms[swarm_id]["state"] = state.value
        self.swarms[swarm_id]["last_update"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "swarm_state_changed",
            "swarm_id": swarm_id,
            "old_state": old_state,
            "new_state": state.value
        })
        
        return True
    
    def update_swarm_intent(self, swarm_id: str, intent: SwarmIntent) -> bool:
        """
        Update the intent of a swarm.
        
        Args:
            swarm_id: ID of the swarm
            intent: New intent of the swarm
            
        Returns:
            True if the intent was updated, False if the swarm was not found
        """
        if swarm_id not in self.swarms:
            return False
            
        old_intent = self.swarms[swarm_id]["intent"]
        self.swarms[swarm_id]["intent"] = intent.value
        self.swarms[swarm_id]["last_update"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "swarm_intent_changed",
            "swarm_id": swarm_id,
            "old_intent": old_intent,
            "new_intent": intent.value
        })
        
        return True
    
    def update_swarm_health(self, swarm_id: str, health: SwarmHealth) -> bool:
        """
        Update the health of a swarm.
        
        Args:
            swarm_id: ID of the swarm
            health: New health of the swarm
            
        Returns:
            True if the health was updated, False if the swarm was not found
        """
        if swarm_id not in self.swarms:
            return False
            
        old_health = self.swarms[swarm_id]["health"]
        self.swarms[swarm_id]["health"] = health.value
        self.swarms[swarm_id]["last_update"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "swarm_health_changed",
            "swarm_id": swarm_id,
            "old_health": old_health,
            "new_health": health.value
        })
        
        return True
    
    def update_swarm_behaviors(self, swarm_id: str, behaviors: List[str]) -> bool:
        """
        Update the behaviors of a swarm.
        
        Args:
            swarm_id: ID of the swarm
            behaviors: List of behavior IDs to apply to this swarm
            
        Returns:
            True if the behaviors were updated, False if the swarm was not found
        """
        if swarm_id not in self.swarms:
            return False
            
        # Validate behaviors
        valid_behaviors = [b for b in behaviors if b in self.behaviors]
        if len(valid_behaviors) != len(behaviors):
            invalid_behaviors = set(behaviors) - set(valid_behaviors)
            self.logger.warning(f"Some behaviors were not found and will be ignored: {invalid_behaviors}")
            
        self.swarms[swarm_id]["behaviors"] = valid_behaviors
        self.swarms[swarm_id]["last_update"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "swarm_behaviors_changed",
            "swarm_id": swarm_id,
            "behaviors": valid_behaviors
        })
        
        return True
    
    def update_swarm_visualization(self, 
                                 swarm_id: str, 
                                 mode: Optional[SwarmVisualizationMode] = None,
                                 color: Optional[str] = None,
                                 opacity: Optional[float] = None,
                                 size: Optional[float] = None,
                                 pulse_rate: Optional[float] = None) -> bool:
        """
        Update the visualization settings of a swarm.
        
        Args:
            swarm_id: ID of the swarm
            mode: Visualization mode
            color: Color of the swarm (hex code)
            opacity: Opacity of the swarm (0.0 to 1.0)
            size: Size multiplier of the swarm (default 1.0)
            pulse_rate: Pulse rate of the swarm (pulses per second)
            
        Returns:
            True if the visualization was updated, False if the swarm was not found
        """
        if swarm_id not in self.swarms:
            return False
            
        visualization = self.swarms[swarm_id]["visualization"]
        
        if mode is not None:
            visualization["mode"] = mode.value
            
        if color is not None:
            visualization["color"] = color
            
        if opacity is not None:
            visualization["opacity"] = max(0.0, min(1.0, opacity))
            
        if size is not None:
            visualization["size"] = max(0.1, size)
            
        if pulse_rate is not None:
            visualization["pulse_rate"] = max(0.1, pulse_rate)
            
        self.swarms[swarm_id]["last_update"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "swarm_visualization_changed",
            "swarm_id": swarm_id,
            "visualization": visualization
        })
        
        return True
    
    def update_swarm_audio(self,
                         swarm_id: str,
                         mode: Optional[SwarmAudioMode] = None,
                         volume: Optional[float] = None,
                         pitch: Optional[float] = None,
                         tempo: Optional[float] = None) -> bool:
        """
        Update the audio settings of a swarm.
        
        Args:
            swarm_id: ID of the swarm
            mode: Audio mode
            volume: Volume of the audio (0.0 to 1.0)
            pitch: Pitch of the audio (0.0 to 1.0)
            tempo: Tempo of the audio (multiplier, default 1.0)
            
        Returns:
            True if the audio was updated, False if the swarm was not found
        """
        if swarm_id not in self.swarms:
            return False
            
        audio = self.swarms[swarm_id]["audio"]
        
        if mode is not None:
            audio["mode"] = mode.value
            
        if volume is not None:
            audio["volume"] = max(0.0, min(1.0, volume))
            
        if pitch is not None:
            audio["pitch"] = max(0.0, min(1.0, pitch))
            
        if tempo is not None:
            audio["tempo"] = max(0.1, tempo)
            
        self.swarms[swarm_id]["last_update"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "swarm_audio_changed",
            "swarm_id": swarm_id,
            "audio": audio
        })
        
        return True
    
    def update_swarm_haptic(self,
                          swarm_id: str,
                          enabled: Optional[bool] = None,
                          intensity: Optional[float] = None,
                          pattern: Optional[str] = None) -> bool:
        """
        Update the haptic feedback settings of a swarm.
        
        Args:
            swarm_id: ID of the swarm
            enabled: Whether haptic feedback is enabled
            intensity: Intensity of the haptic feedback (0.0 to 1.0)
            pattern: Pattern of the haptic feedback (e.g., "pulse", "buzz", "tap")
            
        Returns:
            True if the haptic settings were updated, False if the swarm was not found
        """
        if swarm_id not in self.swarms:
            return False
            
        haptic = self.swarms[swarm_id]["haptic"]
        
        if enabled is not None:
            haptic["enabled"] = enabled
            
        if intensity is not None:
            haptic["intensity"] = max(0.0, min(1.0, intensity))
            
        if pattern is not None:
            haptic["pattern"] = pattern
            
        self.swarms[swarm_id]["last_update"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "swarm_haptic_changed",
            "swarm_id": swarm_id,
            "haptic": haptic
        })
        
        return True
    
    def update(self, dt: float) -> None:
        """
        Update all swarms and agents.
        
        Args:
            dt: Time step in seconds
        """
        # Update each swarm
        for swarm_id, swarm in self.swarms.items():
            # Get agents in this swarm
            agent_ids = swarm["agent_ids"]
            swarm_agents = {agent_id: self.agents[agent_id] for agent_id in agent_ids if agent_id in self.agents}
            
            # Skip if no agents
            if not swarm_agents:
                continue
                
            # Apply behaviors
            for behavior_id in swarm["behaviors"]:
                if behavior_id in self.behaviors:
                    behavior = self.behaviors[behavior_id]
                    try:
                        behavior.update(swarm_agents, dt, {"swarm": swarm})
                    except Exception as e:
                        self.logger.error(f"Error in behavior {behavior_id}: {e}")
                        
            # Update agent positions
            bounds = ((0, 10), (0, 10), (0, 10))  # Example bounds
            for agent in swarm_agents.values():
                agent.update_position(dt, bounds)
                
            # Update swarm health based on agent health
            avg_health = sum(agent.health for agent in swarm_agents.values()) / len(swarm_agents)
            if avg_health > 0.8:
                self.update_swarm_health(swarm_id, SwarmHealth.EXCELLENT)
            elif avg_health > 0.6:
                self.update_swarm_health(swarm_id, SwarmHealth.GOOD)
            elif avg_health > 0.4:
                self.update_swarm_health(swarm_id, SwarmHealth.FAIR)
            elif avg_health > 0.2:
                self.update_swarm_health(swarm_id, SwarmHealth.POOR)
            else:
                self.update_swarm_health(swarm_id, SwarmHealth.CRITICAL)
                
            # Update swarm state based on agent states
            state_counts = {}
            for agent in swarm_agents.values():
                state_counts[agent.state] = state_counts.get(agent.state, 0) + 1
                
            if state_counts:
                dominant_state = max(state_counts.items(), key=lambda x: x[1])[0]
                if dominant_state == "idle":
                    self.update_swarm_state(swarm_id, SwarmState.IDLE)
                elif dominant_state == "busy":
                    self.update_swarm_state(swarm_id, SwarmState.BUSY)
                elif dominant_state == "searching":
                    self.update_swarm_state(swarm_id, SwarmState.SEARCHING)
                elif dominant_state == "learning":
                    self.update_swarm_state(swarm_id, SwarmState.LEARNING)
                elif dominant_state == "collaborating":
                    self.update_swarm_state(swarm_id, SwarmState.COLLABORATING)
                elif dominant_state == "error":
                    self.update_swarm_state(swarm_id, SwarmState.ERROR)
                    
            # Update swarm visualization based on state and health
            state = SwarmState(swarm["state"])
            health = SwarmHealth(swarm["health"])
            
            if state == SwarmState.IDLE:
                self.update_swarm_visualization(
                    swarm_id=swarm_id,
                    pulse_rate=0.5,
                    opacity=0.6
                )
            elif state == SwarmState.BUSY:
                self.update_swarm_visualization(
                    swarm_id=swarm_id,
                    pulse_rate=1.5,
                    opacity=0.9
                )
            elif state == SwarmState.SEARCHING:
                self.update_swarm_visualization(
                    swarm_id=swarm_id,
                    mode=SwarmVisualizationMode.FLOW,
                    pulse_rate=1.0,
                    opacity=0.8
                )
            elif state == SwarmState.ERROR:
                self.update_swarm_visualization(
                    swarm_id=swarm_id,
                    color="#FF5252",
                    pulse_rate=2.0,
                    opacity=1.0
                )
                
            if health == SwarmHealth.EXCELLENT:
                self.update_swarm_audio(
                    swarm_id=swarm_id,
                    mode=SwarmAudioMode.HARMONY,
                    volume=0.3,
                    pitch=0.7
                )
            elif health == SwarmHealth.GOOD:
                self.update_swarm_audio(
                    swarm_id=swarm_id,
                    mode=SwarmAudioMode.AMBIENT,
                    volume=0.4,
                    pitch=0.6
                )
            elif health == SwarmHealth.FAIR:
                self.update_swarm_audio(
                    swarm_id=swarm_id,
                    mode=SwarmAudioMode.PULSE,
                    volume=0.5,
                    pitch=0.5
                )
            elif health == SwarmHealth.POOR:
                self.update_swarm_audio(
                    swarm_id=swarm_id,
                    mode=SwarmAudioMode.PULSE,
                    volume=0.6,
                    pitch=0.4
                )
            elif health == SwarmHealth.CRITICAL:
                self.update_swarm_audio(
                    swarm_id=swarm_id,
                    mode=SwarmAudioMode.ALERT,
                    volume=0.8,
                    pitch=0.3
                )
                
            # Update haptic feedback based on state and health
            if health == SwarmHealth.CRITICAL:
                self.update_swarm_haptic(
                    swarm_id=swarm_id,
                    enabled=True,
                    intensity=0.8,
                    pattern="alert"
                )
            elif state == SwarmState.ERROR:
                self.update_swarm_haptic(
                    swarm_id=swarm_id,
                    enabled=True,
                    intensity=0.7,
                    pattern="error"
                )
            else:
                self.update_swarm_haptic(
                    swarm_id=swarm_id,
                    enabled=health == SwarmHealth.POOR,
                    intensity=0.5,
                    pattern="pulse"
                )
                
    def get_swarm(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a swarm by ID.
        
        Args:
            swarm_id: ID of the swarm
            
        Returns:
            The swarm, or None if not found
        """
        return self.swarms.get(swarm_id)
    
    def get_all_swarms(self) -> List[Dict[str, Any]]:
        """
        Get all swarms.
        
        Returns:
            List of all swarms
        """
        return list(self.swarms.values())
    
    def get_agent(self, agent_id: str) -> Optional[SwarmAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            The agent, or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_swarm_agents(self, swarm_id: str) -> List[SwarmAgent]:
        """
        Get all agents in a swarm.
        
        Args:
            swarm_id: ID of the swarm
            
        Returns:
            List of agents in the swarm, or empty list if swarm not found
        """
        if swarm_id not in self.swarms:
            return []
            
        agent_ids = self.swarms[swarm_id]["agent_ids"]
        return [self.agents[agent_id] for agent_id in agent_ids if agent_id in self.agents]
    
    def get_swarm_visualization_data(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get visualization data for a swarm.
        
        Args:
            swarm_id: ID of the swarm
            
        Returns:
            Visualization data for the swarm, or None if not found
        """
        if swarm_id not in self.swarms:
            return None
            
        swarm = self.swarms[swarm_id]
        agents = self.get_swarm_agents(swarm_id)
        
        # Basic swarm data
        data = {
            "swarm_id": swarm_id,
            "name": swarm["name"],
            "state": swarm["state"],
            "intent": swarm["intent"],
            "health": swarm["health"],
            "agent_count": len(agents),
            "visualization": swarm["visualization"],
            "audio": swarm["audio"],
            "haptic": swarm["haptic"]
        }
        
        # Agent positions and connections
        agent_data = []
        connections = []
        
        for agent in agents:
            agent_data.append({
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type,
                "state": agent.state,
                "position": agent.position,
                "velocity": agent.velocity,
                "health": agent.health,
                "energy": agent.energy,
                "focus": agent.focus
            })
            
            for other_id in agent.connections:
                if other_id in self.agents:
                    connections.append({
                        "source": agent.agent_id,
                        "target": other_id
                    })
                    
        data["agents"] = agent_data
        data["connections"] = connections
        
        return data
    
    def get_swarm_audio_data(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audio data for a swarm.
        
        Args:
            swarm_id: ID of the swarm
            
        Returns:
            Audio data for the swarm, or None if not found
        """
        if swarm_id not in self.swarms:
            return None
            
        swarm = self.swarms[swarm_id]
        
        return {
            "swarm_id": swarm_id,
            "name": swarm["name"],
            "state": swarm["state"],
            "health": swarm["health"],
            "audio": swarm["audio"]
        }
    
    def get_swarm_haptic_data(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get haptic feedback data for a swarm.
        
        Args:
            swarm_id: ID of the swarm
            
        Returns:
            Haptic feedback data for the swarm, or None if not found
        """
        if swarm_id not in self.swarms:
            return None
            
        swarm = self.swarms[swarm_id]
        
        return {
            "swarm_id": swarm_id,
            "name": swarm["name"],
            "state": swarm["state"],
            "health": swarm["health"],
            "haptic": swarm["haptic"]
        }
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for swarm events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for swarm events.
        
        Args:
            listener: The listener to remove
        """
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            
    def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_data: The event data to dispatch
        """
        event_data["timestamp"] = time.time()
        
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in event listener: {e}")
                
    # Default behavior implementations
    
    def _cohesion_behavior(self, 
                         agents: Dict[str, SwarmAgent], 
                         dt: float, 
                         context: Dict[str, Any]) -> None:
        """
        Cohesion behavior: agents move toward the center of mass.
        
        Args:
            agents: Dictionary of agent ID to agent
            dt: Time step in seconds
            context: Context for the update
        """
        if not agents:
            return
            
        # Calculate center of mass
        com_x = sum(agent.position[0] for agent in agents.values()) / len(agents)
        com_y = sum(agent.position[1] for agent in agents.values()) / len(agents)
        com_z = sum(agent.position[2] for agent in agents.values()) / len(agents)
        
        # Move agents toward center of mass
        strength = context.get("strength", self.behaviors["cohesion"].parameters.get("strength", 0.5))
        
        for agent in agents.values():
            x, y, z = agent.position
            
            # Calculate direction to center of mass
            dx = com_x - x
            dy = com_y - y
            dz = com_z - z
            
            # Apply force toward center of mass
            agent.apply_force((dx * strength, dy * strength, dz * strength), dt)
            
    def _separation_behavior(self, 
                           agents: Dict[str, SwarmAgent], 
                           dt: float, 
                           context: Dict[str, Any]) -> None:
        """
        Separation behavior: agents avoid crowding.
        
        Args:
            agents: Dictionary of agent ID to agent
            dt: Time step in seconds
            context: Context for the update
        """
        if not agents:
            return
            
        min_distance = context.get("min_distance", self.behaviors["separation"].parameters.get("min_distance", 0.5))
        strength = context.get("strength", self.behaviors["separation"].parameters.get("strength", 0.3))
        
        for agent_id, agent in agents.items():
            x, y, z = agent.position
            
            # Calculate separation force
            fx, fy, fz = 0, 0, 0
            
            for other_id, other in agents.items():
                if other_id == agent_id:
                    continue
                    
                # Calculate distance and direction
                distance = agent.distance_to(other)
                
                if distance < min_distance:
                    # Calculate repulsion force (inversely proportional to distance)
                    ox, oy, oz = other.position
                    dx = x - ox
                    dy = y - oy
                    dz = z - oz
                    
                    # Normalize and scale by distance
                    factor = 1.0 - (distance / min_distance)
                    
                    fx += dx * factor
                    fy += dy * factor
                    fz += dz * factor
                    
            # Apply separation force
            agent.apply_force((fx * strength, fy * strength, fz * strength), dt)
            
    def _alignment_behavior(self, 
                          agents: Dict[str, SwarmAgent], 
                          dt: float, 
                          context: Dict[str, Any]) -> None:
        """
        Alignment behavior: agents align velocity with neighbors.
        
        Args:
            agents: Dictionary of agent ID to agent
            dt: Time step in seconds
            context: Context for the update
        """
        if not agents:
            return
            
        neighborhood_radius = context.get("neighborhood_radius", self.behaviors["alignment"].parameters.get("neighborhood_radius", 2.0))
        strength = context.get("strength", self.behaviors["alignment"].parameters.get("strength", 0.2))
        
        for agent_id, agent in agents.items():
            # Find neighbors
            neighbors = []
            
            for other_id, other in agents.items():
                if other_id == agent_id:
                    continue
                    
                if agent.distance_to(other) <= neighborhood_radius:
                    neighbors.append(other)
                    
            if not neighbors:
                continue
                
            # Calculate average velocity of neighbors
            avg_vx = sum(neighbor.velocity[0] for neighbor in neighbors) / len(neighbors)
            avg_vy = sum(neighbor.velocity[1] for neighbor in neighbors) / len(neighbors)
            avg_vz = sum(neighbor.velocity[2] for neighbor in neighbors) / len(neighbors)
            
            # Calculate alignment force
            vx, vy, vz = agent.velocity
            fx = (avg_vx - vx) * strength
            fy = (avg_vy - vy) * strength
            fz = (avg_vz - vz) * strength
            
            # Apply alignment force
            agent.apply_force((fx, fy, fz), dt)
            
    def _goal_seeking_behavior(self, 
                             agents: Dict[str, SwarmAgent], 
                             dt: float, 
                             context: Dict[str, Any]) -> None:
        """
        Goal-seeking behavior: agents move toward a goal.
        
        Args:
            agents: Dictionary of agent ID to agent
            dt: Time step in seconds
            context: Context for the update
        """
        if not agents:
            return
            
        # Get goal position from context, or use default
        goal_position = context.get("goal_position", (5.0, 5.0, 5.0))
        strength = context.get("strength", self.behaviors["goal_seeking"].parameters.get("strength", 0.8))
        
        for agent in agents.values():
            x, y, z = agent.position
            gx, gy, gz = goal_position
            
            # Calculate direction to goal
            dx = gx - x
            dy = gy - y
            dz = gz - z
            
            # Calculate distance to goal
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            
            if distance > 0.1:  # Avoid division by zero and stop when close
                # Normalize direction
                dx /= distance
                dy /= distance
                dz /= distance
                
                # Apply force toward goal
                agent.apply_force((dx * strength, dy * strength, dz * strength), dt)
                
    def _wandering_behavior(self, 
                          agents: Dict[str, SwarmAgent], 
                          dt: float, 
                          context: Dict[str, Any]) -> None:
        """
        Wandering behavior: agents move randomly.
        
        Args:
            agents: Dictionary of agent ID to agent
            dt: Time step in seconds
            context: Context for the update
        """
        if not agents:
            return
            
        strength = context.get("strength", self.behaviors["wandering"].parameters.get("strength", 0.1))
        change_direction_probability = context.get("change_direction_probability", self.behaviors["wandering"].parameters.get("change_direction_probability", 0.05))
        
        for agent in agents.values():
            # Randomly change direction with some probability
            if random.random() < change_direction_probability:
                # Random direction
                fx = random.uniform(-1.0, 1.0) * strength
                fy = random.uniform(-1.0, 1.0) * strength
                fz = random.uniform(-1.0, 1.0) * strength
                
                # Apply random force
                agent.apply_force((fx, fy, fz), dt)
                
    def _flocking_behavior(self, 
                         agents: Dict[str, SwarmAgent], 
                         dt: float, 
                         context: Dict[str, Any]) -> None:
        """
        Flocking behavior: combination of cohesion, separation, and alignment.
        
        Args:
            agents: Dictionary of agent ID to agent
            dt: Time step in seconds
            context: Context for the update
        """
        if not agents:
            return
            
        # Get parameters
        params = self.behaviors["flocking"].parameters
        cohesion_strength = context.get("cohesion_strength", params.get("cohesion_strength", 0.5))
        separation_strength = context.get("separation_strength", params.get("separation_strength", 0.3))
        alignment_strength = context.get("alignment_strength", params.get("alignment_strength", 0.2))
        min_distance = context.get("min_distance", params.get("min_distance", 0.5))
        neighborhood_radius = context.get("neighborhood_radius", params.get("neighborhood_radius", 2.0))
        
        # Apply cohesion
        self._cohesion_behavior(agents, dt, {"strength": cohesion_strength})
        
        # Apply separation
        self._separation_behavior(agents, dt, {"min_distance": min_distance, "strength": separation_strength})
        
        # Apply alignment
        self._alignment_behavior(agents, dt, {"neighborhood_radius": neighborhood_radius, "strength": alignment_strength})
"""
