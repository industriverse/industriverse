"""
Workflow Negotiator Agent Module for the Workflow Automation Layer.

This agent handles negotiation between different agents and systems to resolve
conflicts, optimize resource allocation, and establish task contracts.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowNegotiatorAgent:
    """Agent for negotiating task contracts and resource allocation between agents."""

    def __init__(self, workflow_runtime):
        """Initialize the workflow negotiator agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "workflow-negotiator-agent"
        self.agent_capabilities = ["contract_negotiation", "resource_allocation", "conflict_resolution"]
        self.supported_protocols = ["MCP", "A2A"]
        self.active_negotiations = {}  # Store for ongoing negotiations
        self.negotiation_history = {}  # History of completed negotiations
        self.negotiation_strategies = [
            "cooperative",
            "competitive",
            "compromise",
            "integrative",
            "distributive"
        ]
        
        logger.info("Workflow Negotiator Agent initialized")

    async def start_negotiation(self, negotiation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new negotiation process.

        Args:
            negotiation_request: Request data including workflow_id, parties, subject, etc.

        Returns:
            Dict containing negotiation start status.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "parties", "subject"]
            for field in required_fields:
                if field not in negotiation_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = negotiation_request["workflow_id"]
            parties = negotiation_request["parties"]
            subject = negotiation_request["subject"]
            
            # Validate parties (at least 2 required)
            if not isinstance(parties, list) or len(parties) < 2:
                return {
                    "success": False,
                    "error": "At least 2 parties required for negotiation"
                }
            
            # Generate negotiation ID
            negotiation_id = str(uuid.uuid4())
            
            # Get strategy from request or use default
            strategy = negotiation_request.get("strategy", "cooperative")
            if strategy not in self.negotiation_strategies:
                return {
                    "success": False,
                    "error": f"Invalid strategy: {strategy}. Must be one of {self.negotiation_strategies}"
                }
            
            # Store negotiation details
            self.active_negotiations[negotiation_id] = {
                "workflow_id": workflow_id,
                "parties": parties,
                "subject": subject,
                "strategy": strategy,
                "parameters": negotiation_request.get("parameters", {}),
                "start_time": datetime.utcnow().isoformat(),
                "status": "active",
                "rounds": [],
                "current_round": 0,
                "proposals": {},
                "accepted_proposal": None
            }
            
            # Start negotiation process
            asyncio.create_task(self._run_negotiation(negotiation_id))
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "start_negotiation",
                "reason": f"Started {strategy} negotiation for {subject} between {len(parties)} parties in workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Started negotiation {negotiation_id} for workflow {workflow_id}")
            
            return {
                "success": True,
                "negotiation_id": negotiation_id,
                "workflow_id": workflow_id,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error starting negotiation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _run_negotiation(self, negotiation_id: str):
        """Run the negotiation process in the background.

        Args:
            negotiation_id: ID of the negotiation to run.
        """
        if negotiation_id not in self.active_negotiations:
            logger.error(f"Negotiation {negotiation_id} not found")
            return
        
        negotiation = self.active_negotiations[negotiation_id]
        workflow_id = negotiation["workflow_id"]
        parties = negotiation["parties"]
        subject = negotiation["subject"]
        strategy = negotiation["strategy"]
        parameters = negotiation["parameters"]
        
        # Get max rounds from parameters or use default
        max_rounds = parameters.get("max_rounds", 5)
        round_timeout = parameters.get("round_timeout", 30)  # seconds
        
        logger.info(f"Running negotiation {negotiation_id} with strategy {strategy}")
        
        # Initialize negotiation
        await self._initialize_negotiation(negotiation_id)
        
        # Run negotiation rounds
        for round_num in range(1, max_rounds + 1):
            # Check if negotiation is still active
            if negotiation_id not in self.active_negotiations or self.active_negotiations[negotiation_id]["status"] != "active":
                break
            
            # Update current round
            negotiation["current_round"] = round_num
            
            # Create new round
            round_data = {
                "round_number": round_num,
                "start_time": datetime.utcnow().isoformat(),
                "proposals": {},
                "status": "active"
            }
            
            negotiation["rounds"].append(round_data)
            
            # Request proposals from all parties
            await self._request_proposals(negotiation_id, round_num)
            
            # Wait for proposals or timeout
            try:
                await asyncio.wait_for(
                    self._wait_for_all_proposals(negotiation_id, round_num),
                    timeout=round_timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Round {round_num} timed out for negotiation {negotiation_id}")
                round_data["status"] = "timeout"
            
            # Evaluate proposals
            evaluation_result = await self._evaluate_proposals(negotiation_id, round_num)
            
            # Check if agreement reached
            if evaluation_result["agreement_reached"]:
                # Store accepted proposal
                negotiation["accepted_proposal"] = evaluation_result["accepted_proposal"]
                
                # Mark negotiation as completed
                negotiation["status"] = "completed"
                negotiation["end_time"] = datetime.utcnow().isoformat()
                negotiation["result"] = "agreement"
                
                # Mark round as completed
                round_data["status"] = "completed"
                round_data["end_time"] = datetime.utcnow().isoformat()
                
                # Generate agent reason log
                reason_log = {
                    "agent_id": self.agent_id,
                    "action": "negotiation_completed",
                    "reason": f"Agreement reached in round {round_num} for negotiation {negotiation_id}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Add to workflow telemetry
                self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
                
                logger.info(f"Agreement reached in round {round_num} for negotiation {negotiation_id}")
                
                # Notify parties of agreement
                await self._notify_parties_of_agreement(negotiation_id)
                
                break
            else:
                # Mark round as completed
                round_data["status"] = "completed"
                round_data["end_time"] = datetime.utcnow().isoformat()
                
                # Provide feedback to parties
                await self._provide_feedback_to_parties(negotiation_id, round_num, evaluation_result["feedback"])
        
        # Check if max rounds reached without agreement
        if negotiation_id in self.active_negotiations and self.active_negotiations[negotiation_id]["status"] == "active":
            # Mark negotiation as failed
            negotiation["status"] = "failed"
            negotiation["end_time"] = datetime.utcnow().isoformat()
            negotiation["result"] = "no_agreement"
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "negotiation_failed",
                "reason": f"No agreement reached after {max_rounds} rounds for negotiation {negotiation_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"No agreement reached after {max_rounds} rounds for negotiation {negotiation_id}")
            
            # Notify parties of failure
            await self._notify_parties_of_failure(negotiation_id)
        
        # Move to history
        if negotiation_id in self.active_negotiations:
            self.negotiation_history[negotiation_id] = self.active_negotiations[negotiation_id]
            del self.active_negotiations[negotiation_id]

    async def _initialize_negotiation(self, negotiation_id: str):
        """Initialize the negotiation process.

        Args:
            negotiation_id: ID of the negotiation to initialize.
        """
        negotiation = self.active_negotiations[negotiation_id]
        workflow_id = negotiation["workflow_id"]
        parties = negotiation["parties"]
        subject = negotiation["subject"]
        
        # Notify all parties of negotiation start
        for party in parties:
            try:
                # In a real implementation, this would send a message to the party
                logger.info(f"Notifying party {party} of negotiation {negotiation_id} start")
                
                # Send notification via workflow runtime
                await self.workflow_runtime.send_agent_message(
                    source_agent_id=self.agent_id,
                    target_agent_id=party,
                    message_type="negotiation_start",
                    payload={
                        "negotiation_id": negotiation_id,
                        "workflow_id": workflow_id,
                        "subject": subject,
                        "parties": parties
                    }
                )
            except Exception as e:
                logger.error(f"Error notifying party {party} of negotiation start: {str(e)}")

    async def _request_proposals(self, negotiation_id: str, round_num: int):
        """Request proposals from all parties for a negotiation round.

        Args:
            negotiation_id: ID of the negotiation.
            round_num: Current round number.
        """
        negotiation = self.active_negotiations[negotiation_id]
        workflow_id = negotiation["workflow_id"]
        parties = negotiation["parties"]
        subject = negotiation["subject"]
        
        # Get current round data
        round_data = negotiation["rounds"][round_num - 1]
        
        # Request proposals from all parties
        for party in parties:
            try:
                # In a real implementation, this would send a message to the party
                logger.info(f"Requesting proposal from party {party} for round {round_num} of negotiation {negotiation_id}")
                
                # Send request via workflow runtime
                await self.workflow_runtime.send_agent_message(
                    source_agent_id=self.agent_id,
                    target_agent_id=party,
                    message_type="proposal_request",
                    payload={
                        "negotiation_id": negotiation_id,
                        "workflow_id": workflow_id,
                        "subject": subject,
                        "round": round_num,
                        "previous_proposals": negotiation["proposals"] if round_num > 1 else {}
                    }
                )
            except Exception as e:
                logger.error(f"Error requesting proposal from party {party}: {str(e)}")

    async def _wait_for_all_proposals(self, negotiation_id: str, round_num: int):
        """Wait for proposals from all parties for a negotiation round.

        Args:
            negotiation_id: ID of the negotiation.
            round_num: Current round number.
        """
        negotiation = self.active_negotiations[negotiation_id]
        parties = negotiation["parties"]
        
        # Get current round data
        round_data = negotiation["rounds"][round_num - 1]
        
        # Wait until all parties have submitted proposals
        while len(round_data["proposals"]) < len(parties):
            # Check if negotiation is still active
            if negotiation_id not in self.active_negotiations or self.active_negotiations[negotiation_id]["status"] != "active":
                return
            
            # Wait a bit
            await asyncio.sleep(0.5)

    async def submit_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a proposal for a negotiation round.

        Args:
            proposal_data: Proposal data including negotiation_id, party_id, round, proposal.

        Returns:
            Dict containing submission status.
        """
        try:
            # Validate required fields
            required_fields = ["negotiation_id", "party_id", "round", "proposal"]
            for field in required_fields:
                if field not in proposal_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            negotiation_id = proposal_data["negotiation_id"]
            party_id = proposal_data["party_id"]
            round_num = proposal_data["round"]
            proposal = proposal_data["proposal"]
            
            # Check if negotiation exists and is active
            if negotiation_id not in self.active_negotiations:
                return {
                    "success": False,
                    "error": f"Negotiation {negotiation_id} not found or not active"
                }
            
            negotiation = self.active_negotiations[negotiation_id]
            
            # Check if party is part of negotiation
            if party_id not in negotiation["parties"]:
                return {
                    "success": False,
                    "error": f"Party {party_id} is not part of negotiation {negotiation_id}"
                }
            
            # Check if round is current
            if round_num != negotiation["current_round"]:
                return {
                    "success": False,
                    "error": f"Round {round_num} is not the current round ({negotiation['current_round']})"
                }
            
            # Get current round data
            round_data = negotiation["rounds"][round_num - 1]
            
            # Check if party has already submitted a proposal
            if party_id in round_data["proposals"]:
                return {
                    "success": False,
                    "error": f"Party {party_id} has already submitted a proposal for round {round_num}"
                }
            
            # Store proposal
            round_data["proposals"][party_id] = {
                "proposal": proposal,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in negotiation proposals
            if round_num not in negotiation["proposals"]:
                negotiation["proposals"][round_num] = {}
            
            negotiation["proposals"][round_num][party_id] = proposal
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "proposal_received",
                "reason": f"Received proposal from party {party_id} for round {round_num} of negotiation {negotiation_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(negotiation["workflow_id"], reason_log)
            
            logger.info(f"Received proposal from party {party_id} for round {round_num} of negotiation {negotiation_id}")
            
            return {
                "success": True,
                "negotiation_id": negotiation_id,
                "party_id": party_id,
                "round": round_num,
                "status": "accepted"
            }
            
        except Exception as e:
            logger.error(f"Error submitting proposal: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _evaluate_proposals(self, negotiation_id: str, round_num: int) -> Dict[str, Any]:
        """Evaluate proposals for a negotiation round.

        Args:
            negotiation_id: ID of the negotiation.
            round_num: Current round number.

        Returns:
            Dict containing evaluation result.
        """
        negotiation = self.active_negotiations[negotiation_id]
        strategy = negotiation["strategy"]
        
        # Get current round data
        round_data = negotiation["rounds"][round_num - 1]
        proposals = round_data["proposals"]
        
        # Evaluate based on strategy
        if strategy == "cooperative":
            return await self._evaluate_cooperative(negotiation_id, round_num, proposals)
        elif strategy == "competitive":
            return await self._evaluate_competitive(negotiation_id, round_num, proposals)
        elif strategy == "compromise":
            return await self._evaluate_compromise(negotiation_id, round_num, proposals)
        elif strategy == "integrative":
            return await self._evaluate_integrative(negotiation_id, round_num, proposals)
        elif strategy == "distributive":
            return await self._evaluate_distributive(negotiation_id, round_num, proposals)
        else:
            # Default to cooperative
            return await self._evaluate_cooperative(negotiation_id, round_num, proposals)

    async def _evaluate_cooperative(self, negotiation_id: str, round_num: int, proposals: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposals using cooperative strategy.

        Args:
            negotiation_id: ID of the negotiation.
            round_num: Current round number.
            proposals: Proposals from all parties.

        Returns:
            Dict containing evaluation result.
        """
        negotiation = self.active_negotiations[negotiation_id]
        subject = negotiation["subject"]
        
        # In a cooperative strategy, we look for common ground and try to merge proposals
        
        # Extract proposal values
        proposal_values = {party_id: data["proposal"] for party_id, data in proposals.items()}
        
        # Check if all proposals are compatible
        # This is a simplified implementation; in a real system, this would be more sophisticated
        compatible = True
        merged_proposal = {}
        
        # Try to merge proposals
        for party_id, proposal in proposal_values.items():
            for key, value in proposal.items():
                if key in merged_proposal and merged_proposal[key] != value:
                    compatible = False
                    break
                merged_proposal[key] = value
            
            if not compatible:
                break
        
        # If proposals are compatible, accept the merged proposal
        if compatible:
            return {
                "agreement_reached": True,
                "accepted_proposal": merged_proposal,
                "feedback": {
                    "message": "All proposals are compatible and have been merged.",
                    "details": {
                        "merged_proposal": merged_proposal
                    }
                }
            }
        else:
            # Identify common elements
            common_elements = {}
            all_keys = set()
            
            for proposal in proposal_values.values():
                all_keys.update(proposal.keys())
            
            for key in all_keys:
                values = [proposal.get(key) for proposal in proposal_values.values() if key in proposal]
                if len(values) == len(proposal_values) and all(v == values[0] for v in values):
                    common_elements[key] = values[0]
            
            return {
                "agreement_reached": False,
                "feedback": {
                    "message": "Proposals are not fully compatible. Please focus on resolving differences.",
                    "details": {
                        "common_elements": common_elements,
                        "differences": {
                            key: [proposal.get(key) for proposal in proposal_values.values() if key in proposal]
                            for key in all_keys if key not in common_elements
                        }
                    }
                }
            }

    async def _evaluate_competitive(self, negotiation_id: str, round_num: int, proposals: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposals using competitive strategy.

        Args:
            negotiation_id: ID of the negotiation.
            round_num: Current round number.
            proposals: Proposals from all parties.

        Returns:
            Dict containing evaluation result.
        """
        negotiation = self.active_negotiations[negotiation_id]
        subject = negotiation["subject"]
        parameters = negotiation["parameters"]
        
        # In a competitive strategy, we select the best proposal based on objective criteria
        
        # Extract proposal values
        proposal_values = {party_id: data["proposal"] for party_id, data in proposals.items()}
        
        # Get scoring criteria from parameters or use default
        scoring_criteria = parameters.get("scoring_criteria", {})
        
        if not scoring_criteria:
            # No scoring criteria provided, can't evaluate competitively
            return {
                "agreement_reached": False,
                "feedback": {
                    "message": "No scoring criteria provided for competitive evaluation.",
                    "details": {
                        "proposals": proposal_values
                    }
                }
            }
        
        # Score each proposal
        scores = {}
        for party_id, proposal in proposal_values.items():
            score = 0
            for key, value in proposal.items():
                if key in scoring_criteria:
                    criterion = scoring_criteria[key]
                    if criterion["type"] == "numeric":
                        # Higher is better
                        if criterion.get("higher_is_better", True):
                            score += value * criterion.get("weight", 1)
                        # Lower is better
                        else:
                            score += (1 / max(value, 0.001)) * criterion.get("weight", 1)
                    elif criterion["type"] == "boolean":
                        if value == criterion.get("target_value", True):
                            score += criterion.get("weight", 1)
                    elif criterion["type"] == "categorical":
                        if value in criterion.get("preferred_values", []):
                            score += criterion.get("weight", 1)
            
            scores[party_id] = score
        
        # Find highest score
        highest_score = max(scores.values()) if scores else 0
        winners = [party_id for party_id, score in scores.items() if score == highest_score]
        
        # Check if there's a clear winner
        if len(winners) == 1:
            winner = winners[0]
            winning_proposal = proposal_values[winner]
            
            # Check if score meets minimum threshold
            min_threshold = parameters.get("min_score_threshold", 0)
            if highest_score >= min_threshold:
                return {
                    "agreement_reached": True,
                    "accepted_proposal": winning_proposal,
                    "feedback": {
                        "message": f"Proposal from {winner} selected as the winner.",
                        "details": {
                            "scores": scores,
                            "winner": winner,
                            "winning_proposal": winning_proposal
                        }
                    }
                }
            else:
                return {
                    "agreement_reached": False,
                    "feedback": {
                        "message": "No proposal met the minimum score threshold.",
                        "details": {
                            "scores": scores,
                            "min_threshold": min_threshold
                        }
                    }
                }
        else:
            # Tie or no proposals
            return {
                "agreement_reached": False,
                "feedback": {
                    "message": "No clear winner among proposals.",
                    "details": {
                        "scores": scores,
                        "tied_winners": winners if winners else None
                    }
                }
            }

    async def _evaluate_compromise(self, negotiation_id: str, round_num: int, proposals: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposals using compromise strategy.

        Args:
            negotiation_id: ID of the negotiation.
            round_num: Current round number.
            proposals: Proposals from all parties.

        Returns:
            Dict containing evaluation result.
        """
        negotiation = self.active_negotiations[negotiation_id]
        subject = negotiation["subject"]
        
        # In a compromise strategy, we try to find middle ground between proposals
        
        # Extract proposal values
        proposal_values = {party_id: data["proposal"] for party_id, data in proposals.items()}
        
        # Identify numeric fields that can be averaged
        numeric_fields = {}
        all_keys = set()
        
        for proposal in proposal_values.values():
            all_keys.update(proposal.keys())
        
        for key in all_keys:
            values = [proposal.get(key) for proposal in proposal_values.values() if key in proposal]
            if all(isinstance(v, (int, float)) for v in values):
                numeric_fields[key] = values
        
        # Check if we have enough numeric fields to compromise
        if not numeric_fields:
            return {
                "agreement_reached": False,
                "feedback": {
                    "message": "No numeric fields found for compromise.",
                    "details": {
                        "proposals": proposal_values
                    }
                }
            }
        
        # Calculate compromise values
        compromise_proposal = {}
        
        for key, values in numeric_fields.items():
            compromise_proposal[key] = sum(values) / len(values)
        
        # Check if compromise is acceptable
        # In a real implementation, this would involve checking with parties
        # For now, we'll use a simple heuristic: if the compromise is within 20% of all proposals
        acceptable = True
        
        for key, values in numeric_fields.items():
            compromise_value = compromise_proposal[key]
            for value in values:
                if abs(value - compromise_value) / max(abs(value), 0.001) > 0.2:
                    acceptable = False
                    break
            
            if not acceptable:
                break
        
        if acceptable:
            # Add non-numeric fields from first proposal (simplified approach)
            for key in all_keys:
                if key not in compromise_proposal:
                    for proposal in proposal_values.values():
                        if key in proposal:
                            compromise_proposal[key] = proposal[key]
                            break
            
            return {
                "agreement_reached": True,
                "accepted_proposal": compromise_proposal,
                "feedback": {
                    "message": "Compromise proposal created and accepted.",
                    "details": {
                        "compromise_proposal": compromise_proposal,
                        "original_proposals": proposal_values
                    }
                }
            }
        else:
            return {
                "agreement_reached": False,
                "feedback": {
                    "message": "Compromise proposal created but differences are too large.",
                    "details": {
                        "compromise_proposal": compromise_proposal,
                        "numeric_fields": numeric_fields
                    }
                }
            }

    async def _evaluate_integrative(self, negotiation_id: str, round_num: int, proposals: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposals using integrative strategy.

        Args:
            negotiation_id: ID of the negotiation.
            round_num: Current round number.
            proposals: Proposals from all parties.

        Returns:
            Dict containing evaluation result.
        """
        negotiation = self.active_negotiations[negotiation_id]
        subject = negotiation["subject"]
        parameters = negotiation["parameters"]
        
        # In an integrative strategy, we try to maximize joint value
        
        # Extract proposal values
        proposal_values = {party_id: data["proposal"] for party_id, data in proposals.items()}
        
        # Get party preferences from parameters
        party_preferences = parameters.get("party_preferences", {})
        
        if not party_preferences:
            # No preferences provided, fall back to compromise strategy
            return await self._evaluate_compromise(negotiation_id, round_num, proposals)
        
        # Calculate utility for each party for each proposal
        utilities = {}
        
        for party_id, preferences in party_preferences.items():
            utilities[party_id] = {}
            
            for proposer_id, proposal in proposal_values.items():
                utility = 0
                
                for key, value in proposal.items():
                    if key in preferences:
                        pref = preferences[key]
                        
                        if pref["type"] == "numeric":
                            # Linear utility function
                            if pref.get("higher_is_better", True):
                                utility += value * pref.get("weight", 1)
                            else:
                                utility += (pref.get("max_value", 100) - value) * pref.get("weight", 1)
                        elif pref["type"] == "boolean":
                            if value == pref.get("preferred_value", True):
                                utility += pref.get("weight", 1)
                        elif pref["type"] == "categorical":
                            if value in pref.get("preferred_values", []):
                                utility += pref.get("weight", 1)
                
                utilities[party_id][proposer_id] = utility
        
        # Calculate joint utility for each proposal
        joint_utilities = {}
        
        for proposer_id in proposal_values.keys():
            joint_utility = sum(utilities[party_id][proposer_id] for party_id in party_preferences.keys())
            joint_utilities[proposer_id] = joint_utility
        
        # Find proposal with highest joint utility
        highest_utility = max(joint_utilities.values()) if joint_utilities else 0
        winners = [party_id for party_id, utility in joint_utilities.items() if utility == highest_utility]
        
        # Check if there's a clear winner
        if len(winners) == 1:
            winner = winners[0]
            winning_proposal = proposal_values[winner]
            
            # Check if utility meets minimum threshold
            min_threshold = parameters.get("min_joint_utility", 0)
            if highest_utility >= min_threshold:
                return {
                    "agreement_reached": True,
                    "accepted_proposal": winning_proposal,
                    "feedback": {
                        "message": f"Proposal from {winner} selected for highest joint utility.",
                        "details": {
                            "joint_utilities": joint_utilities,
                            "winner": winner,
                            "winning_proposal": winning_proposal
                        }
                    }
                }
            else:
                return {
                    "agreement_reached": False,
                    "feedback": {
                        "message": "No proposal met the minimum joint utility threshold.",
                        "details": {
                            "joint_utilities": joint_utilities,
                            "min_threshold": min_threshold
                        }
                    }
                }
        else:
            # Tie or no proposals
            return {
                "agreement_reached": False,
                "feedback": {
                    "message": "No clear winner among proposals based on joint utility.",
                    "details": {
                        "joint_utilities": joint_utilities,
                        "tied_winners": winners if winners else None
                    }
                }
            }

    async def _evaluate_distributive(self, negotiation_id: str, round_num: int, proposals: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposals using distributive strategy.

        Args:
            negotiation_id: ID of the negotiation.
            round_num: Current round number.
            proposals: Proposals from all parties.

        Returns:
            Dict containing evaluation result.
        """
        negotiation = self.active_negotiations[negotiation_id]
        subject = negotiation["subject"]
        parameters = negotiation["parameters"]
        
        # In a distributive strategy, we focus on a single issue and find middle ground
        
        # Extract proposal values
        proposal_values = {party_id: data["proposal"] for party_id, data in proposals.items()}
        
        # Get key issue from parameters
        key_issue = parameters.get("key_issue")
        
        if not key_issue:
            # No key issue specified, fall back to competitive strategy
            return await self._evaluate_competitive(negotiation_id, round_num, proposals)
        
        # Extract values for key issue
        issue_values = {}
        
        for party_id, proposal in proposal_values.items():
            if key_issue in proposal:
                issue_values[party_id] = proposal[key_issue]
        
        # Check if we have values for the key issue
        if not issue_values:
            return {
                "agreement_reached": False,
                "feedback": {
                    "message": f"Key issue '{key_issue}' not found in proposals.",
                    "details": {
                        "proposals": proposal_values,
                        "key_issue": key_issue
                    }
                }
            }
        
        # Check if all values are numeric
        if not all(isinstance(v, (int, float)) for v in issue_values.values()):
            return {
                "agreement_reached": False,
                "feedback": {
                    "message": f"Values for key issue '{key_issue}' must be numeric.",
                    "details": {
                        "issue_values": issue_values
                    }
                }
            }
        
        # Calculate middle point
        middle_value = sum(issue_values.values()) / len(issue_values)
        
        # Find proposal closest to middle point
        closest_party = min(issue_values.keys(), key=lambda p: abs(issue_values[p] - middle_value))
        closest_value = issue_values[closest_party]
        
        # Create accepted proposal based on closest proposal
        accepted_proposal = dict(proposal_values[closest_party])
        accepted_proposal[key_issue] = middle_value
        
        # Check if middle value is acceptable
        # In a real implementation, this would involve checking with parties
        # For now, we'll use a simple heuristic: if the middle value is within 20% of all proposals
        acceptable = True
        
        for value in issue_values.values():
            if abs(value - middle_value) / max(abs(value), 0.001) > 0.2:
                acceptable = False
                break
        
        if acceptable:
            return {
                "agreement_reached": True,
                "accepted_proposal": accepted_proposal,
                "feedback": {
                    "message": f"Agreement reached on key issue '{key_issue}' with value {middle_value}.",
                    "details": {
                        "key_issue": key_issue,
                        "issue_values": issue_values,
                        "middle_value": middle_value,
                        "accepted_proposal": accepted_proposal
                    }
                }
            }
        else:
            return {
                "agreement_reached": False,
                "feedback": {
                    "message": f"No agreement reached on key issue '{key_issue}'. Values are too far apart.",
                    "details": {
                        "key_issue": key_issue,
                        "issue_values": issue_values,
                        "middle_value": middle_value
                    }
                }
            }

    async def _provide_feedback_to_parties(self, negotiation_id: str, round_num: int, feedback: Dict[str, Any]):
        """Provide feedback to parties after a negotiation round.

        Args:
            negotiation_id: ID of the negotiation.
            round_num: Current round number.
            feedback: Feedback to provide.
        """
        negotiation = self.active_negotiations[negotiation_id]
        workflow_id = negotiation["workflow_id"]
        parties = negotiation["parties"]
        
        # Notify all parties of round result
        for party in parties:
            try:
                # In a real implementation, this would send a message to the party
                logger.info(f"Providing feedback to party {party} for round {round_num} of negotiation {negotiation_id}")
                
                # Send feedback via workflow runtime
                await self.workflow_runtime.send_agent_message(
                    source_agent_id=self.agent_id,
                    target_agent_id=party,
                    message_type="negotiation_feedback",
                    payload={
                        "negotiation_id": negotiation_id,
                        "workflow_id": workflow_id,
                        "round": round_num,
                        "agreement_reached": False,
                        "feedback": feedback
                    }
                )
            except Exception as e:
                logger.error(f"Error providing feedback to party {party}: {str(e)}")

    async def _notify_parties_of_agreement(self, negotiation_id: str):
        """Notify parties of agreement reached.

        Args:
            negotiation_id: ID of the negotiation.
        """
        negotiation = self.active_negotiations[negotiation_id]
        workflow_id = negotiation["workflow_id"]
        parties = negotiation["parties"]
        accepted_proposal = negotiation["accepted_proposal"]
        
        # Notify all parties of agreement
        for party in parties:
            try:
                # In a real implementation, this would send a message to the party
                logger.info(f"Notifying party {party} of agreement for negotiation {negotiation_id}")
                
                # Send notification via workflow runtime
                await self.workflow_runtime.send_agent_message(
                    source_agent_id=self.agent_id,
                    target_agent_id=party,
                    message_type="negotiation_agreement",
                    payload={
                        "negotiation_id": negotiation_id,
                        "workflow_id": workflow_id,
                        "agreement_reached": True,
                        "accepted_proposal": accepted_proposal
                    }
                )
            except Exception as e:
                logger.error(f"Error notifying party {party} of agreement: {str(e)}")

    async def _notify_parties_of_failure(self, negotiation_id: str):
        """Notify parties of negotiation failure.

        Args:
            negotiation_id: ID of the negotiation.
        """
        negotiation = self.active_negotiations[negotiation_id]
        workflow_id = negotiation["workflow_id"]
        parties = negotiation["parties"]
        
        # Notify all parties of failure
        for party in parties:
            try:
                # In a real implementation, this would send a message to the party
                logger.info(f"Notifying party {party} of failure for negotiation {negotiation_id}")
                
                # Send notification via workflow runtime
                await self.workflow_runtime.send_agent_message(
                    source_agent_id=self.agent_id,
                    target_agent_id=party,
                    message_type="negotiation_failure",
                    payload={
                        "negotiation_id": negotiation_id,
                        "workflow_id": workflow_id,
                        "agreement_reached": False,
                        "reason": "Max rounds reached without agreement"
                    }
                )
            except Exception as e:
                logger.error(f"Error notifying party {party} of failure: {str(e)}")

    async def stop_negotiation(self, negotiation_id: str) -> Dict[str, Any]:
        """Stop an ongoing negotiation.

        Args:
            negotiation_id: ID of the negotiation to stop.

        Returns:
            Dict containing negotiation stop status.
        """
        try:
            # Check if negotiation exists and is active
            if negotiation_id not in self.active_negotiations:
                return {
                    "success": False,
                    "error": f"Negotiation {negotiation_id} not found or not active"
                }
            
            negotiation = self.active_negotiations[negotiation_id]
            workflow_id = negotiation["workflow_id"]
            
            # Mark negotiation as stopped
            negotiation["status"] = "stopped"
            negotiation["end_time"] = datetime.utcnow().isoformat()
            negotiation["result"] = "stopped"
            
            # Move to history
            self.negotiation_history[negotiation_id] = negotiation
            del self.active_negotiations[negotiation_id]
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "stop_negotiation",
                "reason": f"Stopped negotiation {negotiation_id} for workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Stopped negotiation {negotiation_id}")
            
            # Notify parties of stop
            for party in negotiation["parties"]:
                try:
                    # Send notification via workflow runtime
                    await self.workflow_runtime.send_agent_message(
                        source_agent_id=self.agent_id,
                        target_agent_id=party,
                        message_type="negotiation_stopped",
                        payload={
                            "negotiation_id": negotiation_id,
                            "workflow_id": workflow_id
                        }
                    )
                except Exception as e:
                    logger.error(f"Error notifying party {party} of negotiation stop: {str(e)}")
            
            return {
                "success": True,
                "negotiation_id": negotiation_id,
                "status": "stopped"
            }
            
        except Exception as e:
            logger.error(f"Error stopping negotiation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_negotiation_status(self, negotiation_id: str) -> Dict[str, Any]:
        """Get the status of a negotiation.

        Args:
            negotiation_id: ID of the negotiation.

        Returns:
            Dict containing negotiation status.
        """
        if negotiation_id in self.active_negotiations:
            negotiation = self.active_negotiations[negotiation_id]
            return {
                "success": True,
                "negotiation_id": negotiation_id,
                "status": negotiation["status"],
                "workflow_id": negotiation["workflow_id"],
                "subject": negotiation["subject"],
                "strategy": negotiation["strategy"],
                "current_round": negotiation["current_round"],
                "start_time": negotiation["start_time"]
            }
        elif negotiation_id in self.negotiation_history:
            negotiation = self.negotiation_history[negotiation_id]
            return {
                "success": True,
                "negotiation_id": negotiation_id,
                "status": negotiation["status"],
                "workflow_id": negotiation["workflow_id"],
                "subject": negotiation["subject"],
                "strategy": negotiation["strategy"],
                "rounds_completed": len(negotiation["rounds"]),
                "start_time": negotiation["start_time"],
                "end_time": negotiation.get("end_time"),
                "result": negotiation.get("result"),
                "accepted_proposal": negotiation.get("accepted_proposal")
            }
        else:
            return {
                "success": False,
                "error": f"Negotiation {negotiation_id} not found"
            }

    async def get_negotiation_history(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get history of negotiations.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing negotiation history.
        """
        if workflow_id:
            # Filter by workflow ID
            history = {
                neg_id: data
                for neg_id, data in self.negotiation_history.items()
                if data["workflow_id"] == workflow_id
            }
        else:
            # Return all history
            history = self.negotiation_history
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "negotiation_count": len(history),
            "negotiations": history
        }

    def get_agent_manifest(self) -> Dict[str, Any]:
        """Get the agent manifest.

        Returns:
            Dict containing agent manifest information.
        """
        return {
            "agent_id": self.agent_id,
            "layer": "workflow_layer",
            "capabilities": self.agent_capabilities,
            "supported_protocols": self.supported_protocols,
            "resilience_mode": "quorum_vote",
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": True,
                "editable_nodes": ["negotiation_node", "proposal_node"]
            }
        }

    async def handle_protocol_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a protocol message.

        Args:
            message: Protocol message to handle.

        Returns:
            Dict containing handling result.
        """
        try:
            message_type = message.get("message_type")
            
            if message_type == "start_negotiation":
                return await self.start_negotiation(message.get("payload", {}))
            elif message_type == "submit_proposal":
                return await self.submit_proposal(message.get("payload", {}))
            elif message_type == "stop_negotiation":
                payload = message.get("payload", {})
                negotiation_id = payload.get("negotiation_id")
                return await self.stop_negotiation(negotiation_id)
            elif message_type == "get_negotiation_status":
                payload = message.get("payload", {})
                negotiation_id = payload.get("negotiation_id")
                return await self.get_negotiation_status(negotiation_id)
            elif message_type == "get_negotiation_history":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_negotiation_history(workflow_id)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {message_type}"
                }
                
        except Exception as e:
            logger.error(f"Error handling protocol message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
