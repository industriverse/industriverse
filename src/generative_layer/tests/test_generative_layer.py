"""
Test suite for Industriverse Generative Layer

This module provides comprehensive testing for the Generative Layer with
protocol-native architecture and MCP/A2A integration.
"""

import json
import os
import pytest
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components to test
from protocols.agent_core import AgentCore
from protocols.protocol_translator import ProtocolTranslator
from protocols.well_known_endpoint import WellKnownEndpoint
from protocols.mesh_boot_lifecycle import MeshBootLifecycle
from protocols.mesh_agent_intent_graph import MeshAgentIntentGraph
from protocols.consensus_resolver_agent import ConsensusResolverAgent
from protocols.protocol_conflict_resolver_agent import ProtocolConflictResolverAgent

from distributed_intelligence.prompt_mutator_agent import PromptMutatorAgent
from distributed_intelligence.artifact_registry_agent import ArtifactRegistryAgent
from distributed_intelligence.agent_capsule_integration import AgentCapsuleIntegration
from distributed_intelligence.agent_lineage_manager import AgentLineageManager
from distributed_intelligence.collaborative_workflow_agent import CollaborativeWorkflowAgent
from distributed_intelligence.zk_artifact_traceability import ZKArtifactTraceability

from template_system import TemplateSystem
from ui_component_system import UIComponentSystem
from variability_management import VariabilityManagement
from performance_optimization import PerformanceOptimization
from documentation_generation import DocumentationGeneration
from security_accessibility import SecurityAccessibility
from testing_framework import TestingFramework

from main import GenerativeLayer

class TestAgentCore(unittest.TestCase):
    """Test cases for AgentCore."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "agent_id": "test_agent",
            "agent_name": "Test Agent",
            "agent_version": "1.0.0",
            "agent_description": "Test Agent Description",
            "mcp_enabled": True,
            "a2a_enabled": True,
            "mesh_coordination_role": "follower",
            "intelligence_role": "generator",
            "resilience_mode": "active"
        }
        self.agent_core = AgentCore(self.config)
    
    def test_initialization(self):
        """Test initialization of AgentCore."""
        self.assertEqual(self.agent_core.agent_id, "test_agent")
        self.assertEqual(self.agent_core.agent_name, "Test Agent")
        self.assertEqual(self.agent_core.agent_version, "1.0.0")
        self.assertEqual(self.agent_core.agent_description, "Test Agent Description")
        self.assertTrue(self.agent_core.mcp_enabled)
        self.assertTrue(self.agent_core.a2a_enabled)
        self.assertEqual(self.agent_core.mesh_coordination_role, "follower")
        self.assertEqual(self.agent_core.intelligence_role, "generator")
        self.assertEqual(self.agent_core.resilience_mode, "active")
    
    def test_register_mcp_event_handler(self):
        """Test registering MCP event handler."""
        handler = MagicMock()
        self.agent_core.register_mcp_event_handler("test_event", handler)
        self.assertIn("test_event", self.agent_core.mcp_event_handlers)
        self.assertEqual(self.agent_core.mcp_event_handlers["test_event"], handler)
    
    def test_register_a2a_event_handler(self):
        """Test registering A2A event handler."""
        handler = MagicMock()
        self.agent_core.register_a2a_event_handler("test_event", handler)
        self.assertIn("test_event", self.agent_core.a2a_event_handlers)
        self.assertEqual(self.agent_core.a2a_event_handlers["test_event"], handler)
    
    @patch.object(AgentCore, '_send_mcp_event_internal')
    def test_send_mcp_event(self, mock_send):
        """Test sending MCP event."""
        event_data = {"key": "value"}
        self.agent_core.send_mcp_event("test_event", event_data)
        mock_send.assert_called_once_with("test_event", event_data)
    
    @patch.object(AgentCore, '_send_a2a_event_internal')
    def test_send_a2a_event(self, mock_send):
        """Test sending A2A event."""
        event_data = {"key": "value"}
        self.agent_core.send_a2a_event("test_event", event_data)
        mock_send.assert_called_once_with("test_event", event_data)

class TestProtocolTranslator(unittest.TestCase):
    """Test cases for ProtocolTranslator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_core = MagicMock()
        self.protocol_translator = ProtocolTranslator(self.agent_core)
    
    def test_translate_mcp_to_a2a(self):
        """Test translating MCP to A2A."""
        mcp_event = {
            "event_type": "test_event",
            "data": {"key": "value"}
        }
        a2a_event = self.protocol_translator.translate_mcp_to_a2a(mcp_event)
        self.assertIn("agentId", a2a_event)
        self.assertIn("eventType", a2a_event)
        self.assertIn("payload", a2a_event)
        self.assertEqual(a2a_event["eventType"], "test_event")
        self.assertEqual(a2a_event["payload"]["key"], "value")
    
    def test_translate_a2a_to_mcp(self):
        """Test translating A2A to MCP."""
        a2a_event = {
            "agentId": "test_agent",
            "eventType": "test_event",
            "payload": {"key": "value"}
        }
        mcp_event = self.protocol_translator.translate_a2a_to_mcp(a2a_event)
        self.assertIn("event_type", mcp_event)
        self.assertIn("data", mcp_event)
        self.assertEqual(mcp_event["event_type"], "test_event")
        self.assertEqual(mcp_event["data"]["key"], "value")

