import uuid
import time
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class ResourceClusterObject:
    """
    Represents a discovered 'Resource Cluster' in the Energy Atlas.
    A pocket of energy/entropy that might be valuable.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    centroid_energy_signature: Dict[str, float] = field(default_factory=dict) # e.g., {'entropy': 0.5, 'temp': 300}
    entropy_gradient: float = 0.0
    stability_index: float = 0.0 # 0.0 to 1.0
    recurrence_time: float = 0.0 # Seconds
    classification_tags: List[str] = field(default_factory=list) # ['thermal', 'vibration']
    created_at: float = field(default_factory=time.time)
    
    # Scores (Calculated later)
    opportunity_score: float = 0.0
    risk_score: float = 0.0

    def to_json(self):
        return json.dumps(asdict(self))

@dataclass
class OpportunityZone:
    """
    A strategic region of meaning, grouping multiple RCOs.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Zone"
    rco_ids: List[str] = field(default_factory=list)
    aggregated_opportunity_score: float = 0.0
    aggregated_risk: float = 0.0
    dominant_tag: str = "Unknown"
    created_at: float = field(default_factory=time.time)

    def to_json(self):
        return json.dumps(asdict(self))
