import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.thermodynamic_layer.signal_processing import UniversalNormalizer

def run():
    print("\n" + "="*60)
    print(" DEMO 26: UNIVERSAL NORMALIZER WITH ADAPTERS")
    print("="*60 + "\n")

    normalizer = UniversalNormalizer()

    print("--- Domain 1: Industrial (Steel Mill) ---")
    raw_temp = 1500.0 # Celsius
    norm_val = normalizer.normalize(raw_temp, "industrial", context={"max_temp": 1800})
    print(f"Raw Temp: {raw_temp}C -> Normalized: {norm_val:.4f} (Thermodynamic Scale)")

    print("\n--- Domain 2: Biological (Neurotransmitter) ---")
    raw_conc = 45.0 # nM
    norm_val = normalizer.normalize(raw_conc, "bio", context={"max_conc": 100})
    print(f"Raw Conc: {raw_conc}nM -> Normalized: {norm_val:.4f} (Thermodynamic Scale)")

    print("\n--- Domain 3: Finance (High Frequency Trading) ---")
    raw_vol = 1000000 # Shares
    norm_val = normalizer.normalize(raw_vol, "finance")
    print(f"Raw Vol: {raw_vol} -> Normalized: {norm_val:.4f} (Thermodynamic Scale)")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: CROSS-DOMAIN ALIGNMENT")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
