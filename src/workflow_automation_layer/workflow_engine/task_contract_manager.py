"""
Task Contract Manager Module for Industriverse Workflow Automation Layer

This module is responsible for managing task contracts, which define the agreements,
expectations, and requirements for tasks within workflows. Task contracts include
input/output schemas, SLAs, fallback plans, and trust models.

The TaskContract class is the central data model that represents a complete
task contract with all its specifications and requirements.
"""

import logging
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator

import yaml

# Configure logging
logger = logging.getLogger(__name__)


class ContractStatus(str, Enum):
    """Enum representing the possible statuses of a task contract."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class TrustLevel(str, Enum):
    """Enum representing the trust levels for task execution."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SLADefinition(BaseModel):
    """Model representing a Service Level Agreement for a task."""
    response_time_ms: Optional[int] = None
    completion_time_ms: Optional[int] = None
    availability_percent: Optional[float] = None
    success_rate_percent: Optional[float] = None
    max_retries: Optional[int] = None
    retry_delay_ms: Optional[int] = None


class FallbackPlan(BaseModel):
    """Model representing a fallback plan for a task."""
    condition: str  # e.g., "response_time > 5000" or "success_rate < 0.9"
    action: str  # e.g., "retry", "escalate", "alternative_task"
    alternative_task_id: Optional[str] = None
    max_attempts: Optional[int] = None
    escalation_path: Optional[str] = None


class SchemaProperty(BaseModel):
    """Model representing a property in a schema."""
    type: str
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    format: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    pattern: Optional[str] = None


class Schema(BaseModel):
    """Model representing a schema for inputs or outputs."""
    type: str = "object"
    properties: Dict[str, SchemaProperty] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)
    
    @validator('required')
    def validate_required(cls, required, values):
        """Validate that required properties exist in the properties dict."""
        if 'properties' in values:
            for prop in required:
                if prop not in values['properties']:
                    raise ValueError(f"Required property '{prop}' not defined in properties")
        return required


class BidCriteria(BaseModel):
    """Model representing criteria for agent bidding in the escalation protocol."""
    name: str
    weight: float = 1.0
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class BidSystem(BaseModel):
    """Model representing a bidding system for agent selection."""
    enabled: bool = False
    criteria: List[str] = Field(default_factory=list)
    timeout_ms: int = 500
    min_bids: int = 1
    max_bids: Optional[int] = None
    bid_criteria: List[BidCriteria] = Field(default_factory=list)


class EscalationProtocol(BaseModel):
    """Model representing the escalation protocol for a task."""
    trigger: str
    resolve_with: str
    fallback: str
    bid_system: Optional[BidSystem] = None


