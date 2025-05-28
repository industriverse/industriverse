"""
Main entry point for the Workflow Automation Layer.

This module initializes and starts all components of the Workflow Automation Layer,
including the workflow engine, agents, n8n integration, and cross-layer integration.
"""

import asyncio
import logging
import os
import sys
import argparse
import json
import yaml
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core components
from workflow_engine.workflow_runtime import WorkflowRuntime
from workflow_engine.workflow_registry import WorkflowRegistry
from workflow_engine.workflow_telemetry import WorkflowTelemetry
from workflow_engine.task_contract_manager import TaskContractManager
from workflow_engine.workflow_manifest_parser import WorkflowManifestParser
from workflow_engine.execution_mode_manager import ExecutionModeManager
from workflow_engine.mesh_topology_manager import MeshTopologyManager
from workflow_engine.capsule_debug_trace_manager import CapsuleDebugTraceManager

# Import agent components
from agents.base_agent import BaseAgent
from agents.workflow_trigger_agent import WorkflowTriggerAgent
from agents.workflow_contract_parser import WorkflowContractParser
from agents.human_intervention_agent import HumanInterventionAgent
from agents.capsule_workflow_controller import CapsuleWorkflowController
from agents.n8n_sync_bridge import N8nSyncBridge
from agents.workflow_optimizer import WorkflowOptimizer

# Import n8n integration
from n8n_integration.n8n_connector import N8nConnector
from n8n_integration.n8n_bridge_service import N8nBridgeService
from n8n_integration.n8n_workflow_templates import N8nWorkflowTemplates

# Import UI components
from ui.dynamic_agent_capsule import DynamicAgentCapsule
from ui.workflow_visualization import WorkflowVisualization

# Import security components
from security.security_compliance_observability import SecurityComplianceManager

# Import cross-layer integration
from cross_layer_integration import CrossLayerIntegrationManager