class TestTemplateSystem(unittest.TestCase):
    """Test cases for TemplateSystem."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_core = MagicMock()
        self.template_system = TemplateSystem(self.agent_core)
    
    def test_register_template(self):
        """Test registering a template."""
        template_id = "test_template"
        name = "Test Template"
        template_content = {"key": "value"}
        metadata = {"meta_key": "meta_value"}
        
        self.template_system.register_template(
            template_id=template_id,
            name=name,
            template_content=template_content,
            metadata=metadata
        )
        
        self.assertIn(template_id, self.template_system.templates)
        self.assertEqual(self.template_system.templates[template_id]["name"], name)
        self.assertEqual(self.template_system.templates[template_id]["content"], template_content)
        self.assertEqual(self.template_system.templates[template_id]["metadata"], metadata)
    
    def test_has_template(self):
        """Test checking if template exists."""
        template_id = "test_template"
        name = "Test Template"
        template_content = {"key": "value"}
        
        self.template_system.register_template(
            template_id=template_id,
            name=name,
            template_content=template_content
        )
        
        self.assertTrue(self.template_system.has_template(template_id))
        self.assertFalse(self.template_system.has_template("non_existent_template"))
    
    def test_generate_from_template(self):
        """Test generating from template."""
        template_id = "test_template"
        name = "Test Template"
        template_content = {
            "type": "test",
            "name": "{{name}}",
            "description": "{{description}}",
            "value": "{{value|default_value}}"
        }
        
        self.template_system.register_template(
            template_id=template_id,
            name=name,
            template_content=template_content
        )
        
        params = {
            "name": "Test Name",
            "description": "Test Description"
        }
        
        result = self.template_system.generate_from_template(
            template_id=template_id,
            params=params
        )
        
        self.assertEqual(result["type"], "test")
        self.assertEqual(result["name"], "Test Name")
        self.assertEqual(result["description"], "Test Description")
        self.assertEqual(result["value"], "default_value")

class TestUIComponentSystem(unittest.TestCase):
    """Test cases for UIComponentSystem."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_core = MagicMock()
        self.ui_component_system = UIComponentSystem(self.agent_core)
    
    def test_register_component_type(self):
        """Test registering a component type."""
        component_type = "test_component"
        schema = {"type": "object", "properties": {"key": {"type": "string"}}}
        renderer = MagicMock()
        
        self.ui_component_system.register_component_type(
            component_type=component_type,
            schema=schema,
            renderer=renderer
        )
        
        self.assertIn(component_type, self.ui_component_system.component_types)
        self.assertEqual(self.ui_component_system.component_types[component_type]["schema"], schema)
        self.assertEqual(self.ui_component_system.component_types[component_type]["renderer"], renderer)
    
    def test_has_component_type(self):
        """Test checking if component type exists."""
        component_type = "test_component"
        schema = {"type": "object", "properties": {"key": {"type": "string"}}}
        renderer = MagicMock()
        
        self.ui_component_system.register_component_type(
            component_type=component_type,
            schema=schema,
            renderer=renderer
        )
        
        self.assertTrue(self.ui_component_system.has_component_type(component_type))
        self.assertFalse(self.ui_component_system.has_component_type("non_existent_component"))

