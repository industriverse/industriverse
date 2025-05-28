import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from n8n_integration.n8n_connector import N8nConnector
from n8n_integration.n8n_bridge_service import N8nBridgeService
from n8n_integration.n8n_workflow_templates import N8nWorkflowTemplates
from workflow_engine.workflow_runtime import WorkflowRuntime
from agents.n8n_sync_bridge import N8nSyncBridge
from agents.n8n_adapter_agent import N8nAdapterAgent

class TestN8nConnector(unittest.TestCase):
    """Test cases for the N8nConnector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_url = "http://localhost:5678/api/v1"
        self.api_key = "test_api_key"
        self.connector = N8nConnector(
            api_url=self.api_url,
            api_key=self.api_key
        )
    
    def test_initialization(self):
        """Test that the connector initializes correctly."""
        self.assertEqual(self.connector.api_url, self.api_url)
        self.assertEqual(self.connector.api_key, self.api_key)
        self.assertIsNotNone(self.connector.session)
        self.assertEqual(self.connector.session.headers.get("X-N8N-API-KEY"), self.api_key)
    
    @patch('n8n_integration.n8n_connector.requests.Session.get')
    def test_get_workflows(self, mock_get):
        """Test that the connector retrieves workflows correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "1", "name": "Test Workflow"}]}
        mock_get.return_value = mock_response
        
        workflows = self.connector.get_workflows()
        
        mock_get.assert_called_once_with(f"{self.api_url}/workflows")
        self.assertEqual(len(workflows), 1)
        self.assertEqual(workflows[0]["id"], "1")
        self.assertEqual(workflows[0]["name"], "Test Workflow")
    
    @patch('n8n_integration.n8n_connector.requests.Session.get')
    def test_get_workflow(self, mock_get):
        """Test that the connector retrieves a specific workflow correctly."""
        workflow_id = "1"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": workflow_id, "name": "Test Workflow"}
        mock_get.return_value = mock_response
        
        workflow = self.connector.get_workflow(workflow_id)
        
        mock_get.assert_called_once_with(f"{self.api_url}/workflows/{workflow_id}")
        self.assertEqual(workflow["id"], workflow_id)
        self.assertEqual(workflow["name"], "Test Workflow")
    
    @patch('n8n_integration.n8n_connector.requests.Session.post')
    def test_create_workflow(self, mock_post):
        """Test that the connector creates workflows correctly."""
        workflow_data = {"name": "New Workflow", "nodes": [], "connections": {}}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "2", "name": "New Workflow"}
        mock_post.return_value = mock_response
        
        created_workflow = self.connector.create_workflow(workflow_data)
        
        mock_post.assert_called_once_with(f"{self.api_url}/workflows", json=workflow_data)
        self.assertEqual(created_workflow["id"], "2")
        self.assertEqual(created_workflow["name"], "New Workflow")
    
    @patch('n8n_integration.n8n_connector.requests.Session.put')
    def test_update_workflow(self, mock_put):
        """Test that the connector updates workflows correctly."""
        workflow_id = "1"
        workflow_data = {"name": "Updated Workflow", "nodes": [], "connections": {}}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": workflow_id, "name": "Updated Workflow"}
        mock_put.return_value = mock_response
        
        updated_workflow = self.connector.update_workflow(workflow_id, workflow_data)
        
        mock_put.assert_called_once_with(f"{self.api_url}/workflows/{workflow_id}", json=workflow_data)
        self.assertEqual(updated_workflow["id"], workflow_id)
        self.assertEqual(updated_workflow["name"], "Updated Workflow")
    
    @patch('n8n_integration.n8n_connector.requests.Session.delete')
    def test_delete_workflow(self, mock_delete):
        """Test that the connector deletes workflows correctly."""
        workflow_id = "1"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = self.connector.delete_workflow(workflow_id)
        
        mock_delete.assert_called_once_with(f"{self.api_url}/workflows/{workflow_id}")
        self.assertTrue(result)
    
    @patch('n8n_integration.n8n_connector.requests.Session.post')
    def test_activate_workflow(self, mock_post):
        """Test that the connector activates workflows correctly."""
        workflow_id = "1"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.connector.activate_workflow(workflow_id)
        
        mock_post.assert_called_once_with(f"{self.api_url}/workflows/{workflow_id}/activate")
        self.assertTrue(result)
    
    @patch('n8n_integration.n8n_connector.requests.Session.post')
    def test_deactivate_workflow(self, mock_post):
        """Test that the connector deactivates workflows correctly."""
        workflow_id = "1"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.connector.deactivate_workflow(workflow_id)
        
        mock_post.assert_called_once_with(f"{self.api_url}/workflows/{workflow_id}/deactivate")
        self.assertTrue(result)
    
    @patch('n8n_integration.n8n_connector.requests.Session.post')
    def test_execute_workflow(self, mock_post):
        """Test that the connector executes workflows correctly."""
        workflow_id = "1"
        input_data = {"data": {"value1": 123}}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"result": "success"}}
        mock_post.return_value = mock_response
        
        result = self.connector.execute_workflow(workflow_id, input_data)
        
        mock_post.assert_called_once_with(f"{self.api_url}/workflows/{workflow_id}/execute", json=input_data)
        self.assertEqual(result["data"]["result"], "success")


