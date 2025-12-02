import time
import hashlib
from dataclasses import dataclass

@dataclass
class TransactionReceipt:
    tx_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: float
    signature: str

class TransactionAgent:
    """
    Manages M2M Payments within the Industriverse.
    Connects 'Work' (Lithography) to 'Value' (Negentropy).
    """
    
    def __init__(self, agent_id: str, initial_balance: float = 1000.0):
        self.agent_id = agent_id
        self.balance = initial_balance
        
    def pay(self, receiver_id: str, amount: float, service_desc: str) -> TransactionReceipt:
        """
        Executes a payment to another agent.
        """
        if self.balance < amount:
            raise ValueError("Insufficient Funds")
            
        self.balance -= amount
        # In a real system, this would call the Blockchain/Ledger
        
        timestamp = time.time()
        tx_hash = hashlib.sha256(f"{self.agent_id}{receiver_id}{amount}{timestamp}".encode()).hexdigest()
        
        return TransactionReceipt(
            tx_id=tx_hash[:16],
            sender=self.agent_id,
            receiver=receiver_id,
            amount=amount,
            timestamp=timestamp,
            signature=f"SIG_{tx_hash[:8]}"
        )

    def receive(self, receipt: TransactionReceipt):
        """
        Receives funds (Mock logic).
        """
        if receipt.receiver != self.agent_id:
            raise ValueError("Invalid Receiver")
        self.balance += receipt.amount

# --- Verification ---
if __name__ == "__main__":
    # Scenario: Lithography Agent pays Compute Agent
    litho_agent = TransactionAgent("AGENT_LITHO_01", 5000.0)
    compute_agent = TransactionAgent("AGENT_COMPUTE_X", 0.0)
    
    print("💸 Executing M2M Transaction...")
    print(f"   - Litho Balance: {litho_agent.balance}")
    print(f"   - Compute Balance: {compute_agent.balance}")
    
    try:
        receipt = litho_agent.pay("AGENT_COMPUTE_X", 150.0, "Mask Optimization Compute")
        compute_agent.receive(receipt)
        
        print("\n✅ Transaction Successful!")
        print(f"   - TX ID: {receipt.tx_id}")
        print(f"   - Amount: {receipt.amount} Negentropy Credits")
        print(f"   - Litho New Balance: {litho_agent.balance}")
        print(f"   - Compute New Balance: {compute_agent.balance}")
        
    except Exception as e:
        print(f"❌ Transaction Failed: {e}")
