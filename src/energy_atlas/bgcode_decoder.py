import struct
import os
from typing import Dict, Any

class BGCodeDecoder:
    """
    Decodes Binary G-code (.bgcode) files.
    
    Structure:
    - Magic: 'GCDE' (4 bytes)
    - Version: 4 bytes
    - Header Size: 2 bytes (uint16) - This is a guess, usually there's a size field.
      Actually, looking at the dump, it seems to be variable length text terminated by null or specific byte.
      We will use a robust search for the text block.
    """
    
    def __init__(self):
        self.header = {}
        
    def decode_header(self, filepath: str) -> Dict[str, Any]:
        """
        Extract metadata from the file header.
        """
        file_size = os.path.getsize(filepath)
        metadata = {"file_size": file_size}
        
        with open(filepath, 'rb') as f:
            # 1. Magic Bytes
            magic = f.read(4)
            if magic != b'GCDE':
                raise ValueError(f"Invalid Magic Bytes: {magic}")
            
            # 2. Read Header Block
            # We'll read 4KB and split by newlines/nulls to find key=val pairs
            f.seek(0)
            head_data = f.read(4096)
            
            # Attempt to decode as ASCII/UTF-8, ignoring errors
            text_block = head_data.decode('utf-8', errors='ignore')
            
            # Parse Key-Value pairs
            lines = text_block.split('\n')
            for line in lines:
                line = line.strip()
                # Stop if we hit binary garbage (non-printable)
                if not line or len(line) > 100: # Heuristic
                    continue
                    
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    
                    # Clean up value
                    val = val.replace('"', '')
                    
                    # Try to convert to number
                    try:
                        if '.' in val:
                            val = float(val)
                        else:
                            val = int(val)
                    except ValueError:
                        pass
                        
                    metadata[key] = val
                    
        return metadata

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python bgcode_decoder.py <file>")
        sys.exit(1)
    
    decoder = BGCodeDecoder()
    try:
        meta = decoder.decode_header(sys.argv[1])
        print(json.dumps(meta, indent=2))
    except Exception as e:
        print(f"Error: {e}")
