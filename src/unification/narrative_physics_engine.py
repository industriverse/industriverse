from dataclasses import dataclass
from typing import Dict

@dataclass
class WorldState:
    social_sentiment: float = 0.5 # 0.0 (Hostile) -> 1.0 (Supportive)
    energy_grid_stability: float = 0.9
    scientific_consensus: float = 0.7
    global_tension: float = 0.2

class NarrativePhysicsEngine:
    """
    The Hippocampus.
    Maintains a unified 'World Model' integrating Social, Industrial, and Scientific signals.
    """
    
    def __init__(self):
        self.world_state = WorldState()
        self.narrative_threads = [] # History of events
        
    def ingest_signal(self, source: str, value: float, description: str):
        """
        Updates the world model based on incoming telemetry.
        """
        print(f"   📜 [NARRATIVE] Ingesting: {source} -> {value} ({description})")
        
        if source == "SPI": # Social Physics
            self.world_state.social_sentiment = (self.world_state.social_sentiment + value) / 2
        elif source == "GRID": # Industrial
            self.world_state.energy_grid_stability = value
        elif source == "LITHOS": # Scientific
            self.world_state.scientific_consensus = value
            
        self.narrative_threads.append(f"[{source}] {description}")
        
    def get_context_summary(self):
        """
        Returns a high-level summary of the world state for the Cortex.
        """
        context = "STABLE"
        if self.world_state.global_tension > 0.8:
            context = "WAR_FOOTING"
        elif self.world_state.social_sentiment < 0.3:
            context = "HOSTILE_ENVIRONMENT"
        elif self.world_state.scientific_consensus > 0.9:
            context = "GOLDEN_AGE"
            
        return {
            "context_mode": context,
            "sentiment": self.world_state.social_sentiment,
            "grid": self.world_state.energy_grid_stability
        }

# --- Verification ---
if __name__ == "__main__":
    engine = NarrativePhysicsEngine()
    
    # Ingest Signals
    engine.ingest_signal("SPI", 0.2, "Detected Anti-AI Sentiment")
    engine.ingest_signal("GRID", 0.95, "Energy Grid Stable")
    
    # Check Context
    print(f"\nWorld Context: {engine.get_context_summary()}")
