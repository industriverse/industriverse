"""
A2A Agent Schema for the Overseer System.

This module defines the schema for A2A agents used in the Overseer System.
"""

from enum import Enum
from typing import Dict, Any, List, Optional

class A2ACapabilityType(str, Enum):
    """Enumeration of A2A agent capabilities."""
    
    # Core capabilities
    TASK_EXECUTION = "task.execution"
    BIDDING = "task.bidding"
    WORKFLOW_EXECUTION = "workflow.execution"
    LEARNING = "agent.learning"
    COLLABORATION = "agent.collaboration"
    
    # Specialized capabilities
    DATA_PROCESSING = "data.processing"
    DATA_ANALYSIS = "data.analysis"
    CONTENT_GENERATION = "content.generation"
    SYSTEM_MONITORING = "system.monitoring"
    RESOURCE_OPTIMIZATION = "resource.optimization"
    ANOMALY_DETECTION = "anomaly.detection"
    MAINTENANCE_SCHEDULING = "maintenance.scheduling"
    COMPLIANCE_VALIDATION = "compliance.validation"
    SCENARIO_SIMULATION = "scenario.simulation"
    ETHICS_ENFORCEMENT = "ethics.enforcement"
    TRUST_MANAGEMENT = "trust.management"
    CAPSULE_EVOLUTION = "capsule.evolution"
    MARKET_STABILIZATION = "market.stabilization"
    TWIN_NEGOTIATION = "twin.negotiation"
    SHADOW_MANAGEMENT = "shadow.management"

class A2ATaskType(str, Enum):
    """Enumeration of A2A task types."""
    
    # Data tasks
    PROCESS_DATA = "process.data"
    ANALYZE_DATA = "analyze.data"
    GENERATE_CONTENT = "generate.content"
    
    # System tasks
    EXECUTE_WORKFLOW = "execute.workflow"
    MONITOR_SYSTEM = "monitor.system"
    OPTIMIZE_RESOURCE = "optimize.resource"
    
    # Specialized tasks
    DETECT_ANOMALY = "detect.anomaly"
    SCHEDULE_MAINTENANCE = "schedule.maintenance"
    VALIDATE_COMPLIANCE = "validate.compliance"
    SIMULATE_SCENARIO = "simulate.scenario"
    
    # Capsule tasks
    INSTANTIATE_CAPSULE = "instantiate.capsule"
    EVOLVE_CAPSULE = "evolve.capsule"
    EVALUATE_CAPSULE = "evaluate.capsule"
    RETIRE_CAPSULE = "retire.capsule"
    
    # Ethics tasks
    CHECK_ETHICS = "check.ethics"
    HANDLE_VIOLATION = "handle.violation"
    ESCALATE_ISSUE = "escalate.issue"
    
    # Trust tasks
    SIMULATE_DRIFT = "simulate.drift"
    ASSIGN_REDEMPTION = "assign.redemption"
    TRIGGER_ROLLBACK = "trigger.rollback"
    
    # Market tasks
    STABILIZE_MARKET = "stabilize.market"
    MANAGE_BID = "manage.bid"
    
    # Twin tasks
    NEGOTIATE_AGREEMENT = "negotiate.agreement"
    MANAGE_SHADOW = "manage.shadow"

class A2AIndustryTag(str, Enum):
    """Enumeration of A2A industry tags."""
    
    # General industries
    MANUFACTURING = "industry.manufacturing"
    HEALTHCARE = "industry.healthcare"
    CONSTRUCTION = "industry.construction"
    RETAIL = "industry.retail"
    FIELD_SERVICE = "industry.field_service"
    FRANCHISE = "industry.franchise"
    
    # Specialized industries
    DEFENSE = "industry.defense"
    AEROSPACE = "industry.aerospace"
    DATA_CENTER = "industry.data_center"
    EDGE_COMPUTING = "industry.edge_computing"
    AI = "industry.ai"
    IOT = "industry.iot"
    PRECISION_MANUFACTURING = "industry.precision_manufacturing"

class A2AAgentSchema:
    """Schema definitions for A2A agents."""
    
    @staticmethod
    def get_schema_for_task_type(task_type: str) -> Dict[str, Any]:
        """
        Get the schema for a specific task type.
        
        Args:
            task_type: Type of task
            
        Returns:
            JSON schema for the task input and output
        """
        # Data tasks
        if task_type == A2ATaskType.PROCESS_DATA:
            return {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "array"},
                        "operations": {"type": "array", "items": {"type": "string"}},
                        "parameters": {"type": "object"}
                    },
                    "required": ["data", "operations"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "processed_data": {"type": "array"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["processed_data"]
                }
            }
        elif task_type == A2ATaskType.ANALYZE_DATA:
            return {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "array"},
                        "analysis_type": {"type": "string"},
                        "parameters": {"type": "object"}
                    },
                    "required": ["data", "analysis_type"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "results": {"type": "object"},
                        "insights": {"type": "array", "items": {"type": "string"}},
                        "visualizations": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["results"]
                }
            }
        elif task_type == A2ATaskType.GENERATE_CONTENT:
            return {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string"},
                        "parameters": {"type": "object"},
                        "context": {"type": "object"}
                    },
                    "required": ["content_type"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["content"]
                }
            }
            
        # System tasks
        elif task_type == A2ATaskType.EXECUTE_WORKFLOW:
            return {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "input_data": {"type": "object"},
                        "parameters": {"type": "object"}
                    },
                    "required": ["workflow_id"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string"},
                        "status": {"type": "string"},
                        "output_data": {"type": "object"}
                    },
                    "required": ["execution_id", "status"]
                }
            }
        elif task_type == A2ATaskType.MONITOR_SYSTEM:
            return {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "system_id": {"type": "string"},
                        "metrics": {"type": "array", "items": {"type": "string"}},
                        "duration": {"type": "integer"}
                    },
                    "required": ["system_id"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "metrics_data": {"type": "object"},
                        "alerts": {"type": "array", "items": {"type": "object"}},
                        "status": {"type": "string"}
                    },
                    "required": ["metrics_data", "status"]
                }
            }
        elif task_type == A2ATaskType.OPTIMIZE_RESOURCE:
            return {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {"type": "string"},
                        "constraints": {"type": "object"},
                        "objectives": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["resource_type", "objectives"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "optimization_result": {"type": "object"},
                        "recommendations": {"type": "array", "items": {"type": "object"}},
                        "metrics": {"type": "object"}
                    },
                    "required": ["optimization_result"]
                }
            }
            
        # Default schema
        return {
            "input_schema": {
                "type": "object",
                "additionalProperties": True
            },
            "output_schema": {
                "type": "object",
                "additionalProperties": True
            }
        }
