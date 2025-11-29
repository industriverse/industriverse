class GlyphSafetyAnalyzer:
    """
    AI Shield v3 - Gate 1: Glyph Static Analysis.
    Checks LCODE sequences for logical hazards before they are compiled to bytecode.
    """
    def __init__(self):
        self.forbidden_sequences = [
            ["⊽0.9", "⊿5P"], # Deep cut + Fast move = Tool Breakage Risk
            ["⊻", "⊸C"]      # Verify BEFORE Align = Logical Error
        ]
        self.max_cut_depth = 0.8 # mm

    def analyze(self, glyphs):
        """
        Input: List of glyph strings ['⊸C', '⊽0.5']
        Output: { safe: bool, issues: [] }
        """
        issues = []
        
        # 1. Parameter Bounds Check
        for g in glyphs:
            if g.startswith("⊽"): # Cut operation
                try:
                    depth = float(g[1:])
                    if depth > self.max_cut_depth:
                        issues.append(f"Safety Violation: Cut depth {depth}mm exceeds limit {self.max_cut_depth}mm.")
                except ValueError:
                    pass # Ignore non-numeric parameters for now

        # 2. Sequence Hazard Check
        # Simple sliding window or pair check
        glyph_str = " ".join(glyphs)
        for seq in self.forbidden_sequences:
            seq_str = " ".join(seq)
            if seq_str in glyph_str:
                issues.append(f"Hazard Detected: Forbidden sequence '{seq_str}' found.")

        return {
            "safe": len(issues) == 0,
            "issues": issues
        }

if __name__ == "__main__":
    analyzer = GlyphSafetyAnalyzer()
    # Test Safe
    print(analyzer.analyze(["⊸C", "⊽0.5", "⊻"]))
    # Test Unsafe
    print(analyzer.analyze(["⊽0.9", "⊿5P"]))
