"""
Override Logger - Logs capsule override events

This module logs override events for capsules, tracking when and how capsules
are overridden from their original configuration or intended state.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class OverrideLogger:
    """
    Logs override events for capsules.
    
    This component is responsible for logging when capsules are overridden
    from their original configuration or intended state, including who
    performed the override, why, and what changes were made.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Override Logger.
        
        Args:
            config: Configuration dictionary for the logger
        """
        self.config = config or {}
        self.override_history = {}  # Capsule ID -> List of overrides
        self.storage_path = self.config.get("storage_path", "/var/log/industriverse/overrides")
        self.max_history_length = self.config.get("max_history_length", 100)
        self.persistence_enabled = self.config.get("persistence_enabled", True)
        self.alert_on_override = self.config.get("alert_on_override", True)
        
        logger.info("Initializing Override Logger")
    
    def initialize(self):
        """Initialize the logger and load any existing override history."""
        logger.info("Initializing Override Logger")
        
        if self.persistence_enabled:
            try:
                self._load_override_history()
                logger.info("Loaded existing override history")
            except Exception as e:
                logger.warning(f"Failed to load override history: {str(e)}")
        
        return True
    
    def log_override(self, capsule_id: str, previous_state: Dict[str, Any], 
                    current_state: Dict[str, Any], changes: Dict[str, Any],
                    override_source: str = "unknown") -> Dict[str, Any]:
        """
        Log an override event for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            previous_state: Previous state of the capsule
            current_state: Current state of the capsule
            changes: Dictionary describing the changes
            override_source: Source of the override (e.g., user, system)
            
        Returns:
            Dictionary with override information
        """
        timestamp = datetime.now().isoformat()
        
        override = {
            "override_id": f"{capsule_id}-{timestamp}",
            "capsule_id": capsule_id,
            "timestamp": timestamp,
            "changes": changes,
            "previous_version": previous_state.get("version", "unknown"),
            "current_version": current_state.get("version", "unknown"),
            "override_source": override_source,
            "metadata": {
                "reason": changes.get("reason", "unknown"),
                "authorized": changes.get("authorized", False),
                "authorization_id": changes.get("authorization_id", None),
                "user_id": changes.get("user_id", None),
                "system_id": changes.get("system_id", None)
            }
        }
        
        # Initialize history for this capsule if it doesn't exist
        if capsule_id not in self.override_history:
            self.override_history[capsule_id] = []
        
        # Add override to history
        self.override_history[capsule_id].append(override)
        
        # Trim history if it exceeds max length
        if len(self.override_history[capsule_id]) > self.max_history_length:
            self.override_history[capsule_id] = self.override_history[capsule_id][-self.max_history_length:]
        
        # Persist override history
        if self.persistence_enabled:
            try:
                self._save_override_history(capsule_id)
            except Exception as e:
                logger.error(f"Failed to save override history for capsule {capsule_id}: {str(e)}")
        
        # Send alert if configured
        if self.alert_on_override:
            self._send_override_alert(override)
        
        logger.info(f"Logged override for capsule {capsule_id}: {override['override_id']}")
        return override
    
    def get_override_history(self, capsule_id: str) -> List[Dict[str, Any]]:
        """
        Get the override history for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            List of override dictionaries
        """
        return self.override_history.get(capsule_id, [])
    
    def get_override(self, capsule_id: str, override_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific override by ID.
        
        Args:
            capsule_id: ID of the capsule
            override_id: ID of the override
            
        Returns:
            Override dictionary or None if not found
        """
        for override in self.override_history.get(capsule_id, []):
            if override["override_id"] == override_id:
                return override
        return None
    
    def get_overrides_by_source(self, capsule_id: str, source: str) -> List[Dict[str, Any]]:
        """
        Get overrides by source.
        
        Args:
            capsule_id: ID of the capsule
            source: Source of the override
            
        Returns:
            List of override dictionaries
        """
        result = []
        for override in self.override_history.get(capsule_id, []):
            if override["override_source"] == source:
                result.append(override)
        return result
    
    def get_overrides_by_timerange(self, capsule_id: str, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """
        Get overrides within a specific time range.
        
        Args:
            capsule_id: ID of the capsule
            start_time: Start time in ISO format
            end_time: End time in ISO format
            
        Returns:
            List of override dictionaries
        """
        result = []
        for override in self.override_history.get(capsule_id, []):
            if start_time <= override["timestamp"] <= end_time:
                result.append(override)
        return result
    
    def clear_history(self, capsule_id: str) -> bool:
        """
        Clear the override history for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            True if successful, False otherwise
        """
        if capsule_id in self.override_history:
            self.override_history[capsule_id] = []
            
            # Persist empty history
            if self.persistence_enabled:
                try:
                    self._save_override_history(capsule_id)
                except Exception as e:
                    logger.error(f"Failed to save empty override history for capsule {capsule_id}: {str(e)}")
                    return False
            
            logger.info(f"Cleared override history for capsule {capsule_id}")
            return True
        
        logger.warning(f"No override history found for capsule {capsule_id}")
        return False
    
    def _save_override_history(self, capsule_id: str):
        """
        Save the override history for a capsule to disk.
        
        Args:
            capsule_id: ID of the capsule
        """
        import os
        
        # Create directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Save history to file
        file_path = os.path.join(self.storage_path, f"{capsule_id}_overrides.json")
        with open(file_path, 'w') as f:
            json.dump(self.override_history[capsule_id], f, indent=2)
    
    def _load_override_history(self):
        """Load all override history from disk."""
        import os
        import glob
        
        # Check if directory exists
        if not os.path.exists(self.storage_path):
            logger.warning(f"Storage path {self.storage_path} does not exist")
            return
        
        # Load all override history files
        pattern = os.path.join(self.storage_path, "*_overrides.json")
        for file_path in glob.glob(pattern):
            try:
                # Extract capsule ID from filename
                filename = os.path.basename(file_path)
                capsule_id = filename.replace("_overrides.json", "")
                
                # Load history from file
                with open(file_path, 'r') as f:
                    self.override_history[capsule_id] = json.load(f)
                
                logger.info(f"Loaded override history for capsule {capsule_id}")
            except Exception as e:
                logger.error(f"Failed to load override history from {file_path}: {str(e)}")
    
    def _send_override_alert(self, override: Dict[str, Any]):
        """
        Send an alert for an override event.
        
        Args:
            override: Override dictionary
        """
        # In a real implementation, this would send an alert to a monitoring system
        # For now, we'll just log it
        logger.warning(f"OVERRIDE ALERT: Capsule {override['capsule_id']} was overridden by {override['override_source']}")
        
        # Integration with MCP for alerting
        try:
            self._send_mcp_alert(override)
        except Exception as e:
            logger.error(f"Failed to send MCP alert for override: {str(e)}")
    
    def _send_mcp_alert(self, override: Dict[str, Any]):
        """
        Send an alert via MCP.
        
        Args:
            override: Override dictionary
        """
        # This is a placeholder for MCP integration
        # In a real implementation, this would use the MCP client to send an alert
        pass
