import random
from src.core.a2a_protocol import A2AProtocol

class NegotiationEngine:
    """
    Challenge #8: Universal Negotiation Protocol.
    Autonomous agent logic for bidding on tasks.
    """
    def __init__(self, agent_id, capabilities):
        self.a2a = A2AProtocol(agent_id)
        self.capabilities = capabilities # List of supported task types
        self.min_margin = 0.15

    def process_ask(self, ask_message):
        """
        Evaluates an ASK message and decides whether to BID.
        """
        payload = ask_message['payload']
        task_type = payload['task_type']
        max_price = payload['max_price']

        if task_type not in self.capabilities:
            print(f"[Negotiator] 🚫 Ignoring ASK for {task_type} (Capability Missing)")
            return None

        # Calculate internal cost (Mock)
        internal_cost = random.uniform(0.1, 0.4)
        bid_price = internal_cost * (1 + self.min_margin)

        if bid_price > max_price:
            print(f"[Negotiator] 📉 Ignoring ASK (Price too low: {max_price} < {bid_price:.2f})")
            return None

        # Generate BID
        bid_payload = {
            "ask_id": ask_message['id'],
            "price": round(bid_price, 4),
            "negentropy_score": random.uniform(90, 99),
            "zk_proof": "mock_zk_proof_string",
            "estimated_duration": random.randint(60, 300)
        }
        
        print(f"[Negotiator] 💰 Bidding on {task_type}: ${bid_price:.2f}")
        return self.a2a.send_message(ask_message['sender'], "BID", bid_payload)

    def run_loop(self):
        """
        Simulates the main loop of the negotiator.
        """
        # In a real system, this would be an async listener.
        # Here we just process the inbox.
        while self.a2a.inbox:
            msg = self.a2a.inbox.pop(0)
            if msg['type'] == 'ASK':
                self.process_ask(msg)
