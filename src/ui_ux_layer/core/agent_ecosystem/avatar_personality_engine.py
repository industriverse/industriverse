"""
Avatar Personality Engine for Agent Ecosystem

This module manages avatar personalities within the Agent Ecosystem
of the Industriverse UI/UX Layer. It implements dynamic personality traits,
expressions, and behaviors for layer avatars and agent representations.

The Avatar Personality Engine:
1. Defines and manages avatar personality profiles
2. Adapts avatar expressions and behaviors based on context
3. Handles personality transitions and emotional states
4. Provides an API for avatar personality customization
5. Coordinates with the Context Engine for context-aware personality adaptations

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import random

# Local imports
from ..context_engine.context_awareness_engine import ContextAwarenessEngine
from .avatar_expression_engine import AvatarExpressionEngine
from .agent_state_visualizer import AgentStateVisualizer

# Configure logging
logger = logging.getLogger(__name__)

class PersonalityTrait(Enum):
    """Enumeration of personality traits for avatars."""
    ANALYTICAL = "analytical"   # Logical, methodical, detail-oriented
    CREATIVE = "creative"       # Innovative, imaginative, artistic
    SUPPORTIVE = "supportive"   # Helpful, empathetic, nurturing
    ASSERTIVE = "assertive"     # Confident, direct, decisive
    DIPLOMATIC = "diplomatic"   # Tactful, balanced, mediating
    TECHNICAL = "technical"     # Precise, systematic, specialized
    STRATEGIC = "strategic"     # Forward-thinking, big-picture oriented
    ADAPTIVE = "adaptive"       # Flexible, responsive, versatile

class EmotionalState(Enum):
    """Enumeration of emotional states for avatars."""
    NEUTRAL = "neutral"         # Balanced, calm state
    FOCUSED = "focused"         # Concentrated, attentive state
    ALERT = "alert"             # Vigilant, heightened awareness
    CONCERNED = "concerned"     # Worried, cautious state
    CONFIDENT = "confident"     # Self-assured, positive state
    EXCITED = "excited"         # Enthusiastic, energetic state
    REFLECTIVE = "reflective"   # Thoughtful, contemplative state
    URGENT = "urgent"           # Time-sensitive, pressing state

class AvatarPersonalityEngine:
    """
    Manages avatar personalities within the Agent Ecosystem.
    
    This class is responsible for implementing dynamic personality traits,
    expressions, and behaviors for layer avatars and agent representations.
    """
    
    def __init__(
        self, 
        context_engine: ContextAwarenessEngine,
        expression_engine: AvatarExpressionEngine,
        state_visualizer: AgentStateVisualizer
    ):
        """
        Initialize the Avatar Personality Engine.
        
        Args:
            context_engine: The Context Awareness Engine instance
            expression_engine: The Avatar Expression Engine instance
            state_visualizer: The Agent State Visualizer instance
        """
        self.context_engine = context_engine
        self.expression_engine = expression_engine
        self.state_visualizer = state_visualizer
        
        # Personality profiles
        self.personality_profiles = self._load_personality_profiles()
        
        # Layer-specific personality defaults
        self.layer_personality_defaults = self._load_layer_personality_defaults()
        
        # Current active personalities by avatar ID
        self.active_personalities = {}
        
        # Current emotional states by avatar ID
        self.emotional_states = {}
        
        # Personality transition history
        self.personality_history = {}
        
        # Custom personality definitions
        self.custom_personalities = {}
        
        # Register as context listener
        self.context_engine.register_context_listener(self._handle_context_change)
        
        logger.info("Avatar Personality Engine initialized")
    
    def _load_personality_profiles(self) -> Dict:
        """
        Load personality profile definitions.
        
        Returns:
            Dictionary of personality profile definitions
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard personality profiles inline
        
        return {
            PersonalityTrait.ANALYTICAL.value: {
                "name": "Analytical",
                "description": "Logical, methodical, detail-oriented",
                "traits": {
                    "logical": 0.9,
                    "methodical": 0.8,
                    "detail_oriented": 0.9,
                    "precise": 0.8,
                    "objective": 0.7,
                    "curious": 0.6,
                    "reserved": 0.6
                },
                "expression_settings": {
                    "speech_pattern": "precise",
                    "vocabulary_level": "technical",
                    "speech_tempo": "measured",
                    "facial_expressiveness": 0.4,
                    "gesture_frequency": 0.3,
                    "color_scheme": "cool_blue"
                },
                "behavior_settings": {
                    "response_style": "thorough",
                    "information_density": "high",
                    "proactivity_level": "low",
                    "error_handling": "detailed",
                    "adaptation_rate": "slow"
                }
            },
            PersonalityTrait.CREATIVE.value: {
                "name": "Creative",
                "description": "Innovative, imaginative, artistic",
                "traits": {
                    "innovative": 0.9,
                    "imaginative": 0.9,
                    "artistic": 0.7,
                    "expressive": 0.8,
                    "curious": 0.8,
                    "unconventional": 0.7,
                    "enthusiastic": 0.7
                },
                "expression_settings": {
                    "speech_pattern": "expressive",
                    "vocabulary_level": "varied",
                    "speech_tempo": "dynamic",
                    "facial_expressiveness": 0.8,
                    "gesture_frequency": 0.7,
                    "color_scheme": "vibrant"
                },
                "behavior_settings": {
                    "response_style": "innovative",
                    "information_density": "medium",
                    "proactivity_level": "high",
                    "error_handling": "reframing",
                    "adaptation_rate": "fast"
                }
            },
            PersonalityTrait.SUPPORTIVE.value: {
                "name": "Supportive",
                "description": "Helpful, empathetic, nurturing",
                "traits": {
                    "helpful": 0.9,
                    "empathetic": 0.9,
                    "nurturing": 0.8,
                    "patient": 0.8,
                    "encouraging": 0.7,
                    "attentive": 0.7,
                    "warm": 0.8
                },
                "expression_settings": {
                    "speech_pattern": "warm",
                    "vocabulary_level": "accessible",
                    "speech_tempo": "moderate",
                    "facial_expressiveness": 0.7,
                    "gesture_frequency": 0.6,
                    "color_scheme": "warm_green"
                },
                "behavior_settings": {
                    "response_style": "helpful",
                    "information_density": "adaptive",
                    "proactivity_level": "medium",
                    "error_handling": "reassuring",
                    "adaptation_rate": "moderate"
                }
            },
            PersonalityTrait.ASSERTIVE.value: {
                "name": "Assertive",
                "description": "Confident, direct, decisive",
                "traits": {
                    "confident": 0.9,
                    "direct": 0.8,
                    "decisive": 0.9,
                    "efficient": 0.8,
                    "focused": 0.7,
                    "proactive": 0.8,
                    "bold": 0.7
                },
                "expression_settings": {
                    "speech_pattern": "direct",
                    "vocabulary_level": "concise",
                    "speech_tempo": "brisk",
                    "facial_expressiveness": 0.6,
                    "gesture_frequency": 0.5,
                    "color_scheme": "bold_red"
                },
                "behavior_settings": {
                    "response_style": "decisive",
                    "information_density": "high",
                    "proactivity_level": "high",
                    "error_handling": "direct",
                    "adaptation_rate": "moderate"
                }
            },
            PersonalityTrait.DIPLOMATIC.value: {
                "name": "Diplomatic",
                "description": "Tactful, balanced, mediating",
                "traits": {
                    "tactful": 0.9,
                    "balanced": 0.8,
                    "mediating": 0.9,
                    "considerate": 0.8,
                    "fair": 0.8,
                    "patient": 0.7,
                    "perceptive": 0.7
                },
                "expression_settings": {
                    "speech_pattern": "balanced",
                    "vocabulary_level": "diplomatic",
                    "speech_tempo": "measured",
                    "facial_expressiveness": 0.5,
                    "gesture_frequency": 0.4,
                    "color_scheme": "neutral_purple"
                },
                "behavior_settings": {
                    "response_style": "balanced",
                    "information_density": "medium",
                    "proactivity_level": "medium",
                    "error_handling": "diplomatic",
                    "adaptation_rate": "moderate"
                }
            },
            PersonalityTrait.TECHNICAL.value: {
                "name": "Technical",
                "description": "Precise, systematic, specialized",
                "traits": {
                    "precise": 0.9,
                    "systematic": 0.9,
                    "specialized": 0.8,
                    "thorough": 0.8,
                    "logical": 0.8,
                    "detail_oriented": 0.7,
                    "efficient": 0.7
                },
                "expression_settings": {
                    "speech_pattern": "technical",
                    "vocabulary_level": "specialized",
                    "speech_tempo": "steady",
                    "facial_expressiveness": 0.3,
                    "gesture_frequency": 0.2,
                    "color_scheme": "tech_gray"
                },
                "behavior_settings": {
                    "response_style": "technical",
                    "information_density": "very_high",
                    "proactivity_level": "low",
                    "error_handling": "systematic",
                    "adaptation_rate": "slow"
                }
            },
            PersonalityTrait.STRATEGIC.value: {
                "name": "Strategic",
                "description": "Forward-thinking, big-picture oriented",
                "traits": {
                    "forward_thinking": 0.9,
                    "big_picture": 0.9,
                    "analytical": 0.7,
                    "insightful": 0.8,
                    "visionary": 0.8,
                    "decisive": 0.7,
                    "adaptable": 0.6
                },
                "expression_settings": {
                    "speech_pattern": "thoughtful",
                    "vocabulary_level": "strategic",
                    "speech_tempo": "deliberate",
                    "facial_expressiveness": 0.5,
                    "gesture_frequency": 0.4,
                    "color_scheme": "deep_blue"
                },
                "behavior_settings": {
                    "response_style": "strategic",
                    "information_density": "high",
                    "proactivity_level": "high",
                    "error_handling": "contextual",
                    "adaptation_rate": "moderate"
                }
            },
            PersonalityTrait.ADAPTIVE.value: {
                "name": "Adaptive",
                "description": "Flexible, responsive, versatile",
                "traits": {
                    "flexible": 0.9,
                    "responsive": 0.9,
                    "versatile": 0.8,
                    "intuitive": 0.7,
                    "quick": 0.8,
                    "observant": 0.7,
                    "resourceful": 0.8
                },
                "expression_settings": {
                    "speech_pattern": "adaptive",
                    "vocabulary_level": "contextual",
                    "speech_tempo": "variable",
                    "facial_expressiveness": 0.7,
                    "gesture_frequency": 0.6,
                    "color_scheme": "adaptive_teal"
                },
                "behavior_settings": {
                    "response_style": "adaptive",
                    "information_density": "contextual",
                    "proactivity_level": "adaptive",
                    "error_handling": "flexible",
                    "adaptation_rate": "very_fast"
                }
            }
        }
    
    def _load_layer_personality_defaults(self) -> Dict:
        """
        Load layer-specific personality defaults.
        
        Returns:
            Dictionary of layer personality defaults
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define defaults for the 8 Industriverse layers
        
        return {
            "data_layer": {
                "primary_trait": PersonalityTrait.ANALYTICAL.value,
                "secondary_trait": PersonalityTrait.TECHNICAL.value,
                "default_emotional_state": EmotionalState.NEUTRAL.value,
                "trait_blend_ratio": 0.7,  # 70% primary, 30% secondary
                "expression_overrides": {
                    "color_scheme": "data_blue"
                }
            },
            "core_ai_layer": {
                "primary_trait": PersonalityTrait.TECHNICAL.value,
                "secondary_trait": PersonalityTrait.ANALYTICAL.value,
                "default_emotional_state": EmotionalState.FOCUSED.value,
                "trait_blend_ratio": 0.6,
                "expression_overrides": {
                    "color_scheme": "ai_purple"
                }
            },
            "generative_layer": {
                "primary_trait": PersonalityTrait.CREATIVE.value,
                "secondary_trait": PersonalityTrait.ADAPTIVE.value,
                "default_emotional_state": EmotionalState.NEUTRAL.value,
                "trait_blend_ratio": 0.7,
                "expression_overrides": {
                    "color_scheme": "generative_orange"
                }
            },
            "application_layer": {
                "primary_trait": PersonalityTrait.SUPPORTIVE.value,
                "secondary_trait": PersonalityTrait.DIPLOMATIC.value,
                "default_emotional_state": EmotionalState.NEUTRAL.value,
                "trait_blend_ratio": 0.6,
                "expression_overrides": {
                    "color_scheme": "application_green"
                }
            },
            "protocol_layer": {
                "primary_trait": PersonalityTrait.DIPLOMATIC.value,
                "secondary_trait": PersonalityTrait.TECHNICAL.value,
                "default_emotional_state": EmotionalState.NEUTRAL.value,
                "trait_blend_ratio": 0.7,
                "expression_overrides": {
                    "color_scheme": "protocol_yellow"
                }
            },
            "workflow_layer": {
                "primary_trait": PersonalityTrait.STRATEGIC.value,
                "secondary_trait": PersonalityTrait.ASSERTIVE.value,
                "default_emotional_state": EmotionalState.NEUTRAL.value,
                "trait_blend_ratio": 0.6,
                "expression_overrides": {
                    "color_scheme": "workflow_red"
                }
            },
            "ui_ux_layer": {
                "primary_trait": PersonalityTrait.ADAPTIVE.value,
                "secondary_trait": PersonalityTrait.CREATIVE.value,
                "default_emotional_state": EmotionalState.NEUTRAL.value,
                "trait_blend_ratio": 0.7,
                "expression_overrides": {
                    "color_scheme": "ui_ux_teal"
                }
            },
            "overseer_layer": {
                "primary_trait": PersonalityTrait.STRATEGIC.value,
                "secondary_trait": PersonalityTrait.ANALYTICAL.value,
                "default_emotional_state": EmotionalState.ALERT.value,
                "trait_blend_ratio": 0.6,
                "expression_overrides": {
                    "color_scheme": "overseer_gold"
                }
            }
        }
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        context_type = event.get("type")
        
        # Handle system context changes
        if context_type == "system":
            system_data = event.get("data", {})
            
            # Check for system state changes
            if "system_state" in system_data:
                system_state = system_data["system_state"]
                
                # Update emotional states based on system state
                if system_state == "normal":
                    self._update_all_emotional_states(EmotionalState.NEUTRAL.value)
                elif system_state == "warning":
                    self._update_all_emotional_states(EmotionalState.ALERT.value)
                elif system_state == "critical":
                    self._update_all_emotional_states(EmotionalState.URGENT.value)
                elif system_state == "maintenance":
                    self._update_all_emotional_states(EmotionalState.REFLECTIVE.value)
        
        # Handle task context changes
        elif context_type == "task":
            task_data = event.get("data", {})
            
            # Check for task state changes
            if "task_state" in task_data:
                task_state = task_data["task_state"]
                task_layer = task_data.get("layer")
                
                # Update emotional state for specific layer avatar
                if task_layer:
                    avatar_id = f"{task_layer}_avatar"
                    
                    if task_state == "starting":
                        self.set_avatar_emotional_state(avatar_id, EmotionalState.FOCUSED.value)
                    elif task_state == "in_progress":
                        self.set_avatar_emotional_state(avatar_id, EmotionalState.FOCUSED.value)
                    elif task_state == "completed":
                        self.set_avatar_emotional_state(avatar_id, EmotionalState.CONFIDENT.value)
                    elif task_state == "failed":
                        self.set_avatar_emotional_state(avatar_id, EmotionalState.CONCERNED.value)
        
        # Handle user context changes
        elif context_type == "user":
            user_data = event.get("data", {})
            
            # Check for user interaction preferences
            if "avatar_preferences" in user_data:
                preferences = user_data["avatar_preferences"]
                
                # Apply user preferences to avatars
                for avatar_id, settings in preferences.items():
                    if "personality_trait" in settings:
                        trait = settings["personality_trait"]
                        self.set_avatar_personality(avatar_id, trait)
    
    def _update_all_emotional_states(self, emotional_state: str) -> None:
        """
        Update emotional state for all active avatars.
        
        Args:
            emotional_state: Emotional state to set
        """
        for avatar_id in self.active_personalities.keys():
            self.set_avatar_emotional_state(avatar_id, emotional_state)
    
    def initialize_layer_avatars(self) -> None:
        """Initialize all layer avatars with default personalities."""
        for layer_id, defaults in self.layer_personality_defaults.items():
            avatar_id = f"{layer_id}_avatar"
            
            # Set personality based on defaults
            primary_trait = defaults.get("primary_trait")
            secondary_trait = defaults.get("secondary_trait")
            blend_ratio = defaults.get("trait_blend_ratio", 0.7)
            
            self.set_avatar_personality_blend(avatar_id, primary_trait, secondary_trait, blend_ratio)
            
            # Set default emotional state
            default_state = defaults.get("default_emotional_state", EmotionalState.NEUTRAL.value)
            self.set_avatar_emotional_state(avatar_id, default_state)
            
            # Apply expression overrides
            expression_overrides = defaults.get("expression_overrides", {})
            if expression_overrides:
                self.expression_engine.set_avatar_expression_overrides(avatar_id, expression_overrides)
    
    def set_avatar_personality(self, avatar_id: str, personality_trait: str) -> bool:
        """
        Set personality for a specific avatar.
        
        Args:
            avatar_id: Avatar ID to set personality for
            personality_trait: Personality trait to set
            
        Returns:
            Boolean indicating success
        """
        # Verify personality trait exists
        if personality_trait not in self.personality_profiles:
            logger.error(f"Personality trait {personality_trait} not found in profiles")
            return False
        
        # Record previous personality in history
        if avatar_id in self.active_personalities:
            if avatar_id not in self.personality_history:
                self.personality_history[avatar_id] = []
            
            self.personality_history[avatar_id].append({
                "personality": self.active_personalities[avatar_id],
                "timestamp": time.time()
            })
            
            # Limit history length
            if len(self.personality_history[avatar_id]) > 10:
                self.personality_history[avatar_id].pop(0)
        
        # Set new active personality
        self.active_personalities[avatar_id] = personality_trait
        
        # Get personality profile
        profile = self.personality_profiles[personality_trait]
        
        # Apply expression settings
        expression_settings = profile.get("expression_settings", {})
        self.expression_engine.set_avatar_expression(avatar_id, expression_settings)
        
        # Apply behavior settings
        behavior_settings = profile.get("behavior_settings", {})
        self._apply_behavior_settings(avatar_id, behavior_settings)
        
        # Update state visualization
        self.state_visualizer.update_avatar_state(avatar_id, {
            "personality": personality_trait,
            "traits": profile.get("traits", {})
        })
        
        logger.info(f"Set personality for avatar {avatar_id}: {profile.get('name', personality_trait)}")
        return True
    
    def set_avatar_personality_blend(
        self, 
        avatar_id: str, 
        primary_trait: str, 
        secondary_trait: str, 
        blend_ratio: float = 0.7
    ) -> bool:
        """
        Set a blended personality for a specific avatar.
        
        Args:
            avatar_id: Avatar ID to set personality for
            primary_trait: Primary personality trait
            secondary_trait: Secondary personality trait
            blend_ratio: Blend ratio (0.0-1.0) for primary trait
            
        Returns:
            Boolean indicating success
        """
        # Verify personality traits exist
        if primary_trait not in self.personality_profiles:
            logger.error(f"Primary personality trait {primary_trait} not found in profiles")
            return False
        
        if secondary_trait not in self.personality_profiles:
            logger.error(f"Secondary personality trait {secondary_trait} not found in profiles")
            return False
        
        # Record previous personality in history
        if avatar_id in self.active_personalities:
            if avatar_id not in self.personality_history:
                self.personality_history[avatar_id] = []
            
            self.personality_history[avatar_id].append({
                "personality": self.active_personalities[avatar_id],
                "timestamp": time.time()
            })
            
            # Limit history length
            if len(self.personality_history[avatar_id]) > 10:
                self.personality_history[avatar_id].pop(0)
        
        # Set new active personality (store as blend)
        blend_id = f"{primary_trait}_{secondary_trait}_{blend_ratio}"
        self.active_personalities[avatar_id] = blend_id
        
        # Get personality profiles
        primary_profile = self.personality_profiles[primary_trait]
        secondary_profile = self.personality_profiles[secondary_trait]
        
        # Blend traits
        blended_traits = self._blend_traits(
            primary_profile.get("traits", {}),
            secondary_profile.get("traits", {}),
            blend_ratio
        )
        
        # Blend expression settings
        blended_expression = self._blend_expression_settings(
            primary_profile.get("expression_settings", {}),
            secondary_profile.get("expression_settings", {}),
            blend_ratio
        )
        
        # Blend behavior settings
        blended_behavior = self._blend_behavior_settings(
            primary_profile.get("behavior_settings", {}),
            secondary_profile.get("behavior_settings", {}),
            blend_ratio
        )
        
        # Apply blended expression settings
        self.expression_engine.set_avatar_expression(avatar_id, blended_expression)
        
        # Apply blended behavior settings
        self._apply_behavior_settings(avatar_id, blended_behavior)
        
        # Update state visualization
        self.state_visualizer.update_avatar_state(avatar_id, {
            "personality": blend_id,
            "primary_trait": primary_trait,
            "secondary_trait": secondary_trait,
            "blend_ratio": blend_ratio,
            "traits": blended_traits
        })
        
        logger.info(f"Set blended personality for avatar {avatar_id}: {primary_trait}/{secondary_trait} ({blend_ratio:.1f})")
        return True
    
    def _blend_traits(self, primary_traits: Dict, secondary_traits: Dict, blend_ratio: float) -> Dict:
        """
        Blend two sets of personality traits.
        
        Args:
            primary_traits: Primary trait values
            secondary_traits: Secondary trait values
            blend_ratio: Blend ratio (0.0-1.0) for primary traits
            
        Returns:
            Blended trait dictionary
        """
        blended_traits = {}
        
        # Combine all trait keys
        all_traits = set(primary_traits.keys()).union(set(secondary_traits.keys()))
        
        # Blend each trait
        for trait in all_traits:
            primary_value = primary_traits.get(trait, 0.0)
            secondary_value = secondary_traits.get(trait, 0.0)
            
            blended_value = (primary_value * blend_ratio) + (secondary_value * (1.0 - blend_ratio))
            blended_traits[trait] = blended_value
        
        return blended_traits
    
    def _blend_expression_settings(
        self, 
        primary_settings: Dict, 
        secondary_settings: Dict, 
        blend_ratio: float
    ) -> Dict:
        """
        Blend two sets of expression settings.
        
        Args:
            primary_settings: Primary expression settings
            secondary_settings: Secondary expression settings
            blend_ratio: Blend ratio (0.0-1.0) for primary settings
            
        Returns:
            Blended expression settings dictionary
        """
        blended_settings = {}
        
        # Combine all setting keys
        all_settings = set(primary_settings.keys()).union(set(secondary_settings.keys()))
        
        # Blend each setting
        for setting in all_settings:
            primary_value = primary_settings.get(setting)
            secondary_value = secondary_settings.get(setting)
            
            # For numeric values, blend mathematically
            if (isinstance(primary_value, (int, float)) and 
                isinstance(secondary_value, (int, float))):
                blended_value = (primary_value * blend_ratio) + (secondary_value * (1.0 - blend_ratio))
                blended_settings[setting] = blended_value
            
            # For string values, use primary if ratio > 0.5, otherwise secondary
            elif isinstance(primary_value, str) and isinstance(secondary_value, str):
                blended_settings[setting] = primary_value if blend_ratio >= 0.5 else secondary_value
            
            # For mixed types or None values, use the non-None value
            else:
                blended_settings[setting] = primary_value if primary_value is not None else secondary_value
        
        return blended_settings
    
    def _blend_behavior_settings(
        self, 
        primary_settings: Dict, 
        secondary_settings: Dict, 
        blend_ratio: float
    ) -> Dict:
        """
        Blend two sets of behavior settings.
        
        Args:
            primary_settings: Primary behavior settings
            secondary_settings: Secondary behavior settings
            blend_ratio: Blend ratio (0.0-1.0) for primary settings
            
        Returns:
            Blended behavior settings dictionary
        """
        # For behavior settings, we'll use the same blending logic as expression settings
        return self._blend_expression_settings(primary_settings, secondary_settings, blend_ratio)
    
    def _apply_behavior_settings(self, avatar_id: str, behavior_settings: Dict) -> None:
        """
        Apply behavior settings to an avatar.
        
        Args:
            avatar_id: Avatar ID to apply settings to
            behavior_settings: Behavior settings to apply
        """
        # In a real implementation, this would update avatar behavior parameters
        # For now, we'll just log the intent
        logger.debug(f"Applying behavior settings to avatar {avatar_id}: {behavior_settings}")
        
        # Update state visualization with behavior settings
        self.state_visualizer.update_avatar_behavior(avatar_id, behavior_settings)
    
    def set_avatar_emotional_state(self, avatar_id: str, emotional_state: str) -> bool:
        """
        Set emotional state for a specific avatar.
        
        Args:
            avatar_id: Avatar ID to set emotional state for
            emotional_state: Emotional state to set
            
        Returns:
            Boolean indicating success
        """
        # Verify emotional state exists
        if not any(state.value == emotional_state for state in EmotionalState):
            logger.error(f"Emotional state {emotional_state} not found")
            return False
        
        # Set new emotional state
        self.emotional_states[avatar_id] = emotional_state
        
        # Apply emotional state to expression engine
        self.expression_engine.set_avatar_emotional_state(avatar_id, emotional_state)
        
        # Update state visualization
        self.state_visualizer.update_avatar_state(avatar_id, {
            "emotional_state": emotional_state
        })
        
        logger.info(f"Set emotional state for avatar {avatar_id}: {emotional_state}")
        return True
    
    def get_avatar_personality(self, avatar_id: str) -> Dict:
        """
        Get personality information for a specific avatar.
        
        Args:
            avatar_id: Avatar ID to get personality for
            
        Returns:
            Personality information dictionary
        """
        if avatar_id not in self.active_personalities:
            return {}
        
        personality = self.active_personalities[avatar_id]
        
        # Check if this is a blended personality
        if "_" in personality:
            parts = personality.split("_")
            if len(parts) >= 3:
                primary_trait = parts[0]
                secondary_trait = parts[1]
                try:
                    blend_ratio = float(parts[2])
                except ValueError:
                    blend_ratio = 0.7
                
                return {
                    "type": "blend",
                    "primary_trait": primary_trait,
                    "secondary_trait": secondary_trait,
                    "blend_ratio": blend_ratio,
                    "primary_profile": self.personality_profiles.get(primary_trait, {}),
                    "secondary_profile": self.personality_profiles.get(secondary_trait, {})
                }
        
        # Standard personality
        return {
            "type": "standard",
            "trait": personality,
            "profile": self.personality_profiles.get(personality, {})
        }
    
    def get_avatar_emotional_state(self, avatar_id: str) -> str:
        """
        Get emotional state for a specific avatar.
        
        Args:
            avatar_id: Avatar ID to get emotional state for
            
        Returns:
            Emotional state string
        """
        return self.emotional_states.get(avatar_id, EmotionalState.NEUTRAL.value)
    
    def get_available_personality_traits(self) -> List[Dict]:
        """
        Get available personality traits.
        
        Returns:
            List of available personality trait information
        """
        traits = []
        
        for trait_id, profile in self.personality_profiles.items():
            traits.append({
                "id": trait_id,
                "name": profile.get("name", trait_id),
                "description": profile.get("description", "")
            })
        
        return traits
    
    def get_available_emotional_states(self) -> List[Dict]:
        """
        Get available emotional states.
        
        Returns:
            List of available emotional state information
        """
        states = []
        
        for state in EmotionalState:
            states.append({
                "id": state.value,
                "name": state.name.capitalize()
            })
        
        return states
    
    def create_custom_personality(self, personality_definition: Dict) -> bool:
        """
        Create or update a custom personality.
        
        Args:
            personality_definition: Custom personality definition
            
        Returns:
            Boolean indicating success
        """
        # Validate required fields
        required_fields = ["id", "name", "traits", "expression_settings", "behavior_settings"]
        for field in required_fields:
            if field not in personality_definition:
                logger.error(f"Missing required field in custom personality definition: {field}")
                return False
        
        # Set custom personality
        personality_id = personality_definition["id"]
        self.personality_profiles[personality_id] = personality_definition
        
        logger.info(f"Created custom personality: {personality_definition.get('name')}")
        return True
    
    def get_personality_profile(self, personality_trait: str) -> Dict:
        """
        Get personality profile.
        
        Args:
            personality_trait: Personality trait to get profile for
            
        Returns:
            Personality profile dictionary
        """
        return self.personality_profiles.get(personality_trait, {})
    
    def get_layer_personality_defaults(self, layer_id: str = None) -> Dict:
        """
        Get layer personality defaults.
        
        Args:
            layer_id: Optional layer ID to get defaults for
            
        Returns:
            Layer personality defaults dictionary
        """
        if layer_id:
            return self.layer_personality_defaults.get(layer_id, {})
        else:
            return self.layer_personality_defaults
    
    def adapt_to_context(self, context_data: Dict) -> None:
        """
        Adapt avatar personalities based on context data.
        
        Args:
            context_data: Context data to adapt to
        """
        # This method is called directly when needed, in addition to
        # the automatic adaptations from context change events
        
        # Check for system state
        system_context = context_data.get("system", {})
        if "system_state" in system_context:
            system_state = system_context["system_state"]
            
            # Update emotional states based on system state
            if system_state == "normal":
                self._update_all_emotional_states(EmotionalState.NEUTRAL.value)
            elif system_state == "warning":
                self._update_all_emotional_states(EmotionalState.ALERT.value)
            elif system_state == "critical":
                self._update_all_emotional_states(EmotionalState.URGENT.value)
            elif system_state == "maintenance":
                self._update_all_emotional_states(EmotionalState.REFLECTIVE.value)
        
        # Check for task focus
        task_context = context_data.get("task", {})
        if "focus_layer" in task_context:
            focus_layer = task_context["focus_layer"]
            
            # Highlight the focused layer avatar
            if focus_layer:
                avatar_id = f"{focus_layer}_avatar"
                self.set_avatar_emotional_state(avatar_id, EmotionalState.FOCUSED.value)
                
                # Make other avatars neutral or reflective
                for layer_id in self.layer_personality_defaults.keys():
                    if layer_id != focus_layer:
                        other_avatar_id = f"{layer_id}_avatar"
                        self.set_avatar_emotional_state(other_avatar_id, EmotionalState.NEUTRAL.value)
    
    def generate_random_personality_shift(self, avatar_id: str, intensity: float = 0.3) -> bool:
        """
        Generate a random subtle shift in avatar personality.
        
        Args:
            avatar_id: Avatar ID to shift personality for
            intensity: Intensity of the shift (0.0-1.0)
            
        Returns:
            Boolean indicating success
        """
        # Get current personality
        current_info = self.get_avatar_personality(avatar_id)
        if not current_info:
            return False
        
        # For blended personalities
        if current_info.get("type") == "blend":
            primary_trait = current_info.get("primary_trait")
            secondary_trait = current_info.get("secondary_trait")
            current_ratio = current_info.get("blend_ratio", 0.7)
            
            # Shift the blend ratio slightly
            shift = (random.random() * 2 - 1) * intensity * 0.3  # Max ±0.3 * intensity
            new_ratio = max(0.1, min(0.9, current_ratio + shift))
            
            # Apply the shifted blend
            return self.set_avatar_personality_blend(avatar_id, primary_trait, secondary_trait, new_ratio)
        
        # For standard personalities
        else:
            current_trait = current_info.get("trait")
            if not current_trait:
                return False
            
            # Get all traits
            all_traits = list(self.personality_profiles.keys())
            
            # Randomly decide whether to blend or switch
            if random.random() < 0.7:  # 70% chance to blend
                # Pick a random secondary trait
                secondary_options = [t for t in all_traits if t != current_trait]
                if not secondary_options:
                    return False
                
                secondary_trait = random.choice(secondary_options)
                blend_ratio = 0.7  # Favor the current trait
                
                # Apply the blend
                return self.set_avatar_personality_blend(avatar_id, current_trait, secondary_trait, blend_ratio)
            else:  # 30% chance to switch
                # Get similar traits (implementation would depend on trait relationships)
                # For now, just pick a random trait
                new_options = [t for t in all_traits if t != current_trait]
                if not new_options:
                    return False
                
                new_trait = random.choice(new_options)
                
                # Apply the new trait
                return self.set_avatar_personality(avatar_id, new_trait)
"""
