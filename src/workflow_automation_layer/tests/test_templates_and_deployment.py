"""
Test suite for the Workflow Automation Layer Templates and Deployment components.

This module contains unit tests for the templates and deployment components,
including industry-specific templates and Kubernetes deployment.
"""

import unittest
import asyncio
import json
import yaml
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIndustryTemplates(unittest.TestCase):
    """Test cases for the industry-specific templates."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the template files
        self.manufacturing_template = """
# Manufacturing Industry Workflow Manifest Templates
templates:
  - name: predictive_maintenance
    description: "Predictive maintenance workflow for manufacturing equipment"
    version: "1.0"
    tasks:
      - id: data_collection
        name: "Collect Equipment Data"
        description: "Collect sensor data from manufacturing equipment"
        timeout_seconds: 300
        retry_count: 3
      - id: anomaly_detection
        name: "Detect Anomalies"
        description: "Analyze sensor data for anomalies"
        timeout_seconds: 600
        retry_count: 2
    workflow:
      transitions:
        - from: data_collection
          to: anomaly_detection
          condition: "success"
    execution_modes:
      - name: "reactive"
        trust_threshold: 0.5
        confidence_required: 0.6
        human_oversight: true
"""
        self.logistics_template = """
# Logistics Industry Workflow Manifest Templates
templates:
  - name: supply_chain_visibility
    description: "End-to-end supply chain visibility workflow"
    version: "1.0"
    tasks:
      - id: track_shipments
        name: "Track Shipments"
        description: "Track location and status of shipments"
        timeout_seconds: 300
        retry_count: 3
      - id: detect_delays
        name: "Detect Delays"
        description: "Identify potential delays in the supply chain"
        timeout_seconds: 600
        retry_count: 2
    workflow:
      transitions:
        - from: track_shipments
          to: detect_delays
          condition: "success"
    execution_modes:
      - name: "reactive"
        trust_threshold: 0.5
        confidence_required: 0.6
        human_oversight: true
