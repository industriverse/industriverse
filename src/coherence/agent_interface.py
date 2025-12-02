from typing import List
from src.coherence.iacp_protocol import IACPProtocol, AgentIdentity, IACPMessage
from src.unification.unified_substrate_model import USMSignal

class CoherentAgent:
    """
    The Social Contract.
    Base class for any agent participating in the IACP Society.
    """
    
    def __init__(self, id: str, role: str, protocol: IACPProtocol):
        self.identity = AgentIdentity(id, role, [])
        self.protocol = protocol
        self.inbox: List[IACPMessage] = []
        
        # Join the Society
        self.protocol.register_agent(self.identity)
        
    def send_message(self, recipient_id: str, payload: USMSignal, msg_type: str = "INFO"):
        """
        Sends an IACP message to another agent.
        """
        msg = IACPMessage(
            sender_id=self.identity.id,
            recipient_id=recipient_id,
            type=msg_type,
            payload=payload
        )
        # In a real system, this would go through a bus. 
        # Here we mock direct delivery for simulation.
        print(f"   📤 [{self.identity.id}] Sending {msg_type} to {recipient_id}")
        return msg

    def receive_message(self, msg: IACPMessage):
        """
        Processes an incoming message.
        """
        print(f"   📥 [{self.identity.id}] Received {msg.type} from {msg.sender_id}")
        self.inbox.append(msg)
        
        # Update Trust based on signal quality
        if msg.payload:
            new_trust = self.protocol.calculate_trust(msg.sender_id, msg.payload)
            # print(f"     -> Adjusted Trust for {msg.sender_id}: {new_trust:.2f}")

    def vote_on_proposal(self, proposal_id: str, description: str) -> bool:
        """
        Decides how to vote on a proposal.
        Override this with specific logic.
        """
        # Default Logic: Vote YES if it sounds safe
        return "DANGEROUS" not in description

# --- Verification ---
if __name__ == "__main__":
    proto = IACPProtocol()
    agent = CoherentAgent("TEST_AGENT", "TESTER", proto)
    agent.send_message("BROADCAST", None)
