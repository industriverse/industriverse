"""
Capsule Ritual Engine for the Industriverse UI/UX Layer.

This module introduces emotionally resonant transitions (glow, ripple, morphs) 
when human users override capsules. It makes agency a ritual, not just a button click.

Author: Manus
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
import uuid
import json
import random
import math

class RitualType(Enum):
    """Enumeration of capsule ritual types."""
    OVERRIDE = "override"  # Human overrides agent decision
    APPROVAL = "approval"  # Human approves agent decision
    DELEGATION = "delegation"  # Human delegates task to agent
    COLLABORATION = "collaboration"  # Human collaborates with agent
    ESCALATION = "escalation"  # Agent escalates to human
    HANDOFF = "handoff"  # Agent hands off to human
    CUSTOM = "custom"  # Custom ritual type

class RitualIntensity(Enum):
    """Enumeration of ritual intensity levels."""
    SUBTLE = "subtle"  # Subtle visual effects
    MODERATE = "moderate"  # Moderate visual effects
    PRONOUNCED = "pronounced"  # Pronounced visual effects
    DRAMATIC = "dramatic"  # Dramatic visual effects
    CUSTOM = "custom"  # Custom intensity level

class RitualEffect(Enum):
    """Enumeration of ritual visual effects."""
    GLOW = "glow"  # Glowing effect
    RIPPLE = "ripple"  # Ripple effect
    MORPH = "morph"  # Morphing effect
    PULSE = "pulse"  # Pulsing effect
    PARTICLES = "particles"  # Particle effect
    COLOR_SHIFT = "color_shift"  # Color shifting effect
    SCALE = "scale"  # Scaling effect
    ROTATION = "rotation"  # Rotation effect
    CUSTOM = "custom"  # Custom effect

class RitualSound(Enum):
    """Enumeration of ritual sound effects."""
    CHIME = "chime"  # Chime sound
    WHOOSH = "whoosh"  # Whoosh sound
    CLICK = "click"  # Click sound
    BELL = "bell"  # Bell sound
    HUM = "hum"  # Humming sound
    TONE = "tone"  # Tone sound
    CUSTOM = "custom"  # Custom sound

class RitualHaptic(Enum):
    """Enumeration of ritual haptic feedback patterns."""
    PULSE = "pulse"  # Pulse haptic feedback
    DOUBLE_PULSE = "double_pulse"  # Double pulse haptic feedback
    TRIPLE_PULSE = "triple_pulse"  # Triple pulse haptic feedback
    LONG_PULSE = "long_pulse"  # Long pulse haptic feedback
    RAMP_UP = "ramp_up"  # Ramp up haptic feedback
    RAMP_DOWN = "ramp_down"  # Ramp down haptic feedback
    CUSTOM = "custom"  # Custom haptic feedback

class RitualTemplate:
    """Represents a template for a capsule ritual."""
    
    def __init__(self,
                 template_id: str,
                 ritual_type: RitualType,
                 effects: List[RitualEffect],
                 intensity: RitualIntensity = RitualIntensity.MODERATE,
                 duration: float = 1.0,
                 sound: Optional[RitualSound] = None,
                 haptic: Optional[RitualHaptic] = None,
                 color: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a ritual template.
        
        Args:
            template_id: Unique identifier for this template
            ritual_type: Type of ritual
            effects: List of visual effects for this ritual
            intensity: Intensity level of the ritual
            duration: Duration of the ritual in seconds
            sound: Optional sound effect for this ritual
            haptic: Optional haptic feedback for this ritual
            color: Optional color for this ritual (hex code)
            metadata: Additional metadata for this template
        """
        self.template_id = template_id
        self.ritual_type = ritual_type
        self.effects = effects
        self.intensity = intensity
        self.duration = duration
        self.sound = sound
        self.haptic = haptic
        self.color = color
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this template to a dictionary representation."""
        return {
            "template_id": self.template_id,
            "ritual_type": self.ritual_type.value,
            "effects": [effect.value for effect in self.effects],
            "intensity": self.intensity.value,
            "duration": self.duration,
            "sound": self.sound.value if self.sound else None,
            "haptic": self.haptic.value if self.haptic else None,
            "color": self.color,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RitualTemplate':
        """Create a ritual template from a dictionary representation."""
        return cls(
            template_id=data["template_id"],
            ritual_type=RitualType(data["ritual_type"]),
            effects=[RitualEffect(effect) for effect in data["effects"]],
            intensity=RitualIntensity(data["intensity"]),
            duration=data["duration"],
            sound=RitualSound(data["sound"]) if data.get("sound") else None,
            haptic=RitualHaptic(data["haptic"]) if data.get("haptic") else None,
            color=data.get("color"),
            metadata=data.get("metadata", {})
        )

class CapsuleRitual:
    """Represents an instance of a capsule ritual."""
    
    def __init__(self,
                 ritual_id: str,
                 template_id: str,
                 capsule_id: str,
                 user_id: str,
                 start_time: float,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a capsule ritual.
        
        Args:
            ritual_id: Unique identifier for this ritual
            template_id: ID of the template this ritual is based on
            capsule_id: ID of the capsule this ritual is associated with
            user_id: ID of the user who triggered this ritual
            start_time: Start time of the ritual
            metadata: Additional metadata for this ritual
        """
        self.ritual_id = ritual_id
        self.template_id = template_id
        self.capsule_id = capsule_id
        self.user_id = user_id
        self.start_time = start_time
        self.metadata = metadata or {}
        self.is_active = True
        self.end_time: Optional[float] = None
        
    def end_ritual(self) -> None:
        """End the ritual."""
        self.is_active = False
        self.end_time = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this ritual to a dictionary representation."""
        return {
            "ritual_id": self.ritual_id,
            "template_id": self.template_id,
            "capsule_id": self.capsule_id,
            "user_id": self.user_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapsuleRitual':
        """Create a capsule ritual from a dictionary representation."""
        ritual = cls(
            ritual_id=data["ritual_id"],
            template_id=data["template_id"],
            capsule_id=data["capsule_id"],
            user_id=data["user_id"],
            start_time=data["start_time"],
            metadata=data.get("metadata", {})
        )
        
        ritual.is_active = data.get("is_active", True)
        ritual.end_time = data.get("end_time")
        
        return ritual

class CapsuleRitualEngine:
    """
    Introduces emotionally resonant transitions when human users override capsules.
    
    This class provides:
    - Ritual templates for different types of human-agent interactions
    - Visual effects for rituals (glow, ripple, morph, etc.)
    - Sound and haptic feedback for rituals
    - Ritual management and playback
    - Integration with the Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Capsule Ritual Engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.templates: Dict[str, RitualTemplate] = {}
        self.rituals: Dict[str, CapsuleRitual] = {}
        self.logger = logging.getLogger(__name__)
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        
        # Initialize default templates
        self._initialize_default_templates()
        
    def _initialize_default_templates(self) -> None:
        """Initialize default ritual templates."""
        # Override ritual
        self.register_template(
            template_id="default_override",
            ritual_type=RitualType.OVERRIDE,
            effects=[RitualEffect.GLOW, RitualEffect.RIPPLE],
            intensity=RitualIntensity.PRONOUNCED,
            duration=1.2,
            sound=RitualSound.WHOOSH,
            haptic=RitualHaptic.DOUBLE_PULSE,
            color="#FF5733"
        )
        
        # Approval ritual
        self.register_template(
            template_id="default_approval",
            ritual_type=RitualType.APPROVAL,
            effects=[RitualEffect.GLOW, RitualEffect.PULSE],
            intensity=RitualIntensity.MODERATE,
            duration=0.8,
            sound=RitualSound.CHIME,
            haptic=RitualHaptic.PULSE,
            color="#33FF57"
        )
        
        # Delegation ritual
        self.register_template(
            template_id="default_delegation",
            ritual_type=RitualType.DELEGATION,
            effects=[RitualEffect.MORPH, RitualEffect.PARTICLES],
            intensity=RitualIntensity.MODERATE,
            duration=1.0,
            sound=RitualSound.WHOOSH,
            haptic=RitualHaptic.LONG_PULSE,
            color="#3357FF"
        )
        
        # Collaboration ritual
        self.register_template(
            template_id="default_collaboration",
            ritual_type=RitualType.COLLABORATION,
            effects=[RitualEffect.COLOR_SHIFT, RitualEffect.PULSE],
            intensity=RitualIntensity.SUBTLE,
            duration=1.5,
            sound=RitualSound.HUM,
            haptic=RitualHaptic.RAMP_UP,
            color="#AA33FF"
        )
        
        # Escalation ritual
        self.register_template(
            template_id="default_escalation",
            ritual_type=RitualType.ESCALATION,
            effects=[RitualEffect.PULSE, RitualEffect.SCALE],
            intensity=RitualIntensity.DRAMATIC,
            duration=1.0,
            sound=RitualSound.BELL,
            haptic=RitualHaptic.TRIPLE_PULSE,
            color="#FF3333"
        )
        
        # Handoff ritual
        self.register_template(
            template_id="default_handoff",
            ritual_type=RitualType.HANDOFF,
            effects=[RitualEffect.MORPH, RitualEffect.ROTATION],
            intensity=RitualIntensity.MODERATE,
            duration=1.2,
            sound=RitualSound.TONE,
            haptic=RitualHaptic.RAMP_DOWN,
            color="#33FFFF"
        )
        
    def register_template(self,
                        template_id: str,
                        ritual_type: RitualType,
                        effects: List[RitualEffect],
                        intensity: RitualIntensity = RitualIntensity.MODERATE,
                        duration: float = 1.0,
                        sound: Optional[RitualSound] = None,
                        haptic: Optional[RitualHaptic] = None,
                        color: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a ritual template.
        
        Args:
            template_id: Unique identifier for this template
            ritual_type: Type of ritual
            effects: List of visual effects for this ritual
            intensity: Intensity level of the ritual
            duration: Duration of the ritual in seconds
            sound: Optional sound effect for this ritual
            haptic: Optional haptic feedback for this ritual
            color: Optional color for this ritual (hex code)
            metadata: Additional metadata for this template
        """
        if template_id in self.templates:
            self.logger.warning(f"Template with ID {template_id} already exists, overwriting")
            
        self.templates[template_id] = RitualTemplate(
            template_id=template_id,
            ritual_type=ritual_type,
            effects=effects,
            intensity=intensity,
            duration=duration,
            sound=sound,
            haptic=haptic,
            color=color,
            metadata=metadata or {}
        )
        
    def unregister_template(self, template_id: str) -> bool:
        """
        Unregister a ritual template.
        
        Args:
            template_id: ID of the template to unregister
            
        Returns:
            True if the template was unregistered, False if not found
        """
        if template_id not in self.templates:
            return False
            
        del self.templates[template_id]
        return True
    
    def start_ritual(self,
                   capsule_id: str,
                   user_id: str,
                   ritual_type: RitualType,
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Start a capsule ritual.
        
        Args:
            capsule_id: ID of the capsule
            user_id: ID of the user who triggered this ritual
            ritual_type: Type of ritual
            metadata: Additional metadata for this ritual
            
        Returns:
            ID of the created ritual, or None if no template was found for the ritual type
        """
        # Find template for this ritual type
        template_id = None
        for tid, template in self.templates.items():
            if template.ritual_type == ritual_type:
                template_id = tid
                break
                
        if template_id is None:
            template_id = f"default_{ritual_type.value}"
            if template_id not in self.templates:
                self.logger.warning(f"No template found for ritual type {ritual_type.value}")
                return None
                
        # Create ritual ID
        ritual_id = str(uuid.uuid4())
        
        # Create ritual
        self.rituals[ritual_id] = CapsuleRitual(
            ritual_id=ritual_id,
            template_id=template_id,
            capsule_id=capsule_id,
            user_id=user_id,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "ritual_started",
            "ritual_id": ritual_id,
            "template_id": template_id,
            "capsule_id": capsule_id,
            "user_id": user_id,
            "ritual_type": ritual_type.value
        })
        
        return ritual_id
    
    def end_ritual(self, ritual_id: str) -> bool:
        """
        End a capsule ritual.
        
        Args:
            ritual_id: ID of the ritual to end
            
        Returns:
            True if the ritual was ended, False if not found
        """
        if ritual_id not in self.rituals:
            return False
            
        ritual = self.rituals[ritual_id]
        
        # End ritual
        ritual.end_ritual()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "ritual_ended",
            "ritual_id": ritual_id,
            "capsule_id": ritual.capsule_id,
            "user_id": ritual.user_id
        })
        
        return True
    
    def update(self, dt: float) -> None:
        """
        Update all active rituals.
        
        Args:
            dt: Time step in seconds
        """
        current_time = time.time()
        
        # Update each ritual
        for ritual_id in list(self.rituals.keys()):
            ritual = self.rituals[ritual_id]
            
            # Skip inactive rituals
            if not ritual.is_active:
                continue
                
            # Get template
            if ritual.template_id not in self.templates:
                self.logger.warning(f"Template {ritual.template_id} not found for ritual {ritual_id}")
                ritual.end_ritual()
                continue
                
            template = self.templates[ritual.template_id]
            
            # Check if ritual duration has elapsed
            elapsed = current_time - ritual.start_time
            if elapsed >= template.duration:
                ritual.end_ritual()
                
                # Dispatch event
                self._dispatch_event({
                    "event_type": "ritual_completed",
                    "ritual_id": ritual_id,
                    "capsule_id": ritual.capsule_id,
                    "user_id": ritual.user_id
                })
                
        # Clean up completed rituals
        for ritual_id in list(self.rituals.keys()):
            ritual = self.rituals[ritual_id]
            
            if not ritual.is_active and current_time - ritual.end_time > 3600:  # 1 hour
                del self.rituals[ritual_id]
                
    def get_template(self, template_id: str) -> Optional[RitualTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template
            
        Returns:
            The template, or None if not found
        """
        return self.templates.get(template_id)
    
    def get_all_templates(self) -> List[RitualTemplate]:
        """
        Get all templates.
        
        Returns:
            List of all templates
        """
        return list(self.templates.values())
    
    def get_ritual(self, ritual_id: str) -> Optional[CapsuleRitual]:
        """
        Get a ritual by ID.
        
        Args:
            ritual_id: ID of the ritual
            
        Returns:
            The ritual, or None if not found
        """
        return self.rituals.get(ritual_id)
    
    def get_active_rituals(self) -> List[CapsuleRitual]:
        """
        Get all active rituals.
        
        Returns:
            List of all active rituals
        """
        return [r for r in self.rituals.values() if r.is_active]
    
    def get_rituals_by_capsule(self, capsule_id: str) -> List[CapsuleRitual]:
        """
        Get all rituals for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            List of all rituals for the capsule
        """
        return [r for r in self.rituals.values() if r.capsule_id == capsule_id]
    
    def get_active_ritual_by_capsule(self, capsule_id: str) -> Optional[CapsuleRitual]:
        """
        Get the active ritual for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            The active ritual for the capsule, or None if not found
        """
        for ritual in self.rituals.values():
            if ritual.capsule_id == capsule_id and ritual.is_active:
                return ritual
                
        return None
    
    def get_ritual_css(self, ritual_id: str) -> Optional[str]:
        """
        Get CSS representation of a ritual for web rendering.
        
        Args:
            ritual_id: ID of the ritual
            
        Returns:
            CSS string for the ritual, or None if not found
        """
        ritual = self.get_ritual(ritual_id)
        if not ritual or not ritual.is_active:
            return None
            
        template = self.get_template(ritual.template_id)
        if not template:
            return None
            
        css_parts = []
        
        # Calculate progress (0.0 to 1.0)
        elapsed = time.time() - ritual.start_time
        progress = min(elapsed / template.duration, 1.0)
        
        # Base styles
        if template.color:
            css_parts.append(f"--ritual-color: {template.color};")
            
        # Apply effects based on template
        for effect in template.effects:
            if effect == RitualEffect.GLOW:
                intensity_factor = self._get_intensity_factor(template.intensity)
                glow_size = 20 * intensity_factor
                glow_opacity = 0.7 * intensity_factor
                
                # Glow animation
                if progress < 0.5:
                    # Ramp up
                    current_glow = glow_size * (progress / 0.5)
                    current_opacity = glow_opacity * (progress / 0.5)
                else:
                    # Ramp down
                    current_glow = glow_size * (1.0 - (progress - 0.5) / 0.5)
                    current_opacity = glow_opacity * (1.0 - (progress - 0.5) / 0.5)
                    
                css_parts.append(f"box-shadow: 0 0 {current_glow}px {current_opacity * 100}% var(--ritual-color);")
                
            elif effect == RitualEffect.RIPPLE:
                intensity_factor = self._get_intensity_factor(template.intensity)
                max_scale = 1.5 * intensity_factor
                
                # Ripple animation
                if progress < 0.3:
                    # Initial expansion
                    current_scale = 1.0 + (max_scale - 1.0) * (progress / 0.3)
                    current_opacity = 1.0
                elif progress < 0.7:
                    # Hold
                    current_scale = max_scale
                    current_opacity = 1.0
                else:
                    # Fade out
                    current_scale = max_scale
                    current_opacity = 1.0 - (progress - 0.7) / 0.3
                    
                css_parts.append(f"--ripple-scale: {current_scale};")
                css_parts.append(f"--ripple-opacity: {current_opacity};")
                css_parts.append("position: relative;")
                css_parts.append("overflow: visible;")
                
                # Add ::after pseudo-element for ripple
                css_parts.append("&::after {")
                css_parts.append("  content: '';")
                css_parts.append("  position: absolute;")
                css_parts.append("  top: 0;")
                css_parts.append("  left: 0;")
                css_parts.append("  right: 0;")
                css_parts.append("  bottom: 0;")
                css_parts.append("  border-radius: inherit;")
                css_parts.append("  border: 2px solid var(--ritual-color);")
                css_parts.append("  opacity: var(--ripple-opacity);")
                css_parts.append("  transform: scale(var(--ripple-scale));")
                css_parts.append("  pointer-events: none;")
                css_parts.append("}")
                
            elif effect == RitualEffect.MORPH:
                intensity_factor = self._get_intensity_factor(template.intensity)
                max_morph = 0.2 * intensity_factor
                
                # Morph animation
                if progress < 0.5:
                    # Morph in
                    current_morph = max_morph * (progress / 0.5)
                else:
                    # Morph out
                    current_morph = max_morph * (1.0 - (progress - 0.5) / 0.5)
                    
                # Apply morphing using border-radius
                css_parts.append(f"border-radius: calc(var(--base-border-radius, 8px) + {current_morph * 100}%);")
                
            elif effect == RitualEffect.PULSE:
                intensity_factor = self._get_intensity_factor(template.intensity)
                max_pulse = 0.1 * intensity_factor
                
                # Pulse animation (using sine wave)
                pulse_frequency = 5.0  # Higher = more pulses
                pulse_phase = progress * pulse_frequency * Math.PI * 2
                current_pulse = max_pulse * Math.sin(pulse_phase)
                
                css_parts.append(f"transform: scale({1.0 + current_pulse});")
                
            elif effect == RitualEffect.PARTICLES:
                # Particles are handled by JavaScript, just add a class
                css_parts.append("--particles-active: 1;")
                css_parts.append(f"--particles-intensity: {self._get_intensity_factor(template.intensity)};")
                css_parts.append(f"--particles-progress: {progress};")
                css_parts.append(f"--particles-color: var(--ritual-color);")
                
            elif effect == RitualEffect.COLOR_SHIFT:
                intensity_factor = self._get_intensity_factor(template.intensity)
                
                # Color shift animation
                if progress < 0.5:
                    # Shift to ritual color
                    current_shift = progress / 0.5
                else:
                    # Shift back to original
                    current_shift = 1.0 - (progress - 0.5) / 0.5
                    
                css_parts.append(f"--color-shift: {current_shift};")
                css_parts.append("background-color: color-mix(in srgb, var(--original-color) calc((1 - var(--color-shift)) * 100%), var(--ritual-color) calc(var(--color-shift) * 100%));")
                css_parts.append("border-color: color-mix(in srgb, var(--original-border-color) calc((1 - var(--color-shift)) * 100%), var(--ritual-color) calc(var(--color-shift) * 100%));")
                
            elif effect == RitualEffect.SCALE:
                intensity_factor = self._get_intensity_factor(template.intensity)
                max_scale = 1.0 + (0.3 * intensity_factor)
                min_scale = 1.0 - (0.1 * intensity_factor)
                
                # Scale animation
                if progress < 0.2:
                    # Scale down
                    current_scale = 1.0 - (1.0 - min_scale) * (progress / 0.2)
                elif progress < 0.5:
                    # Scale up
                    progress_normalized = (progress - 0.2) / 0.3
                    current_scale = min_scale + (max_scale - min_scale) * progress_normalized
                else:
                    # Scale back to normal
                    progress_normalized = (progress - 0.5) / 0.5
                    current_scale = max_scale - (max_scale - 1.0) * progress_normalized
                    
                css_parts.append(f"transform: scale({current_scale});")
                
            elif effect == RitualEffect.ROTATION:
                intensity_factor = self._get_intensity_factor(template.intensity)
                max_rotation = 5 * intensity_factor  # degrees
                
                # Rotation animation
                if progress < 0.25:
                    # Rotate one way
                    current_rotation = max_rotation * (progress / 0.25)
                elif progress < 0.75:
                    # Rotate the other way
                    progress_normalized = (progress - 0.25) / 0.5
                    current_rotation = max_rotation - (2 * max_rotation * progress_normalized)
                else:
                    # Rotate back to normal
                    progress_normalized = (progress - 0.75) / 0.25
                    current_rotation = -max_rotation + (max_rotation * progress_normalized)
                    
                css_parts.append(f"transform: rotate({current_rotation}deg);")
                
        return "\n".join(css_parts)
    
    def get_ritual_keyframes(self, ritual_id: str) -> Optional[str]:
        """
        Get CSS keyframes for a ritual for web rendering.
        
        Args:
            ritual_id: ID of the ritual
            
        Returns:
            CSS keyframes string for the ritual, or None if not found
        """
        ritual = self.get_ritual(ritual_id)
        if not ritual or not ritual.is_active:
            return None
            
        template = self.get_template(ritual.template_id)
        if not template:
            return None
            
        keyframes = []
        
        # Generate keyframes based on effects
        for effect in template.effects:
            if effect == RitualEffect.GLOW:
                intensity_factor = self._get_intensity_factor(template.intensity)
                glow_size = 20 * intensity_factor
                glow_opacity = 0.7 * intensity_factor
                
                keyframes.append(f"@keyframes ritual-glow-{ritual_id} {{")
                keyframes.append(f"  0% {{ box-shadow: 0 0 0px 0% var(--ritual-color); }}")
                keyframes.append(f"  50% {{ box-shadow: 0 0 {glow_size}px {glow_opacity * 100}% var(--ritual-color); }}")
                keyframes.append(f"  100% {{ box-shadow: 0 0 0px 0% var(--ritual-color); }}")
                keyframes.append("}")
                
            elif effect == RitualEffect.RIPPLE:
                intensity_factor = self._get_intensity_factor(template.intensity)
                max_scale = 1.5 * intensity_factor
                
                keyframes.append(f"@keyframes ritual-ripple-{ritual_id} {{")
                keyframes.append(f"  0% {{ transform: scale(1.0); opacity: 1.0; }}")
                keyframes.append(f"  30% {{ transform: scale({max_scale}); opacity: 1.0; }}")
                keyframes.append(f"  70% {{ transform: scale({max_scale}); opacity: 1.0; }}")
                keyframes.append(f"  100% {{ transform: scale({max_scale}); opacity: 0.0; }}")
                keyframes.append("}")
                
            elif effect == RitualEffect.PULSE:
                intensity_factor = self._get_intensity_factor(template.intensity)
                max_pulse = 0.1 * intensity_factor
                
                keyframes.append(f"@keyframes ritual-pulse-{ritual_id} {{")
                keyframes.append(f"  0% {{ transform: scale(1.0); }}")
                keyframes.append(f"  25% {{ transform: scale({1.0 + max_pulse}); }}")
                keyframes.append(f"  50% {{ transform: scale(1.0); }}")
                keyframes.append(f"  75% {{ transform: scale({1.0 - max_pulse / 2}); }}")
                keyframes.append(f"  100% {{ transform: scale(1.0); }}")
                keyframes.append("}")
                
            elif effect == RitualEffect.COLOR_SHIFT:
                keyframes.append(f"@keyframes ritual-color-shift-{ritual_id} {{")
                keyframes.append(f"  0% {{ --color-shift: 0; }}")
                keyframes.append(f"  50% {{ --color-shift: 1; }}")
                keyframes.append(f"  100% {{ --color-shift: 0; }}")
                keyframes.append("}")
                
            elif effect == RitualEffect.SCALE:
                intensity_factor = self._get_intensity_factor(template.intensity)
                max_scale = 1.0 + (0.3 * intensity_factor)
                min_scale = 1.0 - (0.1 * intensity_factor)
                
                keyframes.append(f"@keyframes ritual-scale-{ritual_id} {{")
                keyframes.append(f"  0% {{ transform: scale(1.0); }}")
                keyframes.append(f"  20% {{ transform: scale({min_scale}); }}")
                keyframes.append(f"  50% {{ transform: scale({max_scale}); }}")
                keyframes.append(f"  100% {{ transform: scale(1.0); }}")
                keyframes.append("}")
                
            elif effect == RitualEffect.ROTATION:
                intensity_factor = self._get_intensity_factor(template.intensity)
                max_rotation = 5 * intensity_factor  # degrees
                
                keyframes.append(f"@keyframes ritual-rotation-{ritual_id} {{")
                keyframes.append(f"  0% {{ transform: rotate(0deg); }}")
                keyframes.append(f"  25% {{ transform: rotate({max_rotation}deg); }}")
                keyframes.append(f"  75% {{ transform: rotate({-max_rotation}deg); }}")
                keyframes.append(f"  100% {{ transform: rotate(0deg); }}")
                keyframes.append("}")
                
        return "\n".join(keyframes)
    
    def get_ritual_js(self, ritual_id: str) -> Optional[str]:
        """
        Get JavaScript code for a ritual for web rendering.
        
        Args:
            ritual_id: ID of the ritual
            
        Returns:
            JavaScript code for the ritual, or None if not found
        """
        ritual = self.get_ritual(ritual_id)
        if not ritual or not ritual.is_active:
            return None
            
        template = self.get_template(ritual.template_id)
        if not template:
            return None
            
        js_parts = []
        
        # Generate JavaScript based on effects
        for effect in template.effects:
            if effect == RitualEffect.PARTICLES:
                intensity_factor = self._get_intensity_factor(template.intensity)
                
                js_parts.append(f"// Particle effect for ritual {ritual_id}")
                js_parts.append(f"(function() {{")
                js_parts.append(f"  const capsuleElement = document.getElementById('capsule-{ritual.capsule_id}');")
                js_parts.append(f"  if (!capsuleElement) return;")
                js_parts.append(f"")
                js_parts.append(f"  const particleCount = Math.floor(30 * {intensity_factor});")
                js_parts.append(f"  const particleContainer = document.createElement('div');")
                js_parts.append(f"  particleContainer.className = 'ritual-particles';")
                js_parts.append(f"  particleContainer.style.position = 'absolute';")
                js_parts.append(f"  particleContainer.style.top = '0';")
                js_parts.append(f"  particleContainer.style.left = '0';")
                js_parts.append(f"  particleContainer.style.width = '100%';")
                js_parts.append(f"  particleContainer.style.height = '100%';")
                js_parts.append(f"  particleContainer.style.pointerEvents = 'none';")
                js_parts.append(f"  particleContainer.style.zIndex = '10';")
                js_parts.append(f"  particleContainer.style.overflow = 'visible';")
                js_parts.append(f"")
                js_parts.append(f"  capsuleElement.appendChild(particleContainer);")
                js_parts.append(f"")
                js_parts.append(f"  // Create particles")
                js_parts.append(f"  for (let i = 0; i < particleCount; i++) {{")
                js_parts.append(f"    const particle = document.createElement('div');")
                js_parts.append(f"    particle.className = 'ritual-particle';")
                js_parts.append(f"    particle.style.position = 'absolute';")
                js_parts.append(f"    particle.style.width = '4px';")
                js_parts.append(f"    particle.style.height = '4px';")
                js_parts.append(f"    particle.style.borderRadius = '50%';")
                js_parts.append(f"    particle.style.backgroundColor = getComputedStyle(capsuleElement).getPropertyValue('--ritual-color');")
                js_parts.append(f"    particle.style.opacity = '0';")
                js_parts.append(f"")
                js_parts.append(f"    // Random starting position within the capsule")
                js_parts.append(f"    const x = Math.random() * 100;")
                js_parts.append(f"    const y = Math.random() * 100;")
                js_parts.append(f"    particle.style.left = `${{x}}%`;")
                js_parts.append(f"    particle.style.top = `${{y}}%`;")
                js_parts.append(f"")
                js_parts.append(f"    // Random direction and speed")
                js_parts.append(f"    const angle = Math.random() * Math.PI * 2;")
                js_parts.append(f"    const speed = 50 + Math.random() * 100;  // pixels per second")
                js_parts.append(f"    const vx = Math.cos(angle) * speed;")
                js_parts.append(f"    const vy = Math.sin(angle) * speed;")
                js_parts.append(f"")
                js_parts.append(f"    // Random delay")
                js_parts.append(f"    const delay = Math.random() * 0.5;  // seconds")
                js_parts.append(f"    const duration = 0.5 + Math.random() * 0.5;  // seconds")
                js_parts.append(f"")
                js_parts.append(f"    // Add to container")
                js_parts.append(f"    particleContainer.appendChild(particle);")
                js_parts.append(f"")
                js_parts.append(f"    // Animate")
                js_parts.append(f"    setTimeout(() => {{")
                js_parts.append(f"      particle.style.transition = `opacity ${{duration}}s ease-out, transform ${{duration}}s ease-out`;")
                js_parts.append(f"      particle.style.opacity = '0.8';")
                js_parts.append(f"      particle.style.transform = `translate(${{vx * duration}}px, ${{vy * duration}}px) scale(0)`;")
                js_parts.append(f"")
                js_parts.append(f"      // Remove after animation")
                js_parts.append(f"      setTimeout(() => {{")
                js_parts.append(f"        particle.remove();")
                js_parts.append(f"      }}, duration * 1000);")
                js_parts.append(f"    }}, delay * 1000);")
                js_parts.append(f"  }}")
                js_parts.append(f"")
                js_parts.append(f"  // Remove container after ritual")
                js_parts.append(f"  setTimeout(() => {{")
                js_parts.append(f"    particleContainer.remove();")
                js_parts.append(f"  }}, {template.duration} * 1000);")
                js_parts.append(f"}})();")
                
        # Add sound effect
        if template.sound:
            sound_file = self._get_sound_file(template.sound)
            if sound_file:
                js_parts.append(f"// Sound effect for ritual {ritual_id}")
                js_parts.append(f"(function() {{")
                js_parts.append(f"  const audio = new Audio('{sound_file}');")
                js_parts.append(f"  audio.volume = {self._get_intensity_factor(template.intensity)};")
                js_parts.append(f"  audio.play();")
                js_parts.append(f"}})();")
                
        # Add haptic feedback
        if template.haptic:
            js_parts.append(f"// Haptic feedback for ritual {ritual_id}")
            js_parts.append(f"(function() {{")
            js_parts.append(f"  if ('vibrate' in navigator) {{")
            
            pattern = self._get_haptic_pattern(template.haptic)
            if pattern:
                js_parts.append(f"    navigator.vibrate({pattern});")
                
            js_parts.append(f"  }}")
            js_parts.append(f"}})();")
            
        return "\n".join(js_parts)
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for ritual events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a listener for ritual events.
        
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
                
    def _get_intensity_factor(self, intensity: RitualIntensity) -> float:
        """
        Get a numeric factor based on intensity level.
        
        Args:
            intensity: Intensity level
            
        Returns:
            Numeric factor (0.0 to 1.0)
        """
        if intensity == RitualIntensity.SUBTLE:
            return 0.3
        elif intensity == RitualIntensity.MODERATE:
            return 0.6
        elif intensity == RitualIntensity.PRONOUNCED:
            return 0.8
        elif intensity == RitualIntensity.DRAMATIC:
            return 1.0
        else:
            return 0.6  # Default to moderate
            
    def _get_sound_file(self, sound: RitualSound) -> Optional[str]:
        """
        Get the sound file path for a sound effect.
        
        Args:
            sound: Sound effect
            
        Returns:
            Path to the sound file, or None if not found
        """
        sound_files = {
            RitualSound.CHIME: "/assets/sounds/chime.mp3",
            RitualSound.WHOOSH: "/assets/sounds/whoosh.mp3",
            RitualSound.CLICK: "/assets/sounds/click.mp3",
            RitualSound.BELL: "/assets/sounds/bell.mp3",
            RitualSound.HUM: "/assets/sounds/hum.mp3",
            RitualSound.TONE: "/assets/sounds/tone.mp3"
        }
        
        return sound_files.get(sound)
        
    def _get_haptic_pattern(self, haptic: RitualHaptic) -> Optional[str]:
        """
        Get the vibration pattern for haptic feedback.
        
        Args:
            haptic: Haptic feedback pattern
            
        Returns:
            Vibration pattern as a string, or None if not found
        """
        haptic_patterns = {
            RitualHaptic.PULSE: "[100]",
            RitualHaptic.DOUBLE_PULSE: "[100, 30, 100]",
            RitualHaptic.TRIPLE_PULSE: "[100, 30, 100, 30, 100]",
            RitualHaptic.LONG_PULSE: "[200]",
            RitualHaptic.RAMP_UP: "[50, 20, 100, 20, 150]",
            RitualHaptic.RAMP_DOWN: "[150, 20, 100, 20, 50]"
        }
        
        return haptic_patterns.get(haptic)
"""
