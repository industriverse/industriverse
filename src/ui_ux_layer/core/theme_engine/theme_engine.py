"""
Theme Engine for the Industriverse UI/UX Layer.

This module provides comprehensive theming capabilities for the Universal Skin
and Agent Capsules, enabling consistent visual styling across devices and industrial contexts.

Author: Manus
"""

import logging
import time
import threading
import uuid
import json
import os
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass, field, asdict

class ThemeType(Enum):
    """Enumeration of theme types."""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    CUSTOM = "custom"

class ThemeScope(Enum):
    """Enumeration of theme scopes."""
    GLOBAL = "global"  # Global theme (apply to all contexts)
    CONTEXT = "context"  # Context-specific theme
    ROLE = "role"  # Role-specific theme
    USER = "user"  # User-specific theme
    DEVICE = "device"  # Device-specific theme

@dataclass
class ColorPalette:
    """Data class representing a color palette."""
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    error: str
    warning: str
    success: str
    info: str
    text_primary: str
    text_secondary: str
    text_hint: str
    text_disabled: str
    divider: str
    custom_colors: Dict[str, str] = field(default_factory=dict)

@dataclass
class Typography:
    """Data class representing typography settings."""
    font_family_primary: str
    font_family_secondary: str
    font_size_base: int
    font_size_small: int
    font_size_medium: int
    font_size_large: int
    font_size_xlarge: int
    font_weight_light: int
    font_weight_regular: int
    font_weight_medium: int
    font_weight_bold: int
    line_height_tight: float
    line_height_normal: float
    line_height_relaxed: float
    letter_spacing_normal: float
    custom_typography: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Spacing:
    """Data class representing spacing settings."""
    space_xxsmall: int
    space_xsmall: int
    space_small: int
    space_medium: int
    space_large: int
    space_xlarge: int
    space_xxlarge: int
    custom_spacing: Dict[str, int] = field(default_factory=dict)

@dataclass
class BorderRadius:
    """Data class representing border radius settings."""
    radius_none: int
    radius_small: int
    radius_medium: int
    radius_large: int
    radius_pill: int
    radius_circle: int
    custom_radius: Dict[str, int] = field(default_factory=dict)

@dataclass
class Shadows:
    """Data class representing shadow settings."""
    shadow_none: str
    shadow_small: str
    shadow_medium: str
    shadow_large: str
    shadow_xlarge: str
    custom_shadows: Dict[str, str] = field(default_factory=dict)

