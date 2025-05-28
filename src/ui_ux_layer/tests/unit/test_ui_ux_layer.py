"""
UI/UX Layer Test Suite - Comprehensive tests for all components of the UI/UX Layer.

This module provides a comprehensive test suite for the UI/UX Layer, covering all components,
integrations, and scenarios to ensure the layer meets the requirements for Ambient Intelligence
and Universal Skin.
"""

import os
import sys
import json
import logging
import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional, Union

# Core module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core.universal_skin.universal_skin_shell import UniversalSkinShell
from core.universal_skin.device_adapter import DeviceAdapter
from core.agent_ecosystem.avatar_manager import AvatarManager
from core.capsule_framework.capsule_manager import CapsuleManager
from core.context_engine.context_engine import ContextEngine
from core.interaction_orchestrator.interaction_orchestrator import InteractionOrchestrator
from core.protocol_bridge.protocol_bridge import ProtocolBridge
from core.cross_layer_integration.real_time_context_bus import RealTimeContextBus
from core.rendering_engine.rendering_engine import RenderingEngine
from core.rendering_engine.theme_manager import ThemeManager
from core.rendering_engine.accessibility_manager import AccessibilityManager

class UniversalSkinShellTest(unittest.TestCase):
    """Test case for the Universal Skin Shell."""
    
    def setUp(self):
        """Set up the test case."""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Create mock dependencies
        self.device_adapter = MagicMock(spec=DeviceAdapter)
        self.device_adapter.get_platform.return_value = "web"
        self.device_adapter.get_form_factor.return_value = "desktop"
        self.device_adapter.get_capabilities.return_value = {
            "touch": False,
            "keyboard": True,
            "mouse": True,
            "screen_size": {"width": 1920, "height": 1080},
            "dark_mode": False,
            "high_contrast": False,
            "reduced_motion": False
        }
        
        # Create Universal Skin Shell
        self.universal_skin_shell = UniversalSkinShell(
            device_adapter=self.device_adapter,
            config={
                "theme": "industriverse-default",
                "adaptiveMode": True,
                "ambientIntelligenceLevel": "high",
                "trustVisualization": True,
                "capsuleAnimations": True,
                "accessibilityFeatures": True
            }
        )
    
    def test_initialization(self):
        """Test initialization of the Universal Skin Shell."""
        self.assertEqual(self.universal_skin_shell.config["theme"], "industriverse-default")
        self.assertTrue(self.universal_skin_shell.config["adaptiveMode"])
        self.assertEqual(self.universal_skin_shell.config["ambientIntelligenceLevel"], "high")
        self.assertTrue(self.universal_skin_shell.config["trustVisualization"])
        self.assertTrue(self.universal_skin_shell.config["capsuleAnimations"])
        self.assertTrue(self.universal_skin_shell.config["accessibilityFeatures"])
    
    def test_adapt_to_device(self):
        """Test adaptation to device capabilities."""
        # Call adapt_to_device
        self.universal_skin_shell.adapt_to_device()
        
        # Verify device adapter was called
        self.device_adapter.get_platform.assert_called_once()
        self.device_adapter.get_form_factor.assert_called_once()
        self.device_adapter.get_capabilities.assert_called_once()
    
    def test_register_component(self):
        """Test registering a component."""
        # Create mock component
        component = MagicMock()
        component.get_id.return_value = "test-component"
        
        # Register component
        self.universal_skin_shell.register_component(component)
        
        # Verify component was registered
        self.assertIn("test-component", self.universal_skin_shell.components)
        self.assertEqual(self.universal_skin_shell.components["test-component"], component)
    
    def test_unregister_component(self):
        """Test unregistering a component."""
        # Create mock component
        component = MagicMock()
        component.get_id.return_value = "test-component"
        
        # Register component
        self.universal_skin_shell.register_component(component)
        
        # Unregister component
        self.universal_skin_shell.unregister_component("test-component")
        
        # Verify component was unregistered
        self.assertNotIn("test-component", self.universal_skin_shell.components)
    
    def test_get_component(self):
        """Test getting a component."""
        # Create mock component
        component = MagicMock()
        component.get_id.return_value = "test-component"
        
        # Register component
        self.universal_skin_shell.register_component(component)
        
        # Get component
        retrieved_component = self.universal_skin_shell.get_component("test-component")
        
        # Verify component was retrieved
        self.assertEqual(retrieved_component, component)
    
    def test_get_nonexistent_component(self):
        """Test getting a nonexistent component."""
        # Get nonexistent component
        retrieved_component = self.universal_skin_shell.get_component("nonexistent-component")
        
        # Verify None was returned
        self.assertIsNone(retrieved_component)
    
    def test_initialize(self):
        """Test initializing the Universal Skin Shell."""
        # Initialize
        self.universal_skin_shell.initialize()
        
        # Verify device adapter was called
        self.device_adapter.get_platform.assert_called()
        self.device_adapter.get_form_factor.assert_called()
        self.device_adapter.get_capabilities.assert_called()

