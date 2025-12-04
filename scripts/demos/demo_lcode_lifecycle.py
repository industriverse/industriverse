import sys
import os
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path.cwd()))

from src.lcode.compiler import LCODECompiler
from src.lcode.glyph_registry import GlyphRegistry

def demo_lcode():
    print("🔣 Starting LCODE Lifecycle Demo...")
    print("===================================")
    
    # 1. Registry Inspection
    print("\n--- Glyph Registry ---")
    registry = GlyphRegistry()
    for glyph in registry.list_all():
        print(f" {glyph.symbol} : {glyph.name} ({glyph.description})")

    # 2. Compilation Scenario
    # "Align Center, then Mill 0.5mm, then Repeat 3 times"
    raw_script = ["⊸C", "⊽0.5", "⋙3"]
    print(f"\n--- Compiling Script: {raw_script} ---")
    
    compiler = LCODECompiler()
    bytecode = compiler.compile(raw_script)
    
    # 3. Output Analysis
    if bytecode['valid']:
        print("✅ Compilation Successful.")
        print(f"   Safety Hash: {bytecode['safety_hash']}")
        print("\n   [Industrial Bytecode]")
        print(json.dumps(bytecode['ops'], indent=4))
    else:
        print("❌ Compilation Failed.")
        print(bytecode['errors'])

    # 4. Error Handling Test
    print("\n--- Error Handling Test ---")
    bad_script = ["⊽99.9", "???"] # Depth too high, unknown glyph
    print(f"   Input: {bad_script}")
    bad_result = compiler.compile(bad_script)
    print(f"   Valid: {bad_result['valid']}")
    # Note: Our simple validator might return None for params but not fail the whole op unless strictly enforced.
    # Let's check the ops to see if params were parsed.
    for op in bad_result['ops']:
        print(f"   Op: {op['symbol']} -> Params: {op['params']} (None means invalid)")
    if bad_result['errors']:
        print(f"   Errors: {bad_result['errors']}")

    print("\n===================================")
    print("✅ LCODE Demo Complete.")

if __name__ == "__main__":
    demo_lcode()