class TestPromptMutatorAgent(unittest.TestCase):
    """Test cases for PromptMutatorAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_core = MagicMock()
        self.prompt_mutator = PromptMutatorAgent(self.agent_core)
    
    def test_mutate_prompt(self):
        """Test mutating a prompt."""
        prompt_id = "test_prompt"
        original_prompt = "Generate a dashboard for {{industry}}"
        context = {"industry": "manufacturing"}
        feedback = {"error": "Missing specific metrics"}
        
        result = self.prompt_mutator.mutate_prompt(
            prompt_id=prompt_id,
            original_prompt=original_prompt,
            context=context,
            feedback=feedback
        )
        
        self.assertIn("prompt", result)
        self.assertIn("steps", result)
        self.assertIn("confidence", result)
        self.assertNotEqual(result["prompt"], original_prompt)
        self.assertGreater(len(result["steps"]), 0)
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)

class TestAgentCapsuleIntegration(unittest.TestCase):
    """Test cases for AgentCapsuleIntegration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_core = MagicMock()
        self.agent_capsule_integration = AgentCapsuleIntegration(self.agent_core)
    
    def test_create_capsule(self):
        """Test creating a capsule."""
        agent_id = "test_agent"
        capsule_type = "dynamic_island"
        capsule_data = {
            "title": "Test Capsule",
            "description": "Test Description",
            "status": "active"
        }
        
        result = self.agent_capsule_integration.create_capsule(
            agent_id=agent_id,
            capsule_type=capsule_type,
            capsule_data=capsule_data
        )
        
        self.assertIn("capsule_id", result)
        self.assertIn("html", result)
        self.assertIn("css", result)
        self.assertIn("js", result)
        self.assertIn("Test Capsule", result["html"])

