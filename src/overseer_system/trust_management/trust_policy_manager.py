"""
Trust Policy Manager for the Overseer System.

This module provides comprehensive trust policy management capabilities for the Overseer System,
enabling the definition, enforcement, and management of trust policies across the system.

The Trust Policy Manager is a critical component of the Trust Management framework,
providing a centralized mechanism for defining and enforcing trust policies.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from pydantic import BaseModel, Field

# Import MCP/A2A integration
from ..mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from ..a2a_integration.a2a_protocol_bridge import A2AProtocolBridge

# Import event bus
from ..event_bus.kafka_client import KafkaProducer, KafkaConsumer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("trust_policy_manager")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="trust-policy-manager"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="trust-policy-manager",
    auto_offset_reset="earliest"
)

# Data models
class TrustPolicy(BaseModel):
    """Model for trust policies."""
    policy_id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Human-readable policy name")
    description: str = Field(..., description="Policy description")
    version: int = Field(1, description="Policy version number")
    scope: str = Field(..., description="Policy scope (global, domain, entity)")
    scope_id: Optional[str] = Field(None, description="ID of the scope if not global")
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules")
    priority: int = Field(0, description="Policy priority (higher numbers take precedence)")
    active: bool = Field(True, description="Whether the policy is active")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="ID of the entity that created the policy")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TrustPolicyRule(BaseModel):
    """Model for trust policy rules."""
    rule_id: str = Field(..., description="Unique rule identifier")
    rule_type: str = Field(..., description="Type of rule")
    conditions: List[Dict[str, Any]] = Field(..., description="Rule conditions")
    actions: List[Dict[str, Any]] = Field(..., description="Rule actions")
    priority: int = Field(0, description="Rule priority within the policy")
    description: Optional[str] = Field(None, description="Rule description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PolicyEvaluationRequest(BaseModel):
    """Model for policy evaluation requests."""
    entity_id: str = Field(..., description="Entity ID to evaluate against policies")
    context: Dict[str, Any] = Field(default_factory=dict, description="Evaluation context")
    action: str = Field(..., description="Action being evaluated")
    resource: Optional[str] = Field(None, description="Resource being accessed, if applicable")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes for evaluation")

class PolicyEvaluationResult(BaseModel):
    """Model for policy evaluation results."""
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    entity_id: str = Field(..., description="Entity ID that was evaluated")
    action: str = Field(..., description="Action that was evaluated")
    resource: Optional[str] = Field(None, description="Resource that was evaluated")
    allowed: bool = Field(..., description="Whether the action is allowed")
    policies_evaluated: List[str] = Field(..., description="IDs of policies that were evaluated")
    decisive_policy: Optional[str] = Field(None, description="ID of the policy that made the decision")
    timestamp: datetime = Field(default_factory=datetime.now, description="Evaluation timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Evaluation details")

# In-memory storage (would be replaced with database in production)
trust_policies = {}
policy_evaluations = {}

class TrustPolicyManager:
    """
    Trust Policy Manager implementation for the Overseer System.
    
    This class provides methods for managing trust policies, including:
    - Creating and managing policies
    - Evaluating entities against policies
    - Enforcing policy decisions
    - Managing policy versions and history
    """
    
    def __init__(self):
        """Initialize the Trust Policy Manager."""
        self._initialize_default_policies()
        logger.info("Trust Policy Manager initialized")
    
    def _initialize_default_policies(self):
        """Initialize default trust policies."""
        default_policies = [
            TrustPolicy(
                policy_id="default-access-policy",
                name="Default Access Policy",
                description="Default policy for access control",
                scope="global",
                rules=[
                    {
                        "rule_id": "default-access-rule-1",
                        "rule_type": "access",
                        "conditions": [
                            {"type": "trust_score", "operator": ">=", "value": 0.7}
                        ],
                        "actions": [
                            {"type": "allow"}
                        ],
                        "priority": 0
                    },
                    {
                        "rule_id": "default-access-rule-2",
                        "rule_type": "access",
                        "conditions": [
                            {"type": "trust_score", "operator": "<", "value": 0.7}
                        ],
                        "actions": [
                            {"type": "deny"}
                        ],
                        "priority": 0
                    }
                ],
                priority=0
            ),
            TrustPolicy(
                policy_id="default-collaboration-policy",
                name="Default Collaboration Policy",
                description="Default policy for entity collaboration",
                scope="global",
                rules=[
                    {
                        "rule_id": "default-collab-rule-1",
                        "rule_type": "collaboration",
                        "conditions": [
                            {"type": "trust_score", "operator": ">=", "value": 0.8}
                        ],
                        "actions": [
                            {"type": "allow"}
                        ],
                        "priority": 0
                    },
                    {
                        "rule_id": "default-collab-rule-2",
                        "rule_type": "collaboration",
                        "conditions": [
                            {"type": "trust_score", "operator": "<", "value": 0.8}
                        ],
                        "actions": [
                            {"type": "deny"}
                        ],
                        "priority": 0
                    }
                ],
                priority=0
            ),
            TrustPolicy(
                policy_id="default-data-sharing-policy",
                name="Default Data Sharing Policy",
                description="Default policy for data sharing",
                scope="global",
                rules=[
                    {
                        "rule_id": "default-data-rule-1",
                        "rule_type": "data_sharing",
                        "conditions": [
                            {"type": "trust_score", "operator": ">=", "value": 0.9},
                            {"type": "data_classification", "operator": "!=", "value": "sensitive"}
                        ],
                        "actions": [
                            {"type": "allow"}
                        ],
                        "priority": 0
                    },
                    {
                        "rule_id": "default-data-rule-2",
                        "rule_type": "data_sharing",
                        "conditions": [
                            {"type": "trust_score", "operator": "<", "value": 0.9}
                        ],
                        "actions": [
                            {"type": "deny"}
                        ],
                        "priority": 0
                    },
                    {
                        "rule_id": "default-data-rule-3",
                        "rule_type": "data_sharing",
                        "conditions": [
                            {"type": "data_classification", "operator": "==", "value": "sensitive"}
                        ],
                        "actions": [
                            {"type": "deny"}
                        ],
                        "priority": 1  # Higher priority to override other rules
                    }
                ],
                priority=0
            )
        ]
        
        for policy in default_policies:
            trust_policies[policy.policy_id] = policy.dict()
    
    def create_policy(self, policy: TrustPolicy) -> str:
        """
        Create a new trust policy.
        
        Args:
            policy: The policy to create
            
        Returns:
            str: Policy ID
        """
        policy_dict = policy.dict()
        
        # Generate policy ID if not provided
        if not policy.policy_id:
            policy_dict["policy_id"] = f"policy-{uuid.uuid4()}"
        
        # Set timestamps
        now = datetime.now()
        policy_dict["created_at"] = now.isoformat()
        policy_dict["updated_at"] = now.isoformat()
        
        # Store the policy
        trust_policies[policy_dict["policy_id"]] = policy_dict
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="policy-events",
            key=policy_dict["policy_id"],
            value=json.dumps({
                "event_type": "policy_created",
                "policy_id": policy_dict["policy_id"],
                "name": policy.name,
                "timestamp": now.isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "policy_created",
            "policy_id": policy_dict["policy_id"],
            "name": policy.name,
            "scope": policy.scope
        }
        mcp_bridge.send_context_update("trust_policy_manager", mcp_context)
        
        return policy_dict["policy_id"]
    
    def update_policy(self, policy_id: str, policy: TrustPolicy) -> bool:
        """
        Update an existing trust policy.
        
        Args:
            policy_id: The ID of the policy to update
            policy: The updated policy
            
        Returns:
            bool: Whether the update was successful
        """
        if policy_id not in trust_policies:
            return False
        
        # Get existing policy
        existing_policy = trust_policies[policy_id]
        
        # Create updated policy
        policy_dict = policy.dict()
        policy_dict["policy_id"] = policy_id  # Ensure ID remains the same
        policy_dict["created_at"] = existing_policy["created_at"]  # Preserve creation timestamp
        policy_dict["updated_at"] = datetime.now().isoformat()  # Update modification timestamp
        policy_dict["version"] = existing_policy["version"] + 1  # Increment version
        
        # Store the updated policy
        trust_policies[policy_id] = policy_dict
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="policy-events",
            key=policy_id,
            value=json.dumps({
                "event_type": "policy_updated",
                "policy_id": policy_id,
                "name": policy.name,
                "version": policy_dict["version"],
                "timestamp": policy_dict["updated_at"]
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "policy_updated",
            "policy_id": policy_id,
            "name": policy.name,
            "version": policy_dict["version"]
        }
        mcp_bridge.send_context_update("trust_policy_manager", mcp_context)
        
        return True
    
    def get_policy(self, policy_id: str) -> Optional[TrustPolicy]:
        """
        Get a trust policy by ID.
        
        Args:
            policy_id: The policy ID
            
        Returns:
            Optional[TrustPolicy]: The policy, or None if not found
        """
        if policy_id not in trust_policies:
            return None
        
        return TrustPolicy(**trust_policies[policy_id])
    
    def list_policies(self, scope: Optional[str] = None, scope_id: Optional[str] = None, active_only: bool = True) -> List[TrustPolicy]:
        """
        List trust policies, optionally filtered by scope and active status.
        
        Args:
            scope: Optional scope to filter by
            scope_id: Optional scope ID to filter by
            active_only: Whether to include only active policies
            
        Returns:
            List[TrustPolicy]: List of matching policies
        """
        results = []
        
        for policy_dict in trust_policies.values():
            # Apply filters
            if active_only and not policy_dict["active"]:
                continue
            
            if scope and policy_dict["scope"] != scope:
                continue
            
            if scope_id and policy_dict["scope_id"] != scope_id:
                continue
            
            results.append(TrustPolicy(**policy_dict))
        
        # Sort by priority (higher first)
        results.sort(key=lambda p: p.priority, reverse=True)
        
        return results
    
    def delete_policy(self, policy_id: str) -> bool:
        """
        Delete a trust policy.
        
        Args:
            policy_id: The policy ID
            
        Returns:
            bool: Whether the deletion was successful
        """
        if policy_id not in trust_policies:
            return False
        
        # Get policy details for event
        policy_name = trust_policies[policy_id]["name"]
        
        # Delete the policy
        del trust_policies[policy_id]
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="policy-events",
            key=policy_id,
            value=json.dumps({
                "event_type": "policy_deleted",
                "policy_id": policy_id,
                "name": policy_name,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "policy_deleted",
            "policy_id": policy_id,
            "name": policy_name
        }
        mcp_bridge.send_context_update("trust_policy_manager", mcp_context)
        
        return True
    
    def activate_policy(self, policy_id: str) -> bool:
        """
        Activate a trust policy.
        
        Args:
            policy_id: The policy ID
            
        Returns:
            bool: Whether the activation was successful
        """
        if policy_id not in trust_policies:
            return False
        
        # Update policy status
        trust_policies[policy_id]["active"] = True
        trust_policies[policy_id]["updated_at"] = datetime.now().isoformat()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="policy-events",
            key=policy_id,
            value=json.dumps({
                "event_type": "policy_activated",
                "policy_id": policy_id,
                "name": trust_policies[policy_id]["name"],
                "timestamp": trust_policies[policy_id]["updated_at"]
            })
        )
        
        return True
    
    def deactivate_policy(self, policy_id: str) -> bool:
        """
        Deactivate a trust policy.
        
        Args:
            policy_id: The policy ID
            
        Returns:
            bool: Whether the deactivation was successful
        """
        if policy_id not in trust_policies:
            return False
        
        # Update policy status
        trust_policies[policy_id]["active"] = False
        trust_policies[policy_id]["updated_at"] = datetime.now().isoformat()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="policy-events",
            key=policy_id,
            value=json.dumps({
                "event_type": "policy_deactivated",
                "policy_id": policy_id,
                "name": trust_policies[policy_id]["name"],
                "timestamp": trust_policies[policy_id]["updated_at"]
            })
        )
        
        return True
    
    def evaluate_policies(self, request: PolicyEvaluationRequest) -> PolicyEvaluationResult:
        """
        Evaluate policies for an entity and action.
        
        Args:
            request: The policy evaluation request
            
        Returns:
            PolicyEvaluationResult: The evaluation result
        """
        entity_id = request.entity_id
        action = request.action
        resource = request.resource
        context = request.context
        attributes = request.attributes
        
        # Generate evaluation ID
        evaluation_id = f"eval-{uuid.uuid4()}"
        
        # Get applicable policies
        applicable_policies = []
        
        # First, get global policies
        global_policies = self.list_policies(scope="global")
        applicable_policies.extend(global_policies)
        
        # Then, get domain policies if domain is specified
        if "domain" in context:
            domain_policies = self.list_policies(scope="domain", scope_id=context["domain"])
            applicable_policies.extend(domain_policies)
        
        # Finally, get entity-specific policies
        entity_policies = self.list_policies(scope="entity", scope_id=entity_id)
        applicable_policies.extend(entity_policies)
        
        # Sort by priority (higher first)
        applicable_policies.sort(key=lambda p: p.priority, reverse=True)
        
        # Evaluate policies
        allowed = False
        decisive_policy = None
        evaluation_details = {}
        
        for policy in applicable_policies:
            policy_result = self._evaluate_policy(policy, entity_id, action, resource, context, attributes)
            evaluation_details[policy.policy_id] = policy_result
            
            if policy_result["decision"] is not None:
                allowed = policy_result["decision"]
                decisive_policy = policy.policy_id
                break
        
        # Create evaluation result
        result = PolicyEvaluationResult(
            evaluation_id=evaluation_id,
            entity_id=entity_id,
            action=action,
            resource=resource,
            allowed=allowed,
            policies_evaluated=[p.policy_id for p in applicable_policies],
            decisive_policy=decisive_policy,
            details={
                "policy_results": evaluation_details,
                "context": context,
                "attributes": attributes
            }
        )
        
        # Store the evaluation result
        policy_evaluations[evaluation_id] = result.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="policy-events",
            key=entity_id,
            value=json.dumps({
                "event_type": "policy_evaluation",
                "evaluation_id": evaluation_id,
                "entity_id": entity_id,
                "action": action,
                "allowed": allowed,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "policy_evaluation",
            "evaluation_id": evaluation_id,
            "entity_id": entity_id,
            "requested_action": action,
            "allowed": allowed
        }
        mcp_bridge.send_context_update("trust_policy_manager", mcp_context)
        
        return result
    
    def _evaluate_policy(
        self, policy: TrustPolicy, entity_id: str, action: str, 
        resource: Optional[str], context: Dict[str, Any], attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a single policy.
        
        Args:
            policy: The policy to evaluate
            entity_id: The entity ID
            action: The action being evaluated
            resource: The resource being accessed
            context: The evaluation context
            attributes: Additional attributes for evaluation
            
        Returns:
            Dict[str, Any]: The evaluation result for this policy
        """
        # Find applicable rules for this action
        applicable_rules = []
        for rule in policy.rules:
            if rule["rule_type"] == action or rule["rule_type"] == "any":
                applicable_rules.append(rule)
        
        # Sort rules by priority
        applicable_rules.sort(key=lambda r: r["priority"], reverse=True)
        
        # Evaluate rules
        for rule in applicable_rules:
            rule_result = self._evaluate_rule(rule, entity_id, context, attributes)
            
            if rule_result["matches"]:
                # Rule matched, apply actions
                for action_def in rule["actions"]:
                    if action_def["type"] == "allow":
                        return {
                            "decision": True,
                            "rule_id": rule["rule_id"],
                            "rule_result": rule_result
                        }
                    elif action_def["type"] == "deny":
                        return {
                            "decision": False,
                            "rule_id": rule["rule_id"],
                            "rule_result": rule_result
                        }
        
        # No decisive rule found
        return {
            "decision": None,
            "rule_id": None,
            "message": "No applicable rules found"
        }
    
    def _evaluate_rule(
        self, rule: Dict[str, Any], entity_id: str, 
        context: Dict[str, Any], attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a single rule.
        
        Args:
            rule: The rule to evaluate
            entity_id: The entity ID
            context: The evaluation context
            attributes: Additional attributes for evaluation
            
        Returns:
            Dict[str, Any]: The evaluation result for this rule
        """
        # Check if all conditions match
        condition_results = []
        
        for condition in rule["conditions"]:
            condition_result = self._evaluate_condition(condition, entity_id, context, attributes)
            condition_results.append(condition_result)
            
            if not condition_result["matches"]:
                # If any condition fails, the rule doesn't match
                return {
                    "matches": False,
                    "condition_results": condition_results
                }
        
        # All conditions matched
        return {
            "matches": True,
            "condition_results": condition_results
        }
    
    def _evaluate_condition(
        self, condition: Dict[str, Any], entity_id: str, 
        context: Dict[str, Any], attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a single condition.
        
        Args:
            condition: The condition to evaluate
            entity_id: The entity ID
            context: The evaluation context
            attributes: Additional attributes for evaluation
            
        Returns:
            Dict[str, Any]: The evaluation result for this condition
        """
        condition_type = condition["type"]
        operator = condition["operator"]
        expected_value = condition["value"]
        
        # Get actual value based on condition type
        if condition_type == "trust_score":
            # In a real implementation, this would query the Trust Management Service
            # For demonstration, we'll use a value from attributes or context
            actual_value = attributes.get("trust_score", context.get("trust_score", 0.5))
        elif condition_type == "data_classification":
            actual_value = attributes.get("data_classification", context.get("data_classification", "public"))
        elif condition_type == "time_of_day":
            # Get current hour
            current_hour = datetime.now().hour
            actual_value = current_hour
        elif condition_type == "location":
            actual_value = attributes.get("location", context.get("location", "unknown"))
        elif condition_type == "role":
            actual_value = attributes.get("role", context.get("role", "user"))
        elif condition_type == "attribute":
            # For generic attributes, the attribute name should be specified
            attribute_name = condition.get("attribute_name", "")
            actual_value = attributes.get(attribute_name, context.get(attribute_name, None))
        else:
            # Unknown condition type
            return {
                "matches": False,
                "error": f"Unknown condition type: {condition_type}"
            }
        
        # Apply operator
        if operator == "==":
            matches = actual_value == expected_value
        elif operator == "!=":
            matches = actual_value != expected_value
        elif operator == ">":
            matches = actual_value > expected_value
        elif operator == ">=":
            matches = actual_value >= expected_value
        elif operator == "<":
            matches = actual_value < expected_value
        elif operator == "<=":
            matches = actual_value <= expected_value
        elif operator == "in":
            matches = actual_value in expected_value
        elif operator == "not_in":
            matches = actual_value not in expected_value
        else:
            # Unknown operator
            return {
                "matches": False,
                "error": f"Unknown operator: {operator}"
            }
        
        return {
            "matches": matches,
            "condition_type": condition_type,
            "operator": operator,
            "expected_value": expected_value,
            "actual_value": actual_value
        }
    
    def get_evaluation_result(self, evaluation_id: str) -> Optional[PolicyEvaluationResult]:
        """
        Get a policy evaluation result by ID.
        
        Args:
            evaluation_id: The evaluation ID
            
        Returns:
            Optional[PolicyEvaluationResult]: The evaluation result, or None if not found
        """
        if evaluation_id not in policy_evaluations:
            return None
        
        return PolicyEvaluationResult(**policy_evaluations[evaluation_id])

# Create singleton instance
trust_policy_manager = TrustPolicyManager()

# API endpoints (if this were a standalone service)
app = FastAPI(
    title="Trust Policy Manager",
    description="Trust Policy Manager for the Overseer System",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "trust_policy_manager", "timestamp": datetime.now().isoformat()}

@app.post("/policies")
async def create_policy(policy: TrustPolicy):
    """Create a new trust policy."""
    policy_id = trust_policy_manager.create_policy(policy)
    return {"policy_id": policy_id, "status": "created"}

@app.get("/policies")
async def list_policies(
    scope: Optional[str] = None, 
    scope_id: Optional[str] = None, 
    active_only: bool = True
):
    """List trust policies."""
    policies = trust_policy_manager.list_policies(scope, scope_id, active_only)
    return {"policies": policies, "count": len(policies)}

@app.get("/policies/{policy_id}")
async def get_policy(policy_id: str):
    """Get a trust policy by ID."""
    policy = trust_policy_manager.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return policy

@app.put("/policies/{policy_id}")
async def update_policy(policy_id: str, policy: TrustPolicy):
    """Update a trust policy."""
    success = trust_policy_manager.update_policy(policy_id, policy)
    if not success:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return {"policy_id": policy_id, "status": "updated"}

@app.delete("/policies/{policy_id}")
async def delete_policy(policy_id: str):
    """Delete a trust policy."""
    success = trust_policy_manager.delete_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return {"policy_id": policy_id, "status": "deleted"}

@app.post("/policies/{policy_id}/activate")
async def activate_policy(policy_id: str):
    """Activate a trust policy."""
    success = trust_policy_manager.activate_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return {"policy_id": policy_id, "status": "activated"}

@app.post("/policies/{policy_id}/deactivate")
async def deactivate_policy(policy_id: str):
    """Deactivate a trust policy."""
    success = trust_policy_manager.deactivate_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return {"policy_id": policy_id, "status": "deactivated"}

@app.post("/evaluate")
async def evaluate_policies(request: PolicyEvaluationRequest):
    """Evaluate policies for an entity and action."""
    result = trust_policy_manager.evaluate_policies(request)
    return result

@app.get("/evaluations/{evaluation_id}")
async def get_evaluation(evaluation_id: str):
    """Get a policy evaluation result by ID."""
    result = trust_policy_manager.get_evaluation_result(evaluation_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Evaluation result {evaluation_id} not found")
    return result

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Trust Policy Manager starting up")
    
    # Subscribe to relevant Kafka topics
    kafka_consumer.subscribe(["entity-events", "policy-events"])
    
    logger.info("Trust Policy Manager started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Trust Policy Manager shutting down")
    
    # Close Kafka connections
    kafka_producer.close()
    kafka_consumer.close()
    
    logger.info("Trust Policy Manager shut down successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
