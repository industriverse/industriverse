import AIInterpreter from '../src/utils/AIInterpreter.js';
import Encryption from '../src/utils/Encryption.js';
import CNCDriver from '../backend/drivers/cncDriver.js';

async function runTest() {
    console.log("=== Maestro End-to-End Verification ===\n");

    // 1. User Intent (Glyph)
    const glyph = "⊽0.1";
    const machineId = "Haas_VF2";
    console.log(`1. User Input: ${glyph} (Target: ${machineId})`);

    // 2. Interpretation (The Brain)
    const interpreted = await AIInterpreter.translate(glyph, machineId);
    console.log(`2. Interpreted:`, interpreted);

    if (interpreted.type === 'error') {
        console.error("Interpretation Failed!");
        return;
    }

    // 3. Encryption (The Shield)
    const encrypted = Encryption.encrypt(interpreted.cmd);
    console.log(`3. Encrypted Bubble:`, { iv: encrypted.iv, tag: encrypted.tag });

    // 4. Transmission (Simulated)
    console.log(`4. Transmitting to Machine...`);

    // 5. Decryption (Machine Side)
    const decryptedCmd = Encryption.decrypt(encrypted);
    console.log(`5. Decrypted at Machine: ${decryptedCmd}`);

    if (decryptedCmd !== interpreted.cmd) {
        console.error("Decryption Mismatch!");
        return;
    }

    // 6. Execution (The Driver)
    const driver = new CNCDriver({ id: machineId, type: 'CNC', connection: { ip: 'localhost' } });
    const result = await driver.execute({ ...interpreted, cmd: decryptedCmd });
    console.log(`6. Execution Result:`, result);

    console.log("\n=== Verification SUCCESS ===");
}

runTest();
