"""
Unit tests for the Context Engine components.

This test suite validates the core functionality of the Context Engine,
including context awareness, rules processing, and integration with other components.

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
from core.context_engine.context_engine import ContextEngine
from core.context_engine.context_awareness_engine import ContextAwarenessEngine
from core.context_engine.context_rules_engine import ContextRulesEngine
from core.context_engine.context_integration_bridge import ContextIntegrationBridge


class TestContextEngine(unittest.TestCase):
    """Test cases for the Context Engine components."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test configuration
        self.test_config = {
            "context_sources": {
                "user": {
                    "enabled": True,
                    "priority": 10,
                    "properties": ["role", "preferences", "history", "permissions"]
                },
                "device": {
                    "enabled": True,
                    "priority": 8,
                    "properties": ["type", "screen", "input", "network", "battery"]
                },
                "environment": {
                    "enabled": True,
                    "priority": 6,
                    "properties": ["location", "time", "noise_level", "light_level"]
                },
                "application": {
                    "enabled": True,
                    "priority": 9,
                    "properties": ["state", "active_view", "notifications", "errors"]
                },
                "workflow": {
                    "enabled": True,
                    "priority": 7,
                    "properties": ["active_workflows", "pending_tasks", "completed_tasks"]
                }
            },
            "rules_config": {
                "rule_sets": {
                    "device_adaptation": {
                        "enabled": True,
                        "priority": 10
                    },
                    "user_personalization": {
                        "enabled": True,
                        "priority": 9
                    },
                    "workflow_optimization": {
                        "enabled": True,
                        "priority": 8
                    },
                    "security": {
                        "enabled": True,
                        "priority": 11
                    }
                },
                "default_actions": {
                    "notification": {"type": "notification", "priority": "normal"},
                    "layout_change": {"type": "layout_change", "animate": True},
                    "theme_change": {"type": "theme_change", "animate": True}
                }
            },
            "integration_config": {
                "mcp_enabled": True,
                "a2a_enabled": True,
                "external_services": {
                    "weather": {"enabled": True, "refresh_interval": 3600},
                    "calendar": {"enabled": True, "refresh_interval": 300},
                    "notifications": {"enabled": True, "refresh_interval": 60}
                },
                "sync_interval": 5000
            },
            "persistence": {
                "enabled": True,
                "storage_type": "local",
                "sync_interval": 30000
            }
        }
        
        # Create mocks for dependencies
        self.mock_event_bus = MagicMock()
        
        # Create instances of components
        self.context_engine = ContextEngine(
            config=self.test_config,
            event_bus=self.mock_event_bus
        )
        self.awareness_engine = ContextAwarenessEngine(
            config=self.test_config["context_sources"],
            context_engine=self.context_engine
        )
        self.rules_engine = ContextRulesEngine(
            config=self.test_config["rules_config"],
            context_engine=self.context_engine
        )
        self.integration_bridge = ContextIntegrationBridge(
            config=self.test_config["integration_config"],
            context_engine=self.context_engine
        )

    # --- ContextEngine Tests ---

    def test_context_engine_initialization(self):
        """Test ContextEngine initialization."""
        self.assertEqual(len(self.context_engine.context_data), 0)
        self.assertEqual(self.context_engine.config["persistence"]["storage_type"], "local")

    def test_register_context_provider(self):
        """Test registering a context provider."""
        provider_id = "test_provider"
        provider_config = {"priority": 5, "properties": ["test1", "test2"]}
        mock_provider = MagicMock()
        
        self.context_engine.register_context_provider(provider_id, provider_config, mock_provider)
        
        self.assertIn(provider_id, self.context_engine.context_providers)
        self.assertEqual(self.context_engine.context_providers[provider_id]["instance"], mock_provider)
        self.assertEqual(self.context_engine.context_providers[provider_id]["config"], provider_config)

    def test_register_context_consumer(self):
        """Test registering a context consumer."""
        consumer_id = "test_consumer"
        consumer_config = {"subscriptions": ["user", "device"]}
        mock_consumer = MagicMock()
        
        self.context_engine.register_context_consumer(consumer_id, consumer_config, mock_consumer)
        
        self.assertIn(consumer_id, self.context_engine.context_consumers)
        self.assertEqual(self.context_engine.context_consumers[consumer_id]["instance"], mock_consumer)
        self.assertEqual(self.context_engine.context_consumers[consumer_id]["config"], consumer_config)

    def test_update_context(self):
        """Test updating context data."""
        source = "user"
        context_data = {"role": "process_handler", "preferences": {"theme": "dark"}}
        
        self.context_engine.update_context(source, context_data)
        
        self.assertIn(source, self.context_engine.context_data)
        self.assertEqual(self.context_engine.context_data[source]["role"], "process_handler")
        self.assertEqual(self.context_engine.context_data[source]["preferences"]["theme"], "dark")
        
        # Test partial update
        partial_update = {"preferences": {"language": "en"}}
        self.context_engine.update_context(source, partial_update)
        
        self.assertEqual(self.context_engine.context_data[source]["role"], "process_handler")  # Unchanged
        self.assertEqual(self.context_engine.context_data[source]["preferences"]["theme"], "dark")  # Unchanged
        self.assertEqual(self.context_engine.context_data[source]["preferences"]["language"], "en")  # Added

    def test_get_context(self):
        """Test getting context data."""
        # Set up some context data
        self.context_engine.update_context("user", {"role": "domain_expert"})
        self.context_engine.update_context("device", {"type": "tablet"})
        
        # Get specific context
        user_context = self.context_engine.get_context("user")
        self.assertEqual(user_context["role"], "domain_expert")
        
        # Get all context
        all_context = self.context_engine.get_context()
        self.assertEqual(all_context["user"]["role"], "domain_expert")
        self.assertEqual(all_context["device"]["type"], "tablet")
        
        # Get non-existent context
        empty_context = self.context_engine.get_context("non_existent")
        self.assertEqual(empty_context, {})

    def test_publish_context_update(self):
        """Test publishing context updates."""
        update_data = {
            "type": "role_change",
            "data": {"role": "master"}
        }
        
        self.context_engine.publish_context_update(update_data)
        
        # Verify event bus was called
        self.mock_event_bus.publish.assert_called_with("context_update", update_data)
        
        # Register a consumer and test notification
        consumer_id = "test_consumer"
        consumer_config = {"subscriptions": ["user"]}
        mock_consumer = MagicMock()
        
        self.context_engine.register_context_consumer(consumer_id, consumer_config, mock_consumer)
        
        # Update related to subscribed source
        self.context_engine.update_context("user", {"role": "master"})
        
        # Consumer should be notified
        mock_consumer.on_context_update.assert_called()

    def test_save_and_load_context(self):
        """Test saving and loading context."""
        # Set up some context data
        self.context_engine.update_context("user", {"role": "process_handler"})
        self.context_engine.update_context("device", {"type": "desktop"})
        
        # Mock storage functions
        with patch.object(self.context_engine, '_save_to_storage') as mock_save:
            with patch.object(self.context_engine, '_load_from_storage', return_value={
                "user": {"role": "domain_expert"},
                "device": {"type": "tablet"}
            }) as mock_load:
                
                # Test save
                self.context_engine.save_context()
                mock_save.assert_called_with(self.context_engine.context_data)
                
                # Test load
                self.context_engine.load_context()
                mock_load.assert_called()
                
                # Verify loaded data
                self.assertEqual(self.context_engine.context_data["user"]["role"], "domain_expert")
                self.assertEqual(self.context_engine.context_data["device"]["type"], "tablet")

    # --- ContextAwarenessEngine Tests ---

    def test_awareness_engine_initialization(self):
        """Test ContextAwarenessEngine initialization."""
        self.assertEqual(len(self.awareness_engine.config), 5)  # 5 context sources
        self.assertEqual(self.awareness_engine.config["user"]["priority"], 10)

    def test_collect_context_from_source(self):
        """Test collecting context from a source."""
        source = "device"
        mock_collector = MagicMock(return_value={
            "type": "tablet",
            "screen": {"width": 768, "height": 1024},
            "input": {"touch": True}
        })
        
        self.awareness_engine.register_collector(source, mock_collector)
        context = self.awareness_engine.collect_context_from_source(source)
        
        self.assertEqual(context["type"], "tablet")
        self.assertEqual(context["screen"]["width"], 768)
        mock_collector.assert_called_once()
        
        # Test non-existent source
        with self.assertRaises(ValueError):
            self.awareness_engine.collect_context_from_source("non_existent")

    def test_collect_all_context(self):
        """Test collecting context from all sources."""
        # Register mock collectors
        self.awareness_engine.register_collector("user", MagicMock(return_value={"role": "master"}))
        self.awareness_engine.register_collector("device", MagicMock(return_value={"type": "desktop"}))
        
        self.awareness_engine.collect_all_context()
        
        # Verify context engine was updated
        self.context_engine.update_context.assert_any_call("user", {"role": "master"})
        self.context_engine.update_context.assert_any_call("device", {"type": "desktop"})

    def test_register_collector(self):
        """Test registering a context collector."""
        source = "environment"
        mock_collector = MagicMock()
        
        self.awareness_engine.register_collector(source, mock_collector)
        
        self.assertIn(source, self.awareness_engine.collectors)
        self.assertEqual(self.awareness_engine.collectors[source], mock_collector)
        
        # Test invalid source
        with self.assertRaises(ValueError):
            self.awareness_engine.register_collector("invalid_source", mock_collector)

    def test_get_source_priority(self):
        """Test getting source priority."""
        self.assertEqual(self.awareness_engine.get_source_priority("user"), 10)
        self.assertEqual(self.awareness_engine.get_source_priority("workflow"), 7)
        
        # Test non-existent source
        with self.assertRaises(ValueError):
            self.awareness_engine.get_source_priority("non_existent")

    def test_is_source_enabled(self):
        """Test checking if a source is enabled."""
        self.assertTrue(self.awareness_engine.is_source_enabled("user"))
        
        # Disable a source
        self.awareness_engine.config["workflow"]["enabled"] = False
        self.assertFalse(self.awareness_engine.is_source_enabled("workflow"))
        
        # Test non-existent source
        with self.assertRaises(ValueError):
            self.awareness_engine.is_source_enabled("non_existent")

    # --- ContextRulesEngine Tests ---

    def test_rules_engine_initialization(self):
        """Test ContextRulesEngine initialization."""
        self.assertEqual(len(self.rules_engine.config["rule_sets"]), 4)
        self.assertEqual(self.rules_engine.config["rule_sets"]["security"]["priority"], 11)

    def test_register_rule(self):
        """Test registering a rule."""
        rule_set = "device_adaptation"
        rule_id = "mobile_layout"
        rule_config = {
            "conditions": [{"source": "device", "property": "type", "operator": "equals", "value": "mobile"}],
            "actions": [{"type": "layout_change", "layout": "compact"}],
            "priority": 5
        }
        
        self.rules_engine.register_rule(rule_set, rule_id, rule_config)
        
        self.assertIn(rule_set, self.rules_engine.rules)
        self.assertIn(rule_id, self.rules_engine.rules[rule_set])
        self.assertEqual(self.rules_engine.rules[rule_set][rule_id], rule_config)
        
        # Test invalid rule set
        with self.assertRaises(ValueError):
            self.rules_engine.register_rule("invalid_rule_set", rule_id, rule_config)

    def test_evaluate_condition(self):
        """Test evaluating a condition."""
        # Set up context
        self.context_engine.update_context("device", {"type": "mobile", "screen": {"width": 375}})
        
        # Test equals operator
        condition = {"source": "device", "property": "type", "operator": "equals", "value": "mobile"}
        self.assertTrue(self.rules_engine.evaluate_condition(condition))
        
        # Test not_equals operator
        condition = {"source": "device", "property": "type", "operator": "not_equals", "value": "desktop"}
        self.assertTrue(self.rules_engine.evaluate_condition(condition))
        
        # Test greater_than operator
        condition = {"source": "device", "property": "screen.width", "operator": "greater_than", "value": 300}
        self.assertTrue(self.rules_engine.evaluate_condition(condition))
        
        # Test less_than operator
        condition = {"source": "device", "property": "screen.width", "operator": "less_than", "value": 400}
        self.assertTrue(self.rules_engine.evaluate_condition(condition))
        
        # Test contains operator
        self.context_engine.update_context("user", {"permissions": ["view", "edit"]})
        condition = {"source": "user", "property": "permissions", "operator": "contains", "value": "edit"}
        self.assertTrue(self.rules_engine.evaluate_condition(condition))
        
        # Test not_contains operator
        condition = {"source": "user", "property": "permissions", "operator": "not_contains", "value": "delete"}
        self.assertTrue(self.rules_engine.evaluate_condition(condition))
        
        # Test property not found
        condition = {"source": "device", "property": "non_existent", "operator": "equals", "value": "mobile"}
        self.assertFalse(self.rules_engine.evaluate_condition(condition))
        
        # Test invalid operator
        condition = {"source": "device", "property": "type", "operator": "invalid_operator", "value": "mobile"}
        with self.assertRaises(ValueError):
            self.rules_engine.evaluate_condition(condition)

    def test_evaluate_rule(self):
        """Test evaluating a rule."""
        # Set up context
        self.context_engine.update_context("device", {"type": "tablet", "screen": {"width": 768}})
        self.context_engine.update_context("user", {"role": "domain_expert"})
        
        # Create a rule with multiple conditions (all must be true)
        rule = {
            "conditions": [
                {"source": "device", "property": "type", "operator": "equals", "value": "tablet"},
                {"source": "user", "property": "role", "operator": "equals", "value": "domain_expert"}
            ],
            "actions": [{"type": "layout_change", "layout": "standard"}],
            "priority": 5
        }
        
        result = self.rules_engine.evaluate_rule(rule)
        self.assertTrue(result)
        
        # Test with one false condition
        rule["conditions"][1]["value"] = "master"
        result = self.rules_engine.evaluate_rule(rule)
        self.assertFalse(result)

    def test_execute_action(self):
        """Test executing an action."""
        # Test layout change action
        action = {"type": "layout_change", "layout": "compact"}
        self.rules_engine.execute_action(action)
        self.context_engine.publish_context_update.assert_called_with({
            "type": "layout_change",
            "data": {"layout": "compact", "animate": True}
        })
        
        # Test notification action
        action = {"type": "notification", "message": "Test notification"}
        self.rules_engine.execute_action(action)
        self.context_engine.publish_context_update.assert_called_with({
            "type": "notification",
            "data": {"message": "Test notification", "priority": "normal"}
        })
        
        # Test custom action
        action = {"type": "custom_action", "custom_data": "test"}
        self.rules_engine.execute_action(action)
        self.context_engine.publish_context_update.assert_called_with({
            "type": "custom_action",
            "data": {"custom_data": "test"}
        })

    def test_process_rules(self):
        """Test processing all rules."""
        # Set up context
        self.context_engine.update_context("device", {"type": "mobile"})
        self.context_engine.update_context("user", {"role": "process_handler"})
        
        # Register rules
        rule_set = "device_adaptation"
        rule_id1 = "mobile_layout"
        rule1 = {
            "conditions": [{"source": "device", "property": "type", "operator": "equals", "value": "mobile"}],
            "actions": [{"type": "layout_change", "layout": "compact"}],
            "priority": 5
        }
        rule_id2 = "process_handler_view"
        rule2 = {
            "conditions": [{"source": "user", "property": "role", "operator": "equals", "value": "process_handler"}],
            "actions": [{"type": "view_change", "view": "process"}],
            "priority": 4
        }
        
        self.rules_engine.register_rule(rule_set, rule_id1, rule1)
        self.rules_engine.register_rule(rule_set, rule_id2, rule2)
        
        # Process rules
        self.rules_engine.process_rules()
        
        # Both actions should be executed
        self.context_engine.publish_context_update.assert_any_call({
            "type": "layout_change",
            "data": {"layout": "compact", "animate": True}
        })
        self.context_engine.publish_context_update.assert_any_call({
            "type": "view_change",
            "data": {"view": "process"}
        })

    # --- ContextIntegrationBridge Tests ---

    def test_integration_bridge_initialization(self):
        """Test ContextIntegrationBridge initialization."""
        self.assertTrue(self.integration_bridge.config["mcp_enabled"])
        self.assertTrue(self.integration_bridge.config["a2a_enabled"])
        self.assertEqual(len(self.integration_bridge.config["external_services"]), 3)

    def test_register_external_service(self):
        """Test registering an external service."""
        service_id = "traffic"
        service_config = {"enabled": True, "refresh_interval": 900}
        mock_service = MagicMock()
        
        self.integration_bridge.register_external_service(service_id, service_config, mock_service)
        
        self.assertIn(service_id, self.integration_bridge.external_services)
        self.assertEqual(self.integration_bridge.external_services[service_id]["instance"], mock_service)
        self.assertEqual(self.integration_bridge.external_services[service_id]["config"], service_config)

    def test_fetch_external_service_data(self):
        """Test fetching data from an external service."""
        service_id = "weather"
        mock_service = MagicMock()
        mock_service.fetch_data.return_value = {"temperature": 22, "condition": "sunny"}
        
        self.integration_bridge.register_external_service(
            service_id, 
            self.test_config["integration_config"]["external_services"][service_id],
            mock_service
        )
        
        data = self.integration_bridge.fetch_external_service_data(service_id)
        
        self.assertEqual(data["temperature"], 22)
        self.assertEqual(data["condition"], "sunny")
        mock_service.fetch_data.assert_called_once()
        
        # Test non-existent service
        with self.assertRaises(KeyError):
            self.integration_bridge.fetch_external_service_data("non_existent")

    def test_sync_all_external_services(self):
        """Test syncing all external services."""
        # Register mock services
        weather_service = MagicMock()
        weather_service.fetch_data.return_value = {"temperature": 22}
        
        calendar_service = MagicMock()
        calendar_service.fetch_data.return_value = {"events": ["meeting"]}
        
        self.integration_bridge.register_external_service(
            "weather", 
            self.test_config["integration_config"]["external_services"]["weather"],
            weather_service
        )
        self.integration_bridge.register_external_service(
            "calendar", 
            self.test_config["integration_config"]["external_services"]["calendar"],
            calendar_service
        )
        
        self.integration_bridge.sync_all_external_services()
        
        # Verify services were called
        weather_service.fetch_data.assert_called_once()
        calendar_service.fetch_data.assert_called_once()
        
        # Verify context was updated
        self.context_engine.update_context.assert_any_call("external_weather", {"temperature": 22})
        self.context_engine.update_context.assert_any_call("external_calendar", {"events": ["meeting"]})

    def test_format_mcp_message(self):
        """Test formatting an MCP message."""
        context_data = {"user": {"role": "master"}, "device": {"type": "desktop"}}
        
        mcp_message = self.integration_bridge.format_mcp_message(context_data)
        
        self.assertEqual(mcp_message["protocol"], "mcp")
        self.assertEqual(mcp_message["version"], "1.0")
        self.assertEqual(mcp_message["data"]["user"]["role"], "master")
        self.assertEqual(mcp_message["data"]["device"]["type"], "desktop")
        self.assertIn("timestamp", mcp_message)

    def test_parse_mcp_message(self):
        """Test parsing an MCP message."""
        mcp_message = {
            "protocol": "mcp",
            "version": "1.0",
            "data": {
                "workflow": {"status": "running"},
                "agent": {"state": "active"}
            },
            "timestamp": "2025-05-23T11:45:00Z"
        }
        
        context_data = self.integration_bridge.parse_mcp_message(mcp_message)
        
        self.assertEqual(context_data["workflow"]["status"], "running")
        self.assertEqual(context_data["agent"]["state"], "active")
        
        # Test invalid protocol
        invalid_message = mcp_message.copy()
        invalid_message["protocol"] = "invalid"
        with self.assertRaises(ValueError):
            self.integration_bridge.parse_mcp_message(invalid_message)
        
        # Test invalid version
        invalid_message = mcp_message.copy()
        invalid_message["version"] = "2.0"
        with self.assertRaises(ValueError):
            self.integration_bridge.parse_mcp_message(invalid_message)

    def test_format_a2a_message(self):
        """Test formatting an A2A message."""
        agent_id = "agent_001"
        context_data = {"role": "assistant", "capabilities": ["search", "calculate"]}
        
        a2a_message = self.integration_bridge.format_a2a_message(agent_id, context_data)
        
        self.assertEqual(a2a_message["protocol"], "a2a")
        self.assertEqual(a2a_message["version"], "1.0")
        self.assertEqual(a2a_message["agent_id"], agent_id)
        self.assertEqual(a2a_message["data"]["role"], "assistant")
        self.assertEqual(a2a_message["data"]["capabilities"], ["search", "calculate"])
        self.assertIn("timestamp", a2a_message)
        self.assertIn("industryTags", a2a_message)  # A2A Protocol enhancement

    def test_parse_a2a_message(self):
        """Test parsing an A2A message."""
        a2a_message = {
            "protocol": "a2a",
            "version": "1.0",
            "agent_id": "agent_002",
            "data": {
                "role": "expert",
                "domain": "manufacturing"
            },
            "industryTags": ["manufacturing", "automation"],
            "timestamp": "2025-05-23T11:50:00Z"
        }
        
        agent_id, context_data = self.integration_bridge.parse_a2a_message(a2a_message)
        
        self.assertEqual(agent_id, "agent_002")
        self.assertEqual(context_data["role"], "expert")
        self.assertEqual(context_data["domain"], "manufacturing")
        self.assertEqual(context_data["industryTags"], ["manufacturing", "automation"])
        
        # Test invalid protocol
        invalid_message = a2a_message.copy()
        invalid_message["protocol"] = "invalid"
        with self.assertRaises(ValueError):
            self.integration_bridge.parse_a2a_message(invalid_message)
        
        # Test invalid version
        invalid_message = a2a_message.copy()
        invalid_message["version"] = "2.0"
        with self.assertRaises(ValueError):
            self.integration_bridge.parse_a2a_message(invalid_message)

    def test_handle_incoming_mcp_message(self):
        """Test handling an incoming MCP message."""
        mcp_message = {
            "protocol": "mcp",
            "version": "1.0",
            "data": {
                "workflow": {"status": "completed"},
                "agent": {"state": "idle"}
            },
            "timestamp": "2025-05-23T11:55:00Z"
        }
        
        self.integration_bridge.handle_incoming_mcp_message(mcp_message)
        
        # Verify context was updated
        self.context_engine.update_context.assert_any_call("workflow", {"status": "completed"})
        self.context_engine.update_context.assert_any_call("agent", {"state": "idle"})

    def test_handle_incoming_a2a_message(self):
        """Test handling an incoming A2A message."""
        a2a_message = {
            "protocol": "a2a",
            "version": "1.0",
            "agent_id": "agent_003",
            "data": {
                "task": "analyze_data",
                "status": "in_progress"
            },
            "industryTags": ["energy", "optimization"],
            "timestamp": "2025-05-23T12:00:00Z"
        }
        
        self.integration_bridge.handle_incoming_a2a_message(a2a_message)
        
        # Verify context was updated
        self.context_engine.update_context.assert_called_with(
            "agent_agent_003", 
            {
                "task": "analyze_data", 
                "status": "in_progress",
                "industryTags": ["energy", "optimization"]
            }
        )


if __name__ == '__main__':
    unittest.main()
