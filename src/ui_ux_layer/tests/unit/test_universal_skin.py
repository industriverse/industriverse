"""
Unit tests for the Universal Skin Shell and related components.

This test suite validates the core functionality of the Universal Skin Shell,
which is the central component of the UI/UX Layer's adaptive interface system.
Tests cover device adaptation, role-based views, layout management, and
interaction modes.

Author: Manus
"""

import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import modules to test
from core.universal_skin.universal_skin_shell import UniversalSkinShell
from core.universal_skin.device_adapter import DeviceAdapter
from core.universal_skin.role_view_manager import RoleViewManager
from core.universal_skin.adaptive_layout_manager import AdaptiveLayoutManager
from core.universal_skin.interaction_mode_manager import InteractionModeManager
from core.context_engine.context_engine import ContextEngine
from core.rendering_engine.rendering_engine import RenderingEngine
from core.rendering_engine.theme_manager import ThemeManager


class TestUniversalSkinShell(unittest.TestCase):
    """Test cases for the Universal Skin Shell."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mocks for dependencies
        self.mock_device_adapter = MagicMock(spec=DeviceAdapter)
        self.mock_role_view_manager = MagicMock(spec=RoleViewManager)
        self.mock_adaptive_layout_manager = MagicMock(spec=AdaptiveLayoutManager)
        self.mock_interaction_mode_manager = MagicMock(spec=InteractionModeManager)
        self.mock_context_engine = MagicMock(spec=ContextEngine)
        self.mock_rendering_engine = MagicMock(spec=RenderingEngine)
        self.mock_theme_manager = MagicMock(spec=ThemeManager)
        
        # Configure mock device adapter
        self.mock_device_adapter.get_device_info.return_value = {
            "type": "desktop",
            "screen": {
                "width": 1920,
                "height": 1080,
                "pixel_ratio": 1.0
            },
            "input": {
                "touch": False,
                "keyboard": True,
                "mouse": True
            },
            "network": {
                "type": "wifi",
                "connected": True
            },
            "battery": None
        }
        
        # Create test configuration
        self.test_config = {
            "default_theme": "industrial",
            "default_role": "process_handler",
            "default_layout": "standard",
            "default_interaction_mode": "desktop",
            "enable_animations": True,
            "enable_transitions": True,
            "enable_accessibility": True,
            "enable_offline_mode": True,
            "enable_responsive_layout": True,
            "enable_role_based_views": True,
            "enable_context_awareness": True,
            "enable_device_adaptation": True
        }
        
        # Create instance of UniversalSkinShell
        self.universal_skin = UniversalSkinShell(
            device_adapter=self.mock_device_adapter,
            role_view_manager=self.mock_role_view_manager,
            adaptive_layout_manager=self.mock_adaptive_layout_manager,
            interaction_mode_manager=self.mock_interaction_mode_manager,
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            theme_manager=self.mock_theme_manager,
            config=self.test_config
        )

    def test_initialization(self):
        """Test that UniversalSkinShell initializes correctly."""
        # Verify that the UniversalSkinShell was initialized with the correct configuration
        self.assertEqual(self.universal_skin.config["default_theme"], "industrial")
        self.assertEqual(self.universal_skin.config["default_role"], "process_handler")
        self.assertEqual(self.universal_skin.config["default_layout"], "standard")
        self.assertEqual(self.universal_skin.config["default_interaction_mode"], "desktop")
        
        # Verify that the device adapter was called to get device info
        self.mock_device_adapter.get_device_info.assert_called_once()
        
        # Verify that the role view manager was initialized with the default role
        self.mock_role_view_manager.set_current_role.assert_called_once_with("process_handler")
        
        # Verify that the adaptive layout manager was initialized with the default layout
        self.mock_adaptive_layout_manager.set_layout.assert_called_once_with("standard")
        
        # Verify that the interaction mode manager was initialized with the default mode
        self.mock_interaction_mode_manager.set_mode.assert_called_once_with("desktop")
        
        # Verify that the theme manager was initialized with the default theme
        self.mock_theme_manager.set_theme.assert_called_once_with("industrial")

    def test_set_theme(self):
        """Test setting the theme."""
        # Set a new theme
        self.universal_skin.set_theme("dark")
        
        # Verify that the theme manager was called with the new theme
        self.mock_theme_manager.set_theme.assert_called_with("dark")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "theme_change",
            "data": {
                "theme": "dark"
            }
        })

    def test_set_role(self):
        """Test setting the user role."""
        # Set a new role
        self.universal_skin.set_role("domain_expert")
        
        # Verify that the role view manager was called with the new role
        self.mock_role_view_manager.set_current_role.assert_called_with("domain_expert")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "role_change",
            "data": {
                "role": "domain_expert"
            }
        })

    def test_set_layout(self):
        """Test setting the layout."""
        # Set a new layout
        self.universal_skin.set_layout("compact")
        
        # Verify that the adaptive layout manager was called with the new layout
        self.mock_adaptive_layout_manager.set_layout.assert_called_with("compact")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "layout_change",
            "data": {
                "layout": "compact"
            }
        })

    def test_set_interaction_mode(self):
        """Test setting the interaction mode."""
        # Set a new interaction mode
        self.universal_skin.set_interaction_mode("touch")
        
        # Verify that the interaction mode manager was called with the new mode
        self.mock_interaction_mode_manager.set_mode.assert_called_with("touch")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "interaction_mode_change",
            "data": {
                "mode": "touch"
            }
        })

    def test_register_components(self):
        """Test registering UI components."""
        # Create mock components
        components = ["capsule_dock", "mission_deck", "swarm_lens", "trust_ribbon"]
        
        # Register components
        self.universal_skin.register_components(components)
        
        # Verify that the adaptive layout manager was called to register components
        self.mock_adaptive_layout_manager.register_components.assert_called_with(components)

    def test_handle_context_change(self):
        """Test handling context changes."""
        # Create a mock context change event
        context_event = {
            "type": "device_change",
            "data": {
                "type": "tablet",
                "orientation": "landscape"
            }
        }
        
        # Call the context change handler
        self.universal_skin._handle_context_change(context_event)
        
        # Verify that the interaction mode manager was updated
        self.mock_interaction_mode_manager.set_mode.assert_called_with("touch")
        
        # Verify that the adaptive layout manager was updated
        self.mock_adaptive_layout_manager.set_device_type.assert_called_with("tablet")
        self.mock_adaptive_layout_manager.set_orientation.assert_called_with("landscape")

    def test_handle_device_change(self):
        """Test handling device changes."""
        # Create a mock device change event
        device_info = {
            "type": "mobile",
            "screen": {
                "width": 375,
                "height": 812,
                "pixel_ratio": 2.0
            },
            "input": {
                "touch": True,
                "keyboard": False,
                "mouse": False
            },
            "network": {
                "type": "cellular",
                "connected": True
            },
            "battery": {
                "level": 75,
                "charging": False
            }
        }
        
        # Call the device change handler
        self.universal_skin._handle_device_change(device_info)
        
        # Verify that the interaction mode manager was updated
        self.mock_interaction_mode_manager.set_mode.assert_called_with("touch")
        
        # Verify that the adaptive layout manager was updated
        self.mock_adaptive_layout_manager.set_device_type.assert_called_with("mobile")
        self.mock_adaptive_layout_manager.set_screen_dimensions.assert_called_with(375, 812, 2.0)

    def test_set_offline_mode(self):
        """Test setting offline mode."""
        # Set offline mode
        self.universal_skin.set_offline_mode(True)
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "offline_mode_change",
            "data": {
                "offline": True
            }
        })
        
        # Verify that the rendering engine was updated
        self.mock_rendering_engine.set_offline_mode.assert_called_with(True)

    def test_set_accessibility_features(self):
        """Test setting accessibility features."""
        # Set accessibility features
        self.universal_skin.set_accessibility_features({
            "high_contrast": True,
            "large_text": True,
            "screen_reader": True,
            "reduced_motion": True
        })
        
        # Verify that the theme manager was updated
        self.mock_theme_manager.set_high_contrast.assert_called_with(True)
        self.mock_theme_manager.set_large_text.assert_called_with(True)
        
        # Verify that the rendering engine was updated
        self.mock_rendering_engine.set_reduced_motion.assert_called_with(True)
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "accessibility_change",
            "data": {
                "high_contrast": True,
                "large_text": True,
                "screen_reader": True,
                "reduced_motion": True
            }
        })

    def test_get_current_state(self):
        """Test getting the current state."""
        # Configure mocks to return specific values
        self.mock_role_view_manager.get_current_role.return_value = "process_handler"
        self.mock_adaptive_layout_manager.get_current_layout.return_value = "standard"
        self.mock_interaction_mode_manager.get_current_mode.return_value = "desktop"
        self.mock_theme_manager.get_current_theme.return_value = "industrial"
        
        # Get current state
        state = self.universal_skin.get_current_state()
        
        # Verify the state
        self.assertEqual(state["role"], "process_handler")
        self.assertEqual(state["layout"], "standard")
        self.assertEqual(state["interaction_mode"], "desktop")
        self.assertEqual(state["theme"], "industrial")

    def test_handle_orientation_change(self):
        """Test handling orientation changes."""
        # Call the orientation change handler
        self.universal_skin._handle_orientation_change("portrait")
        
        # Verify that the adaptive layout manager was updated
        self.mock_adaptive_layout_manager.set_orientation.assert_called_with("portrait")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "orientation_change",
            "data": {
                "orientation": "portrait"
            }
        })

    def test_handle_network_change(self):
        """Test handling network changes."""
        # Call the network change handler
        self.universal_skin._handle_network_change({
            "type": "cellular",
            "connected": True
        })
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "network_change",
            "data": {
                "type": "cellular",
                "connected": True
            }
        })
        
        # Test disconnected state
        self.universal_skin._handle_network_change({
            "type": "wifi",
            "connected": False
        })
        
        # Verify that offline mode was set
        self.mock_rendering_engine.set_offline_mode.assert_called_with(True)

    @patch('core.universal_skin.universal_skin_shell.logger')
    def test_error_handling(self, mock_logger):
        """Test error handling."""
        # Configure mock to raise an exception
        self.mock_theme_manager.set_theme.side_effect = Exception("Test error")
        
        # Call method that should handle the exception
        self.universal_skin.set_theme("dark")
        
        # Verify that the error was logged
        mock_logger.error.assert_called()
        
        # Verify that the context engine was updated with the error
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "error",
            "data": {
                "source": "universal_skin",
                "message": "Error setting theme: Test error"
            }
        })


class TestDeviceAdapter(unittest.TestCase):
    """Test cases for the Device Adapter."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock for context engine
        self.mock_context_engine = MagicMock(spec=ContextEngine)
        
        # Create instance of DeviceAdapter
        self.device_adapter = DeviceAdapter(
            context_engine=self.mock_context_engine
        )

    def test_detect_device_capabilities(self):
        """Test detecting device capabilities."""
        # Mock the window object for browser detection
        with patch('core.universal_skin.device_adapter.get_window_object') as mock_get_window:
            # Configure mock to return desktop browser info
            mock_window = MagicMock()
            mock_window.navigator.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            mock_window.screen.width = 1920
            mock_window.screen.height = 1080
            mock_window.devicePixelRatio = 1.0
            mock_window.navigator.maxTouchPoints = 0
            mock_get_window.return_value = mock_window
            
            # Call detect device capabilities
            device_info = self.device_adapter.detect_device_capabilities()
            
            # Verify the detected info
            self.assertEqual(device_info["type"], "desktop")
            self.assertEqual(device_info["screen"]["width"], 1920)
            self.assertEqual(device_info["screen"]["height"], 1080)
            self.assertEqual(device_info["input"]["touch"], False)
            
            # Configure mock to return mobile device info
            mock_window.navigator.userAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
            mock_window.screen.width = 375
            mock_window.screen.height = 812
            mock_window.devicePixelRatio = 2.0
            mock_window.navigator.maxTouchPoints = 5
            
            # Call detect device capabilities
            device_info = self.device_adapter.detect_device_capabilities()
            
            # Verify the detected info
            self.assertEqual(device_info["type"], "mobile")
            self.assertEqual(device_info["screen"]["width"], 375)
            self.assertEqual(device_info["screen"]["height"], 812)
            self.assertEqual(device_info["input"]["touch"], True)

    def test_register_event_handlers(self):
        """Test registering event handlers."""
        # Create mock handlers
        mock_resize_handler = MagicMock()
        mock_orientation_handler = MagicMock()
        mock_network_handler = MagicMock()
        
        # Register handlers
        self.device_adapter.register_resize_handler(mock_resize_handler)
        self.device_adapter.register_orientation_change_handler(mock_orientation_handler)
        self.device_adapter.register_network_status_change_handler(mock_network_handler)
        
        # Verify handlers were registered
        self.assertIn(mock_resize_handler, self.device_adapter.resize_handlers)
        self.assertIn(mock_orientation_handler, self.device_adapter.orientation_change_handlers)
        self.assertIn(mock_network_handler, self.device_adapter.network_status_change_handlers)

    def test_get_device_info(self):
        """Test getting device info."""
        # Mock the detect_device_capabilities method
        with patch.object(self.device_adapter, 'detect_device_capabilities') as mock_detect:
            # Configure mock to return specific device info
            mock_detect.return_value = {
                "type": "tablet",
                "screen": {
                    "width": 768,
                    "height": 1024,
                    "pixel_ratio": 2.0
                },
                "input": {
                    "touch": True,
                    "keyboard": True,
                    "mouse": False
                },
                "network": {
                    "type": "wifi",
                    "connected": True
                },
                "battery": {
                    "level": 80,
                    "charging": True
                }
            }
            
            # Get device info
            device_info = self.device_adapter.get_device_info()
            
            # Verify the info
            self.assertEqual(device_info["type"], "tablet")
            self.assertEqual(device_info["screen"]["width"], 768)
            self.assertEqual(device_info["screen"]["height"], 1024)
            self.assertEqual(device_info["input"]["touch"], True)
            self.assertEqual(device_info["battery"]["level"], 80)


