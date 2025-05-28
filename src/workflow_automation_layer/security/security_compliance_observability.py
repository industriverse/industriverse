"""
Security and Compliance Module for the Workflow Automation Layer

This module implements security, compliance, and observability features for the
Workflow Automation Layer, including:
- Trust-aware execution mode enforcement
- Compliance policy management
- Audit logging and tracing
- EKIS security integration
- Observability instrumentation

The module ensures that workflows execute according to their trust and confidence
requirements while maintaining comprehensive audit trails and observability.
"""

import json
import logging
import uuid
import time
import hashlib
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Enum representing security levels for workflow execution."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    """Enum representing compliance standards."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    NIST = "nist"
    CUSTOM = "custom"


@dataclass
class TrustPolicy:
    """Policy for trust-aware execution."""
    name: str
    description: str
    min_trust_score: float
    min_confidence_score: float
    requires_human_oversight: bool
    security_level: SecurityLevel
    allowed_execution_modes: List[str]
    restricted_data_categories: List[str] = field(default_factory=list)
    restricted_operations: List[str] = field(default_factory=list)
    escalation_threshold: float = 0.7
    cooldown_period_seconds: int = 300
    max_retry_count: int = 3


@dataclass
class CompliancePolicy:
    """Policy for compliance enforcement."""
    name: str
    description: str
    standard: ComplianceStandard
    version: str
    rules: Dict[str, Any]
    data_retention_days: int
    data_categories: List[str]
    required_approvals: List[str] = field(default_factory=list)
    audit_frequency_hours: int = 24
    custom_validators: List[str] = field(default_factory=list)


@dataclass
class AuditRecord:
    """Record for audit logging."""
    id: str
    timestamp: str
    entity_id: str
    entity_type: str
    action: str
    actor_id: str
    actor_type: str
    status: str
    details: Dict[str, Any]
    trust_score: float
    confidence_score: float
    execution_mode: str
    data_categories: List[str]
    ip_address: Optional[str] = None
    geo_location: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    parent_id: Optional[str] = None
    hash_value: Optional[str] = None


