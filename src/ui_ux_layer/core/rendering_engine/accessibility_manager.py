"""
Accessibility Manager for the Rendering Engine

This module manages accessibility features for the Industriverse UI/UX Layer.
It handles screen reader support, keyboard navigation, color contrast,
text scaling, and other accessibility enhancements to ensure the UI is
usable by people with diverse abilities and needs.

The Accessibility Manager:
1. Manages screen reader compatibility
2. Handles keyboard navigation and focus management
3. Ensures proper color contrast and readability
4. Provides text scaling and zoom capabilities
5. Implements motion reduction for animations
6. Supports alternative input methods
7. Ensures WCAG 2.1 AA compliance

Author: Manus
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

# Local imports
from ..context_engine.context_engine import ContextEngine
from .theme_manager import ThemeManager

# Configure logging
logger = logging.getLogger(__name__)

class AccessibilityPreference(Enum):
    """Enumeration of accessibility preferences."""
    SCREEN_READER = "screen_reader"
    KEYBOARD_NAVIGATION = "keyboard_navigation"
    HIGH_CONTRAST = "high_contrast"
    LARGE_TEXT = "large_text"
    REDUCED_MOTION = "reduced_motion"
    REDUCED_TRANSPARENCY = "reduced_transparency"
    AUDIO_DESCRIPTIONS = "audio_descriptions"
    CAPTIONS = "captions"

class AccessibilityManager:
    """
    Manages accessibility features for the Industriverse UI/UX Layer.
    
    This class is responsible for ensuring the UI is accessible to users
    with diverse abilities and needs, in compliance with WCAG 2.1 AA standards.
    """
    
    def __init__(
        self,
        context_engine: ContextEngine,
        theme_manager: ThemeManager,
        config: Dict = None
    ):
        """
        Initialize the Accessibility Manager.
        
        Args:
            context_engine: The Context Engine instance
            theme_manager: The Theme Manager instance
            config: Optional configuration dictionary
        """
        self.context_engine = context_engine
        self.theme_manager = theme_manager
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "preferences_file": "accessibility_preferences.json",
            "preferences_directory": os.path.join(os.path.dirname(__file__), "preferences"),
            "default_preferences": {
                AccessibilityPreference.SCREEN_READER.value: False,
                AccessibilityPreference.KEYBOARD_NAVIGATION.value: True,
                AccessibilityPreference.HIGH_CONTRAST.value: False,
                AccessibilityPreference.LARGE_TEXT.value: False,
                AccessibilityPreference.REDUCED_MOTION.value: False,
                AccessibilityPreference.REDUCED_TRANSPARENCY.value: False,
                AccessibilityPreference.AUDIO_DESCRIPTIONS.value: False,
                AccessibilityPreference.CAPTIONS.value: True
            },
            "text_scale_factors": {
                "normal": 1.0,
                "large": 1.25,
                "x_large": 1.5,
                "xx_large": 1.75
            },
            "focus_outline_width": "3px",
            "focus_outline_color": "#2196F3",
            "focus_outline_style": "solid",
            "keyboard_shortcut_help_enabled": True,
            "auto_detect_preferences": True,
            "announce_page_changes": True,
            "announce_notifications": True,
            "skip_to_content_enabled": True,
            "aria_live_announcements_enabled": True,
            "aria_live_announcements_delay": 500,  # milliseconds
            "tab_index_management_enabled": True
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Ensure preferences directory exists
        os.makedirs(self.config["preferences_directory"], exist_ok=True)
        
        # Current preferences
        self.preferences = self.config["default_preferences"].copy()
        
        # Registered event handlers
        self.event_handlers = {
            "preference_change": [],
            "focus_change": [],
            "announcement": []
        }
        
        # Focus management
        self.focus_history = []
        self.current_focus = None
        
        # Announcement queue
        self.announcement_queue = []
        
        # Load user preferences if available
        self._load_user_preferences()
        
        # Register as context listener
        self.context_engine.register_context_listener(self._handle_context_change)
        
        # Apply initial preferences
        self._apply_preferences()
        
        logger.info("Accessibility Manager initialized")
    
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
    
    def _load_user_preferences(self) -> None:
        """Load user accessibility preferences."""
        try:
            file_path = os.path.join(
                self.config["preferences_directory"],
                self.config["preferences_file"]
            )
            
            if not os.path.exists(file_path):
                logger.debug("User accessibility preferences file not found, using defaults")
                return
            
            with open(file_path, "r") as f:
                preferences = json.load(f)
            
            # Update preferences with loaded values
            for key, value in preferences.items():
                if key in self.preferences:
                    self.preferences[key] = value
            
            logger.info("Loaded user accessibility preferences")
        except Exception as e:
            logger.error(f"Error loading user accessibility preferences: {str(e)}")
    
    def _save_user_preferences(self) -> None:
        """Save user accessibility preferences."""
        try:
            file_path = os.path.join(
                self.config["preferences_directory"],
                self.config["preferences_file"]
            )
            
            with open(file_path, "w") as f:
                json.dump(self.preferences, f, indent=2)
            
            logger.debug("Saved user accessibility preferences")
        except Exception as e:
            logger.error(f"Error saving user accessibility preferences: {str(e)}")
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        context_type = event.get("type")
        
        # Handle user preference context changes
        if context_type == "user_preferences":
            preferences = event.get("data", {})
            
            if "accessibility" in preferences:
                accessibility_prefs = preferences["accessibility"]
                self.update_preferences(accessibility_prefs)
        
        # Handle device capability context changes
        elif context_type == "device_capabilities":
            capabilities = event.get("data", {})
            
            if "accessibility_features" in capabilities and self.config["auto_detect_preferences"]:
                self._adapt_to_device_capabilities(capabilities["accessibility_features"])
    
    def _adapt_to_device_capabilities(self, capabilities: Dict) -> None:
        """
        Adapt accessibility settings to device capabilities.
        
        Args:
            capabilities: Device accessibility capabilities
        """
        updates = {}
        
        # Check for screen reader
        if "screen_reader_active" in capabilities:
            updates[AccessibilityPreference.SCREEN_READER.value] = capabilities["screen_reader_active"]
        
        # Check for reduced motion
        if "prefers_reduced_motion" in capabilities:
            updates[AccessibilityPreference.REDUCED_MOTION.value] = capabilities["prefers_reduced_motion"]
        
        # Check for high contrast
        if "prefers_high_contrast" in capabilities:
            updates[AccessibilityPreference.HIGH_CONTRAST.value] = capabilities["prefers_high_contrast"]
        
        # Check for large text
        if "prefers_large_text" in capabilities:
            updates[AccessibilityPreference.LARGE_TEXT.value] = capabilities["prefers_large_text"]
        
        # Apply updates if any
        if updates:
            self.update_preferences(updates)
            logger.info(f"Adapted accessibility preferences to device capabilities: {updates}")
    
    def _apply_preferences(self) -> None:
        """Apply current accessibility preferences."""
        # Apply high contrast theme if enabled
        if self.preferences[AccessibilityPreference.HIGH_CONTRAST.value]:
            self.theme_manager.set_theme_mode("high_contrast")
        
        # Trigger preference change event
        self._trigger_event("preference_change", {
            "preferences": self.preferences
        })
        
        logger.debug("Applied accessibility preferences")
    
    def update_preferences(self, preferences: Dict) -> None:
        """
        Update accessibility preferences.
        
        Args:
            preferences: Dictionary of preference updates
        """
        changes = {}
        
        for key, value in preferences.items():
            if key in self.preferences and self.preferences[key] != value:
                self.preferences[key] = value
                changes[key] = value
        
        if changes:
            # Apply updated preferences
            self._apply_preferences()
            
            # Save user preferences
            self._save_user_preferences()
            
            logger.info(f"Updated accessibility preferences: {changes}")
    
    def get_preferences(self) -> Dict:
        """
        Get current accessibility preferences.
        
        Returns:
            Dictionary of current preferences
        """
        return self.preferences.copy()
    
    def is_preference_enabled(self, preference: str) -> bool:
        """
        Check if a specific accessibility preference is enabled.
        
        Args:
            preference: Preference identifier
            
        Returns:
            Boolean indicating if preference is enabled
        """
        return self.preferences.get(preference, False)
    
    def get_text_scale_factor(self) -> float:
        """
        Get the current text scale factor based on preferences.
        
        Returns:
            Text scale factor (float)
        """
        if self.preferences[AccessibilityPreference.LARGE_TEXT.value]:
            return self.config["text_scale_factors"]["large"]
        else:
            return self.config["text_scale_factors"]["normal"]
    
    def get_focus_outline_style(self) -> Dict:
        """
        Get the focus outline style based on preferences.
        
        Returns:
            Dictionary with focus outline style properties
        """
        return {
            "width": self.config["focus_outline_width"],
            "color": self.config["focus_outline_color"],
            "style": self.config["focus_outline_style"]
        }
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler.
        
        Args:
            event_type: Event type identifier
            handler: Event handler function
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            logger.debug(f"Registered {event_type} event handler")
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def unregister_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Unregister an event handler.
        
        Args:
            event_type: Event type identifier
            handler: Event handler function
        """
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.debug(f"Unregistered {event_type} event handler")
    
    def _trigger_event(self, event_type: str, data: Dict) -> None:
        """
        Trigger an event.
        
        Args:
            event_type: Event type identifier
            data: Event data
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in {event_type} event handler: {str(e)}")
    
    def announce(self, message: str, priority: str = "polite") -> None:
        """
        Announce a message to screen readers.
        
        Args:
            message: Message to announce
            priority: Announcement priority ("polite" or "assertive")
        """
        if not self.config["aria_live_announcements_enabled"]:
            return
        
        # Add to announcement queue
        self.announcement_queue.append({
            "message": message,
            "priority": priority
        })
        
        # Trigger announcement event
        self._trigger_event("announcement", {
            "message": message,
            "priority": priority
        })
        
        logger.debug(f"Announced: {message} (priority: {priority})")
    
    def announce_page_change(self, page_title: str, page_description: Optional[str] = None) -> None:
        """
        Announce a page change to screen readers.
        
        Args:
            page_title: Page title
            page_description: Optional page description
        """
        if not self.config["announce_page_changes"]:
            return
        
        message = f"Page changed to {page_title}"
        if page_description:
            message += f". {page_description}"
        
        self.announce(message, "assertive")
    
    def announce_notification(self, notification: Dict) -> None:
        """
        Announce a notification to screen readers.
        
        Args:
            notification: Notification data
        """
        if not self.config["announce_notifications"]:
            return
        
        message = notification.get("message", "")
        if message:
            self.announce(message, "polite")
    
    def set_focus(self, element_id: str) -> None:
        """
        Set focus to a specific element.
        
        Args:
            element_id: Element identifier
        """
        # Add current focus to history
        if self.current_focus:
            self.focus_history.append(self.current_focus)
            # Limit history size
            if len(self.focus_history) > 10:
                self.focus_history.pop(0)
        
        # Update current focus
        self.current_focus = element_id
        
        # Trigger focus change event
        self._trigger_event("focus_change", {
            "element_id": element_id,
            "previous": self.focus_history[-1] if self.focus_history else None
        })
        
        logger.debug(f"Focus set to element: {element_id}")
    
    def restore_previous_focus(self) -> Optional[str]:
        """
        Restore focus to the previous element.
        
        Returns:
            Previous element identifier or None if history is empty
        """
        if not self.focus_history:
            return None
        
        # Get previous focus
        previous_focus = self.focus_history.pop()
        
        # Update current focus
        self.current_focus = previous_focus
        
        # Trigger focus change event
        self._trigger_event("focus_change", {
            "element_id": previous_focus,
            "previous": self.focus_history[-1] if self.focus_history else None
        })
        
        logger.debug(f"Focus restored to element: {previous_focus}")
        return previous_focus
    
    def get_current_focus(self) -> Optional[str]:
        """
        Get the currently focused element.
        
        Returns:
            Current element identifier or None if no focus
        """
        return self.current_focus
    
    def clear_focus_history(self) -> None:
        """Clear focus history."""
        self.focus_history = []
        logger.debug("Focus history cleared")
    
    def get_skip_links(self) -> List[Dict]:
        """
        Get skip navigation links.
        
        Returns:
            List of skip link definitions
        """
        if not self.config["skip_to_content_enabled"]:
            return []
        
        return [
            {
                "id": "skip-to-main",
                "target": "main-content",
                "label": "Skip to main content"
            },
            {
                "id": "skip-to-nav",
                "target": "main-navigation",
                "label": "Skip to navigation"
            }
        ]
    
    def get_keyboard_shortcuts(self) -> Dict:
        """
        Get keyboard shortcuts.
        
        Returns:
            Dictionary of keyboard shortcuts
        """
        return {
            "navigation": {
                "?": "Show keyboard shortcuts",
                "g h": "Go to home",
                "g d": "Go to dashboard",
                "g s": "Go to settings",
                "g p": "Go to profile",
                "g m": "Go to messages",
                "g n": "Go to notifications"
            },
            "actions": {
                "n": "New item",
                "e": "Edit current item",
                "d": "Delete current item",
                "s": "Save current item",
                "c": "Cancel current action",
                "r": "Refresh current view",
                "f": "Search"
            },
            "accessibility": {
                "alt+1": "Toggle high contrast",
                "alt+2": "Toggle large text",
                "alt+3": "Toggle reduced motion",
                "alt+4": "Toggle screen reader announcements",
                "alt+0": "Reset accessibility preferences"
            }
        }
    
    def get_accessibility_css(self) -> str:
        """
        Get accessibility-related CSS.
        
        Returns:
            CSS string with accessibility styles
        """
        css = []
        
        # Skip links
        css.append("""
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #000000;
    color: #ffffff;
    padding: 8px;
    z-index: 100;
    transition: top 0.2s;
}

