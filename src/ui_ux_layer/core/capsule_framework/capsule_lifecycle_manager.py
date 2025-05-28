"""
Capsule Lifecycle Manager for the Capsule Framework

This module manages the lifecycle of Dynamic Agent Capsules within the Industriverse UI/UX Layer.
It handles capsule creation, activation, suspension, migration, and termination, ensuring proper
state management throughout the capsule lifecycle.

The Capsule Lifecycle Manager:
1. Creates new capsules based on agent state and context
2. Manages capsule state transitions (active, suspended, migrating)
3. Handles capsule migration between devices and environments
4. Implements capsule termination and cleanup
5. Provides an API for capsule lifecycle operations

Author: Manus
"""

import logging
import json
import time
import uuid
import threading
import queue
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import os

# Local imports
from .capsule_manager import CapsuleManager
from .capsule_memory_manager import CapsuleMemoryManager
from .capsule_morphology_engine import CapsuleMorphologyEngine
from .capsule_state_manager import CapsuleStateManager
from .capsule_interaction_controller import CapsuleInteractionController
from ..context_engine.context_awareness_engine import ContextAwarenessEngine

# Configure logging
logger = logging.getLogger(__name__)

class CapsuleState(Enum):
    """Enumeration of capsule states."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    MIGRATING = "migrating"
    TERMINATING = "terminating"
    TERMINATED = "terminated"
    ERROR = "error"

class CapsuleLifecycleManager:
    """
    Manages the lifecycle of Dynamic Agent Capsules within the Industriverse UI/UX Layer.
    
    This class is responsible for creating, activating, suspending, migrating, and terminating
    capsules, ensuring proper state management throughout the capsule lifecycle.
    """
    
    def __init__(
        self,
        capsule_manager: CapsuleManager,
        capsule_memory_manager: CapsuleMemoryManager,
        capsule_morphology_engine: CapsuleMorphologyEngine,
        capsule_state_manager: CapsuleStateManager,
        capsule_interaction_controller: CapsuleInteractionController,
        context_engine: ContextAwarenessEngine,
        config: Dict = None
    ):
        """
        Initialize the Capsule Lifecycle Manager.
        
        Args:
            capsule_manager: The Capsule Manager instance
            capsule_memory_manager: The Capsule Memory Manager instance
            capsule_morphology_engine: The Capsule Morphology Engine instance
            capsule_state_manager: The Capsule State Manager instance
            capsule_interaction_controller: The Capsule Interaction Controller instance
            context_engine: The Context Awareness Engine instance
            config: Optional configuration dictionary
        """
        self.capsule_manager = capsule_manager
        self.capsule_memory_manager = capsule_memory_manager
        self.capsule_morphology_engine = capsule_morphology_engine
        self.capsule_state_manager = capsule_state_manager
        self.capsule_interaction_controller = capsule_interaction_controller
        self.context_engine = context_engine
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "capsule_creation_timeout": 30,  # seconds
            "capsule_migration_timeout": 60,  # seconds
            "capsule_termination_timeout": 15,  # seconds
            "max_active_capsules": 50,
            "max_suspended_capsules": 100,
            "capsule_state_check_interval": 5,  # seconds
            "capsule_cleanup_interval": 300,  # seconds
            "capsule_state_storage_path": "/tmp/capsule_states",
            "enable_auto_recovery": True,
            "recovery_attempt_limit": 3,
            "recovery_backoff_factor": 2,  # seconds
            "enable_state_persistence": True,
            "state_persistence_interval": 60,  # seconds
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Ensure state storage directory exists
        os.makedirs(self.config["capsule_state_storage_path"], exist_ok=True)
        
        # Active capsules by capsule ID
        self.active_capsules = {}
        
        # Suspended capsules by capsule ID
        self.suspended_capsules = {}
        
        # Migrating capsules by capsule ID
        self.migrating_capsules = {}
        
        # Capsule operations queue
        self.operations_queue = queue.Queue()
        
        # Capsule operation results by operation ID
        self.operation_results = {}
        
        # Operation events by operation ID
        self.operation_events = {}
        
        # Recovery attempts by capsule ID
        self.recovery_attempts = {}
        
        # Start worker threads
        self.running = True
        self.operations_thread = threading.Thread(target=self._operations_worker)
        self.operations_thread.daemon = True
        self.operations_thread.start()
        
        self.state_check_thread = threading.Thread(target=self._state_check_worker)
        self.state_check_thread.daemon = True
        self.state_check_thread.start()
        
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        
        if self.config["enable_state_persistence"]:
            self.persistence_thread = threading.Thread(target=self._persistence_worker)
            self.persistence_thread.daemon = True
            self.persistence_thread.start()
        
        # Register as context listener
        self.context_engine.register_context_listener(self._handle_context_change)
        
        logger.info("Capsule Lifecycle Manager initialized")
    
    def _merge_config(self) -> None:
        """Merge provided configuration with defaults."""
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                # Merge nested dictionaries
                for nested_key, nested_value in value.items():
                    if nested_key not in self.config[key]:
                        self.config[key][nested_key] = nested_value
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        context_type = event.get("type")
        
        # Handle agent context changes
        if context_type == "agent":
            agent_data = event.get("data", {})
            
            # Check for new agent
            if "agent_id" in agent_data and "agent_state" in agent_data:
                agent_id = agent_data["agent_id"]
                agent_state = agent_data["agent_state"]
                
                # Check if we need to create a new capsule
                if agent_state == "active" and not self._has_capsule_for_agent(agent_id):
                    self._create_capsule_for_agent(agent_id, agent_data)
                
                # Check if we need to update capsule state
                elif self._has_capsule_for_agent(agent_id):
                    capsule_id = self._get_capsule_id_for_agent(agent_id)
                    
                    if agent_state == "suspended":
                        self.suspend_capsule(capsule_id)
                    elif agent_state == "terminated":
                        self.terminate_capsule(capsule_id)
                    elif agent_state == "active" and self._is_capsule_suspended(capsule_id):
                        self.activate_capsule(capsule_id)
        
        # Handle device context changes
        elif context_type == "device":
            device_data = event.get("data", {})
            
            # Check for device change that requires migration
            if "device_id" in device_data and "device_type" in device_data:
                device_id = device_data["device_id"]
                device_type = device_data["device_type"]
                
                # Find capsules that need to migrate
                for capsule_id, capsule in self.active_capsules.items():
                    if capsule.get("device_id") != device_id:
                        # Device changed, migrate capsule
                        self.migrate_capsule(capsule_id, device_id, device_type)
    
    def _has_capsule_for_agent(self, agent_id: str) -> bool:
        """
        Check if a capsule exists for an agent.
        
        Args:
            agent_id: Agent ID to check
            
        Returns:
            Boolean indicating if a capsule exists
        """
        # Check active capsules
        for capsule in self.active_capsules.values():
            if capsule.get("agent_id") == agent_id:
                return True
        
        # Check suspended capsules
        for capsule in self.suspended_capsules.values():
            if capsule.get("agent_id") == agent_id:
                return True
        
        # Check migrating capsules
        for capsule in self.migrating_capsules.values():
            if capsule.get("agent_id") == agent_id:
                return True
        
        return False
    
    def _get_capsule_id_for_agent(self, agent_id: str) -> Optional[str]:
        """
        Get capsule ID for an agent.
        
        Args:
            agent_id: Agent ID to get capsule for
            
        Returns:
            Capsule ID or None if not found
        """
        # Check active capsules
        for capsule_id, capsule in self.active_capsules.items():
            if capsule.get("agent_id") == agent_id:
                return capsule_id
        
        # Check suspended capsules
        for capsule_id, capsule in self.suspended_capsules.items():
            if capsule.get("agent_id") == agent_id:
                return capsule_id
        
        # Check migrating capsules
        for capsule_id, capsule in self.migrating_capsules.items():
            if capsule.get("agent_id") == agent_id:
                return capsule_id
        
        return None
    
    def _is_capsule_suspended(self, capsule_id: str) -> bool:
        """
        Check if a capsule is suspended.
        
        Args:
            capsule_id: Capsule ID to check
            
        Returns:
            Boolean indicating if the capsule is suspended
        """
        return capsule_id in self.suspended_capsules
    
    def _create_capsule_for_agent(self, agent_id: str, agent_data: Dict) -> Optional[str]:
        """
        Create a new capsule for an agent.
        
        Args:
            agent_id: Agent ID to create capsule for
            agent_data: Agent data
            
        Returns:
            Capsule ID or None on failure
        """
        # Check if we can create more capsules
        if len(self.active_capsules) >= self.config["max_active_capsules"]:
            logger.warning(f"Cannot create capsule for agent {agent_id}: maximum active capsules reached")
            return None
        
        # Create capsule
        capsule_id = str(uuid.uuid4())
        
        # Get current device context
        device_context = self.context_engine.get_context("device") or {}
        device_id = device_context.get("device_id", "unknown")
        device_type = device_context.get("device_type", "desktop")
        
        # Create capsule data
        capsule_data = {
            "capsule_id": capsule_id,
            "agent_id": agent_id,
            "agent_name": agent_data.get("agent_name", "Unknown Agent"),
            "agent_type": agent_data.get("agent_type", "generic"),
            "agent_layer": agent_data.get("agent_layer", "unknown"),
            "agent_capabilities": agent_data.get("agent_capabilities", []),
            "agent_state": agent_data.get("agent_state", "active"),
            "device_id": device_id,
            "device_type": device_type,
            "state": CapsuleState.INITIALIZING.value,
            "created_at": time.time(),
            "updated_at": time.time(),
            "last_active": time.time(),
            "morphology": {
                "size": "medium",
                "shape": "rounded",
                "color_scheme": "default",
                "animation_level": "standard"
            },
            "position": {
                "x": 0,
                "y": 0,
                "z": 0,
                "docked": True
            },
            "memory": {
                "state_snapshot": {},
                "interaction_history": [],
                "context_history": []
            },
            "interactions": {
                "available_actions": [],
                "current_focus": None,
                "interaction_mode": "standard"
            }
        }
        
        # Queue capsule creation operation
        operation_id = self._queue_operation("create_capsule", {
            "capsule_id": capsule_id,
            "capsule_data": capsule_data
        })
        
        # Wait for operation to complete
        result = self._wait_for_operation(operation_id, self.config["capsule_creation_timeout"])
        
        if result and result.get("success"):
            logger.info(f"Created capsule {capsule_id} for agent {agent_id}")
            return capsule_id
        else:
            error = result.get("error") if result else "Operation timeout"
            logger.error(f"Failed to create capsule for agent {agent_id}: {error}")
            return None
    
    def _queue_operation(self, operation_type: str, operation_data: Dict) -> str:
        """
        Queue a capsule operation.
        
        Args:
            operation_type: Type of operation
            operation_data: Operation data
            
        Returns:
            Operation ID
        """
        operation_id = str(uuid.uuid4())
        
        # Create operation
        operation = {
            "operation_id": operation_id,
            "operation_type": operation_type,
            "operation_data": operation_data,
            "created_at": time.time()
        }
        
        # Create event for operation
        self.operation_events[operation_id] = threading.Event()
        
        # Queue operation
        self.operations_queue.put(operation)
        
        return operation_id
    
    def _wait_for_operation(self, operation_id: str, timeout: float) -> Optional[Dict]:
        """
        Wait for an operation to complete.
        
        Args:
            operation_id: Operation ID to wait for
            timeout: Timeout in seconds
            
        Returns:
            Operation result or None on timeout
        """
        # Get event
        event = self.operation_events.get(operation_id)
        if not event:
            logger.error(f"No event for operation {operation_id}")
            return None
        
        # Wait for event
        if event.wait(timeout):
            # Get result
            result = self.operation_results.get(operation_id)
            
            # Clean up
            del self.operation_events[operation_id]
            del self.operation_results[operation_id]
            
            return result
        else:
            # Timeout
            logger.warning(f"Timeout waiting for operation {operation_id}")
            
            # Clean up
            del self.operation_events[operation_id]
            if operation_id in self.operation_results:
                del self.operation_results[operation_id]
            
            return None
    
    def _operations_worker(self) -> None:
        """Background thread for processing capsule operations."""
        while self.running:
            try:
                # Get next operation from queue
                operation = self.operations_queue.get(timeout=1.0)
                
                # Process operation
                result = self._process_operation(operation)
                
                # Store result
                operation_id = operation.get("operation_id")
                self.operation_results[operation_id] = result
                
                # Signal completion
                if operation_id in self.operation_events:
                    self.operation_events[operation_id].set()
                
                # Mark task as done
                self.operations_queue.task_done()
            except queue.Empty:
                # Queue empty, continue
                pass
            except Exception as e:
                logger.error(f"Error in operations worker: {str(e)}")
                time.sleep(1)  # Avoid tight loop on error
    
    def _process_operation(self, operation: Dict) -> Dict:
        """
        Process a capsule operation.
        
        Args:
            operation: Operation to process
            
        Returns:
            Operation result
        """
        operation_type = operation.get("operation_type")
        operation_data = operation.get("operation_data", {})
        
        try:
            if operation_type == "create_capsule":
                return self._process_create_capsule(operation_data)
            elif operation_type == "activate_capsule":
                return self._process_activate_capsule(operation_data)
            elif operation_type == "suspend_capsule":
                return self._process_suspend_capsule(operation_data)
            elif operation_type == "migrate_capsule":
                return self._process_migrate_capsule(operation_data)
            elif operation_type == "terminate_capsule":
                return self._process_terminate_capsule(operation_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation type: {operation_type}"
                }
        except Exception as e:
            logger.error(f"Error processing operation {operation_type}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_create_capsule(self, operation_data: Dict) -> Dict:
        """
        Process create capsule operation.
        
        Args:
            operation_data: Operation data
            
        Returns:
            Operation result
        """
        capsule_id = operation_data.get("capsule_id")
        capsule_data = operation_data.get("capsule_data", {})
        
        if not capsule_id or not capsule_data:
            return {
                "success": False,
                "error": "Missing capsule_id or capsule_data"
            }
        
        try:
            # Initialize capsule with Capsule Manager
            self.capsule_manager.initialize_capsule(capsule_id, capsule_data)
            
            # Initialize capsule memory
            self.capsule_memory_manager.initialize_memory(capsule_id, capsule_data.get("memory", {}))
            
            # Initialize capsule morphology
            self.capsule_morphology_engine.initialize_morphology(
                capsule_id, 
                capsule_data.get("agent_type", "generic"),
                capsule_data.get("morphology", {})
            )
            
            # Initialize capsule state
            self.capsule_state_manager.initialize_state(capsule_id, CapsuleState.INITIALIZING.value)
            
            # Initialize capsule interactions
            self.capsule_interaction_controller.initialize_interactions(
                capsule_id,
                capsule_data.get("agent_capabilities", []),
                capsule_data.get("interactions", {})
            )
            
            # Store capsule in active capsules
            self.active_capsules[capsule_id] = capsule_data
            
            # Update capsule state
            self.active_capsules[capsule_id]["state"] = CapsuleState.ACTIVE.value
            self.active_capsules[capsule_id]["updated_at"] = time.time()
            
            # Update capsule state in state manager
            self.capsule_state_manager.update_state(capsule_id, CapsuleState.ACTIVE.value)
            
            # Notify context engine of new capsule
            self.context_engine.update_context(
                "capsule",
                {
                    "action": "created",
                    "capsule_id": capsule_id,
                    "agent_id": capsule_data.get("agent_id"),
                    "agent_name": capsule_data.get("agent_name"),
                    "agent_layer": capsule_data.get("agent_layer")
                }
            )
            
            return {
                "success": True,
                "capsule_id": capsule_id,
                "state": CapsuleState.ACTIVE.value
            }
        except Exception as e:
            logger.error(f"Error creating capsule {capsule_id}: {str(e)}")
            
            # Clean up on error
            self._cleanup_capsule(capsule_id)
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_activate_capsule(self, operation_data: Dict) -> Dict:
        """
        Process activate capsule operation.
        
        Args:
            operation_data: Operation data
            
        Returns:
            Operation result
        """
        capsule_id = operation_data.get("capsule_id")
        
        if not capsule_id:
            return {
                "success": False,
                "error": "Missing capsule_id"
            }
        
        # Check if capsule exists in suspended capsules
        if capsule_id not in self.suspended_capsules:
            return {
                "success": False,
                "error": f"Capsule {capsule_id} not found in suspended capsules"
            }
        
        try:
            # Get capsule data
            capsule_data = self.suspended_capsules[capsule_id]
            
            # Restore capsule state
            self.capsule_state_manager.update_state(capsule_id, CapsuleState.ACTIVE.value)
            
            # Restore capsule memory
            self.capsule_memory_manager.restore_memory(capsule_id)
            
            # Restore capsule morphology
            self.capsule_morphology_engine.restore_morphology(capsule_id)
            
            # Restore capsule interactions
            self.capsule_interaction_controller.restore_interactions(capsule_id)
            
            # Move capsule from suspended to active
            self.active_capsules[capsule_id] = capsule_data
            del self.suspended_capsules[capsule_id]
            
            # Update capsule state
            self.active_capsules[capsule_id]["state"] = CapsuleState.ACTIVE.value
            self.active_capsules[capsule_id]["updated_at"] = time.time()
            self.active_capsules[capsule_id]["last_active"] = time.time()
            
            # Notify context engine of capsule activation
            self.context_engine.update_context(
                "capsule",
                {
                    "action": "activated",
                    "capsule_id": capsule_id,
                    "agent_id": capsule_data.get("agent_id"),
                    "agent_name": capsule_data.get("agent_name")
                }
            )
            
            return {
                "success": True,
                "capsule_id": capsule_id,
                "state": CapsuleState.ACTIVE.value
            }
        except Exception as e:
            logger.error(f"Error activating capsule {capsule_id}: {str(e)}")
            
            # Attempt recovery
            if self.config["enable_auto_recovery"]:
                self._attempt_capsule_recovery(capsule_id, "activation_error")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_suspend_capsule(self, operation_data: Dict) -> Dict:
        """
        Process suspend capsule operation.
        
        Args:
            operation_data: Operation data
            
        Returns:
            Operation result
        """
        capsule_id = operation_data.get("capsule_id")
        
        if not capsule_id:
            return {
                "success": False,
                "error": "Missing capsule_id"
            }
        
        # Check if capsule exists in active capsules
        if capsule_id not in self.active_capsules:
            return {
                "success": False,
                "error": f"Capsule {capsule_id} not found in active capsules"
            }
        
        try:
            # Get capsule data
            capsule_data = self.active_capsules[capsule_id]
            
            # Suspend capsule state
            self.capsule_state_manager.update_state(capsule_id, CapsuleState.SUSPENDED.value)
            
            # Snapshot capsule memory
            self.capsule_memory_manager.snapshot_memory(capsule_id)
            
            # Suspend capsule morphology
            self.capsule_morphology_engine.suspend_morphology(capsule_id)
            
            # Suspend capsule interactions
            self.capsule_interaction_controller.suspend_interactions(capsule_id)
            
            # Move capsule from active to suspended
            self.suspended_capsules[capsule_id] = capsule_data
            del self.active_capsules[capsule_id]
            
            # Update capsule state
            self.suspended_capsules[capsule_id]["state"] = CapsuleState.SUSPENDED.value
            self.suspended_capsules[capsule_id]["updated_at"] = time.time()
            
            # Notify context engine of capsule suspension
            self.context_engine.update_context(
                "capsule",
                {
                    "action": "suspended",
                    "capsule_id": capsule_id,
                    "agent_id": capsule_data.get("agent_id"),
                    "agent_name": capsule_data.get("agent_name")
                }
            )
            
            return {
                "success": True,
                "capsule_id": capsule_id,
                "state": CapsuleState.SUSPENDED.value
            }
        except Exception as e:
            logger.error(f"Error suspending capsule {capsule_id}: {str(e)}")
            
            # Attempt recovery
            if self.config["enable_auto_recovery"]:
                self._attempt_capsule_recovery(capsule_id, "suspension_error")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_migrate_capsule(self, operation_data: Dict) -> Dict:
        """
        Process migrate capsule operation.
        
        Args:
            operation_data: Operation data
            
        Returns:
            Operation result
        """
        capsule_id = operation_data.get("capsule_id")
        target_device_id = operation_data.get("target_device_id")
        target_device_type = operation_data.get("target_device_type")
        
        if not capsule_id or not target_device_id or not target_device_type:
            return {
                "success": False,
                "error": "Missing required fields for migration"
            }
        
        # Check if capsule exists in active capsules
        if capsule_id not in self.active_capsules:
            return {
                "success": False,
                "error": f"Capsule {capsule_id} not found in active capsules"
            }
        
        try:
            # Get capsule data
            capsule_data = self.active_capsules[capsule_id]
            
            # Update capsule state
            self.capsule_state_manager.update_state(capsule_id, CapsuleState.MIGRATING.value)
            
            # Move capsule to migrating
            self.migrating_capsules[capsule_id] = capsule_data
            del self.active_capsules[capsule_id]
            
            # Update capsule state
            self.migrating_capsules[capsule_id]["state"] = CapsuleState.MIGRATING.value
            self.migrating_capsules[capsule_id]["updated_at"] = time.time()
            
            # Notify context engine of migration start
            self.context_engine.update_context(
                "capsule",
                {
                    "action": "migration_started",
                    "capsule_id": capsule_id,
                    "agent_id": capsule_data.get("agent_id"),
                    "source_device_id": capsule_data.get("device_id"),
                    "target_device_id": target_device_id
                }
            )
            
            # Snapshot capsule memory
            memory_snapshot = self.capsule_memory_manager.snapshot_memory(capsule_id)
            
            # Snapshot capsule morphology
            morphology_snapshot = self.capsule_morphology_engine.snapshot_morphology(capsule_id)
            
            # Snapshot capsule state
            state_snapshot = self.capsule_state_manager.snapshot_state(capsule_id)
            
            # Snapshot capsule interactions
            interactions_snapshot = self.capsule_interaction_controller.snapshot_interactions(capsule_id)
            
            # Update device information
            self.migrating_capsules[capsule_id]["device_id"] = target_device_id
            self.migrating_capsules[capsule_id]["device_type"] = target_device_type
            
            # Adapt morphology for target device
            adapted_morphology = self.capsule_morphology_engine.adapt_morphology_for_device(
                capsule_id,
                target_device_type,
                morphology_snapshot
            )
            
            # Adapt interactions for target device
            adapted_interactions = self.capsule_interaction_controller.adapt_interactions_for_device(
                capsule_id,
                target_device_type,
                interactions_snapshot
            )
            
            # Restore capsule on target device
            self.capsule_morphology_engine.restore_morphology(
                capsule_id,
                adapted_morphology
            )
            
            self.capsule_interaction_controller.restore_interactions(
                capsule_id,
                adapted_interactions
            )
            
            self.capsule_memory_manager.restore_memory(
                capsule_id,
                memory_snapshot
            )
            
            # Move capsule back to active
            self.active_capsules[capsule_id] = self.migrating_capsules[capsule_id]
            del self.migrating_capsules[capsule_id]
            
            # Update capsule state
            self.active_capsules[capsule_id]["state"] = CapsuleState.ACTIVE.value
            self.active_capsules[capsule_id]["updated_at"] = time.time()
            self.active_capsules[capsule_id]["last_active"] = time.time()
            
            # Update capsule state in state manager
            self.capsule_state_manager.update_state(capsule_id, CapsuleState.ACTIVE.value)
            
            # Notify context engine of migration completion
            self.context_engine.update_context(
                "capsule",
                {
                    "action": "migration_completed",
                    "capsule_id": capsule_id,
                    "agent_id": capsule_data.get("agent_id"),
                    "target_device_id": target_device_id,
                    "target_device_type": target_device_type
                }
            )
            
            return {
                "success": True,
                "capsule_id": capsule_id,
                "state": CapsuleState.ACTIVE.value,
                "device_id": target_device_id,
                "device_type": target_device_type
            }
        except Exception as e:
            logger.error(f"Error migrating capsule {capsule_id}: {str(e)}")
            
            # Attempt recovery
            if self.config["enable_auto_recovery"]:
                self._attempt_capsule_recovery(capsule_id, "migration_error")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_terminate_capsule(self, operation_data: Dict) -> Dict:
        """
        Process terminate capsule operation.
        
        Args:
            operation_data: Operation data
            
        Returns:
            Operation result
        """
        capsule_id = operation_data.get("capsule_id")
        
        if not capsule_id:
            return {
                "success": False,
                "error": "Missing capsule_id"
            }
        
        # Check if capsule exists
        capsule_data = None
        capsule_location = None
        
        if capsule_id in self.active_capsules:
            capsule_data = self.active_capsules[capsule_id]
            capsule_location = "active"
        elif capsule_id in self.suspended_capsules:
            capsule_data = self.suspended_capsules[capsule_id]
            capsule_location = "suspended"
        elif capsule_id in self.migrating_capsules:
            capsule_data = self.migrating_capsules[capsule_id]
            capsule_location = "migrating"
        
        if not capsule_data:
            return {
                "success": False,
                "error": f"Capsule {capsule_id} not found"
            }
        
        try:
            # Update capsule state
            self.capsule_state_manager.update_state(capsule_id, CapsuleState.TERMINATING.value)
            
            # Notify context engine of termination
            self.context_engine.update_context(
                "capsule",
                {
                    "action": "terminating",
                    "capsule_id": capsule_id,
                    "agent_id": capsule_data.get("agent_id"),
                    "agent_name": capsule_data.get("agent_name")
                }
            )
            
            # Clean up capsule resources
            self._cleanup_capsule(capsule_id)
            
            # Remove capsule from appropriate collection
            if capsule_location == "active":
                del self.active_capsules[capsule_id]
            elif capsule_location == "suspended":
                del self.suspended_capsules[capsule_id]
            elif capsule_location == "migrating":
                del self.migrating_capsules[capsule_id]
            
            # Update capsule state
            self.capsule_state_manager.update_state(capsule_id, CapsuleState.TERMINATED.value)
            
            # Notify context engine of termination completion
            self.context_engine.update_context(
                "capsule",
                {
                    "action": "terminated",
                    "capsule_id": capsule_id,
                    "agent_id": capsule_data.get("agent_id"),
                    "agent_name": capsule_data.get("agent_name")
                }
            )
            
            return {
                "success": True,
                "capsule_id": capsule_id,
                "state": CapsuleState.TERMINATED.value
            }
        except Exception as e:
            logger.error(f"Error terminating capsule {capsule_id}: {str(e)}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _cleanup_capsule(self, capsule_id: str) -> None:
        """
        Clean up capsule resources.
        
        Args:
            capsule_id: Capsule ID to clean up
        """
        try:
            # Clean up capsule memory
            self.capsule_memory_manager.cleanup_memory(capsule_id)
            
            # Clean up capsule morphology
            self.capsule_morphology_engine.cleanup_morphology(capsule_id)
            
            # Clean up capsule state
            self.capsule_state_manager.cleanup_state(capsule_id)
            
            # Clean up capsule interactions
            self.capsule_interaction_controller.cleanup_interactions(capsule_id)
            
            # Clean up capsule in manager
            self.capsule_manager.cleanup_capsule(capsule_id)
            
            logger.debug(f"Cleaned up resources for capsule {capsule_id}")
        except Exception as e:
            logger.error(f"Error cleaning up capsule {capsule_id}: {str(e)}")
    
    def _attempt_capsule_recovery(self, capsule_id: str, error_type: str) -> bool:
        """
        Attempt to recover a capsule from error.
        
        Args:
            capsule_id: Capsule ID to recover
            error_type: Type of error
            
        Returns:
            Boolean indicating success
        """
        # Check if we've exceeded recovery attempts
        if capsule_id in self.recovery_attempts:
            attempts = self.recovery_attempts[capsule_id]
            if attempts >= self.config["recovery_attempt_limit"]:
                logger.warning(f"Exceeded recovery attempt limit for capsule {capsule_id}")
                return False
            
            # Increment attempts
            self.recovery_attempts[capsule_id] = attempts + 1
        else:
            # First attempt
            self.recovery_attempts[capsule_id] = 1
        
        # Get attempt number
        attempt = self.recovery_attempts[capsule_id]
        
        # Calculate backoff
        backoff = self.config["recovery_backoff_factor"] * (2 ** (attempt - 1))
        
        logger.info(f"Attempting recovery for capsule {capsule_id} (attempt {attempt}, backoff {backoff}s)")
        
        # Wait for backoff
        time.sleep(backoff)
        
        try:
            # Different recovery strategies based on error type
            if error_type == "activation_error":
                # Try to recreate capsule from suspended state
                if capsule_id in self.suspended_capsules:
                    capsule_data = self.suspended_capsules[capsule_id]
                    
                    # Clean up existing resources
                    self._cleanup_capsule(capsule_id)
                    
                    # Reinitialize capsule
                    self.capsule_manager.initialize_capsule(capsule_id, capsule_data)
                    self.capsule_memory_manager.initialize_memory(capsule_id, capsule_data.get("memory", {}))
                    self.capsule_morphology_engine.initialize_morphology(
                        capsule_id, 
                        capsule_data.get("agent_type", "generic"),
                        capsule_data.get("morphology", {})
                    )
                    self.capsule_state_manager.initialize_state(capsule_id, CapsuleState.ACTIVE.value)
                    self.capsule_interaction_controller.initialize_interactions(
                        capsule_id,
                        capsule_data.get("agent_capabilities", []),
                        capsule_data.get("interactions", {})
                    )
                    
                    # Move to active
                    self.active_capsules[capsule_id] = capsule_data
                    del self.suspended_capsules[capsule_id]
                    
                    # Update state
                    self.active_capsules[capsule_id]["state"] = CapsuleState.ACTIVE.value
                    self.active_capsules[capsule_id]["updated_at"] = time.time()
                    self.active_capsules[capsule_id]["last_active"] = time.time()
                    
                    logger.info(f"Successfully recovered capsule {capsule_id} from activation error")
                    return True
            
            elif error_type == "suspension_error":
                # Try to force suspend
                if capsule_id in self.active_capsules:
                    capsule_data = self.active_capsules[capsule_id]
                    
                    # Force state update
                    self.capsule_state_manager.update_state(capsule_id, CapsuleState.SUSPENDED.value)
                    
                    # Move to suspended
                    self.suspended_capsules[capsule_id] = capsule_data
                    del self.active_capsules[capsule_id]
                    
                    # Update state
                    self.suspended_capsules[capsule_id]["state"] = CapsuleState.SUSPENDED.value
                    self.suspended_capsules[capsule_id]["updated_at"] = time.time()
                    
                    logger.info(f"Successfully recovered capsule {capsule_id} from suspension error")
                    return True
            
            elif error_type == "migration_error":
                # Try to restore to original device
                if capsule_id in self.migrating_capsules:
                    capsule_data = self.migrating_capsules[capsule_id]
                    
                    # Clean up existing resources
                    self._cleanup_capsule(capsule_id)
                    
                    # Reinitialize capsule
                    self.capsule_manager.initialize_capsule(capsule_id, capsule_data)
                    self.capsule_memory_manager.initialize_memory(capsule_id, capsule_data.get("memory", {}))
                    self.capsule_morphology_engine.initialize_morphology(
                        capsule_id, 
                        capsule_data.get("agent_type", "generic"),
                        capsule_data.get("morphology", {})
                    )
                    self.capsule_state_manager.initialize_state(capsule_id, CapsuleState.ACTIVE.value)
                    self.capsule_interaction_controller.initialize_interactions(
                        capsule_id,
                        capsule_data.get("agent_capabilities", []),
                        capsule_data.get("interactions", {})
                    )
                    
                    # Move to active
                    self.active_capsules[capsule_id] = capsule_data
                    del self.migrating_capsules[capsule_id]
                    
                    # Update state
                    self.active_capsules[capsule_id]["state"] = CapsuleState.ACTIVE.value
                    self.active_capsules[capsule_id]["updated_at"] = time.time()
                    self.active_capsules[capsule_id]["last_active"] = time.time()
                    
                    logger.info(f"Successfully recovered capsule {capsule_id} from migration error")
                    return True
            
            # Unknown error type or recovery failed
            return False
        except Exception as e:
            logger.error(f"Error during recovery attempt for capsule {capsule_id}: {str(e)}")
            return False
    
    def _state_check_worker(self) -> None:
        """Background thread for checking capsule states."""
        while self.running:
            try:
                # Check active capsules
                for capsule_id, capsule in list(self.active_capsules.items()):
                    # Check if capsule state matches
                    expected_state = CapsuleState.ACTIVE.value
                    actual_state = self.capsule_state_manager.get_state(capsule_id)
                    
                    if actual_state != expected_state:
                        logger.warning(
                            f"Capsule {capsule_id} state mismatch: "
                            f"expected {expected_state}, actual {actual_state}"
                        )
                        
                        # Attempt to fix state
                        self.capsule_state_manager.update_state(capsule_id, expected_state)
                
                # Check suspended capsules
                for capsule_id, capsule in list(self.suspended_capsules.items()):
                    # Check if capsule state matches
                    expected_state = CapsuleState.SUSPENDED.value
                    actual_state = self.capsule_state_manager.get_state(capsule_id)
                    
                    if actual_state != expected_state:
                        logger.warning(
                            f"Capsule {capsule_id} state mismatch: "
                            f"expected {expected_state}, actual {actual_state}"
                        )
                        
                        # Attempt to fix state
                        self.capsule_state_manager.update_state(capsule_id, expected_state)
                
                # Check migrating capsules
                for capsule_id, capsule in list(self.migrating_capsules.items()):
                    # Check if capsule state matches
                    expected_state = CapsuleState.MIGRATING.value
                    actual_state = self.capsule_state_manager.get_state(capsule_id)
                    
                    if actual_state != expected_state:
                        logger.warning(
                            f"Capsule {capsule_id} state mismatch: "
                            f"expected {expected_state}, actual {actual_state}"
                        )
                        
                        # Attempt to fix state
                        self.capsule_state_manager.update_state(capsule_id, expected_state)
                    
                    # Check if migration has been stuck
                    updated_at = capsule.get("updated_at", 0)
                    if time.time() - updated_at > self.config["capsule_migration_timeout"]:
                        logger.warning(f"Capsule {capsule_id} migration timeout")
                        
                        # Attempt recovery
                        if self.config["enable_auto_recovery"]:
                            self._attempt_capsule_recovery(capsule_id, "migration_error")
                
                # Sleep until next check
                time.sleep(self.config["capsule_state_check_interval"])
            except Exception as e:
                logger.error(f"Error in state check worker: {str(e)}")
                time.sleep(5)  # Avoid tight loop on error
    
    def _cleanup_worker(self) -> None:
        """Background thread for cleaning up stale capsules."""
        while self.running:
            try:
                # Clean up stale suspended capsules
                current_time = time.time()
                
                # Check if we need to clean up suspended capsules
                if len(self.suspended_capsules) > self.config["max_suspended_capsules"]:
                    # Sort by last active time
                    sorted_capsules = sorted(
                        self.suspended_capsules.items(),
                        key=lambda x: x[1].get("last_active", 0)
                    )
                    
                    # Determine how many to remove
                    to_remove = len(self.suspended_capsules) - self.config["max_suspended_capsules"]
                    
                    # Remove oldest capsules
                    for i in range(to_remove):
                        if i < len(sorted_capsules):
                            capsule_id, _ = sorted_capsules[i]
                            self.terminate_capsule(capsule_id)
                            logger.info(f"Cleaned up stale suspended capsule {capsule_id}")
                
                # Sleep until next cleanup
                time.sleep(self.config["capsule_cleanup_interval"])
            except Exception as e:
                logger.error(f"Error in cleanup worker: {str(e)}")
                time.sleep(60)  # Longer sleep on error
    
    def _persistence_worker(self) -> None:
        """Background thread for persisting capsule states."""
        while self.running:
            try:
                # Persist active capsules
                for capsule_id, capsule in self.active_capsules.items():
                    self._persist_capsule_state(capsule_id, capsule)
                
                # Persist suspended capsules
                for capsule_id, capsule in self.suspended_capsules.items():
                    self._persist_capsule_state(capsule_id, capsule)
                
                # Sleep until next persistence
                time.sleep(self.config["state_persistence_interval"])
            except Exception as e:
                logger.error(f"Error in persistence worker: {str(e)}")
                time.sleep(30)  # Longer sleep on error
    
    def _persist_capsule_state(self, capsule_id: str, capsule: Dict) -> None:
        """
        Persist capsule state to disk.
        
        Args:
            capsule_id: Capsule ID
            capsule: Capsule data
        """
        try:
            # Create state file path
            state_file = os.path.join(
                self.config["capsule_state_storage_path"],
                f"{capsule_id}.json"
            )
            
            # Create state data
            state_data = {
                "capsule_id": capsule_id,
                "capsule_data": capsule,
                "memory": self.capsule_memory_manager.snapshot_memory(capsule_id),
                "morphology": self.capsule_morphology_engine.snapshot_morphology(capsule_id),
                "state": self.capsule_state_manager.snapshot_state(capsule_id),
                "interactions": self.capsule_interaction_controller.snapshot_interactions(capsule_id),
                "persisted_at": time.time()
            }
            
            # Write to file
            with open(state_file, "w") as f:
                json.dump(state_data, f)
            
            logger.debug(f"Persisted state for capsule {capsule_id}")
        except Exception as e:
            logger.error(f"Error persisting state for capsule {capsule_id}: {str(e)}")
    
    def _load_persisted_capsule_state(self, capsule_id: str) -> Optional[Dict]:
        """
        Load persisted capsule state from disk.
        
        Args:
            capsule_id: Capsule ID
            
        Returns:
            Capsule state data or None if not found
        """
        try:
            # Create state file path
            state_file = os.path.join(
                self.config["capsule_state_storage_path"],
                f"{capsule_id}.json"
            )
            
            # Check if file exists
            if not os.path.exists(state_file):
                return None
            
            # Read from file
            with open(state_file, "r") as f:
                state_data = json.load(f)
            
            return state_data
        except Exception as e:
            logger.error(f"Error loading persisted state for capsule {capsule_id}: {str(e)}")
            return None
    
    # Public API
    
    def create_capsule(self, agent_id: str, agent_data: Dict) -> Optional[str]:
        """
        Create a new capsule for an agent.
        
        Args:
            agent_id: Agent ID to create capsule for
            agent_data: Agent data
            
        Returns:
            Capsule ID or None on failure
        """
        return self._create_capsule_for_agent(agent_id, agent_data)
    
    def activate_capsule(self, capsule_id: str) -> bool:
        """
        Activate a suspended capsule.
        
        Args:
            capsule_id: Capsule ID to activate
            
        Returns:
            Boolean indicating success
        """
        # Queue operation
        operation_id = self._queue_operation("activate_capsule", {
            "capsule_id": capsule_id
        })
        
        # Wait for operation to complete
        result = self._wait_for_operation(operation_id, self.config["capsule_creation_timeout"])
        
        return result is not None and result.get("success", False)
    
    def suspend_capsule(self, capsule_id: str) -> bool:
        """
        Suspend an active capsule.
        
        Args:
            capsule_id: Capsule ID to suspend
            
        Returns:
            Boolean indicating success
        """
        # Queue operation
        operation_id = self._queue_operation("suspend_capsule", {
            "capsule_id": capsule_id
        })
        
        # Wait for operation to complete
        result = self._wait_for_operation(operation_id, self.config["capsule_creation_timeout"])
        
        return result is not None and result.get("success", False)
    
    def migrate_capsule(self, capsule_id: str, target_device_id: str, target_device_type: str) -> bool:
        """
        Migrate a capsule to another device.
        
        Args:
            capsule_id: Capsule ID to migrate
            target_device_id: Target device ID
            target_device_type: Target device type
            
        Returns:
            Boolean indicating success
        """
        # Queue operation
        operation_id = self._queue_operation("migrate_capsule", {
            "capsule_id": capsule_id,
            "target_device_id": target_device_id,
            "target_device_type": target_device_type
        })
        
        # Wait for operation to complete
        result = self._wait_for_operation(operation_id, self.config["capsule_migration_timeout"])
        
        return result is not None and result.get("success", False)
    
    def terminate_capsule(self, capsule_id: str) -> bool:
        """
        Terminate a capsule.
        
        Args:
            capsule_id: Capsule ID to terminate
            
        Returns:
            Boolean indicating success
        """
        # Queue operation
        operation_id = self._queue_operation("terminate_capsule", {
            "capsule_id": capsule_id
        })
        
        # Wait for operation to complete
        result = self._wait_for_operation(operation_id, self.config["capsule_termination_timeout"])
        
        return result is not None and result.get("success", False)
    
    def get_capsule(self, capsule_id: str) -> Optional[Dict]:
        """
        Get capsule data.
        
        Args:
            capsule_id: Capsule ID to get
            
        Returns:
            Capsule data or None if not found
        """
        # Check active capsules
        if capsule_id in self.active_capsules:
            return self.active_capsules[capsule_id]
        
        # Check suspended capsules
        if capsule_id in self.suspended_capsules:
            return self.suspended_capsules[capsule_id]
        
        # Check migrating capsules
        if capsule_id in self.migrating_capsules:
            return self.migrating_capsules[capsule_id]
        
        return None
    
    def get_capsule_state(self, capsule_id: str) -> Optional[str]:
        """
        Get capsule state.
        
        Args:
            capsule_id: Capsule ID to get state for
            
        Returns:
            Capsule state or None if not found
        """
        return self.capsule_state_manager.get_state(capsule_id)
    
    def get_active_capsules(self) -> Dict[str, Dict]:
        """
        Get all active capsules.
        
        Returns:
            Dictionary of active capsules by capsule ID
        """
        return self.active_capsules.copy()
    
    def get_suspended_capsules(self) -> Dict[str, Dict]:
        """
        Get all suspended capsules.
        
        Returns:
            Dictionary of suspended capsules by capsule ID
        """
        return self.suspended_capsules.copy()
    
    def get_capsules_for_agent(self, agent_id: str) -> List[Dict]:
        """
        Get all capsules for an agent.
        
        Args:
            agent_id: Agent ID to get capsules for
            
        Returns:
            List of capsule data
        """
        result = []
        
        # Check active capsules
        for capsule_id, capsule in self.active_capsules.items():
            if capsule.get("agent_id") == agent_id:
                result.append(capsule)
        
        # Check suspended capsules
        for capsule_id, capsule in self.suspended_capsules.items():
            if capsule.get("agent_id") == agent_id:
                result.append(capsule)
        
        # Check migrating capsules
        for capsule_id, capsule in self.migrating_capsules.items():
            if capsule.get("agent_id") == agent_id:
                result.append(capsule)
        
        return result
    
    def get_capsules_for_device(self, device_id: str) -> List[Dict]:
        """
        Get all capsules for a device.
        
        Args:
            device_id: Device ID to get capsules for
            
        Returns:
            List of capsule data
        """
        result = []
        
        # Check active capsules
        for capsule_id, capsule in self.active_capsules.items():
            if capsule.get("device_id") == device_id:
                result.append(capsule)
        
        # Check suspended capsules
        for capsule_id, capsule in self.suspended_capsules.items():
            if capsule.get("device_id") == device_id:
                result.append(capsule)
        
        # Check migrating capsules
        for capsule_id, capsule in self.migrating_capsules.items():
            if capsule.get("device_id") == device_id:
                result.append(capsule)
        
        return result
    
    def update_capsule_position(self, capsule_id: str, position: Dict) -> bool:
        """
        Update capsule position.
        
        Args:
            capsule_id: Capsule ID to update
            position: New position data
            
        Returns:
            Boolean indicating success
        """
        # Check if capsule exists
        capsule = self.get_capsule(capsule_id)
        if not capsule:
            logger.error(f"Capsule {capsule_id} not found")
            return False
        
        try:
            # Update position
            if capsule_id in self.active_capsules:
                self.active_capsules[capsule_id]["position"] = position
                self.active_capsules[capsule_id]["updated_at"] = time.time()
            elif capsule_id in self.suspended_capsules:
                self.suspended_capsules[capsule_id]["position"] = position
                self.suspended_capsules[capsule_id]["updated_at"] = time.time()
            elif capsule_id in self.migrating_capsules:
                self.migrating_capsules[capsule_id]["position"] = position
                self.migrating_capsules[capsule_id]["updated_at"] = time.time()
            
            # Update morphology
            self.capsule_morphology_engine.update_position(capsule_id, position)
            
            return True
        except Exception as e:
            logger.error(f"Error updating capsule position: {str(e)}")
            return False
    
    def update_capsule_morphology(self, capsule_id: str, morphology: Dict) -> bool:
        """
        Update capsule morphology.
        
        Args:
            capsule_id: Capsule ID to update
            morphology: New morphology data
            
        Returns:
            Boolean indicating success
        """
        # Check if capsule exists
        capsule = self.get_capsule(capsule_id)
        if not capsule:
            logger.error(f"Capsule {capsule_id} not found")
            return False
        
        try:
            # Update morphology
            if capsule_id in self.active_capsules:
                self.active_capsules[capsule_id]["morphology"] = morphology
                self.active_capsules[capsule_id]["updated_at"] = time.time()
            elif capsule_id in self.suspended_capsules:
                self.suspended_capsules[capsule_id]["morphology"] = morphology
                self.suspended_capsules[capsule_id]["updated_at"] = time.time()
            elif capsule_id in self.migrating_capsules:
                self.migrating_capsules[capsule_id]["morphology"] = morphology
                self.migrating_capsules[capsule_id]["updated_at"] = time.time()
            
            # Update morphology engine
            self.capsule_morphology_engine.update_morphology(capsule_id, morphology)
            
            return True
        except Exception as e:
            logger.error(f"Error updating capsule morphology: {str(e)}")
            return False
    
    def update_capsule_interactions(self, capsule_id: str, interactions: Dict) -> bool:
        """
        Update capsule interactions.
        
        Args:
            capsule_id: Capsule ID to update
            interactions: New interactions data
            
        Returns:
            Boolean indicating success
        """
        # Check if capsule exists
        capsule = self.get_capsule(capsule_id)
        if not capsule:
            logger.error(f"Capsule {capsule_id} not found")
            return False
        
        try:
            # Update interactions
            if capsule_id in self.active_capsules:
                self.active_capsules[capsule_id]["interactions"] = interactions
                self.active_capsules[capsule_id]["updated_at"] = time.time()
            elif capsule_id in self.suspended_capsules:
                self.suspended_capsules[capsule_id]["interactions"] = interactions
                self.suspended_capsules[capsule_id]["updated_at"] = time.time()
            elif capsule_id in self.migrating_capsules:
                self.migrating_capsules[capsule_id]["interactions"] = interactions
                self.migrating_capsules[capsule_id]["updated_at"] = time.time()
            
            # Update interaction controller
            self.capsule_interaction_controller.update_interactions(capsule_id, interactions)
            
            return True
        except Exception as e:
            logger.error(f"Error updating capsule interactions: {str(e)}")
            return False
    
    def restore_capsules_from_persistence(self) -> int:
        """
        Restore capsules from persisted state.
        
        Returns:
            Number of capsules restored
        """
        if not self.config["enable_state_persistence"]:
            logger.warning("State persistence is disabled, cannot restore capsules")
            return 0
        
        try:
            # Get all state files
            state_files = [
                f for f in os.listdir(self.config["capsule_state_storage_path"])
                if f.endswith(".json")
            ]
            
            restored_count = 0
            
            # Restore each capsule
            for state_file in state_files:
                try:
                    # Extract capsule ID from filename
                    capsule_id = state_file.replace(".json", "")
                    
                    # Load state data
                    state_data = self._load_persisted_capsule_state(capsule_id)
                    
                    if not state_data:
                        continue
                    
                    # Get capsule data
                    capsule_data = state_data.get("capsule_data")
                    
                    if not capsule_data:
                        continue
                    
                    # Check if capsule already exists
                    if self.get_capsule(capsule_id):
                        logger.debug(f"Capsule {capsule_id} already exists, skipping restore")
                        continue
                    
                    # Restore capsule
                    self.capsule_manager.initialize_capsule(capsule_id, capsule_data)
                    
                    # Restore memory
                    memory_data = state_data.get("memory")
                    if memory_data:
                        self.capsule_memory_manager.restore_memory(capsule_id, memory_data)
                    
                    # Restore morphology
                    morphology_data = state_data.get("morphology")
                    if morphology_data:
                        self.capsule_morphology_engine.restore_morphology(capsule_id, morphology_data)
                    
                    # Restore state
                    state = state_data.get("state")
                    if state:
                        self.capsule_state_manager.restore_state(capsule_id, state)
                    
                    # Restore interactions
                    interactions_data = state_data.get("interactions")
                    if interactions_data:
                        self.capsule_interaction_controller.restore_interactions(capsule_id, interactions_data)
                    
                    # Add to appropriate collection based on state
                    capsule_state = capsule_data.get("state")
                    
                    if capsule_state == CapsuleState.ACTIVE.value:
                        self.active_capsules[capsule_id] = capsule_data
                    elif capsule_state == CapsuleState.SUSPENDED.value:
                        self.suspended_capsules[capsule_id] = capsule_data
                    elif capsule_state == CapsuleState.MIGRATING.value:
                        # Migrating capsules should be restored as active
                        capsule_data["state"] = CapsuleState.ACTIVE.value
                        self.active_capsules[capsule_id] = capsule_data
                    
                    # Update timestamp
                    if capsule_id in self.active_capsules:
                        self.active_capsules[capsule_id]["updated_at"] = time.time()
                    elif capsule_id in self.suspended_capsules:
                        self.suspended_capsules[capsule_id]["updated_at"] = time.time()
                    
                    # Increment count
                    restored_count += 1
                    
                    logger.info(f"Restored capsule {capsule_id} from persistence")
                except Exception as e:
                    logger.error(f"Error restoring capsule from {state_file}: {str(e)}")
            
            return restored_count
        except Exception as e:
            logger.error(f"Error restoring capsules from persistence: {str(e)}")
            return 0
    
    def shutdown(self) -> None:
        """Shutdown the Capsule Lifecycle Manager."""
        logger.info("Shutting down Capsule Lifecycle Manager")
        
        # Stop worker threads
        self.running = False
        
        # Persist all capsules if enabled
        if self.config["enable_state_persistence"]:
            logger.info("Persisting capsule states before shutdown")
            
            # Persist active capsules
            for capsule_id, capsule in self.active_capsules.items():
                self._persist_capsule_state(capsule_id, capsule)
            
            # Persist suspended capsules
            for capsule_id, capsule in self.suspended_capsules.items():
                self._persist_capsule_state(capsule_id, capsule)
        
        # Wait for threads to exit
        if self.operations_thread.is_alive():
            self.operations_thread.join(timeout=2)
        
        if self.state_check_thread.is_alive():
            self.state_check_thread.join(timeout=2)
        
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=2)
        
        if hasattr(self, 'persistence_thread') and self.persistence_thread.is_alive():
            self.persistence_thread.join(timeout=2)
"""
