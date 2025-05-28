"""
A2A Integration Framework for the Overseer System.

This module provides integration with the Agent-to-Agent (A2A) Protocol,
enabling agent-based communication between Overseer System components
and external agent ecosystems.
"""

import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class A2AAgentCard(BaseModel):
    """Agent Card for A2A Protocol."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str
    provider: str
    capabilities: List[str]
    industry_tags: List[str] = []  # Industry-specific metadata
    priority: int = 0  # Task prioritization
    api_url: str
    auth_type: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class A2ATask(BaseModel):
    """Task definition for A2A Protocol."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    input_data: Dict[str, Any]
    status: str = "pending"
    priority: int = 0
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class A2ATaskResult(BaseModel):
    """Task result for A2A Protocol."""
    task_id: str
    agent_id: str
    status: str
    output_data: Dict[str, Any]
    error: Optional[str] = None
    completed_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class A2APart(BaseModel):
    """Part definition for A2A Protocol."""
    part_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    mime_type: str
    data: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)

class A2ABid(BaseModel):
    """Bid definition for A2A Protocol."""
    bid_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    agent_id: str
    bid_amount: float
    confidence_score: float
    estimated_completion_time: int  # in seconds
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class A2AWorkflowTemplate(BaseModel):
    """Workflow template for A2A Protocol."""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    steps: List[Dict[str, Any]]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class A2AProtocolBridge:
    """Bridge for handling A2A protocol communication."""
    
    def __init__(self, agent_card: A2AAgentCard, event_bus_client=None):
        """
        Initialize the A2A Protocol Bridge.
        
        Args:
            agent_card: Agent card for this agent
            event_bus_client: Client for the event bus (Kafka)
        """
        self.agent_card = agent_card
        self.event_bus_client = event_bus_client
        self.task_handlers = {}
        self.active_tasks = {}
        
    def register_task_handler(self, task_type: str, handler_func):
        """
        Register a handler function for a specific task type.
        
        Args:
            task_type: Type of task to handle
            handler_func: Function to call when task is received
        """
        self.task_handlers[task_type] = handler_func
        
    async def register_agent(self) -> bool:
        """
        Register this agent with the A2A registry.
        
        Returns:
            True if registered successfully, False otherwise
        """
        if not self.event_bus_client:
            print(f"Warning: No event bus client configured, agent {self.agent_card.agent_id} not registered")
            return False
            
        try:
            # In production, this would use the actual Kafka client
            topic = "a2a.registry"
            await self.event_bus_client.send(
                topic=topic,
                value=self.agent_card.json(),
                key=self.agent_card.agent_id
            )
            return True
        except Exception as e:
            print(f"Error registering agent: {e}")
            return False
            
    async def create_task(
        self, 
        target_agent_id: str, 
        name: str, 
        description: str, 
        input_data: Dict[str, Any],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> A2ATask:
        """
        Create a new task for another agent.
        
        Args:
            target_agent_id: ID of the target agent
            name: Task name
            description: Task description
            input_data: Input data for the task
            input_schema: Schema for the input data
            output_schema: Schema for the expected output
            priority: Task priority
            metadata: Additional metadata
            
        Returns:
            New task object
        """
        task = A2ATask(
            agent_id=target_agent_id,
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            input_data=input_data,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Store task in active tasks
        self.active_tasks[task.task_id] = task
        
        # Send task to target agent
        if self.event_bus_client:
            try:
                topic = f"a2a.tasks.{target_agent_id}"
                await self.event_bus_client.send(
                    topic=topic,
                    value=task.json(),
                    key=task.task_id
                )
            except Exception as e:
                print(f"Error sending task: {e}")
                
        return task
        
    async def submit_bid(self, task_id: str, bid_amount: float, confidence_score: float, estimated_completion_time: int) -> A2ABid:
        """
        Submit a bid for a task.
        
        Args:
            task_id: ID of the task to bid on
            bid_amount: Bid amount
            confidence_score: Confidence score (0-1)
            estimated_completion_time: Estimated completion time in seconds
            
        Returns:
            New bid object
        """
        bid = A2ABid(
            task_id=task_id,
            agent_id=self.agent_card.agent_id,
            bid_amount=bid_amount,
            confidence_score=confidence_score,
            estimated_completion_time=estimated_completion_time
        )
        
        # Send bid
        if self.event_bus_client:
            try:
                topic = f"a2a.bids.{task_id}"
                await self.event_bus_client.send(
                    topic=topic,
                    value=bid.json(),
                    key=bid.bid_id
                )
            except Exception as e:
                print(f"Error sending bid: {e}")
                
        return bid
        
    async def handle_task(self, task_json: str) -> bool:
        """
        Handle an incoming task.
        
        Args:
            task_json: JSON string of the task
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            task = A2ATask.parse_raw(task_json)
            
            # Find and call the appropriate handler
            handler = self.task_handlers.get(task.name)
            if handler:
                result = await handler(task)
                
                # Send task result
                await self.send_task_result(task.task_id, "completed", result)
                return True
            else:
                print(f"No handler registered for task type: {task.name}")
                await self.send_task_result(task.task_id, "rejected", {"error": f"No handler for {task.name}"})
                return False
                
        except Exception as e:
            print(f"Error handling task: {e}")
            return False
            
    async def send_task_result(self, task_id: str, status: str, output_data: Dict[str, Any], error: Optional[str] = None) -> bool:
        """
        Send a task result.
        
        Args:
            task_id: ID of the task
            status: Task status (completed, failed, etc.)
            output_data: Output data from the task
            error: Error message (if any)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.event_bus_client:
            print(f"Warning: No event bus client configured, task result for {task_id} not sent")
            return False
            
        try:
            # Create task result
            result = A2ATaskResult(
                task_id=task_id,
                agent_id=self.agent_card.agent_id,
                status=status,
                output_data=output_data,
                error=error
            )
            
            # Send result
            topic = f"a2a.results.{task_id}"
            await self.event_bus_client.send(
                topic=topic,
                value=result.json(),
                key=task_id
            )
            return True
        except Exception as e:
            print(f"Error sending task result: {e}")
            return False

class A2AAgentSchema:
    """Schema definitions for A2A agent capabilities and tasks."""
    
    # Agent capabilities
    CAPABILITY_TASK_EXECUTION = "task.execution"
    CAPABILITY_BIDDING = "task.bidding"
    CAPABILITY_WORKFLOW = "workflow.execution"
    CAPABILITY_LEARNING = "agent.learning"
    CAPABILITY_COLLABORATION = "agent.collaboration"
    
    # Task types
    TASK_PROCESS_DATA = "process.data"
    TASK_ANALYZE_DATA = "analyze.data"
    TASK_GENERATE_CONTENT = "generate.content"
    TASK_EXECUTE_WORKFLOW = "execute.workflow"
    TASK_MONITOR_SYSTEM = "monitor.system"
    TASK_OPTIMIZE_RESOURCE = "optimize.resource"
    TASK_DETECT_ANOMALY = "detect.anomaly"
    TASK_SCHEDULE_MAINTENANCE = "schedule.maintenance"
    TASK_VALIDATE_COMPLIANCE = "validate.compliance"
    TASK_SIMULATE_SCENARIO = "simulate.scenario"
    
    # Industry tags
    INDUSTRY_MANUFACTURING = "industry.manufacturing"
    INDUSTRY_HEALTHCARE = "industry.healthcare"
    INDUSTRY_CONSTRUCTION = "industry.construction"
    INDUSTRY_RETAIL = "industry.retail"
    INDUSTRY_FIELD_SERVICE = "industry.field_service"
    INDUSTRY_FRANCHISE = "industry.franchise"
    INDUSTRY_DEFENSE = "industry.defense"
    INDUSTRY_AEROSPACE = "industry.aerospace"
    INDUSTRY_DATA_CENTER = "industry.data_center"
    INDUSTRY_EDGE_COMPUTING = "industry.edge_computing"
    INDUSTRY_AI = "industry.ai"
    INDUSTRY_IOT = "industry.iot"
    INDUSTRY_PRECISION_MANUFACTURING = "industry.precision_manufacturing"

class A2AIntegrationManager:
    """Manager for A2A integration across the Overseer System."""
    
    def __init__(
        self, 
        agent_name: str, 
        agent_description: str, 
        capabilities: List[str],
        industry_tags: List[str],
        api_url: str,
        event_bus_client=None
    ):
        """
        Initialize the A2A Integration Manager.
        
        Args:
            agent_name: Name of the agent
            agent_description: Description of the agent
            capabilities: List of agent capabilities
            industry_tags: List of industry tags
            api_url: URL for the agent's API
            event_bus_client: Client for the event bus (Kafka)
        """
        self.agent_card = A2AAgentCard(
            name=agent_name,
            description=agent_description,
            version="1.0.0",
            provider="Industriverse",
            capabilities=capabilities,
            industry_tags=industry_tags,
            api_url=api_url,
            auth_type="bearer"
        )
        self.protocol_bridge = A2AProtocolBridge(self.agent_card, event_bus_client)
        self.schema = A2AAgentSchema
        
    async def initialize(self):
        """Initialize the A2A integration."""
        # Register agent
        await self.protocol_bridge.register_agent()
        
        # Register for relevant topics
        if self.protocol_bridge.event_bus_client:
            # In production, this would subscribe to Kafka topics
            pass
            
    def register_task_handler(self, task_type: str, handler_func):
        """
        Register a handler function for a specific task type.
        
        Args:
            task_type: Type of task to handle
            handler_func: Function to call when task is received
        """
        self.protocol_bridge.register_task_handler(task_type, handler_func)
        
    async def create_task(
        self, 
        target_agent_id: str, 
        task_type: str, 
        description: str, 
        input_data: Dict[str, Any],
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> A2ATask:
        """
        Create a new task for another agent.
        
        Args:
            target_agent_id: ID of the target agent
            task_type: Type of task
            description: Task description
            input_data: Input data for the task
            priority: Task priority
            metadata: Additional metadata
            
        Returns:
            New task object
        """
        # Define schemas based on task type
        input_schema = {"type": "object"}
        output_schema = {"type": "object"}
        
        return await self.protocol_bridge.create_task(
            target_agent_id=target_agent_id,
            name=task_type,
            description=description,
            input_data=input_data,
            input_schema=input_schema,
            output_schema=output_schema,
            priority=priority,
            metadata=metadata
        )
        
    async def submit_bid(self, task_id: str, bid_amount: float, confidence_score: float, estimated_completion_time: int) -> A2ABid:
        """
        Submit a bid for a task.
        
        Args:
            task_id: ID of the task to bid on
            bid_amount: Bid amount
            confidence_score: Confidence score (0-1)
            estimated_completion_time: Estimated completion time in seconds
            
        Returns:
            New bid object
        """
        return await self.protocol_bridge.submit_bid(
            task_id=task_id,
            bid_amount=bid_amount,
            confidence_score=confidence_score,
            estimated_completion_time=estimated_completion_time
        )
        
    async def create_workflow_template(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> A2AWorkflowTemplate:
        """
        Create a new workflow template.
        
        Args:
            name: Template name
            description: Template description
            steps: Workflow steps
            input_schema: Schema for the input data
            output_schema: Schema for the expected output
            metadata: Additional metadata
            
        Returns:
            New workflow template
        """
        template = A2AWorkflowTemplate(
            name=name,
            description=description,
            steps=steps,
            input_schema=input_schema,
            output_schema=output_schema,
            metadata=metadata or {}
        )
        
        # In production, this would store the template in a database
        
        return template
