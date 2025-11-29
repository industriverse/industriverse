import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class SimulationService {
    constructor() {
        this.scriptPath = path.join(__dirname, '../../src/simulation/simulation_oracle.py');
    }

    /**
     * Simulates a Bytecode program to predict energy and time.
     * @param {Array} bytecode 
     * @returns {Promise<object>}
     */
    async simulate(bytecode) {
        return new Promise((resolve, reject) => {
            const pythonProcess = spawn('python3', ['-c', `
import sys
import json
import os
sys.path.append(os.getcwd())
from src.simulation.simulation_oracle import SimulationOracle

oracle = SimulationOracle()
program = ${JSON.stringify(bytecode)}
print(json.dumps(oracle.simulate(program)))
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
                    reject(new Error(`Simulation Oracle failed: ${errorString}`));
                } else {
                    try {
                        resolve(JSON.parse(dataString));
                    } catch (e) {
                        reject(new Error(`Failed to parse Simulation output: ${e.message}`));
                    }
                }
            });
        });
    }
}

export default new SimulationService();
