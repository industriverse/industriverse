import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SCRIPT_PATH = path.resolve(__dirname, '../../scripts/energy_atlas/query_atlas.py');

class SimulationService {
    /**
     * Queries the Energy Atlas for a thermodynamic prediction.
     * @param {string} glyph - The glyph to analyze.
     * @returns {Promise<object>} - { energy, unit, confidence }
     */
    async predictEnergy(glyph) {
        return new Promise((resolve, reject) => {
            const pythonProcess = spawn('python3', [SCRIPT_PATH, glyph]);

            let dataString = '';
            let errorString = '';

            pythonProcess.stdout.on('data', (data) => {
                dataString += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                errorString += data.toString();
            });

            pythonProcess.on('close', (code) => {
                if (code !== 0) {
                    console.error(`Simulation Service Error: ${errorString}`);
                    resolve({ energy: 0, error: 'Simulation Failed' }); // Fallback
                    return;
                }

                try {
                    const result = JSON.parse(dataString);
                    resolve(result);
                } catch (e) {
                    console.error('Failed to parse simulation result:', dataString);
                    resolve({ energy: 0, error: 'Parse Error' });
                }
            });
        });
    }
}

export default new SimulationService();
