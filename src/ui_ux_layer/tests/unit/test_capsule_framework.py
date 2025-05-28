"""
Unit tests for the Capsule Framework components.

This test suite validates the core functionality of the Capsule Framework,
including capsule management, morphology, memory, state management,
interaction control, and lifecycle management.

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
from core.capsule_framework.capsule_manager import CapsuleManager
from core.capsule_framework.capsule_morphology_engine import CapsuleMorphologyEngine
from core.capsule_framework.capsule_memory_manager import CapsuleMemoryManager
from core.capsule_framework.capsule_state_manager import CapsuleStateManager
from core.capsule_framework.capsule_interaction_controller import CapsuleInteractionController
from core.capsule_framework.capsule_lifecycle_manager import CapsuleLifecycleManager
from core.context_engine.context_engine import ContextEngine
from core.rendering_engine.rendering_engine import RenderingEngine


class TestCapsuleFramework(unittest.TestCase):
    """Test cases for the Capsule Framework components."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mocks for dependencies
        self.mock_context_engine = MagicMock(spec=ContextEngine)
        self.mock_rendering_engine = MagicMock(spec=RenderingEngine)
        
        # Create test configuration
        self.test_config = {
            "capsule_types": {
                "agent": {
                    "icon": "agent_icon.svg",
                    "default_size": {"width": 320, "height": 180},
                    "min_size": {"width": 160, "height": 90},
                    "max_size": {"width": 640, "height": 360},
                    "default_state": "idle",
                    "allowed_states": ["idle", "working", "error", "success"],
                    "default_position": "dock",
                    "allowed_positions": ["dock", "float", "sidebar", "fullscreen"]
                },
                "digital_twin": {
                    "icon": "twin_icon.svg",
                    "default_size": {"width": 400, "height": 300},
                    "min_size": {"width": 200, "height": 150},
                    "max_size": {"width": 800, "height": 600},
                    "default_state": "idle",
                    "allowed_states": ["idle", "active", "error", "warning"],
                    "default_position": "float",
                    "allowed_positions": ["dock", "float", "sidebar", "fullscreen"]
                },
                "workflow": {
                    "icon": "workflow_icon.svg",
                    "default_size": {"width": 480, "height": 270},
                    "min_size": {"width": 240, "height": 135},
                    "max_size": {"width": 960, "height": 540},
                    "default_state": "idle",
                    "allowed_states": ["idle", "running", "paused", "completed", "error"],
                    "default_position": "sidebar",
                    "allowed_positions": ["dock", "float", "sidebar", "fullscreen"]
                }
            },
            "morphology_transitions": {
                "expand": {"duration": 300, "easing": "ease-out"},
                "collapse": {"duration": 250, "easing": "ease-in"},
                "dock": {"duration": 350, "easing": "ease-in-out"},
                "undock": {"duration": 350, "easing": "ease-in-out"}
            },
            "memory_settings": {
                "max_history_items": 100,
                "max_context_size": 1024,
                "persistence_enabled": true,
                "sync_interval": 30000
            },
            "lifecycle_hooks": {
                "pre_create": ["validate_config", "prepare_resources"],
                "post_create": ["initialize_state", "register_listeners"],
                "pre_destroy": ["save_state", "unregister_listeners"],
                "post_destroy": ["release_resources", "notify_dependents"]
            },
            "interaction_modes": {
                "desktop": {
                    "drag_enabled": true,
                    "resize_enabled": true,
                    "context_menu_enabled": true,
                    "hover_actions_enabled": true
                },
                "touch": {
                    "drag_enabled": true,
                    "resize_enabled": true,
                    "context_menu_enabled": true,
                    "hover_actions_enabled": false
                },
                "voice": {
                    "drag_enabled": false,
                    "resize_enabled": false,
                    "context_menu_enabled": true,
                    "hover_actions_enabled": false
                }
            }
        }
        
        # Create instances of components
        self.capsule_manager = CapsuleManager(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )
        self.morphology_engine = CapsuleMorphologyEngine(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )
        self.memory_manager = CapsuleMemoryManager(
            context_engine=self.mock_context_engine,
            config=self.test_config
        )
        self.state_manager = CapsuleStateManager(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )
        self.interaction_controller = CapsuleInteractionController(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )
        self.lifecycle_manager = CapsuleLifecycleManager(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )

    # --- CapsuleManager Tests --- 

    def test_capsule_manager_initialization(self):
        """Test CapsuleManager initialization."""
        self.assertEqual(len(self.capsule_manager.config["capsule_types"]), 3)
        self.assertEqual(len(self.capsule_manager.capsules), 0)

    def test_create_capsule(self):
        """Test creating a capsule."""
        capsule_id = "capsule_001"
        capsule_type = "agent"
        capsule_config = {"name": "Test Agent", "agent_id": "agent_001"}
        
        self.capsule_manager.create_capsule(capsule_id, capsule_type, capsule_config)
        
        self.assertIn(capsule_id, self.capsule_manager.capsules)
        self.assertEqual(self.capsule_manager.capsules[capsule_id]["type"], capsule_type)
        self.assertEqual(self.capsule_manager.capsules[capsule_id]["config"]["name"], "Test Agent")
        
        self.mock_rendering_engine.create_capsule.assert_called_with(
            capsule_id, 
            capsule_type, 
            self.test_config["capsule_types"][capsule_type],
            capsule_config
        )
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test invalid capsule type
        with self.assertRaises(ValueError):
            self.capsule_manager.create_capsule("invalid_capsule", "invalid_type", {})

    def test_get_capsule_info(self):
        """Test getting capsule information."""
        capsule_id = "capsule_002"
        capsule_type = "digital_twin"
        capsule_config = {"name": "Test Twin", "twin_id": "twin_001"}
        
        self.capsule_manager.create_capsule(capsule_id, capsule_type, capsule_config)
        
        info = self.capsule_manager.get_capsule_info(capsule_id)
        self.assertEqual(info["type"], capsule_type)
        self.assertEqual(info["config"]["name"], "Test Twin")
        
        with self.assertRaises(KeyError):
            self.capsule_manager.get_capsule_info("non_existent_capsule")

    def test_update_capsule_config(self):
        """Test updating capsule configuration."""
        capsule_id = "capsule_003"
        capsule_type = "workflow"
        capsule_config = {"name": "Test Workflow", "workflow_id": "workflow_001"}
        
        self.capsule_manager.create_capsule(capsule_id, capsule_type, capsule_config)
        
        updated_config = {"name": "Updated Workflow", "workflow_id": "workflow_001"}
        self.capsule_manager.update_capsule_config(capsule_id, updated_config)
        
        self.assertEqual(self.capsule_manager.capsules[capsule_id]["config"]["name"], "Updated Workflow")
        self.mock_rendering_engine.update_capsule_config.assert_called_with(capsule_id, updated_config)
        self.mock_context_engine.publish_context_update.assert_called()

    def test_remove_capsule(self):
        """Test removing a capsule."""
        capsule_id = "capsule_004"
        capsule_type = "agent"
        capsule_config = {"name": "Test Agent", "agent_id": "agent_002"}
        
        self.capsule_manager.create_capsule(capsule_id, capsule_type, capsule_config)
        self.capsule_manager.remove_capsule(capsule_id)
        
        self.assertNotIn(capsule_id, self.capsule_manager.capsules)
        self.mock_rendering_engine.remove_capsule.assert_called_with(capsule_id)
        self.mock_context_engine.publish_context_update.assert_called()

    def test_get_capsules_by_type(self):
        """Test getting capsules by type."""
        # Create multiple capsules of different types
        self.capsule_manager.create_capsule("capsule_005", "agent", {"name": "Agent 1"})
        self.capsule_manager.create_capsule("capsule_006", "agent", {"name": "Agent 2"})
        self.capsule_manager.create_capsule("capsule_007", "digital_twin", {"name": "Twin 1"})
        
        agent_capsules = self.capsule_manager.get_capsules_by_type("agent")
        self.assertEqual(len(agent_capsules), 2)
        self.assertIn("capsule_005", agent_capsules)
        self.assertIn("capsule_006", agent_capsules)
        
        twin_capsules = self.capsule_manager.get_capsules_by_type("digital_twin")
        self.assertEqual(len(twin_capsules), 1)
        self.assertIn("capsule_007", twin_capsules)
        
        workflow_capsules = self.capsule_manager.get_capsules_by_type("workflow")
        self.assertEqual(len(workflow_capsules), 0)

    # --- CapsuleMorphologyEngine Tests --- 

    def test_morphology_engine_initialization(self):
        """Test CapsuleMorphologyEngine initialization."""
        self.assertEqual(len(self.morphology_engine.config["morphology_transitions"]), 4)

    def test_resize_capsule(self):
        """Test resizing a capsule."""
        capsule_id = "capsule_008"
        new_size = {"width": 400, "height": 300}
        animate = True
        
        self.morphology_engine.resize_capsule(capsule_id, new_size, animate)
        
        self.mock_rendering_engine.resize_capsule.assert_called_with(
            capsule_id, 
            new_size, 
            animate, 
            self.test_config["morphology_transitions"]["expand"]
        )
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "capsule_resize",
            "data": {"capsule_id": capsule_id, "size": new_size, "animated": animate}
        })

    def test_move_capsule(self):
        """Test moving a capsule."""
        capsule_id = "capsule_009"
        new_position = {"x": 100, "y": 200}
        animate = True
        
        self.morphology_engine.move_capsule(capsule_id, new_position, animate)
        
        self.mock_rendering_engine.move_capsule.assert_called_with(
            capsule_id, 
            new_position, 
            animate, 
            self.test_config["morphology_transitions"]["undock"]
        )
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "capsule_move",
            "data": {"capsule_id": capsule_id, "position": new_position, "animated": animate}
        })

    def test_change_capsule_position_type(self):
        """Test changing capsule position type."""
        capsule_id = "capsule_010"
        position_type = "dock"
        animate = True
        
        self.morphology_engine.change_capsule_position_type(capsule_id, position_type, animate)
        
        self.mock_rendering_engine.change_capsule_position_type.assert_called_with(
            capsule_id, 
            position_type, 
            animate, 
            self.test_config["morphology_transitions"]["dock"]
        )
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "capsule_position_type_change",
            "data": {"capsule_id": capsule_id, "position_type": position_type, "animated": animate}
        })
        
        # Test invalid position type
        with self.assertRaises(ValueError):
            self.morphology_engine.change_capsule_position_type(capsule_id, "invalid_position", animate)

    def test_apply_morphology_effect(self):
        """Test applying morphology effect."""
        capsule_id = "capsule_011"
        effect_type = "highlight"
        effect_config = {"color": "#ffcc00", "duration": 1000}
        
        self.morphology_engine.apply_morphology_effect(capsule_id, effect_type, effect_config)
        
        self.mock_rendering_engine.apply_capsule_effect.assert_called_with(
            capsule_id, 
            effect_type, 
            effect_config
        )
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "capsule_effect_applied",
            "data": {"capsule_id": capsule_id, "effect_type": effect_type, "effect_config": effect_config}
        })

    # --- CapsuleMemoryManager Tests --- 

    def test_memory_manager_initialization(self):
        """Test CapsuleMemoryManager initialization."""
        self.assertEqual(self.memory_manager.config["memory_settings"]["max_history_items"], 100)
        self.assertEqual(len(self.memory_manager.capsule_memory), 0)

    def test_initialize_capsule_memory(self):
        """Test initializing capsule memory."""
        capsule_id = "capsule_012"
        initial_context = {"agent_id": "agent_003", "status": "idle"}
        
        self.memory_manager.initialize_capsule_memory(capsule_id, initial_context)
        
        self.assertIn(capsule_id, self.memory_manager.capsule_memory)
        self.assertEqual(self.memory_manager.capsule_memory[capsule_id]["context"], initial_context)
        self.assertEqual(len(self.memory_manager.capsule_memory[capsule_id]["history"]), 0)
        self.mock_context_engine.publish_context_update.assert_called()

    def test_update_capsule_context(self):
        """Test updating capsule context."""
        capsule_id = "capsule_013"
        initial_context = {"agent_id": "agent_004", "status": "idle"}
        self.memory_manager.initialize_capsule_memory(capsule_id, initial_context)
        
        context_update = {"status": "working", "progress": 0.5}
        self.memory_manager.update_capsule_context(capsule_id, context_update)
        
        updated_context = self.memory_manager.capsule_memory[capsule_id]["context"]
        self.assertEqual(updated_context["status"], "working")
        self.assertEqual(updated_context["progress"], 0.5)
        self.assertEqual(updated_context["agent_id"], "agent_004")  # Original value preserved
        self.mock_context_engine.publish_context_update.assert_called()

    def test_add_history_item(self):
        """Test adding history item."""
        capsule_id = "capsule_014"
        initial_context = {"agent_id": "agent_005", "status": "idle"}
        self.memory_manager.initialize_capsule_memory(capsule_id, initial_context)
        
        history_item = {
            "type": "status_change",
            "data": {"old_status": "idle", "new_status": "working"},
            "timestamp": "2025-05-23T11:30:00Z"
        }
        self.memory_manager.add_history_item(capsule_id, history_item)
        
        history = self.memory_manager.capsule_memory[capsule_id]["history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], history_item)
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test max history limit
        self.memory_manager.config["memory_settings"]["max_history_items"] = 2
        
        history_item2 = {
            "type": "action",
            "data": {"action": "process_data"},
            "timestamp": "2025-05-23T11:31:00Z"
        }
        self.memory_manager.add_history_item(capsule_id, history_item2)
        
        history_item3 = {
            "type": "result",
            "data": {"result": "success"},
            "timestamp": "2025-05-23T11:32:00Z"
        }
        self.memory_manager.add_history_item(capsule_id, history_item3)
        
        history = self.memory_manager.capsule_memory[capsule_id]["history"]
        self.assertEqual(len(history), 2)  # Oldest item removed
        self.assertEqual(history[0], history_item2)
        self.assertEqual(history[1], history_item3)

    def test_get_capsule_context(self):
        """Test getting capsule context."""
        capsule_id = "capsule_015"
        initial_context = {"agent_id": "agent_006", "status": "idle"}
        self.memory_manager.initialize_capsule_memory(capsule_id, initial_context)
        
        context = self.memory_manager.get_capsule_context(capsule_id)
        self.assertEqual(context, initial_context)
        
        with self.assertRaises(KeyError):
            self.memory_manager.get_capsule_context("non_existent_capsule")

    def test_get_capsule_history(self):
        """Test getting capsule history."""
        capsule_id = "capsule_016"
        initial_context = {"agent_id": "agent_007", "status": "idle"}
        self.memory_manager.initialize_capsule_memory(capsule_id, initial_context)
        
        history_item = {
            "type": "status_change",
            "data": {"old_status": "idle", "new_status": "working"},
            "timestamp": "2025-05-23T11:35:00Z"
        }
        self.memory_manager.add_history_item(capsule_id, history_item)
        
        history = self.memory_manager.get_capsule_history(capsule_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], history_item)
        
        with self.assertRaises(KeyError):
            self.memory_manager.get_capsule_history("non_existent_capsule")

    def test_clear_capsule_history(self):
        """Test clearing capsule history."""
        capsule_id = "capsule_017"
        initial_context = {"agent_id": "agent_008", "status": "idle"}
        self.memory_manager.initialize_capsule_memory(capsule_id, initial_context)
        
        history_item = {
            "type": "status_change",
            "data": {"old_status": "idle", "new_status": "working"},
            "timestamp": "2025-05-23T11:40:00Z"
        }
        self.memory_manager.add_history_item(capsule_id, history_item)
        
        self.memory_manager.clear_capsule_history(capsule_id)
        
        history = self.memory_manager.get_capsule_history(capsule_id)
        self.assertEqual(len(history), 0)
        self.mock_context_engine.publish_context_update.assert_called()

    # --- CapsuleStateManager Tests --- 

    def test_state_manager_initialization(self):
        """Test CapsuleStateManager initialization."""
        self.assertEqual(len(self.state_manager.capsule_states), 0)

    def test_initialize_capsule_state(self):
        """Test initializing capsule state."""
        capsule_id = "capsule_018"
        capsule_type = "agent"
        
        self.state_manager.initialize_capsule_state(capsule_id, capsule_type)
        
        self.assertIn(capsule_id, self.state_manager.capsule_states)
        default_state = self.test_config["capsule_types"][capsule_type]["default_state"]
        self.assertEqual(self.state_manager.capsule_states[capsule_id], default_state)
        self.mock_rendering_engine.update_capsule_state.assert_called_with(capsule_id, default_state)
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test invalid capsule type
        with self.assertRaises(ValueError):
            self.state_manager.initialize_capsule_state("invalid_capsule", "invalid_type")

    def test_update_capsule_state(self):
        """Test updating capsule state."""
        capsule_id = "capsule_019"
        capsule_type = "workflow"
        self.state_manager.initialize_capsule_state(capsule_id, capsule_type)
        
        new_state = "running"
        self.state_manager.update_capsule_state(capsule_id, new_state)
        
        self.assertEqual(self.state_manager.capsule_states[capsule_id], new_state)
        self.mock_rendering_engine.update_capsule_state.assert_called_with(capsule_id, new_state)
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test invalid state for capsule type
        with self.assertRaises(ValueError):
            self.state_manager.update_capsule_state(capsule_id, "invalid_state")

    def test_get_capsule_state(self):
        """Test getting capsule state."""
        capsule_id = "capsule_020"
        capsule_type = "digital_twin"
        self.state_manager.initialize_capsule_state(capsule_id, capsule_type)
        
        state = self.state_manager.get_capsule_state(capsule_id)
        default_state = self.test_config["capsule_types"][capsule_type]["default_state"]
        self.assertEqual(state, default_state)
        
        with self.assertRaises(KeyError):
            self.state_manager.get_capsule_state("non_existent_capsule")

    def test_is_valid_state_transition(self):
        """Test validating state transition."""
        capsule_type = "workflow"
        current_state = "idle"
        
        # Valid transitions
        self.assertTrue(self.state_manager.is_valid_state_transition(capsule_type, current_state, "running"))
        self.assertTrue(self.state_manager.is_valid_state_transition(capsule_type, current_state, "paused"))
        
        # Invalid transitions (not in allowed states)
        self.assertFalse(self.state_manager.is_valid_state_transition(capsule_type, current_state, "invalid_state"))
        
        # Invalid capsule type
        with self.assertRaises(ValueError):
            self.state_manager.is_valid_state_transition("invalid_type", current_state, "running")

    # --- CapsuleInteractionController Tests --- 

    def test_interaction_controller_initialization(self):
        """Test CapsuleInteractionController initialization."""
        self.assertEqual(len(self.interaction_controller.config["interaction_modes"]), 3)
        self.assertEqual(self.interaction_controller.current_mode, "desktop")  # Default

    def test_set_interaction_mode(self):
        """Test setting interaction mode."""
        mode = "touch"
        self.interaction_controller.set_interaction_mode(mode)
        
        self.assertEqual(self.interaction_controller.current_mode, mode)
        self.mock_rendering_engine.update_capsule_interaction_mode.assert_called_with(
            mode, 
            self.test_config["interaction_modes"][mode]
        )
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test invalid mode
        with self.assertRaises(ValueError):
            self.interaction_controller.set_interaction_mode("invalid_mode")

    def test_register_interaction_handler(self):
        """Test registering interaction handler."""
        capsule_id = "capsule_021"
        event_type = "click"
        handler = MagicMock()
        
        self.interaction_controller.register_interaction_handler(capsule_id, event_type, handler)
        
        self.assertIn(capsule_id, self.interaction_controller.interaction_handlers)
        self.assertIn(event_type, self.interaction_controller.interaction_handlers[capsule_id])
        self.assertEqual(self.interaction_controller.interaction_handlers[capsule_id][event_type], handler)
        self.mock_rendering_engine.register_capsule_event_handler.assert_called_with(capsule_id, event_type)

    def test_unregister_interaction_handler(self):
        """Test unregistering interaction handler."""
        capsule_id = "capsule_022"
        event_type = "click"
        handler = MagicMock()
        
        self.interaction_controller.register_interaction_handler(capsule_id, event_type, handler)
        self.interaction_controller.unregister_interaction_handler(capsule_id, event_type)
        
        self.assertNotIn(event_type, self.interaction_controller.interaction_handlers[capsule_id])
        self.mock_rendering_engine.unregister_capsule_event_handler.assert_called_with(capsule_id, event_type)

    def test_handle_interaction_event(self):
        """Test handling interaction event."""
        capsule_id = "capsule_023"
        event_type = "click"
        event_data = {"x": 100, "y": 50}
        handler = MagicMock()
        
        self.interaction_controller.register_interaction_handler(capsule_id, event_type, handler)
        self.interaction_controller.handle_interaction_event(capsule_id, event_type, event_data)
        
        handler.assert_called_with(event_data)
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test event with no handler
        self.interaction_controller.handle_interaction_event(capsule_id, "hover", event_data)
        # Should not raise an exception, just log a warning

    # --- CapsuleLifecycleManager Tests --- 

    def test_lifecycle_manager_initialization(self):
        """Test CapsuleLifecycleManager initialization."""
        self.assertEqual(len(self.lifecycle_manager.config["lifecycle_hooks"]["pre_create"]), 2)
        self.assertEqual(len(self.lifecycle_manager.capsule_lifecycle_state), 0)

    def test_initialize_capsule_lifecycle(self):
        """Test initializing capsule lifecycle."""
        capsule_id = "capsule_024"
        capsule_type = "agent"
        capsule_config = {"name": "Lifecycle Test Agent", "agent_id": "agent_009"}
        
        self.lifecycle_manager.initialize_capsule_lifecycle(capsule_id, capsule_type, capsule_config)
        
        self.assertIn(capsule_id, self.lifecycle_manager.capsule_lifecycle_state)
        self.assertEqual(self.lifecycle_manager.capsule_lifecycle_state[capsule_id]["status"], "created")
        self.assertEqual(self.lifecycle_manager.capsule_lifecycle_state[capsule_id]["type"], capsule_type)
        self.mock_context_engine.publish_context_update.assert_called()

    def test_execute_lifecycle_hooks(self):
        """Test executing lifecycle hooks."""
        capsule_id = "capsule_025"
        hook_type = "pre_create"
        
        # Mock hook functions
        self.lifecycle_manager.hook_functions = {
            "validate_config": MagicMock(return_value=True),
            "prepare_resources": MagicMock(return_value=True),
            "initialize_state": MagicMock(return_value=True),
            "register_listeners": MagicMock(return_value=True),
            "save_state": MagicMock(return_value=True),
            "unregister_listeners": MagicMock(return_value=True),
            "release_resources": MagicMock(return_value=True),
            "notify_dependents": MagicMock(return_value=True)
        }
        
        result = self.lifecycle_manager.execute_lifecycle_hooks(capsule_id, hook_type)
        
        self.assertTrue(result)
        self.lifecycle_manager.hook_functions["validate_config"].assert_called_with(capsule_id)
        self.lifecycle_manager.hook_functions["prepare_resources"].assert_called_with(capsule_id)
        
        # Test hook failure
        self.lifecycle_manager.hook_functions["validate_config"].return_value = False
        result = self.lifecycle_manager.execute_lifecycle_hooks(capsule_id, hook_type)
        self.assertFalse(result)

    def test_create_capsule(self):
        """Test creating a capsule with lifecycle hooks."""
        capsule_id = "capsule_026"
        capsule_type = "digital_twin"
        capsule_config = {"name": "Lifecycle Test Twin", "twin_id": "twin_002"}
        
        # Mock hook functions and rendering engine
        self.lifecycle_manager.hook_functions = {
            "validate_config": MagicMock(return_value=True),
            "prepare_resources": MagicMock(return_value=True),
            "initialize_state": MagicMock(return_value=True),
            "register_listeners": MagicMock(return_value=True)
        }
        
        result = self.lifecycle_manager.create_capsule(capsule_id, capsule_type, capsule_config)
        
        self.assertTrue(result)
        self.assertIn(capsule_id, self.lifecycle_manager.capsule_lifecycle_state)
        self.assertEqual(self.lifecycle_manager.capsule_lifecycle_state[capsule_id]["status"], "created")
        self.lifecycle_manager.hook_functions["validate_config"].assert_called_with(capsule_id)
        self.lifecycle_manager.hook_functions["initialize_state"].assert_called_with(capsule_id)
        self.mock_rendering_engine.create_capsule.assert_called()
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test hook failure
        self.lifecycle_manager.hook_functions["validate_config"].return_value = False
        result = self.lifecycle_manager.create_capsule("capsule_027", capsule_type, capsule_config)
        self.assertFalse(result)

    def test_destroy_capsule(self):
        """Test destroying a capsule with lifecycle hooks."""
        capsule_id = "capsule_028"
        capsule_type = "workflow"
        capsule_config = {"name": "Lifecycle Test Workflow", "workflow_id": "workflow_002"}
        
        # Create capsule first
        self.lifecycle_manager.initialize_capsule_lifecycle(capsule_id, capsule_type, capsule_config)
        
        # Mock hook functions
        self.lifecycle_manager.hook_functions = {
            "save_state": MagicMock(return_value=True),
            "unregister_listeners": MagicMock(return_value=True),
            "release_resources": MagicMock(return_value=True),
            "notify_dependents": MagicMock(return_value=True)
        }
        
        result = self.lifecycle_manager.destroy_capsule(capsule_id)
        
        self.assertTrue(result)
        self.assertNotIn(capsule_id, self.lifecycle_manager.capsule_lifecycle_state)
        self.lifecycle_manager.hook_functions["save_state"].assert_called_with(capsule_id)
        self.lifecycle_manager.hook_functions["release_resources"].assert_called_with(capsule_id)
        self.mock_rendering_engine.remove_capsule.assert_called_with(capsule_id)
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test non-existent capsule
        result = self.lifecycle_manager.destroy_capsule("non_existent_capsule")
        self.assertFalse(result)

    def test_suspend_capsule(self):
        """Test suspending a capsule."""
        capsule_id = "capsule_029"
        capsule_type = "agent"
        capsule_config = {"name": "Suspend Test Agent", "agent_id": "agent_010"}
        
        # Create capsule first
        self.lifecycle_manager.initialize_capsule_lifecycle(capsule_id, capsule_type, capsule_config)
        
        result = self.lifecycle_manager.suspend_capsule(capsule_id)
        
        self.assertTrue(result)
        self.assertEqual(self.lifecycle_manager.capsule_lifecycle_state[capsule_id]["status"], "suspended")
        self.mock_rendering_engine.update_capsule_visibility.assert_called_with(capsule_id, False)
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test non-existent capsule
        result = self.lifecycle_manager.suspend_capsule("non_existent_capsule")
        self.assertFalse(result)

    def test_resume_capsule(self):
        """Test resuming a capsule."""
        capsule_id = "capsule_030"
        capsule_type = "digital_twin"
        capsule_config = {"name": "Resume Test Twin", "twin_id": "twin_003"}
        
        # Create and suspend capsule first
        self.lifecycle_manager.initialize_capsule_lifecycle(capsule_id, capsule_type, capsule_config)
        self.lifecycle_manager.suspend_capsule(capsule_id)
        
        result = self.lifecycle_manager.resume_capsule(capsule_id)
        
        self.assertTrue(result)
        self.assertEqual(self.lifecycle_manager.capsule_lifecycle_state[capsule_id]["status"], "active")
        self.mock_rendering_engine.update_capsule_visibility.assert_called_with(capsule_id, True)
        self.mock_context_engine.publish_context_update.assert_called()
        
        # Test non-existent capsule
        result = self.lifecycle_manager.resume_capsule("non_existent_capsule")
        self.assertFalse(result)

    def test_get_capsule_lifecycle_status(self):
        """Test getting capsule lifecycle status."""
        capsule_id = "capsule_031"
        capsule_type = "workflow"
        capsule_config = {"name": "Status Test Workflow", "workflow_id": "workflow_003"}
        
        # Create capsule first
        self.lifecycle_manager.initialize_capsule_lifecycle(capsule_id, capsule_type, capsule_config)
        
        status = self.lifecycle_manager.get_capsule_lifecycle_status(capsule_id)
        self.assertEqual(status, "created")
        
        # Suspend capsule
        self.lifecycle_manager.suspend_capsule(capsule_id)
        status = self.lifecycle_manager.get_capsule_lifecycle_status(capsule_id)
        self.assertEqual(status, "suspended")
        
        # Test non-existent capsule
        with self.assertRaises(KeyError):
            self.lifecycle_manager.get_capsule_lifecycle_status("non_existent_capsule")


if __name__ == '__main__':
    unittest.main()
