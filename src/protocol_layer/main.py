"""
Main entry point for the Industriverse Protocol Layer.

This module initializes and starts all components of the Protocol Layer,
serving as the central coordination point for the entire system.
"""

import argparse
import logging
import os
import signal
import sys
import time
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import protocol layer components
from protocols.protocol_base import ProtocolRegistry
from protocols.discovery_service import DiscoveryService
from protocols.mcp.mcp_handler import MCPHandler
from protocols.a2a.a2a_handler import A2AHandler
from protocols.kernel.protocol_kernel_intelligence import ProtocolKernelIntelligence
from protocols.fabric.self_healing_fabric import SelfHealingFabric
from protocols.dtsl.dtsl_handler import DTSLHandler
from protocols.federation.cross_mesh_federation import CrossMeshFederation
from protocols.genetic.pk_alpha import PKAlpha
from protocols.genetic.alphaevolve_integration import AlphaEvolveIntegration
from protocols.contracts.reactive_protocol_contracts import ReactiveProtocolContracts
from protocols.bridge.protocol_native_bridge import ProtocolNativeBridge
from protocols.appstore.dynamic_protocol_appstore import DynamicProtocolAppStore
from protocols.security.trust_fabric_orchestration import TrustFabricOrchestration
from protocols.reflex.agent_reflex_timers import AgentReflexTimers

from industrial.adapters.opcua.opcua_adapter import OPCUAAdapter
from industrial.adapters.modbus.modbus_adapter import ModbusAdapter
from industrial.adapters.mqtt.mqtt_adapter import MQTTAdapter
from industrial.adapters.profinet.profinet_adapter import ProfinetAdapter
from industrial.adapters.dds.dds_adapter import DDSAdapter

from blockchain.connectors.blockchain_connector_base import BlockchainConnectorRegistry
from blockchain.connectors.ethereum_connector import EthereumConnector
from blockchain.connectors.hyperledger_fabric_connector import HyperledgerFabricConnector
from blockchain.connectors.corda_connector import CordaConnector
from blockchain.connectors.quorum_connector import QuorumConnector

from mobile.udep.enhanced_udep_handler import EnhancedUDEPHandler

from security.ekis.ekis_security import EKISSecurity

from simulation_lab.environment.simulation_environment import SimulationEnvironment
from simulation_lab.testing.protocol_testing import ProtocolTesting

from kernel.intent_aware_router import IntentAwareRouter
from kernel.semantic_compressor import SemanticCompressor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('protocol_layer.log')
    ]
)

logger = logging.getLogger(__name__)

