"""
Avatar Animation Controller Module for the UI/UX Layer of Industriverse

This module provides animation control capabilities for avatars in the UI/UX Layer,
managing animation sequences, transitions, and expressions for avatar representations.

The Avatar Animation Controller is responsible for:
1. Managing avatar animation states and transitions
2. Coordinating complex animation sequences
3. Synchronizing animations across multiple avatars
4. Providing animation presets and templates
5. Handling animation events and callbacks

This module works closely with the Avatar Expression Engine and Avatar Personality Engine
to create cohesive and expressive avatar animations that reflect agent states and behaviors.
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from enum import Enum
import json
import math

from .avatar_expression_engine import AvatarExpressionEngine
from .avatar_personality_engine import AvatarPersonalityEngine
from .agent_state_visualizer import AgentStateVisualizer

logger = logging.getLogger(__name__)

class AnimationType(Enum):
    """Enumeration of animation types."""
    IDLE = "idle"
    ACTIVE = "active"
    SPEAKING = "speaking"
    LISTENING = "listening"
    THINKING = "thinking"
    TRANSITIONING = "transitioning"
    APPEARING = "appearing"
    DISAPPEARING = "disappearing"
    CELEBRATING = "celebrating"
    WARNING = "warning"
    ERROR = "error"
    CUSTOM = "custom"


class AnimationEasing(Enum):
    """Enumeration of animation easing functions."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    BACK = "back"