class TaskContract(BaseModel):
    """
    Model representing a complete task contract.
    
    This is the central data structure that defines the agreement, expectations,
    and requirements for a task within a workflow.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    status: ContractStatus = ContractStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Task specifications
    task_type: str
    agent_id: Optional[str] = None
    input_schema: Schema
    output_schema: Schema
    
    # Performance and reliability
    trust_level: TrustLevel = TrustLevel.MEDIUM
    sla: Optional[SLADefinition] = None
    fallback_plans: List[FallbackPlan] = Field(default_factory=list)
    
    # Escalation and human intervention
    escalation_protocol: Optional[EscalationProtocol] = None
    human_approval_required: bool = False
    
    # Integration
    mcp_events: List[str] = Field(default_factory=list)
    a2a_capabilities: List[str] = Field(default_factory=list)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    industry: Optional[str] = None
    
    def is_compatible_with(self, other: 'TaskContract') -> bool:
        """
        Check if this contract is compatible with another contract.
        
        Args:
            other: The other TaskContract to check compatibility with
            
        Returns:
            True if compatible, False otherwise
        """
        # Check if output schema of this contract is compatible with input schema of other
        # This is a simplified check - in a real implementation, we would do a more thorough schema validation
        for required_prop in other.input_schema.required:
            if required_prop not in self.output_schema.properties:
                return False
        
        return True


class TaskContractManager:
    """
    Manager for task contracts.
    
    This class provides methods to create, validate, store, and retrieve task contracts.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the TaskContractManager.
        
        Args:
            storage_path: Optional path to store contracts on disk
        """
        self.contracts: Dict[str, TaskContract] = {}
        self.storage_path = storage_path
        
        logger.info("TaskContractManager initialized")
    
    def create_contract(self, contract_data: Dict[str, Any]) -> TaskContract:
        """
        Create a new task contract.
        
        Args:
            contract_data: Dictionary containing contract data
            
        Returns:
            The created TaskContract
            
        Raises:
            ValueError: If the contract data is invalid
        """
        try:
            contract = TaskContract(**contract_data)
            self.contracts[contract.id] = contract
            
            logger.info(f"Created task contract {contract.id}: {contract.name}")
            return contract
        except Exception as e:
            logger.error(f"Failed to create task contract: {e}")
            raise ValueError(f"Invalid task contract data: {e}")
    
    def get_contract(self, contract_id: str) -> Optional[TaskContract]:
        """
        Get a task contract by ID.
        
        Args:
            contract_id: The ID of the contract to retrieve
            
        Returns:
            The TaskContract if found, None otherwise
        """
        return self.contracts.get(contract_id)
    
    def update_contract(self, contract_id: str, contract_data: Dict[str, Any]) -> TaskContract:
        """
        Update an existing task contract.
        
        Args:
            contract_id: The ID of the contract to update
            contract_data: Dictionary containing updated contract data
            
        Returns:
            The updated TaskContract
            
        Raises:
            ValueError: If the contract doesn't exist or the data is invalid
        """
        if contract_id not in self.contracts:
            raise ValueError(f"Task contract {contract_id} not found")
        
        try:
            # Preserve the ID and created_at
            contract_data['id'] = contract_id
            contract_data['created_at'] = self.contracts[contract_id].created_at
            contract_data['updated_at'] = datetime.now()
            
            contract = TaskContract(**contract_data)
            self.contracts[contract_id] = contract
            
            logger.info(f"Updated task contract {contract_id}")
            return contract
        except Exception as e:
            logger.error(f"Failed to update task contract {contract_id}: {e}")
            raise ValueError(f"Invalid task contract data: {e}")
    
    def delete_contract(self, contract_id: str) -> bool:
        """
        Delete a task contract.
        
        Args:
            contract_id: The ID of the contract to delete
            
        Returns:
            True if the contract was deleted, False if it wasn't found
        """
        if contract_id in self.contracts:
            del self.contracts[contract_id]
            logger.info(f"Deleted task contract {contract_id}")
            return True
        
        logger.warning(f"Attempted to delete non-existent task contract {contract_id}")
        return False
    
    def list_contracts(self, 
                      status: Optional[ContractStatus] = None, 
                      task_type: Optional[str] = None,
                      trust_level: Optional[TrustLevel] = None,
                      tags: Optional[List[str]] = None,
                      industry: Optional[str] = None) -> List[TaskContract]:
        """
        List task contracts, optionally filtered by various criteria.
        
        Args:
            status: Filter by contract status
            task_type: Filter by task type
            trust_level: Filter by trust level
            tags: Filter by tags (contracts must have all specified tags)
            industry: Filter by industry
            
        Returns:
            A list of TaskContract objects matching the criteria
        """
        result = list(self.contracts.values())
        
        # Apply filters
        if status:
            result = [c for c in result if c.status == status]
        
        if task_type:
            result = [c for c in result if c.task_type == task_type]
        
        if trust_level:
            result = [c for c in result if c.trust_level == trust_level]
        
        if tags:
            result = [c for c in result if all(tag in c.tags for tag in tags)]
        
        if industry:
            result = [c for c in result if c.industry == industry]
        
        return result
    
    def validate_contract(self, contract: TaskContract) -> List[str]:
        """
        Validate a task contract beyond schema validation.
        
        Args:
            contract: The TaskContract to validate
            
        Returns:
            A list of validation error messages, empty if valid
        """
        errors = []
        
        # Check for required fields based on task type
        if contract.task_type == "http_request" and "url" not in contract.input_schema.properties:
            errors.append("HTTP request tasks must have a 'url' input property")
        
        # Check for valid fallback plans
        for plan in contract.fallback_plans:
            if plan.action == "alternative_task" and not plan.alternative_task_id:
                errors.append(f"Fallback plan with action 'alternative_task' must specify an alternative_task_id")
        
        # Check for valid escalation protocol
        if contract.escalation_protocol and contract.escalation_protocol.bid_system and contract.escalation_protocol.bid_system.enabled:
            if not contract.escalation_protocol.bid_system.criteria:
                errors.append("Bid system must specify at least one criterion")
        
        return errors
    
    def export_to_yaml(self, contract_id: str) -> str:
        """
        Export a task contract to YAML.
        
        Args:
            contract_id: The ID of the contract to export
            
        Returns:
            A YAML string representation of the contract
            
        Raises:
            ValueError: If the contract doesn't exist
        """
        contract = self.get_contract(contract_id)
        if not contract:
            raise ValueError(f"Task contract {contract_id} not found")
        
        # Convert to dict first to handle datetime serialization
        contract_dict = contract.dict()
        
        # Convert datetime objects to ISO format strings
        contract_dict['created_at'] = contract_dict['created_at'].isoformat()
        contract_dict['updated_at'] = contract_dict['updated_at'].isoformat()
        
        return yaml.dump(contract_dict, sort_keys=False)
    
    def import_from_yaml(self, yaml_str: str) -> TaskContract:
        """
        Import a task contract from YAML.
        
        Args:
            yaml_str: YAML string representation of a contract
            
        Returns:
            The imported TaskContract
            
        Raises:
            ValueError: If the YAML is invalid or doesn't conform to the schema
        """
        try:
            contract_dict = yaml.safe_load(yaml_str)
            return self.create_contract(contract_dict)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise ValueError(f"Invalid YAML: {e}")
        except Exception as e:
            logger.error(f"Failed to import task contract: {e}")
            raise ValueError(f"Invalid task contract: {e}")
    
    def create_contract_from_template(self, template_name: str, **kwargs) -> TaskContract:
        """
        Create a task contract from a predefined template.
        
        Args:
            template_name: The name of the template to use
            **kwargs: Template-specific parameters
            
        Returns:
            The created TaskContract
            
        Raises:
            ValueError: If the template doesn't exist or the parameters are invalid
        """
        if template_name == "http_request":
            return self._create_http_request_template(**kwargs)
        elif template_name == "human_approval":
            return self._create_human_approval_template(**kwargs)
        elif template_name == "agent_task":
            return self._create_agent_task_template(**kwargs)
        else:
            raise ValueError(f"Unknown template: {template_name}")
    
    def _create_http_request_template(self, **kwargs) -> TaskContract:
        """Create a template for HTTP request tasks."""
        name = kwargs.get("name", "HTTP Request")
        description = kwargs.get("description", "Performs an HTTP request to a specified URL")
        
        contract_data = {
            "name": name,
            "description": description,
            "task_type": "http_request",
            "input_schema": {
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to send the request to",
                        "required": True
                    },
                    "method": {
                        "type": "string",
                        "description": "The HTTP method to use",
                        "required": True,
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers to include in the request"
                    },
                    "body": {
                        "type": "string",
                        "description": "Request body for POST, PUT, or PATCH requests"
                    }
                },
                "required": ["url", "method"]
            },
            "output_schema": {
                "properties": {
                    "status_code": {
                        "type": "integer",
                        "description": "HTTP status code of the response"
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers from the response"
                    },
                    "body": {
                        "type": "string",
                        "description": "Response body"
                    }
                },
                "required": ["status_code"]
            },
            "sla": {
                "response_time_ms": 5000,
                "max_retries": 3,
                "retry_delay_ms": 1000
            },
            "fallback_plans": [
                {
                    "condition": "status_code >= 400",
                    "action": "retry",
                    "max_attempts": 3
                },
                {
                    "condition": "response_time_ms > 5000",
                    "action": "escalate",
                    "escalation_path": "timeout_handler"
                }
            ],
            "tags": ["http", "integration"]
        }
        
        # Override with any provided kwargs
        for key, value in kwargs.items():
            if key not in ["name", "description"]:
                if isinstance(value, dict) and key in contract_data and isinstance(contract_data[key], dict):
                    # Merge dictionaries
                    contract_data[key].update(value)
                else:
                    # Replace value
                    contract_data[key] = value
        
        return self.create_contract(contract_data)
    
    def _create_human_approval_template(self, **kwargs) -> TaskContract:
        """Create a template for human approval tasks."""
        name = kwargs.get("name", "Human Approval")
        description = kwargs.get("description", "Requires human approval to proceed")
        
        contract_data = {
            "name": name,
            "description": description,
            "task_type": "human_approval",
            "human_approval_required": True,
            "input_schema": {
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the approval request",
                        "required": True
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what needs to be approved"
                    },
                    "options": {
                        "type": "array",
                        "description": "Options for the approver to choose from"
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Time in seconds before the approval request times out"
                    }
                },
                "required": ["title"]
            },
            "output_schema": {
                "properties": {
                    "approved": {
                        "type": "boolean",
                        "description": "Whether the request was approved"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Optional comment from the approver"
                    },
                    "selected_option": {
                        "type": "string",
                        "description": "The option selected by the approver, if applicable"
                    },
                    "approver_id": {
                        "type": "string",
                        "description": "ID of the user who approved or rejected the request"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Timestamp of the approval or rejection"
                    }
                },
                "required": ["approved"]
            },
            "sla": {
                "completion_time_ms": 86400000,  # 24 hours
            },
            "escalation_protocol": {
                "trigger": "timeout_seconds elapsed",
                "resolve_with": "escalation_manager",
                "fallback": "auto_approve_agent",
                "bid_system": {
                    "enabled": True,
                    "criteria": ["availability", "response_time"],
                    "timeout_ms": 10000
                }
            },
            "tags": ["human", "approval", "workflow"]
        }
        
        # Override with any provided kwargs
        for key, value in kwargs.items():
            if key not in ["name", "description"]:
                if isinstance(value, dict) and key in contract_data and isinstance(contract_data[key], dict):
                    # Merge dictionaries
                    contract_data[key].update(value)
                else:
                    # Replace value
                    contract_data[key] = value
        
        return self.create_contract(contract_data)
    
    def _create_agent_task_template(self, **kwargs) -> TaskContract:
        """Create a template for agent tasks."""
        name = kwargs.get("name", "Agent Task")
        description = kwargs.get("description", "Task executed by an agent")
        agent_id = kwargs.get("agent_id", "default_agent")
        
        contract_data = {
            "name": name,
            "description": description,
            "task_type": "agent_task",
            "agent_id": agent_id,
            "input_schema": {
                "properties": {
                    "task_data": {
                        "type": "object",
                        "description": "Data required for the agent to execute the task",
                        "required": True
                    },
                    "context": {
                        "type": "object",
                        "description": "Context information for the agent"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Priority of the task (1-10, higher is more important)",
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["task_data"]
            },
            "output_schema": {
                "properties": {
                    "result": {
                        "type": "object",
                        "description": "Result of the agent task execution"
                    },
                    "status": {
                        "type": "string",
                        "description": "Status of the task execution",
                        "enum": ["success", "failure", "partial"]
                    },
                    "message": {
                        "type": "string",
                        "description": "Message from the agent"
                    }
                },
                "required": ["status"]
            },
            "trust_level": TrustLevel.MEDIUM,
            "sla": {
                "response_time_ms": 1000,
                "completion_time_ms": 10000,
                "success_rate_percent": 95.0
            },
            "fallback_plans": [
                {
                    "condition": "status == 'failure'",
                    "action": "retry",
                    "max_attempts": 3
                },
                {
                    "condition": "completion_time_ms > 10000",
                    "action": "alternative_task",
                    "alternative_task_id": "fallback_agent_task"
                }
            ],
            "mcp_events": ["agent/task_assigned", "agent/task_completed"],
            "a2a_capabilities": ["task_execution", "status_reporting"],
            "tags": ["agent", "automation"]
        }
        
        # Override with any provided kwargs
        for key, value in kwargs.items():
            if key not in ["name", "description", "agent_id"]:
                if isinstance(value, dict) and key in contract_data and isinstance(contract_data[key], dict):
                    # Merge dictionaries
                    contract_data[key].update(value)
                else:
                    # Replace value
                    contract_data[key] = value
        
        return self.create_contract(contract_data)
