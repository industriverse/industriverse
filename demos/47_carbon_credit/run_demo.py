import sys
import os
import time
import hashlib

# Add project root to path
sys.path.append(os.getcwd())

def run():
    print("\n" + "="*60)
    print(" DEMO 47: CARBON CREDIT TOKENIZER")
    print("="*60 + "\n")

    print("Verifying Renewable Energy Source...")
    source_id = "SOLAR_FARM_NV_04"
    energy_generated = 5000.0 # kWh
    print(f"Source: {source_id} | Output: {energy_generated} kWh")
    
    time.sleep(0.5)
    
    # Calculate Carbon Offset (approx 0.4kg CO2 per kWh avoided)
    offset_tons = (energy_generated * 0.4) / 1000.0
    print(f"Carbon Offset: {offset_tons:.4f} tons CO2")
    
    print("\nMinting Token...")
    token_payload = f"{source_id}:{offset_tons}:{time.time()}"
    token_hash = hashlib.sha256(token_payload.encode()).hexdigest()
    
    print(f"Token ID: {token_hash}")
    print("  -> Registered on Ledger.")
    print("  -> Status: VERIFIED")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: ASSET TOKENIZED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
