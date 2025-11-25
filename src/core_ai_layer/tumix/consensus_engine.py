from typing import List
from .schema import AgentVote, ConsensusResult

class ConsensusEngine:
    """
    Aggregates votes to determine consensus.
    Calculates a 'Truth Score' based on agent confidence and agreement.
    """
    
    def calculate_consensus(self, request_id: str, votes: List[AgentVote], required_majority: float) -> ConsensusResult:
        """
        Calculate the final decision.
        """
        total_votes = len(votes)
        if total_votes == 0:
            return ConsensusResult(
                request_id=request_id,
                status="failed",
                final_decision="rejected",
                truth_score=0.0,
                votes=[],
                synthesis="No votes cast."
            )
            
        approvals = sum(1 for v in votes if v.vote == "approve")
        rejections = sum(1 for v in votes if v.vote == "reject")
        
        approval_ratio = approvals / total_votes
        
        # Calculate weighted truth score
        total_confidence = sum(v.confidence for v in votes)
        weighted_score = sum(v.confidence for v in votes if v.vote == "approve") / total_confidence if total_confidence > 0 else 0.0
        
        status = "dissent"
        final_decision = "rejected"
        
        # Check for Security Veto
        security_veto = any(v.vote == "reject" and v.role.value == "security" and v.confidence > 0.9 for v in votes)
        
        if security_veto:
            status = "vetoed"
            final_decision = "rejected"
        elif approval_ratio >= required_majority:
            status = "consensus_reached"
            final_decision = "approved"
        
        # Synthesize reasoning
        reasons = [f"{v.role.value}: {v.reasoning}" for v in votes]
        synthesis = "; ".join(reasons)
        
        return ConsensusResult(
            request_id=request_id,
            status=status,
            final_decision=final_decision,
            truth_score=weighted_score,
            votes=votes,
            synthesis=synthesis
        )
