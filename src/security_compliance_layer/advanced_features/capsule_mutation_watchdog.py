"""
Capsule Mutation Watchdog Module for the Security & Compliance Layer

This module implements the Capsule Mutation Watchdog feature, which monitors how, when, 
and why capsules evolve, providing security oversight for capsule mutations and lifecycle events.

Key features:
1. Mutation tracking and verification
2. Anomalous mutation detection
3. Mutation policy enforcement
4. Mutation audit trails

Dependencies:
- core.capsule_framework.capsule_lifecycle_manager
- core.policy_governance.policy_enforcement_engine
- advanced_features.ai_security_co_orchestration
- core.audit_traceability.audit_trail_manager

Author: Industriverse Security Team
"""

import logging
import uuid
import time
import json
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class MutationType(Enum):
    """Enumeration of capsule mutation types"""
    CODE_CHANGE = "code_change"
    CONFIGURATION_CHANGE = "configuration_change"
    PERMISSION_CHANGE = "permission_change"
    DEPENDENCY_CHANGE = "dependency_change"
    STATE_CHANGE = "state_change"
    LIFECYCLE_EVENT = "lifecycle_event"
    INTEGRATION_CHANGE = "integration_change"
    POLICY_CHANGE = "policy_change"

class MutationSeverity(Enum):
    """Enumeration of mutation severity levels"""
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CapsuleMutationWatchdog:
    """
    Capsule Mutation Watchdog for the Security & Compliance Layer
    
    This class implements monitoring and security oversight for capsule mutations
    and lifecycle events, providing visibility into how, when, and why capsules evolve.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Capsule Mutation Watchdog
        
        Args:
            config: Configuration dictionary for the Capsule Mutation Watchdog
        """
        self.config = config or {}
        self.mutation_registry = {}  # Maps mutation_id to mutation details
        self.capsule_registry = {}  # Maps capsule_id to capsule mutation history
        self.policy_registry = {}  # Maps policy_id to mutation policies
        self.anomaly_registry = {}  # Maps anomaly_id to detected anomalies
        
        # Default mutation policies
        self.default_policies = self.config.get("default_policies", {
            "require_approval_for_critical": True,
            "block_unsigned_mutations": False,
            "max_mutations_per_day": 50,
            "require_reason_for_changes": True,
            "require_verification_for_permission_changes": True
        })
        
        # Dependencies (will be set via dependency injection)
        self.capsule_lifecycle_manager = None
        self.policy_enforcement_engine = None
        self.ai_security_co_orchestration = None
        self.audit_trail_manager = None
        
        logger.info("Capsule Mutation Watchdog initialized")
    
    def set_dependencies(self, capsule_lifecycle_manager=None, policy_enforcement_engine=None,
                        ai_security_co_orchestration=None, audit_trail_manager=None):
        """
        Set dependencies for the Capsule Mutation Watchdog
        
        Args:
            capsule_lifecycle_manager: Capsule Lifecycle Manager instance
            policy_enforcement_engine: Policy Enforcement Engine instance
            ai_security_co_orchestration: AI-Security Co-Orchestration instance
            audit_trail_manager: Audit Trail Manager instance
        """
        self.capsule_lifecycle_manager = capsule_lifecycle_manager
        self.policy_enforcement_engine = policy_enforcement_engine
        self.ai_security_co_orchestration = ai_security_co_orchestration
        self.audit_trail_manager = audit_trail_manager
        logger.info("Capsule Mutation Watchdog dependencies set")
    
    def register_capsule(self, capsule_id: str, capsule_metadata: Dict[str, Any],
                        initial_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a capsule for mutation monitoring
        
        Args:
            capsule_id: Unique identifier for the capsule
            capsule_metadata: Metadata about the capsule
            initial_state: Initial state of the capsule
            
        Returns:
            Registration details
        """
        # Create capsule record if not exists
        if capsule_id not in self.capsule_registry:
            capsule_record = {
                "capsule_id": capsule_id,
                "metadata": capsule_metadata,
                "initial_state": initial_state,
                "current_state": initial_state,
                "mutation_history": [],
                "anomaly_history": [],
                "registration_date": datetime.utcnow().isoformat(),
                "last_mutation_date": None,
                "mutation_count": 0,
                "status": "active"
            }
            self.capsule_registry[capsule_id] = capsule_record
            
            # Create initial state mutation record
            if initial_state:
                self.record_mutation(
                    capsule_id=capsule_id,
                    mutation_type=MutationType.LIFECYCLE_EVENT,
                    mutation_data={
                        "event": "registration",
                        "initial_state": initial_state
                    },
                    reason="Initial capsule registration",
                    actor_id=capsule_metadata.get("creator_id", "system")
                )
            
            logger.info(f"Registered capsule for mutation monitoring: {capsule_id}")
            return capsule_record
        else:
            # Update existing capsule record
            capsule_record = self.capsule_registry[capsule_id]
            capsule_record["metadata"] = capsule_metadata
            capsule_record["status"] = "active"
            
            logger.info(f"Updated existing capsule registration: {capsule_id}")
            return capsule_record
    
    def record_mutation(self, capsule_id: str, mutation_type: MutationType,
                       mutation_data: Dict[str, Any], reason: str = None,
                       actor_id: str = None, signature: str = None) -> Dict[str, Any]:
        """
        Record a capsule mutation
        
        Args:
            capsule_id: Unique identifier for the capsule
            mutation_type: Type of mutation
            mutation_data: Data describing the mutation
            reason: Reason for the mutation
            actor_id: Identifier of the actor performing the mutation
            signature: Digital signature of the mutation
            
        Returns:
            Mutation record
        """
        if capsule_id not in self.capsule_registry:
            raise ValueError(f"Capsule not registered: {capsule_id}")
        
        capsule_record = self.capsule_registry[capsule_id]
        
        # Verify mutation against policies
        policy_check = self._check_mutation_policies(
            capsule_id=capsule_id,
            mutation_type=mutation_type,
            mutation_data=mutation_data,
            actor_id=actor_id,
            signature=signature
        )
        
        if not policy_check["allowed"]:
            raise ValueError(f"Mutation policy violation: {policy_check['reason']}")
        
        # Create mutation record
        mutation_id = str(uuid.uuid4())
        mutation_record = {
            "mutation_id": mutation_id,
            "capsule_id": capsule_id,
            "mutation_type": mutation_type.value,
            "mutation_data": mutation_data,
            "reason": reason,
            "actor_id": actor_id,
            "signature": signature,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": self._calculate_mutation_severity(mutation_type, mutation_data),
            "verified": signature is not None,
            "policy_checks": policy_check
        }
        self.mutation_registry[mutation_id] = mutation_record
        
        # Update capsule record
        capsule_record["mutation_history"].append(mutation_id)
        capsule_record["last_mutation_date"] = mutation_record["timestamp"]
        capsule_record["mutation_count"] += 1
        
        # Update capsule state if provided in mutation data
        if "new_state" in mutation_data:
            capsule_record["current_state"] = mutation_data["new_state"]
        
        # Check for anomalies
        anomaly_check = self._check_for_anomalies(
            capsule_id=capsule_id,
            mutation_record=mutation_record
        )
        
        if anomaly_check["anomalies_detected"]:
            for anomaly in anomaly_check["anomalies"]:
                capsule_record["anomaly_history"].append(anomaly["anomaly_id"])
        
        # Create audit trail if audit manager is available
        if self.audit_trail_manager:
            self.audit_trail_manager.create_audit_record(
                event_type="capsule_mutation",
                resource_id=capsule_id,
                action=mutation_type.value,
                actor_id=actor_id,
                details={
                    "mutation_id": mutation_id,
                    "mutation_data": mutation_data,
                    "reason": reason,
                    "severity": mutation_record["severity"]
                }
            )
        
        logger.info(f"Recorded mutation {mutation_id} for capsule {capsule_id}: {mutation_type.value}")
        return mutation_record
    
    def verify_mutation(self, mutation_id: str, 
                       verification_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Verify a capsule mutation
        
        Args:
            mutation_id: Unique identifier for the mutation
            verification_data: Data for verification
            
        Returns:
            Verification result
        """
        if mutation_id not in self.mutation_registry:
            raise ValueError(f"Mutation not found: {mutation_id}")
        
        mutation_record = self.mutation_registry[mutation_id]
        
        # Perform verification
        verification_result = {
            "mutation_id": mutation_id,
            "verified": False,
            "verification_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Verify signature if present
        if mutation_record["signature"]:
            # In a real implementation, this would verify the cryptographic signature
            # For this implementation, we'll simulate successful verification
            verification_result["verified"] = True
            verification_result["signature_verification"] = "valid"
        else:
            verification_result["reason"] = "No signature provided"
            verification_result["signature_verification"] = "missing"
        
        # Additional verification logic based on mutation type
        mutation_type = MutationType(mutation_record["mutation_type"])
        
        if mutation_type == MutationType.PERMISSION_CHANGE:
            # For permission changes, verify authorization
            if verification_data and "authorization_proof" in verification_data:
                # In a real implementation, this would verify the authorization proof
                verification_result["authorization_verification"] = "valid"
            else:
                verification_result["verified"] = False
                verification_result["reason"] = "Missing authorization proof for permission change"
                verification_result["authorization_verification"] = "missing"
        
        # Update mutation record with verification result
        mutation_record["verified"] = verification_result["verified"]
        mutation_record["verification"] = {
            "verification_id": verification_result["verification_id"],
            "timestamp": verification_result["timestamp"],
            "result": verification_result["verified"],
            "details": {k: v for k, v in verification_result.items() 
                       if k not in ["mutation_id", "verified", "verification_id", "timestamp"]}
        }
        
        logger.info(f"Verified mutation {mutation_id}, result: {verification_result['verified']}")
        return verification_result
    
    def get_mutation_history(self, capsule_id: str, 
                            mutation_types: List[MutationType] = None,
                            start_time: str = None,
                            end_time: str = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get mutation history for a capsule
        
        Args:
            capsule_id: Unique identifier for the capsule
            mutation_types: List of mutation types to filter (optional)
            start_time: Start time for filtering (ISO format, optional)
            end_time: End time for filtering (ISO format, optional)
            limit: Maximum number of mutations to return
            
        Returns:
            List of mutation records
        """
        if capsule_id not in self.capsule_registry:
            raise ValueError(f"Capsule not registered: {capsule_id}")
        
        capsule_record = self.capsule_registry[capsule_id]
        mutation_ids = capsule_record["mutation_history"]
        
        # Get mutation records
        mutations = [self.mutation_registry[mid] for mid in mutation_ids if mid in self.mutation_registry]
        
        # Apply filters
        if mutation_types:
            mutation_type_values = [mt.value for mt in mutation_types]
            mutations = [m for m in mutations if m["mutation_type"] in mutation_type_values]
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
            mutations = [m for m in mutations if datetime.fromisoformat(m["timestamp"]) >= start_dt]
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
            mutations = [m for m in mutations if datetime.fromisoformat(m["timestamp"]) <= end_dt]
        
        # Sort by timestamp (newest first)
        mutations.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        return mutations[:limit]
    
    def get_anomaly_history(self, capsule_id: str,
                           start_time: str = None,
                           end_time: str = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get anomaly history for a capsule
        
        Args:
            capsule_id: Unique identifier for the capsule
            start_time: Start time for filtering (ISO format, optional)
            end_time: End time for filtering (ISO format, optional)
            limit: Maximum number of anomalies to return
            
        Returns:
            List of anomaly records
        """
        if capsule_id not in self.capsule_registry:
            raise ValueError(f"Capsule not registered: {capsule_id}")
        
        capsule_record = self.capsule_registry[capsule_id]
        anomaly_ids = capsule_record["anomaly_history"]
        
        # Get anomaly records
        anomalies = [self.anomaly_registry[aid] for aid in anomaly_ids if aid in self.anomaly_registry]
        
        # Apply filters
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
            anomalies = [a for a in anomalies if datetime.fromisoformat(a["detection_time"]) >= start_dt]
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
            anomalies = [a for a in anomalies if datetime.fromisoformat(a["detection_time"]) <= end_dt]
        
        # Sort by detection time (newest first)
        anomalies.sort(key=lambda a: a["detection_time"], reverse=True)
        
        # Apply limit
        return anomalies[:limit]
    
    def create_mutation_policy(self, policy_name: str, policy_rules: Dict[str, Any],
                              target_capsules: List[str] = None,
                              target_mutation_types: List[MutationType] = None) -> Dict[str, Any]:
        """
        Create a mutation policy
        
        Args:
            policy_name: Name of the policy
            policy_rules: Rules for the policy
            target_capsules: List of capsule IDs the policy applies to (optional)
            target_mutation_types: List of mutation types the policy applies to (optional)
            
        Returns:
            Policy details
        """
        policy_id = str(uuid.uuid4())
        
        # Create policy
        policy = {
            "policy_id": policy_id,
            "policy_name": policy_name,
            "policy_rules": policy_rules,
            "target_capsules": target_capsules,
            "target_mutation_types": [mt.value for mt in target_mutation_types] if target_mutation_types else None,
            "creation_date": datetime.utcnow().isoformat(),
            "status": "active"
        }
        self.policy_registry[policy_id] = policy
        
        logger.info(f"Created mutation policy: {policy_name} (ID: {policy_id})")
        return policy
    
    def update_mutation_policy(self, policy_id: str, 
                              updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a mutation policy
        
        Args:
            policy_id: Unique identifier for the policy
            updates: Updates to apply to the policy
            
        Returns:
            Updated policy details
        """
        if policy_id not in self.policy_registry:
            raise ValueError(f"Policy not found: {policy_id}")
        
        policy = self.policy_registry[policy_id]
        
        # Apply updates
        for key, value in updates.items():
            if key in ["policy_name", "policy_rules", "target_capsules", "target_mutation_types", "status"]:
                policy[key] = value
        
        policy["last_updated"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated mutation policy: {policy['policy_name']} (ID: {policy_id})")
        return policy
    
    def get_capsule_mutation_analytics(self, capsule_id: str) -> Dict[str, Any]:
        """
        Get mutation analytics for a capsule
        
        Args:
            capsule_id: Unique identifier for the capsule
            
        Returns:
            Capsule mutation analytics
        """
        if capsule_id not in self.capsule_registry:
            raise ValueError(f"Capsule not registered: {capsule_id}")
        
        capsule_record = self.capsule_registry[capsule_id]
        mutation_ids = capsule_record["mutation_history"]
        
        # Get mutation records
        mutations = [self.mutation_registry[mid] for mid in mutation_ids if mid in self.mutation_registry]
        
        # Mutation type distribution
        mutation_type_counts = {}
        for mutation_type in MutationType:
            mutation_type_counts[mutation_type.value] = len([m for m in mutations if m["mutation_type"] == mutation_type.value])
        
        # Severity distribution
        severity_counts = {}
        for severity in MutationSeverity:
            severity_counts[severity.value] = len([m for m in mutations if m["severity"] == severity.value])
        
        # Actor distribution
        actor_counts = {}
        for mutation in mutations:
            actor_id = mutation.get("actor_id")
            if actor_id:
                actor_counts[actor_id] = actor_counts.get(actor_id, 0) + 1
        
        # Time-based analysis
        current_time = datetime.utcnow()
        last_day_count = len([m for m in mutations if 
                             (current_time - datetime.fromisoformat(m["timestamp"])).days <= 1])
        last_week_count = len([m for m in mutations if 
                              (current_time - datetime.fromisoformat(m["timestamp"])).days <= 7])
        last_month_count = len([m for m in mutations if 
                               (current_time - datetime.fromisoformat(m["timestamp"])).days <= 30])
        
        # Verification status
        verified_count = len([m for m in mutations if m.get("verified", False)])
        unverified_count = len(mutations) - verified_count
        
        # Anomaly statistics
        anomaly_ids = capsule_record["anomaly_history"]
        anomalies = [self.anomaly_registry[aid] for aid in anomaly_ids if aid in self.anomaly_registry]
        
        return {
            "capsule_id": capsule_id,
            "total_mutations": len(mutations),
            "mutation_type_distribution": mutation_type_counts,
            "severity_distribution": severity_counts,
            "actor_distribution": actor_counts,
            "time_based_analysis": {
                "last_day_count": last_day_count,
                "last_week_count": last_week_count,
                "last_month_count": last_month_count
            },
            "verification_status": {
                "verified_count": verified_count,
                "unverified_count": unverified_count,
                "verification_rate": verified_count / len(mutations) if mutations else 0
            },
            "anomaly_statistics": {
                "total_anomalies": len(anomalies),
                "open_anomalies": len([a for a in anomalies if a.get("status") == "open"]),
                "resolved_anomalies": len([a for a in anomalies if a.get("status") == "resolved"])
            },
            "timestamp": current_time.isoformat()
        }
    
    def _check_mutation_policies(self, capsule_id: str, mutation_type: MutationType,
                               mutation_data: Dict[str, Any], actor_id: str = None,
                               signature: str = None) -> Dict[str, Any]:
        """
        Check mutation against policies
        
        Args:
            capsule_id: Unique identifier for the capsule
            mutation_type: Type of mutation
            mutation_data: Data describing the mutation
            actor_id: Identifier of the actor performing the mutation
            signature: Digital signature of the mutation
            
        Returns:
            Policy check result
        """
        # Start with default policies
        policies = self.default_policies.copy()
        
        # Apply capsule-specific policies
        capsule_policies = [p for p in self.policy_registry.values() 
                           if p["status"] == "active" and
                           (p["target_capsules"] is None or capsule_id in p["target_capsules"]) and
                           (p["target_mutation_types"] is None or mutation_type.value in p["target_mutation_types"])]
        
        for policy in capsule_policies:
            policies.update(policy["policy_rules"])
        
        # Check policies
        policy_violations = []
        
        # Check signature requirement
        if policies.get("block_unsigned_mutations", False) and not signature:
            policy_violations.append("Unsigned mutations are blocked by policy")
        
        # Check mutation rate limit
        if "max_mutations_per_day" in policies:
            max_per_day = policies["max_mutations_per_day"]
            capsule_record = self.capsule_registry[capsule_id]
            
            # Count mutations in the last 24 hours
            current_time = datetime.utcnow()
            mutation_ids = capsule_record["mutation_history"]
            mutations = [self.mutation_registry[mid] for mid in mutation_ids if mid in self.mutation_registry]
            
            recent_mutations = [m for m in mutations if 
                               (current_time - datetime.fromisoformat(m["timestamp"])).total_seconds() <= 86400]
            
            if len(recent_mutations) >= max_per_day:
                policy_violations.append(f"Exceeded maximum mutations per day ({max_per_day})")
        
        # Check reason requirement
        if policies.get("require_reason_for_changes", False) and not mutation_data.get("reason"):
            policy_violations.append("Reason is required for changes by policy")
        
        # Check permission change verification
        if (mutation_type == MutationType.PERMISSION_CHANGE and
            policies.get("require_verification_for_permission_changes", False) and
            not mutation_data.get("verification")):
            policy_violations.append("Verification is required for permission changes by policy")
        
        # Check critical mutation approval
        mutation_severity = self._calculate_mutation_severity(mutation_type, mutation_data)
        if (mutation_severity == MutationSeverity.CRITICAL.value and
            policies.get("require_approval_for_critical", False) and
            not mutation_data.get("approval")):
            policy_violations.append("Approval is required for critical mutations by policy")
        
        # Return policy check result
        return {
            "allowed": len(policy_violations) == 0,
            "reason": "; ".join(policy_violations) if policy_violations else None,
            "policies_applied": policies
        }
    
    def _calculate_mutation_severity(self, mutation_type: MutationType,
                                   mutation_data: Dict[str, Any]) -> str:
        """
        Calculate severity of a mutation
        
        Args:
            mutation_type: Type of mutation
            mutation_data: Data describing the mutation
            
        Returns:
            Mutation severity
        """
        # Default severities by mutation type
        default_severities = {
            MutationType.CODE_CHANGE: MutationSeverity.HIGH.value,
            MutationType.CONFIGURATION_CHANGE: MutationSeverity.MEDIUM.value,
            MutationType.PERMISSION_CHANGE: MutationSeverity.HIGH.value,
            MutationType.DEPENDENCY_CHANGE: MutationSeverity.MEDIUM.value,
            MutationType.STATE_CHANGE: MutationSeverity.LOW.value,
            MutationType.LIFECYCLE_EVENT: MutationSeverity.INFORMATIONAL.value,
            MutationType.INTEGRATION_CHANGE: MutationSeverity.MEDIUM.value,
            MutationType.POLICY_CHANGE: MutationSeverity.HIGH.value
        }
        
        severity = default_severities.get(mutation_type, MutationSeverity.MEDIUM.value)
        
        # Adjust severity based on mutation data
        if mutation_type == MutationType.PERMISSION_CHANGE:
            # Elevation of privileges is critical
            if mutation_data.get("elevation", False):
                severity = MutationSeverity.CRITICAL.value
        
        elif mutation_type == MutationType.CODE_CHANGE:
            # Small changes might be less severe
            if mutation_data.get("size", 0) < 10:
                severity = MutationSeverity.MEDIUM.value
        
        elif mutation_type == MutationType.CONFIGURATION_CHANGE:
            # Security-related configuration changes are high severity
            if mutation_data.get("security_related", False):
                severity = MutationSeverity.HIGH.value
        
        # Override with explicit severity if provided
        if "severity" in mutation_data:
            severity = mutation_data["severity"]
        
        return severity
    
    def _check_for_anomalies(self, capsule_id: str, 
                            mutation_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for anomalies in a mutation
        
        Args:
            capsule_id: Unique identifier for the capsule
            mutation_record: Mutation record to check
            
        Returns:
            Anomaly check result
        """
        capsule_record = self.capsule_registry[capsule_id]
        mutation_type = MutationType(mutation_record["mutation_type"])
        mutation_data = mutation_record["mutation_data"]
        actor_id = mutation_record["actor_id"]
        
        anomalies = []
        
        # Check for unusual mutation patterns
        
        # 1. Unusual time of day
        mutation_time = datetime.fromisoformat(mutation_record["timestamp"])
        hour = mutation_time.hour
        if hour >= 22 or hour <= 5:  # Night-time mutations might be suspicious
            anomaly_id = str(uuid.uuid4())
            anomaly = {
                "anomaly_id": anomaly_id,
                "capsule_id": capsule_id,
                "mutation_id": mutation_record["mutation_id"],
                "anomaly_type": "unusual_time",
                "description": f"Mutation occurred during unusual hours ({hour}:00)",
                "severity": MutationSeverity.MEDIUM.value,
                "detection_time": datetime.utcnow().isoformat(),
                "status": "open"
            }
            self.anomaly_registry[anomaly_id] = anomaly
            anomalies.append(anomaly)
        
        # 2. Rapid succession of mutations
        recent_mutations = self.get_mutation_history(
            capsule_id=capsule_id,
            start_time=(datetime.utcnow() - timedelta(hours=1)).isoformat(),
            limit=100
        )
        
        if len(recent_mutations) > 10:  # More than 10 mutations in an hour
            anomaly_id = str(uuid.uuid4())
            anomaly = {
                "anomaly_id": anomaly_id,
                "capsule_id": capsule_id,
                "mutation_id": mutation_record["mutation_id"],
                "anomaly_type": "rapid_mutations",
                "description": f"High frequency of mutations: {len(recent_mutations)} in the last hour",
                "severity": MutationSeverity.HIGH.value,
                "detection_time": datetime.utcnow().isoformat(),
                "status": "open"
            }
            self.anomaly_registry[anomaly_id] = anomaly
            anomalies.append(anomaly)
        
        # 3. Unusual actor
        if actor_id:
            # Get previous mutations by this actor
            actor_mutations = [m for m in self.get_mutation_history(capsule_id, limit=1000) 
                              if m.get("actor_id") == actor_id]
            
            if len(actor_mutations) <= 1:  # First-time actor
                anomaly_id = str(uuid.uuid4())
                anomaly = {
                    "anomaly_id": anomaly_id,
                    "capsule_id": capsule_id,
                    "mutation_id": mutation_record["mutation_id"],
                    "anomaly_type": "new_actor",
                    "description": f"First mutation by actor: {actor_id}",
                    "severity": MutationSeverity.LOW.value,
                    "detection_time": datetime.utcnow().isoformat(),
                    "status": "open"
                }
                self.anomaly_registry[anomaly_id] = anomaly
                anomalies.append(anomaly)
        
        # 4. Permission elevation
        if (mutation_type == MutationType.PERMISSION_CHANGE and 
            mutation_data.get("elevation", False)):
            anomaly_id = str(uuid.uuid4())
            anomaly = {
                "anomaly_id": anomaly_id,
                "capsule_id": capsule_id,
                "mutation_id": mutation_record["mutation_id"],
                "anomaly_type": "permission_elevation",
                "description": "Permission elevation detected",
                "severity": MutationSeverity.CRITICAL.value,
                "detection_time": datetime.utcnow().isoformat(),
                "status": "open"
            }
            self.anomaly_registry[anomaly_id] = anomaly
            anomalies.append(anomaly)
        
        # 5. Unusual dependency changes
        if (mutation_type == MutationType.DEPENDENCY_CHANGE and 
            "new_dependencies" in mutation_data):
            new_deps = mutation_data["new_dependencies"]
            if len(new_deps) > 5:  # Large number of new dependencies
                anomaly_id = str(uuid.uuid4())
                anomaly = {
                    "anomaly_id": anomaly_id,
                    "capsule_id": capsule_id,
                    "mutation_id": mutation_record["mutation_id"],
                    "anomaly_type": "many_new_dependencies",
                    "description": f"Large number of new dependencies added: {len(new_deps)}",
                    "severity": MutationSeverity.HIGH.value,
                    "detection_time": datetime.utcnow().isoformat(),
                    "status": "open"
                }
                self.anomaly_registry[anomaly_id] = anomaly
                anomalies.append(anomaly)
        
        # Use AI-Security Co-Orchestration for advanced anomaly detection if available
        if self.ai_security_co_orchestration:
            ai_anomalies = self.ai_security_co_orchestration.detect_anomalies(
                context="capsule_mutation",
                data={
                    "capsule_id": capsule_id,
                    "mutation_record": mutation_record,
                    "capsule_record": capsule_record
                }
            )
            
            for ai_anomaly in ai_anomalies:
                anomaly_id = str(uuid.uuid4())
                anomaly = {
                    "anomaly_id": anomaly_id,
                    "capsule_id": capsule_id,
                    "mutation_id": mutation_record["mutation_id"],
                    "anomaly_type": f"ai_detected_{ai_anomaly['type']}",
                    "description": ai_anomaly["description"],
                    "severity": ai_anomaly["severity"],
                    "detection_time": datetime.utcnow().isoformat(),
                    "status": "open",
                    "ai_detection_details": ai_anomaly.get("details", {})
                }
                self.anomaly_registry[anomaly_id] = anomaly
                anomalies.append(anomaly)
        
        # Create audit records for anomalies if audit manager is available
        if anomalies and self.audit_trail_manager:
            for anomaly in anomalies:
                self.audit_trail_manager.create_audit_record(
                    event_type="capsule_mutation_anomaly",
                    resource_id=capsule_id,
                    action=anomaly["anomaly_type"],
                    actor_id="system",
                    details={
                        "anomaly_id": anomaly["anomaly_id"],
                        "mutation_id": mutation_record["mutation_id"],
                        "description": anomaly["description"],
                        "severity": anomaly["severity"]
                    }
                )
        
        return {
            "anomalies_detected": len(anomalies) > 0,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies
        }
    
    def resolve_anomaly(self, anomaly_id: str, resolution_notes: str,
                       resolver_id: str) -> Dict[str, Any]:
        """
        Resolve a detected anomaly
        
        Args:
            anomaly_id: Unique identifier for the anomaly
            resolution_notes: Notes about the resolution
            resolver_id: Identifier of the resolver
            
        Returns:
            Updated anomaly record
        """
        if anomaly_id not in self.anomaly_registry:
            raise ValueError(f"Anomaly not found: {anomaly_id}")
        
        anomaly = self.anomaly_registry[anomaly_id]
        
        # Update anomaly status
        anomaly["status"] = "resolved"
        anomaly["resolution_notes"] = resolution_notes
        anomaly["resolver_id"] = resolver_id
        anomaly["resolution_time"] = datetime.utcnow().isoformat()
        
        # Create audit record if audit manager is available
        if self.audit_trail_manager:
            self.audit_trail_manager.create_audit_record(
                event_type="capsule_mutation_anomaly_resolution",
                resource_id=anomaly["capsule_id"],
                action="resolve_anomaly",
                actor_id=resolver_id,
                details={
                    "anomaly_id": anomaly_id,
                    "resolution_notes": resolution_notes
                }
            )
        
        logger.info(f"Resolved anomaly {anomaly_id} for capsule {anomaly['capsule_id']}")
        return anomaly
    
    def export_capsule_mutation_data(self, capsule_id: str) -> Dict[str, Any]:
        """
        Export all mutation data for a capsule
        
        Args:
            capsule_id: Unique identifier for the capsule
            
        Returns:
            Capsule mutation data export
        """
        if capsule_id not in self.capsule_registry:
            raise ValueError(f"Capsule not registered: {capsule_id}")
        
        capsule_record = self.capsule_registry[capsule_id]
        
        # Get mutation records
        mutation_ids = capsule_record["mutation_history"]
        mutations = [self.mutation_registry[mid] for mid in mutation_ids if mid in self.mutation_registry]
        
        # Get anomaly records
        anomaly_ids = capsule_record["anomaly_history"]
        anomalies = [self.anomaly_registry[aid] for aid in anomaly_ids if aid in self.anomaly_registry]
        
        # Get applicable policies
        policies = [p for p in self.policy_registry.values() 
                   if p["status"] == "active" and
                   (p["target_capsules"] is None or capsule_id in p["target_capsules"])]
        
        return {
            "capsule": capsule_record,
            "mutations": mutations,
            "anomalies": anomalies,
            "policies": policies,
            "export_date": datetime.utcnow().isoformat()
        }
    
    def import_capsule_mutation_data(self, mutation_data: Dict[str, Any]):
        """
        Import capsule mutation data
        
        Args:
            mutation_data: Capsule mutation data to import
        """
        # Import capsule record
        capsule = mutation_data["capsule"]
        self.capsule_registry[capsule["capsule_id"]] = capsule
        
        # Import mutations
        for mutation in mutation_data["mutations"]:
            self.mutation_registry[mutation["mutation_id"]] = mutation
        
        # Import anomalies
        for anomaly in mutation_data["anomalies"]:
            self.anomaly_registry[anomaly["anomaly_id"]] = anomaly
        
        # Import policies
        for policy in mutation_data["policies"]:
            self.policy_registry[policy["policy_id"]] = policy
        
        logger.info(f"Imported mutation data for capsule {capsule['capsule_id']}")
