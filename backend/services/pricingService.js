import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PricingService {
    constructor() {
        this.scriptPath = path.join(__dirname, '../../src/economy/pricing_engine.py');
    }

    /**
     * Calculates Exergy Price based on simulation results.
     * @param {object} simulationResult 
     * @returns {Promise<object>}
     */
    async calculatePrice(simulationResult) {
        return new Promise((resolve, reject) => {
            const pythonProcess = spawn('python3', ['-c', `
import sys
import json
import os
sys.path.append(os.getcwd())
from src.economy.pricing_engine import ExergyPricingEngine

engine = ExergyPricingEngine()
sim_result = ${JSON.stringify(simulationResult)}
print(json.dumps(engine.calculate_price(sim_result)))
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
                    reject(new Error(`Pricing Engine failed: ${errorString}`));
                } else {
                    try {
                        resolve(JSON.parse(dataString));
                    } catch (e) {
                        reject(new Error(`Failed to parse Pricing output: ${e.message}`));
                    }
                }
            });
        });
    }
}

export default new PricingService();