class ProtocolLayerServer:
    """
    Main server class for the Industriverse Protocol Layer.
    
    This class initializes and manages all components of the Protocol Layer,
    providing a unified interface for the entire system.
    """
    
    def __init__(self, config_path, log_level='info', port=8080, metrics_port=9090, admin_port=8081, data_dir=None):
        """
        Initialize the Protocol Layer server.
        
        Args:
            config_path: Path to the configuration file
            log_level: Logging level
            port: Main API port
            metrics_port: Metrics port
            admin_port: Admin API port
            data_dir: Data directory
        """
        self.config_path = config_path
        self.log_level = log_level
        self.port = port
        self.metrics_port = metrics_port
        self.admin_port = admin_port
        self.data_dir = data_dir or os.environ.get('DATA_DIR', '/opt/industriverse/protocol/data')
        
        # Set up logging
        numeric_level = getattr(logging, log_level.upper(), None)
        if isinstance(numeric_level, int):
            logging.getLogger().setLevel(numeric_level)
        
        # Initialize component registries
        self.protocol_registry = ProtocolRegistry()
        self.blockchain_registry = BlockchainConnectorRegistry()
        
        # Initialize components
        self.components = {}
        self.running = False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
        logger.info(f"Initialized Protocol Layer server on port {port}")
    
    def initialize_components(self):
        """
        Initialize all Protocol Layer components.
        """
        logger.info("Initializing Protocol Layer components...")
        
        # Initialize security components first
        self.components['ekis_security'] = EKISSecurity()
        
        # Initialize core protocol components
        self.components['discovery_service'] = DiscoveryService()
        self.components['mcp_handler'] = MCPHandler()
        self.components['a2a_handler'] = A2AHandler()
        self.components['agent_reflex_timers'] = AgentReflexTimers()
        
        # Initialize Protocol Kernel Intelligence components
        self.components['intent_aware_router'] = IntentAwareRouter()
        self.components['semantic_compressor'] = SemanticCompressor()
        self.components['protocol_kernel_intelligence'] = ProtocolKernelIntelligence()
        
        # Initialize Self-Healing Fabric components
        self.components['self_healing_fabric'] = SelfHealingFabric()
        
        # Initialize Digital Twin Swarm Language components
        self.components['dtsl_handler'] = DTSLHandler()
        
        # Initialize Cross-Mesh Federation components
        self.components['cross_mesh_federation'] = CrossMeshFederation()
        self.components['trust_fabric_orchestration'] = TrustFabricOrchestration()
        
        # Initialize Protocol-Driven Genetic Algorithm components
        self.components['pk_alpha'] = PKAlpha()
        self.components['alphaevolve_integration'] = AlphaEvolveIntegration()
        
        # Initialize Protocol Extension components
        self.components['reactive_protocol_contracts'] = ReactiveProtocolContracts()
        self.components['protocol_native_bridge'] = ProtocolNativeBridge()
        self.components['dynamic_protocol_appstore'] = DynamicProtocolAppStore()
        
        # Initialize Industrial Protocol Adapters
        self.components['opcua_adapter'] = OPCUAAdapter()
        self.components['modbus_adapter'] = ModbusAdapter()
        self.components['mqtt_adapter'] = MQTTAdapter()
        self.components['profinet_adapter'] = ProfinetAdapter()
        self.components['dds_adapter'] = DDSAdapter()
        
        # Initialize Blockchain Connectors
        self.components['ethereum_connector'] = EthereumConnector()
        self.components['hyperledger_connector'] = HyperledgerFabricConnector()
        self.components['corda_connector'] = CordaConnector()
        self.components['quorum_connector'] = QuorumConnector()
        
        # Initialize Mobile/UDEP components
        self.components['enhanced_udep_handler'] = EnhancedUDEPHandler()
        
        # Initialize Simulation Lab components
        self.components['simulation_environment'] = SimulationEnvironment()
        self.components['protocol_testing'] = ProtocolTesting()
        
        # Register components with the protocol registry
        for name, component in self.components.items():
            self.protocol_registry.register_component(name, component)
            logger.info(f"Registered component: {name}")
        
        logger.info("All Protocol Layer components initialized")
    
    def start(self):
        """
        Start the Protocol Layer server and all its components.
        """
        logger.info("Starting Protocol Layer server...")
        
        # Initialize components if not already done
        if not self.components:
            self.initialize_components()
        
        # Start all components
        for name, component in self.components.items():
            logger.info(f"Starting component: {name}")
            if hasattr(component, 'start'):
                component.start()
        
        self.running = True
        logger.info(f"Protocol Layer server started on port {self.port}")
        
        # Main server loop
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
            self.stop()
    
    def stop(self):
        """
        Stop the Protocol Layer server and all its components.
        """
        logger.info("Stopping Protocol Layer server...")
        
        # Stop all components in reverse order
        for name, component in reversed(list(self.components.items())):
            logger.info(f"Stopping component: {name}")
            if hasattr(component, 'stop'):
                component.stop()
        
        self.running = False
        logger.info("Protocol Layer server stopped")
    
    def handle_signal(self, signum, frame):
        """
        Handle signals (SIGINT, SIGTERM).
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Industriverse Protocol Layer Server')
    parser.add_argument('--config', type=str, required=True, help='Path to configuration file')
    parser.add_argument('--log-level', type=str, default='info', choices=['debug', 'info', 'warning', 'error', 'critical'], help='Logging level')
    parser.add_argument('--port', type=int, default=8080, help='Main API port')
    parser.add_argument('--metrics-port', type=int, default=9090, help='Metrics port')
    parser.add_argument('--admin-port', type=int, default=8081, help='Admin API port')
    parser.add_argument('--data-dir', type=str, help='Data directory')
    return parser.parse_args()

def main():
    """
    Main entry point for the Protocol Layer server.
    """
    args = parse_args()
    
    # Create server instance
    server = ProtocolLayerServer(
        config_path=args.config,
        log_level=args.log_level,
        port=args.port,
        metrics_port=args.metrics_port,
        admin_port=args.admin_port,
        data_dir=args.data_dir
    )
    
    # Start server
    server.start()

if __name__ == '__main__':
    main()
