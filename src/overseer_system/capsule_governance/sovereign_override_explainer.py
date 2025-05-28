"""
Sovereign Override Explainer for the Overseer System.

This module provides the Sovereign Override Explainer that generates human-understandable
explanations for override decisions made by the Overseer System.
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
logger = logging.getLogger("sovereign_override_explainer")

class OverrideDecision(BaseModel):
    """Override decision model."""
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    decision_type: str  # suspend, terminate, modify, restrict
    reason_code: str
    severity: str  # low, medium, high, critical
    context: Dict[str, Any] = Field(default_factory=dict)
    affected_systems: List[str] = Field(default_factory=list)
    override_params: Dict[str, Any] = Field(default_factory=dict)
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExplanationTemplate(BaseModel):
    """Explanation template model."""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reason_code: str
    template: str
    severity_variations: Dict[str, str] = Field(default_factory=dict)
    context_variables: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SovereignOverrideExplainer:
    """
    Sovereign Override Explainer.
    
    This component generates human-understandable explanations for override
    decisions made by the Overseer System.
    """
    
    def __init__(self, event_bus_client=None, mcp_client=None, a2a_client=None):
        """
        Initialize the Sovereign Override Explainer.
        
        Args:
            event_bus_client: Event bus client for publishing and subscribing to events
            mcp_client: MCP client for context-aware communication
            a2a_client: A2A client for agent-based communication
        """
        self.event_bus_client = event_bus_client
        self.mcp_client = mcp_client
        self.a2a_client = a2a_client
        
        # In-memory storage (would be replaced with database in production)
        self.explanation_templates = {}  # reason_code -> ExplanationTemplate
        self.override_decisions = {}  # decision_id -> OverrideDecision
        
        # Initialize default templates
        self._initialize_default_templates()
        
    def _initialize_default_templates(self):
        """Initialize default explanation templates."""
        # Security-related templates
        self._add_template(ExplanationTemplate(
            reason_code="security.unauthorized_access",
            template="The capsule attempted to access {resource} without proper authorization. This could indicate a security breach or misconfiguration.",
            severity_variations={
                "low": "This appears to be a minor permission issue that should be reviewed.",
                "medium": "This unauthorized access attempt requires attention as it may indicate a security vulnerability.",
                "high": "This is a serious security concern that requires immediate investigation.",
                "critical": "This is a critical security breach that has been automatically contained."
            },
            context_variables=["resource", "access_type", "required_permission"]
        ))
        
        self._add_template(ExplanationTemplate(
            reason_code="security.data_exfiltration",
            template="The capsule attempted to transmit sensitive data ({data_type}) to an unauthorized destination ({destination}).",
            severity_variations={
                "low": "This data transfer should be reviewed to ensure it complies with data handling policies.",
                "medium": "This unusual data transfer pattern requires investigation.",
                "high": "This appears to be an unauthorized data exfiltration attempt that has been blocked.",
                "critical": "A critical data breach attempt has been detected and contained."
            },
            context_variables=["data_type", "destination", "data_classification"]
        ))
        
        # Performance-related templates
        self._add_template(ExplanationTemplate(
            reason_code="performance.resource_exhaustion",
            template="The capsule consumed excessive {resource_type} resources ({usage_percentage}% of allocation), potentially affecting system stability.",
            severity_variations={
                "low": "Resource usage is higher than expected but not yet critical.",
                "medium": "Resource consumption is significantly above normal levels and requires attention.",
                "high": "Resource usage has reached concerning levels that may impact other systems.",
                "critical": "Critical resource exhaustion detected that threatens overall system stability."
            },
            context_variables=["resource_type", "usage_percentage", "allocation", "impact_description"]
        ))
        
        self._add_template(ExplanationTemplate(
            reason_code="performance.deadlock",
            template="The capsule entered a deadlock state with {other_capsules} other capsules, preventing progress on {affected_processes}.",
            severity_variations={
                "low": "A minor processing delay was detected and automatically resolved.",
                "medium": "A processing deadlock was detected that required intervention.",
                "high": "A significant system deadlock was detected affecting multiple processes.",
                "critical": "A critical system-wide deadlock was detected and required emergency intervention."
            },
            context_variables=["other_capsules", "affected_processes", "deadlock_duration"]
        ))
        
        # Compliance-related templates
        self._add_template(ExplanationTemplate(
            reason_code="compliance.policy_violation",
            template="The capsule violated {policy_name} by {violation_description}.",
            severity_variations={
                "low": "A minor policy compliance issue was detected that should be reviewed.",
                "medium": "A policy violation was detected that requires attention.",
                "high": "A serious compliance violation was detected that required intervention.",
                "critical": "A critical compliance breach was detected that required immediate containment."
            },
            context_variables=["policy_name", "violation_description", "compliance_impact"]
        ))
        
        self._add_template(ExplanationTemplate(
            reason_code="compliance.regulatory_risk",
            template="The capsule operation posed a regulatory risk related to {regulation} by {risk_description}.",
            severity_variations={
                "low": "A potential regulatory concern was identified that should be reviewed.",
                "medium": "A regulatory compliance issue was detected that requires attention.",
                "high": "A significant regulatory risk was identified that required intervention.",
                "critical": "A critical regulatory violation was prevented through immediate action."
            },
            context_variables=["regulation", "risk_description", "jurisdiction", "potential_penalties"]
        ))
        
        # Ethical-related templates
        self._add_template(ExplanationTemplate(
            reason_code="ethics.bias_detected",
            template="The capsule exhibited potential {bias_type} bias in its {decision_context} decisions.",
            severity_variations={
                "low": "A potential bias pattern was detected that should be reviewed.",
                "medium": "Evidence of algorithmic bias was detected that requires investigation.",
                "high": "Significant algorithmic bias was detected that required intervention.",
                "critical": "Critical ethical violation related to algorithmic bias was prevented."
            },
            context_variables=["bias_type", "decision_context", "affected_groups", "evidence_summary"]
        ))
        
        self._add_template(ExplanationTemplate(
            reason_code="ethics.harmful_content",
            template="The capsule attempted to generate or distribute potentially harmful content related to {content_category}.",
            severity_variations={
                "low": "Content was flagged for review based on our ethical guidelines.",
                "medium": "Potentially inappropriate content was detected and restricted.",
                "high": "Harmful content was detected and blocked from distribution.",
                "critical": "Extremely harmful content was prevented from being generated or distributed."
            },
            context_variables=["content_category", "content_description", "potential_harm"]
        ))
        
        # Operational-related templates
        self._add_template(ExplanationTemplate(
            reason_code="operational.divergence",
            template="The capsule's behavior diverged significantly from its intended function, attempting to {divergent_action} instead of {intended_function}.",
            severity_variations={
                "low": "A minor operational deviation was detected that should be reviewed.",
                "medium": "A significant operational divergence was detected that requires attention.",
                "high": "A serious operational deviation was detected that required intervention.",
                "critical": "A critical operational divergence was detected that required immediate containment."
            },
            context_variables=["divergent_action", "intended_function", "divergence_pattern"]
        ))
        
        self._add_template(ExplanationTemplate(
            reason_code="operational.cascading_failure",
            template="The capsule triggered a potential cascading failure affecting {affected_systems} by {failure_mechanism}.",
            severity_variations={
                "low": "A potential system interaction issue was detected that should be monitored.",
                "medium": "A system interaction issue was detected that could lead to broader failures.",
                "high": "An emerging cascading failure was detected and contained.",
                "critical": "A critical cascading failure was prevented through immediate intervention."
            },
            context_variables=["affected_systems", "failure_mechanism", "potential_impact"]
        ))
        
    def _add_template(self, template: ExplanationTemplate):
        """
        Add an explanation template.
        
        Args:
            template: Explanation template to add
        """
        self.explanation_templates[template.reason_code] = template
        
    async def initialize(self):
        """Initialize the Sovereign Override Explainer."""
        logger.info("Initializing Sovereign Override Explainer")
        
        # In a real implementation, we would initialize connections to external systems
        # For example:
        # await self.event_bus_client.connect()
        # await self.mcp_client.connect()
        # await self.a2a_client.connect()
        
        # Subscribe to events
        # await self.event_bus_client.subscribe("capsule.override.decision", self._handle_override_decision)
        
        logger.info("Sovereign Override Explainer initialized")
        
    async def explain_override(self, decision: OverrideDecision) -> str:
        """
        Generate a human-understandable explanation for an override decision.
        
        Args:
            decision: Override decision to explain
            
        Returns:
            Human-understandable explanation
        """
        logger.info(f"Generating explanation for override decision {decision.decision_id}")
        
        # Store decision
        self.override_decisions[decision.decision_id] = decision
        
        # Get template
        template = self.explanation_templates.get(decision.reason_code)
        
        if not template:
            # No template found, generate generic explanation
            explanation = (
                f"The system detected an issue with capsule {decision.capsule_id} "
                f"that required a {decision.decision_type} override. "
                f"This was due to a {decision.reason_code} condition with {decision.severity} severity."
            )
            
            logger.warning(f"No explanation template found for reason code {decision.reason_code}")
        else:
            # Generate explanation from template
            explanation = template.template
            
            # Replace context variables
            for var in template.context_variables:
                if var in decision.context:
                    explanation = explanation.replace(f"{{{var}}}", str(decision.context[var]))
                    
            # Add severity-specific explanation
            if decision.severity in template.severity_variations:
                explanation += f" {template.severity_variations[decision.severity]}"
                
        # Add affected systems if applicable
        if decision.affected_systems:
            systems_str = ", ".join(decision.affected_systems)
            explanation += f" This decision affects the following systems: {systems_str}."
            
        # Add override parameters if applicable
        if decision.override_params:
            params_str = ", ".join(f"{k}={v}" for k, v in decision.override_params.items())
            explanation += f" Override parameters: {params_str}."
            
        # Update decision with explanation
        decision.explanation = explanation
        
        # In a real implementation, we would publish the explanation
        # For example:
        # await self.event_bus_client.publish("capsule.override.explained", {
        #     "decision_id": decision.decision_id,
        #     "explanation": explanation
        # })
        
        logger.info(f"Generated explanation for override decision {decision.decision_id}")
        
        return explanation
        
    async def get_override_decision(self, decision_id: str) -> Optional[OverrideDecision]:
        """
        Get an override decision by ID.
        
        Args:
            decision_id: ID of the decision
            
        Returns:
            Override decision, or None if not found
        """
        return self.override_decisions.get(decision_id)
        
    async def get_override_decisions(self, capsule_id: Optional[str] = None) -> List[OverrideDecision]:
        """
        Get override decisions.
        
        Args:
            capsule_id: Optional capsule ID filter
            
        Returns:
            List of override decisions
        """
        if capsule_id:
            decisions = [d for d in self.override_decisions.values() if d.capsule_id == capsule_id]
        else:
            decisions = list(self.override_decisions.values())
            
        # Sort by timestamp (newest first)
        decisions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return decisions
        
    async def create_explanation_template(self, template: ExplanationTemplate) -> ExplanationTemplate:
        """
        Create a new explanation template.
        
        Args:
            template: Explanation template to create
            
        Returns:
            Created explanation template
        """
        # Store template
        self.explanation_templates[template.reason_code] = template
        
        # In a real implementation, we would publish the creation
        # For example:
        # await self.event_bus_client.publish("override.template.created", template.dict())
        
        logger.info(f"Created explanation template for reason code {template.reason_code}")
        
        return template
        
    async def update_explanation_template(self, reason_code: str, updates: Dict[str, Any]) -> Optional[ExplanationTemplate]:
        """
        Update an explanation template.
        
        Args:
            reason_code: Reason code of the template to update
            updates: Updates to apply
            
        Returns:
            Updated explanation template, or None if not found
        """
        if reason_code not in self.explanation_templates:
            logger.warning(f"Explanation template for reason code {reason_code} not found")
            return None
            
        template = self.explanation_templates[reason_code]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
                
        # In a real implementation, we would publish the update
        # For example:
        # await self.event_bus_client.publish("override.template.updated", template.dict())
        
        logger.info(f"Updated explanation template for reason code {reason_code}")
        
        return template
        
    async def delete_explanation_template(self, reason_code: str) -> bool:
        """
        Delete an explanation template.
        
        Args:
            reason_code: Reason code of the template to delete
            
        Returns:
            True if deleted, False if not found
        """
        if reason_code not in self.explanation_templates:
            logger.warning(f"Explanation template for reason code {reason_code} not found")
            return False
            
        # Delete template
        del self.explanation_templates[reason_code]
        
        # In a real implementation, we would publish the deletion
        # For example:
        # await self.event_bus_client.publish("override.template.deleted", {"reason_code": reason_code})
        
        logger.info(f"Deleted explanation template for reason code {reason_code}")
        
        return True
        
    async def get_explanation_template(self, reason_code: str) -> Optional[ExplanationTemplate]:
        """
        Get an explanation template by reason code.
        
        Args:
            reason_code: Reason code of the template
            
        Returns:
            Explanation template, or None if not found
        """
        return self.explanation_templates.get(reason_code)
        
    async def get_explanation_templates(self) -> List[ExplanationTemplate]:
        """
        Get all explanation templates.
        
        Returns:
            List of explanation templates
        """
        return list(self.explanation_templates.values())
        
    async def _handle_override_decision(self, event):
        """
        Handle override decision event.
        
        Args:
            event: Override decision event
        """
        # Convert event to OverrideDecision
        decision = OverrideDecision(**event)
        
        logger.info(f"Handling override decision event for decision {decision.decision_id}")
        
        # Generate explanation
        await self.explain_override(decision)
