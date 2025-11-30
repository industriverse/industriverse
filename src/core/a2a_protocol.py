import json
import time
import uuid

class A2AProtocol:
    """
    Challenge #5: Self-Optimizing Supply Chains.
    Implements the Agent-to-Agent (A2A) Messaging Bus.
    Supports: DIRECT, BROADCAST, PUBSUB.
    """
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.inbox = []
        self.subscriptions = []

    def send_message(self, target_id, message_type, payload):
        """
        Sends a direct message to another agent.
        """
        message = self._envelope(target_id, message_type, payload)
        print(f"[A2A] 📤 {self.agent_id} -> {target_id}: {message_type}")
        # In a real system, this would go over P2P/Mesh.
        # Here we simulate successful transmission.
        return message

    def broadcast(self, message_type, payload):
        """
        Broadcasts a message to all agents on the mesh.
        """
        message = self._envelope("BROADCAST", message_type, payload)
        print(f"[A2A] 📡 {self.agent_id} BROADCAST: {message_type}")
        return message

    def receive(self, message):
        """
        Simulates receiving a message.
        """
        if message['target'] == self.agent_id or message['target'] == "BROADCAST":
            self.inbox.append(message)
            print(f"[A2A] 📥 {self.agent_id} received {message['type']} from {message['sender']}")
            return True
        return False

    def _envelope(self, target, msg_type, payload):
        return {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "sender": self.agent_id,
            "target": target,
            "type": msg_type,
            "payload": payload,
            "signature": f"zk_sig_{uuid.uuid4().hex[:8]}" # Mock ZK Signature
        }
