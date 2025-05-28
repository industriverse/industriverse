"""
MCP Context Schema for the Overseer System.

This module defines the schema for MCP contexts used in the Overseer System.
"""

from enum import Enum
from typing import Dict, Any, List, Optional

class MCPContextType(str, Enum):
    """Enumeration of MCP context types."""
    
    # System contexts
    SYSTEM_HEARTBEAT = "system.heartbeat"
    SYSTEM_CONFIG_UPDATE = "system.config.update"
    SYSTEM_STATUS = "system.status"
    
    # Agent contexts
    AGENT_REGISTRATION = "agent.registration"
    AGENT_STATUS_UPDATE = "agent.status.update"
    AGENT_CAPABILITY_UPDATE = "agent.capability.update"
    
    # Capsule contexts
    CAPSULE_INSTANTIATION = "capsule.instantiation"
    CAPSULE_LIFECYCLE_UPDATE = "capsule.lifecycle.update"
    CAPSULE_TRUST_UPDATE = "capsule.trust.update"
    CAPSULE_EVOLUTION = "capsule.evolution"
    CAPSULE_LINEAGE_UPDATE = "capsule.lineage.update"
    CAPSULE_RETIREMENT = "capsule.retirement"
    CAPSULE_ETHICS_CHECK = "capsule.ethics.check"
    CAPSULE_ETHICS_VIOLATION = "capsule.ethics.violation"
    CAPSULE_REDEMPTION = "capsule.redemption"
    
    # Process contexts
    PROCESS_DEFINITION = "process.definition"
    PROCESS_EXECUTION = "process.execution"
    PROCESS_STATUS_UPDATE = "process.status.update"
    
    # Monitoring contexts
    MONITORING_METRIC = "monitoring.metric"
    MONITORING_ALERT = "monitoring.alert"
    MONITORING_ANOMALY = "monitoring.anomaly"
    
    # Analytics contexts
    ANALYTICS_REPORT = "analytics.report"
    ANALYTICS_INSIGHT = "analytics.insight"
    
    # Optimization contexts
    OPTIMIZATION_RECOMMENDATION = "optimization.recommendation"
    OPTIMIZATION_EXECUTION = "optimization.execution"
    
    # Compliance contexts
    COMPLIANCE_CHECK = "compliance.check"
    COMPLIANCE_VIOLATION = "compliance.violation"
    COMPLIANCE_REPORT = "compliance.report"
    
    # Simulation contexts
    SIMULATION_SCENARIO = "simulation.scenario"
    SIMULATION_EXECUTION = "simulation.execution"
    SIMULATION_RESULT = "simulation.result"
    SIMULATION_CLONE = "simulation.clone"
    SIMULATION_VARIANT = "simulation.variant"
    
    # Ethics contexts
    ETHICS_CHECK = "ethics.check"
    ETHICS_VIOLATION = "ethics.violation"
    ETHICS_ESCALATION = "ethics.escalation"
    
    # Digital twin contexts
    TWIN_NEGOTIATION = "twin.negotiation"
    TWIN_AGREEMENT = "twin.agreement"
    TWIN_CONFLICT = "twin.conflict"
    TWIN_SHADOW = "twin.shadow"
    
    # Market contexts
    MARKET_BID = "market.bid"
    MARKET_AWARD = "market.award"
    MARKET_STABILIZATION = "market.stabilization"
    
    # Evolution contexts
    EVOLUTION_GENOTYPE = "evolution.genotype"
    EVOLUTION_BREEDING = "evolution.breeding"
    EVOLUTION_EVALUATION = "evolution.evaluation"
    
    # Integration contexts
    INTEGRATION_DATA_LAYER = "integration.data_layer"
    INTEGRATION_CORE_AI_LAYER = "integration.core_ai_layer"
    INTEGRATION_GENERATIVE_LAYER = "integration.generative_layer"
    INTEGRATION_APPLICATION_LAYER = "integration.application_layer"
    INTEGRATION_PROTOCOL_LAYER = "integration.protocol_layer"
    INTEGRATION_WORKFLOW_LAYER = "integration.workflow_layer"
    INTEGRATION_DEPLOYMENT_LAYER = "integration.deployment_layer"
    INTEGRATION_SECURITY_LAYER = "integration.security_layer"
    INTEGRATION_UI_LAYER = "integration.ui_layer"

