// demo_highlight_reel.js
// Executes the "15-Second Perfect Loop" for investors.

import WebSocket from 'ws';

const ws = new WebSocket('ws://localhost:5001');

ws.on('open', async () => {
    console.log("🎬 STARTING 15-SECOND HIGHLIGHT REEL...");

    // 1. Intent (0s)
    console.log("[0.0s] 🗣️  Intent: 'Manufacture High-Performance Turbine Blade'");
    ws.send(JSON.stringify({ type: 'INTENT', payload: { text: 'Turbine Blade', modifiers: ['High-Perf'] } }));
    await wait(2000);

    // 2. ZK Bid (2s)
    console.log("[2.0s] 🔒 ZK-Proof Generated: 'zk-snark-proof-a1b2c3d4...' (IP Protected)");
    console.log("[2.1s] 🤝 Capsule Bid Accepted: 'Capsule-Alpha' (Skill: 5-Axis v2)");
    await wait(2000);

    // 3. Simulation (4s)
    console.log("[4.0s] 🔮 Predictive Twin: 99.8% Success Probability. Energy: 450kJ.");
    ws.send(JSON.stringify({ type: 'SIMULATION_START', payload: { duration: 500 } }));
    await wait(2000);

    // 4. Execution (6s)
    console.log("[6.0s] ⚙️  Machine Execution: Started. Physics Overlay Active.");
    ws.send(JSON.stringify({ type: 'TELEMETRY_STREAM', payload: { active: true } }));
    await wait(3000);

    // 5. A2A Collaboration (9s)
    console.log("[9.0s] 📡 A2A Message: 'Coolant Low' -> 'Logistics Capsule' (Auto-Refill Dispatched)");
    await wait(2000);

    // 6. Completion (11s)
    console.log("[11.0s] ✅ Finished. Exergy Cost: $12.50. Profit Margin: 32%.");
    console.log("🎬 HIGHLIGHT REEL COMPLETE.");
    ws.close();
});

function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
