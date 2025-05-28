"""
Avatar Expression Engine for Agent Ecosystem

This module manages the visual, auditory, and behavioral expressions of AI Avatars
within the Industriverse UI/UX Layer. It implements the dynamic representation of
agent states, emotions, and confidence levels through visual cues, animations,
and interactive behaviors.

The Avatar Expression Engine:
1. Translates agent states into visual expressions
2. Manages animation transitions between expression states
3. Coordinates with the Rendering Engine for visual representation
4. Provides an API for agents to express their current state
5. Adapts expressions based on device capabilities and user preferences

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import math

# Local imports
from ..rendering_engine.rendering_engine import RenderingEngine
from ..context_engine.context_engine import ContextEngine
from ..universal_skin.device_adapter import DeviceAdapter

# Configure logging
logger = logging.getLogger(__name__)

class ExpressionType(Enum):
    """Enumeration of standard expression types for AI Avatars."""
    NEUTRAL = "neutral"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    ALERT = "alert"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    WAITING = "waiting"
    LISTENING = "listening"
    SPEAKING = "speaking"
    THINKING = "thinking"
    SUGGESTING = "suggesting"
    WARNING = "warning"
    CRITICAL = "critical"

class ExpressionIntensity(Enum):
    """Enumeration of expression intensity levels."""
    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"

class AnimationType(Enum):
    """Enumeration of animation types for avatar expressions."""
    PULSE = "pulse"
    GLOW = "glow"
    WAVE = "wave"
    ROTATE = "rotate"
    SCALE = "scale"
    MORPH = "morph"
    FADE = "fade"
    BOUNCE = "bounce"
    SHAKE = "shake"
    FLOAT = "float"

class AvatarExpressionEngine:
    """
    Manages the visual, auditory, and behavioral expressions of AI Avatars.
    
    This class is responsible for translating agent states, confidence levels,
    and other metadata into visual expressions, animations, and interactive
    behaviors for AI Avatars in the Industriverse UI/UX Layer.
    """
    
    def __init__(
        self, 
        rendering_engine: RenderingEngine,
        context_engine: ContextEngine,
        device_adapter: DeviceAdapter
    ):
        """
        Initialize the Avatar Expression Engine.
        
        Args:
            rendering_engine: The Rendering Engine instance for visual representation
            context_engine: The Context Engine instance for context awareness
            device_adapter: The Device Adapter instance for device-specific adaptations
        """
        self.rendering_engine = rendering_engine
        self.context_engine = context_engine
        self.device_adapter = device_adapter
        
        # Expression definitions with associated visual properties
        self.expression_definitions = self._load_expression_definitions()
        
        # Animation definitions with parameters
        self.animation_definitions = self._load_animation_definitions()
        
        # Currently active expressions for each avatar
        self.active_expressions = {}
        
        # Expression history for each avatar
        self.expression_history = {}
        
        # Avatar-specific expression overrides
        self.avatar_expression_overrides = {}
        
        # Expression transition timings
        self.transition_duration = 300  # ms
        
        logger.info("Avatar Expression Engine initialized")
    
    def _load_expression_definitions(self) -> Dict:
        """
        Load expression definitions with visual properties.
        
        Returns:
            Dictionary of expression definitions
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard expressions inline
        
        return {
            ExpressionType.NEUTRAL.value: {
                "color": "#4A90E2",
                "opacity": 0.8,
                "scale": 1.0,
                "pulse_rate": 0,
                "glow_intensity": 0.2,
                "animation": None,
                "sound": None
            },
            ExpressionType.CONFIDENT.value: {
                "color": "#27AE60",
                "opacity": 1.0,
                "scale": 1.05,
                "pulse_rate": 0,
                "glow_intensity": 0.4,
                "animation": AnimationType.GLOW.value,
                "sound": "confident_tone"
            },
            ExpressionType.UNCERTAIN.value: {
                "color": "#F39C12",
                "opacity": 0.7,
                "scale": 0.95,
                "pulse_rate": 1,
                "glow_intensity": 0.1,
                "animation": AnimationType.PULSE.value,
                "sound": "uncertain_tone"
            },
            ExpressionType.ALERT.value: {
                "color": "#E74C3C",
                "opacity": 1.0,
                "scale": 1.1,
                "pulse_rate": 2,
                "glow_intensity": 0.6,
                "animation": AnimationType.PULSE.value,
                "sound": "alert_tone"
            },
            ExpressionType.PROCESSING.value: {
                "color": "#3498DB",
                "opacity": 0.9,
                "scale": 1.0,
                "pulse_rate": 0.5,
                "glow_intensity": 0.3,
                "animation": AnimationType.ROTATE.value,
                "sound": "processing_tone"
            },
            ExpressionType.SUCCESS.value: {
                "color": "#2ECC71",
                "opacity": 1.0,
                "scale": 1.1,
                "pulse_rate": 0,
                "glow_intensity": 0.5,
                "animation": AnimationType.SCALE.value,
                "sound": "success_tone"
            },
            ExpressionType.ERROR.value: {
                "color": "#E74C3C",
                "opacity": 1.0,
                "scale": 1.0,
                "pulse_rate": 0,
                "glow_intensity": 0.4,
                "animation": AnimationType.SHAKE.value,
                "sound": "error_tone"
            },
            ExpressionType.WAITING.value: {
                "color": "#95A5A6",
                "opacity": 0.6,
                "scale": 0.9,
                "pulse_rate": 0.2,
                "glow_intensity": 0.1,
                "animation": AnimationType.PULSE.value,
                "sound": None
            },
            ExpressionType.LISTENING.value: {
                "color": "#3498DB",
                "opacity": 0.9,
                "scale": 1.0,
                "pulse_rate": 0.3,
                "glow_intensity": 0.3,
                "animation": AnimationType.WAVE.value,
                "sound": None
            },
            ExpressionType.SPEAKING.value: {
                "color": "#3498DB",
                "opacity": 1.0,
                "scale": 1.05,
                "pulse_rate": 0.4,
                "glow_intensity": 0.4,
                "animation": AnimationType.WAVE.value,
                "sound": None
            },
            ExpressionType.THINKING.value: {
                "color": "#9B59B6",
                "opacity": 0.8,
                "scale": 1.0,
                "pulse_rate": 0.2,
                "glow_intensity": 0.3,
                "animation": AnimationType.FLOAT.value,
                "sound": "thinking_tone"
            },
            ExpressionType.SUGGESTING.value: {
                "color": "#3498DB",
                "opacity": 0.9,
                "scale": 1.02,
                "pulse_rate": 0,
                "glow_intensity": 0.3,
                "animation": AnimationType.GLOW.value,
                "sound": "suggestion_tone"
            },
            ExpressionType.WARNING.value: {
                "color": "#F39C12",
                "opacity": 1.0,
                "scale": 1.05,
                "pulse_rate": 1,
                "glow_intensity": 0.5,
                "animation": AnimationType.PULSE.value,
                "sound": "warning_tone"
            },
            ExpressionType.CRITICAL.value: {
                "color": "#E74C3C",
                "opacity": 1.0,
                "scale": 1.1,
                "pulse_rate": 3,
                "glow_intensity": 0.7,
                "animation": AnimationType.SHAKE.value,
                "sound": "critical_tone"
            }
        }
    
    def _load_animation_definitions(self) -> Dict:
        """
        Load animation definitions with parameters.
        
        Returns:
            Dictionary of animation definitions
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard animations inline
        
        return {
            AnimationType.PULSE.value: {
                "duration": 1000,  # ms
                "easing": "ease-in-out",
                "repeat": True,
                "properties": ["opacity", "scale"],
                "keyframes": [
                    {"time": 0, "opacity": "base", "scale": "base"},
                    {"time": 50, "opacity": "base * 1.2", "scale": "base * 1.05"},
                    {"time": 100, "opacity": "base", "scale": "base"}
                ]
            },
            AnimationType.GLOW.value: {
                "duration": 2000,  # ms
                "easing": "ease-in-out",
                "repeat": True,
                "properties": ["glow_intensity"],
                "keyframes": [
                    {"time": 0, "glow_intensity": "base"},
                    {"time": 50, "glow_intensity": "base * 1.5"},
                    {"time": 100, "glow_intensity": "base"}
                ]
            },
            AnimationType.WAVE.value: {
                "duration": 3000,  # ms
                "easing": "ease-in-out",
                "repeat": True,
                "properties": ["wave_offset"],
                "keyframes": [
                    {"time": 0, "wave_offset": 0},
                    {"time": 100, "wave_offset": 1}
                ]
            },
            AnimationType.ROTATE.value: {
                "duration": 2000,  # ms
                "easing": "linear",
                "repeat": True,
                "properties": ["rotation"],
                "keyframes": [
                    {"time": 0, "rotation": 0},
                    {"time": 100, "rotation": 360}
                ]
            },
            AnimationType.SCALE.value: {
                "duration": 500,  # ms
                "easing": "ease-out",
                "repeat": False,
                "properties": ["scale"],
                "keyframes": [
                    {"time": 0, "scale": "base * 0.9"},
                    {"time": 70, "scale": "base * 1.1"},
                    {"time": 100, "scale": "base"}
                ]
            },
            AnimationType.MORPH.value: {
                "duration": 1000,  # ms
                "easing": "ease-in-out",
                "repeat": False,
                "properties": ["shape_points"],
                "keyframes": [
                    {"time": 0, "shape_points": "base"},
                    {"time": 100, "shape_points": "target"}
                ]
            },
            AnimationType.FADE.value: {
                "duration": 500,  # ms
                "easing": "ease-in-out",
                "repeat": False,
                "properties": ["opacity"],
                "keyframes": [
                    {"time": 0, "opacity": "base"},
                    {"time": 100, "opacity": "target"}
                ]
            },
            AnimationType.BOUNCE.value: {
                "duration": 800,  # ms
                "easing": "cubic-bezier(0.175, 0.885, 0.32, 1.275)",
                "repeat": False,
                "properties": ["position_y", "scale"],
                "keyframes": [
                    {"time": 0, "position_y": "base", "scale": "base"},
                    {"time": 40, "position_y": "base - 20", "scale": "base * 0.9"},
                    {"time": 60, "position_y": "base", "scale": "base * 1.1"},
                    {"time": 80, "position_y": "base - 10", "scale": "base * 0.95"},
                    {"time": 100, "position_y": "base", "scale": "base"}
                ]
            },
            AnimationType.SHAKE.value: {
                "duration": 500,  # ms
                "easing": "ease-in-out",
                "repeat": False,
                "properties": ["position_x"],
                "keyframes": [
                    {"time": 0, "position_x": "base"},
                    {"time": 10, "position_x": "base - 5"},
                    {"time": 30, "position_x": "base + 5"},
                    {"time": 50, "position_x": "base - 5"},
                    {"time": 70, "position_x": "base + 5"},
                    {"time": 90, "position_x": "base - 5"},
                    {"time": 100, "position_x": "base"}
                ]
            },
            AnimationType.FLOAT.value: {
                "duration": 3000,  # ms
                "easing": "ease-in-out",
                "repeat": True,
                "properties": ["position_y"],
                "keyframes": [
                    {"time": 0, "position_y": "base"},
                    {"time": 50, "position_y": "base - 5"},
                    {"time": 100, "position_y": "base"}
                ]
            }
        }
    
    def set_avatar_expression(
        self, 
        avatar_id: str, 
        expression_type: str, 
        intensity: str = ExpressionIntensity.MODERATE.value,
        duration: int = None,
        metadata: Dict = None
    ) -> bool:
        """
        Set the expression for a specific avatar.
        
        Args:
            avatar_id: The ID of the avatar to set expression for
            expression_type: The type of expression to set
            intensity: The intensity level of the expression
            duration: Optional duration in milliseconds (None for indefinite)
            metadata: Optional additional metadata for the expression
            
        Returns:
            Boolean indicating success
        """
        # Verify expression type exists
        if expression_type not in self.expression_definitions:
            logger.error(f"Expression type {expression_type} not found in expression definitions")
            return False
        
        # Get expression definition
        expression_def = self.expression_definitions[expression_type]
        
        # Apply avatar-specific overrides if they exist
        if avatar_id in self.avatar_expression_overrides:
            avatar_overrides = self.avatar_expression_overrides[avatar_id]
            if expression_type in avatar_overrides:
                # Merge the base expression with avatar-specific overrides
                expression_def = {**expression_def, **avatar_overrides[expression_type]}
        
        # Apply intensity modifications
        modified_expression = self._apply_intensity(expression_def, intensity)
        
        # Add metadata if provided
        if metadata:
            modified_expression["metadata"] = metadata
        
        # Add timestamp
        modified_expression["timestamp"] = time.time()
        
        # Add duration if provided
        if duration:
            modified_expression["duration"] = duration
        
        # Store previous expression in history
        if avatar_id in self.active_expressions:
            if avatar_id not in self.expression_history:
                self.expression_history[avatar_id] = []
            
            # Limit history length
            if len(self.expression_history[avatar_id]) > 20:
                self.expression_history[avatar_id].pop(0)
            
            self.expression_history[avatar_id].append(self.active_expressions[avatar_id])
        
        # Set active expression
        self.active_expressions[avatar_id] = {
            "type": expression_type,
            "intensity": intensity,
            "properties": modified_expression
        }
        
        # Apply the expression through the rendering engine
        self._apply_expression_to_renderer(avatar_id, modified_expression)
        
        logger.info(f"Set expression {expression_type} ({intensity}) for avatar {avatar_id}")
        return True
    
    def _apply_intensity(self, expression_def: Dict, intensity: str) -> Dict:
        """
        Apply intensity modifications to an expression definition.
        
        Args:
            expression_def: The base expression definition
            intensity: The intensity level to apply
            
        Returns:
            Modified expression definition
        """
        # Create a copy of the expression definition
        modified_expression = expression_def.copy()
        
        # Apply intensity-based modifications
        if intensity == ExpressionIntensity.SUBTLE.value:
            modified_expression["opacity"] = expression_def["opacity"] * 0.7
            modified_expression["scale"] = expression_def["scale"] * 0.9
            modified_expression["pulse_rate"] = expression_def["pulse_rate"] * 0.5
            modified_expression["glow_intensity"] = expression_def["glow_intensity"] * 0.5
        elif intensity == ExpressionIntensity.STRONG.value:
            modified_expression["opacity"] = min(1.0, expression_def["opacity"] * 1.3)
            modified_expression["scale"] = expression_def["scale"] * 1.1
            modified_expression["pulse_rate"] = expression_def["pulse_rate"] * 1.5
            modified_expression["glow_intensity"] = min(1.0, expression_def["glow_intensity"] * 1.5)
        
        return modified_expression
    
    def _apply_expression_to_renderer(self, avatar_id: str, expression_properties: Dict) -> None:
        """
        Apply expression properties to the rendering engine.
        
        Args:
            avatar_id: The ID of the avatar to apply expression to
            expression_properties: The expression properties to apply
        """
        # Get animation definition if specified
        animation_def = None
        if expression_properties.get("animation"):
            animation_type = expression_properties["animation"]
            if animation_type in self.animation_definitions:
                animation_def = self.animation_definitions[animation_type]
        
        # Prepare rendering properties
        render_props = {
            "color": expression_properties["color"],
            "opacity": expression_properties["opacity"],
            "scale": expression_properties["scale"],
            "glow_intensity": expression_properties["glow_intensity"]
        }
        
        # Add animation if defined
        if animation_def:
            render_props["animation"] = {
                "type": expression_properties["animation"],
                "duration": animation_def["duration"],
                "easing": animation_def["easing"],
                "repeat": animation_def["repeat"],
                "keyframes": animation_def["keyframes"]
            }
        
        # Apply to rendering engine
        self.rendering_engine.update_avatar_visual(avatar_id, render_props)
        
        # Apply sound if defined and enabled
        if expression_properties.get("sound") and self._should_play_sound():
            self.rendering_engine.play_avatar_sound(
                avatar_id, 
                expression_properties["sound"]
            )
    
    def _should_play_sound(self) -> bool:
        """
        Determine if sounds should be played based on context and device settings.
        
        Returns:
            Boolean indicating if sounds should be played
        """
        # Check device capabilities
        device_capabilities = self.device_adapter.get_device_capabilities()
        if not device_capabilities.get("audio_enabled", True):
            return False
        
        # Check user preferences
        user_preferences = self.context_engine.get_user_preferences()
        if not user_preferences.get("avatar_sounds_enabled", True):
            return False
        
        # Check context appropriateness
        current_context = self.context_engine.get_current_context()
        if current_context.get("quiet_mode", False):
            return False
        
        return True
    
    def get_avatar_expression(self, avatar_id: str) -> Dict:
        """
        Get the current expression for a specific avatar.
        
        Args:
            avatar_id: The ID of the avatar to get expression for
            
        Returns:
            Dictionary containing current expression information
        """
        return self.active_expressions.get(avatar_id, {})
    
    def get_avatar_expression_history(self, avatar_id: str, limit: int = 10) -> List[Dict]:
        """
        Get expression history for a specific avatar.
        
        Args:
            avatar_id: The ID of the avatar to get history for
            limit: Maximum number of history items to return
            
        Returns:
            List of dictionaries containing historical expression information
        """
        history = self.expression_history.get(avatar_id, [])
        return history[-limit:]
    
    def register_avatar_expression_override(
        self, 
        avatar_id: str, 
        expression_type: str, 
        override_properties: Dict
    ) -> bool:
        """
        Register avatar-specific expression overrides.
        
        Args:
            avatar_id: The ID of the avatar to register overrides for
            expression_type: The type of expression to override
            override_properties: The properties to override
            
        Returns:
            Boolean indicating success
        """
        # Verify expression type exists
        if expression_type not in self.expression_definitions:
            logger.error(f"Expression type {expression_type} not found in expression definitions")
            return False
        
        # Initialize avatar overrides if not exists
        if avatar_id not in self.avatar_expression_overrides:
            self.avatar_expression_overrides[avatar_id] = {}
        
        # Register override
        self.avatar_expression_overrides[avatar_id][expression_type] = override_properties
        
        logger.info(f"Registered expression override for avatar {avatar_id}, expression {expression_type}")
        return True
    
    def set_transition_duration(self, duration_ms: int) -> None:
        """
        Set the duration for expression transitions.
        
        Args:
            duration_ms: Transition duration in milliseconds
        """
        self.transition_duration = duration_ms
        self.rendering_engine.set_transition_duration(duration_ms)
        
        logger.info(f"Set expression transition duration to {duration_ms}ms")
    
    def set_expression_from_agent_state(
        self, 
        avatar_id: str, 
        agent_state: Dict
    ) -> bool:
        """
        Set avatar expression based on agent state data.
        
        Args:
            avatar_id: The ID of the avatar to set expression for
            agent_state: Dictionary containing agent state information
            
        Returns:
            Boolean indicating success
        """
        # Map agent state to expression type and intensity
        expression_type = ExpressionType.NEUTRAL.value
        intensity = ExpressionIntensity.MODERATE.value
        
        # Determine expression based on agent state
        if "status" in agent_state:
            status = agent_state["status"]
            
            if status == "processing":
                expression_type = ExpressionType.PROCESSING.value
            elif status == "waiting":
                expression_type = ExpressionType.WAITING.value
            elif status == "error":
                expression_type = ExpressionType.ERROR.value
            elif status == "success":
                expression_type = ExpressionType.SUCCESS.value
        
        if "confidence" in agent_state:
            confidence = agent_state["confidence"]
            
            if confidence > 0.8:
                expression_type = ExpressionType.CONFIDENT.value
            elif confidence < 0.4:
                expression_type = ExpressionType.UNCERTAIN.value
            
            # Adjust intensity based on confidence
            if confidence > 0.9:
                intensity = ExpressionIntensity.STRONG.value
            elif confidence < 0.3:
                intensity = ExpressionIntensity.STRONG.value  # Strong for very low confidence too
            elif 0.4 <= confidence <= 0.6:
                intensity = ExpressionIntensity.SUBTLE.value
        
        if "alert_level" in agent_state:
            alert_level = agent_state["alert_level"]
            
            if alert_level == "warning":
                expression_type = ExpressionType.WARNING.value
            elif alert_level == "critical":
                expression_type = ExpressionType.CRITICAL.value
                intensity = ExpressionIntensity.STRONG.value
            elif alert_level == "alert":
                expression_type = ExpressionType.ALERT.value
        
        if "interaction_mode" in agent_state:
            interaction_mode = agent_state["interaction_mode"]
            
            if interaction_mode == "listening":
                expression_type = ExpressionType.LISTENING.value
            elif interaction_mode == "speaking":
                expression_type = ExpressionType.SPEAKING.value
            elif interaction_mode == "thinking":
                expression_type = ExpressionType.THINKING.value
            elif interaction_mode == "suggesting":
                expression_type = ExpressionType.SUGGESTING.value
        
        # Set the expression
        return self.set_avatar_expression(
            avatar_id, 
            expression_type, 
            intensity, 
            metadata=agent_state
        )
    
    def pulse_avatar(
        self, 
        avatar_id: str, 
        pulse_type: str = ExpressionType.ALERT.value,
        duration_ms: int = 500
    ) -> bool:
        """
        Create a brief pulse effect for an avatar.
        
        Args:
            avatar_id: The ID of the avatar to pulse
            pulse_type: The type of pulse expression
            duration_ms: Duration of the pulse in milliseconds
            
        Returns:
            Boolean indicating success
        """
        # Store current expression
        current_expression = self.get_avatar_expression(avatar_id)
        
        # Apply pulse expression
        result = self.set_avatar_expression(
            avatar_id,
            pulse_type,
            ExpressionIntensity.STRONG.value,
            duration_ms
        )
        
        # Schedule return to previous expression
        if result:
            # In a real implementation, this would use a proper scheduler
            # For now, we'll just log the intent
            logger.info(f"Avatar {avatar_id} will return to previous expression after {duration_ms}ms")
            
            # In a real implementation:
            # self.scheduler.schedule_task(
            #     lambda: self.set_avatar_expression(
            #         avatar_id,
            #         current_expression.get("type", ExpressionType.NEUTRAL.value),
            #         current_expression.get("intensity", ExpressionIntensity.MODERATE.value)
            #     ),
            #     duration_ms
            # )
        
        return result
    
    def adapt_to_context_change(self, context_update: Dict) -> None:
        """
        Adapt avatar expressions based on a context change.
        
        Args:
            context_update: Dictionary containing context update information
        """
        # Check for context-triggered expression adaptations
        context_priority = context_update.get("priority")
        
        if context_priority == "critical":
            # For critical contexts, pulse all active avatars
            for avatar_id in self.active_expressions:
                self.pulse_avatar(avatar_id, ExpressionType.ALERT.value)
        
        # Adapt expression intensity based on context
        ambient_mode = context_update.get("ambient_mode")
        if ambient_mode == "focus":
            # In focus mode, make expressions more subtle
            for avatar_id in self.active_expressions:
                current_expression = self.get_avatar_expression(avatar_id)
                if current_expression:
                    self.set_avatar_expression(
                        avatar_id,
                        current_expression.get("type", ExpressionType.NEUTRAL.value),
                        ExpressionIntensity.SUBTLE.value
                    )
        elif ambient_mode == "ambient":
            # In ambient mode, make expressions more noticeable
            for avatar_id in self.active_expressions:
                current_expression = self.get_avatar_expression(avatar_id)
                if current_expression:
                    self.set_avatar_expression(
                        avatar_id,
                        current_expression.get("type", ExpressionType.NEUTRAL.value),
                        ExpressionIntensity.MODERATE.value
                    )
        
        logger.info(f"Avatar expressions adapted to context change: {context_update.get('type', 'unknown')}")
"""

