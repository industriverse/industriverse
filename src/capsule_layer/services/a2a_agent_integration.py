from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid
import logging
import asyncio

logger = logging.getLogger(__name__)

# --- Models ---
class AgentSkill(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class AgentCard(BaseModel):
    agent_id: str
    name: str
    description: str
    capabilities: List[str]
    skills: List[AgentSkill]
    status: str = "active"
    endpoint: str

class WorkflowRequest(BaseModel):
    workflow_id: str
    steps: List[Dict[str, Any]]
    context: Dict[str, Any]

# --- Agent Registry ---
class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}

    def register_agent(self, card: AgentCard):
        self.agents[card.agent_id] = card
        logger.info(f"Registered agent: {card.name} ({card.agent_id})")

    def get_agent(self, agent_id: str) -> Optional[AgentCard]:
        return self.agents.get(agent_id)

    def find_agents_by_skill(self, skill_name: str) -> List[AgentCard]:
        return [
            agent for agent in self.agents.values()
            if any(s.name == skill_name for s in agent.skills)
        ]

    def list_agents(self) -> List[AgentCard]:
        return list(self.agents.values())

# --- Host Agent ---
class HostAgent:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    async def orchestrate_workflow(self, request: WorkflowRequest):
        logger.info(f"Orchestrating workflow: {request.workflow_id}")
        results = {}
        
        for step in request.steps:
            agent_id = step.get("agent_id")
            skill_name = step.get("skill")
            params = step.get("params", {})
            
            # Find agent
            agent = None
            if agent_id:
                agent = self.registry.get_agent(agent_id)
            elif skill_name:
                candidates = self.registry.find_agents_by_skill(skill_name)
                if candidates:
                    agent = candidates[0] # Simple selection strategy
            
            if not agent:
                logger.error(f"No agent found for step: {step}")
                results[step.get("id", "unknown")] = {"status": "failed", "error": "Agent not found"}
                continue

            # Execute step (Simulated A2A call)
            logger.info(f"Delegating task to {agent.name}: {skill_name}")
            # In a real implementation, this would make an HTTP/RPC call to agent.endpoint
            # Here we simulate success
            await asyncio.sleep(0.1) 
            results[step.get("id")] = {"status": "success", "agent": agent.name, "output": "simulated_output"}

        return {"status": "completed", "results": results}

# --- Singleton Instances ---
registry = AgentRegistry()
host_agent = HostAgent(registry)

# --- Bootstrap Default Agents ---
def bootstrap_agents():
    # Thermodynamic Agent
    registry.register_agent(AgentCard(
        agent_id="agent:thermo:001",
        name="Thermodynamic Core",
        description="Handles energy optimization and entropy calculations.",
        capabilities=["energy_optimization", "entropy_analysis"],
        skills=[
            AgentSkill(name="optimize_energy", description="Optimize energy usage", parameters={"target": "float"}),
            AgentSkill(name="calculate_entropy", description="Calculate system entropy", parameters={})
        ],
        endpoint="http://localhost:8000/thermo"
    ))

    # DAC Factory Agent
    registry.register_agent(AgentCard(
        agent_id="agent:dac:001",
        name="DAC Factory",
        description="Builds and deploys capsules.",
        capabilities=["build", "deploy"],
        skills=[
            AgentSkill(name="build_capsule", description="Build a capsule", parameters={"manifest": "dict"}),
            AgentSkill(name="deploy_capsule", description="Deploy a capsule", parameters={"capsule_id": "str"})
        ],
        endpoint="http://localhost:8000/dac"
    ))

    # Provenance Agent
    registry.register_agent(AgentCard(
        agent_id="agent:provenance:001",
        name="Provenance Tracker",
        description="Tracks UTID lineage and proofs.",
        capabilities=["track", "verify"],
        skills=[
            AgentSkill(name="mint_utid", description="Mint a new UTID", parameters={"parent": "str"}),
            AgentSkill(name="verify_proof", description="Verify a zk-SNARK proof", parameters={"proof": "str"})
        ],
        endpoint="http://localhost:8000/provenance"
    ))

bootstrap_agents()
