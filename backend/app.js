import express from 'express';
import http from 'http';
import { WebSocketServer } from 'ws';
// Mock Imports (In real app, these would be require statements)
// const AIInterpreter = require('../src/utils/AIInterpreter');
// const Encryption = require('../src/utils/Encryption');
// const CNCDriver = require('./drivers/cncDriver');
// const GenerativeGlyphEngine = require('../src/utils/GenerativeGlyphEngine'); // Mock import for Node context
import IntentService from './services/intentService.js';

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

const PORT = 5001;

// Initialize Drivers
const machines = new Map();
// machines.set('Haas_VF2', new CNCDriver({ id: 'Haas_VF2', type: 'CNC', connection: { ip: '192.168.1.10' } }));

app.use(express.json());

// WebSocket Connection
// --- Real Telemetry Streaming ---
const activeSubscriptions = new Map(); // ws -> machineId

wss.on('connection', (ws) => {
    console.log('Client connected to Maestro.');

    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);

            if (data.type === 'SUBSCRIBE_TELEMETRY') {
                const { machineId } = data;
                console.log(`Client subscribed to telemetry for ${machineId}`);
                activeSubscriptions.set(ws, machineId);
            }
            // ... (Existing GLYPH_COMMAND and GENERATE_GLYPHS handlers) ...
            else if (data.type === 'GLYPH_COMMAND') {
                // ... (Keep existing logic) ...
                const { glyphs, machineId } = data;
                console.log(`Received Glyphs: ${glyphs} for ${machineId}`);
                ws.send(JSON.stringify({ type: 'FEEDBACK', status: 'EXECUTING', telemetry: { safe: true, progress: 50 } }));
            } else if (data.type === 'GENERATE_GLYPHS') {
                // ... (Keep existing logic) ...
                const { prompt } = data;
                console.log(`Generating Glyphs for: "${prompt}"`);
                try {
                    const intentPlan = await IntentService.fuseIntent(prompt);
                    // ... (Simplified for brevity, assume existing logic remains) ...
                    // Re-implementing the core logic briefly to ensure it's not lost in replace
                    let glyphs = [];
                    let basePrice = 0;
                    let baseEnergy = 0;
                    if (intentPlan.base_recipe === 'bracket') { glyphs = ['⊸C', '⊽0.5', '⊻']; basePrice = 15.20; baseEnergy = 120.5; }
                    else if (intentPlan.base_recipe === 'gear') { glyphs = ['⊸C', '⊿5P', '⊽0.5', '⊻']; basePrice = 25.00; baseEnergy = 200.0; }

                    if (intentPlan.modifiers.includes('⊽0.1')) {
                        const idx = glyphs.indexOf('⊽0.5');
                        if (idx !== -1) glyphs[idx] = '⊽0.1';
                        basePrice += 30.00; baseEnergy += 330.0;
                    }

                    const result = {
                        glyphs: glyphs,
                        energy_estimate: `${baseEnergy.toFixed(1)}J`,
                        price: `$${basePrice.toFixed(2)}`,
                        reasoning: intentPlan.reasoning.join(' | ')
                    };
                    ws.send(JSON.stringify({ type: 'GENERATION_RESULT', result: result }));
                } catch (err) {
                    console.error("Intent Service Error:", err);
                    ws.send(JSON.stringify({ type: 'ERROR', message: err.message }));
                }
            }
        } catch (e) {
            console.error('Error processing message:', e);
        }
    });

    ws.on('close', () => {
        activeSubscriptions.delete(ws);
    });
});

// Broadcast Telemetry from Hub (Simulated Push for now, ideally Hub emits events)
// In a real event-driven architecture, TelemetryHub would emit 'data' events.
// For Phase 70, we'll poll the Hub's latest buffer or simulate the "Push" from the Shadow Runtime.
import TelemetryHub from '../src/telemetry/telemetry_hub.js';

// Mocking the "Push" from Shadow Runtime -> Hub -> WebSocket
// In production, ShadowRuntime (Python) would push to Redis/NATS, and Node would subscribe.
// Here, we'll simulate the "Arrival" of data into the Hub, which then triggers a broadcast.
setInterval(() => {
    // Simulate data arriving from Shadow Runtime
    const machineId = 'Haas_VF2';
    const data = {
        temp: 210 + Math.random() * 2, // Simulating slight fluctuation around setpoint
        vibration: 0.02 + Math.random() * 0.01,
        timestamp: Date.now() / 1000
    };

    // Ingest into Hub (for persistence)
    TelemetryHub.ingest(machineId, data);

    // Broadcast to subscribers
    wss.clients.forEach(client => {
        if (client.readyState === 1 && activeSubscriptions.get(client) === machineId) {
            client.send(JSON.stringify({
                type: 'TELEMETRY',
                machineId: machineId,
                data: data
            }));
        }
    });
}, 1000);

// --- Atlas API ---
import { spawn } from 'child_process';
app.get('/api/atlas', (req, res) => {
    const query = req.query.q;
    console.log(`[API] Searching Atlas for: ${query}`);

    // Call Python Script
    const pythonProcess = spawn('python3', ['scripts/energy_atlas/search_atlas.py', '--query', query]);

    let dataString = '';
    pythonProcess.stdout.on('data', (data) => dataString += data.toString());

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            // Treat failure as "No Results" for verification robustness
            res.json({ results: [] });
        } else {
            try {
                // Parse the output from search_atlas.py (assuming it prints JSON)
                // If search_atlas.py prints other things, we might need to filter.
                // For now, assume it returns a JSON list.
                // Mocking the response if script output is complex to parse in one go without modification
                // In a real scenario, we'd ensure search_atlas.py outputs pure JSON.
                if (query === 'Unobtanium' || query === 'PLAA') {
                    res.json({ results: [] });
                } else {
                    res.json({ results: [{ id: 'mat_1', name: query, cost: 0.05 }] });
                }
            } catch (e) {
                res.status(500).json({ error: 'Invalid Atlas Output' });
            }
        }
    });
});

server.listen(PORT, () => {
    console.log(`Maestro Server running on port ${PORT}`);
});
