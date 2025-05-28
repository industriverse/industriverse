"""
Capsule Morphology Engine for Capsule Framework

This module manages the visual morphology and transformation of Agent Capsules
within the Industriverse UI/UX Layer. It implements the dynamic shape-shifting
capabilities of capsules based on agent role, confidence, trust level, and context.

The Capsule Morphology Engine:
1. Defines base morphologies for different capsule types
2. Manages transitions between morphology states
3. Adapts capsule shapes based on agent state and context
4. Provides an API for dynamic morphology transformations
5. Coordinates with the Rendering Engine for visual representation

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

class MorphologyType(Enum):
    """Enumeration of base morphology types for Agent Capsules."""
    STANDARD = "standard"         # Default capsule shape
    ROUTER = "router"             # Branch-like with dynamic tendrils
    ESCALATOR = "escalator"       # Towering with gradient risk heatmap
    PREDICTIVE = "predictive"     # Crystal-like with depth pulses
    HUMAN_IN_LOOP = "human_in_loop"  # Semi-transparent with face reveal
    MONITOR = "monitor"           # Eye-like with scanning motion
    CONTROLLER = "controller"     # Gear-like with rotation
    ANALYZER = "analyzer"         # Grid-like with data visualization
    EXECUTOR = "executor"         # Arrow-like with direction
    COORDINATOR = "coordinator"   # Hub-like with connections
    CUSTOM = "custom"             # Custom morphology

class MorphologyState(Enum):
    """Enumeration of morphology states for Agent Capsules."""
    DORMANT = "dormant"           # Inactive, minimal state
    ACTIVE = "active"             # Normal active state
    FOCUSED = "focused"           # Emphasized, attention-grabbing state
    EXPANDED = "expanded"         # Fully expanded state with details
    MINIMIZED = "minimized"       # Reduced, compact state
    ALERT = "alert"               # Warning or error state
    PROCESSING = "processing"     # Busy or working state
    SUCCESS = "success"           # Completed successfully state
    ERROR = "error"               # Error or failure state

class CapsuleMorphologyEngine:
    """
    Manages the visual morphology and transformation of Agent Capsules.
    
    This class is responsible for defining and managing the dynamic shape-shifting
    capabilities of capsules based on agent role, confidence, trust level, and
    context within the Industriverse UI/UX Layer.
    """
    
    def __init__(
        self, 
        rendering_engine: RenderingEngine,
        context_engine: ContextEngine,
        device_adapter: DeviceAdapter
    ):
        """
        Initialize the Capsule Morphology Engine.
        
        Args:
            rendering_engine: The Rendering Engine instance for visual representation
            context_engine: The Context Engine instance for context awareness
            device_adapter: The Device Adapter instance for device-specific adaptations
        """
        self.rendering_engine = rendering_engine
        self.context_engine = context_engine
        self.device_adapter = device_adapter
        
        # Base morphology definitions
        self.morphology_definitions = self._load_morphology_definitions()
        
        # State-specific morphology modifications
        self.state_modifications = self._load_state_modifications()
        
        # Currently active morphologies for each capsule
        self.active_morphologies = {}
        
        # Morphology history for each capsule
        self.morphology_history = {}
        
        # Capsule-specific morphology overrides
        self.capsule_morphology_overrides = {}
        
        # Morphology transition timings
        self.transition_duration = 300  # ms
        
        logger.info("Capsule Morphology Engine initialized")
    
    def _load_morphology_definitions(self) -> Dict:
        """
        Load base morphology definitions.
        
        Returns:
            Dictionary of morphology definitions
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard morphologies inline
        
        return {
            MorphologyType.STANDARD.value: {
                "shape": "capsule",
                "aspect_ratio": 2.5,
                "corner_radius": 20,
                "base_color": "#4A90E2",
                "gradient": True,
                "gradient_direction": "to bottom right",
                "gradient_colors": ["#4A90E2", "#3498DB"],
                "border_width": 1,
                "border_color": "rgba(255, 255, 255, 0.2)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.2)",
                "shadow_blur": 10,
                "shadow_offset_x": 0,
                "shadow_offset_y": 2,
                "glow": False,
                "glow_color": "rgba(74, 144, 226, 0.5)",
                "glow_blur": 15,
                "animation": None,
                "animation_duration": 0,
                "animation_easing": "ease-in-out",
                "animation_repeat": False,
                "texture": None,
                "texture_opacity": 0.1,
                "inner_elements": []
            },
            MorphologyType.ROUTER.value: {
                "shape": "router",
                "aspect_ratio": 1.8,
                "corner_radius": 5,
                "base_color": "#3498DB",
                "gradient": True,
                "gradient_direction": "to bottom right",
                "gradient_colors": ["#3498DB", "#2980B9"],
                "border_width": 1,
                "border_color": "rgba(255, 255, 255, 0.2)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.2)",
                "shadow_blur": 10,
                "shadow_offset_x": 0,
                "shadow_offset_y": 2,
                "glow": False,
                "glow_color": "rgba(52, 152, 219, 0.5)",
                "glow_blur": 15,
                "animation": "tendril_wave",
                "animation_duration": 3000,
                "animation_easing": "ease-in-out",
                "animation_repeat": True,
                "texture": "network",
                "texture_opacity": 0.1,
                "inner_elements": [
                    {
                        "type": "tendril",
                        "count": 5,
                        "length_range": [10, 30],
                        "width_range": [1, 3],
                        "color": "rgba(255, 255, 255, 0.7)",
                        "animated": True
                    }
                ]
            },
            MorphologyType.ESCALATOR.value: {
                "shape": "tower",
                "aspect_ratio": 0.6,
                "corner_radius": 5,
                "base_color": "#E74C3C",
                "gradient": True,
                "gradient_direction": "to top",
                "gradient_colors": ["#E74C3C", "#C0392B"],
                "border_width": 1,
                "border_color": "rgba(255, 255, 255, 0.2)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.3)",
                "shadow_blur": 15,
                "shadow_offset_x": 0,
                "shadow_offset_y": 5,
                "glow": False,
                "glow_color": "rgba(231, 76, 60, 0.5)",
                "glow_blur": 15,
                "animation": "pulse",
                "animation_duration": 2000,
                "animation_easing": "ease-in-out",
                "animation_repeat": True,
                "texture": "gradient_bars",
                "texture_opacity": 0.2,
                "inner_elements": [
                    {
                        "type": "risk_heatmap",
                        "height": "80%",
                        "width": "60%",
                        "colors": ["#27AE60", "#F1C40F", "#E74C3C"],
                        "animated": True
                    }
                ]
            },
            MorphologyType.PREDICTIVE.value: {
                "shape": "crystal",
                "aspect_ratio": 1.2,
                "corner_radius": 0,
                "base_color": "#9B59B6",
                "gradient": True,
                "gradient_direction": "to bottom right",
                "gradient_colors": ["#9B59B6", "#8E44AD"],
                "border_width": 1,
                "border_color": "rgba(255, 255, 255, 0.3)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.2)",
                "shadow_blur": 10,
                "shadow_offset_x": 0,
                "shadow_offset_y": 2,
                "glow": True,
                "glow_color": "rgba(155, 89, 182, 0.5)",
                "glow_blur": 15,
                "animation": "depth_pulse",
                "animation_duration": 4000,
                "animation_easing": "ease-in-out",
                "animation_repeat": True,
                "texture": "crystal_facets",
                "texture_opacity": 0.2,
                "inner_elements": [
                    {
                        "type": "depth_layers",
                        "count": 3,
                        "opacity_range": [0.3, 0.7],
                        "scale_range": [0.5, 0.9],
                        "color": "rgba(255, 255, 255, 0.5)",
                        "animated": True
                    }
                ]
            },
            MorphologyType.HUMAN_IN_LOOP.value: {
                "shape": "rounded_rect",
                "aspect_ratio": 1.5,
                "corner_radius": 15,
                "base_color": "#2ECC71",
                "gradient": True,
                "gradient_direction": "to bottom right",
                "gradient_colors": ["#2ECC71", "#27AE60"],
                "border_width": 1,
                "border_color": "rgba(255, 255, 255, 0.3)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.2)",
                "shadow_blur": 10,
                "shadow_offset_x": 0,
                "shadow_offset_y": 2,
                "glow": False,
                "glow_color": "rgba(46, 204, 113, 0.5)",
                "glow_blur": 15,
                "animation": "breathe",
                "animation_duration": 3000,
                "animation_easing": "ease-in-out",
                "animation_repeat": True,
                "texture": "subtle_dots",
                "texture_opacity": 0.1,
                "inner_elements": [
                    {
                        "type": "avatar_silhouette",
                        "opacity": 0.7,
                        "scale": 0.6,
                        "color": "rgba(255, 255, 255, 0.9)",
                        "animated": True
                    },
                    {
                        "type": "context_bubbles",
                        "count": 3,
                        "size_range": [5, 15],
                        "color": "rgba(255, 255, 255, 0.7)",
                        "animated": True
                    }
                ]
            },
            MorphologyType.MONITOR.value: {
                "shape": "circle",
                "aspect_ratio": 1.0,
                "corner_radius": 0,
                "base_color": "#F39C12",
                "gradient": True,
                "gradient_direction": "radial",
                "gradient_colors": ["#F39C12", "#D35400"],
                "border_width": 2,
                "border_color": "rgba(255, 255, 255, 0.3)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.2)",
                "shadow_blur": 10,
                "shadow_offset_x": 0,
                "shadow_offset_y": 2,
                "glow": True,
                "glow_color": "rgba(243, 156, 18, 0.5)",
                "glow_blur": 15,
                "animation": "scan",
                "animation_duration": 3000,
                "animation_easing": "ease-in-out",
                "animation_repeat": True,
                "texture": "concentric_circles",
                "texture_opacity": 0.2,
                "inner_elements": [
                    {
                        "type": "iris",
                        "scale": 0.6,
                        "color": "rgba(255, 255, 255, 0.9)",
                        "animated": True
                    },
                    {
                        "type": "scan_line",
                        "width": "80%",
                        "height": 2,
                        "color": "rgba(255, 255, 255, 0.7)",
                        "animated": True
                    }
                ]
            },
            MorphologyType.CONTROLLER.value: {
                "shape": "gear",
                "aspect_ratio": 1.0,
                "corner_radius": 0,
                "base_color": "#34495E",
                "gradient": True,
                "gradient_direction": "radial",
                "gradient_colors": ["#34495E", "#2C3E50"],
                "border_width": 1,
                "border_color": "rgba(255, 255, 255, 0.2)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.3)",
                "shadow_blur": 10,
                "shadow_offset_x": 0,
                "shadow_offset_y": 2,
                "glow": False,
                "glow_color": "rgba(52, 73, 94, 0.5)",
                "glow_blur": 15,
                "animation": "rotate",
                "animation_duration": 10000,
                "animation_easing": "linear",
                "animation_repeat": True,
                "texture": "gear_teeth",
                "texture_opacity": 0.3,
                "inner_elements": [
                    {
                        "type": "inner_gear",
                        "scale": 0.6,
                        "color": "rgba(255, 255, 255, 0.2)",
                        "animated": True,
                        "animation": "rotate_reverse"
                    }
                ]
            },
            MorphologyType.ANALYZER.value: {
                "shape": "rounded_rect",
                "aspect_ratio": 1.2,
                "corner_radius": 10,
                "base_color": "#1ABC9C",
                "gradient": True,
                "gradient_direction": "to bottom right",
                "gradient_colors": ["#1ABC9C", "#16A085"],
                "border_width": 1,
                "border_color": "rgba(255, 255, 255, 0.2)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.2)",
                "shadow_blur": 10,
                "shadow_offset_x": 0,
                "shadow_offset_y": 2,
                "glow": False,
                "glow_color": "rgba(26, 188, 156, 0.5)",
                "glow_blur": 15,
                "animation": "data_flow",
                "animation_duration": 5000,
                "animation_easing": "linear",
                "animation_repeat": True,
                "texture": "grid",
                "texture_opacity": 0.2,
                "inner_elements": [
                    {
                        "type": "data_points",
                        "count": 10,
                        "size_range": [2, 5],
                        "color": "rgba(255, 255, 255, 0.7)",
                        "animated": True
                    },
                    {
                        "type": "graph_lines",
                        "count": 3,
                        "width": 1,
                        "color": "rgba(255, 255, 255, 0.5)",
                        "animated": True
                    }
                ]
            },
            MorphologyType.EXECUTOR.value: {
                "shape": "arrow",
                "aspect_ratio": 1.8,
                "corner_radius": 5,
                "base_color": "#E67E22",
                "gradient": True,
                "gradient_direction": "to right",
                "gradient_colors": ["#E67E22", "#D35400"],
                "border_width": 1,
                "border_color": "rgba(255, 255, 255, 0.2)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.2)",
                "shadow_blur": 10,
                "shadow_offset_x": 0,
                "shadow_offset_y": 2,
                "glow": False,
                "glow_color": "rgba(230, 126, 34, 0.5)",
                "glow_blur": 15,
                "animation": "pulse_forward",
                "animation_duration": 2000,
                "animation_easing": "ease-in-out",
                "animation_repeat": True,
                "texture": "direction_lines",
                "texture_opacity": 0.2,
                "inner_elements": [
                    {
                        "type": "progress_bar",
                        "width": "70%",
                        "height": "20%",
                        "color": "rgba(255, 255, 255, 0.7)",
                        "animated": True
                    }
                ]
            },
            MorphologyType.COORDINATOR.value: {
                "shape": "hexagon",
                "aspect_ratio": 1.0,
                "corner_radius": 0,
                "base_color": "#8E44AD",
                "gradient": True,
                "gradient_direction": "to bottom right",
                "gradient_colors": ["#8E44AD", "#9B59B6"],
                "border_width": 1,
                "border_color": "rgba(255, 255, 255, 0.2)",
                "shadow": True,
                "shadow_color": "rgba(0, 0, 0, 0.2)",
                "shadow_blur": 10,
                "shadow_offset_x": 0,
                "shadow_offset_y": 2,
                "glow": True,
                "glow_color": "rgba(142, 68, 173, 0.5)",
                "glow_blur": 15,
                "animation": "connection_pulse",
                "animation_duration": 4000,
                "animation_easing": "ease-in-out",
                "animation_repeat": True,
                "texture": "honeycomb",
                "texture_opacity": 0.1,
                "inner_elements": [
                    {
                        "type": "connection_points",
                        "count": 6,
                        "size": 4,
                        "color": "rgba(255, 255, 255, 0.7)",
                        "animated": True
                    },
                    {
                        "type": "connection_lines",
                        "count": 3,
                        "width": 1,
                        "color": "rgba(255, 255, 255, 0.4)",
                        "animated": True
                    }
                ]
            }
        }
    
    def _load_state_modifications(self) -> Dict:
        """
        Load state-specific morphology modifications.
        
        Returns:
            Dictionary of state modifications
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard state modifications inline
        
        return {
            MorphologyState.DORMANT.value: {
                "scale": 0.8,
                "opacity": 0.5,
                "shadow_blur": 5,
                "glow": False,
                "animation": None,
                "border_width": 1,
                "inner_elements_opacity": 0.3,
                "color_adjustment": {
                    "saturation": -30,
                    "brightness": -20
                }
            },
            MorphologyState.ACTIVE.value: {
                "scale": 1.0,
                "opacity": 1.0,
                "shadow_blur": 10,
                "glow": False,
                "animation": "default",
                "border_width": 1,
                "inner_elements_opacity": 1.0,
                "color_adjustment": {
                    "saturation": 0,
                    "brightness": 0
                }
            },
            MorphologyState.FOCUSED.value: {
                "scale": 1.1,
                "opacity": 1.0,
                "shadow_blur": 15,
                "glow": True,
                "animation": "default",
                "border_width": 2,
                "inner_elements_opacity": 1.0,
                "color_adjustment": {
                    "saturation": 10,
                    "brightness": 10
                }
            },
            MorphologyState.EXPANDED.value: {
                "scale": 1.3,
                "opacity": 1.0,
                "shadow_blur": 20,
                "glow": True,
                "animation": "default",
                "border_width": 2,
                "inner_elements_opacity": 1.0,
                "color_adjustment": {
                    "saturation": 10,
                    "brightness": 10
                }
            },
            MorphologyState.MINIMIZED.value: {
                "scale": 0.6,
                "opacity": 0.8,
                "shadow_blur": 5,
                "glow": False,
                "animation": None,
                "border_width": 1,
                "inner_elements_opacity": 0.5,
                "color_adjustment": {
                    "saturation": -10,
                    "brightness": -10
                }
            },
            MorphologyState.ALERT.value: {
                "scale": 1.1,
                "opacity": 1.0,
                "shadow_blur": 15,
                "glow": True,
                "glow_color": "rgba(231, 76, 60, 0.5)",
                "animation": "pulse",
                "animation_duration": 1000,
                "border_width": 2,
                "border_color": "rgba(231, 76, 60, 0.7)",
                "inner_elements_opacity": 1.0,
                "color_adjustment": {
                    "saturation": 20,
                    "brightness": 10,
                    "hue_shift": "red"
                }
            },
            MorphologyState.PROCESSING.value: {
                "scale": 1.0,
                "opacity": 1.0,
                "shadow_blur": 10,
                "glow": True,
                "glow_color": "rgba(52, 152, 219, 0.5)",
                "animation": "processing",
                "animation_duration": 2000,
                "border_width": 1,
                "inner_elements_opacity": 1.0,
                "color_adjustment": {
                    "saturation": 0,
                    "brightness": 0,
                    "hue_shift": "blue"
                }
            },
            MorphologyState.SUCCESS.value: {
                "scale": 1.1,
                "opacity": 1.0,
                "shadow_blur": 15,
                "glow": True,
                "glow_color": "rgba(46, 204, 113, 0.5)",
                "animation": "success",
                "animation_duration": 1000,
                "border_width": 2,
                "border_color": "rgba(46, 204, 113, 0.7)",
                "inner_elements_opacity": 1.0,
                "color_adjustment": {
                    "saturation": 20,
                    "brightness": 10,
                    "hue_shift": "green"
                }
            },
            MorphologyState.ERROR.value: {
                "scale": 1.0,
                "opacity": 1.0,
                "shadow_blur": 15,
                "glow": True,
                "glow_color": "rgba(231, 76, 60, 0.5)",
                "animation": "error",
                "animation_duration": 1000,
                "border_width": 2,
                "border_color": "rgba(231, 76, 60, 0.7)",
                "inner_elements_opacity": 1.0,
                "color_adjustment": {
                    "saturation": 20,
                    "brightness": 0,
                    "hue_shift": "red"
                }
            }
        }
    
    def set_capsule_morphology(
        self, 
        capsule_id: str, 
        morphology_type: str, 
        state: str = MorphologyState.ACTIVE.value,
        options: Dict = None
    ) -> bool:
        """
        Set the morphology for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to set morphology for
            morphology_type: The type of morphology to set
            state: The state of the morphology
            options: Optional additional morphology options
            
        Returns:
            Boolean indicating success
        """
        # Verify morphology type exists
        if morphology_type not in self.morphology_definitions:
            logger.error(f"Morphology type {morphology_type} not found in morphology definitions")
            return False
        
        # Verify state exists
        if state not in self.state_modifications:
            logger.error(f"Morphology state {state} not found in state modifications")
            return False
        
        # Get base morphology definition
        morphology_def = self.morphology_definitions[morphology_type]
        
        # Apply state modifications
        state_mods = self.state_modifications[state]
        
        # Apply capsule-specific overrides if they exist
        if capsule_id in self.capsule_morphology_overrides:
            capsule_overrides = self.capsule_morphology_overrides[capsule_id]
            # Merge the base morphology with capsule-specific overrides
            morphology_def = {**morphology_def, **capsule_overrides}
        
        # Apply options if provided
        if options:
            # Merge options with morphology definition
            morphology_def = {**morphology_def, **options}
        
        # Create final morphology by applying state modifications
        final_morphology = self._apply_state_modifications(morphology_def, state_mods)
        
        # Store previous morphology in history
        if capsule_id in self.active_morphologies:
            if capsule_id not in self.morphology_history:
                self.morphology_history[capsule_id] = []
            
            # Limit history length
            if len(self.morphology_history[capsule_id]) > 20:
                self.morphology_history[capsule_id].pop(0)
            
            self.morphology_history[capsule_id].append(self.active_morphologies[capsule_id])
        
        # Set active morphology
        self.active_morphologies[capsule_id] = {
            "type": morphology_type,
            "state": state,
            "properties": final_morphology,
            "timestamp": time.time()
        }
        
        # Apply the morphology through the rendering engine
        self._apply_morphology_to_renderer(capsule_id, final_morphology)
        
        logger.info(f"Set morphology {morphology_type} ({state}) for capsule {capsule_id}")
        return True
    
    def _apply_state_modifications(self, morphology_def: Dict, state_mods: Dict) -> Dict:
        """
        Apply state modifications to a morphology definition.
        
        Args:
            morphology_def: The base morphology definition
            state_mods: The state modifications to apply
            
        Returns:
            Modified morphology definition
        """
        # Create a copy of the morphology definition
        final_morphology = morphology_def.copy()
        
        # Apply scale modification
        if "scale" in state_mods:
            final_morphology["scale"] = state_mods["scale"]
        
        # Apply opacity modification
        if "opacity" in state_mods:
            final_morphology["opacity"] = state_mods["opacity"]
        
        # Apply shadow modifications
        if "shadow_blur" in state_mods:
            final_morphology["shadow_blur"] = state_mods["shadow_blur"]
        
        # Apply glow modifications
        if "glow" in state_mods:
            final_morphology["glow"] = state_mods["glow"]
        
        if "glow_color" in state_mods:
            final_morphology["glow_color"] = state_mods["glow_color"]
        
        # Apply animation modifications
        if "animation" in state_mods:
            if state_mods["animation"] == "default":
                # Keep the default animation from morphology definition
                pass
            elif state_mods["animation"] is None:
                # Remove animation
                final_morphology["animation"] = None
            else:
                # Set to specified animation
                final_morphology["animation"] = state_mods["animation"]
        
        if "animation_duration" in state_mods:
            final_morphology["animation_duration"] = state_mods["animation_duration"]
        
        # Apply border modifications
        if "border_width" in state_mods:
            final_morphology["border_width"] = state_mods["border_width"]
        
        if "border_color" in state_mods:
            final_morphology["border_color"] = state_mods["border_color"]
        
        # Apply inner elements opacity
        if "inner_elements_opacity" in state_mods:
            inner_elements_opacity = state_mods["inner_elements_opacity"]
            for element in final_morphology.get("inner_elements", []):
                element["opacity"] = element.get("opacity", 1.0) * inner_elements_opacity
        
        # Apply color adjustments
        if "color_adjustment" in state_mods:
            color_adj = state_mods["color_adjustment"]
            
            # Apply saturation adjustment
            if "saturation" in color_adj:
                # In a real implementation, this would adjust the saturation of colors
                # For now, we'll just log the intent
                logger.debug(f"Adjusting saturation by {color_adj['saturation']}")
            
            # Apply brightness adjustment
            if "brightness" in color_adj:
                # In a real implementation, this would adjust the brightness of colors
                # For now, we'll just log the intent
                logger.debug(f"Adjusting brightness by {color_adj['brightness']}")
            
            # Apply hue shift
            if "hue_shift" in color_adj:
                hue_shift = color_adj["hue_shift"]
                if hue_shift == "red":
                    final_morphology["base_color"] = "#E74C3C"
                    if "gradient_colors" in final_morphology:
                        final_morphology["gradient_colors"] = ["#E74C3C", "#C0392B"]
                elif hue_shift == "green":
                    final_morphology["base_color"] = "#2ECC71"
                    if "gradient_colors" in final_morphology:
                        final_morphology["gradient_colors"] = ["#2ECC71", "#27AE60"]
                elif hue_shift == "blue":
                    final_morphology["base_color"] = "#3498DB"
                    if "gradient_colors" in final_morphology:
                        final_morphology["gradient_colors"] = ["#3498DB", "#2980B9"]
        
        return final_morphology
    
    def _apply_morphology_to_renderer(self, capsule_id: str, morphology_properties: Dict) -> None:
        """
        Apply morphology properties to the rendering engine.
        
        Args:
            capsule_id: The ID of the capsule to apply morphology to
            morphology_properties: The morphology properties to apply
        """
        # Prepare rendering properties
        render_props = {
            "shape": morphology_properties.get("shape", "capsule"),
            "aspect_ratio": morphology_properties.get("aspect_ratio", 1.0),
            "corner_radius": morphology_properties.get("corner_radius", 0),
            "color": morphology_properties.get("base_color", "#4A90E2"),
            "opacity": morphology_properties.get("opacity", 1.0),
            "scale": morphology_properties.get("scale", 1.0),
            "border": {
                "width": morphology_properties.get("border_width", 0),
                "color": morphology_properties.get("border_color", "transparent")
            },
            "shadow": {
                "enabled": morphology_properties.get("shadow", False),
                "color": morphology_properties.get("shadow_color", "rgba(0, 0, 0, 0.2)"),
                "blur": morphology_properties.get("shadow_blur", 10),
                "offset_x": morphology_properties.get("shadow_offset_x", 0),
                "offset_y": morphology_properties.get("shadow_offset_y", 2)
            },
            "glow": {
                "enabled": morphology_properties.get("glow", False),
                "color": morphology_properties.get("glow_color", "rgba(74, 144, 226, 0.5)"),
                "blur": morphology_properties.get("glow_blur", 15)
            },
            "gradient": {
                "enabled": morphology_properties.get("gradient", False),
                "direction": morphology_properties.get("gradient_direction", "to bottom"),
                "colors": morphology_properties.get("gradient_colors", [])
            },
            "texture": {
                "type": morphology_properties.get("texture"),
                "opacity": morphology_properties.get("texture_opacity", 0.1)
            },
            "inner_elements": morphology_properties.get("inner_elements", [])
        }
        
        # Add animation if defined
        if morphology_properties.get("animation"):
            render_props["animation"] = {
                "type": morphology_properties["animation"],
                "duration": morphology_properties.get("animation_duration", 1000),
                "easing": morphology_properties.get("animation_easing", "ease-in-out"),
                "repeat": morphology_properties.get("animation_repeat", False)
            }
        
        # Apply to rendering engine
        self.rendering_engine.update_capsule_visual(capsule_id, render_props)
    
    def get_capsule_morphology(self, capsule_id: str) -> Dict:
        """
        Get the current morphology for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to get morphology for
            
        Returns:
            Dictionary containing current morphology information
        """
        return self.active_morphologies.get(capsule_id, {})
    
    def get_capsule_morphology_history(self, capsule_id: str, limit: int = 10) -> List[Dict]:
        """
        Get morphology history for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to get history for
            limit: Maximum number of history items to return
            
        Returns:
            List of dictionaries containing historical morphology information
        """
        history = self.morphology_history.get(capsule_id, [])
        return history[-limit:]
    
    def register_capsule_morphology_override(
        self, 
        capsule_id: str, 
        override_properties: Dict
    ) -> bool:
        """
        Register capsule-specific morphology overrides.
        
        Args:
            capsule_id: The ID of the capsule to register overrides for
            override_properties: The properties to override
            
        Returns:
            Boolean indicating success
        """
        # Register override
        self.capsule_morphology_overrides[capsule_id] = override_properties
        
        logger.info(f"Registered morphology override for capsule {capsule_id}")
        return True
    
    def set_transition_duration(self, duration_ms: int) -> None:
        """
        Set the duration for morphology transitions.
        
        Args:
            duration_ms: Transition duration in milliseconds
        """
        self.transition_duration = duration_ms
        self.rendering_engine.set_transition_duration(duration_ms)
        
        logger.info(f"Set morphology transition duration to {duration_ms}ms")
    
    def set_morphology_from_agent_state(
        self, 
        capsule_id: str, 
        agent_state: Dict
    ) -> bool:
        """
        Set capsule morphology based on agent state data.
        
        Args:
            capsule_id: The ID of the capsule to set morphology for
            agent_state: Dictionary containing agent state information
            
        Returns:
            Boolean indicating success
        """
        # Map agent type to morphology type
        morphology_type = MorphologyType.STANDARD.value
        agent_type = agent_state.get("type", "unknown")
        
        if agent_type == "router":
            morphology_type = MorphologyType.ROUTER.value
        elif agent_type == "escalator":
            morphology_type = MorphologyType.ESCALATOR.value
        elif agent_type == "predictor":
            morphology_type = MorphologyType.PREDICTIVE.value
        elif agent_type == "human_in_loop":
            morphology_type = MorphologyType.HUMAN_IN_LOOP.value
        elif agent_type == "monitor":
            morphology_type = MorphologyType.MONITOR.value
        elif agent_type == "controller":
            morphology_type = MorphologyType.CONTROLLER.value
        elif agent_type == "analyzer":
            morphology_type = MorphologyType.ANALYZER.value
        elif agent_type == "executor":
            morphology_type = MorphologyType.EXECUTOR.value
        elif agent_type == "coordinator":
            morphology_type = MorphologyType.COORDINATOR.value
        
        # Map agent state to morphology state
        morphology_state = MorphologyState.ACTIVE.value
        
        if "status" in agent_state:
            status = agent_state["status"]
            
            if status == "dormant":
                morphology_state = MorphologyState.DORMANT.value
            elif status == "active":
                morphology_state = MorphologyState.ACTIVE.value
            elif status == "processing":
                morphology_state = MorphologyState.PROCESSING.value
            elif status == "error":
                morphology_state = MorphologyState.ERROR.value
            elif status == "success":
                morphology_state = MorphologyState.SUCCESS.value
        
        if "focus" in agent_state:
            focus = agent_state["focus"]
            
            if focus == "focused":
                morphology_state = MorphologyState.FOCUSED.value
            elif focus == "expanded":
                morphology_state = MorphologyState.EXPANDED.value
            elif focus == "minimized":
                morphology_state = MorphologyState.MINIMIZED.value
        
        if "alert_level" in agent_state:
            alert_level = agent_state["alert_level"]
            
            if alert_level == "warning" or alert_level == "critical":
                morphology_state = MorphologyState.ALERT.value
        
        # Set the morphology
        return self.set_capsule_morphology(
            capsule_id, 
            morphology_type, 
            morphology_state
        )
    
    def morph_capsule(
        self, 
        capsule_id: str, 
        target_state: str,
        duration_ms: int = None
    ) -> bool:
        """
        Morph a capsule to a new state.
        
        Args:
            capsule_id: The ID of the capsule to morph
            target_state: The target state to morph to
            duration_ms: Optional custom transition duration
            
        Returns:
            Boolean indicating success
        """
        # Get current morphology
        current_morphology = self.get_capsule_morphology(capsule_id)
        if not current_morphology:
            logger.error(f"No active morphology found for capsule {capsule_id}")
            return False
        
        # Set custom transition duration if provided
        if duration_ms:
            self.rendering_engine.set_transition_duration(duration_ms)
        
        # Set morphology with new state but same type
        result = self.set_capsule_morphology(
            capsule_id,
            current_morphology.get("type", MorphologyType.STANDARD.value),
            target_state
        )
        
        # Reset transition duration if custom was provided
        if duration_ms:
            self.rendering_engine.set_transition_duration(self.transition_duration)
        
        return result
    
    def adapt_to_context_change(self, context_update: Dict) -> None:
        """
        Adapt capsule morphologies based on a context change.
        
        Args:
            context_update: Dictionary containing context update information
        """
        # Check for context-triggered morphology adaptations
        context_priority = context_update.get("priority")
        
        if context_priority == "critical":
            # For critical contexts, morph all active capsules to alert state
            for capsule_id in self.active_morphologies:
                self.morph_capsule(capsule_id, MorphologyState.ALERT.value)
        
        # Adapt morphology based on context
        ambient_mode = context_update.get("ambient_mode")
        if ambient_mode == "focus":
            # In focus mode, minimize non-essential capsules
            for capsule_id in self.active_morphologies:
                # In a real implementation, we would check if the capsule is non-essential
                # For now, we'll just log the intent
                logger.debug(f"Would minimize non-essential capsule {capsule_id} in focus mode")
        elif ambient_mode == "ambient":
            # In ambient mode, restore normal states
            for capsule_id in self.active_morphologies:
                current_morphology = self.get_capsule_morphology(capsule_id)
                if current_morphology.get("state") == MorphologyState.MINIMIZED.value:
                    self.morph_capsule(capsule_id, MorphologyState.ACTIVE.value)
        
        logger.info(f"Capsule morphologies adapted to context change: {context_update.get('type', 'unknown')}")
"""
