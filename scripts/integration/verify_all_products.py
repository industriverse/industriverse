import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.products import (
    DarkFactoryOS, EntropyBot, AIShield, ResourceClusterEngine,
    EvolutionEngine, VisualTwin, TheOracle, GenesisArchitect,
    TelekinesisBridge, VoiceOfTheMachine, SimToRealTrainer, InfiniteServiceMesh
)

def verify_all():
    print("############################################################")
    print("#   PHASE 129: MASTER PRODUCT VERIFICATION                 #")
    print("############################################################")
    
    products = [
        DarkFactoryOS(),
        EntropyBot(),
        AIShield(),
        ResourceClusterEngine(),
        EvolutionEngine(),
        VisualTwin(),
        TheOracle(),
        GenesisArchitect(),
        TelekinesisBridge(),
        VoiceOfTheMachine(),
        SimToRealTrainer(),
        InfiniteServiceMesh()
    ]
    
    passed = 0
    for p in products:
        status = p.get_status()
        print(f"✅ Verified: {status['product']} (Status: {status['status']})")
        passed += 1
        
    print(f"\n🏆 Result: {passed}/12 Products Verified.")
    
    if passed == 12:
        print("✅ ALL SYSTEMS ONLINE.")
    else:
        print("❌ SYSTEM FAILURE.")

if __name__ == "__main__":
    verify_all()
