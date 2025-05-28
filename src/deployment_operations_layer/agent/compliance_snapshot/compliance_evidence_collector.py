"""
Compliance Evidence Collector

This module is responsible for collecting evidence for compliance validation.
It gathers information about the deployment and environment to be used in
compliance validation against policy sets.
"""

import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ComplianceEvidenceCollector:
    """
    Collects evidence for compliance validation.
    
    This class gathers information about the deployment and environment to be used in
    compliance validation against policy sets. It collects evidence across various
    categories including security, data protection, regulatory, and operational.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Compliance Evidence Collector.
        
        Args:
            config: Configuration dictionary for the collector
        """
        self.config = config or {}
        
        # Collection settings
        self.collection_timeout = self.config.get("collection_timeout", 300)  # 5 minutes
        self.collection_depth = self.config.get("collection_depth", "standard")  # standard, deep, minimal
        
        # Evidence sources
        self.evidence_sources = self.config.get("evidence_sources", [
            "deployment_manifest",
            "environment_config",
            "runtime_inspection",
            "security_scans",
            "logs"
        ])
        
        logger.info("Compliance Evidence Collector initialized")
    
    def collect_evidence(self,
                        deployment_manifest: Dict[str, Any],
                        environment_config: Dict[str, Any],
                        policy_set: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect evidence for compliance validation.
        
        Args:
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            policy_set: Policy set to collect evidence for
            
        Returns:
            Dictionary containing collected evidence
        """
        logger.info(f"Collecting evidence for deployment {deployment_manifest.get('id', 'unknown')}")
        
        start_time = time.time()
        
        # Initialize evidence
        evidence = {
            "timestamp": time.time(),
            "collection_time": 0,
            "deployment_id": deployment_manifest.get("id", "unknown"),
            "environment": environment_config.get("name", "unknown"),
            "policy_set_id": policy_set.get("id", "unknown"),
            "collection_depth": self.collection_depth,
            "evidence_sources": self.evidence_sources
        }
        
        try:
            # Determine required evidence types based on policy set
            required_evidence_types = self._determine_required_evidence_types(policy_set)
            
            # Collect evidence for each required type
            for evidence_type in required_evidence_types:
                if evidence_type == "security":
                    evidence["security"] = self._collect_security_evidence(
                        deployment_manifest,
                        environment_config,
                        policy_set
                    )
                
                elif evidence_type == "data_protection":
                    evidence["data_protection"] = self._collect_data_protection_evidence(
                        deployment_manifest,
                        environment_config,
                        policy_set
                    )
                
                elif evidence_type == "regulatory":
                    evidence["regulatory"] = self._collect_regulatory_evidence(
                        deployment_manifest,
                        environment_config,
                        policy_set
                    )
                
                elif evidence_type == "operational":
                    evidence["operational"] = self._collect_operational_evidence(
                        deployment_manifest,
                        environment_config,
                        policy_set
                    )
            
            # Add collection metadata
            evidence["collection_time"] = time.time() - start_time
            evidence["collection_status"] = "completed"
            
        except Exception as e:
            logger.exception(f"Error collecting evidence: {e}")
            evidence["collection_status"] = "error"
            evidence["error"] = str(e)
        
        logger.info(f"Evidence collection completed in {evidence.get('collection_time', 0):.2f} seconds")
        
        return evidence
    
    def _determine_required_evidence_types(self, policy_set: Dict[str, Any]) -> List[str]:
        """
        Determine required evidence types based on policy set.
        
        Args:
            policy_set: Policy set to analyze
            
        Returns:
            List of required evidence types
        """
        required_types = set()
        
        # Check each policy
        for policy in policy_set.get("policies", []):
            policy_type = policy.get("type", "unknown")
            required_types.add(policy_type)
            
            # Check rules for evidence checks
            for rule in policy.get("rules", []):
                if rule.get("type") == "evidence_check":
                    evidence_type = rule.get("evidence_type", "unknown")
                    required_types.add(evidence_type)
        
        return list(required_types)
    
    def _collect_security_evidence(self,
                                  deployment_manifest: Dict[str, Any],
                                  environment_config: Dict[str, Any],
                                  policy_set: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect security evidence.
        
        Args:
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            policy_set: Policy set to collect evidence for
            
        Returns:
            Dictionary containing security evidence
        """
        logger.info("Collecting security evidence")
        
        # Extract security configuration from manifest
        security_config = deployment_manifest.get("configuration", {}).get("security", {})
        
        # Determine implemented controls
        implemented_controls = []
        
        # Check for access control
        if security_config.get("access_control_enabled", False):
            implemented_controls.append("access_control")
        
        # Check for encryption in transit
        if security_config.get("tls_enabled", False) or security_config.get("ssl_enabled", False):
            implemented_controls.append("encryption_in_transit")
        
        # Check for secure configuration
        if security_config.get("secure_configuration", False):
            implemented_controls.append("secure_configuration")
        
        # Check for network security
        if security_config.get("network_security_enabled", False):
            implemented_controls.append("network_security")
        
        # Check for identity management
        if security_config.get("identity_provider", None):
            implemented_controls.append("identity_management")
        
        # Check for Kubernetes-specific controls
        if environment_config.get("type") == "kubernetes":
            k8s_config = deployment_manifest.get("kubernetes", {})
            
            # Check for pod security policies
            if k8s_config.get("pod_security_policies_enabled", False):
                implemented_controls.append("pod_security_policies")
            
            # Check for network policies
            if k8s_config.get("network_policies_enabled", False):
                implemented_controls.append("network_policies")
            
            # Check for RBAC
            if k8s_config.get("rbac_enabled", False):
                implemented_controls.append("rbac")
            
            # Check for secure service accounts
            if k8s_config.get("secure_service_accounts", False):
                implemented_controls.append("secure_service_accounts")
        
        # Check for edge-specific controls
        if environment_config.get("is_edge", False):
            edge_config = deployment_manifest.get("edge", {})
            
            # Check for device authentication
            if edge_config.get("device_authentication_enabled", False):
                implemented_controls.append("device_authentication")
            
            # Check for secure boot
            if edge_config.get("secure_boot_enabled", False):
                implemented_controls.append("secure_boot")
            
            # Check for encrypted storage
            if edge_config.get("encrypted_storage_enabled", False):
                implemented_controls.append("encrypted_storage")
            
            # Check for secure communication
            if edge_config.get("secure_communication_enabled", False):
                implemented_controls.append("secure_communication")
        
        # Check for vulnerability scan results
        vulnerability_scan = deployment_manifest.get("security_scans", {}).get("vulnerability_scan", {})
        vulnerability_scan_completed = vulnerability_scan.get("completed", False)
        
        # Create security evidence
        security_evidence = {
            "implemented_controls": implemented_controls,
            "secure_communication": security_config.get("tls_enabled", False) or security_config.get("ssl_enabled", False),
            "authentication_enabled": security_config.get("authentication_enabled", False),
            "authorization_enabled": security_config.get("authorization_enabled", False),
            "vulnerability_scan_completed": vulnerability_scan_completed,
            "high_vulnerabilities": vulnerability_scan.get("high", 0),
            "medium_vulnerabilities": vulnerability_scan.get("medium", 0),
            "low_vulnerabilities": vulnerability_scan.get("low", 0)
        }
        
        return security_evidence
    
    def _collect_data_protection_evidence(self,
                                         deployment_manifest: Dict[str, Any],
                                         environment_config: Dict[str, Any],
                                         policy_set: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect data protection evidence.
        
        Args:
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            policy_set: Policy set to collect evidence for
            
        Returns:
            Dictionary containing data protection evidence
        """
        logger.info("Collecting data protection evidence")
        
        # Extract data configuration from manifest
        data_config = deployment_manifest.get("configuration", {}).get("data", {})
        
        # Create data protection evidence
        data_protection_evidence = {
            "encryption_enabled": data_config.get("encryption_enabled", False),
            "encryption_at_rest": data_config.get("encryption_at_rest", False),
            "encryption_in_transit": data_config.get("encryption_in_transit", False),
            "data_classification_implemented": data_config.get("data_classification_implemented", False),
            "data_retention_policy_implemented": data_config.get("data_retention_policy_implemented", False),
            "data_backup_configured": data_config.get("backup_enabled", False),
            "data_sovereignty_compliant": self._check_data_sovereignty(data_config, environment_config)
        }
        
        # Check for edge-specific data protection
        if environment_config.get("is_edge", False):
            edge_data_config = deployment_manifest.get("edge", {}).get("data", {})
            
            data_protection_evidence.update({
                "local_storage_encryption": edge_data_config.get("local_storage_encryption", False),
                "data_sync_encryption": edge_data_config.get("data_sync_encryption", False),
                "retention_days": edge_data_config.get("retention_days", 0)
            })
        
        return data_protection_evidence
    
    def _check_data_sovereignty(self,
                               data_config: Dict[str, Any],
                               environment_config: Dict[str, Any]) -> bool:
        """
        Check data sovereignty compliance.
        
        Args:
            data_config: Data configuration
            environment_config: Environment configuration
            
        Returns:
            True if compliant, False otherwise
        """
        # Get deployment region
        region = environment_config.get("region", "unknown")
        
        # Get data sovereignty requirements
        data_sovereignty = data_config.get("data_sovereignty", {})
        allowed_regions = data_sovereignty.get("allowed_regions", [])
        
        # If no specific regions are required, assume compliant
        if not allowed_regions:
            return True
        
        # Check if deployment region is allowed
        return region in allowed_regions
    
    def _collect_regulatory_evidence(self,
                                    deployment_manifest: Dict[str, Any],
                                    environment_config: Dict[str, Any],
                                    policy_set: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect regulatory evidence.
        
        Args:
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            policy_set: Policy set to collect evidence for
            
        Returns:
            Dictionary containing regulatory evidence
        """
        logger.info("Collecting regulatory evidence")
        
        # Extract regulatory configuration from manifest
        regulatory_config = deployment_manifest.get("configuration", {}).get("regulatory", {})
        
        # Get implemented frameworks
        implemented_frameworks = regulatory_config.get("implemented_frameworks", [])
        
        # Get obtained certifications
        obtained_certifications = regulatory_config.get("obtained_certifications", [])
        
        # Create regulatory evidence
        regulatory_evidence = {
            "implemented_frameworks": implemented_frameworks,
            "obtained_certifications": obtained_certifications,
            "data_residency_region": environment_config.get("region", "unknown"),
            "compliance_documentation_available": regulatory_config.get("compliance_documentation_available", False),
            "compliance_contact": regulatory_config.get("compliance_contact", "")
        }
        
        return regulatory_evidence
    
    def _collect_operational_evidence(self,
                                     deployment_manifest: Dict[str, Any],
                                     environment_config: Dict[str, Any],
                                     policy_set: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect operational evidence.
        
        Args:
            deployment_manifest: The deployment manifest
            environment_config: Configuration of the target environment
            policy_set: Policy set to collect evidence for
            
        Returns:
            Dictionary containing operational evidence
        """
        logger.info("Collecting operational evidence")
        
        # Extract operational configuration from manifest
        operational_config = deployment_manifest.get("configuration", {})
        monitoring_config = operational_config.get("monitoring", {})
        logging_config = operational_config.get("logging", {})
        alerting_config = operational_config.get("alerting", {})
        resources_config = operational_config.get("resources", {})
        
        # Create operational evidence
        operational_evidence = {
            "monitoring_configured": monitoring_config.get("enabled", False),
            "logging_configured": logging_config.get("enabled", False),
            "alerting_configured": alerting_config.get("enabled", False),
            "resource_limits_configured": self._check_resource_limits(resources_config, deployment_manifest)
        }
        
        # Check for Kubernetes-specific operational evidence
        if environment_config.get("type") == "kubernetes":
            k8s_config = deployment_manifest.get("kubernetes", {})
            
            operational_evidence.update({
                "health_probes_configured": k8s_config.get("health_probes_configured", False),
                "horizontal_pod_autoscaler_configured": k8s_config.get("horizontal_pod_autoscaler_configured", False),
                "pod_disruption_budget_configured": k8s_config.get("pod_disruption_budget_configured", False)
            })
        
        # Check for edge-specific operational evidence
        if environment_config.get("is_edge", False):
            edge_config = deployment_manifest.get("edge", {})
            
            operational_evidence.update({
                "offline_operation_supported": edge_config.get("offline_operation_supported", False),
                "local_monitoring_enabled": edge_config.get("local_monitoring_enabled", False),
                "remote_management_enabled": edge_config.get("remote_management_enabled", False)
            })
        
        return operational_evidence
    
    def _check_resource_limits(self,
                              resources_config: Dict[str, Any],
                              deployment_manifest: Dict[str, Any]) -> bool:
        """
        Check if resource limits are configured.
        
        Args:
            resources_config: Resources configuration
            deployment_manifest: The deployment manifest
            
        Returns:
            True if resource limits are configured, False otherwise
        """
        # Check global resource limits
        if resources_config.get("cpu_limit", 0) > 0 and resources_config.get("memory_limit", 0) > 0:
            return True
        
        # Check component resource limits
        components = deployment_manifest.get("components", [])
        
        for component in components:
            component_resources = component.get("resources", {})
            if not component_resources:
                return False
            
            if component_resources.get("limits", {}).get("cpu", 0) <= 0:
                return False
            
            if component_resources.get("limits", {}).get("memory", 0) <= 0:
                return False
        
        return len(components) > 0