class MCPContextSchema:
    """Schema definitions for MCP contexts."""
    
    @staticmethod
    def get_schema_for_context_type(context_type: str) -> Dict[str, Any]:
        """
        Get the schema for a specific context type.
        
        Args:
            context_type: Type of context
            
        Returns:
            JSON schema for the context payload
        """
        # System contexts
        if context_type == MCPContextType.SYSTEM_HEARTBEAT:
            return {
                "type": "object",
                "properties": {
                    "service_name": {"type": "string"},
                    "status": {"type": "string", "enum": ["online", "offline", "degraded"]},
                    "timestamp": {"type": "string", "format": "date-time"}
                },
                "required": ["service_name", "status", "timestamp"]
            }
        elif context_type == MCPContextType.SYSTEM_CONFIG_UPDATE:
            return {
                "type": "object",
                "properties": {
                    "component": {"type": "string"},
                    "key": {"type": "string"},
                    "value": {"type": "object"},
                    "environment": {"type": "string"}
                },
                "required": ["component", "key", "value"]
            }
        elif context_type == MCPContextType.SYSTEM_STATUS:
            return {
                "type": "object",
                "properties": {
                    "component": {"type": "string"},
                    "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"]},
                    "details": {"type": "object"}
                },
                "required": ["component", "status"]
            }
            
        # Agent contexts
        elif context_type == MCPContextType.AGENT_REGISTRATION:
            return {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "capabilities": {"type": "array", "items": {"type": "string"}},
                    "api_url": {"type": "string"}
                },
                "required": ["agent_id", "name", "capabilities"]
            }
        elif context_type == MCPContextType.AGENT_STATUS_UPDATE:
            return {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["online", "offline", "busy", "idle"]},
                    "details": {"type": "object"}
                },
                "required": ["agent_id", "status"]
            }
        elif context_type == MCPContextType.AGENT_CAPABILITY_UPDATE:
            return {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "capabilities": {"type": "array", "items": {"type": "string"}},
                    "operation": {"type": "string", "enum": ["add", "remove", "replace"]}
                },
                "required": ["agent_id", "capabilities", "operation"]
            }
            
        # Capsule contexts
        elif context_type == MCPContextType.CAPSULE_INSTANTIATION:
            return {
                "type": "object",
                "properties": {
                    "capsule_id": {"type": "string"},
                    "blueprint_id": {"type": "string"},
                    "parameters": {"type": "object"},
                    "environment": {"type": "object"}
                },
                "required": ["capsule_id", "blueprint_id"]
            }
        elif context_type == MCPContextType.CAPSULE_LIFECYCLE_UPDATE:
            return {
                "type": "object",
                "properties": {
                    "capsule_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["created", "initialized", "running", "paused", "stopped", "failed", "retired"]},
                    "details": {"type": "object"}
                },
                "required": ["capsule_id", "status"]
            }
        elif context_type == MCPContextType.CAPSULE_TRUST_UPDATE:
            return {
                "type": "object",
                "properties": {
                    "capsule_id": {"type": "string"},
                    "trust_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "reason": {"type": "string"},
                    "evidence": {"type": "object"}
                },
                "required": ["capsule_id", "trust_score"]
            }
        elif context_type == MCPContextType.CAPSULE_EVOLUTION:
            return {
                "type": "object",
                "properties": {
                    "capsule_id": {"type": "string"},
                    "parent_ids": {"type": "array", "items": {"type": "string"}},
                    "mutation_type": {"type": "string", "enum": ["breeding", "optimization", "adaptation"]},
                    "changes": {"type": "object"}
                },
                "required": ["capsule_id", "mutation_type"]
            }
        elif context_type == MCPContextType.CAPSULE_LINEAGE_UPDATE:
            return {
                "type": "object",
                "properties": {
                    "capsule_id": {"type": "string"},
                    "parent_ids": {"type": "array", "items": {"type": "string"}},
                    "lineage_tree": {"type": "object"},
                    "certificate": {"type": "string"}
                },
                "required": ["capsule_id"]
            }
        elif context_type == MCPContextType.CAPSULE_RETIREMENT:
            return {
                "type": "object",
                "properties": {
                    "capsule_id": {"type": "string"},
                    "reason": {"type": "string"},
                    "legacy_data": {"type": "object"},
                    "replacement_id": {"type": "string"}
                },
                "required": ["capsule_id", "reason"]
            }
        elif context_type == MCPContextType.CAPSULE_ETHICS_CHECK:
            return {
                "type": "object",
                "properties": {
                    "capsule_id": {"type": "string"},
                    "decision": {"type": "object"},
                    "rules": {"type": "array", "items": {"type": "string"}},
                    "result": {"type": "string", "enum": ["pass", "fail", "warning"]}
                },
                "required": ["capsule_id", "decision", "result"]
            }
        elif context_type == MCPContextType.CAPSULE_ETHICS_VIOLATION:
            return {
                "type": "object",
                "properties": {
                    "capsule_id": {"type": "string"},
                    "decision": {"type": "object"},
                    "violated_rules": {"type": "array", "items": {"type": "string"}},
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                },
                "required": ["capsule_id", "decision", "violated_rules", "severity"]
            }
        elif context_type == MCPContextType.CAPSULE_REDEMPTION:
            return {
                "type": "object",
                "properties": {
                    "capsule_id": {"type": "string"},
                    "mission_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["assigned", "in_progress", "completed", "failed"]},
                    "trust_impact": {"type": "number"}
                },
                "required": ["capsule_id", "mission_id", "status"]
            }
            
        # Process contexts
        elif context_type == MCPContextType.PROCESS_DEFINITION:
            return {
                "type": "object",
                "properties": {
                    "process_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "steps": {"type": "array", "items": {"type": "object"}},
                    "input_schema": {"type": "object"},
                    "output_schema": {"type": "object"}
                },
                "required": ["process_id", "name", "steps"]
            }
        elif context_type == MCPContextType.PROCESS_EXECUTION:
            return {
                "type": "object",
                "properties": {
                    "process_id": {"type": "string"},
                    "execution_id": {"type": "string"},
                    "input_data": {"type": "object"},
                    "parameters": {"type": "object"}
                },
                "required": ["process_id", "execution_id"]
            }
        elif context_type == MCPContextType.PROCESS_STATUS_UPDATE:
            return {
                "type": "object",
                "properties": {
                    "process_id": {"type": "string"},
                    "execution_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["started", "in_progress", "completed", "failed", "cancelled"]},
                    "current_step": {"type": "integer"},
                    "progress": {"type": "number", "minimum": 0, "maximum": 100},
                    "output_data": {"type": "object"},
                    "error": {"type": "string"}
                },
                "required": ["process_id", "execution_id", "status"]
            }
            
        # Default schema
        return {
            "type": "object",
            "additionalProperties": True
        }