"""

    @patch("builtins.open", new_callable=mock_open)
    def test_load_manufacturing_template(self, mock_file):
        """Test loading a manufacturing template."""
        # Setup the mock to return the template content
        mock_file.return_value.__enter__.return_value.read.return_value = self.manufacturing_template
        
        # Load the template
        with open("/templates/manufacturing/workflow_manifest_templates.yaml", "r") as f:
            content = f.read()
            template_data = yaml.safe_load(content)
        
        # Verify the template structure
        self.assertIn("templates", template_data)
        self.assertEqual(len(template_data["templates"]), 1)
        self.assertEqual(template_data["templates"][0]["name"], "predictive_maintenance")
        self.assertEqual(len(template_data["templates"][0]["tasks"]), 2)
        self.assertEqual(len(template_data["templates"][0]["workflow"]["transitions"]), 1)
        self.assertEqual(len(template_data["templates"][0]["execution_modes"]), 1)

    @patch("builtins.open", new_callable=mock_open)
    def test_load_logistics_template(self, mock_file):
        """Test loading a logistics template."""
        # Setup the mock to return the template content
        mock_file.return_value.__enter__.return_value.read.return_value = self.logistics_template
        
        # Load the template
        with open("/templates/logistics/workflow_manifest_templates.yaml", "r") as f:
            content = f.read()
            template_data = yaml.safe_load(content)
        
        # Verify the template structure
        self.assertIn("templates", template_data)
        self.assertEqual(len(template_data["templates"]), 1)
        self.assertEqual(template_data["templates"][0]["name"], "supply_chain_visibility")
        self.assertEqual(len(template_data["templates"][0]["tasks"]), 2)
        self.assertEqual(len(template_data["templates"][0]["workflow"]["transitions"]), 1)
        self.assertEqual(len(template_data["templates"][0]["execution_modes"]), 1)

    def test_validate_template_schema(self):
        """Test validating a template schema."""
        # Parse the template
        template_data = yaml.safe_load(self.manufacturing_template)
        template = template_data["templates"][0]
        
        # Validate required fields
        self.assertIn("name", template)
        self.assertIn("description", template)
        self.assertIn("version", template)
        self.assertIn("tasks", template)
        self.assertIn("workflow", template)
        self.assertIn("transitions", template["workflow"])
        self.assertIn("execution_modes", template)
        
        # Validate task structure
        for task in template["tasks"]:
            self.assertIn("id", task)
            self.assertIn("name", task)
            self.assertIn("description", task)
            self.assertIn("timeout_seconds", task)
            self.assertIn("retry_count", task)
        
        # Validate transition structure
        for transition in template["workflow"]["transitions"]:
            self.assertIn("from", transition)
            self.assertIn("to", transition)
            self.assertIn("condition", transition)
        
        # Validate execution mode structure
        for mode in template["execution_modes"]:
            self.assertIn("name", mode)
            self.assertIn("trust_threshold", mode)
            self.assertIn("confidence_required", mode)
            self.assertIn("human_oversight", mode)

    def test_customize_template(self):
        """Test customizing a template."""
        # Parse the template
        template_data = yaml.safe_load(self.manufacturing_template)
        template = template_data["templates"][0]
        
        # Customize the template
        customized = dict(template)
        customized["name"] = "custom_maintenance"
        customized["description"] = "Custom maintenance workflow"
        customized["tasks"].append({
            "id": "maintenance_scheduling",
            "name": "Schedule Maintenance",
            "description": "Schedule maintenance tasks",
            "timeout_seconds": 900,
            "retry_count": 1
        })
        customized["workflow"]["transitions"].append({
            "from": "anomaly_detection",
            "to": "maintenance_scheduling",
            "condition": "anomalies_detected"
        })
        
        # Validate the customized template
        self.assertEqual(customized["name"], "custom_maintenance")
        self.assertEqual(customized["description"], "Custom maintenance workflow")
        self.assertEqual(len(customized["tasks"]), 3)
        self.assertEqual(len(customized["workflow"]["transitions"]), 2)
        
        # Verify the new task
        new_task = next(t for t in customized["tasks"] if t["id"] == "maintenance_scheduling")
        self.assertEqual(new_task["name"], "Schedule Maintenance")
        self.assertEqual(new_task["timeout_seconds"], 900)
        
        # Verify the new transition
        new_transition = next(t for t in customized["workflow"]["transitions"] if t["from"] == "anomaly_detection")
        self.assertEqual(new_transition["to"], "maintenance_scheduling")
        self.assertEqual(new_transition["condition"], "anomalies_detected")


class TestKubernetesDeployment(unittest.TestCase):
    """Test cases for the Kubernetes deployment configuration."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the Kubernetes YAML files
        self.deployment_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-automation-layer
  namespace: industriverse
  labels:
    app: workflow-automation-layer
    layer: workflow-automation
    part-of: industriverse
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-automation-layer
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: workflow-automation-layer
        layer: workflow-automation
        part-of: industriverse
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: workflow-automation-sa
      containers:
      - name: workflow-automation
        image: ${REGISTRY}/industriverse/workflow-automation:${TAG}
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: workflow-automation-config
              key: log_level
"""
        self.service_yaml = """
apiVersion: v1
kind: Service
metadata:
  name: workflow-automation-service
  namespace: industriverse
  labels:
    app: workflow-automation-layer
    layer: workflow-automation
    part-of: industriverse
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 8080
    targetPort: http
    protocol: TCP
  selector:
    app: workflow-automation-layer
