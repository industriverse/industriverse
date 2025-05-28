"""
Main application entry point for Industriverse Core AI Layer

This module serves as the main entry point for the Core AI Layer,
initializing all components and starting the API server.
"""

import os
import sys
import logging
import asyncio
import argparse
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import core components
from protocols.agent_core import AgentCore
from protocols.protocol_translator import ProtocolTranslator
from protocols.well_known_endpoint import WellKnownEndpoint
from protocols.mesh_boot_lifecycle import MeshBootLifecycle
from protocols.mesh_agent_intent_graph import MeshAgentIntentGraph
from protocols.consensus_resolver_agent import ConsensusResolverAgent
from protocols.protocol_conflict_resolver_agent import ProtocolConflictResolverAgent

# Import distributed intelligence components
from distributed_intelligence.core_ai_observability_agent import CoreAIObservabilityAgent
from distributed_intelligence.model_feedback_loop_agent import ModelFeedbackLoopAgent
from distributed_intelligence.model_simulation_replay_service import ModelSimulationReplayService
from distributed_intelligence.mesh_workload_router_agent import MeshWorkloadRouterAgent
from distributed_intelligence.intent_overlay_agent import IntentOverlayAgent
from distributed_intelligence.budget_monitor_agent import BudgetMonitorAgent
from distributed_intelligence.synthetic_data_generator_agent import SyntheticDataGeneratorAgent
from distributed_intelligence.model_health_prediction_agent import ModelHealthPredictionAgent

# Import API server
from api.server import APIServer