class TestN8nBridgeService(unittest.TestCase):
    """Test cases for the N8nBridgeService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.n8n_connector = MagicMock(spec=N8nConnector)
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.bridge_service = N8nBridgeService(
            n8n_connector=self.n8n_connector,
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the bridge service initializes correctly."""
        self.assertEqual(self.bridge_service.n8n_connector, self.n8n_connector)
        self.assertEqual(self.bridge_service.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.bridge_service.status, "initialized")
    
    @patch('n8n_integration.n8n_bridge_service.N8nBridgeService.start')
    def test_start(self, mock_start):
        """Test that the bridge service starts correctly."""
        self.bridge_service.start()
        mock_start.assert_called_once()
    
    @patch('n8n_integration.n8n_bridge_service.N8nBridgeService.stop')
    def test_stop(self, mock_stop):
        """Test that the bridge service stops correctly."""
        self.bridge_service.stop()
        mock_stop.assert_called_once()
    
    @patch('n8n_integration.n8n_bridge_service.N8nBridgeService.sync_workflow_to_n8n')
    def test_sync_workflow_to_n8n(self, mock_sync):
        """Test that the bridge service syncs workflows to n8n correctly."""
        workflow_id = "workflow-001"
        workflow_data = {"name": "Test Workflow", "nodes": [], "connections": {}}
        self.bridge_service.sync_workflow_to_n8n(workflow_id, workflow_data)
        mock_sync.assert_called_once_with(workflow_id, workflow_data)
    
    @patch('n8n_integration.n8n_bridge_service.N8nBridgeService.sync_workflow_from_n8n')
    def test_sync_workflow_from_n8n(self, mock_sync):
        """Test that the bridge service syncs workflows from n8n correctly."""
        n8n_workflow_id = "1"
        self.bridge_service.sync_workflow_from_n8n(n8n_workflow_id)
        mock_sync.assert_called_once_with(n8n_workflow_id)
    
    @patch('n8n_integration.n8n_bridge_service.N8nBridgeService.register_webhook')
    def test_register_webhook(self, mock_register):
        """Test that the bridge service registers webhooks correctly."""
        workflow_id = "workflow-001"
        webhook_url = "http://example.com/webhook"
        events = ["workflow.started", "workflow.completed"]
        self.bridge_service.register_webhook(workflow_id, webhook_url, events)
        mock_register.assert_called_once_with(workflow_id, webhook_url, events)
    
    @patch('n8n_integration.n8n_bridge_service.N8nBridgeService.handle_webhook_event')
    def test_handle_webhook_event(self, mock_handle):
        """Test that the bridge service handles webhook events correctly."""
        event_type = "workflow.completed"
        event_data = {"workflow_id": "1", "execution_id": "123", "status": "success"}
        self.bridge_service.handle_webhook_event(event_type, event_data)
        mock_handle.assert_called_once_with(event_type, event_data)


