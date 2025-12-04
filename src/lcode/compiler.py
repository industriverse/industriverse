import hashlib
import json
import time
from typing import List, Dict, Any
from .glyph_registry import GlyphRegistry

class LCODECompiler:
    """
    Translates LCODE Glyphs -> Industrial Bytecode (IB).
    """
    def __init__(self):
        self.registry = GlyphRegistry()

    def compile(self, glyphs: List[str]) -> Dict[str, Any]:
        """
        Compiles a list of glyph strings (e.g., ["⊸C", "⊽0.5"]) into an execution plan.
        """
        ops = []
        errors = []
        
        for g_str in glyphs:
            if not g_str:
                continue
                
            # Parse Symbol vs Parameter
            # Assuming 1-char symbol for now, but could be more complex
            symbol_char = g_str[0]
            param_str = g_str[1:] if len(g_str) > 1 else None
            
            definition = self.registry.get(symbol_char)
            
            if not definition:
                errors.append(f"Unknown Glyph: {symbol_char}")
                continue
                
            # Validate Parameter
            parsed_param = self._validate_param(definition, param_str)
            if parsed_param is None and definition.param_type != 'none':
                 # It might be valid if param is optional, but for now let's assume strict
                 pass 

            op = {
                "op_code": definition.name,
                "symbol": symbol_char,
                "params": parsed_param,
                "raw": g_str
            }
            ops.append(op)

        # Generate Safety Hash (Integrity Check)
        payload = json.dumps(ops, sort_keys=True)
        safety_hash = hashlib.sha256(payload.encode()).hexdigest()

        return {
            "version": "1.0",
            "timestamp": time.time(),
            "ops": ops,
            "errors": errors,
            "safety_hash": safety_hash,
            "valid": len(errors) == 0
        }

    def _validate_param(self, definition, param_str):
        if definition.param_type == 'float':
            try:
                val = float(param_str)
                # Check constraints
                if 'min' in definition.constraints and val < definition.constraints['min']:
                    return None # Error
                if 'max' in definition.constraints and val > definition.constraints['max']:
                    return None # Error
                return val
            except:
                return None
        elif definition.param_type == 'int':
            try:
                return int(param_str)
            except:
                return None
        elif definition.param_type == 'enum':
            if param_str in definition.constraints.get('options', []):
                return param_str
            return None # Invalid option
        return param_str
