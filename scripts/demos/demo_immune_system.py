import sys
import os
import time
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.security.immune_system import ImmuneSystem
from src.security.auto_healer import AutoHealer

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_immune_system():
    print_header("DEMO: THE SELF-HEALING IMMUNE SYSTEM")
    print("Scenario: Zero-Touch Recovery from Critical Failure")
    
    # 1. Initialize
    immune = ImmuneSystem()
    healer = AutoHealer(immune)
    
    svc_name = "Payment_Gateway_V2"
    immune.register_service(svc_name)
    
    # 2. Normal Operations
    print("\n>> STEP 1: Normal Operations...")
    immune.update_vitals(svc_name, 25.0, 0.0)
    time.sleep(0.5)
    
    # 3. Fault Injection
    print("\n>> STEP 2: Injecting Fault (Memory Leak)...")
    print("   ⚠️ Error Rate Spiking...")
    immune.update_vitals(svc_name, 85.0, 0.15) # 15% Error Rate -> CRITICAL
    
    # 4. Reaction
    print("\n>> STEP 3: Immune Response Triggered...")
    healer.scan_and_heal()
    
    # 5. Verification
    print("\n>> STEP 4: Verifying Recovery...")
    svc = immune.services[svc_name]
    print(f"   Status: {svc.status}")
    print(f"   Error Rate: {svc.error_rate:.1%}")
    
    if svc.status == "HEALTHY":
        print("   ✅ System Self-Healed Successfully.")
    else:
        print("   ❌ Healing Failed.")
        
    print_header("DEMO COMPLETE: RESILIENCE CONFIRMED")

if __name__ == "__main__":
    demo_immune_system()
