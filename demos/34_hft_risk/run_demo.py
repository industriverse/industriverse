import sys
import os
import time
import random

# Add project root to path
sys.path.append(os.getcwd())

from src.thermodynamic_layer.signal_processing import UniversalNormalizer

def run():
    print("\n" + "="*60)
    print(" DEMO 34: HFT RISK ENGINE")
    print("="*60 + "\n")

    normalizer = UniversalNormalizer()

    print("Monitoring Trading Algo: STRATEGY_ALPHA_1...")
    
    # Simulate trade volumes
    volumes = [1000, 5000, 20000, 1000000, 50000000] # Exponential growth
    
    for vol in volumes:
        time.sleep(0.5)
        print(f"Trade Volume: {vol} shares")
        
        # Normalize to thermodynamic risk score (0-1)
        risk_score = normalizer.normalize(vol, "finance")
        print(f"  -> Thermodynamic Risk Score: {risk_score:.4f}")
        
        if risk_score > 0.8:
            print("  🚨 CRITICAL RISK: Circuit Breaker Triggered!")
            print("  -> Trading Halted.")
            break
        else:
            print("  ✅ Risk Acceptable.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: MARKET STABILIZED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
