import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.energy_atlas.bgcode_decoder import BGCodeDecoder

def test_decoder(filepath):
    print(f"Testing Decoder on: {filepath}")
    decoder = BGCodeDecoder()
    
    try:
        metadata = decoder.decode_header(filepath)
        print("\n--- Decoded Metadata ---")
        for k, v in metadata.items():
            print(f"{k}: {v}")
            
        if not metadata:
            print("FAILED: No metadata extracted.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_decoder.py <bgcode_file>")
        sys.exit(1)
    
    test_decoder(sys.argv[1])
