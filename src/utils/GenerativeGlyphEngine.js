import grammar from './glyph_grammar.json' with { type: "json" };
import AIInterpreter from './AIInterpreter.js';

class GenerativeGlyphEngine {
    constructor() {
        this.grammar = grammar;
    }

    /**
     * Generates a Glyph sequence from a natural language prompt.
     * @param {string} prompt - e.g., "Make a lightweight bracket"
     * @returns {Promise<object>} - { glyphs: [], energy_estimate: string, reasoning: string }
     */
    async generate(prompt) {
        const lowerPrompt = prompt.toLowerCase();
        const sequence = [];
        let reasoning = [];

        // 1. Identify Recipe (Noun)
        let recipeKey = null;
        for (const [key, value] of Object.entries(this.grammar.keywords)) {
            if (value.recipe && lowerPrompt.includes(key)) {
                recipeKey = value.recipe;
                reasoning.push(`Identified object: ${key} -> Recipe: ${recipeKey}`);
                break;
            }
        }

        if (!recipeKey) {
            return { error: "Could not identify a valid object to manufacture." };
        }

        // 2. Load Base Recipe
        let currentSequence = [...this.grammar.recipes[recipeKey]];

        // 3. Apply Modifiers (Adjectives)
        for (const [key, value] of Object.entries(this.grammar.keywords)) {
            if (value.modifier && lowerPrompt.includes(key)) {
                reasoning.push(`Applied modifier: ${key} -> ${value.desc}`);

                // Logic: Replace standard operations with optimized ones
                if (key === 'lightweight') {
                    // Replace rough cuts with fine cuts
                    const index = currentSequence.indexOf('⊽0.5');
                    if (index !== -1) {
                        currentSequence[index] = value.glyph; // Swap ⊽0.5 for ⊽0.1
                    }
                } else if (key === 'fast') {
                    // Replace Plasma (Slow) with Rough Mill (Fast)
                    const index = currentSequence.indexOf('⊿5P');
                    if (index !== -1) {
                        currentSequence[index] = value.glyph;
                    }
                }
            }
        }

        // 4. Validate Grammar (Simple Dependency Check)
        // Ensure 'align' (⊸) is present if 'cut' (⊽) is used.
        const hasCut = currentSequence.some(g => g.startsWith('⊽'));
        const hasAlign = currentSequence.some(g => g.startsWith('⊸'));

        if (hasCut && !hasAlign) {
            currentSequence.unshift('⊸C'); // Auto-fix
            reasoning.push("Auto-corrected: Added Alignment step.");
        }

        // 5. Thermodynamic Estimation & Pricing
        let totalEnergy = 0;
        let totalPrice = 0;

        for (const glyph of currentSequence) {
            const result = await AIInterpreter.translate(glyph);
            totalEnergy += parseFloat(result.energy) || 0;
            totalPrice += parseFloat(result.price.replace('$', '')) || 0;
        }

        return {
            glyphs: currentSequence,
            energy_estimate: `${totalEnergy.toFixed(1)}J`,
            price: `$${totalPrice.toFixed(2)}`,
            reasoning: reasoning.join(' | ')
        };
    }
}

export default new GenerativeGlyphEngine();
