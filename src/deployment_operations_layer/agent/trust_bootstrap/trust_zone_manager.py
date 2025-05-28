"""
Trust Zone Manager

This module manages trust zones for deployments. It handles the initialization,
configuration, and management of trust zones that define security boundaries
within a deployment.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class TrustZoneManager:
    """
    Manager for trust zones in deployments.
    """
    
    def __init__(self, zone_definitions_path: Optional[str] = None):
        """
        Initialize the Trust Zone Manager.
        
        Args:
            zone_definitions_path: Path to zone definitions file
        """
        self.zone_definitions_path = zone_definitions_path or os.environ.get(
            "TRUST_ZONE_DEFINITIONS_PATH", "/var/lib/industriverse/trust/zones.json"
        )
        self.zone_definitions = self._load_zone_definitions()
        logger.info("Trust Zone Manager initialized")
    
    def initialize_zones(self, 
                        deployment_manifest: Dict[str, Any], 
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize trust zones for a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            
        Returns:
            Dict containing initialized zones
        """
        logger.info(f"Initializing trust zones for deployment: {deployment_manifest.get('name', 'unnamed')}")
        
        try:
            # Determine required zones based on manifest and context
            required_zones = self._determine_required_zones(deployment_manifest, context)
            
            # Create zone configurations
            zones = {}
            for zone_name in required_zones:
                zone_config = self._create_zone_config(zone_name, deployment_manifest, context)
                zones[zone_name] = zone_config
            
            # Establish zone boundaries and relationships
            self._establish_zone_boundaries(zones, deployment_manifest, context)
            
            return {
                "success": True,
                "zones": zones
            }
            
        except Exception as e:
            logger.exception(f"Error initializing trust zones: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_zone_config(self, zone_name: str) -> Dict[str, Any]:
        """
        Get configuration for a trust zone.
        
        Args:
            zone_name: Name of the zone
            
        Returns:
            Zone configuration
        """
        if zone_name in self.zone_definitions:
            return self.zone_definitions[zone_name]
        else:
            return {
                "name": zone_name,
                "default_trust_level": "medium",
                "isolation_level": "standard",
                "crypto_requirements": "standard"
            }
    
    def validate_zone_compatibility(self, 
                                  zone1: str, 
                                  zone2: str, 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate compatibility between two trust zones.
        
        Args:
            zone1: First zone name
            zone2: Second zone name
            context: Validation context
            
        Returns:
            Dict containing validation result
        """
        logger.info(f"Validating compatibility between zones {zone1} and {zone2}")
        
        try:
            zone1_config = self.get_zone_config(zone1)
            zone2_config = self.get_zone_config(zone2)
            
            # In a real implementation, this would perform complex compatibility checks
            # For now, use a simple rule: zones are compatible if they have the same or adjacent trust levels
            trust_levels = ["low", "medium", "high", "critical"]
            
            zone1_level = zone1_config.get("default_trust_level", "medium")
            zone2_level = zone2_config.get("default_trust_level", "medium")
            
            if zone1_level not in trust_levels or zone2_level not in trust_levels:
                return {
                    "compatible": False,
                    "reason": f"Invalid trust level: {zone1_level} or {zone2_level}"
                }
            
            zone1_idx = trust_levels.index(zone1_level)
            zone2_idx = trust_levels.index(zone2_level)
            
            # Compatible if same level or adjacent levels
            compatible = abs(zone1_idx - zone2_idx) <= 1
            
            return {
                "compatible": compatible,
                "reason": "Trust levels are compatible" if compatible else "Trust levels are too different"
            }
            
        except Exception as e:
            logger.exception(f"Error validating zone compatibility: {str(e)}")
            return {
                "compatible": False,
                "reason": f"Error: {str(e)}"
            }
    
    def _load_zone_definitions(self) -> Dict[str, Any]:
        """
        Load trust zone definitions from file.
        
        Returns:
            Dict containing zone definitions
        """
        try:
            if os.path.exists(self.zone_definitions_path):
                with open(self.zone_definitions_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Zone definitions file not found: {self.zone_definitions_path}")
                return self._get_default_zone_definitions()
                
        except Exception as e:
            logger.exception(f"Error loading zone definitions: {str(e)}")
            return self._get_default_zone_definitions()
    
    def _get_default_zone_definitions(self) -> Dict[str, Any]:
        """
        Get default trust zone definitions.
        
        Returns:
            Dict containing default zone definitions
        """
        return {
            "public": {
                "name": "public",
                "description": "Public-facing zone with lowest trust",
                "default_trust_level": "low",
                "isolation_level": "high",
                "crypto_requirements": "standard",
                "allowed_connections": ["dmz", "internal"],
                "default_policies": ["public_access_policy"]
            },
            "dmz": {
                "name": "dmz",
                "description": "Demilitarized zone for semi-trusted components",
                "default_trust_level": "medium",
                "isolation_level": "high",
                "crypto_requirements": "standard",
                "allowed_connections": ["public", "internal"],
                "default_policies": ["dmz_access_policy"]
            },
            "internal": {
                "name": "internal",
                "description": "Internal zone for trusted components",
                "default_trust_level": "high",
                "isolation_level": "standard",
                "crypto_requirements": "standard",
                "allowed_connections": ["dmz", "secure"],
                "default_policies": ["internal_access_policy"]
            },
            "secure": {
                "name": "secure",
                "description": "Secure zone for highly sensitive components",
                "default_trust_level": "critical",
                "isolation_level": "maximum",
                "crypto_requirements": "high",
                "allowed_connections": ["internal"],
                "default_policies": ["secure_access_policy"]
            }
        }
    
    def _determine_required_zones(self, 
                                deployment_manifest: Dict[str, Any], 
                                context: Dict[str, Any]) -> List[str]:
        """
        Determine required trust zones for a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            
        Returns:
            List of required zone names
        """
        # Start with default zones
        required_zones = ["internal"]
        
        # Check if deployment has public-facing components
        if self._has_public_facing_components(deployment_manifest):
            required_zones.extend(["public", "dmz"])
        
        # Check if deployment has secure components
        if self._has_secure_components(deployment_manifest, context):
            required_zones.append("secure")
        
        # Add any explicitly requested zones
        if "trust_zones" in deployment_manifest:
            required_zones.extend(deployment_manifest["trust_zones"])
        
        # Remove duplicates and return
        return list(set(required_zones))
    
    def _has_public_facing_components(self, deployment_manifest: Dict[str, Any]) -> bool:
        """
        Check if deployment has public-facing components.
        
        Args:
            deployment_manifest: Deployment manifest
            
        Returns:
            True if deployment has public-facing components, False otherwise
        """
        # Check for ingress configurations
        if "ingress" in deployment_manifest:
            return True
        
        # Check for public services
        if "services" in deployment_manifest:
            for service in deployment_manifest["services"]:
                if service.get("exposure", "internal") == "public":
                    return True
        
        return False
    
    def _has_secure_components(self, 
                             deployment_manifest: Dict[str, Any], 
                             context: Dict[str, Any]) -> bool:
        """
        Check if deployment has secure components.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            
        Returns:
            True if deployment has secure components, False otherwise
        """
        # Check for secure data handling
        if "data_classification" in deployment_manifest:
            classifications = deployment_manifest["data_classification"]
            if "secret" in classifications or "top_secret" in classifications:
                return True
        
        # Check for secure industry context
        industry = context.get("industry")
        if industry in ["healthcare", "finance", "government", "defense"]:
            return True
        
        # Check for secure components
        if "components" in deployment_manifest:
            for component in deployment_manifest["components"].values():
                if component.get("security_level", "standard") == "high":
                    return True
        
        return False
    
    def _create_zone_config(self, 
                          zone_name: str, 
                          deployment_manifest: Dict[str, Any], 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create configuration for a trust zone.
        
        Args:
            zone_name: Name of the zone
            deployment_manifest: Deployment manifest
            context: Deployment context
            
        Returns:
            Zone configuration
        """
        # Get base configuration from definitions
        base_config = self.get_zone_config(zone_name)
        
        # Create a copy to avoid modifying the original
        zone_config = dict(base_config)
        
        # Add deployment-specific configuration
        zone_config.update({
            "deployment_id": deployment_manifest.get("id", "unknown"),
            "deployment_name": deployment_manifest.get("name", "unnamed"),
            "environment": context.get("environment", {}).get("type", "default"),
            "region": context.get("region", "default"),
            "created_at": self._get_timestamp()
        })
        
        # Apply any zone-specific overrides from manifest
        if "trust_zone_configs" in deployment_manifest and zone_name in deployment_manifest["trust_zone_configs"]:
            zone_config.update(deployment_manifest["trust_zone_configs"][zone_name])
        
        return zone_config
    
    def _establish_zone_boundaries(self, 
                                 zones: Dict[str, Any], 
                                 deployment_manifest: Dict[str, Any], 
                                 context: Dict[str, Any]):
        """
        Establish boundaries and relationships between trust zones.
        
        Args:
            zones: Dict of zone configurations
            deployment_manifest: Deployment manifest
            context: Deployment context
        """
        # For each zone, establish its boundaries with other zones
        for zone_name, zone_config in zones.items():
            zone_config["boundaries"] = {}
            
            for other_zone_name, other_zone_config in zones.items():
                if zone_name != other_zone_name:
                    # Determine boundary type based on zone definitions
                    boundary_type = self._determine_boundary_type(
                        zone_name, other_zone_name, deployment_manifest, context
                    )
                    
                    zone_config["boundaries"][other_zone_name] = {
                        "type": boundary_type,
                        "policy": f"{zone_name}_to_{other_zone_name}_policy"
                    }
    
    def _determine_boundary_type(self, 
                               zone1: str, 
                               zone2: str, 
                               deployment_manifest: Dict[str, Any], 
                               context: Dict[str, Any]) -> str:
        """
        Determine boundary type between two zones.
        
        Args:
            zone1: First zone name
            zone2: Second zone name
            deployment_manifest: Deployment manifest
            context: Deployment context
            
        Returns:
            Boundary type
        """
        # Get zone configurations
        zone1_config = self.get_zone_config(zone1)
        zone2_config = self.get_zone_config(zone2)
        
        # Check if zones allow connections to each other
        zone1_allows_zone2 = zone2 in zone1_config.get("allowed_connections", [])
        zone2_allows_zone1 = zone1 in zone2_config.get("allowed_connections", [])
        
        if zone1_allows_zone2 and zone2_allows_zone1:
            return "bidirectional"
        elif zone1_allows_zone2:
            return "outbound"
        elif zone2_allows_zone1:
            return "inbound"
        else:
            return "isolated"
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
