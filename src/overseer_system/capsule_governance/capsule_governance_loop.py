"""
Capsule Governance Loop for the Overseer System.

This module provides the Capsule Governance Loop that continuously monitors, evaluates,
and governs capsules across the Industriverse ecosystem.
"""

import os
import json
import logging
import asyncio
import datetime
import uuid
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("capsule_governance_loop")

class GovernanceState(BaseModel):
    """Governance state for a capsule."""
    capsule_id: str
    state_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    status: str  # active, restricted, suspended, terminated
    trust_score: float
    compliance_score: float
    morality_score: float
    performance_score: float
    governance_version: str
    last_assessment: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GovernanceAction(BaseModel):
    """Governance action for a capsule."""
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    action_type: str  # assess, restrict, suspend, terminate, restore, upgrade
    reason: str
    context: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GovernancePolicy(BaseModel):
    """Governance policy."""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str
    scope: str  # global, industry, organization, capsule_type
    scope_id: Optional[str] = None
    rules: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    priority: int
    enabled: bool = True
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CapsuleGovernanceLoop:
    """
    Capsule Governance Loop.
    
    This loop continuously monitors, evaluates, and governs capsules across the Industriverse ecosystem.
    """
    
    def __init__(self, event_bus_client=None, mcp_client=None, a2a_client=None, 
                 morality_engine=None, trust_engine=None, compliance_engine=None):
        """
        Initialize the Capsule Governance Loop.
        
        Args:
            event_bus_client: Event bus client for publishing and subscribing to events
            mcp_client: MCP client for context-aware communication
            a2a_client: A2A client for agent-based communication
            morality_engine: Capsule Morality Engine
            trust_engine: Trust Management Engine
            compliance_engine: Compliance Engine
        """
        self.event_bus_client = event_bus_client
        self.mcp_client = mcp_client
        self.a2a_client = a2a_client
        self.morality_engine = morality_engine
        self.trust_engine = trust_engine
        self.compliance_engine = compliance_engine
        
        # In-memory storage (would be replaced with database in production)
        self.governance_states = {}  # capsule_id -> GovernanceState
        self.governance_actions = []  # List of GovernanceAction
        self.governance_policies = {}  # policy_id -> GovernancePolicy
        
        # Initialize default policies
        self._initialize_default_policies()
        
        # Governance loop control
        self.running = False
        self.loop_interval = 60  # seconds
        self.governance_task = None
        
    def _initialize_default_policies(self):
        """Initialize default governance policies."""
        # Global minimum trust policy
        global_trust_policy = GovernancePolicy(
            name="Global Minimum Trust Policy",
            description="Ensures all capsules maintain a minimum trust score",
            version="1.0.0",
            scope="global",
            priority=100,
            rules=[
                {
                    "attribute": "trust_score",
                    "operator": "less_than",
                    "value": 0.5,
                    "action": "suspend",
                    "reason": "Trust score below minimum threshold"
                },
                {
                    "attribute": "trust_score",
                    "operator": "less_than",
                    "value": 0.3,
                    "action": "terminate",
                    "reason": "Trust score critically low"
                }
            ],
            actions=[
                {
                    "name": "notify_admin",
                    "description": "Notify administrators of policy violation",
                    "parameters": {
                        "channel": "admin",
                        "priority": "high"
                    }
                },
                {
                    "name": "log_violation",
                    "description": "Log policy violation",
                    "parameters": {
                        "level": "warning"
                    }
                }
            ]
        )
        
        # Global minimum morality policy
        global_morality_policy = GovernancePolicy(
            name="Global Minimum Morality Policy",
            description="Ensures all capsules maintain ethical standards",
            version="1.0.0",
            scope="global",
            priority=90,
            rules=[
                {
                    "attribute": "morality_score",
                    "operator": "less_than",
                    "value": 0.7,
                    "action": "restrict",
                    "reason": "Morality score below acceptable threshold"
                },
                {
                    "attribute": "morality_score",
                    "operator": "less_than",
                    "value": 0.5,
                    "action": "suspend",
                    "reason": "Morality score significantly below threshold"
                }
            ],
            actions=[
                {
                    "name": "notify_admin",
                    "description": "Notify administrators of policy violation",
                    "parameters": {
                        "channel": "admin",
                        "priority": "high"
                    }
                },
                {
                    "name": "log_violation",
                    "description": "Log policy violation",
                    "parameters": {
                        "level": "warning"
                    }
                }
            ]
        )
        
        # Global minimum compliance policy
        global_compliance_policy = GovernancePolicy(
            name="Global Minimum Compliance Policy",
            description="Ensures all capsules maintain compliance with regulations",
            version="1.0.0",
            scope="global",
            priority=80,
            rules=[
                {
                    "attribute": "compliance_score",
                    "operator": "less_than",
                    "value": 0.8,
                    "action": "restrict",
                    "reason": "Compliance score below acceptable threshold"
                },
                {
                    "attribute": "compliance_score",
                    "operator": "less_than",
                    "value": 0.6,
                    "action": "suspend",
                    "reason": "Compliance score significantly below threshold"
                }
            ],
            actions=[
                {
                    "name": "notify_admin",
                    "description": "Notify administrators of policy violation",
                    "parameters": {
                        "channel": "admin",
                        "priority": "high"
                    }
                },
                {
                    "name": "log_violation",
                    "description": "Log policy violation",
                    "parameters": {
                        "level": "warning"
                    }
                }
            ]
        )
        
        # Global minimum performance policy
        global_performance_policy = GovernancePolicy(
            name="Global Minimum Performance Policy",
            description="Ensures all capsules maintain acceptable performance",
            version="1.0.0",
            scope="global",
            priority=70,
            rules=[
                {
                    "attribute": "performance_score",
                    "operator": "less_than",
                    "value": 0.6,
                    "action": "restrict",
                    "reason": "Performance score below acceptable threshold"
                },
                {
                    "attribute": "performance_score",
                    "operator": "less_than",
                    "value": 0.4,
                    "action": "suspend",
                    "reason": "Performance score significantly below threshold"
                }
            ],
            actions=[
                {
                    "name": "notify_admin",
                    "description": "Notify administrators of policy violation",
                    "parameters": {
                        "channel": "admin",
                        "priority": "medium"
                    }
                },
                {
                    "name": "log_violation",
                    "description": "Log policy violation",
                    "parameters": {
                        "level": "warning"
                    }
                }
            ]
        )
        
        # Store policies
        self.governance_policies[global_trust_policy.policy_id] = global_trust_policy
        self.governance_policies[global_morality_policy.policy_id] = global_morality_policy
        self.governance_policies[global_compliance_policy.policy_id] = global_compliance_policy
        self.governance_policies[global_performance_policy.policy_id] = global_performance_policy
        
    async def initialize(self):
        """Initialize the Capsule Governance Loop."""
        logger.info("Initializing Capsule Governance Loop")
        
        # In a real implementation, we would initialize connections to external systems
        # For example:
        # await self.event_bus_client.connect()
        # await self.mcp_client.connect()
        # await self.a2a_client.connect()
        
        # Subscribe to events
        # await self.event_bus_client.subscribe("capsule.created", self._handle_capsule_created)
        # await self.event_bus_client.subscribe("capsule.updated", self._handle_capsule_updated)
        # await self.event_bus_client.subscribe("capsule.action", self._handle_capsule_action)
        
        logger.info("Capsule Governance Loop initialized")
        
    async def start(self):
        """Start the governance loop."""
        if self.running:
            logger.warning("Governance loop already running")
            return
            
        logger.info("Starting governance loop")
        self.running = True
        self.governance_task = asyncio.create_task(self._governance_loop())
        
    async def stop(self):
        """Stop the governance loop."""
        if not self.running:
            logger.warning("Governance loop not running")
            return
            
        logger.info("Stopping governance loop")
        self.running = False
        if self.governance_task:
            await self.governance_task
            self.governance_task = None
            
    async def _governance_loop(self):
        """Main governance loop."""
        logger.info("Governance loop started")
        
        try:
            while self.running:
                logger.info("Running governance cycle")
                
                # Get all capsules
                # In a real implementation, we would retrieve capsules from a database
                # For simplicity, we'll use the capsules we know about
                capsule_ids = list(self.governance_states.keys())
                
                # Process each capsule
                for capsule_id in capsule_ids:
                    try:
                        await self._process_capsule(capsule_id)
                    except Exception as e:
                        logger.error(f"Error processing capsule {capsule_id}: {e}")
                
                # Wait for next cycle
                logger.info(f"Governance cycle completed, waiting {self.loop_interval} seconds")
                await asyncio.sleep(self.loop_interval)
                
        except asyncio.CancelledError:
            logger.info("Governance loop cancelled")
        except Exception as e:
            logger.error(f"Error in governance loop: {e}")
            raise
        finally:
            logger.info("Governance loop stopped")
            
    async def _process_capsule(self, capsule_id: str):
        """
        Process a capsule in the governance loop.
        
        Args:
            capsule_id: ID of the capsule to process
        """
        logger.info(f"Processing capsule {capsule_id}")
        
        # Get current state
        state = self.governance_states.get(capsule_id)
        if not state:
            # Create initial state
            state = await self._create_initial_state(capsule_id)
            
        # Check if assessment is needed
        now = datetime.datetime.now()
        assessment_age = (now - state.last_assessment).total_seconds()
        assessment_interval = 3600  # 1 hour
        
        if assessment_age >= assessment_interval:
            # Assess capsule
            await self._assess_capsule(capsule_id, state)
            
        # Apply policies
        await self._apply_policies(capsule_id, state)
        
    async def _create_initial_state(self, capsule_id: str) -> GovernanceState:
        """
        Create initial governance state for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Initial governance state
        """
        logger.info(f"Creating initial governance state for capsule {capsule_id}")
        
        # In a real implementation, we would retrieve capsule data
        # For simplicity, we'll create a default state
        
        state = GovernanceState(
            capsule_id=capsule_id,
            status="active",
            trust_score=0.8,
            compliance_score=0.9,
            morality_score=0.85,
            performance_score=0.75,
            governance_version="1.0.0"
        )
        
        # Store state
        self.governance_states[capsule_id] = state
        
        # Record action
        action = GovernanceAction(
            capsule_id=capsule_id,
            action_type="assess",
            reason="Initial assessment",
            result="active"
        )
        
        self.governance_actions.append(action)
        
        # In a real implementation, we would publish the state and action
        # For example:
        # await self.event_bus_client.publish("governance.state.created", state.dict())
        # await self.event_bus_client.publish("governance.action", action.dict())
        
        return state
        
    async def _assess_capsule(self, capsule_id: str, state: GovernanceState):
        """
        Assess a capsule and update its governance state.
        
        Args:
            capsule_id: ID of the capsule
            state: Current governance state
        """
        logger.info(f"Assessing capsule {capsule_id}")
        
        # In a real implementation, we would retrieve assessment data from various engines
        # For simplicity, we'll generate simulated scores
        
        import random
        
        # Generate new scores with some variation from current scores
        def vary_score(current, max_delta=0.1):
            delta = random.uniform(-max_delta, max_delta)
            new_score = current + delta
            return max(0.0, min(1.0, new_score))
            
        trust_score = vary_score(state.trust_score)
        compliance_score = vary_score(state.compliance_score)
        morality_score = vary_score(state.morality_score)
        performance_score = vary_score(state.performance_score)
        
        # Update state
        old_status = state.status
        state.trust_score = trust_score
        state.compliance_score = compliance_score
        state.morality_score = morality_score
        state.performance_score = performance_score
        state.last_assessment = datetime.datetime.now()
        
        # Record action
        action = GovernanceAction(
            capsule_id=capsule_id,
            action_type="assess",
            reason="Scheduled assessment",
            context={
                "trust_score": trust_score,
                "compliance_score": compliance_score,
                "morality_score": morality_score,
                "performance_score": performance_score
            },
            result=state.status
        )
        
        self.governance_actions.append(action)
        
        # In a real implementation, we would publish the updated state and action
        # For example:
        # await self.event_bus_client.publish("governance.state.updated", state.dict())
        # await self.event_bus_client.publish("governance.action", action.dict())
        
        logger.info(f"Assessment completed for capsule {capsule_id}: status={state.status}")
        
    async def _apply_policies(self, capsule_id: str, state: GovernanceState):
        """
        Apply governance policies to a capsule.
        
        Args:
            capsule_id: ID of the capsule
            state: Current governance state
        """
        logger.info(f"Applying policies to capsule {capsule_id}")
        
        # Get applicable policies
        policies = self._get_applicable_policies(capsule_id, state)
        
        # Sort policies by priority (highest first)
        policies.sort(key=lambda x: x.priority, reverse=True)
        
        # Apply policies
        for policy in policies:
            await self._apply_policy(capsule_id, state, policy)
            
    def _get_applicable_policies(self, capsule_id: str, state: GovernanceState) -> List[GovernancePolicy]:
        """
        Get policies applicable to a capsule.
        
        Args:
            capsule_id: ID of the capsule
            state: Current governance state
            
        Returns:
            List of applicable policies
        """
        # In a real implementation, we would have more complex logic
        # For simplicity, we'll return all global policies
        
        return [
            policy for policy in self.governance_policies.values()
            if policy.scope == "global" and policy.enabled
        ]
        
    async def _apply_policy(self, capsule_id: str, state: GovernanceState, policy: GovernancePolicy):
        """
        Apply a policy to a capsule.
        
        Args:
            capsule_id: ID of the capsule
            state: Current governance state
            policy: Policy to apply
        """
        logger.info(f"Applying policy {policy.name} to capsule {capsule_id}")
        
        # Check each rule
        for rule in policy.rules:
            # Get attribute value
            attribute = rule["attribute"]
            if attribute == "trust_score":
                value = state.trust_score
            elif attribute == "compliance_score":
                value = state.compliance_score
            elif attribute == "morality_score":
                value = state.morality_score
            elif attribute == "performance_score":
                value = state.performance_score
            else:
                logger.warning(f"Unknown attribute {attribute} in policy {policy.name}")
                continue
                
            # Check condition
            operator = rule["operator"]
            threshold = rule["value"]
            
            if operator == "less_than" and value < threshold:
                # Rule triggered
                action_type = rule["action"]
                reason = rule["reason"]
                
                # Apply action
                await self._apply_action(capsule_id, state, action_type, reason, policy)
                
                # Execute policy actions
                for action_def in policy.actions:
                    await self._execute_policy_action(capsule_id, state, action_def, policy)
                    
    async def _apply_action(self, capsule_id: str, state: GovernanceState, action_type: str, reason: str, policy: GovernancePolicy):
        """
        Apply a governance action to a capsule.
        
        Args:
            capsule_id: ID of the capsule
            state: Current governance state
            action_type: Type of action to apply
            reason: Reason for the action
            policy: Policy triggering the action
        """
        logger.info(f"Applying action {action_type} to capsule {capsule_id}: {reason}")
        
        # Check if action changes state
        old_status = state.status
        new_status = old_status
        
        if action_type == "restrict" and old_status == "active":
            new_status = "restricted"
        elif action_type == "suspend" and old_status in ["active", "restricted"]:
            new_status = "suspended"
        elif action_type == "terminate" and old_status in ["active", "restricted", "suspended"]:
            new_status = "terminated"
        elif action_type == "restore" and old_status in ["restricted", "suspended"]:
            new_status = "active"
            
        # If status changed, update state
        if new_status != old_status:
            state.status = new_status
            
            # Record action
            action = GovernanceAction(
                capsule_id=capsule_id,
                action_type=action_type,
                reason=reason,
                context={
                    "policy_id": policy.policy_id,
                    "policy_name": policy.name,
                    "old_status": old_status
                },
                result=new_status
            )
            
            self.governance_actions.append(action)
            
            # In a real implementation, we would publish the updated state and action
            # For example:
            # await self.event_bus_client.publish("governance.state.updated", state.dict())
            # await self.event_bus_client.publish("governance.action", action.dict())
            
            logger.info(f"Status changed for capsule {capsule_id}: {old_status} -> {new_status}")
            
    async def _execute_policy_action(self, capsule_id: str, state: GovernanceState, action_def: Dict[str, Any], policy: GovernancePolicy):
        """
        Execute a policy action.
        
        Args:
            capsule_id: ID of the capsule
            state: Current governance state
            action_def: Action definition
            policy: Policy triggering the action
        """
        action_name = action_def["name"]
        logger.info(f"Executing policy action {action_name} for capsule {capsule_id}")
        
        # In a real implementation, we would have more complex logic
        # For simplicity, we'll just log the action
        
        if action_name == "notify_admin":
            channel = action_def["parameters"]["channel"]
            priority = action_def["parameters"]["priority"]
            logger.info(f"Notifying admin via {channel} with priority {priority} for capsule {capsule_id}")
            
        elif action_name == "log_violation":
            level = action_def["parameters"]["level"]
            logger.info(f"Logging violation with level {level} for capsule {capsule_id}")
            
    async def get_governance_state(self, capsule_id: str) -> Optional[GovernanceState]:
        """
        Get the governance state for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Governance state, or None if not found
        """
        return self.governance_states.get(capsule_id)
        
    async def get_governance_actions(self, capsule_id: str) -> List[GovernanceAction]:
        """
        Get governance actions for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            List of governance actions
        """
        actions = [
            action for action in self.governance_actions
            if action.capsule_id == capsule_id
        ]
        
        # Sort by timestamp (newest first)
        actions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return actions
        
    async def get_governance_policies(self, scope: Optional[str] = None, scope_id: Optional[str] = None) -> List[GovernancePolicy]:
        """
        Get governance policies.
        
        Args:
            scope: Filter by scope (global, industry, organization, capsule_type)
            scope_id: Filter by scope ID
            
        Returns:
            List of governance policies
        """
        policies = list(self.governance_policies.values())
        
        # Filter by scope
        if scope:
            policies = [policy for policy in policies if policy.scope == scope]
            
        # Filter by scope ID
        if scope_id:
            policies = [policy for policy in policies if policy.scope_id == scope_id]
            
        # Sort by priority (highest first)
        policies.sort(key=lambda x: x.priority, reverse=True)
        
        return policies
        
    async def create_governance_policy(self, policy: GovernancePolicy) -> GovernancePolicy:
        """
        Create a governance policy.
        
        Args:
            policy: Governance policy to create
            
        Returns:
            Created governance policy
        """
        # Store policy
        self.governance_policies[policy.policy_id] = policy
        
        # In a real implementation, we would publish the creation
        # For example:
        # await self.event_bus_client.publish("governance.policy.created", policy.dict())
        
        logger.info(f"Created governance policy {policy.policy_id}: {policy.name}")
        
        return policy
        
    async def update_governance_policy(self, policy_id: str, updates: Dict[str, Any]) -> GovernancePolicy:
        """
        Update a governance policy.
        
        Args:
            policy_id: ID of the policy to update
            updates: Updates to apply
            
        Returns:
            Updated governance policy
        """
        if policy_id not in self.governance_policies:
            raise ValueError(f"Governance policy {policy_id} not found")
            
        # Get policy
        policy = self.governance_policies[policy_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
                
        # Update timestamp
        policy.updated_at = datetime.datetime.now()
        
        # In a real implementation, we would publish the update
        # For example:
        # await self.event_bus_client.publish("governance.policy.updated", policy.dict())
        
        logger.info(f"Updated governance policy {policy_id}: {policy.name}")
        
        return policy
        
    async def delete_governance_policy(self, policy_id: str):
        """
        Delete a governance policy.
        
        Args:
            policy_id: ID of the policy to delete
        """
        if policy_id not in self.governance_policies:
            raise ValueError(f"Governance policy {policy_id} not found")
            
        # Get policy
        policy = self.governance_policies[policy_id]
        
        # Delete policy
        del self.governance_policies[policy_id]
        
        # In a real implementation, we would publish the deletion
        # For example:
        # await self.event_bus_client.publish("governance.policy.deleted", {"policy_id": policy_id})
        
        logger.info(f"Deleted governance policy {policy_id}: {policy.name}")
        
    async def _handle_capsule_created(self, event):
        """
        Handle capsule created event.
        
        Args:
            event: Capsule created event
        """
        capsule_id = event["capsule_id"]
        logger.info(f"Handling capsule created event for capsule {capsule_id}")
        
        # Create initial state
        await self._create_initial_state(capsule_id)
        
    async def _handle_capsule_updated(self, event):
        """
        Handle capsule updated event.
        
        Args:
            event: Capsule updated event
        """
        capsule_id = event["capsule_id"]
        logger.info(f"Handling capsule updated event for capsule {capsule_id}")
        
        # Get state
        state = self.governance_states.get(capsule_id)
        if not state:
            # Create initial state
            state = await self._create_initial_state(capsule_id)
            
        # Assess capsule
        await self._assess_capsule(capsule_id, state)
        
        # Apply policies
        await self._apply_policies(capsule_id, state)
        
    async def _handle_capsule_action(self, event):
        """
        Handle capsule action event.
        
        Args:
            event: Capsule action event
        """
        capsule_id = event["capsule_id"]
        action = event["action"]
        logger.info(f"Handling capsule action event for capsule {capsule_id}: {action}")
        
        # Get state
        state = self.governance_states.get(capsule_id)
        if not state:
            # Create initial state
            state = await self._create_initial_state(capsule_id)
            
        # Check if action is allowed based on status
        if state.status == "terminated":
            # Capsule is terminated, block all actions
            logger.warning(f"Blocking action {action} for terminated capsule {capsule_id}")
            
            # In a real implementation, we would publish a block event
            # For example:
            # await self.event_bus_client.publish("governance.action.blocked", {
            #     "capsule_id": capsule_id,
            #     "action": action,
            #     "reason": "Capsule is terminated"
            # })
            
            return False
            
        elif state.status == "suspended":
            # Capsule is suspended, block most actions
            # In a real implementation, we would have a whitelist of allowed actions
            logger.warning(f"Blocking action {action} for suspended capsule {capsule_id}")
            
            # In a real implementation, we would publish a block event
            # For example:
            # await self.event_bus_client.publish("governance.action.blocked", {
            #     "capsule_id": capsule_id,
            #     "action": action,
            #     "reason": "Capsule is suspended"
            # })
            
            return False
            
        elif state.status == "restricted":
            # Capsule is restricted, check if action is allowed
            # In a real implementation, we would have more complex logic
            logger.info(f"Allowing restricted action {action} for capsule {capsule_id}")
            
            return True
            
        else:
            # Capsule is active, allow action
            logger.info(f"Allowing action {action} for capsule {capsule_id}")
            
            return True
