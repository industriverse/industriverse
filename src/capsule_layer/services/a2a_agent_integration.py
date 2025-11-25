"""
A2A (Agent-to-Agent) Integration for Thermodynamic Services

Transforms all thermodynamic services into discoverable, orchestratable agents
that can communicate via Agent-to-Agent protocol.

This connects:
- TOP: Thermodynamic computing (JAX/Jasmin/Thermodynasty + MicroAdapt)
- MIDDLE: A2A protocol (agent orchestration)
- BOTTOM: 10-layer Industriverse framework + DAC Factory

Key Features:
- Agent Card system for discovery
- MCP-enhanced context in A2A messages
- Host Agent for workflow orchestration
- Dynamic Agent Capsules UX
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

# ============================================================================
# AGENT CARD SYSTEM
# ============================================================================

class AgentCapability(BaseModel):
    """Agent capability definition"""
    skill: str = Field(..., description="Skill identifier (e.g., 'thermal_optimization')")
    description: str = Field(..., description="Human-readable description")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for input")
    output_schema: Dict[str, Any] = Field(..., description="JSON schema for output")
    mcp_enabled: bool = Field(default=True, description="Whether MCP context is supported")


class AgentStatus(str, Enum):
    """Agent operational status"""
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    OFFLINE = "offline"


class AgentCard(BaseModel):
    """
    Agent Card for service discovery
    
    Published by each thermodynamic service to enable
    agent-to-agent communication and orchestration.
    """
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="Agent description")
    version: str = Field(..., description="Agent version")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE, description="Current status")
    endpoint: str = Field(..., description="Agent endpoint URL")
    mcp_endpoint: Optional[str] = Field(None, description="MCP endpoint if available")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


# ============================================================================
# AGENT CARDS FOR THERMODYNAMIC SERVICES
# ============================================================================

THERMAL_SAMPLER_AGENT_CARD = AgentCard(
    agent_id="thermal_sampler_agent",
    name="Thermal Sampler Agent",
    description="Energy-based optimization using thermodynamic computing (thrml/TSU)",
    version="1.0.0",
    capabilities=[
        AgentCapability(
            skill="thermal_optimization",
            description="Solve combinatorial optimization problems using simulated annealing",
            input_schema={
                "type": "object",
                "properties": {
                    "problem_type": {"type": "string"},
                    "variables": {"type": "integer"},
                    "constraints": {"type": "array"},
                    "num_samples": {"type": "integer"},
                    "temperature": {"type": "number"}
                },
                "required": ["problem_type", "variables"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "sampling_id": {"type": "string"},
                    "best_solution": {"type": "object"},
                    "best_energy": {"type": "number"},
                    "convergence_history": {"type": "array"}
                }
            }
        ),
        AgentCapability(
            skill="energy_landscape_creation",
            description="Create energy landscapes for constraint encoding",
            input_schema={
                "type": "object",
                "properties": {
                    "problem_type": {"type": "string"},
                    "dimensions": {"type": "integer"},
                    "constraints": {"type": "array"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "landscape_id": {"type": "string"},
                    "dimensions": {"type": "integer"}
                }
            }
        )
    ],
    endpoint="/api/v1/thermodynamic/thermal",
    mcp_endpoint="/api/v1/thermodynamic/thermal",
    metadata={
        "domain": "thermodynamic_computing",
        "edge_compatible": True,
        "real_time": True
    }
)

WORLD_MODEL_AGENT_CARD = AgentCard(
    agent_id="world_model_agent",
    name="World Model Agent",
    description="Physics-based simulation using JAX (resist diffusion, plasma dynamics)",
    version="1.0.0",
    capabilities=[
        AgentCapability(
            skill="physics_simulation",
            description="Simulate physical processes with JAX-accelerated computation",
            input_schema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "enum": ["resist", "plasma", "thermal", "fluid"]},
                    "initial_state": {"type": "array"},
                    "parameters": {"type": "object"},
                    "time_steps": {"type": "integer"}
                },
                "required": ["domain", "initial_state"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "simulation_id": {"type": "string"},
                    "trajectory": {"type": "array"},
                    "final_state": {"type": "array"},
                    "metrics": {"type": "object"}
                }
            }
        ),
        AgentCapability(
            skill="multi_step_rollout",
            description="Predict future states with action sequences",
            input_schema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "initial_state": {"type": "array"},
                    "actions": {"type": "array"},
                    "horizon": {"type": "integer"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "predictions": {"type": "array"},
                    "rewards": {"type": "array"}
                }
            }
        )
    ],
    endpoint="/api/v1/thermodynamic/worldmodel",
    mcp_endpoint="/api/v1/thermodynamic/worldmodel",
    metadata={
        "domain": "physics_simulation",
        "jax_accelerated": True,
        "real_time": False
    }
)

MICROADAPT_EDGE_AGENT_CARD = AgentCard(
    agent_id="microadapt_edge_agent",
    name="MicroAdapt Edge Agent",
    description="Self-evolutionary adaptive modeling with O(1) time complexity (KDD '25)",
    version="1.0.0",
    capabilities=[
        AgentCapability(
            skill="adaptive_update",
            description="Update model with new observations in O(1) time",
            input_schema={
                "type": "object",
                "properties": {
                    "timestamp": {"type": "number"},
                    "value": {"type": "number"},
                    "features": {"type": "array"}
                },
                "required": ["timestamp", "value"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "updated": {"type": "boolean"},
                    "current_regime": {"type": "string"},
                    "regime_confidence": {"type": "number"},
                    "prediction_error": {"type": "number"}
                }
            }
        ),
        AgentCapability(
            skill="adaptive_forecast",
            description="Forecast future values with regime-aware predictions",
            input_schema={
                "type": "object",
                "properties": {
                    "horizon": {"type": "integer"}
                },
                "required": ["horizon"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "predictions": {"type": "array"},
                    "confidence_intervals": {"type": "array"},
                    "regime_sequence": {"type": "array"}
                }
            }
        )
    ],
    endpoint="/api/v1/thermodynamic/microadapt",
    mcp_endpoint="/api/v1/thermodynamic/microadapt",
    metadata={
        "domain": "adaptive_modeling",
        "edge_native": True,
        "raspberry_pi_validated": True,
        "time_complexity": "O(1)",
        "real_time": True
    }
)

SIMULATED_SNAPSHOT_AGENT_CARD = AgentCard(
    agent_id="simulated_snapshot_agent",
    name="Simulated Snapshot Agent",
    description="Sim/real calibration for digital twins and Energy Atlas integration",
    version="1.0.0",
    capabilities=[
        AgentCapability(
            skill="snapshot_storage",
            description="Store simulated snapshots with real data comparison",
            input_schema={
                "type": "object",
                "properties": {
                    "snapshot_type": {"type": "string"},
                    "simulator_id": {"type": "string"},
                    "real_data": {"type": "object"},
                    "simulated_data": {"type": "object"},
                    "metadata": {"type": "object"}
                },
                "required": ["snapshot_type", "simulator_id", "real_data", "simulated_data"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "snapshot_id": {"type": "string"},
                    "stored": {"type": "boolean"}
                }
            }
        ),
        AgentCapability(
            skill="simulator_calibration",
            description="Calibrate simulators using sim/real error metrics",
            input_schema={
                "type": "object",
                "properties": {
                    "snapshot_id": {"type": "string"},
                    "calibration_method": {"type": "string"}
                },
                "required": ["snapshot_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "correction_factors": {"type": "object"},
                    "error_metrics": {"type": "object"},
                    "calibrated": {"type": "boolean"}
                }
            }
        )
    ],
    endpoint="/api/v1/thermodynamic/snapshot",
    mcp_endpoint="/api/v1/thermodynamic/snapshot",
    metadata={
        "domain": "digital_twin",
        "energy_atlas_integrated": True,
        "blockchain_anchored": True
    }
)

# ============================================================================
# AGENT REGISTRY
# ============================================================================

class AgentRegistry:
    """
    Central registry for all thermodynamic agents
    
    Enables agent discovery and orchestration
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentCard] = {
            "thermal_sampler": THERMAL_SAMPLER_AGENT_CARD,
            "world_model": WORLD_MODEL_AGENT_CARD,
            "microadapt_edge": MICROADAPT_EDGE_AGENT_CARD,
            "simulated_snapshot": SIMULATED_SNAPSHOT_AGENT_CARD
        }
    
    def get_agent(self, agent_id: str) -> Optional[AgentCard]:
        """Get agent card by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self, status: Optional[AgentStatus] = None) -> List[AgentCard]:
        """List all agents, optionally filtered by status"""
        agents = list(self.agents.values())
        if status:
            agents = [a for a in agents if a.status == status]
        return agents
    
    def find_agents_by_skill(self, skill: str) -> List[AgentCard]:
        """Find agents that have a specific skill"""
        result = []
        for agent in self.agents.values():
            for capability in agent.capabilities:
                if capability.skill == skill:
                    result.append(agent)
                    break
        return result
    
    def get_all_capabilities(self) -> Dict[str, List[AgentCapability]]:
        """Get all capabilities organized by agent"""
        return {
            agent_id: agent.capabilities
            for agent_id, agent in self.agents.items()
        }


# ============================================================================
# HOST AGENT FOR WORKFLOW ORCHESTRATION
# ============================================================================

class TaskRequest(BaseModel):
    """A2A task request"""
    task_id: str
    task_type: str
    input_data: Dict[str, Any]
    mcp_context: Optional[Dict[str, Any]] = None
    priority: int = Field(default=5, ge=1, le=10)


class TaskResult(BaseModel):
    """A2A task result"""
    task_id: str
    success: bool
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float
    agent_id: str


class HostAgent:
    """
    Host Agent for workflow orchestration
    
    Decomposes complex tasks, delegates to specialized agents,
    and aggregates results with MCP-enhanced context.
    """
    
    def __init__(self):
        self.registry = AgentRegistry()
    
    async def orchestrate_workflow(
        self,
        workflow_description: str,
        input_data: Dict[str, Any],
        mcp_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate complex workflow across multiple agents
        
        Example workflows:
        - "Optimize fab layout using thermal sampling and physics simulation"
        - "Forecast sensor data and calibrate digital twin"
        - "Run adaptive edge inference with real-time optimization"
        """
        # In production, would use LLM to decompose workflow
        # For now, return agent discovery info
        
        agents = self.registry.list_agents(status=AgentStatus.ACTIVE)
        
        return {
            "workflow": workflow_description,
            "available_agents": len(agents),
            "agent_cards": [agent.dict() for agent in agents],
            "mcp_enabled": all(agent.mcp_endpoint for agent in agents),
            "orchestration_ready": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def discover_agents(self, skill: Optional[str] = None) -> List[AgentCard]:
        """Discover available agents, optionally by skill"""
        if skill:
            return self.registry.find_agents_by_skill(skill)
        return self.registry.list_agents()


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_host_agent() -> HostAgent:
    """Create Host Agent for workflow orchestration"""
    return HostAgent()


def get_agent_registry() -> AgentRegistry:
    """Get global agent registry"""
    return AgentRegistry()
