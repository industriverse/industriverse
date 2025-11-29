class PackBRunner {
    constructor() {
        this.packId = "pack_b";
    }

    async run(demoId, config, logCallback) {
        logCallback(`[Pack B] Initializing ${demoId}...`);

        switch (demoId) {
            case 'b1': return this.runTextToGlyph(config, logCallback);
            case 'b2': return this.runModifierLightweight(config, logCallback);
            case 'b3': return this.runModifierPrecision(config, logCallback);
            case 'b4': return this.runGrammarCheck(config, logCallback);
            case 'b5': return this.runAmbiguity(config, logCallback);
            case 'b6': return this.runIntentChain(config, logCallback);
            case 'b7': return this.runSafetyConstraint(config, logCallback);
            case 'b8': return this.runPricingPreview(config, logCallback);
            case 'b9': return this.runPlanCompare(config, logCallback);
            case 'b10': return this.runFeedbackLoop(config, logCallback);
            default: logCallback(`Unknown demo: ${demoId}`);
        }
    }

    async runTextToGlyph(config, log) {
        log(`Processing Prompt: "${config.prompt}"...`);
        await this.delay(600);
        log("Intent Vector: [0.8, 0.1, 0.4]");
        log("Generated Glyphs: ⊸C ⊽0.5 ⌬PLA");
    }

    async runModifierLightweight(config, log) {
        log(`Applying Modifier: Lightweight...`);
        await this.delay(400);
        log("Detected Keyword: 'Lightweight'");
        log("Mapped to LCODE: ⊽0.1 (Infill Density 10%)");
        log("Thermodynamic Impact: -40% Mass, -30% Energy");
    }

    async runModifierPrecision(config, log) {
        log(`Applying Modifier: Precision...`);
        await this.delay(400);
        log("Detected Keyword: 'Precision'");
        log("Mapped to LCODE: ⊸C (Optical Alignment)");
        log("Thermodynamic Impact: +20% Time, +15% Energy");
    }

    async runGrammarCheck(config, log) {
        log(`Validating LCODE: ${config.code}...`);
        await this.delay(300);
        log("Syntax Check: PASS");
        log("Semantic Check: PASS");
        log("Thermodynamic Check: PASS");
        log("Status: Valid Sequence");
    }

    async runAmbiguity(config, log) {
        log(`Resolving Ambiguity: "${config.prompt}"...`);
        await this.delay(600);
        log("Ambiguous Term: 'Fast'");
        log("Option A: High Feed Rate (⊳3000) - High Risk");
        log("Option B: Low Infill (⊽0.1) - Low Strength");
        log("Selected Option A (Context: Prototyping)");
    }

    async runIntentChain(config, log) {
        log(`Chaining Intents: "${config.prompt}"...`);
        await this.delay(800);
        log("Step 1: Roughing Pass (⊳5000 ⊽0.5)");
        log("Step 2: Finish Pass (⊳1000 ⊸C)");
        log("Sequence Compiled Successfully.");
    }

    async runSafetyConstraint(config, log) {
        log(`Injecting Constraint: "${config.constraint}"...`);
        await this.delay(500);
        log("Constraint Active: Max Temp < 220C");
        log("Adjusting Plan...");
        log("Original: 230C (TPU)");
        log("Modified: 215C (PLA+)");
        log("Constraint Satisfied.");
    }

    async runPricingPreview(config, log) {
        log("Estimating Exergy Price...");
        await this.delay(700);
        log("Energy: 450kJ ($0.12)");
        log("Material: 50g ($1.50)");
        log("Entropy Risk: Low ($0.05)");
        log("Total Quote: $1.67");
    }

    async runPlanCompare(config, log) {
        log("Comparing Alternatives...");
        await this.delay(1000);
        log("Plan A (Speed): 12m, $2.00, Risk: High");
        log("Plan B (Quality): 45m, $5.00, Risk: Low");
        log("Recommendation: Plan B (Safety Priority)");
    }

    async runFeedbackLoop(config, log) {
        log("Processing User Feedback...");
        log("User: 'Too expensive'");
        await this.delay(500);
        log("Re-optimizing for Cost...");
        log("New Plan: Reduced Infill (20% -> 10%)");
        log("New Price: $1.20 (-40%)");
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

export default new PackBRunner();
