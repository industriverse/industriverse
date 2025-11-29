import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class TelemetryHub {
    constructor() {
        this.buffer = {}; // { machineId: [data points] }
        this.flushInterval = 5000; // Flush every 5 seconds
        this.loggerPath = path.join(__dirname, 'telemetry_logger.py');

        // Start Flush Loop
        setInterval(() => this.flushAll(), this.flushInterval);
    }

    /**
     * Ingests a single telemetry point.
     * @param {string} machineId 
     * @param {object} data { temp: 25.5, vibration: 0.01, timestamp: 1234567890 }
     */
    ingest(machineId, data) {
        if (!this.buffer[machineId]) {
            this.buffer[machineId] = [];
        }
        // Add timestamp if missing
        if (!data.timestamp) data.timestamp = Date.now() / 1000;

        this.buffer[machineId].push(data);
    }

    async flushAll() {
        const promises = Object.keys(this.buffer).map(machineId => {
            const batch = this.buffer[machineId];
            if (batch.length === 0) return Promise.resolve();

            // Clear buffer immediately to avoid double-write
            this.buffer[machineId] = [];

            return this.flushMachine(machineId, batch);
        });

        await Promise.all(promises);
    }

    async flushMachine(machineId, batch) {
        return new Promise((resolve, reject) => {
            const payload = JSON.stringify({ machine_id: machineId, batch });

            const pythonProcess = spawn('python3', [this.loggerPath, payload]);

            let dataString = '';

            pythonProcess.stdout.on('data', (data) => {
                dataString += data.toString();
            });

            pythonProcess.on('close', (code) => {
                if (code !== 0) {
                    console.error(`Telemetry Logger failed for ${machineId}`);
                    resolve(); // Don't crash hub on log failure
                } else {
                    console.log(`Python Response: ${dataString}`);
                    console.log(`Flushed ${batch.length} points for ${machineId}`);
                    resolve();
                }
            });
        });
    }
}

export default new TelemetryHub();
