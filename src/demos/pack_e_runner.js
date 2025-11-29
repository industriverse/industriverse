class PackERunner {
    constructor() {
        this.packId = "pack_e";
    }

    async run(demoId, config, logCallback) {
        logCallback(`[Pack E] Initializing ${demoId}...`);

        switch (demoId) {
            case 'e1': return this.runGrandLoop(config, logCallback);
            case 'e2': return this.runBiddingViz(config, logCallback);
            case 'e3': return this.runLearningViz(config, logCallback);
            case 'e4': return this.runPricingViz(config, logCallback);
            case 'e5': return this.runOrchestration(config, logCallback);
            case 'e6': return this.runRecovery(config, logCallback);
            case 'e7': return this.runSupplyChain(config, logCallback);
            case 'e8': return this.runOptimization(config, logCallback);
            case 'e9': return this.runShowstopper(config, logCallback);
            case 'e10': return this.runShutdown(config, logCallback);
            default: logCallback(`Unknown demo: ${demoId}`);
        }
    }

    async runGrandLoop(config, log) {
        log(`Starting End-to-End Job: ${config.job}...`);
        await this.delay(500);
        log("1. Intent: 'Make a bracket' -> ⊸C ⊽0.5");
        await this.delay(500);
        log("2. Dispatch: Selected 'Precision Miller Alpha'");
        await this.delay(500);
        log("3. Safety: Certified Safe (Risk: Low)");
        await this.delay(500);
        log("4. Execution: Printing Layer 1/50...");
        await this.delay(500);
        log("Job Complete. Cost: $2.50");
    }

    async runBiddingViz(config, log) {
        log("Broadcasting Intent to Capsule Network...");
        await this.delay(600);
        log("Received 3 Bids:");
        log("1. Precision Miller Alpha (Score: 1.0) - $2.50");
        log("2. Fast Printer Beta (Score: 0.8) - $1.80");
        log("3. Heavy Duty Gamma (Score: 0.5) - $5.00");
        log("Winner: Precision Miller Alpha");
    }

    async runLearningViz(config, log) {
        log("Analyzing Operator Behavior...");
        await this.delay(500);
        log("Detected Override: Reduced Speed (-20%)");
        log("Updating Profile: 'Conservative Style'");
        log("Future Prediction: Will likely reduce speed for Job #105");
    }

    async runPricingViz(config, log) {
        log("Negotiating Thermodynamic Contract...");
        await this.delay(500);
        log("Base Energy: 500kJ");
        log("Spot Price: $0.10/kJ");
        log("Risk Multiplier: 1.0x");
        log("Final Quote: $50.00");
    }

    async runOrchestration(config, log) {
        log("Orchestrating Multi-Machine Workflow...");
        await this.delay(800);
        log("Step 1: CNC Mill (Capsule A) - Complete");
        log("Step 2: Robot Arm (Capsule B) - Transferring...");
        log("Step 3: Heat Treat (Capsule C) - Heating...");
        log("Workflow Status: Active");
    }

    async runRecovery(config, log) {
        log("Simulating Error State...");
        await this.delay(500);
        log("Error: Filament Jam (Capsule A)");
        log("Rerouting Job...");
        log("Selected Backup: Capsule D (Score: 0.9)");
        log("Recovery Successful. Delay: +2m");
    }

    async runSupplyChain(config, log) {
        log("Checking Material Inventory...");
        await this.delay(400);
        log("PLA: 50kg (Sufficient)");
        log("TPU: 2kg (Low - Reordering)");
        log("Order Placed: 10kg TPU (ETA: 2 Days)");
    }

    async runOptimization(config, log) {
        log("Optimizing Global Energy Consumption...");
        await this.delay(600);
        log("Current Load: 50kW");
        log("Strategy: Shift Heating to Off-Peak");
        log("New Load: 35kW (-30%)");
        log("Savings: $150/day");
    }

    async runShowstopper(config, log) {
        log("Initiating Investor Demo Sequence...");
        await this.delay(1000);
        log("1. The Hook: 'Make a drone frame'");
        await this.delay(1000);
        log("2. The Brain: Physics Intent Vectorized");
        await this.delay(1000);
        log("3. The Shield: Threat Neutralized");
        await this.delay(1000);
        log("4. The Twin: Thermal Drift Corrected");
        await this.delay(1000);
        log("5. The Close: Part Ejected. 'Welcome to the Industriverse'");
    }

    async runShutdown(config, log) {
        log("Generating Final Report...");
        await this.delay(500);
        log("Total Jobs: 50");
        log("Total Energy: 1.2 GJ");
        log("Total Value: $5,000");
        log("System Shutdown Sequence Initiated...");
        log("Goodbye.");
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

export default new PackERunner();
