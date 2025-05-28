"""
Human Intervention Agent Module for Industriverse Workflow Automation Layer

This module implements the Human Intervention Agent, which is responsible for
managing human-in-the-loop interactions within workflows. It handles escalations,
approvals, reviews, and other human touchpoints in automated workflows.

The HumanInterventionAgent class extends the BaseAgent to provide specialized
functionality for human-workflow interaction.
"""

import logging
import asyncio
import json
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta

from pydantic import BaseModel, Field, validator

from .base_agent import BaseAgent, AgentMetadata, AgentConfig, AgentContext, AgentResult, AgentCapability

# Configure logging
logger = logging.getLogger(__name__)


class InterventionType(str, Enum):
    """Enum representing the possible types of human interventions."""
    APPROVAL = "approval"
    REVIEW = "review"
    INPUT = "input"
    DECISION = "decision"
    ESCALATION = "escalation"
    EXCEPTION_HANDLING = "exception_handling"
    QUALITY_CHECK = "quality_check"


class InterventionPriority(str, Enum):
    """Enum representing the possible priorities of human interventions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionStatus(str, Enum):
    """Enum representing the possible statuses of human interventions."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    DELEGATED = "delegated"
    AUTOMATED = "automated"  # When AI decides it can handle without human


class InterventionRequest(BaseModel):
    """Model representing a request for human intervention."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    execution_id: str
    task_id: str
    intervention_type: InterventionType
    priority: InterventionPriority = InterventionPriority.MEDIUM
    title: str
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    status: InterventionStatus = InterventionStatus.PENDING
    context_data: Dict[str, Any] = Field(default_factory=dict)
    options: List[Dict[str, Any]] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)
    trust_threshold: float = 0.7
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('expires_at')
    def expires_at_must_be_future(cls, v, values):
        """Validate that expires_at is in the future."""
        if v and v <= values.get('created_at', datetime.now()):
            raise ValueError('expires_at must be in the future')
        return v


class InterventionResponse(BaseModel):
    """Model representing a response to a human intervention request."""
    intervention_id: str
    responder_id: str
    response_time: datetime = Field(default_factory=datetime.now)
    decision: str
    comments: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    trust_score: float = 1.0  # Human responses are fully trusted by default
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EscalationBid(BaseModel):
    """Model representing a bid from an agent to handle an escalation."""
    agent_id: str
    intervention_id: str
    confidence: float
    capabilities: List[str]
    bid_time: datetime = Field(default_factory=datetime.now)
    estimated_completion_time: Optional[datetime] = None
    proposed_solution: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HumanInterventionAgent(BaseAgent):
    """
    Agent responsible for managing human-in-the-loop interactions within workflows.
    
    This agent handles escalations, approvals, reviews, and other human touchpoints
    in automated workflows, ensuring that human expertise is integrated at the right
    points in the process.
    """
    
    def __init__(self, metadata: Optional[AgentMetadata] = None, config: Optional[AgentConfig] = None):
        """
        Initialize the HumanInterventionAgent.
        
        Args:
            metadata: Optional metadata for the agent
            config: Optional configuration for the agent
        """
        if metadata is None:
            metadata = AgentMetadata(
                id="human_intervention_agent",
                name="Human Intervention Agent",
                description="Manages human-in-the-loop interactions within workflows",
                capabilities=[AgentCapability.HUMAN_INTERVENTION]
            )
        
        super().__init__(metadata, config)
        
        # Store intervention requests
        self.intervention_requests: Dict[str, InterventionRequest] = {}
        
        # Store intervention responses
        self.intervention_responses: Dict[str, InterventionResponse] = {}
        
        # Store escalation bids
        self.escalation_bids: Dict[str, List[EscalationBid]] = {}
        
        # Callbacks
        self.on_intervention_requested: Optional[Callable[[InterventionRequest], None]] = None
        self.on_intervention_completed: Optional[Callable[[InterventionRequest, InterventionResponse], None]] = None
        self.on_intervention_expired: Optional[Callable[[InterventionRequest], None]] = None
        
        # Background tasks
        self.background_tasks = []
        
        logger.info(f"HumanInterventionAgent initialized")
    
    async def _initialize_impl(self) -> bool:
        """
        Implementation of agent initialization.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        # Start background tasks for monitoring interventions
        self._start_expiration_monitor()
        
        return True
    
    def _start_expiration_monitor(self):
        """Start the background task for monitoring intervention expirations."""
        task = asyncio.create_task(self._monitor_intervention_expirations())
        self.background_tasks.append(task)
    
    async def _monitor_intervention_expirations(self):
        """Monitor intervention expirations and handle expired interventions."""
        while True:
            try:
                now = datetime.now()
                
                # Check each intervention for expiration
                for intervention_id, intervention in list(self.intervention_requests.items()):
                    if (intervention.status == InterventionStatus.PENDING and 
                        intervention.expires_at and 
                        now >= intervention.expires_at):
                        
                        # Mark as expired
                        intervention.status = InterventionStatus.EXPIRED
                        
                        # Notify callback if registered
                        if self.on_intervention_expired:
                            self.on_intervention_expired(intervention)
                        
                        logger.info(f"Intervention {intervention_id} expired")
                
                # Sleep for a short time before checking again
                await asyncio.sleep(10)
            
            except Exception as e:
                logger.error(f"Error in intervention expiration monitor: {e}")
                await asyncio.sleep(30)  # Sleep longer on error
    
    async def request_intervention(self, request: Dict[str, Any]) -> str:
        """
        Request a human intervention.
        
        Args:
            request: The intervention request parameters
            
        Returns:
            The ID of the created intervention request
            
        Raises:
            ValueError: If the request is invalid
        """
        try:
            # Create intervention request
            intervention = InterventionRequest(**request)
            
            # Store the request
            self.intervention_requests[intervention.id] = intervention
            
            # Notify callback if registered
            if self.on_intervention_requested:
                self.on_intervention_requested(intervention)
            
            logger.info(f"Created intervention request {intervention.id} for workflow {intervention.workflow_id}")
            return intervention.id
        
        except Exception as e:
            logger.error(f"Failed to create intervention request: {e}")
            raise ValueError(f"Invalid intervention request: {e}")
    
    async def get_intervention(self, intervention_id: str) -> Optional[InterventionRequest]:
        """
        Get an intervention request by ID.
        
        Args:
            intervention_id: The ID of the intervention request
            
        Returns:
            The intervention request if found, None otherwise
        """
        return self.intervention_requests.get(intervention_id)
    
    async def list_interventions(self, 
                               workflow_id: Optional[str] = None, 
                               status: Optional[InterventionStatus] = None,
                               assigned_to: Optional[str] = None) -> List[InterventionRequest]:
        """
        List intervention requests, optionally filtered.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            status: Optional status to filter by
            assigned_to: Optional assignee to filter by
            
        Returns:
            A list of matching intervention requests
        """
        result = []
        
        for intervention in self.intervention_requests.values():
            if (workflow_id is None or intervention.workflow_id == workflow_id) and \
               (status is None or intervention.status == status) and \
               (assigned_to is None or intervention.assigned_to == assigned_to):
                result.append(intervention)
        
        return result
    
    async def submit_response(self, response: Dict[str, Any]) -> bool:
        """
        Submit a response to an intervention request.
        
        Args:
            response: The intervention response parameters
            
        Returns:
            True if the response was submitted successfully, False otherwise
            
        Raises:
            ValueError: If the response is invalid
        """
        try:
            # Create intervention response
            intervention_response = InterventionResponse(**response)
            
            # Check if the intervention exists
            intervention_id = intervention_response.intervention_id
            if intervention_id not in self.intervention_requests:
                logger.warning(f"Attempted to respond to unknown intervention {intervention_id}")
                return False
            
            # Get the intervention
            intervention = self.intervention_requests[intervention_id]
            
            # Check if the intervention is still pending
            if intervention.status != InterventionStatus.PENDING and intervention.status != InterventionStatus.IN_PROGRESS:
                logger.warning(f"Attempted to respond to non-pending intervention {intervention_id} (status: {intervention.status})")
                return False
            
            # Store the response
            self.intervention_responses[intervention_id] = intervention_response
            
            # Update the intervention status
            intervention.status = InterventionStatus.COMPLETED
            
            # Notify callback if registered
            if self.on_intervention_completed:
                self.on_intervention_completed(intervention, intervention_response)
            
            logger.info(f"Submitted response to intervention {intervention_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to submit intervention response: {e}")
            raise ValueError(f"Invalid intervention response: {e}")
    
    async def get_response(self, intervention_id: str) -> Optional[InterventionResponse]:
        """
        Get a response to an intervention request.
        
        Args:
            intervention_id: The ID of the intervention request
            
        Returns:
            The intervention response if found, None otherwise
        """
        return self.intervention_responses.get(intervention_id)
    
    async def cancel_intervention(self, intervention_id: str, reason: Optional[str] = None) -> bool:
        """
        Cancel an intervention request.
        
        Args:
            intervention_id: The ID of the intervention request
            reason: Optional reason for cancellation
            
        Returns:
            True if the intervention was cancelled, False if it wasn't found or couldn't be cancelled
        """
        if intervention_id not in self.intervention_requests:
            logger.warning(f"Attempted to cancel unknown intervention {intervention_id}")
            return False
        
        intervention = self.intervention_requests[intervention_id]
        
        # Check if the intervention can be cancelled
        if intervention.status != InterventionStatus.PENDING and intervention.status != InterventionStatus.IN_PROGRESS:
            logger.warning(f"Attempted to cancel intervention {intervention_id} with status {intervention.status}")
            return False
        
        # Update the intervention status
        intervention.status = InterventionStatus.CANCELLED
        
        # Add cancellation reason to metadata
        if reason:
            intervention.metadata["cancellation_reason"] = reason
        
        logger.info(f"Cancelled intervention {intervention_id}")
        return True
    
    async def assign_intervention(self, intervention_id: str, assignee_id: str) -> bool:
        """
        Assign an intervention request to a specific user.
        
        Args:
            intervention_id: The ID of the intervention request
            assignee_id: The ID of the user to assign to
            
        Returns:
            True if the intervention was assigned, False if it wasn't found or couldn't be assigned
        """
        if intervention_id not in self.intervention_requests:
            logger.warning(f"Attempted to assign unknown intervention {intervention_id}")
            return False
        
        intervention = self.intervention_requests[intervention_id]
        
        # Check if the intervention can be assigned
        if intervention.status != InterventionStatus.PENDING:
            logger.warning(f"Attempted to assign intervention {intervention_id} with status {intervention.status}")
            return False
        
        # Update the intervention
        intervention.assigned_to = assignee_id
        intervention.status = InterventionStatus.IN_PROGRESS
        
        logger.info(f"Assigned intervention {intervention_id} to {assignee_id}")
        return True
    
    async def delegate_intervention(self, intervention_id: str, delegate_to: str, reason: Optional[str] = None) -> bool:
        """
        Delegate an intervention request to another entity.
        
        Args:
            intervention_id: The ID of the intervention request
            delegate_to: The ID of the entity to delegate to
            reason: Optional reason for delegation
            
        Returns:
            True if the intervention was delegated, False if it wasn't found or couldn't be delegated
        """
        if intervention_id not in self.intervention_requests:
            logger.warning(f"Attempted to delegate unknown intervention {intervention_id}")
            return False
        
        intervention = self.intervention_requests[intervention_id]
        
        # Check if the intervention can be delegated
        if intervention.status != InterventionStatus.PENDING and intervention.status != InterventionStatus.IN_PROGRESS:
            logger.warning(f"Attempted to delegate intervention {intervention_id} with status {intervention.status}")
            return False
        
        # Update the intervention status
        intervention.status = InterventionStatus.DELEGATED
        
        # Add delegation info to metadata
        intervention.metadata["delegated_to"] = delegate_to
        if reason:
            intervention.metadata["delegation_reason"] = reason
        
        logger.info(f"Delegated intervention {intervention_id} to {delegate_to}")
        return True
    
    async def automate_intervention(self, intervention_id: str, agent_id: str, solution: Dict[str, Any]) -> bool:
        """
        Mark an intervention as automated by an agent.
        
        Args:
            intervention_id: The ID of the intervention request
            agent_id: The ID of the agent that automated the intervention
            solution: The solution provided by the agent
            
        Returns:
            True if the intervention was automated, False if it wasn't found or couldn't be automated
        """
        if intervention_id not in self.intervention_requests:
            logger.warning(f"Attempted to automate unknown intervention {intervention_id}")
            return False
        
        intervention = self.intervention_requests[intervention_id]
        
        # Check if the intervention can be automated
        if intervention.status != InterventionStatus.PENDING:
            logger.warning(f"Attempted to automate intervention {intervention_id} with status {intervention.status}")
            return False
        
        # Update the intervention status
        intervention.status = InterventionStatus.AUTOMATED
        
        # Add automation info to metadata
        intervention.metadata["automated_by"] = agent_id
        intervention.metadata["automation_solution"] = solution
        
        # Create a synthetic response
        response = InterventionResponse(
            intervention_id=intervention_id,
            responder_id=f"agent:{agent_id}",
            decision="automated",
            comments=f"Automated by agent {agent_id}",
            data=solution,
            trust_score=0.9,  # High but not perfect trust for automated solutions
            metadata={"automated": True, "agent_id": agent_id}
        )
        
        # Store the response
        self.intervention_responses[intervention_id] = response
        
        # Notify callback if registered
        if self.on_intervention_completed:
            self.on_intervention_completed(intervention, response)
        
        logger.info(f"Automated intervention {intervention_id} by agent {agent_id}")
        return True
    
    async def submit_escalation_bid(self, bid: Dict[str, Any]) -> bool:
        """
        Submit a bid from an agent to handle an escalation.
        
        Args:
            bid: The escalation bid parameters
            
        Returns:
            True if the bid was submitted successfully, False otherwise
            
        Raises:
            ValueError: If the bid is invalid
        """
        try:
            # Create escalation bid
            escalation_bid = EscalationBid(**bid)
            
            # Check if the intervention exists
            intervention_id = escalation_bid.intervention_id
            if intervention_id not in self.intervention_requests:
                logger.warning(f"Attempted to bid on unknown intervention {intervention_id}")
                return False
            
            # Get the intervention
            intervention = self.intervention_requests[intervention_id]
            
            # Check if the intervention is still pending
            if intervention.status != InterventionStatus.PENDING:
                logger.warning(f"Attempted to bid on non-pending intervention {intervention_id} (status: {intervention.status})")
                return False
            
            # Initialize bid list if needed
            if intervention_id not in self.escalation_bids:
                self.escalation_bids[intervention_id] = []
            
            # Add the bid
            self.escalation_bids[intervention_id].append(escalation_bid)
            
            logger.info(f"Submitted escalation bid from agent {escalation_bid.agent_id} for intervention {intervention_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to submit escalation bid: {e}")
            raise ValueError(f"Invalid escalation bid: {e}")
    
    async def get_escalation_bids(self, intervention_id: str) -> List[EscalationBid]:
        """
        Get all bids for an intervention.
        
        Args:
            intervention_id: The ID of the intervention request
            
        Returns:
            A list of escalation bids
        """
        return self.escalation_bids.get(intervention_id, [])
    
    async def select_best_bid(self, intervention_id: str) -> Optional[EscalationBid]:
        """
        Select the best bid for an intervention.
        
        Args:
            intervention_id: The ID of the intervention request
            
        Returns:
            The best bid if any, None otherwise
        """
        if intervention_id not in self.escalation_bids or not self.escalation_bids[intervention_id]:
            return None
        
        # Get the intervention
        intervention = self.intervention_requests.get(intervention_id)
        if not intervention:
            return None
        
        # Get all bids
        bids = self.escalation_bids[intervention_id]
        
        # Filter bids by required capabilities
        if intervention.required_capabilities:
            qualified_bids = []
            for bid in bids:
                if all(cap in bid.capabilities for cap in intervention.required_capabilities):
                    qualified_bids.append(bid)
            
            if qualified_bids:
                bids = qualified_bids
        
        # Select the bid with the highest confidence
        return max(bids, key=lambda b: b.confidence)
    
    async def accept_bid(self, intervention_id: str, agent_id: str) -> bool:
        """
        Accept a bid from an agent to handle an escalation.
        
        Args:
            intervention_id: The ID of the intervention request
            agent_id: The ID of the agent whose bid to accept
            
        Returns:
            True if the bid was accepted, False otherwise
        """
        if intervention_id not in self.escalation_bids:
            logger.warning(f"No bids found for intervention {intervention_id}")
            return False
        
        # Find the bid
        bid = None
        for b in self.escalation_bids[intervention_id]:
            if b.agent_id == agent_id:
                bid = b
                break
        
        if not bid:
            logger.warning(f"No bid found from agent {agent_id} for intervention {intervention_id}")
            return False
        
        # Delegate the intervention to the agent
        return await self.delegate_intervention(
            intervention_id=intervention_id,
            delegate_to=agent_id,
            reason=f"Bid accepted with confidence {bid.confidence}"
        )
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        Args:
            context: The execution context for the agent
            
        Returns:
            The result of the agent execution
        """
        # Extract parameters from context
        action = context.variables.get("action", "request_intervention")
        
        if action == "request_intervention":
            # Request a human intervention
            request_data = context.variables.get("request")
            if not request_data:
                return AgentResult(
                    success=False,
                    message="Missing intervention request data",
                    error="request is required for request_intervention action"
                )
            
            try:
                intervention_id = await self.request_intervention(request_data)
                
                return AgentResult(
                    success=True,
                    message=f"Created intervention request {intervention_id}",
                    data={"intervention_id": intervention_id}
                )
            except ValueError as e:
                return AgentResult(
                    success=False,
                    message=f"Failed to create intervention request",
                    error=str(e)
                )
        
        elif action == "get_intervention":
            # Get an intervention request
            intervention_id = context.variables.get("intervention_id")
            if not intervention_id:
                return AgentResult(
                    success=False,
                    message="Missing intervention ID",
                    error="intervention_id is required for get_intervention action"
                )
            
            intervention = await self.get_intervention(intervention_id)
            
            if intervention:
                return AgentResult(
                    success=True,
                    message=f"Retrieved intervention {intervention_id}",
                    data={"intervention": intervention.dict()}
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to get intervention {intervention_id}",
                    error=f"Intervention {intervention_id} not found"
                )
        
        elif action == "list_interventions":
            # List interventions
            workflow_id = context.variables.get("workflow_id")
            status_str = context.variables.get("status")
            assigned_to = context.variables.get("assigned_to")
            
            status = None
            if status_str:
                try:
                    status = InterventionStatus(status_str)
                except ValueError:
                    return AgentResult(
                        success=False,
                        message=f"Invalid intervention status: {status_str}",
                        error=f"Status must be one of: {', '.join(e.value for e in InterventionStatus)}"
                    )
            
            interventions = await self.list_interventions(workflow_id, status, assigned_to)
            
            return AgentResult(
                success=True,
                message=f"Listed {len(interventions)} interventions",
                data={"interventions": [i.dict() for i in interventions]}
            )
        
        elif action == "submit_response":
            # Submit a response to an intervention
            response_data = context.variables.get("response")
            if not response_data:
                return AgentResult(
                    success=False,
                    message="Missing intervention response data",
                    error="response is required for submit_response action"
                )
            
            try:
                success = await self.submit_response(response_data)
                
                if success:
                    return AgentResult(
                        success=True,
                        message=f"Submitted response to intervention {response_data.get('intervention_id')}"
                    )
                else:
                    return AgentResult(
                        success=False,
                        message=f"Failed to submit response to intervention {response_data.get('intervention_id')}",
                        error="Intervention not found or not in a valid state"
                    )
            except ValueError as e:
                return AgentResult(
                    success=False,
                    message=f"Failed to submit intervention response",
                    error=str(e)
                )
        
        elif action == "get_response":
            # Get a response to an intervention
            intervention_id = context.variables.get("intervention_id")
            if not intervention_id:
                return AgentResult(
                    success=False,
                    message="Missing intervention ID",
                    error="intervention_id is required for get_response action"
                )
            
            response = await self.get_response(intervention_id)
            
            if response:
                return AgentResult(
                    success=True,
                    message=f"Retrieved response for intervention {intervention_id}",
                    data={"response": response.dict()}
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to get response for intervention {intervention_id}",
                    error=f"No response found for intervention {intervention_id}"
                )
        
        elif action == "cancel_intervention":
            # Cancel an intervention
            intervention_id = context.variables.get("intervention_id")
            reason = context.variables.get("reason")
            
            if not intervention_id:
                return AgentResult(
                    success=False,
                    message="Missing intervention ID",
                    error="intervention_id is required for cancel_intervention action"
                )
            
            success = await self.cancel_intervention(intervention_id, reason)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Cancelled intervention {intervention_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to cancel intervention {intervention_id}",
                    error="Intervention not found or not in a valid state"
                )
        
        elif action == "assign_intervention":
            # Assign an intervention
            intervention_id = context.variables.get("intervention_id")
            assignee_id = context.variables.get("assignee_id")
            
            if not intervention_id or not assignee_id:
                return AgentResult(
                    success=False,
                    message="Missing intervention ID or assignee ID",
                    error="intervention_id and assignee_id are required for assign_intervention action"
                )
            
            success = await self.assign_intervention(intervention_id, assignee_id)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Assigned intervention {intervention_id} to {assignee_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to assign intervention {intervention_id}",
                    error="Intervention not found or not in a valid state"
                )
        
        elif action == "delegate_intervention":
            # Delegate an intervention
            intervention_id = context.variables.get("intervention_id")
            delegate_to = context.variables.get("delegate_to")
            reason = context.variables.get("reason")
            
            if not intervention_id or not delegate_to:
                return AgentResult(
                    success=False,
                    message="Missing intervention ID or delegate ID",
                    error="intervention_id and delegate_to are required for delegate_intervention action"
                )
            
            success = await self.delegate_intervention(intervention_id, delegate_to, reason)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Delegated intervention {intervention_id} to {delegate_to}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to delegate intervention {intervention_id}",
                    error="Intervention not found or not in a valid state"
                )
        
        elif action == "automate_intervention":
            # Automate an intervention
            intervention_id = context.variables.get("intervention_id")
            agent_id = context.variables.get("agent_id")
            solution = context.variables.get("solution", {})
            
            if not intervention_id or not agent_id:
                return AgentResult(
                    success=False,
                    message="Missing intervention ID or agent ID",
                    error="intervention_id and agent_id are required for automate_intervention action"
                )
            
            success = await self.automate_intervention(intervention_id, agent_id, solution)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Automated intervention {intervention_id} by agent {agent_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to automate intervention {intervention_id}",
                    error="Intervention not found or not in a valid state"
                )
        
        elif action == "submit_escalation_bid":
            # Submit an escalation bid
            bid_data = context.variables.get("bid")
            if not bid_data:
                return AgentResult(
                    success=False,
                    message="Missing escalation bid data",
                    error="bid is required for submit_escalation_bid action"
                )
            
            try:
                success = await self.submit_escalation_bid(bid_data)
                
                if success:
                    return AgentResult(
                        success=True,
                        message=f"Submitted escalation bid for intervention {bid_data.get('intervention_id')}"
                    )
                else:
                    return AgentResult(
                        success=False,
                        message=f"Failed to submit escalation bid for intervention {bid_data.get('intervention_id')}",
                        error="Intervention not found or not in a valid state"
                    )
            except ValueError as e:
                return AgentResult(
                    success=False,
                    message=f"Failed to submit escalation bid",
                    error=str(e)
                )
        
        elif action == "get_escalation_bids":
            # Get escalation bids
            intervention_id = context.variables.get("intervention_id")
            if not intervention_id:
                return AgentResult(
                    success=False,
                    message="Missing intervention ID",
                    error="intervention_id is required for get_escalation_bids action"
                )
            
            bids = await self.get_escalation_bids(intervention_id)
            
            return AgentResult(
                success=True,
                message=f"Retrieved {len(bids)} escalation bids for intervention {intervention_id}",
                data={"bids": [b.dict() for b in bids]}
            )
        
        elif action == "select_best_bid":
            # Select the best bid
            intervention_id = context.variables.get("intervention_id")
            if not intervention_id:
                return AgentResult(
                    success=False,
                    message="Missing intervention ID",
                    error="intervention_id is required for select_best_bid action"
                )
            
            best_bid = await self.select_best_bid(intervention_id)
            
            if best_bid:
                return AgentResult(
                    success=True,
                    message=f"Selected best bid from agent {best_bid.agent_id} for intervention {intervention_id}",
                    data={"best_bid": best_bid.dict()}
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"No suitable bids found for intervention {intervention_id}",
                    error="No bids available or no bids meet the requirements"
                )
        
        elif action == "accept_bid":
            # Accept a bid
            intervention_id = context.variables.get("intervention_id")
            agent_id = context.variables.get("agent_id")
            
            if not intervention_id or not agent_id:
                return AgentResult(
                    success=False,
                    message="Missing intervention ID or agent ID",
                    error="intervention_id and agent_id are required for accept_bid action"
                )
            
            success = await self.accept_bid(intervention_id, agent_id)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Accepted bid from agent {agent_id} for intervention {intervention_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to accept bid from agent {agent_id} for intervention {intervention_id}",
                    error="Bid not found or intervention not in a valid state"
                )
        
        else:
            # Unknown action
            return AgentResult(
                success=False,
                message=f"Unknown action: {action}",
                error=f"Action {action} is not supported"
            )
