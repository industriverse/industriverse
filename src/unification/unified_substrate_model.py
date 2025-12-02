from dataclasses import dataclass, field
from typing import List, Dict, Any
import time
import uuid

@dataclass
class USMEntropy:
    """
    Standardized measure of disorder/uncertainty.
    Range: 0.0 (Perfect Order) to 1.0 (Max Chaos).
    """
    value: float
    type: str # THERMAL, INFORMATION, SOCIAL, ECONOMIC

@dataclass
class USMSignal:
    """
    The Atomic Unit of the Substrate.
    Represents a single data point in the unified field.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = "UNKNOWN"
    timestamp: float = field(default_factory=time.time)
    
    # The Payload
    value: float = 0.0
    entropy: USMEntropy = field(default_factory=lambda: USMEntropy(0.0, "INFORMATION"))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"<Signal {self.id[:8]} | Val:{self.value:.2f} | Ent:{self.entropy.value:.2f} ({self.entropy.type})>"

@dataclass
class USMField:
    """
    A collection of signals representing a state over time/space.
    """
    name: str
    signals: List[USMSignal] = field(default_factory=list)
    
    def add_signal(self, signal: USMSignal):
        self.signals.append(signal)
        
    def get_average_entropy(self) -> float:
        if not self.signals: return 0.0
        return sum(s.entropy.value for s in self.signals) / len(self.signals)

# --- Verification ---
if __name__ == "__main__":
    s1 = USMSignal(value=100.0, entropy=USMEntropy(0.1, "THERMAL"))
    s2 = USMSignal(value=105.0, entropy=USMEntropy(0.8, "THERMAL")) # High disorder
    
    field_obj = USMField("Reactor_Core_Temp")
    field_obj.add_signal(s1)
    field_obj.add_signal(s2)
    
    print(f"Field: {field_obj.name}")
    print(f"Avg Entropy: {field_obj.get_average_entropy():.2f}")
