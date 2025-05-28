"""
Consensus Resolver Agent for Industriverse Core AI Layer

This module implements the consensus resolver agent for cross-agent decision making
and conflict resolution in the Core AI Layer mesh.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsensusResolverAgent:
    """
    Implements the consensus resolver agent for Core AI Layer.
    Provides cross-agent decision making and conflict resolution capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the consensus resolver agent.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or "config/consensus_resolver.yaml"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize state
        self.active_decisions = {}
        self.decision_history = []
        self.agent_votes = {}
        self.quorum_violations = []
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration.
        
        Returns:
            The configuration as a dictionary
        """
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return {}
                
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def initiate_decision(self, decision_type: str, decision_data: Dict[str, Any], 
                               participating_agents: List[str]) -> str:
        """
        Initiate a new consensus decision.
        
        Args:
            decision_type: Type of decision
            decision_data: Decision data
            participating_agents: List of agents participating in the decision
            
        Returns:
            Decision ID
        """
        decision_id = f"decision-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        timestamp = datetime.utcnow().isoformat()
        
        # Create decision entry
        decision = {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "timestamp": timestamp,
            "data": decision_data,
            "participating_agents": participating_agents,
            "required_quorum": self._calculate_quorum(participating_agents),
            "status": "initiated",
            "votes": {},
            "result": None,
            "completion_timestamp": None
        }
        
        # Add to active decisions
        self.active_decisions[decision_id] = decision
        
        # Initialize agent votes
        self.agent_votes[decision_id] = {}
        
        logger.info(f"Initiated decision {decision_id}: {decision_type} with {len(participating_agents)} agents")
        
        # Notify participating agents
        await self._notify_agents(decision_id, participating_agents)
        
        return decision_id
    
    def _calculate_quorum(self, participating_agents: List[str]) -> int:
        """
        Calculate the required quorum for a decision.
        
        Args:
            participating_agents: List of participating agents
            
        Returns:
            Required quorum count
        """
        # Default: simple majority
        return len(participating_agents) // 2 + 1
    
    async def _notify_agents(self, decision_id: str, agents: List[str]) -> None:
        """
        Notify agents about a decision.
        
        Args:
            decision_id: ID of the decision
            agents: List of agents to notify
        """
        # In a real implementation, this would use the MCP adapter
        # to send notifications to the agents
        
        logger.info(f"Notified {len(agents)} agents about decision {decision_id}")
    
    async def submit_vote(self, decision_id: str, agent_id: str, vote: Dict[str, Any]) -> bool:
        """
        Submit a vote for a decision.
        
        Args:
            decision_id: ID of the decision
            agent_id: ID of the voting agent
            vote: Vote data
            
        Returns:
            True if vote was accepted, False otherwise
        """
        if decision_id not in self.active_decisions:
            logger.warning(f"Decision not found: {decision_id}")
            return False
            
        decision = self.active_decisions[decision_id]
        
        if agent_id not in decision["participating_agents"]:
            logger.warning(f"Agent {agent_id} not participating in decision {decision_id}")
            return False
            
        if decision["status"] != "initiated":
            logger.warning(f"Decision {decision_id} is not in initiated state: {decision['status']}")
            return False
        
        # Record vote
        decision["votes"][agent_id] = {
            "timestamp": datetime.utcnow().isoformat(),
            "vote": vote
        }
        
        self.agent_votes[decision_id][agent_id] = vote
        
        logger.info(f"Recorded vote from {agent_id} for decision {decision_id}")
        
        # Check if quorum is reached
        if len(decision["votes"]) >= decision["required_quorum"]:
            await self._resolve_decision(decision_id)
        
        return True
    
    async def _resolve_decision(self, decision_id: str) -> None:
        """
        Resolve a decision based on votes.
        
        Args:
            decision_id: ID of the decision
        """
        if decision_id not in self.active_decisions:
            logger.warning(f"Decision not found: {decision_id}")
            return
            
        decision = self.active_decisions[decision_id]
        votes = self.agent_votes[decision_id]
        
        logger.info(f"Resolving decision {decision_id} with {len(votes)} votes")
        
        # Resolve based on decision type
        if decision["decision_type"] == "binary":
            result = await self._resolve_binary_decision(votes)
        elif decision["decision_type"] == "multi_option":
            result = await self._resolve_multi_option_decision(votes)
        elif decision["decision_type"] == "numeric":
            result = await self._resolve_numeric_decision(votes)
        elif decision["decision_type"] == "conflict_resolution":
            result = await self._resolve_conflict_decision(votes, decision["data"])
        else:
            logger.warning(f"Unknown decision type: {decision['decision_type']}")
            result = {"error": f"Unknown decision type: {decision['decision_type']}"}
        
        # Update decision
        decision["status"] = "resolved"
        decision["result"] = result
        decision["completion_timestamp"] = datetime.utcnow().isoformat()
        
        # Move to history
        self.decision_history.append(decision)
        del self.active_decisions[decision_id]
        
        logger.info(f"Decision {decision_id} resolved: {result}")
        
        # Notify participating agents
        await self._notify_resolution(decision_id, decision["participating_agents"], result)
    
    async def _resolve_binary_decision(self, votes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a binary decision.
        
        Args:
            votes: Dictionary of votes
            
        Returns:
            Decision result
        """
        # Count votes
        true_votes = sum(1 for v in votes.values() if v.get("value") is True)
        false_votes = sum(1 for v in votes.values() if v.get("value") is False)
        
        # Determine result
        result_value = true_votes > false_votes
        confidence = abs(true_votes - false_votes) / len(votes) if votes else 0
        
        return {
            "value": result_value,
            "true_votes": true_votes,
            "false_votes": false_votes,
            "confidence": confidence
        }
    
    async def _resolve_multi_option_decision(self, votes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a multi-option decision.
        
        Args:
            votes: Dictionary of votes
            
        Returns:
            Decision result
        """
        # Count votes for each option
        option_counts = {}
        
        for vote in votes.values():
            option = vote.get("option")
            if option:
                option_counts[option] = option_counts.get(option, 0) + 1
        
        # Find winning option
        winning_option = None
        max_votes = 0
        
        for option, count in option_counts.items():
            if count > max_votes:
                winning_option = option
                max_votes = count
        
        # Calculate confidence
        confidence = max_votes / len(votes) if votes else 0
        
        return {
            "winning_option": winning_option,
            "option_counts": option_counts,
            "confidence": confidence
        }
    
    async def _resolve_numeric_decision(self, votes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a numeric decision.
        
        Args:
            votes: Dictionary of votes
            
        Returns:
            Decision result
        """
        # Collect numeric values
        values = [v.get("value") for v in votes.values() if isinstance(v.get("value"), (int, float))]
        
        if not values:
            return {"error": "No valid numeric votes"}
        
        # Calculate statistics
        mean = sum(values) / len(values)
        median = sorted(values)[len(values) // 2]
        
        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # Determine result based on aggregation method
        # Default to median as it's more robust to outliers
        result_value = median
        
        return {
            "value": result_value,
            "mean": mean,
            "median": median,
            "std_dev": std_dev,
            "confidence": 1.0 - (std_dev / mean if mean != 0 else 1.0)
        }
    
    async def _resolve_conflict_decision(self, votes: Dict[str, Any], conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a conflict decision.
        
        Args:
            votes: Dictionary of votes
            conflict_data: Conflict data
            
        Returns:
            Decision result
        """
        # Extract conflict options
        options = conflict_data.get("options", [])
        
        if not options:
            return {"error": "No conflict options provided"}
        
        # Count votes for each option
        option_counts = {}
        
        for vote in votes.values():
            option = vote.get("option")
            if option in options:
                option_counts[option] = option_counts.get(option, 0) + 1
        
        # Find winning option
        winning_option = None
        max_votes = 0
        
        for option, count in option_counts.items():
            if count > max_votes:
                winning_option = option
                max_votes = count
        
        # Calculate confidence
        confidence = max_votes / len(votes) if votes else 0
        
        return {
            "winning_option": winning_option,
            "option_counts": option_counts,
            "confidence": confidence,
            "resolution_type": "majority_vote"
        }
    
    async def _notify_resolution(self, decision_id: str, agents: List[str], result: Dict[str, Any]) -> None:
        """
        Notify agents about a decision resolution.
        
        Args:
            decision_id: ID of the decision
            agents: List of agents to notify
            result: Decision result
        """
        # In a real implementation, this would use the MCP adapter
        # to send notifications to the agents
        
        logger.info(f"Notified {len(agents)} agents about resolution of decision {decision_id}")
    
    async def resolve_with_fallback(self, decision_id: str) -> Dict[str, Any]:
        """
        Resolve a decision with fallback when quorum is violated.
        
        Args:
            decision_id: ID of the decision
            
        Returns:
            Decision result
        """
        if decision_id not in self.active_decisions:
            logger.warning(f"Decision not found: {decision_id}")
            return {"error": "Decision not found"}
            
        decision = self.active_decisions[decision_id]
        votes = self.agent_votes.get(decision_id, {})
        
        logger.warning(f"Quorum violation for decision {decision_id}: {len(votes)} votes, {decision['required_quorum']} required")
        
        # Record quorum violation
        violation = {
            "decision_id": decision_id,
            "timestamp": datetime.utcnow().isoformat(),
            "required_quorum": decision["required_quorum"],
            "actual_votes": len(votes),
            "participating_agents": decision["participating_agents"],
            "voting_agents": list(votes.keys())
        }
        
        self.quorum_violations.append(violation)
        
        # Apply fallback strategy
        fallback_strategy = self.config.get("fallback_strategy", "use_available_votes")
        
        if fallback_strategy == "use_available_votes":
            # Resolve with available votes
            logger.info(f"Applying fallback strategy: use_available_votes for decision {decision_id}")
            await self._resolve_decision(decision_id)
            
            # Get the result from history
            for d in self.decision_history:
                if d["decision_id"] == decision_id:
                    result = d["result"]
                    result["fallback_applied"] = True
                    return result
                    
            return {"error": "Failed to find decision result after fallback"}
            
        elif fallback_strategy == "default_value":
            # Use default value
            default_value = self.config.get("default_fallback_value")
            
            logger.info(f"Applying fallback strategy: default_value for decision {decision_id}")
            
            result = {
                "value": default_value,
                "fallback_applied": True,
                "fallback_strategy": "default_value"
            }
            
            # Update decision
            decision["status"] = "resolved_fallback"
            decision["result"] = result
            decision["completion_timestamp"] = datetime.utcnow().isoformat()
            
            # Move to history
            self.decision_history.append(decision)
            del self.active_decisions[decision_id]
            
            return result
            
        else:
            logger.error(f"Unknown fallback strategy: {fallback_strategy}")
            return {"error": f"Unknown fallback strategy: {fallback_strategy}"}
    
    def get_decision(self, decision_id: str) -> Dict[str, Any]:
        """
        Get a decision by ID.
        
        Args:
            decision_id: ID of the decision
            
        Returns:
            Decision data
        """
        # Check active decisions
        if decision_id in self.active_decisions:
            return self.active_decisions[decision_id]
            
        # Check history
        for decision in self.decision_history:
            if decision["decision_id"] == decision_id:
                return decision
                
        logger.warning(f"Decision not found: {decision_id}")
        return {}
    
    def get_active_decisions(self) -> List[Dict[str, Any]]:
        """
        Get all active decisions.
        
        Returns:
            List of active decisions
        """
        return list(self.active_decisions.values())
    
    def get_decision_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get decision history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of historical decisions
        """
        return self.decision_history[-limit:]
    
    def get_quorum_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get quorum violations.
        
        Args:
            limit: Maximum number of violations to return
            
        Returns:
            List of quorum violations
        """
        return self.quorum_violations[-limit:]


# Example usage
if __name__ == "__main__":
    async def main():
        # Create a consensus resolver agent
        resolver = ConsensusResolverAgent()
        
        # Initiate a binary decision
        decision_id = await resolver.initiate_decision(
            "binary",
            {"question": "Should we deploy the model?"},
            ["agent1", "agent2", "agent3", "agent4", "agent5"]
        )
        
        # Submit votes
        await resolver.submit_vote(decision_id, "agent1", {"value": True})
        await resolver.submit_vote(decision_id, "agent2", {"value": True})
        await resolver.submit_vote(decision_id, "agent3", {"value": False})
        
        # Decision should not be resolved yet (quorum is 3)
        
        # Submit more votes to reach quorum
        await resolver.submit_vote(decision_id, "agent4", {"value": True})
        
        # Decision should be resolved now
        
        # Get the decision
        decision = resolver.get_decision(decision_id)
        print(f"Decision {decision_id} result: {decision.get('result')}")
        
        # Initiate a multi-option decision
        decision_id2 = await resolver.initiate_decision(
            "multi_option",
            {"question": "Which model should we use?", "options": ["model1", "model2", "model3"]},
            ["agent1", "agent2", "agent3"]
        )
        
        # Submit votes
        await resolver.submit_vote(decision_id2, "agent1", {"option": "model1"})
        await resolver.submit_vote(decision_id2, "agent2", {"option": "model2"})
        
        # Test fallback resolution for quorum violation
        result = await resolver.resolve_with_fallback(decision_id2)
        print(f"Fallback result: {result}")
    
    asyncio.run(main())
