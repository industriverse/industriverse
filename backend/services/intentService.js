import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class IntentService {
    constructor() {
        this.scriptPath = path.join(__dirname, '../../src/intent/glyph_intent_fuser.py');
    }

    /**
     * Fuses a natural language prompt into a Glyph plan using the Python Intent Kernel.
     * @param {string} prompt 
     * @returns {Promise<object>}
     */
    async fuseIntent(prompt) {
        return new Promise((resolve, reject) => {
            // Create a temporary script runner to call the python class
            const pythonProcess = spawn('python3', ['-c', `
import sys
import json
import os
sys.path.append(os.getcwd())
from src.intent.glyph_intent_fuser import GlyphIntentFuser

fuser = GlyphIntentFuser()
result = fuser.fuse("${prompt}")
print(json.dumps(result))
            `]);

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
                    reject(new Error(`Intent Kernel failed: ${errorString}`));
                } else {
                    try {
                        resolve(JSON.parse(dataString));
                    } catch (e) {
                        reject(new Error(`Failed to parse Intent Kernel output: ${e.message}`));
                    }
                }
            });
        });
    }
}

export default new IntentService();
