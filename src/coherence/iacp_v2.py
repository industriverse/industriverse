from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum
import time
import uuid

class IACPIntent(Enum):
    """
    The Semantic Intent of a message.
    """
    QUERY_KNOWLEDGE = "QUERY_KNOWLEDGE"
    SHARE_INSIGHT = "SHARE_INSIGHT"
    REQUEST_RESOURCE = "REQUEST_RESOURCE"
    NEGOTIATE_CONTRACT = "NEGOTIATE_CONTRACT"
    ISSUE_WARNING = "ISSUE_WARNING"
    ACKNOWLEDGE = "ACKNOWLEDGE"

@dataclass
class IACPContext:
    """
    The Situational Awareness attached to a message.
    """
    urgency: float # 0.0 to 1.0
    domain: str # SECURITY, ECONOMICS, PHYSICS
    reference_id: Optional[str] = None # ID of related event/task

@dataclass
class IACPMessage:
    """
    The Envelope of the Inter-Agent Coherence Protocol V2.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = "UNKNOWN"
    target_id: str = "BROADCAST"
    intent: IACPIntent = IACPIntent.SHARE_INSIGHT
    context: IACPContext = field(default_factory=lambda: IACPContext(0.5, "GENERAL"))
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def __repr__(self):
        return f"<IACP Msg {self.id[:8]} | {self.intent.name} | From: {self.sender_id}>"

# --- Verification ---
if __name__ == "__main__":
    msg = IACPMessage(
        sender_id="Agent_Alpha",
        intent=IACPIntent.ISSUE_WARNING,
        context=IACPContext(urgency=0.9, domain="SECURITY"),
        payload={"threat": "Intrusion Detected"}
    )
    print(msg)
