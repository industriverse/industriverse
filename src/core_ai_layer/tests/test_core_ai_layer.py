"""
Test suite for Industriverse Core AI Layer

This module implements comprehensive tests for the Core AI Layer,
validating protocol-native architecture, distributed intelligence,
and resilience features.
"""

import os
import sys
import unittest
import asyncio
import logging
from unittest.mock import MagicMock, patch
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import components to test
from protocols.agent_core import AgentCore
from protocols.protocol_translator import ProtocolTranslator
from protocols.well_known_endpoint import WellKnownEndpoint
from protocols.mesh_boot_lifecycle import MeshBootLifecycle
from protocols.mesh_agent_intent_graph import MeshAgentIntentGraph
from protocols.consensus_resolver_agent import ConsensusResolverAgent
from protocols.protocol_conflict_resolver_agent import ProtocolConflictResolverAgent

from distributed_intelligence.core_ai_observability_agent import CoreAIObservabilityAgent
from distributed_intelligence.model_feedback_loop_agent import ModelFeedbackLoopAgent
from distributed_intelligence.model_simulation_replay_service import ModelSimulationReplayService
from distributed_intelligence.mesh_workload_router_agent import MeshWorkloadRouterAgent
from distributed_intelligence.intent_overlay_agent import IntentOverlayAgent
from distributed_intelligence.budget_monitor_agent import BudgetMonitorAgent
from distributed_intelligence.synthetic_data_generator_agent import SyntheticDataGeneratorAgent
from distributed_intelligence.model_health_prediction_agent import ModelHealthPredictionAgent

from main import CoreAILayer