class TestRoleViewManager(unittest.TestCase):
    """Test cases for the Role View Manager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock for context engine
        self.mock_context_engine = MagicMock(spec=ContextEngine)
        
        # Create test configuration
        self.test_config = {
            "roles": {
                "master": {
                    "name": "Master",
                    "description": "Overall system view with strategic insights",
                    "components": ["mission_deck", "swarm_lens", "trust_ribbon", "timeline_view"],
                    "permissions": ["view_all", "manage_all"]
                },
                "domain_expert": {
                    "name": "Domain Expert",
                    "description": "Domain-specific view with specialized tools",
                    "components": ["mission_deck", "digital_twin_viewer", "workflow_canvas"],
                    "permissions": ["view_domain", "manage_domain"]
                },
                "process_handler": {
                    "name": "Process Handler",
                    "description": "Process-focused view with operational tools",
                    "components": ["workflow_canvas", "digital_twin_viewer", "trust_ribbon"],
                    "permissions": ["view_process", "manage_process"]
                },
                "agent": {
                    "name": "Agent",
                    "description": "Agent-focused view with collaboration tools",
                    "components": ["swarm_lens", "protocol_visualizer", "capsule_dock"],
                    "permissions": ["view_agent", "manage_agent"]
                }
            },
            "default_role": "process_handler"
        }
        
        # Create instance of RoleViewManager
        self.role_view_manager = RoleViewManager(
            context_engine=self.mock_context_engine,
            config=self.test_config
        )

    def test_initialization(self):
        """Test that RoleViewManager initializes correctly."""
        # Verify that the RoleViewManager was initialized with the correct configuration
        self.assertEqual(self.role_view_manager.config["default_role"], "process_handler")
        self.assertEqual(len(self.role_view_manager.config["roles"]), 4)
        
        # Verify that the current role was set to the default
        self.assertEqual(self.role_view_manager.current_role, "process_handler")

    def test_set_current_role(self):
        """Test setting the current role."""
        # Set a new role
        self.role_view_manager.set_current_role("domain_expert")
        
        # Verify that the current role was updated
        self.assertEqual(self.role_view_manager.current_role, "domain_expert")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "role_change",
            "data": {
                "role": "domain_expert",
                "components": ["mission_deck", "digital_twin_viewer", "workflow_canvas"],
                "permissions": ["view_domain", "manage_domain"]
            }
        })
        
        # Test setting an invalid role
        with self.assertRaises(ValueError):
            self.role_view_manager.set_current_role("invalid_role")

    def test_get_current_role(self):
        """Test getting the current role."""
        # Set a role first
        self.role_view_manager.set_current_role("master")
        
        # Get the current role
        role = self.role_view_manager.get_current_role()
        
        # Verify the role
        self.assertEqual(role, "master")

    def test_get_role_info(self):
        """Test getting role information."""
        # Get info for a specific role
        role_info = self.role_view_manager.get_role_info("agent")
        
        # Verify the info
        self.assertEqual(role_info["name"], "Agent")
        self.assertEqual(role_info["description"], "Agent-focused view with collaboration tools")
        self.assertIn("swarm_lens", role_info["components"])
        self.assertIn("view_agent", role_info["permissions"])
        
        # Test getting info for an invalid role
        with self.assertRaises(ValueError):
            self.role_view_manager.get_role_info("invalid_role")

    def test_get_available_roles(self):
        """Test getting available roles."""
        # Get available roles
        roles = self.role_view_manager.get_available_roles()
        
        # Verify the roles
        self.assertEqual(len(roles), 4)
        self.assertIn("master", roles)
        self.assertIn("domain_expert", roles)
        self.assertIn("process_handler", roles)
        self.assertIn("agent", roles)

    def test_get_role_components(self):
        """Test getting components for a role."""
        # Get components for a specific role
        components = self.role_view_manager.get_role_components("domain_expert")
        
        # Verify the components
        self.assertEqual(len(components), 3)
        self.assertIn("mission_deck", components)
        self.assertIn("digital_twin_viewer", components)
        self.assertIn("workflow_canvas", components)
        
        # Test getting components for the current role
        self.role_view_manager.set_current_role("process_handler")
        components = self.role_view_manager.get_current_role_components()
        
        # Verify the components
        self.assertEqual(len(components), 3)
        self.assertIn("workflow_canvas", components)
        self.assertIn("digital_twin_viewer", components)
        self.assertIn("trust_ribbon", components)

    def test_has_permission(self):
        """Test checking permissions for a role."""
        # Set the current role
        self.role_view_manager.set_current_role("master")
        
        # Check permissions
        self.assertTrue(self.role_view_manager.has_permission("view_all"))
        self.assertTrue(self.role_view_manager.has_permission("manage_all"))
        self.assertFalse(self.role_view_manager.has_permission("invalid_permission"))
        
        # Change role and check permissions
        self.role_view_manager.set_current_role("process_handler")
        self.assertTrue(self.role_view_manager.has_permission("view_process"))
        self.assertTrue(self.role_view_manager.has_permission("manage_process"))
        self.assertFalse(self.role_view_manager.has_permission("view_all"))

    def test_add_custom_role(self):
        """Test adding a custom role."""
        # Add a custom role
        custom_role = {
            "name": "Custom Role",
            "description": "A custom role for testing",
            "components": ["mission_deck", "trust_ribbon"],
            "permissions": ["view_custom", "manage_custom"]
        }
        self.role_view_manager.add_custom_role("custom", custom_role)
        
        # Verify the role was added
        self.assertIn("custom", self.role_view_manager.config["roles"])
        
        # Set the custom role as current
        self.role_view_manager.set_current_role("custom")
        
        # Verify the current role
        self.assertEqual(self.role_view_manager.current_role, "custom")
        
        # Check permissions for the custom role
        self.assertTrue(self.role_view_manager.has_permission("view_custom"))
        self.assertTrue(self.role_view_manager.has_permission("manage_custom"))


class TestAdaptiveLayoutManager(unittest.TestCase):
    """Test cases for the Adaptive Layout Manager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock for context engine
        self.mock_context_engine = MagicMock(spec=ContextEngine)
        self.mock_rendering_engine = MagicMock(spec=RenderingEngine)
        
        # Create test configuration
        self.test_config = {
            "layouts": {
                "standard": {
                    "name": "Standard",
                    "description": "Default layout with all components",
                    "sidebar_visible": True,
                    "capsule_dock_position": "left",
                    "mission_deck_compact": False,
                    "swarm_lens_simplified": False,
                    "trust_ribbon_position": "bottom",
                    "timeline_view_compact": False,
                    "context_panel_overlay": False,
                    "action_menu_floating": False,
                    "notification_center_overlay": False
                },
                "compact": {
                    "name": "Compact",
                    "description": "Space-efficient layout for smaller screens",
                    "sidebar_visible": False,
                    "capsule_dock_position": "bottom",
                    "mission_deck_compact": True,
                    "swarm_lens_simplified": True,
                    "trust_ribbon_position": "top",
                    "timeline_view_compact": True,
                    "context_panel_overlay": True,
                    "action_menu_floating": True,
                    "notification_center_overlay": True
                },
                "focused": {
                    "name": "Focused",
                    "description": "Minimalist layout focusing on primary content",
                    "sidebar_visible": False,
                    "capsule_dock_position": "hidden",
                    "mission_deck_compact": False,
                    "swarm_lens_simplified": True,
                    "trust_ribbon_position": "hidden",
                    "timeline_view_compact": True,
                    "context_panel_overlay": True,
                    "action_menu_floating": True,
                    "notification_center_overlay": True
                }
            },
            "device_layouts": {
                "desktop": "standard",
                "tablet": "standard",
                "mobile": "compact"
            },
            "orientation_layouts": {
                "landscape": {},
                "portrait": {
                    "tablet": "compact",
                    "mobile": "compact"
                }
            },
            "default_layout": "standard"
        }
        
        # Create instance of AdaptiveLayoutManager
        self.layout_manager = AdaptiveLayoutManager(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )

    def test_initialization(self):
        """Test that AdaptiveLayoutManager initializes correctly."""
        # Verify that the AdaptiveLayoutManager was initialized with the correct configuration
        self.assertEqual(self.layout_manager.config["default_layout"], "standard")
        self.assertEqual(len(self.layout_manager.config["layouts"]), 3)
        
        # Verify that the current layout was set to the default
        self.assertEqual(self.layout_manager.current_layout, "standard")
        
        # Verify default device type and orientation
        self.assertEqual(self.layout_manager.device_type, "desktop")
        self.assertEqual(self.layout_manager.orientation, "landscape")

    def test_set_layout(self):
        """Test setting the layout."""
        # Set a new layout
        self.layout_manager.set_layout("compact")
        
        # Verify that the current layout was updated
        self.assertEqual(self.layout_manager.current_layout, "compact")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "layout_change",
            "data": {
                "layout": "compact",
                "settings": self.test_config["layouts"]["compact"]
            }
        })
        
        # Verify that the rendering engine was updated
        self.mock_rendering_engine.update_layout.assert_called_with(
            "compact",
            self.test_config["layouts"]["compact"]
        )
        
        # Test setting an invalid layout
        with self.assertRaises(ValueError):
            self.layout_manager.set_layout("invalid_layout")

    def test_get_current_layout(self):
        """Test getting the current layout."""
        # Set a layout first
        self.layout_manager.set_layout("focused")
        
        # Get the current layout
        layout = self.layout_manager.get_current_layout()
        
        # Verify the layout
        self.assertEqual(layout, "focused")

    def test_get_layout_info(self):
        """Test getting layout information."""
        # Get info for a specific layout
        layout_info = self.layout_manager.get_layout_info("compact")
        
        # Verify the info
        self.assertEqual(layout_info["name"], "Compact")
        self.assertEqual(layout_info["description"], "Space-efficient layout for smaller screens")
        self.assertEqual(layout_info["sidebar_visible"], False)
        self.assertEqual(layout_info["capsule_dock_position"], "bottom")
        
        # Test getting info for an invalid layout
        with self.assertRaises(ValueError):
            self.layout_manager.get_layout_info("invalid_layout")

    def test_get_available_layouts(self):
        """Test getting available layouts."""
        # Get available layouts
        layouts = self.layout_manager.get_available_layouts()
        
        # Verify the layouts
        self.assertEqual(len(layouts), 3)
        self.assertIn("standard", layouts)
        self.assertIn("compact", layouts)
        self.assertIn("focused", layouts)

    def test_set_device_type(self):
        """Test setting the device type."""
        # Set device type to mobile
        self.layout_manager.set_device_type("mobile")
        
        # Verify that the device type was updated
        self.assertEqual(self.layout_manager.device_type, "mobile")
        
        # Verify that the layout was updated based on device type
        self.assertEqual(self.layout_manager.current_layout, "compact")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "layout_change",
            "data": {
                "layout": "compact",
                "settings": self.test_config["layouts"]["compact"]
            }
        })

    def test_set_orientation(self):
        """Test setting the orientation."""
        # Set device type to tablet first
        self.layout_manager.set_device_type("tablet")
        
        # Set orientation to portrait
        self.layout_manager.set_orientation("portrait")
        
        # Verify that the orientation was updated
        self.assertEqual(self.layout_manager.orientation, "portrait")
        
        # Verify that the layout was updated based on orientation
        self.assertEqual(self.layout_manager.current_layout, "compact")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "layout_change",
            "data": {
                "layout": "compact",
                "settings": self.test_config["layouts"]["compact"]
            }
        })

    def test_set_screen_dimensions(self):
        """Test setting screen dimensions."""
        # Set screen dimensions
        self.layout_manager.set_screen_dimensions(375, 812, 2.0)
        
        # Verify that the screen dimensions were updated
        self.assertEqual(self.layout_manager.screen_width, 375)
        self.assertEqual(self.layout_manager.screen_height, 812)
        self.assertEqual(self.layout_manager.pixel_ratio, 2.0)
        
        # Verify that the device type was updated to mobile
        self.assertEqual(self.layout_manager.device_type, "mobile")
        
        # Verify that the orientation was updated to portrait
        self.assertEqual(self.layout_manager.orientation, "portrait")
        
        # Verify that the layout was updated
        self.assertEqual(self.layout_manager.current_layout, "compact")

    def test_register_components(self):
        """Test registering UI components."""
        # Create mock components
        components = ["capsule_dock", "mission_deck", "swarm_lens", "trust_ribbon"]
        
        # Register components
        self.layout_manager.register_components(components)
        
        # Verify that the components were registered
        self.assertEqual(self.layout_manager.registered_components, components)
        
        # Verify that the rendering engine was updated
        self.mock_rendering_engine.register_components.assert_called_with(components)

    def test_apply_layout_settings(self):
        """Test applying layout settings."""
        # Set a layout
        self.layout_manager.set_layout("compact")
        
        # Verify that the layout settings were applied
        self.mock_rendering_engine.update_layout.assert_called_with(
            "compact",
            self.test_config["layouts"]["compact"]
        )
        
        # Verify individual settings
        self.mock_rendering_engine.set_sidebar_visible.assert_called_with(False)
        self.mock_rendering_engine.set_capsule_dock_position.assert_called_with("bottom")
        self.mock_rendering_engine.set_mission_deck_compact.assert_called_with(True)
        self.mock_rendering_engine.set_swarm_lens_simplified.assert_called_with(True)
        self.mock_rendering_engine.set_trust_ribbon_position.assert_called_with("top")
        self.mock_rendering_engine.set_timeline_view_compact.assert_called_with(True)
        self.mock_rendering_engine.set_context_panel_overlay.assert_called_with(True)
        self.mock_rendering_engine.set_action_menu_floating.assert_called_with(True)
        self.mock_rendering_engine.set_notification_center_overlay.assert_called_with(True)

    def test_add_custom_layout(self):
        """Test adding a custom layout."""
        # Add a custom layout
        custom_layout = {
            "name": "Custom",
            "description": "A custom layout for testing",
            "sidebar_visible": True,
            "capsule_dock_position": "right",
            "mission_deck_compact": False,
            "swarm_lens_simplified": False,
            "trust_ribbon_position": "top",
            "timeline_view_compact": False,
            "context_panel_overlay": False,
            "action_menu_floating": True,
            "notification_center_overlay": False
        }
        self.layout_manager.add_custom_layout("custom", custom_layout)
        
        # Verify the layout was added
        self.assertIn("custom", self.layout_manager.config["layouts"])
        
        # Set the custom layout as current
        self.layout_manager.set_layout("custom")
        
        # Verify the current layout
        self.assertEqual(self.layout_manager.current_layout, "custom")


