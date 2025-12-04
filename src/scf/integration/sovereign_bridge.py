from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class EnergyContext:
    """
    Represents the instantaneous state of the Sovereign Organism.
    Combines Real-time Pulse (Telemetry) and Energy Atlas (Spatial/Static).
    """
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    pulse_metrics: Dict[str, Any] = field(default_factory=dict)
    atlas_state: Dict[str, Any] = field(default_factory=dict)
    daemon_gear: str = "STANDARD"
    
    @property
    def total_system_entropy(self) -> float:
        return self.pulse_metrics.get("system_entropy", 0.0)

    @property
    def active_nodes(self) -> int:
        return self.atlas_state.get("node_count", 0)
