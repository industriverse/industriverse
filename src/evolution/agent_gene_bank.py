from dataclasses import dataclass, field
from typing import List, Dict
import uuid
import random

@dataclass
class AgentGenome:
    """
    The DNA of a Sovereign Agent.
    """
    id: str
    generation: int
    capabilities: List[str] # e.g., ["DATA_MINING", "PATTERN_MATCHING"]
    traits: Dict[str, float] # e.g., {"speed": 0.8, "accuracy": 0.9}
    parent_id: str = None

class AgentGeneBank:
    """
    The Archive of Industrial Life.
    Stores and evolves agent genomes.
    """
    
    def __init__(self):
        self.genomes: Dict[str, AgentGenome] = {}
        
    def register_genome(self, genome: AgentGenome):
        self.genomes[genome.id] = genome
        print(f"   🧬 [GENE BANK] Registered Genome: {genome.id} (Gen {genome.generation})")
        
    def mutate_genome(self, parent_id: str) -> AgentGenome:
        """
        Creates a mutated offspring from a parent genome.
        """
        parent = self.genomes.get(parent_id)
        if not parent:
            raise ValueError(f"Parent genome {parent_id} not found")
            
        # Create Offspring
        new_traits = parent.traits.copy()
        
        # Mutation Logic: Randomly adjust a trait
        trait_to_mutate = random.choice(list(new_traits.keys()))
        mutation_factor = random.uniform(0.9, 1.1) # +/- 10%
        new_traits[trait_to_mutate] *= mutation_factor
        
        offspring = AgentGenome(
            id=str(uuid.uuid4()),
            generation=parent.generation + 1,
            capabilities=parent.capabilities.copy(),
            traits=new_traits,
            parent_id=parent.id
        )
        
        print(f"   ⚡ [EVOLUTION] Mutation: {trait_to_mutate} changed by {mutation_factor:.2f}x")
        self.register_genome(offspring)
        return offspring

# --- Verification ---
if __name__ == "__main__":
    bank = AgentGeneBank()
    
    # Genesis
    g1 = AgentGenome(
        id="GENESIS_ALPHA", 
        generation=1, 
        capabilities=["CODING"], 
        traits={"speed": 1.0, "creativity": 0.5}
    )
    bank.register_genome(g1)
    
    # Evolve
    g2 = bank.mutate_genome(g1.id)