class AvatarAnimationController:
    """
    Controls animations for avatars in the UI/UX Layer.
    
    This class provides methods for managing animation states, coordinating sequences,
    synchronizing animations, and handling animation events.
    """

    def __init__(
        self,
        avatar_expression_engine: AvatarExpressionEngine,
        avatar_personality_engine: AvatarPersonalityEngine,
        agent_state_visualizer: AgentStateVisualizer
    ):
        """
        Initialize the AvatarAnimationController.
        
        Args:
            avatar_expression_engine: Engine for avatar expressions
            avatar_personality_engine: Engine for avatar personalities
            agent_state_visualizer: Visualizer for agent states
        """
        self.avatar_expression_engine = avatar_expression_engine
        self.avatar_personality_engine = avatar_personality_engine
        self.agent_state_visualizer = agent_state_visualizer
        
        # Initialize animation state tracking
        self.animation_states = {}
        self.active_animations = {}
        self.animation_sequences = {}
        self.animation_callbacks = {}
        self.animation_presets = self._initialize_animation_presets()
        
        logger.info("AvatarAnimationController initialized")

    def _initialize_animation_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize animation presets.
        
        Returns:
            Dictionary of animation presets
        """
        return {
            "greeting": {
                "type": AnimationType.APPEARING.value,
                "duration": 1.0,
                "easing": AnimationEasing.EASE_OUT.value,
                "keyframes": [
                    {"time": 0.0, "scale": 0.0, "opacity": 0.0, "rotation": 0},
                    {"time": 0.5, "scale": 1.2, "opacity": 0.8, "rotation": 10},
                    {"time": 1.0, "scale": 1.0, "opacity": 1.0, "rotation": 0}
                ],
                "expression": "friendly",
                "expression_intensity": 0.8
            },
            "farewell": {
                "type": AnimationType.DISAPPEARING.value,
                "duration": 0.8,
                "easing": AnimationEasing.EASE_IN.value,
                "keyframes": [
                    {"time": 0.0, "scale": 1.0, "opacity": 1.0, "rotation": 0},
                    {"time": 0.4, "scale": 1.1, "opacity": 0.7, "rotation": -5},
                    {"time": 0.8, "scale": 0.0, "opacity": 0.0, "rotation": -10}
                ],
                "expression": "satisfied",
                "expression_intensity": 0.6
            },
            "thinking": {
                "type": AnimationType.THINKING.value,
                "duration": 2.0,
                "easing": AnimationEasing.EASE_IN_OUT.value,
                "keyframes": [
                    {"time": 0.0, "scale": 1.0, "opacity": 1.0, "pulse": 0.0},
                    {"time": 0.5, "scale": 0.95, "opacity": 0.9, "pulse": 0.5},
                    {"time": 1.0, "scale": 1.0, "opacity": 1.0, "pulse": 1.0},
                    {"time": 1.5, "scale": 0.95, "opacity": 0.9, "pulse": 0.5},
                    {"time": 2.0, "scale": 1.0, "opacity": 1.0, "pulse": 0.0}
                ],
                "expression": "thoughtful",
                "expression_intensity": 0.7,
                "loop": True
            },
            "success": {
                "type": AnimationType.CELEBRATING.value,
                "duration": 1.5,
                "easing": AnimationEasing.BOUNCE.value,
                "keyframes": [
                    {"time": 0.0, "scale": 1.0, "opacity": 1.0, "y": 0},
                    {"time": 0.3, "scale": 1.1, "opacity": 1.0, "y": -10},
                    {"time": 0.6, "scale": 1.0, "opacity": 1.0, "y": 0},
                    {"time": 0.9, "scale": 1.1, "opacity": 1.0, "y": -5},
                    {"time": 1.2, "scale": 1.0, "opacity": 1.0, "y": 0},
                    {"time": 1.5, "scale": 1.0, "opacity": 1.0, "y": 0}
                ],
                "expression": "excited",
                "expression_intensity": 0.9
            },
            "error": {
                "type": AnimationType.ERROR.value,
                "duration": 0.8,
                "easing": AnimationEasing.BACK.value,
                "keyframes": [
                    {"time": 0.0, "scale": 1.0, "opacity": 1.0, "x": 0},
                    {"time": 0.1, "scale": 1.0, "opacity": 1.0, "x": -5},
                    {"time": 0.3, "scale": 1.0, "opacity": 1.0, "x": 5},
                    {"time": 0.5, "scale": 1.0, "opacity": 1.0, "x": -3},
                    {"time": 0.7, "scale": 1.0, "opacity": 1.0, "x": 2},
                    {"time": 0.8, "scale": 1.0, "opacity": 1.0, "x": 0}
                ],
                "expression": "concerned",
                "expression_intensity": 0.8
            },
            "idle": {
                "type": AnimationType.IDLE.value,
                "duration": 4.0,
                "easing": AnimationEasing.EASE_IN_OUT.value,
                "keyframes": [
                    {"time": 0.0, "scale": 1.00, "opacity": 1.0, "y": 0},
                    {"time": 1.0, "scale": 0.98, "opacity": 0.98, "y": 1},
                    {"time": 2.0, "scale": 1.00, "opacity": 1.0, "y": 0},
                    {"time": 3.0, "scale": 0.98, "opacity": 0.98, "y": 1},
                    {"time": 4.0, "scale": 1.00, "opacity": 1.0, "y": 0}
                ],
                "expression": "neutral",
                "expression_intensity": 0.3,
                "loop": True
            },
            "speaking": {
                "type": AnimationType.SPEAKING.value,
                "duration": 1.0,
                "easing": AnimationEasing.LINEAR.value,
                "keyframes": [
                    {"time": 0.0, "scale": 1.00, "opacity": 1.0, "pulse": 0.0},
                    {"time": 0.2, "scale": 1.03, "opacity": 1.0, "pulse": 0.5},
                    {"time": 0.5, "scale": 1.00, "opacity": 1.0, "pulse": 1.0},
                    {"time": 0.7, "scale": 1.02, "opacity": 1.0, "pulse": 0.7},
                    {"time": 1.0, "scale": 1.00, "opacity": 1.0, "pulse": 0.0}
                ],
                "expression": "engaged",
                "expression_intensity": 0.6,
                "loop": True
            },
            "listening": {
                "type": AnimationType.LISTENING.value,
                "duration": 2.0,
                "easing": AnimationEasing.EASE_IN_OUT.value,
                "keyframes": [
                    {"time": 0.0, "scale": 1.00, "opacity": 1.0, "tilt": 0},
                    {"time": 0.5, "scale": 1.00, "opacity": 1.0, "tilt": 2},
                    {"time": 1.0, "scale": 1.00, "opacity": 1.0, "tilt": 0},
                    {"time": 1.5, "scale": 1.00, "opacity": 1.0, "tilt": -2},
                    {"time": 2.0, "scale": 1.00, "opacity": 1.0, "tilt": 0}
                ],
                "expression": "attentive",
                "expression_intensity": 0.7,
                "loop": True
            }
        }

    def animate(
        self,
        avatar_id: str,
        animation_type: AnimationType,
        duration: float = 1.0,
        easing: AnimationEasing = AnimationEasing.EASE_IN_OUT,
        keyframes: Optional[List[Dict[str, Any]]] = None,
        expression: Optional[str] = None,
        expression_intensity: float = 0.7,
        loop: bool = False,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Animate an avatar.
        
        Args:
            avatar_id: ID of the avatar to animate
            animation_type: Type of animation
            duration: Duration of animation in seconds
            easing: Easing function for animation
            keyframes: Optional keyframes for animation
            expression: Optional expression to show during animation
            expression_intensity: Intensity of expression
            loop: Whether to loop the animation
            callback: Optional callback function to call when animation completes
            
        Returns:
            Animation ID for tracking
        """
        # Generate animation ID
        animation_id = str(uuid.uuid4())
        
        # Create default keyframes if not provided
        if keyframes is None:
            keyframes = [
                {"time": 0.0, "scale": 1.0, "opacity": 1.0},
                {"time": duration, "scale": 1.0, "opacity": 1.0}
            ]
        
        # Create animation record
        animation = {
            "id": animation_id,
            "avatar_id": avatar_id,
            "type": animation_type.value,
            "duration": duration,
            "easing": easing.value,
            "keyframes": keyframes,
            "expression": expression,
            "expression_intensity": expression_intensity,
            "loop": loop,
            "start_time": time.time(),
            "end_time": time.time() + duration,
            "status": "running"
        }
        
        # Store animation
        self.active_animations[animation_id] = animation
        
        # Store callback if provided
        if callback:
            self.animation_callbacks[animation_id] = callback
        
        # Update animation state for avatar
        self.animation_states[avatar_id] = {
            "current_animation": animation_id,
            "animation_type": animation_type.value,
            "start_time": time.time(),
            "duration": duration,
            "loop": loop
        }
        
        # Apply expression if provided
        if expression:
            self.avatar_expression_engine.express_emotion(
                avatar_id,
                expression,
                intensity=expression_intensity,
                duration=duration
            )
        
        # Schedule animation completion if not looping
        if not loop:
            # In a real implementation, this would use a proper scheduler
            # For simplicity, we'll use a timer thread
            import threading
            threading.Timer(
                duration,
                lambda: self._complete_animation(animation_id)
            ).start()
        
        logger.debug(f"Started animation {animation_id} of type {animation_type.value} for avatar {avatar_id}")
        return animation_id

    def animate_with_preset(
        self,
        avatar_id: str,
        preset_name: str,
        override_params: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Animate an avatar using a preset.
        
        Args:
            avatar_id: ID of the avatar to animate
            preset_name: Name of the animation preset
            override_params: Optional parameters to override in the preset
            callback: Optional callback function to call when animation completes
            
        Returns:
            Animation ID for tracking
        """
        if preset_name not in self.animation_presets:
            logger.warning(f"Unknown animation preset: {preset_name}")
            return ""
        
        # Get preset
        preset = self.animation_presets[preset_name].copy()
        
        # Override parameters if provided
        if override_params:
            preset.update(override_params)
        
        # Extract parameters
        animation_type = AnimationType(preset["type"])
        duration = preset["duration"]
        easing = AnimationEasing(preset["easing"])
        keyframes = preset["keyframes"]
        expression = preset.get("expression")
        expression_intensity = preset.get("expression_intensity", 0.7)
        loop = preset.get("loop", False)
        
        # Animate avatar
        return self.animate(
            avatar_id=avatar_id,
            animation_type=animation_type,
            duration=duration,
            easing=easing,
            keyframes=keyframes,
            expression=expression,
            expression_intensity=expression_intensity,
            loop=loop,
            callback=callback
        )

    def stop_animation(self, animation_id: str) -> bool:
        """
        Stop an active animation.
        
        Args:
            animation_id: ID of the animation to stop
            
        Returns:
            True if animation was stopped, False otherwise
        """
        if animation_id not in self.active_animations:
            logger.warning(f"Unknown animation ID: {animation_id}")
            return False
        
        # Get animation data
        animation = self.active_animations[animation_id]
        avatar_id = animation["avatar_id"]
        
        # Update animation status
        animation["status"] = "stopped"
        animation["end_time"] = time.time()
        
        # Update animation state for avatar
        if avatar_id in self.animation_states and self.animation_states[avatar_id]["current_animation"] == animation_id:
            self.animation_states[avatar_id] = {
                "current_animation": None,
                "animation_type": None,
                "start_time": None,
                "duration": None,
                "loop": False
            }
        
        # Remove from active animations
        del self.active_animations[animation_id]
        
        # Remove callback if registered
        if animation_id in self.animation_callbacks:
            del self.animation_callbacks[animation_id]
        
        logger.debug(f"Stopped animation {animation_id} for avatar {avatar_id}")
        return True

    def stop_all_animations_for_avatar(self, avatar_id: str) -> int:
        """
        Stop all active animations for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            Number of animations stopped
        """
        # Find all animations for this avatar
        animations_to_stop = []
        
        for animation_id, animation in self.active_animations.items():
            if animation["avatar_id"] == avatar_id:
                animations_to_stop.append(animation_id)
        
        # Stop each animation
        for animation_id in animations_to_stop:
            self.stop_animation(animation_id)
        
        # Update animation state for avatar
        if avatar_id in self.animation_states:
            self.animation_states[avatar_id] = {
                "current_animation": None,
                "animation_type": None,
                "start_time": None,
                "duration": None,
                "loop": False
            }
        
        logger.debug(f"Stopped {len(animations_to_stop)} animations for avatar {avatar_id}")
        return len(animations_to_stop)

    def _complete_animation(self, animation_id: str):
        """
        Complete an animation.
        
        Args:
            animation_id: ID of the animation
        """
        if animation_id not in self.active_animations:
            return
        
        # Get animation data
        animation = self.active_animations[animation_id]
        avatar_id = animation["avatar_id"]
        
        # Check if animation is looping
        if animation["loop"]:
            # Update start time for next loop
            animation["start_time"] = time.time()
            animation["end_time"] = time.time() + animation["duration"]
            return
        
        # Update animation status
        animation["status"] = "completed"
        animation["end_time"] = time.time()
        
        # Update animation state for avatar
        if avatar_id in self.animation_states and self.animation_states[avatar_id]["current_animation"] == animation_id:
            self.animation_states[avatar_id] = {
                "current_animation": None,
                "animation_type": None,
                "start_time": None,
                "duration": None,
                "loop": False
            }
        
        # Call callback if registered
        if animation_id in self.animation_callbacks:
            callback = self.animation_callbacks[animation_id]
            try:
                callback(animation)
            except Exception as e:
                logger.error(f"Error in animation callback: {e}")
            
            # Remove callback after calling
            del self.animation_callbacks[animation_id]
        
        # Remove from active animations
        del self.active_animations[animation_id]
        
        logger.debug(f"Completed animation {animation_id} for avatar {avatar_id}")

    def create_animation_sequence(
        self,
        avatar_id: str,
        animations: List[Dict[str, Any]],
        loop_sequence: bool = False,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Create a sequence of animations for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            animations: List of animation definitions
            loop_sequence: Whether to loop the sequence
            callback: Optional callback function to call when sequence completes
            
        Returns:
            Sequence ID for tracking
        """
        # Generate sequence ID
        sequence_id = str(uuid.uuid4())
        
        # Create sequence record
        sequence = {
            "id": sequence_id,
            "avatar_id": avatar_id,
            "animations": animations,
            "current_index": 0,
            "loop": loop_sequence,
            "start_time": time.time(),
            "status": "running"
        }
        
        # Store sequence
        self.animation_sequences[sequence_id] = sequence
        
        # Store callback if provided
        if callback:
            self.animation_callbacks[sequence_id] = callback
        
        # Start first animation in sequence
        self._play_next_in_sequence(sequence_id)
        
        logger.debug(f"Started animation sequence {sequence_id} for avatar {avatar_id}")
        return sequence_id

    def _play_next_in_sequence(self, sequence_id: str):
        """
        Play the next animation in a sequence.
        
        Args:
            sequence_id: ID of the sequence
        """
        if sequence_id not in self.animation_sequences:
            return
        
        # Get sequence data
        sequence = self.animation_sequences[sequence_id]
        avatar_id = sequence["avatar_id"]
        current_index = sequence["current_index"]
        animations = sequence["animations"]
        
        # Check if sequence is complete
        if current_index >= len(animations):
            if sequence["loop"]:
                # Reset index for next loop
                sequence["current_index"] = 0
                self._play_next_in_sequence(sequence_id)
            else:
                # Complete sequence
                self._complete_sequence(sequence_id)
            return
        
        # Get current animation definition
        animation_def = animations[current_index]
        
        # Extract parameters
        animation_type = AnimationType(animation_def.get("type", AnimationType.CUSTOM.value))
        duration = animation_def.get("duration", 1.0)
        easing = AnimationEasing(animation_def.get("easing", AnimationEasing.EASE_IN_OUT.value))
        keyframes = animation_def.get("keyframes")
        expression = animation_def.get("expression")
        expression_intensity = animation_def.get("expression_intensity", 0.7)
        
        # Define callback for when this animation completes
        def animation_completed(animation):
            # Increment index
            sequence = self.animation_sequences.get(sequence_id)
            if sequence:
                sequence["current_index"] += 1
                # Play next animation
                self._play_next_in_sequence(sequence_id)
        
        # Animate avatar
        self.animate(
            avatar_id=avatar_id,
            animation_type=animation_type,
            duration=duration,
            easing=easing,
            keyframes=keyframes,
            expression=expression,
            expression_intensity=expression_intensity,
            loop=False,
            callback=animation_completed
        )

    def _complete_sequence(self, sequence_id: str):
        """
        Complete an animation sequence.
        
        Args:
            sequence_id: ID of the sequence
        """
        if sequence_id not in self.animation_sequences:
            return
        
        # Get sequence data
        sequence = self.animation_sequences[sequence_id]
        avatar_id = sequence["avatar_id"]
        
        # Update sequence status
        sequence["status"] = "completed"
        sequence["end_time"] = time.time()
        
        # Call callback if registered
        if sequence_id in self.animation_callbacks:
            callback = self.animation_callbacks[sequence_id]
            try:
                callback(sequence)
            except Exception as e:
                logger.error(f"Error in sequence callback: {e}")
            
            # Remove callback after calling
            del self.animation_callbacks[sequence_id]
        
        # Remove from sequences
        del self.animation_sequences[sequence_id]
        
        logger.debug(f"Completed animation sequence {sequence_id} for avatar {avatar_id}")

    def stop_sequence(self, sequence_id: str) -> bool:
        """
        Stop an animation sequence.
        
        Args:
            sequence_id: ID of the sequence to stop
            
        Returns:
            True if sequence was stopped, False otherwise
        """
        if sequence_id not in self.animation_sequences:
            logger.warning(f"Unknown sequence ID: {sequence_id}")
            return False
        
        # Get sequence data
        sequence = self.animation_sequences[sequence_id]
        avatar_id = sequence["avatar_id"]
        
        # Stop all animations for this avatar
        self.stop_all_animations_for_avatar(avatar_id)
        
        # Update sequence status
        sequence["status"] = "stopped"
        sequence["end_time"] = time.time()
        
        # Remove callback if registered
        if sequence_id in self.animation_callbacks:
            del self.animation_callbacks[sequence_id]
        
        # Remove from sequences
        del self.animation_sequences[sequence_id]
        
        logger.debug(f"Stopped animation sequence {sequence_id} for avatar {avatar_id}")
        return True

    def create_animation_preset(
        self,
        preset_name: str,
        animation_type: AnimationType,
        duration: float = 1.0,
        easing: AnimationEasing = AnimationEasing.EASE_IN_OUT,
        keyframes: List[Dict[str, Any]] = None,
        expression: Optional[str] = None,
        expression_intensity: float = 0.7,
        loop: bool = False
    ) -> bool:
        """
        Create a new animation preset.
        
        Args:
            preset_name: Name of the preset
            animation_type: Type of animation
            duration: Duration of animation in seconds
            easing: Easing function for animation
            keyframes: Keyframes for animation
            expression: Optional expression to show during animation
            expression_intensity: Intensity of expression
            loop: Whether to loop the animation
            
        Returns:
            True if preset was created, False otherwise
        """
        if preset_name in self.animation_presets:
            logger.warning(f"Animation preset {preset_name} already exists, overwriting")
        
        # Create default keyframes if not provided
        if keyframes is None:
            keyframes = [
                {"time": 0.0, "scale": 1.0, "opacity": 1.0},
                {"time": duration, "scale": 1.0, "opacity": 1.0}
            ]
        
        # Create preset
        self.animation_presets[preset_name] = {
            "type": animation_type.value,
            "duration": duration,
            "easing": easing.value,
            "keyframes": keyframes,
            "expression": expression,
            "expression_intensity": expression_intensity,
            "loop": loop
        }
        
        logger.info(f"Created animation preset {preset_name}")
        return True

    def get_animation_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Get an animation preset.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Preset if found, None otherwise
        """
        return self.animation_presets.get(preset_name)

    def get_all_animation_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all animation presets.
        
        Returns:
            Dictionary of animation presets
        """
        return self.animation_presets

    def delete_animation_preset(self, preset_name: str) -> bool:
        """
        Delete an animation preset.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            True if preset was deleted, False otherwise
        """
        if preset_name not in self.animation_presets:
            logger.warning(f"Unknown animation preset: {preset_name}")
            return False
        
        # Delete preset
        del self.animation_presets[preset_name]
        
        logger.info(f"Deleted animation preset {preset_name}")
        return True

    def get_active_animations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active animations.
        
        Returns:
            Dictionary of active animations
        """
        return self.active_animations

    def get_active_sequences(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active animation sequences.
        
        Returns:
            Dictionary of active sequences
        """
        return self.animation_sequences

    def get_avatar_animation_state(self, avatar_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the animation state of an avatar.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            Animation state if found, None otherwise
        """
        return self.animation_states.get(avatar_id)

    def synchronize_animations(
        self,
        avatar_ids: List[str],
        animation_type: AnimationType,
        duration: float = 1.0,
        easing: AnimationEasing = AnimationEasing.EASE_IN_OUT,
        keyframes: Optional[List[Dict[str, Any]]] = None,
        expression: Optional[str] = None,
        expression_intensity: float = 0.7,
        callback: Optional[Callable] = None
    ) -> Dict[str, str]:
        """
        Synchronize animations across multiple avatars.
        
        Args:
            avatar_ids: List of avatar IDs
            animation_type: Type of animation
            duration: Duration of animation in seconds
            easing: Easing function for animation
            keyframes: Optional keyframes for animation
            expression: Optional expression to show during animation
            expression_intensity: Intensity of expression
            callback: Optional callback function to call when all animations complete
            
        Returns:
            Dictionary mapping avatar IDs to animation IDs
        """
        animation_ids = {}
        completed_count = 0
        total_count = len(avatar_ids)
        
        # Define callback for individual animations
        def animation_completed(animation):
            nonlocal completed_count
            completed_count += 1
            
            # If all animations are complete, call the main callback
            if completed_count == total_count and callback:
                callback(animation_ids)
        
        # Animate each avatar
        for avatar_id in avatar_ids:
            animation_id = self.animate(
                avatar_id=avatar_id,
                animation_type=animation_type,
                duration=duration,
                easing=easing,
                keyframes=keyframes,
                expression=expression,
                expression_intensity=expression_intensity,
                loop=False,
                callback=animation_completed
            )
            
            animation_ids[avatar_id] = animation_id
        
        return animation_ids

    def animate_transition(
        self,
        avatar_id: str,
        from_state: str,
        to_state: str,
        duration: float = 1.0,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Animate a transition between states for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            from_state: Starting state
            to_state: Ending state
            duration: Duration of transition in seconds
            callback: Optional callback function to call when transition completes
            
        Returns:
            Animation ID for tracking
        """
        # Define transition animation based on states
        if from_state == "idle" and to_state == "active":
            return self.animate_with_preset(
                avatar_id=avatar_id,
                preset_name="greeting",
                override_params={"duration": duration},
                callback=callback
            )
        
        elif from_state == "active" and to_state == "idle":
            return self.animate_with_preset(
                avatar_id=avatar_id,
                preset_name="farewell",
                override_params={"duration": duration},
                callback=callback
            )
        
        elif from_state == "idle" and to_state == "thinking":
            return self.animate_with_preset(
                avatar_id=avatar_id,
                preset_name="thinking",
                override_params={"duration": duration},
                callback=callback
            )
        
        elif from_state == "thinking" and to_state == "active":
            # Create custom transition
            keyframes = [
                {"time": 0.0, "scale": 0.95, "opacity": 0.9, "pulse": 0.5},
                {"time": duration * 0.5, "scale": 1.1, "opacity": 1.0, "pulse": 0.0},
                {"time": duration, "scale": 1.0, "opacity": 1.0, "pulse": 0.0}
            ]
            
            return self.animate(
                avatar_id=avatar_id,
                animation_type=AnimationType.TRANSITIONING,
                duration=duration,
                easing=AnimationEasing.EASE_OUT,
                keyframes=keyframes,
                expression="satisfied",
                expression_intensity=0.7,
                callback=callback
            )
        
        else:
            # Default transition
            keyframes = [
                {"time": 0.0, "scale": 1.0, "opacity": 0.8},
                {"time": duration * 0.5, "scale": 0.9, "opacity": 0.9},
                {"time": duration, "scale": 1.0, "opacity": 1.0}
            ]
            
            return self.animate(
                avatar_id=avatar_id,
                animation_type=AnimationType.TRANSITIONING,
                duration=duration,
                easing=AnimationEasing.EASE_IN_OUT,
                keyframes=keyframes,
                callback=callback
            )

    def animate_based_on_agent_state(
        self,
        avatar_id: str,
        agent_id: str,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Animate an avatar based on agent state.
        
        Args:
            avatar_id: ID of the avatar
            agent_id: ID of the agent
            callback: Optional callback function to call when animation completes
            
        Returns:
            Animation ID for tracking
        """
        # Get agent state
        agent_state = self.agent_state_visualizer.get_agent_state(agent_id)
        
        if not agent_state:
            logger.warning(f"Unknown agent: {agent_id}")
            return ""
        
        # Determine animation based on agent state
        state = agent_state.get("state", "idle")
        
        if state == "processing_interaction":
            return self.animate_with_preset(
                avatar_id=avatar_id,
                preset_name="thinking",
                callback=callback
            )
        
        elif state == "interaction_completed":
            status = agent_state.get("response_status", "unknown")
            
            if status == "success":
                return self.animate_with_preset(
                    avatar_id=avatar_id,
                    preset_name="success",
                    callback=callback
                )
            elif status == "error":
                return self.animate_with_preset(
                    avatar_id=avatar_id,
                    preset_name="error",
                    callback=callback
                )
            else:
                return self.animate_with_preset(
                    avatar_id=avatar_id,
                    preset_name="idle",
                    callback=callback
                )
        
        elif state == "speaking":
            return self.animate_with_preset(
                avatar_id=avatar_id,
                preset_name="speaking",
                callback=callback
            )
        
        elif state == "listening":
            return self.animate_with_preset(
                avatar_id=avatar_id,
                preset_name="listening",
                callback=callback
            )
        
        else:
            return self.animate_with_preset(
                avatar_id=avatar_id,
                preset_name="idle",
                callback=callback
            )

    def _apply_easing(self, t: float, easing: str) -> float:
        """
        Apply easing function to a time value.
        
        Args:
            t: Time value between 0 and 1
            easing: Easing function name
            
        Returns:
            Eased time value
        """
        if easing == AnimationEasing.LINEAR.value:
            return t
        
        elif easing == AnimationEasing.EASE_IN.value:
            return t * t
        
        elif easing == AnimationEasing.EASE_OUT.value:
            return t * (2 - t)
        
        elif easing == AnimationEasing.EASE_IN_OUT.value:
            return t * t * (3 - 2 * t)
        
        elif easing == AnimationEasing.BOUNCE.value:
            if t < 0.5:
                return 4 * t * t
            else:
                return 4 * (t - 1) * (t - 1) + 1
        
        elif easing == AnimationEasing.ELASTIC.value:
            return math.sin(13 * math.pi / 2 * t) * math.pow(2, 10 * (t - 1))
        
        elif easing == AnimationEasing.BACK.value:
            s = 1.70158
            return t * t * ((s + 1) * t - s)
        
        return t

    def get_animation_value_at_time(
        self,
        animation_id: str,
        property_name: str,
        time_offset: float = 0.0
    ) -> Optional[float]:
        """
        Get the value of an animation property at a specific time.
        
        Args:
            animation_id: ID of the animation
            property_name: Name of the property
            time_offset: Time offset from animation start
            
        Returns:
            Property value if found, None otherwise
        """
        if animation_id not in self.active_animations:
            return None
        
        # Get animation data
        animation = self.active_animations[animation_id]
        keyframes = animation["keyframes"]
        duration = animation["duration"]
        easing = animation["easing"]
        
        # Calculate normalized time
        animation_time = time.time() - animation["start_time"] + time_offset
        
        # Handle looping
        if animation["loop"]:
            animation_time = animation_time % duration
        
        # Ensure time is within bounds
        if animation_time < 0:
            animation_time = 0
        elif animation_time > duration:
            animation_time = duration
        
        # Normalize time to 0-1 range
        t = animation_time / duration
        
        # Apply easing
        t_eased = self._apply_easing(t, easing)
        
        # Find keyframes that bracket the current time
        prev_keyframe = None
        next_keyframe = None
        
        for keyframe in keyframes:
            keyframe_time = keyframe["time"]
            
            if keyframe_time <= animation_time:
                if prev_keyframe is None or keyframe_time > prev_keyframe["time"]:
                    prev_keyframe = keyframe
            
            if keyframe_time >= animation_time:
                if next_keyframe is None or keyframe_time < next_keyframe["time"]:
                    next_keyframe = keyframe
        
        # If no bracketing keyframes found, return None
        if prev_keyframe is None or next_keyframe is None:
            return None
        
        # If property not in keyframes, return None
        if property_name not in prev_keyframe or property_name not in next_keyframe:
            return None
        
        # If keyframes are the same, return value
        if prev_keyframe["time"] == next_keyframe["time"]:
            return prev_keyframe[property_name]
        
        # Interpolate between keyframes
        t_between = (animation_time - prev_keyframe["time"]) / (next_keyframe["time"] - prev_keyframe["time"])
        
        # Apply easing to interpolation
        t_between_eased = self._apply_easing(t_between, easing)
        
        # Interpolate value
        prev_value = prev_keyframe[property_name]
        next_value = next_keyframe[property_name]
        
        return prev_value + (next_value - prev_value) * t_between_eased

    def export_animation_presets(self, format: str = "json") -> str:
        """
        Export animation presets in specified format.
        
        Args:
            format: Export format ("json" or "yaml")
            
        Returns:
            Exported presets as string
        """
        if format.lower() == "json":
            return json.dumps(self.animation_presets, indent=2)
        
        elif format.lower() == "yaml":
            try:
                import yaml
                return yaml.dump(self.animation_presets, default_flow_style=False)
            except ImportError:
                logger.error("PyYAML not installed, falling back to JSON")
                return json.dumps(self.animation_presets, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_animation_presets(self, data: str, format: str = "json") -> int:
        """
        Import animation presets from specified format.
        
        Args:
            data: Data to import
            format: Import format ("json" or "yaml")
            
        Returns:
            Number of presets imported
        """
        if format.lower() == "json":
            try:
                presets = json.loads(data)
                self.animation_presets.update(presets)
                return len(presets)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON: {e}")
                raise ValueError(f"Invalid JSON data: {e}")
        
        elif format.lower() == "yaml":
            try:
                import yaml
                presets = yaml.safe_load(data)
                self.animation_presets.update(presets)
                return len(presets)
            except ImportError:
                logger.error("PyYAML not installed")
                raise ValueError("PyYAML not installed")
            except yaml.YAMLError as e:
                logger.error(f"Error decoding YAML: {e}")
                raise ValueError(f"Invalid YAML data: {e}")
        
        else:
            raise ValueError(f"Unsupported import format: {format}")
