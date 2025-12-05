from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Capsule:
    capsule_id: str
    name: str
    price_usd: float
    description: str

class CapsuleStorefront:
    """
    Marketplace for buying/selling Industrial Capsules.
    """
    def __init__(self):
        self.catalog = {
            "cap_predictive_maint": Capsule(
                "cap_predictive_maint", 
                "Predictive Maintenance Pack", 
                1500.0, 
                "Detects bearing failures 2 weeks in advance."
            ),
            "cap_energy_opt": Capsule(
                "cap_energy_opt", 
                "HVAC Energy Optimizer", 
                800.0, 
                "Reduces HVAC spend by 15%."
            )
        }
        self.purchases = []

    def list_capsules(self) -> List[Capsule]:
        return list(self.catalog.values())

    def purchase_capsule(self, client_id: str, capsule_id: str) -> bool:
        if capsule_id not in self.catalog:
            print(f"❌ Capsule not found: {capsule_id}")
            return False
            
        self.purchases.append({"client_id": client_id, "capsule_id": capsule_id})
        print(f"💰 Client {client_id} purchased {capsule_id}")
        return True
