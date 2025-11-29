import PricingService from '../backend/services/pricingService.js';

async function runTest() {
    console.log("--- Testing Pricing Service ---");

    // 1. Define Sample Simulation Result
    const simResult = {
        "energy_j": 5000,
        "time_s": 300,
        "avg_power_w": 120
    };

    try {
        // 2. Call Service
        console.log("Calculating Price...");
        const result = await PricingService.calculatePrice(simResult);
        console.log("Result:", result);

        // 3. Verify Logic
        // Energy: 5000 * 0.00005 = 0.25
        // Time: 300 * 0.008 = 2.40
        // Material: (5000/100) * 0.05 = 2.50
        // Total: 5.15

        const expectedPrice = 5.15;
        const tolerance = 0.1;

        if (Math.abs(result.total_price - expectedPrice) < tolerance) {
            console.log(`✅ Total Price correct (approx $${expectedPrice}).`);
        } else {
            console.error(`❌ Total Price incorrect. Expected $${expectedPrice}, got $${result.total_price}`);
            process.exit(1);
        }

        if (result.breakdown.risk_multiplier === 1.0) {
            console.log("✅ Risk Multiplier correct (Base).");
        } else {
            console.error("❌ Risk Multiplier incorrect.");
            process.exit(1);
        }

        console.log("✅ Pricing Engine Verified.");

    } catch (err) {
        console.error("❌ Test Failed:", err);
        process.exit(1);
    }
}

runTest();
