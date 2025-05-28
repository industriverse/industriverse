"""
Multi-Region Deployment Orchestrator for the Deployment Operations Layer

This module provides specialized orchestration capabilities for deploying
across multiple geographic regions, ensuring coordinated, reliable deployments
with proper sequencing, dependency management, and rollback capabilities.

The orchestrator serves as the central coordination point for executing
deployment missions across multiple regions in the Industriverse ecosystem.
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
from .layer_deployment_orchestrator import LayerDeploymentOrchestrator, DeploymentStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegionDeploymentStrategy(Enum):
    """Enum representing the strategy for multi-region deployments."""
    SEQUENTIAL = "sequential"  # Deploy to regions one after another
    PARALLEL = "parallel"      # Deploy to all regions simultaneously
    CANARY = "canary"          # Deploy to a subset of regions first, then the rest
    BLUE_GREEN = "blue_green"  # Deploy to new infrastructure in each region, then switch

class RegionStatus(Enum):
    """Enum representing the status of a region in a multi-region deployment."""
    PENDING = "pending"
    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"

class MultiRegionDeploymentOrchestrator:
    """
    Orchestrates deployments across multiple geographic regions.
    
    This class provides specialized orchestration capabilities for deploying
    across multiple regions, ensuring coordinated, reliable deployments
    with proper sequencing, dependency management, and rollback capabilities.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Multi-Region Deployment Orchestrator.
        
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
        
        # Create layer deployment orchestrator for each region
        self.region_orchestrators = {}
        for region in self.config["regions"]:
            self.region_orchestrators[region] = LayerDeploymentOrchestrator()
        
        # Initialize deployment tracking
        self.active_deployments = {}
        self.deployment_history = []
        
        # Initialize locks for thread safety
        self.deployment_lock = threading.Lock()
        
        logger.info("Multi-Region Deployment Orchestrator initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration for the orchestrator.
        
        Args:
            config_path: Path to the configuration file.
            
        Returns:
            Dict containing the configuration.
        """
        default_config = {
            "regions": [
                "us-east",
                "us-west",
                "eu-central",
                "ap-southeast"
            ],
            "default_strategy": "sequential",
            "simulation": {
                "enabled": True,
                "timeout_seconds": 300,
                "success_threshold": 0.95
            },
            "deployment": {
                "max_concurrent_regions": 2,
                "timeout_seconds": 3600,
                "retry_attempts": 3,
                "retry_delay_seconds": 30
            },
            "rollback": {
                "automatic": True,
                "timeout_seconds": 1800
            },
            "canary": {
                "initial_regions": ["us-east"],
                "validation_period_seconds": 600
            },
            "blue_green": {
                "switch_timeout_seconds": 300
            },
            "health_check": {
                "interval_seconds": 30,
                "timeout_seconds": 10,
                "failure_threshold": 3
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
        Create a new multi-region deployment mission.
        
        Args:
            mission_spec: Specification for the deployment mission.
            
        Returns:
            String containing the mission ID.
        """
        logger.info(f"Creating multi-region deployment mission with spec: {mission_spec}")
        
        # Validate mission spec
        self._validate_mission_spec(mission_spec)
        
        # Generate mission ID
        mission_id = f"multi-region-mission-{int(time.time())}-{os.urandom(4).hex()}"
        
        # Determine regions to deploy to
        regions = mission_spec.get("regions", self.config["regions"])
        
        # Determine deployment strategy
        strategy = mission_spec.get("strategy", self.config["default_strategy"])
        
        # Create mission plan for each region
        region_plans = {}
        for region in regions:
            # Create region-specific mission spec
            region_spec = mission_spec.copy()
            region_spec["region"] = region
            
            # Apply region-specific overrides if provided
            if "region_overrides" in mission_spec and region in mission_spec["region_overrides"]:
                for key, value in mission_spec["region_overrides"][region].items():
                    region_spec[key] = value
            
            # Create mission plan for the region
            region_plans[region] = self.mission_planner.create_mission_plan(region_spec)
        
        # Initialize deployment tracking
        with self.deployment_lock:
            self.active_deployments[mission_id] = {
                "mission_id": mission_id,
                "mission_spec": mission_spec,
                "strategy": strategy,
                "regions": regions,
                "region_plans": region_plans,
                "region_statuses": {region: RegionStatus.PENDING.value for region in regions},
                "region_progress": {region: 0 for region in regions},
                "region_results": {},
                "status": DeploymentStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "layers": mission_spec.get("layers", []),
                "environment": mission_spec.get("environment", "production"),
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
            event_type="multi_region_mission_created",
            details={
                "mission_spec": mission_spec,
                "regions": regions,
                "strategy": strategy
            }
        )
        
        logger.info(f"Created multi-region deployment mission with ID: {mission_id}")
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
        
        # Validate regions if provided
        if "regions" in mission_spec:
            if not isinstance(mission_spec["regions"], list):
                raise ValueError(f"Regions must be a list: {mission_spec['regions']}")
            
            for region in mission_spec["regions"]:
                if region not in self.config["regions"]:
                    raise ValueError(f"Invalid region in mission spec: {region}")
        
        # Validate strategy if provided
        if "strategy" in mission_spec:
            try:
                RegionDeploymentStrategy(mission_spec["strategy"])
            except ValueError:
                raise ValueError(f"Invalid deployment strategy in mission spec: {mission_spec['strategy']}")
        
        # Validate region_overrides if provided
        if "region_overrides" in mission_spec:
            if not isinstance(mission_spec["region_overrides"], dict):
                raise ValueError(f"Region overrides must be a dictionary: {mission_spec['region_overrides']}")
            
            for region, overrides in mission_spec["region_overrides"].items():
                if region not in self.config["regions"]:
                    raise ValueError(f"Invalid region in region overrides: {region}")
                
                if not isinstance(overrides, dict):
                    raise ValueError(f"Overrides for region {region} must be a dictionary: {overrides}")
    
    def simulate_deployment(self, mission_id: str) -> Dict[str, Any]:
        """
        Simulate a multi-region deployment mission.
        
        Args:
            mission_id: ID of the mission to simulate.
            
        Returns:
            Dict containing the simulation results.
        """
        logger.info(f"Simulating multi-region deployment mission: {mission_id}")
        
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
            event_type="multi_region_simulation_started",
            details={}
        )
        
        try:
            # Simulate deployment for each region
            region_simulation_results = {}
            overall_success = True
            failures = []
            
            for region in mission["regions"]:
                logger.info(f"Simulating deployment for region {region} in mission {mission_id}")
                
                # Run simulation for the region
                region_result = self.simulation_engine.run_simulation(
                    mission["region_plans"][region],
                    timeout=self.config["simulation"]["timeout_seconds"]
                )
                
                region_simulation_results[region] = region_result
                
                # Check if region simulation was successful
                if region_result["success_rate"] < self.config["simulation"]["success_threshold"]:
                    overall_success = False
                    failures.append({
                        "region": region,
                        "success_rate": region_result["success_rate"],
                        "failures": region_result["failures"]
                    })
            
            # Compile overall simulation results
            simulation_results = {
                "overall_success": overall_success,
                "region_results": region_simulation_results,
                "failures": failures
            }
            
            # Update mission with simulation results
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["simulation_results"] = simulation_results
                mission["updated_at"] = datetime.now().isoformat()
                
                # Update mission status based on simulation results
                if overall_success:
                    mission["status"] = DeploymentStatus.PENDING.value
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": "Multi-region simulation successful"
                    })
                else:
                    mission["status"] = DeploymentStatus.FAILED.value
                    mission["error"] = {
                        "code": "SIMULATION_FAILED",
                        "message": "Multi-region simulation failed",
                        "details": failures
                    }
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": "Multi-region simulation failed"
                    })
            
            # Log simulation completion
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="multi_region_simulation_completed",
                details={
                    "overall_success": overall_success,
                    "failures": failures
                }
            )
            
            logger.info(f"Multi-region simulation completed for mission {mission_id} with success: {overall_success}")
            return simulation_results
            
        except Exception as e:
            logger.error(f"Error simulating multi-region deployment mission {mission_id}: {str(e)}")
            
            # Update mission with error
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["status"] = DeploymentStatus.FAILED.value
                mission["error"] = {
                    "code": "SIMULATION_ERROR",
                    "message": f"Error simulating multi-region deployment: {str(e)}",
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                }
                mission["updated_at"] = datetime.now().isoformat()
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"Error simulating multi-region deployment: {str(e)}"
                })
            
            # Log simulation error
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="multi_region_simulation_error",
                details={
                    "error": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            )
            
            raise
    
    def execute_deployment(self, mission_id: str) -> Dict[str, Any]:
        """
        Execute a multi-region deployment mission.
        
        Args:
            mission_id: ID of the mission to execute.
            
        Returns:
            Dict containing the execution results.
        """
        logger.info(f"Executing multi-region deployment mission: {mission_id}")
        
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
                "message": "Preparing for multi-region deployment execution"
            })
        
        # Log execution start
        self.deployment_journal.log_event(
            mission_id=mission_id,
            event_type="multi_region_execution_started",
            details={}
        )
        
        try:
            # Execute deployment based on strategy
            strategy = RegionDeploymentStrategy(mission["strategy"])
            
            if strategy == RegionDeploymentStrategy.SEQUENTIAL:
                execution_results = self._execute_sequential(mission_id)
            elif strategy == RegionDeploymentStrategy.PARALLEL:
                execution_results = self._execute_parallel(mission_id)
            elif strategy == RegionDeploymentStrategy.CANARY:
                execution_results = self._execute_canary(mission_id)
            elif strategy == RegionDeploymentStrategy.BLUE_GREEN:
                execution_results = self._execute_blue_green(mission_id)
            else:
                raise ValueError(f"Unsupported deployment strategy: {strategy}")
            
            # Update mission with execution results
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["execution_results"] = execution_results
                mission["updated_at"] = datetime.now().isoformat()
                
                # Update mission status based on execution results
                if execution_results["overall_success"]:
                    mission["status"] = DeploymentStatus.COMPLETED.value
                    mission["progress"] = 100
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": "Multi-region deployment execution completed successfully"
                    })
                else:
                    mission["status"] = DeploymentStatus.FAILED.value
                    mission["error"] = {
                        "code": "EXECUTION_FAILED",
                        "message": "Multi-region deployment execution failed",
                        "details": execution_results["failures"]
                    }
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": "Multi-region deployment execution failed"
                    })
            
            # Log execution completion
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="multi_region_execution_completed",
                details={
                    "overall_success": execution_results["overall_success"],
                    "failures": execution_results["failures"] if not execution_results["overall_success"] else None
                }
            )
            
            # Move to deployment history if completed or failed
            if mission["status"] in [DeploymentStatus.COMPLETED.value, DeploymentStatus.FAILED.value]:
                with self.deployment_lock:
                    self.deployment_history.append(mission)
                    del self.active_deployments[mission_id]
            
            logger.info(f"Multi-region execution completed for mission {mission_id} with success: {execution_results['overall_success']}")
            return execution_results
            
        except Exception as e:
            logger.error(f"Error executing multi-region deployment mission {mission_id}: {str(e)}")
            
            # Update mission with error
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["status"] = DeploymentStatus.FAILED.value
                mission["error"] = {
                    "code": "EXECUTION_ERROR",
                    "message": f"Error executing multi-region deployment: {str(e)}",
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                }
                mission["updated_at"] = datetime.now().isoformat()
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"Error executing multi-region deployment: {str(e)}"
                })
            
            # Log execution error
            self.deployment_journal.log_event(
                mission_id=mission_id,
                event_type="multi_region_execution_error",
                details={
                    "error": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            )
            
            raise
    
    def _execute_sequential(self, mission_id: str) -> Dict[str, Any]:
        """
        Execute a multi-region deployment mission sequentially.
        
        Args:
            mission_id: ID of the mission to execute.
            
        Returns:
            Dict containing the execution results.
        """
        logger.info(f"Executing sequential multi-region deployment for mission: {mission_id}")
        
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            regions = mission["regions"]
            
            # Update mission status
            mission["status"] = DeploymentStatus.IN_PROGRESS.value
            mission["updated_at"] = datetime.now().isoformat()
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Starting sequential deployment to {len(regions)} regions"
            })
        
        # Execute deployment for each region sequentially
        region_results = {}
        overall_success = True
        failures = []
        
        for i, region in enumerate(regions):
            logger.info(f"Deploying to region {region} ({i+1}/{len(regions)}) in mission {mission_id}")
            
            # Update region status
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["region_statuses"][region] = RegionStatus.IN_PROGRESS.value
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Deploying to region {region} ({i+1}/{len(regions)})"
                })
            
            try:
                # Execute deployment for the region
                region_result = self.region_orchestrators[region].execute_deployment(
                    mission["region_plans"][region],
                    timeout=self.config["deployment"]["timeout_seconds"]
                )
                
                region_results[region] = region_result
                
                # Check if region deployment was successful
                if not region_result["success"]:
                    overall_success = False
                    failures.append({
                        "region": region,
                        "error": region_result["error"],
                        "details": region_result["failures"]
                    })
                    
                    # Update region status
                    with self.deployment_lock:
                        mission = self.active_deployments[mission_id]
                        mission["region_statuses"][region] = RegionStatus.FAILED.value
                        mission["region_results"][region] = region_result
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "ERROR",
                            "message": f"Deployment to region {region} failed"
                        })
                    
                    # Stop sequential deployment if a region fails
                    logger.error(f"Deployment to region {region} failed, stopping sequential deployment")
                    break
                else:
                    # Update region status
                    with self.deployment_lock:
                        mission = self.active_deployments[mission_id]
                        mission["region_statuses"][region] = RegionStatus.COMPLETED.value
                        mission["region_progress"][region] = 100
                        mission["region_results"][region] = region_result
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "message": f"Deployment to region {region} completed successfully"
                        })
                
                # Update overall mission progress
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    completed_regions = sum(1 for status in mission["region_statuses"].values() 
                                          if status in [RegionStatus.COMPLETED.value, RegionStatus.FAILED.value, RegionStatus.SKIPPED.value])
                    mission["progress"] = int((completed_regions / len(regions)) * 100)
                
            except Exception as e:
                logger.error(f"Error deploying to region {region} in mission {mission_id}: {str(e)}")
                
                overall_success = False
                failures.append({
                    "region": region,
                    "error": str(e),
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                })
                
                # Update region status
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["region_statuses"][region] = RegionStatus.FAILED.value
                    mission["region_results"][region] = {
                        "success": False,
                        "error": str(e),
                        "details": {
                            "exception": str(e),
                            "traceback": logging.traceback.format_exc()
                        }
                    }
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Error deploying to region {region}: {str(e)}"
                    })
                
                # Stop sequential deployment if a region fails
                break
        
        # Mark remaining regions as skipped if there was a failure
        if not overall_success:
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                for region in regions:
                    if mission["region_statuses"][region] == RegionStatus.PENDING.value:
                        mission["region_statuses"][region] = RegionStatus.SKIPPED.value
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "message": f"Deployment to region {region} skipped due to previous failure"
                        })
        
        # Compile overall execution results
        execution_results = {
            "overall_success": overall_success,
            "region_results": region_results,
            "failures": failures
        }
        
        return execution_results
    
    def _execute_parallel(self, mission_id: str) -> Dict[str, Any]:
        """
        Execute a multi-region deployment mission in parallel.
        
        Args:
            mission_id: ID of the mission to execute.
            
        Returns:
            Dict containing the execution results.
        """
        logger.info(f"Executing parallel multi-region deployment for mission: {mission_id}")
        
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            regions = mission["regions"]
            
            # Update mission status
            mission["status"] = DeploymentStatus.IN_PROGRESS.value
            mission["updated_at"] = datetime.now().isoformat()
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Starting parallel deployment to {len(regions)} regions"
            })
        
        # Execute deployment for each region in parallel
        max_concurrent = self.config["deployment"]["max_concurrent_regions"]
        region_results = {}
        region_threads = {}
        region_errors = {}
        
        # Process regions in batches to respect max_concurrent
        for i in range(0, len(regions), max_concurrent):
            batch_regions = regions[i:i+max_concurrent]
            logger.info(f"Deploying to batch of {len(batch_regions)} regions in mission {mission_id}")
            
            # Start deployment threads for each region in the batch
            for region in batch_regions:
                logger.info(f"Starting deployment thread for region {region} in mission {mission_id}")
                
                # Update region status
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["region_statuses"][region] = RegionStatus.IN_PROGRESS.value
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": f"Deploying to region {region}"
                    })
                
                # Start deployment thread for the region
                thread = threading.Thread(
                    target=self._execute_region_deployment,
                    args=(mission_id, region, region_results, region_errors)
                )
                thread.start()
                region_threads[region] = thread
            
            # Wait for all threads in the batch to complete
            for region in batch_regions:
                region_threads[region].join()
                
                # Update overall mission progress
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    completed_regions = sum(1 for status in mission["region_statuses"].values() 
                                          if status in [RegionStatus.COMPLETED.value, RegionStatus.FAILED.value])
                    mission["progress"] = int((completed_regions / len(regions)) * 100)
        
        # Check if all regions were successful
        overall_success = True
        failures = []
        
        for region, error in region_errors.items():
            if error:
                overall_success = False
                failures.append({
                    "region": region,
                    "error": str(error),
                    "details": {
                        "exception": str(error),
                        "traceback": getattr(error, "traceback", "")
                    }
                })
        
        # Compile overall execution results
        execution_results = {
            "overall_success": overall_success,
            "region_results": region_results,
            "failures": failures
        }
        
        return execution_results
    
    def _execute_region_deployment(self, mission_id: str, region: str, results_dict: Dict[str, Any], errors_dict: Dict[str, Exception]):
        """
        Execute deployment for a specific region.
        
        Args:
            mission_id: ID of the mission.
            region: Region to deploy to.
            results_dict: Dictionary to store results.
            errors_dict: Dictionary to store errors.
        """
        logger.info(f"Executing deployment for region {region} in mission {mission_id}")
        
        try:
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                region_plan = mission["region_plans"][region]
            
            # Execute deployment for the region
            region_result = self.region_orchestrators[region].execute_deployment(
                region_plan,
                timeout=self.config["deployment"]["timeout_seconds"]
            )
            
            # Store result
            results_dict[region] = region_result
            errors_dict[region] = None
            
            # Update region status
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                
                if region_result["success"]:
                    mission["region_statuses"][region] = RegionStatus.COMPLETED.value
                    mission["region_progress"][region] = 100
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": f"Deployment to region {region} completed successfully"
                    })
                else:
                    mission["region_statuses"][region] = RegionStatus.FAILED.value
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Deployment to region {region} failed"
                    })
                
                mission["region_results"][region] = region_result
            
            logger.info(f"Deployment for region {region} in mission {mission_id} completed with success: {region_result['success']}")
            
        except Exception as e:
            logger.error(f"Error deploying to region {region} in mission {mission_id}: {str(e)}")
            
            # Store error
            errors_dict[region] = e
            results_dict[region] = {
                "success": False,
                "error": str(e),
                "details": {
                    "exception": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            }
            
            # Update region status
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["region_statuses"][region] = RegionStatus.FAILED.value
                mission["region_results"][region] = results_dict[region]
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"Error deploying to region {region}: {str(e)}"
                })
    
    def _execute_canary(self, mission_id: str) -> Dict[str, Any]:
        """
        Execute a multi-region deployment mission using canary strategy.
        
        Args:
            mission_id: ID of the mission to execute.
            
        Returns:
            Dict containing the execution results.
        """
        logger.info(f"Executing canary multi-region deployment for mission: {mission_id}")
        
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            regions = mission["regions"]
            
            # Determine canary regions
            canary_regions = mission["mission_spec"].get("canary_regions", self.config["canary"]["initial_regions"])
            
            # Ensure all canary regions are in the deployment regions
            canary_regions = [region for region in canary_regions if region in regions]
            
            # If no valid canary regions, use the first region
            if not canary_regions and regions:
                canary_regions = [regions[0]]
            
            # Determine remaining regions
            remaining_regions = [region for region in regions if region not in canary_regions]
            
            # Update mission with canary information
            mission["canary_regions"] = canary_regions
            mission["remaining_regions"] = remaining_regions
            mission["status"] = DeploymentStatus.IN_PROGRESS.value
            mission["updated_at"] = datetime.now().isoformat()
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Starting canary deployment with initial regions: {canary_regions}"
            })
        
        # Execute deployment for canary regions
        canary_results = {}
        canary_success = True
        canary_failures = []
        
        for region in canary_regions:
            logger.info(f"Deploying to canary region {region} in mission {mission_id}")
            
            # Update region status
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["region_statuses"][region] = RegionStatus.IN_PROGRESS.value
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Deploying to canary region {region}"
                })
            
            try:
                # Execute deployment for the region
                region_result = self.region_orchestrators[region].execute_deployment(
                    mission["region_plans"][region],
                    timeout=self.config["deployment"]["timeout_seconds"]
                )
                
                canary_results[region] = region_result
                
                # Check if region deployment was successful
                if not region_result["success"]:
                    canary_success = False
                    canary_failures.append({
                        "region": region,
                        "error": region_result["error"],
                        "details": region_result["failures"]
                    })
                    
                    # Update region status
                    with self.deployment_lock:
                        mission = self.active_deployments[mission_id]
                        mission["region_statuses"][region] = RegionStatus.FAILED.value
                        mission["region_results"][region] = region_result
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "ERROR",
                            "message": f"Deployment to canary region {region} failed"
                        })
                else:
                    # Update region status
                    with self.deployment_lock:
                        mission = self.active_deployments[mission_id]
                        mission["region_statuses"][region] = RegionStatus.COMPLETED.value
                        mission["region_progress"][region] = 100
                        mission["region_results"][region] = region_result
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "message": f"Deployment to canary region {region} completed successfully"
                        })
                
            except Exception as e:
                logger.error(f"Error deploying to canary region {region} in mission {mission_id}: {str(e)}")
                
                canary_success = False
                canary_failures.append({
                    "region": region,
                    "error": str(e),
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                })
                
                # Update region status
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["region_statuses"][region] = RegionStatus.FAILED.value
                    mission["region_results"][region] = {
                        "success": False,
                        "error": str(e),
                        "details": {
                            "exception": str(e),
                            "traceback": logging.traceback.format_exc()
                        }
                    }
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Error deploying to canary region {region}: {str(e)}"
                    })
        
        # Update overall mission progress
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            completed_regions = sum(1 for status in mission["region_statuses"].values() 
                                  if status in [RegionStatus.COMPLETED.value, RegionStatus.FAILED.value, RegionStatus.SKIPPED.value])
            mission["progress"] = int((completed_regions / len(regions)) * 100)
        
        # If canary deployment failed, mark remaining regions as skipped
        if not canary_success:
            logger.error(f"Canary deployment failed for mission {mission_id}, skipping remaining regions")
            
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                for region in remaining_regions:
                    mission["region_statuses"][region] = RegionStatus.SKIPPED.value
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": f"Deployment to region {region} skipped due to canary failure"
                    })
            
            # Compile overall execution results
            execution_results = {
                "overall_success": False,
                "region_results": canary_results,
                "failures": canary_failures
            }
            
            return execution_results
        
        # Wait for validation period
        validation_period = mission["mission_spec"].get("validation_period_seconds", 
                                                      self.config["canary"]["validation_period_seconds"])
        
        logger.info(f"Canary deployment successful, waiting for validation period of {validation_period} seconds")
        
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Canary deployment successful, waiting for validation period of {validation_period} seconds"
            })
        
        # Sleep for validation period
        time.sleep(validation_period)
        
        # Check canary health
        canary_health = self._check_canary_health(mission_id, canary_regions)
        
        if not canary_health["healthy"]:
            logger.error(f"Canary health check failed for mission {mission_id}, skipping remaining regions")
            
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"Canary health check failed: {canary_health['reason']}"
                })
                
                for region in remaining_regions:
                    mission["region_statuses"][region] = RegionStatus.SKIPPED.value
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": f"Deployment to region {region} skipped due to canary health check failure"
                    })
            
            # Compile overall execution results
            execution_results = {
                "overall_success": False,
                "region_results": canary_results,
                "failures": [{
                    "error": "CANARY_HEALTH_CHECK_FAILED",
                    "message": canary_health["reason"],
                    "details": canary_health["details"]
                }]
            }
            
            return execution_results
        
        # Deploy to remaining regions
        logger.info(f"Canary health check passed, deploying to remaining {len(remaining_regions)} regions")
        
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Canary health check passed, deploying to remaining {len(remaining_regions)} regions"
            })
        
        # Execute deployment for remaining regions
        remaining_results = {}
        remaining_success = True
        remaining_failures = []
        
        for region in remaining_regions:
            logger.info(f"Deploying to region {region} in mission {mission_id}")
            
            # Update region status
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["region_statuses"][region] = RegionStatus.IN_PROGRESS.value
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Deploying to region {region}"
                })
            
            try:
                # Execute deployment for the region
                region_result = self.region_orchestrators[region].execute_deployment(
                    mission["region_plans"][region],
                    timeout=self.config["deployment"]["timeout_seconds"]
                )
                
                remaining_results[region] = region_result
                
                # Check if region deployment was successful
                if not region_result["success"]:
                    remaining_success = False
                    remaining_failures.append({
                        "region": region,
                        "error": region_result["error"],
                        "details": region_result["failures"]
                    })
                    
                    # Update region status
                    with self.deployment_lock:
                        mission = self.active_deployments[mission_id]
                        mission["region_statuses"][region] = RegionStatus.FAILED.value
                        mission["region_results"][region] = region_result
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "ERROR",
                            "message": f"Deployment to region {region} failed"
                        })
                else:
                    # Update region status
                    with self.deployment_lock:
                        mission = self.active_deployments[mission_id]
                        mission["region_statuses"][region] = RegionStatus.COMPLETED.value
                        mission["region_progress"][region] = 100
                        mission["region_results"][region] = region_result
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "message": f"Deployment to region {region} completed successfully"
                        })
                
                # Update overall mission progress
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    completed_regions = sum(1 for status in mission["region_statuses"].values() 
                                          if status in [RegionStatus.COMPLETED.value, RegionStatus.FAILED.value, RegionStatus.SKIPPED.value])
                    mission["progress"] = int((completed_regions / len(regions)) * 100)
                
            except Exception as e:
                logger.error(f"Error deploying to region {region} in mission {mission_id}: {str(e)}")
                
                remaining_success = False
                remaining_failures.append({
                    "region": region,
                    "error": str(e),
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                })
                
                # Update region status
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["region_statuses"][region] = RegionStatus.FAILED.value
                    mission["region_results"][region] = {
                        "success": False,
                        "error": str(e),
                        "details": {
                            "exception": str(e),
                            "traceback": logging.traceback.format_exc()
                        }
                    }
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Error deploying to region {region}: {str(e)}"
                    })
        
        # Combine results
        all_results = {**canary_results, **remaining_results}
        all_failures = canary_failures + remaining_failures
        
        # Compile overall execution results
        execution_results = {
            "overall_success": canary_success and remaining_success,
            "region_results": all_results,
            "failures": all_failures
        }
        
        return execution_results
    
    def _check_canary_health(self, mission_id: str, canary_regions: List[str]) -> Dict[str, Any]:
        """
        Check health of canary regions.
        
        Args:
            mission_id: ID of the mission.
            canary_regions: List of canary regions to check.
            
        Returns:
            Dict containing health check results.
        """
        logger.info(f"Checking health of canary regions for mission {mission_id}")
        
        # Get mission details
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
        
        # Check health of each canary region
        unhealthy_regions = []
        
        for region in canary_regions:
            # Skip regions that failed deployment
            if mission["region_statuses"][region] != RegionStatus.COMPLETED.value:
                continue
            
            # Check region health
            try:
                health_result = self._check_region_health(mission_id, region)
                
                if not health_result["healthy"]:
                    unhealthy_regions.append({
                        "region": region,
                        "reason": health_result["reason"],
                        "details": health_result["details"]
                    })
            except Exception as e:
                logger.error(f"Error checking health of region {region} in mission {mission_id}: {str(e)}")
                
                unhealthy_regions.append({
                    "region": region,
                    "reason": f"Health check error: {str(e)}",
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                })
        
        # Determine overall health
        if unhealthy_regions:
            return {
                "healthy": False,
                "reason": f"{len(unhealthy_regions)} canary regions are unhealthy",
                "details": unhealthy_regions
            }
        else:
            return {
                "healthy": True,
                "reason": "All canary regions are healthy",
                "details": {}
            }
    
    def _check_region_health(self, mission_id: str, region: str) -> Dict[str, Any]:
        """
        Check health of a specific region.
        
        Args:
            mission_id: ID of the mission.
            region: Region to check.
            
        Returns:
            Dict containing health check results.
        """
        logger.info(f"Checking health of region {region} in mission {mission_id}")
        
        # Get mission details
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            layers = mission["layers"]
        
        # Check health of each layer in the region
        unhealthy_layers = []
        
        for layer in layers:
            try:
                # Get layer adapter for the region
                layer_adapter = self.layer_integration_manager.get_layer_adapter(layer, region)
                
                # Check layer health
                health_result = layer_adapter.check_health(
                    timeout=self.config["health_check"]["timeout_seconds"]
                )
                
                if not health_result["healthy"]:
                    unhealthy_layers.append({
                        "layer": layer,
                        "reason": health_result["reason"],
                        "details": health_result["details"]
                    })
            except Exception as e:
                logger.error(f"Error checking health of layer {layer} in region {region}: {str(e)}")
                
                unhealthy_layers.append({
                    "layer": layer,
                    "reason": f"Health check error: {str(e)}",
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                })
        
        # Determine overall health
        if unhealthy_layers:
            return {
                "healthy": False,
                "reason": f"{len(unhealthy_layers)} layers are unhealthy in region {region}",
                "details": unhealthy_layers
            }
        else:
            return {
                "healthy": True,
                "reason": f"All layers are healthy in region {region}",
                "details": {}
            }
    
    def _execute_blue_green(self, mission_id: str) -> Dict[str, Any]:
        """
        Execute a multi-region deployment mission using blue-green strategy.
        
        Args:
            mission_id: ID of the mission to execute.
            
        Returns:
            Dict containing the execution results.
        """
        logger.info(f"Executing blue-green multi-region deployment for mission: {mission_id}")
        
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            regions = mission["regions"]
            
            # Update mission status
            mission["status"] = DeploymentStatus.IN_PROGRESS.value
            mission["updated_at"] = datetime.now().isoformat()
            mission["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Starting blue-green deployment to {len(regions)} regions"
            })
        
        # Execute blue-green deployment for each region
        region_results = {}
        overall_success = True
        failures = []
        
        for region in regions:
            logger.info(f"Executing blue-green deployment for region {region} in mission {mission_id}")
            
            # Update region status
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["region_statuses"][region] = RegionStatus.IN_PROGRESS.value
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Executing blue-green deployment for region {region}"
                })
            
            try:
                # Execute blue-green deployment for the region
                region_result = self._execute_blue_green_for_region(mission_id, region)
                
                region_results[region] = region_result
                
                # Check if region deployment was successful
                if not region_result["success"]:
                    overall_success = False
                    failures.append({
                        "region": region,
                        "error": region_result["error"],
                        "details": region_result["details"]
                    })
                    
                    # Update region status
                    with self.deployment_lock:
                        mission = self.active_deployments[mission_id]
                        mission["region_statuses"][region] = RegionStatus.FAILED.value
                        mission["region_results"][region] = region_result
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "ERROR",
                            "message": f"Blue-green deployment for region {region} failed"
                        })
                else:
                    # Update region status
                    with self.deployment_lock:
                        mission = self.active_deployments[mission_id]
                        mission["region_statuses"][region] = RegionStatus.COMPLETED.value
                        mission["region_progress"][region] = 100
                        mission["region_results"][region] = region_result
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "message": f"Blue-green deployment for region {region} completed successfully"
                        })
                
                # Update overall mission progress
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    completed_regions = sum(1 for status in mission["region_statuses"].values() 
                                          if status in [RegionStatus.COMPLETED.value, RegionStatus.FAILED.value, RegionStatus.SKIPPED.value])
                    mission["progress"] = int((completed_regions / len(regions)) * 100)
                
            except Exception as e:
                logger.error(f"Error executing blue-green deployment for region {region} in mission {mission_id}: {str(e)}")
                
                overall_success = False
                failures.append({
                    "region": region,
                    "error": str(e),
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                })
                
                # Update region status
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["region_statuses"][region] = RegionStatus.FAILED.value
                    mission["region_results"][region] = {
                        "success": False,
                        "error": str(e),
                        "details": {
                            "exception": str(e),
                            "traceback": logging.traceback.format_exc()
                        }
                    }
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Error executing blue-green deployment for region {region}: {str(e)}"
                    })
        
        # Compile overall execution results
        execution_results = {
            "overall_success": overall_success,
            "region_results": region_results,
            "failures": failures
        }
        
        return execution_results
    
    def _execute_blue_green_for_region(self, mission_id: str, region: str) -> Dict[str, Any]:
        """
        Execute blue-green deployment for a specific region.
        
        Args:
            mission_id: ID of the mission.
            region: Region to deploy to.
            
        Returns:
            Dict containing the execution results.
        """
        logger.info(f"Executing blue-green deployment for region {region} in mission {mission_id}")
        
        # Get mission details
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            region_plan = mission["region_plans"][region]
        
        try:
            # Step 1: Deploy to green environment
            logger.info(f"Deploying to green environment for region {region} in mission {mission_id}")
            
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Deploying to green environment for region {region}"
                })
            
            # Modify region plan for green environment
            green_plan = region_plan.copy()
            green_plan["environment"] = "green"
            
            # Execute deployment to green environment
            green_result = self.region_orchestrators[region].execute_deployment(
                green_plan,
                timeout=self.config["deployment"]["timeout_seconds"]
            )
            
            # Check if green deployment was successful
            if not green_result["success"]:
                logger.error(f"Deployment to green environment failed for region {region} in mission {mission_id}")
                
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Deployment to green environment failed for region {region}"
                    })
                
                return {
                    "success": False,
                    "error": "GREEN_DEPLOYMENT_FAILED",
                    "details": green_result["failures"]
                }
            
            # Step 2: Check health of green environment
            logger.info(f"Checking health of green environment for region {region} in mission {mission_id}")
            
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Checking health of green environment for region {region}"
                })
            
            # Check health of green environment
            green_health = self._check_environment_health(mission_id, region, "green")
            
            if not green_health["healthy"]:
                logger.error(f"Health check failed for green environment in region {region} in mission {mission_id}")
                
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Health check failed for green environment in region {region}: {green_health['reason']}"
                    })
                
                return {
                    "success": False,
                    "error": "GREEN_HEALTH_CHECK_FAILED",
                    "details": green_health["details"]
                }
            
            # Step 3: Switch traffic to green environment
            logger.info(f"Switching traffic to green environment for region {region} in mission {mission_id}")
            
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Switching traffic to green environment for region {region}"
                })
            
            # Switch traffic to green environment
            switch_result = self._switch_environment(mission_id, region, "green")
            
            if not switch_result["success"]:
                logger.error(f"Failed to switch traffic to green environment in region {region} in mission {mission_id}")
                
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Failed to switch traffic to green environment in region {region}: {switch_result['error']}"
                    })
                
                return {
                    "success": False,
                    "error": "TRAFFIC_SWITCH_FAILED",
                    "details": switch_result["details"]
                }
            
            # Step 4: Verify green environment after switch
            logger.info(f"Verifying green environment after switch for region {region} in mission {mission_id}")
            
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Verifying green environment after switch for region {region}"
                })
            
            # Verify green environment after switch
            verification_result = self._verify_environment_after_switch(mission_id, region, "green")
            
            if not verification_result["success"]:
                logger.error(f"Verification failed for green environment after switch in region {region} in mission {mission_id}")
                
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Verification failed for green environment after switch in region {region}: {verification_result['error']}"
                    })
                
                # Rollback to blue environment
                logger.info(f"Rolling back to blue environment for region {region} in mission {mission_id}")
                
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": f"Rolling back to blue environment for region {region}"
                    })
                
                rollback_result = self._switch_environment(mission_id, region, "blue")
                
                if not rollback_result["success"]:
                    logger.error(f"Failed to rollback to blue environment in region {region} in mission {mission_id}")
                    
                    with self.deployment_lock:
                        mission = self.active_deployments[mission_id]
                        mission["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "ERROR",
                            "message": f"Failed to rollback to blue environment in region {region}: {rollback_result['error']}"
                        })
                
                return {
                    "success": False,
                    "error": "POST_SWITCH_VERIFICATION_FAILED",
                    "details": verification_result["details"]
                }
            
            # Step 5: Decommission blue environment
            logger.info(f"Decommissioning blue environment for region {region} in mission {mission_id}")
            
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Decommissioning blue environment for region {region}"
                })
            
            # Decommission blue environment
            decommission_result = self._decommission_environment(mission_id, region, "blue")
            
            if not decommission_result["success"]:
                logger.warning(f"Failed to decommission blue environment in region {region} in mission {mission_id}")
                
                with self.deployment_lock:
                    mission = self.active_deployments[mission_id]
                    mission["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "WARNING",
                        "message": f"Failed to decommission blue environment in region {region}: {decommission_result['error']}"
                    })
                
                # This is not a critical failure, so we still consider the deployment successful
            
            # Blue-green deployment for the region was successful
            logger.info(f"Blue-green deployment completed successfully for region {region} in mission {mission_id}")
            
            with self.deployment_lock:
                mission = self.active_deployments[mission_id]
                mission["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Blue-green deployment completed successfully for region {region}"
                })
            
            return {
                "success": True,
                "details": {
                    "green_deployment": green_result,
                    "green_health": green_health,
                    "switch": switch_result,
                    "verification": verification_result,
                    "decommission": decommission_result
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing blue-green deployment for region {region} in mission {mission_id}: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "details": {
                    "exception": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            }
    
    def _check_environment_health(self, mission_id: str, region: str, environment: str) -> Dict[str, Any]:
        """
        Check health of a specific environment in a region.
        
        Args:
            mission_id: ID of the mission.
            region: Region to check.
            environment: Environment to check (blue or green).
            
        Returns:
            Dict containing health check results.
        """
        logger.info(f"Checking health of {environment} environment in region {region} for mission {mission_id}")
        
        # Get mission details
        with self.deployment_lock:
            mission = self.active_deployments[mission_id]
            layers = mission["layers"]
        
        # Check health of each layer in the environment
        unhealthy_layers = []
        
        for layer in layers:
            try:
                # Get layer adapter for the region
                layer_adapter = self.layer_integration_manager.get_layer_adapter(layer, region)
                
                # Check layer health in the environment
                health_result = layer_adapter.check_environment_health(
                    environment=environment,
                    timeout=self.config["health_check"]["timeout_seconds"]
                )
                
                if not health_result["healthy"]:
                    unhealthy_layers.append({
                        "layer": layer,
                        "reason": health_result["reason"],
                        "details": health_result["details"]
                    })
            except Exception as e:
                logger.error(f"Error checking health of layer {layer} in {environment} environment in region {region}: {str(e)}")
                
                unhealthy_layers.append({
                    "layer": layer,
                    "reason": f"Health check error: {str(e)}",
                    "details": {
                        "exception": str(e),
                        "traceback": logging.traceback.format_exc()
                    }
                })
        
        # Determine overall health
        if unhealthy_layers:
            return {
                "healthy": False,
                "reason": f"{len(unhealthy_layers)} layers are unhealthy in {environment} environment in region {region}",
                "details": unhealthy_layers
            }
        else:
            return {
                "healthy": True,
                "reason": f"All layers are healthy in {environment} environment in region {region}",
                "details": {}
            }
    
    def _switch_environment(self, mission_id: str, region: str, target_environment: str) -> Dict[str, Any]:
        """
        Switch traffic to a specific environment in a region.
        
        Args:
            mission_id: ID of the mission.
            region: Region to switch.
            target_environment: Target environment to switch to (blue or green).
            
        Returns:
            Dict containing switch results.
        """
        logger.info(f"Switching traffic to {target_environment} environment in region {region} for mission {mission_id}")
        
        try:
            # Get region orchestrator
            region_orchestrator = self.region_orchestrators[region]
            
            # Switch traffic to target environment
            switch_result = region_orchestrator.switch_environment(
                target_environment=target_environment,
                timeout=self.config["blue_green"]["switch_timeout_seconds"]
            )
            
            return switch_result
            
        except Exception as e:
            logger.error(f"Error switching traffic to {target_environment} environment in region {region}: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "details": {
                    "exception": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            }
    
    def _verify_environment_after_switch(self, mission_id: str, region: str, environment: str) -> Dict[str, Any]:
        """
        Verify environment after traffic switch.
        
        Args:
            mission_id: ID of the mission.
            region: Region to verify.
            environment: Environment to verify (blue or green).
            
        Returns:
            Dict containing verification results.
        """
        logger.info(f"Verifying {environment} environment after switch in region {region} for mission {mission_id}")
        
        try:
            # Get region orchestrator
            region_orchestrator = self.region_orchestrators[region]
            
            # Verify environment after switch
            verification_result = region_orchestrator.verify_environment_after_switch(
                environment=environment,
                timeout=self.config["health_check"]["timeout_seconds"]
            )
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Error verifying {environment} environment after switch in region {region}: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "details": {
                    "exception": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            }
    
    def _decommission_environment(self, mission_id: str, region: str, environment: str) -> Dict[str, Any]:
        """
        Decommission a specific environment in a region.
        
        Args:
            mission_id: ID of the mission.
            region: Region to decommission.
            environment: Environment to decommission (blue or green).
            
        Returns:
            Dict containing decommission results.
        """
        logger.info(f"Decommissioning {environment} environment in region {region} for mission {mission_id}")
        
        try:
            # Get region orchestrator
            region_orchestrator = self.region_orchestrators[region]
            
            # Decommission environment
            decommission_result = region_orchestrator.decommission_environment(
                environment=environment,
                timeout=self.config["deployment"]["timeout_seconds"]
            )
            
            return decommission_result
            
        except Exception as e:
            logger.error(f"Error decommissioning {environment} environment in region {region}: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "details": {
                    "exception": str(e),
                    "traceback": logging.traceback.format_exc()
                }
            }
    
    def get_mission_details(self, mission_id: str) -> Dict[str, Any]:
        """
        Get details for a multi-region deployment mission.
        
        Args:
            mission_id: ID of the mission.
            
        Returns:
            Dict containing the mission details.
        """
        logger.info(f"Getting details for multi-region mission: {mission_id}")
        
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
        Get all active multi-region deployment missions.
        
        Returns:
            List of dicts containing mission details.
        """
        logger.info("Getting all active multi-region missions")
        
        with self.deployment_lock:
            return list(self.active_deployments.values())
    
    def get_mission_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get multi-region deployment mission history.
        
        Args:
            limit: Maximum number of missions to return.
            
        Returns:
            List of dicts containing mission details.
        """
        logger.info(f"Getting multi-region mission history with limit: {limit}")
        
        # Sort history by creation time (newest first)
        sorted_history = sorted(
            self.deployment_history,
            key=lambda x: x["created_at"],
            reverse=True
        )
        
        return sorted_history[:limit]
