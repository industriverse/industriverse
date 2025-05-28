"""
Test suite for the Industriverse Application Layer.

This module provides comprehensive tests for the Application Layer components,
ensuring protocol-native functionality and integration with other layers.
"""

import unittest
import json
import os
import sys
import time
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components to test
from protocols.agent_core import AgentCore
from protocols.mcp_handler import MCPHandler
from protocols.a2a_handler import A2AHandler
from protocols.well_known_endpoint import WellKnownEndpoint
from protocols.protocol_translator import ProtocolTranslator
from protocols.mesh_boot_lifecycle import MeshBootLifecycle
from application_avatar_interface import ApplicationAvatarInterface
from universal_skin_manager import UniversalSkinManager
from agent_capsule_factory import AgentCapsuleFactory
from capsule_view_models import CapsuleViewModels
from capsule_interaction_handler import CapsuleInteractionHandler
from main_app_coordinator import MainAppCoordinator
from application_ui_component_system import ApplicationUIComponentSystem
from digital_twin_components import DigitalTwinComponents
from industry_specific_modules import IndustrySpecificModules
from workflow_orchestration import WorkflowOrchestration
from omniverse_integration_services import OmniverseIntegrationServices
from api.server import APIServer

class TestAgentCore(unittest.TestCase):
    """
    Test cases for the AgentCore component.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.config = {
            "agent_id": "test-agent",
            "agent_name": "Test Agent",
            "agent_version": "1.0.0"
        }
        self.agent_core = AgentCore(self.config)
    
    def test_initialization(self):
        """
        Test agent core initialization.
        """
        self.assertEqual(self.agent_core.agent_id, "test-agent")
        self.assertEqual(self.agent_core.agent_name, "Test Agent")
        self.assertEqual(self.agent_core.agent_version, "1.0.0")
        self.assertIsNotNone(self.agent_core.start_time)
        self.assertFalse(self.agent_core.running)
    
    def test_component_registration(self):
        """
        Test component registration.
        """
        # Create mock component
        mock_component = MagicMock()
        mock_component.get_info.return_value = {
            "id": "mock-component",
            "type": "MockComponent",
            "name": "Mock Component"
        }
        
        # Register component
        self.agent_core.register_component("mock-component", mock_component)
        
        # Verify component is registered
        self.assertIn("mock-component", self.agent_core.components)
        self.assertEqual(self.agent_core.components["mock-component"], mock_component)
        
        # Test get_component
        retrieved_component = self.agent_core.get_component("mock-component")
        self.assertEqual(retrieved_component, mock_component)
    
    def test_mcp_event_emission(self):
        """
        Test MCP event emission.
        """
        # Create mock MCP handler
        mock_mcp_handler = MagicMock()
        self.agent_core.register_component("mcp_handler", mock_mcp_handler)
        
        # Emit MCP event
        event_type = "test/event"
        event_data = {"key": "value"}
        self.agent_core.emit_mcp_event(event_type, event_data)
        
        # Verify MCP handler was called
        mock_mcp_handler.emit_event.assert_called_once()
        args, kwargs = mock_mcp_handler.emit_event.call_args
        self.assertEqual(args[0], event_type)
        self.assertEqual(args[1]["key"], "value")
        self.assertIn("timestamp", args[1])
        self.assertIn("agent_id", args[1])
        self.assertEqual(args[1]["agent_id"], "test-agent")
    
    def test_start_stop(self):
        """
        Test agent core start and stop.
        """
        # Start agent core
        self.agent_core.start()
        self.assertTrue(self.agent_core.running)
        
        # Stop agent core
        self.agent_core.stop()
        self.assertFalse(self.agent_core.running)

class TestMCPHandler(unittest.TestCase):
    """
    Test cases for the MCPHandler component.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.agent_core = MagicMock()
        self.agent_core.agent_id = "test-agent"
        self.agent_core.agent_name = "Test Agent"
        self.agent_core.agent_version = "1.0.0"
        self.mcp_handler = MCPHandler(self.agent_core)
    
    def test_initialization(self):
        """
        Test MCP handler initialization.
        """
        self.assertEqual(self.mcp_handler.agent_core, self.agent_core)
        self.assertIsNotNone(self.mcp_handler.events)
        self.assertIsNotNone(self.mcp_handler.event_handlers)
    
    def test_event_emission(self):
        """
        Test event emission.
        """
        # Emit event
        event_type = "test/event"
        event_data = {"key": "value"}
        result = self.mcp_handler.emit_event(event_type, event_data)
        
        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertIn("event_id", result)
        
        # Verify event was stored
        self.assertIn(result["event_id"], self.mcp_handler.events)
        stored_event = self.mcp_handler.events[result["event_id"]]
        self.assertEqual(stored_event["type"], event_type)
        self.assertEqual(stored_event["data"]["key"], "value")
        self.assertIn("timestamp", stored_event)
        self.assertIn("agent_id", stored_event)
        self.assertEqual(stored_event["agent_id"], "test-agent")
    
    def test_event_handling(self):
        """
        Test event handling.
        """
        # Create mock event handler
        mock_handler = MagicMock()
        mock_handler.return_value = {"status": "handled"}
        
        # Register handler
        event_type = "test/event"
        self.mcp_handler.register_event_handler(event_type, mock_handler)
        
        # Create event
        event_data = {
            "type": event_type,
            "data": {"key": "value"},
            "agent_id": "sender-agent",
            "timestamp": time.time()
        }
        
        # Handle event
        result = self.mcp_handler.handle_event(event_data)
        
        # Verify handler was called
        mock_handler.assert_called_once()
        args, kwargs = mock_handler.call_args
        self.assertEqual(args[0]["type"], event_type)
        self.assertEqual(args[0]["data"]["key"], "value")
        
        # Verify result
        self.assertEqual(result["status"], "handled")

