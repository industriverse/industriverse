import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.integration.sovereign_organism_v2 import SovereignOrganismV2
from src.unification.unified_substrate_model import USMSignal, USMEntropy

def verify_sovereign_organism_v2():
    print("🌍 INITIALIZING SOVEREIGN ORGANISM V2 GRAND SIMULATION...")
    
    # 1. Birth
    gaia = SovereignOrganismV2("Gaia_Prime")
    
    # 2. Simulate Peace (Baseline)
    print("\n--- Phase 1: Peacetime ---")
    gaia.heartbeat()
    
    # 3. Simulate Attack (Crisis)
    print("\n--- Phase 2: Cyber-Physical Attack Injection ---")
    # Inject signals that trigger the "CYBER_PHYSICAL_ATTACK" inference
    # Rule: High Security Entropy (>0.7) AND High Thermal Entropy (>0.7)
    
    sig_sec = USMSignal(value=1.0, entropy=USMEntropy(0.95, "SECURITY"))
    sig_therm = USMSignal(value=1.0, entropy=USMEntropy(0.85, "THERMAL"))
    
    gaia.ingest_signal("SECURITY", sig_sec)
    gaia.ingest_signal("THERMAL", sig_therm)
    
    # 4. Reaction Cycle
    print("\n--- Phase 3: The Organism Reacts ---")
    gaia.heartbeat()
    
    # 5. Verification
    print("\n--- Phase 4: Verification ---")
    
    # Check if Defenders were spawned
    defender_count = 0
    for agent in gaia.workforce.active_agents.values():
        if "DEFENDER" in agent.genome.id:
            defender_count += 1
            
    if defender_count >= 5:
        print(f"✅ Organism successfully mobilized defense force (Count: {defender_count}).")
    else:
        print(f"❌ Organism failed to mobilize. Defender Count: {defender_count}")
        sys.exit(1)
        
    print("\n✅ Sovereign Organism V2 Verification Complete. IT IS ALIVE.")

if __name__ == "__main__":
    verify_sovereign_organism_v2()
