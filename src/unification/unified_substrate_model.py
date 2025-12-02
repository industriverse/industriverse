from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time
import uuid

class SignalType(Enum):
    THERMAL = "THERMAL"       # Heat, CPU Load
    SOCIAL = "SOCIAL"         # Sentiment, Influence
    ECONOMIC = "ECONOMIC"     # Price, Transaction
    SECURITY = "SECURITY"     # Threat, Intrusion
    SCIENTIFIC = "SCIENTIFIC" # Law, Constant
    INTERNAL = "INTERNAL"     # Health, Drive

@dataclass
class USMEnergy:
    """
    Canonical representation of Energy.
    Unifies Joules, Compute Cycles, and Economic Value.
    """
    joules: float = 0.0
    compute_flops: float = 0.0
    economic_value: float = 0.0
    
    def to_negentropy_credits(self) -> float:
        # Conversion logic: 1 Credit = 1 MJ + 1 TFLOP
        return (self.joules / 1e6) + (self.compute_flops / 1e12)

@dataclass
class USMEntropy:
    """
    Canonical representation of Entropy (Disorder).
    Unifies Shannon Entropy (Info) and Thermodynamic Entropy (Heat).
    """
    shannon_index: float = 0.0 # 0.0 (Ordered) -> 1.0 (Random)
    thermo_disorder: float = 0.0
    social_discord: float = 0.0
    
    def get_composite_score(self) -> float:
        return (self.shannon_index + self.thermo_disorder + self.social_discord) / 3

@dataclass
class USMSignal:
    """
    The Atomic Unit of Information in the Organism.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: SignalType = SignalType.INTERNAL
    timestamp: float = field(default_factory=time.time)
    source_id: str = "UNKNOWN"
    
    # Payload
    energy_delta: Optional[USMEnergy] = None
    entropy_delta: Optional[USMEntropy] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """
        Stringent validation of signal integrity.
        """
        if not self.id or not self.source_id:
            return False
        if self.timestamp > time.time() + 1.0: # Future timestamp check
            return False
        return True

# --- Verification ---
if __name__ == "__main__":
    # Test Energy Conversion
    energy = USMEnergy(joules=5000000, compute_flops=2e12)
    print(f"Negentropy Credits: {energy.to_negentropy_credits()}")
    
    # Test Signal Validation
    sig = USMSignal(type=SignalType.THERMAL, source_id="SENSOR_01")
    print(f"Signal Valid: {sig.validate()}")
