"""
Compliance Validator

This module is responsible for validating deployment compliance against security and regulatory requirements.
It checks deployments against policy sets to ensure they meet all necessary compliance standards
before going live.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class ComplianceValidator:
    """
    Validates deployment compliance against security and regulatory requirements.
    
    This class checks deployments against policy sets to ensure they meet all necessary
    compliance standards before going live. It performs detailed validation of various
    compliance aspects including security, data protection, and regulatory requirements.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Compliance Validator.
        
        Args:
            config: Configuration dictionary for the validator
        """
        self.config = config or {}
        
        # Validation settings
        self.validation_timeout = self.config.get("validation_timeout", 300)  # 5 minutes
        self.strict_mode = self.config.get("strict_mode", True)
        
        logger.info("Compliance Validator initialized")
    
    def validate_compliance(self,
                           deployment_manifest: Dict[str, Any],
                           environment_config: Dict[str, Any],
                           policy_set: Dict[str, Any],
                           evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate deployment compliance against a policy set.
        
        Args:
            deployment_manifest: The deployment manifest to validate
            environment_config: Configuration of the target environment
            policy_set: Policy set to validate against
            evidence: Evidence collected for validation
            
        Returns:
            Dictionary containing validation results
        """
        logger.info(f"Validating compliance for deployment {deployment_manifest.get('id', 'unknown')}")
        
        start_time = time.time()
        
        # Initialize results
        results = {
            "compliant": False,
            "timestamp": time.time(),
            "validation_time": 0,
            "policy_set_id": policy_set.get("id", "unknown"),
            "policy_set_version": policy_set.get("version", "unknown"),
            "policy_results": [],
            "violations": [],
            "warnings": [],
            "summary": {}
        }
        
        try:
            # Get policies from policy set
            policies = policy_set.get("policies", [])
            
            if not policies:
                logger.warning(f"Policy set {policy_set.get('id', 'unknown')} has no policies")
                results["warnings"].append({
                    "code": "empty_policy_set",
                    "message": f"Policy set {policy_set.get('id', 'unknown')} has no policies"
                })
                results["compliant"] = True  # Empty policy set means compliant by default
                return self._finalize_results(results, start_time)
            
            # Validate each policy
            for policy in policies:
                policy_result = self._validate_policy(
                    policy,
                    deployment_manifest,
                    environment_config,
                    evidence
                )
                
                results["policy_results"].append(policy_result)
                
                # Add violations
                if not policy_result["compliant"]:
                    for violation in policy_result["violations"]:
                        results["violations"].append({
                            "policy_id": policy.get("id", "unknown"),
                            "policy_name": policy.get("name", "unknown"),
                            "severity": policy.get("severity", "medium"),
                            **violation
                        })
            
            # Determine overall compliance
            if self.strict_mode:
                # In strict mode, all policies must be compliant
                results["compliant"] = all(r["compliant"] for r in results["policy_results"])
            else:
                # In non-strict mode, only high severity policies must be compliant
                high_severity_results = [
                    r for r in results["policy_results"]
                    if r.get("policy_severity", "medium") == "high"
                ]
                
                if high_severity_results:
                    results["compliant"] = all(r["compliant"] for r in high_severity_results)
                else:
                    # If no high severity policies, at least 80% must be compliant
                    compliance_rate = sum(1 for r in results["policy_results"] if r["compliant"]) / len(results["policy_results"])
                    results["compliant"] = compliance_rate >= 0.8
            
            # Generate summary
            results["summary"] = self._generate_summary(results["policy_results"])
            
        except Exception as e:
            logger.exception(f"Error validating compliance: {e}")
            results["compliant"] = False
            results["violations"].append({
                "code": "validation_error",
                "message": f"Error validating compliance: {str(e)}",
                "severity": "high",
                "component": "validator"
            })
        
        return self._finalize_results(results, start_time)
    
    def _validate_policy(self,
                        policy: Dict[str, Any],
                        deployment_manifest: Dict[str, Any],
                        environment_config: Dict[str, Any],
                        evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single policy.
        
        Args:
            policy: Policy to validate
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            evidence: Evidence collected for validation
            
        Returns:
            Dictionary containing policy validation results
        """
        policy_id = policy.get("id", "unknown")
        policy_name = policy.get("name", "unknown")
        policy_type = policy.get("type", "unknown")
        policy_severity = policy.get("severity", "medium")
        
        logger.info(f"Validating policy {policy_id}: {policy_name}")
        
        # Initialize result
        result = {
            "policy_id": policy_id,
            "policy_name": policy_name,
            "policy_type": policy_type,
            "policy_severity": policy_severity,
            "compliant": False,
            "violations": [],
            "details": {}
        }
        
        # Validate based on policy type
        if policy_type == "security":
            self._validate_security_policy(policy, deployment_manifest, environment_config, evidence, result)
        elif policy_type == "data_protection":
            self._validate_data_protection_policy(policy, deployment_manifest, environment_config, evidence, result)
        elif policy_type == "regulatory":
            self._validate_regulatory_policy(policy, deployment_manifest, environment_config, evidence, result)
        elif policy_type == "operational":
            self._validate_operational_policy(policy, deployment_manifest, environment_config, evidence, result)
        else:
            logger.warning(f"Unknown policy type: {policy_type}")
            result["violations"].append({
                "code": "unknown_policy_type",
                "message": f"Unknown policy type: {policy_type}",
                "component": "validator"
            })
        
        # Determine compliance
        result["compliant"] = len(result["violations"]) == 0
        
        return result
    
    def _validate_security_policy(self,
                                 policy: Dict[str, Any],
                                 deployment_manifest: Dict[str, Any],
                                 environment_config: Dict[str, Any],
                                 evidence: Dict[str, Any],
                                 result: Dict[str, Any]):
        """
        Validate a security policy.
        
        Args:
            policy: Security policy to validate
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            evidence: Evidence collected for validation
            result: Result dictionary to update
        """
        rules = policy.get("rules", [])
        
        # Security-specific validations
        security_evidence = evidence.get("security", {})
        
        # Check for required security controls
        required_controls = policy.get("required_controls", [])
        implemented_controls = security_evidence.get("implemented_controls", [])
        
        missing_controls = [c for c in required_controls if c not in implemented_controls]
        if missing_controls:
            result["violations"].append({
                "code": "missing_security_controls",
                "message": f"Missing required security controls: {', '.join(missing_controls)}",
                "missing_controls": missing_controls
            })
        
        # Check for secure communication
        if policy.get("require_secure_communication", False):
            if not security_evidence.get("secure_communication", False):
                result["violations"].append({
                    "code": "insecure_communication",
                    "message": "Deployment does not use secure communication channels"
                })
        
        # Check for authentication
        if policy.get("require_authentication", False):
            if not security_evidence.get("authentication_enabled", False):
                result["violations"].append({
                    "code": "missing_authentication",
                    "message": "Deployment does not have authentication enabled"
                })
        
        # Check for authorization
        if policy.get("require_authorization", False):
            if not security_evidence.get("authorization_enabled", False):
                result["violations"].append({
                    "code": "missing_authorization",
                    "message": "Deployment does not have authorization enabled"
                })
        
        # Check for vulnerability scan results
        if policy.get("require_vulnerability_scan", False):
            if not security_evidence.get("vulnerability_scan_completed", False):
                result["violations"].append({
                    "code": "missing_vulnerability_scan",
                    "message": "Deployment has not undergone vulnerability scanning"
                })
            elif security_evidence.get("high_vulnerabilities", 0) > 0:
                result["violations"].append({
                    "code": "high_vulnerabilities",
                    "message": f"Deployment has {security_evidence.get('high_vulnerabilities', 0)} high severity vulnerabilities"
                })
        
        # Validate each rule
        for rule in rules:
            self._validate_rule(rule, deployment_manifest, environment_config, evidence, result)
        
        # Add security-specific details
        result["details"]["security"] = {
            "implemented_controls": implemented_controls,
            "missing_controls": missing_controls,
            "secure_communication": security_evidence.get("secure_communication", False),
            "authentication_enabled": security_evidence.get("authentication_enabled", False),
            "authorization_enabled": security_evidence.get("authorization_enabled", False),
            "vulnerability_scan_completed": security_evidence.get("vulnerability_scan_completed", False),
            "vulnerabilities": {
                "high": security_evidence.get("high_vulnerabilities", 0),
                "medium": security_evidence.get("medium_vulnerabilities", 0),
                "low": security_evidence.get("low_vulnerabilities", 0)
            }
        }
    
    def _validate_data_protection_policy(self,
                                        policy: Dict[str, Any],
                                        deployment_manifest: Dict[str, Any],
                                        environment_config: Dict[str, Any],
                                        evidence: Dict[str, Any],
                                        result: Dict[str, Any]):
        """
        Validate a data protection policy.
        
        Args:
            policy: Data protection policy to validate
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            evidence: Evidence collected for validation
            result: Result dictionary to update
        """
        rules = policy.get("rules", [])
        
        # Data protection-specific validations
        data_evidence = evidence.get("data_protection", {})
        
        # Check for data encryption
        if policy.get("require_encryption", False):
            if not data_evidence.get("encryption_enabled", False):
                result["violations"].append({
                    "code": "missing_encryption",
                    "message": "Deployment does not have data encryption enabled"
                })
        
        # Check for data classification
        if policy.get("require_data_classification", False):
            if not data_evidence.get("data_classification_implemented", False):
                result["violations"].append({
                    "code": "missing_data_classification",
                    "message": "Deployment does not implement data classification"
                })
        
        # Check for data retention policies
        if policy.get("require_data_retention_policy", False):
            if not data_evidence.get("data_retention_policy_implemented", False):
                result["violations"].append({
                    "code": "missing_data_retention_policy",
                    "message": "Deployment does not implement data retention policies"
                })
        
        # Check for data backup
        if policy.get("require_data_backup", False):
            if not data_evidence.get("data_backup_configured", False):
                result["violations"].append({
                    "code": "missing_data_backup",
                    "message": "Deployment does not have data backup configured"
                })
        
        # Validate each rule
        for rule in rules:
            self._validate_rule(rule, deployment_manifest, environment_config, evidence, result)
        
        # Add data protection-specific details
        result["details"]["data_protection"] = {
            "encryption_enabled": data_evidence.get("encryption_enabled", False),
            "data_classification_implemented": data_evidence.get("data_classification_implemented", False),
            "data_retention_policy_implemented": data_evidence.get("data_retention_policy_implemented", False),
            "data_backup_configured": data_evidence.get("data_backup_configured", False)
        }
    
    def _validate_regulatory_policy(self,
                                   policy: Dict[str, Any],
                                   deployment_manifest: Dict[str, Any],
                                   environment_config: Dict[str, Any],
                                   evidence: Dict[str, Any],
                                   result: Dict[str, Any]):
        """
        Validate a regulatory policy.
        
        Args:
            policy: Regulatory policy to validate
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            evidence: Evidence collected for validation
            result: Result dictionary to update
        """
        rules = policy.get("rules", [])
        
        # Regulatory-specific validations
        regulatory_evidence = evidence.get("regulatory", {})
        
        # Check for required regulatory frameworks
        required_frameworks = policy.get("required_frameworks", [])
        implemented_frameworks = regulatory_evidence.get("implemented_frameworks", [])
        
        missing_frameworks = [f for f in required_frameworks if f not in implemented_frameworks]
        if missing_frameworks:
            result["violations"].append({
                "code": "missing_regulatory_frameworks",
                "message": f"Missing required regulatory frameworks: {', '.join(missing_frameworks)}",
                "missing_frameworks": missing_frameworks
            })
        
        # Check for compliance certifications
        required_certifications = policy.get("required_certifications", [])
        obtained_certifications = regulatory_evidence.get("obtained_certifications", [])
        
        missing_certifications = [c for c in required_certifications if c not in obtained_certifications]
        if missing_certifications:
            result["violations"].append({
                "code": "missing_certifications",
                "message": f"Missing required compliance certifications: {', '.join(missing_certifications)}",
                "missing_certifications": missing_certifications
            })
        
        # Check for data sovereignty
        if policy.get("require_data_sovereignty", False):
            region = environment_config.get("region", "unknown")
            allowed_regions = policy.get("allowed_regions", [])
            
            if allowed_regions and region not in allowed_regions:
                result["violations"].append({
                    "code": "data_sovereignty_violation",
                    "message": f"Deployment region {region} is not in allowed regions: {', '.join(allowed_regions)}",
                    "current_region": region,
                    "allowed_regions": allowed_regions
                })
        
        # Validate each rule
        for rule in rules:
            self._validate_rule(rule, deployment_manifest, environment_config, evidence, result)
        
        # Add regulatory-specific details
        result["details"]["regulatory"] = {
            "implemented_frameworks": implemented_frameworks,
            "missing_frameworks": missing_frameworks,
            "obtained_certifications": obtained_certifications,
            "missing_certifications": missing_certifications,
            "region": environment_config.get("region", "unknown")
        }
    
    def _validate_operational_policy(self,
                                    policy: Dict[str, Any],
                                    deployment_manifest: Dict[str, Any],
                                    environment_config: Dict[str, Any],
                                    evidence: Dict[str, Any],
                                    result: Dict[str, Any]):
        """
        Validate an operational policy.
        
        Args:
            policy: Operational policy to validate
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            evidence: Evidence collected for validation
            result: Result dictionary to update
        """
        rules = policy.get("rules", [])
        
        # Operational-specific validations
        operational_evidence = evidence.get("operational", {})
        
        # Check for monitoring
        if policy.get("require_monitoring", False):
            if not operational_evidence.get("monitoring_configured", False):
                result["violations"].append({
                    "code": "missing_monitoring",
                    "message": "Deployment does not have monitoring configured"
                })
        
        # Check for logging
        if policy.get("require_logging", False):
            if not operational_evidence.get("logging_configured", False):
                result["violations"].append({
                    "code": "missing_logging",
                    "message": "Deployment does not have logging configured"
                })
        
        # Check for alerting
        if policy.get("require_alerting", False):
            if not operational_evidence.get("alerting_configured", False):
                result["violations"].append({
                    "code": "missing_alerting",
                    "message": "Deployment does not have alerting configured"
                })
        
        # Check for resource limits
        if policy.get("require_resource_limits", False):
            if not operational_evidence.get("resource_limits_configured", False):
                result["violations"].append({
                    "code": "missing_resource_limits",
                    "message": "Deployment does not have resource limits configured"
                })
        
        # Validate each rule
        for rule in rules:
            self._validate_rule(rule, deployment_manifest, environment_config, evidence, result)
        
        # Add operational-specific details
        result["details"]["operational"] = {
            "monitoring_configured": operational_evidence.get("monitoring_configured", False),
            "logging_configured": operational_evidence.get("logging_configured", False),
            "alerting_configured": operational_evidence.get("alerting_configured", False),
            "resource_limits_configured": operational_evidence.get("resource_limits_configured", False)
        }
    
    def _validate_rule(self,
                      rule: Dict[str, Any],
                      deployment_manifest: Dict[str, Any],
                      environment_config: Dict[str, Any],
                      evidence: Dict[str, Any],
                      result: Dict[str, Any]):
        """
        Validate a single rule.
        
        Args:
            rule: Rule to validate
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            evidence: Evidence collected for validation
            result: Result dictionary to update
        """
        rule_id = rule.get("id", "unknown")
        rule_type = rule.get("type", "unknown")
        
        # Validate based on rule type
        if rule_type == "resource_check":
            self._validate_resource_check_rule(rule, deployment_manifest, result)
        elif rule_type == "configuration_check":
            self._validate_configuration_check_rule(rule, deployment_manifest, result)
        elif rule_type == "evidence_check":
            self._validate_evidence_check_rule(rule, evidence, result)
        elif rule_type == "environment_check":
            self._validate_environment_check_rule(rule, environment_config, result)
        else:
            logger.warning(f"Unknown rule type: {rule_type}")
            result["violations"].append({
                "code": "unknown_rule_type",
                "message": f"Unknown rule type: {rule_type}",
                "rule_id": rule_id
            })
    
    def _validate_resource_check_rule(self,
                                     rule: Dict[str, Any],
                                     deployment_manifest: Dict[str, Any],
                                     result: Dict[str, Any]):
        """
        Validate a resource check rule.
        
        Args:
            rule: Resource check rule to validate
            deployment_manifest: The deployment manifest
            result: Result dictionary to update
        """
        rule_id = rule.get("id", "unknown")
        resource_type = rule.get("resource_type", "")
        resource_property = rule.get("resource_property", "")
        expected_value = rule.get("expected_value", None)
        operator = rule.get("operator", "equals")
        
        # Get resources from manifest
        resources = deployment_manifest.get("resources", [])
        
        # Filter resources by type
        matching_resources = [r for r in resources if r.get("type") == resource_type]
        
        if not matching_resources:
            if rule.get("required", False):
                result["violations"].append({
                    "code": "missing_required_resource",
                    "message": f"Required resource of type {resource_type} not found",
                    "rule_id": rule_id
                })
            return
        
        # Check property for each resource
        for resource in matching_resources:
            if resource_property not in resource:
                result["violations"].append({
                    "code": "missing_resource_property",
                    "message": f"Resource of type {resource_type} is missing property {resource_property}",
                    "rule_id": rule_id,
                    "resource_id": resource.get("id", "unknown")
                })
                continue
            
            actual_value = resource[resource_property]
            
            # Compare values based on operator
            if not self._compare_values(actual_value, expected_value, operator):
                result["violations"].append({
                    "code": "resource_property_violation",
                    "message": f"Resource property {resource_property} value {actual_value} does not match expected value {expected_value} with operator {operator}",
                    "rule_id": rule_id,
                    "resource_id": resource.get("id", "unknown"),
                    "property": resource_property,
                    "actual_value": actual_value,
                    "expected_value": expected_value,
                    "operator": operator
                })
    
    def _validate_configuration_check_rule(self,
                                          rule: Dict[str, Any],
                                          deployment_manifest: Dict[str, Any],
                                          result: Dict[str, Any]):
        """
        Validate a configuration check rule.
        
        Args:
            rule: Configuration check rule to validate
            deployment_manifest: The deployment manifest
            result: Result dictionary to update
        """
        rule_id = rule.get("id", "unknown")
        config_path = rule.get("config_path", "")
        expected_value = rule.get("expected_value", None)
        operator = rule.get("operator", "equals")
        
        # Get configuration from manifest
        config = deployment_manifest.get("configuration", {})
        
        # Navigate config path
        path_parts = config_path.split(".")
        current = config
        
        for part in path_parts:
            if part not in current:
                if rule.get("required", False):
                    result["violations"].append({
                        "code": "missing_config_path",
                        "message": f"Required configuration path {config_path} not found",
                        "rule_id": rule_id
                    })
                return
            current = current[part]
        
        # Compare values based on operator
        if not self._compare_values(current, expected_value, operator):
            result["violations"].append({
                "code": "config_value_violation",
                "message": f"Configuration value at path {config_path} value {current} does not match expected value {expected_value} with operator {operator}",
                "rule_id": rule_id,
                "config_path": config_path,
                "actual_value": current,
                "expected_value": expected_value,
                "operator": operator
            })
    
    def _validate_evidence_check_rule(self,
                                     rule: Dict[str, Any],
                                     evidence: Dict[str, Any],
                                     result: Dict[str, Any]):
        """
        Validate an evidence check rule.
        
        Args:
            rule: Evidence check rule to validate
            evidence: Evidence collected for validation
            result: Result dictionary to update
        """
        rule_id = rule.get("id", "unknown")
        evidence_type = rule.get("evidence_type", "")
        evidence_property = rule.get("evidence_property", "")
        expected_value = rule.get("expected_value", None)
        operator = rule.get("operator", "equals")
        
        # Get evidence of specified type
        evidence_data = evidence.get(evidence_type, {})
        
        if not evidence_data:
            if rule.get("required", False):
                result["violations"].append({
                    "code": "missing_evidence_type",
                    "message": f"Required evidence of type {evidence_type} not found",
                    "rule_id": rule_id
                })
            return
        
        # Check property
        if evidence_property not in evidence_data:
            if rule.get("required", False):
                result["violations"].append({
                    "code": "missing_evidence_property",
                    "message": f"Evidence of type {evidence_type} is missing property {evidence_property}",
                    "rule_id": rule_id
                })
            return
        
        actual_value = evidence_data[evidence_property]
        
        # Compare values based on operator
        if not self._compare_values(actual_value, expected_value, operator):
            result["violations"].append({
                "code": "evidence_value_violation",
                "message": f"Evidence property {evidence_property} value {actual_value} does not match expected value {expected_value} with operator {operator}",
                "rule_id": rule_id,
                "evidence_type": evidence_type,
                "property": evidence_property,
                "actual_value": actual_value,
                "expected_value": expected_value,
                "operator": operator
            })
    
    def _validate_environment_check_rule(self,
                                        rule: Dict[str, Any],
                                        environment_config: Dict[str, Any],
                                        result: Dict[str, Any]):
        """
        Validate an environment check rule.
        
        Args:
            rule: Environment check rule to validate
            environment_config: Configuration of the target environment
            result: Result dictionary to update
        """
        rule_id = rule.get("id", "unknown")
        env_property = rule.get("env_property", "")
        expected_value = rule.get("expected_value", None)
        operator = rule.get("operator", "equals")
        
        # Check if property exists
        if env_property not in environment_config:
            if rule.get("required", False):
                result["violations"].append({
                    "code": "missing_env_property",
                    "message": f"Environment is missing property {env_property}",
                    "rule_id": rule_id
                })
            return
        
        actual_value = environment_config[env_property]
        
        # Compare values based on operator
        if not self._compare_values(actual_value, expected_value, operator):
            result["violations"].append({
                "code": "env_value_violation",
                "message": f"Environment property {env_property} value {actual_value} does not match expected value {expected_value} with operator {operator}",
                "rule_id": rule_id,
                "property": env_property,
                "actual_value": actual_value,
                "expected_value": expected_value,
                "operator": operator
            })
    
    def _compare_values(self, actual_value: Any, expected_value: Any, operator: str) -> bool:
        """
        Compare values based on the specified operator.
        
        Args:
            actual_value: Actual value to compare
            expected_value: Expected value to compare against
            operator: Comparison operator
            
        Returns:
            True if comparison succeeds, False otherwise
        """
        if operator == "equals":
            return actual_value == expected_value
        elif operator == "not_equals":
            return actual_value != expected_value
        elif operator == "greater_than":
            return actual_value > expected_value
        elif operator == "less_than":
            return actual_value < expected_value
        elif operator == "greater_than_or_equals":
            return actual_value >= expected_value
        elif operator == "less_than_or_equals":
            return actual_value <= expected_value
        elif operator == "contains":
            return expected_value in actual_value
        elif operator == "not_contains":
            return expected_value not in actual_value
        elif operator == "in":
            return actual_value in expected_value
        elif operator == "not_in":
            return actual_value not in expected_value
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _generate_summary(self, policy_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of policy validation results.
        
        Args:
            policy_results: List of policy validation results
            
        Returns:
            Dictionary containing summary information
        """
        total_policies = len(policy_results)
        compliant_policies = sum(1 for r in policy_results if r["compliant"])
        compliance_rate = compliant_policies / total_policies if total_policies > 0 else 0
        
        # Count by severity
        severity_counts = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        severity_compliance = {
            "high": {"total": 0, "compliant": 0},
            "medium": {"total": 0, "compliant": 0},
            "low": {"total": 0, "compliant": 0}
        }
        
        for result in policy_results:
            severity = result.get("policy_severity", "medium")
            severity_counts[severity] += 1
            severity_compliance[severity]["total"] += 1
            if result["compliant"]:
                severity_compliance[severity]["compliant"] += 1
        
        # Calculate compliance rates by severity
        for severity, counts in severity_compliance.items():
            if counts["total"] > 0:
                counts["rate"] = counts["compliant"] / counts["total"]
            else:
                counts["rate"] = 0
        
        # Count by policy type
        type_counts = {}
        type_compliance = {}
        
        for result in policy_results:
            policy_type = result.get("policy_type", "unknown")
            
            if policy_type not in type_counts:
                type_counts[policy_type] = 0
                type_compliance[policy_type] = {"total": 0, "compliant": 0}
            
            type_counts[policy_type] += 1
            type_compliance[policy_type]["total"] += 1
            
            if result["compliant"]:
                type_compliance[policy_type]["compliant"] += 1
        
        # Calculate compliance rates by type
        for policy_type, counts in type_compliance.items():
            if counts["total"] > 0:
                counts["rate"] = counts["compliant"] / counts["total"]
            else:
                counts["rate"] = 0
        
        return {
            "total_policies": total_policies,
            "compliant_policies": compliant_policies,
            "compliance_rate": compliance_rate,
            "severity_counts": severity_counts,
            "severity_compliance": severity_compliance,
            "type_counts": type_counts,
            "type_compliance": type_compliance
        }
    
    def _finalize_results(self, results: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """
        Finalize validation results.
        
        Args:
            results: Results dictionary to finalize
            start_time: Validation start time
            
        Returns:
            Finalized results dictionary
        """
        # Calculate validation time
        results["validation_time"] = time.time() - start_time
        
        # Sort violations by severity
        results["violations"].sort(key=lambda v: {
            "high": 0,
            "medium": 1,
            "low": 2
        }.get(v.get("severity", "medium"), 1))
        
        return results
