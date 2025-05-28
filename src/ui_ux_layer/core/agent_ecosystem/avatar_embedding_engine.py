"""
Avatar Embedding Engine for the Industriverse UI/UX Layer.

This module enables agent avatars to "step out" of their capsules when needed
(e.g., during an escalation) and hold natural language conversations in the Universal Skin.
It manages avatar presence, animations, expressions, and conversational capabilities.

Author: Manus
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
import uuid
import json
import random

class AvatarState(Enum):
    """Enumeration of avatar states."""
    EMBEDDED = "embedded"  # Avatar is embedded in its capsule
    EMERGING = "emerging"  # Avatar is in the process of stepping out
    CONVERSING = "conversing"  # Avatar is engaged in conversation
    PRESENTING = "presenting"  # Avatar is presenting information
    RETURNING = "returning"  # Avatar is returning to its capsule
    IDLE = "idle"  # Avatar is idle outside its capsule
    THINKING = "thinking"  # Avatar is processing information
    LISTENING = "listening"  # Avatar is listening to user input
    CUSTOM = "custom"  # Custom state

class AvatarExpression(Enum):
    """Enumeration of avatar expressions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    CONCERNED = "concerned"
    CONFUSED = "confused"
    FOCUSED = "focused"
    EXCITED = "excited"
    THOUGHTFUL = "thoughtful"
    SURPRISED = "surprised"
    CONFIDENT = "confident"
    CUSTOM = "custom"

class AvatarAnimationType(Enum):
    """Enumeration of avatar animation types."""
    EMERGE = "emerge"  # Stepping out of capsule
    RETURN = "return"  # Returning to capsule
    SPEAK = "speak"  # Speaking animation
    LISTEN = "listen"  # Listening animation
    THINK = "think"  # Thinking animation
    GESTURE = "gesture"  # Gesturing animation
    IDLE = "idle"  # Idle animation
    ATTENTION = "attention"  # Getting attention
    CUSTOM = "custom"  # Custom animation

class AvatarGesture(Enum):
    """Enumeration of avatar gestures."""
    POINT = "point"
    WAVE = "wave"
    NOD = "nod"
    SHAKE = "shake"
    SHRUG = "shrug"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    PRESENT = "present"
    CUSTOM = "custom"

class AvatarEmbeddingMode(Enum):
    """Enumeration of avatar embedding modes."""
    FULL = "full"  # Avatar fully emerges from capsule
    PARTIAL = "partial"  # Avatar partially emerges (e.g., just head and shoulders)
    OVERLAY = "overlay"  # Avatar appears as an overlay on the capsule
    SIDE = "side"  # Avatar appears beside the capsule
    REPLACE = "replace"  # Avatar temporarily replaces the capsule
    CUSTOM = "custom"  # Custom embedding mode

class AvatarConversationMode(Enum):
    """Enumeration of avatar conversation modes."""
    DIRECT = "direct"  # Direct conversation with user
    AMBIENT = "ambient"  # Ambient conversation (not directed at user)
    NARRATION = "narration"  # Narrating information
    PRESENTATION = "presentation"  # Presenting information
    COLLABORATION = "collaboration"  # Collaborating with other avatars
    CUSTOM = "custom"  # Custom conversation mode

