"""
Capsule Registry for the Deployment Operations Layer.

This module provides capsule registry capabilities for deployment operations
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CapsuleRegistry:
    """
    Registry for deployment capsules.
    
    This class provides methods for managing deployment capsules,
    including registration, retrieval, and lifecycle management.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Capsule Registry.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.registry_id = config.get("registry_id", f"registry-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9006")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize registry storage
        self.storage_type = config.get("storage_type", "memory")
        self.storage_path = config.get("storage_path", "/tmp/capsule_registry")
        self.capsules = {}
        
        # Initialize registry configuration
        self.capsule_types = config.get("capsule_types", [
            "application", "data", "ai", "generative", "protocol", "workflow", "ui", "security", "native"
        ])
        self.capsule_states = config.get("capsule_states", [
            "created", "registered", "deployed", "running", "paused", "stopped", "failed", "archived"
        ])
        self.default_state = config.get("default_state", "created")
        
        # Initialize blockchain integration for immutable records
        from ..blockchain.blockchain_integration import BlockchainIntegration
        self.blockchain = BlockchainIntegration(config.get("blockchain", {}))
        
        # Initialize analytics manager for registry tracking
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        # Load existing capsules if using file storage
        if self.storage_type == "file":
            self._load_capsules()
        
        logger.info(f"Capsule Registry {self.registry_id} initialized")
    
    def register_capsule(self, capsule_data: Dict) -> Dict:
        """
        Register a new capsule.
        
        Args:
            capsule_data: Capsule data
            
        Returns:
            Dict: Registration results
        """
        try:
            # Generate capsule ID if not provided
            capsule_id = capsule_data.get("capsule_id")
            if not capsule_id:
                capsule_id = f"capsule-{uuid.uuid4().hex}"
                capsule_data["capsule_id"] = capsule_id
            
            # Check if capsule already exists
            if capsule_id in self.capsules:
                return {
                    "status": "error",
                    "message": f"Capsule already exists: {capsule_id}"
                }
            
            # Validate capsule data
            validation_result = self._validate_capsule_data(capsule_data)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Add registration metadata
            capsule_data["registry_id"] = self.registry_id
            capsule_data["registration_timestamp"] = datetime.now().isoformat()
            capsule_data["last_updated_timestamp"] = datetime.now().isoformat()
            capsule_data["state"] = capsule_data.get("state", self.default_state)
            
            # Add lineage information
            parent_id = capsule_data.get("parent_id")
            if parent_id:
                parent = self.get_capsule(parent_id)
                if parent:
                    capsule_data["lineage"] = parent.get("lineage", []) + [parent_id]
                else:
                    capsule_data["lineage"] = [parent_id]
            else:
                capsule_data["lineage"] = []
            
            # Add version information
            capsule_data["version"] = capsule_data.get("version", "1.0.0")
            capsule_data["version_history"] = capsule_data.get("version_history", [])
            
            # Store capsule
            self.capsules[capsule_id] = capsule_data
            
            # Save to storage if using file storage
            if self.storage_type == "file":
                self._save_capsules()
            
            # Record on blockchain
            blockchain_result = self._record_on_blockchain("register", capsule_data)
            
            # Track registration
            self._track_capsule_event("register", capsule_data)
            
            return {
                "status": "success",
                "message": "Capsule registered successfully",
                "capsule_id": capsule_id,
                "registration_timestamp": capsule_data["registration_timestamp"],
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error registering capsule: {e}")
            return {"status": "error", "message": str(e)}
    
    def update_capsule(self, capsule_id: str, update_data: Dict) -> Dict:
        """
        Update an existing capsule.
        
        Args:
            capsule_id: Capsule ID
            update_data: Update data
            
        Returns:
            Dict: Update results
        """
        try:
            # Check if capsule exists
            if capsule_id not in self.capsules:
                return {
                    "status": "error",
                    "message": f"Capsule not found: {capsule_id}"
                }
            
            # Get current capsule data
            capsule_data = self.capsules[capsule_id]
            
            # Check if update includes state change
            if "state" in update_data and update_data["state"] != capsule_data["state"]:
                state_change_result = self._validate_state_change(
                    capsule_data["state"], update_data["state"], capsule_data
                )
                if state_change_result.get("status") != "success":
                    return state_change_result
            
            # Check if update includes version change
            if "version" in update_data and update_data["version"] != capsule_data["version"]:
                # Add current version to version history
                if "version_history" not in capsule_data:
                    capsule_data["version_history"] = []
                
                capsule_data["version_history"].append({
                    "version": capsule_data["version"],
                    "timestamp": capsule_data["last_updated_timestamp"]
                })
            
            # Update capsule data
            for key, value in update_data.items():
                if key not in ["capsule_id", "registry_id", "registration_timestamp", "lineage"]:
                    capsule_data[key] = value
            
            # Update last updated timestamp
            capsule_data["last_updated_timestamp"] = datetime.now().isoformat()
            
            # Save to storage if using file storage
            if self.storage_type == "file":
                self._save_capsules()
            
            # Record on blockchain
            blockchain_result = self._record_on_blockchain("update", capsule_data)
            
            # Track update
            self._track_capsule_event("update", capsule_data)
            
            return {
                "status": "success",
                "message": "Capsule updated successfully",
                "capsule_id": capsule_id,
                "last_updated_timestamp": capsule_data["last_updated_timestamp"],
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error updating capsule: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_capsule(self, capsule_id: str) -> Optional[Dict]:
        """
        Get a capsule by ID.
        
        Args:
            capsule_id: Capsule ID
            
        Returns:
            Optional[Dict]: Capsule data or None if not found
        """
        return self.capsules.get(capsule_id)
    
    def list_capsules(self, filters: Dict = None) -> List[Dict]:
        """
        List capsules with optional filtering.
        
        Args:
            filters: Filter criteria
            
        Returns:
            List[Dict]: List of capsules
        """
        if not filters:
            return list(self.capsules.values())
        
        filtered_capsules = []
        for capsule in self.capsules.values():
            match = True
            for key, value in filters.items():
                if key not in capsule or capsule[key] != value:
                    match = False
                    break
            
            if match:
                filtered_capsules.append(capsule)
        
        return filtered_capsules
    
    def delete_capsule(self, capsule_id: str) -> Dict:
        """
        Delete a capsule.
        
        Args:
            capsule_id: Capsule ID
            
        Returns:
            Dict: Deletion results
        """
        try:
            # Check if capsule exists
            if capsule_id not in self.capsules:
                return {
                    "status": "error",
                    "message": f"Capsule not found: {capsule_id}"
                }
            
            # Get capsule data for tracking
            capsule_data = self.capsules[capsule_id]
            
            # Delete capsule
            del self.capsules[capsule_id]
            
            # Save to storage if using file storage
            if self.storage_type == "file":
                self._save_capsules()
            
            # Record on blockchain
            blockchain_result = self._record_on_blockchain("delete", capsule_data)
            
            # Track deletion
            self._track_capsule_event("delete", capsule_data)
            
            return {
                "status": "success",
                "message": "Capsule deleted successfully",
                "capsule_id": capsule_id,
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error deleting capsule: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_capsule_lineage(self, capsule_id: str) -> Dict:
        """
        Get the lineage of a capsule.
        
        Args:
            capsule_id: Capsule ID
            
        Returns:
            Dict: Lineage results
        """
        try:
            # Check if capsule exists
            if capsule_id not in self.capsules:
                return {
                    "status": "error",
                    "message": f"Capsule not found: {capsule_id}"
                }
            
            # Get capsule data
            capsule_data = self.capsules[capsule_id]
            
            # Get lineage
            lineage = capsule_data.get("lineage", [])
            
            # Get lineage capsules
            lineage_capsules = []
            for ancestor_id in lineage:
                ancestor = self.get_capsule(ancestor_id)
                if ancestor:
                    lineage_capsules.append(ancestor)
            
            # Get descendants
            descendants = []
            for potential_descendant_id, potential_descendant in self.capsules.items():
                if capsule_id in potential_descendant.get("lineage", []):
                    descendants.append(potential_descendant)
            
            return {
                "status": "success",
                "message": "Capsule lineage retrieved successfully",
                "capsule_id": capsule_id,
                "ancestors": lineage,
                "ancestor_capsules": lineage_capsules,
                "descendants": [d["capsule_id"] for d in descendants],
                "descendant_capsules": descendants
            }
        except Exception as e:
            logger.error(f"Error getting capsule lineage: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_capsule_history(self, capsule_id: str) -> Dict:
        """
        Get the history of a capsule.
        
        Args:
            capsule_id: Capsule ID
            
        Returns:
            Dict: History results
        """
        try:
            # Check if capsule exists
            if capsule_id not in self.capsules:
                return {
                    "status": "error",
                    "message": f"Capsule not found: {capsule_id}"
                }
            
            # Get capsule data
            capsule_data = self.capsules[capsule_id]
            
            # Get blockchain history
            blockchain_history = self.blockchain.get_entity_history(capsule_id)
            
            return {
                "status": "success",
                "message": "Capsule history retrieved successfully",
                "capsule_id": capsule_id,
                "registration_timestamp": capsule_data.get("registration_timestamp"),
                "last_updated_timestamp": capsule_data.get("last_updated_timestamp"),
                "version": capsule_data.get("version"),
                "version_history": capsule_data.get("version_history", []),
                "blockchain_history": blockchain_history
            }
        except Exception as e:
            logger.error(f"Error getting capsule history: {e}")
            return {"status": "error", "message": str(e)}
    
    def _validate_capsule_data(self, capsule_data: Dict) -> Dict:
        """
        Validate capsule data.
        
        Args:
            capsule_data: Capsule data
            
        Returns:
            Dict: Validation results
        """
        # Check required fields
        required_fields = ["name", "type"]
        for field in required_fields:
            if field not in capsule_data:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }
        
        # Validate capsule type
        if capsule_data["type"] not in self.capsule_types:
            return {
                "status": "error",
                "message": f"Invalid capsule type: {capsule_data['type']}"
            }
        
        # Validate state if provided
        if "state" in capsule_data and capsule_data["state"] not in self.capsule_states:
            return {
                "status": "error",
                "message": f"Invalid capsule state: {capsule_data['state']}"
            }
        
        return {"status": "success"}
    
    def _validate_state_change(self, current_state: str, new_state: str, capsule_data: Dict) -> Dict:
        """
        Validate a state change.
        
        Args:
            current_state: Current state
            new_state: New state
            capsule_data: Capsule data
            
        Returns:
            Dict: Validation results
        """
        # Define valid state transitions
        valid_transitions = {
            "created": ["registered", "archived"],
            "registered": ["deployed", "archived"],
            "deployed": ["running", "failed", "archived"],
            "running": ["paused", "stopped", "failed", "archived"],
            "paused": ["running", "stopped", "archived"],
            "stopped": ["deployed", "archived"],
            "failed": ["deployed", "archived"],
            "archived": []
        }
        
        # Check if transition is valid
        if new_state not in valid_transitions.get(current_state, []):
            return {
                "status": "error",
                "message": f"Invalid state transition: {current_state} -> {new_state}"
            }
        
        return {"status": "success"}
    
    def _record_on_blockchain(self, action: str, capsule_data: Dict) -> Dict:
        """
        Record a capsule action on the blockchain.
        
        Args:
            action: Action type
            capsule_data: Capsule data
            
        Returns:
            Dict: Blockchain recording results
        """
        try:
            # Prepare record data
            record_data = {
                "action": action,
                "capsule_id": capsule_data["capsule_id"],
                "timestamp": datetime.now().isoformat(),
                "registry_id": self.registry_id
            }
            
            # Add action-specific data
            if action == "register":
                record_data.update({
                    "name": capsule_data["name"],
                    "type": capsule_data["type"],
                    "version": capsule_data["version"],
                    "state": capsule_data["state"]
                })
            elif action == "update":
                record_data.update({
                    "version": capsule_data["version"],
                    "state": capsule_data["state"]
                })
            
            # Record on blockchain
            return self.blockchain.record_transaction(record_data)
        except Exception as e:
            logger.error(f"Error recording on blockchain: {e}")
            return {"status": "error", "message": str(e)}
    
    def _track_capsule_event(self, event_type: str, capsule_data: Dict) -> None:
        """
        Track a capsule event in analytics.
        
        Args:
            event_type: Event type
            capsule_data: Capsule data
        """
        try:
            # Prepare metrics
            metrics = {
                "type": f"capsule_{event_type}",
                "timestamp": datetime.now().isoformat(),
                "capsule_id": capsule_data["capsule_id"],
                "capsule_type": capsule_data["type"],
                "capsule_state": capsule_data.get("state", self.default_state),
                "registry_id": self.registry_id
            }
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking capsule event: {e}")
    
    def _load_capsules(self) -> None:
        """
        Load capsules from file storage.
        """
        try:
            # Create storage directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # Check if storage file exists
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r") as f:
                    self.capsules = json.load(f)
                
                logger.info(f"Loaded {len(self.capsules)} capsules from storage")
        except Exception as e:
            logger.error(f"Error loading capsules: {e}")
    
    def _save_capsules(self) -> None:
        """
        Save capsules to file storage.
        """
        try:
            # Create storage directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # Save capsules to file
            with open(self.storage_path, "w") as f:
                json.dump(self.capsules, f)
            
            logger.info(f"Saved {len(self.capsules)} capsules to storage")
        except Exception as e:
            logger.error(f"Error saving capsules: {e}")
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Capsule Registry.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "storage_type" in config:
                self.storage_type = config["storage_type"]
            
            if "storage_path" in config:
                self.storage_path = config["storage_path"]
            
            if "capsule_types" in config:
                self.capsule_types = config["capsule_types"]
            
            if "capsule_states" in config:
                self.capsule_states = config["capsule_states"]
            
            if "default_state" in config:
                self.default_state = config["default_state"]
            
            # Configure blockchain integration
            blockchain_result = None
            if "blockchain" in config:
                blockchain_result = self.blockchain.configure(config["blockchain"])
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            # Reload capsules if storage type or path changed
            if "storage_type" in config or "storage_path" in config:
                if self.storage_type == "file":
                    self._load_capsules()
            
            return {
                "status": "success",
                "message": "Capsule Registry configured successfully",
                "registry_id": self.registry_id,
                "blockchain_result": blockchain_result,
                "analytics_result": analytics_result
            }
        except Exception as e:
            logger.error(f"Error configuring Capsule Registry: {e}")
            return {"status": "error", "message": str(e)}
