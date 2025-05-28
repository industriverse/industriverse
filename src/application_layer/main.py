"""
Main entry point for the Industriverse Application Layer.

This module initializes and starts the Application Layer with all components
and protocol-native interfaces.
"""

import logging
import os
import sys
import time
import json
import argparse
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import protocol components
from protocols.agent_core import AgentCore
from protocols.mcp_handler import MCPHandler
from protocols.a2a_handler import A2AHandler
from protocols.well_known_endpoint import WellKnownEndpoint
from protocols.protocol_translator import ProtocolTranslator
from protocols.mesh_boot_lifecycle import MeshBootLifecycle

# Import application components
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

# Import API server
from api.server import APIServer

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration data
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {e}")
        return {}

def initialize_components(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize all components.
    
    Args:
        config: Configuration data
        
    Returns:
        Dictionary of initialized components
    """
    logger.info("Initializing components...")
    
    # Initialize agent core
    agent_core = AgentCore(config.get("agent_core", {}))
    
    # Initialize protocol components
    mcp_handler = MCPHandler(agent_core)
    a2a_handler = A2AHandler(agent_core)
    well_known_endpoint = WellKnownEndpoint(agent_core)
    protocol_translator = ProtocolTranslator(agent_core)
    mesh_boot_lifecycle = MeshBootLifecycle(agent_core)
    
    # Initialize application components
    application_avatar_interface = ApplicationAvatarInterface(agent_core)
    universal_skin_manager = UniversalSkinManager(agent_core)
    agent_capsule_factory = AgentCapsuleFactory(agent_core)
    capsule_view_models = CapsuleViewModels(agent_core)
    capsule_interaction_handler = CapsuleInteractionHandler(agent_core)
    main_app_coordinator = MainAppCoordinator(agent_core)
    application_ui_component_system = ApplicationUIComponentSystem(agent_core)
    digital_twin_components = DigitalTwinComponents(agent_core)
    industry_specific_modules = IndustrySpecificModules(agent_core)
    workflow_orchestration = WorkflowOrchestration(agent_core)
    omniverse_integration_services = OmniverseIntegrationServices(agent_core)
    
    # Initialize API server
    api_server = APIServer(agent_core, config.get("api_server", {}))
    
    # Register all components with agent core
    components = {
        "agent_core": agent_core,
        "mcp_handler": mcp_handler,
        "a2a_handler": a2a_handler,
        "well_known_endpoint": well_known_endpoint,
        "protocol_translator": protocol_translator,
        "mesh_boot_lifecycle": mesh_boot_lifecycle,
        "application_avatar_interface": application_avatar_interface,
        "universal_skin_manager": universal_skin_manager,
        "agent_capsule_factory": agent_capsule_factory,
        "capsule_view_models": capsule_view_models,
        "capsule_interaction_handler": capsule_interaction_handler,
        "main_app_coordinator": main_app_coordinator,
        "application_ui_component_system": application_ui_component_system,
        "digital_twin_components": digital_twin_components,
        "industry_specific_modules": industry_specific_modules,
        "workflow_orchestration": workflow_orchestration,
        "omniverse_integration_services": omniverse_integration_services,
        "api_server": api_server
    }
    
    logger.info("All components initialized")
    
    return components

def start_components(components: Dict[str, Any]) -> None:
    """
    Start all components.
    
    Args:
        components: Dictionary of initialized components
    """
    logger.info("Starting components...")
    
    # Start agent core
    components["agent_core"].start()
    
    # Start protocol components
    components["mcp_handler"].start()
    components["a2a_handler"].start()
    components["well_known_endpoint"].start()
    components["protocol_translator"].start()
    components["mesh_boot_lifecycle"].start()
    
    # Start application components
    components["application_avatar_interface"].start()
    components["universal_skin_manager"].start()
    components["agent_capsule_factory"].start()
    components["capsule_view_models"].start()
    components["capsule_interaction_handler"].start()
    components["main_app_coordinator"].start()
    components["application_ui_component_system"].start()
    components["digital_twin_components"].start()
    components["industry_specific_modules"].start()
    components["workflow_orchestration"].start()
    components["omniverse_integration_services"].start()
    
    # Start API server
    components["api_server"].start()
    
    logger.info("All components started")

def initialize_default_data(components: Dict[str, Any]) -> None:
    """
    Initialize default data for components.
    
    Args:
        components: Dictionary of initialized components
    """
    logger.info("Initializing default data...")
    
    # Initialize default UI components
    components["application_ui_component_system"].initialize_default_components()
    
    # Initialize default workflow templates
    components["workflow_orchestration"].initialize_default_templates()
    
    # Initialize default industry modules
    components["industry_specific_modules"].initialize_default_modules()
    
    logger.info("Default data initialized")

def main():
    """
    Main entry point.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Industriverse Application Layer")
    parser.add_argument("--config", type=str, default="/etc/industriverse/application_layer/config.json",
                        help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting Industriverse Application Layer...")
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize components
    components = initialize_components(config)
    
    # Start components
    start_components(components)
    
    # Initialize default data
    initialize_default_data(components)
    
    logger.info("Industriverse Application Layer started")
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down Industriverse Application Layer...")
        
        # Stop components in reverse order
        components["api_server"].stop()
        components["omniverse_integration_services"].stop()
        components["workflow_orchestration"].stop()
        components["industry_specific_modules"].stop()
        components["digital_twin_components"].stop()
        components["application_ui_component_system"].stop()
        components["main_app_coordinator"].stop()
        components["capsule_interaction_handler"].stop()
        components["capsule_view_models"].stop()
        components["agent_capsule_factory"].stop()
        components["universal_skin_manager"].stop()
        components["application_avatar_interface"].stop()
        components["mesh_boot_lifecycle"].stop()
        components["protocol_translator"].stop()
        components["well_known_endpoint"].stop()
        components["a2a_handler"].stop()
        components["mcp_handler"].stop()
        components["agent_core"].stop()
        
        logger.info("Industriverse Application Layer stopped")

if __name__ == "__main__":
    main()
