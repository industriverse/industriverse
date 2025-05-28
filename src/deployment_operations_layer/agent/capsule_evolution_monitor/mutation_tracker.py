"""
Mutation Tracker - Tracks capsule mutations

This module tracks mutations to capsules after deployment, recording all changes
to their configuration, state, or behavior.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MutationTracker:
    """
    Tracks mutations to capsules after deployment.
    
    This component is responsible for recording all changes to capsules,
    including configuration changes, state changes, and behavior changes.
    It maintains a history of mutations for each capsule.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Mutation Tracker.
        
        Args:
            config: Configuration dictionary for the tracker
        """
        self.config = config or {}
        self.mutation_history = {}  # Capsule ID -> List of mutations
        self.storage_path = self.config.get("storage_path", "/var/log/industriverse/mutations")
        self.max_history_length = self.config.get("max_history_length", 100)
        self.persistence_enabled = self.config.get("persistence_enabled", True)
        
        logger.info("Initializing Mutation Tracker")
    
    def initialize(self):
        """Initialize the tracker and load any existing mutation history."""
        logger.info("Initializing Mutation Tracker")
        
        if self.persistence_enabled:
            try:
                self._load_mutation_history()
                logger.info("Loaded existing mutation history")
            except Exception as e:
                logger.warning(f"Failed to load mutation history: {str(e)}")
        
        return True
    
    def track_mutation(self, capsule_id: str, previous_state: Dict[str, Any], 
                      current_state: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track a mutation to a capsule.
        
        Args:
            capsule_id: ID of the capsule
            previous_state: Previous state of the capsule
            current_state: Current state of the capsule
            changes: Dictionary describing the changes
            
        Returns:
            Dictionary with mutation information
        """
        timestamp = datetime.now().isoformat()
        
        mutation = {
            "mutation_id": f"{capsule_id}-{timestamp}",
            "capsule_id": capsule_id,
            "timestamp": timestamp,
            "changes": changes,
            "previous_version": previous_state.get("version", "unknown"),
            "current_version": current_state.get("version", "unknown"),
            "metadata": {
                "source": changes.get("source", "unknown"),
                "reason": changes.get("reason", "unknown"),
                "authorized": changes.get("authorized", False)
            }
        }
        
        # Initialize history for this capsule if it doesn't exist
        if capsule_id not in self.mutation_history:
            self.mutation_history[capsule_id] = []
        
        # Add mutation to history
        self.mutation_history[capsule_id].append(mutation)
        
        # Trim history if it exceeds max length
        if len(self.mutation_history[capsule_id]) > self.max_history_length:
            self.mutation_history[capsule_id] = self.mutation_history[capsule_id][-self.max_history_length:]
        
        # Persist mutation history
        if self.persistence_enabled:
            try:
                self._save_mutation_history(capsule_id)
            except Exception as e:
                logger.error(f"Failed to save mutation history for capsule {capsule_id}: {str(e)}")
        
        logger.info(f"Tracked mutation for capsule {capsule_id}: {mutation['mutation_id']}")
        return mutation
    
    def get_mutation_history(self, capsule_id: str) -> List[Dict[str, Any]]:
        """
        Get the mutation history for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            List of mutation dictionaries
        """
        return self.mutation_history.get(capsule_id, [])
    
    def get_mutation(self, capsule_id: str, mutation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific mutation by ID.
        
        Args:
            capsule_id: ID of the capsule
            mutation_id: ID of the mutation
            
        Returns:
            Mutation dictionary or None if not found
        """
        for mutation in self.mutation_history.get(capsule_id, []):
            if mutation["mutation_id"] == mutation_id:
                return mutation
        return None
    
    def get_mutations_by_timerange(self, capsule_id: str, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """
        Get mutations within a specific time range.
        
        Args:
            capsule_id: ID of the capsule
            start_time: Start time in ISO format
            end_time: End time in ISO format
            
        Returns:
            List of mutation dictionaries
        """
        result = []
        for mutation in self.mutation_history.get(capsule_id, []):
            if start_time <= mutation["timestamp"] <= end_time:
                result.append(mutation)
        return result
    
    def clear_history(self, capsule_id: str) -> bool:
        """
        Clear the mutation history for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            True if successful, False otherwise
        """
        if capsule_id in self.mutation_history:
            self.mutation_history[capsule_id] = []
            
            # Persist empty history
            if self.persistence_enabled:
                try:
                    self._save_mutation_history(capsule_id)
                except Exception as e:
                    logger.error(f"Failed to save empty mutation history for capsule {capsule_id}: {str(e)}")
                    return False
            
            logger.info(f"Cleared mutation history for capsule {capsule_id}")
            return True
        
        logger.warning(f"No mutation history found for capsule {capsule_id}")
        return False
    
    def _save_mutation_history(self, capsule_id: str):
        """
        Save the mutation history for a capsule to disk.
        
        Args:
            capsule_id: ID of the capsule
        """
        import os
        
        # Create directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Save history to file
        file_path = os.path.join(self.storage_path, f"{capsule_id}_mutations.json")
        with open(file_path, 'w') as f:
            json.dump(self.mutation_history[capsule_id], f, indent=2)
    
    def _load_mutation_history(self):
        """Load all mutation history from disk."""
        import os
        import glob
        
        # Check if directory exists
        if not os.path.exists(self.storage_path):
            logger.warning(f"Storage path {self.storage_path} does not exist")
            return
        
        # Load all mutation history files
        pattern = os.path.join(self.storage_path, "*_mutations.json")
        for file_path in glob.glob(pattern):
            try:
                # Extract capsule ID from filename
                filename = os.path.basename(file_path)
                capsule_id = filename.replace("_mutations.json", "")
                
                # Load history from file
                with open(file_path, 'r') as f:
                    self.mutation_history[capsule_id] = json.load(f)
                
                logger.info(f"Loaded mutation history for capsule {capsule_id}")
            except Exception as e:
                logger.error(f"Failed to load mutation history from {file_path}: {str(e)}")
