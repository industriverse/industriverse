import TelemetryHub from '../src/telemetry/telemetry_hub.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runTest() {
    console.log("--- Testing Telemetry Hub ---");

    // 1. Ingest Data
    const machineId = "Test_Machine_001";
    console.log(`Ingesting data for ${machineId}...`);

    for (let i = 0; i < 10; i++) {
        TelemetryHub.ingest(machineId, {
            temp: 20 + i,
            vibration: 0.01 * i,
            timestamp: Date.now() / 1000
        });
    }

    // 2. Force Flush
    console.log("Flushing buffer...");
    // Override logger path to be relative to CWD for testing if needed, 
    // but the class uses absolute path based on its location, which is correct.

    try {
        await TelemetryHub.flushAll();
        console.log("✅ Flush completed.");
        process.exit(0);
    } catch (err) {
        console.error("❌ Flush failed:", err);
        process.exit(1);
    }
}

runTest();