class WorkflowAutomationLayer:
    """Main class for the Workflow Automation Layer."""

    def __init__(self, config_path: str = None):
        """Initialize the Workflow Automation Layer.

        Args:
            config_path: Path to the configuration file.
        """
        self.config = self._load_config(config_path)
        self.components = {}
        self.initialized = False
        self.api_server = None

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file or environment variables.

        Args:
            config_path: Path to the configuration file.

        Returns:
            Dict containing configuration settings.
        """
        config = {
            "log_level": os.environ.get("LOG_LEVEL", "INFO"),
            "api_host": os.environ.get("API_HOST", "0.0.0.0"),
            "api_port": int(os.environ.get("API_PORT", "8080")),
            "protocol_layer_url": os.environ.get("PROTOCOL_LAYER_URL", "http://protocol-layer-service:8080"),
            "core_ai_layer_url": os.environ.get("CORE_AI_LAYER_URL", "http://core-ai-layer-service:8080"),
            "application_layer_url": os.environ.get("APPLICATION_LAYER_URL", "http://application-layer-service:8080"),
            "n8n_api_url": os.environ.get("N8N_API_URL", "http://n8n-service:5678/api"),
            "n8n_api_key": os.environ.get("N8N_API_KEY", ""),
            "ekis_security_enabled": os.environ.get("EKIS_SECURITY_ENABLED", "true").lower() == "true",
            "ekis_api_url": os.environ.get("EKIS_API_URL", "http://ekis-service:8080/api"),
            "ekis_api_key": os.environ.get("EKIS_API_KEY", ""),
            "trust_threshold": float(os.environ.get("TRUST_THRESHOLD", "0.7")),
            "confidence_threshold": float(os.environ.get("CONFIDENCE_THRESHOLD", "0.8")),
            "template_dir": os.environ.get("TEMPLATE_DIR", "/templates"),
            "data_dir": os.environ.get("DATA_DIR", "/data"),
            "debug_mode": os.environ.get("DEBUG_MODE", "false").lower() == "true"
        }
        
        # Override with config file if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        config.update(file_config)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration from {config_path}: {str(e)}")
        
        return config

    async def initialize(self) -> bool:
        """Initialize all components of the Workflow Automation Layer.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            logger.info("Initializing Workflow Automation Layer")
            
            # Set log level
            logging.getLogger().setLevel(getattr(logging, self.config["log_level"]))
            
            # Initialize core components
            logger.info("Initializing core components")
            workflow_registry = WorkflowRegistry(self.config)
            workflow_telemetry = WorkflowTelemetry(self.config)
            task_contract_manager = TaskContractManager(self.config)
            workflow_manifest_parser = WorkflowManifestParser(self.config)
            execution_mode_manager = ExecutionModeManager(self.config)
            mesh_topology_manager = MeshTopologyManager(self.config)
            capsule_debug_trace_manager = CapsuleDebugTraceManager(self.config)
            
            # Initialize workflow runtime
            workflow_runtime = WorkflowRuntime(
                workflow_registry=workflow_registry,
                workflow_telemetry=workflow_telemetry,
                task_contract_manager=task_contract_manager,
                execution_mode_manager=execution_mode_manager,
                mesh_topology_manager=mesh_topology_manager,
                capsule_debug_trace_manager=capsule_debug_trace_manager,
                config=self.config
            )
            
            # Initialize agents
            logger.info("Initializing agents")
            trigger_agent = WorkflowTriggerAgent(workflow_runtime)
            contract_parser = WorkflowContractParser(workflow_runtime)
            human_agent = HumanInterventionAgent(workflow_runtime)
            capsule_controller = CapsuleWorkflowController(workflow_runtime)
            workflow_optimizer = WorkflowOptimizer(workflow_runtime)
            
            # Register agents with workflow runtime
            workflow_runtime.register_agent("trigger", trigger_agent)
            workflow_runtime.register_agent("contract_parser", contract_parser)
            workflow_runtime.register_agent("human_intervention", human_agent)
            workflow_runtime.register_agent("capsule_controller", capsule_controller)
            workflow_runtime.register_agent("optimizer", workflow_optimizer)
            
            # Initialize n8n integration
            logger.info("Initializing n8n integration")
            n8n_config = {
                "api_url": self.config["n8n_api_url"],
                "api_key": self.config["n8n_api_key"],
                "webhook_base_url": f"http://{self.config['api_host']}:{self.config['api_port']}/api/n8n/webhook"
            }
            n8n_connector = N8nConnector(n8n_config)
            n8n_templates = N8nWorkflowTemplates()
            n8n_bridge_service = N8nBridgeService(n8n_connector, workflow_registry, workflow_runtime)
            n8n_sync_agent = N8nSyncBridge(workflow_runtime, n8n_bridge_service)
            
            # Register n8n sync agent with workflow runtime
            workflow_runtime.register_agent("n8n_sync", n8n_sync_agent)
            
            # Initialize UI components
            logger.info("Initializing UI components")
            workflow_visualization = WorkflowVisualization(workflow_registry, workflow_telemetry)
            
            # Initialize security components
            logger.info("Initializing security components")
            security_config = {
                "ekis_security_enabled": self.config["ekis_security_enabled"],
                "ekis_api_url": self.config["ekis_api_url"],
                "ekis_api_key": self.config["ekis_api_key"],
                "trust_threshold": self.config["trust_threshold"],
                "confidence_threshold": self.config["confidence_threshold"],
                "compliance_frameworks": ["GDPR", "ISO27001"],
                "audit_log_retention_days": 90
            }
            security_manager = SecurityComplianceManager(security_config)
            
            # Initialize cross-layer integration
            logger.info("Initializing cross-layer integration")
            integration_config = {
                "protocol_layer": {
                    "protocol_layer_url": self.config["protocol_layer_url"],
                    "api_key": os.environ.get("PROTOCOL_LAYER_API_KEY", "")
                },
                "core_ai_layer": {
                    "core_ai_url": self.config["core_ai_layer_url"],
                    "api_key": os.environ.get("CORE_AI_LAYER_API_KEY", "")
                },
                "application_layer": {
                    "application_url": self.config["application_layer_url"],
                    "api_key": os.environ.get("APPLICATION_LAYER_API_KEY", "")
                }
            }
            integration_manager = CrossLayerIntegrationManager(integration_config)
            integration_manager.register_workflow_runtime(workflow_runtime)
            
            # Store components for later use
            self.components = {
                "workflow_registry": workflow_registry,
                "workflow_telemetry": workflow_telemetry,
                "task_contract_manager": task_contract_manager,
                "workflow_manifest_parser": workflow_manifest_parser,
                "execution_mode_manager": execution_mode_manager,
                "mesh_topology_manager": mesh_topology_manager,
                "capsule_debug_trace_manager": capsule_debug_trace_manager,
                "workflow_runtime": workflow_runtime,
                "trigger_agent": trigger_agent,
                "contract_parser": contract_parser,
                "human_agent": human_agent,
                "capsule_controller": capsule_controller,
                "workflow_optimizer": workflow_optimizer,
                "n8n_connector": n8n_connector,
                "n8n_templates": n8n_templates,
                "n8n_bridge_service": n8n_bridge_service,
                "n8n_sync_agent": n8n_sync_agent,
                "workflow_visualization": workflow_visualization,
                "security_manager": security_manager,
                "integration_manager": integration_manager
            }
            
            # Initialize API server
            logger.info("Initializing API server")
            from api.api_server import create_api_server
            self.api_server = await create_api_server(self.components, self.config)
            
            # Initialize cross-layer integration
            logger.info("Connecting to other layers")
            integration_result = await integration_manager.initialize()
            if not integration_result["success"]:
                logger.warning(f"Cross-layer integration initialization warning: {integration_result}")
            
            self.initialized = True
            logger.info("Workflow Automation Layer initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Workflow Automation Layer: {str(e)}", exc_info=True)
            return False

    async def start(self) -> bool:
        """Start the Workflow Automation Layer.

        Returns:
            bool: True if startup was successful, False otherwise.
        """
        if not self.initialized:
            success = await self.initialize()
            if not success:
                return False
        
        try:
            logger.info("Starting Workflow Automation Layer")
            
            # Start API server
            host = self.config["api_host"]
            port = self.config["api_port"]
            logger.info(f"Starting API server on {host}:{port}")
            await self.api_server.start(host, port)
            
            # Load templates
            logger.info("Loading workflow templates")
            workflow_registry = self.components["workflow_registry"]
            workflow_manifest_parser = self.components["workflow_manifest_parser"]
            template_dir = self.config["template_dir"]
            
            # Load industry-specific templates
            industries = ["manufacturing", "logistics", "energy", "retail"]
            for industry in industries:
                industry_dir = os.path.join(template_dir, industry)
                if os.path.exists(industry_dir):
                    template_file = os.path.join(industry_dir, "workflow_manifest_templates.yaml")
                    if os.path.exists(template_file):
                        try:
                            with open(template_file, 'r') as f:
                                templates = yaml.safe_load(f)
                                if templates and "templates" in templates:
                                    for template in templates["templates"]:
                                        workflow_registry.register_template(template)
                                        logger.info(f"Registered template: {template['name']} for industry: {industry}")
                        except Exception as e:
                            logger.error(f"Error loading templates from {template_file}: {str(e)}")
            
            # Setup n8n webhooks
            logger.info("Setting up n8n webhooks")
            n8n_bridge_service = self.components["n8n_bridge_service"]
            await n8n_bridge_service.setup_webhooks()
            
            logger.info("Workflow Automation Layer started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Workflow Automation Layer: {str(e)}", exc_info=True)
            return False

    async def stop(self) -> bool:
        """Stop the Workflow Automation Layer.

        Returns:
            bool: True if shutdown was successful, False otherwise.
        """
        try:
            logger.info("Stopping Workflow Automation Layer")
            
            # Stop API server
            if self.api_server:
                await self.api_server.stop()
            
            # Perform cleanup
            workflow_runtime = self.components.get("workflow_runtime")
            if workflow_runtime:
                await workflow_runtime.shutdown()
            
            logger.info("Workflow Automation Layer stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Workflow Automation Layer: {str(e)}", exc_info=True)
            return False


async def main():
    """Main entry point for the Workflow Automation Layer."""
    parser = argparse.ArgumentParser(description="Workflow Automation Layer")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    
    workflow_automation = WorkflowAutomationLayer(args.config)
    
    try:
        success = await workflow_automation.start()
        if not success:
            logger.error("Failed to start Workflow Automation Layer")
            sys.exit(1)
        
        # Keep the application running
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await workflow_automation.stop()


if __name__ == "__main__":
    asyncio.run(main())
