import { WebSocket } from 'ws';
import http from 'http';

// Simple test to verify Backend <-> Frontend wiring
// 1. Connects to WS
// 2. Subscribes to Telemetry
// 3. Sends Intent
// 4. Verifies Responses

const PORT = 5001;
const WS_URL = `ws://localhost:${PORT}`;

function testWiring() {
    console.log("--- Testing Phase 70 Wiring ---");

    const ws = new WebSocket(WS_URL);

    ws.on('open', () => {
        console.log("✅ Connected to Backend.");

        // 1. Test Telemetry Subscription
        console.log("[1] Testing Telemetry Subscription...");
        ws.send(JSON.stringify({ type: 'SUBSCRIBE_TELEMETRY', machineId: 'Haas_VF2' }));

        // 2. Test Intent Generation
        console.log("[2] Testing Intent Generation...");
        ws.send(JSON.stringify({ type: 'GENERATE_GLYPHS', prompt: 'Make a strong bracket' }));
    });

    let telemetryReceived = false;
    let intentReceived = false;

    ws.on('message', (data) => {
        const msg = JSON.parse(data);

        if (msg.type === 'TELEMETRY') {
            if (!telemetryReceived) {
                console.log(`✅ Telemetry Received: Temp=${msg.data.temp.toFixed(2)}C`);
                telemetryReceived = true;
            }
        } else if (msg.type === 'GENERATION_RESULT') {
            console.log(`✅ Intent Result Received: ${msg.result.glyphs.join(' ')}`);
            intentReceived = true;
        } else if (msg.type === 'ERROR') {
            console.log(`❌ Error Received: ${msg.message}`);
        }

        if (telemetryReceived && intentReceived) {
            console.log("\n✅ All Wiring Tests Passed.");
            ws.close();
            process.exit(0);
        }
    });

    ws.on('error', (err) => {
        console.error("❌ Connection Error:", err);
        process.exit(1);
    });

    // Timeout
    setTimeout(() => {
        console.log("\n❌ Test Timed Out.");
        if (!telemetryReceived) console.log("   - Telemetry missing");
        if (!intentReceived) console.log("   - Intent result missing");
        process.exit(1);
    }, 10000);
}

testWiring();
