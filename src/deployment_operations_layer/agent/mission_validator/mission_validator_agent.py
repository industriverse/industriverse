"""
Mission Validator Agent

This module is responsible for validating mission intent and ensuring proper alignment
between business outcomes and capsule stack configurations. It serves as a critical
safeguard against mission interpretation failures in the Deployment Operations Layer.

The Mission Validator Agent performs comprehensive validation of deployment missions,
ensuring that the capsule stack accurately reflects the intended business outcomes,
compliance requirements, and operational constraints.
"""

import logging
import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple, Set

from ...protocol.mcp_integration.mcp_context_schema import MCPContextSchema
from ...protocol.a2a_integration.a2a_agent_schema import A2AAgentSchema
from ..agent_utils import AgentBase

logger = logging.getLogger(__name__)

class MissionValidatorAgent(AgentBase):
    """
    Agent responsible for validating mission intent and ensuring proper alignment
    between business outcomes and capsule stack configurations.
    
    This agent serves as a critical safeguard against mission interpretation failures
    by validating that the capsule stack accurately reflects the intended business
    outcomes, compliance requirements, and operational constraints.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Mission Validator Agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        super().__init__(name="MissionValidatorAgent", config=config)
        
        # Initialize validation rules
        self.validation_rules = self.config.get("validation_rules", {})
        if not self.validation_rules:
            self._initialize_default_validation_rules()
        
        # Initialize validation history
        self.validation_history = []
        
        # MCP/A2A integration
        self.mcp_schema = MCPContextSchema()
        self.a2a_schema = A2AAgentSchema()
        
        logger.info("Mission Validator Agent initialized")
    
    def _initialize_default_validation_rules(self):
        """
        Initialize default validation rules.
        """
        self.validation_rules = {
            "mission_intent": {
                "required_fields": [
                    "mission_id",
                    "mission_name",
                    "mission_description",
                    "business_outcomes",
                    "target_environment",
                    "compliance_requirements"
                ],
                "outcome_mapping_required": True,
                "domain_validation_required": True
            },
            "capsule_stack": {
                "required_fields": [
                    "stack_id",
                    "capsules",
                    "dependencies",
                    "trust_requirements"
                ],
                "circular_dependency_check": True,
                "trust_validation_required": True
            },
            "environment": {
                "required_fields": [
                    "environment_id",
                    "environment_type",
                    "regions",
                    "capabilities"
                ],
                "capability_validation_required": True,
                "geo_compliance_check": True
            },
            "compliance": {
                "required_fields": [
                    "compliance_id",
                    "regulations",
                    "data_sovereignty",
                    "audit_requirements"
                ],
                "regulation_validation_required": True,
                "sovereignty_check": True
            }
        }
    
    def validate_mission(self, 
                        mission_intent: Dict[str, Any],
                        capsule_stack: Dict[str, Any],
                        environment: Dict[str, Any],
                        compliance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a deployment mission against the capsule stack, environment, and compliance requirements.
        
        Args:
            mission_intent: Mission intent dictionary
            capsule_stack: Capsule stack dictionary
            environment: Environment dictionary
            compliance: Compliance dictionary
            
        Returns:
            Validation results dictionary
        """
        validation_id = f"validation-{int(time.time())}-{hashlib.md5(json.dumps(mission_intent).encode()).hexdigest()[:8]}"
        
        logger.info(f"Starting mission validation: {validation_id}")
        
        # Initialize validation results
        validation_results = {
            "validation_id": validation_id,
            "timestamp": time.time(),
            "status": "pending",
            "mission_id": mission_intent.get("mission_id", "unknown"),
            "validations": {},
            "issues": [],
            "recommendations": []
        }
        
        # Validate mission intent
        intent_validation = self._validate_mission_intent(mission_intent)
        validation_results["validations"]["mission_intent"] = intent_validation
        validation_results["issues"].extend(intent_validation.get("issues", []))
        validation_results["recommendations"].extend(intent_validation.get("recommendations", []))
        
        # Validate capsule stack
        stack_validation = self._validate_capsule_stack(capsule_stack)
        validation_results["validations"]["capsule_stack"] = stack_validation
        validation_results["issues"].extend(stack_validation.get("issues", []))
        validation_results["recommendations"].extend(stack_validation.get("recommendations", []))
        
        # Validate environment
        env_validation = self._validate_environment(environment)
        validation_results["validations"]["environment"] = env_validation
        validation_results["issues"].extend(env_validation.get("issues", []))
        validation_results["recommendations"].extend(env_validation.get("recommendations", []))
        
        # Validate compliance
        compliance_validation = self._validate_compliance(compliance)
        validation_results["validations"]["compliance"] = compliance_validation
        validation_results["issues"].extend(compliance_validation.get("issues", []))
        validation_results["recommendations"].extend(compliance_validation.get("recommendations", []))
        
        # Validate cross-component alignment
        alignment_validation = self._validate_cross_component_alignment(
            mission_intent, capsule_stack, environment, compliance
        )
        validation_results["validations"]["alignment"] = alignment_validation
        validation_results["issues"].extend(alignment_validation.get("issues", []))
        validation_results["recommendations"].extend(alignment_validation.get("recommendations", []))
        
        # Determine overall validation status
        if any(issue.get("severity") == "critical" for issue in validation_results["issues"]):
            validation_results["status"] = "failed"
        elif any(issue.get("severity") == "high" for issue in validation_results["issues"]):
            validation_results["status"] = "warning"
        else:
            validation_results["status"] = "passed"
        
        # Add to validation history
        self.validation_history.append({
            "validation_id": validation_id,
            "timestamp": validation_results["timestamp"],
            "mission_id": validation_results["mission_id"],
            "status": validation_results["status"],
            "issue_count": len(validation_results["issues"])
        })
        
        logger.info(f"Mission validation completed: {validation_id} - Status: {validation_results['status']}")
        
        return validation_results
    
    def _validate_mission_intent(self, mission_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate mission intent.
        
        Args:
            mission_intent: Mission intent dictionary
            
        Returns:
            Validation results for mission intent
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check required fields
        required_fields = self.validation_rules["mission_intent"]["required_fields"]
        for field in required_fields:
            if field not in mission_intent or not mission_intent[field]:
                results["issues"].append({
                    "type": "missing_field",
                    "component": "mission_intent",
                    "field": field,
                    "severity": "high",
                    "message": f"Required field '{field}' is missing or empty in mission intent"
                })
        
        # Validate business outcomes
        if "business_outcomes" in mission_intent and isinstance(mission_intent["business_outcomes"], list):
            if len(mission_intent["business_outcomes"]) == 0:
                results["issues"].append({
                    "type": "empty_outcomes",
                    "component": "mission_intent",
                    "severity": "high",
                    "message": "Business outcomes list is empty"
                })
            
            # Check for vague or unmeasurable outcomes
            for i, outcome in enumerate(mission_intent["business_outcomes"]):
                if isinstance(outcome, str) and len(outcome.split()) < 3:
                    results["issues"].append({
                        "type": "vague_outcome",
                        "component": "mission_intent",
                        "index": i,
                        "severity": "medium",
                        "message": f"Business outcome '{outcome}' appears vague or too brief"
                    })
                    
                    results["recommendations"].append({
                        "type": "outcome_enhancement",
                        "component": "mission_intent",
                        "index": i,
                        "message": f"Consider expanding outcome '{outcome}' with measurable metrics and timeframes"
                    })
        
        # Validate domain specificity
        if self.validation_rules["mission_intent"]["domain_validation_required"]:
            if "industry_domain" not in mission_intent:
                results["issues"].append({
                    "type": "missing_domain",
                    "component": "mission_intent",
                    "severity": "medium",
                    "message": "Industry domain not specified in mission intent"
                })
                
                results["recommendations"].append({
                    "type": "add_domain",
                    "component": "mission_intent",
                    "message": "Add industry domain to enable domain-specific validations and optimizations"
                })
        
        # Determine status
        if any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "medium" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _validate_capsule_stack(self, capsule_stack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate capsule stack.
        
        Args:
            capsule_stack: Capsule stack dictionary
            
        Returns:
            Validation results for capsule stack
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check required fields
        required_fields = self.validation_rules["capsule_stack"]["required_fields"]
        for field in required_fields:
            if field not in capsule_stack or not capsule_stack[field]:
                results["issues"].append({
                    "type": "missing_field",
                    "component": "capsule_stack",
                    "field": field,
                    "severity": "high",
                    "message": f"Required field '{field}' is missing or empty in capsule stack"
                })
        
        # Validate capsules
        if "capsules" in capsule_stack and isinstance(capsule_stack["capsules"], list):
            if len(capsule_stack["capsules"]) == 0:
                results["issues"].append({
                    "type": "empty_capsules",
                    "component": "capsule_stack",
                    "severity": "critical",
                    "message": "Capsule list is empty"
                })
            
            # Check for required capsule fields
            for i, capsule in enumerate(capsule_stack["capsules"]):
                if not isinstance(capsule, dict):
                    results["issues"].append({
                        "type": "invalid_capsule",
                        "component": "capsule_stack",
                        "index": i,
                        "severity": "high",
                        "message": f"Capsule at index {i} is not a valid dictionary"
                    })
                    continue
                
                required_capsule_fields = ["id", "name", "version", "type", "capabilities"]
                for field in required_capsule_fields:
                    if field not in capsule or not capsule[field]:
                        results["issues"].append({
                            "type": "missing_capsule_field",
                            "component": "capsule_stack",
                            "capsule_index": i,
                            "field": field,
                            "severity": "high",
                            "message": f"Required field '{field}' is missing or empty in capsule at index {i}"
                        })
        
        # Check for circular dependencies
        if self.validation_rules["capsule_stack"]["circular_dependency_check"]:
            if "dependencies" in capsule_stack and isinstance(capsule_stack["dependencies"], dict):
                circular_deps = self._detect_circular_dependencies(capsule_stack["dependencies"])
                for dep_chain in circular_deps:
                    results["issues"].append({
                        "type": "circular_dependency",
                        "component": "capsule_stack",
                        "dependency_chain": dep_chain,
                        "severity": "critical",
                        "message": f"Circular dependency detected: {' -> '.join(dep_chain)}"
                    })
        
        # Validate trust requirements
        if self.validation_rules["capsule_stack"]["trust_validation_required"]:
            if "trust_requirements" in capsule_stack:
                trust_reqs = capsule_stack["trust_requirements"]
                
                # Check for missing trust fields
                required_trust_fields = ["minimum_trust_score", "trust_zones", "override_policy"]
                for field in required_trust_fields:
                    if field not in trust_reqs or not trust_reqs[field]:
                        results["issues"].append({
                            "type": "missing_trust_field",
                            "component": "capsule_stack",
                            "field": field,
                            "severity": "high",
                            "message": f"Required trust field '{field}' is missing or empty"
                        })
                
                # Validate minimum trust score
                if "minimum_trust_score" in trust_reqs:
                    try:
                        trust_score = float(trust_reqs["minimum_trust_score"])
                        if trust_score < 0 or trust_score > 1:
                            results["issues"].append({
                                "type": "invalid_trust_score",
                                "component": "capsule_stack",
                                "severity": "high",
                                "message": f"Minimum trust score must be between 0 and 1, got {trust_score}"
                            })
                    except (ValueError, TypeError):
                        results["issues"].append({
                            "type": "invalid_trust_score",
                            "component": "capsule_stack",
                            "severity": "high",
                            "message": f"Minimum trust score must be a number between 0 and 1"
                        })
        
        # Determine status
        if any(issue["severity"] == "critical" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _validate_environment(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate environment.
        
        Args:
            environment: Environment dictionary
            
        Returns:
            Validation results for environment
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check required fields
        required_fields = self.validation_rules["environment"]["required_fields"]
        for field in required_fields:
            if field not in environment or not environment[field]:
                results["issues"].append({
                    "type": "missing_field",
                    "component": "environment",
                    "field": field,
                    "severity": "high",
                    "message": f"Required field '{field}' is missing or empty in environment"
                })
        
        # Validate environment type
        if "environment_type" in environment:
            valid_env_types = ["cloud", "edge", "hybrid", "on-premise", "multi-cloud"]
            if environment["environment_type"] not in valid_env_types:
                results["issues"].append({
                    "type": "invalid_environment_type",
                    "component": "environment",
                    "severity": "medium",
                    "message": f"Environment type '{environment['environment_type']}' is not one of {valid_env_types}"
                })
        
        # Validate regions
        if "regions" in environment and isinstance(environment["regions"], list):
            if len(environment["regions"]) == 0:
                results["issues"].append({
                    "type": "empty_regions",
                    "component": "environment",
                    "severity": "medium",
                    "message": "Regions list is empty"
                })
            
            # Check for region details
            for i, region in enumerate(environment["regions"]):
                if not isinstance(region, dict):
                    results["issues"].append({
                        "type": "invalid_region",
                        "component": "environment",
                        "index": i,
                        "severity": "medium",
                        "message": f"Region at index {i} is not a valid dictionary"
                    })
                    continue
                
                required_region_fields = ["id", "name", "provider", "location"]
                for field in required_region_fields:
                    if field not in region or not region[field]:
                        results["issues"].append({
                            "type": "missing_region_field",
                            "component": "environment",
                            "region_index": i,
                            "field": field,
                            "severity": "medium",
                            "message": f"Required field '{field}' is missing or empty in region at index {i}"
                        })
        
        # Validate capabilities
        if "capabilities" in environment and isinstance(environment["capabilities"], dict):
            required_capability_sections = ["compute", "storage", "network", "security"]
            for section in required_capability_sections:
                if section not in environment["capabilities"] or not environment["capabilities"][section]:
                    results["issues"].append({
                        "type": "missing_capability_section",
                        "component": "environment",
                        "section": section,
                        "severity": "medium",
                        "message": f"Required capability section '{section}' is missing or empty"
                    })
        
        # Validate geo-compliance
        if self.validation_rules["environment"]["geo_compliance_check"]:
            if "regions" in environment and isinstance(environment["regions"], list):
                for i, region in enumerate(environment["regions"]):
                    if isinstance(region, dict) and "location" in region:
                        # Check for restricted locations
                        restricted_locations = ["restricted-zone-1", "restricted-zone-2"]
                        if region["location"] in restricted_locations:
                            results["issues"].append({
                                "type": "restricted_location",
                                "component": "environment",
                                "region_index": i,
                                "location": region["location"],
                                "severity": "high",
                                "message": f"Region '{region.get('name', 'unknown')}' is in a restricted location: {region['location']}"
                            })
        
        # Determine status
        if any(issue["severity"] == "critical" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _validate_compliance(self, compliance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate compliance.
        
        Args:
            compliance: Compliance dictionary
            
        Returns:
            Validation results for compliance
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Check required fields
        required_fields = self.validation_rules["compliance"]["required_fields"]
        for field in required_fields:
            if field not in compliance or not compliance[field]:
                results["issues"].append({
                    "type": "missing_field",
                    "component": "compliance",
                    "field": field,
                    "severity": "high",
                    "message": f"Required field '{field}' is missing or empty in compliance"
                })
        
        # Validate regulations
        if "regulations" in compliance and isinstance(compliance["regulations"], list):
            if len(compliance["regulations"]) == 0:
                results["recommendations"].append({
                    "type": "empty_regulations",
                    "component": "compliance",
                    "message": "No regulations specified. Confirm if this is intentional."
                })
            
            # Check for regulation details
            for i, regulation in enumerate(compliance["regulations"]):
                if not isinstance(regulation, dict):
                    results["issues"].append({
                        "type": "invalid_regulation",
                        "component": "compliance",
                        "index": i,
                        "severity": "medium",
                        "message": f"Regulation at index {i} is not a valid dictionary"
                    })
                    continue
                
                required_regulation_fields = ["id", "name", "description", "requirements"]
                for field in required_regulation_fields:
                    if field not in regulation or not regulation[field]:
                        results["issues"].append({
                            "type": "missing_regulation_field",
                            "component": "compliance",
                            "regulation_index": i,
                            "field": field,
                            "severity": "medium",
                            "message": f"Required field '{field}' is missing or empty in regulation at index {i}"
                        })
        
        # Validate data sovereignty
        if "data_sovereignty" in compliance and isinstance(compliance["data_sovereignty"], dict):
            required_sovereignty_fields = ["requirements", "restricted_regions", "data_classification"]
            for field in required_sovereignty_fields:
                if field not in compliance["data_sovereignty"] or not compliance["data_sovereignty"][field]:
                    results["issues"].append({
                        "type": "missing_sovereignty_field",
                        "component": "compliance",
                        "field": field,
                        "severity": "high",
                        "message": f"Required field '{field}' is missing or empty in data sovereignty"
                    })
        
        # Validate audit requirements
        if "audit_requirements" in compliance and isinstance(compliance["audit_requirements"], dict):
            required_audit_fields = ["audit_frequency", "audit_type", "retention_period"]
            for field in required_audit_fields:
                if field not in compliance["audit_requirements"] or not compliance["audit_requirements"][field]:
                    results["issues"].append({
                        "type": "missing_audit_field",
                        "component": "compliance",
                        "field": field,
                        "severity": "medium",
                        "message": f"Required field '{field}' is missing or empty in audit requirements"
                    })
        
        # Determine status
        if any(issue["severity"] == "critical" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _validate_cross_component_alignment(self,
                                          mission_intent: Dict[str, Any],
                                          capsule_stack: Dict[str, Any],
                                          environment: Dict[str, Any],
                                          compliance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate alignment between mission intent, capsule stack, environment, and compliance.
        
        Args:
            mission_intent: Mission intent dictionary
            capsule_stack: Capsule stack dictionary
            environment: Environment dictionary
            compliance: Compliance dictionary
            
        Returns:
            Validation results for cross-component alignment
        """
        results = {
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Validate business outcome to capsule alignment
        if "business_outcomes" in mission_intent and isinstance(mission_intent["business_outcomes"], list) and \
           "capsules" in capsule_stack and isinstance(capsule_stack["capsules"], list):
            
            # Check if each business outcome is addressed by at least one capsule
            for i, outcome in enumerate(mission_intent["business_outcomes"]):
                outcome_addressed = False
                
                # Simple check: look for outcome keywords in capsule capabilities
                outcome_keywords = self._extract_keywords(outcome)
                
                for capsule in capsule_stack["capsules"]:
                    if not isinstance(capsule, dict) or "capabilities" not in capsule:
                        continue
                    
                    capabilities_text = json.dumps(capsule["capabilities"]).lower()
                    
                    # Check if any keyword is in capabilities
                    if any(keyword in capabilities_text for keyword in outcome_keywords):
                        outcome_addressed = True
                        break
                
                if not outcome_addressed:
                    results["issues"].append({
                        "type": "unaddressed_outcome",
                        "component": "alignment",
                        "outcome_index": i,
                        "severity": "high",
                        "message": f"Business outcome '{outcome}' does not appear to be addressed by any capsule"
                    })
                    
                    results["recommendations"].append({
                        "type": "add_capsule",
                        "component": "alignment",
                        "message": f"Consider adding a capsule to address business outcome: '{outcome}'"
                    })
        
        # Validate environment to capsule requirements alignment
        if "capsules" in capsule_stack and isinstance(capsule_stack["capsules"], list) and \
           "capabilities" in environment and isinstance(environment["capabilities"], dict):
            
            for i, capsule in enumerate(capsule_stack["capsules"]):
                if not isinstance(capsule, dict) or "requirements" not in capsule:
                    continue
                
                # Check if capsule requirements are met by environment capabilities
                if "compute" in capsule["requirements"] and "compute" in environment["capabilities"]:
                    capsule_compute = capsule["requirements"]["compute"]
                    env_compute = environment["capabilities"]["compute"]
                    
                    # Check CPU requirements
                    if "cpu" in capsule_compute and "cpu" in env_compute:
                        if capsule_compute["cpu"] > env_compute["cpu"]:
                            results["issues"].append({
                                "type": "insufficient_resource",
                                "component": "alignment",
                                "capsule_index": i,
                                "resource": "cpu",
                                "required": capsule_compute["cpu"],
                                "available": env_compute["cpu"],
                                "severity": "high",
                                "message": f"Capsule '{capsule.get('name', 'unknown')}' requires {capsule_compute['cpu']} CPU units, but environment only provides {env_compute['cpu']}"
                            })
                    
                    # Check memory requirements
                    if "memory" in capsule_compute and "memory" in env_compute:
                        if capsule_compute["memory"] > env_compute["memory"]:
                            results["issues"].append({
                                "type": "insufficient_resource",
                                "component": "alignment",
                                "capsule_index": i,
                                "resource": "memory",
                                "required": capsule_compute["memory"],
                                "available": env_compute["memory"],
                                "severity": "high",
                                "message": f"Capsule '{capsule.get('name', 'unknown')}' requires {capsule_compute['memory']} memory units, but environment only provides {env_compute['memory']}"
                            })
        
        # Validate compliance to environment alignment
        if "data_sovereignty" in compliance and isinstance(compliance["data_sovereignty"], dict) and \
           "regions" in environment and isinstance(environment["regions"], list):
            
            # Check if any region is in the restricted list
            if "restricted_regions" in compliance["data_sovereignty"]:
                restricted_regions = compliance["data_sovereignty"]["restricted_regions"]
                
                for i, region in enumerate(environment["regions"]):
                    if not isinstance(region, dict) or "name" not in region:
                        continue
                    
                    if region["name"] in restricted_regions:
                        results["issues"].append({
                            "type": "restricted_region",
                            "component": "alignment",
                            "region_index": i,
                            "region": region["name"],
                            "severity": "critical",
                            "message": f"Region '{region['name']}' is in the restricted regions list for data sovereignty"
                        })
        
        # Determine status
        if any(issue["severity"] == "critical" for issue in results["issues"]):
            results["status"] = "failed"
        elif any(issue["severity"] == "high" for issue in results["issues"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _detect_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """
        Detect circular dependencies in the dependency graph.
        
        Args:
            dependencies: Dictionary mapping capsule IDs to lists of dependency IDs
            
        Returns:
            List of circular dependency chains
        """
        circular_deps = []
        visited = set()
        path = []
        
        def dfs(node):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                circular_deps.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for dep in dependencies.get(node, []):
                dfs(dep)
            
            path.pop()
        
        # Run DFS from each node
        for node in dependencies:
            if node not in visited:
                dfs(node)
        
        return circular_deps
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction: lowercase words with at least 4 characters
        if not isinstance(text, str):
            return []
        
        words = text.lower().split()
        keywords = [word for word in words if len(word) >= 4]
        
        return keywords
    
    def run_pre_deployment_simulation(self, 
                                    mission_intent: Dict[str, Any],
                                    capsule_stack: Dict[str, Any],
                                    environment: Dict[str, Any],
                                    compliance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a pre-deployment simulation to validate mission goals against the capsule stack.
        
        Args:
            mission_intent: Mission intent dictionary
            capsule_stack: Capsule stack dictionary
            environment: Environment dictionary
            compliance: Compliance dictionary
            
        Returns:
            Simulation results dictionary
        """
        simulation_id = f"sim-{int(time.time())}-{hashlib.md5(json.dumps(mission_intent).encode()).hexdigest()[:8]}"
        
        logger.info(f"Starting pre-deployment simulation: {simulation_id}")
        
        # Initialize simulation results
        simulation_results = {
            "simulation_id": simulation_id,
            "timestamp": time.time(),
            "status": "pending",
            "mission_id": mission_intent.get("mission_id", "unknown"),
            "scenarios": [],
            "issues": [],
            "recommendations": []
        }
        
        # Define simulation scenarios
        scenarios = [
            {
                "name": "normal_operation",
                "description": "Normal operation with all systems functioning correctly",
                "conditions": {}
            },
            {
                "name": "partial_failure",
                "description": "Partial system failure with some capsules unavailable",
                "conditions": {
                    "failed_capsules": ["random", 0.2]  # Random 20% of capsules fail
                }
            },
            {
                "name": "network_partition",
                "description": "Network partition between regions",
                "conditions": {
                    "network_partition": True
                }
            },
            {
                "name": "high_load",
                "description": "High load on the system",
                "conditions": {
                    "load_factor": 2.0  # 2x normal load
                }
            },
            {
                "name": "compliance_audit",
                "description": "Compliance audit scenario",
                "conditions": {
                    "audit_mode": True
                }
            }
        ]
        
        # Run each scenario
        for scenario in scenarios:
            scenario_result = self._run_simulation_scenario(
                scenario, mission_intent, capsule_stack, environment, compliance
            )
            
            simulation_results["scenarios"].append(scenario_result)
            simulation_results["issues"].extend(scenario_result.get("issues", []))
            simulation_results["recommendations"].extend(scenario_result.get("recommendations", []))
        
        # Determine overall simulation status
        if any(scenario["status"] == "failed" for scenario in simulation_results["scenarios"]):
            simulation_results["status"] = "failed"
        elif any(scenario["status"] == "warning" for scenario in simulation_results["scenarios"]):
            simulation_results["status"] = "warning"
        else:
            simulation_results["status"] = "passed"
        
        logger.info(f"Pre-deployment simulation completed: {simulation_id} - Status: {simulation_results['status']}")
        
        return simulation_results
    
    def _run_simulation_scenario(self,
                               scenario: Dict[str, Any],
                               mission_intent: Dict[str, Any],
                               capsule_stack: Dict[str, Any],
                               environment: Dict[str, Any],
                               compliance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a simulation scenario.
        
        Args:
            scenario: Scenario dictionary
            mission_intent: Mission intent dictionary
            capsule_stack: Capsule stack dictionary
            environment: Environment dictionary
            compliance: Compliance dictionary
            
        Returns:
            Scenario results dictionary
        """
        scenario_name = scenario["name"]
        scenario_description = scenario["description"]
        conditions = scenario["conditions"]
        
        logger.info(f"Running simulation scenario: {scenario_name}")
        
        # Initialize scenario results
        scenario_results = {
            "name": scenario_name,
            "description": scenario_description,
            "status": "pending",
            "issues": [],
            "recommendations": []
        }
        
        # Apply scenario conditions
        modified_capsule_stack = self._apply_scenario_conditions_to_capsule_stack(
            capsule_stack, conditions
        )
        
        modified_environment = self._apply_scenario_conditions_to_environment(
            environment, conditions
        )
        
        # Validate modified configuration
        validation_results = self.validate_mission(
            mission_intent, modified_capsule_stack, modified_environment, compliance
        )
        
        # Check business outcomes achievement
        outcome_results = self._check_business_outcomes_achievement(
            mission_intent, modified_capsule_stack, modified_environment, conditions
        )
        
        # Combine results
        scenario_results["validation"] = validation_results
        scenario_results["outcome_achievement"] = outcome_results
        
        # Add issues and recommendations
        scenario_results["issues"].extend(validation_results.get("issues", []))
        scenario_results["issues"].extend(outcome_results.get("issues", []))
        
        scenario_results["recommendations"].extend(validation_results.get("recommendations", []))
        scenario_results["recommendations"].extend(outcome_results.get("recommendations", []))
        
        # Determine scenario status
        if any(issue.get("severity") == "critical" for issue in scenario_results["issues"]):
            scenario_results["status"] = "failed"
        elif any(issue.get("severity") == "high" for issue in scenario_results["issues"]):
            scenario_results["status"] = "warning"
        else:
            scenario_results["status"] = "passed"
        
        logger.info(f"Simulation scenario completed: {scenario_name} - Status: {scenario_results['status']}")
        
        return scenario_results
    
    def _apply_scenario_conditions_to_capsule_stack(self,
                                                 capsule_stack: Dict[str, Any],
                                                 conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply scenario conditions to the capsule stack.
        
        Args:
            capsule_stack: Capsule stack dictionary
            conditions: Scenario conditions
            
        Returns:
            Modified capsule stack dictionary
        """
        # Create a deep copy to avoid modifying the original
        modified_stack = json.loads(json.dumps(capsule_stack))
        
        # Apply failed capsules condition
        if "failed_capsules" in conditions:
            failed_capsules_spec = conditions["failed_capsules"]
            
            if failed_capsules_spec[0] == "random" and len(failed_capsules_spec) > 1:
                # Random failure of capsules
                failure_rate = float(failed_capsules_spec[1])
                
                if "capsules" in modified_stack and isinstance(modified_stack["capsules"], list):
                    for i, capsule in enumerate(modified_stack["capsules"]):
                        if random.random() < failure_rate:
                            # Mark capsule as failed
                            if isinstance(capsule, dict):
                                capsule["status"] = "failed"
                                capsule["available"] = False
            
            elif isinstance(failed_capsules_spec, list) and all(isinstance(item, str) for item in failed_capsules_spec):
                # Specific capsules to fail
                if "capsules" in modified_stack and isinstance(modified_stack["capsules"], list):
                    for i, capsule in enumerate(modified_stack["capsules"]):
                        if isinstance(capsule, dict) and "id" in capsule and capsule["id"] in failed_capsules_spec:
                            # Mark capsule as failed
                            capsule["status"] = "failed"
                            capsule["available"] = False
        
        # Apply high load condition
        if "load_factor" in conditions:
            load_factor = float(conditions["load_factor"])
            
            if "capsules" in modified_stack and isinstance(modified_stack["capsules"], list):
                for i, capsule in enumerate(modified_stack["capsules"]):
                    if isinstance(capsule, dict) and "resources" in capsule:
                        # Increase resource usage
                        if "current_usage" in capsule["resources"]:
                            for resource, usage in capsule["resources"]["current_usage"].items():
                                if isinstance(usage, (int, float)):
                                    capsule["resources"]["current_usage"][resource] = usage * load_factor
        
        return modified_stack
    
    def _apply_scenario_conditions_to_environment(self,
                                               environment: Dict[str, Any],
                                               conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply scenario conditions to the environment.
        
        Args:
            environment: Environment dictionary
            conditions: Scenario conditions
            
        Returns:
            Modified environment dictionary
        """
        # Create a deep copy to avoid modifying the original
        modified_env = json.loads(json.dumps(environment))
        
        # Apply network partition condition
        if "network_partition" in conditions and conditions["network_partition"]:
            if "regions" in modified_env and isinstance(modified_env["regions"], list) and len(modified_env["regions"]) > 1:
                # Simulate network partition between first and other regions
                if len(modified_env["regions"]) > 0 and isinstance(modified_env["regions"][0], dict):
                    modified_env["regions"][0]["partitioned"] = True
        
        # Apply high load condition
        if "load_factor" in conditions:
            load_factor = float(conditions["load_factor"])
            
            if "capabilities" in modified_env and "compute" in modified_env["capabilities"]:
                # Decrease available compute resources
                compute = modified_env["capabilities"]["compute"]
                
                for resource, value in compute.items():
                    if isinstance(value, (int, float)):
                        compute[resource] = value / load_factor
        
        return modified_env
    
    def _check_business_outcomes_achievement(self,
                                          mission_intent: Dict[str, Any],
                                          capsule_stack: Dict[str, Any],
                                          environment: Dict[str, Any],
                                          conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if business outcomes can be achieved under the given conditions.
        
        Args:
            mission_intent: Mission intent dictionary
            capsule_stack: Capsule stack dictionary
            environment: Environment dictionary
            conditions: Scenario conditions
            
        Returns:
            Outcome achievement results dictionary
        """
        results = {
            "status": "pending",
            "outcomes": [],
            "issues": [],
            "recommendations": []
        }
        
        # Check each business outcome
        if "business_outcomes" in mission_intent and isinstance(mission_intent["business_outcomes"], list):
            for i, outcome in enumerate(mission_intent["business_outcomes"]):
                outcome_result = {
                    "outcome": outcome,
                    "achievable": True,
                    "confidence": 1.0,
                    "dependencies": []
                }
                
                # Check if required capsules are available
                required_capsules = self._identify_capsules_for_outcome(outcome, capsule_stack)
                
                for capsule_id in required_capsules:
                    capsule_available = False
                    
                    if "capsules" in capsule_stack and isinstance(capsule_stack["capsules"], list):
                        for capsule in capsule_stack["capsules"]:
                            if isinstance(capsule, dict) and "id" in capsule and capsule["id"] == capsule_id:
                                if capsule.get("status") != "failed" and capsule.get("available", True):
                                    capsule_available = True
                                    outcome_result["dependencies"].append({
                                        "capsule_id": capsule_id,
                                        "available": True
                                    })
                                else:
                                    outcome_result["dependencies"].append({
                                        "capsule_id": capsule_id,
                                        "available": False
                                    })
                    
                    if not capsule_available:
                        outcome_result["achievable"] = False
                        outcome_result["confidence"] *= 0.5
                        
                        results["issues"].append({
                            "type": "unavailable_dependency",
                            "component": "outcome_achievement",
                            "outcome_index": i,
                            "capsule_id": capsule_id,
                            "severity": "high",
                            "message": f"Required capsule '{capsule_id}' for outcome '{outcome}' is unavailable"
                        })
                
                # Check environment conditions
                if "network_partition" in conditions and conditions["network_partition"]:
                    # Network partition affects distributed outcomes
                    outcome_result["confidence"] *= 0.7
                    
                    results["issues"].append({
                        "type": "network_partition",
                        "component": "outcome_achievement",
                        "outcome_index": i,
                        "severity": "medium",
                        "message": f"Network partition may affect achievement of outcome '{outcome}'"
                    })
                
                if "load_factor" in conditions and conditions["load_factor"] > 1.5:
                    # High load affects performance-sensitive outcomes
                    outcome_result["confidence"] *= 0.8
                    
                    results["issues"].append({
                        "type": "high_load",
                        "component": "outcome_achievement",
                        "outcome_index": i,
                        "severity": "medium",
                        "message": f"High load may affect achievement of outcome '{outcome}'"
                    })
                
                # Add outcome result
                results["outcomes"].append(outcome_result)
                
                # Add recommendations for unachievable outcomes
                if not outcome_result["achievable"]:
                    results["recommendations"].append({
                        "type": "fallback_strategy",
                        "component": "outcome_achievement",
                        "outcome_index": i,
                        "message": f"Implement fallback strategy for outcome '{outcome}' to handle dependency failures"
                    })
        
        # Determine overall status
        if any(not outcome["achievable"] for outcome in results["outcomes"]):
            results["status"] = "failed"
        elif any(outcome["confidence"] < 0.7 for outcome in results["outcomes"]):
            results["status"] = "warning"
        else:
            results["status"] = "passed"
        
        return results
    
    def _identify_capsules_for_outcome(self, outcome: str, capsule_stack: Dict[str, Any]) -> List[str]:
        """
        Identify capsules required for a business outcome.
        
        Args:
            outcome: Business outcome
            capsule_stack: Capsule stack dictionary
            
        Returns:
            List of capsule IDs required for the outcome
        """
        required_capsules = []
        
        # Extract keywords from outcome
        outcome_keywords = self._extract_keywords(outcome)
        
        # Find capsules with matching capabilities
        if "capsules" in capsule_stack and isinstance(capsule_stack["capsules"], list):
            for capsule in capsule_stack["capsules"]:
                if not isinstance(capsule, dict) or "id" not in capsule or "capabilities" not in capsule:
                    continue
                
                capabilities_text = json.dumps(capsule["capabilities"]).lower()
                
                # Check if any keyword is in capabilities
                if any(keyword in capabilities_text for keyword in outcome_keywords):
                    required_capsules.append(capsule["id"])
        
        return required_capsules
    
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """
        Get validation history.
        
        Returns:
            List of validation history entries
        """
        return self.validation_history
    
    def get_validation_result(self, validation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific validation result by ID.
        
        Args:
            validation_id: Validation ID
            
        Returns:
            Validation result dictionary or None if not found
        """
        # This would typically retrieve from a database or cache
        # For simplicity, we'll just return a placeholder
        return {
            "validation_id": validation_id,
            "timestamp": time.time(),
            "status": "passed",
            "mission_id": "example-mission",
            "validations": {},
            "issues": [],
            "recommendations": []
        }
    
    def generate_validation_report(self, validation_id: str) -> Dict[str, Any]:
        """
        Generate a detailed validation report.
        
        Args:
            validation_id: Validation ID
            
        Returns:
            Validation report dictionary
        """
        validation_result = self.get_validation_result(validation_id)
        
        if not validation_result:
            return {
                "status": "error",
                "message": f"Validation result not found for ID: {validation_id}"
            }
        
        # Generate report
        report = {
            "report_id": f"report-{validation_id}",
            "timestamp": time.time(),
            "validation_id": validation_id,
            "mission_id": validation_result.get("mission_id", "unknown"),
            "status": validation_result.get("status", "unknown"),
            "summary": self._generate_validation_summary(validation_result),
            "details": validation_result,
            "recommendations": validation_result.get("recommendations", [])
        }
        
        return report
    
    def _generate_validation_summary(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of validation results.
        
        Args:
            validation_result: Validation result dictionary
            
        Returns:
            Validation summary dictionary
        """
        issues = validation_result.get("issues", [])
        
        # Count issues by severity
        issue_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for issue in issues:
            severity = issue.get("severity", "low")
            issue_counts[severity] = issue_counts.get(severity, 0) + 1
        
        # Count issues by component
        component_counts = {}
        
        for issue in issues:
            component = issue.get("component", "unknown")
            component_counts[component] = component_counts.get(component, 0) + 1
        
        # Generate summary
        summary = {
            "status": validation_result.get("status", "unknown"),
            "issue_counts": issue_counts,
            "component_counts": component_counts,
            "total_issues": len(issues),
            "total_recommendations": len(validation_result.get("recommendations", [])),
            "pass_rate": self._calculate_pass_rate(validation_result)
        }
        
        return summary
    
    def _calculate_pass_rate(self, validation_result: Dict[str, Any]) -> float:
        """
        Calculate the pass rate for a validation result.
        
        Args:
            validation_result: Validation result dictionary
            
        Returns:
            Pass rate as a percentage
        """
        validations = validation_result.get("validations", {})
        
        if not validations:
            return 0.0
        
        passed = 0
        total = 0
        
        for component, result in validations.items():
            total += 1
            if result.get("status") == "passed":
                passed += 1
        
        return (passed / total * 100) if total > 0 else 0.0
