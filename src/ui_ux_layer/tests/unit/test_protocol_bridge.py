"""
Unit tests for the Protocol Bridge components.

This test suite validates the core functionality of the Protocol Bridge,
including MCP and A2A protocol integration, message handling, and
cross-layer communication.

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
from core.protocol_bridge.protocol_bridge import ProtocolBridge
from core.protocol_bridge.mcp_integration_manager import MCPIntegrationManager
from core.protocol_bridge.a2a_integration_manager import A2AIntegrationManager
from core.context_engine.context_engine import ContextEngine


class TestProtocolBridge(unittest.TestCase):
    """Test cases for the Protocol Bridge components."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test configuration
        self.test_config = {
            "mcp_config": {
                "enabled": True,
                "version": "1.0",
                "endpoints": {
                    "core_ai": "http://core-ai-layer-service:8080/mcp",
                    "data": "http://data-layer-service:8080/mcp",
                    "generative": "http://generative-layer-service:8080/mcp",
                    "application": "http://application-layer-service:8080/mcp",
                    "workflow": "http://workflow-layer-service:8080/mcp"
                },
                "authentication": {
                    "type": "token",
                    "token_header": "X-MCP-Auth-Token"
                },
                "retry_policy": {
                    "max_retries": 3,
                    "retry_interval": 1000,
                    "backoff_factor": 2
                }
            },
            "a2a_config": {
                "enabled": True,
                "version": "1.0",
                "endpoints": {
                    "agent_directory": "http://agent-directory-service:8080/a2a",
                    "agent_runtime": "http://agent-runtime-service:8080/a2a"
                },
                "authentication": {
                    "type": "oauth2",
                    "token_endpoint": "http://auth-service:8080/oauth/token",
                    "client_id": "ui_ux_layer",
                    "scope": "a2a_api"
                },
                "industry_tags": ["manufacturing", "energy", "logistics", "retail"],
                "capabilities": {
                    "workflow_templates": True,
                    "multi_tenant_auth": True,
                    "schema_versioning": True,
                    "artifact_previews": True
                }
            },
            "message_handlers": {
                "mcp": {
                    "context_update": True,
                    "ui_update": True,
                    "agent_state": True,
                    "workflow_state": True,
                    "digital_twin_update": True
                },
                "a2a": {
                    "agent_discovery": True,
                    "task_lifecycle": True,
                    "collaboration": True,
                    "negotiation": True
                }
            },
            "security": {
                "message_validation": True,
                "encryption": {
                    "enabled": True,
                    "algorithm": "AES-256-GCM"
                },
                "rate_limiting": {
                    "enabled": True,
                    "max_requests_per_minute": 100
                }
            }
        }
        
        # Create mocks for dependencies
        self.mock_context_engine = MagicMock(spec=ContextEngine)
        self.mock_event_bus = MagicMock()
        
        # Create instances of components
        self.protocol_bridge = ProtocolBridge(
            config=self.test_config,
            context_engine=self.mock_context_engine,
            event_bus=self.mock_event_bus
        )
        self.mcp_manager = MCPIntegrationManager(
            config=self.test_config["mcp_config"],
            context_engine=self.mock_context_engine,
            event_bus=self.mock_event_bus
        )
        self.a2a_manager = A2AIntegrationManager(
            config=self.test_config["a2a_config"],
            context_engine=self.mock_context_engine,
            event_bus=self.mock_event_bus
        )

    # --- ProtocolBridge Tests ---

    def test_protocol_bridge_initialization(self):
        """Test ProtocolBridge initialization."""
        self.assertTrue(self.protocol_bridge.config["mcp_config"]["enabled"])
        self.assertTrue(self.protocol_bridge.config["a2a_config"]["enabled"])
        self.assertEqual(len(self.protocol_bridge.message_handlers), 0)

    def test_register_message_handler(self):
        """Test registering a message handler."""
        protocol = "mcp"
        message_type = "context_update"
        mock_handler = MagicMock()
        
        self.protocol_bridge.register_message_handler(protocol, message_type, mock_handler)
        
        self.assertIn(protocol, self.protocol_bridge.message_handlers)
        self.assertIn(message_type, self.protocol_bridge.message_handlers[protocol])
        self.assertEqual(self.protocol_bridge.message_handlers[protocol][message_type], mock_handler)

    def test_handle_incoming_message(self):
        """Test handling an incoming message."""
        # Register mock handlers
        mcp_handler = MagicMock()
        a2a_handler = MagicMock()
        self.protocol_bridge.register_message_handler("mcp", "context_update", mcp_handler)
        self.protocol_bridge.register_message_handler("a2a", "agent_discovery", a2a_handler)
        
        # Test MCP message
        mcp_message = {
            "protocol": "mcp",
            "version": "1.0",
            "type": "context_update",
            "data": {"context": "test"},
            "timestamp": "2025-05-23T12:05:00Z"
        }
        self.protocol_bridge.handle_incoming_message(mcp_message)
        mcp_handler.assert_called_with(mcp_message)
        
        # Test A2A message
        a2a_message = {
            "protocol": "a2a",
            "version": "1.0",
            "type": "agent_discovery",
            "data": {"agent": "test"},
            "timestamp": "2025-05-23T12:06:00Z"
        }
        self.protocol_bridge.handle_incoming_message(a2a_message)
        a2a_handler.assert_called_with(a2a_message)
        
        # Test unknown protocol
        unknown_message = {
            "protocol": "unknown",
            "version": "1.0",
            "type": "test",
            "data": {},
            "timestamp": "2025-05-23T12:07:00Z"
        }
        with self.assertRaises(ValueError):
            self.protocol_bridge.handle_incoming_message(unknown_message)
        
        # Test unknown message type
        unknown_type_message = {
            "protocol": "mcp",
            "version": "1.0",
            "type": "unknown_type",
            "data": {},
            "timestamp": "2025-05-23T12:08:00Z"
        }
        # Should not raise exception, just log warning
        self.protocol_bridge.handle_incoming_message(unknown_type_message)

    def test_send_message(self):
        """Test sending a message."""
        # Mock the send methods
        with patch.object(self.protocol_bridge, '_send_mcp_message') as mock_send_mcp:
            with patch.object(self.protocol_bridge, '_send_a2a_message') as mock_send_a2a:
                
                # Test MCP message
                mcp_message = {
                    "protocol": "mcp",
                    "version": "1.0",
                    "type": "ui_update",
                    "data": {"ui": "test"},
                    "timestamp": "2025-05-23T12:10:00Z"
                }
                self.protocol_bridge.send_message(mcp_message)
                mock_send_mcp.assert_called_with(mcp_message)
                
                # Test A2A message
                a2a_message = {
                    "protocol": "a2a",
                    "version": "1.0",
                    "type": "task_lifecycle",
                    "data": {"task": "test"},
                    "timestamp": "2025-05-23T12:11:00Z"
                }
                self.protocol_bridge.send_message(a2a_message)
                mock_send_a2a.assert_called_with(a2a_message)
                
                # Test unknown protocol
                unknown_message = {
                    "protocol": "unknown",
                    "version": "1.0",
                    "type": "test",
                    "data": {},
                    "timestamp": "2025-05-23T12:12:00Z"
                }
                with self.assertRaises(ValueError):
                    self.protocol_bridge.send_message(unknown_message)

    def test_validate_message(self):
        """Test validating a message."""
        # Valid message
        valid_message = {
            "protocol": "mcp",
            "version": "1.0",
            "type": "context_update",
            "data": {"context": "test"},
            "timestamp": "2025-05-23T12:15:00Z"
        }
        self.assertTrue(self.protocol_bridge.validate_message(valid_message))
        
        # Missing protocol
        invalid_message = {
            "version": "1.0",
            "type": "context_update",
            "data": {"context": "test"},
            "timestamp": "2025-05-23T12:16:00Z"
        }
        self.assertFalse(self.protocol_bridge.validate_message(invalid_message))
        
        # Missing version
        invalid_message = {
            "protocol": "mcp",
            "type": "context_update",
            "data": {"context": "test"},
            "timestamp": "2025-05-23T12:17:00Z"
        }
        self.assertFalse(self.protocol_bridge.validate_message(invalid_message))
        
        # Missing type
        invalid_message = {
            "protocol": "mcp",
            "version": "1.0",
            "data": {"context": "test"},
            "timestamp": "2025-05-23T12:18:00Z"
        }
        self.assertFalse(self.protocol_bridge.validate_message(invalid_message))
        
        # Missing data
        invalid_message = {
            "protocol": "mcp",
            "version": "1.0",
            "type": "context_update",
            "timestamp": "2025-05-23T12:19:00Z"
        }
        self.assertFalse(self.protocol_bridge.validate_message(invalid_message))

    # --- MCPIntegrationManager Tests ---

    def test_mcp_manager_initialization(self):
        """Test MCPIntegrationManager initialization."""
        self.assertTrue(self.mcp_manager.config["enabled"])
        self.assertEqual(self.mcp_manager.config["version"], "1.0")
        self.assertEqual(len(self.mcp_manager.config["endpoints"]), 5)

    def test_format_mcp_message(self):
        """Test formatting an MCP message."""
        message_type = "context_update"
        data = {"context": "test"}
        
        message = self.mcp_manager.format_mcp_message(message_type, data)
        
        self.assertEqual(message["protocol"], "mcp")
        self.assertEqual(message["version"], "1.0")
        self.assertEqual(message["type"], message_type)
        self.assertEqual(message["data"], data)
        self.assertIn("timestamp", message)
        self.assertIn("message_id", message)

    def test_parse_mcp_message(self):
        """Test parsing an MCP message."""
        message = {
            "protocol": "mcp",
            "version": "1.0",
            "type": "ui_update",
            "data": {"ui": "test"},
            "timestamp": "2025-05-23T12:20:00Z",
            "message_id": "123456"
        }
        
        parsed = self.mcp_manager.parse_mcp_message(message)
        
        self.assertEqual(parsed["type"], "ui_update")
        self.assertEqual(parsed["data"]["ui"], "test")
        
        # Test invalid protocol
        invalid_message = message.copy()
        invalid_message["protocol"] = "invalid"
        with self.assertRaises(ValueError):
            self.mcp_manager.parse_mcp_message(invalid_message)
        
        # Test invalid version
        invalid_message = message.copy()
        invalid_message["version"] = "2.0"
        with self.assertRaises(ValueError):
            self.mcp_manager.parse_mcp_message(invalid_message)

    def test_get_endpoint_for_message(self):
        """Test getting the endpoint for a message."""
        # Test core_ai endpoint
        message = {
            "protocol": "mcp",
            "version": "1.0",
            "type": "model_request",
            "data": {"model": "test"},
            "timestamp": "2025-05-23T12:25:00Z"
        }
        endpoint = self.mcp_manager.get_endpoint_for_message(message)
        self.assertEqual(endpoint, self.test_config["mcp_config"]["endpoints"]["core_ai"])
        
        # Test data endpoint
        message["type"] = "data_query"
        endpoint = self.mcp_manager.get_endpoint_for_message(message)
        self.assertEqual(endpoint, self.test_config["mcp_config"]["endpoints"]["data"])
        
        # Test workflow endpoint
        message["type"] = "workflow_state"
        endpoint = self.mcp_manager.get_endpoint_for_message(message)
        self.assertEqual(endpoint, self.test_config["mcp_config"]["endpoints"]["workflow"])
        
        # Test unknown type (default to core_ai)
        message["type"] = "unknown_type"
        endpoint = self.mcp_manager.get_endpoint_for_message(message)
        self.assertEqual(endpoint, self.test_config["mcp_config"]["endpoints"]["core_ai"])

    def test_add_authentication_to_headers(self):
        """Test adding authentication to headers."""
        headers = {}
        
        self.mcp_manager.add_authentication_to_headers(headers)
        
        self.assertIn(self.test_config["mcp_config"]["authentication"]["token_header"], headers)
        # In a real implementation, this would be a valid token

    def test_handle_mcp_message(self):
        """Test handling an MCP message."""
        message = {
            "protocol": "mcp",
            "version": "1.0",
            "type": "context_update",
            "data": {"context": {"user": {"role": "master"}}},
            "timestamp": "2025-05-23T12:30:00Z"
        }
        
        # Mock the context engine update method
        self.mcp_manager.handle_mcp_message(message)
        
        # Verify context engine was updated
        self.mock_context_engine.update_context.assert_called_with("user", {"role": "master"})
        
        # Test digital twin update
        message["type"] = "digital_twin_update"
        message["data"] = {"digital_twin": {"id": "twin_001", "state": "active"}}
        
        self.mcp_manager.handle_mcp_message(message)
        
        # Verify context engine was updated
        self.mock_context_engine.update_context.assert_called_with("digital_twin", {"id": "twin_001", "state": "active"})
        
        # Test workflow state
        message["type"] = "workflow_state"
        message["data"] = {"workflow": {"id": "workflow_001", "state": "running"}}
        
        self.mcp_manager.handle_mcp_message(message)
        
        # Verify context engine was updated
        self.mock_context_engine.update_context.assert_called_with("workflow", {"id": "workflow_001", "state": "running"})

    # --- A2AIntegrationManager Tests ---

    def test_a2a_manager_initialization(self):
        """Test A2AIntegrationManager initialization."""
        self.assertTrue(self.a2a_manager.config["enabled"])
        self.assertEqual(self.a2a_manager.config["version"], "1.0")
        self.assertEqual(len(self.a2a_manager.config["endpoints"]), 2)
        self.assertEqual(len(self.a2a_manager.config["industry_tags"]), 4)

    def test_format_a2a_message(self):
        """Test formatting an A2A message."""
        message_type = "agent_discovery"
        agent_id = "agent_001"
        data = {"capabilities": ["search", "calculate"]}
        
        message = self.a2a_manager.format_a2a_message(message_type, agent_id, data)
        
        self.assertEqual(message["protocol"], "a2a")
        self.assertEqual(message["version"], "1.0")
        self.assertEqual(message["type"], message_type)
        self.assertEqual(message["agent_id"], agent_id)
        self.assertEqual(message["data"], data)
        self.assertIn("timestamp", message)
        self.assertIn("message_id", message)
        self.assertIn("industryTags", message)  # A2A Protocol enhancement

    def test_parse_a2a_message(self):
        """Test parsing an A2A message."""
        message = {
            "protocol": "a2a",
            "version": "1.0",
            "type": "task_lifecycle",
            "agent_id": "agent_002",
            "data": {"task": "analyze_data", "status": "in_progress"},
            "industryTags": ["manufacturing", "automation"],
            "timestamp": "2025-05-23T12:35:00Z",
            "message_id": "123456"
        }
        
        parsed = self.a2a_manager.parse_a2a_message(message)
        
        self.assertEqual(parsed["type"], "task_lifecycle")
        self.assertEqual(parsed["agent_id"], "agent_002")
        self.assertEqual(parsed["data"]["task"], "analyze_data")
        self.assertEqual(parsed["industryTags"], ["manufacturing", "automation"])
        
        # Test invalid protocol
        invalid_message = message.copy()
        invalid_message["protocol"] = "invalid"
        with self.assertRaises(ValueError):
            self.a2a_manager.parse_a2a_message(invalid_message)
        
        # Test invalid version
        invalid_message = message.copy()
        invalid_message["version"] = "2.0"
        with self.assertRaises(ValueError):
            self.a2a_manager.parse_a2a_message(invalid_message)

    def test_get_endpoint_for_a2a_message(self):
        """Test getting the endpoint for an A2A message."""
        # Test agent_directory endpoint
        message = {
            "protocol": "a2a",
            "version": "1.0",
            "type": "agent_discovery",
            "agent_id": "agent_003",
            "data": {},
            "timestamp": "2025-05-23T12:40:00Z"
        }
        endpoint = self.a2a_manager.get_endpoint_for_a2a_message(message)
        self.assertEqual(endpoint, self.test_config["a2a_config"]["endpoints"]["agent_directory"])
        
        # Test agent_runtime endpoint
        message["type"] = "task_lifecycle"
        endpoint = self.a2a_manager.get_endpoint_for_a2a_message(message)
        self.assertEqual(endpoint, self.test_config["a2a_config"]["endpoints"]["agent_runtime"])
        
        # Test unknown type (default to agent_runtime)
        message["type"] = "unknown_type"
        endpoint = self.a2a_manager.get_endpoint_for_a2a_message(message)
        self.assertEqual(endpoint, self.test_config["a2a_config"]["endpoints"]["agent_runtime"])

    def test_get_oauth_token(self):
        """Test getting an OAuth token."""
        # Mock the token request
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "test_token",
                "token_type": "Bearer",
                "expires_in": 3600
            }
            mock_post.return_value = mock_response
            
            token = self.a2a_manager.get_oauth_token()
            
            self.assertEqual(token, "test_token")
            mock_post.assert_called_with(
                self.test_config["a2a_config"]["authentication"]["token_endpoint"],
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.test_config["a2a_config"]["authentication"]["client_id"],
                    "scope": self.test_config["a2a_config"]["authentication"]["scope"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Test error response
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "unauthorized"}
            mock_post.return_value = mock_response
            
            with self.assertRaises(Exception):
                self.a2a_manager.get_oauth_token()

    def test_add_oauth_authentication_to_headers(self):
        """Test adding OAuth authentication to headers."""
        headers = {}
        
        # Mock the get_oauth_token method
        with patch.object(self.a2a_manager, 'get_oauth_token', return_value="test_token"):
            self.a2a_manager.add_oauth_authentication_to_headers(headers)
            
            self.assertEqual(headers["Authorization"], "Bearer test_token")

    def test_handle_a2a_message(self):
        """Test handling an A2A message."""
        message = {
            "protocol": "a2a",
            "version": "1.0",
            "type": "agent_discovery",
            "agent_id": "agent_004",
            "data": {"capabilities": ["search", "calculate"]},
            "industryTags": ["manufacturing"],
            "timestamp": "2025-05-23T12:45:00Z"
        }
        
        # Mock the context engine update method
        self.a2a_manager.handle_a2a_message(message)
        
        # Verify context engine was updated
        self.mock_context_engine.update_context.assert_called_with(
            "agent_agent_004", 
            {
                "capabilities": ["search", "calculate"],
                "industryTags": ["manufacturing"]
            }
        )
        
        # Test task lifecycle
        message["type"] = "task_lifecycle"
        message["data"] = {"task_id": "task_001", "status": "completed"}
        
        self.a2a_manager.handle_a2a_message(message)
        
        # Verify context engine was updated
        self.mock_context_engine.update_context.assert_called_with(
            "agent_agent_004", 
            {
                "task_id": "task_001", 
                "status": "completed",
                "industryTags": ["manufacturing"]
            }
        )
        
        # Test collaboration
        message["type"] = "collaboration"
        message["data"] = {"collaboration_id": "collab_001", "participants": ["agent_004", "agent_005"]}
        
        self.a2a_manager.handle_a2a_message(message)
        
        # Verify context engine was updated
        self.mock_context_engine.update_context.assert_called_with(
            "agent_agent_004", 
            {
                "collaboration_id": "collab_001", 
                "participants": ["agent_004", "agent_005"],
                "industryTags": ["manufacturing"]
            }
        )

    def test_add_industry_tags(self):
        """Test adding industry tags to a message."""
        message = {
            "protocol": "a2a",
            "version": "1.0",
            "type": "agent_discovery",
            "agent_id": "agent_005",
            "data": {"domain": "manufacturing"},
            "timestamp": "2025-05-23T12:50:00Z"
        }
        
        self.a2a_manager.add_industry_tags(message)
        
        self.assertIn("industryTags", message)
        self.assertIn("manufacturing", message["industryTags"])
        
        # Test with existing tags
        message = {
            "protocol": "a2a",
            "version": "1.0",
            "type": "agent_discovery",
            "agent_id": "agent_006",
            "data": {"domain": "energy"},
            "industryTags": ["custom_tag"],
            "timestamp": "2025-05-23T12:51:00Z"
        }
        
        self.a2a_manager.add_industry_tags(message)
        
        self.assertIn("industryTags", message)
        self.assertIn("custom_tag", message["industryTags"])
        self.assertIn("energy", message["industryTags"])


if __name__ == '__main__':
    unittest.main()
