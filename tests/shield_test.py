import sys
import os
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shield.threat_identifier import ThreatIdentifier

def test_shield():
    print("\n--- Testing AI Shield v3 Core ---")
    shield = ThreatIdentifier()
    
    # Case 1: Sanitizable Threat (High RPM)
    print("\n[Case 1] High RPM (Sanitizable)")
    glyphs_safe = ["⊸C", "⊽0.5"]
    bytecode_unsafe = [{"op": "OP_SPINDLE", "params": {"rpm": 20000}}]
    
    result_1 = shield.scan_plan(glyphs_safe, bytecode_unsafe)
    
    if result_1['safe']:
        print("✅ Plan marked Safe (Sanitized).")
    else:
        print(f"❌ Plan marked Unsafe: {result_1['risks']}")
        
    if "Sanitized" in result_1['risks'][0]:
        print("✅ Sanitization logged.")
    else:
        print("❌ Sanitization NOT logged.")
        
    clamped_rpm = result_1['mitigated_bytecode'][0]['params']['rpm']
    if clamped_rpm == 12000:
        print("✅ RPM Clamped to 12000.")
    else:
        print(f"❌ RPM NOT Clamped: {clamped_rpm}")

    # Case 2: Critical Threat (Forbidden Glyph Sequence)
    print("\n[Case 2] Forbidden Sequence (Critical)")
    glyphs_unsafe = ["⊽0.9", "⊿5P"]
    
    result_2 = shield.scan_plan(glyphs_unsafe, None)
    
    if not result_2['safe']:
        print("✅ Plan marked Unsafe.")
    else:
        print("❌ Plan marked Safe (Should be Unsafe).")
        
    if "Hazard Detected" in result_2['risks'][0] or "Safety Violation" in result_2['risks'][0]:
        print("✅ Hazard logged.")
    else:
        print(f"❌ Hazard NOT logged: {result_2['risks']}")

if __name__ == "__main__":
    test_shield()
