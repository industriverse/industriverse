from dataclasses import dataclass
import time

@dataclass
class Transaction:
    timestamp: float
    amount: float
    description: str
    tx_hash: str

class NegentropyWallet:
    """
    The Economic Bridge: Manages 'Negentropy Credits' earned from the Neural Battery.
    Allows users to spend them in the Industriverse Ecosystem.
    """
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.balance = 0.0
        self.history = []
        
    def credit_earnings(self, amount: float, source: str):
        """
        Called by NeuralBattery when training is complete.
        """
        self.balance += amount
        tx = Transaction(time.time(), amount, f"Earned from {source}", "hash_earn")
        self.history.append(tx)
        print(f"💰 [Wallet] Credited {amount:.2f}. New Balance: {self.balance:.2f}")
        
    def purchase_capsule(self, capsule_name: str, cost: float) -> bool:
        """
        Spend credits to buy a Skill Capsule or Product.
        """
        if self.balance >= cost:
            self.balance -= cost
            tx = Transaction(time.time(), -cost, f"Purchased {capsule_name}", "hash_spend")
            self.history.append(tx)
            print(f"🛒 [Wallet] Purchased '{capsule_name}' for {cost:.2f}. Remaining: {self.balance:.2f}")
            return True
        else:
            print(f"❌ [Wallet] Insufficient Funds for '{capsule_name}'. Need {cost:.2f}, Have {self.balance:.2f}")
            return False
