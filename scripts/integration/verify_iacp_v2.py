import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.coherence.iacp_v2 import IACPMessage, IACPIntent, IACPContext
from src.coherence.intent_parser import IntentParser

def verify_iacp_v2():
    print("🗣️ INITIALIZING IACP V2 COHERENCE SIMULATION...")
    
    # 1. Setup Responder Agent
    responder_parser = IntentParser()
    response_log = []
    
    def handle_warning(msg: IACPMessage):
        print(f"   🛡️ [RESPONDER] Defense Protocol Initiated: {msg.payload['threat']}")
        response_log.append("DEFENSE_ACTIVE")
        
    def handle_ack(msg: IACPMessage):
        print(f"   ✅ [SENTINEL] Acknowledgement Received.")
        response_log.append("ACK_RECEIVED")

    responder_parser.register_handler(IACPIntent.ISSUE_WARNING, handle_warning)
    
    # 2. Simulate Dialogue
    print("\n--- Step 1: Sentinel Issues Warning ---")
    warning_msg = IACPMessage(
        sender_id="Sentinel_01",
        target_id="Responder_Command",
        intent=IACPIntent.ISSUE_WARNING,
        context=IACPContext(urgency=0.95, domain="SECURITY"),
        payload={"threat": "UNAUTHORIZED_ACCESS_SECTOR_7"}
    )
    
    responder_parser.process(warning_msg)
    
    if "DEFENSE_ACTIVE" in response_log:
        print("✅ Responder correctly handled High Urgency Warning.")
    else:
        print("❌ Responder failed to react.")
        sys.exit(1)
        
    # 3. Simulate Response
    print("\n--- Step 2: Responder Acknowledges ---")
    sentinel_parser = IntentParser()
    sentinel_parser.register_handler(IACPIntent.ACKNOWLEDGE, handle_ack)
    
    ack_msg = IACPMessage(
        sender_id="Responder_Command",
        target_id="Sentinel_01",
        intent=IACPIntent.ACKNOWLEDGE,
        context=IACPContext(0.1, "ADMIN"),
        payload={"status": "DEPLOYING_COUNTERMEASURES"}
    )
    
    sentinel_parser.process(ack_msg)
    
    if "ACK_RECEIVED" in response_log:
        print("✅ Sentinel received acknowledgement.")
    else:
        print("❌ Sentinel failed to receive ack.")
        sys.exit(1)
        
    print("\n✅ IACP V2 Verification Complete. The Organism Speaks.")

if __name__ == "__main__":
    verify_iacp_v2()
