"""
Proximity Context Resolver - Resolves context for proximity-based triggers

This module resolves context for proximity-based triggers, determining what
capsules should be instantiated based on proximity to physical objects or locations.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import math

logger = logging.getLogger(__name__)

class ProximityContextResolver:
    """
    Resolves context for proximity-based triggers.
    
    This component is responsible for determining what capsules should be
    instantiated based on proximity to physical objects or locations, using
    data from proximity sensors or beacons.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Proximity Context Resolver.
        
        Args:
            config: Configuration dictionary for the resolver
        """
        self.config = config or {}
        self.proximity_zones = {}  # Zone ID -> Zone configuration
        self.location_mappings = {}  # Location ID -> Location configuration
        self.object_mappings = {}  # Object ID -> Object configuration
        
        logger.info("Initializing Proximity Context Resolver")
    
    def initialize(self):
        """Initialize the resolver and load zone and mapping data."""
        logger.info("Initializing Proximity Context Resolver")
        
        # Load proximity zones
        self._load_proximity_zones()
        
        # Load location mappings
        self._load_location_mappings()
        
        # Load object mappings
        self._load_object_mappings()
        
        logger.info(f"Loaded {len(self.proximity_zones)} proximity zones, " +
                   f"{len(self.location_mappings)} location mappings, and " +
                   f"{len(self.object_mappings)} object mappings")
        return True
    
    def resolve_context(self, trigger_id: str, trigger_config: Dict[str, Any], 
                       signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve context for a proximity-based trigger.
        
        Args:
            trigger_id: ID of the trigger
            trigger_config: Configuration for the trigger
            signal_data: Data from the trigger signal
            
        Returns:
            Dictionary with resolution result
        """
        logger.info(f"Resolving proximity context for trigger {trigger_id}")
        
        # Extract proximity data
        proximity_type = signal_data.get("proximity_type")
        proximity_data = signal_data.get("proximity_data", {})
        
        if not proximity_type:
            logger.error("No proximity type in signal data")
            return {"success": False, "error": "No proximity type in signal data"}
        
        # Process based on proximity type
        if proximity_type == "zone":
            return self._resolve_zone_context(trigger_id, trigger_config, proximity_data)
        elif proximity_type == "location":
            return self._resolve_location_context(trigger_id, trigger_config, proximity_data)
        elif proximity_type == "object":
            return self._resolve_object_context(trigger_id, trigger_config, proximity_data)
        elif proximity_type == "beacon":
            return self._resolve_beacon_context(trigger_id, trigger_config, proximity_data)
        elif proximity_type == "gps":
            return self._resolve_gps_context(trigger_id, trigger_config, proximity_data)
        else:
            logger.error(f"Unsupported proximity type: {proximity_type}")
            return {"success": False, "error": f"Unsupported proximity type: {proximity_type}"}
    
    def register_proximity_zone(self, zone_id: str, zone_config: Dict[str, Any]) -> bool:
        """
        Register a proximity zone.
        
        Args:
            zone_id: ID of the zone
            zone_config: Configuration for the zone
            
        Returns:
            True if successful, False otherwise
        """
        if zone_id in self.proximity_zones:
            logger.warning(f"Zone {zone_id} is already registered")
            return False
        
        # Validate zone configuration
        if not self._validate_zone_config(zone_config):
            logger.error(f"Invalid zone configuration for {zone_id}")
            return False
        
        # Register zone
        self.proximity_zones[zone_id] = zone_config
        
        # Save proximity zones
        self._save_proximity_zones()
        
        logger.info(f"Registered proximity zone {zone_id}")
        return True
    
    def unregister_proximity_zone(self, zone_id: str) -> bool:
        """
        Unregister a proximity zone.
        
        Args:
            zone_id: ID of the zone
            
        Returns:
            True if successful, False otherwise
        """
        if zone_id not in self.proximity_zones:
            logger.warning(f"Zone {zone_id} is not registered")
            return False
        
        # Unregister zone
        del self.proximity_zones[zone_id]
        
        # Save proximity zones
        self._save_proximity_zones()
        
        logger.info(f"Unregistered proximity zone {zone_id}")
        return True
    
    def register_location_mapping(self, location_id: str, location_config: Dict[str, Any]) -> bool:
        """
        Register a location mapping.
        
        Args:
            location_id: ID of the location
            location_config: Configuration for the location
            
        Returns:
            True if successful, False otherwise
        """
        if location_id in self.location_mappings:
            logger.warning(f"Location {location_id} is already registered")
            return False
        
        # Validate location configuration
        if not self._validate_location_config(location_config):
            logger.error(f"Invalid location configuration for {location_id}")
            return False
        
        # Register location
        self.location_mappings[location_id] = location_config
        
        # Save location mappings
        self._save_location_mappings()
        
        logger.info(f"Registered location mapping {location_id}")
        return True
    
    def unregister_location_mapping(self, location_id: str) -> bool:
        """
        Unregister a location mapping.
        
        Args:
            location_id: ID of the location
            
        Returns:
            True if successful, False otherwise
        """
        if location_id not in self.location_mappings:
            logger.warning(f"Location {location_id} is not registered")
            return False
        
        # Unregister location
        del self.location_mappings[location_id]
        
        # Save location mappings
        self._save_location_mappings()
        
        logger.info(f"Unregistered location mapping {location_id}")
        return True
    
    def register_object_mapping(self, object_id: str, object_config: Dict[str, Any]) -> bool:
        """
        Register an object mapping.
        
        Args:
            object_id: ID of the object
            object_config: Configuration for the object
            
        Returns:
            True if successful, False otherwise
        """
        if object_id in self.object_mappings:
            logger.warning(f"Object {object_id} is already registered")
            return False
        
        # Validate object configuration
        if not self._validate_object_config(object_config):
            logger.error(f"Invalid object configuration for {object_id}")
            return False
        
        # Register object
        self.object_mappings[object_id] = object_config
        
        # Save object mappings
        self._save_object_mappings()
        
        logger.info(f"Registered object mapping {object_id}")
        return True
    
    def unregister_object_mapping(self, object_id: str) -> bool:
        """
        Unregister an object mapping.
        
        Args:
            object_id: ID of the object
            
        Returns:
            True if successful, False otherwise
        """
        if object_id not in self.object_mappings:
            logger.warning(f"Object {object_id} is not registered")
            return False
        
        # Unregister object
        del self.object_mappings[object_id]
        
        # Save object mappings
        self._save_object_mappings()
        
        logger.info(f"Unregistered object mapping {object_id}")
        return True
    
    def _resolve_zone_context(self, trigger_id: str, trigger_config: Dict[str, Any], 
                             proximity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve context for a zone-based proximity trigger.
        
        Args:
            trigger_id: ID of the trigger
            trigger_config: Configuration for the trigger
            proximity_data: Proximity data
            
        Returns:
            Dictionary with resolution result
        """
        # Extract zone ID
        zone_id = proximity_data.get("zone_id")
        
        if not zone_id:
            logger.error("No zone ID in proximity data")
            return {"success": False, "error": "No zone ID in proximity data"}
        
        # Check if zone exists
        if zone_id not in self.proximity_zones:
            logger.error(f"Zone {zone_id} not found")
            return {"success": False, "error": f"Zone {zone_id} not found"}
        
        # Get zone configuration
        zone_config = self.proximity_zones[zone_id]
        
        # Extract proximity level
        proximity_level = proximity_data.get("proximity_level", "unknown")
        
        # Check if proximity level is valid
        valid_levels = ["near", "medium", "far", "unknown"]
        if proximity_level not in valid_levels:
            logger.warning(f"Invalid proximity level: {proximity_level}, defaulting to 'unknown'")
            proximity_level = "unknown"
        
        # Get action for this zone and proximity level
        action = zone_config.get("actions", {}).get(proximity_level)
        
        if not action:
            logger.error(f"No action defined for zone {zone_id} and proximity level {proximity_level}")
            return {"success": False, "error": f"No action defined for zone {zone_id} and proximity level {proximity_level}"}
        
        # Build context
        context = {
            "trigger_id": trigger_id,
            "proximity_type": "zone",
            "zone_id": zone_id,
            "zone_name": zone_config.get("name", "Unknown Zone"),
            "proximity_level": proximity_level,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add zone-specific context
        if "context_data" in zone_config:
            context["zone_context"] = zone_config["context_data"]
        
        logger.info(f"Resolved zone context for trigger {trigger_id}, zone {zone_id}, proximity level {proximity_level}")
        
        return {
            "success": True,
            "context": context,
            "action": action
        }
    
    def _resolve_location_context(self, trigger_id: str, trigger_config: Dict[str, Any], 
                                proximity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve context for a location-based proximity trigger.
        
        Args:
            trigger_id: ID of the trigger
            trigger_config: Configuration for the trigger
            proximity_data: Proximity data
            
        Returns:
            Dictionary with resolution result
        """
        # Extract location ID
        location_id = proximity_data.get("location_id")
        
        if not location_id:
            logger.error("No location ID in proximity data")
            return {"success": False, "error": "No location ID in proximity data"}
        
        # Check if location exists
        if location_id not in self.location_mappings:
            logger.error(f"Location {location_id} not found")
            return {"success": False, "error": f"Location {location_id} not found"}
        
        # Get location configuration
        location_config = self.location_mappings[location_id]
        
        # Extract distance
        distance = proximity_data.get("distance")
        
        # Determine proximity level based on distance
        proximity_level = "unknown"
        if distance is not None:
            thresholds = location_config.get("distance_thresholds", {})
            if distance <= thresholds.get("near", 1):
                proximity_level = "near"
            elif distance <= thresholds.get("medium", 5):
                proximity_level = "medium"
            else:
                proximity_level = "far"
        
        # Get action for this location and proximity level
        action = location_config.get("actions", {}).get(proximity_level)
        
        if not action:
            logger.error(f"No action defined for location {location_id} and proximity level {proximity_level}")
            return {"success": False, "error": f"No action defined for location {location_id} and proximity level {proximity_level}"}
        
        # Build context
        context = {
            "trigger_id": trigger_id,
            "proximity_type": "location",
            "location_id": location_id,
            "location_name": location_config.get("name", "Unknown Location"),
            "distance": distance,
            "proximity_level": proximity_level,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add location-specific context
        if "context_data" in location_config:
            context["location_context"] = location_config["context_data"]
        
        logger.info(f"Resolved location context for trigger {trigger_id}, location {location_id}, proximity level {proximity_level}")
        
        return {
            "success": True,
            "context": context,
            "action": action
        }
    
    def _resolve_object_context(self, trigger_id: str, trigger_config: Dict[str, Any], 
                              proximity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve context for an object-based proximity trigger.
        
        Args:
            trigger_id: ID of the trigger
            trigger_config: Configuration for the trigger
            proximity_data: Proximity data
            
        Returns:
            Dictionary with resolution result
        """
        # Extract object ID
        object_id = proximity_data.get("object_id")
        
        if not object_id:
            logger.error("No object ID in proximity data")
            return {"success": False, "error": "No object ID in proximity data"}
        
        # Check if object exists
        if object_id not in self.object_mappings:
            logger.error(f"Object {object_id} not found")
            return {"success": False, "error": f"Object {object_id} not found"}
        
        # Get object configuration
        object_config = self.object_mappings[object_id]
        
        # Extract distance
        distance = proximity_data.get("distance")
        
        # Determine proximity level based on distance
        proximity_level = "unknown"
        if distance is not None:
            thresholds = object_config.get("distance_thresholds", {})
            if distance <= thresholds.get("near", 0.5):
                proximity_level = "near"
            elif distance <= thresholds.get("medium", 2):
                proximity_level = "medium"
            else:
                proximity_level = "far"
        
        # Get action for this object and proximity level
        action = object_config.get("actions", {}).get(proximity_level)
        
        if not action:
            logger.error(f"No action defined for object {object_id} and proximity level {proximity_level}")
            return {"success": False, "error": f"No action defined for object {object_id} and proximity level {proximity_level}"}
        
        # Build context
        context = {
            "trigger_id": trigger_id,
            "proximity_type": "object",
            "object_id": object_id,
            "object_name": object_config.get("name", "Unknown Object"),
            "object_type": object_config.get("type", "unknown"),
            "distance": distance,
            "proximity_level": proximity_level,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add object-specific context
        if "context_data" in object_config:
            context["object_context"] = object_config["context_data"]
        
        logger.info(f"Resolved object context for trigger {trigger_id}, object {object_id}, proximity level {proximity_level}")
        
        return {
            "success": True,
            "context": context,
            "action": action
        }
    
    def _resolve_beacon_context(self, trigger_id: str, trigger_config: Dict[str, Any], 
                              proximity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve context for a beacon-based proximity trigger.
        
        Args:
            trigger_id: ID of the trigger
            trigger_config: Configuration for the trigger
            proximity_data: Proximity data
            
        Returns:
            Dictionary with resolution result
        """
        # Extract beacon ID and RSSI
        beacon_id = proximity_data.get("beacon_id")
        rssi = proximity_data.get("rssi")
        
        if not beacon_id:
            logger.error("No beacon ID in proximity data")
            return {"success": False, "error": "No beacon ID in proximity data"}
        
        if rssi is None:
            logger.error("No RSSI value in proximity data")
            return {"success": False, "error": "No RSSI value in proximity data"}
        
        # Map beacon to location or object
        location_id = None
        object_id = None
        
        # Check if beacon is mapped to a location
        for loc_id, loc_config in self.location_mappings.items():
            if "beacons" in loc_config and beacon_id in loc_config["beacons"]:
                location_id = loc_id
                break
        
        # If not mapped to a location, check if mapped to an object
        if not location_id:
            for obj_id, obj_config in self.object_mappings.items():
                if "beacons" in obj_config and beacon_id in obj_config["beacons"]:
                    object_id = obj_id
                    break
        
        # If beacon is not mapped, return error
        if not location_id and not object_id:
            logger.error(f"Beacon {beacon_id} not mapped to any location or object")
            return {"success": False, "error": f"Beacon {beacon_id} not mapped to any location or object"}
        
        # Determine proximity level based on RSSI
        # RSSI values are negative, with values closer to 0 indicating closer proximity
        proximity_level = "unknown"
        if rssi >= -50:  # Very close
            proximity_level = "near"
        elif rssi >= -70:  # Medium distance
            proximity_level = "medium"
        else:  # Far away
            proximity_level = "far"
        
        # Resolve context based on mapping
        if location_id:
            # Create proximity data for location resolution
            location_proximity_data = {
                "location_id": location_id,
                "distance": self._rssi_to_distance(rssi)
            }
            return self._resolve_location_context(trigger_id, trigger_config, location_proximity_data)
        else:
            # Create proximity data for object resolution
            object_proximity_data = {
                "object_id": object_id,
                "distance": self._rssi_to_distance(rssi)
            }
            return self._resolve_object_context(trigger_id, trigger_config, object_proximity_data)
    
    def _resolve_gps_context(self, trigger_id: str, trigger_config: Dict[str, Any], 
                           proximity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve context for a GPS-based proximity trigger.
        
        Args:
            trigger_id: ID of the trigger
            trigger_config: Configuration for the trigger
            proximity_data: Proximity data
            
        Returns:
            Dictionary with resolution result
        """
        # Extract GPS coordinates
        latitude = proximity_data.get("latitude")
        longitude = proximity_data.get("longitude")
        
        if latitude is None or longitude is None:
            logger.error("Missing GPS coordinates in proximity data")
            return {"success": False, "error": "Missing GPS coordinates in proximity data"}
        
        # Find nearest location
        nearest_location_id = None
        nearest_distance = float('inf')
        
        for location_id, location_config in self.location_mappings.items():
            if "gps" in location_config:
                loc_lat = location_config["gps"].get("latitude")
                loc_lon = location_config["gps"].get("longitude")
                
                if loc_lat is not None and loc_lon is not None:
                    distance = self._calculate_gps_distance(latitude, longitude, loc_lat, loc_lon)
                    
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_location_id = location_id
        
        if not nearest_location_id:
            logger.error("No locations with GPS coordinates found")
            return {"success": False, "error": "No locations with GPS coordinates found"}
        
        # Create proximity data for location resolution
        location_proximity_data = {
            "location_id": nearest_location_id,
            "distance": nearest_distance
        }
        
        return self._resolve_location_context(trigger_id, trigger_config, location_proximity_data)
    
    def _validate_zone_config(self, zone_config: Dict[str, Any]) -> bool:
        """
        Validate a zone configuration.
        
        Args:
            zone_config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in zone_config:
                logger.error(f"Missing required field in zone configuration: {field}")
                return False
        
        # Check actions
        if "actions" not in zone_config:
            logger.error("Missing actions in zone configuration")
            return False
        
        # Check that at least one proximity level has an action
        proximity_levels = ["near", "medium", "far", "unknown"]
        if not any(level in zone_config["actions"] for level in proximity_levels):
            logger.error("No actions defined for any proximity level")
            return False
        
        return True
    
    def _validate_location_config(self, location_config: Dict[str, Any]) -> bool:
        """
        Validate a location configuration.
        
        Args:
            location_config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in location_config:
                logger.error(f"Missing required field in location configuration: {field}")
                return False
        
        # Check actions
        if "actions" not in location_config:
            logger.error("Missing actions in location configuration")
            return False
        
        # Check that at least one proximity level has an action
        proximity_levels = ["near", "medium", "far", "unknown"]
        if not any(level in location_config["actions"] for level in proximity_levels):
            logger.error("No actions defined for any proximity level")
            return False
        
        # Check location identifiers
        location_identifiers = ["gps", "beacons", "zone_id"]
        if not any(identifier in location_config for identifier in location_identifiers):
            logger.error("No location identifiers defined")
            return False
        
        return True
    
    def _validate_object_config(self, object_config: Dict[str, Any]) -> bool:
        """
        Validate an object configuration.
        
        Args:
            object_config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "type"]
        for field in required_fields:
            if field not in object_config:
                logger.error(f"Missing required field in object configuration: {field}")
                return False
        
        # Check actions
        if "actions" not in object_config:
            logger.error("Missing actions in object configuration")
            return False
        
        # Check that at least one proximity level has an action
        proximity_levels = ["near", "medium", "far", "unknown"]
        if not any(level in object_config["actions"] for level in proximity_levels):
            logger.error("No actions defined for any proximity level")
            return False
        
        # Check object identifiers
        object_identifiers = ["beacons", "rfid", "qr_code"]
        if not any(identifier in object_config for identifier in object_identifiers):
            logger.error("No object identifiers defined")
            return False
        
        return True
    
    def _calculate_gps_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two GPS coordinates using the Haversine formula.
        
        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point
            
        Returns:
            Distance in kilometers
        """
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def _rssi_to_distance(self, rssi: int) -> float:
        """
        Convert RSSI to approximate distance.
        
        Args:
            rssi: RSSI value
            
        Returns:
            Approximate distance in meters
        """
        # This is a simplified model
        # In a real implementation, this would use a more sophisticated model
        # that takes into account the specific beacon and environment
        
        # RSSI at 1 meter
        rssi_at_1m = -60
        
        # Path loss exponent (depends on environment)
        n = 2.0
        
        # Calculate distance
        if rssi >= 0:
            return 0.1  # Very close
        
        distance = 10 ** ((rssi_at_1m - rssi) / (10 * n))
        
        return distance
    
    def _load_proximity_zones(self):
        """Load proximity zones from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.proximity_zones = {}
            logger.info("Loaded proximity zones")
        except Exception as e:
            logger.error(f"Failed to load proximity zones: {str(e)}")
    
    def _save_proximity_zones(self):
        """Save proximity zones to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.proximity_zones)} proximity zones")
        except Exception as e:
            logger.error(f"Failed to save proximity zones: {str(e)}")
    
    def _load_location_mappings(self):
        """Load location mappings from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.location_mappings = {}
            logger.info("Loaded location mappings")
        except Exception as e:
            logger.error(f"Failed to load location mappings: {str(e)}")
    
    def _save_location_mappings(self):
        """Save location mappings to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.location_mappings)} location mappings")
        except Exception as e:
            logger.error(f"Failed to save location mappings: {str(e)}")
    
    def _load_object_mappings(self):
        """Load object mappings from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.object_mappings = {}
            logger.info("Loaded object mappings")
        except Exception as e:
            logger.error(f"Failed to load object mappings: {str(e)}")
    
    def _save_object_mappings(self):
        """Save object mappings to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.object_mappings)} object mappings")
        except Exception as e:
            logger.error(f"Failed to save object mappings: {str(e)}")