@dataclass
class Animations:
    """Data class representing animation settings."""
    duration_instant: int
    duration_fast: int
    duration_normal: int
    duration_slow: int
    easing_standard: str
    easing_accelerate: str
    easing_decelerate: str
    custom_animations: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Theme:
    """Data class representing a complete theme."""
    theme_id: str
    name: str
    type: ThemeType
    scope: ThemeScope
    colors: ColorPalette
    typography: Typography
    spacing: Spacing
    border_radius: BorderRadius
    shadows: Shadows
    animations: Animations
    user_id: Optional[str] = None
    context_id: Optional[str] = None
    role_id: Optional[str] = None
    device_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ThemeEngine:
    """
    Provides comprehensive theming capabilities for the Industriverse UI/UX Layer.
    
    This class provides:
    - Theme creation and management
    - Scope-based theme application (global, context, role, user, device)
    - Theme inheritance and override
    - Dynamic theme switching
    - Theme export and import
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Theme Engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.themes: Dict[str, Theme] = {}
        self.active_theme_id: Optional[str] = None
        self.theme_listeners: Dict[str, List[Callable[[Theme], None]]] = {}
        self.scope_listeners: Dict[ThemeScope, List[Callable[[Theme], None]]] = {}
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        self.storage_path = self.config.get("storage_path", "themes")
        
        # Initialize theme scopes
        for scope in ThemeScope:
            self.scope_listeners[scope] = []
            
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
    def start(self) -> bool:
        """
        Start the Theme Engine.
        
        Returns:
            True if the engine was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Load themes from storage
        self._load_themes()
        
        # Create default themes if none exist
        if not self.themes:
            self._create_default_themes()
            
        # Set active theme
        if not self.active_theme_id and self.themes:
            # Use the first global theme as default
            for theme_id, theme in self.themes.items():
                if theme.scope == ThemeScope.GLOBAL:
                    self.active_theme_id = theme_id
                    break
                    
        # Dispatch event
        self._dispatch_event({
            "event_type": "theme_engine_started",
            "active_theme_id": self.active_theme_id
        })
        
        self.logger.info("Theme Engine started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Theme Engine.
        
        Returns:
            True if the engine was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Save themes to storage
        self._save_themes()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "theme_engine_stopped"
        })
        
        self.logger.info("Theme Engine stopped.")
        return True
    
    def create_theme(self,
                   name: str,
                   type: ThemeType,
                   scope: ThemeScope,
                   colors: ColorPalette,
                   typography: Typography,
                   spacing: Spacing,
                   border_radius: BorderRadius,
                   shadows: Shadows,
                   animations: Animations,
                   user_id: Optional[str] = None,
                   context_id: Optional[str] = None,
                   role_id: Optional[str] = None,
                   device_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new theme.
        
        Args:
            name: Theme name
            type: Theme type
            scope: Theme scope
            colors: Color palette
            typography: Typography settings
            spacing: Spacing settings
            border_radius: Border radius settings
            shadows: Shadow settings
            animations: Animation settings
            user_id: Optional user ID for user-specific themes
            context_id: Optional context ID for context-specific themes
            role_id: Optional role ID for role-specific themes
            device_id: Optional device ID for device-specific themes
            metadata: Additional metadata for this theme
            
        Returns:
            The theme ID
        """
        # Validate scope-specific parameters
        if scope == ThemeScope.USER and user_id is None:
            raise ValueError("User ID is required for user-specific themes")
        if scope == ThemeScope.CONTEXT and context_id is None:
            raise ValueError("Context ID is required for context-specific themes")
        if scope == ThemeScope.ROLE and role_id is None:
            raise ValueError("Role ID is required for role-specific themes")
        if scope == ThemeScope.DEVICE and device_id is None:
            raise ValueError("Device ID is required for device-specific themes")
            
        # Generate theme ID
        theme_id = str(uuid.uuid4())
        
        # Create theme
        theme = Theme(
            theme_id=theme_id,
            name=name,
            type=type,
            scope=scope,
            colors=colors,
            typography=typography,
            spacing=spacing,
            border_radius=border_radius,
            shadows=shadows,
            animations=animations,
            user_id=user_id,
            context_id=context_id,
            role_id=role_id,
            device_id=device_id,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        # Store theme
        self.themes[theme_id] = theme
        
        # Save themes to storage
        self._save_themes()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "theme_created",
            "theme_id": theme_id,
            "name": name,
            "type": type.value,
            "scope": scope.value
        })
        
        # Notify theme listeners
        if theme_id in self.theme_listeners:
            for listener in self.theme_listeners[theme_id]:
                try:
                    listener(theme)
                except Exception as e:
                    self.logger.error(f"Error in theme listener for {theme_id}: {e}")
                    
        # Notify scope listeners
        for listener in self.scope_listeners[scope]:
            try:
                listener(theme)
            except Exception as e:
                self.logger.error(f"Error in scope listener for {scope.value}: {e}")
                
        self.logger.debug(f"Created theme: {theme_id} ({name})")
        return theme_id
    
    def get_theme(self, theme_id: str) -> Optional[Theme]:
        """
        Get a theme by ID.
        
        Args:
            theme_id: ID of the theme to get
            
        Returns:
            The theme, or None if not found
        """
        return self.themes.get(theme_id)
    
    def get_active_theme(self) -> Optional[Theme]:
        """
        Get the active theme.
        
        Returns:
            The active theme, or None if no active theme
        """
        if self.active_theme_id:
            return self.themes.get(self.active_theme_id)
        return None
    
    def get_theme_for_context(self,
                            user_id: Optional[str] = None,
                            context_id: Optional[str] = None,
                            role_id: Optional[str] = None,
                            device_id: Optional[str] = None) -> Optional[Theme]:
        """
        Get the appropriate theme for a given context with scope inheritance.
        
        This method implements theme inheritance in the following order:
        1. User-specific theme
        2. Device-specific theme
        3. Role-specific theme
        4. Context-specific theme
        5. Global theme
        
        Args:
            user_id: Optional user ID for user-specific themes
            context_id: Optional context ID for context-specific themes
            role_id: Optional role ID for role-specific themes
            device_id: Optional device ID for device-specific themes
            
        Returns:
            The appropriate theme, or None if no theme found
        """
        # Check user-specific theme
        if user_id is not None:
            for theme in self.themes.values():
                if (theme.scope == ThemeScope.USER and
                    theme.user_id == user_id):
                    return theme
                    
        # Check device-specific theme
        if device_id is not None:
            for theme in self.themes.values():
                if (theme.scope == ThemeScope.DEVICE and
                    theme.device_id == device_id):
                    return theme
                    
        # Check role-specific theme
        if role_id is not None:
            for theme in self.themes.values():
                if (theme.scope == ThemeScope.ROLE and
                    theme.role_id == role_id):
                    return theme
                    
        # Check context-specific theme
        if context_id is not None:
            for theme in self.themes.values():
                if (theme.scope == ThemeScope.CONTEXT and
                    theme.context_id == context_id):
                    return theme
                    
        # Check global theme
        for theme in self.themes.values():
            if theme.scope == ThemeScope.GLOBAL:
                return theme
                
        return None
    
    def set_active_theme(self, theme_id: str) -> bool:
        """
        Set the active theme.
        
        Args:
            theme_id: ID of the theme to set as active
            
        Returns:
            True if the theme was set as active, False if not found
        """
        if theme_id not in self.themes:
            self.logger.warning(f"Theme {theme_id} not found.")
            return False
            
        old_theme_id = self.active_theme_id
        self.active_theme_id = theme_id
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "active_theme_changed",
            "theme_id": theme_id,
            "old_theme_id": old_theme_id,
            "name": self.themes[theme_id].name,
            "type": self.themes[theme_id].type.value
        })
        
        self.logger.debug(f"Set active theme: {theme_id} ({self.themes[theme_id].name})")
        return True
    
    def update_theme(self,
                   theme_id: str,
                   name: Optional[str] = None,
                   type: Optional[ThemeType] = None,
                   colors: Optional[ColorPalette] = None,
                   typography: Optional[Typography] = None,
                   spacing: Optional[Spacing] = None,
                   border_radius: Optional[BorderRadius] = None,
                   shadows: Optional[Shadows] = None,
                   animations: Optional[Animations] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing theme.
        
        Args:
            theme_id: ID of the theme to update
            name: Optional new name
            type: Optional new type
            colors: Optional new color palette
            typography: Optional new typography settings
            spacing: Optional new spacing settings
            border_radius: Optional new border radius settings
            shadows: Optional new shadow settings
            animations: Optional new animation settings
            metadata: Optional new metadata
            
        Returns:
            True if the theme was updated, False if not found
        """
        if theme_id not in self.themes:
            self.logger.warning(f"Theme {theme_id} not found.")
            return False
            
        theme = self.themes[theme_id]
        
        # Update theme properties
        if name is not None:
            theme.name = name
        if type is not None:
            theme.type = type
        if colors is not None:
            theme.colors = colors
        if typography is not None:
            theme.typography = typography
        if spacing is not None:
            theme.spacing = spacing
        if border_radius is not None:
            theme.border_radius = border_radius
        if shadows is not None:
            theme.shadows = shadows
        if animations is not None:
            theme.animations = animations
        if metadata is not None:
            theme.metadata.update(metadata)
            
        # Update timestamp
        theme.timestamp = time.time()
        
        # Save themes to storage
        self._save_themes()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "theme_updated",
            "theme_id": theme_id,
            "name": theme.name,
            "type": theme.type.value,
            "scope": theme.scope.value
        })
        
        # Notify theme listeners
        if theme_id in self.theme_listeners:
            for listener in self.theme_listeners[theme_id]:
                try:
                    listener(theme)
                except Exception as e:
                    self.logger.error(f"Error in theme listener for {theme_id}: {e}")
                    
        # Notify scope listeners
        for listener in self.scope_listeners[theme.scope]:
            try:
                listener(theme)
            except Exception as e:
                self.logger.error(f"Error in scope listener for {theme.scope.value}: {e}")
                
        self.logger.debug(f"Updated theme: {theme_id} ({theme.name})")
        return True
    
    def delete_theme(self, theme_id: str) -> bool:
        """
        Delete a theme.
        
        Args:
            theme_id: ID of the theme to delete
            
        Returns:
            True if the theme was deleted, False if not found
        """
        if theme_id not in self.themes:
            self.logger.warning(f"Theme {theme_id} not found.")
            return False
            
        theme = self.themes[theme_id]
        
        # Check if this is the active theme
        if theme_id == self.active_theme_id:
            # Find another theme to set as active
            for other_theme_id, other_theme in self.themes.items():
                if other_theme_id != theme_id and other_theme.scope == ThemeScope.GLOBAL:
                    self.active_theme_id = other_theme_id
                    break
            else:
                self.active_theme_id = None
                
        # Remove theme
        del self.themes[theme_id]
        
        # Save themes to storage
        self._save_themes()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "theme_deleted",
            "theme_id": theme_id,
            "name": theme.name,
            "type": theme.type.value,
            "scope": theme.scope.value
        })
        
        self.logger.debug(f"Deleted theme: {theme_id} ({theme.name})")
        return True
    
    def import_themes(self, themes_data: Dict[str, Any]) -> int:
        """
        Import themes from a dictionary.
        
        Args:
            themes_data: Dictionary of theme data
            
        Returns:
            Number of themes imported
        """
        count = 0
        
        for theme_data in themes_data.get("themes", []):
            try:
                # Create color palette
                colors_data = theme_data["colors"]
                colors = ColorPalette(
                    primary=colors_data["primary"],
                    secondary=colors_data["secondary"],
                    accent=colors_data["accent"],
                    background=colors_data["background"],
                    surface=colors_data["surface"],
                    error=colors_data["error"],
                    warning=colors_data["warning"],
                    success=colors_data["success"],
                    info=colors_data["info"],
                    text_primary=colors_data["text_primary"],
                    text_secondary=colors_data["text_secondary"],
                    text_hint=colors_data["text_hint"],
                    text_disabled=colors_data["text_disabled"],
                    divider=colors_data["divider"],
                    custom_colors=colors_data.get("custom_colors", {})
                )
                
                # Create typography
                typography_data = theme_data["typography"]
                typography = Typography(
                    font_family_primary=typography_data["font_family_primary"],
                    font_family_secondary=typography_data["font_family_secondary"],
                    font_size_base=typography_data["font_size_base"],
                    font_size_small=typography_data["font_size_small"],
                    font_size_medium=typography_data["font_size_medium"],
                    font_size_large=typography_data["font_size_large"],
                    font_size_xlarge=typography_data["font_size_xlarge"],
                    font_weight_light=typography_data["font_weight_light"],
                    font_weight_regular=typography_data["font_weight_regular"],
                    font_weight_medium=typography_data["font_weight_medium"],
                    font_weight_bold=typography_data["font_weight_bold"],
                    line_height_tight=typography_data["line_height_tight"],
                    line_height_normal=typography_data["line_height_normal"],
                    line_height_relaxed=typography_data["line_height_relaxed"],
                    letter_spacing_normal=typography_data["letter_spacing_normal"],
                    custom_typography=typography_data.get("custom_typography", {})
                )
                
                # Create spacing
                spacing_data = theme_data["spacing"]
                spacing = Spacing(
                    space_xxsmall=spacing_data["space_xxsmall"],
                    space_xsmall=spacing_data["space_xsmall"],
                    space_small=spacing_data["space_small"],
                    space_medium=spacing_data["space_medium"],
                    space_large=spacing_data["space_large"],
                    space_xlarge=spacing_data["space_xlarge"],
                    space_xxlarge=spacing_data["space_xxlarge"],
                    custom_spacing=spacing_data.get("custom_spacing", {})
                )
                
                # Create border radius
                border_radius_data = theme_data["border_radius"]
                border_radius = BorderRadius(
                    radius_none=border_radius_data["radius_none"],
                    radius_small=border_radius_data["radius_small"],
                    radius_medium=border_radius_data["radius_medium"],
                    radius_large=border_radius_data["radius_large"],
                    radius_pill=border_radius_data["radius_pill"],
                    radius_circle=border_radius_data["radius_circle"],
                    custom_radius=border_radius_data.get("custom_radius", {})
                )
                
                # Create shadows
                shadows_data = theme_data["shadows"]
                shadows = Shadows(
                    shadow_none=shadows_data["shadow_none"],
                    shadow_small=shadows_data["shadow_small"],
                    shadow_medium=shadows_data["shadow_medium"],
                    shadow_large=shadows_data["shadow_large"],
                    shadow_xlarge=shadows_data["shadow_xlarge"],
                    custom_shadows=shadows_data.get("custom_shadows", {})
                )
                
                # Create animations
                animations_data = theme_data["animations"]
                animations = Animations(
                    duration_instant=animations_data["duration_instant"],
                    duration_fast=animations_data["duration_fast"],
                    duration_normal=animations_data["duration_normal"],
                    duration_slow=animations_data["duration_slow"],
                    easing_standard=animations_data["easing_standard"],
                    easing_accelerate=animations_data["easing_accelerate"],
                    easing_decelerate=animations_data["easing_decelerate"],
                    custom_animations=animations_data.get("custom_animations", {})
                )
                
                # Create theme
                theme = Theme(
                    theme_id=theme_data.get("theme_id", str(uuid.uuid4())),
                    name=theme_data["name"],
                    type=ThemeType(theme_data["type"]),
                    scope=ThemeScope(theme_data["scope"]),
                    colors=colors,
                    typography=typography,
                    spacing=spacing,
                    border_radius=border_radius,
                    shadows=shadows,
                    animations=animations,
                    user_id=theme_data.get("user_id"),
                    context_id=theme_data.get("context_id"),
                    role_id=theme_data.get("role_id"),
                    device_id=theme_data.get("device_id"),
                    timestamp=theme_data.get("timestamp", time.time()),
                    metadata=theme_data.get("metadata", {})
                )
                
                # Store theme
                self.themes[theme.theme_id] = theme
                count += 1
                
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error importing theme: {e}")
                
        # Save themes to storage
        self._save_themes()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "themes_imported",
            "count": count
        })
        
        self.logger.debug(f"Imported {count} themes")
        return count
    
    def export_themes(self,
                    scope: Optional[ThemeScope] = None,
                    user_id: Optional[str] = None,
                    context_id: Optional[str] = None,
                    role_id: Optional[str] = None,
                    device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Export themes to a dictionary.
        
        Args:
            scope: Optional scope to export
            user_id: Optional user ID for user-specific themes
            context_id: Optional context ID for context-specific themes
            role_id: Optional role ID for role-specific themes
            device_id: Optional device ID for device-specific themes
            
        Returns:
            Dictionary of theme data
        """
        themes_to_export = []
        
        for theme in self.themes.values():
            # Apply filters
            if scope is not None and theme.scope != scope:
                continue
                
            if user_id is not None and theme.user_id != user_id:
                continue
                
            if context_id is not None and theme.context_id != context_id:
                continue
                
            if role_id is not None and theme.role_id != role_id:
                continue
                
            if device_id is not None and theme.device_id != device_id:
                continue
                
            # Convert theme to dictionary
            theme_dict = {
                "theme_id": theme.theme_id,
                "name": theme.name,
                "type": theme.type.value,
                "scope": theme.scope.value,
                "user_id": theme.user_id,
                "context_id": theme.context_id,
                "role_id": theme.role_id,
                "device_id": theme.device_id,
                "timestamp": theme.timestamp,
                "metadata": theme.metadata,
                
                # Color palette
                "colors": {
                    "primary": theme.colors.primary,
                    "secondary": theme.colors.secondary,
                    "accent": theme.colors.accent,
                    "background": theme.colors.background,
                    "surface": theme.colors.surface,
                    "error": theme.colors.error,
                    "warning": theme.colors.warning,
                    "success": theme.colors.success,
                    "info": theme.colors.info,
                    "text_primary": theme.colors.text_primary,
                    "text_secondary": theme.colors.text_secondary,
                    "text_hint": theme.colors.text_hint,
                    "text_disabled": theme.colors.text_disabled,
                    "divider": theme.colors.divider,
                    "custom_colors": theme.colors.custom_colors
                },
                
                # Typography
                "typography": {
                    "font_family_primary": theme.typography.font_family_primary,
                    "font_family_secondary": theme.typography.font_family_secondary,
                    "font_size_base": theme.typography.font_size_base,
                    "font_size_small": theme.typography.font_size_small,
                    "font_size_medium": theme.typography.font_size_medium,
                    "font_size_large": theme.typography.font_size_large,
                    "font_size_xlarge": theme.typography.font_size_xlarge,
                    "font_weight_light": theme.typography.font_weight_light,
                    "font_weight_regular": theme.typography.font_weight_regular,
                    "font_weight_medium": theme.typography.font_weight_medium,
                    "font_weight_bold": theme.typography.font_weight_bold,
                    "line_height_tight": theme.typography.line_height_tight,
                    "line_height_normal": theme.typography.line_height_normal,
                    "line_height_relaxed": theme.typography.line_height_relaxed,
                    "letter_spacing_normal": theme.typography.letter_spacing_normal,
                    "custom_typography": theme.typography.custom_typography
                },
                
                # Spacing
                "spacing": {
                    "space_xxsmall": theme.spacing.space_xxsmall,
                    "space_xsmall": theme.spacing.space_xsmall,
                    "space_small": theme.spacing.space_small,
                    "space_medium": theme.spacing.space_medium,
                    "space_large": theme.spacing.space_large,
                    "space_xlarge": theme.spacing.space_xlarge,
                    "space_xxlarge": theme.spacing.space_xxlarge,
                    "custom_spacing": theme.spacing.custom_spacing
                },
                
                # Border radius
                "border_radius": {
                    "radius_none": theme.border_radius.radius_none,
                    "radius_small": theme.border_radius.radius_small,
                    "radius_medium": theme.border_radius.radius_medium,
                    "radius_large": theme.border_radius.radius_large,
                    "radius_pill": theme.border_radius.radius_pill,
                    "radius_circle": theme.border_radius.radius_circle,
                    "custom_radius": theme.border_radius.custom_radius
                },
                
                # Shadows
                "shadows": {
                    "shadow_none": theme.shadows.shadow_none,
                    "shadow_small": theme.shadows.shadow_small,
                    "shadow_medium": theme.shadows.shadow_medium,
                    "shadow_large": theme.shadows.shadow_large,
                    "shadow_xlarge": theme.shadows.shadow_xlarge,
                    "custom_shadows": theme.shadows.custom_shadows
                },
                
                # Animations
                "animations": {
                    "duration_instant": theme.animations.duration_instant,
                    "duration_fast": theme.animations.duration_fast,
                    "duration_normal": theme.animations.duration_normal,
                    "duration_slow": theme.animations.duration_slow,
                    "easing_standard": theme.animations.easing_standard,
                    "easing_accelerate": theme.animations.easing_accelerate,
                    "easing_decelerate": theme.animations.easing_decelerate,
                    "custom_animations": theme.animations.custom_animations
                }
            }
            
            themes_to_export.append(theme_dict)
            
        # Create export data
        export_data = {
            "version": "1.0",
            "timestamp": time.time(),
            "themes": themes_to_export
        }
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "themes_exported",
            "count": len(themes_to_export)
        })
        
        self.logger.debug(f"Exported {len(themes_to_export)} themes")
        return export_data
    
    def add_theme_listener(self, theme_id: str, listener: Callable[[Theme], None]) -> bool:
        """
        Add a listener for a specific theme.
        
        Args:
            theme_id: ID of the theme
            listener: Callback function that will be called when the theme is updated
            
        Returns:
            True if the listener was added, False if theme not found
        """
        if theme_id not in self.themes:
            self.logger.warning(f"Theme {theme_id} not found.")
            return False
            
        if theme_id not in self.theme_listeners:
            self.theme_listeners[theme_id] = []
            
        self.theme_listeners[theme_id].append(listener)
        return True
    
    def add_scope_listener(self, scope: ThemeScope, listener: Callable[[Theme], None]) -> bool:
        """
        Add a listener for a specific theme scope.
        
        Args:
            scope: The theme scope
            listener: Callback function that will be called when a theme in this scope is updated
            
        Returns:
            True if the listener was added
        """
        self.scope_listeners[scope].append(listener)
        return True
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all theme engine events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            return True
            
        return False
    
    def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_data: The event data to dispatch
        """
        # Add source if not present
        if "source" not in event_data:
            event_data["source"] = "ThemeEngine"
            
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = time.time()
            
        # Dispatch to global event listeners
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in theme event listener: {e}")
                
    def _load_themes(self) -> None:
        """Load themes from storage."""
        try:
            storage_file = os.path.join(self.storage_path, "themes.json")
            
            if os.path.exists(storage_file):
                with open(storage_file, "r") as f:
                    themes_data = json.load(f)
                    
                self.import_themes(themes_data)
                self.logger.info(f"Loaded themes from {storage_file}")
                
        except Exception as e:
            self.logger.error(f"Error loading themes: {e}")
            
    def _save_themes(self) -> None:
        """Save themes to storage."""
        try:
            storage_file = os.path.join(self.storage_path, "themes.json")
            
            # Export all themes
            themes_data = self.export_themes()
            
            # Save to file
            with open(storage_file, "w") as f:
                json.dump(themes_data, f, indent=2)
                
            self.logger.debug(f"Saved themes to {storage_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving themes: {e}")
            
    def _create_default_themes(self) -> None:
        """Create default themes."""
        # Create light theme
        light_theme_id = self.create_theme(
            name="Light",
            type=ThemeType.LIGHT,
            scope=ThemeScope.GLOBAL,
            colors=ColorPalette(
                primary="#1976D2",
                secondary="#424242",
                accent="#FF4081",
                background="#FFFFFF",
                surface="#F5F5F5",
                error="#B00020",
                warning="#FB8C00",
                success="#43A047",
                info="#2196F3",
                text_primary="#212121",
                text_secondary="#757575",
                text_hint="#9E9E9E",
                text_disabled="#BDBDBD",
                divider="#EEEEEE"
            ),
            typography=Typography(
                font_family_primary="Roboto, sans-serif",
                font_family_secondary="Roboto Slab, serif",
                font_size_base=16,
                font_size_small=14,
                font_size_medium=16,
                font_size_large=20,
                font_size_xlarge=24,
                font_weight_light=300,
                font_weight_regular=400,
                font_weight_medium=500,
                font_weight_bold=700,
                line_height_tight=1.2,
                line_height_normal=1.5,
                line_height_relaxed=1.8,
                letter_spacing_normal=0
            ),
            spacing=Spacing(
                space_xxsmall=4,
                space_xsmall=8,
                space_small=12,
                space_medium=16,
                space_large=24,
                space_xlarge=32,
                space_xxlarge=48
            ),
            border_radius=BorderRadius(
                radius_none=0,
                radius_small=4,
                radius_medium=8,
                radius_large=16,
                radius_pill=9999,
                radius_circle=50
            ),
            shadows=Shadows(
                shadow_none="none",
                shadow_small="0 2px 4px rgba(0,0,0,0.1)",
                shadow_medium="0 4px 8px rgba(0,0,0,0.12)",
                shadow_large="0 8px 16px rgba(0,0,0,0.14)",
                shadow_xlarge="0 16px 24px rgba(0,0,0,0.16)"
            ),
            animations=Animations(
                duration_instant=0,
                duration_fast=150,
                duration_normal=300,
                duration_slow=500,
                easing_standard="cubic-bezier(0.4, 0.0, 0.2, 1)",
                easing_accelerate="cubic-bezier(0.4, 0.0, 1.0, 1.0)",
                easing_decelerate="cubic-bezier(0.0, 0.0, 0.2, 1.0)"
            )
        )
        
        # Create dark theme
        dark_theme_id = self.create_theme(
            name="Dark",
            type=ThemeType.DARK,
            scope=ThemeScope.GLOBAL,
            colors=ColorPalette(
                primary="#90CAF9",
                secondary="#A1887F",
                accent="#FF80AB",
                background="#121212",
                surface="#1E1E1E",
                error="#CF6679",
                warning="#FFB74D",
                success="#81C784",
                info="#64B5F6",
                text_primary="#FFFFFF",
                text_secondary="#B0BEC5",
                text_hint="#78909C",
                text_disabled="#607D8B",
                divider="#2A2A2A"
            ),
            typography=Typography(
                font_family_primary="Roboto, sans-serif",
                font_family_secondary="Roboto Slab, serif",
                font_size_base=16,
                font_size_small=14,
                font_size_medium=16,
                font_size_large=20,
                font_size_xlarge=24,
                font_weight_light=300,
                font_weight_regular=400,
                font_weight_medium=500,
                font_weight_bold=700,
                line_height_tight=1.2,
                line_height_normal=1.5,
                line_height_relaxed=1.8,
                letter_spacing_normal=0
            ),
            spacing=Spacing(
                space_xxsmall=4,
                space_xsmall=8,
                space_small=12,
                space_medium=16,
                space_large=24,
                space_xlarge=32,
                space_xxlarge=48
            ),
            border_radius=BorderRadius(
                radius_none=0,
                radius_small=4,
                radius_medium=8,
                radius_large=16,
                radius_pill=9999,
                radius_circle=50
            ),
            shadows=Shadows(
                shadow_none="none",
                shadow_small="0 2px 4px rgba(0,0,0,0.2)",
                shadow_medium="0 4px 8px rgba(0,0,0,0.24)",
                shadow_large="0 8px 16px rgba(0,0,0,0.28)",
                shadow_xlarge="0 16px 24px rgba(0,0,0,0.32)"
            ),
            animations=Animations(
                duration_instant=0,
                duration_fast=150,
                duration_normal=300,
                duration_slow=500,
                easing_standard="cubic-bezier(0.4, 0.0, 0.2, 1)",
                easing_accelerate="cubic-bezier(0.4, 0.0, 1.0, 1.0)",
                easing_decelerate="cubic-bezier(0.0, 0.0, 0.2, 1.0)"
            )
        )
        
        # Create high contrast theme
        high_contrast_theme_id = self.create_theme(
            name="High Contrast",
            type=ThemeType.HIGH_CONTRAST,
            scope=ThemeScope.GLOBAL,
            colors=ColorPalette(
                primary="#FFFF00",
                secondary="#FFFFFF",
                accent="#00FFFF",
                background="#000000",
                surface="#000000",
                error="#FF0000",
                warning="#FFFF00",
                success="#00FF00",
                info="#00FFFF",
                text_primary="#FFFFFF",
                text_secondary="#FFFFFF",
                text_hint="#FFFFFF",
                text_disabled="#AAAAAA",
                divider="#FFFFFF"
            ),
            typography=Typography(
                font_family_primary="Roboto, sans-serif",
                font_family_secondary="Roboto Slab, serif",
                font_size_base=18,
                font_size_small=16,
                font_size_medium=18,
                font_size_large=22,
                font_size_xlarge=26,
                font_weight_light=400,
                font_weight_regular=500,
                font_weight_medium=600,
                font_weight_bold=700,
                line_height_tight=1.2,
                line_height_normal=1.5,
                line_height_relaxed=1.8,
                letter_spacing_normal=0.1
            ),
            spacing=Spacing(
                space_xxsmall=4,
                space_xsmall=8,
                space_small=12,
                space_medium=16,
                space_large=24,
                space_xlarge=32,
                space_xxlarge=48
            ),
            border_radius=BorderRadius(
                radius_none=0,
                radius_small=2,
                radius_medium=4,
                radius_large=8,
                radius_pill=9999,
                radius_circle=50
            ),
            shadows=Shadows(
                shadow_none="none",
                shadow_small="0 0 0 2px #FFFFFF",
                shadow_medium="0 0 0 3px #FFFFFF",
                shadow_large="0 0 0 4px #FFFFFF",
                shadow_xlarge="0 0 0 5px #FFFFFF"
            ),
            animations=Animations(
                duration_instant=0,
                duration_fast=100,
                duration_normal=200,
                duration_slow=300,
                easing_standard="linear",
                easing_accelerate="linear",
                easing_decelerate="linear"
            )
        )
        
        # Create industrial theme
        industrial_theme_id = self.create_theme(
            name="Industrial",
            type=ThemeType.CUSTOM,
            scope=ThemeScope.GLOBAL,
            colors=ColorPalette(
                primary="#FF9800",
                secondary="#607D8B",
                accent="#4CAF50",
                background="#263238",
                surface="#37474F",
                error="#F44336",
                warning="#FFC107",
                success="#4CAF50",
                info="#2196F3",
                text_primary="#ECEFF1",
                text_secondary="#B0BEC5",
                text_hint="#78909C",
                text_disabled="#546E7A",
                divider="#455A64",
                custom_colors={
                    "machine_active": "#4CAF50",
                    "machine_idle": "#FFC107",
                    "machine_error": "#F44336",
                    "machine_maintenance": "#2196F3",
                    "energy_high": "#F44336",
                    "energy_medium": "#FFC107",
                    "energy_low": "#4CAF50"
                }
            ),
            typography=Typography(
                font_family_primary="Roboto Mono, monospace",
                font_family_secondary="Roboto, sans-serif",
                font_size_base=14,
                font_size_small=12,
                font_size_medium=14,
                font_size_large=18,
                font_size_xlarge=22,
                font_weight_light=300,
                font_weight_regular=400,
                font_weight_medium=500,
                font_weight_bold=700,
                line_height_tight=1.2,
                line_height_normal=1.5,
                line_height_relaxed=1.8,
                letter_spacing_normal=0
            ),
            spacing=Spacing(
                space_xxsmall=4,
                space_xsmall=8,
                space_small=12,
                space_medium=16,
                space_large=24,
                space_xlarge=32,
                space_xxlarge=48
            ),
            border_radius=BorderRadius(
                radius_none=0,
                radius_small=2,
                radius_medium=4,
                radius_large=8,
                radius_pill=9999,
                radius_circle=50
            ),
            shadows=Shadows(
                shadow_none="none",
                shadow_small="0 2px 4px rgba(0,0,0,0.3)",
                shadow_medium="0 4px 8px rgba(0,0,0,0.36)",
                shadow_large="0 8px 16px rgba(0,0,0,0.42)",
                shadow_xlarge="0 16px 24px rgba(0,0,0,0.48)"
            ),
            animations=Animations(
                duration_instant=0,
                duration_fast=150,
                duration_normal=300,
                duration_slow=500,
                easing_standard="cubic-bezier(0.4, 0.0, 0.2, 1)",
                easing_accelerate="cubic-bezier(0.4, 0.0, 1.0, 1.0)",
                easing_decelerate="cubic-bezier(0.0, 0.0, 0.2, 1.0)"
            )
        )
        
        # Set industrial theme as active
        self.active_theme_id = industrial_theme_id
        
        self.logger.info("Created default themes")

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create theme engine
    theme_engine = ThemeEngine(config={"storage_path": "/tmp/themes"})
    
    # Start the engine
    theme_engine.start()
    
    # Add an event listener
    def on_event(event):
        print(f"Event: {event['event_type']}")
        
    theme_engine.add_event_listener(on_event)
    
    # Get active theme
    active_theme = theme_engine.get_active_theme()
    print(f"Active Theme: {active_theme.name} ({active_theme.type.value})")
    
    # Create a custom theme for manufacturing context
    manufacturing_theme_id = theme_engine.create_theme(
        name="Manufacturing",
        type=ThemeType.CUSTOM,
        scope=ThemeScope.CONTEXT,
        context_id="manufacturing",
        colors=ColorPalette(
            primary="#FF9800",
            secondary="#607D8B",
            accent="#4CAF50",
            background="#263238",
            surface="#37474F",
            error="#F44336",
            warning="#FFC107",
            success="#4CAF50",
            info="#2196F3",
            text_primary="#ECEFF1",
            text_secondary="#B0BEC5",
            text_hint="#78909C",
            text_disabled="#546E7A",
            divider="#455A64",
            custom_colors={
                "machine_active": "#4CAF50",
                "machine_idle": "#FFC107",
                "machine_error": "#F44336",
                "machine_maintenance": "#2196F3"
            }
        ),
        typography=Typography(
            font_family_primary="Roboto Mono, monospace",
            font_family_secondary="Roboto, sans-serif",
            font_size_base=14,
            font_size_small=12,
            font_size_medium=14,
            font_size_large=18,
            font_size_xlarge=22,
            font_weight_light=300,
            font_weight_regular=400,
            font_weight_medium=500,
            font_weight_bold=700,
            line_height_tight=1.2,
            line_height_normal=1.5,
            line_height_relaxed=1.8,
            letter_spacing_normal=0
        ),
        spacing=Spacing(
            space_xxsmall=4,
            space_xsmall=8,
            space_small=12,
            space_medium=16,
            space_large=24,
            space_xlarge=32,
            space_xxlarge=48
        ),
        border_radius=BorderRadius(
            radius_none=0,
            radius_small=2,
            radius_medium=4,
            radius_large=8,
            radius_pill=9999,
            radius_circle=50
        ),
        shadows=Shadows(
            shadow_none="none",
            shadow_small="0 2px 4px rgba(0,0,0,0.3)",
            shadow_medium="0 4px 8px rgba(0,0,0,0.36)",
            shadow_large="0 8px 16px rgba(0,0,0,0.42)",
            shadow_xlarge="0 16px 24px rgba(0,0,0,0.48)"
        ),
        animations=Animations(
            duration_instant=0,
            duration_fast=150,
            duration_normal=300,
            duration_slow=500,
            easing_standard="cubic-bezier(0.4, 0.0, 0.2, 1)",
            easing_accelerate="cubic-bezier(0.4, 0.0, 1.0, 1.0)",
            easing_decelerate="cubic-bezier(0.0, 0.0, 0.2, 1.0)"
        )
    )
    
    # Get theme for manufacturing context
    manufacturing_theme = theme_engine.get_theme_for_context(context_id="manufacturing")
    print(f"Manufacturing Theme: {manufacturing_theme.name} ({manufacturing_theme.type.value})")
    
    # Export themes
    export_data = theme_engine.export_themes()
    print(f"Exported {len(export_data['themes'])} themes")
    
    # Stop the engine
    theme_engine.stop()
