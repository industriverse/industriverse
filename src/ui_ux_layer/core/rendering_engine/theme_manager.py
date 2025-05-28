"""
Theme Manager for the Rendering Engine

This module manages the theming system for the Industriverse UI/UX Layer.
It handles theme definition, switching, customization, and application
across different components and contexts.

The Theme Manager:
1. Manages theme definitions (colors, typography, spacing, etc.)
2. Handles theme switching and persistence
3. Supports dynamic theme adaptation based on context
4. Provides theme customization capabilities
5. Implements industry-specific theme variations
6. Ensures consistent theme application across components

Author: Manus
"""

import logging
import json
import os
import time
from typing import Dict, List, Optional, Any
from enum import Enum
import colorsys

# Local imports
from ..context_engine.context_awareness_engine import ContextAwarenessEngine

# Configure logging
logger = logging.getLogger(__name__)

class ThemeMode(Enum):
    """Enumeration of theme modes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    HIGH_CONTRAST = "high_contrast"

class ThemeManager:
    """
    Manages the theming system for the Industriverse UI/UX Layer.
    
    This class is responsible for theme definition, switching, customization,
    and application across different components and contexts.
    """
    
    def __init__(
        self,
        context_engine: ContextAwarenessEngine,
        config: Dict = None
    ):
        """
        Initialize the Theme Manager.
        
        Args:
            context_engine: The Context Awareness Engine instance
            config: Optional configuration dictionary
        """
        self.context_engine = context_engine
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "themes_directory": os.path.join(os.path.dirname(__file__), "themes"),
            "default_theme": "industriverse",
            "default_mode": ThemeMode.LIGHT.value,
            "enable_auto_mode": True,
            "auto_mode_light_hours": (6, 18),  # 6 AM to 6 PM
            "enable_context_adaptation": True,
            "enable_user_customization": True,
            "theme_persistence_file": "user_theme_preferences.json",
            "color_adaptation_strength": 0.3,  # 0.0 to 1.0
            "animation_enabled": True,
            "transition_duration": 300,  # milliseconds
            "cache_themes": True,
            "cache_expiry": 3600,  # seconds
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Ensure themes directory exists
        os.makedirs(self.config["themes_directory"], exist_ok=True)
        
        # Current theme and mode
        self.current_theme_name = self.config["default_theme"]
        self.current_mode = self.config["default_mode"]
        
        # Theme cache
        self.theme_cache = {}
        self.theme_cache_timestamps = {}
        
        # User customizations
        self.user_customizations = {}
        
        # Industry-specific theme adaptations
        self.industry_adaptations = {}
        
        # Load built-in themes
        self._load_built_in_themes()
        
        # Load user preferences if available
        self._load_user_preferences()
        
        # Register as context listener
        self.context_engine.register_context_listener(self._handle_context_change)
        
        logger.info(f"Theme Manager initialized with theme '{self.current_theme_name}' in mode '{self.current_mode}'")
    
    def _merge_config(self) -> None:
        """Merge provided configuration with defaults."""
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                # Merge nested dictionaries
                for nested_key, nested_value in value.items():
                    if nested_key not in self.config[key]:
                        self.config[key][nested_key] = nested_value
    
    def _load_built_in_themes(self) -> None:
        """Load built-in themes."""
        # Define the base Industriverse theme
        self._create_industriverse_base_theme()
        
        # Define industry-specific theme adaptations
        self._create_industry_adaptations()
    
    def _create_industriverse_base_theme(self) -> None:
        """Create the base Industriverse theme."""
        # Base colors
        primary_color = "#0056B3"  # Deep blue
        secondary_color = "#6C757D"  # Gray
        accent_color = "#00C6FF"  # Bright blue
        success_color = "#28A745"  # Green
        warning_color = "#FFC107"  # Yellow
        danger_color = "#DC3545"  # Red
        info_color = "#17A2B8"  # Teal
        
        # Light mode
        light_theme = {
            "name": "industriverse",
            "mode": ThemeMode.LIGHT.value,
            "colors": {
                "primary": primary_color,
                "secondary": secondary_color,
                "accent": accent_color,
                "success": success_color,
                "warning": warning_color,
                "danger": danger_color,
                "info": info_color,
                "background": {
                    "primary": "#FFFFFF",
                    "secondary": "#F8F9FA",
                    "tertiary": "#E9ECEF"
                },
                "surface": {
                    "primary": "#FFFFFF",
                    "secondary": "#F8F9FA",
                    "tertiary": "#E9ECEF"
                },
                "text": {
                    "primary": "#212529",
                    "secondary": "#6C757D",
                    "tertiary": "#ADB5BD",
                    "on_primary": "#FFFFFF",
                    "on_secondary": "#FFFFFF",
                    "on_accent": "#FFFFFF",
                    "on_success": "#FFFFFF",
                    "on_warning": "#212529",
                    "on_danger": "#FFFFFF",
                    "on_info": "#FFFFFF"
                },
                "border": {
                    "light": "#DEE2E6",
                    "medium": "#CED4DA",
                    "dark": "#ADB5BD"
                },
                "shadow": {
                    "light": "rgba(0, 0, 0, 0.05)",
                    "medium": "rgba(0, 0, 0, 0.1)",
                    "dark": "rgba(0, 0, 0, 0.2)"
                },
                "overlay": "rgba(0, 0, 0, 0.5)",
                "scrim": "rgba(0, 0, 0, 0.3)"
            },
            "typography": {
                "font_family": {
                    "primary": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif",
                    "secondary": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif",
                    "monospace": "'Roboto Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace"
                },
                "font_size": {
                    "xs": "0.75rem",
                    "sm": "0.875rem",
                    "md": "1rem",
                    "lg": "1.125rem",
                    "xl": "1.25rem",
                    "2xl": "1.5rem",
                    "3xl": "1.875rem",
                    "4xl": "2.25rem",
                    "5xl": "3rem",
                    "6xl": "4rem"
                },
                "font_weight": {
                    "light": 300,
                    "regular": 400,
                    "medium": 500,
                    "semibold": 600,
                    "bold": 700
                },
                "line_height": {
                    "tight": 1.25,
                    "normal": 1.5,
                    "relaxed": 1.75,
                    "loose": 2
                },
                "letter_spacing": {
                    "tighter": "-0.05em",
                    "tight": "-0.025em",
                    "normal": "0",
                    "wide": "0.025em",
                    "wider": "0.05em",
                    "widest": "0.1em"
                }
            },
            "spacing": {
                "0": "0",
                "1": "0.25rem",
                "2": "0.5rem",
                "3": "0.75rem",
                "4": "1rem",
                "5": "1.25rem",
                "6": "1.5rem",
                "8": "2rem",
                "10": "2.5rem",
                "12": "3rem",
                "16": "4rem",
                "20": "5rem",
                "24": "6rem",
                "32": "8rem",
                "40": "10rem",
                "48": "12rem",
                "56": "14rem",
                "64": "16rem"
            },
            "borders": {
                "radius": {
                    "none": "0",
                    "sm": "0.125rem",
                    "md": "0.25rem",
                    "lg": "0.5rem",
                    "xl": "0.75rem",
                    "2xl": "1rem",
                    "full": "9999px"
                },
                "width": {
                    "none": "0",
                    "thin": "1px",
                    "medium": "2px",
                    "thick": "4px"
                }
            },
            "shadows": {
                "none": "none",
                "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
                "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"
            },
            "transitions": {
                "duration": {
                    "fastest": "50ms",
                    "fast": "100ms",
                    "normal": "200ms",
                    "slow": "300ms",
                    "slowest": "500ms"
                },
                "timing": {
                    "ease": "ease",
                    "linear": "linear",
                    "ease_in": "cubic-bezier(0.4, 0, 1, 1)",
                    "ease_out": "cubic-bezier(0, 0, 0.2, 1)",
                    "ease_in_out": "cubic-bezier(0.4, 0, 0.2, 1)"
                }
            },
            "z_index": {
                "0": "0",
                "10": "10",
                "20": "20",
                "30": "30",
                "40": "40",
                "50": "50",
                "auto": "auto"
            },
            "components": {
                "capsule": {
                    "background": "linear-gradient(135deg, #0056B3, #00C6FF)",
                    "text_color": "#FFFFFF",
                    "border_radius": "0.75rem",
                    "shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                    "active_glow": "0 0 15px rgba(0, 198, 255, 0.5)"
                },
                "trust_ribbon": {
                    "background": "rgba(255, 255, 255, 0.9)",
                    "border": "1px solid #DEE2E6",
                    "shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
                },
                "mission_deck": {
                    "background": "#FFFFFF",
                    "card_background": "#F8F9FA",
                    "card_border": "1px solid #DEE2E6",
                    "card_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
                },
                "swarm_lens": {
                    "background": "rgba(248, 249, 250, 0.8)",
                    "connection_line": "#ADB5BD",
                    "active_connection": "#0056B3",
                    "node_fill": "#FFFFFF",
                    "node_stroke": "#6C757D"
                },
                "timeline_view": {
                    "background": "#F8F9FA",
                    "line_color": "#DEE2E6",
                    "event_background": "#FFFFFF",
                    "event_border": "1px solid #DEE2E6"
                },
                "ambient_veil": {
                    "background": "linear-gradient(180deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)",
                    "text_color": "#212529",
                    "glow_color": "rgba(0, 198, 255, 0.2)"
                }
            }
        }
        
        # Dark mode - derived from light mode with color inversions
        dark_theme = self._create_dark_mode_variant(light_theme)
        
        # High contrast mode - derived from light mode with enhanced contrast
        high_contrast_theme = self._create_high_contrast_variant(light_theme)
        
        # Store themes in cache
        self.theme_cache["industriverse_light"] = light_theme
        self.theme_cache["industriverse_dark"] = dark_theme
        self.theme_cache["industriverse_high_contrast"] = high_contrast_theme
        
        # Update cache timestamps
        current_time = time.time()
        self.theme_cache_timestamps["industriverse_light"] = current_time
        self.theme_cache_timestamps["industriverse_dark"] = current_time
        self.theme_cache_timestamps["industriverse_high_contrast"] = current_time
        
        # Save themes to files
        self._save_theme_to_file("industriverse_light", light_theme)
        self._save_theme_to_file("industriverse_dark", dark_theme)
        self._save_theme_to_file("industriverse_high_contrast", high_contrast_theme)
    
    def _create_dark_mode_variant(self, light_theme: Dict) -> Dict:
        """
        Create a dark mode variant of a light theme.
        
        Args:
            light_theme: Light theme definition
            
        Returns:
            Dark mode theme definition
        """
        # Create a deep copy of the light theme
        dark_theme = json.loads(json.dumps(light_theme))
        
        # Update theme metadata
        dark_theme["mode"] = ThemeMode.DARK.value
        
        # Invert background colors
        dark_theme["colors"]["background"]["primary"] = "#121212"
        dark_theme["colors"]["background"]["secondary"] = "#1E1E1E"
        dark_theme["colors"]["background"]["tertiary"] = "#2C2C2C"
        
        dark_theme["colors"]["surface"]["primary"] = "#121212"
        dark_theme["colors"]["surface"]["secondary"] = "#1E1E1E"
        dark_theme["colors"]["surface"]["tertiary"] = "#2C2C2C"
        
        # Invert text colors
        dark_theme["colors"]["text"]["primary"] = "#E0E0E0"
        dark_theme["colors"]["text"]["secondary"] = "#A0A0A0"
        dark_theme["colors"]["text"]["tertiary"] = "#707070"
        
        # Adjust border colors
        dark_theme["colors"]["border"]["light"] = "#333333"
        dark_theme["colors"]["border"]["medium"] = "#444444"
        dark_theme["colors"]["border"]["dark"] = "#555555"
        
        # Adjust shadow colors
        dark_theme["colors"]["shadow"]["light"] = "rgba(0, 0, 0, 0.2)"
        dark_theme["colors"]["shadow"]["medium"] = "rgba(0, 0, 0, 0.4)"
        dark_theme["colors"]["shadow"]["dark"] = "rgba(0, 0, 0, 0.6)"
        
        # Adjust overlay and scrim
        dark_theme["colors"]["overlay"] = "rgba(0, 0, 0, 0.7)"
        dark_theme["colors"]["scrim"] = "rgba(0, 0, 0, 0.5)"
        
        # Adjust component-specific styles
        dark_theme["components"]["capsule"]["background"] = "linear-gradient(135deg, #003366, #0099CC)"
        dark_theme["components"]["capsule"]["shadow"] = "0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)"
        
        dark_theme["components"]["trust_ribbon"]["background"] = "rgba(30, 30, 30, 0.9)"
        dark_theme["components"]["trust_ribbon"]["border"] = "1px solid #333333"
        
        dark_theme["components"]["mission_deck"]["background"] = "#121212"
        dark_theme["components"]["mission_deck"]["card_background"] = "#1E1E1E"
        dark_theme["components"]["mission_deck"]["card_border"] = "1px solid #333333"
        
        dark_theme["components"]["swarm_lens"]["background"] = "rgba(30, 30, 30, 0.8)"
        dark_theme["components"]["swarm_lens"]["node_fill"] = "#2C2C2C"
        
        dark_theme["components"]["timeline_view"]["background"] = "#1E1E1E"
        dark_theme["components"]["timeline_view"]["line_color"] = "#333333"
        dark_theme["components"]["timeline_view"]["event_background"] = "#2C2C2C"
        dark_theme["components"]["timeline_view"]["event_border"] = "1px solid #333333"
        
        dark_theme["components"]["ambient_veil"]["background"] = "linear-gradient(180deg, rgba(18,18,18,0.9) 0%, rgba(18,18,18,0.7) 100%)"
        dark_theme["components"]["ambient_veil"]["text_color"] = "#E0E0E0"
        
        return dark_theme
    
    def _create_high_contrast_variant(self, light_theme: Dict) -> Dict:
        """
        Create a high contrast variant of a light theme.
        
        Args:
            light_theme: Light theme definition
            
        Returns:
            High contrast theme definition
        """
        # Create a deep copy of the light theme
        high_contrast_theme = json.loads(json.dumps(light_theme))
        
        # Update theme metadata
        high_contrast_theme["mode"] = ThemeMode.HIGH_CONTRAST.value
        
        # Set high contrast colors
        high_contrast_theme["colors"]["primary"] = "#0000FF"  # Pure blue
        high_contrast_theme["colors"]["secondary"] = "#000000"  # Black
        high_contrast_theme["colors"]["accent"] = "#FF0000"  # Pure red
        high_contrast_theme["colors"]["success"] = "#008000"  # Pure green
        high_contrast_theme["colors"]["warning"] = "#FF8000"  # Orange
        high_contrast_theme["colors"]["danger"] = "#FF0000"  # Pure red
        high_contrast_theme["colors"]["info"] = "#0080FF"  # Bright blue
        
        # Set extreme contrast for backgrounds and text
        high_contrast_theme["colors"]["background"]["primary"] = "#FFFFFF"
        high_contrast_theme["colors"]["background"]["secondary"] = "#F0F0F0"
        high_contrast_theme["colors"]["background"]["tertiary"] = "#E0E0E0"
        
        high_contrast_theme["colors"]["text"]["primary"] = "#000000"
        high_contrast_theme["colors"]["text"]["secondary"] = "#000000"
        high_contrast_theme["colors"]["text"]["tertiary"] = "#404040"
        
        # Ensure text on colored backgrounds is always visible
        high_contrast_theme["colors"]["text"]["on_primary"] = "#FFFFFF"
        high_contrast_theme["colors"]["text"]["on_secondary"] = "#FFFFFF"
        high_contrast_theme["colors"]["text"]["on_accent"] = "#FFFFFF"
        high_contrast_theme["colors"]["text"]["on_success"] = "#FFFFFF"
        high_contrast_theme["colors"]["text"]["on_warning"] = "#000000"
        high_contrast_theme["colors"]["text"]["on_danger"] = "#FFFFFF"
        high_contrast_theme["colors"]["text"]["on_info"] = "#FFFFFF"
        
        # Increase border contrast
        high_contrast_theme["colors"]["border"]["light"] = "#000000"
        high_contrast_theme["colors"]["border"]["medium"] = "#000000"
        high_contrast_theme["colors"]["border"]["dark"] = "#000000"
        
        # Increase shadow contrast
        high_contrast_theme["colors"]["shadow"]["light"] = "rgba(0, 0, 0, 0.3)"
        high_contrast_theme["colors"]["shadow"]["medium"] = "rgba(0, 0, 0, 0.5)"
        high_contrast_theme["colors"]["shadow"]["dark"] = "rgba(0, 0, 0, 0.7)"
        
        # Adjust component-specific styles for high contrast
        high_contrast_theme["components"]["capsule"]["background"] = "#0000FF"
        high_contrast_theme["components"]["capsule"]["text_color"] = "#FFFFFF"
        high_contrast_theme["components"]["capsule"]["border_radius"] = "0.5rem"
        high_contrast_theme["components"]["capsule"]["shadow"] = "0 0 0 2px #000000"
        
        high_contrast_theme["components"]["trust_ribbon"]["background"] = "#FFFFFF"
        high_contrast_theme["components"]["trust_ribbon"]["border"] = "2px solid #000000"
        
        high_contrast_theme["components"]["mission_deck"]["card_border"] = "2px solid #000000"
        
        high_contrast_theme["components"]["swarm_lens"]["connection_line"] = "#000000"
        high_contrast_theme["components"]["swarm_lens"]["active_connection"] = "#0000FF"
        high_contrast_theme["components"]["swarm_lens"]["node_stroke"] = "#000000"
        
        high_contrast_theme["components"]["timeline_view"]["line_color"] = "#000000"
        high_contrast_theme["components"]["timeline_view"]["event_border"] = "2px solid #000000"
        
        # Increase font sizes for better readability
        for key in high_contrast_theme["typography"]["font_size"]:
            # Parse the rem value and increase by 10%
            current_size = float(high_contrast_theme["typography"]["font_size"][key].replace("rem", ""))
            new_size = current_size * 1.1
            high_contrast_theme["typography"]["font_size"][key] = f"{new_size:.3f}rem"
        
        # Increase font weights for better readability
        high_contrast_theme["typography"]["font_weight"]["regular"] = 500
        high_contrast_theme["typography"]["font_weight"]["medium"] = 600
        high_contrast_theme["typography"]["font_weight"]["semibold"] = 700
        high_contrast_theme["typography"]["font_weight"]["bold"] = 800
        
        return high_contrast_theme
    
    def _create_industry_adaptations(self) -> None:
        """Create industry-specific theme adaptations."""
        # Manufacturing industry adaptation
        manufacturing_adaptation = {
            "primary_color": "#FF6B00",  # Orange
            "secondary_color": "#555555",  # Dark gray
            "accent_color": "#FFB800",  # Amber
            "background_tint": "#FFF9F0",  # Warm white
            "component_styles": {
                "capsule": {
                    "background": "linear-gradient(135deg, #FF6B00, #FFB800)"
                },
                "ambient_veil": {
                    "background": "linear-gradient(180deg, rgba(255,249,240,0.9) 0%, rgba(255,249,240,0.7) 100%)",
                    "glow_color": "rgba(255, 107, 0, 0.2)"
                }
            }
        }
        
        # Logistics industry adaptation
        logistics_adaptation = {
            "primary_color": "#0077B6",  # Blue
            "secondary_color": "#023E8A",  # Dark blue
            "accent_color": "#00B4D8",  # Cyan
            "background_tint": "#F0F7FF",  # Cool white
            "component_styles": {
                "capsule": {
                    "background": "linear-gradient(135deg, #0077B6, #00B4D8)"
                },
                "ambient_veil": {
                    "background": "linear-gradient(180deg, rgba(240,247,255,0.9) 0%, rgba(240,247,255,0.7) 100%)",
                    "glow_color": "rgba(0, 119, 182, 0.2)"
                }
            }
        }
        
        # Energy industry adaptation
        energy_adaptation = {
            "primary_color": "#2B9348",  # Green
            "secondary_color": "#007F5F",  # Dark green
            "accent_color": "#55A630",  # Light green
            "background_tint": "#F0FFF4",  # Mint white
            "component_styles": {
                "capsule": {
                    "background": "linear-gradient(135deg, #2B9348, #55A630)"
                },
                "ambient_veil": {
                    "background": "linear-gradient(180deg, rgba(240,255,244,0.9) 0%, rgba(240,255,244,0.7) 100%)",
                    "glow_color": "rgba(43, 147, 72, 0.2)"
                }
            }
        }
        
        # Retail industry adaptation
        retail_adaptation = {
            "primary_color": "#9D4EDD",  # Purple
            "secondary_color": "#7B2CBF",  # Dark purple
            "accent_color": "#C77DFF",  # Light purple
            "background_tint": "#F8F0FF",  # Lavender white
            "component_styles": {
                "capsule": {
                    "background": "linear-gradient(135deg, #9D4EDD, #C77DFF)"
                },
                "ambient_veil": {
                    "background": "linear-gradient(180deg, rgba(248,240,255,0.9) 0%, rgba(248,240,255,0.7) 100%)",
                    "glow_color": "rgba(157, 78, 221, 0.2)"
                }
            }
        }
        
        # Store industry adaptations
        self.industry_adaptations["manufacturing"] = manufacturing_adaptation
        self.industry_adaptations["logistics"] = logistics_adaptation
        self.industry_adaptations["energy"] = energy_adaptation
        self.industry_adaptations["retail"] = retail_adaptation
    
    def _save_theme_to_file(self, theme_id: str, theme: Dict) -> None:
        """
        Save a theme to a file.
        
        Args:
            theme_id: Theme identifier
            theme: Theme definition
        """
        try:
            file_path = os.path.join(self.config["themes_directory"], f"{theme_id}.json")
            with open(file_path, "w") as f:
                json.dump(theme, f, indent=2)
            logger.debug(f"Saved theme '{theme_id}' to file")
        except Exception as e:
            logger.error(f"Error saving theme '{theme_id}' to file: {str(e)}")
    
    def _load_theme_from_file(self, theme_id: str) -> Optional[Dict]:
        """
        Load a theme from a file.
        
        Args:
            theme_id: Theme identifier
            
        Returns:
            Theme definition or None if not found
        """
        try:
            file_path = os.path.join(self.config["themes_directory"], f"{theme_id}.json")
            if not os.path.exists(file_path):
                logger.warning(f"Theme file not found: {file_path}")
                return None
            
            with open(file_path, "r") as f:
                theme = json.load(f)
            
            logger.debug(f"Loaded theme '{theme_id}' from file")
            return theme
        except Exception as e:
            logger.error(f"Error loading theme '{theme_id}' from file: {str(e)}")
            return None
    
    def _load_user_preferences(self) -> None:
        """Load user theme preferences."""
        try:
            file_path = os.path.join(self.config["themes_directory"], self.config["theme_persistence_file"])
            if not os.path.exists(file_path):
                logger.debug("User preferences file not found, using defaults")
                return
            
            with open(file_path, "r") as f:
                preferences = json.load(f)
            
            # Apply preferences
            if "theme" in preferences:
                self.current_theme_name = preferences["theme"]
            
            if "mode" in preferences:
                self.current_mode = preferences["mode"]
            
            if "customizations" in preferences:
                self.user_customizations = preferences["customizations"]
            
            logger.info(f"Loaded user preferences: theme='{self.current_theme_name}', mode='{self.current_mode}'")
        except Exception as e:
            logger.error(f"Error loading user preferences: {str(e)}")
    
    def _save_user_preferences(self) -> None:
        """Save user theme preferences."""
        try:
            preferences = {
                "theme": self.current_theme_name,
                "mode": self.current_mode,
                "customizations": self.user_customizations
            }
            
            file_path = os.path.join(self.config["themes_directory"], self.config["theme_persistence_file"])
            with open(file_path, "w") as f:
                json.dump(preferences, f, indent=2)
            
            logger.debug("Saved user preferences")
        except Exception as e:
            logger.error(f"Error saving user preferences: {str(e)}")
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        if not self.config["enable_context_adaptation"]:
            return
        
        context_type = event.get("type")
        
        # Handle industry context changes
        if context_type == "industry":
            industry_data = event.get("data", {})
            
            if "industry" in industry_data:
                industry = industry_data["industry"]
                self._adapt_theme_to_industry(industry)
        
        # Handle time context changes for auto mode
        elif context_type == "time" and self.current_mode == ThemeMode.AUTO.value:
            time_data = event.get("data", {})
            
            if "hour" in time_data:
                hour = time_data["hour"]
                self._adapt_theme_to_time(hour)
        
        # Handle user preference context changes
        elif context_type == "user_preferences":
            preferences = event.get("data", {})
            
            if "theme_mode" in preferences:
                self.set_theme_mode(preferences["theme_mode"])
            
            if "theme_name" in preferences:
                self.set_theme(preferences["theme_name"])
            
            if "theme_customizations" in preferences:
                self.apply_user_customizations(preferences["theme_customizations"])
    
    def _adapt_theme_to_industry(self, industry: str) -> None:
        """
        Adapt the current theme to an industry.
        
        Args:
            industry: Industry identifier
        """
        if industry not in self.industry_adaptations:
            logger.debug(f"No theme adaptation for industry: {industry}")
            return
        
        logger.info(f"Adapting theme to industry: {industry}")
        
        # Get industry adaptation
        adaptation = self.industry_adaptations[industry]
        
        # Apply adaptation to current theme
        current_theme = self.get_current_theme()
        if not current_theme:
            logger.error("Cannot adapt theme: Current theme not found")
            return
        
        # Create adapted theme ID
        adapted_theme_id = f"{self.current_theme_name}_{self.current_mode}_{industry}"
        
        # Check if adapted theme is already cached
        if (
            self.config["cache_themes"] and 
            adapted_theme_id in self.theme_cache and 
            time.time() - self.theme_cache_timestamps.get(adapted_theme_id, 0) < self.config["cache_expiry"]
        ):
            # Use cached theme
            self.current_theme_name = adapted_theme_id
            logger.debug(f"Using cached industry-adapted theme: {adapted_theme_id}")
            return
        
        # Create a deep copy of the current theme
        adapted_theme = json.loads(json.dumps(current_theme))
        
        # Apply industry-specific colors
        if "primary_color" in adaptation:
            adapted_theme["colors"]["primary"] = adaptation["primary_color"]
        
        if "secondary_color" in adaptation:
            adapted_theme["colors"]["secondary"] = adaptation["secondary_color"]
        
        if "accent_color" in adaptation:
            adapted_theme["colors"]["accent"] = adaptation["accent_color"]
        
        # Apply background tint if in light mode
        if self.current_mode == ThemeMode.LIGHT.value and "background_tint" in adaptation:
            adapted_theme["colors"]["background"]["primary"] = adaptation["background_tint"]
        
        # Apply component-specific styles
        if "component_styles" in adaptation:
            for component, styles in adaptation["component_styles"].items():
                if component in adapted_theme["components"]:
                    for style_key, style_value in styles.items():
                        adapted_theme["components"][component][style_key] = style_value
        
        # Store adapted theme in cache
        self.theme_cache[adapted_theme_id] = adapted_theme
        self.theme_cache_timestamps[adapted_theme_id] = time.time()
        
        # Update current theme name
        self.current_theme_name = adapted_theme_id
        
        logger.info(f"Created industry-adapted theme: {adapted_theme_id}")
    
    def _adapt_theme_to_time(self, hour: int) -> None:
        """
        Adapt the theme mode based on time of day.
        
        Args:
            hour: Current hour (0-23)
        """
        if not self.config["enable_auto_mode"]:
            return
        
        light_start, light_end = self.config["auto_mode_light_hours"]
        
        # Determine if it should be light or dark mode
        if light_start <= hour < light_end:
            # Daytime - use light mode
            if self.current_mode != ThemeMode.LIGHT.value:
                logger.info(f"Auto switching to light mode (hour: {hour})")
                self.set_theme_mode(ThemeMode.LIGHT.value)
        else:
            # Nighttime - use dark mode
            if self.current_mode != ThemeMode.DARK.value:
                logger.info(f"Auto switching to dark mode (hour: {hour})")
                self.set_theme_mode(ThemeMode.DARK.value)
    
    def get_current_theme(self) -> Optional[Dict]:
        """
        Get the current theme definition.
        
        Returns:
            Current theme definition or None if not found
        """
        # Check if theme is in cache
        if (
            self.config["cache_themes"] and 
            self.current_theme_name in self.theme_cache and 
            time.time() - self.theme_cache_timestamps.get(self.current_theme_name, 0) < self.config["cache_expiry"]
        ):
            # Use cached theme
            theme = self.theme_cache[self.current_theme_name]
        else:
            # Load theme from file
            theme_id = self.current_theme_name
            
            # If theme includes mode, extract base theme name
            if "_" in theme_id:
                parts = theme_id.split("_")
                base_theme = parts[0]
                mode = parts[1]
                
                # Load base theme
                theme = self._load_theme_from_file(f"{base_theme}_{mode}")
            else:
                # Load theme with current mode
                theme = self._load_theme_from_file(f"{theme_id}_{self.current_mode}")
            
            if not theme:
                # Fall back to default theme
                logger.warning(f"Theme '{theme_id}' not found, falling back to default")
                theme = self._load_theme_from_file(f"{self.config['default_theme']}_{self.current_mode}")
            
            if not theme:
                logger.error("Default theme not found")
                return None
            
            # Cache theme
            if self.config["cache_themes"]:
                self.theme_cache[self.current_theme_name] = theme
                self.theme_cache_timestamps[self.current_theme_name] = time.time()
        
        # Apply user customizations
        if self.user_customizations and self.config["enable_user_customization"]:
            theme = self._apply_customizations_to_theme(theme, self.user_customizations)
        
        return theme
    
    def _apply_customizations_to_theme(self, theme: Dict, customizations: Dict) -> Dict:
        """
        Apply user customizations to a theme.
        
        Args:
            theme: Theme definition
            customizations: User customizations
            
        Returns:
            Customized theme definition
        """
        # Create a deep copy of the theme
        customized_theme = json.loads(json.dumps(theme))
        
        # Apply color customizations
        if "colors" in customizations:
            for color_key, color_value in customizations["colors"].items():
                if color_key in customized_theme["colors"]:
                    if isinstance(customized_theme["colors"][color_key], dict):
                        # Handle nested color objects (e.g., background, text)
                        for nested_key, nested_value in color_value.items():
                            if nested_key in customized_theme["colors"][color_key]:
                                customized_theme["colors"][color_key][nested_key] = nested_value
                    else:
                        # Handle direct color values
                        customized_theme["colors"][color_key] = color_value
        
        # Apply typography customizations
        if "typography" in customizations:
            for typo_key, typo_value in customizations["typography"].items():
                if typo_key in customized_theme["typography"]:
                    if isinstance(customized_theme["typography"][typo_key], dict):
                        # Handle nested typography objects (e.g., font_size, font_weight)
                        for nested_key, nested_value in typo_value.items():
                            if nested_key in customized_theme["typography"][typo_key]:
                                customized_theme["typography"][typo_key][nested_key] = nested_value
                    else:
                        # Handle direct typography values
                        customized_theme["typography"][typo_key] = typo_value
        
        # Apply component customizations
        if "components" in customizations:
            for component_key, component_value in customizations["components"].items():
                if component_key in customized_theme["components"]:
                    for style_key, style_value in component_value.items():
                        customized_theme["components"][component_key][style_key] = style_value
        
        return customized_theme
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Set the current theme.
        
        Args:
            theme_name: Theme name
            
        Returns:
            Boolean indicating success
        """
        # Check if theme exists
        theme_id = f"{theme_name}_{self.current_mode}"
        theme = self._load_theme_from_file(theme_id)
        
        if not theme:
            logger.error(f"Theme '{theme_name}' not found")
            return False
        
        # Update current theme
        self.current_theme_name = theme_name
        
        # Save user preferences
        self._save_user_preferences()
        
        logger.info(f"Set theme to '{theme_name}'")
        return True
    
    def set_theme_mode(self, mode: str) -> bool:
        """
        Set the current theme mode.
        
        Args:
            mode: Theme mode (light, dark, auto, high_contrast)
            
        Returns:
            Boolean indicating success
        """
        # Validate mode
        try:
            theme_mode = ThemeMode(mode)
        except ValueError:
            logger.error(f"Invalid theme mode: {mode}")
            return False
        
        # Update current mode
        self.current_mode = mode
        
        # If auto mode, immediately adapt to current time
        if mode == ThemeMode.AUTO.value and self.config["enable_auto_mode"]:
            import datetime
            current_hour = datetime.datetime.now().hour
            self._adapt_theme_to_time(current_hour)
        
        # Save user preferences
        self._save_user_preferences()
        
        logger.info(f"Set theme mode to '{mode}'")
        return True
    
    def apply_user_customizations(self, customizations: Dict) -> bool:
        """
        Apply user customizations to the current theme.
        
        Args:
            customizations: User customizations
            
        Returns:
            Boolean indicating success
        """
        if not self.config["enable_user_customization"]:
            logger.warning("User customization is disabled")
            return False
        
        # Update user customizations
        self.user_customizations = customizations
        
        # Save user preferences
        self._save_user_preferences()
        
        logger.info("Applied user customizations to theme")
        return True
    
    def reset_user_customizations(self) -> bool:
        """
        Reset user customizations.
        
        Returns:
            Boolean indicating success
        """
        # Clear user customizations
        self.user_customizations = {}
        
        # Save user preferences
        self._save_user_preferences()
        
        logger.info("Reset user customizations")
        return True
    
    def get_available_themes(self) -> List[str]:
        """
        Get a list of available themes.
        
        Returns:
            List of theme names
        """
        try:
            # Get all theme files
            theme_files = [
                f for f in os.listdir(self.config["themes_directory"])
                if f.endswith(".json") and f != self.config["theme_persistence_file"]
            ]
            
            # Extract theme names
            theme_names = set()
            for file_name in theme_files:
                # Remove .json extension
                name = file_name.replace(".json", "")
                
                # Extract base theme name (before mode)
                if "_" in name:
                    base_name = name.split("_")[0]
                    theme_names.add(base_name)
                else:
                    theme_names.add(name)
            
            return sorted(list(theme_names))
        except Exception as e:
            logger.error(f"Error getting available themes: {str(e)}")
            return [self.config["default_theme"]]
    
    def get_theme_css_variables(self) -> str:
        """
        Get the current theme as CSS variables.
        
        Returns:
            CSS variables string
        """
        theme = self.get_current_theme()
        if not theme:
            logger.error("Cannot generate CSS variables: Current theme not found")
            return ""
        
        css_vars = [":root {"]
        
        # Add color variables
        for color_key, color_value in theme["colors"].items():
            if isinstance(color_value, dict):
                # Handle nested color objects (e.g., background, text)
                for nested_key, nested_value in color_value.items():
                    css_vars.append(f"  --color-{color_key}-{nested_key}: {nested_value};")
            else:
                # Handle direct color values
                css_vars.append(f"  --color-{color_key}: {color_value};")
        
        # Add typography variables
        for typo_key, typo_value in theme["typography"].items():
            if isinstance(typo_value, dict):
                # Handle nested typography objects (e.g., font_size, font_weight)
                for nested_key, nested_value in typo_value.items():
                    css_vars.append(f"  --typography-{typo_key}-{nested_key}: {nested_value};")
            else:
                # Handle direct typography values
                css_vars.append(f"  --typography-{typo_key}: {typo_value};")
        
        # Add spacing variables
        for spacing_key, spacing_value in theme["spacing"].items():
            css_vars.append(f"  --spacing-{spacing_key}: {spacing_value};")
        
        # Add border variables
        for border_key, border_value in theme["borders"].items():
            if isinstance(border_value, dict):
                for nested_key, nested_value in border_value.items():
                    css_vars.append(f"  --border-{border_key}-{nested_key}: {nested_value};")
            else:
                css_vars.append(f"  --border-{border_key}: {border_value};")
        
        # Add shadow variables
        for shadow_key, shadow_value in theme["shadows"].items():
            css_vars.append(f"  --shadow-{shadow_key}: {shadow_value};")
        
        # Add transition variables
        for trans_key, trans_value in theme["transitions"].items():
            if isinstance(trans_value, dict):
                for nested_key, nested_value in trans_value.items():
                    css_vars.append(f"  --transition-{trans_key}-{nested_key}: {nested_value};")
            else:
                css_vars.append(f"  --transition-{trans_key}: {trans_value};")
        
        # Add z-index variables
        for z_key, z_value in theme["z_index"].items():
            css_vars.append(f"  --z-index-{z_key}: {z_value};")
        
        # Add component variables
        for component_key, component_value in theme["components"].items():
            for style_key, style_value in component_value.items():
                css_vars.append(f"  --component-{component_key}-{style_key}: {style_value};")
        
        # Add animation flag
        css_vars.append(f"  --animation-enabled: {str(self.config['animation_enabled']).lower()};")
        css_vars.append(f"  --transition-duration: {self.config['transition_duration']}ms;")
        
        css_vars.append("}")
        
        return "\n".join(css_vars)
    
    def get_theme_json(self) -> str:
        """
        Get the current theme as a JSON string.
        
        Returns:
            JSON string representation of the current theme
        """
        theme = self.get_current_theme()
        if not theme:
            logger.error("Cannot generate JSON: Current theme not found")
            return "{}"
        
        return json.dumps(theme, indent=2)
    
    def generate_color_palette(self, base_color: str, count: int = 5) -> List[str]:
        """
        Generate a color palette based on a base color.
        
        Args:
            base_color: Base color in hex format (e.g., "#0056B3")
            count: Number of colors to generate
            
        Returns:
            List of hex color strings
        """
        try:
            # Convert hex to RGB
            base_color = base_color.lstrip("#")
            r = int(base_color[0:2], 16) / 255.0
            g = int(base_color[2:4], 16) / 255.0
            b = int(base_color[4:6], 16) / 255.0
            
            # Convert RGB to HSV
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Generate palette
            palette = []
            for i in range(count):
                # Vary saturation and value
                new_s = max(0.1, min(1.0, s - 0.1 + (i / count) * 0.2))
                new_v = max(0.2, min(1.0, v - 0.3 + (i / count) * 0.6))
                
                # Convert back to RGB
                new_r, new_g, new_b = colorsys.hsv_to_rgb(h, new_s, new_v)
                
                # Convert to hex
                hex_color = "#{:02x}{:02x}{:02x}".format(
                    int(new_r * 255), 
                    int(new_g * 255), 
                    int(new_b * 255)
                )
                
                palette.append(hex_color)
            
            return palette
        except Exception as e:
            logger.error(f"Error generating color palette: {str(e)}")
            return [base_color] * count
    
    def get_contrast_color(self, background_color: str) -> str:
        """
        Get a contrasting text color for a background color.
        
        Args:
            background_color: Background color in hex format (e.g., "#0056B3")
            
        Returns:
            Contrasting color ("#FFFFFF" or "#000000")
        """
        try:
            # Convert hex to RGB
            background_color = background_color.lstrip("#")
            r = int(background_color[0:2], 16) / 255.0
            g = int(background_color[2:4], 16) / 255.0
            b = int(background_color[4:6], 16) / 255.0
            
            # Calculate luminance
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            
            # Return white for dark backgrounds, black for light backgrounds
            return "#000000" if luminance > 0.5 else "#FFFFFF"
        except Exception as e:
            logger.error(f"Error calculating contrast color: {str(e)}")
            return "#000000"  # Default to black on error
    
    def shutdown(self) -> None:
        """Shutdown the Theme Manager."""
        logger.info("Shutting down Theme Manager")
        
        # Save user preferences
        self._save_user_preferences()
