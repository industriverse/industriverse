import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.integration.sovereign_organism_v3 import SovereignOrganismV3

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_sovereign_organism_v3():
    print_header("DEMO: THE SOVEREIGN ORGANISM V3 (GRAND UNIFICATION)")
    print("Scenario: Autonomous Defense & Self-Healing")
    
    # 1. Genesis
    organism = SovereignOrganismV3()
    
    # 2. Normal Cycle
    print("\n>> STEP 1: Normal Operations...")
    organism.heartbeat()
    time.sleep(1)
    
    # 3. Attack Simulation
    print("\n>> STEP 2: CYBER-PHYSICAL ATTACK DETECTED!")
    # Inject Signal via NATS
    organism.nats.publish("usm.security.alert", {"type": "DDOS", "severity": "CRITICAL"})
    
    # Simulate USM Ingestion
    print("   📡 [USM] Signal Integrated: Security Alert (DDOS)")
    
    # Simulate Overseer Response
    print("   🧠 [OVERSEER] Threat Assessment: HIGH. Initiating Protocol: LOCKDOWN.")
    
    # Simulate Action
    print("   🛡️ [WORKFORCE] Deploying Counter-Measure Agents...")
    organism.workforce.spawn_agent("Security_Bot_Alpha", "DEFENSE")
    
    # Simulate Edge Response
    print("   🔒 [EDGE] Locking down 5 Nodes...")
    
    # 4. Stress & Healing
    print("\n>> STEP 3: System Stress & Healing...")
    # Simulate Overseer Stress
    organism.immune.update_vitals("Overseer", 95.0, 0.0) # High CPU
    organism.healer.scan_and_heal() # Should Scale Up
    
    # 5. Resolution
    print("\n>> STEP 4: Threat Neutralized.")
    print("   ✅ Organism Stabilized.")
    
    print_header("DEMO COMPLETE: THE ORGANISM LIVES")

if __name__ == "__main__":
    demo_sovereign_organism_v3()
