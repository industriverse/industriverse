"""
Capsule Validator

This module is responsible for validating capsule configurations against schemas,
security requirements, and compliance frameworks. It ensures that capsules meet
all necessary criteria before deployment.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
import jsonschema

logger = logging.getLogger(__name__)

class CapsuleValidator:
    """
    Validator for capsule configurations.
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the Capsule Validator.
        
        Args:
            schema_path: Path to the schema directory
        """
        self.schema_path = schema_path or os.environ.get(
            "CAPSULE_SCHEMA_PATH", "/var/lib/industriverse/schemas"
        )
        self.schemas = {}
        self._load_schemas()
        logger.info("Capsule Validator initialized")
    
    def validate_capsule(self, capsule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a capsule against schemas and requirements.
        
        Args:
            capsule: Capsule to validate
            context: Validation context
            
        Returns:
            Validation result
        """
        logger.info(f"Validating capsule: {capsule.get('name', 'unnamed')}")
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        # Schema validation
        schema_result = self._validate_schema(capsule)
        validation_results["checks"]["schema"] = schema_result
        
        if not schema_result["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(schema_result["errors"])
        
        # Security validation
        security_result = self._validate_security(capsule, context)
        validation_results["checks"]["security"] = security_result
        
        if not security_result["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(security_result["errors"])
        
        # Compliance validation
        compliance_result = self._validate_compliance(capsule, context)
        validation_results["checks"]["compliance"] = compliance_result
        
        if not compliance_result["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(compliance_result["errors"])
        
        # Resource validation
        resource_result = self._validate_resources(capsule, context)
        validation_results["checks"]["resources"] = resource_result
        
        if not resource_result["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(resource_result["errors"])
        
        # Dependency validation
        dependency_result = self._validate_dependencies(capsule, context)
        validation_results["checks"]["dependencies"] = dependency_result
        
        if not dependency_result["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(dependency_result["errors"])
        
        # Protocol validation
        protocol_result = self._validate_protocols(capsule, context)
        validation_results["checks"]["protocols"] = protocol_result
        
        if not protocol_result["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(protocol_result["errors"])
        
        # Log validation result
        if validation_results["valid"]:
            logger.info(f"Capsule validation successful: {capsule.get('name', 'unnamed')}")
        else:
            logger.error(f"Capsule validation failed: {capsule.get('name', 'unnamed')}")
            for error in validation_results["errors"]:
                logger.error(f"Validation error: {error}")
        
        return validation_results
    
    def _validate_schema(self, capsule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate capsule against JSON schema.
        
        Args:
            capsule: Capsule to validate
            
        Returns:
            Schema validation result
        """
        result = {
            "valid": True,
            "errors": []
        }
        
        # Get capsule type
        capsule_type = capsule.get("type", "generic")
        
        # Get schema for this capsule type
        schema = self._get_schema(capsule_type)
        
        if not schema:
            result["valid"] = False
            result["errors"].append(f"No schema found for capsule type: {capsule_type}")
            return result
        
        # Validate against schema
        try:
            jsonschema.validate(instance=capsule, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            result["valid"] = False
            result["errors"].append(f"Schema validation error: {str(e)}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Schema validation exception: {str(e)}")
        
        return result
    
    def _validate_security(self, capsule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate capsule security configuration.
        
        Args:
            capsule: Capsule to validate
            context: Validation context
            
        Returns:
            Security validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if security section exists
        if "security" not in capsule:
            result["valid"] = False
            result["errors"].append("Missing security configuration")
            return result
        
        security = capsule["security"]
        
        # Check trust zone
        if "trust_zone" not in security:
            result["valid"] = False
            result["errors"].append("Missing trust zone in security configuration")
        elif security["trust_zone"] not in self._get_valid_trust_zones(context):
            result["valid"] = False
            result["errors"].append(f"Invalid trust zone: {security['trust_zone']}")
        
        # Check crypto zone
        if "crypto_zone" not in security:
            result["valid"] = False
            result["errors"].append("Missing crypto zone in security configuration")
        elif security["crypto_zone"] not in self._get_valid_crypto_zones(context):
            result["valid"] = False
            result["errors"].append(f"Invalid crypto zone: {security['crypto_zone']}")
        
        # Check permissions
        if "permissions" not in security:
            result["valid"] = False
            result["errors"].append("Missing permissions in security configuration")
        else:
            # Validate permissions against allowed permissions
            invalid_permissions = [
                p for p in security["permissions"] 
                if p not in self._get_valid_permissions(context)
            ]
            
            if invalid_permissions:
                result["valid"] = False
                result["errors"].append(f"Invalid permissions: {', '.join(invalid_permissions)}")
        
        return result
    
    def _validate_compliance(self, capsule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate capsule compliance configuration.
        
        Args:
            capsule: Capsule to validate
            context: Validation context
            
        Returns:
            Compliance validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if security section exists
        if "security" not in capsule or "compliance" not in capsule["security"]:
            result["valid"] = False
            result["errors"].append("Missing compliance configuration")
            return result
        
        compliance = capsule["security"]["compliance"]
        
        # Check compliance frameworks
        if "frameworks" not in compliance:
            result["valid"] = False
            result["errors"].append("Missing compliance frameworks")
        else:
            # Check if required frameworks are included
            required_frameworks = self._get_required_compliance_frameworks(context)
            missing_frameworks = [
                f for f in required_frameworks 
                if f not in compliance["frameworks"]
            ]
            
            if missing_frameworks:
                result["valid"] = False
                result["errors"].append(f"Missing required compliance frameworks: {', '.join(missing_frameworks)}")
        
        return result
    
    def _validate_resources(self, capsule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate capsule resource configuration.
        
        Args:
            capsule: Capsule to validate
            context: Validation context
            
        Returns:
            Resource validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if runtime section exists
        if "runtime" not in capsule or "resources" not in capsule["runtime"]:
            result["valid"] = False
            result["errors"].append("Missing resource configuration")
            return result
        
        resources = capsule["runtime"]["resources"]
        
        # Check required resource types
        required_resources = ["cpu", "memory"]
        missing_resources = [r for r in required_resources if r not in resources]
        
        if missing_resources:
            result["valid"] = False
            result["errors"].append(f"Missing required resources: {', '.join(missing_resources)}")
        
        # Check resource limits based on environment
        env_type = context.get("environment", {}).get("type", "default")
        
        if env_type == "edge":
            # Check if resources are within edge limits
            if "cpu" in resources and not self._is_within_edge_cpu_limit(resources["cpu"]):
                result["valid"] = False
                result["errors"].append(f"CPU resource exceeds edge limit: {resources['cpu']}")
            
            if "memory" in resources and not self._is_within_edge_memory_limit(resources["memory"]):
                result["valid"] = False
                result["errors"].append(f"Memory resource exceeds edge limit: {resources['memory']}")
        
        return result
    
    def _validate_dependencies(self, capsule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate capsule dependencies.
        
        Args:
            capsule: Capsule to validate
            context: Validation context
            
        Returns:
            Dependency validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if integration section exists
        if "integration" not in capsule or "dependencies" not in capsule["integration"]:
            return result  # No dependencies is valid
        
        dependencies = capsule["integration"]["dependencies"]
        
        # Check for circular dependencies
        # This would require knowledge of all capsules in the deployment
        # For now, just check for self-dependency
        for dep in dependencies:
            if dep.get("name") == capsule.get("name"):
                result["valid"] = False
                result["errors"].append(f"Circular dependency: capsule depends on itself")
        
        # Check for required fields in dependencies
        for i, dep in enumerate(dependencies):
            if "name" not in dep:
                result["valid"] = False
                result["errors"].append(f"Missing name in dependency at index {i}")
            
            if "version" not in dep:
                result["warnings"].append(f"Missing version in dependency {dep.get('name', f'at index {i}')}")
        
        return result
    
    def _validate_protocols(self, capsule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate capsule protocol configuration.
        
        Args:
            capsule: Capsule to validate
            context: Validation context
            
        Returns:
            Protocol validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if protocols section exists
        if "protocols" not in capsule:
            result["valid"] = False
            result["errors"].append("Missing protocols configuration")
            return result
        
        protocols = capsule["protocols"]
        
        # Check MCP configuration
        if "mcp" not in protocols:
            result["valid"] = False
            result["errors"].append("Missing MCP protocol configuration")
        else:
            mcp = protocols["mcp"]
            
            # Check if MCP is enabled
            if not mcp.get("enabled", True):
                result["warnings"].append("MCP protocol is disabled")
            
            # Check MCP version
            if "version" not in mcp:
                result["valid"] = False
                result["errors"].append("Missing MCP version")
            elif not self._is_valid_mcp_version(mcp["version"]):
                result["valid"] = False
                result["errors"].append(f"Invalid MCP version: {mcp['version']}")
        
        # Check A2A configuration
        if "a2a" not in protocols:
            result["valid"] = False
            result["errors"].append("Missing A2A protocol configuration")
        else:
            a2a = protocols["a2a"]
            
            # Check if A2A is enabled
            if not a2a.get("enabled", True):
                result["warnings"].append("A2A protocol is disabled")
            
            # Check A2A version
            if "version" not in a2a:
                result["valid"] = False
                result["errors"].append("Missing A2A version")
            elif not self._is_valid_a2a_version(a2a["version"]):
                result["valid"] = False
                result["errors"].append(f"Invalid A2A version: {a2a['version']}")
            
            # Check agent card
            if "agent_card" not in a2a:
                result["valid"] = False
                result["errors"].append("Missing A2A agent card")
            else:
                agent_card = a2a["agent_card"]
                
                # Check required agent card fields
                required_fields = ["name"]
                missing_fields = [f for f in required_fields if f not in agent_card]
                
                if missing_fields:
                    result["valid"] = False
                    result["errors"].append(f"Missing required agent card fields: {', '.join(missing_fields)}")
                
                # Check industry tags if industry is specified in context
                industry = context.get("industry")
                if industry and "industryTags" in agent_card:
                    if industry not in agent_card["industryTags"]:
                        result["warnings"].append(f"Industry {industry} not included in agent card industryTags")
        
        return result
    
    def _load_schemas(self):
        """
        Load JSON schemas from the schema directory.
        """
        if not os.path.exists(self.schema_path):
            logger.warning(f"Schema path does not exist: {self.schema_path}")
            return
        
        for filename in os.listdir(self.schema_path):
            if filename.endswith('.json'):
                schema_type = os.path.splitext(filename)[0]
                schema_path = os.path.join(self.schema_path, filename)
                
                try:
                    with open(schema_path, 'r') as f:
                        self.schemas[schema_type] = json.load(f)
                    logger.debug(f"Loaded schema: {schema_type}")
                except Exception as e:
                    logger.error(f"Error loading schema {schema_type}: {str(e)}")
    
    def _get_schema(self, capsule_type: str) -> Dict[str, Any]:
        """
        Get schema for a capsule type.
        
        Args:
            capsule_type: Type of capsule
            
        Returns:
            Schema for the capsule type, or None if not found
        """
        # Try to get exact match
        if capsule_type in self.schemas:
            return self.schemas[capsule_type]
        
        # Try to get generic schema
        if "generic" in self.schemas:
            return self.schemas["generic"]
        
        return None
    
    def _get_valid_trust_zones(self, context: Dict[str, Any]) -> List[str]:
        """
        Get valid trust zones for the given context.
        
        Args:
            context: Validation context
            
        Returns:
            List of valid trust zones
        """
        # This would typically come from a configuration or service
        # For now, return a default list
        return context.get("valid_trust_zones", ["default", "secure", "public", "private"])
    
    def _get_valid_crypto_zones(self, context: Dict[str, Any]) -> List[str]:
        """
        Get valid crypto zones for the given context.
        
        Args:
            context: Validation context
            
        Returns:
            List of valid crypto zones
        """
        # This would typically come from a configuration or service
        # For now, return a default list
        return context.get("valid_crypto_zones", ["default", "high", "medium", "low"])
    
    def _get_valid_permissions(self, context: Dict[str, Any]) -> List[str]:
        """
        Get valid permissions for the given context.
        
        Args:
            context: Validation context
            
        Returns:
            List of valid permissions
        """
        # This would typically come from a configuration or service
        # For now, return a default list
        return context.get("valid_permissions", [
            "read", "write", "execute", "network", "storage", "admin",
            "mcp:read", "mcp:write", "a2a:read", "a2a:write"
        ])
    
    def _get_required_compliance_frameworks(self, context: Dict[str, Any]) -> List[str]:
        """
        Get required compliance frameworks for the given context.
        
        Args:
            context: Validation context
            
        Returns:
            List of required compliance frameworks
        """
        # This would typically come from a configuration or service
        # For now, return a default list based on context
        industry = context.get("industry")
        
        if industry == "healthcare":
            return ["HIPAA"]
        elif industry == "finance":
            return ["PCI-DSS"]
        elif industry == "government":
            return ["FISMA"]
        
        return []
    
    def _is_within_edge_cpu_limit(self, cpu: str) -> bool:
        """
        Check if CPU resource is within edge limit.
        
        Args:
            cpu: CPU resource value
            
        Returns:
            True if within limit, False otherwise
        """
        try:
            if cpu.endswith('m'):
                value = int(cpu[:-1])
                return value <= 500  # 500m limit for edge
            else:
                value = float(cpu)
                return value <= 0.5  # 0.5 CPU limit for edge
        except (ValueError, AttributeError):
            return False
    
    def _is_within_edge_memory_limit(self, memory: str) -> bool:
        """
        Check if memory resource is within edge limit.
        
        Args:
            memory: Memory resource value
            
        Returns:
            True if within limit, False otherwise
        """
        try:
            if memory.endswith('Mi'):
                value = int(memory[:-2])
                return value <= 512  # 512Mi limit for edge
            elif memory.endswith('Gi'):
                value = float(memory[:-2])
                return value <= 0.5  # 0.5Gi limit for edge
            else:
                value = int(memory)
                return value <= 512 * 1024 * 1024  # 512Mi in bytes
        except (ValueError, AttributeError):
            return False
    
    def _is_valid_mcp_version(self, version: str) -> bool:
        """
        Check if MCP version is valid.
        
        Args:
            version: MCP version
            
        Returns:
            True if valid, False otherwise
        """
        # This would typically check against a list of supported versions
        # For now, accept any version-like string
        import re
        return bool(re.match(r'^\d+(\.\d+)*$', version))
    
    def _is_valid_a2a_version(self, version: str) -> bool:
        """
        Check if A2A version is valid.
        
        Args:
            version: A2A version
            
        Returns:
            True if valid, False otherwise
        """
        # This would typically check against a list of supported versions
        # For now, accept any version-like string
        import re
        return bool(re.match(r'^\d+(\.\d+)*$', version))
