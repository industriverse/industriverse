from .intent_vectorizer import IntentVectorizer

class GlyphIntentFuser:
    """
    Fuses the abstract 'Intent Vector' with the concrete 'Glyph Grammar'.
    Translates physics desires (Vector) into LCODE modifiers.
    """
    def __init__(self):
        self.vectorizer = IntentVectorizer()
        
        # Mapping from Vector Space regions to Glyph Modifiers
        # (Simplified rule-based mapping for now)
        self.modifier_map = {
            "lightweight": {"glyph": "⊽0.1", "desc": "Fine Mill (Mass Reduction)"},
            "fast": {"glyph": "⊽0.5", "desc": "Rough Mill (Speed)"},
            "strong": {"glyph": "⊼13E", "desc": "EUV Hardening (Integrity)"},
            "precision": {"glyph": "⊸C", "desc": "Optical Alignment (Accuracy)"}
        }

    def fuse(self, prompt):
        """
        Input: "Make a lightweight bracket"
        Output: { 
            base_recipe: "bracket", 
            modifiers: ["⊽0.1"], 
            reasoning: "Vector indicates high mass-reduction intent." 
        }
        """
        intent = self.vectorizer.vectorize(prompt)
        keywords = intent['keywords']
        
        fused_plan = {
            "original_prompt": prompt,
            "intent_vector": intent['vector'],
            "base_recipe": None,
            "modifiers": [],
            "reasoning": []
        }
        
        # 1. Identify Base Recipe (Noun)
        for kw in keywords:
            if kw in ["bracket", "gear", "housing"]: # Known objects
                fused_plan["base_recipe"] = kw
                fused_plan["reasoning"].append(f"Identified base object: {kw}")
        
        # 2. Map Modifiers (Adjectives)
        for kw in keywords:
            if kw in self.modifier_map:
                mod = self.modifier_map[kw]
                fused_plan["modifiers"].append(mod["glyph"])
                fused_plan["reasoning"].append(f"Mapped '{kw}' to modifier {mod['glyph']} ({mod['desc']})")
                
        return fused_plan

if __name__ == "__main__":
    fuser = GlyphIntentFuser()
    print(fuser.fuse("Make a lightweight strong bracket"))