class TestProtocolNativeArchitecture(unittest.TestCase):
    """
    Test cases for protocol-native architecture.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.protocol_translator = ProtocolTranslator()
        self.agent_core = AgentCore(self.protocol_translator)
    
    def tearDown(self):
        """
        Clean up test environment.
        """
        pass
    
    def test_agent_core_initialization(self):
        """
        Test agent core initialization.
        """
        self.assertIsNotNone(self.agent_core)
        self.assertIsNotNone(self.agent_core.protocol_translator)
    
    def test_protocol_translator_initialization(self):
        """
        Test protocol translator initialization.
        """
        self.assertIsNotNone(self.protocol_translator)
    
    async def test_agent_registration(self):
        """
        Test agent registration.
        """
        agent_id = "test-agent"
        agent_type = "test"
        capabilities = {"test": True}
        
        result = await self.agent_core.register_agent(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities
        )
        
        self.assertTrue(result.get("success", False))
        
        agent = await self.agent_core.get_agent(agent_id)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.get("agent_id"), agent_id)
        self.assertEqual(agent.get("agent_type"), agent_type)
    
    async def test_protocol_translation(self):
        """
        Test protocol translation.
        """
        source_protocol = "mcp"
        target_protocol = "a2a"
        message = {"type": "test", "content": "Hello, world!"}
        
        result = await self.protocol_translator.translate(
            source_protocol=source_protocol,
            target_protocol=target_protocol,
            message=message
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.get("protocol"), target_protocol)
    
    async def test_well_known_endpoint(self):
        """
        Test well-known endpoint.
        """
        well_known_endpoint = WellKnownEndpoint(self.agent_core)
        
        self.assertIsNotNone(well_known_endpoint)
        
        # Start endpoint
        await well_known_endpoint.start()
        
        # Check if endpoint is running
        self.assertTrue(well_known_endpoint.is_running())
        
        # Stop endpoint
        await well_known_endpoint.stop()
        
        # Check if endpoint is stopped
        self.assertFalse(well_known_endpoint.is_running())


class TestDistributedIntelligence(unittest.TestCase):
    """
    Test cases for distributed intelligence features.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.protocol_translator = ProtocolTranslator()
        self.agent_core = AgentCore(self.protocol_translator)
        self.mesh_agent_intent_graph = MeshAgentIntentGraph(self.agent_core)
    
    def tearDown(self):
        """
        Clean up test environment.
        """
        pass
    
    def test_observability_agent_initialization(self):
        """
        Test observability agent initialization.
        """
        observability_agent = CoreAIObservabilityAgent()
        self.assertIsNotNone(observability_agent)
    
    def test_model_feedback_loop_initialization(self):
        """
        Test model feedback loop initialization.
        """
        model_feedback_loop = ModelFeedbackLoopAgent()
        self.assertIsNotNone(model_feedback_loop)
    
    def test_model_simulation_replay_initialization(self):
        """
        Test model simulation replay initialization.
        """
        model_simulation_replay = ModelSimulationReplayService()
        self.assertIsNotNone(model_simulation_replay)
    
    def test_mesh_workload_router_initialization(self):
        """
        Test mesh workload router initialization.
        """
        mesh_workload_router = MeshWorkloadRouterAgent(self.agent_core)
        self.assertIsNotNone(mesh_workload_router)
    
    def test_intent_overlay_initialization(self):
        """
        Test intent overlay initialization.
        """
        intent_overlay = IntentOverlayAgent(self.mesh_agent_intent_graph)
        self.assertIsNotNone(intent_overlay)
    
    def test_budget_monitor_initialization(self):
        """
        Test budget monitor initialization.
        """
        budget_monitor = BudgetMonitorAgent()
        self.assertIsNotNone(budget_monitor)
    
    async def test_synthetic_data_generation(self):
        """
        Test synthetic data generation.
        """
        synthetic_data_generator = SyntheticDataGeneratorAgent()
        self.assertIsNotNone(synthetic_data_generator)
        
        # Register a dataset
        dataset_id = "test-dataset"
        dataset_type = "tabular"
        dataset_schema = {
            "columns": [
                {"name": "feature1", "type": "numeric", "min": 0, "max": 100},
                {"name": "feature2", "type": "numeric", "min": -50, "max": 50},
                {"name": "label", "type": "boolean", "prob_true": 0.3}
            ]
        }
        
        result = await synthetic_data_generator.register_dataset(
            dataset_id=dataset_id,
            dataset_type=dataset_type,
            dataset_schema=dataset_schema
        )
        
        self.assertTrue(result)
        
        # Register a generator
        generator_id = "test-generator"
        generator_type = "tabular"
        generator_config = {"method": "random"}
        
        result = await synthetic_data_generator.register_generator(
            generator_id=generator_id,
            generator_type=generator_type,
            generator_config=generator_config
        )
        
        self.assertTrue(result)
        
        # Link generator to dataset
        result = await synthetic_data_generator.link_generator_to_dataset(
            generator_id=generator_id,
            dataset_id=dataset_id
        )
        
        self.assertTrue(result)
        
        # Generate synthetic data
        result = await synthetic_data_generator.generate_synthetic_data(
            dataset_id=dataset_id,
            generator_id=generator_id,
            sample_count=10
        )
        
        self.assertTrue(result.get("success", False))
        self.assertEqual(len(result["data"]["data"]["feature1"]), 10)
    
    async def test_model_health_prediction(self):
        """
        Test model health prediction.
        """
        model_health_prediction = ModelHealthPredictionAgent()
        self.assertIsNotNone(model_health_prediction)
        
        # Register a model
        model_id = "test-model"
        model_type = "llm"
        model_metadata = {
            "version": "1.0",
            "parameters": "1.5T",
            "training_date": "2023-01-01"
        }
        
        result = await model_health_prediction.register_model(
            model_id=model_id,
            model_type=model_type,
            model_metadata=model_metadata
        )
        
        self.assertTrue(result)
        
        # Record health metrics
        result = await model_health_prediction.record_health_metrics(
            model_id=model_id,
            metrics={
                "accuracy": 0.95,
                "latency": 100,
                "error_rate": 0.01,
                "drift_score": 0.1,
                "resource_usage": 0.5
            }
        )
        
        self.assertTrue(result)
        
        # Get model
        model = model_health_prediction.get_model(model_id)
        self.assertIsNotNone(model)
        self.assertEqual(model.get("model_id"), model_id)
        self.assertEqual(model.get("model_type"), model_type)