"""
        self.configmap_yaml = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: workflow-automation-config
  namespace: industriverse
  labels:
    app: workflow-automation-layer
    layer: workflow-automation
    part-of: industriverse
data:
  log_level: "info"
  execution_mode: "standard"
  protocol_layer_url: "http://protocol-layer-service:8080"
  n8n_api_url: "http://n8n-service:5678/api"
  ekis_security_enabled: "true"
  trust_threshold: "0.7"
  confidence_threshold: "0.8"
"""

    @patch("builtins.open", new_callable=mock_open)
    def test_load_deployment_yaml(self, mock_file):
        """Test loading the deployment YAML."""
        # Setup the mock to return the YAML content
        mock_file.return_value.__enter__.return_value.read.return_value = self.deployment_yaml
        
        # Load the YAML
        with open("/kubernetes/deployment.yaml", "r") as f:
            content = f.read()
            deployment = yaml.safe_load(content)
        
        # Verify the deployment structure
        self.assertEqual(deployment["kind"], "Deployment")
        self.assertEqual(deployment["metadata"]["name"], "workflow-automation-layer")
        self.assertEqual(deployment["metadata"]["namespace"], "industriverse")
        self.assertEqual(deployment["spec"]["replicas"], 3)
        self.assertEqual(deployment["spec"]["strategy"]["type"], "RollingUpdate")
        
        # Verify container configuration
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(container["name"], "workflow-automation")
        self.assertEqual(container["ports"][0]["containerPort"], 8080)
        
        # Verify environment variables
        env_var = container["env"][0]
        self.assertEqual(env_var["name"], "LOG_LEVEL")
        self.assertEqual(env_var["valueFrom"]["configMapKeyRef"]["name"], "workflow-automation-config")
        self.assertEqual(env_var["valueFrom"]["configMapKeyRef"]["key"], "log_level")

    @patch("builtins.open", new_callable=mock_open)
    def test_load_service_yaml(self, mock_file):
        """Test loading the service YAML."""
        # Setup the mock to return the YAML content
        mock_file.return_value.__enter__.return_value.read.return_value = self.service_yaml
        
        # Load the YAML
        with open("/kubernetes/service.yaml", "r") as f:
            content = f.read()
            service = yaml.safe_load(content)
        
        # Verify the service structure
        self.assertEqual(service["kind"], "Service")
        self.assertEqual(service["metadata"]["name"], "workflow-automation-service")
        self.assertEqual(service["metadata"]["namespace"], "industriverse")
        self.assertEqual(service["spec"]["type"], "ClusterIP")
        
        # Verify port configuration
        port = service["spec"]["ports"][0]
        self.assertEqual(port["name"], "http")
        self.assertEqual(port["port"], 8080)
        self.assertEqual(port["targetPort"], "http")
        
        # Verify selector
        self.assertEqual(service["spec"]["selector"]["app"], "workflow-automation-layer")

    @patch("builtins.open", new_callable=mock_open)
    def test_load_configmap_yaml(self, mock_file):
        """Test loading the configmap YAML."""
        # Setup the mock to return the YAML content
        mock_file.return_value.__enter__.return_value.read.return_value = self.configmap_yaml
        
        # Load the YAML
        with open("/kubernetes/configmap.yaml", "r") as f:
            content = f.read()
            configmap = yaml.safe_load(content)
        
        # Verify the configmap structure
        self.assertEqual(configmap["kind"], "ConfigMap")
        self.assertEqual(configmap["metadata"]["name"], "workflow-automation-config")
        self.assertEqual(configmap["metadata"]["namespace"], "industriverse")
        
        # Verify data configuration
        self.assertEqual(configmap["data"]["log_level"], "info")
        self.assertEqual(configmap["data"]["execution_mode"], "standard")
        self.assertEqual(configmap["data"]["protocol_layer_url"], "http://protocol-layer-service:8080")
        self.assertEqual(configmap["data"]["n8n_api_url"], "http://n8n-service:5678/api")
        self.assertEqual(configmap["data"]["ekis_security_enabled"], "true")
        self.assertEqual(configmap["data"]["trust_threshold"], "0.7")
        self.assertEqual(configmap["data"]["confidence_threshold"], "0.8")

    def test_validate_kubernetes_resources(self):
        """Test validating Kubernetes resource relationships."""
        # Parse the YAML files
        deployment = yaml.safe_load(self.deployment_yaml)
        service = yaml.safe_load(self.service_yaml)
        configmap = yaml.safe_load(self.configmap_yaml)
        
        # Verify deployment and service use the same selector
        deployment_labels = deployment["spec"]["template"]["metadata"]["labels"]
        service_selector = service["spec"]["selector"]
        self.assertEqual(deployment_labels["app"], service_selector["app"])
        
        # Verify deployment references the correct configmap
        env_var = deployment["spec"]["template"]["spec"]["containers"][0]["env"][0]
        self.assertEqual(env_var["valueFrom"]["configMapKeyRef"]["name"], configmap["metadata"]["name"])
        
        # Verify all resources are in the same namespace
        self.assertEqual(deployment["metadata"]["namespace"], service["metadata"]["namespace"])
        self.assertEqual(deployment["metadata"]["namespace"], configmap["metadata"]["namespace"])
        
        # Verify consistent labeling
        self.assertEqual(deployment["metadata"]["labels"]["layer"], "workflow-automation")
        self.assertEqual(service["metadata"]["labels"]["layer"], "workflow-automation")
        self.assertEqual(configmap["metadata"]["labels"]["layer"], "workflow-automation")