class DeviceAdapterTest(unittest.TestCase):
    """Test case for the Device Adapter."""
    
    def setUp(self):
        """Set up the test case."""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Create Device Adapter
        self.device_adapter = DeviceAdapter(
            platform="web",
            form_factor="desktop",
            capabilities={
                "touch": False,
                "keyboard": True,
                "mouse": True,
                "screen_size": {"width": 1920, "height": 1080},
                "dark_mode": False,
                "high_contrast": False,
                "reduced_motion": False
            }
        )
    
    def test_initialization(self):
        """Test initialization of the Device Adapter."""
        self.assertEqual(self.device_adapter.platform, "web")
        self.assertEqual(self.device_adapter.form_factor, "desktop")
        self.assertEqual(self.device_adapter.capabilities["touch"], False)
        self.assertEqual(self.device_adapter.capabilities["keyboard"], True)
        self.assertEqual(self.device_adapter.capabilities["mouse"], True)
        self.assertEqual(self.device_adapter.capabilities["screen_size"]["width"], 1920)
        self.assertEqual(self.device_adapter.capabilities["screen_size"]["height"], 1080)
        self.assertEqual(self.device_adapter.capabilities["dark_mode"], False)
        self.assertEqual(self.device_adapter.capabilities["high_contrast"], False)
        self.assertEqual(self.device_adapter.capabilities["reduced_motion"], False)
    
    def test_get_platform(self):
        """Test getting the platform."""
        self.assertEqual(self.device_adapter.get_platform(), "web")
    
    def test_get_form_factor(self):
        """Test getting the form factor."""
        self.assertEqual(self.device_adapter.get_form_factor(), "desktop")
    
    def test_get_capabilities(self):
        """Test getting the capabilities."""
        capabilities = self.device_adapter.get_capabilities()
        self.assertEqual(capabilities["touch"], False)
        self.assertEqual(capabilities["keyboard"], True)
        self.assertEqual(capabilities["mouse"], True)
        self.assertEqual(capabilities["screen_size"]["width"], 1920)
        self.assertEqual(capabilities["screen_size"]["height"], 1080)
        self.assertEqual(capabilities["dark_mode"], False)
        self.assertEqual(capabilities["high_contrast"], False)
        self.assertEqual(capabilities["reduced_motion"], False)
    
    def test_get_context(self):
        """Test getting the context."""
        context = self.device_adapter.get_context()
        self.assertEqual(context["platform"], "web")
        self.assertEqual(context["form_factor"], "desktop")
        self.assertEqual(context["capabilities"]["touch"], False)
        self.assertEqual(context["capabilities"]["keyboard"], True)
        self.assertEqual(context["capabilities"]["mouse"], True)
        self.assertEqual(context["capabilities"]["screen_size"]["width"], 1920)
        self.assertEqual(context["capabilities"]["screen_size"]["height"], 1080)
        self.assertEqual(context["capabilities"]["dark_mode"], False)
        self.assertEqual(context["capabilities"]["high_contrast"], False)
        self.assertEqual(context["capabilities"]["reduced_motion"], False)
    
    def test_update_capabilities(self):
        """Test updating capabilities."""
        # Update capabilities
        self.device_adapter.update_capabilities({
            "dark_mode": True,
            "screen_size": {"width": 1280, "height": 720}
        })
        
        # Verify capabilities were updated
        capabilities = self.device_adapter.get_capabilities()
        self.assertEqual(capabilities["dark_mode"], True)
        self.assertEqual(capabilities["screen_size"]["width"], 1280)
        self.assertEqual(capabilities["screen_size"]["height"], 720)
        
        # Verify other capabilities were not changed
        self.assertEqual(capabilities["touch"], False)
        self.assertEqual(capabilities["keyboard"], True)
        self.assertEqual(capabilities["mouse"], True)
        self.assertEqual(capabilities["high_contrast"], False)
        self.assertEqual(capabilities["reduced_motion"], False)
    
    def test_is_mobile(self):
        """Test checking if the device is mobile."""
        # Desktop device
        self.assertFalse(self.device_adapter.is_mobile())
        
        # Mobile device
        mobile_adapter = DeviceAdapter(
            platform="web",
            form_factor="mobile",
            capabilities={
                "touch": True,
                "keyboard": False,
                "mouse": False,
                "screen_size": {"width": 375, "height": 812},
                "dark_mode": False,
                "high_contrast": False,
                "reduced_motion": False
            }
        )
        self.assertTrue(mobile_adapter.is_mobile())
    
    def test_is_tablet(self):
        """Test checking if the device is a tablet."""
        # Desktop device
        self.assertFalse(self.device_adapter.is_tablet())
        
        # Tablet device
        tablet_adapter = DeviceAdapter(
            platform="web",
            form_factor="tablet",
            capabilities={
                "touch": True,
                "keyboard": False,
                "mouse": False,
                "screen_size": {"width": 768, "height": 1024},
                "dark_mode": False,
                "high_contrast": False,
                "reduced_motion": False
            }
        )
        self.assertTrue(tablet_adapter.is_tablet())
    
    def test_is_desktop(self):
        """Test checking if the device is a desktop."""
        # Desktop device
        self.assertTrue(self.device_adapter.is_desktop())
        
        # Mobile device
        mobile_adapter = DeviceAdapter(
            platform="web",
            form_factor="mobile",
            capabilities={
                "touch": True,
                "keyboard": False,
                "mouse": False,
                "screen_size": {"width": 375, "height": 812},
                "dark_mode": False,
                "high_contrast": False,
                "reduced_motion": False
            }
        )
        self.assertFalse(mobile_adapter.is_desktop())
    
    def test_supports_touch(self):
        """Test checking if the device supports touch."""
        # Non-touch device
        self.assertFalse(self.device_adapter.supports_touch())
        
        # Touch device
        touch_adapter = DeviceAdapter(
            platform="web",
            form_factor="mobile",
            capabilities={
                "touch": True,
                "keyboard": False,
                "mouse": False,
                "screen_size": {"width": 375, "height": 812},
                "dark_mode": False,
                "high_contrast": False,
                "reduced_motion": False
            }
        )
        self.assertTrue(touch_adapter.supports_touch())