class TestZKArtifactTraceability(unittest.TestCase):
    """Test cases for ZKArtifactTraceability."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_core = MagicMock()
        self.zk_artifact_traceability = ZKArtifactTraceability(self.agent_core)
    
    def test_generate_proof(self):
        """Test generating a proof."""
        content = {"key": "value"}
        metadata = {"meta_key": "meta_value"}
        
        proof_hash = self.zk_artifact_traceability.generate_proof(
            content=content,
            metadata=metadata
        )
        
        self.assertIsNotNone(proof_hash)
        self.assertGreater(len(proof_hash), 0)
    
    def test_verify_proof(self):
        """Test verifying a proof."""
        content = {"key": "value"}
        metadata = {"meta_key": "meta_value"}
        
        proof_hash = self.zk_artifact_traceability.generate_proof(
            content=content,
            metadata=metadata
        )
        
        result = self.zk_artifact_traceability.verify_proof(
            content=content,
            metadata=metadata,
            proof_hash=proof_hash
        )
        
        self.assertTrue(result)
        
        # Test with modified content
        modified_content = {"key": "modified_value"}
        result = self.zk_artifact_traceability.verify_proof(
            content=modified_content,
            metadata=metadata,
            proof_hash=proof_hash
        )
        
        self.assertFalse(result)

class TestGenerativeLayer(unittest.TestCase):
    """Test cases for GenerativeLayer."""
    
    @patch.object(AgentCore, '__init__', return_value=None)
    @patch.object(AgentCore, 'register_mcp_event_handler')
    @patch.object(AgentCore, 'register_a2a_event_handler')
    @patch.object(MeshBootLifecycle, 'initialize')
    @patch.object(MeshBootLifecycle, 'register_with_node')
    @patch.object(MeshAgentIntentGraph, 'initialize')
    def setUp(self, mock_intent_init, mock_register, mock_boot_init, 
              mock_register_a2a, mock_register_mcp, mock_agent_init):
        """Set up test fixtures."""
        self.generative_layer = GenerativeLayer()
        
        # Mock components
        self.generative_layer.agent_core = MagicMock()
        self.generative_layer.protocol_translator = MagicMock()
        self.generative_layer.well_known_endpoint = MagicMock()
        self.generative_layer.mesh_boot_lifecycle = MagicMock()
        self.generative_layer.mesh_agent_intent_graph = MagicMock()
        self.generative_layer.consensus_resolver = MagicMock()
        self.generative_layer.protocol_conflict_resolver = MagicMock()
        self.generative_layer.prompt_mutator = MagicMock()
        self.generative_layer.artifact_registry = MagicMock()
        self.generative_layer.agent_capsule_integration = MagicMock()
        self.generative_layer.agent_lineage_manager = MagicMock()
        self.generative_layer.collaborative_workflow = MagicMock()
        self.generative_layer.zk_artifact_traceability = MagicMock()
        self.generative_layer.template_system = MagicMock()
        self.generative_layer.ui_component_system = MagicMock()
        self.generative_layer.variability_management = MagicMock()
        self.generative_layer.performance_optimization = MagicMock()
        self.generative_layer.documentation_generation = MagicMock()
        self.generative_layer.security_accessibility = MagicMock()
        self.generative_layer.testing_framework = MagicMock()
    
    def test_handle_template_generate(self):
        """Test handling template generation event."""
        # Mock template_system.generate_from_template
        self.generative_layer.template_system.generate_from_template.return_value = {"key": "value"}
        
        # Mock zk_artifact_traceability.generate_proof
        self.generative_layer.zk_artifact_traceability.generate_proof.return_value = "proof_hash"
        
        event = {
            "template_id": "test_template",
            "params": {"key": "value"},
            "options": {}
        }
        
        result = self.generative_layer._handle_template_generate(event)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["template_id"], "test_template")
        self.assertEqual(result["result"], {"key": "value"})
        self.assertEqual(result["zk_proof_hash"], "proof_hash")
        
        self.generative_layer.template_system.generate_from_template.assert_called_once_with(
            template_id="test_template",
            params={"key": "value"},
            options={}
        )
    
    def test_handle_ui_component_generate(self):
        """Test handling UI component generation event."""
        # Mock ui_component_system.generate_component
        self.generative_layer.ui_component_system.generate_component.return_value = {"key": "value"}
        
        # Mock zk_artifact_traceability.generate_proof
        self.generative_layer.zk_artifact_traceability.generate_proof.return_value = "proof_hash"
        
        event = {
            "component_type": "test_component",
            "params": {"key": "value"},
            "options": {}
        }
        
        result = self.generative_layer._handle_ui_component_generate(event)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["component_type"], "test_component")
        self.assertEqual(result["result"], {"key": "value"})
        self.assertEqual(result["zk_proof_hash"], "proof_hash")
        
        self.generative_layer.ui_component_system.generate_component.assert_called_once_with(
            component_type="test_component",
            params={"key": "value"},
            options={}
        )
    
    def test_handle_offer_generate(self):
        """Test handling offer generation event."""
        # Mock template_system.has_template
        self.generative_layer.template_system.has_template.return_value = True
        
        # Mock template_system.generate_from_template
        self.generative_layer.template_system.generate_from_template.return_value = {"key": "value"}
        
        # Mock ui_component_system.generate_component
        self.generative_layer.ui_component_system.generate_component.return_value = {"ui_key": "ui_value"}
        
        # Mock documentation_generation.generate_documentation
        self.generative_layer.documentation_generation.generate_documentation.return_value = {"doc_key": "doc_value"}
        
        # Mock zk_artifact_traceability.generate_proof
        self.generative_layer.zk_artifact_traceability.generate_proof.return_value = "proof_hash"
        
        event = {
            "offer_id": "test_offer",
            "offer_type": "industrial_dashboard",
            "params": {"key": "value"},
            "options": {
                "generate_ui": True,
                "ui_component_types": ["dashboard"],
                "generate_documentation": True
            }
        }
        
        result = self.generative_layer._handle_offer_generate(event)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["offer_id"], "test_offer")
        self.assertEqual(result["template_result"], {"key": "value"})
        self.assertEqual(result["ui_components"], {"dashboard": {"ui_key": "ui_value"}})
        self.assertEqual(result["documentation"], {"doc_key": "doc_value"})
        self.assertEqual(result["zk_proof_hash"], "proof_hash")
        
        self.generative_layer.template_system.generate_from_template.assert_called_once_with(
            template_id="industrial_dashboard_template",
            params={"key": "value"},
            options={"generate_ui": True, "ui_component_types": ["dashboard"], "generate_documentation": True}
        )
        
        self.generative_layer.ui_component_system.generate_component.assert_called_once_with(
            component_type="dashboard",
            params={"key": "value"},
            options={"generate_ui": True, "ui_component_types": ["dashboard"], "generate_documentation": True}
        )
        
        self.generative_layer.documentation_generation.generate_documentation.assert_called_once()
        
        self.generative_layer.artifact_registry.register_artifact.assert_called_once()

if __name__ == "__main__":
    unittest.main()
