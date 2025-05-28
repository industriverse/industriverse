"""
Drift Detector - Detects capsule drift from original configuration

This module detects when capsules drift from their original configuration or intended state,
identifying changes that may affect capsule behavior or performance.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import copy
import difflib

logger = logging.getLogger(__name__)

class DriftDetector:
    """
    Detects drift in capsule configuration and state.
    
    This component is responsible for detecting when capsules drift from their
    original configuration or intended state, identifying changes that may
    affect capsule behavior or performance.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Drift Detector.
        
        Args:
            config: Configuration dictionary for the detector
        """
        self.config = config or {}
        self.baseline_states = {}  # Capsule ID -> Baseline state
        self.drift_history = {}  # Capsule ID -> List of drift events
        self.drift_thresholds = self.config.get("drift_thresholds", {
            "configuration": 0.1,  # 10% change in configuration
            "resources": 0.2,  # 20% change in resource usage
            "performance": 0.15  # 15% change in performance metrics
        })
        self.max_history_length = self.config.get("max_history_length", 100)
        
        logger.info("Initializing Drift Detector")
    
    def initialize(self):
        """Initialize the detector."""
        logger.info("Initializing Drift Detector")
        return True
    
    def set_baseline(self, capsule_id: str, baseline_state: Dict[str, Any]) -> bool:
        """
        Set the baseline state for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            baseline_state: Baseline state to compare against
            
        Returns:
            True if successful, False otherwise
        """
        self.baseline_states[capsule_id] = copy.deepcopy(baseline_state)
        logger.info(f"Set baseline state for capsule {capsule_id}")
        return True
    
    def detect_drift(self, previous_state: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect drift between previous and current states.
        
        Args:
            previous_state: Previous state of the capsule
            current_state: Current state of the capsule
            
        Returns:
            Dictionary with drift information
        """
        capsule_id = current_state.get("capsule_id", "unknown")
        
        # Initialize result
        result = {
            "has_changes": False,
            "changes": {},
            "is_override": False,
            "override_source": None,
            "drift_percentage": 0.0,
            "drift_details": {}
        }
        
        # Compare states
        changes = self._compare_states(previous_state, current_state)
        
        if changes:
            result["has_changes"] = True
            result["changes"] = changes
            
            # Check if this is an override
            if "override_source" in changes:
                result["is_override"] = True
                result["override_source"] = changes["override_source"]
            
            # Calculate drift percentage
            drift_percentage, drift_details = self._calculate_drift(previous_state, current_state, changes)
            result["drift_percentage"] = drift_percentage
            result["drift_details"] = drift_details
            
            # Record drift event
            self._record_drift_event(capsule_id, previous_state, current_state, result)
        
        return result
    
    def detect_baseline_drift(self, capsule_id: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect drift from baseline state.
        
        Args:
            capsule_id: ID of the capsule
            current_state: Current state of the capsule
            
        Returns:
            Dictionary with drift information
        """
        if capsule_id not in self.baseline_states:
            logger.warning(f"No baseline state found for capsule {capsule_id}")
            return {
                "has_changes": False,
                "error": "No baseline state found"
            }
        
        baseline_state = self.baseline_states[capsule_id]
        
        # Detect drift
        result = self.detect_drift(baseline_state, current_state)
        
        # Add baseline-specific information
        result["from_baseline"] = True
        result["baseline_version"] = baseline_state.get("version", "unknown")
        
        return result
    
    def get_drift_history(self, capsule_id: str) -> List[Dict[str, Any]]:
        """
        Get the drift history for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            List of drift event dictionaries
        """
        return self.drift_history.get(capsule_id, [])
    
    def get_drift_summary(self, capsule_id: str) -> Dict[str, Any]:
        """
        Get a summary of drift for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Dictionary with drift summary
        """
        history = self.drift_history.get(capsule_id, [])
        
        if not history:
            return {
                "capsule_id": capsule_id,
                "drift_detected": False,
                "total_drift_events": 0
            }
        
        # Calculate average drift percentage
        avg_drift = sum(event["drift_percentage"] for event in history) / len(history)
        
        # Count drift events by category
        drift_categories = {}
        for event in history:
            for category, details in event["drift_details"].items():
                if category not in drift_categories:
                    drift_categories[category] = 0
                drift_categories[category] += 1
        
        # Determine if drift exceeds thresholds
        exceeds_thresholds = False
        for category, threshold in self.drift_thresholds.items():
            if category in drift_categories and drift_categories[category] > 0:
                exceeds_thresholds = True
                break
        
        return {
            "capsule_id": capsule_id,
            "drift_detected": True,
            "total_drift_events": len(history),
            "average_drift_percentage": avg_drift,
            "drift_categories": drift_categories,
            "exceeds_thresholds": exceeds_thresholds,
            "first_drift_time": history[0]["timestamp"],
            "latest_drift_time": history[-1]["timestamp"]
        }
    
    def _compare_states(self, previous_state: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare previous and current states to identify changes.
        
        Args:
            previous_state: Previous state of the capsule
            current_state: Current state of the capsule
            
        Returns:
            Dictionary with changes
        """
        changes = {}
        
        # Compare top-level fields
        for key in set(list(previous_state.keys()) + list(current_state.keys())):
            # Skip timestamp and other metadata fields
            if key in ["timestamp", "last_updated"]:
                continue
            
            # Check if field exists in both states
            if key in previous_state and key in current_state:
                # Check if values are different
                if previous_state[key] != current_state[key]:
                    changes[key] = {
                        "previous": previous_state[key],
                        "current": current_state[key]
                    }
            # Field exists only in previous state
            elif key in previous_state:
                changes[key] = {
                    "previous": previous_state[key],
                    "current": None
                }
            # Field exists only in current state
            else:
                changes[key] = {
                    "previous": None,
                    "current": current_state[key]
                }
        
        # Deep comparison for configuration
        if "configuration" in previous_state and "configuration" in current_state:
            config_changes = self._compare_configurations(
                previous_state["configuration"], 
                current_state["configuration"]
            )
            if config_changes:
                changes["configuration_details"] = config_changes
        
        return changes
    
    def _compare_configurations(self, previous_config: Dict[str, Any], current_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare previous and current configurations to identify changes.
        
        Args:
            previous_config: Previous configuration
            current_config: Current configuration
            
        Returns:
            Dictionary with configuration changes
        """
        changes = {}
        
        # Convert to JSON strings for comparison if they're dictionaries
        if isinstance(previous_config, dict) and isinstance(current_config, dict):
            prev_json = json.dumps(previous_config, sort_keys=True, indent=2).splitlines()
            curr_json = json.dumps(current_config, sort_keys=True, indent=2).splitlines()
            
            # Generate diff
            diff = list(difflib.unified_diff(prev_json, curr_json, n=0))
            
            if diff:
                # Process diff to extract changes
                for line in diff:
                    if line.startswith('+') and not line.startswith('+++'):
                        # Added line
                        key = line[1:].strip()
                        if key and not key.startswith('{') and not key.startswith('['):
                            parts = key.split(':', 1)
                            if len(parts) == 2:
                                field = parts[0].strip(' "')
                                value = parts[1].strip(' ,')
                                changes[field] = {
                                    "type": "added",
                                    "value": value
                                }
                    elif line.startswith('-') and not line.startswith('---'):
                        # Removed line
                        key = line[1:].strip()
                        if key and not key.startswith('{') and not key.startswith('['):
                            parts = key.split(':', 1)
                            if len(parts) == 2:
                                field = parts[0].strip(' "')
                                value = parts[1].strip(' ,')
                                changes[field] = {
                                    "type": "removed",
                                    "value": value
                                }
        else:
            # Simple comparison for non-dict types
            if previous_config != current_config:
                changes["value"] = {
                    "previous": previous_config,
                    "current": current_config
                }
        
        return changes
    
    def _calculate_drift(self, previous_state: Dict[str, Any], current_state: Dict[str, Any], 
                        changes: Dict[str, Any]) -> tuple:
        """
        Calculate drift percentage and details.
        
        Args:
            previous_state: Previous state of the capsule
            current_state: Current state of the capsule
            changes: Dictionary with changes
            
        Returns:
            Tuple of (drift_percentage, drift_details)
        """
        drift_details = {}
        total_fields = 0
        changed_fields = 0
        
        # Count total and changed fields in configuration
        if "configuration" in previous_state and "configuration" in current_state:
            config_fields = self._count_fields(previous_state["configuration"])
            total_fields += config_fields
            
            if "configuration_details" in changes:
                changed_config_fields = len(changes["configuration_details"])
                changed_fields += changed_config_fields
                
                # Calculate configuration drift percentage
                if config_fields > 0:
                    config_drift = changed_config_fields / config_fields
                    drift_details["configuration"] = config_drift
        
        # Count total and changed fields in other categories
        for category in ["resources", "status", "metadata"]:
            if category in previous_state and category in current_state:
                category_fields = self._count_fields(previous_state[category])
                total_fields += category_fields
                
                # Count changed fields in this category
                category_changes = 0
                for key in changes:
                    if key == category or key.startswith(f"{category}_"):
                        category_changes += 1
                
                changed_fields += category_changes
                
                # Calculate category drift percentage
                if category_fields > 0:
                    category_drift = category_changes / category_fields
                    drift_details[category] = category_drift
        
        # Calculate overall drift percentage
        if total_fields > 0:
            drift_percentage = changed_fields / total_fields
        else:
            drift_percentage = 0
        
        return drift_percentage, drift_details
    
    def _count_fields(self, obj: Any, prefix: str = "") -> int:
        """
        Count the number of fields in an object.
        
        Args:
            obj: Object to count fields in
            prefix: Prefix for nested fields
            
        Returns:
            Number of fields
        """
        if isinstance(obj, dict):
            count = 0
            for key, value in obj.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                count += self._count_fields(value, new_prefix)
            return count
        elif isinstance(obj, list):
            count = 0
            for i, item in enumerate(obj):
                new_prefix = f"{prefix}[{i}]"
                count += self._count_fields(item, new_prefix)
            return count
        else:
            return 1
    
    def _record_drift_event(self, capsule_id: str, previous_state: Dict[str, Any], 
                           current_state: Dict[str, Any], drift_result: Dict[str, Any]):
        """
        Record a drift event.
        
        Args:
            capsule_id: ID of the capsule
            previous_state: Previous state of the capsule
            current_state: Current state of the capsule
            drift_result: Result of drift detection
        """
        # Create drift event
        event = {
            "capsule_id": capsule_id,
            "timestamp": datetime.now().isoformat(),
            "previous_version": previous_state.get("version", "unknown"),
            "current_version": current_state.get("current_version", "unknown"),
            "drift_percentage": drift_result["drift_percentage"],
            "drift_details": drift_result["drift_details"],
            "is_override": drift_result["is_override"],
            "changes": drift_result["changes"]
        }
        
        # Initialize history for this capsule if it doesn't exist
        if capsule_id not in self.drift_history:
            self.drift_history[capsule_id] = []
        
        # Add event to history
        self.drift_history[capsule_id].append(event)
        
        # Trim history if it exceeds max length
        if len(self.drift_history[capsule_id]) > self.max_history_length:
            self.drift_history[capsule_id] = self.drift_history[capsule_id][-self.max_history_length:]
        
        logger.info(f"Recorded drift event for capsule {capsule_id}: {drift_result['drift_percentage']:.2f} drift")
        
        # Check if drift exceeds thresholds
        for category, threshold in self.drift_thresholds.items():
            if category in drift_result["drift_details"] and drift_result["drift_details"][category] > threshold:
                logger.warning(f"Drift in {category} exceeds threshold for capsule {capsule_id}: " +
                              f"{drift_result['drift_details'][category]:.2f} > {threshold}")
                
                # Integrate with MCP for alerting
                self._send_drift_alert(capsule_id, category, drift_result)
    
    def _send_drift_alert(self, capsule_id: str, category: str, drift_result: Dict[str, Any]):
        """
        Send an alert for a drift event.
        
        Args:
            capsule_id: ID of the capsule
            category: Category that exceeded threshold
            drift_result: Result of drift detection
        """
        # In a real implementation, this would send an alert to a monitoring system
        # For now, we'll just log it
        logger.warning(f"DRIFT ALERT: Capsule {capsule_id} has excessive drift in {category}")
        
        # Integration with MCP for alerting
        try:
            self._send_mcp_alert(capsule_id, category, drift_result)
        except Exception as e:
            logger.error(f"Failed to send MCP alert for drift: {str(e)}")
    
    def _send_mcp_alert(self, capsule_id: str, category: str, drift_result: Dict[str, Any]):
        """
        Send an alert via MCP.
        
        Args:
            capsule_id: ID of the capsule
            category: Category that exceeded threshold
            drift_result: Result of drift detection
        """
        # This is a placeholder for MCP integration
        # In a real implementation, this would use the MCP client to send an alert
        pass
