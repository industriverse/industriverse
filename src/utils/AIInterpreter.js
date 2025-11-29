import glyphs from './glyphs.json' with { type: "json" };

class AIInterpreter {
    constructor() {
        this.commands = glyphs;
        this.cache = new Map();
    }

    /**
     * Translates a Glyph into a Machine Command.
     * @param {string} glyph - The glyph symbol (e.g., "⊼13E")
     * @param {string} machineType - The target machine ID (e.g., "ASML_NXE_3400")
     * @returns {object} - { type, cmd, energy }
     */
    translate(glyph, machineType = 'default') {
        // 1. Check Cache
        const cacheKey = `${glyph}:${machineType}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        // 2. Lookup in Vault
        const entry = this.commands[glyph];
        if (!entry) {
            return this.slowTranslate(glyph, machineType);
        }

        // 3. Resolve Command
        const cmd = entry[machineType] || entry['default'];
        const result = {
            type: machineType,
            cmd: cmd,
            energy: entry.energy_cost,
            timestamp: Date.now()
        };

        // 4. Cache Result
        this.cache.set(cacheKey, result);
        return result;
    }

    /**
     * Fallback for novel glyphs (simulates Manus AI inference).
     */
    slowTranslate(glyph, machineType) {
        console.warn(`[Manus AI] Novel glyph detected: ${glyph}. Inferring intent...`);

        // Mock Inference Logic
        if (glyph.startsWith('⋜')) {
            return {
                type: machineType,
                cmd: "QUANTUM_OP_STUB",
                energy: "Unknown",
                inferred: true
            };
        }

        return {
            type: 'error',
            cmd: `Unknown Glyph: ${glyph}`,
            energy: '0J'
        };
    }
}

export default new AIInterpreter();