class TestResilience(unittest.TestCase):
    """
    Test cases for resilience features.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        self.protocol_translator = ProtocolTranslator()
        self.agent_core = AgentCore(self.protocol_translator)
        
        # Create a mock config
        self.config = {
            "mesh_id": "test-mesh",
            "discovery": {
                "enabled": True,
                "interval_seconds": 30,
                "protocol": "mcp"
            },
            "coordination": {
                "leader_election": True,
                "quorum_size": 2,
                "heartbeat_interval_seconds": 5,
                "timeout_seconds": 15
            },
            "resilience": {
                "failover_chains": True,
                "redundant_pairs": True,
                "quorum_voting": True
            }
        }
        
        self.mesh_boot_lifecycle = MeshBootLifecycle(self.agent_core, self.config)
    
    def tearDown(self):
        """
        Clean up test environment.
        """
        pass
    
    def test_mesh_boot_lifecycle_initialization(self):
        """
        Test mesh boot lifecycle initialization.
        """
        self.assertIsNotNone(self.mesh_boot_lifecycle)
        self.assertEqual(self.mesh_boot_lifecycle.config.get("mesh_id"), "test-mesh")
    
    async def test_consensus_resolver(self):
        """
        Test consensus resolver.
        """
        consensus_resolver = ConsensusResolverAgent(self.agent_core)
        self.assertIsNotNone(consensus_resolver)
        
        # Start consensus resolver
        await consensus_resolver.start()
        
        # Check if consensus resolver is running
        self.assertTrue(consensus_resolver.is_running())
        
        # Submit a decision
        decision_id = "test-decision"
        options = ["option1", "option2", "option3"]
        weights = [0.5, 0.3, 0.2]
        
        result = await consensus_resolver.submit_decision(
            decision_id=decision_id,
            options=options,
            weights=weights
        )
        
        self.assertTrue(result.get("success", False))
        
        # Get decision
        decision = await consensus_resolver.get_decision(decision_id)
        self.assertIsNotNone(decision)
        self.assertEqual(decision.get("decision_id"), decision_id)
        
        # Stop consensus resolver
        await consensus_resolver.stop()
        
        # Check if consensus resolver is stopped
        self.assertFalse(consensus_resolver.is_running())
    
    async def test_protocol_conflict_resolver(self):
        """
        Test protocol conflict resolver.
        """
        protocol_conflict_resolver = ProtocolConflictResolverAgent(self.protocol_translator)
        self.assertIsNotNone(protocol_conflict_resolver)
        
        # Start protocol conflict resolver
        await protocol_conflict_resolver.start()
        
        # Check if protocol conflict resolver is running
        self.assertTrue(protocol_conflict_resolver.is_running())
        
        # Submit a conflict
        conflict_id = "test-conflict"
        protocol1 = "mcp"
        protocol2 = "a2a"
        message1 = {"type": "test", "content": "Hello from MCP!"}
        message2 = {"type": "test", "content": "Hello from A2A!"}
        
        result = await protocol_conflict_resolver.submit_conflict(
            conflict_id=conflict_id,
            protocol1=protocol1,
            protocol2=protocol2,
            message1=message1,
            message2=message2
        )
        
        self.assertTrue(result.get("success", False))
        
        # Get resolution
        resolution = await protocol_conflict_resolver.get_resolution(conflict_id)
        self.assertIsNotNone(resolution)
        self.assertEqual(resolution.get("conflict_id"), conflict_id)
        
        # Stop protocol conflict resolver
        await protocol_conflict_resolver.stop()
        
        # Check if protocol conflict resolver is stopped
        self.assertFalse(protocol_conflict_resolver.is_running())


class TestCoreAILayer(unittest.TestCase):
    """
    Test cases for the Core AI Layer as a whole.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        # Create a mock config path
        self.config_path = "tests/mock_config.yaml"
        
        # Create a mock config file
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, "w") as f:
            json.dump({
                "mesh_id": "test-mesh",
                "discovery": {
                    "enabled": True,
                    "interval_seconds": 30,
                    "protocol": "mcp"
                },
                "coordination": {
                    "leader_election": True,
                    "quorum_size": 2,
                    "heartbeat_interval_seconds": 5,
                    "timeout_seconds": 15
                },
                "resilience": {
                    "failover_chains": True,
                    "redundant_pairs": True,
                    "quorum_voting": True
                }
            }, f)
        
        # Create Core AI Layer
        self.core_ai_layer = CoreAILayer(config_path=self.config_path)
    
    def tearDown(self):
        """
        Clean up test environment.
        """
        # Remove mock config file
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
    
    def test_core_ai_layer_initialization(self):
        """
        Test Core AI Layer initialization.
        """
        self.assertIsNotNone(self.core_ai_layer)
    
    async def test_core_ai_layer_lifecycle(self):
        """
        Test Core AI Layer lifecycle.
        """
        # Initialize Core AI Layer
        result = await self.core_ai_layer.initialize()
        self.assertTrue(result)
        
        # Start Core AI Layer
        result = await self.core_ai_layer.start()
        self.assertTrue(result)
        
        # Check if Core AI Layer is running
        self.assertTrue(self.core_ai_layer.running)
        
        # Perform health check
        health = await self.core_ai_layer.health_check()
        self.assertIsNotNone(health)
        self.assertEqual(health.get("status"), "healthy")
        
        # Stop Core AI Layer
        result = await self.core_ai_layer.stop()
        self.assertTrue(result)
        
        # Check if Core AI Layer is stopped
        self.assertFalse(self.core_ai_layer.running)


def run_async_test(test_case):
    """
    Run an async test case.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_case())


if __name__ == "__main__":
    unittest.main()
