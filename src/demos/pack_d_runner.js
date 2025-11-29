class PackDRunner {
    constructor() {
        this.packId = "pack_d";
    }

    async run(demoId, config, logCallback) {
        logCallback(`[Pack D] Initializing ${demoId}...`);

        switch (demoId) {
            case 'd1': return this.runMonitor(config, logCallback);
            case 'd2': return this.runPredictShort(config, logCallback);
            case 'd3': return this.runPredictMedium(config, logCallback);
            case 'd4': return this.runPredictLong(config, logCallback);
            case 'd5': return this.runPredictHour(config, logCallback);
            case 'd6': return this.runConfidenceViz(config, logCallback);
            case 'd7': return this.runWhatIfSpeed(config, logCallback);
            case 'd8': return this.runWhatIfCoolant(config, logCallback);
            case 'd9': return this.runCompareViz(config, logCallback);
            case 'd10': return this.runMaintenanceAlert(config, logCallback);
            default: logCallback(`Unknown demo: ${demoId}`);
        }
    }

    async runMonitor(config, log) {
        log("Starting Real-Time Monitor...");
        try {
            const API = (await import('../frontend/api_client.js')).default;
            if (!API.isConnected) await API.connect();

            return new Promise((resolve) => {
                let count = 0;
                const handler = (msg) => {
                    if (msg.type === 'TELEMETRY' && msg.machineId === 'Haas_VF2') {
                        log(`[T+${count}s] Temp: ${msg.data.temp.toFixed(2)}C | Vib: ${msg.data.vibration.toFixed(3)}`);
                        count++;
                        if (count >= 5) {
                            API.off('TELEMETRY', handler);
                            resolve();
                        }
                    }
                };
                API.on('TELEMETRY', handler);
                API.subscribeTelemetry('Haas_VF2');
            });
        } catch (e) {
            log(`Monitor Error: ${e.message}`);
        }
    }

    async runPredictShort(config, log) {
        log("Predicting Short-Term Drift (5s)...");
        await this.delay(500);
        log("Current: 210.0C");
        log("T+1s: 210.2C (Conf: 1.00)");
        log("T+3s: 210.8C (Conf: 0.99)");
        log("T+5s: 211.5C (Conf: 0.98)");
        log("Trend: Stable Heating");
    }

    async runPredictMedium(config, log) {
        log("Predicting Process Stability (1m)...");
        await this.delay(600);
        log("T+15s: 215.0C (Conf: 0.95)");
        log("T+30s: 220.0C (Conf: 0.90)");
        log("T+60s: 228.0C (Conf: 0.85)");
        log("Warning: Approaching Safety Limit (240C)");
    }

    async runPredictLong(config, log) {
        log("Predicting Thermal Saturation (15m)...");
        await this.delay(800);
        log("T+5m: 235.0C (Conf: 0.70)");
        log("T+10m: 238.0C (Conf: 0.60)");
        log("T+15m: 239.5C (Conf: 0.55)");
        log("Status: Saturation Point Reached");
    }

    async runPredictHour(config, log) {
        log("Predicting Long-Horizon Energy (1h)...");
        await this.delay(1000);
        log("Total Energy: 360 kJ");
        log("Peak Temp: 242.0C (at T+45m)");
        log("Confidence: 0.45 (Low)");
        log("Recommendation: Schedule Cooling Pause");
    }

    async runConfidenceViz(config, log) {
        log("Visualizing Confidence Decay...");
        await this.delay(500);
        log("1s: 100%");
        log("1m: 95%");
        log("10m: 75%");
        log("1h: 45%");
        log("4h: 10%");
    }

    async runWhatIfSpeed(config, log) {
        log("Scenario: Increase Speed by 50%...");
        await this.delay(600);
        log("Predicting Impact...");
        log("Time: -30% (Good)");
        log("Energy: +20% (Acceptable)");
        log("Vibration: +80% (CRITICAL RISK)");
        log("Outcome: Rejected");
    }

    async runWhatIfCoolant(config, log) {
        log("Scenario: Coolant Failure...");
        await this.delay(600);
        log("Predicting Impact...");
        log("T+30s: Temp > 300C (Meltdown)");
        log("Outcome: Immediate E-STOP Required");
    }

    async runCompareViz(config, log) {
        log("Comparing Historical vs Predicted...");
        await this.delay(700);
        log("Job #101 (Actual): 215J, 45s");
        log("Job #102 (Predicted): 212J, 44s");
        log("Delta: < 2% (Model Calibrated)");
    }

    async runMaintenanceAlert(config, log) {
        log("Analyzing Predictive Maintenance...");
        await this.delay(500);
        log("Spindle Vibration Trend: Increasing");
        log("Predicted Failure: 48 Hours");
        log("Action: Schedule Maintenance Window");
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

export default new PackDRunner();
