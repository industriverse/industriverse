import crypto from 'crypto';

class Encryption {
    constructor() {
        // In a real implementation, this would use a post-quantum library like liboqs.
        // For now, we simulate Lattice Encryption using AES-256-GCM but wrapped in a "Lattice" API.
        this.algorithm = 'aes-256-gcm';
        this.key = crypto.randomBytes(32); // Simulates the Lattice Key
    }

    /**
     * Encrypts a command using "Lattice" bubble.
     * @param {string} text - The raw command (e.g., "G01 X0.1")
     * @returns {object} - { iv, content, tag } (The "Bubble")
     */
    encrypt(text) {
        const iv = crypto.randomBytes(12);
        const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);

        let encrypted = cipher.update(text, 'utf8', 'hex');
        encrypted += cipher.final('hex');

        return {
            iv: iv.toString('hex'),
            content: encrypted,
            tag: cipher.getAuthTag().toString('hex'),
            type: 'LATTICE_V1' // Marker for the machine
        };
    }

    /**
     * Decrypts the bubble (Machine Side).
     */
    decrypt(bubble) {
        const decipher = crypto.createDecipheriv(
            this.algorithm,
            this.key,
            Buffer.from(bubble.iv, 'hex')
        );

        decipher.setAuthTag(Buffer.from(bubble.tag, 'hex'));

        let decrypted = decipher.update(bubble.content, 'hex', 'utf8');
        decrypted += decipher.final('utf8');

        return decrypted;
    }
}

export default new Encryption();
