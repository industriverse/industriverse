"""
Capsule State Manager for Capsule Framework

This module manages the state of capsules within the Capsule Framework
of the Industriverse UI/UX Layer. It implements state tracking, persistence,
and synchronization for Dynamic Agent Capsules.

The Capsule State Manager:
1. Defines and manages capsule states and lifecycles
2. Tracks state transitions and history
3. Persists capsule states across sessions
4. Synchronizes states across devices and environments
5. Provides an API for capsule state operations

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import uuid
import threading

# Local imports
from ..context_engine.context_awareness_engine import ContextAwarenessEngine
from ..protocol_bridge.protocol_bridge import ProtocolBridge
from .capsule_memory_manager import CapsuleMemoryManager

# Configure logging
logger = logging.getLogger(__name__)

class CapsuleState(Enum):
    """Enumeration of capsule states."""
    INITIALIZING = "initializing"  # Capsule is being initialized
    ACTIVE = "active"              # Capsule is active and running
    PAUSED = "paused"              # Capsule is paused but retains state
    SUSPENDED = "suspended"        # Capsule is suspended to storage
    MIGRATING = "migrating"        # Capsule is being migrated
    FORKING = "forking"            # Capsule is being forked
    TERMINATING = "terminating"    # Capsule is being terminated
    TERMINATED = "terminated"      # Capsule has been terminated
    ERROR = "error"                # Capsule is in error state

class CapsuleStateManager:
    """
    Manages the state of capsules within the Capsule Framework.
    
    This class is responsible for implementing state tracking, persistence,
    and synchronization for Dynamic Agent Capsules.
    """
    
    def __init__(
        self, 
        context_engine: ContextAwarenessEngine,
        protocol_bridge: ProtocolBridge,
        memory_manager: CapsuleMemoryManager
    ):
        """
        Initialize the Capsule State Manager.
        
        Args:
            context_engine: The Context Awareness Engine instance
            protocol_bridge: The Protocol Bridge instance
            memory_manager: The Capsule Memory Manager instance
        """
        self.context_engine = context_engine
        self.protocol_bridge = protocol_bridge
        self.memory_manager = memory_manager
        
        # Active capsules by ID
        self.active_capsules = {}
        
        # Capsule state history
        self.state_history = {}
        
        # Capsule state change listeners
        self.state_listeners = {}
        
        # State synchronization lock
        self.state_lock = threading.RLock()
        
        # Register as context listener
        self.context_engine.register_context_listener(self._handle_context_change)
        
        # Start state synchronization thread
        self.sync_thread_running = True
        self.sync_thread = threading.Thread(target=self._state_sync_thread)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        
        logger.info("Capsule State Manager initialized")
    
    def _handle_context_change(self, event: Dict) -> None:
        """
        Handle context change events.
        
        Args:
            event: Context change event
        """
        context_type = event.get("type")
        
        # Handle device context changes
        if context_type == "device":
            device_data = event.get("data", {})
            
            # Check for device state changes
            if "device_state" in device_data:
                device_state = device_data["device_state"]
                
                # Handle device sleep/wake
                if device_state == "sleeping":
                    self._handle_device_sleep()
                elif device_state == "waking":
                    self._handle_device_wake()
        
        # Handle system context changes
        elif context_type == "system":
            system_data = event.get("data", {})
            
            # Check for system state changes
            if "system_state" in system_data:
                system_state = system_data["system_state"]
                
                # Handle system shutdown/restart
                if system_state == "shutting_down":
                    self._handle_system_shutdown()
                elif system_state == "starting":
                    self._handle_system_startup()
    
    def _handle_device_sleep(self) -> None:
        """Handle device sleep event."""
        logger.info("Device sleeping, suspending active capsules")
        
        with self.state_lock:
            # Suspend all active capsules
            for capsule_id, capsule_data in list(self.active_capsules.items()):
                if capsule_data.get("state") == CapsuleState.ACTIVE.value:
                    self.suspend_capsule(capsule_id)
    
    def _handle_device_wake(self) -> None:
        """Handle device wake event."""
        logger.info("Device waking, restoring suspended capsules")
        
        # Restore recently suspended capsules
        restored_count = 0
        
        with self.state_lock:
            for capsule_id, capsule_data in list(self.active_capsules.items()):
                if capsule_data.get("state") == CapsuleState.SUSPENDED.value:
                    # Check if suspension was recent (within last hour)
                    suspend_time = capsule_data.get("state_changed", 0)
                    if time.time() - suspend_time < 3600:  # 1 hour
                        self.activate_capsule(capsule_id)
                        restored_count += 1
        
        logger.info(f"Restored {restored_count} recently suspended capsules")
    
    def _handle_system_shutdown(self) -> None:
        """Handle system shutdown event."""
        logger.info("System shutting down, persisting all capsule states")
        
        with self.state_lock:
            # Persist all capsule states
            for capsule_id, capsule_data in list(self.active_capsules.items()):
                self._persist_capsule_state(capsule_id, capsule_data)
                
                # If active or paused, suspend first
                if capsule_data.get("state") in [CapsuleState.ACTIVE.value, CapsuleState.PAUSED.value]:
                    self.suspend_capsule(capsule_id)
    
    def _handle_system_startup(self) -> None:
        """Handle system startup event."""
        logger.info("System starting up, loading persisted capsule states")
        
        # Load persisted capsule states
        self._load_persisted_capsule_states()
    
    def _state_sync_thread(self) -> None:
        """Background thread for state synchronization."""
        while self.sync_thread_running:
            try:
                # Synchronize states with other devices
                self._sync_capsule_states()
                
                # Check for state timeouts
                self._check_state_timeouts()
                
                # Sleep for sync interval
                time.sleep(30)  # 30 seconds
            except Exception as e:
                logger.error(f"Error in state sync thread: {str(e)}")
                time.sleep(60)  # Longer sleep on error
    
    def _sync_capsule_states(self) -> None:
        """Synchronize capsule states with other devices."""
        # In a real implementation, this would sync with a central service or peer devices
        # For now, we'll just log the intent
        logger.debug("Synchronizing capsule states")
        
        # Create MCP message with state updates
        with self.state_lock:
            # Only sync active and suspended capsules
            sync_states = {}
            for capsule_id, capsule_data in self.active_capsules.items():
                if capsule_data.get("state") in [
                    CapsuleState.ACTIVE.value,
                    CapsuleState.PAUSED.value,
                    CapsuleState.SUSPENDED.value
                ]:
                    sync_states[capsule_id] = {
                        "state": capsule_data.get("state"),
                        "state_changed": capsule_data.get("state_changed"),
                        "metadata": capsule_data.get("metadata", {})
                    }
            
            if sync_states:
                # Send via Protocol Bridge
                try:
                    mcp_message = {
                        "protocol": "mcp",
                        "version": "1.0",
                        "message_id": str(uuid.uuid4()),
                        "message_type": "capsule_state_sync",
                        "source": "ui_ux_layer",
                        "destination": "all",
                        "timestamp": time.time(),
                        "payload": {
                            "device_id": self._get_device_id(),
                            "capsule_states": sync_states
                        }
                    }
                    
                    self.protocol_bridge.send_mcp_message(mcp_message)
                    logger.debug(f"Sent state sync for {len(sync_states)} capsules")
                except Exception as e:
                    logger.error(f"Failed to send state sync: {str(e)}")
    
    def _check_state_timeouts(self) -> None:
        """Check for state timeouts and take appropriate actions."""
        current_time = time.time()
        
        with self.state_lock:
            for capsule_id, capsule_data in list(self.active_capsules.items()):
                state = capsule_data.get("state")
                state_changed = capsule_data.get("state_changed", 0)
                
                # Check for stuck transitional states
                if state in [
                    CapsuleState.INITIALIZING.value,
                    CapsuleState.MIGRATING.value,
                    CapsuleState.FORKING.value,
                    CapsuleState.TERMINATING.value
                ]:
                    # If stuck for more than 5 minutes
                    if current_time - state_changed > 300:  # 5 minutes
                        logger.warning(f"Capsule {capsule_id} stuck in {state} state for >5 minutes")
                        
                        # Set to error state
                        self._update_capsule_state(
                            capsule_id, 
                            CapsuleState.ERROR.value,
                            {"error": f"Timeout in {state} state"}
                        )
                
                # Auto-suspend inactive capsules
                elif state == CapsuleState.PAUSED.value:
                    # If paused for more than 2 hours
                    if current_time - state_changed > 7200:  # 2 hours
                        logger.info(f"Auto-suspending inactive capsule {capsule_id}")
                        self.suspend_capsule(capsule_id)
    
    def _get_device_id(self) -> str:
        """
        Get current device ID.
        
        Returns:
            Device ID string
        """
        # In a real implementation, this would get a persistent device ID
        # For now, we'll use a placeholder
        return "device_1"
    
    def _persist_capsule_state(self, capsule_id: str, capsule_data: Dict) -> bool:
        """
        Persist capsule state to storage.
        
        Args:
            capsule_id: Capsule ID to persist
            capsule_data: Capsule data to persist
            
        Returns:
            Boolean indicating success
        """
        # In a real implementation, this would save to persistent storage
        # For now, we'll use the memory manager
        try:
            # Create a snapshot of the capsule state
            snapshot = {
                "capsule_id": capsule_id,
                "state": capsule_data.get("state"),
                "state_changed": capsule_data.get("state_changed"),
                "metadata": capsule_data.get("metadata", {}),
                "snapshot_time": time.time()
            }
            
            # Store in memory manager
            self.memory_manager.store_capsule_memory(
                capsule_id,
                "state_snapshot",
                snapshot
            )
            
            logger.debug(f"Persisted state for capsule {capsule_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to persist state for capsule {capsule_id}: {str(e)}")
            return False
    
    def _load_persisted_capsule_states(self) -> None:
        """Load persisted capsule states from storage."""
        # In a real implementation, this would load from persistent storage
        # For now, we'll use the memory manager
        try:
            # Get all capsule IDs with state snapshots
            capsule_ids = self.memory_manager.get_capsules_with_memory_type("state_snapshot")
            
            loaded_count = 0
            for capsule_id in capsule_ids:
                # Get latest state snapshot
                snapshot = self.memory_manager.retrieve_capsule_memory(
                    capsule_id,
                    "state_snapshot"
                )
                
                if snapshot:
                    # Create capsule from snapshot
                    with self.state_lock:
                        self.active_capsules[capsule_id] = {
                            "state": snapshot.get("state", CapsuleState.SUSPENDED.value),
                            "state_changed": snapshot.get("state_changed", time.time()),
                            "metadata": snapshot.get("metadata", {})
                        }
                    
                    loaded_count += 1
            
            logger.info(f"Loaded {loaded_count} persisted capsule states")
        except Exception as e:
            logger.error(f"Failed to load persisted capsule states: {str(e)}")
    
    def create_capsule(self, metadata: Dict) -> str:
        """
        Create a new capsule.
        
        Args:
            metadata: Metadata for the new capsule
            
        Returns:
            New capsule ID
        """
        # Generate new capsule ID
        capsule_id = str(uuid.uuid4())
        
        # Initialize capsule data
        capsule_data = {
            "state": CapsuleState.INITIALIZING.value,
            "state_changed": time.time(),
            "metadata": metadata
        }
        
        # Add to active capsules
        with self.state_lock:
            self.active_capsules[capsule_id] = capsule_data
            
            # Initialize state history
            self.state_history[capsule_id] = [{
                "state": CapsuleState.INITIALIZING.value,
                "timestamp": time.time(),
                "metadata": metadata
            }]
        
        logger.info(f"Created new capsule {capsule_id}")
        
        # Notify listeners
        self._notify_state_listeners(capsule_id, CapsuleState.INITIALIZING.value, metadata)
        
        return capsule_id
    
    def activate_capsule(self, capsule_id: str) -> bool:
        """
        Activate a capsule.
        
        Args:
            capsule_id: Capsule ID to activate
            
        Returns:
            Boolean indicating success
        """
        with self.state_lock:
            # Verify capsule exists
            if capsule_id not in self.active_capsules:
                logger.error(f"Capsule {capsule_id} not found")
                return False
            
            # Get current state
            current_state = self.active_capsules[capsule_id].get("state")
            
            # Check if activation is allowed from current state
            if current_state not in [
                CapsuleState.INITIALIZING.value,
                CapsuleState.PAUSED.value,
                CapsuleState.SUSPENDED.value
            ]:
                logger.error(f"Cannot activate capsule {capsule_id} from state {current_state}")
                return False
            
            # Update state
            self._update_capsule_state(capsule_id, CapsuleState.ACTIVE.value)
        
        logger.info(f"Activated capsule {capsule_id}")
        return True
    
    def pause_capsule(self, capsule_id: str) -> bool:
        """
        Pause a capsule.
        
        Args:
            capsule_id: Capsule ID to pause
            
        Returns:
            Boolean indicating success
        """
        with self.state_lock:
            # Verify capsule exists
            if capsule_id not in self.active_capsules:
                logger.error(f"Capsule {capsule_id} not found")
                return False
            
            # Get current state
            current_state = self.active_capsules[capsule_id].get("state")
            
            # Check if pause is allowed from current state
            if current_state != CapsuleState.ACTIVE.value:
                logger.error(f"Cannot pause capsule {capsule_id} from state {current_state}")
                return False
            
            # Update state
            self._update_capsule_state(capsule_id, CapsuleState.PAUSED.value)
        
        logger.info(f"Paused capsule {capsule_id}")
        return True
    
    def suspend_capsule(self, capsule_id: str) -> bool:
        """
        Suspend a capsule.
        
        Args:
            capsule_id: Capsule ID to suspend
            
        Returns:
            Boolean indicating success
        """
        with self.state_lock:
            # Verify capsule exists
            if capsule_id not in self.active_capsules:
                logger.error(f"Capsule {capsule_id} not found")
                return False
            
            # Get current state
            current_state = self.active_capsules[capsule_id].get("state")
            
            # Check if suspension is allowed from current state
            if current_state not in [
                CapsuleState.ACTIVE.value,
                CapsuleState.PAUSED.value
            ]:
                logger.error(f"Cannot suspend capsule {capsule_id} from state {current_state}")
                return False
            
            # Get capsule data
            capsule_data = self.active_capsules[capsule_id]
            
            # Persist state before suspending
            self._persist_capsule_state(capsule_id, capsule_data)
            
            # Update state
            self._update_capsule_state(capsule_id, CapsuleState.SUSPENDED.value)
        
        logger.info(f"Suspended capsule {capsule_id}")
        return True
    
    def migrate_capsule(self, capsule_id: str, target_device: str) -> bool:
        """
        Migrate a capsule to another device.
        
        Args:
            capsule_id: Capsule ID to migrate
            target_device: Target device ID
            
        Returns:
            Boolean indicating success
        """
        with self.state_lock:
            # Verify capsule exists
            if capsule_id not in self.active_capsules:
                logger.error(f"Capsule {capsule_id} not found")
                return False
            
            # Get current state
            current_state = self.active_capsules[capsule_id].get("state")
            
            # Check if migration is allowed from current state
            if current_state not in [
                CapsuleState.ACTIVE.value,
                CapsuleState.PAUSED.value
            ]:
                logger.error(f"Cannot migrate capsule {capsule_id} from state {current_state}")
                return False
            
            # Update state
            self._update_capsule_state(
                capsule_id, 
                CapsuleState.MIGRATING.value,
                {"target_device": target_device}
            )
            
            # Get capsule data
            capsule_data = self.active_capsules[capsule_id]
            
            # Create migration package
            migration_package = {
                "capsule_id": capsule_id,
                "source_device": self._get_device_id(),
                "target_device": target_device,
                "state": CapsuleState.ACTIVE.value,  # Target state after migration
                "metadata": capsule_data.get("metadata", {}),
                "memory": self.memory_manager.get_all_capsule_memory(capsule_id),
                "timestamp": time.time()
            }
            
            # Send migration package via MCP
            try:
                mcp_message = {
                    "protocol": "mcp",
                    "version": "1.0",
                    "message_id": str(uuid.uuid4()),
                    "message_type": "capsule_migration",
                    "source": "ui_ux_layer",
                    "destination": f"ui_ux_layer.{target_device}",
                    "timestamp": time.time(),
                    "payload": migration_package
                }
                
                self.protocol_bridge.send_mcp_message(mcp_message)
                
                # Update state to terminated (on this device)
                self._update_capsule_state(
                    capsule_id, 
                    CapsuleState.TERMINATED.value,
                    {"reason": "migrated", "target_device": target_device}
                )
                
                logger.info(f"Migrated capsule {capsule_id} to device {target_device}")
                return True
            except Exception as e:
                logger.error(f"Failed to migrate capsule {capsule_id}: {str(e)}")
                
                # Revert to previous state
                self._update_capsule_state(
                    capsule_id, 
                    current_state,
                    {"error": f"Migration failed: {str(e)}"}
                )
                
                return False
    
    def fork_capsule(self, capsule_id: str) -> Optional[str]:
        """
        Fork a capsule to create a new instance.
        
        Args:
            capsule_id: Capsule ID to fork
            
        Returns:
            New capsule ID if successful, None otherwise
        """
        with self.state_lock:
            # Verify capsule exists
            if capsule_id not in self.active_capsules:
                logger.error(f"Capsule {capsule_id} not found")
                return None
            
            # Get current state
            current_state = self.active_capsules[capsule_id].get("state")
            
            # Check if forking is allowed from current state
            if current_state not in [
                CapsuleState.ACTIVE.value,
                CapsuleState.PAUSED.value
            ]:
                logger.error(f"Cannot fork capsule {capsule_id} from state {current_state}")
                return None
            
            # Update state
            self._update_capsule_state(
                capsule_id, 
                CapsuleState.FORKING.value
            )
            
            # Get capsule data
            capsule_data = self.active_capsules[capsule_id]
            
            try:
                # Create new capsule ID
                new_capsule_id = str(uuid.uuid4())
                
                # Clone metadata
                new_metadata = capsule_data.get("metadata", {}).copy()
                new_metadata["forked_from"] = capsule_id
                new_metadata["fork_time"] = time.time()
                
                # Create new capsule
                self.active_capsules[new_capsule_id] = {
                    "state": CapsuleState.INITIALIZING.value,
                    "state_changed": time.time(),
                    "metadata": new_metadata
                }
                
                # Initialize state history
                self.state_history[new_capsule_id] = [{
                    "state": CapsuleState.INITIALIZING.value,
                    "timestamp": time.time(),
                    "metadata": new_metadata
                }]
                
                # Clone memory
                self.memory_manager.clone_capsule_memory(capsule_id, new_capsule_id)
                
                # Restore original capsule state
                self._update_capsule_state(capsule_id, current_state)
                
                # Activate new capsule
                self._update_capsule_state(new_capsule_id, CapsuleState.ACTIVE.value)
                
                logger.info(f"Forked capsule {capsule_id} to new capsule {new_capsule_id}")
                
                # Notify listeners for new capsule
                self._notify_state_listeners(
                    new_capsule_id, 
                    CapsuleState.ACTIVE.value, 
                    new_metadata
                )
                
                return new_capsule_id
            except Exception as e:
                logger.error(f"Failed to fork capsule {capsule_id}: {str(e)}")
                
                # Revert to previous state
                self._update_capsule_state(
                    capsule_id, 
                    current_state,
                    {"error": f"Fork failed: {str(e)}"}
                )
                
                return None
    
    def terminate_capsule(self, capsule_id: str) -> bool:
        """
        Terminate a capsule.
        
        Args:
            capsule_id: Capsule ID to terminate
            
        Returns:
            Boolean indicating success
        """
        with self.state_lock:
            # Verify capsule exists
            if capsule_id not in self.active_capsules:
                logger.error(f"Capsule {capsule_id} not found")
                return False
            
            # Get current state
            current_state = self.active_capsules[capsule_id].get("state")
            
            # Check if termination is allowed from current state
            if current_state == CapsuleState.TERMINATED.value:
                logger.error(f"Capsule {capsule_id} already terminated")
                return False
            
            # Update state
            self._update_capsule_state(
                capsule_id, 
                CapsuleState.TERMINATING.value
            )
            
            try:
                # Perform cleanup
                self.memory_manager.clear_capsule_memory(capsule_id)
                
                # Update state to terminated
                self._update_capsule_state(
                    capsule_id, 
                    CapsuleState.TERMINATED.value,
                    {"reason": "user_terminated"}
                )
                
                logger.info(f"Terminated capsule {capsule_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to terminate capsule {capsule_id}: {str(e)}")
                
                # Set to error state
                self._update_capsule_state(
                    capsule_id, 
                    CapsuleState.ERROR.value,
                    {"error": f"Termination failed: {str(e)}"}
                )
                
                return False
    
    def _update_capsule_state(self, capsule_id: str, state: str, metadata_updates: Dict = None) -> None:
        """
        Update capsule state.
        
        Args:
            capsule_id: Capsule ID to update
            state: New state
            metadata_updates: Optional metadata updates
        """
        with self.state_lock:
            # Verify capsule exists
            if capsule_id not in self.active_capsules:
                logger.error(f"Capsule {capsule_id} not found")
                return
            
            # Get current capsule data
            capsule_data = self.active_capsules[capsule_id]
            
            # Update state
            capsule_data["state"] = state
            capsule_data["state_changed"] = time.time()
            
            # Update metadata if provided
            if metadata_updates:
                if "metadata" not in capsule_data:
                    capsule_data["metadata"] = {}
                
                capsule_data["metadata"].update(metadata_updates)
            
            # Update state history
            if capsule_id not in self.state_history:
                self.state_history[capsule_id] = []
            
            self.state_history[capsule_id].append({
                "state": state,
                "timestamp": time.time(),
                "metadata": metadata_updates
            })
            
            # Limit history length
            if len(self.state_history[capsule_id]) > 20:
                self.state_history[capsule_id].pop(0)
        
        # Notify listeners
        self._notify_state_listeners(capsule_id, state, metadata_updates)
    
    def _notify_state_listeners(self, capsule_id: str, state: str, metadata: Dict = None) -> None:
        """
        Notify state change listeners.
        
        Args:
            capsule_id: Capsule ID that changed
            state: New state
            metadata: Optional metadata
        """
        # Notify global listeners
        if "global" in self.state_listeners:
            for listener in self.state_listeners["global"]:
                try:
                    listener(capsule_id, state, metadata)
                except Exception as e:
                    logger.error(f"Error in global state listener: {str(e)}")
        
        # Notify capsule-specific listeners
        if capsule_id in self.state_listeners:
            for listener in self.state_listeners[capsule_id]:
                try:
                    listener(capsule_id, state, metadata)
                except Exception as e:
                    logger.error(f"Error in capsule state listener: {str(e)}")
    
    def register_state_listener(self, listener: callable, capsule_id: str = "global") -> bool:
        """
        Register a state change listener.
        
        Args:
            listener: Callback function to register
            capsule_id: Capsule ID to listen for, or "global" for all capsules
            
        Returns:
            Boolean indicating success
        """
        if capsule_id not in self.state_listeners:
            self.state_listeners[capsule_id] = []
        
        if listener not in self.state_listeners[capsule_id]:
            self.state_listeners[capsule_id].append(listener)
            logger.debug(f"Registered state listener for {capsule_id}")
            return True
        
        return False
    
    def unregister_state_listener(self, listener: callable, capsule_id: str = "global") -> bool:
        """
        Unregister a state change listener.
        
        Args:
            listener: Callback function to unregister
            capsule_id: Capsule ID the listener was registered for
            
        Returns:
            Boolean indicating success
        """
        if capsule_id in self.state_listeners and listener in self.state_listeners[capsule_id]:
            self.state_listeners[capsule_id].remove(listener)
            logger.debug(f"Unregistered state listener for {capsule_id}")
            return True
        
        return False
    
    def get_capsule_state(self, capsule_id: str) -> Dict:
        """
        Get current state for a capsule.
        
        Args:
            capsule_id: Capsule ID to get state for
            
        Returns:
            Capsule state information dictionary
        """
        with self.state_lock:
            if capsule_id not in self.active_capsules:
                return {}
            
            capsule_data = self.active_capsules[capsule_id]
            
            return {
                "capsule_id": capsule_id,
                "state": capsule_data.get("state"),
                "state_changed": capsule_data.get("state_changed"),
                "metadata": capsule_data.get("metadata", {})
            }
    
    def get_capsule_state_history(self, capsule_id: str) -> List[Dict]:
        """
        Get state history for a capsule.
        
        Args:
            capsule_id: Capsule ID to get history for
            
        Returns:
            List of state history records
        """
        with self.state_lock:
            if capsule_id not in self.state_history:
                return []
            
            return self.state_history[capsule_id]
    
    def get_active_capsules(self, filter_state: str = None) -> List[Dict]:
        """
        Get all active capsules.
        
        Args:
            filter_state: Optional state to filter by
            
        Returns:
            List of capsule information dictionaries
        """
        capsules = []
        
        with self.state_lock:
            for capsule_id, capsule_data in self.active_capsules.items():
                state = capsule_data.get("state")
                
                # Skip terminated capsules
                if state == CapsuleState.TERMINATED.value:
                    continue
                
                # Apply state filter if specified
                if filter_state and state != filter_state:
                    continue
                
                capsules.append({
                    "capsule_id": capsule_id,
                    "state": state,
                    "state_changed": capsule_data.get("state_changed"),
                    "metadata": capsule_data.get("metadata", {})
                })
        
        return capsules
    
    def update_capsule_metadata(self, capsule_id: str, metadata_updates: Dict) -> bool:
        """
        Update metadata for a capsule.
        
        Args:
            capsule_id: Capsule ID to update
            metadata_updates: Metadata updates to apply
            
        Returns:
            Boolean indicating success
        """
        with self.state_lock:
            # Verify capsule exists
            if capsule_id not in self.active_capsules:
                logger.error(f"Capsule {capsule_id} not found")
                return False
            
            # Get current capsule data
            capsule_data = self.active_capsules[capsule_id]
            
            # Update metadata
            if "metadata" not in capsule_data:
                capsule_data["metadata"] = {}
            
            capsule_data["metadata"].update(metadata_updates)
            
            logger.debug(f"Updated metadata for capsule {capsule_id}")
            return True
    
    def handle_mcp_message(self, message: Dict) -> None:
        """
        Handle incoming MCP messages.
        
        Args:
            message: The MCP message to handle
        """
        message_type = message.get("message_type")
        
        # Handle capsule migration messages
        if message_type == "capsule_migration":
            payload = message.get("payload", {})
            
            # Check if this device is the target
            target_device = payload.get("target_device")
            if target_device == self._get_device_id():
                self._handle_capsule_migration(payload)
        
        # Handle capsule state sync messages
        elif message_type == "capsule_state_sync":
            payload = message.get("payload", {})
            
            # Check if this is from another device
            device_id = payload.get("device_id")
            if device_id != self._get_device_id():
                self._handle_capsule_state_sync(payload)
    
    def _handle_capsule_migration(self, migration_package: Dict) -> None:
        """
        Handle incoming capsule migration.
        
        Args:
            migration_package: Migration package data
        """
        capsule_id = migration_package.get("capsule_id")
        source_device = migration_package.get("source_device")
        
        logger.info(f"Received capsule migration for {capsule_id} from device {source_device}")
        
        try:
            # Create or update capsule
            with self.state_lock:
                # Initialize capsule data
                self.active_capsules[capsule_id] = {
                    "state": CapsuleState.INITIALIZING.value,
                    "state_changed": time.time(),
                    "metadata": migration_package.get("metadata", {})
                }
                
                # Initialize state history
                self.state_history[capsule_id] = [{
                    "state": CapsuleState.INITIALIZING.value,
                    "timestamp": time.time(),
                    "metadata": {"migrated_from": source_device}
                }]
            
            # Restore memory
            memory_data = migration_package.get("memory", {})
            for memory_type, memory_content in memory_data.items():
                self.memory_manager.store_capsule_memory(
                    capsule_id,
                    memory_type,
                    memory_content
                )
            
            # Activate capsule
            target_state = migration_package.get("state", CapsuleState.ACTIVE.value)
            self._update_capsule_state(
                capsule_id, 
                target_state,
                {"migrated_from": source_device}
            )
            
            logger.info(f"Successfully migrated capsule {capsule_id} from device {source_device}")
            
            # Send acknowledgement
            self._send_migration_ack(capsule_id, source_device, True)
        except Exception as e:
            logger.error(f"Failed to handle capsule migration: {str(e)}")
            
            # Send failure acknowledgement
            self._send_migration_ack(capsule_id, source_device, False, str(e))
    
    def _send_migration_ack(
        self, 
        capsule_id: str, 
        target_device: str, 
        success: bool, 
        error: str = None
    ) -> None:
        """
        Send migration acknowledgement.
        
        Args:
            capsule_id: Capsule ID that was migrated
            target_device: Device to send acknowledgement to
            success: Whether migration was successful
            error: Optional error message
        """
        try:
            mcp_message = {
                "protocol": "mcp",
                "version": "1.0",
                "message_id": str(uuid.uuid4()),
                "message_type": "capsule_migration_ack",
                "source": "ui_ux_layer",
                "destination": f"ui_ux_layer.{target_device}",
                "timestamp": time.time(),
                "payload": {
                    "capsule_id": capsule_id,
                    "success": success,
                    "error": error,
                    "device_id": self._get_device_id()
                }
            }
            
            self.protocol_bridge.send_mcp_message(mcp_message)
            logger.debug(f"Sent migration acknowledgement for capsule {capsule_id}")
        except Exception as e:
            logger.error(f"Failed to send migration acknowledgement: {str(e)}")
    
    def _handle_capsule_state_sync(self, sync_data: Dict) -> None:
        """
        Handle incoming capsule state sync.
        
        Args:
            sync_data: State sync data
        """
        device_id = sync_data.get("device_id")
        capsule_states = sync_data.get("capsule_states", {})
        
        logger.debug(f"Received state sync for {len(capsule_states)} capsules from device {device_id}")
        
        with self.state_lock:
            for capsule_id, state_data in capsule_states.items():
                # Check if we have this capsule
                if capsule_id in self.active_capsules:
                    # Get local and remote timestamps
                    local_changed = self.active_capsules[capsule_id].get("state_changed", 0)
                    remote_changed = state_data.get("state_changed", 0)
                    
                    # Only update if remote state is newer
                    if remote_changed > local_changed:
                        # Update local state
                        self.active_capsules[capsule_id].update({
                            "state": state_data.get("state"),
                            "state_changed": remote_changed,
                            "metadata": state_data.get("metadata", {})
                        })
                        
                        # Add to state history
                        if capsule_id not in self.state_history:
                            self.state_history[capsule_id] = []
                        
                        self.state_history[capsule_id].append({
                            "state": state_data.get("state"),
                            "timestamp": time.time(),
                            "metadata": {"synced_from": device_id}
                        })
                        
                        # Limit history length
                        if len(self.state_history[capsule_id]) > 20:
                            self.state_history[capsule_id].pop(0)
                        
                        # Notify listeners
                        self._notify_state_listeners(
                            capsule_id, 
                            state_data.get("state"), 
                            {"synced_from": device_id}
                        )
                else:
                    # This is a new capsule from another device
                    # Only add if it's in an active or suspended state
                    state = state_data.get("state")
                    if state in [
                        CapsuleState.ACTIVE.value,
                        CapsuleState.PAUSED.value,
                        CapsuleState.SUSPENDED.value
                    ]:
                        # Add to active capsules
                        self.active_capsules[capsule_id] = {
                            "state": state,
                            "state_changed": state_data.get("state_changed", time.time()),
                            "metadata": state_data.get("metadata", {})
                        }
                        
                        # Initialize state history
                        self.state_history[capsule_id] = [{
                            "state": state,
                            "timestamp": time.time(),
                            "metadata": {"synced_from": device_id}
                        }]
                        
                        # Notify listeners
                        self._notify_state_listeners(
                            capsule_id, 
                            state, 
                            {"synced_from": device_id}
                        )
    
    def shutdown(self) -> None:
        """Shutdown the Capsule State Manager."""
        logger.info("Shutting down Capsule State Manager")
        
        # Stop sync thread
        self.sync_thread_running = False
        if self.sync_thread.is_alive():
            self.sync_thread.join(timeout=2)
        
        # Persist all capsule states
        with self.state_lock:
            for capsule_id, capsule_data in list(self.active_capsules.items()):
                self._persist_capsule_state(capsule_id, capsule_data)
"""