class TestA2AHandler(unittest.TestCase):
    """
    Test cases for the A2AHandler component.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.agent_core = MagicMock()
        self.agent_core.agent_id = "test-agent"
        self.agent_core.agent_name = "Test Agent"
        self.agent_core.agent_version = "1.0.0"
        self.a2a_handler = A2AHandler(self.agent_core)
    
    def test_initialization(self):
        """
        Test A2A handler initialization.
        """
        self.assertEqual(self.a2a_handler.agent_core, self.agent_core)
        self.assertIsNotNone(self.a2a_handler.capabilities)
        self.assertIsNotNone(self.a2a_handler.invocations)
    
    def test_agent_card(self):
        """
        Test agent card generation.
        """
        # Get agent card
        agent_card = self.a2a_handler.get_agent_card()
        
        # Verify agent card
        self.assertEqual(agent_card["agent_id"], "test-agent")
        self.assertEqual(agent_card["name"], "Test Agent")
        self.assertEqual(agent_card["version"], "1.0.0")
        self.assertIn("description", agent_card)
        self.assertIn("capabilities", agent_card)
        self.assertIn("industryTags", agent_card)
    
    def test_capabilities(self):
        """
        Test capabilities retrieval.
        """
        # Register capability
        capability_id = "test-capability"
        capability_data = {
            "name": "Test Capability",
            "description": "A test capability",
            "inputs": {
                "param1": {
                    "type": "string",
                    "description": "Parameter 1"
                }
            },
            "outputs": {
                "result": {
                    "type": "string",
                    "description": "Result"
                }
            }
        }
        self.a2a_handler.register_capability(capability_id, capability_data)
        
        # Get capabilities
        capabilities = self.a2a_handler.get_capabilities()
        
        # Verify capabilities
        self.assertIn(capability_id, capabilities)
        self.assertEqual(capabilities[capability_id]["name"], "Test Capability")
        self.assertEqual(capabilities[capability_id]["description"], "A test capability")
        self.assertIn("inputs", capabilities[capability_id])
        self.assertIn("outputs", capabilities[capability_id])
    
    def test_invoke(self):
        """
        Test capability invocation.
        """
        # Create mock handler
        mock_handler = MagicMock()
        mock_handler.return_value = {"status": "success", "result": "test result"}
        
        # Register capability
        capability_id = "test-capability"
        capability_data = {
            "name": "Test Capability",
            "description": "A test capability",
            "inputs": {
                "param1": {
                    "type": "string",
                    "description": "Parameter 1"
                }
            },
            "outputs": {
                "result": {
                    "type": "string",
                    "description": "Result"
                }
            },
            "handler": mock_handler
        }
        self.a2a_handler.register_capability(capability_id, capability_data)
        
        # Create invoke data
        invoke_data = {
            "capability_id": capability_id,
            "inputs": {
                "param1": "test value"
            },
            "caller_id": "caller-agent"
        }
        
        # Invoke capability
        result = self.a2a_handler.handle_invoke(invoke_data)
        
        # Verify handler was called
        mock_handler.assert_called_once()
        args, kwargs = mock_handler.call_args
        self.assertEqual(args[0]["param1"], "test value")
        
        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], "test result")
        
        # Verify invocation was stored
        self.assertEqual(len(self.a2a_handler.invocations), 1)
        invocation = list(self.a2a_handler.invocations.values())[0]
        self.assertEqual(invocation["capability_id"], capability_id)
        self.assertEqual(invocation["caller_id"], "caller-agent")
        self.assertEqual(invocation["inputs"]["param1"], "test value")
        self.assertEqual(invocation["outputs"]["result"], "test result")

class TestApplicationAvatarInterface(unittest.TestCase):
    """
    Test cases for the ApplicationAvatarInterface component.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.agent_core = MagicMock()
        self.avatar_interface = ApplicationAvatarInterface(self.agent_core)
    
    def test_initialization(self):
        """
        Test avatar interface initialization.
        """
        self.assertEqual(self.avatar_interface.agent_core, self.agent_core)
        self.assertIsNotNone(self.avatar_interface.avatars)
    
    def test_avatar_creation(self):
        """
        Test avatar creation.
        """
        # Create avatar
        avatar_data = {
            "name": "Test Avatar",
            "description": "A test avatar",
            "layer": "application",
            "personality": "helpful",
            "appearance": {
                "color": "#1976d2",
                "icon": "robot"
            }
        }
        result = self.avatar_interface.create_avatar(avatar_data)
        
        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertIn("avatar_id", result)
        
        # Verify avatar was stored
        avatar_id = result["avatar_id"]
        self.assertIn(avatar_id, self.avatar_interface.avatars)
        stored_avatar = self.avatar_interface.avatars[avatar_id]
        self.assertEqual(stored_avatar["name"], "Test Avatar")
        self.assertEqual(stored_avatar["description"], "A test avatar")
        self.assertEqual(stored_avatar["layer"], "application")
        self.assertEqual(stored_avatar["personality"], "helpful")
        self.assertEqual(stored_avatar["appearance"]["color"], "#1976d2")
        self.assertEqual(stored_avatar["appearance"]["icon"], "robot")
    
    def test_avatar_update(self):
        """
        Test avatar update.
        """
        # Create avatar
        avatar_data = {
            "name": "Test Avatar",
            "description": "A test avatar",
            "layer": "application",
            "personality": "helpful",
            "appearance": {
                "color": "#1976d2",
                "icon": "robot"
            }
        }
        result = self.avatar_interface.create_avatar(avatar_data)
        avatar_id = result["avatar_id"]
        
        # Update avatar
        update_data = {
            "name": "Updated Avatar",
            "personality": "friendly"
        }
        update_result = self.avatar_interface.update_avatar(avatar_id, update_data)
        
        # Verify result
        self.assertEqual(update_result["status"], "success")
        
        # Verify avatar was updated
        updated_avatar = self.avatar_interface.avatars[avatar_id]
        self.assertEqual(updated_avatar["name"], "Updated Avatar")
        self.assertEqual(updated_avatar["description"], "A test avatar")  # Unchanged
        self.assertEqual(updated_avatar["personality"], "friendly")
        self.assertEqual(updated_avatar["appearance"]["color"], "#1976d2")  # Unchanged
    
    def test_avatar_retrieval(self):
        """
        Test avatar retrieval.
        """
        # Create avatar
        avatar_data = {
            "name": "Test Avatar",
            "description": "A test avatar",
            "layer": "application",
            "personality": "helpful",
            "appearance": {
                "color": "#1976d2",
                "icon": "robot"
            }
        }
        result = self.avatar_interface.create_avatar(avatar_data)
        avatar_id = result["avatar_id"]
        
        # Get avatar
        avatar = self.avatar_interface.get_avatar(avatar_id)
        
        # Verify avatar
        self.assertEqual(avatar["name"], "Test Avatar")
        self.assertEqual(avatar["description"], "A test avatar")
        self.assertEqual(avatar["layer"], "application")
        self.assertEqual(avatar["personality"], "helpful")
        self.assertEqual(avatar["appearance"]["color"], "#1976d2")
        self.assertEqual(avatar["appearance"]["icon"], "robot")
    
    def test_avatar_expression(self):
        """
        Test avatar expression.
        """
        # Create avatar
        avatar_data = {
            "name": "Test Avatar",
            "description": "A test avatar",
            "layer": "application",
            "personality": "helpful",
            "appearance": {
                "color": "#1976d2",
                "icon": "robot"
            }
        }
        result = self.avatar_interface.create_avatar(avatar_data)
        avatar_id = result["avatar_id"]
        
        # Express emotion
        expression_data = {
            "emotion": "happy",
            "intensity": 0.8,
            "duration": 5
        }
        expression_result = self.avatar_interface.express_emotion(avatar_id, expression_data)
        
        # Verify result
        self.assertEqual(expression_result["status"], "success")
        
        # Verify expression was stored
        avatar = self.avatar_interface.avatars[avatar_id]
        self.assertEqual(avatar["current_expression"]["emotion"], "happy")
        self.assertEqual(avatar["current_expression"]["intensity"], 0.8)