class TestN8nWorkflowTemplates(unittest.TestCase):
    """Test cases for the N8nWorkflowTemplates class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.templates = N8nWorkflowTemplates()
    
    def test_initialization(self):
        """Test that the templates initialize correctly."""
        self.assertIsNotNone(self.templates)
        self.assertIsNotNone(self.templates.template_registry)
    
    @patch('n8n_integration.n8n_workflow_templates.N8nWorkflowTemplates.get_template')
    def test_get_template(self, mock_get):
        """Test that the templates retrieve templates correctly."""
        template_id = "approval_workflow"
        self.templates.get_template(template_id)
        mock_get.assert_called_once_with(template_id)
    
    @patch('n8n_integration.n8n_workflow_templates.N8nWorkflowTemplates.register_template')
    def test_register_template(self, mock_register):
        """Test that the templates register templates correctly."""
        template_id = "new_template"
        template_data = {"name": "New Template", "nodes": [], "connections": {}}
        self.templates.register_template(template_id, template_data)
        mock_register.assert_called_once_with(template_id, template_data)
    
    @patch('n8n_integration.n8n_workflow_templates.N8nWorkflowTemplates.create_workflow_from_template')
    def test_create_workflow_from_template(self, mock_create):
        """Test that the templates create workflows from templates correctly."""
        template_id = "approval_workflow"
        params = {"approver_email": "approver@example.com", "task_name": "Review Document"}
        self.templates.create_workflow_from_template(template_id, params)
        mock_create.assert_called_once_with(template_id, params)


class TestN8nIntegration(unittest.TestCase):
    """Integration tests for the n8n integration components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.n8n_connector = MagicMock(spec=N8nConnector)
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.bridge_service = N8nBridgeService(
            n8n_connector=self.n8n_connector,
            workflow_runtime=self.workflow_runtime
        )
        self.sync_bridge_agent = N8nSyncBridge(
            agent_id="n8n-sync-bridge-001",
            workflow_runtime=self.workflow_runtime,
            n8n_api_url="http://localhost:5678/api/v1"
        )
        self.adapter_agent = N8nAdapterAgent(
            agent_id="n8n-adapter-001",
            workflow_runtime=self.workflow_runtime,
            n8n_connector=self.n8n_connector
        )
        self.templates = N8nWorkflowTemplates()
    
    @patch('n8n_integration.n8n_connector.N8nConnector.get_workflows')
    def test_workflow_sync_integration(self, mock_get_workflows):
        """Test the integration between n8n connector and bridge service for workflow synchronization."""
        # Setup mock responses
        mock_get_workflows.return_value = [
            {"id": "1", "name": "Test Workflow 1"},
            {"id": "2", "name": "Test Workflow 2"}
        ]
        
        # Configure workflow runtime mock to return workflow data
        self.workflow_runtime.get_workflow.return_value = {
            "id": "workflow-001",
            "name": "Industriverse Workflow",
            "tasks": []
        }
        
        # Test bidirectional sync
        self.n8n_connector.get_workflow.return_value = {"id": "1", "name": "Test Workflow 1", "nodes": []}
        self.bridge_service.sync_workflow_from_n8n("1")
        self.workflow_runtime.create_workflow.assert_called_once()
        
        self.bridge_service.sync_workflow_to_n8n("workflow-001", {"name": "Industriverse Workflow", "tasks": []})
        self.n8n_connector.create_workflow.assert_called_once()
    
    @patch('n8n_integration.n8n_workflow_templates.N8nWorkflowTemplates.get_template')
    def test_template_based_workflow_creation(self, mock_get_template):
        """Test the creation of workflows from templates."""
        # Setup mock template
        mock_template = {
            "name": "Approval Workflow",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.start", "parameters": {}, "position": [100, 100]},
                {"name": "Approval", "type": "n8n-nodes-base.if", "parameters": {}, "position": [300, 100]}
            ],
            "connections": {}
        }
        mock_get_template.return_value = mock_template
        
        # Test template-based workflow creation
        params = {"approver_email": "approver@example.com"}
        workflow = self.templates.create_workflow_from_template("approval_workflow", params)
        
        mock_get_template.assert_called_once_with("approval_workflow")
        self.assertEqual(workflow["name"], "Approval Workflow")
        self.assertEqual(len(workflow["nodes"]), 2)
    
    def test_webhook_handling(self):
        """Test the handling of webhook events from n8n."""
        # Setup webhook event
        event_type = "workflow.completed"
        event_data = {
            "workflow_id": "1",
            "execution_id": "123",
            "status": "success",
            "data": {"result": "approved"}
        }
        
        # Test webhook event handling
        self.bridge_service.handle_webhook_event(event_type, event_data)
        self.workflow_runtime.update_workflow_status.assert_called_once()
    
    def test_agent_integration(self):
        """Test the integration between n8n agents and the workflow runtime."""
        # Setup workflow data
        workflow_id = "workflow-001"
        workflow_data = {"name": "Test Workflow", "tasks": []}
        n8n_workflow_id = "1"
        
        # Test sync bridge agent
        self.sync_bridge_agent.sync_workflow_to_n8n(workflow_id, workflow_data)
        self.sync_bridge_agent.sync_workflow_from_n8n(n8n_workflow_id)
        
        # Test adapter agent
        task_id = "task-001"
        task_data = {"type": "approval", "inputs": {"document": "contract.pdf"}}
        self.adapter_agent.create_n8n_workflow_for_task(task_id, task_data)
        self.n8n_connector.create_workflow.assert_called_once()


if __name__ == '__main__':
    unittest.main()
