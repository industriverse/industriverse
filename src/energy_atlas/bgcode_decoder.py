import struct
import re
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
            
            # Extract Metadata Block
            # (Simplified: In real BGCode, this is a structured binary block. 
            # We look for known keys in the header area).
            
            # 1. Filament Used (Material)
            filament_match = re.search(rb'filament used \[cm3\]\x00(.*?)\x00', head_data)
            if filament_match:
                try:
                    metadata['filament_used_cm3'] = float(filament_match.group(1).decode('utf-8', errors='ignore'))
                except: pass

            # 2. Layer Height (Geometry/Precision)
            layer_match = re.search(rb'layer_height\x00(.*?)\x00', head_data)
            if layer_match:
                try:
                    metadata['layer_height_mm'] = float(layer_match.group(1).decode('utf-8', errors='ignore'))
                except: pass

            # 3. Estimated Time
            time_match = re.search(rb'estimated printing time \(normal mode\)\x00(.*?)\x00', head_data)
            if time_match:
                try:
                    metadata['estimated_time_s'] = self._parse_time(time_match.group(1).decode('utf-8', errors='ignore'))
                except: pass

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
