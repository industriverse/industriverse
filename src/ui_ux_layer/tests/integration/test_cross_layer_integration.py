"""
Integration Test Module - Tests the integration between the UI/UX Layer and all other layers of the Industriverse ecosystem.

This module provides comprehensive tests for cross-layer integration, ensuring bidirectional communication,
state synchronization, and seamless user experience across the entire Industriverse ecosystem.
"""

import os
import sys
import json
import logging
import asyncio
import unittest
from typing import Dict, List, Any, Optional, Union

# Core module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core.cross_layer_integration.cross_layer_integration import CrossLayerIntegration, LayerType, IntegrationStatus

class CrossLayerIntegrationTest(unittest.TestCase):
    """Test case for cross-layer integration."""
    
    def setUp(self):
        """Set up the test case."""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Create cross-layer integration
        self.integration = CrossLayerIntegration({
            'data_layer_url': os.environ.get('DATA_LAYER_URL', 'http://data-layer.industriverse.svc.cluster.local:8080'),
            'core_ai_layer_url': os.environ.get('CORE_AI_LAYER_URL', 'http://core-ai-layer.industriverse.svc.cluster.local:8080'),
            'generative_layer_url': os.environ.get('GENERATIVE_LAYER_URL', 'http://generative-layer.industriverse.svc.cluster.local:8080'),
            'application_layer_url': os.environ.get('APPLICATION_LAYER_URL', 'http://application-layer.industriverse.svc.cluster.local:8080'),
            'protocol_layer_url': os.environ.get('PROTOCOL_LAYER_URL', 'http://protocol-layer.industriverse.svc.cluster.local:8080'),
            'workflow_layer_url': os.environ.get('WORKFLOW_LAYER_URL', 'http://workflow-layer.industriverse.svc.cluster.local:8080'),
            'security_layer_url': os.environ.get('SECURITY_LAYER_URL', 'http://security-layer.industriverse.svc.cluster.local:8080')
        })
    
    async def asyncSetUp(self):
        """Async set up for the test case."""
        # Connect to all layers
        await self.integration.connect_to_all_layers()
        
        # Start event listener
        await self.integration.start_event_listener()
    
    async def asyncTearDown(self):
        """Async tear down for the test case."""
        # Stop event listener
        await self.integration.stop_event_listener()
        
        # Disconnect from all layers
        await self.integration.disconnect_from_all_layers()
    
    async def test_connect_to_all_layers(self):
        """Test connecting to all layers."""
        # Check connection status for all layers
        for layer_type in LayerType:
            if layer_type != LayerType.UI_UX:  # Don't check ourselves
                status = self.integration.get_layer_status(layer_type)
                self.assertEqual(status, IntegrationStatus.CONNECTED, f"Failed to connect to {layer_type.value} layer")
    
    async def test_data_layer_integration(self):
        """Test integration with the Data Layer."""
        # Test connection
        connection_working = await self.integration.test_layer_connection(LayerType.DATA)
        self.assertTrue(connection_working, "Connection to Data Layer is not working")
        
        # Set up event handler
        data_received = asyncio.Event()
        received_data = {}
        
        async def data_handler(event_data):
            nonlocal received_data
            received_data = event_data
            data_received.set()
        
        # Register event handler
        self.integration.register_event_handler(LayerType.DATA, "data.response", data_handler)
        
        # Send data request event
        await self.integration.send_event_to_layer(LayerType.DATA, "data.request", {
            "query": "SELECT * FROM test_table LIMIT 1",
            "request_id": "test-request-1"
        })
        
        # Wait for response with timeout
        try:
            await asyncio.wait_for(data_received.wait(), timeout=5.0)
            self.assertIn("request_id", received_data, "Response does not contain request_id")
            self.assertEqual(received_data["request_id"], "test-request-1", "Response request_id does not match")
        except asyncio.TimeoutError:
            self.fail("Timeout waiting for response from Data Layer")
        finally:
            # Unregister event handler
            self.integration.unregister_event_handler(LayerType.DATA, "data.response", data_handler)
    
    async def test_core_ai_layer_integration(self):
        """Test integration with the Core AI Layer."""
        # Test connection
        connection_working = await self.integration.test_layer_connection(LayerType.CORE_AI)
        self.assertTrue(connection_working, "Connection to Core AI Layer is not working")
        
        # Set up event handler
        response_received = asyncio.Event()
        received_data = {}
        
        async def response_handler(event_data):
            nonlocal received_data
            received_data = event_data
            response_received.set()
        
        # Register event handler
        self.integration.register_event_handler(LayerType.CORE_AI, "core_ai.inference.response", response_handler)
        
        # Send inference request event
        await self.integration.send_event_to_layer(LayerType.CORE_AI, "core_ai.inference.request", {
            "model": "test-model",
            "input": "Hello, world!",
            "request_id": "test-request-2"
        })
        
        # Wait for response with timeout
        try:
            await asyncio.wait_for(response_received.wait(), timeout=5.0)
            self.assertIn("request_id", received_data, "Response does not contain request_id")
            self.assertEqual(received_data["request_id"], "test-request-2", "Response request_id does not match")
        except asyncio.TimeoutError:
            self.fail("Timeout waiting for response from Core AI Layer")
        finally:
            # Unregister event handler
            self.integration.unregister_event_handler(LayerType.CORE_AI, "core_ai.inference.response", response_handler)
    
    async def test_workflow_layer_integration(self):
        """Test integration with the Workflow Layer."""
        # Test connection
        connection_working = await self.integration.test_layer_connection(LayerType.WORKFLOW)
        self.assertTrue(connection_working, "Connection to Workflow Layer is not working")
        
        # Set up event handler
        response_received = asyncio.Event()
        received_data = {}
        
        async def response_handler(event_data):
            nonlocal received_data
            received_data = event_data
            response_received.set()
        
        # Register event handler
        self.integration.register_event_handler(LayerType.WORKFLOW, "workflow.capsule.response", response_handler)
        
        # Send capsule request event
        await self.integration.send_event_to_layer(LayerType.WORKFLOW, "workflow.capsule.request", {
            "capsule_id": "test-capsule",
            "action": "get",
            "request_id": "test-request-3"
        })
        
        # Wait for response with timeout
        try:
            await asyncio.wait_for(response_received.wait(), timeout=5.0)
            self.assertIn("request_id", received_data, "Response does not contain request_id")
            self.assertEqual(received_data["request_id"], "test-request-3", "Response request_id does not match")
        except asyncio.TimeoutError:
            self.fail("Timeout waiting for response from Workflow Layer")
        finally:
            # Unregister event handler
            self.integration.unregister_event_handler(LayerType.WORKFLOW, "workflow.capsule.response", response_handler)
    
    async def test_protocol_layer_integration(self):
        """Test integration with the Protocol Layer."""
        # Test connection
        connection_working = await self.integration.test_layer_connection(LayerType.PROTOCOL)
        self.assertTrue(connection_working, "Connection to Protocol Layer is not working")
        
        # Set up event handler
        response_received = asyncio.Event()
        received_data = {}
        
        async def response_handler(event_data):
            nonlocal received_data
            received_data = event_data
            response_received.set()
        
        # Register event handler
        self.integration.register_event_handler(LayerType.PROTOCOL, "protocol.mcp.response", response_handler)
        
        # Send MCP request event
        await self.integration.send_event_to_layer(LayerType.PROTOCOL, "protocol.mcp.request", {
            "action": "get_schema",
            "protocol": "mcp",
            "request_id": "test-request-4"
        })
        
        # Wait for response with timeout
        try:
            await asyncio.wait_for(response_received.wait(), timeout=5.0)
            self.assertIn("request_id", received_data, "Response does not contain request_id")
            self.assertEqual(received_data["request_id"], "test-request-4", "Response request_id does not match")
        except asyncio.TimeoutError:
            self.fail("Timeout waiting for response from Protocol Layer")
        finally:
            # Unregister event handler
            self.integration.unregister_event_handler(LayerType.PROTOCOL, "protocol.mcp.response", response_handler)
    
    async def test_all_layer_integration(self):
        """Test integration with all layers simultaneously."""
        # Set up event handlers and futures for all layers
        futures = {}
        handlers = {}
        
        for layer_type in LayerType:
            if layer_type != LayerType.UI_UX:  # Don't test ourselves
                futures[layer_type] = asyncio.Future()
                
                async def create_handler(lt):
                    async def handler(event_data):
                        if "request_id" in event_data and event_data["request_id"] == f"test-all-{lt.value}":
                            futures[lt].set_result(True)
                    return handler
                
                handlers[layer_type] = await create_handler(layer_type)
                
                # Register event handler
                response_type = {
                    LayerType.DATA: "data.response",
                    LayerType.CORE_AI: "core_ai.response",
                    LayerType.GENERATIVE: "generative.response",
                    LayerType.APPLICATION: "application.response",
                    LayerType.PROTOCOL: "protocol.response",
                    LayerType.WORKFLOW: "workflow.response",
                    LayerType.SECURITY: "security.response"
                }
                self.integration.register_event_handler(layer_type, response_type[layer_type], handlers[layer_type])
        
        # Send events to all layers
        for layer_type in LayerType:
            if layer_type != LayerType.UI_UX:  # Don't send to ourselves
                request_type = {
                    LayerType.DATA: "data.request",
                    LayerType.CORE_AI: "core_ai.request",
                    LayerType.GENERATIVE: "generative.request",
                    LayerType.APPLICATION: "application.request",
                    LayerType.PROTOCOL: "protocol.request",
                    LayerType.WORKFLOW: "workflow.request",
                    LayerType.SECURITY: "security.request"
                }
                await self.integration.send_event_to_layer(layer_type, request_type[layer_type], {
                    "action": "test",
                    "request_id": f"test-all-{layer_type.value}"
                })
        
        # Wait for all responses with timeout
        try:
            await asyncio.wait_for(asyncio.gather(*futures.values()), timeout=10.0)
            for layer_type, future in futures.items():
                self.assertTrue(future.result(), f"Failed to receive response from {layer_type.value} layer")
        except asyncio.TimeoutError:
            self.fail("Timeout waiting for responses from all layers")
        finally:
            # Unregister all event handlers
            for layer_type in LayerType:
                if layer_type != LayerType.UI_UX:  # Don't unregister from ourselves
                    response_type = {
                        LayerType.DATA: "data.response",
                        LayerType.CORE_AI: "core_ai.response",
                        LayerType.GENERATIVE: "generative.response",
                        LayerType.APPLICATION: "application.response",
                        LayerType.PROTOCOL: "protocol.response",
                        LayerType.WORKFLOW: "workflow.response",
                        LayerType.SECURITY: "security.response"
                    }
                    self.integration.unregister_event_handler(layer_type, response_type[layer_type], handlers[layer_type])

def run_tests():
    """Run the integration tests."""
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(CrossLayerIntegrationTest("test_connect_to_all_layers"))
    suite.addTest(CrossLayerIntegrationTest("test_data_layer_integration"))
    suite.addTest(CrossLayerIntegrationTest("test_core_ai_layer_integration"))
    suite.addTest(CrossLayerIntegrationTest("test_workflow_layer_integration"))
    suite.addTest(CrossLayerIntegrationTest("test_protocol_layer_integration"))
    suite.addTest(CrossLayerIntegrationTest("test_all_layer_integration"))
    
    # Run tests
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    # Run tests
    run_tests()
