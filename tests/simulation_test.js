import SimulationService from '../backend/services/simulationService.js';

async function runTest() {
    console.log("--- Testing Simulation Service ---");

    // 1. Define Sample Bytecode
    // Move 100mm in X at 3000mm/min (50mm/s) -> Should take 2 seconds
    const bytecode = [
        { "op": "OP_MOVE", "params": { "x": 100, "y": 0, "z": 0, "f": 3000 } }
    ];

    try {
        // 2. Call Service
        console.log("Simulating program...");
        const result = await SimulationService.simulate(bytecode);
        console.log("Result:", result);

        // 3. Verify Logic
        const expectedTime = 2.0; // 100 / 50
        const tolerance = 0.1;

        if (Math.abs(result.time_s - expectedTime) < tolerance) {
            console.log("✅ Time calculation correct (approx 2s).");
        } else {
            console.error(`❌ Time calculation incorrect. Expected ${expectedTime}, got ${result.time_s}`);
            process.exit(1);
        }

        if (result.energy_j > 0) {
            console.log(`✅ Energy calculated: ${result.energy_j}J`);
        } else {
            console.error("❌ Energy calculation failed (<= 0).");
            process.exit(1);
        }

        console.log("✅ Simulation Oracle Verified.");

    } catch (err) {
        console.error("❌ Test Failed:", err);
        process.exit(1);
    }
}

runTest();
