"""
Layer Deployment Orchestrator for the Deployment Operations Layer

This module provides comprehensive orchestration capabilities for deploying
across all Industriverse layers, ensuring coordinated, reliable deployments
with proper sequencing, dependency management, and rollback capabilities.

The orchestrator serves as the central coordination point for executing
deployment missions across the entire Industriverse ecosystem.
"""

import os
import json
import logging
import threading
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

from ..agent.mission_planner import MissionPlanner
from ..agent.mission_executor import MissionExecutor
from ..agent.error_handler import ErrorHandler
from ..agent.recovery_manager import RecoveryManager
from ..integration.layer_integration_manager import LayerIntegrationManager
from ..integration.cross_layer_integration_manager import CrossLayerIntegrationManager
from ..simulation.simulation_engine import SimulationEngine
from ..analytics.analytics_manager import AnalyticsManager
from ..journal.deployment_journal import DeploymentJournal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    """Enum representing the status of a deployment."""
    PENDING = "pending"
    SIMULATING = "simulating"
    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"

class LayerDeploymentOrchestrator:
    """
    Orchestrates deployments across all Industriverse layers.
    
    This class provides comprehensive orchestration capabilities for deploying
    across all Industriverse layers, ensuring coordinated, reliable deployments
    with proper sequencing, dependency management, and rollback capabilities.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Layer Deployment Orchestrator.
        
        Args:
            config_path: Path to the configuration file for the orchestrator.
        """
        self.config = self._load_config(config_path)
        self.mission_planner = MissionPlanner()
        self.mission_executor = MissionExecutor()
        self.error_handler = ErrorHandler()
        self.recovery_manager = RecoveryManager()
        self.layer_integration_manager = LayerIntegrationManager()
        self.cross_layer_integration_manager = CrossLayerIntegrationManager()
        self.simulation_engine = SimulationEngine()
        self.analytics_manager = AnalyticsManager()
        self.deployment_journal = DeploymentJournal()
        
        # Initialize deployment tracking
        self.active_deployments = {}
        self.deployment_history = []
        
        # Initialize locks for thread safety
        self.deployment_lock = threading.Lock()
        
        logger.info("Layer Deployment Orchestrator initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration for the orchestrator.
        
        Args:
            config_path: Path to the configuration file.
            
        Returns:
            Dict containing the configuration.
        """
        default_config = {
            "simulation": {
                "enabled": True,
                "timeout_seconds": 300,
                "success_threshold": 0.95
            },
            "deployment": {
                "max_concurrent": 5,
                "timeout_seconds": 1800,
                "retry_attempts": 3,
                "retry_delay_seconds": 30
            },
            "rollback": {
                "automatic": True,
                "timeout_seconds": 600
            },
            "layer_sequence": {
                "default": [
                    "data",
                    "core_ai",
                    "generative",
                    "application",
                    "protocol",
                    "workflow",
                    "ui_ux",
                    "security",
                    "native_app"
                ]
            },
            "monitoring": {
                "health_check_interval_seconds": 30,
                "metrics_collection_interval_seconds": 60
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with default config
                    for key, value in user_config.items():
                        if key in default_config and isinstance(default_config[key], dict) and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                logger.error(f"Error loading orchestrator config: {str(e)}")
        
        return default_config
    
    def create_deployment_mission(self, mission_spec: Dict[str, Any]) -> str:
        """
        Create a new deployment mission.
        
        Args:
            mission_spec: Specification for the deployment mission.
            
        Returns:
            String containing the mission ID.
        """
        logger.info(f"Creating deployment mission with spec: {mission_spec}")
        
        # Validate mission spec
        self._validate_mission_spec(mission_spec)
        
        # Generate mission ID
        mission_id = f"mission-{int(time.time())}-{os.urandom(4).hex()}"
        
        # Create mission plan
        mission_plan = self.mission_planner.create_mission_plan(mission_spec)
        
        # Initialize deployment tracking
        with self.deployment_lock:
            self.active_deployments[mission_id] = {
                "mission_id": mission_id,
                "mission_spec": mission_spec,
                "mission_plan": mission_plan,
                "status": DeploymentStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "layers": mission_spec.get("layers", []),
                "environment": mission_spec.get("environment", "production"),
                "region": mission_spec.get("region", "global"),
                "progress": 0,
                "logs": [],
                "metrics": {},
                "simulation_results": None,
                "execution_results": None,
                "error": None
            }
        
        # Log mission creation
        self.deployment_journal.log_event(
            mission_id=mission_id,
            event_type="mission_created",
            details={
                "mission_spec": mission_spec,
                "mission_plan": mission_plan
            }
        )
        
        logger.info(f"Created deployment mission with ID: {mission_id}")
        return mission_id
    
    def _validate_mission_spec(self, mission_spec: Dict[str, Any]):
        """
        Validate a mission specification.
        
        Args:
            mission_spec: Specification for the deployment mission.
            
        Raises:
            ValueError: If the mission spec is invalid.
        """
        # Check required fields
        required_fields = ["layers", "environment"]
        for field in required_fields:
            if field not in mission_spec:
                raise ValueError(f"Missing required field in mission spec: {field}")
        
        # Validate layers
        valid_layers = [
            "data",
            "core_ai",
            "generative",
            "application",
            "protocol",
            "workflow",
            "ui_ux",
            "security",
            "native_app"
        ]
        
        if isinstance(mission_spec["layers"], list):
            for layer in mission_spec["layers"]:
                if layer not in valid_layers:
                    raise ValueError(f"Invalid layer in mission spec: {layer}")
        elif mission_spec["layers"] == "all":
            # "all" is a valid value for layers
            pass
        else:
            raise ValueError(f"Invalid value for layers in mission spec: {mission_spec['layers']}")
        
        # Validate environment
        valid_environments = ["production", "staging", "development", "testing"]
        if mission_spec["environment"] not in valid_environments:
            raise ValueError(f"Invalid environment in mission spec: {mission_spec['environment']}")
    
    def simulate_deployment(self, mission_id: str) -> Dict[str, Any]:
        """
        Simulate a deployment mission.
        
        Args:
            mission_id: ID of the mission to simulate.
            
        Returns:
            Dict containing the simulation results.
        """
        logger.info(f"Simulating deployment mission: {mission_id}")
        
        # Get mission details
        with self.deployment_lock:
            if mission_id not in self.active_deployments:
                raise ValueError(f"Mission not found: {mission_id}")
            
            mission = self.active_deployments[mission_id]
            
            # Update mission status
            mission["status"] = DeploymentStatus.SIMULATING.value
            mission["updated_at"] = datetime.now().isoformat()
        
        # Log simulation start
        self.deployment_journal.log_event(
            mission_id=mission_id,
            event_type="simulation_started",
            details={}
        )
        
        try:
            # Run simulation
            simulation_results = self.simulation_engine.run_simulation(
                mission["mission_plan"],
                timeout=self.config["simulation"]["timeout_seconds"]
            )
            
            # Update mission with simulation results
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["simulation_results"] = simulation_results
                mission["updated_at"] = datetime.now().isoformat()
                
                # Update mission status based on simulation results
                if simulation_results["success_rate"] >= self.config["simulation"]["success_threshold"]:
                    mission["status"] = DeploymentStatus.PENDING.value
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": f"Simulation successful with success rate: {simulation_results['success_rate']}"
                    })
                else:
                    mission["status"] = DeploymentStatus.FAILED.value
                    mission["error"] = {
                        "code": "SIMULATION_FAILED",
                        "message": f"Simulation failed with success rate: {simulation_results['success_rate']}",
                        "details": simulation_results["failures"]
                    }
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Simulation failed with success rate: {simulation_results['success_rate']}"
                    })
            
            # Log simulation completion
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="simulation_completed",
                details={
                    "success_rate": simulation_results["success_rate"],
                    "failures": simulation_results["failures"]
                }
            )
            
            logger.info(f"Simulation completed for mission {mission_id} with success rate: {simulation_results['success_rate']}")
            return simulation_results
            
        except Exception as e:
            logger.error(f"Error simulating deployment mission {mission_id}: {str(e)}")
            
            # Update mission with error
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["status"] = DeploymentStatus.FAILED.value
                mission["error"] = {
                    "code": "SIMULATION_ERROR",
                    "message": f"Error simulating deployment: {str(e)}",
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                }
                mission["updated_at"] = datetime.now().isoformat()
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"Error simulating deployment: {str(e)}"
                })
            
            # Log simulation error
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="simulation_error",
                details={
                    "error": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            )
            
            raise
    
    def execute_deployment(self, mission_id: str) -> Dict[str, Any]:
        """
        Execute a deployment mission.
        
        Args:
            mission_id: ID of the mission to execute.
            
        Returns:
            Dict containing the execution results.
        """
        logger.info(f"Executing deployment mission: {mission_id}")
        
        # Get mission details
        with self.deployment_lock:
            if mission_id not in self.active_deployments:
                raise ValueError(f"Mission not found: {mission_id}")
            
            mission = self.active_deployments[mission_id]
            
            # Check if simulation is required but not completed
            if (self.config["simulation"]["enabled"] and 
                mission["simulation_results"] is None and
                mission["status"] != DeploymentStatus.FAILED.value):
                raise ValueError(f"Simulation required but not completed for mission: {mission_id}")
            
            # Check if mission failed simulation
            if mission["status"] == DeploymentStatus.FAILED.value:
                raise ValueError(f"Cannot execute failed mission: {mission_id}")
            
            # Update mission status
            mission["status"] = DeploymentStatus.PREPARING.value
            mission["updated_at"] = datetime.now().isoformat()
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Preparing for deployment execution"
            })
        
        # Log execution start
        self.deployment_journal.log_event(
            mission_id=mission_id,
            event_type="execution_started",
            details={}
        )
        
        try:
            # Prepare for execution
            self._prepare_for_execution(mission_id)
            
            # Update mission status
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["status"] = DeploymentStatus.IN_PROGRESS.value
                mission["updated_at"] = datetime.now().isoformat()
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": "Deployment execution in progress"
                })
            
            # Execute mission
            execution_results = self.mission_executor.execute_mission(
                mission["mission_plan"],
                timeout=self.config["deployment"]["timeout_seconds"]
            )
            
            # Update mission with execution results
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["execution_results"] = execution_results
                mission["updated_at"] = datetime.now().isoformat()
                
                # Update mission status based on execution results
                if execution_results["success"]:
                    mission["status"] = DeploymentStatus.COMPLETED.value
                    mission["progress"] = 100
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": "Deployment execution completed successfully"
                    })
                else:
                    mission["status"] = DeploymentStatus.FAILED.value
                    mission["error"] = {
                        "code": "EXECUTION_FAILED",
                        "message": "Deployment execution failed",
                        "details": execution_results["failures"]
                    }
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": "Deployment execution failed"
                    })
                    
                    # Attempt automatic rollback if configured
                    if self.config["rollback"]["automatic"]:
                        self._initiate_rollback(mission_id, "Automatic rollback due to execution failure")
            
            # Log execution completion
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="execution_completed",
                details={
                    "success": execution_results["success"],
                    "failures": execution_results["failures"] if not execution_results["success"] else None
                }
            )
            
            # Move to deployment history if completed or failed
            if mission["status"] in [DeploymentStatus.COMPLETED.value, DeploymentStatus.FAILED.value]:
                with self.deployment_lock:
                    self.deployment_history.append(mission)
                    del self.active_deployments[mission_id]
            
            logger.info(f"Execution completed for mission {mission_id} with success: {execution_results['success']}")
            return execution_results
            
        except Exception as e:
            logger.error(f"Error executing deployment mission {mission_id}: {str(e)}")
            
            # Update mission with error
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["status"] = DeploymentStatus.FAILED.value
                mission["error"] = {
                    "code": "EXECUTION_ERROR",
                    "message": f"Error executing deployment: {str(e)}",
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                }
                mission["updated_at"] = datetime.now().isoformat()
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"Error executing deployment: {str(e)}"
                })
                
                # Attempt automatic rollback if configured
                if self.config["rollback"]["automatic"]:
                    self._initiate_rollback(mission_id, "Automatic rollback due to execution error")
            
            # Log execution error
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="execution_error",
                details={
                    "error": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            )
            
            raise
    
    def _prepare_for_execution(self, mission_id: str):
        """
        Prepare for mission execution.
        
        Args:
            mission_id: ID of the mission to prepare for execution.
        """
        logger.info(f"Preparing for execution of mission: {mission_id}")
        
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            
            # Get layers to deploy
            layers = mission["mission_spec"]["layers"]
            if layers == "all":
                layers = self.config["layer_sequence"]["default"]
            
            # Determine layer sequence
            layer_sequence = []
            for layer in self.config["layer_sequence"]["default"]:
                if layer in layers:
                    layer_sequence.append(layer)
            
            # Update mission with layer sequence
            mission["layer_sequence"] = layer_sequence
            mission["current_layer_index"] = 0
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Determined layer sequence: {layer_sequence}"
            })
    
    def _initiate_rollback(self, mission_id: str, reason: str):
        """
        Initiate rollback for a mission.
        
        Args:
            mission_id: ID of the mission to rollback.
            reason: Reason for the rollback.
        """
        logger.info(f"Initiating rollback for mission {mission_id}: {reason}")
        
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            mission["status"] = DeploymentStatus.ROLLING_BACK.value
            mission["updated_at"] = datetime.now().isoformat()
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Initiating rollback: {reason}"
            })
        
        # Log rollback initiation
        self.deployment_journal.log_event(
            mission_id=mission_id,
            event_type="rollback_initiated",
            details={
                "reason": reason
            }
        )
        
        # Start rollback in a separate thread
        threading.Thread(target=self._execute_rollback, args=(mission_id,)).start()
    
    def _execute_rollback(self, mission_id: str):
        """
        Execute rollback for a mission.
        
        Args:
            mission_id: ID of the mission to rollback.
        """
        logger.info(f"Executing rollback for mission: {mission_id}")
        
        try:
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                
                # Create rollback plan
                rollback_plan = self.recovery_manager.create_rollback_plan(mission["mission_plan"])
                
                # Update mission with rollback plan
                mission["rollback_plan"] = rollback_plan
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": "Created rollback plan"
                })
            
            # Execute rollback
            rollback_results = self.recovery_manager.execute_rollback(
                rollback_plan,
                timeout=self.config["rollback"]["timeout_seconds"]
            )
            
            # Update mission with rollback results
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["rollback_results"] = rollback_results
                mission["updated_at"] = datetime.now().isoformat()
                
                # Update mission status based on rollback results
                if rollback_results["success"]:
                    mission["status"] = DeploymentStatus.ROLLED_BACK.value
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": "Rollback completed successfully"
                    })
                else:
                    mission["status"] = DeploymentStatus.FAILED.value
                    mission["error"] = {
                        "code": "ROLLBACK_FAILED",
                        "message": "Rollback failed",
                        "details": rollback_results["failures"]
                    }
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": "Rollback failed"
                    })
            
            # Log rollback completion
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="rollback_completed",
                details={
                    "success": rollback_results["success"],
                    "failures": rollback_results["failures"] if not rollback_results["success"] else None
                }
            )
            
            # Move to deployment history if rolled back or failed
            if mission["status"] in [DeploymentStatus.ROLLED_BACK.value, DeploymentStatus.FAILED.value]:
                with self.deployment_lock:
                    self.deployment_history.append(mission)
                    del self.active_deployments[mission_id]
            
            logger.info(f"Rollback completed for mission {mission_id} with success: {rollback_results['success']}")
            
        except Exception as e:
            logger.error(f"Error executing rollback for mission {mission_id}: {str(e)}")
            
            # Update mission with error
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["status"] = DeploymentStatus.FAILED.value
                mission["error"] = {
                    "code": "ROLLBACK_ERROR",
                    "message": f"Error executing rollback: {str(e)}",
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                }
                mission["updated_at"] = datetime.now().isoformat()
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"Error executing rollback: {str(e)}"
                })
            
            # Log rollback error
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="rollback_error",
                details={
                    "error": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            )
    
    def pause_deployment(self, mission_id: str) -> Dict[str, Any]:
        """
        Pause a deployment mission.
        
        Args:
            mission_id: ID of the mission to pause.
            
        Returns:
            Dict containing the updated mission details.
        """
        logger.info(f"Pausing deployment mission: {mission_id}")
        
        with self.deployment_lock:
            if mission_id not in self.active_deployments:
                raise ValueError(f"Mission not found: {mission_id}")
            
            mission = self.active_deployments[mission_id]
            
            # Check if mission can be paused
            if mission["status"] not in [DeploymentStatus.IN_PROGRESS.value]:
                raise ValueError(f"Cannot pause mission with status: {mission['status']}")
            
            # Update mission status
            mission["status"] = DeploymentStatus.PAUSED.value
            mission["updated_at"] = datetime.now().isoformat()
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Deployment paused"
            })
        
        # Log pause
        self.deployment_journal.log_event(
            mission_id=mission_id,
            event_type="mission_paused",
            details={}
        )
        
        # Pause mission execution
        self.mission_executor.pause_mission(mission_id)
        
        logger.info(f"Paused deployment mission: {mission_id}")
        return self.get_mission_details(mission_id)
    
    def resume_deployment(self, mission_id: str) -> Dict[str, Any]:
        """
        Resume a paused deployment mission.
        
        Args:
            mission_id: ID of the mission to resume.
            
        Returns:
            Dict containing the updated mission details.
        """
        logger.info(f"Resuming deployment mission: {mission_id}")
        
        with self.deployment_lock:
            if mission_id not in self.active_deployments:
                raise ValueError(f"Mission not found: {mission_id}")
            
            mission = self.active_deployments[mission_id]
            
            # Check if mission can be resumed
            if mission["status"] != DeploymentStatus.PAUSED.value:
                raise ValueError(f"Cannot resume mission with status: {mission['status']}")
            
            # Update mission status
            mission["status"] = DeploymentStatus.IN_PROGRESS.value
            mission["updated_at"] = datetime.now().isoformat()
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Deployment resumed"
            })
        
        # Log resume
        self.deployment_journal.log_event(
            mission_id=mission_id,
            event_type="mission_resumed",
            details={}
        )
        
        # Resume mission execution
        self.mission_executor.resume_mission(mission_id)
        
        logger.info(f"Resumed deployment mission: {mission_id}")
        return self.get_mission_details(mission_id)
    
    def cancel_deployment(self, mission_id: str) -> Dict[str, Any]:
        """
        Cancel a deployment mission.
        
        Args:
            mission_id: ID of the mission to cancel.
            
        Returns:
            Dict containing the updated mission details.
        """
        logger.info(f"Cancelling deployment mission: {mission_id}")
        
        with self.deployment_lock:
            if mission_id not in self.active_deployments:
                raise ValueError(f"Mission not found: {mission_id}")
            
            mission = self.active_deployments[mission_id]
            
            # Check if mission can be cancelled
            if mission["status"] in [DeploymentStatus.COMPLETED.value, DeploymentStatus.FAILED.value, DeploymentStatus.ROLLED_BACK.value, DeploymentStatus.CANCELLED.value]:
                raise ValueError(f"Cannot cancel mission with status: {mission['status']}")
            
            # Update mission status
            mission["status"] = DeploymentStatus.CANCELLED.value
            mission["updated_at"] = datetime.now().isoformat()
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Deployment cancelled"
            })
        
        # Log cancellation
        self.deployment_journal.log_event(
            mission_id=mission_id,
            event_type="mission_cancelled",
            details={}
        )
        
        # Cancel mission execution
        if mission["status"] == DeploymentStatus.IN_PROGRESS.value:
            self.mission_executor.cancel_mission(mission_id)
        
        # Move to deployment history
        with self.deployment_lock:
            self.deployment_history.append(mission)
            del self.active_deployments[mission_id]
        
        logger.info(f"Cancelled deployment mission: {mission_id}")
        return mission
    
    def rollback_deployment(self, mission_id: str, reason: str) -> Dict[str, Any]:
        """
        Rollback a deployment mission.
        
        Args:
            mission_id: ID of the mission to rollback.
            reason: Reason for the rollback.
            
        Returns:
            Dict containing the updated mission details.
        """
        logger.info(f"Rolling back deployment mission: {mission_id}")
        
        with self.deployment_lock:
            if mission_id not in self.active_deployments:
                # Check if mission is in history
                for mission in self.deployment_history:
                    if mission["mission_id"] == mission_id:
                        # Move mission back to active deployments
                        self.active_deployments[mission_id] = mission
                        self.deployment_history.remove(mission)
                        break
                else:
                    raise ValueError(f"Mission not found: {mission_id}")
            
            mission = self.active_deployments[mission_id]
            
            # Check if mission can be rolled back
            if mission["status"] in [DeploymentStatus.PENDING.value, DeploymentStatus.SIMULATING.value, DeploymentStatus.ROLLING_BACK.value, DeploymentStatus.ROLLED_BACK.value]:
                raise ValueError(f"Cannot rollback mission with status: {mission['status']}")
        
        # Initiate rollback
        self._initiate_rollback(mission_id, reason)
        
        logger.info(f"Initiated rollback for deployment mission: {mission_id}")
        return self.get_mission_details(mission_id)
    
    def get_mission_details(self, mission_id: str) -> Dict[str, Any]:
        """
        Get details for a deployment mission.
        
        Args:
            mission_id: ID of the mission.
            
        Returns:
            Dict containing the mission details.
        """
        logger.info(f"Getting details for mission: {mission_id}")
        
        # Check active deployments
        with self.deployment_lock:
            if mission_id in self.active_deployments:
                return self.active_deployments[mission_id]
        
        # Check deployment history
        for mission in self.deployment_history:
            if mission["mission_id"] == mission_id:
                return mission
        
        raise ValueError(f"Mission not found: {mission_id}")
    
    def get_active_missions(self) -> List[Dict[str, Any]]:
        """
        Get all active deployment missions.
        
        Returns:
            List of dicts containing mission details.
        """
        logger.info("Getting all active missions")
        
        with self.deployment_lock:
            return list(self.active_deployments.values())
    
    def get_mission_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get deployment mission history.
        
        Args:
            limit: Maximum number of missions to return.
            
        Returns:
            List of dicts containing mission details.
        """
        logger.info(f"Getting mission history with limit: {limit}")
        
        # Sort history by creation time (newest first)
        sorted_history = sorted(
            self.deployment_history,
            key=lambda x: x["created_at"],
            reverse=True
        )
        
        return sorted_history[:limit]
    
    def get_mission_logs(self, mission_id: str) -> List[Dict[str, Any]]:
        """
        Get logs for a deployment mission.
        
        Args:
            mission_id: ID of the mission.
            
        Returns:
            List of dicts containing log entries.
        """
        logger.info(f"Getting logs for mission: {mission_id}")
        
        mission = self.get_mission_details(mission_id)
        return mission["logs"]
    
    def get_mission_metrics(self, mission_id: str) -> Dict[str, Any]:
        """
        Get metrics for a deployment mission.
        
        Args:
            mission_id: ID of the mission.
            
        Returns:
            Dict containing mission metrics.
        """
        logger.info(f"Getting metrics for mission: {mission_id}")
        
        mission = self.get_mission_details(mission_id)
        
        # If metrics are not yet collected, collect them now
        if not mission["metrics"]:
            mission["metrics"] = self.analytics_manager.collect_mission_metrics(mission_id)
        
        return mission["metrics"]
    
    def update_mission_progress(self, mission_id: str, progress: int, message: str = None):
        """
        Update progress for a deployment mission.
        
        Args:
            mission_id: ID of the mission.
            progress: Progress percentage (0-100).
            message: Optional progress message.
        """
        logger.info(f"Updating progress for mission {mission_id}: {progress}%")
        
        with self.deployment_lock:
            if mission_id not in self.active_deployments:
                raise ValueError(f"Mission not found: {mission_id}")
            
            mission = self.active_deployments[mission_id]
            mission["progress"] = progress
            mission["updated_at"] = datetime.now().isoformat()
            
            if message:
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": message
                })
        
        # Log progress update
        self.deployment_journal.log_event(
            mission_id=mission_id,
            event_type="progress_updated",
            details={
                "progress": progress,
                "message": message
            }
        )