.skip-link:focus {
    top: 0;
}
        """)
        
        # Focus styles
        focus_style = self.get_focus_outline_style()
        css.append(f"""
:focus {{
    outline: {focus_style["width"]} {focus_style["style"]} {focus_style["color"]};
    outline-offset: 2px;
}}

:focus:not(:focus-visible) {{
    outline: none;
}}

:focus-visible {{
    outline: {focus_style["width"]} {focus_style["style"]} {focus_style["color"]};
    outline-offset: 2px;
}}
        """)
        
        # Large text
        if self.preferences[AccessibilityPreference.LARGE_TEXT.value]:
            text_scale = self.get_text_scale_factor()
            css.append(f"""
html {{
    font-size: {text_scale * 100}%;
}}
            """)
        
        # Reduced motion
        if self.preferences[AccessibilityPreference.REDUCED_MOTION.value]:
            css.append("""
*, *::before, *::after {
    animation-duration: 0.001s !important;
    transition-duration: 0.001s !important;
}
            """)
        
        # Reduced transparency
        if self.preferences[AccessibilityPreference.REDUCED_TRANSPARENCY.value]:
            css.append("""
.glass-effect, .blur-background, .transparent-element {
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    background-color: var(--color-background-primary) !important;
    opacity: 1 !important;
}
            """)
        
        return "\n".join(css)
    
    def get_aria_live_regions(self) -> List[Dict]:
        """
        Get ARIA live regions configuration.
        
        Returns:
            List of ARIA live region definitions
        """
        if not self.config["aria_live_announcements_enabled"]:
            return []
        
        return [
            {
                "id": "aria-live-polite",
                "aria_live": "polite",
                "aria_atomic": "true",
                "role": "status"
            },
            {
                "id": "aria-live-assertive",
                "aria_live": "assertive",
                "aria_atomic": "true",
                "role": "alert"
            }
        ]
    
    def validate_accessibility(self, html_content: str) -> Dict:
        """
        Validate HTML content for accessibility issues.
        
        Args:
            html_content: HTML content to validate
            
        Returns:
            Dictionary with validation results
        """
        # This is a simplified validation that checks for common issues
        # In a production environment, this would use a more comprehensive validator
        
        issues = []
        warnings = []
        
        # Check for missing alt attributes on images
        if "<img " in html_content and not 'alt="' in html_content:
            issues.append({
                "type": "missing_alt",
                "description": "Image missing alt attribute",
                "impact": "critical",
                "wcag": "1.1.1"
            })
        
        # Check for missing form labels
        if "<input " in html_content and not "<label" in html_content:
            issues.append({
                "type": "missing_label",
                "description": "Form control missing label",
                "impact": "critical",
                "wcag": "3.3.2"
            })
        
        # Check for missing heading structure
        if not "<h1" in html_content:
            issues.append({
                "type": "missing_h1",
                "description": "Page missing main heading (h1)",
                "impact": "serious",
                "wcag": "1.3.1"
            })
        
        # Check for missing language attribute
        if not 'lang="' in html_content:
            issues.append({
                "type": "missing_lang",
                "description": "HTML element missing lang attribute",
                "impact": "serious",
                "wcag": "3.1.1"
            })
        
        # Check for potential keyboard traps
        if "onkeydown=" in html_content and "preventDefault" in html_content:
            warnings.append({
                "type": "potential_keyboard_trap",
                "description": "Potential keyboard trap detected",
                "impact": "critical",
                "wcag": "2.1.2"
            })
        
        return {
            "issues": issues,
            "warnings": warnings,
            "pass": len(issues) == 0,
            "total_issues": len(issues),
            "total_warnings": len(warnings)
        }
    
    def shutdown(self) -> None:
        """Shutdown the Accessibility Manager."""
        logger.info("Shutting down Accessibility Manager")
        
        # Save user preferences
        self._save_user_preferences()
