"""
A2A Protocol Bridge for the Overseer System.

This module provides a bridge for A2A protocol communication between Overseer System components
and external agent ecosystems.
"""

import json
import uuid
import datetime
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from pydantic import BaseModel, Field

from .a2a_agent_schema import A2ATaskType, A2ACapabilityType, A2AIndustryTag

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
        self.logger = logging.getLogger("a2a_protocol_bridge")
        
    async def initialize(self):
        """Initialize the A2A Protocol Bridge."""
        if not self.event_bus_client:
            self.logger.warning("No event bus client provided, A2A bridge will operate in local-only mode")
            return
            
        # Register agent
        await self.register_agent()
        
        # Subscribe to A2A topics
        await self._subscribe_to_topics()
        
    async def _subscribe_to_topics(self):
        """Subscribe to relevant A2A topics."""
        if not self.event_bus_client:
            return
            
        # Subscribe to tasks for this agent
        agent_topic = f"a2a.tasks.{self.agent_card.agent_id}"
        await self.event_bus_client.subscribe(agent_topic, self._handle_a2a_message)
        
        # Subscribe to task results for active tasks
        for task_id in self.active_tasks.keys():
            result_topic = f"a2a.results.{task_id}"
            await self.event_bus_client.subscribe(result_topic, self._handle_a2a_message)
        
    async def _handle_a2a_message(self, topic: str, value: Any, key: Optional[str]):
        """
        Handle an incoming A2A message.
        
        Args:
            topic: Kafka topic
            value: Message value
            key: Message key
        """
        try:
            if topic.startswith("a2a.tasks."):
                # Handle task
                task = A2ATask.parse_obj(value)
                await self.handle_task(task)
            elif topic.startswith("a2a.results."):
                # Handle task result
                result = A2ATaskResult.parse_obj(value)
                await self._handle_task_result(result)
            elif topic.startswith("a2a.bids."):
                # Handle bid
                bid = A2ABid.parse_obj(value)
                await self._handle_bid(bid)
                
        except Exception as e:
            self.logger.error(f"Error handling A2A message: {e}")
        
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
            self.logger.warning(f"No event bus client configured, agent {self.agent_card.agent_id} not registered")
            return False
            
        try:
            # Send agent card to registry topic
            topic = "a2a.registry"
            return await self.event_bus_client.send(
                topic=topic,
                value=self.agent_card.dict(),
                key=self.agent_card.agent_id
            )
        except Exception as e:
            self.logger.error(f"Error registering agent: {e}")
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
                    value=task.dict(),
                    key=task.task_id
                )
                
                # Subscribe to results topic
                result_topic = f"a2a.results.{task.task_id}"
                await self.event_bus_client.subscribe(result_topic, self._handle_a2a_message)
            except Exception as e:
                self.logger.error(f"Error sending task: {e}")
                
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
                    value=bid.dict(),
                    key=bid.bid_id
                )
            except Exception as e:
                self.logger.error(f"Error sending bid: {e}")
                
        return bid
        
    async def handle_task(self, task: A2ATask) -> bool:
        """
        Handle an incoming task.
        
        Args:
            task: Task to handle
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # Find and call the appropriate handler
            handler = self.task_handlers.get(task.name)
            if handler:
                result = await handler(task)
                
                # Send task result
                await self.send_task_result(task.task_id, "completed", result)
                return True
            else:
                self.logger.warning(f"No handler registered for task type: {task.name}")
                await self.send_task_result(task.task_id, "rejected", {"error": f"No handler for {task.name}"})
                return False
                
        except Exception as e:
            self.logger.error(f"Error handling task: {e}")
            await self.send_task_result(task.task_id, "failed", {"error": str(e)})
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
            self.logger.warning(f"No event bus client configured, task result for {task_id} not sent")
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
            return await self.event_bus_client.send(
                topic=topic,
                value=result.dict(),
                key=task_id
            )
        except Exception as e:
            self.logger.error(f"Error sending task result: {e}")
            return False
            
    async def _handle_task_result(self, result: A2ATaskResult):
        """
        Handle a task result.
        
        Args:
            result: Task result
        """
        # Remove task from active tasks
        if result.task_id in self.active_tasks:
            del self.active_tasks[result.task_id]
            
            # Unsubscribe from results topic
            if self.event_bus_client:
                result_topic = f"a2a.results.{result.task_id}"
                await self.event_bus_client.unsubscribe(result_topic)
                
    async def _handle_bid(self, bid: A2ABid):
        """
        Handle a bid.
        
        Args:
            bid: Bid
        """
        # This would be implemented by services that use bidding
        pass
