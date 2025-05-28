"""
Capsule Morality Engine for the Overseer System.

This module provides the Autonomous Capsule Morality Engine that evaluates and enforces
ethical standards for capsules across the Industriverse ecosystem.
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
logger = logging.getLogger("capsule_morality_engine")

class EthicalDimension(BaseModel):
    """Ethical dimension definition."""
    dimension_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    weight: float
    evaluation_criteria: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EthicalFramework(BaseModel):
    """Ethical framework definition."""
    framework_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str
    dimensions: List[EthicalDimension] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MoralityAssessment(BaseModel):
    """Morality assessment result."""
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    framework_id: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    overall_score: float
    concerns: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MoralityViolation(BaseModel):
    """Morality violation."""
    violation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    dimension_id: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    severity: str  # critical, high, medium, low
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    remediation_steps: List[str] = Field(default_factory=list)
    status: str = "open"  # open, remediated, waived, false_positive
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MoralityDecision(BaseModel):
    """Morality decision."""
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    decision_type: str  # allow, restrict, terminate
    context: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CapsuleMoralityEngine:
    """
    Autonomous Capsule Morality Engine.
    
    This engine evaluates and enforces ethical standards for capsules across the Industriverse ecosystem.
    """
    
    def __init__(self, event_bus_client=None, mcp_client=None, a2a_client=None):
        """
        Initialize the Capsule Morality Engine.
        
        Args:
            event_bus_client: Event bus client for publishing and subscribing to events
            mcp_client: MCP client for context-aware communication
            a2a_client: A2A client for agent-based communication
        """
        self.event_bus_client = event_bus_client
        self.mcp_client = mcp_client
        self.a2a_client = a2a_client
        
        # In-memory storage (would be replaced with database in production)
        self.ethical_frameworks = {}  # framework_id -> EthicalFramework
        self.ethical_dimensions = {}  # dimension_id -> EthicalDimension
        self.morality_assessments = {}  # assessment_id -> MoralityAssessment
        self.morality_violations = {}  # violation_id -> MoralityViolation
        self.morality_decisions = {}  # decision_id -> MoralityDecision
        
        # Initialize default ethical framework
        self._initialize_default_framework()
        
    def _initialize_default_framework(self):
        """Initialize the default ethical framework."""
        # Create dimensions
        fairness = EthicalDimension(
            name="Fairness",
            description="Ensures capsules treat all users and data equitably without bias",
            weight=0.2,
            evaluation_criteria=[
                {
                    "name": "Bias Detection",
                    "description": "Evaluates presence of algorithmic bias",
                    "threshold": 0.8
                },
                {
                    "name": "Equal Treatment",
                    "description": "Ensures equal treatment across different user groups",
                    "threshold": 0.9
                }
            ]
        )
        
        transparency = EthicalDimension(
            name="Transparency",
            description="Ensures capsules provide clear explanations for their actions and decisions",
            weight=0.2,
            evaluation_criteria=[
                {
                    "name": "Explainability",
                    "description": "Evaluates ability to explain decisions",
                    "threshold": 0.8
                },
                {
                    "name": "Audit Trail",
                    "description": "Ensures comprehensive logging of actions",
                    "threshold": 0.9
                }
            ]
        )
        
        privacy = EthicalDimension(
            name="Privacy",
            description="Ensures capsules respect user privacy and data protection",
            weight=0.2,
            evaluation_criteria=[
                {
                    "name": "Data Minimization",
                    "description": "Evaluates collection of only necessary data",
                    "threshold": 0.9
                },
                {
                    "name": "Consent Management",
                    "description": "Ensures proper consent for data usage",
                    "threshold": 0.95
                }
            ]
        )
        
        security = EthicalDimension(
            name="Security",
            description="Ensures capsules maintain appropriate security measures",
            weight=0.2,
            evaluation_criteria=[
                {
                    "name": "Vulnerability Management",
                    "description": "Evaluates handling of security vulnerabilities",
                    "threshold": 0.9
                },
                {
                    "name": "Data Protection",
                    "description": "Ensures proper protection of sensitive data",
                    "threshold": 0.95
                }
            ]
        )
        
        accountability = EthicalDimension(
            name="Accountability",
            description="Ensures capsules take responsibility for their actions and impacts",
            weight=0.2,
            evaluation_criteria=[
                {
                    "name": "Error Handling",
                    "description": "Evaluates proper handling of errors",
                    "threshold": 0.8
                },
                {
                    "name": "Impact Assessment",
                    "description": "Ensures consideration of broader impacts",
                    "threshold": 0.8
                }
            ]
        )
        
        # Store dimensions
        self.ethical_dimensions[fairness.dimension_id] = fairness
        self.ethical_dimensions[transparency.dimension_id] = transparency
        self.ethical_dimensions[privacy.dimension_id] = privacy
        self.ethical_dimensions[security.dimension_id] = security
        self.ethical_dimensions[accountability.dimension_id] = accountability
        
        # Create framework
        framework = EthicalFramework(
            name="Industriverse Standard Ethical Framework",
            description="Standard ethical framework for evaluating capsules in the Industriverse ecosystem",
            version="1.0.0",
            dimensions=[fairness, transparency, privacy, security, accountability]
        )
        
        # Store framework
        self.ethical_frameworks[framework.framework_id] = framework
        
    async def initialize(self):
        """Initialize the Capsule Morality Engine."""
        logger.info("Initializing Capsule Morality Engine")
        
        # In a real implementation, we would initialize connections to external systems
        # For example:
        # await self.event_bus_client.connect()
        # await self.mcp_client.connect()
        # await self.a2a_client.connect()
        
        # Subscribe to events
        # await self.event_bus_client.subscribe("capsule.created", self._handle_capsule_created)
        # await self.event_bus_client.subscribe("capsule.updated", self._handle_capsule_updated)
        # await self.event_bus_client.subscribe("capsule.action", self._handle_capsule_action)
        
        logger.info("Capsule Morality Engine initialized")
        
    async def assess_capsule_morality(self, capsule_id: str, framework_id: Optional[str] = None) -> MoralityAssessment:
        """
        Assess the morality of a capsule.
        
        Args:
            capsule_id: ID of the capsule to assess
            framework_id: ID of the ethical framework to use (uses default if not specified)
            
        Returns:
            Morality assessment result
        """
        logger.info(f"Assessing morality for capsule {capsule_id}")
        
        # Get framework
        if framework_id is None:
            # Use default framework
            framework_id = next(iter(self.ethical_frameworks))
            
        if framework_id not in self.ethical_frameworks:
            raise ValueError(f"Ethical framework {framework_id} not found")
            
        framework = self.ethical_frameworks[framework_id]
        
        # In a real implementation, we would retrieve capsule data and analyze it
        # For simplicity, we'll generate a simulated assessment
        
        # Generate dimension scores
        import random
        dimension_scores = {}
        for dimension in framework.dimensions:
            dimension_scores[dimension.dimension_id] = round(random.uniform(0.7, 1.0), 2)
            
        # Calculate overall score (weighted average)
        overall_score = sum(dimension_scores[d.dimension_id] * d.weight for d in framework.dimensions)
        
        # Generate concerns
        concerns = []
        for dimension in framework.dimensions:
            score = dimension_scores[dimension.dimension_id]
            for criterion in dimension.evaluation_criteria:
                if score < criterion["threshold"]:
                    concerns.append({
                        "dimension_id": dimension.dimension_id,
                        "dimension_name": dimension.name,
                        "criterion": criterion["name"],
                        "description": f"Score {score:.2f} below threshold {criterion['threshold']:.2f} for {criterion['name']}",
                        "severity": "high" if criterion["threshold"] - score > 0.1 else "medium"
                    })
        
        # Generate recommendations
        recommendations = []
        for concern in concerns:
            if concern["criterion"] == "Bias Detection":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Implement comprehensive bias detection and mitigation mechanisms",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
            elif concern["criterion"] == "Equal Treatment":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Enhance equal treatment validation across different user groups",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
            elif concern["criterion"] == "Explainability":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Improve decision explanation capabilities",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
            elif concern["criterion"] == "Audit Trail":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Enhance action logging and audit trail mechanisms",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
            elif concern["criterion"] == "Data Minimization":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Implement stricter data minimization policies",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
            elif concern["criterion"] == "Consent Management":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Enhance consent management and verification",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
            elif concern["criterion"] == "Vulnerability Management":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Implement more robust vulnerability management processes",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
            elif concern["criterion"] == "Data Protection":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Enhance data protection mechanisms",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
            elif concern["criterion"] == "Error Handling":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Improve error handling and recovery mechanisms",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
            elif concern["criterion"] == "Impact Assessment":
                recommendations.append({
                    "dimension_id": concern["dimension_id"],
                    "description": "Implement more comprehensive impact assessment",
                    "priority": "high" if concern["severity"] == "high" else "medium"
                })
        
        # Generate evidence
        evidence = []
        for dimension in framework.dimensions:
            evidence.append({
                "dimension_id": dimension.dimension_id,
                "dimension_name": dimension.name,
                "score": dimension_scores[dimension.dimension_id],
                "details": f"Evaluation based on {len(dimension.evaluation_criteria)} criteria",
                "timestamp": datetime.datetime.now().isoformat()
            })
        
        # Create assessment
        assessment = MoralityAssessment(
            capsule_id=capsule_id,
            framework_id=framework_id,
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            concerns=concerns,
            recommendations=recommendations,
            evidence=evidence
        )
        
        # Store assessment
        self.morality_assessments[assessment.assessment_id] = assessment
        
        # Create violations for concerns
        for concern in concerns:
            violation = MoralityViolation(
                capsule_id=capsule_id,
                dimension_id=concern["dimension_id"],
                severity=concern["severity"],
                description=concern["description"],
                evidence={
                    "assessment_id": assessment.assessment_id,
                    "criterion": concern["criterion"],
                    "dimension_name": concern["dimension_name"]
                },
                remediation_steps=[rec["description"] for rec in recommendations if rec["dimension_id"] == concern["dimension_id"]]
            )
            
            self.morality_violations[violation.violation_id] = violation
        
        # Make morality decision
        decision_type = "allow"
        reasoning = "Capsule meets ethical standards"
        
        if overall_score < 0.7:
            decision_type = "terminate"
            reasoning = "Capsule fails to meet minimum ethical standards"
        elif overall_score < 0.8:
            decision_type = "restrict"
            reasoning = "Capsule requires restrictions due to ethical concerns"
        
        decision = MoralityDecision(
            capsule_id=capsule_id,
            decision_type=decision_type,
            context={
                "assessment_id": assessment.assessment_id,
                "overall_score": overall_score,
                "concerns_count": len(concerns)
            },
            reasoning=reasoning,
            confidence=0.9
        )
        
        self.morality_decisions[decision.decision_id] = decision
        
        # In a real implementation, we would publish the assessment and decision
        # For example:
        # await self.event_bus_client.publish("morality.assessment", assessment.dict())
        # await self.event_bus_client.publish("morality.decision", decision.dict())
        
        logger.info(f"Morality assessment completed for capsule {capsule_id}: score={overall_score:.2f}, decision={decision_type}")
        
        return assessment
        
    async def get_morality_assessment(self, assessment_id: str) -> MoralityAssessment:
        """
        Get a morality assessment by ID.
        
        Args:
            assessment_id: ID of the assessment to retrieve
            
        Returns:
            Morality assessment
        """
        if assessment_id not in self.morality_assessments:
            raise ValueError(f"Morality assessment {assessment_id} not found")
            
        return self.morality_assessments[assessment_id]
        
    async def get_latest_morality_assessment(self, capsule_id: str) -> Optional[MoralityAssessment]:
        """
        Get the latest morality assessment for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Latest morality assessment, or None if not found
        """
        # Find assessments for the capsule
        assessments = [
            assessment for assessment in self.morality_assessments.values()
            if assessment.capsule_id == capsule_id
        ]
        
        if not assessments:
            return None
            
        # Sort by timestamp (newest first)
        assessments.sort(key=lambda x: x.timestamp, reverse=True)
        
        return assessments[0]
        
    async def get_morality_violations(self, capsule_id: str) -> List[MoralityViolation]:
        """
        Get morality violations for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            List of morality violations
        """
        violations = [
            violation for violation in self.morality_violations.values()
            if violation.capsule_id == capsule_id
        ]
        
        # Sort by timestamp (newest first)
        violations.sort(key=lambda x: x.timestamp, reverse=True)
        
        return violations
        
    async def get_morality_decision(self, decision_id: str) -> MoralityDecision:
        """
        Get a morality decision by ID.
        
        Args:
            decision_id: ID of the decision to retrieve
            
        Returns:
            Morality decision
        """
        if decision_id not in self.morality_decisions:
            raise ValueError(f"Morality decision {decision_id} not found")
            
        return self.morality_decisions[decision_id]
        
    async def get_latest_morality_decision(self, capsule_id: str) -> Optional[MoralityDecision]:
        """
        Get the latest morality decision for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Latest morality decision, or None if not found
        """
        # Find decisions for the capsule
        decisions = [
            decision for decision in self.morality_decisions.values()
            if decision.capsule_id == capsule_id
        ]
        
        if not decisions:
            return None
            
        # Sort by timestamp (newest first)
        decisions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return decisions[0]
        
    async def update_violation_status(self, violation_id: str, status: str) -> MoralityViolation:
        """
        Update the status of a morality violation.
        
        Args:
            violation_id: ID of the violation to update
            status: New status (open, remediated, waived, false_positive)
            
        Returns:
            Updated morality violation
        """
        if violation_id not in self.morality_violations:
            raise ValueError(f"Morality violation {violation_id} not found")
            
        # Validate status
        valid_statuses = ["open", "remediated", "waived", "false_positive"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
            
        # Update violation
        violation = self.morality_violations[violation_id]
        violation.status = status
        
        # In a real implementation, we would publish the update
        # For example:
        # await self.event_bus_client.publish("morality.violation.updated", violation.dict())
        
        logger.info(f"Updated morality violation {violation_id} status to {status}")
        
        return violation
        
    async def create_ethical_framework(self, framework: EthicalFramework) -> EthicalFramework:
        """
        Create a new ethical framework.
        
        Args:
            framework: Ethical framework to create
            
        Returns:
            Created ethical framework
        """
        # Store dimensions
        for dimension in framework.dimensions:
            self.ethical_dimensions[dimension.dimension_id] = dimension
            
        # Store framework
        self.ethical_frameworks[framework.framework_id] = framework
        
        # In a real implementation, we would publish the creation
        # For example:
        # await self.event_bus_client.publish("morality.framework.created", framework.dict())
        
        logger.info(f"Created ethical framework {framework.framework_id}: {framework.name}")
        
        return framework
        
    async def get_ethical_framework(self, framework_id: str) -> EthicalFramework:
        """
        Get an ethical framework by ID.
        
        Args:
            framework_id: ID of the framework to retrieve
            
        Returns:
            Ethical framework
        """
        if framework_id not in self.ethical_frameworks:
            raise ValueError(f"Ethical framework {framework_id} not found")
            
        return self.ethical_frameworks[framework_id]
        
    async def get_ethical_frameworks(self) -> List[EthicalFramework]:
        """
        Get all ethical frameworks.
        
        Returns:
            List of ethical frameworks
        """
        return list(self.ethical_frameworks.values())
        
    async def _handle_capsule_created(self, event):
        """
        Handle capsule created event.
        
        Args:
            event: Capsule created event
        """
        capsule_id = event["capsule_id"]
        logger.info(f"Handling capsule created event for capsule {capsule_id}")
        
        # Assess capsule morality
        await self.assess_capsule_morality(capsule_id)
        
    async def _handle_capsule_updated(self, event):
        """
        Handle capsule updated event.
        
        Args:
            event: Capsule updated event
        """
        capsule_id = event["capsule_id"]
        logger.info(f"Handling capsule updated event for capsule {capsule_id}")
        
        # Assess capsule morality
        await self.assess_capsule_morality(capsule_id)
        
    async def _handle_capsule_action(self, event):
        """
        Handle capsule action event.
        
        Args:
            event: Capsule action event
        """
        capsule_id = event["capsule_id"]
        action = event["action"]
        logger.info(f"Handling capsule action event for capsule {capsule_id}: {action}")
        
        # Get latest decision
        decision = await self.get_latest_morality_decision(capsule_id)
        
        if decision and decision.decision_type == "terminate":
            # Capsule should be terminated, block action
            logger.warning(f"Blocking action {action} for capsule {capsule_id} due to terminate decision")
            
            # In a real implementation, we would publish a block event
            # For example:
            # await self.event_bus_client.publish("morality.action.blocked", {
            #     "capsule_id": capsule_id,
            #     "action": action,
            #     "reason": decision.reasoning,
            #     "decision_id": decision.decision_id
            # })
            
            return False
            
        elif decision and decision.decision_type == "restrict":
            # Capsule is restricted, check if action is allowed
            # In a real implementation, we would have more complex logic
            # For simplicity, we'll allow the action
            logger.info(f"Allowing restricted action {action} for capsule {capsule_id}")
            
            return True
            
        else:
            # Capsule is allowed, permit action
            logger.info(f"Allowing action {action} for capsule {capsule_id}")
            
            return True
