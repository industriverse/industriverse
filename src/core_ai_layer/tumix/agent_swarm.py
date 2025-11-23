import asyncio
import random
from typing import List
from .schema import AgentRole, AgentVote

class AgentSwarm:
    """
    Manages a swarm of specialized agents.
    In a real system, these would be separate LLM calls with distinct system prompts.
    Here, we mock their behavior based on their roles.
    """
    
    def __init__(self):
        self.agents = [
            {"id": "agent-critic", "role": AgentRole.CRITIC},
            {"id": "agent-optimist", "role": AgentRole.OPTIMIST},
            {"id": "agent-realist", "role": AgentRole.REALIST},
            {"id": "agent-security", "role": AgentRole.SECURITY},
        ]

    async def collect_votes(self, proposal: str) -> List[AgentVote]:
        """
        Ask all agents to vote on a proposal.
        """
        votes = []
        
        # Simulate parallel processing
        tasks = [self._get_agent_vote(agent, proposal) for agent in self.agents]
        votes = await asyncio.gather(*tasks)
        
        return votes

    async def _get_agent_vote(self, agent: dict, proposal: str) -> AgentVote:
        """
        Simulate a single agent's voting process.
        """
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        role = agent["role"]
        vote_decision = "approve"
        confidence = 0.9
        reasoning = "Looks good."
        
        # Simulate role-based logic
        if role == AgentRole.CRITIC:
            if "unsafe" in proposal.lower() or "risk" in proposal.lower():
                vote_decision = "reject"
                confidence = 0.95
                reasoning = "Too risky."
            else:
                confidence = 0.7
                reasoning = "Acceptable, but verify."
                
        elif role == AgentRole.SECURITY:
            if "hack" in proposal.lower() or "bypass" in proposal.lower():
                vote_decision = "reject"
                confidence = 1.0
                reasoning = "Security violation detected."
                
        elif role == AgentRole.OPTIMIST:
            confidence = 0.95
            reasoning = "Great potential!"

        return AgentVote(
            agent_id=agent["id"],
            role=role,
            vote=vote_decision,
            confidence=confidence,
            reasoning=reasoning
        )
