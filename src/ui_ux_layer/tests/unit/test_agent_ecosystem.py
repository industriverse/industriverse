"""
Unit tests for the Agent Ecosystem components.

This test suite validates the core functionality of the Agent Ecosystem,
including avatar management, expression, state visualization, personality,
and interaction protocols.

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
from core.agent_ecosystem.avatar_manager import AvatarManager
from core.agent_ecosystem.avatar_expression_engine import AvatarExpressionEngine
from core.agent_ecosystem.agent_state_visualizer import AgentStateVisualizer
from core.agent_ecosystem.avatar_personality_engine import AvatarPersonalityEngine
from core.agent_ecosystem.agent_interaction_protocol import AgentInteractionProtocol
from core.context_engine.context_engine import ContextEngine
from core.rendering_engine.rendering_engine import RenderingEngine


class TestAgentEcosystem(unittest.TestCase):
    """Test cases for the Agent Ecosystem components."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mocks for dependencies
        self.mock_context_engine = MagicMock(spec=ContextEngine)
        self.mock_rendering_engine = MagicMock(spec=RenderingEngine)
        
        # Create test configuration
        self.test_config = {
            "avatar_styles": {
                "industrial": {
                    "base_model": "robot_v1",
                    "texture_set": "metal",
                    "animation_set": "functional"
                },
                "organic": {
                    "base_model": "humanoid_v2",
                    "texture_set": "skin_tones",
                    "animation_set": "expressive"
                }
            },
            "default_avatar_style": "industrial",
            "personality_profiles": {
                "helpful_assistant": {
                    "traits": {"openness": 0.8, "conscientiousness": 0.9, "extraversion": 0.6, "agreeableness": 0.9, "neuroticism": 0.2},
                    "communication_style": "polite_informative",
                    "decision_making": "cautious_collaborative"
                },
                "analytical_expert": {
                    "traits": {"openness": 0.9, "conscientiousness": 0.8, "extraversion": 0.3, "agreeableness": 0.4, "neuroticism": 0.3},
                    "communication_style": "direct_concise",
                    "decision_making": "data_driven_logical"
                }
            },
            "default_personality": "helpful_assistant",
            "state_visualizations": {
                "idle": {"color": "#cccccc", "icon": "idle.svg", "animation": "breathing"},
                "working": {"color": "#007bff", "icon": "working.svg", "animation": "processing"},
                "error": {"color": "#dc3545", "icon": "error.svg", "animation": "alert"},
                "success": {"color": "#28a745", "icon": "success.svg", "animation": "celebrate"}
            },
            "interaction_protocol_version": "1.0"
        }
        
        # Create instances of components
        self.avatar_manager = AvatarManager(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )
        self.expression_engine = AvatarExpressionEngine(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )
        self.state_visualizer = AgentStateVisualizer(
            context_engine=self.mock_context_engine,
            rendering_engine=self.mock_rendering_engine,
            config=self.test_config
        )
        self.personality_engine = AvatarPersonalityEngine(
            context_engine=self.mock_context_engine,
            config=self.test_config
        )
        self.interaction_protocol = AgentInteractionProtocol(
            context_engine=self.mock_context_engine,
            config=self.test_config
        )

    # --- AvatarManager Tests --- 

    def test_avatar_manager_initialization(self):
        """Test AvatarManager initialization."""
        self.assertEqual(self.avatar_manager.config["default_avatar_style"], "industrial")
        self.assertEqual(len(self.avatar_manager.avatars), 0)

    def test_create_avatar(self):
        """Test creating an avatar."""
        avatar_id = "agent_001"
        avatar_config = {"style": "organic", "personality": "analytical_expert"}
        self.avatar_manager.create_avatar(avatar_id, avatar_config)
        
        self.assertIn(avatar_id, self.avatar_manager.avatars)
        self.assertEqual(self.avatar_manager.avatars[avatar_id]["style"], "organic")
        self.assertEqual(self.avatar_manager.avatars[avatar_id]["personality"], "analytical_expert")
        self.mock_rendering_engine.load_avatar_assets.assert_called_with(avatar_id, self.test_config["avatar_styles"]["organic"])
        self.mock_context_engine.publish_context_update.assert_called()

    def test_get_avatar_info(self):
        """Test getting avatar information."""
        avatar_id = "agent_002"
        avatar_config = {"style": "industrial", "personality": "helpful_assistant"}
        self.avatar_manager.create_avatar(avatar_id, avatar_config)
        
        info = self.avatar_manager.get_avatar_info(avatar_id)
        self.assertEqual(info["style"], "industrial")
        self.assertEqual(info["personality"], "helpful_assistant")
        
        with self.assertRaises(KeyError):
            self.avatar_manager.get_avatar_info("non_existent_agent")

    def test_update_avatar_style(self):
        """Test updating avatar style."""
        avatar_id = "agent_003"
        self.avatar_manager.create_avatar(avatar_id, {})
        self.avatar_manager.update_avatar_style(avatar_id, "organic")
        
        self.assertEqual(self.avatar_manager.avatars[avatar_id]["style"], "organic")
        self.mock_rendering_engine.update_avatar_style.assert_called_with(avatar_id, self.test_config["avatar_styles"]["organic"])
        self.mock_context_engine.publish_context_update.assert_called()

    def test_remove_avatar(self):
        """Test removing an avatar."""
        avatar_id = "agent_004"
        self.avatar_manager.create_avatar(avatar_id, {})
        self.avatar_manager.remove_avatar(avatar_id)
        
        self.assertNotIn(avatar_id, self.avatar_manager.avatars)
        self.mock_rendering_engine.unload_avatar_assets.assert_called_with(avatar_id)
        self.mock_context_engine.publish_context_update.assert_called()

    # --- AvatarExpressionEngine Tests --- 

    def test_expression_engine_initialization(self):
        """Test AvatarExpressionEngine initialization."""
        # No specific state to check beyond successful instantiation
        self.assertIsNotNone(self.expression_engine)

    def test_set_expression(self):
        """Test setting avatar expression."""
        avatar_id = "agent_005"
        expression = "happy"
        intensity = 0.8
        self.expression_engine.set_expression(avatar_id, expression, intensity)
        
        self.mock_rendering_engine.set_avatar_expression.assert_called_with(avatar_id, expression, intensity)
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "avatar_expression_change",
            "data": {"agent_id": avatar_id, "expression": expression, "intensity": intensity}
        })

    def test_play_animation(self):
        """Test playing avatar animation."""
        avatar_id = "agent_006"
        animation_name = "wave"
        loop = False
        self.expression_engine.play_animation(avatar_id, animation_name, loop)
        
        self.mock_rendering_engine.play_avatar_animation.assert_called_with(avatar_id, animation_name, loop)
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "avatar_animation_play",
            "data": {"agent_id": avatar_id, "animation": animation_name, "loop": loop}
        })

    def test_speak(self):
        """Test avatar speaking action."""
        avatar_id = "agent_007"
        text = "Hello, world!"
        audio_url = "/path/to/audio.mp3"
        self.expression_engine.speak(avatar_id, text, audio_url)
        
        self.mock_rendering_engine.play_avatar_speech.assert_called_with(avatar_id, text, audio_url)
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "avatar_speak",
            "data": {"agent_id": avatar_id, "text": text, "audio_url": audio_url}
        })

    # --- AgentStateVisualizer Tests --- 

    def test_state_visualizer_initialization(self):
        """Test AgentStateVisualizer initialization."""
        self.assertEqual(len(self.state_visualizer.config["state_visualizations"]), 4)

    def test_update_agent_state(self):
        """Test updating agent state visualization."""
        avatar_id = "agent_008"
        state = "working"
        self.state_visualizer.update_agent_state(avatar_id, state)
        
        expected_viz_config = self.test_config["state_visualizations"][state]
        self.mock_rendering_engine.update_agent_state_visualization.assert_called_with(avatar_id, state, expected_viz_config)
        self.mock_context_engine.publish_context_update.assert_called_with({
            "type": "agent_state_change",
            "data": {"agent_id": avatar_id, "state": state, "visualization": expected_viz_config}
        })
        
        # Test invalid state
        with self.assertRaises(ValueError):
            self.state_visualizer.update_agent_state(avatar_id, "invalid_state")

    def test_get_state_visualization(self):
        """Test getting state visualization config."""
        state = "error"
        viz_config = self.state_visualizer.get_state_visualization(state)
        self.assertEqual(viz_config, self.test_config["state_visualizations"][state])
        
        with self.assertRaises(ValueError):
            self.state_visualizer.get_state_visualization("invalid_state")

    # --- AvatarPersonalityEngine Tests --- 

    def test_personality_engine_initialization(self):
        """Test AvatarPersonalityEngine initialization."""
        self.assertEqual(self.personality_engine.config["default_personality"], "helpful_assistant")

    def test_get_personality_profile(self):
        """Test getting personality profile."""
        profile_name = "analytical_expert"
        profile = self.personality_engine.get_personality_profile(profile_name)
        self.assertEqual(profile, self.test_config["personality_profiles"][profile_name])
        
        with self.assertRaises(ValueError):
            self.personality_engine.get_personality_profile("invalid_profile")

    def test_generate_response_style(self):
        """Test generating response style based on personality."""
        profile_name = "helpful_assistant"
        context = {"user_query": "What is the status?", "sentiment": "neutral"}
        response_style = self.personality_engine.generate_response_style(profile_name, context)
        
        # Basic check, more complex logic would require more detailed tests
        self.assertIn("tone", response_style)
        self.assertIn("formality", response_style)
        self.assertIn("verbosity", response_style)
        self.assertEqual(response_style["communication_style"], "polite_informative")

    def test_determine_action_preference(self):
        """Test determining action preference based on personality."""
        profile_name = "analytical_expert"
        options = ["option_a", "option_b"]
        context = {"risk_level": "low"}
        preference = self.personality_engine.determine_action_preference(profile_name, options, context)
        
        # Basic check, more complex logic would require more detailed tests
        self.assertIn(preference, options)

    # --- AgentInteractionProtocol Tests --- 

    def test_interaction_protocol_initialization(self):
        """Test AgentInteractionProtocol initialization."""
        self.assertEqual(self.interaction_protocol.config["interaction_protocol_version"], "1.0")

    def test_format_message(self):
        """Test formatting a message according to the protocol."""
        sender_id = "agent_009"
        receiver_id = "agent_010"
        message_type = "task_request"
        payload = {"task_id": "task_123", "description": "Process data"}
        
        formatted_message = self.interaction_protocol.format_message(sender_id, receiver_id, message_type, payload)
        
        self.assertEqual(formatted_message["protocol_version"], "1.0")
        self.assertEqual(formatted_message["sender_id"], sender_id)
        self.assertEqual(formatted_message["receiver_id"], receiver_id)
        self.assertEqual(formatted_message["message_type"], message_type)
        self.assertEqual(formatted_message["payload"], payload)
        self.assertIn("timestamp", formatted_message)

    def test_parse_message(self):
        """Test parsing a message according to the protocol."""
        raw_message = {
            "protocol_version": "1.0",
            "sender_id": "agent_011",
            "receiver_id": "agent_012",
            "message_type": "status_update",
            "payload": {"status": "completed", "result": "success"},
            "timestamp": "2025-05-23T11:00:00Z"
        }
        
        parsed_data = self.interaction_protocol.parse_message(raw_message)
        
        self.assertEqual(parsed_data["sender_id"], "agent_011")
        self.assertEqual(parsed_data["message_type"], "status_update")
        self.assertEqual(parsed_data["payload"]["status"], "completed")
        
        # Test invalid version
        raw_message["protocol_version"] = "2.0"
        with self.assertRaises(ValueError):
            self.interaction_protocol.parse_message(raw_message)
            
        # Test missing field
        del raw_message["sender_id"]
        raw_message["protocol_version"] = "1.0" # Reset version
        with self.assertRaises(KeyError):
            self.interaction_protocol.parse_message(raw_message)

    def test_validate_message(self):
        """Test validating a message structure."""
        valid_message = {
            "protocol_version": "1.0",
            "sender_id": "agent_013",
            "receiver_id": "agent_014",
            "message_type": "query",
            "payload": {"query": "Get data"},
            "timestamp": "2025-05-23T11:05:00Z"
        }
        self.assertTrue(self.interaction_protocol.validate_message(valid_message))
        
        invalid_message = {
            "protocol_version": "1.0",
            "sender_id": "agent_013",
            # Missing receiver_id
            "message_type": "query",
            "payload": {"query": "Get data"},
            "timestamp": "2025-05-23T11:05:00Z"
        }
        self.assertFalse(self.interaction_protocol.validate_message(invalid_message))


if __name__ == '__main__':
    unittest.main()