class AvatarAnimation:
    """Represents an animation for an avatar."""
    
    def __init__(self,
                 animation_id: str,
                 animation_type: AvatarAnimationType,
                 duration: float,
                 keyframes: List[Dict[str, Any]],
                 loop: bool = False,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an avatar animation.
        
        Args:
            animation_id: Unique identifier for this animation
            animation_type: Type of animation
            duration: Duration of the animation in seconds
            keyframes: List of keyframes for the animation
            loop: Whether the animation should loop
            metadata: Additional metadata for this animation
        """
        self.animation_id = animation_id
        self.animation_type = animation_type
        self.duration = duration
        self.keyframes = keyframes
        self.loop = loop
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this animation to a dictionary representation."""
        return {
            "animation_id": self.animation_id,
            "animation_type": self.animation_type.value,
            "duration": self.duration,
            "keyframes": self.keyframes,
            "loop": self.loop,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AvatarAnimation':
        """Create an avatar animation from a dictionary representation."""
        return cls(
            animation_id=data["animation_id"],
            animation_type=AvatarAnimationType(data["animation_type"]),
            duration=data["duration"],
            keyframes=data["keyframes"],
            loop=data.get("loop", False),
            metadata=data.get("metadata", {})
        )

class AvatarConversation:
    """Represents a conversation involving an avatar."""
    
    def __init__(self,
                 conversation_id: str,
                 avatar_id: str,
                 mode: AvatarConversationMode,
                 start_time: float,
                 participants: List[str],
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an avatar conversation.
        
        Args:
            conversation_id: Unique identifier for this conversation
            avatar_id: ID of the avatar involved in the conversation
            mode: Conversation mode
            start_time: Start time of the conversation
            participants: List of participant IDs (can include user IDs and other avatar IDs)
            metadata: Additional metadata for this conversation
        """
        self.conversation_id = conversation_id
        self.avatar_id = avatar_id
        self.mode = mode
        self.start_time = start_time
        self.participants = participants
        self.metadata = metadata or {}
        self.messages: List[Dict[str, Any]] = []
        self.is_active = True
        self.end_time: Optional[float] = None
        
    def add_message(self,
                  sender_id: str,
                  content: str,
                  timestamp: Optional[float] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a message to the conversation.
        
        Args:
            sender_id: ID of the message sender
            content: Message content
            timestamp: Message timestamp (defaults to current time)
            metadata: Additional metadata for this message
            
        Returns:
            ID of the created message
        """
        message_id = str(uuid.uuid4())
        
        message = {
            "message_id": message_id,
            "sender_id": sender_id,
            "content": content,
            "timestamp": timestamp or time.time(),
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        return message_id
        
    def end_conversation(self) -> None:
        """End the conversation."""
        self.is_active = False
        self.end_time = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this conversation to a dictionary representation."""
        return {
            "conversation_id": self.conversation_id,
            "avatar_id": self.avatar_id,
            "mode": self.mode.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "participants": self.participants,
            "messages": self.messages,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AvatarConversation':
        """Create an avatar conversation from a dictionary representation."""
        conversation = cls(
            conversation_id=data["conversation_id"],
            avatar_id=data["avatar_id"],
            mode=AvatarConversationMode(data["mode"]),
            start_time=data["start_time"],
            participants=data["participants"],
            metadata=data.get("metadata", {})
        )
        
        conversation.messages = data.get("messages", [])
        conversation.is_active = data.get("is_active", True)
        conversation.end_time = data.get("end_time")
        
        return conversation

class EmbeddedAvatar:
    """Represents an avatar that can be embedded in or emerge from a capsule."""
    
    def __init__(self,
                 avatar_id: str,
                 name: str,
                 capsule_id: Optional[str],
                 avatar_type: str,
                 state: AvatarState = AvatarState.EMBEDDED,
                 expression: AvatarExpression = AvatarExpression.NEUTRAL,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an embedded avatar.
        
        Args:
            avatar_id: Unique identifier for this avatar
            name: Name of the avatar
            capsule_id: ID of the capsule this avatar is associated with (None if not associated)
            avatar_type: Type of avatar (e.g., "agent", "assistant", "expert")
            state: Current state of the avatar
            expression: Current expression of the avatar
            metadata: Additional metadata for this avatar
        """
        self.avatar_id = avatar_id
        self.name = name
        self.capsule_id = capsule_id
        self.avatar_type = avatar_type
        self.state = state
        self.expression = expression
        self.metadata = metadata or {}
        self.current_animation: Optional[str] = None
        self.current_conversation: Optional[str] = None
        self.embedding_mode = AvatarEmbeddingMode.FULL
        self.position: Optional[Tuple[float, float]] = None  # Position when emerged (x, y)
        self.size: Tuple[float, float] = (1.0, 1.0)  # Size when emerged (width, height)
        self.opacity = 1.0
        self.z_index = 100
        self.last_update = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this avatar to a dictionary representation."""
        return {
            "avatar_id": self.avatar_id,
            "name": self.name,
            "capsule_id": self.capsule_id,
            "avatar_type": self.avatar_type,
            "state": self.state.value,
            "expression": self.expression.value,
            "current_animation": self.current_animation,
            "current_conversation": self.current_conversation,
            "embedding_mode": self.embedding_mode.value,
            "position": self.position,
            "size": self.size,
            "opacity": self.opacity,
            "z_index": self.z_index,
            "last_update": self.last_update,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmbeddedAvatar':
        """Create an embedded avatar from a dictionary representation."""
        avatar = cls(
            avatar_id=data["avatar_id"],
            name=data["name"],
            capsule_id=data["capsule_id"],
            avatar_type=data["avatar_type"],
            state=AvatarState(data["state"]),
            expression=AvatarExpression(data["expression"]),
            metadata=data.get("metadata", {})
        )
        
        avatar.current_animation = data.get("current_animation")
        avatar.current_conversation = data.get("current_conversation")
        avatar.embedding_mode = AvatarEmbeddingMode(data["embedding_mode"])
        avatar.position = data.get("position")
        avatar.size = data.get("size", (1.0, 1.0))
        avatar.opacity = data.get("opacity", 1.0)
        avatar.z_index = data.get("z_index", 100)
        avatar.last_update = data.get("last_update", time.time())
        
        return avatar

class AvatarEmbeddingEngine:
    """
    Enables agent avatars to "step out" of their capsules for natural language conversations.
    
    This class provides:
    - Avatar emergence and return animations
    - Conversational capabilities for avatars
    - Expression and gesture management
    - Spatial positioning of emerged avatars
    - Integration with the Universal Skin Shell
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Avatar Embedding Engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.avatars: Dict[str, EmbeddedAvatar] = {}
        self.animations: Dict[str, AvatarAnimation] = {}
        self.conversations: Dict[str, AvatarConversation] = {}
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        
        # Initialize default animations
        self._initialize_default_animations()
        
    def _initialize_default_animations(self) -> None:
        """Initialize default avatar animations."""
        # Emerge animation
        self.register_animation(
            animation_id="default_emerge",
            animation_type=AvatarAnimationType.EMERGE,
            duration=0.8,
            keyframes=[
                {"time": 0.0, "opacity": 0.0, "scale": 0.5, "y": 20},
                {"time": 0.5, "opacity": 0.7, "scale": 0.8, "y": 10},
                {"time": 1.0, "opacity": 1.0, "scale": 1.0, "y": 0}
            ]
        )
        
        # Return animation
        self.register_animation(
            animation_id="default_return",
            animation_type=AvatarAnimationType.RETURN,
            duration=0.6,
            keyframes=[
                {"time": 0.0, "opacity": 1.0, "scale": 1.0, "y": 0},
                {"time": 0.5, "opacity": 0.7, "scale": 0.8, "y": 10},
                {"time": 1.0, "opacity": 0.0, "scale": 0.5, "y": 20}
            ]
        )
        
        # Speak animation
        self.register_animation(
            animation_id="default_speak",
            animation_type=AvatarAnimationType.SPEAK,
            duration=2.0,
            keyframes=[
                {"time": 0.0, "mouth_open": 0.0},
                {"time": 0.1, "mouth_open": 0.5},
                {"time": 0.2, "mouth_open": 0.2},
                {"time": 0.3, "mouth_open": 0.7},
                {"time": 0.4, "mouth_open": 0.3},
                {"time": 0.5, "mouth_open": 0.6},
                {"time": 0.6, "mouth_open": 0.2},
                {"time": 0.7, "mouth_open": 0.5},
                {"time": 0.8, "mouth_open": 0.1},
                {"time": 0.9, "mouth_open": 0.4},
                {"time": 1.0, "mouth_open": 0.0}
            ],
            loop=True
        )
        
        # Listen animation
        self.register_animation(
            animation_id="default_listen",
            animation_type=AvatarAnimationType.LISTEN,
            duration=3.0,
            keyframes=[
                {"time": 0.0, "head_tilt": 0.0},
                {"time": 0.3, "head_tilt": 0.1},
                {"time": 0.6, "head_tilt": -0.1},
                {"time": 1.0, "head_tilt": 0.0}
            ],
            loop=True
        )
        
        # Think animation
        self.register_animation(
            animation_id="default_think",
            animation_type=AvatarAnimationType.THINK,
            duration=4.0,
            keyframes=[
                {"time": 0.0, "head_tilt": 0.0, "eye_blink": 0.0},
                {"time": 0.1, "head_tilt": 0.0, "eye_blink": 1.0},
                {"time": 0.2, "head_tilt": 0.0, "eye_blink": 0.0},
                {"time": 0.5, "head_tilt": 0.1, "eye_blink": 0.0},
                {"time": 1.0, "head_tilt": 0.2, "eye_blink": 0.0},
                {"time": 1.5, "head_tilt": 0.1, "eye_blink": 0.0},
                {"time": 2.0, "head_tilt": 0.0, "eye_blink": 0.0},
                {"time": 2.1, "head_tilt": 0.0, "eye_blink": 1.0},
                {"time": 2.2, "head_tilt": 0.0, "eye_blink": 0.0},
                {"time": 2.5, "head_tilt": -0.1, "eye_blink": 0.0},
                {"time": 3.0, "head_tilt": -0.2, "eye_blink": 0.0},
                {"time": 3.5, "head_tilt": -0.1, "eye_blink": 0.0},
                {"time": 4.0, "head_tilt": 0.0, "eye_blink": 0.0}
            ],
            loop=True
        )
        
        # Idle animation
        self.register_animation(
            animation_id="default_idle",
            animation_type=AvatarAnimationType.IDLE,
            duration=5.0,
            keyframes=[
                {"time": 0.0, "body_sway": 0.0, "eye_blink": 0.0},
                {"time": 0.1, "body_sway": 0.0, "eye_blink": 1.0},
                {"time": 0.2, "body_sway": 0.0, "eye_blink": 0.0},
                {"time": 1.25, "body_sway": 0.05, "eye_blink": 0.0},
                {"time": 2.5, "body_sway": 0.0, "eye_blink": 0.0},
                {"time": 2.6, "body_sway": 0.0, "eye_blink": 1.0},
                {"time": 2.7, "body_sway": 0.0, "eye_blink": 0.0},
                {"time": 3.75, "body_sway": -0.05, "eye_blink": 0.0},
                {"time": 5.0, "body_sway": 0.0, "eye_blink": 0.0}
            ],
            loop=True
        )
        
        # Attention animation
        self.register_animation(
            animation_id="default_attention",
            animation_type=AvatarAnimationType.ATTENTION,
            duration=1.0,
            keyframes=[
                {"time": 0.0, "scale": 1.0, "glow": 0.0},
                {"time": 0.5, "scale": 1.1, "glow": 0.8},
                {"time": 1.0, "scale": 1.0, "glow": 0.0}
            ]
        )
        
        # Gesture animations
        self.register_animation(
            animation_id="gesture_point",
            animation_type=AvatarAnimationType.GESTURE,
            duration=1.5,
            keyframes=[
                {"time": 0.0, "arm_extend": 0.0, "finger_point": 0.0},
                {"time": 0.5, "arm_extend": 0.8, "finger_point": 0.5},
                {"time": 1.0, "arm_extend": 1.0, "finger_point": 1.0},
                {"time": 1.5, "arm_extend": 0.0, "finger_point": 0.0}
            ],
            metadata={"gesture": "point"}
        )
        
        self.register_animation(
            animation_id="gesture_wave",
            animation_type=AvatarAnimationType.GESTURE,
            duration=2.0,
            keyframes=[
                {"time": 0.0, "arm_raise": 0.0, "hand_wave": 0.0},
                {"time": 0.3, "arm_raise": 0.8, "hand_wave": 0.0},
                {"time": 0.5, "arm_raise": 1.0, "hand_wave": -0.5},
                {"time": 0.7, "arm_raise": 1.0, "hand_wave": 0.5},
                {"time": 0.9, "arm_raise": 1.0, "hand_wave": -0.5},
                {"time": 1.1, "arm_raise": 1.0, "hand_wave": 0.5},
                {"time": 1.3, "arm_raise": 1.0, "hand_wave": -0.5},
                {"time": 1.5, "arm_raise": 1.0, "hand_wave": 0.0},
                {"time": 2.0, "arm_raise": 0.0, "hand_wave": 0.0}
            ],
            metadata={"gesture": "wave"}
        )
        
    def register_animation(self,
                         animation_id: str,
                         animation_type: AvatarAnimationType,
                         duration: float,
                         keyframes: List[Dict[str, Any]],
                         loop: bool = False,
                         metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register an avatar animation.
        
        Args:
            animation_id: Unique identifier for this animation
            animation_type: Type of animation
            duration: Duration of the animation in seconds
            keyframes: List of keyframes for the animation
            loop: Whether the animation should loop
            metadata: Additional metadata for this animation
        """
        if animation_id in self.animations:
            self.logger.warning(f"Animation with ID {animation_id} already exists, overwriting")
            
        self.animations[animation_id] = AvatarAnimation(
            animation_id=animation_id,
            animation_type=animation_type,
            duration=duration,
            keyframes=keyframes,
            loop=loop,
            metadata=metadata or {}
        )
        
    def unregister_animation(self, animation_id: str) -> bool:
        """
        Unregister an avatar animation.
        
        Args:
            animation_id: ID of the animation to unregister
            
        Returns:
            True if the animation was unregistered, False if not found
        """
        if animation_id not in self.animations:
            return False
            
        del self.animations[animation_id]
        return True
    
    def register_avatar(self,
                      avatar_id: str,
                      name: str,
                      capsule_id: Optional[str],
                      avatar_type: str,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Register an avatar.
        
        Args:
            avatar_id: Unique identifier for this avatar
            name: Name of the avatar
            capsule_id: ID of the capsule this avatar is associated with (None if not associated)
            avatar_type: Type of avatar (e.g., "agent", "assistant", "expert")
            metadata: Additional metadata for this avatar
            
        Returns:
            ID of the registered avatar
        """
        if avatar_id in self.avatars:
            self.logger.warning(f"Avatar with ID {avatar_id} already exists, overwriting")
            
        self.avatars[avatar_id] = EmbeddedAvatar(
            avatar_id=avatar_id,
            name=name,
            capsule_id=capsule_id,
            avatar_type=avatar_type,
            metadata=metadata or {}
        )
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "avatar_registered",
            "avatar_id": avatar_id,
            "name": name,
            "capsule_id": capsule_id,
            "avatar_type": avatar_type
        })
        
        return avatar_id
    
    def unregister_avatar(self, avatar_id: str) -> bool:
        """
        Unregister an avatar.
        
        Args:
            avatar_id: ID of the avatar to unregister
            
        Returns:
            True if the avatar was unregistered, False if not found
        """
        if avatar_id not in self.avatars:
            return False
            
        # End any active conversations
        avatar = self.avatars[avatar_id]
        if avatar.current_conversation and avatar.current_conversation in self.conversations:
            self.end_conversation(avatar.current_conversation)
            
        # Delete avatar
        del self.avatars[avatar_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "avatar_unregistered",
            "avatar_id": avatar_id
        })
        
        return True
    
    def emerge_avatar(self,
                    avatar_id: str,
                    position: Optional[Tuple[float, float]] = None,
                    embedding_mode: AvatarEmbeddingMode = AvatarEmbeddingMode.FULL,
                    animation_id: Optional[str] = None) -> bool:
        """
        Make an avatar emerge from its capsule.
        
        Args:
            avatar_id: ID of the avatar to emerge
            position: Optional position for the emerged avatar (x, y)
            embedding_mode: Mode of embedding for the avatar
            animation_id: Optional ID of the animation to use (defaults to "default_emerge")
            
        Returns:
            True if the avatar emerged, False if not found
        """
        if avatar_id not in self.avatars:
            return False
            
        avatar = self.avatars[avatar_id]
        
        # Skip if already emerged
        if avatar.state != AvatarState.EMBEDDED and avatar.state != AvatarState.RETURNING:
            return True
            
        # Update avatar state
        avatar.state = AvatarState.EMERGING
        avatar.embedding_mode = embedding_mode
        avatar.position = position
        avatar.last_update = time.time()
        
        # Set animation
        animation_id = animation_id or "default_emerge"
        if animation_id in self.animations:
            avatar.current_animation = animation_id
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "avatar_emerging",
            "avatar_id": avatar_id,
            "embedding_mode": embedding_mode.value,
            "position": position,
            "animation_id": animation_id
        })
        
        return True
    
    def return_avatar(self,
                    avatar_id: str,
                    animation_id: Optional[str] = None) -> bool:
        """
        Make an avatar return to its capsule.
        
        Args:
            avatar_id: ID of the avatar to return
            animation_id: Optional ID of the animation to use (defaults to "default_return")
            
        Returns:
            True if the avatar is returning, False if not found
        """
        if avatar_id not in self.avatars:
            return False
            
        avatar = self.avatars[avatar_id]
        
        # Skip if already embedded
        if avatar.state == AvatarState.EMBEDDED:
            return True
            
        # End any active conversations
        if avatar.current_conversation and avatar.current_conversation in self.conversations:
            self.end_conversation(avatar.current_conversation)
            
        # Update avatar state
        avatar.state = AvatarState.RETURNING
        avatar.last_update = time.time()
        
        # Set animation
        animation_id = animation_id or "default_return"
        if animation_id in self.animations:
            avatar.current_animation = animation_id
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "avatar_returning",
            "avatar_id": avatar_id,
            "animation_id": animation_id
        })
        
        return True
    
    def set_avatar_state(self,
                       avatar_id: str,
                       state: AvatarState,
                       animation_id: Optional[str] = None) -> bool:
        """
        Set the state of an avatar.
        
        Args:
            avatar_id: ID of the avatar
            state: New state of the avatar
            animation_id: Optional ID of the animation to use
            
        Returns:
            True if the state was set, False if the avatar was not found
        """
        if avatar_id not in self.avatars:
            return False
            
        avatar = self.avatars[avatar_id]
        old_state = avatar.state
        
        # Update avatar state
        avatar.state = state
        avatar.last_update = time.time()
        
        # Set animation if provided
        if animation_id and animation_id in self.animations:
            avatar.current_animation = animation_id
        else:
            # Set default animation based on state
            if state == AvatarState.CONVERSING:
                avatar.current_animation = "default_speak"
            elif state == AvatarState.LISTENING:
                avatar.current_animation = "default_listen"
            elif state == AvatarState.THINKING:
                avatar.current_animation = "default_think"
            elif state == AvatarState.IDLE:
                avatar.current_animation = "default_idle"
                
        # Dispatch event
        self._dispatch_event({
            "event_type": "avatar_state_changed",
            "avatar_id": avatar_id,
            "old_state": old_state.value,
            "new_state": state.value,
            "animation_id": avatar.current_animation
        })
        
        return True
    
    def set_avatar_expression(self,
                            avatar_id: str,
                            expression: AvatarExpression) -> bool:
        """
        Set the expression of an avatar.
        
        Args:
            avatar_id: ID of the avatar
            expression: New expression of the avatar
            
        Returns:
            True if the expression was set, False if the avatar was not found
        """
        if avatar_id not in self.avatars:
            return False
            
        avatar = self.avatars[avatar_id]
        old_expression = avatar.expression
        
        # Update avatar expression
        avatar.expression = expression
        avatar.last_update = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "avatar_expression_changed",
            "avatar_id": avatar_id,
            "old_expression": old_expression.value,
            "new_expression": expression.value
        })
        
        return True
    
    def perform_gesture(self,
                      avatar_id: str,
                      gesture: AvatarGesture,
                      animation_id: Optional[str] = None) -> bool:
        """
        Make an avatar perform a gesture.
        
        Args:
            avatar_id: ID of the avatar
            gesture: Gesture to perform
            animation_id: Optional ID of the animation to use (defaults to gesture-specific animation)
            
        Returns:
            True if the gesture was performed, False if the avatar was not found
        """
        if avatar_id not in self.avatars:
            return False
            
        avatar = self.avatars[avatar_id]
        
        # Skip if embedded
        if avatar.state == AvatarState.EMBEDDED or avatar.state == AvatarState.RETURNING:
            return False
            
        # Determine animation ID
        if animation_id is None:
            animation_id = f"gesture_{gesture.value}"
            
        # Set animation if it exists
        if animation_id in self.animations:
            avatar.current_animation = animation_id
            avatar.last_update = time.time()
            
            # Dispatch event
            self._dispatch_event({
                "event_type": "avatar_gesture",
                "avatar_id": avatar_id,
                "gesture": gesture.value,
                "animation_id": animation_id
            })
            
            return True
        else:
            self.logger.warning(f"Animation {animation_id} not found for gesture {gesture.value}")
            return False
    
    def start_conversation(self,
                         avatar_id: str,
                         mode: AvatarConversationMode,
                         participants: List[str],
                         metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Start a conversation involving an avatar.
        
        Args:
            avatar_id: ID of the avatar
            mode: Conversation mode
            participants: List of participant IDs (can include user IDs and other avatar IDs)
            metadata: Additional metadata for this conversation
            
        Returns:
            ID of the created conversation, or None if the avatar was not found
        """
        if avatar_id not in self.avatars:
            return None
            
        avatar = self.avatars[avatar_id]
        
        # End any active conversations
        if avatar.current_conversation and avatar.current_conversation in self.conversations:
            self.end_conversation(avatar.current_conversation)
            
        # Create conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Create conversation
        self.conversations[conversation_id] = AvatarConversation(
            conversation_id=conversation_id,
            avatar_id=avatar_id,
            mode=mode,
            start_time=time.time(),
            participants=participants,
            metadata=metadata or {}
        )
        
        # Update avatar state
        avatar.current_conversation = conversation_id
        self.set_avatar_state(avatar_id, AvatarState.CONVERSING)
        
        # Ensure avatar is emerged
        if avatar.state == AvatarState.EMBEDDED:
            self.emerge_avatar(avatar_id)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "conversation_started",
            "conversation_id": conversation_id,
            "avatar_id": avatar_id,
            "mode": mode.value,
            "participants": participants
        })
        
        return conversation_id
    
    def end_conversation(self, conversation_id: str) -> bool:
        """
        End a conversation.
        
        Args:
            conversation_id: ID of the conversation to end
            
        Returns:
            True if the conversation was ended, False if not found
        """
        if conversation_id not in self.conversations:
            return False
            
        conversation = self.conversations[conversation_id]
        
        # End conversation
        conversation.end_conversation()
        
        # Update avatar state
        avatar_id = conversation.avatar_id
        if avatar_id in self.avatars:
            avatar = self.avatars[avatar_id]
            if avatar.current_conversation == conversation_id:
                avatar.current_conversation = None
                self.set_avatar_state(avatar_id, AvatarState.IDLE)
                
        # Dispatch event
        self._dispatch_event({
            "event_type": "conversation_ended",
            "conversation_id": conversation_id,
            "avatar_id": avatar_id
        })
        
        return True
    
    def add_message_to_conversation(self,
                                  conversation_id: str,
                                  sender_id: str,
                                  content: str,
                                  metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            sender_id: ID of the message sender
            content: Message content
            metadata: Additional metadata for this message
            
        Returns:
            ID of the created message, or None if the conversation was not found
        """
        if conversation_id not in self.conversations:
            return None
            
        conversation = self.conversations[conversation_id]
        
        # Skip if conversation is not active
        if not conversation.is_active:
            return None
            
        # Add message
        message_id = conversation.add_message(
            sender_id=sender_id,
            content=content,
            metadata=metadata
        )
        
        # Update avatar state based on sender
        avatar_id = conversation.avatar_id
        if avatar_id in self.avatars:
            avatar = self.avatars[avatar_id]
            
            if sender_id == avatar_id:
                # Avatar is speaking
                self.set_avatar_state(avatar_id, AvatarState.CONVERSING)
            else:
                # Avatar is listening
                self.set_avatar_state(avatar_id, AvatarState.LISTENING)
                
        # Dispatch event
        self._dispatch_event({
            "event_type": "conversation_message",
            "conversation_id": conversation_id,
            "message_id": message_id,
            "sender_id": sender_id,
            "content": content
        })
        
        return message_id
    
    def update(self, dt: float) -> None:
        """
        Update all avatars and animations.
        
        Args:
            dt: Time step in seconds
        """
        current_time = time.time()
        
        # Update each avatar
        for avatar_id, avatar in self.avatars.items():
            # Handle state transitions
            if avatar.state == AvatarState.EMERGING:
                # Check if emerge animation is complete
                if avatar.current_animation and avatar.current_animation in self.animations:
                    animation = self.animations[avatar.current_animation]
                    elapsed = current_time - avatar.last_update
                    
                    if elapsed >= animation.duration:
                        # Transition to idle state
                        self.set_avatar_state(avatar_id, AvatarState.IDLE)
                        
            elif avatar.state == AvatarState.RETURNING:
                # Check if return animation is complete
                if avatar.current_animation and avatar.current_animation in self.animations:
                    animation = self.animations[avatar.current_animation]
                    elapsed = current_time - avatar.last_update
                    
                    if elapsed >= animation.duration:
                        # Transition to embedded state
                        avatar.state = AvatarState.EMBEDDED
                        avatar.current_animation = None
                        avatar.position = None
                        avatar.last_update = current_time
                        
                        # Dispatch event
                        self._dispatch_event({
                            "event_type": "avatar_embedded",
                            "avatar_id": avatar_id
                        })
                        
        # Clean up completed conversations
        for conversation_id in list(self.conversations.keys()):
            conversation = self.conversations[conversation_id]
            
            if not conversation.is_active and current_time - conversation.end_time > 3600:  # 1 hour
                del self.conversations[conversation_id]
                
    def get_avatar(self, avatar_id: str) -> Optional[EmbeddedAvatar]:
        """
        Get an avatar by ID.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            The avatar, or None if not found
        """
        return self.avatars.get(avatar_id)
    
    def get_all_avatars(self) -> List[EmbeddedAvatar]:
        """
        Get all avatars.
        
        Returns:
            List of all avatars
        """
        return list(self.avatars.values())
    
    def get_conversation(self, conversation_id: str) -> Optional[AvatarConversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            The conversation, or None if not found
        """
        return self.conversations.get(conversation_id)
    
    def get_active_conversations(self) -> List[AvatarConversation]:
        """
        Get all active conversations.
        
        Returns:
            List of all active conversations
        """
        return [c for c in self.conversations.values() if c.is_active]
    
    def get_avatar_by_capsule(self, capsule_id: str) -> Optional[EmbeddedAvatar]:
        """
        Get an avatar by its associated capsule ID.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            The avatar, or None if not found
        """
        for avatar in self.avatars.values():
            if avatar.capsule_id == capsule_id:
                return avatar
                
        return None
    
    def get_animation(self, animation_id: str) -> Optional[AvatarAnimation]:
        """
        Get an animation by ID.
        
        Args:
            animation_id: ID of the animation
            
        Returns:
            The animation, or None if not found
        """
        return self.animations.get(animation_id)
    
    def get_avatar_css(self, avatar_id: str) -> Optional[str]:
        """
        Get CSS representation of an avatar for web rendering.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            CSS string for the avatar, or None if not found
        """
        avatar = self.get_avatar(avatar_id)
        if not avatar:
            return None
            
        css_parts = []
        
        # Base styles
        css_parts.append(f"opacity: {avatar.opacity};")
        css_parts.append(f"z-index: {avatar.z_index};")
        
        if avatar.position:
            x, y = avatar.position
            css_parts.append(f"position: absolute;")
            css_parts.append(f"left: {x}px;")
            css_parts.append(f"top: {y}px;")
            
        width, height = avatar.size
        css_parts.append(f"width: {width * 100}%;")
        css_parts.append(f"height: {height * 100}%;")
        
        # Animation
        if avatar.current_animation and avatar.current_animation in self.animations:
            animation = self.animations[avatar.current_animation]
            
            if animation.animation_type == AvatarAnimationType.EMERGE:
                css_parts.append("animation: avatar-emerge 0.8s ease-out forwards;")
            elif animation.animation_type == AvatarAnimationType.RETURN:
                css_parts.append("animation: avatar-return 0.6s ease-in forwards;")
            elif animation.animation_type == AvatarAnimationType.SPEAK:
                css_parts.append("animation: avatar-speak 2s ease-in-out infinite;")
            elif animation.animation_type == AvatarAnimationType.LISTEN:
                css_parts.append("animation: avatar-listen 3s ease-in-out infinite;")
            elif animation.animation_type == AvatarAnimationType.THINK:
                css_parts.append("animation: avatar-think 4s ease-in-out infinite;")
            elif animation.animation_type == AvatarAnimationType.IDLE:
                css_parts.append("animation: avatar-idle 5s ease-in-out infinite;")
            elif animation.animation_type == AvatarAnimationType.ATTENTION:
                css_parts.append("animation: avatar-attention 1s ease-in-out;")
            elif animation.animation_type == AvatarAnimationType.GESTURE:
                gesture = animation.metadata.get("gesture", "custom")
                css_parts.append(f"animation: avatar-gesture-{gesture} {animation.duration}s ease-in-out;")
                
        # Expression
        if avatar.expression == AvatarExpression.HAPPY:
            css_parts.append("--mouth-curve: 0.3;")
            css_parts.append("--eye-openness: 0.8;")
        elif avatar.expression == AvatarExpression.CONCERNED:
            css_parts.append("--mouth-curve: -0.1;")
            css_parts.append("--eye-openness: 0.7;")
            css_parts.append("--brow-angle: -0.2;")
        elif avatar.expression == AvatarExpression.CONFUSED:
            css_parts.append("--mouth-curve: 0;")
            css_parts.append("--eye-openness: 0.8;")
            css_parts.append("--brow-angle: 0.3;")
            css_parts.append("--head-tilt: 0.1;")
        elif avatar.expression == AvatarExpression.FOCUSED:
            css_parts.append("--mouth-curve: 0;")
            css_parts.append("--eye-openness: 0.9;")
            css_parts.append("--brow-angle: -0.1;")
        elif avatar.expression == AvatarExpression.EXCITED:
            css_parts.append("--mouth-curve: 0.4;")
            css_parts.append("--eye-openness: 1.0;")
            css_parts.append("--brow-angle: 0.2;")
        elif avatar.expression == AvatarExpression.THOUGHTFUL:
            css_parts.append("--mouth-curve: 0.1;")
            css_parts.append("--eye-openness: 0.7;")
            css_parts.append("--brow-angle: -0.1;")
            css_parts.append("--head-tilt: 0.2;")
            
        return "\n".join(css_parts)
    
    def get_avatar_keyframes(self, avatar_id: str) -> Optional[str]:
        """
        Get CSS keyframes for an avatar for web rendering.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            CSS keyframes string for the avatar, or None if not found
        """
        avatar = self.get_avatar(avatar_id)
        if not avatar or not avatar.current_animation or avatar.current_animation not in self.animations:
            return None
            
        animation = self.animations[avatar.current_animation]
        keyframes = []
        
        if animation.animation_type == AvatarAnimationType.EMERGE:
            keyframes.append("@keyframes avatar-emerge {")
            keyframes.append("  0% { opacity: 0; transform: scale(0.5) translateY(20px); }")
            keyframes.append("  50% { opacity: 0.7; transform: scale(0.8) translateY(10px); }")
            keyframes.append("  100% { opacity: 1; transform: scale(1) translateY(0); }")
            keyframes.append("}")
            
        elif animation.animation_type == AvatarAnimationType.RETURN:
            keyframes.append("@keyframes avatar-return {")
            keyframes.append("  0% { opacity: 1; transform: scale(1) translateY(0); }")
            keyframes.append("  50% { opacity: 0.7; transform: scale(0.8) translateY(10px); }")
            keyframes.append("  100% { opacity: 0; transform: scale(0.5) translateY(20px); }")
            keyframes.append("}")
            
        elif animation.animation_type == AvatarAnimationType.SPEAK:
            keyframes.append("@keyframes avatar-speak {")
            keyframes.append("  0% { --mouth-open: 0; }")
            keyframes.append("  10% { --mouth-open: 0.5; }")
            keyframes.append("  20% { --mouth-open: 0.2; }")
            keyframes.append("  30% { --mouth-open: 0.7; }")
            keyframes.append("  40% { --mouth-open: 0.3; }")
            keyframes.append("  50% { --mouth-open: 0.6; }")
            keyframes.append("  60% { --mouth-open: 0.2; }")
            keyframes.append("  70% { --mouth-open: 0.5; }")
            keyframes.append("  80% { --mouth-open: 0.1; }")
            keyframes.append("  90% { --mouth-open: 0.4; }")
            keyframes.append("  100% { --mouth-open: 0; }")
            keyframes.append("}")
            
        elif animation.animation_type == AvatarAnimationType.LISTEN:
            keyframes.append("@keyframes avatar-listen {")
            keyframes.append("  0% { --head-tilt: 0; }")
            keyframes.append("  30% { --head-tilt: 0.1; }")
            keyframes.append("  60% { --head-tilt: -0.1; }")
            keyframes.append("  100% { --head-tilt: 0; }")
            keyframes.append("}")
            
        elif animation.animation_type == AvatarAnimationType.THINK:
            keyframes.append("@keyframes avatar-think {")
            keyframes.append("  0% { --head-tilt: 0; --eye-blink: 0; }")
            keyframes.append("  2.5% { --head-tilt: 0; --eye-blink: 1; }")
            keyframes.append("  5% { --head-tilt: 0; --eye-blink: 0; }")
            keyframes.append("  12.5% { --head-tilt: 0.1; --eye-blink: 0; }")
            keyframes.append("  25% { --head-tilt: 0.2; --eye-blink: 0; }")
            keyframes.append("  37.5% { --head-tilt: 0.1; --eye-blink: 0; }")
            keyframes.append("  50% { --head-tilt: 0; --eye-blink: 0; }")
            keyframes.append("  52.5% { --head-tilt: 0; --eye-blink: 1; }")
            keyframes.append("  55% { --head-tilt: 0; --eye-blink: 0; }")
            keyframes.append("  62.5% { --head-tilt: -0.1; --eye-blink: 0; }")
            keyframes.append("  75% { --head-tilt: -0.2; --eye-blink: 0; }")
            keyframes.append("  87.5% { --head-tilt: -0.1; --eye-blink: 0; }")
            keyframes.append("  100% { --head-tilt: 0; --eye-blink: 0; }")
            keyframes.append("}")
            
        elif animation.animation_type == AvatarAnimationType.IDLE:
            keyframes.append("@keyframes avatar-idle {")
            keyframes.append("  0% { --body-sway: 0; --eye-blink: 0; }")
            keyframes.append("  2% { --body-sway: 0; --eye-blink: 1; }")
            keyframes.append("  4% { --body-sway: 0; --eye-blink: 0; }")
            keyframes.append("  25% { --body-sway: 0.05; --eye-blink: 0; }")
            keyframes.append("  50% { --body-sway: 0; --eye-blink: 0; }")
            keyframes.append("  52% { --body-sway: 0; --eye-blink: 1; }")
            keyframes.append("  54% { --body-sway: 0; --eye-blink: 0; }")
            keyframes.append("  75% { --body-sway: -0.05; --eye-blink: 0; }")
            keyframes.append("  100% { --body-sway: 0; --eye-blink: 0; }")
            keyframes.append("}")
            
        elif animation.animation_type == AvatarAnimationType.ATTENTION:
            keyframes.append("@keyframes avatar-attention {")
            keyframes.append("  0% { transform: scale(1); filter: drop-shadow(0 0 0 rgba(255, 255, 255, 0)); }")
            keyframes.append("  50% { transform: scale(1.1); filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.8)); }")
            keyframes.append("  100% { transform: scale(1); filter: drop-shadow(0 0 0 rgba(255, 255, 255, 0)); }")
            keyframes.append("}")
            
        elif animation.animation_type == AvatarAnimationType.GESTURE:
            gesture = animation.metadata.get("gesture", "custom")
            
            if gesture == "point":
                keyframes.append("@keyframes avatar-gesture-point {")
                keyframes.append("  0% { --arm-extend: 0; --finger-point: 0; }")
                keyframes.append("  33% { --arm-extend: 0.8; --finger-point: 0.5; }")
                keyframes.append("  67% { --arm-extend: 1.0; --finger-point: 1.0; }")
                keyframes.append("  100% { --arm-extend: 0; --finger-point: 0; }")
                keyframes.append("}")
                
            elif gesture == "wave":
                keyframes.append("@keyframes avatar-gesture-wave {")
                keyframes.append("  0% { --arm-raise: 0; --hand-wave: 0; }")
                keyframes.append("  15% { --arm-raise: 0.8; --hand-wave: 0; }")
                keyframes.append("  25% { --arm-raise: 1.0; --hand-wave: -0.5; }")
                keyframes.append("  35% { --arm-raise: 1.0; --hand-wave: 0.5; }")
                keyframes.append("  45% { --arm-raise: 1.0; --hand-wave: -0.5; }")
                keyframes.append("  55% { --arm-raise: 1.0; --hand-wave: 0.5; }")
                keyframes.append("  65% { --arm-raise: 1.0; --hand-wave: -0.5; }")
                keyframes.append("  75% { --arm-raise: 1.0; --hand-wave: 0; }")
                keyframes.append("  100% { --arm-raise: 0; --hand-wave: 0; }")
                keyframes.append("}")
                
        return "\n".join(keyframes)
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for avatar events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for avatar events.
        
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
"""
