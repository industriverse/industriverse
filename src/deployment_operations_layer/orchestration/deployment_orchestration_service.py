"""
Deployment Orchestration Service for the Deployment Operations Layer

This module provides comprehensive orchestration capabilities for executing
deployments across all Industriverse layers. It coordinates the deployment
process, manages dependencies between layers, and ensures successful execution
of deployment missions.

The orchestration service integrates with layer execution adapters, monitoring
services, and analytics to provide a complete deployment lifecycle management
solution.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

from ..execution.layer_execution_adapter import create_layer_execution_adapter
from ..monitoring.runtime_monitoring_service import get_runtime_monitoring_service
from ..analytics.analytics_manager import AnalyticsManager
from ..agent.agent_utils import AgentUtils
from ..security.security_framework_manager import SecurityFrameworkManager
from ..simulation.simulation_engine import SimulationEngine
from ..journal.deployment_journal import DeploymentJournal

# Configure logging
logger = logging.getLogger(__name__)

class DeploymentOrchestrationService:
    """Deployment orchestration service for coordinating deployments across layers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the deployment orchestration service
        
        Args:
            config: Configuration for the orchestration service
        """
        self.config = config
        self.analytics_manager = AnalyticsManager()
        self.agent_utils = AgentUtils()
        self.security_manager = SecurityFrameworkManager()
        self.simulation_engine = SimulationEngine()
        self.deployment_journal = DeploymentJournal()
        self.monitoring_service = get_runtime_monitoring_service()
        
        # Initialize layer adapters for deployment
        self.layer_adapters = {}
        for layer_name, layer_config in config.get("layers", {}).items():
            self.layer_adapters[layer_name] = create_layer_execution_adapter(
                layer_name, layer_config
            )
        
        # Initialize deployment state
        self.active_missions = {}
        self.mission_history = {}
        self.status = "initialized"
        
        logger.info("Initialized deployment orchestration service")
    
    async def start_mission(self, mission_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a new deployment mission
        
        Args:
            mission_spec: Deployment mission specification
            
        Returns:
            Dict containing mission start results
        """
        # Generate mission ID
        mission_id = self.agent_utils.generate_id()
        
        logger.info(f"Starting deployment mission {mission_id}")
        
        # Validate mission specification
        validation_result = await self._validate_mission_spec(mission_spec)
        if validation_result.get("status") != "valid":
            logger.error(f"Mission validation failed: {validation_result.get('error')}")
            return {
                "status": "error",
                "error": f"Mission validation failed: {validation_result.get('error')}",
                "mission_id": mission_id
            }
        
        # Create mission record
        mission_record = {
            "mission_id": mission_id,
            "spec": mission_spec,
            "status": "preparing",
            "created_at": self.agent_utils.get_current_timestamp(),
            "updated_at": self.agent_utils.get_current_timestamp(),
            "layers": {},
            "dependencies": mission_spec.get("dependencies", {}),
            "simulation_results": None,
            "execution_results": {},
            "errors": []
        }
        
        # Store mission record
        self.active_missions[mission_id] = mission_record
        
        # Record mission start in journal
        await self.deployment_journal.record_event(
            event_type="mission_started",
            event_data={
                "mission_id": mission_id,
                "spec": mission_spec
            }
        )
        
        # Run simulation if required
        if mission_spec.get("simulate", True):
            logger.info(f"Running simulation for mission {mission_id}")
            mission_record["status"] = "simulating"
            mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
            
            simulation_result = await self.simulation_engine.run_simulation(mission_spec)
            mission_record["simulation_results"] = simulation_result
            
            if simulation_result.get("status") != "success":
                logger.error(f"Simulation failed for mission {mission_id}: {simulation_result.get('error')}")
                mission_record["status"] = "simulation_failed"
                mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
                mission_record["errors"].append({
                    "phase": "simulation",
                    "error": simulation_result.get("error"),
                    "timestamp": self.agent_utils.get_current_timestamp()
                })
                
                # Record simulation failure in journal
                await self.deployment_journal.record_event(
                    event_type="simulation_failed",
                    event_data={
                        "mission_id": mission_id,
                        "error": simulation_result.get("error")
                    }
                )
                
                return {
                    "status": "simulation_failed",
                    "mission_id": mission_id,
                    "error": simulation_result.get("error")
                }
            
            logger.info(f"Simulation successful for mission {mission_id}")
            
            # Record simulation success in journal
            await self.deployment_journal.record_event(
                event_type="simulation_succeeded",
                event_data={
                    "mission_id": mission_id,
                    "results": simulation_result
                }
            )
        
        # Start execution
        logger.info(f"Starting execution for mission {mission_id}")
        mission_record["status"] = "executing"
        mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
        
        # Execute deployment asynchronously
        asyncio.create_task(self._execute_mission(mission_id))
        
        return {
            "status": "started",
            "mission_id": mission_id,
            "simulation_results": mission_record.get("simulation_results")
        }
    
    async def _execute_mission(self, mission_id: str):
        """
        Execute a deployment mission
        
        Args:
            mission_id: ID of the mission to execute
        """
        if mission_id not in self.active_missions:
            logger.error(f"Mission {mission_id} not found")
            return
        
        mission_record = self.active_missions[mission_id]
        mission_spec = mission_record["spec"]
        
        logger.info(f"Executing mission {mission_id}")
        
        # Record execution start in journal
        await self.deployment_journal.record_event(
            event_type="execution_started",
            event_data={
                "mission_id": mission_id
            }
        )
        
        try:
            # Determine layer execution order based on dependencies
            execution_order = await self._determine_execution_order(mission_spec)
            
            # Execute layers in order
            for layer_name in execution_order:
                if layer_name not in mission_spec.get("layers", {}):
                    continue
                
                layer_spec = mission_spec["layers"][layer_name]
                
                logger.info(f"Executing layer {layer_name} for mission {mission_id}")
                mission_record["layers"][layer_name] = {
                    "status": "executing",
                    "started_at": self.agent_utils.get_current_timestamp()
                }
                
                # Record layer execution start in journal
                await self.deployment_journal.record_event(
                    event_type="layer_execution_started",
                    event_data={
                        "mission_id": mission_id,
                        "layer": layer_name
                    }
                )
                
                # Execute layer deployment
                try:
                    if layer_name in self.layer_adapters:
                        layer_result = await self.layer_adapters[layer_name].execute_deployment(
                            mission_id, layer_spec
                        )
                    else:
                        raise ValueError(f"No adapter available for layer {layer_name}")
                    
                    mission_record["layers"][layer_name]["status"] = layer_result.get("status", "unknown")
                    mission_record["layers"][layer_name]["completed_at"] = self.agent_utils.get_current_timestamp()
                    mission_record["layers"][layer_name]["result"] = layer_result
                    mission_record["execution_results"][layer_name] = layer_result
                    
                    # Record layer execution result in journal
                    await self.deployment_journal.record_event(
                        event_type="layer_execution_completed",
                        event_data={
                            "mission_id": mission_id,
                            "layer": layer_name,
                            "status": layer_result.get("status"),
                            "result": layer_result
                        }
                    )
                    
                    if layer_result.get("status") != "success":
                        logger.error(f"Layer {layer_name} execution failed for mission {mission_id}: {layer_result.get('error')}")
                        mission_record["errors"].append({
                            "phase": "execution",
                            "layer": layer_name,
                            "error": layer_result.get("error"),
                            "timestamp": self.agent_utils.get_current_timestamp()
                        })
                        
                        # Handle layer failure based on mission policy
                        if mission_spec.get("failure_policy", "stop") == "stop":
                            logger.info(f"Stopping mission {mission_id} due to layer {layer_name} failure")
                            mission_record["status"] = "failed"
                            mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
                            
                            # Record mission failure in journal
                            await self.deployment_journal.record_event(
                                event_type="mission_failed",
                                event_data={
                                    "mission_id": mission_id,
                                    "layer": layer_name,
                                    "error": layer_result.get("error")
                                }
                            )
                            
                            return
                        else:
                            logger.info(f"Continuing mission {mission_id} despite layer {layer_name} failure")
                except Exception as e:
                    logger.error(f"Error executing layer {layer_name} for mission {mission_id}: {str(e)}")
                    mission_record["layers"][layer_name]["status"] = "error"
                    mission_record["layers"][layer_name]["completed_at"] = self.agent_utils.get_current_timestamp()
                    mission_record["layers"][layer_name]["error"] = str(e)
                    mission_record["errors"].append({
                        "phase": "execution",
                        "layer": layer_name,
                        "error": str(e),
                        "timestamp": self.agent_utils.get_current_timestamp()
                    })
                    
                    # Record layer execution error in journal
                    await self.deployment_journal.record_event(
                        event_type="layer_execution_error",
                        event_data={
                            "mission_id": mission_id,
                            "layer": layer_name,
                            "error": str(e)
                        }
                    )
                    
                    # Handle layer failure based on mission policy
                    if mission_spec.get("failure_policy", "stop") == "stop":
                        logger.info(f"Stopping mission {mission_id} due to layer {layer_name} failure")
                        mission_record["status"] = "failed"
                        mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
                        
                        # Record mission failure in journal
                        await self.deployment_journal.record_event(
                            event_type="mission_failed",
                            event_data={
                                "mission_id": mission_id,
                                "layer": layer_name,
                                "error": str(e)
                            }
                        )
                        
                        return
                    else:
                        logger.info(f"Continuing mission {mission_id} despite layer {layer_name} failure")
            
            # Check if all layers were successful
            all_successful = True
            for layer_name, layer_status in mission_record["layers"].items():
                if layer_status.get("status") != "success":
                    all_successful = False
                    break
            
            if all_successful:
                mission_record["status"] = "completed"
            else:
                mission_record["status"] = "completed_with_errors"
            
            mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
            mission_record["completed_at"] = self.agent_utils.get_current_timestamp()
            
            # Record mission completion in journal
            await self.deployment_journal.record_event(
                event_type="mission_completed",
                event_data={
                    "mission_id": mission_id,
                    "status": mission_record["status"],
                    "results": mission_record["execution_results"]
                }
            )
            
            logger.info(f"Mission {mission_id} {mission_record['status']}")
        except Exception as e:
            logger.error(f"Error executing mission {mission_id}: {str(e)}")
            mission_record["status"] = "failed"
            mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
            mission_record["errors"].append({
                "phase": "execution",
                "error": str(e),
                "timestamp": self.agent_utils.get_current_timestamp()
            })
            
            # Record mission failure in journal
            await self.deployment_journal.record_event(
                event_type="mission_failed",
                event_data={
                    "mission_id": mission_id,
                    "error": str(e)
                }
            )
        
        # Move mission from active to history
        self.mission_history[mission_id] = mission_record
        if mission_id in self.active_missions:
            del self.active_missions[mission_id]
    
    async def _validate_mission_spec(self, mission_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a mission specification
        
        Args:
            mission_spec: Mission specification to validate
            
        Returns:
            Dict containing validation results
        """
        # Check required fields
        if "layers" not in mission_spec:
            return {
                "status": "invalid",
                "error": "Mission specification must include 'layers'"
            }
        
        # Validate each layer specification
        for layer_name, layer_spec in mission_spec.get("layers", {}).items():
            if layer_name not in self.layer_adapters:
                return {
                    "status": "invalid",
                    "error": f"Unknown layer: {layer_name}"
                }
            
            # Additional layer-specific validation could be added here
        
        # Validate dependencies
        dependencies = mission_spec.get("dependencies", {})
        for layer_name, layer_deps in dependencies.items():
            if layer_name not in mission_spec.get("layers", {}):
                return {
                    "status": "invalid",
                    "error": f"Dependency specified for non-existent layer: {layer_name}"
                }
            
            for dep_layer in layer_deps:
                if dep_layer not in mission_spec.get("layers", {}):
                    return {
                        "status": "invalid",
                        "error": f"Layer {layer_name} depends on non-existent layer: {dep_layer}"
                    }
        
        # Check for circular dependencies
        try:
            await self._determine_execution_order(mission_spec)
        except ValueError as e:
            return {
                "status": "invalid",
                "error": f"Invalid dependencies: {str(e)}"
            }
        
        return {
            "status": "valid"
        }
    
    async def _determine_execution_order(self, mission_spec: Dict[str, Any]) -> List[str]:
        """
        Determine the execution order of layers based on dependencies
        
        Args:
            mission_spec: Mission specification
            
        Returns:
            List of layer names in execution order
            
        Raises:
            ValueError: If circular dependencies are detected
        """
        layers = list(mission_spec.get("layers", {}).keys())
        dependencies = mission_spec.get("dependencies", {})
        
        # Build dependency graph
        graph = {layer: set(dependencies.get(layer, [])) for layer in layers}
        
        # Topological sort
        result = []
        temp_marked = set()
        unmarked = set(layers)
        
        def visit(node):
            if node in temp_marked:
                raise ValueError(f"Circular dependency detected involving layer: {node}")
            
            if node in unmarked:
                temp_marked.add(node)
                for dep in graph.get(node, set()):
                    visit(dep)
                
                temp_marked.remove(node)
                unmarked.remove(node)
                result.append(node)
        
        while unmarked:
            visit(next(iter(unmarked)))
        
        # Reverse the result to get the correct execution order
        result.reverse()
        
        return result
    
    async def get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """
        Get the status of a deployment mission
        
        Args:
            mission_id: ID of the mission
            
        Returns:
            Dict containing mission status
        """
        if mission_id in self.active_missions:
            mission_record = self.active_missions[mission_id]
        elif mission_id in self.mission_history:
            mission_record = self.mission_history[mission_id]
        else:
            return {
                "status": "not_found",
                "mission_id": mission_id
            }
        
        return {
            "mission_id": mission_id,
            "status": mission_record["status"],
            "created_at": mission_record["created_at"],
            "updated_at": mission_record["updated_at"],
            "completed_at": mission_record.get("completed_at"),
            "layers": {
                layer_name: {
                    "status": layer_data.get("status"),
                    "started_at": layer_data.get("started_at"),
                    "completed_at": layer_data.get("completed_at")
                }
                for layer_name, layer_data in mission_record.get("layers", {}).items()
            },
            "errors": mission_record.get("errors", [])
        }
    
    async def list_missions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List deployment missions
        
        Args:
            status: Filter by status, or None for all
            
        Returns:
            List of mission summaries
        """
        missions = []
        
        # Add active missions
        for mission_id, mission_record in self.active_missions.items():
            if status is None or mission_record["status"] == status:
                missions.append({
                    "mission_id": mission_id,
                    "status": mission_record["status"],
                    "created_at": mission_record["created_at"],
                    "updated_at": mission_record["updated_at"]
                })
        
        # Add historical missions
        for mission_id, mission_record in self.mission_history.items():
            if status is None or mission_record["status"] == status:
                missions.append({
                    "mission_id": mission_id,
                    "status": mission_record["status"],
                    "created_at": mission_record["created_at"],
                    "updated_at": mission_record["updated_at"],
                    "completed_at": mission_record.get("completed_at")
                })
        
        # Sort by creation time (newest first)
        missions.sort(key=lambda m: m["created_at"], reverse=True)
        
        return missions
    
    async def cancel_mission(self, mission_id: str) -> Dict[str, Any]:
        """
        Cancel a deployment mission
        
        Args:
            mission_id: ID of the mission to cancel
            
        Returns:
            Dict containing cancellation results
        """
        if mission_id not in self.active_missions:
            return {
                "status": "not_found",
                "mission_id": mission_id
            }
        
        mission_record = self.active_missions[mission_id]
        
        if mission_record["status"] in ["completed", "failed", "cancelled"]:
            return {
                "status": "invalid_state",
                "mission_id": mission_id,
                "current_status": mission_record["status"]
            }
        
        logger.info(f"Cancelling mission {mission_id}")
        
        mission_record["status"] = "cancelling"
        mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
        
        # Record cancellation in journal
        await self.deployment_journal.record_event(
            event_type="mission_cancelling",
            event_data={
                "mission_id": mission_id
            }
        )
        
        # Cancel ongoing layer executions
        # This would involve calling cancel methods on layer adapters
        # For simplicity, we're just marking the mission as cancelled
        
        mission_record["status"] = "cancelled"
        mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
        mission_record["completed_at"] = self.agent_utils.get_current_timestamp()
        
        # Move mission from active to history
        self.mission_history[mission_id] = mission_record
        del self.active_missions[mission_id]
        
        # Record cancellation completion in journal
        await self.deployment_journal.record_event(
            event_type="mission_cancelled",
            event_data={
                "mission_id": mission_id
            }
        )
        
        return {
            "status": "cancelled",
            "mission_id": mission_id
        }
    
    async def rollback_mission(self, mission_id: str) -> Dict[str, Any]:
        """
        Rollback a deployment mission
        
        Args:
            mission_id: ID of the mission to rollback
            
        Returns:
            Dict containing rollback results
        """
        if mission_id in self.active_missions:
            mission_record = self.active_missions[mission_id]
        elif mission_id in self.mission_history:
            mission_record = self.mission_history[mission_id]
        else:
            return {
                "status": "not_found",
                "mission_id": mission_id
            }
        
        if mission_record["status"] not in ["completed", "completed_with_errors", "failed"]:
            return {
                "status": "invalid_state",
                "mission_id": mission_id,
                "current_status": mission_record["status"]
            }
        
        logger.info(f"Rolling back mission {mission_id}")
        
        # Generate rollback mission ID
        rollback_mission_id = f"{mission_id}-rollback-{self.agent_utils.generate_id()}"
        
        # Create rollback mission record
        rollback_mission_record = {
            "mission_id": rollback_mission_id,
            "original_mission_id": mission_id,
            "status": "preparing",
            "created_at": self.agent_utils.get_current_timestamp(),
            "updated_at": self.agent_utils.get_current_timestamp(),
            "layers": {},
            "execution_results": {},
            "errors": []
        }
        
        # Store rollback mission record
        self.active_missions[rollback_mission_id] = rollback_mission_record
        
        # Record rollback start in journal
        await self.deployment_journal.record_event(
            event_type="rollback_started",
            event_data={
                "mission_id": rollback_mission_id,
                "original_mission_id": mission_id
            }
        )
        
        # Start rollback execution
        rollback_mission_record["status"] = "executing"
        rollback_mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
        
        # Execute rollback asynchronously
        asyncio.create_task(self._execute_rollback(rollback_mission_id, mission_id))
        
        return {
            "status": "started",
            "mission_id": rollback_mission_id,
            "original_mission_id": mission_id
        }
    
    async def _execute_rollback(self, rollback_mission_id: str, original_mission_id: str):
        """
        Execute a rollback mission
        
        Args:
            rollback_mission_id: ID of the rollback mission
            original_mission_id: ID of the original mission to rollback
        """
        if rollback_mission_id not in self.active_missions:
            logger.error(f"Rollback mission {rollback_mission_id} not found")
            return
        
        if original_mission_id in self.active_missions:
            original_mission_record = self.active_missions[original_mission_id]
        elif original_mission_id in self.mission_history:
            original_mission_record = self.mission_history[original_mission_id]
        else:
            logger.error(f"Original mission {original_mission_id} not found")
            return
        
        rollback_mission_record = self.active_missions[rollback_mission_id]
        
        logger.info(f"Executing rollback mission {rollback_mission_id} for original mission {original_mission_id}")
        
        try:
            # Determine layer rollback order (reverse of original execution order)
            original_layers = list(original_mission_record.get("layers", {}).keys())
            rollback_order = list(reversed(original_layers))
            
            # Execute layer rollbacks in order
            for layer_name in rollback_order:
                if layer_name not in original_mission_record.get("layers", {}):
                    continue
                
                original_layer_data = original_mission_record["layers"][layer_name]
                if original_layer_data.get("status") != "success":
                    logger.info(f"Skipping rollback for layer {layer_name} as it was not successfully deployed")
                    continue
                
                logger.info(f"Rolling back layer {layer_name} for mission {rollback_mission_id}")
                rollback_mission_record["layers"][layer_name] = {
                    "status": "executing",
                    "started_at": self.agent_utils.get_current_timestamp()
                }
                
                # Record layer rollback start in journal
                await self.deployment_journal.record_event(
                    event_type="layer_rollback_started",
                    event_data={
                        "mission_id": rollback_mission_id,
                        "original_mission_id": original_mission_id,
                        "layer": layer_name
                    }
                )
                
                # Execute layer rollback
                try:
                    if layer_name in self.layer_adapters:
                        deployment_id = original_layer_data.get("result", {}).get("deployment_id")
                        if not deployment_id:
                            raise ValueError(f"No deployment ID found for layer {layer_name}")
                        
                        layer_result = await self.layer_adapters[layer_name].rollback_deployment(
                            original_mission_id, deployment_id
                        )
                    else:
                        raise ValueError(f"No adapter available for layer {layer_name}")
                    
                    rollback_mission_record["layers"][layer_name]["status"] = layer_result.get("status", "unknown")
                    rollback_mission_record["layers"][layer_name]["completed_at"] = self.agent_utils.get_current_timestamp()
                    rollback_mission_record["layers"][layer_name]["result"] = layer_result
                    rollback_mission_record["execution_results"][layer_name] = layer_result
                    
                    # Record layer rollback result in journal
                    await self.deployment_journal.record_event(
                        event_type="layer_rollback_completed",
                        event_data={
                            "mission_id": rollback_mission_id,
                            "original_mission_id": original_mission_id,
                            "layer": layer_name,
                            "status": layer_result.get("status"),
                            "result": layer_result
                        }
                    )
                    
                    if layer_result.get("status") != "success":
                        logger.error(f"Layer {layer_name} rollback failed for mission {rollback_mission_id}: {layer_result.get('error')}")
                        rollback_mission_record["errors"].append({
                            "phase": "rollback",
                            "layer": layer_name,
                            "error": layer_result.get("error"),
                            "timestamp": self.agent_utils.get_current_timestamp()
                        })
                except Exception as e:
                    logger.error(f"Error rolling back layer {layer_name} for mission {rollback_mission_id}: {str(e)}")
                    rollback_mission_record["layers"][layer_name]["status"] = "error"
                    rollback_mission_record["layers"][layer_name]["completed_at"] = self.agent_utils.get_current_timestamp()
                    rollback_mission_record["layers"][layer_name]["error"] = str(e)
                    rollback_mission_record["errors"].append({
                        "phase": "rollback",
                        "layer": layer_name,
                        "error": str(e),
                        "timestamp": self.agent_utils.get_current_timestamp()
                    })
                    
                    # Record layer rollback error in journal
                    await self.deployment_journal.record_event(
                        event_type="layer_rollback_error",
                        event_data={
                            "mission_id": rollback_mission_id,
                            "original_mission_id": original_mission_id,
                            "layer": layer_name,
                            "error": str(e)
                        }
                    )
            
            # Check if all layers were successfully rolled back
            all_successful = True
            for layer_name, layer_status in rollback_mission_record["layers"].items():
                if layer_status.get("status") != "success":
                    all_successful = False
                    break
            
            if all_successful:
                rollback_mission_record["status"] = "completed"
            else:
                rollback_mission_record["status"] = "completed_with_errors"
            
            rollback_mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
            rollback_mission_record["completed_at"] = self.agent_utils.get_current_timestamp()
            
            # Record rollback completion in journal
            await self.deployment_journal.record_event(
                event_type="rollback_completed",
                event_data={
                    "mission_id": rollback_mission_id,
                    "original_mission_id": original_mission_id,
                    "status": rollback_mission_record["status"],
                    "results": rollback_mission_record["execution_results"]
                }
            )
            
            logger.info(f"Rollback mission {rollback_mission_id} {rollback_mission_record['status']}")
        except Exception as e:
            logger.error(f"Error executing rollback mission {rollback_mission_id}: {str(e)}")
            rollback_mission_record["status"] = "failed"
            rollback_mission_record["updated_at"] = self.agent_utils.get_current_timestamp()
            rollback_mission_record["errors"].append({
                "phase": "rollback",
                "error": str(e),
                "timestamp": self.agent_utils.get_current_timestamp()
            })
            
            # Record rollback failure in journal
            await self.deployment_journal.record_event(
                event_type="rollback_failed",
                event_data={
                    "mission_id": rollback_mission_id,
                    "original_mission_id": original_mission_id,
                    "error": str(e)
                }
            )
        
        # Move mission from active to history
        self.mission_history[rollback_mission_id] = rollback_mission_record
        if rollback_mission_id in self.active_missions:
            del self.active_missions[rollback_mission_id]
    
    async def cleanup(self):
        """Clean up resources used by the orchestration service"""
        # Clean up layer adapters
        for adapter in self.layer_adapters.values():
            await adapter.cleanup()
        
        logger.info("Cleaned up deployment orchestration service")


# Singleton instance
_instance = None

def get_deployment_orchestration_service(config: Optional[Dict[str, Any]] = None) -> DeploymentOrchestrationService:
    """
    Get the singleton instance of the deployment orchestration service
    
    Args:
        config: Configuration for the orchestration service (only used if creating a new instance)
        
    Returns:
        DeploymentOrchestrationService instance
    """
    global _instance
    
    if _instance is None:
        if config is None:
            config = {}
        
        _instance = DeploymentOrchestrationService(config)
    
    return _instance