class AvatarManagerTest(unittest.TestCase):
    """Test case for the Avatar Manager."""
    
    def setUp(self):
        """Set up the test case."""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Create mock dependencies
        self.context_engine = MagicMock(spec=ContextEngine)
        
        # Create Avatar Manager
        self.avatar_manager = AvatarManager(
            context_engine=self.context_engine,
            config={
                "avatarUpdateFrequency": 250,
                "defaultAvatarStyle": "industriverse-default",
                "expressionEnabled": True,
                "personalityEnabled": True
            }
        )
    
    def test_initialization(self):
        """Test initialization of the Avatar Manager."""
        self.assertEqual(self.avatar_manager.config["avatarUpdateFrequency"], 250)
        self.assertEqual(self.avatar_manager.config["defaultAvatarStyle"], "industriverse-default")
        self.assertTrue(self.avatar_manager.config["expressionEnabled"])
        self.assertTrue(self.avatar_manager.config["personalityEnabled"])
    
    def test_create_avatar(self):
        """Test creating an avatar."""
        # Create avatar
        avatar_id = self.avatar_manager.create_avatar("data_layer", {
            "name": "Data Layer Avatar",
            "style": "data-layer-style",
            "personality": "analytical"
        })
        
        # Verify avatar was created
        self.assertIsNotNone(avatar_id)
        self.assertIn(avatar_id, self.avatar_manager.avatars)
        self.assertEqual(self.avatar_manager.avatars[avatar_id]["name"], "Data Layer Avatar")
        self.assertEqual(self.avatar_manager.avatars[avatar_id]["style"], "data-layer-style")
        self.assertEqual(self.avatar_manager.avatars[avatar_id]["personality"], "analytical")
    
    def test_get_avatar(self):
        """Test getting an avatar."""
        # Create avatar
        avatar_id = self.avatar_manager.create_avatar("data_layer", {
            "name": "Data Layer Avatar",
            "style": "data-layer-style",
            "personality": "analytical"
        })
        
        # Get avatar
        avatar = self.avatar_manager.get_avatar(avatar_id)
        
        # Verify avatar was retrieved
        self.assertIsNotNone(avatar)
        self.assertEqual(avatar["name"], "Data Layer Avatar")
        self.assertEqual(avatar["style"], "data-layer-style")
        self.assertEqual(avatar["personality"], "analytical")
    
    def test_get_nonexistent_avatar(self):
        """Test getting a nonexistent avatar."""
        # Get nonexistent avatar
        avatar = self.avatar_manager.get_avatar("nonexistent-avatar")
        
        # Verify None was returned
        self.assertIsNone(avatar)
    
    def test_update_avatar(self):
        """Test updating an avatar."""
        # Create avatar
        avatar_id = self.avatar_manager.create_avatar("data_layer", {
            "name": "Data Layer Avatar",
            "style": "data-layer-style",
            "personality": "analytical"
        })
        
        # Update avatar
        self.avatar_manager.update_avatar(avatar_id, {
            "name": "Updated Data Layer Avatar",
            "expression": "happy"
        })
        
        # Verify avatar was updated
        avatar = self.avatar_manager.get_avatar(avatar_id)
        self.assertEqual(avatar["name"], "Updated Data Layer Avatar")
        self.assertEqual(avatar["expression"], "happy")
        
        # Verify other properties were not changed
        self.assertEqual(avatar["style"], "data-layer-style")
        self.assertEqual(avatar["personality"], "analytical")
    
    def test_delete_avatar(self):
        """Test deleting an avatar."""
        # Create avatar
        avatar_id = self.avatar_manager.create_avatar("data_layer", {
            "name": "Data Layer Avatar",
            "style": "data-layer-style",
            "personality": "analytical"
        })
        
        # Delete avatar
        self.avatar_manager.delete_avatar(avatar_id)
        
        # Verify avatar was deleted
        self.assertNotIn(avatar_id, self.avatar_manager.avatars)
    
    def test_get_all_avatars(self):
        """Test getting all avatars."""
        # Create avatars
        avatar_id1 = self.avatar_manager.create_avatar("data_layer", {
            "name": "Data Layer Avatar",
            "style": "data-layer-style",
            "personality": "analytical"
        })
        avatar_id2 = self.avatar_manager.create_avatar("core_ai_layer", {
            "name": "Core AI Layer Avatar",
            "style": "core-ai-layer-style",
            "personality": "intelligent"
        })
        
        # Get all avatars
        avatars = self.avatar_manager.get_all_avatars()
        
        # Verify avatars were retrieved
        self.assertEqual(len(avatars), 2)
        self.assertIn(avatar_id1, avatars)
        self.assertIn(avatar_id2, avatars)
        self.assertEqual(avatars[avatar_id1]["name"], "Data Layer Avatar")
        self.assertEqual(avatars[avatar_id2]["name"], "Core AI Layer Avatar")
    
    def test_set_avatar_expression(self):
        """Test setting an avatar's expression."""
        # Create avatar
        avatar_id = self.avatar_manager.create_avatar("data_layer", {
            "name": "Data Layer Avatar",
            "style": "data-layer-style",
            "personality": "analytical"
        })
        
        # Set expression
        self.avatar_manager.set_avatar_expression(avatar_id, "happy")
        
        # Verify expression was set
        avatar = self.avatar_manager.get_avatar(avatar_id)
        self.assertEqual(avatar["expression"], "happy")
    
    def test_set_avatar_state(self):
        """Test setting an avatar's state."""
        # Create avatar
        avatar_id = self.avatar_manager.create_avatar("data_layer", {
            "name": "Data Layer Avatar",
            "style": "data-layer-style",
            "personality": "analytical"
        })
        
        # Set state
        self.avatar_manager.set_avatar_state(avatar_id, "busy")
        
        # Verify state was set
        avatar = self.avatar_manager.get_avatar(avatar_id)
        self.assertEqual(avatar["state"], "busy")

