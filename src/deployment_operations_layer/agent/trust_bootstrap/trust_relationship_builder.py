"""
Trust Relationship Builder

This module builds trust relationships between capsules and components in a deployment.
It establishes the connections and dependencies between different entities in the
trust ecosystem, ensuring proper communication and security boundaries.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class TrustRelationshipBuilder:
    """
    Builder for trust relationships in deployments.
    """
    
    def __init__(self, relationship_templates_path: Optional[str] = None):
        """
        Initialize the Trust Relationship Builder.
        
        Args:
            relationship_templates_path: Path to relationship templates file
        """
        self.relationship_templates_path = relationship_templates_path or os.environ.get(
            "TRUST_RELATIONSHIP_TEMPLATES_PATH", "/var/lib/industriverse/trust/relationship_templates.json"
        )
        self.relationship_templates = self._load_relationship_templates()
        logger.info("Trust Relationship Builder initialized")
    
    def build_relationships(self, 
                          deployment_manifest: Dict[str, Any], 
                          context: Dict[str, Any],
                          zones: Dict[str, Any],
                          scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build trust relationships for a deployment.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            zones: Trust zones configuration
            scores: Trust scores
            
        Returns:
            Dict containing built relationships
        """
        logger.info(f"Building trust relationships for deployment: {deployment_manifest.get('name', 'unnamed')}")
        
        try:
            # Build component-to-component relationships
            component_relationships = self._build_component_relationships(
                deployment_manifest, context, zones, scores
            )
            
            # Build zone-to-zone relationships
            zone_relationships = self._build_zone_relationships(
                deployment_manifest, context, zones
            )
            
            # Build external relationships
            external_relationships = self._build_external_relationships(
                deployment_manifest, context, zones, scores
            )
            
            # Prepare result
            relationships = {
                "component": component_relationships,
                "zone": zone_relationships,
                "external": external_relationships,
                "timestamp": self._get_timestamp()
            }
            
            return {
                "success": True,
                "relationships": relationships
            }
            
        except Exception as e:
            logger.exception(f"Error building trust relationships: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_relationship(self, 
                            source: str, 
                            target: str, 
                            relationship_type: str,
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a trust relationship.
        
        Args:
            source: Source entity
            target: Target entity
            relationship_type: Type of relationship
            context: Validation context
            
        Returns:
            Dict containing validation result
        """
        logger.info(f"Validating {relationship_type} relationship from {source} to {target}")
        
        try:
            # In a real implementation, this would perform complex validation
            # For now, return a simulated result
            return {
                "valid": True,
                "source": source,
                "target": target,
                "type": relationship_type
            }
            
        except Exception as e:
            logger.exception(f"Error validating relationship: {str(e)}")
            return {
                "valid": False,
                "source": source,
                "target": target,
                "type": relationship_type,
                "error": str(e)
            }
    
    def _load_relationship_templates(self) -> Dict[str, Any]:
        """
        Load trust relationship templates from file.
        
        Returns:
            Dict containing relationship templates
        """
        try:
            if os.path.exists(self.relationship_templates_path):
                with open(self.relationship_templates_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Relationship templates file not found: {self.relationship_templates_path}")
                return self._get_default_relationship_templates()
                
        except Exception as e:
            logger.exception(f"Error loading relationship templates: {str(e)}")
            return self._get_default_relationship_templates()
    
    def _get_default_relationship_templates(self) -> Dict[str, Any]:
        """
        Get default trust relationship templates.
        
        Returns:
            Dict containing default relationship templates
        """
        return {
            "component": {
                "depends_on": {
                    "description": "Component depends on another component",
                    "trust_level": "high",
                    "bidirectional": False,
                    "default_policies": ["dependency_access_policy"]
                },
                "communicates_with": {
                    "description": "Component communicates with another component",
                    "trust_level": "medium",
                    "bidirectional": True,
                    "default_policies": ["communication_access_policy"]
                },
                "monitors": {
                    "description": "Component monitors another component",
                    "trust_level": "medium",
                    "bidirectional": False,
                    "default_policies": ["monitoring_access_policy"]
                },
                "manages": {
                    "description": "Component manages another component",
                    "trust_level": "high",
                    "bidirectional": False,
                    "default_policies": ["management_access_policy"]
                }
            },
            "zone": {
                "connects_to": {
                    "description": "Zone connects to another zone",
                    "trust_level": "medium",
                    "bidirectional": False,
                    "default_policies": ["zone_connection_policy"]
                },
                "contains": {
                    "description": "Zone contains another zone",
                    "trust_level": "high",
                    "bidirectional": False,
                    "default_policies": ["zone_containment_policy"]
                }
            },
            "external": {
                "integrates_with": {
                    "description": "Component integrates with external system",
                    "trust_level": "low",
                    "bidirectional": True,
                    "default_policies": ["external_integration_policy"]
                },
                "authenticates_with": {
                    "description": "Component authenticates with external system",
                    "trust_level": "medium",
                    "bidirectional": True,
                    "default_policies": ["external_authentication_policy"]
                }
            }
        }
    
    def _build_component_relationships(self, 
                                     deployment_manifest: Dict[str, Any], 
                                     context: Dict[str, Any],
                                     zones: Dict[str, Any],
                                     scores: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build component-to-component relationships.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            zones: Trust zones configuration
            scores: Trust scores
            
        Returns:
            List of component relationships
        """
        relationships = []
        
        # Get components from manifest
        components = deployment_manifest.get("components", {})
        
        # Process each component
        for component_name, component_config in components.items():
            # Process dependencies
            if "dependencies" in component_config:
                for dependency in component_config["dependencies"]:
                    dep_name = dependency.get("name")
                    if dep_name and dep_name in components:
                        relationship = self._create_component_relationship(
                            component_name, dep_name, "depends_on",
                            deployment_manifest, context, zones, scores
                        )
                        relationships.append(relationship)
            
            # Process communications
            if "communications" in component_config:
                for comm in component_config["communications"]:
                    target_name = comm.get("target")
                    if target_name and target_name in components:
                        relationship = self._create_component_relationship(
                            component_name, target_name, "communicates_with",
                            deployment_manifest, context, zones, scores
                        )
                        relationships.append(relationship)
            
            # Process monitoring
            if "monitors" in component_config:
                for monitored in component_config["monitors"]:
                    if monitored in components:
                        relationship = self._create_component_relationship(
                            component_name, monitored, "monitors",
                            deployment_manifest, context, zones, scores
                        )
                        relationships.append(relationship)
            
            # Process management
            if "manages" in component_config:
                for managed in component_config["manages"]:
                    if managed in components:
                        relationship = self._create_component_relationship(
                            component_name, managed, "manages",
                            deployment_manifest, context, zones, scores
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _create_component_relationship(self, 
                                     source: str, 
                                     target: str, 
                                     relationship_type: str,
                                     deployment_manifest: Dict[str, Any],
                                     context: Dict[str, Any],
                                     zones: Dict[str, Any],
                                     scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a component relationship.
        
        Args:
            source: Source component
            target: Target component
            relationship_type: Type of relationship
            deployment_manifest: Deployment manifest
            context: Deployment context
            zones: Trust zones configuration
            scores: Trust scores
            
        Returns:
            Component relationship
        """
        # Get template for this relationship type
        template = self.relationship_templates["component"].get(relationship_type, {
            "trust_level": "medium",
            "bidirectional": False,
            "default_policies": []
        })
        
        # Get component configurations
        components = deployment_manifest.get("components", {})
        source_config = components.get(source, {})
        target_config = components.get(target, {})
        
        # Get component zones
        source_zone = source_config.get("trust_zone", "internal")
        target_zone = target_config.get("trust_zone", "internal")
        
        # Get component scores
        source_score = scores.get("components", {}).get(source, {}).get("score", 80)
        target_score = scores.get("components", {}).get(target, {}).get("score", 80)
        
        # Calculate trust level based on scores
        trust_level = self._calculate_relationship_trust_level(
            source_score, target_score, template["trust_level"]
        )
        
        # Create relationship
        relationship = {
            "source": source,
            "target": target,
            "type": relationship_type,
            "trust_level": trust_level,
            "bidirectional": template["bidirectional"],
            "source_zone": source_zone,
            "target_zone": target_zone,
            "policies": list(template["default_policies"]),
            "created_at": self._get_timestamp()
        }
        
        return relationship
    
    def _build_zone_relationships(self, 
                                deployment_manifest: Dict[str, Any], 
                                context: Dict[str, Any],
                                zones: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build zone-to-zone relationships.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            zones: Trust zones configuration
            
        Returns:
            List of zone relationships
        """
        relationships = []
        
        # Process each zone
        for zone_name, zone_config in zones.items():
            # Process boundaries
            if "boundaries" in zone_config:
                for target_zone, boundary in zone_config["boundaries"].items():
                    if target_zone in zones:
                        boundary_type = boundary.get("type")
                        
                        if boundary_type == "bidirectional":
                            relationship = self._create_zone_relationship(
                                zone_name, target_zone, "connects_to",
                                deployment_manifest, context, zones
                            )
                            relationships.append(relationship)
                            
                            # Add reverse relationship
                            relationship = self._create_zone_relationship(
                                target_zone, zone_name, "connects_to",
                                deployment_manifest, context, zones
                            )
                            relationships.append(relationship)
                            
                        elif boundary_type == "outbound":
                            relationship = self._create_zone_relationship(
                                zone_name, target_zone, "connects_to",
                                deployment_manifest, context, zones
                            )
                            relationships.append(relationship)
                            
                        elif boundary_type == "inbound":
                            relationship = self._create_zone_relationship(
                                target_zone, zone_name, "connects_to",
                                deployment_manifest, context, zones
                            )
                            relationships.append(relationship)
        
        return relationships
    
    def _create_zone_relationship(self, 
                                source: str, 
                                target: str, 
                                relationship_type: str,
                                deployment_manifest: Dict[str, Any],
                                context: Dict[str, Any],
                                zones: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a zone relationship.
        
        Args:
            source: Source zone
            target: Target zone
            relationship_type: Type of relationship
            deployment_manifest: Deployment manifest
            context: Deployment context
            zones: Trust zones configuration
            
        Returns:
            Zone relationship
        """
        # Get template for this relationship type
        template = self.relationship_templates["zone"].get(relationship_type, {
            "trust_level": "medium",
            "bidirectional": False,
            "default_policies": []
        })
        
        # Get zone configurations
        source_config = zones.get(source, {})
        target_config = zones.get(target, {})
        
        # Create relationship
        relationship = {
            "source": source,
            "target": target,
            "type": relationship_type,
            "trust_level": template["trust_level"],
            "bidirectional": template["bidirectional"],
            "policies": list(template["default_policies"]),
            "created_at": self._get_timestamp()
        }
        
        return relationship
    
    def _build_external_relationships(self, 
                                    deployment_manifest: Dict[str, Any], 
                                    context: Dict[str, Any],
                                    zones: Dict[str, Any],
                                    scores: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build relationships with external systems.
        
        Args:
            deployment_manifest: Deployment manifest
            context: Deployment context
            zones: Trust zones configuration
            scores: Trust scores
            
        Returns:
            List of external relationships
        """
        relationships = []
        
        # Get components from manifest
        components = deployment_manifest.get("components", {})
        
        # Get external integrations
        external_integrations = deployment_manifest.get("external_integrations", [])
        
        # Process each integration
        for integration in external_integrations:
            integration_name = integration.get("name")
            integration_type = integration.get("type", "integrates_with")
            
            # Get components that use this integration
            for component_name, component_config in components.items():
                if "external_integrations" in component_config:
                    if integration_name in component_config["external_integrations"]:
                        relationship = self._create_external_relationship(
                            component_name, integration_name, integration_type,
                            deployment_manifest, context, zones, scores
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _create_external_relationship(self, 
                                    source: str, 
                                    target: str, 
                                    relationship_type: str,
                                    deployment_manifest: Dict[str, Any],
                                    context: Dict[str, Any],
                                    zones: Dict[str, Any],
                                    scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an external relationship.
        
        Args:
            source: Source component
            target: External system name
            relationship_type: Type of relationship
            deployment_manifest: Deployment manifest
            context: Deployment context
            zones: Trust zones configuration
            scores: Trust scores
            
        Returns:
            External relationship
        """
        # Get template for this relationship type
        template = self.relationship_templates["external"].get(relationship_type, {
            "trust_level": "low",
            "bidirectional": True,
            "default_policies": []
        })
        
        # Get component configuration
        components = deployment_manifest.get("components", {})
        source_config = components.get(source, {})
        
        # Get component zone
        source_zone = source_config.get("trust_zone", "internal")
        
        # Get external integrations
        external_integrations = deployment_manifest.get("external_integrations", [])
        target_config = next((i for i in external_integrations if i.get("name") == target), {})
        
        # Create relationship
        relationship = {
            "source": source,
            "target": target,
            "type": relationship_type,
            "trust_level": template["trust_level"],
            "bidirectional": template["bidirectional"],
            "source_zone": source_zone,
            "external_type": target_config.get("system_type", "unknown"),
            "policies": list(template["default_policies"]),
            "created_at": self._get_timestamp()
        }
        
        return relationship
    
    def _calculate_relationship_trust_level(self, 
                                          source_score: float, 
                                          target_score: float,
                                          base_level: str) -> str:
        """
        Calculate trust level for a relationship based on component scores.
        
        Args:
            source_score: Source component trust score
            target_score: Target component trust score
            base_level: Base trust level from template
            
        Returns:
            Calculated trust level
        """
        # Define trust level thresholds
        trust_levels = {
            "critical": 90,
            "high": 80,
            "medium": 70,
            "low": 60,
            "minimal": 0
        }
        
        # Calculate average score
        avg_score = (source_score + target_score) / 2
        
        # Determine trust level based on average score
        if avg_score >= trust_levels["critical"]:
            return "critical"
        elif avg_score >= trust_levels["high"]:
            return "high"
        elif avg_score >= trust_levels["medium"]:
            return "medium"
        elif avg_score >= trust_levels["low"]:
            return "low"
        else:
            return "minimal"
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
