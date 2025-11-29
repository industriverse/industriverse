class APIClient {
    constructor(baseUrl = 'http://localhost:5001', wsUrl = 'ws://localhost:5001') {
        this.baseUrl = baseUrl;
        this.wsUrl = wsUrl;
        this.ws = null;
        this.listeners = {};
        this.isConnected = false;
    }

    connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.wsUrl);

            this.ws.onopen = () => {
                console.log('[API] Connected to Maestro Backend');
                this.isConnected = true;
                resolve();
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this._handleMessage(data);
                } catch (e) {
                    console.error('[API] Failed to parse message:', e);
                }
            };

            this.ws.onerror = (err) => {
                console.error('[API] Connection Error:', err);
                reject(err);
            };

            this.ws.onclose = () => {
                console.log('[API] Disconnected');
                this.isConnected = false;
            };
        });
    }

    _handleMessage(data) {
        if (this.listeners[data.type]) {
            this.listeners[data.type].forEach(cb => cb(data));
        }
        // Also fire generic 'message' listener
        if (this.listeners['*']) {
            this.listeners['*'].forEach(cb => cb(data));
        }
    }

    on(type, callback) {
        if (!this.listeners[type]) {
            this.listeners[type] = [];
        }
        this.listeners[type].push(callback);
    }

    off(type, callback) {
        if (this.listeners[type]) {
            this.listeners[type] = this.listeners[type].filter(cb => cb !== callback);
        }
    }

    // --- HTTP Methods ---

    async fetchAtlas(query) {
        const response = await fetch(`${this.baseUrl}/api/atlas?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error(`Atlas Query Failed: ${response.statusText}`);
        return await response.json();
    }

    // --- WebSocket Methods ---

    sendIntent(prompt) {
        this._send({
            type: 'GENERATE_GLYPHS',
            prompt: prompt
        });
    }

    subscribeTelemetry(machineId) {
        this._send({
            type: 'SUBSCRIBE_TELEMETRY',
            machineId: machineId
        });
    }

    _send(payload) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify(payload));
        } else {
            console.warn('[API] Not connected. Dropping message:', payload);
        }
    }
}

export default new APIClient();
