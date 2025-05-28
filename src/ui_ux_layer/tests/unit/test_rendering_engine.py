"""
Unit tests for the Rendering Engine components.

This test suite validates the core functionality of the Rendering Engine,
including theme management, accessibility features, and rendering of UI components.

Author: Manus
"""

import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import modules to test
from core.rendering_engine.rendering_engine import RenderingEngine
from core.rendering_engine.theme_manager import ThemeManager
from core.rendering_engine.accessibility_manager import AccessibilityManager
from core.context_engine.context_engine import ContextEngine


class TestRenderingEngine(unittest.TestCase):
    """Test cases for the Rendering Engine components."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test configuration
        self.test_config = {
            "themes": {
                "industrial": {
                    "name": "Industrial",
                    "description": "Default industrial theme with dark background and high contrast",
                    "colors": {
                        "primary": "#007bff",
                        "secondary": "#6c757d",
                        "success": "#28a745",
                        "danger": "#dc3545",
                        "warning": "#ffc107",
                        "info": "#17a2b8",
                        "light": "#f8f9fa",
                        "dark": "#343a40",
                        "background": "#1e1e1e",
                        "surface": "#2d2d2d",
                        "text": "#ffffff",
                        "text_secondary": "#cccccc"
                    },
                    "typography": {
                        "font_family": "'Roboto', sans-serif",
                        "base_size": "16px",
                        "heading_scale": 1.2,
                        "line_height": 1.5
                    },
                    "spacing": {
                        "base": "8px",
                        "scale": 2
                    },
                    "borders": {
                        "radius": "4px",
                        "width": "1px",
                        "color": "#444444"
                    },
                    "shadows": {
                        "small": "0 2px 4px rgba(0, 0, 0, 0.3)",
                        "medium": "0 4px 8px rgba(0, 0, 0, 0.3)",
                        "large": "0 8px 16px rgba(0, 0, 0, 0.3)"
                    },
                    "animations": {
                        "duration_short": "150ms",
                        "duration_medium": "300ms",
                        "duration_long": "500ms",
                        "easing": "cubic-bezier(0.4, 0.0, 0.2, 1)"
                    }
                },
                "light": {
                    "name": "Light",
                    "description": "Light theme with white background",
                    "colors": {
                        "primary": "#0066cc",
                        "secondary": "#6c757d",
                        "success": "#28a745",
                        "danger": "#dc3545",
                        "warning": "#ffc107",
                        "info": "#17a2b8",
                        "light": "#f8f9fa",
                        "dark": "#343a40",
                        "background": "#ffffff",
                        "surface": "#f5f5f5",
                        "text": "#212529",
                        "text_secondary": "#6c757d"
                    },
                    "typography": {
                        "font_family": "'Roboto', sans-serif",
                        "base_size": "16px",
                        "heading_scale": 1.2,
                        "line_height": 1.5
                    },
                    "spacing": {
                        "base": "8px",
                        "scale": 2
                    },
                    "borders": {
                        "radius": "4px",
                        "width": "1px",
                        "color": "#e0e0e0"
                    },
                    "shadows": {
                        "small": "0 2px 4px rgba(0, 0, 0, 0.1)",
                        "medium": "0 4px 8px rgba(0, 0, 0, 0.1)",
                        "large": "0 8px 16px rgba(0, 0, 0, 0.1)"
                    },
                    "animations": {
                        "duration_short": "150ms",
                        "duration_medium": "300ms",
                        "duration_long": "500ms",
                        "easing": "cubic-bezier(0.4, 0.0, 0.2, 1)"
                    }
                },
                "high_contrast": {
                    "name": "High Contrast",
                    "description": "High contrast theme for accessibility",
                    "colors": {
                        "primary": "#0066ff",
                        "secondary": "#ffffff",
                        "success": "#00cc00",
                        "danger": "#ff0000",
                        "warning": "#ffcc00",
                        "info": "#00ccff",
                        "light": "#ffffff",
                        "dark": "#000000",
                        "background": "#000000",
                        "surface": "#000000",
                        "text": "#ffffff",
                        "text_secondary": "#ffffff"
                    },
                    "typography": {
                        "font_family": "'Roboto', sans-serif",
                        "base_size": "18px",
                        "heading_scale": 1.3,
                        "line_height": 1.6
                    },
                    "spacing": {
                        "base": "10px",
                        "scale": 2
                    },
                    "borders": {
                        "radius": "0px",
                        "width": "2px",
                        "color": "#ffffff"
                    },
                    "shadows": {
                        "small": "none",
                        "medium": "none",
                        "large": "none"
                    },
                    "animations": {
                        "duration_short": "0ms",
                        "duration_medium": "0ms",
                        "duration_long": "0ms",
                        "easing": "linear"
                    }
                }
            },
            "accessibility": {
                "high_contrast_mode": {
                    "enabled": false,
                    "theme": "high_contrast"
                },
                "large_text_mode": {
                    "enabled": false,
                    "scale_factor": 1.25
                },
                "reduced_motion_mode": {
                    "enabled": false
                },
                "screen_reader_support": {
                    "enabled": true,
                    "aria_live_announcements": true
                },
                "keyboard_navigation": {
                    "enabled": true,
                    "focus_visible": true,
                    "tab_index_management": true
                }
            },
            "rendering": {
                "default_theme": "industrial",
                "default_layout": "standard",
                "default_interaction_mode": "desktop",
                "animation_enabled": true,
                "transition_enabled": true,
                "offline_mode_enabled": false,
                "debug_mode_enabled": false,
                "performance_mode": "balanced"
            }
        }
        
        # Create mocks for dependencies
        self.mock_context_engine = MagicMock(spec=ContextEngine)
        self.mock_dom_manager = MagicMock()
        
        # Create instances of components
        self.theme_manager = ThemeManager(
            config=self.test_config["themes"],
            context_engine=self.mock_context_engine,
            default_theme=self.test_config["rendering"]["default_theme"]
        )
        self.accessibility_manager = AccessibilityManager(
            config=self.test_config["accessibility"],
            context_engine=self.mock_context_engine
        )
        self.rendering_engine = RenderingEngine(
            config=self.test_config["rendering"],
            context_engine=self.mock_context_engine,
            theme_manager=self.theme_manager,
            accessibility_manager=self.accessibility_manager,
            dom_manager=self.mock_dom_manager
        )

    # --- RenderingEngine Tests ---

    def test_rendering_engine_initialization(self):
        """Test RenderingEngine initialization."""
        self.assertEqual(self.rendering_engine.config["default_theme"], "industrial")
        self.assertEqual(self.rendering_engine.config["default_layout"], "standard")
        self.assertEqual(self.rendering_engine.config["default_interaction_mode"], "desktop")
        self.assertTrue(self.rendering_engine.config["animation_enabled"])
        self.assertTrue(self.rendering_engine.config["transition_enabled"])
        self.assertFalse(self.rendering_engine.config["offline_mode_enabled"])
        self.assertFalse(self.rendering_engine.config["debug_mode_enabled"])
        self.assertEqual(self.rendering_engine.config["performance_mode"], "balanced")

    def test_register_components(self):
        """Test registering UI components."""
        components = ["capsule_dock", "mission_deck", "swarm_lens", "trust_ribbon"]
        
        self.rendering_engine.register_components(components)
        
        self.assertEqual(self.rendering_engine.registered_components, components)
        self.mock_dom_manager.register_components.assert_called_with(components)

    def test_update_layout(self):
        """Test updating layout."""
        layout_name = "compact"
        layout_settings = {
            "sidebar_visible": False,
            "capsule_dock_position": "bottom",
            "mission_deck_compact": True,
            "swarm_lens_simplified": True,
            "trust_ribbon_position": "top",
            "timeline_view_compact": True,
            "context_panel_overlay": True,
            "action_menu_floating": True,
            "notification_center_overlay": True
        }
        
        self.rendering_engine.update_layout(layout_name, layout_settings)
        
        self.assertEqual(self.rendering_engine.current_layout, layout_name)
        self.assertEqual(self.rendering_engine.layout_settings, layout_settings)
        self.mock_dom_manager.update_layout.assert_called_with(layout_name, layout_settings)
        
        # Test individual layout settings
        self.rendering_engine.set_sidebar_visible(False)
        self.mock_dom_manager.set_sidebar_visible.assert_called_with(False)
        
        self.rendering_engine.set_capsule_dock_position("bottom")
        self.mock_dom_manager.set_capsule_dock_position.assert_called_with("bottom")
        
        self.rendering_engine.set_mission_deck_compact(True)
        self.mock_dom_manager.set_mission_deck_compact.assert_called_with(True)
        
        self.rendering_engine.set_swarm_lens_simplified(True)
        self.mock_dom_manager.set_swarm_lens_simplified.assert_called_with(True)
        
        self.rendering_engine.set_trust_ribbon_position("top")
        self.mock_dom_manager.set_trust_ribbon_position.assert_called_with("top")
        
        self.rendering_engine.set_timeline_view_compact(True)
        self.mock_dom_manager.set_timeline_view_compact.assert_called_with(True)
        
        self.rendering_engine.set_context_panel_overlay(True)
        self.mock_dom_manager.set_context_panel_overlay.assert_called_with(True)
        
        self.rendering_engine.set_action_menu_floating(True)
        self.mock_dom_manager.set_action_menu_floating.assert_called_with(True)
        
        self.rendering_engine.set_notification_center_overlay(True)
        self.mock_dom_manager.set_notification_center_overlay.assert_called_with(True)

    def test_update_interaction_mode(self):
        """Test updating interaction mode."""
        mode_name = "touch"
        mode_settings = {
            "touch_target_size": 44,
            "hover_enabled": False,
            "keyboard_shortcuts_enabled": False,
            "context_menus_enabled": True,
            "drag_drop_enabled": True,
            "tooltip_delay": 0,
            "double_click_enabled": False,
            "scroll_behavior": "momentum"
        }
        
        self.rendering_engine.update_interaction_mode(mode_name, mode_settings)
        
        self.assertEqual(self.rendering_engine.current_interaction_mode, mode_name)
        self.assertEqual(self.rendering_engine.interaction_mode_settings, mode_settings)
        self.mock_dom_manager.update_interaction_mode.assert_called_with(mode_name, mode_settings)
        
        # Test individual interaction mode settings
        self.rendering_engine.set_touch_target_size(44)
        self.mock_dom_manager.set_touch_target_size.assert_called_with(44)
        
        self.rendering_engine.set_hover_enabled(False)
        self.mock_dom_manager.set_hover_enabled.assert_called_with(False)
        
        self.rendering_engine.set_keyboard_shortcuts_enabled(False)
        self.mock_dom_manager.set_keyboard_shortcuts_enabled.assert_called_with(False)
        
        self.rendering_engine.set_context_menus_enabled(True)
        self.mock_dom_manager.set_context_menus_enabled.assert_called_with(True)
        
        self.rendering_engine.set_drag_drop_enabled(True)
        self.mock_dom_manager.set_drag_drop_enabled.assert_called_with(True)
        
        self.rendering_engine.set_tooltip_delay(0)
        self.mock_dom_manager.set_tooltip_delay.assert_called_with(0)
        
        self.rendering_engine.set_double_click_enabled(False)
        self.mock_dom_manager.set_double_click_enabled.assert_called_with(False)
        
        self.rendering_engine.set_scroll_behavior("momentum")
        self.mock_dom_manager.set_scroll_behavior.assert_called_with("momentum")

    def test_create_capsule(self):
        """Test creating a capsule."""
        capsule_id = "capsule_001"
        capsule_type = "agent"
        capsule_type_config = {
            "icon": "agent_icon.svg",
            "default_size": {"width": 320, "height": 180},
            "min_size": {"width": 160, "height": 90},
            "max_size": {"width": 640, "height": 360},
            "default_state": "idle",
            "allowed_states": ["idle", "working", "error", "success"],
            "default_position": "dock",
            "allowed_positions": ["dock", "float", "sidebar", "fullscreen"]
        }
        capsule_config = {"name": "Test Agent", "agent_id": "agent_001"}
        
        self.rendering_engine.create_capsule(capsule_id, capsule_type, capsule_type_config, capsule_config)
        
        self.mock_dom_manager.create_capsule.assert_called_with(
            capsule_id, 
            capsule_type, 
            capsule_type_config, 
            capsule_config
        )

    def test_update_capsule_state(self):
        """Test updating capsule state."""
        capsule_id = "capsule_002"
        state = "working"
        
        self.rendering_engine.update_capsule_state(capsule_id, state)
        
        self.mock_dom_manager.update_capsule_state.assert_called_with(capsule_id, state)

    def test_update_capsule_config(self):
        """Test updating capsule configuration."""
        capsule_id = "capsule_003"
        config = {"name": "Updated Agent", "agent_id": "agent_001"}
        
        self.rendering_engine.update_capsule_config(capsule_id, config)
        
        self.mock_dom_manager.update_capsule_config.assert_called_with(capsule_id, config)

    def test_resize_capsule(self):
        """Test resizing a capsule."""
        capsule_id = "capsule_004"
        size = {"width": 400, "height": 300}
        animate = True
        transition = {"duration": 300, "easing": "ease-out"}
        
        self.rendering_engine.resize_capsule(capsule_id, size, animate, transition)
        
        self.mock_dom_manager.resize_capsule.assert_called_with(capsule_id, size, animate, transition)

    def test_move_capsule(self):
        """Test moving a capsule."""
        capsule_id = "capsule_005"
        position = {"x": 100, "y": 200}
        animate = True
        transition = {"duration": 300, "easing": "ease-out"}
        
        self.rendering_engine.move_capsule(capsule_id, position, animate, transition)
        
        self.mock_dom_manager.move_capsule.assert_called_with(capsule_id, position, animate, transition)

    def test_change_capsule_position_type(self):
        """Test changing capsule position type."""
        capsule_id = "capsule_006"
        position_type = "float"
        animate = True
        transition = {"duration": 300, "easing": "ease-out"}
        
        self.rendering_engine.change_capsule_position_type(capsule_id, position_type, animate, transition)
        
        self.mock_dom_manager.change_capsule_position_type.assert_called_with(
            capsule_id, 
            position_type, 
            animate, 
            transition
        )

    def test_remove_capsule(self):
        """Test removing a capsule."""
        capsule_id = "capsule_007"
        
        self.rendering_engine.remove_capsule(capsule_id)
        
        self.mock_dom_manager.remove_capsule.assert_called_with(capsule_id)

    def test_update_capsule_visibility(self):
        """Test updating capsule visibility."""
        capsule_id = "capsule_008"
        visible = False
        
        self.rendering_engine.update_capsule_visibility(capsule_id, visible)
        
        self.mock_dom_manager.update_capsule_visibility.assert_called_with(capsule_id, visible)

    def test_apply_capsule_effect(self):
        """Test applying an effect to a capsule."""
        capsule_id = "capsule_009"
        effect_type = "highlight"
        effect_config = {"color": "#ffcc00", "duration": 1000}
        
        self.rendering_engine.apply_capsule_effect(capsule_id, effect_type, effect_config)
        
        self.mock_dom_manager.apply_capsule_effect.assert_called_with(capsule_id, effect_type, effect_config)

    def test_register_capsule_event_handler(self):
        """Test registering a capsule event handler."""
        capsule_id = "capsule_010"
        event_type = "click"
        
        self.rendering_engine.register_capsule_event_handler(capsule_id, event_type)
        
        self.mock_dom_manager.register_capsule_event_handler.assert_called_with(capsule_id, event_type)

    def test_unregister_capsule_event_handler(self):
        """Test unregistering a capsule event handler."""
        capsule_id = "capsule_011"
        event_type = "click"
        
        self.rendering_engine.unregister_capsule_event_handler(capsule_id, event_type)
        
        self.mock_dom_manager.unregister_capsule_event_handler.assert_called_with(capsule_id, event_type)

    def test_set_offline_mode(self):
        """Test setting offline mode."""
        offline = True
        
        self.rendering_engine.set_offline_mode(offline)
        
        self.assertTrue(self.rendering_engine.offline_mode)
        self.mock_dom_manager.set_offline_mode.assert_called_with(offline)

    def test_set_debug_mode(self):
        """Test setting debug mode."""
        debug = True
        
        self.rendering_engine.set_debug_mode(debug)
        
        self.assertTrue(self.rendering_engine.debug_mode)
        self.mock_dom_manager.set_debug_mode.assert_called_with(debug)

    def test_set_performance_mode(self):
        """Test setting performance mode."""
        mode = "high_performance"
        
        self.rendering_engine.set_performance_mode(mode)
        
        self.assertEqual(self.rendering_engine.performance_mode, mode)
        self.mock_dom_manager.set_performance_mode.assert_called_with(mode)

    def test_set_reduced_motion(self):
        """Test setting reduced motion."""
        reduced_motion = True
        
        self.rendering_engine.set_reduced_motion(reduced_motion)
        
        self.assertTrue(self.rendering_engine.reduced_motion)
        self.mock_dom_manager.set_reduced_motion.assert_called_with(reduced_motion)

    # --- ThemeManager Tests ---

    def test_theme_manager_initialization(self):
        """Test ThemeManager initialization."""
        self.assertEqual(self.theme_manager.current_theme, "industrial")
        self.assertEqual(len(self.theme_manager.themes), 3)
        self.assertFalse(self.theme_manager.high_contrast)
        self.assertFalse(self.theme_manager.large_text)

    def test_set_theme(self):
        """Test setting theme."""
        theme_name = "light"
        
        self.theme_manager.set_theme(theme_name)
        
        self.assertEqual(self.theme_manager.current_theme, theme_name)
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "theme_change",
            "data": {
                "theme": theme_name,
                "theme_data": self.test_config["themes"][theme_name]
            }
        })
        
        # Test invalid theme
        with self.assertRaises(ValueError):
            self.theme_manager.set_theme("invalid_theme")

    def test_get_current_theme(self):
        """Test getting current theme."""
        self.theme_manager.set_theme("light")
        
        theme = self.theme_manager.get_current_theme()
        
        self.assertEqual(theme, "light")

    def test_get_theme_data(self):
        """Test getting theme data."""
        theme_data = self.theme_manager.get_theme_data("industrial")
        
        self.assertEqual(theme_data["name"], "Industrial")
        self.assertEqual(theme_data["colors"]["primary"], "#007bff")
        
        # Test invalid theme
        with self.assertRaises(ValueError):
            self.theme_manager.get_theme_data("invalid_theme")

    def test_get_current_theme_data(self):
        """Test getting current theme data."""
        self.theme_manager.set_theme("light")
        
        theme_data = self.theme_manager.get_current_theme_data()
        
        self.assertEqual(theme_data["name"], "Light")
        self.assertEqual(theme_data["colors"]["primary"], "#0066cc")

    def test_set_high_contrast(self):
        """Test setting high contrast mode."""
        high_contrast = True
        
        self.theme_manager.set_high_contrast(high_contrast)
        
        self.assertTrue(self.theme_manager.high_contrast)
        self.assertEqual(self.theme_manager.current_theme, "high_contrast")
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "theme_change",
            "data": {
                "theme": "high_contrast",
                "theme_data": self.test_config["themes"]["high_contrast"]
            }
        })
        
        # Test disabling high contrast (should revert to previous theme)
        self.theme_manager.previous_theme = "industrial"
        self.theme_manager.set_high_contrast(False)
        
        self.assertFalse(self.theme_manager.high_contrast)
        self.assertEqual(self.theme_manager.current_theme, "industrial")

    def test_set_large_text(self):
        """Test setting large text mode."""
        large_text = True
        
        self.theme_manager.set_large_text(large_text)
        
        self.assertTrue(self.theme_manager.large_text)
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "typography_change",
            "data": {
                "large_text": large_text,
                "scale_factor": 1.25
            }
        })

    def test_get_css_variables(self):
        """Test getting CSS variables for a theme."""
        css_vars = self.theme_manager.get_css_variables("industrial")
        
        self.assertIn("--color-primary", css_vars)
        self.assertEqual(css_vars["--color-primary"], "#007bff")
        self.assertIn("--font-family", css_vars)
        self.assertEqual(css_vars["--font-family"], "'Roboto', sans-serif")
        
        # Test with large text
        self.theme_manager.set_large_text(True)
        css_vars = self.theme_manager.get_css_variables("industrial")
        
        self.assertIn("--font-size-base", css_vars)
        # Base size should be scaled up
        self.assertNotEqual(css_vars["--font-size-base"], "16px")

    def test_add_custom_theme(self):
        """Test adding a custom theme."""
        theme_name = "custom"
        theme_data = {
            "name": "Custom",
            "description": "Custom theme for testing",
            "colors": {
                "primary": "#ff5500",
                "secondary": "#6c757d",
                "success": "#28a745",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8",
                "light": "#f8f9fa",
                "dark": "#343a40",
                "background": "#f0f0f0",
                "surface": "#ffffff",
                "text": "#333333",
                "text_secondary": "#666666"
            },
            "typography": {
                "font_family": "'Open Sans', sans-serif",
                "base_size": "16px",
                "heading_scale": 1.2,
                "line_height": 1.5
            },
            "spacing": {
                "base": "8px",
                "scale": 2
            },
            "borders": {
                "radius": "8px",
                "width": "1px",
                "color": "#dddddd"
            },
            "shadows": {
                "small": "0 2px 4px rgba(0, 0, 0, 0.1)",
                "medium": "0 4px 8px rgba(0, 0, 0, 0.1)",
                "large": "0 8px 16px rgba(0, 0, 0, 0.1)"
            },
            "animations": {
                "duration_short": "150ms",
                "duration_medium": "300ms",
                "duration_long": "500ms",
                "easing": "cubic-bezier(0.4, 0.0, 0.2, 1)"
            }
        }
        
        self.theme_manager.add_custom_theme(theme_name, theme_data)
        
        self.assertIn(theme_name, self.theme_manager.themes)
        self.assertEqual(self.theme_manager.themes[theme_name], theme_data)
        
        # Test setting the custom theme
        self.theme_manager.set_theme(theme_name)
        self.assertEqual(self.theme_manager.current_theme, theme_name)

    # --- AccessibilityManager Tests ---

    def test_accessibility_manager_initialization(self):
        """Test AccessibilityManager initialization."""
        self.assertFalse(self.accessibility_manager.config["high_contrast_mode"]["enabled"])
        self.assertFalse(self.accessibility_manager.config["large_text_mode"]["enabled"])
        self.assertFalse(self.accessibility_manager.config["reduced_motion_mode"]["enabled"])
        self.assertTrue(self.accessibility_manager.config["screen_reader_support"]["enabled"])
        self.assertTrue(self.accessibility_manager.config["keyboard_navigation"]["enabled"])

    def test_set_high_contrast_mode(self):
        """Test setting high contrast mode."""
        enabled = True
        
        self.accessibility_manager.set_high_contrast_mode(enabled)
        
        self.assertTrue(self.accessibility_manager.config["high_contrast_mode"]["enabled"])
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "accessibility_change",
            "data": {
                "high_contrast_mode": {
                    "enabled": enabled,
                    "theme": "high_contrast"
                }
            }
        })

    def test_set_large_text_mode(self):
        """Test setting large text mode."""
        enabled = True
        scale_factor = 1.5
        
        self.accessibility_manager.set_large_text_mode(enabled, scale_factor)
        
        self.assertTrue(self.accessibility_manager.config["large_text_mode"]["enabled"])
        self.assertEqual(self.accessibility_manager.config["large_text_mode"]["scale_factor"], scale_factor)
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "accessibility_change",
            "data": {
                "large_text_mode": {
                    "enabled": enabled,
                    "scale_factor": scale_factor
                }
            }
        })

    def test_set_reduced_motion_mode(self):
        """Test setting reduced motion mode."""
        enabled = True
        
        self.accessibility_manager.set_reduced_motion_mode(enabled)
        
        self.assertTrue(self.accessibility_manager.config["reduced_motion_mode"]["enabled"])
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "accessibility_change",
            "data": {
                "reduced_motion_mode": {
                    "enabled": enabled
                }
            }
        })

    def test_set_screen_reader_support(self):
        """Test setting screen reader support."""
        enabled = False
        aria_live_announcements = False
        
        self.accessibility_manager.set_screen_reader_support(enabled, aria_live_announcements)
        
        self.assertFalse(self.accessibility_manager.config["screen_reader_support"]["enabled"])
        self.assertFalse(self.accessibility_manager.config["screen_reader_support"]["aria_live_announcements"])
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "accessibility_change",
            "data": {
                "screen_reader_support": {
                    "enabled": enabled,
                    "aria_live_announcements": aria_live_announcements
                }
            }
        })

    def test_set_keyboard_navigation(self):
        """Test setting keyboard navigation."""
        enabled = False
        focus_visible = False
        tab_index_management = False
        
        self.accessibility_manager.set_keyboard_navigation(enabled, focus_visible, tab_index_management)
        
        self.assertFalse(self.accessibility_manager.config["keyboard_navigation"]["enabled"])
        self.assertFalse(self.accessibility_manager.config["keyboard_navigation"]["focus_visible"])
        self.assertFalse(self.accessibility_manager.config["keyboard_navigation"]["tab_index_management"])
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "accessibility_change",
            "data": {
                "keyboard_navigation": {
                    "enabled": enabled,
                    "focus_visible": focus_visible,
                    "tab_index_management": tab_index_management
                }
            }
        })

    def test_get_accessibility_settings(self):
        """Test getting accessibility settings."""
        settings = self.accessibility_manager.get_accessibility_settings()
        
        self.assertEqual(settings, self.accessibility_manager.config)

    def test_announce_screen_reader_message(self):
        """Test announcing a message for screen readers."""
        message = "Test announcement"
        priority = "assertive"
        
        self.accessibility_manager.announce_screen_reader_message(message, priority)
        
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "screen_reader_announcement",
            "data": {
                "message": message,
                "priority": priority
            }
        })

    def test_apply_accessibility_settings(self):
        """Test applying all accessibility settings at once."""
        settings = {
            "high_contrast_mode": {
                "enabled": True,
                "theme": "high_contrast"
            },
            "large_text_mode": {
                "enabled": True,
                "scale_factor": 1.5
            },
            "reduced_motion_mode": {
                "enabled": True
            },
            "screen_reader_support": {
                "enabled": True,
                "aria_live_announcements": True
            },
            "keyboard_navigation": {
                "enabled": True,
                "focus_visible": True,
                "tab_index_management": True
            }
        }
        
        self.accessibility_manager.apply_accessibility_settings(settings)
        
        self.assertEqual(self.accessibility_manager.config, settings)
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "accessibility_change",
            "data": settings
        })


if __name__ == '__main__':
    unittest.main()
"""
