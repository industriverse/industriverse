import WebSocket from 'ws';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Start the Server
const serverProcess = spawn('node', ['backend/app.js'], {
    cwd: path.join(__dirname, '../'),
    stdio: 'pipe' // Capture output
});

let ws;
const PORT = 5001; // Match app.js port

serverProcess.stdout.on('data', (data) => {
    console.log(`SERVER: ${data}`);
    if (data.toString().includes(`Server running on port ${PORT}`)) {
        startTest();
    }
});

serverProcess.stderr.on('data', (data) => {
    console.error(`SERVER ERROR: ${data}`);
});

function startTest() {
    console.log('Connecting to WebSocket...');
    ws = new WebSocket(`ws://localhost:${PORT}`);

    ws.on('open', () => {
        console.log('Connected.');

        // Test Case 1: Lightweight Bracket
        const prompt = "Make a lightweight bracket";
        console.log(`Sending Prompt: "${prompt}"`);

        ws.send(JSON.stringify({
            type: 'GENERATE_GLYPHS',
            prompt: prompt
        }));
    });

    ws.on('message', (data) => {
        const response = JSON.parse(data);
        console.log('Received Response:', response);

        if (response.type === 'GENERATION_RESULT') {
            const result = response.result;

            // Verification Logic
            const hasFineMill = result.glyphs.includes('⊽0.1');
            const hasAlign = result.glyphs.includes('⊸C');

            if (hasFineMill && hasAlign) {
                console.log('✅ TEST PASSED: Generated correct Glyphs for "lightweight bracket".');
                cleanup(0);
            } else {
                console.error('❌ TEST FAILED: Incorrect Glyphs generated.');
                console.error('Expected "⊽0.1" (Fine Mill) and "⊸C" (Align).');
                cleanup(1);
            }
        } else if (response.type === 'ERROR') {
            console.error('❌ TEST FAILED: Server returned error:', response.message);
            cleanup(1);
        }
    });

    ws.on('error', (err) => {
        console.error('WebSocket Error:', err);
        cleanup(1);
    });
}

function cleanup(exitCode) {
    if (ws) ws.close();
    serverProcess.kill();
    process.exit(exitCode);
}

// Timeout
setTimeout(() => {
    console.error('❌ TEST TIMEOUT');
    cleanup(1);
}, 10000);
