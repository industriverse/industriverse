"""
Scenario Manager for the Deployment Operations Layer.

This module provides scenario management capabilities for deployment operations
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
import yaml
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScenarioManager:
    """
    Manager for deployment scenarios.
    
    This class provides methods for managing deployment scenarios,
    including creation, retrieval, and application.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Scenario Manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.manager_id = config.get("manager_id", f"scenario-manager-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9016")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize scenario storage
        self.storage_type = config.get("storage_type", "file")
        self.storage_path = config.get("storage_path", "/tmp/scenarios")
        self.scenarios = {}
        
        # Initialize scenario configuration
        self.scenario_types = config.get("scenario_types", [
            "deployment", "scaling", "failover", "recovery", "upgrade", "custom"
        ])
        self.scenario_categories = config.get("scenario_categories", [
            "standard", "edge", "multi-region", "disaster-recovery", "security", "performance"
        ])
        
        # Initialize analytics manager for scenario tracking
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        # Load existing scenarios
        self._load_scenarios()
        
        logger.info(f"Scenario Manager {self.manager_id} initialized")
    
    def create_scenario(self, scenario_data: Dict) -> Dict:
        """
        Create a new scenario.
        
        Args:
            scenario_data: Scenario data
            
        Returns:
            Dict: Creation results
        """
        try:
            # Generate scenario ID if not provided
            scenario_id = scenario_data.get("scenario_id")
            if not scenario_id:
                scenario_id = f"scenario-{uuid.uuid4().hex}"
                scenario_data["scenario_id"] = scenario_id
            
            # Check if scenario already exists
            if scenario_id in self.scenarios:
                return {
                    "status": "error",
                    "message": f"Scenario already exists: {scenario_id}"
                }
            
            # Validate scenario data
            validation_result = self._validate_scenario_data(scenario_data)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Add creation metadata
            scenario_data["creation_timestamp"] = datetime.now().isoformat()
            scenario_data["last_updated_timestamp"] = datetime.now().isoformat()
            
            # Add version information
            scenario_data["version"] = scenario_data.get("version", "1.0.0")
            scenario_data["version_history"] = scenario_data.get("version_history", [])
            
            # Store scenario
            self.scenarios[scenario_id] = scenario_data
            
            # Save scenario to storage
            self._save_scenario(scenario_id, scenario_data)
            
            # Track scenario creation
            self._track_scenario_event("create", scenario_data)
            
            return {
                "status": "success",
                "message": "Scenario created successfully",
                "scenario_id": scenario_id,
                "creation_timestamp": scenario_data["creation_timestamp"]
            }
        except Exception as e:
            logger.error(f"Error creating scenario: {e}")
            return {"status": "error", "message": str(e)}
    
    def update_scenario(self, scenario_id: str, update_data: Dict) -> Dict:
        """
        Update an existing scenario.
        
        Args:
            scenario_id: Scenario ID
            update_data: Update data
            
        Returns:
            Dict: Update results
        """
        try:
            # Check if scenario exists
            if scenario_id not in self.scenarios:
                return {
                    "status": "error",
                    "message": f"Scenario not found: {scenario_id}"
                }
            
            # Get current scenario data
            scenario_data = self.scenarios[scenario_id]
            
            # Check if update includes version change
            if "version" in update_data and update_data["version"] != scenario_data["version"]:
                # Add current version to version history
                if "version_history" not in scenario_data:
                    scenario_data["version_history"] = []
                
                scenario_data["version_history"].append({
                    "version": scenario_data["version"],
                    "timestamp": scenario_data["last_updated_timestamp"]
                })
            
            # Update scenario data
            for key, value in update_data.items():
                if key not in ["scenario_id", "creation_timestamp"]:
                    scenario_data[key] = value
            
            # Update last updated timestamp
            scenario_data["last_updated_timestamp"] = datetime.now().isoformat()
            
            # Save scenario to storage
            self._save_scenario(scenario_id, scenario_data)
            
            # Track scenario update
            self._track_scenario_event("update", scenario_data)
            
            return {
                "status": "success",
                "message": "Scenario updated successfully",
                "scenario_id": scenario_id,
                "last_updated_timestamp": scenario_data["last_updated_timestamp"]
            }
        except Exception as e:
            logger.error(f"Error updating scenario: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_scenario(self, scenario_id: str) -> Optional[Dict]:
        """
        Get a scenario by ID.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Optional[Dict]: Scenario data or None if not found
        """
        return self.scenarios.get(scenario_id)
    
    def list_scenarios(self, filters: Dict = None) -> List[Dict]:
        """
        List scenarios with optional filtering.
        
        Args:
            filters: Filter criteria
            
        Returns:
            List[Dict]: List of scenarios
        """
        if not filters:
            return list(self.scenarios.values())
        
        filtered_scenarios = []
        for scenario in self.scenarios.values():
            match = True
            for key, value in filters.items():
                if key not in scenario or scenario[key] != value:
                    match = False
                    break
            
            if match:
                filtered_scenarios.append(scenario)
        
        return filtered_scenarios
    
    def delete_scenario(self, scenario_id: str) -> Dict:
        """
        Delete a scenario.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Dict: Deletion results
        """
        try:
            # Check if scenario exists
            if scenario_id not in self.scenarios:
                return {
                    "status": "error",
                    "message": f"Scenario not found: {scenario_id}"
                }
            
            # Get scenario data for tracking
            scenario_data = self.scenarios[scenario_id]
            
            # Delete scenario
            del self.scenarios[scenario_id]
            
            # Delete scenario from storage
            self._delete_scenario(scenario_id)
            
            # Track scenario deletion
            self._track_scenario_event("delete", scenario_data)
            
            return {
                "status": "success",
                "message": "Scenario deleted successfully",
                "scenario_id": scenario_id
            }
        except Exception as e:
            logger.error(f"Error deleting scenario: {e}")
            return {"status": "error", "message": str(e)}
    
    def clone_scenario(self, scenario_id: str, new_name: str = None) -> Dict:
        """
        Clone a scenario.
        
        Args:
            scenario_id: Scenario ID
            new_name: New scenario name
            
        Returns:
            Dict: Cloning results
        """
        try:
            # Check if scenario exists
            if scenario_id not in self.scenarios:
                return {
                    "status": "error",
                    "message": f"Scenario not found: {scenario_id}"
                }
            
            # Get scenario data
            scenario_data = self.scenarios[scenario_id]
            
            # Create clone data
            clone_data = scenario_data.copy()
            
            # Remove ID and timestamps
            clone_data.pop("scenario_id", None)
            clone_data.pop("creation_timestamp", None)
            clone_data.pop("last_updated_timestamp", None)
            
            # Update name if provided
            if new_name:
                clone_data["name"] = new_name
            else:
                clone_data["name"] = f"Clone of {scenario_data.get('name', 'Unnamed Scenario')}"
            
            # Create new scenario
            return self.create_scenario(clone_data)
        except Exception as e:
            logger.error(f"Error cloning scenario: {e}")
            return {"status": "error", "message": str(e)}
    
    def export_scenario(self, scenario_id: str, format: str = "json") -> Dict:
        """
        Export a scenario.
        
        Args:
            scenario_id: Scenario ID
            format: Export format
            
        Returns:
            Dict: Export results
        """
        try:
            # Check if scenario exists
            if scenario_id not in self.scenarios:
                return {
                    "status": "error",
                    "message": f"Scenario not found: {scenario_id}"
                }
            
            # Get scenario data
            scenario_data = self.scenarios[scenario_id]
            
            # Export based on format
            if format == "json":
                # Export as JSON
                export_data = json.dumps(scenario_data, indent=2)
                export_mime_type = "application/json"
            elif format == "yaml":
                # Export as YAML
                export_data = yaml.dump(scenario_data)
                export_mime_type = "application/yaml"
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported export format: {format}"
                }
            
            # Track scenario export
            self._track_scenario_event("export", scenario_data)
            
            return {
                "status": "success",
                "message": "Scenario exported successfully",
                "scenario_id": scenario_id,
                "format": format,
                "mime_type": export_mime_type,
                "data": export_data
            }
        except Exception as e:
            logger.error(f"Error exporting scenario: {e}")
            return {"status": "error", "message": str(e)}
    
    def import_scenario(self, import_data: str, format: str = "json") -> Dict:
        """
        Import a scenario.
        
        Args:
            import_data: Import data
            format: Import format
            
        Returns:
            Dict: Import results
        """
        try:
            # Parse import data based on format
            if format == "json":
                # Parse JSON
                scenario_data = json.loads(import_data)
            elif format == "yaml":
                # Parse YAML
                scenario_data = yaml.safe_load(import_data)
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported import format: {format}"
                }
            
            # Create new scenario
            result = self.create_scenario(scenario_data)
            
            # Add import metadata
            if result.get("status") == "success":
                scenario_id = result.get("scenario_id")
                if scenario_id in self.scenarios:
                    self.scenarios[scenario_id]["imported"] = True
                    self.scenarios[scenario_id]["import_timestamp"] = datetime.now().isoformat()
                    self.scenarios[scenario_id]["import_format"] = format
                    
                    # Save scenario to storage
                    self._save_scenario(scenario_id, self.scenarios[scenario_id])
            
            return result
        except Exception as e:
            logger.error(f"Error importing scenario: {e}")
            return {"status": "error", "message": str(e)}
    
    def _validate_scenario_data(self, scenario_data: Dict) -> Dict:
        """
        Validate scenario data.
        
        Args:
            scenario_data: Scenario data
            
        Returns:
            Dict: Validation results
        """
        # Check required fields
        required_fields = ["name", "type"]
        for field in required_fields:
            if field not in scenario_data:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }
        
        # Validate scenario type
        if scenario_data["type"] not in self.scenario_types:
            return {
                "status": "error",
                "message": f"Invalid scenario type: {scenario_data['type']}"
            }
        
        # Validate scenario category if provided
        if "category" in scenario_data and scenario_data["category"] not in self.scenario_categories:
            return {
                "status": "error",
                "message": f"Invalid scenario category: {scenario_data['category']}"
            }
        
        return {"status": "success"}
    
    def _load_scenarios(self) -> None:
        """
        Load scenarios from storage.
        """
        try:
            if self.storage_type == "file":
                # Create storage directory if it doesn't exist
                os.makedirs(self.storage_path, exist_ok=True)
                
                # Get scenario files
                scenario_files = []
                for root, _, files in os.walk(self.storage_path):
                    for file in files:
                        if file.endswith(".json"):
                            scenario_files.append(os.path.join(root, file))
                
                # Load scenarios
                for scenario_file in scenario_files:
                    try:
                        with open(scenario_file, "r") as f:
                            scenario_data = json.load(f)
                            
                            # Add scenario to scenarios
                            scenario_id = scenario_data.get("scenario_id")
                            if scenario_id:
                                self.scenarios[scenario_id] = scenario_data
                    except Exception as e:
                        logger.error(f"Error loading scenario file {scenario_file}: {e}")
                
                logger.info(f"Loaded {len(self.scenarios)} scenarios from storage")
        except Exception as e:
            logger.error(f"Error loading scenarios: {e}")
    
    def _save_scenario(self, scenario_id: str, scenario_data: Dict) -> None:
        """
        Save a scenario to storage.
        
        Args:
            scenario_id: Scenario ID
            scenario_data: Scenario data
        """
        try:
            if self.storage_type == "file":
                # Create storage directory if it doesn't exist
                os.makedirs(self.storage_path, exist_ok=True)
                
                # Save scenario to file
                scenario_file = os.path.join(self.storage_path, f"{scenario_id}.json")
                with open(scenario_file, "w") as f:
                    json.dump(scenario_data, f, indent=2)
                
                logger.info(f"Saved scenario {scenario_id} to storage")
        except Exception as e:
            logger.error(f"Error saving scenario {scenario_id}: {e}")
    
    def _delete_scenario(self, scenario_id: str) -> None:
        """
        Delete a scenario from storage.
        
        Args:
            scenario_id: Scenario ID
        """
        try:
            if self.storage_type == "file":
                # Delete scenario file
                scenario_file = os.path.join(self.storage_path, f"{scenario_id}.json")
                if os.path.exists(scenario_file):
                    os.remove(scenario_file)
                
                logger.info(f"Deleted scenario {scenario_id} from storage")
        except Exception as e:
            logger.error(f"Error deleting scenario {scenario_id}: {e}")
    
    def _track_scenario_event(self, event_type: str, scenario_data: Dict) -> None:
        """
        Track a scenario event in analytics.
        
        Args:
            event_type: Event type
            scenario_data: Scenario data
        """
        try:
            # Prepare metrics
            metrics = {
                "type": f"scenario_{event_type}",
                "timestamp": datetime.now().isoformat(),
                "scenario_id": scenario_data.get("scenario_id"),
                "scenario_type": scenario_data.get("type"),
                "manager_id": self.manager_id
            }
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking scenario event: {e}")
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Scenario Manager.
        
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
            
            if "scenario_types" in config:
                self.scenario_types = config["scenario_types"]
            
            if "scenario_categories" in config:
                self.scenario_categories = config["scenario_categories"]
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            # Reload scenarios if storage type or path changed
            if "storage_type" in config or "storage_path" in config:
                self._load_scenarios()
            
            return {
                "status": "success",
                "message": "Scenario Manager configured successfully",
                "manager_id": self.manager_id,
                "analytics_result": analytics_result
            }
        except Exception as e:
            logger.error(f"Error configuring Scenario Manager: {e}")
            return {"status": "error", "message": str(e)}
