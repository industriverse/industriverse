"""
AlphaEvolve Prompt Broker for the Overseer System.

This module provides comprehensive prompt brokering capabilities for the Overseer System,
enabling the generation of optimized prompts based on deployment context, constraints,
and feedback history.

The AlphaEvolve Prompt Broker is a critical component of the Capsule Evolution phase,
providing mechanisms for continuous improvement of capsule prompts.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import os
import time
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any, Set

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from pydantic import BaseModel, Field, validator

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
logger = logging.getLogger("alphaevolve_prompt_broker")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="alphaevolve-prompt-broker"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="alphaevolve-prompt-broker",
    auto_offset_reset="earliest"
)

# Data models
class DeploymentContext(BaseModel):
    """Model for deployment context."""
    context_id: str = Field(..., description="Unique context identifier")
    industry: str = Field(..., description="Industry context")
    environment: str = Field(..., description="Deployment environment")
    user_roles: List[str] = Field(default_factory=list, description="User roles")
    system_capabilities: List[str] = Field(default_factory=list, description="System capabilities")
    integration_points: List[str] = Field(default_factory=list, description="Integration points")
    data_sources: List[str] = Field(default_factory=list, description="Available data sources")
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")
    performance_constraints: Dict[str, Any] = Field(default_factory=dict, description="Performance constraints")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PromptConstraint(BaseModel):
    """Model for prompt constraints."""
    constraint_id: str = Field(..., description="Unique constraint identifier")
    name: str = Field(..., description="Constraint name")
    description: str = Field(..., description="Constraint description")
    constraint_type: str = Field(..., description="Constraint type (length, content, structure, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Constraint parameters")
    severity: str = Field("medium", description="Constraint severity (low, medium, high)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class FeedbackEntry(BaseModel):
    """Model for feedback entry."""
    feedback_id: str = Field(..., description="Unique feedback identifier")
    prompt_id: str = Field(..., description="Prompt ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Feedback timestamp")
    source: str = Field(..., description="Feedback source")
    rating: Optional[float] = Field(None, description="Numerical rating (0.0 to 1.0)")
    comments: Optional[str] = Field(None, description="Feedback comments")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class Prompt(BaseModel):
    """Model for prompt."""
    prompt_id: str = Field(..., description="Unique prompt identifier")
    name: str = Field(..., description="Prompt name")
    description: str = Field(..., description="Prompt description")
    version: str = Field(..., description="Prompt version")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    content: str = Field(..., description="Prompt content")
    template_variables: Dict[str, str] = Field(default_factory=dict, description="Template variables")
    context_id: Optional[str] = Field(None, description="Associated deployment context ID")
    parent_prompt_ids: List[str] = Field(default_factory=list, description="Parent prompt IDs")
    tags: List[str] = Field(default_factory=list, description="Prompt tags")
    performance_score: float = Field(0.0, description="Performance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PromptGenerationRequest(BaseModel):
    """Model for prompt generation request."""
    request_id: str = Field(..., description="Unique request identifier")
    context_id: str = Field(..., description="Deployment context ID")
    constraint_ids: List[str] = Field(default_factory=list, description="Constraint IDs to apply")
    parent_prompt_ids: List[str] = Field(default_factory=list, description="Parent prompt IDs")
    target_capabilities: List[str] = Field(default_factory=list, description="Target capabilities")
    generation_parameters: Dict[str, Any] = Field(default_factory=dict, description="Generation parameters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PromptGenerationResult(BaseModel):
    """Model for prompt generation result."""
    result_id: str = Field(..., description="Unique result identifier")
    request_id: str = Field(..., description="Request ID")
    prompt_id: Optional[str] = Field(None, description="Generated prompt ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Result timestamp")
    success: bool = Field(True, description="Whether generation was successful")
    error_message: Optional[str] = Field(None, description="Error message if unsuccessful")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Generation metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PromptOptimizationRequest(BaseModel):
    """Model for prompt optimization request."""
    request_id: str = Field(..., description="Unique request identifier")
    prompt_id: str = Field(..., description="Prompt ID to optimize")
    optimization_goals: List[str] = Field(..., description="Optimization goals")
    constraint_ids: List[str] = Field(default_factory=list, description="Constraint IDs to apply")
    feedback_window: Optional[int] = Field(None, description="Feedback window in days")
    optimization_parameters: Dict[str, Any] = Field(default_factory=dict, description="Optimization parameters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PromptOptimizationResult(BaseModel):
    """Model for prompt optimization result."""
    result_id: str = Field(..., description="Unique result identifier")
    request_id: str = Field(..., description="Request ID")
    original_prompt_id: str = Field(..., description="Original prompt ID")
    optimized_prompt_id: Optional[str] = Field(None, description="Optimized prompt ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Result timestamp")
    success: bool = Field(True, description="Whether optimization was successful")
    error_message: Optional[str] = Field(None, description="Error message if unsuccessful")
    improvement_metrics: Dict[str, Any] = Field(default_factory=dict, description="Improvement metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# In-memory storage (would be replaced with database in production)
deployment_contexts = {}
prompt_constraints = {}
feedback_entries = {}
prompts = {}
generation_results = {}
optimization_results = {}

class ContextGatherer:
    """
    Gathers and manages deployment context information.
    
    This class provides methods for creating, retrieving, updating, and analyzing
    deployment contexts.
    """
    
    def __init__(self):
        """Initialize the Context Gatherer."""
        logger.info("Context Gatherer initialized")
    
    def create_context(self, context: DeploymentContext) -> str:
        """
        Create a new deployment context.
        
        Args:
            context: The deployment context to create
            
        Returns:
            str: The context ID
        """
        # Store the context
        deployment_contexts[context.context_id] = context.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="deployment-contexts",
            key=context.context_id,
            value=json.dumps({
                "action": "create",
                "context_id": context.context_id,
                "industry": context.industry
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "deployment_context_created",
            "context_id": context.context_id,
            "industry": context.industry
        }
        mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="alphaevolve_prompt_broker",
            message={
                "type": "deployment_context_created",
                "context_id": context.context_id,
                "industry": context.industry
            }
        )
        
        return context.context_id
    
    def get_context(self, context_id: str) -> Optional[DeploymentContext]:
        """
        Get a deployment context by ID.
        
        Args:
            context_id: The context ID
            
        Returns:
            Optional[DeploymentContext]: The context, or None if not found
        """
        if context_id not in deployment_contexts:
            return None
        
        return DeploymentContext(**deployment_contexts[context_id])
    
    def update_context(self, context_id: str, context: DeploymentContext) -> bool:
        """
        Update a deployment context.
        
        Args:
            context_id: The context ID to update
            context: The updated context
            
        Returns:
            bool: True if successful, False if context not found
        """
        if context_id not in deployment_contexts:
            return False
        
        # Update the context
        deployment_contexts[context_id] = context.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="deployment-contexts",
            key=context_id,
            value=json.dumps({
                "action": "update",
                "context_id": context_id,
                "industry": context.industry
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "deployment_context_updated",
            "context_id": context_id,
            "industry": context.industry
        }
        mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="alphaevolve_prompt_broker",
            message={
                "type": "deployment_context_updated",
                "context_id": context_id,
                "industry": context.industry
            }
        )
        
        return True
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a deployment context.
        
        Args:
            context_id: The context ID to delete
            
        Returns:
            bool: True if successful, False if context not found
        """
        if context_id not in deployment_contexts:
            return False
        
        # Get context info before deletion
        context_info = deployment_contexts[context_id]
        
        # Delete the context
        del deployment_contexts[context_id]
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="deployment-contexts",
            key=context_id,
            value=json.dumps({
                "action": "delete",
                "context_id": context_id,
                "industry": context_info["industry"]
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "deployment_context_deleted",
            "context_id": context_id,
            "industry": context_info["industry"]
        }
        mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="alphaevolve_prompt_broker",
            message={
                "type": "deployment_context_deleted",
                "context_id": context_id,
                "industry": context_info["industry"]
            }
        )
        
        return True
    
    def list_contexts(
        self,
        industry_filter: Optional[str] = None,
        environment_filter: Optional[str] = None,
        capability_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[DeploymentContext]:
        """
        List deployment contexts, optionally filtered.
        
        Args:
            industry_filter: Optional filter for industry
            environment_filter: Optional filter for environment
            capability_filter: Optional filter for system capability
            limit: Maximum number of contexts to return
            
        Returns:
            List[DeploymentContext]: List of matching contexts
        """
        results = []
        
        for context_dict in deployment_contexts.values():
            # Apply filters
            if industry_filter and context_dict["industry"] != industry_filter:
                continue
            
            if environment_filter and context_dict["environment"] != environment_filter:
                continue
            
            if capability_filter and capability_filter not in context_dict["system_capabilities"]:
                continue
            
            results.append(DeploymentContext(**context_dict))
        
        # Sort by industry and environment
        results.sort(key=lambda c: (c.industry, c.environment))
        
        # Apply limit
        return results[:limit]
    
    def analyze_context(self, context_id: str) -> Dict[str, Any]:
        """
        Analyze a deployment context to extract key insights.
        
        Args:
            context_id: The context ID to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        context = self.get_context(context_id)
        if not context:
            return {"error": "Context not found"}
        
        # Analyze user roles
        role_categories = {
            "executive": ["ceo", "cfo", "cio", "cto", "executive", "director", "manager"],
            "technical": ["engineer", "developer", "architect", "technician", "operator"],
            "business": ["analyst", "consultant", "specialist", "coordinator", "planner"],
            "support": ["support", "service", "maintenance", "help desk"]
        }
        
        role_analysis = {}
        for category, keywords in role_categories.items():
            matching_roles = [role for role in context.user_roles if any(kw in role.lower() for kw in keywords)]
            role_analysis[category] = matching_roles
        
        # Analyze system capabilities
        capability_categories = {
            "data": ["data", "analytics", "reporting", "dashboard", "visualization"],
            "integration": ["integration", "api", "connector", "interface", "protocol"],
            "automation": ["automation", "workflow", "process", "orchestration", "scheduling"],
            "security": ["security", "authentication", "authorization", "encryption", "compliance"]
        }
        
        capability_analysis = {}
        for category, keywords in capability_categories.items():
            matching_capabilities = [cap for cap in context.system_capabilities if any(kw in cap.lower() for kw in keywords)]
            capability_analysis[category] = matching_capabilities
        
        # Analyze compliance requirements
        compliance_categories = {
            "data_privacy": ["gdpr", "ccpa", "privacy", "data protection"],
            "industry_specific": ["hipaa", "pci", "sox", "finra", "ferc"],
            "security": ["iso27001", "nist", "security", "encryption"],
            "operational": ["iso9001", "quality", "operational", "process"]
        }
        
        compliance_analysis = {}
        for category, keywords in compliance_categories.items():
            matching_requirements = [req for req in context.compliance_requirements if any(kw in req.lower() for kw in keywords)]
            compliance_analysis[category] = matching_requirements
        
        return {
            "context_id": context_id,
            "industry": context.industry,
            "environment": context.environment,
            "role_analysis": role_analysis,
            "capability_analysis": capability_analysis,
            "compliance_analysis": compliance_analysis,
            "integration_count": len(context.integration_points),
            "data_source_count": len(context.data_sources)
        }

class FeedbackIntegrator:
    """
    Manages and integrates feedback for prompts.
    
    This class provides methods for recording, retrieving, and analyzing
    feedback on prompts.
    """
    
    def __init__(self):
        """Initialize the Feedback Integrator."""
        logger.info("Feedback Integrator initialized")
    
    def record_feedback(self, feedback: FeedbackEntry) -> str:
        """
        Record feedback for a prompt.
        
        Args:
            feedback: The feedback to record
            
        Returns:
            str: The feedback ID
        """
        # Store the feedback
        feedback_entries[feedback.feedback_id] = feedback.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="prompt-feedback",
            key=feedback.prompt_id,
            value=json.dumps({
                "action": "record",
                "feedback_id": feedback.feedback_id,
                "prompt_id": feedback.prompt_id,
                "rating": feedback.rating
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "prompt_feedback_recorded",
            "feedback_id": feedback.feedback_id,
            "prompt_id": feedback.prompt_id,
            "rating": feedback.rating
        }
        mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="alphaevolve_prompt_broker",
            message={
                "type": "prompt_feedback_recorded",
                "feedback_id": feedback.feedback_id,
                "prompt_id": feedback.prompt_id,
                "rating": feedback.rating
            }
        )
        
        return feedback.feedback_id
    
    def get_feedback(self, feedback_id: str) -> Optional[FeedbackEntry]:
        """
        Get feedback by ID.
        
        Args:
            feedback_id: The feedback ID
            
        Returns:
            Optional[FeedbackEntry]: The feedback, or None if not found
        """
        if feedback_id not in feedback_entries:
            return None
        
        return FeedbackEntry(**feedback_entries[feedback_id])
    
    def list_feedback(
        self,
        prompt_id: Optional[str] = None,
        source_filter: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[FeedbackEntry]:
        """
        List feedback entries, optionally filtered.
        
        Args:
            prompt_id: Optional filter for prompt ID
            source_filter: Optional filter for feedback source
            min_rating: Optional minimum rating
            max_rating: Optional maximum rating
            start_date: Optional start date
            end_date: Optional end date
            limit: Maximum number of entries to return
            
        Returns:
            List[FeedbackEntry]: List of matching feedback entries
        """
        results = []
        
        for feedback_dict in feedback_entries.values():
            # Apply filters
            if prompt_id and feedback_dict["prompt_id"] != prompt_id:
                continue
            
            if source_filter and feedback_dict["source"] != source_filter:
                continue
            
            if min_rating is not None and (feedback_dict["rating"] is None or feedback_dict["rating"] < min_rating):
                continue
            
            if max_rating is not None and (feedback_dict["rating"] is None or feedback_dict["rating"] > max_rating):
                continue
            
            feedback_time = datetime.fromisoformat(feedback_dict["timestamp"]) if isinstance(feedback_dict["timestamp"], str) else feedback_dict["timestamp"]
            
            if start_date and feedback_time < start_date:
                continue
            
            if end_date and feedback_time > end_date:
                continue
            
            results.append(FeedbackEntry(**feedback_dict))
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda f: f.timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def analyze_feedback(
        self,
        prompt_id: str,
        window_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze feedback for a prompt.
        
        Args:
            prompt_id: The prompt ID to analyze
            window_days: Optional window of days to analyze (from now)
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Get feedback for the prompt
        if window_days is not None:
            start_date = datetime.now() - timedelta(days=window_days)
            feedback_list = self.list_feedback(
                prompt_id=prompt_id,
                start_date=start_date,
                limit=1000  # High limit to get all relevant feedback
            )
        else:
            feedback_list = self.list_feedback(
                prompt_id=prompt_id,
                limit=1000  # High limit to get all relevant feedback
            )
        
        if not feedback_list:
            return {
                "prompt_id": prompt_id,
                "feedback_count": 0,
                "average_rating": None,
                "rating_distribution": {},
                "sources": [],
                "metrics": {}
            }
        
        # Calculate average rating
        ratings = [f.rating for f in feedback_list if f.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        
        # Calculate rating distribution
        rating_distribution = {}
        for rating in ratings:
            # Round to nearest 0.1
            rounded = round(rating * 10) / 10
            key = str(rounded)
            if key in rating_distribution:
                rating_distribution[key] += 1
            else:
                rating_distribution[key] = 1
        
        # Get unique sources
        sources = list(set(f.source for f in feedback_list))
        
        # Aggregate metrics
        all_metrics = {}
        for feedback in feedback_list:
            for key, value in feedback.metrics.items():
                if isinstance(value, (int, float)):
                    if key in all_metrics:
                        all_metrics[key].append(value)
                    else:
                        all_metrics[key] = [value]
        
        # Calculate metric statistics
        metric_stats = {}
        for key, values in all_metrics.items():
            if values:
                metric_stats[key] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "count": len(values)
                }
        
        # Extract common themes from comments
        comments = [f.comments for f in feedback_list if f.comments]
        
        return {
            "prompt_id": prompt_id,
            "feedback_count": len(feedback_list),
            "rated_feedback_count": len(ratings),
            "average_rating": avg_rating,
            "rating_distribution": rating_distribution,
            "sources": sources,
            "metrics": metric_stats,
            "comment_count": len(comments),
            "window_days": window_days
        }

class PromptOptimizer:
    """
    Optimizes prompts based on feedback and constraints.
    
    This class provides methods for generating and optimizing prompts
    based on deployment context, constraints, and feedback.
    """
    
    def __init__(self):
        """Initialize the Prompt Optimizer."""
        logger.info("Prompt Optimizer initialized")
    
    def create_prompt(self, prompt: Prompt) -> str:
        """
        Create a new prompt.
        
        Args:
            prompt: The prompt to create
            
        Returns:
            str: The prompt ID
        """
        # Store the prompt
        prompts[prompt.prompt_id] = prompt.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="prompts",
            key=prompt.prompt_id,
            value=json.dumps({
                "action": "create",
                "prompt_id": prompt.prompt_id,
                "name": prompt.name,
                "version": prompt.version
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "prompt_created",
            "prompt_id": prompt.prompt_id,
            "name": prompt.name,
            "version": prompt.version
        }
        mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="alphaevolve_prompt_broker",
            message={
                "type": "prompt_created",
                "prompt_id": prompt.prompt_id,
                "name": prompt.name,
                "version": prompt.version
            }
        )
        
        return prompt.prompt_id
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """
        Get a prompt by ID.
        
        Args:
            prompt_id: The prompt ID
            
        Returns:
            Optional[Prompt]: The prompt, or None if not found
        """
        if prompt_id not in prompts:
            return None
        
        return Prompt(**prompts[prompt_id])
    
    def update_prompt(self, prompt_id: str, prompt: Prompt) -> bool:
        """
        Update a prompt.
        
        Args:
            prompt_id: The prompt ID to update
            prompt: The updated prompt
            
        Returns:
            bool: True if successful, False if prompt not found
        """
        if prompt_id not in prompts:
            return False
        
        # Update the prompt
        prompt.updated_at = datetime.now()
        prompts[prompt_id] = prompt.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="prompts",
            key=prompt_id,
            value=json.dumps({
                "action": "update",
                "prompt_id": prompt_id,
                "name": prompt.name,
                "version": prompt.version
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "prompt_updated",
            "prompt_id": prompt_id,
            "name": prompt.name,
            "version": prompt.version
        }
        mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="alphaevolve_prompt_broker",
            message={
                "type": "prompt_updated",
                "prompt_id": prompt_id,
                "name": prompt.name,
                "version": prompt.version
            }
        )
        
        return True
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """
        Delete a prompt.
        
        Args:
            prompt_id: The prompt ID to delete
            
        Returns:
            bool: True if successful, False if prompt not found
        """
        if prompt_id not in prompts:
            return False
        
        # Get prompt info before deletion
        prompt_info = prompts[prompt_id]
        
        # Delete the prompt
        del prompts[prompt_id]
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="prompts",
            key=prompt_id,
            value=json.dumps({
                "action": "delete",
                "prompt_id": prompt_id,
                "name": prompt_info["name"],
                "version": prompt_info["version"]
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "prompt_deleted",
            "prompt_id": prompt_id,
            "name": prompt_info["name"],
            "version": prompt_info["version"]
        }
        mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="alphaevolve_prompt_broker",
            message={
                "type": "prompt_deleted",
                "prompt_id": prompt_id,
                "name": prompt_info["name"],
                "version": prompt_info["version"]
            }
        )
        
        return True
    
    def list_prompts(
        self,
        name_filter: Optional[str] = None,
        context_id: Optional[str] = None,
        tag_filter: Optional[str] = None,
        min_performance: Optional[float] = None,
        limit: int = 100
    ) -> List[Prompt]:
        """
        List prompts, optionally filtered.
        
        Args:
            name_filter: Optional filter for prompt name (case-insensitive substring match)
            context_id: Optional filter for context ID
            tag_filter: Optional filter for tag
            min_performance: Optional minimum performance score
            limit: Maximum number of prompts to return
            
        Returns:
            List[Prompt]: List of matching prompts
        """
        results = []
        
        for prompt_dict in prompts.values():
            # Apply filters
            if name_filter and name_filter.lower() not in prompt_dict["name"].lower():
                continue
            
            if context_id and prompt_dict["context_id"] != context_id:
                continue
            
            if tag_filter and tag_filter not in prompt_dict["tags"]:
                continue
            
            if min_performance is not None and prompt_dict["performance_score"] < min_performance:
                continue
            
            results.append(Prompt(**prompt_dict))
        
        # Sort by performance score (highest first)
        results.sort(key=lambda p: p.performance_score, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    def create_constraint(self, constraint: PromptConstraint) -> str:
        """
        Create a new prompt constraint.
        
        Args:
            constraint: The constraint to create
            
        Returns:
            str: The constraint ID
        """
        # Store the constraint
        prompt_constraints[constraint.constraint_id] = constraint.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="prompt-constraints",
            key=constraint.constraint_id,
            value=json.dumps({
                "action": "create",
                "constraint_id": constraint.constraint_id,
                "name": constraint.name
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "prompt_constraint_created",
            "constraint_id": constraint.constraint_id,
            "name": constraint.name
        }
        mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="alphaevolve_prompt_broker",
            message={
                "type": "prompt_constraint_created",
                "constraint_id": constraint.constraint_id,
                "name": constraint.name
            }
        )
        
        return constraint.constraint_id
    
    def get_constraint(self, constraint_id: str) -> Optional[PromptConstraint]:
        """
        Get a prompt constraint by ID.
        
        Args:
            constraint_id: The constraint ID
            
        Returns:
            Optional[PromptConstraint]: The constraint, or None if not found
        """
        if constraint_id not in prompt_constraints:
            return None
        
        return PromptConstraint(**prompt_constraints[constraint_id])
    
    def list_constraints(
        self,
        type_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[PromptConstraint]:
        """
        List prompt constraints, optionally filtered.
        
        Args:
            type_filter: Optional filter for constraint type
            severity_filter: Optional filter for constraint severity
            limit: Maximum number of constraints to return
            
        Returns:
            List[PromptConstraint]: List of matching constraints
        """
        results = []
        
        for constraint_dict in prompt_constraints.values():
            # Apply filters
            if type_filter and constraint_dict["constraint_type"] != type_filter:
                continue
            
            if severity_filter and constraint_dict["severity"] != severity_filter:
                continue
            
            results.append(PromptConstraint(**constraint_dict))
        
        # Sort by severity (high to low) and name
        severity_order = {"high": 0, "medium": 1, "low": 2}
        results.sort(key=lambda c: (severity_order.get(c.severity, 3), c.name))
        
        # Apply limit
        return results[:limit]
    
    def validate_prompt(
        self,
        prompt: Prompt,
        constraint_ids: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate a prompt against constraints.
        
        Args:
            prompt: The prompt to validate
            constraint_ids: Optional list of constraint IDs to validate against
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of validation errors)
        """
        errors = []
        
        # Get constraints to validate against
        constraints = []
        if constraint_ids:
            for constraint_id in constraint_ids:
                constraint = self.get_constraint(constraint_id)
                if constraint:
                    constraints.append(constraint)
        else:
            # Use all constraints
            constraints = [PromptConstraint(**c) for c in prompt_constraints.values()]
        
        # Validate against each constraint
        for constraint in constraints:
            if constraint.constraint_type == "length":
                # Length constraints
                if "min_length" in constraint.parameters:
                    min_length = constraint.parameters["min_length"]
                    if len(prompt.content) < min_length:
                        errors.append(f"Prompt content length ({len(prompt.content)}) is less than minimum required length ({min_length})")
                
                if "max_length" in constraint.parameters:
                    max_length = constraint.parameters["max_length"]
                    if len(prompt.content) > max_length:
                        errors.append(f"Prompt content length ({len(prompt.content)}) exceeds maximum allowed length ({max_length})")
            
            elif constraint.constraint_type == "content":
                # Content constraints
                if "required_phrases" in constraint.parameters:
                    for phrase in constraint.parameters["required_phrases"]:
                        if phrase not in prompt.content:
                            errors.append(f"Required phrase '{phrase}' not found in prompt content")
                
                if "prohibited_phrases" in constraint.parameters:
                    for phrase in constraint.parameters["prohibited_phrases"]:
                        if phrase in prompt.content:
                            errors.append(f"Prohibited phrase '{phrase}' found in prompt content")
            
            elif constraint.constraint_type == "structure":
                # Structure constraints
                if "required_sections" in constraint.parameters:
                    for section in constraint.parameters["required_sections"]:
                        if section not in prompt.content:
                            errors.append(f"Required section '{section}' not found in prompt content")
            
            elif constraint.constraint_type == "variables":
                # Template variable constraints
                if "required_variables" in constraint.parameters:
                    for variable in constraint.parameters["required_variables"]:
                        if variable not in prompt.template_variables:
                            errors.append(f"Required template variable '{variable}' not defined")
        
        return (len(errors) == 0, errors)
    
    def generate_prompt(
        self,
        request: PromptGenerationRequest,
        context_gatherer: ContextGatherer,
        feedback_integrator: FeedbackIntegrator
    ) -> PromptGenerationResult:
        """
        Generate a new prompt based on the request.
        
        Args:
            request: The generation request
            context_gatherer: Context gatherer instance
            feedback_integrator: Feedback integrator instance
            
        Returns:
            PromptGenerationResult: The generation result
        """
        result_id = f"gen-result-{uuid.uuid4()}"
        
        try:
            # Get the deployment context
            context = context_gatherer.get_context(request.context_id)
            if not context:
                raise ValueError(f"Unknown deployment context: {request.context_id}")
            
            # Get constraints
            constraints = []
            for constraint_id in request.constraint_ids:
                constraint = self.get_constraint(constraint_id)
                if constraint:
                    constraints.append(constraint)
            
            # Get parent prompts
            parent_prompts = []
            for parent_id in request.parent_prompt_ids:
                parent = self.get_prompt(parent_id)
                if parent:
                    parent_prompts.append(parent)
            
            # Analyze context
            context_analysis = context_gatherer.analyze_context(request.context_id)
            
            # Analyze parent prompt feedback if available
            feedback_analysis = {}
            for parent in parent_prompts:
                feedback_analysis[parent.prompt_id] = feedback_integrator.analyze_feedback(
                    parent.prompt_id,
                    window_days=30  # Last 30 days
                )
            
            # Generate prompt content
            prompt_content = self._generate_prompt_content(
                context,
                context_analysis,
                constraints,
                parent_prompts,
                feedback_analysis,
                request.target_capabilities,
                request.generation_parameters
            )
            
            # Create template variables
            template_variables = self._extract_template_variables(prompt_content)
            
            # Generate name and description
            name = f"Generated prompt for {context.industry} - {context.environment}"
            if request.target_capabilities:
                name += f" - {request.target_capabilities[0]}"
            
            description = f"Prompt generated for {context.industry} deployment in {context.environment} environment. "
            if parent_prompts:
                parent_names = [p.name for p in parent_prompts]
                description += f"Based on parent prompts: {', '.join(parent_names)}. "
            
            if request.target_capabilities:
                description += f"Target capabilities: {', '.join(request.target_capabilities)}."
            
            # Create the prompt
            prompt_id = f"prompt-{uuid.uuid4()}"
            prompt = Prompt(
                prompt_id=prompt_id,
                name=name,
                description=description,
                version="1.0.0",
                content=prompt_content,
                template_variables=template_variables,
                context_id=request.context_id,
                parent_prompt_ids=[p.prompt_id for p in parent_prompts],
                tags=request.target_capabilities.copy() if request.target_capabilities else [],
                performance_score=0.0,  # Will be updated based on feedback
                metadata={
                    "generation_request_id": request.request_id,
                    "generation_timestamp": datetime.now().isoformat()
                }
            )
            
            # Validate the prompt
            is_valid, validation_errors = self.validate_prompt(prompt, request.constraint_ids)
            
            if not is_valid:
                # Store the prompt anyway, but mark as invalid
                prompt.metadata["validation_errors"] = validation_errors
                self.create_prompt(prompt)
                
                # Create error result
                result = PromptGenerationResult(
                    result_id=result_id,
                    request_id=request.request_id,
                    prompt_id=prompt_id,
                    success=False,
                    error_message="Prompt validation failed",
                    metrics={
                        "validation_errors": len(validation_errors)
                    },
                    metadata={
                        "validation_errors": validation_errors
                    }
                )
            else:
                # Store the valid prompt
                self.create_prompt(prompt)
                
                # Create success result
                result = PromptGenerationResult(
                    result_id=result_id,
                    request_id=request.request_id,
                    prompt_id=prompt_id,
                    success=True,
                    metrics={
                        "content_length": len(prompt_content),
                        "variable_count": len(template_variables),
                        "parent_count": len(parent_prompts)
                    },
                    metadata={
                        "context_id": request.context_id,
                        "industry": context.industry,
                        "environment": context.environment
                    }
                )
            
            # Store the result
            generation_results[result_id] = result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="prompt-generation-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "prompt_id": prompt_id,
                    "success": result.success
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "prompt_generated",
                "result_id": result_id,
                "request_id": request.request_id,
                "prompt_id": prompt_id,
                "success": result.success
            }
            mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="alphaevolve_prompt_broker",
                message={
                    "type": "prompt_generated",
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "prompt_id": prompt_id,
                    "success": result.success
                }
            )
            
            return result
        
        except Exception as e:
            # Create error result
            result = PromptGenerationResult(
                result_id=result_id,
                request_id=request.request_id,
                prompt_id=None,
                success=False,
                error_message=str(e),
                metrics={},
                metadata={}
            )
            
            # Store the result
            generation_results[result_id] = result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="prompt-generation-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "success": False,
                    "error": str(e)
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "prompt_generation_failed",
                "result_id": result_id,
                "request_id": request.request_id,
                "error": str(e)
            }
            mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="alphaevolve_prompt_broker",
                message={
                    "type": "prompt_generation_failed",
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "error": str(e)
                }
            )
            
            return result
    
    def optimize_prompt(
        self,
        request: PromptOptimizationRequest,
        feedback_integrator: FeedbackIntegrator
    ) -> PromptOptimizationResult:
        """
        Optimize a prompt based on feedback and goals.
        
        Args:
            request: The optimization request
            feedback_integrator: Feedback integrator instance
            
        Returns:
            PromptOptimizationResult: The optimization result
        """
        result_id = f"opt-result-{uuid.uuid4()}"
        
        try:
            # Get the original prompt
            original_prompt = self.get_prompt(request.prompt_id)
            if not original_prompt:
                raise ValueError(f"Unknown prompt: {request.prompt_id}")
            
            # Get constraints
            constraints = []
            for constraint_id in request.constraint_ids:
                constraint = self.get_constraint(constraint_id)
                if constraint:
                    constraints.append(constraint)
            
            # Analyze feedback
            feedback_analysis = feedback_integrator.analyze_feedback(
                request.prompt_id,
                window_days=request.feedback_window
            )
            
            # Optimize prompt content
            optimized_content = self._optimize_prompt_content(
                original_prompt,
                feedback_analysis,
                constraints,
                request.optimization_goals,
                request.optimization_parameters
            )
            
            # Create template variables
            template_variables = self._extract_template_variables(optimized_content)
            
            # Generate name and description
            name = f"{original_prompt.name} (Optimized)"
            description = f"Optimized version of prompt '{original_prompt.name}'. "
            description += f"Optimization goals: {', '.join(request.optimization_goals)}."
            
            # Create the optimized prompt
            optimized_prompt_id = f"prompt-{uuid.uuid4()}"
            optimized_prompt = Prompt(
                prompt_id=optimized_prompt_id,
                name=name,
                description=description,
                version=self._increment_version(original_prompt.version),
                content=optimized_content,
                template_variables=template_variables,
                context_id=original_prompt.context_id,
                parent_prompt_ids=[original_prompt.prompt_id],
                tags=original_prompt.tags.copy(),
                performance_score=original_prompt.performance_score,  # Will be updated based on feedback
                metadata={
                    "optimization_request_id": request.request_id,
                    "optimization_timestamp": datetime.now().isoformat(),
                    "optimization_goals": request.optimization_goals,
                    "original_prompt_id": original_prompt.prompt_id
                }
            )
            
            # Validate the prompt
            is_valid, validation_errors = self.validate_prompt(optimized_prompt, request.constraint_ids)
            
            if not is_valid:
                # Store the prompt anyway, but mark as invalid
                optimized_prompt.metadata["validation_errors"] = validation_errors
                self.create_prompt(optimized_prompt)
                
                # Create error result
                result = PromptOptimizationResult(
                    result_id=result_id,
                    request_id=request.request_id,
                    original_prompt_id=request.prompt_id,
                    optimized_prompt_id=optimized_prompt_id,
                    success=False,
                    error_message="Optimized prompt validation failed",
                    improvement_metrics={
                        "validation_errors": len(validation_errors)
                    },
                    metadata={
                        "validation_errors": validation_errors
                    }
                )
            else:
                # Store the valid prompt
                self.create_prompt(optimized_prompt)
                
                # Calculate improvement metrics
                improvement_metrics = self._calculate_improvement_metrics(
                    original_prompt,
                    optimized_prompt,
                    request.optimization_goals
                )
                
                # Create success result
                result = PromptOptimizationResult(
                    result_id=result_id,
                    request_id=request.request_id,
                    original_prompt_id=request.prompt_id,
                    optimized_prompt_id=optimized_prompt_id,
                    success=True,
                    improvement_metrics=improvement_metrics,
                    metadata={
                        "optimization_goals": request.optimization_goals,
                        "feedback_window": request.feedback_window
                    }
                )
            
            # Store the result
            optimization_results[result_id] = result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="prompt-optimization-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "original_prompt_id": request.prompt_id,
                    "optimized_prompt_id": optimized_prompt_id,
                    "success": result.success
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "prompt_optimized",
                "result_id": result_id,
                "request_id": request.request_id,
                "original_prompt_id": request.prompt_id,
                "optimized_prompt_id": optimized_prompt_id,
                "success": result.success
            }
            mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="alphaevolve_prompt_broker",
                message={
                    "type": "prompt_optimized",
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "original_prompt_id": request.prompt_id,
                    "optimized_prompt_id": optimized_prompt_id,
                    "success": result.success
                }
            )
            
            return result
        
        except Exception as e:
            # Create error result
            result = PromptOptimizationResult(
                result_id=result_id,
                request_id=request.request_id,
                original_prompt_id=request.prompt_id,
                optimized_prompt_id=None,
                success=False,
                error_message=str(e),
                improvement_metrics={},
                metadata={}
            )
            
            # Store the result
            optimization_results[result_id] = result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="prompt-optimization-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "original_prompt_id": request.prompt_id,
                    "success": False,
                    "error": str(e)
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "prompt_optimization_failed",
                "result_id": result_id,
                "request_id": request.request_id,
                "original_prompt_id": request.prompt_id,
                "error": str(e)
            }
            mcp_bridge.send_context_update("alphaevolve_prompt_broker", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="alphaevolve_prompt_broker",
                message={
                    "type": "prompt_optimization_failed",
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "original_prompt_id": request.prompt_id,
                    "error": str(e)
                }
            )
            
            return result
    
    def get_generation_result(self, result_id: str) -> Optional[PromptGenerationResult]:
        """
        Get a prompt generation result by ID.
        
        Args:
            result_id: The result ID
            
        Returns:
            Optional[PromptGenerationResult]: The result, or None if not found
        """
        if result_id not in generation_results:
            return None
        
        return PromptGenerationResult(**generation_results[result_id])
    
    def get_optimization_result(self, result_id: str) -> Optional[PromptOptimizationResult]:
        """
        Get a prompt optimization result by ID.
        
        Args:
            result_id: The result ID
            
        Returns:
            Optional[PromptOptimizationResult]: The result, or None if not found
        """
        if result_id not in optimization_results:
            return None
        
        return PromptOptimizationResult(**optimization_results[result_id])
    
    def _generate_prompt_content(
        self,
        context: DeploymentContext,
        context_analysis: Dict[str, Any],
        constraints: List[PromptConstraint],
        parent_prompts: List[Prompt],
        feedback_analysis: Dict[str, Dict[str, Any]],
        target_capabilities: List[str],
        generation_parameters: Dict[str, Any]
    ) -> str:
        """
        Generate prompt content based on context, constraints, and parent prompts.
        
        Args:
            context: Deployment context
            context_analysis: Context analysis results
            constraints: List of constraints
            parent_prompts: List of parent prompts
            feedback_analysis: Feedback analysis for parent prompts
            target_capabilities: Target capabilities
            generation_parameters: Generation parameters
            
        Returns:
            str: Generated prompt content
        """
        # This is a simplified implementation
        # In production, this would use more sophisticated techniques
        
        # Start with a template based on industry
        industry_templates = {
            "manufacturing": "You are an AI assistant specialized in manufacturing processes. Your role is to help with {{task}} in the {{environment}} environment. Focus on efficiency, quality, and safety.",
            "healthcare": "You are an AI assistant specialized in healthcare. Your role is to help with {{task}} in the {{environment}} environment. Focus on patient care, accuracy, and compliance with {{compliance_requirements}}.",
            "finance": "You are an AI assistant specialized in finance. Your role is to help with {{task}} in the {{environment}} environment. Focus on accuracy, security, and compliance with {{compliance_requirements}}.",
            "retail": "You are an AI assistant specialized in retail. Your role is to help with {{task}} in the {{environment}} environment. Focus on customer experience, inventory management, and sales optimization.",
            "energy": "You are an AI assistant specialized in energy. Your role is to help with {{task}} in the {{environment}} environment. Focus on efficiency, sustainability, and safety.",
            "construction": "You are an AI assistant specialized in construction. Your role is to help with {{task}} in the {{environment}} environment. Focus on safety, quality, and project management."
        }
        
        # Get template for industry or use default
        template = industry_templates.get(
            context.industry.lower(),
            "You are an AI assistant specialized in {{industry}}. Your role is to help with {{task}} in the {{environment}} environment."
        )
        
        # Replace basic variables
        content = template.replace("{{industry}}", context.industry)
        content = content.replace("{{environment}}", context.environment)
        
        # Add compliance requirements if available
        if context.compliance_requirements:
            compliance_text = ", ".join(context.compliance_requirements)
            content = content.replace("{{compliance_requirements}}", compliance_text)
        else:
            content = content.replace("{{compliance_requirements}}", "relevant regulations")
        
        # Add task placeholder
        content = content.replace("{{task}}", "{{task}}")
        
        # Add capabilities section
        if target_capabilities:
            content += "\n\n## Capabilities\n\n"
            for capability in target_capabilities:
                content += f"- {capability}\n"
        
        # Add user roles section
        if context.user_roles:
            content += "\n\n## User Roles\n\n"
            content += "You will interact with users in the following roles:\n\n"
            for role in context.user_roles:
                content += f"- {role}\n"
        
        # Add data sources section
        if context.data_sources:
            content += "\n\n## Data Sources\n\n"
            content += "You have access to the following data sources:\n\n"
            for source in context.data_sources:
                content += f"- {source}\n"
        
        # Add integration points section
        if context.integration_points:
            content += "\n\n## Integration Points\n\n"
            content += "You can integrate with the following systems:\n\n"
            for integration in context.integration_points:
                content += f"- {integration}\n"
        
        # Add constraints section
        if constraints:
            content += "\n\n## Constraints\n\n"
            for constraint in constraints:
                content += f"- {constraint.name}: {constraint.description}\n"
        
        # Add guidelines section
        content += "\n\n## Guidelines\n\n"
        content += "1. Always prioritize user needs and goals.\n"
        content += "2. Provide clear, concise, and accurate information.\n"
        content += "3. Respect privacy and confidentiality.\n"
        content += "4. Acknowledge limitations and uncertainties.\n"
        content += "5. Maintain a professional and helpful tone.\n"
        
        # Incorporate elements from parent prompts if available
        if parent_prompts:
            content += "\n\n## Additional Instructions\n\n"
            
            # Extract key sections from parent prompts
            for parent in parent_prompts:
                # Simple extraction of sections (would be more sophisticated in production)
                sections = parent.content.split("\n\n")
                for section in sections:
                    if "##" in section and not any(keyword in section.lower() for keyword in ["capability", "user role", "data source", "integration", "constraint", "guideline"]):
                        content += f"\n\n{section}\n"
            
            # Incorporate feedback-based improvements
            for parent_id, analysis in feedback_analysis.items():
                if analysis.get("feedback_count", 0) > 0 and analysis.get("average_rating") is not None:
                    # Only incorporate feedback if it's substantial
                    if analysis["average_rating"] < 0.7:
                        content += f"\n\nNote: Based on feedback, improve upon previous limitations in clarity and accuracy.\n"
        
        # Add template variables section
        content += "\n\n## Template Variables\n\n"
        content += "- {{task}}: Specific task or query the user needs help with\n"
        content += "- {{user_role}}: Role of the current user\n"
        content += "- {{context}}: Additional context provided by the user\n"
        
        return content
    
    def _optimize_prompt_content(
        self,
        original_prompt: Prompt,
        feedback_analysis: Dict[str, Any],
        constraints: List[PromptConstraint],
        optimization_goals: List[str],
        optimization_parameters: Dict[str, Any]
    ) -> str:
        """
        Optimize prompt content based on feedback and goals.
        
        Args:
            original_prompt: Original prompt
            feedback_analysis: Feedback analysis
            constraints: List of constraints
            optimization_goals: Optimization goals
            optimization_parameters: Optimization parameters
            
        Returns:
            str: Optimized prompt content
        """
        # This is a simplified implementation
        # In production, this would use more sophisticated techniques
        
        # Start with the original content
        content = original_prompt.content
        
        # Apply optimizations based on goals
        for goal in optimization_goals:
            if goal == "clarity":
                # Improve clarity
                content = self._optimize_for_clarity(content, feedback_analysis)
            
            elif goal == "specificity":
                # Improve specificity
                content = self._optimize_for_specificity(content, feedback_analysis)
            
            elif goal == "conciseness":
                # Improve conciseness
                content = self._optimize_for_conciseness(content, feedback_analysis)
            
            elif goal == "performance":
                # Improve performance
                content = self._optimize_for_performance(content, feedback_analysis)
        
        # Add optimization note
        content += f"\n\n## Optimization Note\n\n"
        content += f"This prompt was optimized on {datetime.now().strftime('%Y-%m-%d')} "
        content += f"with the following goals: {', '.join(optimization_goals)}.\n"
        
        return content
    
    def _optimize_for_clarity(self, content: str, feedback_analysis: Dict[str, Any]) -> str:
        """
        Optimize prompt content for clarity.
        
        Args:
            content: Original content
            feedback_analysis: Feedback analysis
            
        Returns:
            str: Optimized content
        """
        # This is a simplified implementation
        # In production, this would use more sophisticated techniques
        
        # Add clarity improvements
        if "## Guidelines" in content:
            # Add clarity guideline
            if "Be clear and avoid ambiguity" not in content:
                guidelines_section = content.split("## Guidelines")[1].split("\n\n")[0]
                new_guidelines = guidelines_section + "\n6. Be clear and avoid ambiguity in all responses.\n"
                content = content.replace(guidelines_section, new_guidelines)
        else:
            # Add guidelines section
            content += "\n\n## Guidelines\n\n"
            content += "1. Be clear and avoid ambiguity in all responses.\n"
            content += "2. Use simple language and avoid jargon when possible.\n"
            content += "3. Structure responses with headings and bullet points for readability.\n"
        
        # Add examples section if not present
        if "## Examples" not in content:
            content += "\n\n## Examples\n\n"
            content += "Example 1: When asked about a complex topic, break it down into simple steps.\n\n"
            content += "Example 2: When providing options, clearly list pros and cons for each.\n"
        
        return content
    
    def _optimize_for_specificity(self, content: str, feedback_analysis: Dict[str, Any]) -> str:
        """
        Optimize prompt content for specificity.
        
        Args:
            content: Original content
            feedback_analysis: Feedback analysis
            
        Returns:
            str: Optimized content
        """
        # This is a simplified implementation
        # In production, this would use more sophisticated techniques
        
        # Add specificity improvements
        if "## Guidelines" in content:
            # Add specificity guideline
            if "Provide specific, actionable information" not in content:
                guidelines_section = content.split("## Guidelines")[1].split("\n\n")[0]
                new_guidelines = guidelines_section + "\n7. Provide specific, actionable information rather than general advice.\n"
                content = content.replace(guidelines_section, new_guidelines)
        
        # Add domain-specific instructions
        if "## Domain-Specific Instructions" not in content:
            content += "\n\n## Domain-Specific Instructions\n\n"
            content += "1. When discussing technical concepts, provide concrete examples.\n"
            content += "2. Include relevant metrics and measurements when applicable.\n"
            content += "3. Reference specific processes, tools, or methodologies rather than generic approaches.\n"
        
        return content
    
    def _optimize_for_conciseness(self, content: str, feedback_analysis: Dict[str, Any]) -> str:
        """
        Optimize prompt content for conciseness.
        
        Args:
            content: Original content
            feedback_analysis: Feedback analysis
            
        Returns:
            str: Optimized content
        """
        # This is a simplified implementation
        # In production, this would use more sophisticated techniques
        
        # Add conciseness improvements
        if "## Guidelines" in content:
            # Add conciseness guideline
            if "Be concise and avoid unnecessary verbosity" not in content:
                guidelines_section = content.split("## Guidelines")[1].split("\n\n")[0]
                new_guidelines = guidelines_section + "\n8. Be concise and avoid unnecessary verbosity.\n"
                content = content.replace(guidelines_section, new_guidelines)
        
        # Add response format instructions
        if "## Response Format" not in content:
            content += "\n\n## Response Format\n\n"
            content += "1. Start with a brief summary (1-2 sentences).\n"
            content += "2. Provide key points in bullet form when appropriate.\n"
            content += "3. Use tables for comparing multiple items or options.\n"
            content += "4. Only elaborate on details when specifically requested.\n"
        
        return content
    
    def _optimize_for_performance(self, content: str, feedback_analysis: Dict[str, Any]) -> str:
        """
        Optimize prompt content for performance.
        
        Args:
            content: Original content
            feedback_analysis: Feedback analysis
            
        Returns:
            str: Optimized content
        """
        # This is a simplified implementation
        # In production, this would use more sophisticated techniques
        
        # Add performance improvements
        if "## Performance Optimization" not in content:
            content += "\n\n## Performance Optimization\n\n"
            content += "1. Prioritize accuracy over speed, but aim for efficient responses.\n"
            content += "2. Use a step-by-step approach for complex problems.\n"
            content += "3. When uncertain, acknowledge limitations rather than providing incorrect information.\n"
            content += "4. For resource-intensive tasks, focus on the most important aspects first.\n"
        
        return content
    
    def _extract_template_variables(self, content: str) -> Dict[str, str]:
        """
        Extract template variables from prompt content.
        
        Args:
            content: Prompt content
            
        Returns:
            Dict[str, str]: Template variables with descriptions
        """
        variables = {}
        
        # Look for {{variable}} patterns
        import re
        pattern = r"{{([a-zA-Z0-9_]+)}}"
        matches = re.findall(pattern, content)
        
        # Extract unique variables
        for variable in set(matches):
            # Look for descriptions in the content
            desc_pattern = f"- {{{{(variable)}}}}: (.*?)(?:\n|$)"
            desc_matches = re.findall(desc_pattern, content)
            
            if desc_matches:
                variables[variable] = desc_matches[0]
            else:
                variables[variable] = f"Value for {variable}"
        
        return variables
    
    def _increment_version(self, version: str) -> str:
        """
        Increment the version number.
        
        Args:
            version: Current version
            
        Returns:
            str: Incremented version
        """
        # Parse version (assuming semantic versioning)
        parts = version.split(".")
        
        if len(parts) >= 3:
            # Increment patch version
            parts[2] = str(int(parts[2]) + 1)
        elif len(parts) == 2:
            # Add patch version
            parts.append("1")
        elif len(parts) == 1:
            # Add minor and patch versions
            parts.extend(["0", "1"])
        
        return ".".join(parts)
    
    def _calculate_improvement_metrics(
        self,
        original_prompt: Prompt,
        optimized_prompt: Prompt,
        optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate improvement metrics between original and optimized prompts.
        
        Args:
            original_prompt: Original prompt
            optimized_prompt: Optimized prompt
            optimization_goals: Optimization goals
            
        Returns:
            Dict[str, Any]: Improvement metrics
        """
        metrics = {}
        
        # Basic metrics
        metrics["content_length_original"] = len(original_prompt.content)
        metrics["content_length_optimized"] = len(optimized_prompt.content)
        metrics["content_length_change"] = len(optimized_prompt.content) - len(original_prompt.content)
        metrics["content_length_change_percent"] = (metrics["content_length_change"] / metrics["content_length_original"]) * 100 if metrics["content_length_original"] > 0 else 0
        
        metrics["variable_count_original"] = len(original_prompt.template_variables)
        metrics["variable_count_optimized"] = len(optimized_prompt.template_variables)
        metrics["variable_count_change"] = len(optimized_prompt.template_variables) - len(original_prompt.template_variables)
        
        # Goal-specific metrics
        if "clarity" in optimization_goals:
            # Simple clarity metric based on section count
            original_sections = original_prompt.content.count("##")
            optimized_sections = optimized_prompt.content.count("##")
            metrics["clarity_section_count_change"] = optimized_sections - original_sections
            
            # Example count
            original_examples = original_prompt.content.count("Example")
            optimized_examples = optimized_prompt.content.count("Example")
            metrics["clarity_example_count_change"] = optimized_examples - original_examples
        
        if "specificity" in optimization_goals:
            # Simple specificity metric based on specific terms
            specificity_terms = ["specific", "exactly", "precisely", "concrete", "detailed"]
            original_specificity = sum(original_prompt.content.lower().count(term) for term in specificity_terms)
            optimized_specificity = sum(optimized_prompt.content.lower().count(term) for term in specificity_terms)
            metrics["specificity_term_count_change"] = optimized_specificity - original_specificity
        
        if "conciseness" in optimization_goals:
            # Simple conciseness metric based on average sentence length
            import re
            original_sentences = re.split(r'[.!?]', original_prompt.content)
            original_sentence_lengths = [len(s.strip().split()) for s in original_sentences if s.strip()]
            original_avg_sentence_length = sum(original_sentence_lengths) / len(original_sentence_lengths) if original_sentence_lengths else 0
            
            optimized_sentences = re.split(r'[.!?]', optimized_prompt.content)
            optimized_sentence_lengths = [len(s.strip().split()) for s in optimized_sentences if s.strip()]
            optimized_avg_sentence_length = sum(optimized_sentence_lengths) / len(optimized_sentence_lengths) if optimized_sentence_lengths else 0
            
            metrics["conciseness_avg_sentence_length_original"] = original_avg_sentence_length
            metrics["conciseness_avg_sentence_length_optimized"] = optimized_avg_sentence_length
            metrics["conciseness_avg_sentence_length_change"] = optimized_avg_sentence_length - original_avg_sentence_length
        
        if "performance" in optimization_goals:
            # Simple performance metric based on performance-related terms
            performance_terms = ["efficient", "performance", "optimize", "prioritize", "step-by-step"]
            original_performance = sum(original_prompt.content.lower().count(term) for term in performance_terms)
            optimized_performance = sum(optimized_prompt.content.lower().count(term) for term in performance_terms)
            metrics["performance_term_count_change"] = optimized_performance - original_performance
        
        # Overall improvement score (simplified)
        improvement_score = 0.0
        score_components = 0
        
        if "clarity" in optimization_goals and metrics.get("clarity_section_count_change", 0) > 0:
            improvement_score += 0.25
            score_components += 1
        
        if "specificity" in optimization_goals and metrics.get("specificity_term_count_change", 0) > 0:
            improvement_score += 0.25
            score_components += 1
        
        if "conciseness" in optimization_goals and metrics.get("conciseness_avg_sentence_length_change", 0) < 0:
            improvement_score += 0.25
            score_components += 1
        
        if "performance" in optimization_goals and metrics.get("performance_term_count_change", 0) > 0:
            improvement_score += 0.25
            score_components += 1
        
        if score_components > 0:
            metrics["overall_improvement_score"] = improvement_score / score_components
        else:
            metrics["overall_improvement_score"] = 0.0
        
        return metrics

class AlphaEvolvePromptBroker:
    """
    AlphaEvolve Prompt Broker implementation for the Overseer System.
    
    This class provides methods for brokering prompts, including:
    - Managing deployment contexts
    - Gathering and integrating feedback
    - Generating and optimizing prompts
    - Validating prompts against constraints
    """
    
    def __init__(self):
        """Initialize the AlphaEvolve Prompt Broker."""
        self.context_gatherer = ContextGatherer()
        self.feedback_integrator = FeedbackIntegrator()
        self.prompt_optimizer = PromptOptimizer()
        logger.info("AlphaEvolve Prompt Broker initialized")
    
    # Context management methods
    
    def create_context(self, context: DeploymentContext) -> str:
        """
        Create a new deployment context.
        
        Args:
            context: The deployment context to create
            
        Returns:
            str: The context ID
        """
        return self.context_gatherer.create_context(context)
    
    def get_context(self, context_id: str) -> Optional[DeploymentContext]:
        """
        Get a deployment context by ID.
        
        Args:
            context_id: The context ID
            
        Returns:
            Optional[DeploymentContext]: The context, or None if not found
        """
        return self.context_gatherer.get_context(context_id)
    
    def update_context(self, context_id: str, context: DeploymentContext) -> bool:
        """
        Update a deployment context.
        
        Args:
            context_id: The context ID to update
            context: The updated context
            
        Returns:
            bool: True if successful, False if context not found
        """
        return self.context_gatherer.update_context(context_id, context)
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a deployment context.
        
        Args:
            context_id: The context ID to delete
            
        Returns:
            bool: True if successful, False if context not found
        """
        return self.context_gatherer.delete_context(context_id)
    
    def list_contexts(
        self,
        industry_filter: Optional[str] = None,
        environment_filter: Optional[str] = None,
        capability_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[DeploymentContext]:
        """
        List deployment contexts, optionally filtered.
        
        Args:
            industry_filter: Optional filter for industry
            environment_filter: Optional filter for environment
            capability_filter: Optional filter for system capability
            limit: Maximum number of contexts to return
            
        Returns:
            List[DeploymentContext]: List of matching contexts
        """
        return self.context_gatherer.list_contexts(
            industry_filter=industry_filter,
            environment_filter=environment_filter,
            capability_filter=capability_filter,
            limit=limit
        )
    
    def analyze_context(self, context_id: str) -> Dict[str, Any]:
        """
        Analyze a deployment context to extract key insights.
        
        Args:
            context_id: The context ID to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        return self.context_gatherer.analyze_context(context_id)
    
    # Feedback management methods
    
    def record_feedback(self, feedback: FeedbackEntry) -> str:
        """
        Record feedback for a prompt.
        
        Args:
            feedback: The feedback to record
            
        Returns:
            str: The feedback ID
        """
        return self.feedback_integrator.record_feedback(feedback)
    
    def get_feedback(self, feedback_id: str) -> Optional[FeedbackEntry]:
        """
        Get feedback by ID.
        
        Args:
            feedback_id: The feedback ID
            
        Returns:
            Optional[FeedbackEntry]: The feedback, or None if not found
        """
        return self.feedback_integrator.get_feedback(feedback_id)
    
    def list_feedback(
        self,
        prompt_id: Optional[str] = None,
        source_filter: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[FeedbackEntry]:
        """
        List feedback entries, optionally filtered.
        
        Args:
            prompt_id: Optional filter for prompt ID
            source_filter: Optional filter for feedback source
            min_rating: Optional minimum rating
            max_rating: Optional maximum rating
            start_date: Optional start date
            end_date: Optional end date
            limit: Maximum number of entries to return
            
        Returns:
            List[FeedbackEntry]: List of matching feedback entries
        """
        return self.feedback_integrator.list_feedback(
            prompt_id=prompt_id,
            source_filter=source_filter,
            min_rating=min_rating,
            max_rating=max_rating,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    def analyze_feedback(
        self,
        prompt_id: str,
        window_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze feedback for a prompt.
        
        Args:
            prompt_id: The prompt ID to analyze
            window_days: Optional window of days to analyze (from now)
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        return self.feedback_integrator.analyze_feedback(
            prompt_id=prompt_id,
            window_days=window_days
        )
    
    # Prompt management methods
    
    def create_prompt(self, prompt: Prompt) -> str:
        """
        Create a new prompt.
        
        Args:
            prompt: The prompt to create
            
        Returns:
            str: The prompt ID
        """
        return self.prompt_optimizer.create_prompt(prompt)
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """
        Get a prompt by ID.
        
        Args:
            prompt_id: The prompt ID
            
        Returns:
            Optional[Prompt]: The prompt, or None if not found
        """
        return self.prompt_optimizer.get_prompt(prompt_id)
    
    def update_prompt(self, prompt_id: str, prompt: Prompt) -> bool:
        """
        Update a prompt.
        
        Args:
            prompt_id: The prompt ID to update
            prompt: The updated prompt
            
        Returns:
            bool: True if successful, False if prompt not found
        """
        return self.prompt_optimizer.update_prompt(prompt_id, prompt)
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """
        Delete a prompt.
        
        Args:
            prompt_id: The prompt ID to delete
            
        Returns:
            bool: True if successful, False if prompt not found
        """
        return self.prompt_optimizer.delete_prompt(prompt_id)
    
    def list_prompts(
        self,
        name_filter: Optional[str] = None,
        context_id: Optional[str] = None,
        tag_filter: Optional[str] = None,
        min_performance: Optional[float] = None,
        limit: int = 100
    ) -> List[Prompt]:
        """
        List prompts, optionally filtered.
        
        Args:
            name_filter: Optional filter for prompt name (case-insensitive substring match)
            context_id: Optional filter for context ID
            tag_filter: Optional filter for tag
            min_performance: Optional minimum performance score
            limit: Maximum number of prompts to return
            
        Returns:
            List[Prompt]: List of matching prompts
        """
        return self.prompt_optimizer.list_prompts(
            name_filter=name_filter,
            context_id=context_id,
            tag_filter=tag_filter,
            min_performance=min_performance,
            limit=limit
        )
    
    # Constraint management methods
    
    def create_constraint(self, constraint: PromptConstraint) -> str:
        """
        Create a new prompt constraint.
        
        Args:
            constraint: The constraint to create
            
        Returns:
            str: The constraint ID
        """
        return self.prompt_optimizer.create_constraint(constraint)
    
    def get_constraint(self, constraint_id: str) -> Optional[PromptConstraint]:
        """
        Get a prompt constraint by ID.
        
        Args:
            constraint_id: The constraint ID
            
        Returns:
            Optional[PromptConstraint]: The constraint, or None if not found
        """
        return self.prompt_optimizer.get_constraint(constraint_id)
    
    def list_constraints(
        self,
        type_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[PromptConstraint]:
        """
        List prompt constraints, optionally filtered.
        
        Args:
            type_filter: Optional filter for constraint type
            severity_filter: Optional filter for constraint severity
            limit: Maximum number of constraints to return
            
        Returns:
            List[PromptConstraint]: List of matching constraints
        """
        return self.prompt_optimizer.list_constraints(
            type_filter=type_filter,
            severity_filter=severity_filter,
            limit=limit
        )
    
    def validate_prompt(
        self,
        prompt: Prompt,
        constraint_ids: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate a prompt against constraints.
        
        Args:
            prompt: The prompt to validate
            constraint_ids: Optional list of constraint IDs to validate against
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of validation errors)
        """
        return self.prompt_optimizer.validate_prompt(
            prompt=prompt,
            constraint_ids=constraint_ids
        )
    
    # Prompt generation and optimization methods
    
    def generate_prompt(self, request: PromptGenerationRequest) -> PromptGenerationResult:
        """
        Generate a new prompt based on the request.
        
        Args:
            request: The generation request
            
        Returns:
            PromptGenerationResult: The generation result
        """
        return self.prompt_optimizer.generate_prompt(
            request=request,
            context_gatherer=self.context_gatherer,
            feedback_integrator=self.feedback_integrator
        )
    
    def optimize_prompt(self, request: PromptOptimizationRequest) -> PromptOptimizationResult:
        """
        Optimize a prompt based on feedback and goals.
        
        Args:
            request: The optimization request
            
        Returns:
            PromptOptimizationResult: The optimization result
        """
        return self.prompt_optimizer.optimize_prompt(
            request=request,
            feedback_integrator=self.feedback_integrator
        )
    
    def get_generation_result(self, result_id: str) -> Optional[PromptGenerationResult]:
        """
        Get a prompt generation result by ID.
        
        Args:
            result_id: The result ID
            
        Returns:
            Optional[PromptGenerationResult]: The result, or None if not found
        """
        return self.prompt_optimizer.get_generation_result(result_id)
    
    def get_optimization_result(self, result_id: str) -> Optional[PromptOptimizationResult]:
        """
        Get a prompt optimization result by ID.
        
        Args:
            result_id: The result ID
            
        Returns:
            Optional[PromptOptimizationResult]: The result, or None if not found
        """
        return self.prompt_optimizer.get_optimization_result(result_id)
