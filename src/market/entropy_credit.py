import hashlib
import json
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class EntropyCredit:
    credit_id: str
    amount_mj: float # 1 Credit = 1 MJ
    owner_id: str
    minted_at: float
    proof_hash: str

class EntropyCreditEngine:
    """
    Manages the lifecycle of Entropy Credits.
    Energy Savings -> Verification -> Minting -> Asset.
    """
    def __init__(self):
        self.ledger: List[EntropyCredit] = []

    def mint_credits(self, energy_saved_kwh: float, owner_id: str, proof_hash: str) -> EntropyCredit:
        """
        Mint credits based on verified energy savings.
        1 kWh = 3.6 MJ.
        """
        if energy_saved_kwh <= 0:
            raise ValueError("Cannot mint credits for zero or negative savings.")

        amount_mj = energy_saved_kwh * 3.6
        credit_id = hashlib.sha256(f"{owner_id}:{amount_mj}:{time.time()}".encode()).hexdigest()
        
        credit = EntropyCredit(
            credit_id=credit_id,
            amount_mj=amount_mj,
            owner_id=owner_id,
            minted_at=time.time(),
            proof_hash=proof_hash
        )
        
        self.ledger.append(credit)
        print(f"💰 Minted {amount_mj:.2f} Entropy Credits for {owner_id} (ID: {credit_id[:8]})")
        return credit

    def get_balance(self, owner_id: str) -> float:
        """
        Get total credits for an owner.
        """
        return sum(c.amount_mj for c in self.ledger if c.owner_id == owner_id)

    def transfer_credits(self, from_id: str, to_id: str, amount: float) -> bool:
        """
        Simple transfer logic (burn and re-mint for now, or just decrement/increment ledger).
        For this MVP, we just check balance.
        """
        balance = self.get_balance(from_id)
        if balance < amount:
            return False
        
        # In a real system, we'd consume specific UTXOs. 
        # Here we mock the transfer by logging it.
        print(f"💸 Transferred {amount} credits from {from_id} to {to_id}")
        return True
