"""
Capsule Memory Manager for Capsule Framework

This module manages the memory and state persistence of Agent Capsules
within the Industriverse UI/UX Layer. It implements the storage, retrieval,
and synchronization of capsule state across sessions and devices.

The Capsule Memory Manager:
1. Stores and retrieves capsule state and memory
2. Manages persistence across sessions and devices
3. Implements memory compression and prioritization
4. Provides an API for capsule memory operations
5. Coordinates with the Context Engine for context-aware memory

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import os
import hashlib

# Local imports
from ..context_engine.context_engine import ContextEngine
from ..protocol_bridge.protocol_bridge import ProtocolBridge

# Configure logging
logger = logging.getLogger(__name__)

class MemoryPriority(Enum):
    """Enumeration of memory priority levels for capsule memory."""
    CRITICAL = "critical"       # Essential memory that must be preserved
    HIGH = "high"               # Important memory with high retention
    MEDIUM = "medium"           # Standard memory with normal retention
    LOW = "low"                 # Less important memory that can be compressed or discarded
    TRANSIENT = "transient"     # Temporary memory that doesn't need persistence

class MemoryScope(Enum):
    """Enumeration of memory scopes for capsule memory."""
    GLOBAL = "global"           # Available across all sessions and devices
    USER = "user"               # Available for a specific user across devices
    SESSION = "session"         # Available only for the current session
    DEVICE = "device"           # Available only on the current device
    EPHEMERAL = "ephemeral"     # Not persisted beyond current use

class CapsuleMemoryManager:
    """
    Manages the memory and state persistence of Agent Capsules.
    
    This class is responsible for storing, retrieving, and synchronizing
    capsule state and memory across sessions and devices within the
    Industriverse UI/UX Layer.
    """
    
    def __init__(
        self, 
        context_engine: ContextEngine,
        protocol_bridge: ProtocolBridge,
        storage_path: str = None
    ):
        """
        Initialize the Capsule Memory Manager.
        
        Args:
            context_engine: The Context Engine instance for context awareness
            protocol_bridge: The Protocol Bridge instance for remote synchronization
            storage_path: Optional path for local storage
        """
        self.context_engine = context_engine
        self.protocol_bridge = protocol_bridge
        
        # Set storage path
        self.storage_path = storage_path or os.path.join(os.path.dirname(__file__), "../../data/capsule_memory")
        os.makedirs(self.storage_path, exist_ok=True)
        
        # In-memory cache of capsule memory
        self.memory_cache = {}
        
        # Memory retention policies
        self.retention_policies = self._load_retention_policies()
        
        # Memory compression settings
        self.compression_settings = self._load_compression_settings()
        
        # Synchronization status
        self.sync_status = {}
        
        # Memory access history
        self.access_history = {}
        
        logger.info("Capsule Memory Manager initialized")
    
    def _load_retention_policies(self) -> Dict:
        """
        Load memory retention policies.
        
        Returns:
            Dictionary of retention policies
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard retention policies inline
        
        return {
            MemoryPriority.CRITICAL.value: {
                "retention_period": None,  # Indefinite
                "compression_threshold": None,  # Never compress
                "sync_priority": 1,  # Highest priority
                "backup_count": 3  # Number of backups to maintain
            },
            MemoryPriority.HIGH.value: {
                "retention_period": 365 * 24 * 60 * 60,  # 1 year in seconds
                "compression_threshold": 90 * 24 * 60 * 60,  # 90 days in seconds
                "sync_priority": 2,
                "backup_count": 2
            },
            MemoryPriority.MEDIUM.value: {
                "retention_period": 90 * 24 * 60 * 60,  # 90 days in seconds
                "compression_threshold": 30 * 24 * 60 * 60,  # 30 days in seconds
                "sync_priority": 3,
                "backup_count": 1
            },
            MemoryPriority.LOW.value: {
                "retention_period": 30 * 24 * 60 * 60,  # 30 days in seconds
                "compression_threshold": 7 * 24 * 60 * 60,  # 7 days in seconds
                "sync_priority": 4,
                "backup_count": 0
            },
            MemoryPriority.TRANSIENT.value: {
                "retention_period": 24 * 60 * 60,  # 1 day in seconds
                "compression_threshold": 1 * 60 * 60,  # 1 hour in seconds
                "sync_priority": 5,  # Lowest priority
                "backup_count": 0
            }
        }
    
    def _load_compression_settings(self) -> Dict:
        """
        Load memory compression settings.
        
        Returns:
            Dictionary of compression settings
        """
        # In a production environment, this would load from a configuration file or service
        # For now, we'll define standard compression settings inline
        
        return {
            "enabled": True,
            "algorithms": {
                "json_minify": {
                    "enabled": True,
                    "level": 1
                },
                "key_abbreviation": {
                    "enabled": True,
                    "abbreviations": {
                        "timestamp": "ts",
                        "description": "desc",
                        "priority": "pri",
                        "metadata": "meta",
                        "confidence": "conf",
                        "decision": "dec",
                        "explanation": "exp"
                    }
                },
                "value_summarization": {
                    "enabled": True,
                    "max_string_length": 100,
                    "summarize_arrays": True,
                    "max_array_items": 10
                }
            },
            "thresholds": {
                "size_threshold": 1024 * 10,  # 10 KB
                "age_threshold": 7 * 24 * 60 * 60  # 7 days in seconds
            }
        }
    
    def store_memory(
        self, 
        capsule_id: str, 
        memory_data: Dict, 
        priority: str = MemoryPriority.MEDIUM.value,
        scope: str = MemoryScope.USER.value,
        tags: List[str] = None
    ) -> bool:
        """
        Store memory data for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to store memory for
            memory_data: The memory data to store
            priority: The priority level of the memory
            scope: The scope of the memory
            tags: Optional tags for categorizing the memory
            
        Returns:
            Boolean indicating success
        """
        # Verify priority is valid
        if priority not in [p.value for p in MemoryPriority]:
            logger.error(f"Invalid memory priority: {priority}")
            return False
        
        # Verify scope is valid
        if scope not in [s.value for s in MemoryScope]:
            logger.error(f"Invalid memory scope: {scope}")
            return False
        
        # Add metadata to memory data
        memory_entry = {
            "data": memory_data,
            "metadata": {
                "timestamp": time.time(),
                "priority": priority,
                "scope": scope,
                "tags": tags or [],
                "version": 1,
                "hash": self._generate_memory_hash(memory_data)
            }
        }
        
        # Initialize capsule memory if not exists
        if capsule_id not in self.memory_cache:
            self.memory_cache[capsule_id] = []
        
        # Add memory entry to cache
        self.memory_cache[capsule_id].append(memory_entry)
        
        # Record access
        self._record_memory_access(capsule_id, "write")
        
        # Persist memory based on scope
        if scope != MemoryScope.EPHEMERAL.value:
            self._persist_memory(capsule_id, memory_entry)
        
        # Synchronize memory based on scope and priority
        if scope in [MemoryScope.GLOBAL.value, MemoryScope.USER.value]:
            self._schedule_memory_sync(capsule_id, memory_entry)
        
        logger.info(f"Stored memory for capsule {capsule_id} with priority {priority} and scope {scope}")
        return True
    
    def retrieve_memory(
        self, 
        capsule_id: str, 
        query: Dict = None, 
        limit: int = None,
        include_metadata: bool = False
    ) -> List[Dict]:
        """
        Retrieve memory data for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to retrieve memory for
            query: Optional query parameters for filtering memory
            limit: Optional maximum number of memory entries to retrieve
            include_metadata: Whether to include metadata in the results
            
        Returns:
            List of memory entries
        """
        # Check if capsule has memory
        if capsule_id not in self.memory_cache:
            # Try to load from persistent storage
            self._load_memory_from_storage(capsule_id)
            
            # If still not found, return empty list
            if capsule_id not in self.memory_cache:
                return []
        
        # Get memory entries
        memory_entries = self.memory_cache[capsule_id]
        
        # Filter by query if provided
        if query:
            filtered_entries = []
            for entry in memory_entries:
                match = True
                
                # Check metadata filters
                if "metadata" in query:
                    for key, value in query["metadata"].items():
                        if key not in entry["metadata"] or entry["metadata"][key] != value:
                            match = False
                            break
                
                # Check data filters
                if "data" in query:
                    for key, value in query["data"].items():
                        if key not in entry["data"] or entry["data"][key] != value:
                            match = False
                            break
                
                # Check tag filters
                if "tags" in query:
                    for tag in query["tags"]:
                        if tag not in entry["metadata"].get("tags", []):
                            match = False
                            break
                
                # Check time range filter
                if "time_range" in query:
                    time_range = query["time_range"]
                    timestamp = entry["metadata"]["timestamp"]
                    
                    if "start" in time_range and timestamp < time_range["start"]:
                        match = False
                    
                    if "end" in time_range and timestamp > time_range["end"]:
                        match = False
                
                if match:
                    filtered_entries.append(entry)
            
            memory_entries = filtered_entries
        
        # Sort by timestamp (newest first)
        memory_entries.sort(key=lambda x: x["metadata"]["timestamp"], reverse=True)
        
        # Apply limit if provided
        if limit:
            memory_entries = memory_entries[:limit]
        
        # Record access
        self._record_memory_access(capsule_id, "read")
        
        # Format results
        if include_metadata:
            return memory_entries
        else:
            return [entry["data"] for entry in memory_entries]
    
    def update_memory(
        self, 
        capsule_id: str, 
        memory_id: str, 
        updated_data: Dict,
        update_metadata: Dict = None
    ) -> bool:
        """
        Update existing memory data for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to update memory for
            memory_id: The ID or hash of the memory entry to update
            updated_data: The updated memory data
            update_metadata: Optional metadata updates
            
        Returns:
            Boolean indicating success
        """
        # Check if capsule has memory
        if capsule_id not in self.memory_cache:
            logger.error(f"No memory found for capsule {capsule_id}")
            return False
        
        # Find memory entry by ID or hash
        found = False
        for i, entry in enumerate(self.memory_cache[capsule_id]):
            entry_hash = entry["metadata"]["hash"]
            
            if entry_hash == memory_id:
                # Update data
                self.memory_cache[capsule_id][i]["data"] = updated_data
                
                # Update metadata if provided
                if update_metadata:
                    for key, value in update_metadata.items():
                        self.memory_cache[capsule_id][i]["metadata"][key] = value
                
                # Update version and hash
                self.memory_cache[capsule_id][i]["metadata"]["version"] += 1
                self.memory_cache[capsule_id][i]["metadata"]["hash"] = self._generate_memory_hash(updated_data)
                
                # Record access
                self._record_memory_access(capsule_id, "update")
                
                # Persist updated memory
                scope = self.memory_cache[capsule_id][i]["metadata"]["scope"]
                if scope != MemoryScope.EPHEMERAL.value:
                    self._persist_memory(capsule_id, self.memory_cache[capsule_id][i])
                
                # Synchronize updated memory
                if scope in [MemoryScope.GLOBAL.value, MemoryScope.USER.value]:
                    self._schedule_memory_sync(capsule_id, self.memory_cache[capsule_id][i])
                
                found = True
                break
        
        if not found:
            logger.error(f"Memory entry with ID {memory_id} not found for capsule {capsule_id}")
            return False
        
        logger.info(f"Updated memory for capsule {capsule_id}")
        return True
    
    def delete_memory(
        self, 
        capsule_id: str, 
        memory_id: str = None,
        query: Dict = None
    ) -> bool:
        """
        Delete memory data for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to delete memory for
            memory_id: Optional ID or hash of the specific memory entry to delete
            query: Optional query parameters for filtering memory to delete
            
        Returns:
            Boolean indicating success
        """
        # Check if capsule has memory
        if capsule_id not in self.memory_cache:
            logger.error(f"No memory found for capsule {capsule_id}")
            return False
        
        # Delete specific memory entry if ID provided
        if memory_id:
            found = False
            for i, entry in enumerate(self.memory_cache[capsule_id]):
                entry_hash = entry["metadata"]["hash"]
                
                if entry_hash == memory_id:
                    # Remove entry
                    deleted_entry = self.memory_cache[capsule_id].pop(i)
                    
                    # Record access
                    self._record_memory_access(capsule_id, "delete")
                    
                    # Delete from persistent storage
                    scope = deleted_entry["metadata"]["scope"]
                    if scope != MemoryScope.EPHEMERAL.value:
                        self._delete_persisted_memory(capsule_id, deleted_entry)
                    
                    # Synchronize deletion
                    if scope in [MemoryScope.GLOBAL.value, MemoryScope.USER.value]:
                        self._schedule_memory_deletion_sync(capsule_id, deleted_entry)
                    
                    found = True
                    break
            
            if not found:
                logger.error(f"Memory entry with ID {memory_id} not found for capsule {capsule_id}")
                return False
        
        # Delete memory entries matching query if provided
        elif query:
            deleted_count = 0
            entries_to_delete = []
            
            # Identify entries to delete
            for entry in self.memory_cache[capsule_id]:
                match = True
                
                # Check metadata filters
                if "metadata" in query:
                    for key, value in query["metadata"].items():
                        if key not in entry["metadata"] or entry["metadata"][key] != value:
                            match = False
                            break
                
                # Check data filters
                if "data" in query:
                    for key, value in query["data"].items():
                        if key not in entry["data"] or entry["data"][key] != value:
                            match = False
                            break
                
                # Check tag filters
                if "tags" in query:
                    for tag in query["tags"]:
                        if tag not in entry["metadata"].get("tags", []):
                            match = False
                            break
                
                # Check time range filter
                if "time_range" in query:
                    time_range = query["time_range"]
                    timestamp = entry["metadata"]["timestamp"]
                    
                    if "start" in time_range and timestamp < time_range["start"]:
                        match = False
                    
                    if "end" in time_range and timestamp > time_range["end"]:
                        match = False
                
                if match:
                    entries_to_delete.append(entry)
            
            # Delete identified entries
            for entry in entries_to_delete:
                self.memory_cache[capsule_id].remove(entry)
                
                # Delete from persistent storage
                scope = entry["metadata"]["scope"]
                if scope != MemoryScope.EPHEMERAL.value:
                    self._delete_persisted_memory(capsule_id, entry)
                
                # Synchronize deletion
                if scope in [MemoryScope.GLOBAL.value, MemoryScope.USER.value]:
                    self._schedule_memory_deletion_sync(capsule_id, entry)
                
                deleted_count += 1
            
            # Record access
            if deleted_count > 0:
                self._record_memory_access(capsule_id, "delete")
            
            if deleted_count == 0:
                logger.warning(f"No memory entries matched query for capsule {capsule_id}")
                return False
        
        # Delete all memory for the capsule if no ID or query provided
        else:
            # Record access
            self._record_memory_access(capsule_id, "delete")
            
            # Delete all entries from persistent storage
            for entry in self.memory_cache[capsule_id]:
                scope = entry["metadata"]["scope"]
                if scope != MemoryScope.EPHEMERAL.value:
                    self._delete_persisted_memory(capsule_id, entry)
                
                # Synchronize deletion
                if scope in [MemoryScope.GLOBAL.value, MemoryScope.USER.value]:
                    self._schedule_memory_deletion_sync(capsule_id, entry)
            
            # Clear memory cache
            self.memory_cache[capsule_id] = []
        
        logger.info(f"Deleted memory for capsule {capsule_id}")
        return True
    
    def _generate_memory_hash(self, memory_data: Dict) -> str:
        """
        Generate a hash for memory data.
        
        Args:
            memory_data: The memory data to hash
            
        Returns:
            Hash string
        """
        # Convert data to JSON string
        json_str = json.dumps(memory_data, sort_keys=True)
        
        # Generate hash
        hash_obj = hashlib.sha256(json_str.encode())
        return hash_obj.hexdigest()
    
    def _persist_memory(self, capsule_id: str, memory_entry: Dict) -> bool:
        """
        Persist memory to storage.
        
        Args:
            capsule_id: The ID of the capsule
            memory_entry: The memory entry to persist
            
        Returns:
            Boolean indicating success
        """
        # Determine storage path based on scope
        scope = memory_entry["metadata"]["scope"]
        
        if scope == MemoryScope.GLOBAL.value:
            storage_dir = os.path.join(self.storage_path, "global")
        elif scope == MemoryScope.USER.value:
            user_id = self.context_engine.get_current_user_id()
            storage_dir = os.path.join(self.storage_path, "user", user_id)
        elif scope == MemoryScope.SESSION.value:
            session_id = self.context_engine.get_current_session_id()
            storage_dir = os.path.join(self.storage_path, "session", session_id)
        elif scope == MemoryScope.DEVICE.value:
            device_id = self.context_engine.get_current_device_id()
            storage_dir = os.path.join(self.storage_path, "device", device_id)
        else:
            # Ephemeral memory is not persisted
            return True
        
        # Create directory if not exists
        os.makedirs(storage_dir, exist_ok=True)
        
        # Determine file path
        memory_hash = memory_entry["metadata"]["hash"]
        file_path = os.path.join(storage_dir, f"{capsule_id}_{memory_hash}.json")
        
        try:
            # Check if compression should be applied
            should_compress = self._should_compress_memory(memory_entry)
            
            # Apply compression if needed
            if should_compress:
                memory_entry = self._compress_memory(memory_entry)
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(memory_entry, f)
            
            logger.debug(f"Persisted memory for capsule {capsule_id} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to persist memory for capsule {capsule_id}: {str(e)}")
            return False
    
    def _load_memory_from_storage(self, capsule_id: str) -> bool:
        """
        Load memory from storage for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to load memory for
            
        Returns:
            Boolean indicating success
        """
        # Initialize memory cache for capsule
        self.memory_cache[capsule_id] = []
        
        # Determine storage paths to check
        storage_paths = []
        
        # Global scope
        storage_paths.append(os.path.join(self.storage_path, "global"))
        
        # User scope
        user_id = self.context_engine.get_current_user_id()
        if user_id:
            storage_paths.append(os.path.join(self.storage_path, "user", user_id))
        
        # Session scope
        session_id = self.context_engine.get_current_session_id()
        if session_id:
            storage_paths.append(os.path.join(self.storage_path, "session", session_id))
        
        # Device scope
        device_id = self.context_engine.get_current_device_id()
        if device_id:
            storage_paths.append(os.path.join(self.storage_path, "device", device_id))
        
        # Load memory from each path
        loaded_count = 0
        for path in storage_paths:
            if not os.path.exists(path):
                continue
            
            # Find files for this capsule
            for filename in os.listdir(path):
                if filename.startswith(f"{capsule_id}_") and filename.endswith(".json"):
                    file_path = os.path.join(path, filename)
                    
                    try:
                        # Read file
                        with open(file_path, 'r') as f:
                            memory_entry = json.load(f)
                        
                        # Decompress if needed
                        if self._is_compressed(memory_entry):
                            memory_entry = self._decompress_memory(memory_entry)
                        
                        # Add to cache
                        self.memory_cache[capsule_id].append(memory_entry)
                        loaded_count += 1
                    except Exception as e:
                        logger.error(f"Failed to load memory from {file_path}: {str(e)}")
        
        logger.info(f"Loaded {loaded_count} memory entries for capsule {capsule_id}")
        return loaded_count > 0
    
    def _delete_persisted_memory(self, capsule_id: str, memory_entry: Dict) -> bool:
        """
        Delete persisted memory from storage.
        
        Args:
            capsule_id: The ID of the capsule
            memory_entry: The memory entry to delete
            
        Returns:
            Boolean indicating success
        """
        # Determine storage path based on scope
        scope = memory_entry["metadata"]["scope"]
        
        if scope == MemoryScope.GLOBAL.value:
            storage_dir = os.path.join(self.storage_path, "global")
        elif scope == MemoryScope.USER.value:
            user_id = self.context_engine.get_current_user_id()
            storage_dir = os.path.join(self.storage_path, "user", user_id)
        elif scope == MemoryScope.SESSION.value:
            session_id = self.context_engine.get_current_session_id()
            storage_dir = os.path.join(self.storage_path, "session", session_id)
        elif scope == MemoryScope.DEVICE.value:
            device_id = self.context_engine.get_current_device_id()
            storage_dir = os.path.join(self.storage_path, "device", device_id)
        else:
            # Ephemeral memory is not persisted
            return True
        
        # Determine file path
        memory_hash = memory_entry["metadata"]["hash"]
        file_path = os.path.join(storage_dir, f"{capsule_id}_{memory_hash}.json")
        
        # Delete file if exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Deleted persisted memory for capsule {capsule_id} from {file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete persisted memory for capsule {capsule_id}: {str(e)}")
                return False
        
        return True  # File doesn't exist, consider it a success
    
    def _record_memory_access(self, capsule_id: str, access_type: str) -> None:
        """
        Record memory access for analytics and optimization.
        
        Args:
            capsule_id: The ID of the capsule
            access_type: The type of access (read, write, update, delete)
        """
        # Initialize access history for capsule if not exists
        if capsule_id not in self.access_history:
            self.access_history[capsule_id] = []
        
        # Add access record
        self.access_history[capsule_id].append({
            "timestamp": time.time(),
            "type": access_type,
            "user_id": self.context_engine.get_current_user_id(),
            "session_id": self.context_engine.get_current_session_id(),
            "device_id": self.context_engine.get_current_device_id()
        })
        
        # Limit history length
        if len(self.access_history[capsule_id]) > 100:
            self.access_history[capsule_id].pop(0)
    
    def _schedule_memory_sync(self, capsule_id: str, memory_entry: Dict) -> None:
        """
        Schedule memory synchronization with remote storage.
        
        Args:
            capsule_id: The ID of the capsule
            memory_entry: The memory entry to synchronize
        """
        # In a real implementation, this would queue the sync operation
        # For now, we'll just log the intent
        
        priority = memory_entry["metadata"]["priority"]
        scope = memory_entry["metadata"]["scope"]
        
        logger.info(f"Scheduled sync for capsule {capsule_id} memory with priority {priority} and scope {scope}")
        
        # Update sync status
        if capsule_id not in self.sync_status:
            self.sync_status[capsule_id] = {}
        
        memory_hash = memory_entry["metadata"]["hash"]
        self.sync_status[capsule_id][memory_hash] = {
            "status": "pending",
            "timestamp": time.time(),
            "retry_count": 0
        }
        
        # In a real implementation, this would be handled by a sync worker
        # self.sync_worker.queue_sync(capsule_id, memory_entry)
    
    def _schedule_memory_deletion_sync(self, capsule_id: str, memory_entry: Dict) -> None:
        """
        Schedule memory deletion synchronization with remote storage.
        
        Args:
            capsule_id: The ID of the capsule
            memory_entry: The memory entry to delete
        """
        # In a real implementation, this would queue the deletion sync operation
        # For now, we'll just log the intent
        
        priority = memory_entry["metadata"]["priority"]
        scope = memory_entry["metadata"]["scope"]
        
        logger.info(f"Scheduled deletion sync for capsule {capsule_id} memory with priority {priority} and scope {scope}")
        
        # Update sync status
        if capsule_id not in self.sync_status:
            self.sync_status[capsule_id] = {}
        
        memory_hash = memory_entry["metadata"]["hash"]
        self.sync_status[capsule_id][memory_hash] = {
            "status": "pending_deletion",
            "timestamp": time.time(),
            "retry_count": 0
        }
        
        # In a real implementation, this would be handled by a sync worker
        # self.sync_worker.queue_deletion_sync(capsule_id, memory_entry)
    
    def _should_compress_memory(self, memory_entry: Dict) -> bool:
        """
        Determine if memory should be compressed.
        
        Args:
            memory_entry: The memory entry to check
            
        Returns:
            Boolean indicating if compression should be applied
        """
        # Check if compression is enabled
        if not self.compression_settings["enabled"]:
            return False
        
        # Check memory priority
        priority = memory_entry["metadata"]["priority"]
        if priority == MemoryPriority.CRITICAL.value:
            # Never compress critical memory
            return False
        
        # Check memory age
        timestamp = memory_entry["metadata"]["timestamp"]
        current_time = time.time()
        age = current_time - timestamp
        
        # Get compression threshold for this priority
        threshold = self.retention_policies[priority]["compression_threshold"]
        
        # If threshold is None, never compress
        if threshold is None:
            return False
        
        # Check if age exceeds threshold
        if age > threshold:
            return True
        
        # Check memory size
        memory_size = len(json.dumps(memory_entry))
        if memory_size > self.compression_settings["thresholds"]["size_threshold"]:
            return True
        
        return False
    
    def _is_compressed(self, memory_entry: Dict) -> bool:
        """
        Check if memory entry is compressed.
        
        Args:
            memory_entry: The memory entry to check
            
        Returns:
            Boolean indicating if memory is compressed
        """
        return memory_entry["metadata"].get("compressed", False)
    
    def _compress_memory(self, memory_entry: Dict) -> Dict:
        """
        Compress memory entry.
        
        Args:
            memory_entry: The memory entry to compress
            
        Returns:
            Compressed memory entry
        """
        # Create a copy of the memory entry
        compressed_entry = {
            "data": {},
            "metadata": memory_entry["metadata"].copy()
        }
        
        # Mark as compressed
        compressed_entry["metadata"]["compressed"] = True
        
        # Apply compression algorithms
        algorithms = self.compression_settings["algorithms"]
        
        # JSON minify (remove whitespace)
        if algorithms["json_minify"]["enabled"]:
            # This is already handled by json.dumps with no extra whitespace
            pass
        
        # Key abbreviation
        if algorithms["key_abbreviation"]["enabled"]:
            abbreviations = algorithms["key_abbreviation"]["abbreviations"]
            
            # Abbreviate keys in data
            compressed_data = {}
            for key, value in memory_entry["data"].items():
                if key in abbreviations:
                    compressed_data[abbreviations[key]] = value
                else:
                    compressed_data[key] = value
            
            compressed_entry["data"] = compressed_data
        else:
            compressed_entry["data"] = memory_entry["data"].copy()
        
        # Value summarization
        if algorithms["value_summarization"]["enabled"]:
            max_string_length = algorithms["value_summarization"]["max_string_length"]
            summarize_arrays = algorithms["value_summarization"]["summarize_arrays"]
            max_array_items = algorithms["value_summarization"]["max_array_items"]
            
            # Summarize values in data
            for key, value in compressed_entry["data"].items():
                if isinstance(value, str) and len(value) > max_string_length:
                    # Truncate long strings
                    compressed_entry["data"][key] = value[:max_string_length] + "..."
                elif summarize_arrays and isinstance(value, list) and len(value) > max_array_items:
                    # Truncate long arrays
                    compressed_entry["data"][key] = value[:max_array_items] + ["..."]
        
        logger.debug(f"Compressed memory entry, original size: {len(json.dumps(memory_entry))}, compressed size: {len(json.dumps(compressed_entry))}")
        return compressed_entry
    
    def _decompress_memory(self, compressed_entry: Dict) -> Dict:
        """
        Decompress memory entry.
        
        Args:
            compressed_entry: The compressed memory entry
            
        Returns:
            Decompressed memory entry
        """
        # Create a copy of the compressed entry
        decompressed_entry = {
            "data": {},
            "metadata": compressed_entry["metadata"].copy()
        }
        
        # Remove compressed flag
        decompressed_entry["metadata"].pop("compressed", None)
        
        # Reverse key abbreviation
        algorithms = self.compression_settings["algorithms"]
        if algorithms["key_abbreviation"]["enabled"]:
            abbreviations = algorithms["key_abbreviation"]["abbreviations"]
            reverse_abbreviations = {v: k for k, v in abbreviations.items()}
            
            # Reverse abbreviations in data
            for key, value in compressed_entry["data"].items():
                if key in reverse_abbreviations:
                    decompressed_entry["data"][reverse_abbreviations[key]] = value
                else:
                    decompressed_entry["data"][key] = value
        else:
            decompressed_entry["data"] = compressed_entry["data"].copy()
        
        # Note: Value summarization cannot be fully reversed
        # Truncated strings and arrays remain truncated
        
        logger.debug(f"Decompressed memory entry")
        return decompressed_entry
    
    def get_memory_stats(self, capsule_id: str = None) -> Dict:
        """
        Get memory statistics.
        
        Args:
            capsule_id: Optional ID of the capsule to get statistics for
            
        Returns:
            Dictionary of memory statistics
        """
        stats = {
            "total_capsules": len(self.memory_cache),
            "total_memory_entries": 0,
            "memory_by_priority": {
                MemoryPriority.CRITICAL.value: 0,
                MemoryPriority.HIGH.value: 0,
                MemoryPriority.MEDIUM.value: 0,
                MemoryPriority.LOW.value: 0,
                MemoryPriority.TRANSIENT.value: 0
            },
            "memory_by_scope": {
                MemoryScope.GLOBAL.value: 0,
                MemoryScope.USER.value: 0,
                MemoryScope.SESSION.value: 0,
                MemoryScope.DEVICE.value: 0,
                MemoryScope.EPHEMERAL.value: 0
            },
            "compressed_entries": 0,
            "sync_pending": 0,
            "sync_completed": 0,
            "sync_failed": 0
        }
        
        # If capsule_id provided, get stats for that capsule only
        if capsule_id:
            if capsule_id not in self.memory_cache:
                return {
                    "capsule_id": capsule_id,
                    "memory_entries": 0,
                    "memory_by_priority": {},
                    "memory_by_scope": {},
                    "compressed_entries": 0,
                    "sync_status": {}
                }
            
            capsule_stats = {
                "capsule_id": capsule_id,
                "memory_entries": len(self.memory_cache[capsule_id]),
                "memory_by_priority": {
                    MemoryPriority.CRITICAL.value: 0,
                    MemoryPriority.HIGH.value: 0,
                    MemoryPriority.MEDIUM.value: 0,
                    MemoryPriority.LOW.value: 0,
                    MemoryPriority.TRANSIENT.value: 0
                },
                "memory_by_scope": {
                    MemoryScope.GLOBAL.value: 0,
                    MemoryScope.USER.value: 0,
                    MemoryScope.SESSION.value: 0,
                    MemoryScope.DEVICE.value: 0,
                    MemoryScope.EPHEMERAL.value: 0
                },
                "compressed_entries": 0,
                "sync_status": self.sync_status.get(capsule_id, {})
            }
            
            # Count by priority and scope
            for entry in self.memory_cache[capsule_id]:
                priority = entry["metadata"]["priority"]
                scope = entry["metadata"]["scope"]
                
                capsule_stats["memory_by_priority"][priority] = capsule_stats["memory_by_priority"].get(priority, 0) + 1
                capsule_stats["memory_by_scope"][scope] = capsule_stats["memory_by_scope"].get(scope, 0) + 1
                
                if entry["metadata"].get("compressed", False):
                    capsule_stats["compressed_entries"] += 1
            
            return capsule_stats
        
        # Get stats for all capsules
        for capsule_id, entries in self.memory_cache.items():
            stats["total_memory_entries"] += len(entries)
            
            # Count by priority and scope
            for entry in entries:
                priority = entry["metadata"]["priority"]
                scope = entry["metadata"]["scope"]
                
                stats["memory_by_priority"][priority] = stats["memory_by_priority"].get(priority, 0) + 1
                stats["memory_by_scope"][scope] = stats["memory_by_scope"].get(scope, 0) + 1
                
                if entry["metadata"].get("compressed", False):
                    stats["compressed_entries"] += 1
        
        # Count sync status
        for capsule_id, sync_entries in self.sync_status.items():
            for memory_hash, sync_info in sync_entries.items():
                status = sync_info["status"]
                
                if status == "pending" or status == "pending_deletion":
                    stats["sync_pending"] += 1
                elif status == "completed":
                    stats["sync_completed"] += 1
                elif status == "failed":
                    stats["sync_failed"] += 1
        
        return stats
    
    def cleanup_expired_memory(self) -> int:
        """
        Clean up expired memory based on retention policies.
        
        Returns:
            Number of memory entries cleaned up
        """
        cleaned_count = 0
        current_time = time.time()
        
        # Check each capsule
        for capsule_id in list(self.memory_cache.keys()):
            entries_to_delete = []
            
            # Check each memory entry
            for entry in self.memory_cache[capsule_id]:
                priority = entry["metadata"]["priority"]
                timestamp = entry["metadata"]["timestamp"]
                
                # Get retention period for this priority
                retention_period = self.retention_policies[priority]["retention_period"]
                
                # If retention period is None, keep indefinitely
                if retention_period is None:
                    continue
                
                # Check if expired
                age = current_time - timestamp
                if age > retention_period:
                    entries_to_delete.append(entry)
            
            # Delete expired entries
            for entry in entries_to_delete:
                # Remove from cache
                self.memory_cache[capsule_id].remove(entry)
                
                # Delete from persistent storage
                scope = entry["metadata"]["scope"]
                if scope != MemoryScope.EPHEMERAL.value:
                    self._delete_persisted_memory(capsule_id, entry)
                
                # Synchronize deletion
                if scope in [MemoryScope.GLOBAL.value, MemoryScope.USER.value]:
                    self._schedule_memory_deletion_sync(capsule_id, entry)
                
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} expired memory entries")
        return cleaned_count
    
    def get_memory_access_history(self, capsule_id: str, limit: int = 20) -> List[Dict]:
        """
        Get memory access history for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to get history for
            limit: Maximum number of history items to return
            
        Returns:
            List of access history records
        """
        if capsule_id not in self.access_history:
            return []
        
        # Sort by timestamp (newest first)
        history = sorted(self.access_history[capsule_id], key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        return history[:limit]
    
    def sync_with_remote(self, force: bool = False) -> Dict:
        """
        Synchronize memory with remote storage.
        
        Args:
            force: Whether to force synchronization of all memory
            
        Returns:
            Dictionary of synchronization results
        """
        # In a real implementation, this would perform actual synchronization
        # For now, we'll just log the intent and return mock results
        
        results = {
            "sync_attempted": 0,
            "sync_succeeded": 0,
            "sync_failed": 0,
            "deletion_attempted": 0,
            "deletion_succeeded": 0,
            "deletion_failed": 0
        }
        
        logger.info(f"Synchronizing memory with remote storage (force={force})")
        
        # In a real implementation, this would be handled by a sync worker
        # results = self.sync_worker.perform_sync(force)
        
        return results
    
    def import_memory(self, capsule_id: str, memory_data: List[Dict]) -> int:
        """
        Import memory data for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to import memory for
            memory_data: List of memory entries to import
            
        Returns:
            Number of memory entries imported
        """
        imported_count = 0
        
        # Initialize capsule memory if not exists
        if capsule_id not in self.memory_cache:
            self.memory_cache[capsule_id] = []
        
        # Import each memory entry
        for entry in memory_data:
            # Validate entry structure
            if "data" not in entry or "metadata" not in entry:
                logger.warning(f"Skipping invalid memory entry for capsule {capsule_id}")
                continue
            
            # Add to cache
            self.memory_cache[capsule_id].append(entry)
            
            # Persist memory based on scope
            scope = entry["metadata"]["scope"]
            if scope != MemoryScope.EPHEMERAL.value:
                self._persist_memory(capsule_id, entry)
            
            imported_count += 1
        
        # Record access
        if imported_count > 0:
            self._record_memory_access(capsule_id, "import")
        
        logger.info(f"Imported {imported_count} memory entries for capsule {capsule_id}")
        return imported_count
    
    def export_memory(self, capsule_id: str, query: Dict = None) -> List[Dict]:
        """
        Export memory data for a specific capsule.
        
        Args:
            capsule_id: The ID of the capsule to export memory for
            query: Optional query parameters for filtering memory
            
        Returns:
            List of memory entries
        """
        # Retrieve memory with metadata included
        memory_entries = self.retrieve_memory(capsule_id, query, include_metadata=True)
        
        # Record access
        if memory_entries:
            self._record_memory_access(capsule_id, "export")
        
        logger.info(f"Exported {len(memory_entries)} memory entries for capsule {capsule_id}")
        return memory_entries
    
    def adapt_to_context_change(self, context_update: Dict) -> None:
        """
        Adapt memory management based on a context change.
        
        Args:
            context_update: Dictionary containing context update information
        """
        # Check for context-triggered memory adaptations
        context_priority = context_update.get("priority")
        
        if context_priority == "critical":
            # For critical contexts, ensure all critical memory is loaded
            logger.info("Critical context detected, ensuring all critical memory is loaded")
            
            # In a real implementation, this would preload critical memory
            # self._preload_critical_memory()
        
        # Adapt memory management based on device capabilities
        device_capabilities = self.context_engine.get_device_capabilities()
        
        if device_capabilities.get("storage_constrained", False):
            # For storage-constrained devices, be more aggressive with compression
            logger.info("Storage-constrained device detected, adjusting compression settings")
            
            # In a real implementation, this would adjust compression settings
            # self._adjust_compression_for_constrained_storage()
        
        logger.info(f"Memory management adapted to context change: {context_update.get('type', 'unknown')}")
"""
