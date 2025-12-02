from enum import Enum
from typing import Dict, Any

# Import SOK components for type hinting (mock if circular dependency issues arise)
# from src.sok.organism_kernel import SovereignOrganism

class StrategicMode(Enum):
    PEACE = "PEACE"             # Balanced Growth
    WAR = "WAR"                 # High Defense, Low Risk
    SINGULARITY = "SINGULARITY" # Max Discovery, High Risk
    HIBERNATION = "HIBERNATION" # Max Safety, Min Energy

class OverseerStratiform:
    """
    The Strategic Brain.
    Orchestrates the Organism's high-level strategy based on Narrative and Safety context.
    """
    
    def __init__(self):
        self.current_mode = StrategicMode.PEACE
        self.strategy_log = []
        
    def evaluate_strategy(self, organism) -> StrategicMode:
        """
        Decides the optimal strategy based on the Organism's full context.
        """
        # 1. Get Context
        narrative = organism.narrative.get_context_summary()
        safety_status, safety_reason = organism.safety.evaluate_safety(organism.state)
        
        print(f"   🧠 [OVERSEER] Evaluating Strategy... (Context: {narrative['context_mode']})")
        
        new_mode = self.current_mode
        
        # 2. Safety Override (Highest Priority)
        if not safety_status:
            print(f"     -> 🛑 SAFETY OVERRIDE: {safety_reason}")
            new_mode = StrategicMode.HIBERNATION
            
        # 3. Narrative-Driven Strategy
        elif narrative['context_mode'] == "WAR_FOOTING":
            new_mode = StrategicMode.WAR
        elif narrative['context_mode'] == "GOLDEN_AGE":
            new_mode = StrategicMode.SINGULARITY
        else:
            new_mode = StrategicMode.PEACE
            
        # 4. Apply Strategy if Changed
        if new_mode != self.current_mode:
            self._apply_strategy(organism, new_mode)
            
        return new_mode

    def _apply_strategy(self, organism, mode: StrategicMode):
        """
        Reconfigures the Organism's organs for the new mode.
        """
        print(f"   🔄 [OVERSEER] Shifting Strategy: {self.current_mode.name} -> {mode.name}")
        self.current_mode = mode
        self.strategy_log.append(f"Shifted to {mode.name}")
        
        if mode == StrategicMode.WAR:
            # High Defense, High Efficiency
            organism.nervous_system.set_level("ACCELERATED") # Vigilance
            organism.incentives.shape_gradient("SURVIVAL")
            
        elif mode == StrategicMode.SINGULARITY:
            # Max Discovery
            organism.nervous_system.set_level("SINGULARITY")
            organism.incentives.shape_gradient("CURIOSITY")
            
        elif mode == StrategicMode.HIBERNATION:
            # Min Energy
            organism.nervous_system.set_level("STANDARD")
            # organism.state.energy_consumption = 0.1 # Mock
            
        elif mode == StrategicMode.PEACE:
            # Balanced
            organism.nervous_system.set_level("STANDARD")
            organism.incentives.shape_gradient("EXPANSION")

# --- Verification ---
if __name__ == "__main__":
    # Mock Organism for testing
    class MockOrganism:
        def __init__(self):
            self.narrative = None
            self.safety = None
            self.nervous_system = None
            self.incentives = None
            self.state = None
            
    overseer = OverseerStratiform()
    print(f"Initial Mode: {overseer.current_mode}")
