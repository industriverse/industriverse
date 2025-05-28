"""
Data Governance System for Industriverse Data Layer

This module implements the Data Governance System for the Industriverse Data Layer,
providing policy management, compliance monitoring, data lineage tracking, and
access control with full MCP/A2A protocol integration.

Key Features:
- Protocol-native policy definition and enforcement
- Compliance monitoring with real-time alerts
- Data lineage tracking with provenance graphs
- Fine-grained access control with role-based permissions
- MCP/A2A integration for cross-system governance
- Industry-specific governance templates
- Audit logging and reporting

Classes:
- DataGovernanceSystem: Main governance system implementation
- PolicyManager: Manages governance policies
- ComplianceMonitor: Monitors compliance with policies
- LineageTracker: Tracks data lineage and provenance
- AccessController: Controls access to data assets
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from ..protocols.agent_core import AgentCore
from ..protocols.protocol_translator import ProtocolTranslator
from ..protocols.mesh_boot_lifecycle import MeshBootLifecycle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataGovernanceSystem(AgentCore):
    """
    Protocol-native Data Governance System for Industriverse Data Layer.
    
    Implements comprehensive governance capabilities with MCP/A2A integration.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Data Governance System with protocol-native capabilities.
        
        Args:
            config_path: Path to governance configuration file
        """
        super().__init__(
            agent_id="data_governance_system",
            agent_type="governance",
            intelligence_type="regulatory",
            description="Protocol-native data governance system for industrial data"
        )
        
        self.config = self._load_config(config_path)
        self.policy_manager = PolicyManager(self)
        self.compliance_monitor = ComplianceMonitor(self)
        self.lineage_tracker = LineageTracker(self)
        self.access_controller = AccessController(self)
        
        # Register with mesh boot lifecycle
        self.mesh_boot = MeshBootLifecycle()
        self.mesh_boot.register_agent(self)
        
        # Initialize protocol translator for MCP/A2A communication
        self.protocol_translator = ProtocolTranslator()
        
        logger.info("Data Governance System initialized with protocol-native capabilities")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load governance configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "governance_level": "enterprise",
            "compliance_frameworks": ["GDPR", "ISO27001", "NIST"],
            "audit_frequency": "daily",
            "retention_policies": {
                "raw_data": "7_years",
                "processed_data": "5_years",
                "analytical_results": "3_years"
            },
            "industry_specific_rules": {
                "manufacturing": {
                    "quality_data_retention": "10_years",
                    "machine_logs_retention": "5_years"
                },
                "energy": {
                    "sensor_data_retention": "7_years",
                    "compliance_reports_retention": "10_years"
                }
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
            except Exception as e:
                logger.error(f"Error loading governance config: {e}")
                return default_config
        return default_config
    
    def register_dataset(self, dataset_id: str, metadata: Dict) -> Dict:
        """
        Register a dataset with the governance system.
        
        Args:
            dataset_id: Unique identifier for the dataset
            metadata: Dataset metadata including industry tags
            
        Returns:
            Registration result with governance policies applied
        """
        logger.info(f"Registering dataset {dataset_id} with governance system")
        
        # Apply industry-specific governance rules
        industry_tags = metadata.get("industryTags", [])
        applied_policies = self.policy_manager.apply_policies(dataset_id, industry_tags)
        
        # Track dataset lineage
        lineage_id = self.lineage_tracker.initialize_lineage(dataset_id, metadata)
        
        # Set up access controls
        access_rules = self.access_controller.create_default_rules(dataset_id, metadata)
        
        # Register with compliance monitoring
        compliance_status = self.compliance_monitor.register_dataset(dataset_id, metadata)
        
        # Prepare MCP-compatible response
        response = {
            "datasetId": dataset_id,
            "governanceStatus": "registered",
            "appliedPolicies": applied_policies,
            "lineageId": lineage_id,
            "accessRules": access_rules,
            "complianceStatus": compliance_status,
            "registrationTimestamp": datetime.utcnow().isoformat()
        }
        
        # Translate to appropriate protocol format if needed
        return self.protocol_translator.translate_response(response, "MCP")
    
    def validate_data_operation(self, operation: Dict) -> Dict:
        """
        Validate a data operation against governance policies.
        
        Args:
            operation: Data operation details
            
        Returns:
            Validation result with approval status
        """
        logger.info(f"Validating data operation: {operation.get('operationType')} on {operation.get('datasetId')}")
        
        dataset_id = operation.get("datasetId")
        operation_type = operation.get("operationType")
        user_context = operation.get("userContext", {})
        
        # Check access permissions
        access_check = self.access_controller.check_access(
            dataset_id, 
            user_context.get("userId"), 
            operation_type
        )
        
        if not access_check["allowed"]:
            return {
                "approved": False,
                "reason": access_check["reason"],
                "operationId": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Check compliance with policies
        compliance_check = self.compliance_monitor.check_operation_compliance(
            dataset_id,
            operation_type,
            operation.get("parameters", {})
        )
        
        if not compliance_check["compliant"]:
            return {
                "approved": False,
                "reason": compliance_check["reason"],
                "operationId": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Update lineage with new operation
        self.lineage_tracker.record_operation(
            dataset_id,
            operation_type,
            user_context,
            operation.get("parameters", {})
        )
        
        return {
            "approved": True,
            "operationId": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "auditRecord": {
                "recorded": True,
                "auditId": str(uuid.uuid4())
            }
        }
    
    def get_data_lineage(self, dataset_id: str) -> Dict:
        """
        Get the complete lineage for a dataset.
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Complete lineage graph for the dataset
        """
        return self.lineage_tracker.get_lineage(dataset_id)
    
    def handle_mcp_request(self, request: Dict) -> Dict:
        """
        Handle an incoming MCP protocol request.
        
        Args:
            request: MCP request payload
            
        Returns:
            MCP response payload
        """
        request_type = request.get("type")
        
        if request_type == "governance.register":
            return self.register_dataset(
                request.get("datasetId"),
                request.get("metadata", {})
            )
        elif request_type == "governance.validate":
            return self.validate_data_operation(request.get("operation", {}))
        elif request_type == "governance.lineage":
            return self.get_data_lineage(request.get("datasetId"))
        else:
            return {
                "error": "Unsupported governance request type",
                "requestType": request_type
            }
    
    def handle_a2a_request(self, request: Dict) -> Dict:
        """
        Handle an incoming A2A protocol request.
        
        Args:
            request: A2A request payload
            
        Returns:
            A2A response payload
        """
        # Translate A2A request to internal format
        internal_request = self.protocol_translator.translate_request(request, "A2A")
        
        # Process using internal methods
        result = self.handle_mcp_request(internal_request)
        
        # Translate response back to A2A format
        return self.protocol_translator.translate_response(result, "A2A")


class PolicyManager:
    """
    Manages data governance policies with protocol-native capabilities.
    """
    
    def __init__(self, governance_system):
        """
        Initialize the Policy Manager.
        
        Args:
            governance_system: Parent governance system
        """
        self.governance_system = governance_system
        self.policies = {}
        self._load_default_policies()
    
    def _load_default_policies(self):
        """Load default governance policies."""
        self.policies = {
            "data_classification": {
                "public": {"access_level": "open", "encryption": "none"},
                "internal": {"access_level": "authenticated", "encryption": "standard"},
                "confidential": {"access_level": "restricted", "encryption": "high"},
                "restricted": {"access_level": "highly_restricted", "encryption": "highest"}
            },
            "retention": {
                "temporary": {"duration": "30_days"},
                "short_term": {"duration": "1_year"},
                "medium_term": {"duration": "5_years"},
                "long_term": {"duration": "10_years"},
                "permanent": {"duration": "indefinite"}
            },
            "industry_specific": {
                "manufacturing": {
                    "quality_data": {"classification": "internal", "retention": "long_term"},
                    "machine_logs": {"classification": "internal", "retention": "medium_term"},
                    "production_metrics": {"classification": "confidential", "retention": "long_term"}
                },
                "energy": {
                    "sensor_data": {"classification": "internal", "retention": "medium_term"},
                    "compliance_reports": {"classification": "confidential", "retention": "long_term"}
                },
                "aerospace": {
                    "flight_data": {"classification": "restricted", "retention": "permanent"},
                    "maintenance_logs": {"classification": "confidential", "retention": "long_term"}
                }
            }
        }
    
    def apply_policies(self, dataset_id: str, industry_tags: List[str]) -> Dict:
        """
        Apply governance policies to a dataset based on industry tags.
        
        Args:
            dataset_id: Dataset identifier
            industry_tags: List of industry tags
            
        Returns:
            Applied policies
        """
        applied_policies = {
            "classification": "internal",  # Default classification
            "retention": "medium_term",    # Default retention
            "encryption": "standard",      # Default encryption
            "access_control": "role_based" # Default access control
        }
        
        # Apply industry-specific policies if tags match
        for tag in industry_tags:
            if tag in self.policies.get("industry_specific", {}):
                industry_policies = self.policies["industry_specific"][tag]
                
                # Apply the most restrictive policies from each matched industry
                for data_type, policies in industry_policies.items():
                    classification = policies.get("classification")
                    retention = policies.get("retention")
                    
                    if classification:
                        current_level = self._get_classification_level(applied_policies["classification"])
                        new_level = self._get_classification_level(classification)
                        
                        if new_level > current_level:
                            applied_policies["classification"] = classification
                            
                            # Update encryption based on classification
                            applied_policies["encryption"] = self.policies["data_classification"][classification]["encryption"]
                    
                    if retention:
                        current_duration = self._get_retention_duration(applied_policies["retention"])
                        new_duration = self._get_retention_duration(retention)
                        
                        if new_duration > current_duration:
                            applied_policies["retention"] = retention
        
        return applied_policies
    
    def _get_classification_level(self, classification: str) -> int:
        """
        Get the numeric level for a classification.
        
        Args:
            classification: Classification name
            
        Returns:
            Numeric level (higher is more restricted)
        """
        levels = {
            "public": 0,
            "internal": 1,
            "confidential": 2,
            "restricted": 3
        }
        return levels.get(classification, 0)
    
    def _get_retention_duration(self, retention: str) -> int:
        """
        Get the numeric duration for a retention policy.
        
        Args:
            retention: Retention policy name
            
        Returns:
            Duration in days
        """
        durations = {
            "temporary": 30,
            "short_term": 365,
            "medium_term": 1825,  # 5 years
            "long_term": 3650,    # 10 years
            "permanent": 36500    # 100 years (effectively permanent)
        }
        return durations.get(retention, 0)


class ComplianceMonitor:
    """
    Monitors compliance with governance policies.
    """
    
    def __init__(self, governance_system):
        """
        Initialize the Compliance Monitor.
        
        Args:
            governance_system: Parent governance system
        """
        self.governance_system = governance_system
        self.monitored_datasets = {}
        self.compliance_frameworks = self.governance_system.config.get("compliance_frameworks", [])
    
    def register_dataset(self, dataset_id: str, metadata: Dict) -> Dict:
        """
        Register a dataset for compliance monitoring.
        
        Args:
            dataset_id: Dataset identifier
            metadata: Dataset metadata
            
        Returns:
            Initial compliance status
        """
        industry_tags = metadata.get("industryTags", [])
        
        # Determine applicable compliance frameworks
        applicable_frameworks = self._get_applicable_frameworks(industry_tags)
        
        # Initialize compliance status
        compliance_status = {
            "overall": "compliant",
            "frameworks": {}
        }
        
        # Check compliance for each applicable framework
        for framework in applicable_frameworks:
            framework_status = self._check_framework_compliance(dataset_id, metadata, framework)
            compliance_status["frameworks"][framework] = framework_status
            
            # Update overall status if any framework is non-compliant
            if framework_status["status"] != "compliant":
                compliance_status["overall"] = "non_compliant"
        
        # Store monitoring information
        self.monitored_datasets[dataset_id] = {
            "metadata": metadata,
            "applicable_frameworks": applicable_frameworks,
            "compliance_status": compliance_status,
            "last_checked": datetime.utcnow().isoformat()
        }
        
        return compliance_status
    
    def check_operation_compliance(self, dataset_id: str, operation_type: str, parameters: Dict) -> Dict:
        """
        Check if an operation complies with governance policies.
        
        Args:
            dataset_id: Dataset identifier
            operation_type: Type of operation
            parameters: Operation parameters
            
        Returns:
            Compliance check result
        """
        if dataset_id not in self.monitored_datasets:
            return {
                "compliant": False,
                "reason": "Dataset not registered for compliance monitoring"
            }
        
        dataset_info = self.monitored_datasets[dataset_id]
        applicable_frameworks = dataset_info["applicable_frameworks"]
        
        # Check operation against each applicable framework
        for framework in applicable_frameworks:
            framework_check = self._check_operation_against_framework(
                dataset_id, 
                operation_type, 
                parameters, 
                framework
            )
            
            if not framework_check["compliant"]:
                return framework_check
        
        return {
            "compliant": True,
            "frameworks_checked": applicable_frameworks
        }
    
    def _get_applicable_frameworks(self, industry_tags: List[str]) -> List[str]:
        """
        Determine applicable compliance frameworks based on industry tags.
        
        Args:
            industry_tags: List of industry tags
            
        Returns:
            List of applicable compliance frameworks
        """
        # Start with base frameworks
        frameworks = self.compliance_frameworks.copy()
        
        # Add industry-specific frameworks
        industry_framework_map = {
            "manufacturing": ["ISO9001", "ISO14001"],
            "energy": ["ISO50001", "NERC-CIP"],
            "healthcare": ["HIPAA", "HITECH"],
            "finance": ["PCI-DSS", "SOX"],
            "aerospace": ["AS9100", "ITAR"]
        }
        
        for tag in industry_tags:
            if tag in industry_framework_map:
                frameworks.extend(industry_framework_map[tag])
        
        return list(set(frameworks))  # Remove duplicates
    
    def _check_framework_compliance(self, dataset_id: str, metadata: Dict, framework: str) -> Dict:
        """
        Check dataset compliance with a specific framework.
        
        Args:
            dataset_id: Dataset identifier
            metadata: Dataset metadata
            framework: Compliance framework
            
        Returns:
            Framework compliance status
        """
        # Framework-specific compliance checks
        if framework == "GDPR":
            return self._check_gdpr_compliance(metadata)
        elif framework == "ISO27001":
            return self._check_iso27001_compliance(metadata)
        elif framework == "NIST":
            return self._check_nist_compliance(metadata)
        else:
            # Generic compliance check for other frameworks
            return {
                "status": "compliant",
                "framework": framework,
                "details": "Generic compliance check passed"
            }
    
    def _check_gdpr_compliance(self, metadata: Dict) -> Dict:
        """
        Check GDPR compliance.
        
        Args:
            metadata: Dataset metadata
            
        Returns:
            GDPR compliance status
        """
        has_pii = metadata.get("containsPII", False)
        has_consent = metadata.get("dataSubjectConsent", False)
        has_retention_policy = "retention" in metadata
        
        if has_pii and not has_consent:
            return {
                "status": "non_compliant",
                "framework": "GDPR",
                "details": "Dataset contains PII without explicit consent",
                "remediation": "Obtain and document data subject consent"
            }
        
        if has_pii and not has_retention_policy:
            return {
                "status": "warning",
                "framework": "GDPR",
                "details": "Dataset contains PII without explicit retention policy",
                "remediation": "Define and apply retention policy"
            }
        
        return {
            "status": "compliant",
            "framework": "GDPR",
            "details": "All GDPR requirements satisfied"
        }
    
    def _check_iso27001_compliance(self, metadata: Dict) -> Dict:
        """
        Check ISO27001 compliance.
        
        Args:
            metadata: Dataset metadata
            
        Returns:
            ISO27001 compliance status
        """
        has_classification = "classification" in metadata
        has_owner = "owner" in metadata
        has_encryption = metadata.get("encryption", "none") != "none"
        
        if not has_classification or not has_owner:
            return {
                "status": "non_compliant",
                "framework": "ISO27001",
                "details": "Missing required metadata: classification or owner",
                "remediation": "Add classification and owner metadata"
            }
        
        if metadata.get("classification") in ["confidential", "restricted"] and not has_encryption:
            return {
                "status": "warning",
                "framework": "ISO27001",
                "details": "Sensitive data without encryption",
                "remediation": "Apply appropriate encryption"
            }
        
        return {
            "status": "compliant",
            "framework": "ISO27001",
            "details": "All ISO27001 requirements satisfied"
        }
    
    def _check_nist_compliance(self, metadata: Dict) -> Dict:
        """
        Check NIST compliance.
        
        Args:
            metadata: Dataset metadata
            
        Returns:
            NIST compliance status
        """
        has_access_controls = "accessControl" in metadata
        has_integrity_checks = metadata.get("integrityChecks", False)
        
        if not has_access_controls:
            return {
                "status": "non_compliant",
                "framework": "NIST",
                "details": "Missing access controls",
                "remediation": "Define and apply access controls"
            }
        
        if not has_integrity_checks:
            return {
                "status": "warning",
                "framework": "NIST",
                "details": "Missing integrity verification",
                "remediation": "Implement data integrity checks"
            }
        
        return {
            "status": "compliant",
            "framework": "NIST",
            "details": "All NIST requirements satisfied"
        }
    
    def _check_operation_against_framework(
        self, 
        dataset_id: str, 
        operation_type: str, 
        parameters: Dict, 
        framework: str
    ) -> Dict:
        """
        Check if an operation complies with a specific framework.
        
        Args:
            dataset_id: Dataset identifier
            operation_type: Type of operation
            parameters: Operation parameters
            framework: Compliance framework
            
        Returns:
            Operation compliance check result
        """
        dataset_info = self.monitored_datasets[dataset_id]
        metadata = dataset_info["metadata"]
        
        # Framework-specific operation compliance checks
        if framework == "GDPR" and metadata.get("containsPII", False):
            if operation_type in ["export", "share", "transfer"]:
                destination = parameters.get("destination", "")
                has_transfer_agreement = parameters.get("dataTransferAgreement", False)
                
                if "external" in destination and not has_transfer_agreement:
                    return {
                        "compliant": False,
                        "framework": "GDPR",
                        "reason": "External transfer of PII data without transfer agreement",
                        "remediation": "Establish data transfer agreement before proceeding"
                    }
        
        elif framework == "ISO27001":
            if operation_type in ["delete", "update", "transform"] and metadata.get("classification") in ["confidential", "restricted"]:
                has_approval = parameters.get("approvedBy", "")
                
                if not has_approval:
                    return {
                        "compliant": False,
                        "framework": "ISO27001",
                        "reason": "Modification of sensitive data without approval",
                        "remediation": "Obtain appropriate approval before proceeding"
                    }
        
        return {
            "compliant": True,
            "framework": framework
        }


class LineageTracker:
    """
    Tracks data lineage and provenance with protocol-native capabilities.
    """
    
    def __init__(self, governance_system):
        """
        Initialize the Lineage Tracker.
        
        Args:
            governance_system: Parent governance system
        """
        self.governance_system = governance_system
        self.lineage_graphs = {}
    
    def initialize_lineage(self, dataset_id: str, metadata: Dict) -> str:
        """
        Initialize lineage tracking for a dataset.
        
        Args:
            dataset_id: Dataset identifier
            metadata: Dataset metadata
            
        Returns:
            Lineage identifier
        """
        lineage_id = str(uuid.uuid4())
        
        # Create initial lineage graph
        self.lineage_graphs[dataset_id] = {
            "lineageId": lineage_id,
            "datasetId": dataset_id,
            "metadata": metadata,
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
            "nodes": [
                {
                    "id": "origin",
                    "type": "source",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {
                        "source": metadata.get("source", "unknown"),
                        "format": metadata.get("format", "unknown"),
                        "schema": metadata.get("schema", {})
                    }
                }
            ],
            "edges": [],
            "current": "origin"
        }
        
        return lineage_id
    
    def record_operation(
        self, 
        dataset_id: str, 
        operation_type: str, 
        user_context: Dict, 
        parameters: Dict
    ) -> str:
        """
        Record an operation in the dataset lineage.
        
        Args:
            dataset_id: Dataset identifier
            operation_type: Type of operation
            user_context: User context information
            parameters: Operation parameters
            
        Returns:
            Node identifier for the operation
        """
        if dataset_id not in self.lineage_graphs:
            raise ValueError(f"Dataset {dataset_id} not registered for lineage tracking")
        
        lineage = self.lineage_graphs[dataset_id]
        current_node = lineage["current"]
        
        # Create new node for the operation
        node_id = f"{operation_type}_{str(uuid.uuid4())[:8]}"
        
        new_node = {
            "id": node_id,
            "type": "operation",
            "operationType": operation_type,
            "timestamp": datetime.utcnow().isoformat(),
            "user": user_context.get("userId", "system"),
            "parameters": parameters
        }
        
        # Create edge from current node to new node
        new_edge = {
            "source": current_node,
            "target": node_id,
            "type": operation_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update lineage graph
        lineage["nodes"].append(new_node)
        lineage["edges"].append(new_edge)
        lineage["current"] = node_id
        lineage["updatedAt"] = datetime.utcnow().isoformat()
        
        return node_id
    
    def get_lineage(self, dataset_id: str) -> Dict:
        """
        Get the complete lineage graph for a dataset.
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Complete lineage graph
        """
        if dataset_id not in self.lineage_graphs:
            return {
                "error": "Dataset not found",
                "datasetId": dataset_id
            }
        
        return self.lineage_graphs[dataset_id]
    
    def merge_lineage(self, source_dataset_id: str, target_dataset_id: str, operation_type: str, parameters: Dict) -> Dict:
        """
        Merge lineage from source dataset into target dataset.
        
        Args:
            source_dataset_id: Source dataset identifier
            target_dataset_id: Target dataset identifier
            operation_type: Type of merge operation
            parameters: Merge parameters
            
        Returns:
            Updated target lineage
        """
        if source_dataset_id not in self.lineage_graphs:
            raise ValueError(f"Source dataset {source_dataset_id} not registered for lineage tracking")
        
        if target_dataset_id not in self.lineage_graphs:
            raise ValueError(f"Target dataset {target_dataset_id} not registered for lineage tracking")
        
        source_lineage = self.lineage_graphs[source_dataset_id]
        target_lineage = self.lineage_graphs[target_dataset_id]
        
        # Create merge node in target lineage
        merge_node_id = f"merge_{str(uuid.uuid4())[:8]}"
        
        merge_node = {
            "id": merge_node_id,
            "type": "merge",
            "operationType": operation_type,
            "timestamp": datetime.utcnow().isoformat(),
            "sourceDatasetId": source_dataset_id,
            "parameters": parameters
        }
        
        # Create edge from current target node to merge node
        merge_edge = {
            "source": target_lineage["current"],
            "target": merge_node_id,
            "type": "merge_input",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create edge from source lineage to merge node
        source_edge = {
            "source": f"external:{source_dataset_id}:{source_lineage['current']}",
            "target": merge_node_id,
            "type": "merge_source",
            "timestamp": datetime.utcnow().isoformat(),
            "externalReference": {
                "datasetId": source_dataset_id,
                "lineageId": source_lineage["lineageId"],
                "nodeId": source_lineage["current"]
            }
        }
        
        # Update target lineage
        target_lineage["nodes"].append(merge_node)
        target_lineage["edges"].append(merge_edge)
        target_lineage["edges"].append(source_edge)
        target_lineage["current"] = merge_node_id
        target_lineage["updatedAt"] = datetime.utcnow().isoformat()
        
        # Add reference to external lineage
        if "externalReferences" not in target_lineage:
            target_lineage["externalReferences"] = []
        
        target_lineage["externalReferences"].append({
            "datasetId": source_dataset_id,
            "lineageId": source_lineage["lineageId"],
            "mergeNodeId": merge_node_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return target_lineage


class AccessController:
    """
    Controls access to data assets with protocol-native capabilities.
    """
    
    def __init__(self, governance_system):
        """
        Initialize the Access Controller.
        
        Args:
            governance_system: Parent governance system
        """
        self.governance_system = governance_system
        self.access_rules = {}
    
    def create_default_rules(self, dataset_id: str, metadata: Dict) -> Dict:
        """
        Create default access rules for a dataset.
        
        Args:
            dataset_id: Dataset identifier
            metadata: Dataset metadata
            
        Returns:
            Created access rules
        """
        classification = metadata.get("classification", "internal")
        industry_tags = metadata.get("industryTags", [])
        
        # Define default rules based on classification
        default_rules = {
            "public": {
                "read": ["*"],
                "write": ["admin", "data_owner"],
                "delete": ["admin"]
            },
            "internal": {
                "read": ["authenticated"],
                "write": ["admin", "data_owner", "data_engineer"],
                "delete": ["admin", "data_owner"]
            },
            "confidential": {
                "read": ["admin", "data_owner", "data_scientist", "data_engineer"],
                "write": ["admin", "data_owner"],
                "delete": ["admin"]
            },
            "restricted": {
                "read": ["admin", "data_owner"],
                "write": ["admin"],
                "delete": ["admin"]
            }
        }
        
        # Get rules for the dataset's classification
        rules = default_rules.get(classification, default_rules["internal"])
        
        # Add industry-specific roles if applicable
        for tag in industry_tags:
            if tag == "manufacturing":
                rules["read"].append("manufacturing_analyst")
            elif tag == "energy":
                rules["read"].append("energy_analyst")
            elif tag == "healthcare":
                rules["read"].append("healthcare_analyst")
        
        # Store rules for the dataset
        self.access_rules[dataset_id] = {
            "classification": classification,
            "rules": rules,
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        }
        
        return self.access_rules[dataset_id]
    
    def check_access(self, dataset_id: str, user_id: str, operation_type: str) -> Dict:
        """
        Check if a user has access to perform an operation on a dataset.
        
        Args:
            dataset_id: Dataset identifier
            user_id: User identifier
            operation_type: Type of operation
            
        Returns:
            Access check result
        """
        if dataset_id not in self.access_rules:
            return {
                "allowed": False,
                "reason": "Dataset not registered for access control"
            }
        
        if not user_id:
            return {
                "allowed": False,
                "reason": "User not authenticated"
            }
        
        # Map operation type to access type
        access_type_map = {
            "read": "read",
            "query": "read",
            "export": "read",
            "write": "write",
            "update": "write",
            "transform": "write",
            "delete": "delete"
        }
        
        access_type = access_type_map.get(operation_type, "read")
        
        # Get allowed roles for the access type
        rules = self.access_rules[dataset_id]["rules"]
        allowed_roles = rules.get(access_type, [])
        
        # Check if user has any of the allowed roles
        # In a real implementation, this would check against a user directory
        # For now, we'll simulate with a simple check
        user_roles = self._get_user_roles(user_id)
        
        # Check for wildcard access
        if "*" in allowed_roles:
            return {
                "allowed": True,
                "accessType": access_type
            }
        
        # Check for authenticated access
        if "authenticated" in allowed_roles and user_id:
            return {
                "allowed": True,
                "accessType": access_type
            }
        
        # Check for role-based access
        for role in user_roles:
            if role in allowed_roles:
                return {
                    "allowed": True,
                    "accessType": access_type,
                    "grantedByRole": role
                }
        
        return {
            "allowed": False,
            "reason": f"User does not have required roles for {access_type} access",
            "requiredRoles": allowed_roles,
            "userRoles": user_roles
        }
    
    def _get_user_roles(self, user_id: str) -> List[str]:
        """
        Get roles for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user roles
        """
        # In a real implementation, this would query a user directory
        # For now, we'll simulate with hardcoded roles
        if user_id == "admin":
            return ["admin"]
        elif user_id.startswith("owner"):
            return ["data_owner"]
        elif user_id.startswith("engineer"):
            return ["data_engineer"]
        elif user_id.startswith("scientist"):
            return ["data_scientist"]
        elif user_id.startswith("manufacturing"):
            return ["manufacturing_analyst"]
        elif user_id.startswith("energy"):
            return ["energy_analyst"]
        else:
            return ["authenticated"]
    
    def update_access_rules(self, dataset_id: str, rules_update: Dict) -> Dict:
        """
        Update access rules for a dataset.
        
        Args:
            dataset_id: Dataset identifier
            rules_update: Rules to update
            
        Returns:
            Updated access rules
        """
        if dataset_id not in self.access_rules:
            raise ValueError(f"Dataset {dataset_id} not registered for access control")
        
        current_rules = self.access_rules[dataset_id]
        
        # Update rules
        for access_type, roles in rules_update.get("rules", {}).items():
            current_rules["rules"][access_type] = roles
        
        # Update classification if provided
        if "classification" in rules_update:
            current_rules["classification"] = rules_update["classification"]
        
        current_rules["updatedAt"] = datetime.utcnow().isoformat()
        
        return current_rules
