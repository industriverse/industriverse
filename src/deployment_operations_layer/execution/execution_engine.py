"""
Deployment Operations Layer Execution Engine

This module provides the core execution engine for the Deployment Operations Layer,
responsible for orchestrating and executing deployment missions across the Industriverse ecosystem.
"""

import os
import sys
import json
import logging
import uuid
import datetime
import time
import threading
import queue
import asyncio
import traceback
from typing import Dict, List, Optional, Any, Union, Callable, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('deployment_ops_execution_engine')

class MissionStatus:
    """Mission status constants"""
    PENDING = "pending"
    PLANNING = "planning"
    SIMULATING = "simulating"
    EXECUTING = "executing"
    PAUSED = "paused"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"

class MissionType:
    """Mission type constants"""
    DEPLOY = "deploy"
    UPDATE = "update"
    ROLLBACK = "rollback"
    SCALE = "scale"
    MIGRATE = "migrate"
    BACKUP = "backup"
    RESTORE = "restore"
    HEALTH_CHECK = "health_check"
    SECURITY_SCAN = "security_scan"
    COMPLIANCE_CHECK = "compliance_check"

class Mission:
    """
    Represents a deployment mission with all its metadata, configuration, and state.
    """
    def __init__(
        self,
        mission_id: str,
        mission_type: str,
        priority: int,
        target_layers: List[str],
        configuration: Dict[str, Any],
        simulation_required: bool = True,
        rollback_on_failure: bool = True,
        timeout_seconds: Optional[int] = None,
        description: Optional[str] = None
    ):
        self.mission_id = mission_id
        self.type = mission_type
        self.status = MissionStatus.PENDING
        self.priority = priority
        self.timestamp = datetime.datetime.utcnow().isoformat()
        self.engine_id = None
        self.target_layers = target_layers
        self.configuration = configuration
        self.simulation_required = simulation_required
        self.rollback_on_failure = rollback_on_failure
        self.timeout_seconds = timeout_seconds
        self.description = description
        
        # Timestamps
        self.planning_started_at = None
        self.planning_completed_at = None
        self.simulation_started_at = None
        self.simulation_completed_at = None
        self.execution_started_at = None
        self.execution_completed_at = None
        self.succeeded_at = None
        self.failed_at = None
        self.canceled_at = None
        self.paused_at = None
        self.resumed_at = None
        self.rollback_started_at = None
        self.rollback_completed_at = None
        
        # Results
        self.error = None
        self.plan_summary = None
        self.simulation_summary = None
        self.execution_summary = None
        self.timeline = []
        self.resources = {
            "cpu_usage": [],
            "memory_usage": [],
            "network_usage": []
        }
        self.capsules = []
        self.layers = []
        self.validation_results = {
            "resource_validation": [],
            "dependency_validation": [],
            "security_validation": []
        }
        
        # Add initial timeline event
        self.add_timeline_event("Mission created", "Mission created and queued for execution")
    
    def add_timeline_event(self, event: str, details: str, status: str = "info"):
        """Add an event to the mission timeline"""
        self.timeline.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event": event,
            "details": details,
            "status": status
        })
    
    def update_status(self, status: str):
        """Update the mission status and record the appropriate timestamp"""
        self.status = status
        
        if status == MissionStatus.PLANNING:
            self.planning_started_at = datetime.datetime.utcnow().isoformat()
            self.add_timeline_event("Planning started", "Mission planning phase initiated")
        elif status == MissionStatus.SIMULATING:
            self.simulation_started_at = datetime.datetime.utcnow().isoformat()
            self.add_timeline_event("Simulation started", "Pre-deployment simulation initiated")
        elif status == MissionStatus.EXECUTING:
            self.execution_started_at = datetime.datetime.utcnow().isoformat()
            self.add_timeline_event("Execution started", "Deployment execution initiated")
        elif status == MissionStatus.PAUSED:
            self.paused_at = datetime.datetime.utcnow().isoformat()
            self.add_timeline_event("Mission paused", "Mission execution paused", "warning")
        elif status == MissionStatus.SUCCEEDED:
            self.succeeded_at = datetime.datetime.utcnow().isoformat()
            self.add_timeline_event("Mission succeeded", "All deployment operations completed successfully", "success")
        elif status == MissionStatus.FAILED:
            self.failed_at = datetime.datetime.utcnow().isoformat()
            self.add_timeline_event("Mission failed", f"Mission failed: {self.error}", "error")
        elif status == MissionStatus.CANCELED:
            self.canceled_at = datetime.datetime.utcnow().isoformat()
            self.add_timeline_event("Mission canceled", "Mission was canceled by user", "warning")
        elif status == MissionStatus.ROLLING_BACK:
            self.rollback_started_at = datetime.datetime.utcnow().isoformat()
            self.add_timeline_event("Rollback started", "Rolling back deployment changes", "warning")
        elif status == MissionStatus.ROLLED_BACK:
            self.rollback_completed_at = datetime.datetime.utcnow().isoformat()
            self.add_timeline_event("Rollback completed", "Deployment changes successfully rolled back", "warning")
    
    def complete_planning(self, plan_summary: str):
        """Mark planning as completed and record the summary"""
        self.planning_completed_at = datetime.datetime.utcnow().isoformat()
        self.plan_summary = plan_summary
        self.add_timeline_event("Planning completed", "Mission plan generated successfully", "success")
    
    def complete_simulation(self, simulation_summary: str, validation_results: Dict[str, List[Dict[str, Any]]]):
        """Mark simulation as completed and record the results"""
        self.simulation_completed_at = datetime.datetime.utcnow().isoformat()
        self.simulation_summary = simulation_summary
        self.validation_results = validation_results
        self.add_timeline_event("Simulation completed", "Simulation completed successfully with no issues detected", "success")
    
    def complete_execution(self, execution_summary: str):
        """Mark execution as completed and record the summary"""
        self.execution_completed_at = datetime.datetime.utcnow().isoformat()
        self.execution_summary = execution_summary
        self.add_timeline_event("Execution completed", "All deployment operations completed", "success")
    
    def fail(self, error: str):
        """Mark the mission as failed with the given error"""
        self.error = error
        self.update_status(MissionStatus.FAILED)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the mission to a dictionary representation"""
        return {
            "mission_id": self.mission_id,
            "type": self.type,
            "status": self.status,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "engine_id": self.engine_id,
            "target_layers": self.target_layers,
            "configuration": self.configuration,
            "simulation_required": self.simulation_required,
            "rollback_on_failure": self.rollback_on_failure,
            "timeout_seconds": self.timeout_seconds,
            "description": self.description,
            "planning_started_at": self.planning_started_at,
            "planning_completed_at": self.planning_completed_at,
            "simulation_started_at": self.simulation_started_at,
            "simulation_completed_at": self.simulation_completed_at,
            "execution_started_at": self.execution_started_at,
            "execution_completed_at": self.execution_completed_at,
            "succeeded_at": self.succeeded_at,
            "failed_at": self.failed_at,
            "canceled_at": self.canceled_at,
            "paused_at": self.paused_at,
            "resumed_at": self.resumed_at,
            "rollback_started_at": self.rollback_started_at,
            "rollback_completed_at": self.rollback_completed_at,
            "error": self.error,
            "plan_summary": self.plan_summary,
            "simulation_summary": self.simulation_summary,
            "execution_summary": self.execution_summary,
            "timeline": self.timeline,
            "resources": self.resources,
            "capsules": self.capsules,
            "layers": self.layers,
            "validation_results": self.validation_results
        }

class Worker(threading.Thread):
    """
    Worker thread for executing missions.
    """
    def __init__(
        self,
        worker_id: str,
        mission_queue: queue.PriorityQueue,
        mission_planner,
        simulation_engine,
        mission_executor,
        error_handler,
        recovery_manager,
        mission_store,
        event_bus
    ):
        super().__init__()
        self.worker_id = worker_id
        self.mission_queue = mission_queue
        self.mission_planner = mission_planner
        self.simulation_engine = simulation_engine
        self.mission_executor = mission_executor
        self.error_handler = error_handler
        self.recovery_manager = recovery_manager
        self.mission_store = mission_store
        self.event_bus = event_bus
        self.running = True
        self.active = False
        self.current_mission = None
        self.daemon = True
    
    def run(self):
        """Main worker loop"""
        logger.info(f"Worker {self.worker_id} started")
        
        while self.running:
            try:
                # Get a mission from the queue
                priority, mission = self.mission_queue.get(block=True, timeout=1.0)
                self.active = True
                self.current_mission = mission
                
                # Process the mission
                self._process_mission(mission)
                
                # Mark the mission as done in the queue
                self.mission_queue.task_done()
                
                # Reset worker state
                self.active = False
                self.current_mission = None
            
            except queue.Empty:
                # No missions in the queue, continue waiting
                pass
            
            except Exception as e:
                logger.error(f"Worker {self.worker_id} encountered an error: {str(e)}")
                logger.error(traceback.format_exc())
                
                # If we have a current mission, mark it as failed
                if self.current_mission:
                    self.current_mission.fail(f"Worker error: {str(e)}")
                    self.mission_store.update_mission(self.current_mission)
                    self.event_bus.publish("mission.failed", self.current_mission)
                
                # Reset worker state
                self.active = False
                self.current_mission = None
        
        logger.info(f"Worker {self.worker_id} stopped")
    
    def _process_mission(self, mission: Mission):
        """Process a mission through all its phases"""
        logger.info(f"Worker {self.worker_id} processing mission {mission.mission_id}")
        
        # Set the engine ID
        mission.engine_id = self.worker_id
        
        try:
            # Planning phase
            mission.update_status(MissionStatus.PLANNING)
            self.mission_store.update_mission(mission)
            self.event_bus.publish("mission.planning", mission)
            
            plan_result = self.mission_planner.plan_mission(mission)
            if not plan_result["success"]:
                mission.fail(plan_result["error"])
                self.mission_store.update_mission(mission)
                self.event_bus.publish("mission.failed", mission)
                return
            
            mission.complete_planning(plan_result["summary"])
            self.mission_store.update_mission(mission)
            self.event_bus.publish("mission.planned", mission)
            
            # Simulation phase (if required)
            if mission.simulation_required:
                mission.update_status(MissionStatus.SIMULATING)
                self.mission_store.update_mission(mission)
                self.event_bus.publish("mission.simulating", mission)
                
                sim_result = self.simulation_engine.simulate_mission(mission)
                if not sim_result["success"]:
                    mission.fail(sim_result["error"])
                    self.mission_store.update_mission(mission)
                    self.event_bus.publish("mission.failed", mission)
                    return
                
                mission.complete_simulation(sim_result["summary"], sim_result["validation_results"])
                mission.capsules = sim_result.get("capsules", [])
                mission.layers = sim_result.get("layers", [])
                self.mission_store.update_mission(mission)
                self.event_bus.publish("mission.simulated", mission)
            
            # Execution phase
            mission.update_status(MissionStatus.EXECUTING)
            self.mission_store.update_mission(mission)
            self.event_bus.publish("mission.executing", mission)
            
            exec_result = self.mission_executor.execute_mission(mission)
            if not exec_result["success"]:
                error_msg = exec_result["error"]
                mission.add_timeline_event("Execution failed", f"Deployment execution failed: {error_msg}", "error")
                
                # Handle rollback if enabled
                if mission.rollback_on_failure:
                    mission.update_status(MissionStatus.ROLLING_BACK)
                    self.mission_store.update_mission(mission)
                    self.event_bus.publish("mission.rolling_back", mission)
                    
                    rollback_result = self.recovery_manager.rollback_mission(mission)
                    if rollback_result["success"]:
                        mission.update_status(MissionStatus.ROLLED_BACK)
                        self.mission_store.update_mission(mission)
                        self.event_bus.publish("mission.rolled_back", mission)
                    else:
                        rollback_error = rollback_result["error"]
                        mission.add_timeline_event(
                            "Rollback failed", 
                            f"Failed to rollback deployment: {rollback_error}", 
                            "error"
                        )
                
                mission.fail(error_msg)
                self.mission_store.update_mission(mission)
                self.event_bus.publish("mission.failed", mission)
                return
            
            # Mission succeeded
            mission.complete_execution(exec_result["summary"])
            mission.capsules = exec_result.get("capsules", mission.capsules)
            mission.layers = exec_result.get("layers", mission.layers)
            mission.update_status(MissionStatus.SUCCEEDED)
            self.mission_store.update_mission(mission)
            self.event_bus.publish("mission.succeeded", mission)
        
        except Exception as e:
            logger.error(f"Error processing mission {mission.mission_id}: {str(e)}")
            logger.error(traceback.format_exc())
            
            error_info = self.error_handler.handle_error(mission, e)
            mission.fail(error_info["error_message"])
            self.mission_store.update_mission(mission)
            self.event_bus.publish("mission.failed", mission)
    
    def stop(self):
        """Stop the worker"""
        self.running = False

class EventBus:
    """
    Simple event bus for publishing and subscribing to events.
    """
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
    
    def publish(self, event_type: str, data: Any):
        """Publish an event"""
        if event_type not in self.subscribers:
            return
        
        for callback in self.subscribers[event_type]:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in event subscriber for {event_type}: {str(e)}")

class MissionStore:
    """
    Storage for missions.
    """
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "missions")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.missions = {}
        self._load_missions()
    
    def _load_missions(self):
        """Load missions from storage"""
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.storage_dir, filename), "r") as f:
                        mission_data = json.load(f)
                        self.missions[mission_data["mission_id"]] = mission_data
                except Exception as e:
                    logger.error(f"Error loading mission from {filename}: {str(e)}")
    
    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get a mission by ID"""
        return self.missions.get(mission_id)
    
    def get_missions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all missions, optionally filtered by status"""
        if status:
            return [m for m in self.missions.values() if m["status"] == status]
        return list(self.missions.values())
    
    def create_mission(self, mission: Mission) -> str:
        """Create a new mission"""
        mission_dict = mission.to_dict()
        self.missions[mission.mission_id] = mission_dict
        
        # Save to storage
        with open(os.path.join(self.storage_dir, f"{mission.mission_id}.json"), "w") as f:
            json.dump(mission_dict, f, indent=2)
        
        return mission.mission_id
    
    def update_mission(self, mission: Mission):
        """Update an existing mission"""
        mission_dict = mission.to_dict()
        self.missions[mission.mission_id] = mission_dict
        
        # Save to storage
        with open(os.path.join(self.storage_dir, f"{mission.mission_id}.json"), "w") as f:
            json.dump(mission_dict, f, indent=2)
    
    def delete_mission(self, mission_id: str):
        """Delete a mission"""
        if mission_id in self.missions:
            del self.missions[mission_id]
            
            # Remove from storage
            try:
                os.remove(os.path.join(self.storage_dir, f"{mission_id}.json"))
            except Exception as e:
                logger.error(f"Error deleting mission file for {mission_id}: {str(e)}")

class ExecutionEngine:
    """
    Main execution engine for the Deployment Operations Layer.
    """
    def __init__(
        self,
        mission_planner,
        simulation_engine,
        mission_executor,
        error_handler,
        recovery_manager,
        worker_count: int = 5
    ):
        self.engine_id = f"engine-{str(uuid.uuid4())[:8]}"
        self.mission_planner = mission_planner
        self.simulation_engine = simulation_engine
        self.mission_executor = mission_executor
        self.error_handler = error_handler
        self.recovery_manager = recovery_manager
        self.worker_count = worker_count
        
        self.mission_queue = queue.PriorityQueue()
        self.mission_store = MissionStore()
        self.event_bus = EventBus()
        
        self.workers = []
        self.running = False
        self.start_time = None
    
    def start(self):
        """Start the execution engine"""
        if self.running:
            logger.warning("Execution engine is already running")
            return
        
        logger.info(f"Starting execution engine {self.engine_id}")
        self.running = True
        self.start_time = time.time()
        
        # Start workers
        for i in range(self.worker_count):
            worker_id = f"worker-{i+1}"
            worker = Worker(
                worker_id,
                self.mission_queue,
                self.mission_planner,
                self.simulation_engine,
                self.mission_executor,
                self.error_handler,
                self.recovery_manager,
                self.mission_store,
                self.event_bus
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Execution engine {self.engine_id} started with {self.worker_count} workers")
    
    def stop(self):
        """Stop the execution engine"""
        if not self.running:
            logger.warning("Execution engine is not running")
            return
        
        logger.info(f"Stopping execution engine {self.engine_id}")
        self.running = False
        
        # Stop workers
        for worker in self.workers:
            worker.stop()
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        self.workers = []
        self.start_time = None
        
        logger.info(f"Execution engine {self.engine_id} stopped")
    
    def submit_mission(self, mission: Mission) -> str:
        """Submit a mission for execution"""
        if not self.running:
            raise RuntimeError("Execution engine is not running")
        
        # Store the mission
        self.mission_store.create_mission(mission)
        
        # Add to queue
        self.mission_queue.put((mission.priority, mission))
        
        # Publish event
        self.event_bus.publish("mission.submitted", mission)
        
        logger.info(f"Mission {mission.mission_id} submitted for execution")
        return mission.mission_id
    
    def cancel_mission(self, mission_id: str) -> bool:
        """Cancel a mission"""
        mission_data = self.mission_store.get_mission(mission_id)
        if not mission_data:
            logger.warning(f"Mission {mission_id} not found")
            return False
        
        # Check if mission can be canceled
        status = mission_data["status"]
        if status not in [MissionStatus.PENDING, MissionStatus.PLANNING, MissionStatus.SIMULATING, MissionStatus.EXECUTING, MissionStatus.PAUSED]:
            logger.warning(f"Mission {mission_id} cannot be canceled in state {status}")
            return False
        
        # Find the worker handling this mission
        target_worker = None
        for worker in self.workers:
            if worker.current_mission and worker.current_mission.mission_id == mission_id:
                target_worker = worker
                break
        
        if target_worker:
            # Mission is being processed by a worker
            # In a real implementation, we would need a way to signal the worker to cancel the mission
            # For now, we'll just update the mission status
            mission = Mission(
                mission_id=mission_data["mission_id"],
                mission_type=mission_data["type"],
                priority=mission_data["priority"],
                target_layers=mission_data["target_layers"],
                configuration=mission_data["configuration"],
                simulation_required=mission_data["simulation_required"],
                rollback_on_failure=mission_data["rollback_on_failure"],
                timeout_seconds=mission_data["timeout_seconds"],
                description=mission_data["description"]
            )
            mission.update_status(MissionStatus.CANCELED)
            self.mission_store.update_mission(mission)
            self.event_bus.publish("mission.canceled", mission)
            
            logger.info(f"Mission {mission_id} canceled")
            return True
        else:
            # Mission is in the queue but not being processed yet
            # We need to remove it from the queue, but PriorityQueue doesn't support removal
            # In a real implementation, we would need a more sophisticated queue
            # For now, we'll just update the mission status and let the worker handle it
            mission = Mission(
                mission_id=mission_data["mission_id"],
                mission_type=mission_data["type"],
                priority=mission_data["priority"],
                target_layers=mission_data["target_layers"],
                configuration=mission_data["configuration"],
                simulation_required=mission_data["simulation_required"],
                rollback_on_failure=mission_data["rollback_on_failure"],
                timeout_seconds=mission_data["timeout_seconds"],
                description=mission_data["description"]
            )
            mission.update_status(MissionStatus.CANCELED)
            self.mission_store.update_mission(mission)
            self.event_bus.publish("mission.canceled", mission)
            
            logger.info(f"Mission {mission_id} marked for cancellation")
            return True
    
    def pause_mission(self, mission_id: str) -> bool:
        """Pause a mission"""
        mission_data = self.mission_store.get_mission(mission_id)
        if not mission_data:
            logger.warning(f"Mission {mission_id} not found")
            return False
        
        # Check if mission can be paused
        status = mission_data["status"]
        if status != MissionStatus.EXECUTING:
            logger.warning(f"Mission {mission_id} cannot be paused in state {status}")
            return False
        
        # Find the worker handling this mission
        target_worker = None
        for worker in self.workers:
            if worker.current_mission and worker.current_mission.mission_id == mission_id:
                target_worker = worker
                break
        
        if target_worker:
            # Mission is being processed by a worker
            # In a real implementation, we would need a way to signal the worker to pause the mission
            # For now, we'll just update the mission status
            mission = Mission(
                mission_id=mission_data["mission_id"],
                mission_type=mission_data["type"],
                priority=mission_data["priority"],
                target_layers=mission_data["target_layers"],
                configuration=mission_data["configuration"],
                simulation_required=mission_data["simulation_required"],
                rollback_on_failure=mission_data["rollback_on_failure"],
                timeout_seconds=mission_data["timeout_seconds"],
                description=mission_data["description"]
            )
            mission.update_status(MissionStatus.PAUSED)
            self.mission_store.update_mission(mission)
            self.event_bus.publish("mission.paused", mission)
            
            logger.info(f"Mission {mission_id} paused")
            return True
        else:
            logger.warning(f"Mission {mission_id} is not being processed by any worker")
            return False
    
    def resume_mission(self, mission_id: str) -> bool:
        """Resume a paused mission"""
        mission_data = self.mission_store.get_mission(mission_id)
        if not mission_data:
            logger.warning(f"Mission {mission_id} not found")
            return False
        
        # Check if mission can be resumed
        status = mission_data["status"]
        if status != MissionStatus.PAUSED:
            logger.warning(f"Mission {mission_id} cannot be resumed in state {status}")
            return False
        
        # Find the worker handling this mission
        target_worker = None
        for worker in self.workers:
            if worker.current_mission and worker.current_mission.mission_id == mission_id:
                target_worker = worker
                break
        
        if target_worker:
            # Mission is being processed by a worker
            # In a real implementation, we would need a way to signal the worker to resume the mission
            # For now, we'll just update the mission status
            mission = Mission(
                mission_id=mission_data["mission_id"],
                mission_type=mission_data["type"],
                priority=mission_data["priority"],
                target_layers=mission_data["target_layers"],
                configuration=mission_data["configuration"],
                simulation_required=mission_data["simulation_required"],
                rollback_on_failure=mission_data["rollback_on_failure"],
                timeout_seconds=mission_data["timeout_seconds"],
                description=mission_data["description"]
            )
            mission.update_status(MissionStatus.EXECUTING)
            mission.resumed_at = datetime.datetime.utcnow().isoformat()
            mission.add_timeline_event("Mission resumed", "Mission execution resumed")
            self.mission_store.update_mission(mission)
            self.event_bus.publish("mission.resumed", mission)
            
            logger.info(f"Mission {mission_id} resumed")
            return True
        else:
            logger.warning(f"Mission {mission_id} is not being processed by any worker")
            return False
    
    def rollback_mission(self, mission_id: str) -> bool:
        """Rollback a mission"""
        mission_data = self.mission_store.get_mission(mission_id)
        if not mission_data:
            logger.warning(f"Mission {mission_id} not found")
            return False
        
        # Check if mission can be rolled back
        status = mission_data["status"]
        if status not in [MissionStatus.SUCCEEDED, MissionStatus.FAILED, MissionStatus.EXECUTING]:
            logger.warning(f"Mission {mission_id} cannot be rolled back in state {status}")
            return False
        
        # Create a new rollback mission
        rollback_mission = Mission(
            mission_id=f"rollback-{mission_id}",
            mission_type=MissionType.ROLLBACK,
            priority=1,  # High priority for rollbacks
            target_layers=mission_data["target_layers"],
            configuration={
                "original_mission_id": mission_id,
                "rollback_type": "full"
            },
            simulation_required=True,
            rollback_on_failure=False,  # Can't rollback a rollback
            description=f"Rollback of mission {mission_id}"
        )
        
        # Submit the rollback mission
        self.submit_mission(rollback_mission)
        
        logger.info(f"Rollback mission created for {mission_id}")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the execution engine"""
        active_workers = sum(1 for w in self.workers if w.active)
        
        return {
            "is_running": self.running,
            "queue_size": self.mission_queue.qsize(),
            "active_mission_count": active_workers,
            "worker_count": len(self.workers),
            "active_worker_count": active_workers,
            "uptime_seconds": int(time.time() - self.start_time) if self.start_time else None,
            "version": "1.0.0"
        }
    
    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get a mission by ID"""
        return self.mission_store.get_mission(mission_id)
    
    def get_missions(self, status: Optional[str] = None, limit: int = 10, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Get missions, optionally filtered by status"""
        missions = self.mission_store.get_missions(status)
        
        # Sort by timestamp (newest first)
        missions.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply pagination
        paginated = missions[offset:offset + limit]
        
        return paginated, len(missions)
    
    def subscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Subscribe to events"""
        self.event_bus.subscribe(event_type, callback)

# Factory function to create an execution engine
def create_execution_engine(
    mission_planner,
    simulation_engine,
    mission_executor,
    error_handler,
    recovery_manager,
    worker_count: int = 5
) -> ExecutionEngine:
    """Create and configure an execution engine"""
    engine = ExecutionEngine(
        mission_planner,
        simulation_engine,
        mission_executor,
        error_handler,
        recovery_manager,
        worker_count
    )
    
    return engine