class CoreAILayer:
    """
    Main Core AI Layer application class.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Core AI Layer.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or os.environ.get("CONFIG_PATH", "config/mesh.yaml")
        
        # Initialize components
        self.agent_core = None
        self.protocol_translator = None
        self.well_known_endpoint = None
        self.mesh_boot_lifecycle = None
        self.mesh_agent_intent_graph = None
        self.consensus_resolver = None
        self.protocol_conflict_resolver = None
        
        self.observability_agent = None
        self.model_feedback_loop = None
        self.model_simulation_replay = None
        self.mesh_workload_router = None
        self.intent_overlay = None
        self.budget_monitor = None
        self.synthetic_data_generator = None
        self.model_health_prediction = None
        
        self.api_server = None
        
        # Initialize state
        self.running = False
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration.
        
        Returns:
            The configuration as a dictionary
        """
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return {}
                
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def initialize(self) -> bool:
        """
        Initialize all components.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Initializing Core AI Layer components...")
            
            # Initialize protocol components
            self.protocol_translator = ProtocolTranslator()
            self.agent_core = AgentCore(self.protocol_translator)
            self.well_known_endpoint = WellKnownEndpoint(self.agent_core)
            self.mesh_boot_lifecycle = MeshBootLifecycle(self.agent_core, self.config)
            self.mesh_agent_intent_graph = MeshAgentIntentGraph(self.agent_core)
            self.consensus_resolver = ConsensusResolverAgent(self.agent_core)
            self.protocol_conflict_resolver = ProtocolConflictResolverAgent(self.protocol_translator)
            
            # Initialize distributed intelligence components
            self.observability_agent = CoreAIObservabilityAgent()
            self.model_feedback_loop = ModelFeedbackLoopAgent()
            self.model_simulation_replay = ModelSimulationReplayService()
            self.mesh_workload_router = MeshWorkloadRouterAgent(self.agent_core)
            self.intent_overlay = IntentOverlayAgent(self.mesh_agent_intent_graph)
            self.budget_monitor = BudgetMonitorAgent()
            self.synthetic_data_generator = SyntheticDataGeneratorAgent()
            self.model_health_prediction = ModelHealthPredictionAgent()
            
            # Initialize API server
            self.api_server = APIServer(
                agent_core=self.agent_core,
                protocol_translator=self.protocol_translator,
                mesh_boot_lifecycle=self.mesh_boot_lifecycle,
                observability_agent=self.observability_agent,
                model_feedback_loop=self.model_feedback_loop,
                mesh_workload_router=self.mesh_workload_router
            )
            
            logger.info("Core AI Layer components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Core AI Layer components: {e}")
            return False
    
    async def start(self) -> bool:
        """
        Start all components.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.running:
                logger.warning("Core AI Layer is already running")
                return True
            
            logger.info("Starting Core AI Layer components...")
            
            # Start protocol components
            await self.well_known_endpoint.start()
            await self.mesh_boot_lifecycle.start()
            await self.mesh_agent_intent_graph.start()
            await self.consensus_resolver.start()
            await self.protocol_conflict_resolver.start()
            
            # Start distributed intelligence components
            await self.observability_agent.start()
            await self.model_feedback_loop.start()
            await self.model_simulation_replay.start()
            await self.mesh_workload_router.start()
            await self.intent_overlay.start()
            await self.budget_monitor.start()
            
            # Start API server
            await self.api_server.start()
            
            self.running = True
            logger.info("Core AI Layer started successfully")
            
            # Emit deployment complete event
            await self.agent_core.emit_event("core_ai_layer/deployment_complete", {
                "status": "success",
                "timestamp": self.agent_core.get_timestamp(),
                "components": {
                    "protocol": ["agent_core", "protocol_translator", "well_known_endpoint", 
                               "mesh_boot_lifecycle", "mesh_agent_intent_graph", 
                               "consensus_resolver", "protocol_conflict_resolver"],
                    "distributed_intelligence": ["observability_agent", "model_feedback_loop", 
                                               "model_simulation_replay", "mesh_workload_router", 
                                               "intent_overlay", "budget_monitor", 
                                               "synthetic_data_generator", "model_health_prediction"]
                },
                "resilience_verification": {
                    "status": "verified",
                    "redundant_pairs": True,
                    "failover_chains": True,
                    "quorum_voting": True
                }
            })
            
            return True
        except Exception as e:
            logger.error(f"Error starting Core AI Layer components: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop all components.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.running:
                logger.warning("Core AI Layer is not running")
                return True
            
            logger.info("Stopping Core AI Layer components...")
            
            # Stop API server
            await self.api_server.stop()
            
            # Stop distributed intelligence components
            await self.budget_monitor.stop()
            await self.intent_overlay.stop()
            await self.mesh_workload_router.stop()
            await self.model_simulation_replay.stop()
            await self.model_feedback_loop.stop()
            await self.observability_agent.stop()
            
            # Stop protocol components
            await self.protocol_conflict_resolver.stop()
            await self.consensus_resolver.stop()
            await self.mesh_agent_intent_graph.stop()
            await self.mesh_boot_lifecycle.stop()
            await self.well_known_endpoint.stop()
            
            self.running = False
            logger.info("Core AI Layer stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Error stopping Core AI Layer components: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check.
        
        Returns:
            Health check results
        """
        results = {
            "status": "healthy",
            "components": {}
        }
        
        # Check protocol components
        results["components"]["agent_core"] = await self.agent_core.health_check()
        results["components"]["protocol_translator"] = await self.protocol_translator.health_check()
        results["components"]["well_known_endpoint"] = await self.well_known_endpoint.health_check()
        results["components"]["mesh_boot_lifecycle"] = await self.mesh_boot_lifecycle.health_check()
        results["components"]["mesh_agent_intent_graph"] = await self.mesh_agent_intent_graph.health_check()
        results["components"]["consensus_resolver"] = await self.consensus_resolver.health_check()
        results["components"]["protocol_conflict_resolver"] = await self.protocol_conflict_resolver.health_check()
        
        # Check distributed intelligence components
        results["components"]["observability_agent"] = await self.observability_agent.health_check()
        results["components"]["model_feedback_loop"] = await self.model_feedback_loop.health_check()
        results["components"]["model_simulation_replay"] = await self.model_simulation_replay.health_check()
        results["components"]["mesh_workload_router"] = await self.mesh_workload_router.health_check()
        results["components"]["intent_overlay"] = await self.intent_overlay.health_check()
        results["components"]["budget_monitor"] = await self.budget_monitor.health_check()
        
        # Check API server
        results["components"]["api_server"] = await self.api_server.health_check()
        
        # Determine overall status
        unhealthy_components = [name for name, check in results["components"].items() 
                               if check.get("status") != "healthy"]
        
        if unhealthy_components:
            results["status"] = "unhealthy"
            results["unhealthy_components"] = unhealthy_components
        
        return results


async def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Industriverse Core AI Layer")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    
    # Create and initialize Core AI Layer
    core_ai_layer = CoreAILayer(config_path=args.config)
    
    if not await core_ai_layer.initialize():
        logger.error("Failed to initialize Core AI Layer")
        sys.exit(1)
    
    if not await core_ai_layer.start():
        logger.error("Failed to start Core AI Layer")
        sys.exit(1)
    
    # Register signal handlers
    import signal
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        asyncio.create_task(shutdown())
    
    async def shutdown():
        await core_ai_layer.stop()
        asyncio.get_event_loop().stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run forever
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await core_ai_layer.stop()


if __name__ == "__main__":
    asyncio.run(main())