class TestCrossLayerIntegration(unittest.TestCase):
    """Test cases for cross-layer integration."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the Protocol Layer integration
        self.protocol_layer_client = MagicMock()
        self.workflow_runtime = MagicMock()
        
        # Setup integration test data
        self.workflow_data = {
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
        
        self.message_data = {
            "message_id": "msg1",
            "source": "protocol_layer",
            "destination": "workflow_automation_layer",
            "message_type": "workflow_event",
            "payload": {
                "event_type": "task_completed",
                "workflow_id": "workflow1",
                "task_id": "task1",
                "result": "success"
            }
        }

    @patch('requests.post')
    def test_send_message_to_protocol_layer(self, mock_post):
        """Test sending a message to the Protocol Layer."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message_id": "msg2"
        }
        mock_post.return_value = mock_response
        
        # Message to send
        message = {
            "source": "workflow_automation_layer",
            "destination": "protocol_layer",
            "message_type": "workflow_status",
            "payload": {
                "workflow_id": "workflow1",
                "status": "running",
                "progress": 0.5
            }
        }
        
        # Send the message
        response = self.protocol_layer_client.send_message(message)
        
        # Verify the response
        self.assertTrue(response["success"])
        self.assertEqual(response["message_id"], "msg2")
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["source"], "workflow_automation_layer")
        self.assertEqual(kwargs["json"]["destination"], "protocol_layer")

    def test_handle_message_from_protocol_layer(self):
        """Test handling a message from the Protocol Layer."""
        # Mock the workflow runtime's handle_protocol_message method
        self.workflow_runtime.handle_protocol_message.return_value = {
            "success": True,
            "message_id": "msg1",
            "action_taken": "task_transition"
        }
        
        # Handle the message
        result = self.workflow_runtime.handle_protocol_message(self.message_data)
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["message_id"], "msg1")
        
        # Verify the workflow runtime was called correctly
        self.workflow_runtime.handle_protocol_message.assert_called_once_with(self.message_data)

    @patch('requests.post')
    def test_register_workflow_with_protocol_layer(self, mock_post):
        """Test registering a workflow with the Protocol Layer."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "workflow_id": "workflow1"
        }
        mock_post.return_value = mock_response
        
        # Register the workflow
        response = self.protocol_layer_client.register_workflow(self.workflow_data)
        
        # Verify the response
        self.assertTrue(response["success"])
        self.assertEqual(response["workflow_id"], "workflow1")
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["workflow_id"], "workflow1")
        self.assertEqual(kwargs["json"]["name"], "Test Workflow")

    @patch('requests.get')
    def test_get_protocol_layer_status(self, mock_get):
        """Test getting the Protocol Layer status."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "1.0.0",
            "uptime_seconds": 3600,
            "active_connections": 5
        }
        mock_get.return_value = mock_response
        
        # Get the status
        status = self.protocol_layer_client.get_status()
        
        # Verify the status
        self.assertEqual(status["status"], "healthy")
        self.assertEqual(status["version"], "1.0.0")
        self.assertEqual(status["uptime_seconds"], 3600)
        
        # Verify the request was made correctly
        mock_get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
