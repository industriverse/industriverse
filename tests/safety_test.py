import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.safety.glyph_safety import GlyphSafetyAnalyzer
from src.safety.bytecode_sanitizer import BytecodeSanitizer

def test_glyph_safety():
    print("\n--- Testing Glyph Safety Analyzer ---")
    analyzer = GlyphSafetyAnalyzer()
    
    # Case 1: Safe Sequence
    safe_seq = ["⊸C", "⊽0.5", "⊻"]
    result = analyzer.analyze(safe_seq)
    if result['safe']:
        print("✅ Safe sequence passed.")
    else:
        print(f"❌ Safe sequence failed: {result['issues']}")

    # Case 2: Unsafe Cut Depth
    unsafe_cut = ["⊽1.5"] # Limit is 0.8
    result = analyzer.analyze(unsafe_cut)
    if not result['safe'] and "exceeds limit" in result['issues'][0]:
        print("✅ Unsafe cut depth detected.")
    else:
        print(f"❌ Unsafe cut depth NOT detected: {result}")

    # Case 3: Forbidden Sequence
    forbidden = ["⊽0.9", "⊿5P"]
    result = analyzer.analyze(forbidden)
    # Check if ANY issue contains the forbidden sequence message
    found_forbidden = any("Forbidden sequence" in issue for issue in result['issues'])
    
    if not result['safe'] and found_forbidden:
        print("✅ Forbidden sequence detected.")
    else:
        print(f"❌ Forbidden sequence NOT detected: {result}")

def test_bytecode_sanitizer():
    print("\n--- Testing Bytecode Sanitizer ---")
    sanitizer = BytecodeSanitizer()
    
    # Case 1: Forbidden Op
    program = [{"op": "OP_OVERRIDE_SAFETY"}]
    result = sanitizer.sanitize(program)
    if len(result['sanitized_program']) == 0 and "Removed forbidden op" in result['modifications'][0]:
        print("✅ Forbidden op removed.")
    else:
        print(f"❌ Forbidden op NOT removed: {result}")

    # Case 2: Parameter Clamping
    program = [{"op": "OP_SPINDLE", "params": {"rpm": 20000}}] # Limit 12000
    result = sanitizer.sanitize(program)
    clamped_rpm = result['sanitized_program'][0]['params']['rpm']
    if clamped_rpm == 12000:
        print("✅ RPM clamped correctly.")
    else:
        print(f"❌ RPM NOT clamped: {clamped_rpm}")

if __name__ == "__main__":
    test_glyph_safety()
    test_bytecode_sanitizer()