class CapsuleManagerTest(unittest.TestCase):
    """Test case for the Capsule Manager."""
    
    def setUp(self):
        """Set up the test case."""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Create mock dependencies
        self.context_engine = MagicMock(spec=ContextEngine)
        
        # Create Capsule Manager
        self.capsule_manager = CapsuleManager(
            context_engine=self.context_engine,
            config={
                "capsuleUpdateFrequency": 250,
                "defaultCapsuleStyle": "industriverse-default",
                "animationsEnabled": True,
                "maxActiveCapsules": 10
            }
        )
    
    def test_initialization(self):
        """Test initialization of the Capsule Manager."""
        self.assertEqual(self.capsule_manager.config["capsuleUpdateFrequency"], 250)
        self.assertEqual(self.capsule_manager.config["defaultCapsuleStyle"], "industriverse-default")
        self.assertTrue(self.capsule_manager.config["animationsEnabled"])
        self.assertEqual(self.capsule_manager.config["maxActiveCapsules"], 10)
    
    def test_create_capsule(self):
        """Test creating a capsule."""
        # Create capsule
        capsule_id = self.capsule_manager.create_capsule("workflow_visualizer", {
            "name": "Workflow Visualizer",
            "style": "workflow-visualizer-style",
            "type": "visualization",
            "source": "workflow_layer"
        })
        
        # Verify capsule was created
        self.assertIsNotNone(capsule_id)
        self.assertIn(capsule_id, self.capsule_manager.capsules)
        self.assertEqual(self.capsule_manager.capsules[capsule_id]["name"], "Workflow Visualizer")
        self.assertEqual(self.capsule_manager.capsules[capsule_id]["style"], "workflow-visualizer-style")
        self.assertEqual(self.capsule_manager.capsules[capsule_id]["type"], "visualization")
        self.assertEqual(self.capsule_manager.capsules[capsule_id]["source"], "workflow_layer")
    
    def test_get_capsule(self):
        """Test getting a capsule."""
        # Create capsule
        capsule_id = self.capsule_manager.create_capsule("workflow_visualizer", {
            "name": "Workflow Visualizer",
            "style": "workflow-visualizer-style",
            "type": "visualization",
            "source": "workflow_layer"
        })
        
        # Get capsule
        capsule = self.capsule_manager.get_capsule(capsule_id)
        
        # Verify capsule was retrieved
        self.assertIsNotNone(capsule)
        self.assertEqual(capsule["name"], "Workflow Visualizer")
        self.assertEqual(capsule["style"], "workflow-visualizer-style")
        self.assertEqual(capsule["type"], "visualization")
        self.assertEqual(capsule["source"], "workflow_layer")
    
    def test_get_nonexistent_capsule(self):
        """Test getting a nonexistent capsule."""
        # Get nonexistent capsule
        capsule = self.capsule_manager.get_capsule("nonexistent-capsule")
        
        # Verify None was returned
        self.assertIsNone(capsule)
    
    def test_update_capsule(self):
        """Test updating a capsule."""
        # Create capsule
        capsule_id = self.capsule_manager.create_capsule("workflow_visualizer", {
            "name": "Workflow Visualizer",
            "style": "workflow-visualizer-style",
            "type": "visualization",
            "source": "workflow_layer"
        })
        
        # Update capsule
        self.capsule_manager.update_capsule(capsule_id, {
            "name": "Updated Workflow Visualizer",
            "state": "active"
        })
        
        # Verify capsule was updated
        capsule = self.capsule_manager.get_capsule(capsule_id)
        self.assertEqual(capsule["name"], "Updated Workflow Visualizer")
        self.assertEqual(capsule["state"], "active")
        
        # Verify other properties were not changed
        self.assertEqual(capsule["style"], "workflow-visualizer-style")
        self.assertEqual(capsule["type"], "visualization")
        self.assertEqual(capsule["source"], "workflow_layer")
    
    def test_delete_capsule(self):
        """Test deleting a capsule."""
        # Create capsule
        capsule_id = self.capsule_manager.create_capsule("workflow_visualizer", {
            "name": "Workflow Visualizer",
            "style": "workflow-visualizer-style",
            "type": "visualization",
            "source": "workflow_layer"
        })
        
        # Delete capsule
        self.capsule_manager.delete_capsule(capsule_id)
        
        # Verify capsule was deleted
        self.assertNotIn(capsule_id, self.capsule_manager.capsules)
    
    def test_get_all_capsules(self):
        """Test getting all capsules."""
        # Create capsules
        capsule_id1 = self.capsule_manager.create_capsule("workflow_visualizer", {
            "name": "Workflow Visualizer",
            "style": "workflow-visualizer-style",
            "type": "visualization",
            "source": "workflow_layer"
        })
        capsule_id2 = self.capsule_manager.create_capsule("data_explorer", {
            "name": "Data Explorer",
            "style": "data-explorer-style",
            "type": "exploration",
            "source": "data_layer"
        })
        
        # Get all capsules
        capsules = self.capsule_manager.get_all_capsules()
        
        # Verify capsules were retrieved
        self.assertEqual(len(capsules), 2)
        self.assertIn(capsule_id1, capsules)
        self.assertIn(capsule_id2, capsules)
        self.assertEqual(capsules[capsule_id1]["name"], "Workflow Visualizer")
        self.assertEqual(capsules[capsule_id2]["name"], "Data Explorer")
    
    def test_activate_capsule(self):
        """Test activating a capsule."""
        # Create capsule
        capsule_id = self.capsule_manager.create_capsule("workflow_visualizer", {
            "name": "Workflow Visualizer",
            "style": "workflow-visualizer-style",
            "type": "visualization",
            "source": "workflow_layer"
        })
        
        # Activate capsule
        self.capsule_manager.activate_capsule(capsule_id)
        
        # Verify capsule was activated
        capsule = self.capsule_manager.get_capsule(capsule_id)
        self.assertEqual(capsule["state"], "active")
    
    def test_deactivate_capsule(self):
        """Test deactivating a capsule."""
        # Create capsule
        capsule_id = self.capsule_manager.create_capsule("workflow_visualizer", {
            "name": "Workflow Visualizer",
            "style": "workflow-visualizer-style",
            "type": "visualization",
            "source": "workflow_layer"
        })
        
        # Activate capsule
        self.capsule_manager.activate_capsule(capsule_id)
        
        # Deactivate capsule
        self.capsule_manager.deactivate_capsule(capsule_id)
        
        # Verify capsule was deactivated
        capsule = self.capsule_manager.get_capsule(capsule_id)
        self.assertEqual(capsule["state"], "inactive")
    
    def test_get_active_capsules(self):
        """Test getting active capsules."""
        # Create capsules
        capsule_id1 = self.capsule_manager.create_capsule("workflow_visualizer", {
            "name": "Workflow Visualizer",
            "style": "workflow-visualizer-style",
            "type": "visualization",
            "source": "workflow_layer"
        })
        capsule_id2 = self.capsule_manager.create_capsule("data_explorer", {
            "name": "Data Explorer",
            "style": "data-explorer-style",
            "type": "exploration",
            "source": "data_layer"
        })
        
        # Activate first capsule
        self.capsule_manager.activate_capsule(capsule_id1)
        
        # Get active capsules
        active_capsules = self.capsule_manager.get_active_capsules()
        
        # Verify active capsules were retrieved
        self.assertEqual(len(active_capsules), 1)
        self.assertIn(capsule_id1, active_capsules)
        self.assertNotIn(capsule_id2, active_capsules)
        self.assertEqual(active_capsules[capsule_id1]["name"], "Workflow Visualizer")

