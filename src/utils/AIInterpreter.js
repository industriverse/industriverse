import glyphs from './glyphs.json' with { type: "json" };
import SimulationService from '../../backend/services/simulationService.js';

class AIInterpreter {
    constructor() {
        this.commands = glyphs;
        this.cache = new Map();
    }

    /**
     * Translates a Glyph into a Machine Command with Thermodynamic Checks.
     * @param {string} glyph - The glyph symbol (e.g., "⊼13E")
     * @param {string} machineType - The target machine ID (e.g., "ASML_NXE_3400")
     * @returns {Promise<object>} - { type, cmd, energy, warning? }
     */
    async translate(glyph, machineType = 'default') {
        // 1. Check Cache (Fast Path)
        const cacheKey = `${glyph}:${machineType}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        // 2. Lookup in Vault
        const entry = this.commands[glyph];
        if (!entry) {
            return this.slowTranslate(glyph, machineType);
        }

        // 3. Thermodynamic Simulation (The Grand Synthesis)
        // Query the Energy Atlas for the "Ground Truth" cost
        const simResult = await SimulationService.predictEnergy(glyph);

        // 4. Thermodynamic Autocorrect & Pricing
        let warning = null;
        let energy = simResult.energy || parseFloat(entry.energy_cost) || 0;
        let price = parseFloat(entry.base_price) || 0;

        // Dynamic Pricing: Energy Surcharge (e.g., $0.001 per Joule)
        const energySurcharge = energy * 0.001;
        const totalPrice = (price + energySurcharge).toFixed(2);

        // Threshold Check: If energy > 100J, flag it (Heuristic)
        if (energy > 100.0) {
            warning = `High Energy Alert: ${energy.toFixed(1)}J. Consider optimization.`;
        }

        // 5. Resolve Command
        const cmd = entry[machineType] || entry['default'];
        const result = {
            type: machineType,
            cmd: cmd,
            energy: `${energy.toFixed(1)}J`,
            price: `$${totalPrice}`,
            source: simResult.source || "Vault",
            warning: warning,
            timestamp: Date.now()
        };

        // 6. Cache Result
        this.cache.set(cacheKey, result);
        return result;
    }

    /**
     * Fallback for novel glyphs (simulates Manus AI inference).
     */
    async slowTranslate(glyph, machineType) {
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
