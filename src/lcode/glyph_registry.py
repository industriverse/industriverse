from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class GlyphDefinition:
    symbol: str
    name: str
    description: str
    param_type: str  # 'float', 'int', 'enum', 'none'
    constraints: Dict[str, Any]

class GlyphRegistry:
    """
    The Definitive Dictionary of LCODE.
    """
    def __init__(self):
        self._glyphs: Dict[str, GlyphDefinition] = {}
        self._load_standard_library()

    def _load_standard_library(self):
        # Material Removal (Subtractive)
        self.register(GlyphDefinition(
            symbol="⊽",
            name="MILL",
            description="Remove material to specified depth.",
            param_type="float",
            constraints={"min": 0.0, "max": 5.0, "unit": "mm"}
        ))
        
        # Alignment (Metrology)
        self.register(GlyphDefinition(
            symbol="⊸",
            name="ALIGN",
            description="Perform optical or mechanical alignment.",
            param_type="enum",
            constraints={"options": ["C", "TL", "TR", "BL", "BR"]} # Center, TopLeft, etc.
        ))
        
        # Lithography (Additive/Patterning)
        self.register(GlyphDefinition(
            symbol="⊼",
            name="EXPOSE",
            description="Expose photoresist at specified wavelength/energy.",
            param_type="string", # e.g., "13E" for 13.5nm EUV
            constraints={}
        ))
        
        # Control Flow / Safety
        self.register(GlyphDefinition(
            symbol="⊿",
            name="ALERT",
            description="Trigger alert or correction on condition.",
            param_type="string",
            constraints={}
        ))
        
        # Multi-Patterning
        self.register(GlyphDefinition(
            symbol="⋙",
            name="REPEAT",
            description="Repeat previous operation N times.",
            param_type="int",
            constraints={"min": 1, "max": 100}
        ))

    def register(self, definition: GlyphDefinition):
        self._glyphs[definition.symbol] = definition

    def get(self, symbol_char: str) -> Optional[GlyphDefinition]:
        return self._glyphs.get(symbol_char)

    def list_all(self) -> List[GlyphDefinition]:
        return list(self._glyphs.values())