class TestDigitalTwinComponents(unittest.TestCase):
    """
    Test cases for the DigitalTwinComponents component.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.agent_core = MagicMock()
        self.digital_twin = DigitalTwinComponents(self.agent_core)
    
    def test_initialization(self):
        """
        Test digital twin initialization.
        """
        self.assertEqual(self.digital_twin.agent_core, self.agent_core)
        self.assertIsNotNone(self.digital_twin.digital_twins)
        self.assertIsNotNone(self.digital_twin.twin_telemetry)
    
    def test_digital_twin_creation(self):
        """
        Test digital twin creation.
        """
        # Create digital twin
        twin_data = {
            "name": "Test Twin",
            "description": "A test digital twin",
            "type": "equipment",
            "model": "test-model",
            "attributes": {
                "temperature": {
                    "type": "number",
                    "unit": "celsius",
                    "min": 0,
                    "max": 100
                },
                "pressure": {
                    "type": "number",
                    "unit": "bar",
                    "min": 0,
                    "max": 10
                }
            }
        }
        result = self.digital_twin.create_digital_twin(twin_data)
        
        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertIn("twin_id", result)
        
        # Verify twin was stored
        twin_id = result["twin_id"]
        self.assertIn(twin_id, self.digital_twin.digital_twins)
        stored_twin = self.digital_twin.digital_twins[twin_id]
        self.assertEqual(stored_twin["name"], "Test Twin")
        self.assertEqual(stored_twin["description"], "A test digital twin")
        self.assertEqual(stored_twin["type"], "equipment")
        self.assertEqual(stored_twin["model"], "test-model")
        self.assertIn("attributes", stored_twin)
        self.assertIn("temperature", stored_twin["attributes"])
        self.assertIn("pressure", stored_twin["attributes"])
    
    def test_telemetry_update(self):
        """
        Test telemetry update.
        """
        # Create digital twin
        twin_data = {
            "name": "Test Twin",
            "description": "A test digital twin",
            "type": "equipment",
            "model": "test-model",
            "attributes": {
                "temperature": {
                    "type": "number",
                    "unit": "celsius",
                    "min": 0,
                    "max": 100
                },
                "pressure": {
                    "type": "number",
                    "unit": "bar",
                    "min": 0,
                    "max": 10
                }
            }
        }
        result = self.digital_twin.create_digital_twin(twin_data)
        twin_id = result["twin_id"]
        
        # Update telemetry
        telemetry_data = {
            "temperature": 75.5,
            "pressure": 5.2
        }
        telemetry_result = self.digital_twin.update_telemetry(twin_id, telemetry_data)
        
        # Verify result
        self.assertEqual(telemetry_result["status"], "success")
        
        # Verify telemetry was stored
        self.assertIn(twin_id, self.digital_twin.twin_telemetry)
        stored_telemetry = self.digital_twin.twin_telemetry[twin_id]
        self.assertEqual(stored_telemetry["temperature"], 75.5)
        self.assertEqual(stored_telemetry["pressure"], 5.2)
    
    def test_twin_retrieval(self):
        """
        Test digital twin retrieval.
        """
        # Create digital twin
        twin_data = {
            "name": "Test Twin",
            "description": "A test digital twin",
            "type": "equipment",
            "model": "test-model",
            "attributes": {
                "temperature": {
                    "type": "number",
                    "unit": "celsius",
                    "min": 0,
                    "max": 100
                },
                "pressure": {
                    "type": "number",
                    "unit": "bar",
                    "min": 0,
                    "max": 10
                }
            }
        }
        result = self.digital_twin.create_digital_twin(twin_data)
        twin_id = result["twin_id"]
        
        # Get digital twin
        twin = self.digital_twin.get_digital_twin(twin_id)
        
        # Verify twin
        self.assertEqual(twin["name"], "Test Twin")
        self.assertEqual(twin["description"], "A test digital twin")
        self.assertEqual(twin["type"], "equipment")
        self.assertEqual(twin["model"], "test-model")
        self.assertIn("attributes", twin)
        self.assertIn("temperature", twin["attributes"])
        self.assertIn("pressure", twin["attributes"])

class TestWorkflowOrchestration(unittest.TestCase):
    """
    Test cases for the WorkflowOrchestration component.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.agent_core = MagicMock()
        self.workflow = WorkflowOrchestration(self.agent_core)
    
    def test_initialization(self):
        """
        Test workflow orchestration initialization.
        """
        self.assertEqual(self.workflow.agent_core, self.agent_core)
        self.assertIsNotNone(self.workflow.workflow_templates)
        self.assertIsNotNone(self.workflow.workflow_instances)
        self.assertIsNotNone(self.workflow.workflow_executions)
    
    def test_template_registration(self):
        """
        Test workflow template registration.
        """
        # Register template
        template_config = {
            "template_id": "test-template",
            "name": "Test Template",
            "description": "A test workflow template",
            "tasks": [
                {
                    "task_id": "task1",
                    "name": "Task 1",
                    "type": "data_processing",
                    "config": {
                        "data_source": "test_source"
                    }
                },
                {
                    "task_id": "task2",
                    "name": "Task 2",
                    "type": "notification",
                    "config": {
                        "message": "Test message"
                    }
                }
            ],
            "connections": [
                {
                    "source": "task1",
                    "target": "task2"
                }
            ]
        }
        result = self.workflow.register_workflow_template(template_config)
        
        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["template_id"], "test-template")
        
        # Verify template was stored
        self.assertIn("test-template", self.workflow.workflow_templates)
        stored_template = self.workflow.workflow_templates["test-template"]
        self.assertEqual(stored_template["name"], "Test Template")
        self.assertEqual(stored_template["description"], "A test workflow template")
        self.assertEqual(len(stored_template["tasks"]), 2)
        self.assertEqual(len(stored_template["connections"]), 1)
    
    def test_instance_creation(self):
        """
        Test workflow instance creation.
        """
        # Register template
        template_config = {
            "template_id": "test-template",
            "name": "Test Template",
            "description": "A test workflow template",
            "tasks": [
                {
                    "task_id": "task1",
                    "name": "Task 1",
                    "type": "data_processing",
                    "config": {
                        "data_source": "test_source"
                    }
                },
                {
                    "task_id": "task2",
                    "name": "Task 2",
                    "type": "notification",
                    "config": {
                        "message": "Test message"
                    }
                }
            ],
            "connections": [
                {
                    "source": "task1",
                    "target": "task2"
                }
            ]
        }
        self.workflow.register_workflow_template(template_config)
        
        # Create instance
        instance_config = {
            "name": "Test Instance",
            "description": "A test workflow instance"
        }
        result = self.workflow.create_workflow_instance("test-template", instance_config)
        
        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertIn("instance_id", result)
        
        # Verify instance was stored
        instance_id = result["instance_id"]
        self.assertIn(instance_id, self.workflow.workflow_instances)
        stored_instance = self.workflow.workflow_instances[instance_id]
        self.assertEqual(stored_instance["name"], "Test Instance")
        self.assertEqual(stored_instance["description"], "A test workflow instance")
        self.assertEqual(stored_instance["template_id"], "test-template")
        self.assertEqual(len(stored_instance["tasks"]), 2)
        self.assertEqual(len(stored_instance["connections"]), 1)
    
    def test_workflow_execution(self):
        """
        Test workflow execution.
        """
        # Register template
        template_config = {
            "template_id": "test-template",
            "name": "Test Template",
            "description": "A test workflow template",
            "tasks": [
                {
                    "task_id": "task1",
                    "name": "Task 1",
                    "type": "data_processing",
                    "config": {
                        "data_source": "test_source"
                    }
                },
                {
                    "task_id": "task2",
                    "name": "Task 2",
                    "type": "notification",
                    "config": {
                        "message": "Test message"
                    }
                }
            ],
            "connections": [
                {
                    "source": "task1",
                    "target": "task2"
                }
            ]
        }
        self.workflow.register_workflow_template(template_config)
        
        # Create instance
        instance_config = {
            "name": "Test Instance",
            "description": "A test workflow instance"
        }
        instance_result = self.workflow.create_workflow_instance("test-template", instance_config)
        instance_id = instance_result["instance_id"]
        
        # Execute workflow
        execution_config = {
            "input_data": {
                "param1": "value1"
            }
        }
        execution_result = self.workflow.execute_workflow(instance_id, execution_config)
        
        # Verify result
        self.assertEqual(execution_result["status"], "success")
        self.assertIn("execution_id", execution_result)
        
        # Verify execution was stored
        execution_id = execution_result["execution_id"]
        self.assertIn(execution_id, self.workflow.workflow_executions)
        stored_execution = self.workflow.workflow_executions[execution_id]
        self.assertEqual(stored_execution["instance_id"], instance_id)
        self.assertEqual(stored_execution["status"], "running")
        self.assertIn("task_statuses", stored_execution)
        self.assertIn("current_tasks", stored_execution)
        self.assertEqual(stored_execution["input_data"]["param1"], "value1")