class TestInteractionModeManager(unittest.TestCase):
    """Test cases for the Interaction Mode Manager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock for context engine
        self.mock_context_engine = MagicMock(spec=ContextEngine)
        self.mock_rendering_engine = MagicMock(spec=RenderingEngine)
        
        # Create test configuration
        self.test_config = {
            "modes": {
                "desktop": {
                    "name": "Desktop",
                    "description": "Optimized for desktop with keyboard and mouse",
                    "touch_target_size": 24,
                    "hover_enabled": True,
                    "keyboard_shortcuts_enabled": True,
                    "context_menus_enabled": True,
                    "drag_drop_enabled": True,
                    "tooltip_delay": 500,
                    "double_click_enabled": True,
                    "scroll_behavior": "standard"
                },
                "touch": {
                    "name": "Touch",
                    "description": "Optimized for touch devices",
                    "touch_target_size": 44,
                    "hover_enabled": False,
                    "keyboard_shortcuts_enabled": False,
                    "context_menus_enabled": True,
                    "drag_drop_enabled": True,
                    "tooltip_delay": 0,
                    "double_click_enabled": False,
                    "scroll_behavior": "momentum"
                },
                "voice": {
                    "name": "Voice",
                    "description": "Optimized for voice control",
                    "touch_target_size": 32,
                    "hover_enabled": False,
                    "keyboard_shortcuts_enabled": False,
                    "context_menus_enabled": True,
                    "drag_drop_enabled": False,
                    "tooltip_delay": 1000,
                    "double_click_enabled": False,
                    "scroll_behavior": "paged"
                }
            },
            "device_modes": {
                "desktop": "desktop",
                "tablet": "touch",
                "mobile": "touch"
            },
            "default_mode": "desktop"
        }
        
        # Create instance of InteractionModeManager
        self.mode_manager = InteractionModeManager(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )

    def test_initialization(self):
        """Test that InteractionModeManager initializes correctly."""
        # Verify that the InteractionModeManager was initialized with the correct configuration
        self.assertEqual(self.mode_manager.config["default_mode"], "desktop")
        self.assertEqual(len(self.mode_manager.config["modes"]), 3)
        
        # Verify that the current mode was set to the default
        self.assertEqual(self.mode_manager.current_mode, "desktop")

    def test_set_mode(self):
        """Test setting the interaction mode."""
        # Set a new mode
        self.mode_manager.set_mode("touch")
        
        # Verify that the current mode was updated
        self.assertEqual(self.mode_manager.current_mode, "touch")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "interaction_mode_change",
            "data": {
                "mode": "touch",
                "settings": self.test_config["modes"]["touch"]
            }
        })
        
        # Verify that the rendering engine was updated
        self.mock_rendering_engine.update_interaction_mode.assert_called_with(
            "touch",
            self.test_config["modes"]["touch"]
        )
        
        # Test setting an invalid mode
        with self.assertRaises(ValueError):
            self.mode_manager.set_mode("invalid_mode")

    def test_get_current_mode(self):
        """Test getting the current interaction mode."""
        # Set a mode first
        self.mode_manager.set_mode("voice")
        
        # Get the current mode
        mode = self.mode_manager.get_current_mode()
        
        # Verify the mode
        self.assertEqual(mode, "voice")

    def test_get_mode_info(self):
        """Test getting mode information."""
        # Get info for a specific mode
        mode_info = self.mode_manager.get_mode_info("touch")
        
        # Verify the info
        self.assertEqual(mode_info["name"], "Touch")
        self.assertEqual(mode_info["description"], "Optimized for touch devices")
        self.assertEqual(mode_info["touch_target_size"], 44)
        self.assertEqual(mode_info["hover_enabled"], False)
        
        # Test getting info for an invalid mode
        with self.assertRaises(ValueError):
            self.mode_manager.get_mode_info("invalid_mode")

    def test_get_available_modes(self):
        """Test getting available interaction modes."""
        # Get available modes
        modes = self.mode_manager.get_available_modes()
        
        # Verify the modes
        self.assertEqual(len(modes), 3)
        self.assertIn("desktop", modes)
        self.assertIn("touch", modes)
        self.assertIn("voice", modes)

    def test_set_device_type(self):
        """Test setting the device type."""
        # Set device type to tablet
        self.mode_manager.set_device_type("tablet")
        
        # Verify that the device type was updated
        self.assertEqual(self.mode_manager.device_type, "tablet")
        
        # Verify that the mode was updated based on device type
        self.assertEqual(self.mode_manager.current_mode, "touch")
        
        # Verify that the context engine was updated
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "interaction_mode_change",
            "data": {
                "mode": "touch",
                "settings": self.test_config["modes"]["touch"]
            }
        })

    def test_apply_mode_settings(self):
        """Test applying interaction mode settings."""
        # Set a mode
        self.mode_manager.set_mode("touch")
        
        # Verify that the mode settings were applied
        self.mock_rendering_engine.update_interaction_mode.assert_called_with(
            "touch",
            self.test_config["modes"]["touch"]
        )
        
        # Verify individual settings
        self.mock_rendering_engine.set_touch_target_size.assert_called_with(44)
        self.mock_rendering_engine.set_hover_enabled.assert_called_with(False)
        self.mock_rendering_engine.set_keyboard_shortcuts_enabled.assert_called_with(False)
        self.mock_rendering_engine.set_context_menus_enabled.assert_called_with(True)
        self.mock_rendering_engine.set_drag_drop_enabled.assert_called_with(True)
        self.mock_rendering_engine.set_tooltip_delay.assert_called_with(0)
        self.mock_rendering_engine.set_double_click_enabled.assert_called_with(False)
        self.mock_rendering_engine.set_scroll_behavior.assert_called_with("momentum")

    def test_add_custom_mode(self):
        """Test adding a custom interaction mode."""
        # Add a custom mode
        custom_mode = {
            "name": "Custom",
            "description": "A custom interaction mode for testing",
            "touch_target_size": 36,
            "hover_enabled": True,
            "keyboard_shortcuts_enabled": True,
            "context_menus_enabled": False,
            "drag_drop_enabled": True,
            "tooltip_delay": 250,
            "double_click_enabled": True,
            "scroll_behavior": "smooth"
        }
        self.mode_manager.add_custom_mode("custom", custom_mode)
        
        # Verify the mode was added
        self.assertIn("custom", self.mode_manager.config["modes"])
        
        # Set the custom mode as current
        self.mode_manager.set_mode("custom")
        
        # Verify the current mode
        self.assertEqual(self.mode_manager.current_mode, "custom")


if __name__ == '__main__':
    unittest.main()