class ContextEngineTest(unittest.TestCase):
    """Test case for the Context Engine."""
    
    def setUp(self):
        """Set up the test case."""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Create mock dependencies
        self.device_context = {
            "platform": "web",
            "form_factor": "desktop",
            "capabilities": {
                "touch": False,
                "keyboard": True,
                "mouse": True,
                "screen_size": {"width": 1920, "height": 1080},
                "dark_mode": False,
                "high_contrast": False,
                "reduced_motion": False
            }
        }
        
        # Create Context Engine
        self.context_engine = ContextEngine(
            device_context=self.device_context,
            config={
                "contextUpdateFrequency": 250,
                "priorityLevels": ["critical", "high", "medium", "low", "ambient"],
                "contextHistoryLength": 100,
                "spatialAwarenessEnabled": True
            }
        )
    
    def test_initialization(self):
        """Test initialization of the Context Engine."""
        self.assertEqual(self.context_engine.config["contextUpdateFrequency"], 250)
        self.assertEqual(self.context_engine.config["priorityLevels"], ["critical", "high", "medium", "low", "ambient"])
        self.assertEqual(self.context_engine.config["contextHistoryLength"], 100)
        self.assertTrue(self.context_engine.config["spatialAwarenessEnabled"])
        
        # Verify device context was set
        self.assertEqual(self.context_engine.context["device"]["platform"], "web")
        self.assertEqual(self.context_engine.context["device"]["form_factor"], "desktop")
        self.assertEqual(self.context_engine.context["device"]["capabilities"]["touch"], False)
        self.assertEqual(self.context_engine.context["device"]["capabilities"]["keyboard"], True)
        self.assertEqual(self.context_engine.context["device"]["capabilities"]["mouse"], True)
        self.assertEqual(self.context_engine.context["device"]["capabilities"]["screen_size"]["width"], 1920)
        self.assertEqual(self.context_engine.context["device"]["capabilities"]["screen_size"]["height"], 1080)
        self.assertEqual(self.context_engine.context["device"]["capabilities"]["dark_mode"], False)
        self.assertEqual(self.context_engine.context["device"]["capabilities"]["high_contrast"], False)
        self.assertEqual(self.context_engine.context["device"]["capabilities"]["reduced_motion"], False)
    
    def test_update_context(self):
        """Test updating context."""
        # Update context
        self.context_engine.update_context("user", {
            "name": "Test User",
            "role": "admin",
            "preferences": {
                "theme": "dark",
                "language": "en"
            }
        })
        
        # Verify context was updated
        self.assertEqual(self.context_engine.context["user"]["name"], "Test User")
        self.assertEqual(self.context_engine.context["user"]["role"], "admin")
        self.assertEqual(self.context_engine.context["user"]["preferences"]["theme"], "dark")
        self.assertEqual(self.context_engine.context["user"]["preferences"]["language"], "en")
    
    def test_get_context(self):
        """Test getting context."""
        # Update context
        self.context_engine.update_context("user", {
            "name": "Test User",
            "role": "admin",
            "preferences": {
                "theme": "dark",
                "language": "en"
            }
        })
        
        # Get context
        context = self.context_engine.get_context()
        
        # Verify context was retrieved
        self.assertEqual(context["user"]["name"], "Test User")
        self.assertEqual(context["user"]["role"], "admin")
        self.assertEqual(context["user"]["preferences"]["theme"], "dark")
        self.assertEqual(context["user"]["preferences"]["language"], "en")
        self.assertEqual(context["device"]["platform"], "web")
        self.assertEqual(context["device"]["form_factor"], "desktop")
    
    def test_get_context_by_key(self):
        """Test getting context by key."""
        # Update context
        self.context_engine.update_context("user", {
            "name": "Test User",
            "role": "admin",
            "preferences": {
                "theme": "dark",
                "language": "en"
            }
        })
        
        # Get context by key
        user_context = self.context_engine.get_context_by_key("user")
        
        # Verify context was retrieved
        self.assertEqual(user_context["name"], "Test User")
        self.assertEqual(user_context["role"], "admin")
        self.assertEqual(user_context["preferences"]["theme"], "dark")
        self.assertEqual(user_context["preferences"]["language"], "en")
    
    def test_get_nonexistent_context_by_key(self):
        """Test getting nonexistent context by key."""
        # Get nonexistent context by key
        nonexistent_context = self.context_engine.get_context_by_key("nonexistent")
        
        # Verify None was returned
        self.assertIsNone(nonexistent_context)
    
    def test_remove_context(self):
        """Test removing context."""
        # Update context
        self.context_engine.update_context("user", {
            "name": "Test User",
            "role": "admin",
            "preferences": {
                "theme": "dark",
                "language": "en"
            }
        })
        
        # Remove context
        self.context_engine.remove_context("user")
        
        # Verify context was removed
        self.assertNotIn("user", self.context_engine.context)
    
    def test_add_context_listener(self):
        """Test adding a context listener."""
        # Create mock listener
        listener = MagicMock()
        
        # Add listener
        self.context_engine.add_context_listener("user", listener)
        
        # Update context
        self.context_engine.update_context("user", {
            "name": "Test User",
            "role": "admin"
        })
        
        # Verify listener was called
        listener.assert_called_once()
        args, kwargs = listener.call_args
        self.assertEqual(args[0], "user")
        self.assertEqual(args[1]["name"], "Test User")
        self.assertEqual(args[1]["role"], "admin")
    
    def test_remove_context_listener(self):
        """Test removing a context listener."""
        # Create mock listener
        listener = MagicMock()
        
        # Add listener
        self.context_engine.add_context_listener("user", listener)
        
        # Remove listener
        self.context_engine.remove_context_listener("user", listener)
        
        # Update context
        self.context_engine.update_context("user", {
            "name": "Test User",
            "role": "admin"
        })
        
        # Verify listener was not called
        listener.assert_not_called()
    
    def test_add_priority_event(self):
        """Test adding a priority event."""
        # Add priority event
        self.context_engine.add_priority_event("critical", {
            "type": "alert",
            "message": "Critical alert",
            "timestamp": 1621234567890
        })
        
        # Verify event was added
        self.assertEqual(len(self.context_engine.priority_events["critical"]), 1)
        self.assertEqual(self.context_engine.priority_events["critical"][0]["type"], "alert")
        self.assertEqual(self.context_engine.priority_events["critical"][0]["message"], "Critical alert")
        self.assertEqual(self.context_engine.priority_events["critical"][0]["timestamp"], 1621234567890)
    
    def test_get_priority_events(self):
        """Test getting priority events."""
        # Add priority events
        self.context_engine.add_priority_event("critical", {
            "type": "alert",
            "message": "Critical alert",
            "timestamp": 1621234567890
        })
        self.context_engine.add_priority_event("high", {
            "type": "warning",
            "message": "High warning",
            "timestamp": 1621234567891
        })
        
        # Get priority events
        events = self.context_engine.get_priority_events()
        
        # Verify events were retrieved
        self.assertEqual(len(events["critical"]), 1)
        self.assertEqual(len(events["high"]), 1)
        self.assertEqual(events["critical"][0]["type"], "alert")
        self.assertEqual(events["critical"][0]["message"], "Critical alert")
        self.assertEqual(events["high"][0]["type"], "warning")
        self.assertEqual(events["high"][0]["message"], "High warning")
    
    def test_get_priority_events_by_level(self):
        """Test getting priority events by level."""
        # Add priority events
        self.context_engine.add_priority_event("critical", {
            "type": "alert",
            "message": "Critical alert",
            "timestamp": 1621234567890
        })
        self.context_engine.add_priority_event("high", {
            "type": "warning",
            "message": "High warning",
            "timestamp": 1621234567891
        })
        
        # Get priority events by level
        critical_events = self.context_engine.get_priority_events_by_level("critical")
        
        # Verify events were retrieved
        self.assertEqual(len(critical_events), 1)
        self.assertEqual(critical_events[0]["type"], "alert")
        self.assertEqual(critical_events[0]["message"], "Critical alert")
    
    def test_clear_priority_events(self):
        """Test clearing priority events."""
        # Add priority events
        self.context_engine.add_priority_event("critical", {
            "type": "alert",
            "message": "Critical alert",
            "timestamp": 1621234567890
        })
        self.context_engine.add_priority_event("high", {
            "type": "warning",
            "message": "High warning",
            "timestamp": 1621234567891
        })
        
        # Clear priority events
        self.context_engine.clear_priority_events()
        
        # Verify events were cleared
        self.assertEqual(len(self.context_engine.priority_events["critical"]), 0)
        self.assertEqual(len(self.context_engine.priority_events["high"]), 0)
    
    def test_clear_priority_events_by_level(self):
        """Test clearing priority events by level."""
        # Add priority events
        self.context_engine.add_priority_event("critical", {
            "type": "alert",
            "message": "Critical alert",
            "timestamp": 1621234567890
        })
        self.context_engine.add_priority_event("high", {
            "type": "warning",
            "message": "High warning",
            "timestamp": 1621234567891
        })
        
        # Clear priority events by level
        self.context_engine.clear_priority_events_by_level("critical")
        
        # Verify events were cleared
        self.assertEqual(len(self.context_engine.priority_events["critical"]), 0)
        self.assertEqual(len(self.context_engine.priority_events["high"]), 1)

def run_tests():
    """Run the UI/UX Layer tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(UniversalSkinShellTest))
    suite.addTest(unittest.makeSuite(DeviceAdapterTest))
    suite.addTest(unittest.makeSuite(AvatarManagerTest))
    suite.addTest(unittest.makeSuite(CapsuleManagerTest))
    suite.addTest(unittest.makeSuite(ContextEngineTest))
    
    # Run tests
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    # Run tests
    run_tests()
