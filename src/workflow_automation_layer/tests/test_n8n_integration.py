"""
Test suite for the Workflow Automation Layer n8n Integration components.

This module contains unit tests for the n8n integration components,
including n8n connector, bridge service, and workflow templates.
"""

import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from n8n_integration.n8n_connector import N8nConnector
from n8n_integration.n8n_bridge_service import N8nBridgeService
from n8n_integration.n8n_workflow_templates import N8nWorkflowTemplates


class TestN8nConnector(unittest.TestCase):
    """Test cases for the N8nConnector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "api_url": "http://localhost:5678/api",
            "api_key": "test_api_key",
            "webhook_base_url": "http://localhost:8080/api/n8n/webhook"
        }
        self.connector = N8nConnector(self.config)

    @patch('n8n_integration.n8n_connector.requests.get')
    def test_get_workflows(self, mock_get):
        """Test getting workflows from n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "1",
                    "name": "Workflow 1",
                    "active": True
                },
                {
                    "id": "2",
                    "name": "Workflow 2",
                    "active": False
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.connector.get_workflows()
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(len(result["workflows"]), 2)
        self.assertEqual(result["workflows"][0]["id"], "1")
        self.assertEqual(result["workflows"][0]["name"], "Workflow 1")
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "http://localhost:5678/api/workflows",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )

    @patch('n8n_integration.n8n_connector.requests.get')
    def test_get_workflow(self, mock_get):
        """Test getting a specific workflow from n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "1",
                "name": "Workflow 1",
                "active": True,
                "nodes": [
                    {
                        "id": "node1",
                        "name": "Start",
                        "type": "n8n-nodes-base.start"
                    },
                    {
                        "id": "node2",
                        "name": "Function",
                        "type": "n8n-nodes-base.function"
                    }
                ],
                "connections": {
                    "Start": {
                        "main": [[{"node": "Function", "type": "main", "index": 0}]]
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.connector.get_workflow("1")
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["workflow"]["id"], "1")
        self.assertEqual(result["workflow"]["name"], "Workflow 1")
        self.assertEqual(len(result["workflow"]["nodes"]), 2)
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "http://localhost:5678/api/workflows/1",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )

    @patch('n8n_integration.n8n_connector.requests.post')
    def test_create_workflow(self, mock_post):
        """Test creating a workflow in n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "3",
                "name": "New Workflow",
                "active": False
            }
        }
        mock_post.return_value = mock_response
        
        # Workflow data to create
        workflow_data = {
            "name": "New Workflow",
            "nodes": [
                {
                    "id": "node1",
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "position": [100, 100]
                },
                {
                    "id": "node2",
                    "name": "Function",
                    "type": "n8n-nodes-base.function",
                    "position": [300, 100],
                    "parameters": {
                        "functionCode": "return {result: 'Hello World'};"
                    }
                }
            ],
            "connections": {
                "Start": {
                    "main": [[{"node": "Function", "type": "main", "index": 0}]]
                }
            }
        }
        
        # Call the method
        result = self.connector.create_workflow(workflow_data)
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["workflow"]["id"], "3")
        self.assertEqual(result["workflow"]["name"], "New Workflow")
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            "http://localhost:5678/api/workflows",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            },
            json=workflow_data
        )

    @patch('n8n_integration.n8n_connector.requests.put')
    def test_update_workflow(self, mock_put):
        """Test updating a workflow in n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "1",
                "name": "Updated Workflow",
                "active": True
            }
        }
        mock_put.return_value = mock_response
        
        # Workflow data to update
        workflow_data = {
            "name": "Updated Workflow",
            "active": True,
            "nodes": [
                {
                    "id": "node1",
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "position": [100, 100]
                },
                {
                    "id": "node2",
                    "name": "Function",
                    "type": "n8n-nodes-base.function",
                    "position": [300, 100],
                    "parameters": {
                        "functionCode": "return {result: 'Updated'};"
                    }
                }
            ],
            "connections": {
                "Start": {
                    "main": [[{"node": "Function", "type": "main", "index": 0}]]
                }
            }
        }
        
        # Call the method
        result = self.connector.update_workflow("1", workflow_data)
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["workflow"]["id"], "1")
        self.assertEqual(result["workflow"]["name"], "Updated Workflow")
        
        # Verify the request was made correctly
        mock_put.assert_called_once_with(
            "http://localhost:5678/api/workflows/1",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            },
            json=workflow_data
        )

    @patch('n8n_integration.n8n_connector.requests.delete')
    def test_delete_workflow(self, mock_delete):
        """Test deleting a workflow in n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        # Call the method
        result = self.connector.delete_workflow("1")
        
        # Verify the result
        self.assertTrue(result["success"])
        
        # Verify the request was made correctly
        mock_delete.assert_called_once_with(
            "http://localhost:5678/api/workflows/1",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )

    @patch('n8n_integration.n8n_connector.requests.post')
    def test_activate_workflow(self, mock_post):
        """Test activating a workflow in n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "1",
                "name": "Workflow 1",
                "active": True
            }
        }
        mock_post.return_value = mock_response
        
        # Call the method
        result = self.connector.activate_workflow("1")
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertTrue(result["workflow"]["active"])
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            "http://localhost:5678/api/workflows/1/activate",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )

    @patch('n8n_integration.n8n_connector.requests.post')
    def test_deactivate_workflow(self, mock_post):
        """Test deactivating a workflow in n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "1",
                "name": "Workflow 1",
                "active": False
            }
        }
        mock_post.return_value = mock_response
        
        # Call the method
        result = self.connector.deactivate_workflow("1")
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertFalse(result["workflow"]["active"])
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            "http://localhost:5678/api/workflows/1/deactivate",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )

    @patch('n8n_integration.n8n_connector.requests.post')
    def test_execute_workflow(self, mock_post):
        """Test executing a workflow in n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "executionId": "exec123",
                "waitingForWebhook": False
            }
        }
        mock_post.return_value = mock_response
        
        # Input data for workflow execution
        input_data = {
            "param1": "value1",
            "param2": 42
        }
        
        # Call the method
        result = self.connector.execute_workflow("1", input_data)
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["execution_id"], "exec123")
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            "http://localhost:5678/api/workflows/1/execute",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            },
            json={"data": input_data}
        )

    @patch('n8n_integration.n8n_connector.requests.get')
    def test_get_execution_data(self, mock_get):
        """Test getting execution data from n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "exec123",
                "finished": True,
                "status": "success",
                "data": {
                    "resultData": {
                        "runData": {
                            "node1": [
                                {
                                    "data": {"result": "Hello World"}
                                }
                            ]
                        }
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.connector.get_execution_data("1", "exec123")
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["execution"]["id"], "exec123")
        self.assertEqual(result["execution"]["status"], "success")
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "http://localhost:5678/api/executions/exec123",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            }
        )

    @patch('n8n_integration.n8n_connector.requests.post')
    def test_create_webhook(self, mock_post):
        """Test creating a webhook in n8n."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "webhook123",
                "webhookPath": "abc123",
                "webhookUrl": "http://localhost:5678/webhook/abc123"
            }
        }
        mock_post.return_value = mock_response
        
        # Webhook data
        webhook_data = {
            "name": "Test Webhook",
            "event": "workflow.started",
            "workflow_id": "1"
        }
        
        # Call the method
        result = self.connector.create_webhook(webhook_data)
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["webhook"]["id"], "webhook123")
        self.assertEqual(result["webhook"]["webhookUrl"], "http://localhost:5678/webhook/abc123")
        
        # Verify the request was made correctly
        expected_data = {
            "name": "Test Webhook",
            "event": "workflow.started",
            "workflow_id": "1",
            "callback_url": "http://localhost:8080/api/n8n/webhook"
        }
        mock_post.assert_called_once_with(
            "http://localhost:5678/api/webhooks",
            headers={
                "X-N8N-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            },
            json=expected_data
        )


class TestN8nBridgeService(unittest.TestCase):
    """Test cases for the N8nBridgeService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.n8n_connector = MagicMock()
        self.workflow_registry = MagicMock()
        self.workflow_runtime = MagicMock()
        
        self.service = N8nBridgeService(
            self.n8n_connector,
            self.workflow_registry,
            self.workflow_runtime
        )

    async def test_sync_workflow_to_n8n(self):
        """Test syncing a workflow to n8n."""
        # Mock the workflow registry's get_workflow method
        self.workflow_registry.get_workflow.return_value = {
            "workflow_id": "workflow1",
            "name": "Test Workflow",
            "description": "Workflow for testing",
            "tasks": [
                {"task_id": "task1", "name": "Task 1"},
                {"task_id": "task2", "name": "Task 2"}
            ],
            "transitions": [
                {"from": "task1", "to": "task2", "condition": "success"}
            ]
        }
        
        # Mock the n8n connector's create_workflow method
        self.n8n_connector.create_workflow.return_value = {
            "success": True,
            "workflow": {
                "id": "n8n123",
                "name": "Test Workflow"
            }
        }
        
        # Call the method
        result = await self.service.sync_workflow_to_n8n("workflow1")
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["n8n_workflow_id"], "n8n123")
        
        # Verify the mapping was stored
        self.assertIn("workflow1", self.service.workflow_mappings)
        self.assertEqual(self.service.workflow_mappings["workflow1"], "n8n123")

    async def test_sync_workflow_from_n8n(self):
        """Test syncing a workflow from n8n."""
        # Mock the n8n connector's get_workflow method
        self.n8n_connector.get_workflow.return_value = {
            "success": True,
            "workflow": {
                "id": "n8n123",
                "name": "Test Workflow",
                "nodes": [
                    {"name": "Start", "type": "n8n-nodes-base.start"},
                    {"name": "Task 1", "type": "n8n-nodes-base.function"},
                    {"name": "Task 2", "type": "n8n-nodes-base.function"}
                ],
                "connections": {
                    "Start": {
                        "main": [[{"node": "Task 1", "type": "main", "index": 0}]]
                    },
                    "Task 1": {
                        "main": [[{"node": "Task 2", "type": "main", "index": 0}]]
                    }
                }
            }
        }
        
        # Mock the workflow registry's register_workflow method
        self.workflow_registry.register_workflow.return_value = {
            "success": True,
            "workflow_id": "workflow1"
        }
        
        # Call the method
        result = await self.service.sync_workflow_from_n8n("n8n123")
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["workflow_id"], "workflow1")
        
        # Verify the mapping was stored
        self.assertIn("workflow1", self.service.workflow_mappings)
        self.assertEqual(self.service.workflow_mappings["workflow1"], "n8n123")

    async def test_handle_n8n_webhook(self):
        """Test handling an n8n webhook."""
        # Setup the workflow mapping
        self.service.workflow_mappings = {"workflow1": "n8n123"}
        
        # Mock the n8n connector's get_execution_data method
        self.n8n_connector.get_execution_data.return_value = {
            "success": True,
            "execution": {
                "id": "exec456",
                "status": "success",
                "data": {"result": "Hello World"}
            }
        }
        
        # Webhook data
        webhook_data = {
            "workflow_id": "n8n123",
            "execution_id": "exec456",
            "event_type": "workflow.completed",
            "timestamp": "2025-05-22T15:30:00Z",
            "payload": {
                "workflow": {"id": "n8n123", "name": "Test Workflow"},
                "execution": {"id": "exec456", "status": "success"}
            }
        }
        
        # Call the method
        result = await self.service.handle_n8n_webhook(webhook_data)
        
        # Verify the result
        self.assertTrue(result["success"])
        
        # Verify the workflow runtime was called
        self.workflow_runtime.handle_external_event.assert_called_once()
        args = self.workflow_runtime.handle_external_event.call_args[0]
        self.assertEqual(args[0]["source"], "n8n")
        self.assertEqual(args[0]["workflow_id"], "workflow1")
        self.assertEqual(args[0]["event_type"], "workflow.completed")

    async def test_execute_n8n_workflow(self):
        """Test executing an n8n workflow."""
        # Setup the workflow mapping
        self.service.workflow_mappings = {"workflow1": "n8n123"}
        
        # Mock the n8n connector's execute_workflow method
        self.n8n_connector.execute_workflow.return_value = {
            "success": True,
            "execution_id": "exec456"
        }
        
        # Input data
        input_data = {
            "param1": "value1",
            "param2": 42
        }
        
        # Call the method
        result = await self.service.execute_n8n_workflow("workflow1", input_data)
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["execution_id"], "exec456")
        
        # Verify the n8n connector was called
        self.n8n_connector.execute_workflow.assert_called_once_with("n8n123", input_data)

    async def test_setup_webhooks(self):
        """Test setting up webhooks."""
        # Mock the n8n connector's create_webhook method
        self.n8n_connector.create_webhook.return_value = {
            "success": True,
            "webhook": {
                "id": "webhook123",
                "webhookUrl": "http://localhost:5678/webhook/abc123"
            }
        }
        
        # Setup the workflow mapping
        self.service.workflow_mappings = {"workflow1": "n8n123"}
        
        # Call the method
        result = await self.service.setup_webhooks()
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(len(result["webhooks"]), 1)
        
        # Verify the n8n connector was called
        self.n8n_connector.create_webhook.assert_called()


