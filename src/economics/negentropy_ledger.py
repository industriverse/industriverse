import hashlib
import time
import uuid

class NegentropyLedger:
    """
    Challenge #10: Negentropy Accounting System.
    The Industrial Negentropy Ledger (INL).
    Mints tokens for thermodynamic value creation.
    """
    def __init__(self):
        self.ledger = []
        self.token_supply = 0.0

    def record_transaction(self, agent_id, task_id, entropy_reduction):
        """
        Records a 'Negentropy Event' and mints tokens.
        Entropy Reduction (Joules/Kelvin) -> Credits.
        """
        # 1. Calculate Value
        # 1 Unit of Negentropy = 10 Credits (Arbitrary Exchange Rate)
        value = entropy_reduction * 10.0
        
        # 2. Create Transaction Block
        tx = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "agent": agent_id,
            "task": task_id,
            "entropy_reduction": entropy_reduction,
            "value_credits": value,
            "prev_hash": self.ledger[-1]['hash'] if self.ledger else "GENESIS_BLOCK"
        }
        
        # 3. Hash Transaction (Proof of Work/History)
        tx_string = f"{tx['id']}{tx['timestamp']}{tx['agent']}{tx['value_credits']}{tx['prev_hash']}"
        tx['hash'] = hashlib.sha256(tx_string.encode()).hexdigest()
        
        # 4. Commit to Ledger
        self.ledger.append(tx)
        self.token_supply += value
        
        print(f"[INL] 🏦 Minted {value:.2f} Credits for {agent_id}. Hash: {tx['hash'][:8]}...")
        return tx

    def get_balance(self, agent_id):
        """
        Returns the balance of an agent.
        """
        balance = 0.0
        for tx in self.ledger:
            if tx['agent'] == agent_id:
                balance += tx['value_credits']
        return balance