class TestAPIServer(unittest.TestCase):
    """
    Test cases for the APIServer component.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.agent_core = MagicMock()
        self.config = {
            "host": "127.0.0.1",
            "port": 8000,
            "cors_origins": ["*"]
        }
        self.api_server = APIServer(self.agent_core, self.config)
    
    def test_initialization(self):
        """
        Test API server initialization.
        """
        self.assertEqual(self.api_server.agent_core, self.agent_core)
        self.assertEqual(self.api_server.config, self.config)
        self.assertIsNotNone(self.api_server.app)
        self.assertFalse(self.api_server.running)
    
    def test_start_stop(self):
        """
        Test API server start and stop.
        """
        # Mock uvicorn.run to avoid actually starting a server
        with patch("uvicorn.run"):
            # Start server
            self.api_server.start()
            self.assertTrue(self.api_server.running)
            
            # Stop server
            self.api_server.stop()
            self.assertFalse(self.api_server.running)
    
    def test_get_info(self):
        """
        Test get_info method.
        """
        info = self.api_server.get_info()
        self.assertEqual(info["id"], "api_server")
        self.assertEqual(info["type"], "APIServer")
        self.assertEqual(info["name"], "API Server")
        self.assertEqual(info["status"], "stopped")
        self.assertEqual(info["host"], "127.0.0.1")
        self.assertEqual(info["port"], 8000)

if __name__ == "__main__":
    unittest.main()