class TrustAwareSecurityManager:
    """
    Manager for trust-aware security enforcement.
    
    This class provides methods for enforcing trust-aware execution policies,
    managing security levels, and handling security-related events.
    """
    
    def __init__(self):
        """Initialize a new TrustAwareSecurityManager."""
        self.trust_policies = {}
        self.entity_trust_scores = {}
        self.entity_confidence_scores = {}
        self.entity_execution_modes = {}
        self.security_events = []
        self.policy_violations = []
        self.escalation_handlers = {}
        
        logger.info("Initialized TrustAwareSecurityManager")
    
    def register_trust_policy(self, policy: TrustPolicy) -> None:
        """
        Register a trust policy.
        
        Args:
            policy: Trust policy to register
        """
        self.trust_policies[policy.name] = policy
        logger.info(f"Registered trust policy: {policy.name}")
    
    def update_entity_scores(
        self,
        entity_id: str,
        trust_score: float,
        confidence_score: float,
        execution_mode: str
    ) -> None:
        """
        Update trust and confidence scores for an entity.
        
        Args:
            entity_id: ID of the entity
            trust_score: Trust score (0-1)
            confidence_score: Confidence score (0-1)
            execution_mode: Current execution mode
        """
        self.entity_trust_scores[entity_id] = trust_score
        self.entity_confidence_scores[entity_id] = confidence_score
        self.entity_execution_modes[entity_id] = execution_mode
        
        logger.debug(
            f"Updated scores for {entity_id}: "
            f"trust={trust_score}, confidence={confidence_score}, "
            f"mode={execution_mode}"
        )
    
    def check_execution_permission(
        self,
        entity_id: str,
        policy_name: str,
        operation: str,
        data_categories: List[str] = None
    ) -> Dict[str, Any]:
        """
        Check if an entity has permission to execute an operation.
        
        Args:
            entity_id: ID of the entity
            policy_name: Name of the trust policy to check against
            operation: Operation to check permission for
            data_categories: Categories of data involved in the operation
            
        Returns:
            Dictionary with permission result and details
        """
        if policy_name not in self.trust_policies:
            logger.error(f"Trust policy not found: {policy_name}")
            return {
                "permitted": False,
                "reason": f"Trust policy not found: {policy_name}",
                "escalation_required": True
            }
        
        policy = self.trust_policies[policy_name]
        trust_score = self.entity_trust_scores.get(entity_id, 0.0)
        confidence_score = self.entity_confidence_scores.get(entity_id, 0.0)
        execution_mode = self.entity_execution_modes.get(entity_id, "unknown")
        
        # Check if trust and confidence scores meet policy requirements
        if trust_score < policy.min_trust_score:
            return {
                "permitted": False,
                "reason": f"Trust score too low: {trust_score} < {policy.min_trust_score}",
                "escalation_required": trust_score < policy.escalation_threshold
            }
        
        if confidence_score < policy.min_confidence_score:
            return {
                "permitted": False,
                "reason": f"Confidence score too low: {confidence_score} < {policy.min_confidence_score}",
                "escalation_required": confidence_score < policy.escalation_threshold
            }
        
        # Check if execution mode is allowed
        if execution_mode not in policy.allowed_execution_modes:
            return {
                "permitted": False,
                "reason": f"Execution mode not allowed: {execution_mode}",
                "escalation_required": True
            }
        
        # Check if operation is restricted
        if operation in policy.restricted_operations:
            return {
                "permitted": False,
                "reason": f"Operation restricted: {operation}",
                "escalation_required": True
            }
        
        # Check if data categories are restricted
        if data_categories:
            restricted_categories = set(policy.restricted_data_categories) & set(data_categories)
            if restricted_categories:
                return {
                    "permitted": False,
                    "reason": f"Restricted data categories: {restricted_categories}",
                    "escalation_required": True
                }
        
        # All checks passed
        return {
            "permitted": True,
            "reason": "All security checks passed",
            "escalation_required": False
        }
    
    def record_security_event(
        self,
        entity_id: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> str:
        """
        Record a security event.
        
        Args:
            entity_id: ID of the entity
            event_type: Type of security event
            details: Details of the event
            
        Returns:
            ID of the recorded event
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        event = {
            "id": event_id,
            "timestamp": timestamp,
            "entity_id": entity_id,
            "event_type": event_type,
            "details": details,
            "trust_score": self.entity_trust_scores.get(entity_id, 0.0),
            "confidence_score": self.entity_confidence_scores.get(entity_id, 0.0),
            "execution_mode": self.entity_execution_modes.get(entity_id, "unknown")
        }
        
        self.security_events.append(event)
        logger.info(f"Recorded security event: {event_type} for {entity_id}")
        
        return event_id
    
    def record_policy_violation(
        self,
        entity_id: str,
        policy_name: str,
        violation_type: str,
        details: Dict[str, Any]
    ) -> str:
        """
        Record a policy violation.
        
        Args:
            entity_id: ID of the entity
            policy_name: Name of the violated policy
            violation_type: Type of violation
            details: Details of the violation
            
        Returns:
            ID of the recorded violation
        """
        violation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        violation = {
            "id": violation_id,
            "timestamp": timestamp,
            "entity_id": entity_id,
            "policy_name": policy_name,
            "violation_type": violation_type,
            "details": details,
            "trust_score": self.entity_trust_scores.get(entity_id, 0.0),
            "confidence_score": self.entity_confidence_scores.get(entity_id, 0.0),
            "execution_mode": self.entity_execution_modes.get(entity_id, "unknown")
        }
        
        self.policy_violations.append(violation)
        logger.warning(f"Recorded policy violation: {violation_type} for {entity_id}")
        
        # Trigger escalation if handler exists
        if violation_type in self.escalation_handlers:
            self.escalation_handlers[violation_type](violation)
        
        return violation_id
    
    def register_escalation_handler(
        self,
        violation_type: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Register a handler for policy violation escalation.
        
        Args:
            violation_type: Type of violation to handle
            handler: Function to call when violation occurs
        """
        self.escalation_handlers[violation_type] = handler
        logger.info(f"Registered escalation handler for: {violation_type}")
    
    def get_security_events(
        self,
        entity_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get security events matching the specified filters.
        
        Args:
            entity_id: Optional entity ID filter
            event_type: Optional event type filter
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            
        Returns:
            List of matching security events
        """
        filtered_events = self.security_events
        
        if entity_id:
            filtered_events = [e for e in filtered_events if e["entity_id"] == entity_id]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e["event_type"] == event_type]
        
        if start_time:
            filtered_events = [e for e in filtered_events if e["timestamp"] >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e["timestamp"] <= end_time]
        
        return filtered_events
    
    def get_policy_violations(
        self,
        entity_id: Optional[str] = None,
        policy_name: Optional[str] = None,
        violation_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get policy violations matching the specified filters.
        
        Args:
            entity_id: Optional entity ID filter
            policy_name: Optional policy name filter
            violation_type: Optional violation type filter
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            
        Returns:
            List of matching policy violations
        """
        filtered_violations = self.policy_violations
        
        if entity_id:
            filtered_violations = [v for v in filtered_violations if v["entity_id"] == entity_id]
        
        if policy_name:
            filtered_violations = [v for v in filtered_violations if v["policy_name"] == policy_name]
        
        if violation_type:
            filtered_violations = [v for v in filtered_violations if v["violation_type"] == violation_type]
        
        if start_time:
            filtered_violations = [v for v in filtered_violations if v["timestamp"] >= start_time]
        
        if end_time:
            filtered_violations = [v for v in filtered_violations if v["timestamp"] <= end_time]
        
        return filtered_violations


class ComplianceManager:
    """
    Manager for compliance policy enforcement.
    
    This class provides methods for enforcing compliance policies,
    validating operations against compliance rules, and managing
    compliance-related documentation.
    """
    
    def __init__(self):
        """Initialize a new ComplianceManager."""
        self.compliance_policies = {}
        self.compliance_validations = []
        self.compliance_reports = []
        self.custom_validators = {}
        
        logger.info("Initialized ComplianceManager")
    
    def register_compliance_policy(self, policy: CompliancePolicy) -> None:
        """
        Register a compliance policy.
        
        Args:
            policy: Compliance policy to register
        """
        self.compliance_policies[policy.name] = policy
        logger.info(f"Registered compliance policy: {policy.name}")
    
    def register_custom_validator(
        self,
        validator_name: str,
        validator_func: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """
        Register a custom compliance validator function.
        
        Args:
            validator_name: Name of the validator
            validator_func: Validator function that takes operation details and
                           policy rules, and returns validation result
        """
        self.custom_validators[validator_name] = validator_func
        logger.info(f"Registered custom validator: {validator_name}")
    
    def validate_operation(
        self,
        operation_type: str,
        operation_details: Dict[str, Any],
        policy_name: str,
        data_categories: List[str] = None
    ) -> Dict[str, Any]:
        """
        Validate an operation against a compliance policy.
        
        Args:
            operation_type: Type of operation
            operation_details: Details of the operation
            policy_name: Name of the compliance policy to check against
            data_categories: Categories of data involved in the operation
            
        Returns:
            Dictionary with validation result and details
        """
        if policy_name not in self.compliance_policies:
            logger.error(f"Compliance policy not found: {policy_name}")
            return {
                "valid": False,
                "reason": f"Compliance policy not found: {policy_name}",
                "violations": ["policy_not_found"]
            }
        
        policy = self.compliance_policies[policy_name]
        rules = policy.rules
        violations = []
        
        # Check if operation type is allowed
        if "allowed_operations" in rules and operation_type not in rules["allowed_operations"]:
            violations.append({
                "rule": "allowed_operations",
                "reason": f"Operation type not allowed: {operation_type}"
            })
        
        # Check data categories
        if data_categories and "data_category_rules" in rules:
            for category in data_categories:
                if category in rules["data_category_rules"]:
                    category_rules = rules["data_category_rules"][category]
                    
                    # Check if operation is allowed for this data category
                    if "allowed_operations" in category_rules and operation_type not in category_rules["allowed_operations"]:
                        violations.append({
                            "rule": f"data_category_rules.{category}.allowed_operations",
                            "reason": f"Operation {operation_type} not allowed for data category {category}"
                        })
        
        # Run custom validators
        for validator_name in policy.custom_validators:
            if validator_name in self.custom_validators:
                validator_func = self.custom_validators[validator_name]
                result = validator_func(operation_details, rules)
                
                if not result.get("valid", True):
                    violations.append({
                        "rule": f"custom_validator.{validator_name}",
                        "reason": result.get("reason", "Custom validation failed"),
                        "details": result.get("details", {})
                    })
        
        # Record validation
        validation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        validation = {
            "id": validation_id,
            "timestamp": timestamp,
            "operation_type": operation_type,
            "policy_name": policy_name,
            "data_categories": data_categories or [],
            "valid": len(violations) == 0,
            "violations": violations
        }
        
        self.compliance_validations.append(validation)
        
        if violations:
            logger.warning(f"Compliance validation failed with {len(violations)} violations")
            for v in violations:
                logger.warning(f"Violation: {v['rule']} - {v['reason']}")
        else:
            logger.info(f"Compliance validation passed for {operation_type}")
        
        return {
            "valid": len(violations) == 0,
            "validation_id": validation_id,
            "violations": violations
        }
    
    def generate_compliance_report(
        self,
        policy_name: str,
        start_time: str,
        end_time: str,
        report_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        Generate a compliance report for a specific policy.
        
        Args:
            policy_name: Name of the compliance policy
            start_time: Start time for the report period (ISO format)
            end_time: End time for the report period (ISO format)
            report_type: Type of report ("summary", "detailed", "violations")
            
        Returns:
            Dictionary containing the compliance report
        """
        if policy_name not in self.compliance_policies:
            logger.error(f"Compliance policy not found: {policy_name}")
            return {
                "error": f"Compliance policy not found: {policy_name}"
            }
        
        policy = self.compliance_policies[policy_name]
        
        # Filter validations for this policy and time period
        validations = [
            v for v in self.compliance_validations
            if v["policy_name"] == policy_name
            and v["timestamp"] >= start_time
            and v["timestamp"] <= end_time
        ]
        
        # Calculate statistics
        total_validations = len(validations)
        valid_validations = len([v for v in validations if v["valid"]])
        invalid_validations = total_validations - valid_validations
        
        compliance_rate = 1.0 if total_validations == 0 else valid_validations / total_validations
        
        # Group violations by rule
        violation_counts = {}
        for validation in validations:
            if not validation["valid"]:
                for violation in validation["violations"]:
                    rule = violation["rule"]
                    if rule not in violation_counts:
                        violation_counts[rule] = 0
                    violation_counts[rule] += 1
        
        # Create report
        report_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        report = {
            "id": report_id,
            "timestamp": timestamp,
            "policy_name": policy_name,
            "policy_standard": policy.standard.value,
            "policy_version": policy.version,
            "start_time": start_time,
            "end_time": end_time,
            "report_type": report_type,
            "statistics": {
                "total_validations": total_validations,
                "valid_validations": valid_validations,
                "invalid_validations": invalid_validations,
                "compliance_rate": compliance_rate
            },
            "violation_summary": violation_counts
        }
        
        # Add detailed information based on report type
        if report_type == "detailed":
            report["validations"] = validations
        elif report_type == "violations":
            report["violations"] = [v for v in validations if not v["valid"]]
        
        self.compliance_reports.append(report)
        logger.info(f"Generated compliance report: {report_id} for policy {policy_name}")
        
        return report


class AuditLogger:
    """
    Logger for audit records.
    
    This class provides methods for creating, storing, and retrieving
    audit records for workflow operations and security events.
    """
    
    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize a new AuditLogger.
        
        Args:
            storage_backend: Optional backend for storing audit records
        """
        self.storage_backend = storage_backend
        self.audit_records = []
        self.current_session_id = None
        
        logger.info("Initialized AuditLogger")
    
    def start_session(self) -> str:
        """
        Start a new audit session.
        
        Returns:
            ID of the new session
        """
        self.current_session_id = str(uuid.uuid4())
        logger.info(f"Started new audit session: {self.current_session_id}")
        return self.current_session_id
    
    def create_audit_record(
        self,
        entity_id: str,
        entity_type: str,
        action: str,
        actor_id: str,
        actor_type: str,
        status: str,
        details: Dict[str, Any],
        trust_score: float,
        confidence_score: float,
        execution_mode: str,
        data_categories: List[str],
        ip_address: Optional[str] = None,
        geo_location: Optional[str] = None,
        request_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> AuditRecord:
        """
        Create a new audit record.
        
        Args:
            entity_id: ID of the entity being acted upon
            entity_type: Type of the entity
            action: Action being performed
            actor_id: ID of the actor performing the action
            actor_type: Type of the actor
            status: Status of the action
            details: Details of the action
            trust_score: Trust score at the time of the action
            confidence_score: Confidence score at the time of the action
            execution_mode: Execution mode at the time of the action
            data_categories: Categories of data involved
            ip_address: Optional IP address
            geo_location: Optional geographic location
            request_id: Optional request ID
            parent_id: Optional parent audit record ID
            
        Returns:
            The created audit record
        """
        record_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Create a hash of the record for integrity verification
        hash_input = f"{record_id}|{timestamp}|{entity_id}|{action}|{actor_id}|{status}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()
        
        record = AuditRecord(
            id=record_id,
            timestamp=timestamp,
            entity_id=entity_id,
            entity_type=entity_type,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            status=status,
            details=details,
            trust_score=trust_score,
            confidence_score=confidence_score,
            execution_mode=execution_mode,
            data_categories=data_categories,
            ip_address=ip_address,
            geo_location=geo_location,
            session_id=self.current_session_id,
            request_id=request_id,
            parent_id=parent_id,
            hash_value=hash_value
        )
        
        self.audit_records.append(record)
        
        # Store in backend if available
        if self.storage_backend:
            self.storage_backend.store_audit_record(record)
        
        logger.info(f"Created audit record: {record_id} for {action} on {entity_id}")
        
        return record
    
    def get_audit_records(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        actor_id: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[AuditRecord]:
        """
        Get audit records matching the specified filters.
        
        Args:
            entity_id: Optional entity ID filter
            entity_type: Optional entity type filter
            action: Optional action filter
            actor_id: Optional actor ID filter
            status: Optional status filter
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            session_id: Optional session ID filter
            
        Returns:
            List of matching audit records
        """
        filtered_records = self.audit_records
        
        if entity_id:
            filtered_records = [r for r in filtered_records if r.entity_id == entity_id]
        
        if entity_type:
            filtered_records = [r for r in filtered_records if r.entity_type == entity_type]
        
        if action:
            filtered_records = [r for r in filtered_records if r.action == action]
        
        if actor_id:
            filtered_records = [r for r in filtered_records if r.actor_id == actor_id]
        
        if status:
            filtered_records = [r for r in filtered_records if r.status == status]
        
        if start_time:
            filtered_records = [r for r in filtered_records if r.timestamp >= start_time]
        
        if end_time:
            filtered_records = [r for r in filtered_records if r.timestamp <= end_time]
        
        if session_id:
            filtered_records = [r for r in filtered_records if r.session_id == session_id]
        
        return filtered_records
    
    def verify_record_integrity(self, record: AuditRecord) -> bool:
        """
        Verify the integrity of an audit record.
        
        Args:
            record: Audit record to verify
            
        Returns:
            True if the record's integrity is verified, False otherwise
        """
        hash_input = f"{record.id}|{record.timestamp}|{record.entity_id}|{record.action}|{record.actor_id}|{record.status}"
        computed_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        return computed_hash == record.hash_value


class EKISSecurityIntegration:
    """
    Integration with EKIS security framework.
    
    This class provides methods for integrating with the EKIS security
    framework, including authentication, authorization, and secure
    communication.
    """
    
    def __init__(self, ekis_config: Dict[str, Any]):
        """
        Initialize a new EKIS security integration.
        
        Args:
            ekis_config: Configuration for EKIS integration
        """
        self.ekis_config = ekis_config
        self.ekis_client = None
        self.security_context = {}
        self.token_cache = {}
        
        logger.info("Initialized EKIS Security Integration")
    
    def initialize(self) -> bool:
        """
        Initialize the EKIS client.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # In a real implementation, this would initialize the actual EKIS client
            # For now, we'll just simulate it
            self.ekis_client = {
                "initialized": True,
                "version": "1.0.0",
                "capabilities": ["authentication", "authorization", "encryption", "key_management"]
            }
            
            self.security_context = {
                "session_id": str(uuid.uuid4()),
                "initialized_at": datetime.now().isoformat(),
                "security_level": self.ekis_config.get("security_level", "standard")
            }
            
            logger.info("EKIS client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize EKIS client: {str(e)}")
            return False
    
    def authenticate(
        self,
        entity_id: str,
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Authenticate an entity with EKIS.
        
        Args:
            entity_id: ID of the entity to authenticate
            credentials: Authentication credentials
            
        Returns:
            Authentication result with token if successful
        """
        if not self.ekis_client:
            logger.error("EKIS client not initialized")
            return {
                "authenticated": False,
                "reason": "EKIS client not initialized"
            }
        
        # In a real implementation, this would call the EKIS authentication service
        # For now, we'll just simulate it
        
        # Simulate authentication logic
        is_authenticated = True  # In a real implementation, this would be based on actual authentication
        
        if is_authenticated:
            token = str(uuid.uuid4())
            expiration = int(time.time()) + 3600  # 1 hour from now
            
            self.token_cache[token] = {
                "entity_id": entity_id,
                "expiration": expiration,
                "security_context": {
                    "roles": credentials.get("roles", []),
                    "permissions": credentials.get("permissions", []),
                    "security_level": credentials.get("security_level", "standard")
                }
            }
            
            logger.info(f"Entity {entity_id} authenticated successfully")
            
            return {
                "authenticated": True,
                "token": token,
                "expiration": expiration,
                "security_context": self.token_cache[token]["security_context"]
            }
        else:
            logger.warning(f"Authentication failed for entity {entity_id}")
            
            return {
                "authenticated": False,
                "reason": "Invalid credentials"
            }
    
    def authorize(
        self,
        token: str,
        resource: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Authorize an action on a resource.
        
        Args:
            token: Authentication token
            resource: Resource to access
            action: Action to perform
            
        Returns:
            Authorization result
        """
        if not self.ekis_client:
            logger.error("EKIS client not initialized")
            return {
                "authorized": False,
                "reason": "EKIS client not initialized"
            }
        
        # Check if token is valid
        if token not in self.token_cache:
            logger.warning(f"Invalid token: {token}")
            return {
                "authorized": False,
                "reason": "Invalid token"
            }
        
        token_data = self.token_cache[token]
        
        # Check if token is expired
        if token_data["expiration"] < int(time.time()):
            logger.warning(f"Expired token: {token}")
            return {
                "authorized": False,
                "reason": "Expired token"
            }
        
        # In a real implementation, this would call the EKIS authorization service
        # For now, we'll just simulate it
        
        # Simulate authorization logic
        security_context = token_data["security_context"]
        permissions = security_context.get("permissions", [])
        
        # Check if the entity has the required permission
        required_permission = f"{resource}:{action}"
        is_authorized = required_permission in permissions or "*:*" in permissions
        
        if is_authorized:
            logger.info(f"Entity {token_data['entity_id']} authorized for {required_permission}")
            
            return {
                "authorized": True,
                "entity_id": token_data["entity_id"],
                "resource": resource,
                "action": action
            }
        else:
            logger.warning(f"Authorization failed for {token_data['entity_id']} on {required_permission}")
            
            return {
                "authorized": False,
                "reason": f"Missing required permission: {required_permission}"
            }
    
    def encrypt_data(
        self,
        data: Any,
        security_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        Encrypt data using EKIS.
        
        Args:
            data: Data to encrypt
            security_level: Security level for encryption
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        if not self.ekis_client:
            logger.error("EKIS client not initialized")
            return {
                "success": False,
                "reason": "EKIS client not initialized"
            }
        
        # In a real implementation, this would call the EKIS encryption service
        # For now, we'll just simulate it
        
        # Simulate encryption
        encrypted_data = f"ENCRYPTED_{data}_WITH_{security_level}_SECURITY"
        encryption_id = str(uuid.uuid4())
        
        logger.info(f"Data encrypted with {security_level} security")
        
        return {
            "success": True,
            "encrypted_data": encrypted_data,
            "encryption_id": encryption_id,
            "security_level": security_level,
            "timestamp": datetime.now().isoformat()
        }
    
    def decrypt_data(
        self,
        encrypted_data: str,
        encryption_id: str
    ) -> Dict[str, Any]:
        """
        Decrypt data using EKIS.
        
        Args:
            encrypted_data: Encrypted data
            encryption_id: ID of the encryption
            
        Returns:
            Dictionary with decrypted data and metadata
        """
        if not self.ekis_client:
            logger.error("EKIS client not initialized")
            return {
                "success": False,
                "reason": "EKIS client not initialized"
            }
        
        # In a real implementation, this would call the EKIS decryption service
        # For now, we'll just simulate it
        
        # Simulate decryption
        if encrypted_data.startswith("ENCRYPTED_") and "_WITH_" in encrypted_data:
            parts = encrypted_data.split("_WITH_")
            data = parts[0].replace("ENCRYPTED_", "")
            
            logger.info(f"Data decrypted successfully")
            
            return {
                "success": True,
                "decrypted_data": data,
                "encryption_id": encryption_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.warning("Failed to decrypt data: invalid format")
            
            return {
                "success": False,
                "reason": "Invalid encrypted data format"
            }


class ObservabilityManager:
    """
    Manager for workflow observability.
    
    This class provides methods for instrumenting workflows with
    observability features, collecting metrics, and generating
    observability reports.
    """
    
    def __init__(self):
        """Initialize a new ObservabilityManager."""
        self.metrics = {}
        self.traces = {}
        self.spans = {}
        self.logs = []
        self.alerts = []
        self.dashboards = {}
        
        logger.info("Initialized ObservabilityManager")
    
    def register_metric(
        self,
        name: str,
        description: str,
        metric_type: str,
        unit: str,
        labels: List[str] = None
    ) -> None:
        """
        Register a new metric.
        
        Args:
            name: Name of the metric
            description: Description of the metric
            metric_type: Type of metric (counter, gauge, histogram, summary)
            unit: Unit of measurement
            labels: Optional list of label names for the metric
        """
        self.metrics[name] = {
            "name": name,
            "description": description,
            "type": metric_type,
            "unit": unit,
            "labels": labels or [],
            "values": []
        }
        
        logger.info(f"Registered metric: {name}")
    
    def record_metric(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] = None,
        timestamp: Optional[str] = None
    ) -> None:
        """
        Record a metric value.
        
        Args:
            name: Name of the metric
            value: Value to record
            labels: Optional labels for this metric value
            timestamp: Optional timestamp (ISO format)
        """
        if name not in self.metrics:
            logger.warning(f"Metric not registered: {name}")
            return
        
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        self.metrics[name]["values"].append({
            "value": value,
            "labels": labels or {},
            "timestamp": timestamp
        })
        
        logger.debug(f"Recorded metric {name}: {value}")
    
    def start_trace(
        self,
        name: str,
        trace_type: str,
        entity_id: str,
        attributes: Dict[str, Any] = None
    ) -> str:
        """
        Start a new trace.
        
        Args:
            name: Name of the trace
            trace_type: Type of trace
            entity_id: ID of the entity being traced
            attributes: Optional attributes for the trace
            
        Returns:
            ID of the new trace
        """
        trace_id = str(uuid.uuid4())
        start_time = datetime.now().isoformat()
        
        self.traces[trace_id] = {
            "id": trace_id,
            "name": name,
            "type": trace_type,
            "entity_id": entity_id,
            "attributes": attributes or {},
            "start_time": start_time,
            "end_time": None,
            "status": "active",
            "spans": []
        }
        
        logger.info(f"Started trace {trace_id}: {name}")
        
        return trace_id
    
    def end_trace(
        self,
        trace_id: str,
        status: str = "completed",
        result: Dict[str, Any] = None
    ) -> None:
        """
        End a trace.
        
        Args:
            trace_id: ID of the trace to end
            status: Final status of the trace
            result: Optional result data
        """
        if trace_id not in self.traces:
            logger.warning(f"Trace not found: {trace_id}")
            return
        
        end_time = datetime.now().isoformat()
        
        self.traces[trace_id]["end_time"] = end_time
        self.traces[trace_id]["status"] = status
        
        if result:
            self.traces[trace_id]["result"] = result
        
        logger.info(f"Ended trace {trace_id} with status {status}")
    
    def start_span(
        self,
        trace_id: str,
        name: str,
        attributes: Dict[str, Any] = None,
        parent_span_id: Optional[str] = None
    ) -> str:
        """
        Start a new span within a trace.
        
        Args:
            trace_id: ID of the parent trace
            name: Name of the span
            attributes: Optional attributes for the span
            parent_span_id: Optional ID of the parent span
            
        Returns:
            ID of the new span
        """
        if trace_id not in self.traces:
            logger.warning(f"Trace not found: {trace_id}")
            return None
        
        span_id = str(uuid.uuid4())
        start_time = datetime.now().isoformat()
        
        span = {
            "id": span_id,
            "trace_id": trace_id,
            "name": name,
            "attributes": attributes or {},
            "start_time": start_time,
            "end_time": None,
            "status": "active",
            "parent_span_id": parent_span_id,
            "events": []
        }
        
        self.spans[span_id] = span
        self.traces[trace_id]["spans"].append(span_id)
        
        logger.debug(f"Started span {span_id}: {name} in trace {trace_id}")
        
        return span_id
    
    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        result: Dict[str, Any] = None
    ) -> None:
        """
        End a span.
        
        Args:
            span_id: ID of the span to end
            status: Final status of the span
            result: Optional result data
        """
        if span_id not in self.spans:
            logger.warning(f"Span not found: {span_id}")
            return
        
        end_time = datetime.now().isoformat()
        
        self.spans[span_id]["end_time"] = end_time
        self.spans[span_id]["status"] = status
        
        if result:
            self.spans[span_id]["result"] = result
        
        logger.debug(f"Ended span {span_id} with status {status}")
    
    def add_span_event(
        self,
        span_id: str,
        name: str,
        attributes: Dict[str, Any] = None
    ) -> None:
        """
        Add an event to a span.
        
        Args:
            span_id: ID of the span
            name: Name of the event
            attributes: Optional attributes for the event
        """
        if span_id not in self.spans:
            logger.warning(f"Span not found: {span_id}")
            return
        
        timestamp = datetime.now().isoformat()
        
        event = {
            "name": name,
            "timestamp": timestamp,
            "attributes": attributes or {}
        }
        
        self.spans[span_id]["events"].append(event)
        
        logger.debug(f"Added event {name} to span {span_id}")
    
    def log_message(
        self,
        level: str,
        message: str,
        context: Dict[str, Any] = None,
        entity_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None
    ) -> None:
        """
        Log a message with observability context.
        
        Args:
            level: Log level
            message: Log message
            context: Optional additional context
            entity_id: Optional entity ID
            trace_id: Optional trace ID
            span_id: Optional span ID
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "context": context or {},
            "entity_id": entity_id,
            "trace_id": trace_id,
            "span_id": span_id
        }
        
        self.logs.append(log_entry)
        
        # Also log to the standard logger
        if level == "debug":
            logger.debug(message)
        elif level == "info":
            logger.info(message)
        elif level == "warning":
            logger.warning(message)
        elif level == "error":
            logger.error(message)
        elif level == "critical":
            logger.critical(message)
    
    def create_alert(
        self,
        name: str,
        severity: str,
        message: str,
        entity_id: Optional[str] = None,
        context: Dict[str, Any] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Create an observability alert.
        
        Args:
            name: Name of the alert
            severity: Severity level
            message: Alert message
            entity_id: Optional entity ID
            context: Optional additional context
            trace_id: Optional trace ID
            
        Returns:
            ID of the new alert
        """
        alert_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        alert = {
            "id": alert_id,
            "name": name,
            "severity": severity,
            "message": message,
            "timestamp": timestamp,
            "entity_id": entity_id,
            "context": context or {},
            "trace_id": trace_id,
            "status": "active",
            "resolved_at": None,
            "resolution": None
        }
        
        self.alerts.append(alert)
        
        logger.warning(f"Created alert {alert_id}: {name} - {message}")
        
        return alert_id
    
    def resolve_alert(
        self,
        alert_id: str,
        resolution: str
    ) -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: ID of the alert to resolve
            resolution: Resolution message
            
        Returns:
            True if the alert was resolved, False otherwise
        """
        for alert in self.alerts:
            if alert["id"] == alert_id and alert["status"] == "active":
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.now().isoformat()
                alert["resolution"] = resolution
                
                logger.info(f"Resolved alert {alert_id}: {resolution}")
                return True
        
        logger.warning(f"Alert not found or already resolved: {alert_id}")
        return False
    
    def register_dashboard(
        self,
        name: str,
        description: str,
        panels: List[Dict[str, Any]]
    ) -> str:
        """
        Register an observability dashboard.
        
        Args:
            name: Name of the dashboard
            description: Description of the dashboard
            panels: List of dashboard panels
            
        Returns:
            ID of the new dashboard
        """
        dashboard_id = str(uuid.uuid4())
        
        self.dashboards[dashboard_id] = {
            "id": dashboard_id,
            "name": name,
            "description": description,
            "panels": panels,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Registered dashboard {dashboard_id}: {name}")
        
        return dashboard_id
    
    def get_metrics(
        self,
        name: Optional[str] = None,
        metric_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Get metrics matching the specified filters.
        
        Args:
            name: Optional metric name filter
            metric_type: Optional metric type filter
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            labels: Optional labels filter
            
        Returns:
            Dictionary of matching metrics
        """
        filtered_metrics = {}
        
        for metric_name, metric in self.metrics.items():
            if name and metric_name != name:
                continue
            
            if metric_type and metric["type"] != metric_type:
                continue
            
            # Filter values by time range and labels
            filtered_values = metric["values"]
            
            if start_time:
                filtered_values = [v for v in filtered_values if v["timestamp"] >= start_time]
            
            if end_time:
                filtered_values = [v for v in filtered_values if v["timestamp"] <= end_time]
            
            if labels:
                filtered_values = [
                    v for v in filtered_values
                    if all(k in v["labels"] and v["labels"][k] == labels[k] for k in labels)
                ]
            
            # Include the metric if it has matching values
            if filtered_values:
                filtered_metrics[metric_name] = {
                    **metric,
                    "values": filtered_values
                }
        
        return filtered_metrics
    
    def get_traces(
        self,
        trace_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        trace_type: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get traces matching the specified filters.
        
        Args:
            trace_id: Optional trace ID filter
            entity_id: Optional entity ID filter
            trace_type: Optional trace type filter
            status: Optional status filter
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            
        Returns:
            Dictionary of matching traces
        """
        filtered_traces = {}
        
        for tid, trace in self.traces.items():
            if trace_id and tid != trace_id:
                continue
            
            if entity_id and trace["entity_id"] != entity_id:
                continue
            
            if trace_type and trace["type"] != trace_type:
                continue
            
            if status and trace["status"] != status:
                continue
            
            if start_time and trace["start_time"] < start_time:
                continue
            
            if end_time and (not trace["end_time"] or trace["end_time"] > end_time):
                continue
            
            # Include the trace and its spans
            trace_copy = dict(trace)
            trace_copy["spans"] = [self.spans[span_id] for span_id in trace["spans"] if span_id in self.spans]
            filtered_traces[tid] = trace_copy
        
        return filtered_traces
    
    def get_alerts(
        self,
        alert_id: Optional[str] = None,
        name: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        entity_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get alerts matching the specified filters.
        
        Args:
            alert_id: Optional alert ID filter
            name: Optional alert name filter
            severity: Optional severity filter
            status: Optional status filter
            entity_id: Optional entity ID filter
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            
        Returns:
            List of matching alerts
        """
        filtered_alerts = self.alerts
        
        if alert_id:
            filtered_alerts = [a for a in filtered_alerts if a["id"] == alert_id]
        
        if name:
            filtered_alerts = [a for a in filtered_alerts if a["name"] == name]
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a["severity"] == severity]
        
        if status:
            filtered_alerts = [a for a in filtered_alerts if a["status"] == status]
        
        if entity_id:
            filtered_alerts = [a for a in filtered_alerts if a["entity_id"] == entity_id]
        
        if start_time:
            filtered_alerts = [a for a in filtered_alerts if a["timestamp"] >= start_time]
        
        if end_time:
            filtered_alerts = [a for a in filtered_alerts if a["timestamp"] <= end_time]
        
        return filtered_alerts


# Example usage
if __name__ == "__main__":
    # Create a trust-aware security manager
    security_manager = TrustAwareSecurityManager()
    
    # Register a trust policy
    policy = TrustPolicy(
        name="standard_workflow",
        description="Standard policy for workflow execution",
        min_trust_score=0.7,
        min_confidence_score=0.8,
        requires_human_oversight=True,
        security_level=SecurityLevel.MEDIUM,
        allowed_execution_modes=["reactive", "proactive"],
        restricted_data_categories=["pii", "financial"],
        restricted_operations=["delete", "modify_system"]
    )
    security_manager.register_trust_policy(policy)
    
    # Update entity scores
    security_manager.update_entity_scores(
        entity_id="workflow-001",
        trust_score=0.85,
        confidence_score=0.92,
        execution_mode="proactive"
    )
    
    # Check execution permission
    permission = security_manager.check_execution_permission(
        entity_id="workflow-001",
        policy_name="standard_workflow",
        operation="read",
        data_categories=["operational", "metrics"]
    )
    print(f"Permission result: {permission}")
    
    # Create a compliance manager
    compliance_manager = ComplianceManager()
    
    # Register a compliance policy
    compliance_policy = CompliancePolicy(
        name="data_privacy",
        description="Data privacy compliance policy",
        standard=ComplianceStandard.GDPR,
        version="1.0",
        rules={
            "allowed_operations": ["read", "analyze", "report"],
            "data_category_rules": {
                "pii": {
                    "allowed_operations": ["read"],
                    "retention_days": 30,
                    "requires_consent": True
                }
            }
        },
        data_retention_days=90,
        data_categories=["pii", "operational", "metrics"],
        required_approvals=["data_officer"]
    )
    compliance_manager.register_compliance_policy(compliance_policy)
    
    # Validate an operation
    validation = compliance_manager.validate_operation(
        operation_type="analyze",
        operation_details={"purpose": "performance_optimization"},
        policy_name="data_privacy",
        data_categories=["operational", "metrics"]
    )
    print(f"Validation result: {validation}")
    
    # Create an audit logger
    audit_logger = AuditLogger()
    
    # Start an audit session
    session_id = audit_logger.start_session()
    
    # Create an audit record
    record = audit_logger.create_audit_record(
        entity_id="workflow-001",
        entity_type="workflow",
        action="execute",
        actor_id="system",
        actor_type="system",
        status="success",
        details={"duration_ms": 1500},
        trust_score=0.85,
        confidence_score=0.92,
        execution_mode="proactive",
        data_categories=["operational", "metrics"]
    )
    print(f"Audit record created: {record.id}")
    
    # Create an observability manager
    observability = ObservabilityManager()
    
    # Register a metric
    observability.register_metric(
        name="workflow_execution_time",
        description="Time taken to execute a workflow",
        metric_type="histogram",
        unit="milliseconds",
        labels=["workflow_id", "execution_mode"]
    )
    
    # Record a metric value
    observability.record_metric(
        name="workflow_execution_time",
        value=1500,
        labels={"workflow_id": "workflow-001", "execution_mode": "proactive"}
    )
    
    # Start a trace
    trace_id = observability.start_trace(
        name="workflow_execution",
        trace_type="workflow",
        entity_id="workflow-001",
        attributes={"execution_mode": "proactive"}
    )
    
    # Start a span
    span_id = observability.start_span(
        trace_id=trace_id,
        name="task_execution",
        attributes={"task_id": "task-001"}
    )
    
    # Add a span event
    observability.add_span_event(
        span_id=span_id,
        name="subtask_completed",
        attributes={"subtask_id": "subtask-001"}
    )
    
    # End the span
    observability.end_span(
        span_id=span_id,
        status="completed",
        result={"output": "task_result"}
    )
    
    # End the trace
    observability.end_trace(
        trace_id=trace_id,
        status="completed",
        result={"workflow_output": "success"}
    )
    
    # Create an alert
    alert_id = observability.create_alert(
        name="high_execution_time",
        severity="warning",
        message="Workflow execution time exceeded threshold",
        entity_id="workflow-001",
        context={"execution_time_ms": 1500, "threshold_ms": 1000}
    )
    
    # Resolve the alert
    observability.resolve_alert(
        alert_id=alert_id,
        resolution="Optimized workflow execution"
    )
