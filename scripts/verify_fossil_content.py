from src.scf.dataloading.fossil_streamer import FossilStreamer
import json

VAULT_PATH = "/Volumes/Expansion/fossil_vault"

def verify_content():
    print(f"🔍 Verifying content from {VAULT_PATH}...")
    streamer = FossilStreamer(VAULT_PATH, batch_size=1, max_files=1)
    
    # Manually iterate to get the raw fossil data (bypassing the tensor conversion for inspection if possible, 
    # but FossilStreamer yields tensors. I should check the raw file reading logic or just trust the tensor extraction 
    # if I can't easily access raw dicts from the iterator. 
    # Actually, let's just read the first file manually using the SAME logic as streamer to be sure.)
    
    if not streamer.files:
        print("❌ No files found!")
        return

    first_file = streamer.files[0]
    print(f"   Reading first file: {first_file}")
    
    with open(first_file, 'r') as f:
        for line in f:
            try:
                fossil = json.loads(line)
                print("\n✅ Fossil Sample Found:")
                print(f"   ID: {fossil.get('id')}")
                print(f"   Meta Keys: {list(fossil.get('meta', {}).keys())}")
                
                thermo = fossil.get('meta', {}).get('thermodynamics', {})
                print(f"   Thermodynamics: {thermo}")
                
                if 'temperature_c' in thermo and 'entropy_rate' in thermo:
                    print("   ✨ Physics Data Confirmed (Temp & Entropy present)")
                else:
                    print("   ⚠️ Missing Physics Fields!")
                
                break # Only need one
            except Exception as e:
                print(f"   ❌ Error parsing line: {e}")

if __name__ == "__main__":
    verify_content()