class TestN8nWorkflowTemplates(unittest.TestCase):
    """Test cases for the N8nWorkflowTemplates class."""

    def setUp(self):
        """Set up test fixtures."""
        self.templates = N8nWorkflowTemplates()

    def test_get_template_names(self):
        """Test getting template names."""
        template_names = self.templates.get_template_names()
        self.assertIsInstance(template_names, list)
        self.assertGreater(len(template_names), 0)
        self.assertIn("data_processing", template_names)

    def test_get_template(self):
        """Test getting a specific template."""
        template = self.templates.get_template("data_processing")
        self.assertIsNotNone(template)
        self.assertEqual(template["name"], "Data Processing Workflow")
        self.assertIn("nodes", template)
        self.assertIn("connections", template)

    def test_get_nonexistent_template(self):
        """Test getting a non-existent template."""
        template = self.templates.get_template("nonexistent")
        self.assertIsNone(template)

    def test_customize_template(self):
        """Test customizing a template."""
        # Get the base template
        template = self.templates.get_template("data_processing")
        
        # Customization parameters
        params = {
            "name": "Custom Data Processing",
            "input_node_name": "Custom Input",
            "output_node_name": "Custom Output",
            "processing_steps": 3
        }
        
        # Customize the template
        customized = self.templates.customize_template("data_processing", params)
        
        # Verify the customization
        self.assertEqual(customized["name"], "Custom Data Processing")
        
        # Check that nodes were customized
        node_names = [node["name"] for node in customized["nodes"]]
        self.assertIn("Custom Input", node_names)
        self.assertIn("Custom Output", node_names)
        
        # Check that the number of processing steps was adjusted
        processing_nodes = [node for node in customized["nodes"] if "Processing" in node["name"]]
        self.assertEqual(len(processing_nodes), 3)

    def test_generate_workflow_from_manifest(self):
        """Test generating an n8n workflow from a manifest."""
        # Create a workflow manifest
        manifest = {
            "name": "Test Workflow",
            "description": "Workflow for testing",
            "tasks": [
                {
                    "id": "task1",
                    "name": "Task 1",
                    "description": "First task",
                    "timeout_seconds": 300,
                    "retry_count": 3
                },
                {
                    "id": "task2",
                    "name": "Task 2",
                    "description": "Second task",
                    "timeout_seconds": 600,
                    "retry_count": 2
                }
            ],
            "workflow": {
                "transitions": [
                    {
                        "from": "task1",
                        "to": "task2",
                        "condition": "success"
                    }
                ]
            }
        }
        
        # Generate the n8n workflow
        n8n_workflow = self.templates.generate_workflow_from_manifest(manifest)
        
        # Verify the generated workflow
        self.assertEqual(n8n_workflow["name"], "Test Workflow")
        
        # Check that nodes were created for each task
        node_names = [node["name"] for node in n8n_workflow["nodes"]]
        self.assertIn("Task 1", node_names)
        self.assertIn("Task 2", node_names)
        
        # Check that connections were created based on transitions
        self.assertIn("Task 1", n8n_workflow["connections"])
        self.assertEqual(
            n8n_workflow["connections"]["Task 1"]["main"][0][0]["node"],
            "Task 2"
        )


if __name__ == "__main__":
    unittest.main()
